"""
Document Parser Module
Extracts YAML frontmatter and markdown content from files
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ParsedDocument:
    """Structure for parsed document data"""
    filepath: Path
    filename: str
    metadata: Dict
    content: str
    parse_success: bool
    parse_error: Optional[str] = None


def _strip_code_block_wrapper(content: str) -> tuple[str, bool]:
    """
    Strip code block wrappers from YAML frontmatter if present

    Handles cases like:
    ```yml
    ---
    title: ...
    ---
    ```
    # Content

    Returns:
        (stripped_content, was_wrapped)
    """

    # Check if content starts with code block
    if content.startswith('```yml\n') or content.startswith('```yaml\n'):
        # Remove opening code block
        content = re.sub(r'^```ya?ml\n', '', content)

        # Find and remove closing ``` after YAML frontmatter
        # Pattern: --- YAML --- followed by ``` then rest of content
        pattern = r'^(---\s*\n.*?\n---)\s*\n```\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            yaml_part = match.group(1)
            markdown_part = match.group(2)
            return f"{yaml_part}\n\n{markdown_part}", True

        # Fallback: just remove opening ``` if pattern doesn't match
        return content, True

    # No wrapper found
    return content, False


def parse_markdown_with_frontmatter(filepath: Path) -> ParsedDocument:
    """
    Parse markdown file with YAML frontmatter

    Handles cases where YAML is wrapped in code blocks (```yml or ```yaml)
    and automatically strips them.

    Returns ParsedDocument with:
    - metadata: dict (empty if parsing fails)
    - content: str (always extracted)
    - parse_success: bool
    - parse_error: str or None
    """

    with open(filepath, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # Auto-fix: Strip code block wrappers if present
    # Handles: ```yml\n---\n...---\n```
    stripped_content, was_wrapped = _strip_code_block_wrapper(raw_content)

    # Try to extract YAML frontmatter
    # Pattern: starts with ---, YAML content, ends with ---
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', stripped_content, re.DOTALL)

    if not frontmatter_match:
        # No frontmatter found - return content only
        error_msg = "No YAML frontmatter found (missing --- markers)"
        if was_wrapped:
            error_msg += " (code block wrapper was stripped)"

        return ParsedDocument(
            filepath=filepath,
            filename=filepath.name,
            metadata={},
            content=stripped_content,
            parse_success=False,
            parse_error=error_msg
        )

    frontmatter_text = frontmatter_match.group(1)
    markdown_body = frontmatter_match.group(2)

    # Try to parse YAML
    try:
        metadata = yaml.safe_load(frontmatter_text)

        if not metadata or not isinstance(metadata, dict):
            return ParsedDocument(
                filepath=filepath,
                filename=filepath.name,
                metadata={},
                content=markdown_body,
                parse_success=False,
                parse_error="YAML parsed but is empty or not a dictionary"
            )

        return ParsedDocument(
            filepath=filepath,
            filename=filepath.name,
            metadata=metadata,
            content=markdown_body,
            parse_success=True,
            parse_error=None
        )

    except yaml.YAMLError as e:
        return ParsedDocument(
            filepath=filepath,
            filename=filepath.name,
            metadata={},
            content=markdown_body,
            parse_success=False,
            parse_error=f"YAML parsing error: {str(e)}"
        )


def main():
    """Test the parser on a single file"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_markdown_file>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Parse
    result = parse_markdown_with_frontmatter(filepath)

    # Display results
    print("="*80)
    print(f"File: {result.filename}")
    print("="*80)
    print(f"\nParse Success: {result.parse_success}")

    if result.parse_error:
        print(f"Parse Error: {result.parse_error}")

    print(f"\nMetadata ({len(result.metadata)} fields):")
    for key, value in result.metadata.items():
        print(f"  {key}: {value}")

    print(f"\nContent Preview ({len(result.content)} chars):")
    print(result.content[:300])
    print("...")


if __name__ == "__main__":
    main()
