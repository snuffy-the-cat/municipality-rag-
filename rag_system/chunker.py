"""
Document Chunker Module
Splits markdown content into semantic chunks by headers
"""

import re
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Chunk:
    """Structure for a document chunk"""
    header: str
    content: str
    chunk_index: int
    chunk_type: str = "section"


def chunk_by_headers(markdown_content: str, default_header: str = "Overview") -> List[Chunk]:
    """
    Chunk markdown content by headers (semantic chunking)

    Each chunk includes:
    - header: The section header (# Header Text)
    - content: Text content under that header
    - chunk_index: Position in document (0, 1, 2...)
    - chunk_type: Always 'section' for now

    Args:
        markdown_content: The markdown text to chunk
        default_header: Header to use for content before first header

    Returns:
        List of Chunk objects
    """

    chunks = []

    # Split by headers (# or ## or ###)
    # Pattern captures header lines like "# Title" or "## Section"
    sections = re.split(r'\n(#{1,3}\s+.+)\n', markdown_content)

    # sections array structure:
    # [content_before_first_header, '# Header1', 'content1', '## Header2', 'content2', ...]

    current_header = default_header
    current_content = []
    chunk_index = 0

    for i, section in enumerate(sections):
        section_stripped = section.strip()

        if not section_stripped:
            continue

        # Check if this section is a header
        if section_stripped.startswith('#'):
            # Save previous chunk if it has content
            if current_content:
                chunk_text = '\n'.join(current_content).strip()
                if chunk_text:  # Only add non-empty chunks
                    chunks.append(Chunk(
                        header=current_header,
                        content=chunk_text,
                        chunk_index=chunk_index,
                        chunk_type='section'
                    ))
                    chunk_index += 1

            # Start new chunk
            current_header = section_stripped
            current_content = []
        else:
            # This is content
            current_content.append(section_stripped)

    # Add final chunk
    if current_content:
        chunk_text = '\n'.join(current_content).strip()
        if chunk_text:
            chunks.append(Chunk(
                header=current_header,
                content=chunk_text,
                chunk_index=chunk_index,
                chunk_type='section'
            ))

    return chunks


def main():
    """Test the chunker on sample markdown"""
    import sys
    from pathlib import Path

    # If file path provided, read and chunk it
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])

        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove YAML frontmatter if present
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

        chunks = chunk_by_headers(content)

        print("="*80)
        print(f"File: {filepath.name}")
        print("="*80)
        print(f"\nTotal chunks: {len(chunks)}\n")

        for chunk in chunks:
            print(f"Chunk {chunk.chunk_index}: {chunk.header}")
            print(f"  Type: {chunk.chunk_type}")
            print(f"  Length: {len(chunk.content)} chars")
            print(f"  Preview: {chunk.content[:100]}...")
            print()
    else:
        # Test with sample content
        sample = """
# Introduction

This is the introduction section with some text.

## Procedures

Here are the procedures:
1. Step one
2. Step two

### Sub-procedure

Additional details here.

## Common Issues

List of common issues and solutions.
"""

        chunks = chunk_by_headers(sample)

        print("="*80)
        print("Sample Markdown Chunking Test")
        print("="*80)
        print(f"\nTotal chunks: {len(chunks)}\n")

        for chunk in chunks:
            print(f"Chunk {chunk.chunk_index}: {chunk.header}")
            print(f"  Content: {chunk.content[:60]}...")
            print()


if __name__ == "__main__":
    main()
