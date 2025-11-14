"""
New Modular Indexing Script
Uses parser, chunker, validator, and logger modules
"""

import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings

# Import our modules
from parser import parse_markdown_with_frontmatter
from chunker import chunk_by_headers
from validator import ChunkValidator
from logger_config import StructuredLogger

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "data/preprocessed/markdown"  # Use preprocessed files
DB_PATH = PROJECT_ROOT / "database/chroma"
LOG_DIR = PROJECT_ROOT / "outputs/logs"


def create_chromadb_collection(structured_logger: StructuredLogger):
    """Initialize ChromaDB client and collection"""

    structured_logger.log_structured(
        event_type='db_init',
        level='info',
        message=f"Initializing ChromaDB at: {DB_PATH}"
    )

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
        structured_logger.log_structured(
            event_type='db_reset',
            level='info',
            message="Deleted existing collection"
        )
    except:
        pass

    # Create new collection
    collection = client.create_collection(
        name="municipality_docs",
        metadata={"description": "Municipal departure documentation"}
    )

    structured_logger.log_structured(
        event_type='db_created',
        level='info',
        message="ChromaDB collection created"
    )

    return client, collection


def index_all_documents(docs_dir: Path, collection, structured_logger: StructuredLogger):
    """
    Index all markdown documents into ChromaDB using modular pipeline
    Returns statistics
    """

    structured_logger.log_structured(
        event_type='indexing_start',
        level='info',
        message=f"Reading documents from: {docs_dir}"
    )

    # Get all markdown files
    md_files = list(docs_dir.glob("*.md"))
    structured_logger.log_structured(
        event_type='files_found',
        level='info',
        message=f"Found {len(md_files)} markdown files",
        file_count=len(md_files)
    )

    # Initialize validator
    validator = ChunkValidator()

    # Statistics
    stats = {
        'total_files': len(md_files),
        'total_chunks': 0,
        'indexed_chunks': 0,
        'warnings': 0,
        'errors': 0,
        'parse_failures': 0
    }

    # Process each file
    for md_file in sorted(md_files):
        # Step 1: Parse
        parsed_doc = parse_markdown_with_frontmatter(md_file)

        # Log parsing result
        structured_logger.log_file_parsing(
            filename=parsed_doc.filename,
            parse_success=parsed_doc.parse_success,
            parse_error=parsed_doc.parse_error,
            metadata_fields=len(parsed_doc.metadata)
        )

        if not parsed_doc.parse_success:
            stats['parse_failures'] += 1

        # Step 2: Chunk
        chunks = chunk_by_headers(
            parsed_doc.content,
            parsed_doc.metadata.get('title', 'Overview')
        )

        stats['total_chunks'] += len(chunks)

        # Step 3: Validate and index each chunk
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            # Validate chunk
            validation_result = validator.validate_chunk(chunk, parsed_doc)

            # Log validation
            structured_logger.log_chunk_validation(
                filename=parsed_doc.filename,
                chunk_index=chunk.chunk_index,
                header=chunk.header,
                is_valid=validation_result.is_valid,
                severity=validation_result.severity,
                issues=validation_result.issues,
                metadata=validation_result.enriched_metadata
            )

            # Count warnings/errors
            if validation_result.severity == 'warning':
                stats['warnings'] += 1
            elif validation_result.severity == 'critical':
                stats['errors'] += 1

            # Skip invalid chunks
            if not validation_result.is_valid:
                continue

            # Prepare for indexing
            chunk_id = f"{md_file.stem}_chunk_{chunk.chunk_index}"

            # Enrich chunk text with Tier 2 metadata for better embedding
            # This makes contacts, emails, systems searchable via semantic search
            metadata_context = []
            meta = validation_result.enriched_metadata

            if meta.get('contact_names'):
                metadata_context.append(f"Contacts: {meta['contact_names']}")
            if meta.get('contact_emails'):
                metadata_context.append(f"Emails: {meta['contact_emails']}")
            if meta.get('system_names'):
                metadata_context.append(f"Systems: {meta['system_names']}")
            if meta.get('related_doc_ids'):
                metadata_context.append(f"Related: {meta['related_doc_ids']}")

            # Combine: header + content + metadata context
            chunk_text = f"{chunk.header}\n\n{chunk.content}"
            if metadata_context:
                chunk_text += "\n\n[Metadata: " + " | ".join(metadata_context) + "]"

            ids.append(chunk_id)
            documents.append(chunk_text)
            metadatas.append(validation_result.enriched_metadata)

        # Index chunks for this file
        if documents:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            stats['indexed_chunks'] += len(documents)

            # Log indexed chunks
            for chunk_id in ids:
                structured_logger.log_chunk_indexed(
                    filename=parsed_doc.filename,
                    chunk_index=int(chunk_id.split('_chunk_')[1]),
                    chunk_id=chunk_id
                )

    return stats


def main():
    """Main indexing function"""

    print("="*80)
    print("Municipality RAG - Modular Document Indexing")
    print("="*80)
    print()

    # Initialize structured logger
    structured_logger = StructuredLogger(LOG_DIR)

    try:
        # Check if documents exist
        if not DOCS_DIR.exists():
            structured_logger.log_structured(
                event_type='error',
                level='error',
                message=f"Documents directory not found: {DOCS_DIR}"
            )
            print(f"Error: Documents directory not found: {DOCS_DIR}")
            print("Run generate_documents.py first to create documents")
            sys.exit(1)

        # Create ChromaDB collection
        client, collection = create_chromadb_collection(structured_logger)

        # Index all documents
        stats = index_all_documents(DOCS_DIR, collection, structured_logger)

        # Log summary
        structured_logger.log_summary(
            total_files=stats['total_files'],
            total_chunks=stats['total_chunks'],
            indexed_chunks=stats['indexed_chunks'],
            warnings=stats['warnings'],
            errors=stats['errors']
        )

        # Additional stats
        print()
        print("Additional Statistics:")
        print(f"  Parse failures: {stats['parse_failures']}")
        print(f"  Database location: {DB_PATH}")
        print(f"  Log files: {LOG_DIR}")
        print()

        # Test query
        print("="*80)
        print("Testing retrieval with sample query...")
        print("="*80)

        test_query = "How do I process a building permit?"
        results = collection.query(
            query_texts=[test_query],
            n_results=3
        )

        print(f"\nQuery: '{test_query}'")
        print(f"Found {len(results['ids'][0])} results:\n")

        for i, (doc_id, doc, metadata) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0]
        ), 1):
            print(f"{i}. {metadata['title']} - {metadata['header']}")
            print(f"   File: {metadata['filename']}")
            print(f"   Category: {metadata['category']}")
            print(f"   Preview: {doc[:100]}...")
            print()

    finally:
        # Close logger
        structured_logger.close()


if __name__ == "__main__":
    main()
