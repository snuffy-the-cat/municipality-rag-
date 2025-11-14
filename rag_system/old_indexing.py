"""
RAG Indexing Script
Reads generated markdown documents and indexes them into ChromaDB
"""

import os
import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add(PROJECT_ROOT / "outputs/logs/indexing_{time}.log", rotation="10 MB")

# Paths
DOCS_DIR = PROJECT_ROOT / "data/generated/markdown"
DB_PATH = PROJECT_ROOT / "database/chroma"


def parse_markdown_with_frontmatter(filepath: Path) -> Dict:
    """Parse markdown file with YAML frontmatter"""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)

    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        markdown_body = frontmatter_match.group(2)

        # Parse YAML
        try:
            metadata = yaml.safe_load(frontmatter_text)
        except Exception as e:
            logger.warning(f"Failed to parse YAML frontmatter in {filepath.name}: {e}")
            metadata = {}
    else:
        # No frontmatter found
        metadata = {}
        markdown_body = content

    return {
        'metadata': metadata,
        'content': markdown_body,
        'filepath': str(filepath),
        'filename': filepath.name
    }


def chunk_by_headers(markdown_content: str, metadata: Dict) -> List[Dict]:
    """
    Chunk markdown content by headers (semantic chunking)
    Each chunk includes the header and content under it
    """

    chunks = []

    # Split by headers (# or ##)
    sections = re.split(r'\n(#{1,3}\s+.+)\n', markdown_content)

    # sections will be: ['intro text', '# Header 1', 'content 1', '## Header 2', 'content 2', ...]

    current_header = metadata.get('title', 'Overview')
    current_content = []

    for i, section in enumerate(sections):
        if section.strip().startswith('#'):
            # This is a header
            # Save previous chunk if exists
            if current_content:
                chunk_text = '\n'.join(current_content).strip()
                if chunk_text:  # Only add non-empty chunks
                    chunks.append({
                        'header': current_header,
                        'content': chunk_text,
                        'chunk_type': 'section'
                    })

            # Start new chunk
            current_header = section.strip()
            current_content = []
        else:
            # This is content
            if section.strip():
                current_content.append(section.strip())

    # Add last chunk
    if current_content:
        chunk_text = '\n'.join(current_content).strip()
        if chunk_text:
            chunks.append({
                'header': current_header,
                'content': chunk_text,
                'chunk_type': 'section'
            })

    return chunks


def create_embeddings_collection():
    """Initialize ChromaDB client and collection"""

    logger.info(f"Initializing ChromaDB at: {DB_PATH}")

    # Ensure directory exists
    DB_PATH.mkdir(parents=True, exist_ok=True)

    # Create ChromaDB client
    client = chromadb.PersistentClient(
        path=str(DB_PATH),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    # Delete existing collection if exists (for fresh start)
    try:
        client.delete_collection(name="municipality_docs")
        logger.info("Deleted existing collection")
    except:
        pass

    # Create new collection
    # ChromaDB will use default embedding function (all-MiniLM-L6-v2)
    collection = client.create_collection(
        name="municipality_docs",
        metadata={"description": "Municipal departure documentation"}
    )

    logger.success("ChromaDB collection created")

    return client, collection


def index_all_documents(docs_dir: Path, collection) -> int:
    """
    Index all markdown documents into ChromaDB
    Returns number of chunks indexed
    """

    logger.info(f"Reading documents from: {docs_dir}")

    # Get all markdown files
    md_files = list(docs_dir.glob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files")

    total_chunks = 0

    for md_file in md_files:
        logger.info(f"Processing: {md_file.name}")

        # Parse document
        doc = parse_markdown_with_frontmatter(md_file)
        metadata = doc['metadata']
        content = doc['content']

        # Chunk by headers
        chunks = chunk_by_headers(content, metadata)
        logger.debug(f"  Created {len(chunks)} chunks")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{md_file.stem}_chunk_{i}"

            # Combine header and content for embedding
            chunk_text = f"{chunk['header']}\n\n{chunk['content']}"

            # Metadata for this chunk
            chunk_metadata = {
                'filename': md_file.name,
                'doc_id': md_file.stem,
                'chunk_index': i,
                'header': chunk['header'],
                'chunk_type': chunk['chunk_type'],
                # Document-level metadata
                'title': metadata.get('title', 'Unknown'),
                'category': metadata.get('category', 'Unknown'),
                'subcategory': metadata.get('subcategory', ''),
                'priority': metadata.get('priority', ''),
                'cluster': metadata.get('cluster', ''),
                'frequency': metadata.get('frequency', ''),
            }

            ids.append(chunk_id)
            documents.append(chunk_text)
            metadatas.append(chunk_metadata)

        # Add to collection (ChromaDB handles embeddings automatically)
        if documents:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            total_chunks += len(documents)
            logger.success(f"  Indexed {len(documents)} chunks")

    return total_chunks


def main():
    """Main indexing function"""

    logger.info("="*80)
    logger.info("Municipality RAG - Document Indexing")
    logger.info("="*80)

    # Check if documents exist
    if not DOCS_DIR.exists():
        logger.error(f"Documents directory not found: {DOCS_DIR}")
        logger.error("Run generate_documents.py first to create documents")
        sys.exit(1)

    # Create ChromaDB collection
    client, collection = create_embeddings_collection()

    # Index all documents
    total_chunks = index_all_documents(DOCS_DIR, collection)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("INDEXING COMPLETE")
    logger.info("="*80)
    logger.info(f"Total chunks indexed: {total_chunks}")
    logger.info(f"Database location: {DB_PATH}")
    logger.info(f"Collection: municipality_docs")

    # Test query
    logger.info("\n" + "="*80)
    logger.info("Testing retrieval with sample query...")
    logger.info("="*80)

    test_query = "How do I process a building permit?"
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )

    logger.info(f"\nQuery: '{test_query}'")
    logger.info(f"Found {len(results['ids'][0])} results:\n")

    for i, (doc_id, doc, metadata) in enumerate(zip(
        results['ids'][0],
        results['documents'][0],
        results['metadatas'][0]
    ), 1):
        logger.info(f"{i}. {metadata['title']} - {metadata['header']}")
        logger.info(f"   File: {metadata['filename']}")
        logger.info(f"   Preview: {doc[:150]}...")
        logger.info("")


if __name__ == "__main__":
    main()
