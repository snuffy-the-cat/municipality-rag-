"""
Chunk Validator Module
Validates and enriches chunks before indexing
"""

from typing import Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from parser import ParsedDocument
from chunker import Chunk


@dataclass
class ValidationResult:
    """Result of chunk validation"""
    is_valid: bool
    severity: str  # 'info', 'warning', 'critical'
    issues: list
    enriched_metadata: Dict


class ChunkValidator:
    """
    Validates chunks and enriches metadata with fallbacks
    """

    def __init__(self):
        self.default_metadata = {
            'category': 'Unknown',
            'subcategory': '',
            'priority': '',
            'cluster': '',
            'frequency': ''
        }

    def validate_chunk(
        self,
        chunk: Chunk,
        parsed_doc: ParsedDocument
    ) -> ValidationResult:
        """
        Validate a chunk and enrich its metadata

        Args:
            chunk: The chunk to validate
            parsed_doc: Original parsed document with metadata

        Returns:
            ValidationResult with validation status and enriched metadata
        """

        issues = []
        severity = 'info'

        # Start with parsed metadata or defaults
        metadata = parsed_doc.metadata.copy() if parsed_doc.metadata else {}

        # Check if parsing failed
        if not parsed_doc.parse_success:
            issues.append(f"YAML parsing failed: {parsed_doc.parse_error}")
            severity = 'warning'

            # Try to extract title from first markdown header if missing
            if 'title' not in metadata or not metadata['title']:
                metadata['title'] = self._extract_title_from_content(
                    parsed_doc.content,
                    parsed_doc.filename
                )
                issues.append(f"Title extracted from content/filename")

        # Validate chunk has content
        if not chunk.content or len(chunk.content.strip()) < 10:
            issues.append(f"Chunk {chunk.chunk_index} has insufficient content ({len(chunk.content)} chars)")
            severity = 'warning'

        # Enrich metadata with defaults for missing fields
        for field, default_value in self.default_metadata.items():
            if field not in metadata or metadata[field] is None:
                metadata[field] = default_value

        # Add chunk-specific metadata
        enriched_metadata = {
            'filename': parsed_doc.filename,
            'doc_id': parsed_doc.filepath.stem,
            'chunk_index': chunk.chunk_index,
            'header': chunk.header,
            'chunk_type': chunk.chunk_type,
            # Tier 1: Document-level metadata (essential)
            'title': metadata.get('title', parsed_doc.filename),
            'category': metadata.get('category', 'Unknown'),
            'subcategory': metadata.get('subcategory', ''),
            'priority': metadata.get('priority', ''),
            'cluster': metadata.get('cluster', ''),
            'frequency': metadata.get('frequency', ''),
            # Tier 2: Extracted metadata (searchable via text enrichment)
            'contact_names': metadata.get('contact_names', ''),
            'contact_emails': metadata.get('contact_emails', ''),
            'system_names': metadata.get('system_names', ''),
            'related_doc_ids': metadata.get('related_doc_ids', ''),
        }

        # Determine if chunk is valid for indexing
        # Currently, we index everything unless content is too short
        is_valid = len(chunk.content.strip()) >= 10

        if not is_valid:
            severity = 'critical'

        return ValidationResult(
            is_valid=is_valid,
            severity=severity,
            issues=issues,
            enriched_metadata=enriched_metadata
        )

    def _extract_title_from_content(self, content: str, filename: str) -> str:
        """
        Extract title from first markdown header or use filename

        Args:
            content: Markdown content
            filename: File name as fallback

        Returns:
            Extracted or fallback title
        """

        import re

        # Try to find first # header
        header_match = re.search(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)

        if header_match:
            return header_match.group(1).strip()

        # Fallback to filename without extension
        return Path(filename).stem.replace('_', ' ').title()


def main():
    """Test the validator"""
    import sys
    from pathlib import Path
    from parser import parse_markdown_with_frontmatter
    from chunker import chunk_by_headers

    if len(sys.argv) < 2:
        print("Usage: python validator.py <path_to_markdown_file>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Parse document
    parsed_doc = parse_markdown_with_frontmatter(filepath)

    print("="*80)
    print(f"File: {parsed_doc.filename}")
    print("="*80)
    print(f"Parse Success: {parsed_doc.parse_success}")
    if parsed_doc.parse_error:
        print(f"Parse Error: {parsed_doc.parse_error}")

    # Chunk content
    chunks = chunk_by_headers(parsed_doc.content, parsed_doc.metadata.get('title', 'Overview'))

    print(f"\nTotal chunks: {len(chunks)}\n")

    # Validate each chunk
    validator = ChunkValidator()

    for chunk in chunks:
        result = validator.validate_chunk(chunk, parsed_doc)

        print(f"Chunk {chunk.chunk_index}: {chunk.header}")
        print(f"  Valid: {result.is_valid}")
        print(f"  Severity: {result.severity}")

        if result.issues:
            print(f"  Issues:")
            for issue in result.issues:
                print(f"    - {issue}")

        print(f"  Metadata:")
        print(f"    Title: {result.enriched_metadata['title']}")
        print(f"    Category: {result.enriched_metadata['category']}")
        print(f"    Priority: {result.enriched_metadata['priority']}")
        print()


if __name__ == "__main__":
    main()
