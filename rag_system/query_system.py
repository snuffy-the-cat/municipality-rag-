"""
RAG Query System
Interactive CLI for querying the municipal knowledge base
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
import ollama
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

# Paths
DB_PATH = PROJECT_ROOT / "database/chroma"

# Ollama settings
OLLAMA_MODEL = "llama3.1"


def load_collection():
    """Load ChromaDB collection"""

    logger.info(f"Loading ChromaDB from: {DB_PATH}")

    if not DB_PATH.exists():
        logger.error(f"Database not found at: {DB_PATH}")
        logger.error("Run indexing.py first to create the database")
        sys.exit(1)

    # Create client
    client = chromadb.PersistentClient(
        path=str(DB_PATH),
        settings=Settings(
            anonymized_telemetry=False
        )
    )

    # Get collection
    collection = client.get_collection(name="municipality_docs")

    logger.success(f"Loaded collection with {collection.count()} chunks")

    return collection


def retrieve_relevant_chunks(query: str, collection, n_results: int = 5) -> List[Dict]:
    """
    Retrieve relevant chunks from ChromaDB
    Returns list of chunks with metadata
    """

    logger.info(f"Searching for: '{query}'")

    # Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    # Format results
    chunks = []
    for i, (doc_id, doc, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        chunks.append({
            'id': doc_id,
            'content': doc,
            'metadata': metadata,
            'distance': distance,
            'rank': i + 1
        })

    logger.success(f"Found {len(chunks)} relevant chunks")

    return chunks


def synthesize_answer(query: str, chunks: List[Dict]) -> str:
    """
    Use Ollama to synthesize an answer from retrieved chunks
    """

    logger.info("Synthesizing answer with Ollama...")

    # Build context from chunks
    context_parts = []
    for chunk in chunks:
        source_info = f"[{chunk['metadata']['title']} - {chunk['metadata']['header']}]"
        context_parts.append(f"{source_info}\n{chunk['content']}\n")

    context = "\n---\n".join(context_parts)

    # Build prompt
    prompt = f"""You are a helpful assistant answering questions about municipal procedures and responsibilities.

Use ONLY the information provided in the context below to answer the question. If the context doesn't contain enough information to fully answer the question, say so.

CONTEXT:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Provide a clear, concise answer based on the context
2. When citing sources, use this format: (Source: Document Title - Section Name)
3. Keep citations brief and readable - just mention the document title and section
4. If information is missing or incomplete, mention it
5. Be practical and helpful for a municipal employee

ANSWER:"""

    # Generate with Ollama
    try:
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={
                "temperature": 0.3,  # Lower temperature for factual answers
                "num_predict": 500,
            }
        )

        answer = response['response'].strip()
        logger.success("Answer generated")

        return answer

    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        return "[Error: Could not generate answer]"


def display_results(query: str, answer: str, chunks: List[Dict]):
    """Display query results in a nice format"""

    print("\n" + "="*80)
    print(f"QUESTION: {query}")
    print("="*80)

    print(f"\nANSWER:\n{answer}")

    print("\n" + "-"*80)
    print("SOURCES:")
    print("-"*80)

    # Group chunks by document
    docs_seen = set()
    for chunk in chunks[:3]:  # Show top 3 sources
        doc_key = chunk['metadata']['filename']
        if doc_key not in docs_seen:
            docs_seen.add(doc_key)
            print(f"\n{len(docs_seen)}. {chunk['metadata']['title']}")
            print(f"   File: {chunk['metadata']['filename']}")
            print(f"   Section: {chunk['metadata']['header']}")
            print(f"   Category: {chunk['metadata']['category']}")
            if chunk['metadata'].get('priority'):
                print(f"   Priority: {chunk['metadata']['priority']}")

    print("\n" + "="*80)


def interactive_mode(collection):
    """Run interactive query mode"""

    print("\n" + "="*80)
    print("MUNICIPALITY RAG - Interactive Query System")
    print("="*80)
    print("\nAsk questions about municipal procedures and responsibilities.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            # Get query from user
            query = input("Question: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            # Retrieve relevant chunks
            chunks = retrieve_relevant_chunks(query, collection, n_results=5)

            # Synthesize answer
            answer = synthesize_answer(query, chunks)

            # Display results
            display_results(query, answer, chunks)

            print()  # Extra line before next question

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\nError: {e}\n")


def single_query_mode(query: str, collection):
    """Run a single query and exit"""

    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(query, collection, n_results=5)

    # Synthesize answer
    answer = synthesize_answer(query, chunks)

    # Display results
    display_results(query, answer, chunks)


def main():
    """Main function"""

    import argparse

    parser = argparse.ArgumentParser(description="Query the municipal RAG system")
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Single query to run (exits after answer)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=True,
        help="Run in interactive mode (default)"
    )

    args = parser.parse_args()

    # Load collection
    collection = load_collection()

    # Run query mode
    if args.query:
        single_query_mode(args.query, collection)
    else:
        interactive_mode(collection)


if __name__ == "__main__":
    main()
