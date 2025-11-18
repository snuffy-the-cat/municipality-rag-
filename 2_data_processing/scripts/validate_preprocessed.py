"""
Validate Preprocessed Files
Checks that all YAML parses correctly after preprocessing
"""

import sys
import yaml
import re
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PREPROCESSED_DIR = PROJECT_ROOT / "data/preprocessed/markdown"


def validate_all_files():
    """
    Validate that all preprocessed files have valid YAML
    """

    print("="*80)
    print("VALIDATION - Preprocessed Files")
    print("="*80)
    print()

    # Check directory
    if not PREPROCESSED_DIR.exists():
        print(f"[ERROR] Preprocessed directory not found: {PREPROCESSED_DIR}")
        sys.exit(1)

    # Get all markdown files
    md_files = sorted(PREPROCESSED_DIR.glob("*.md"))
    print(f"Found {len(md_files)} preprocessed files")
    print()

    # Statistics
    stats = {
        'total': len(md_files),
        'valid_yaml': 0,
        'invalid_yaml': 0,
        'no_yaml': 0,
        'missing_fields': []
    }

    # Required fields
    required_fields = ['title', 'category']

    print("="*80)
    print("VALIDATING FILES")
    print("="*80)
    print()

    for md_file in md_files:
        print(f"Validating: {md_file.name}")

        # Read file
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

        if not match:
            print(f"  [WARNING] No YAML frontmatter found")
            stats['no_yaml'] += 1
            print()
            continue

        yaml_text = match.group(1)

        # Try to parse
        try:
            metadata = yaml.safe_load(yaml_text)

            if not isinstance(metadata, dict):
                print(f"  [FAIL] YAML did not parse to dictionary")
                stats['invalid_yaml'] += 1
                print()
                continue

            # Check fields
            field_count = len(metadata)
            missing = [f for f in required_fields if not metadata.get(f)]

            if missing:
                print(f"  [WARNING] {field_count} fields, missing: {', '.join(missing)}")
                stats['missing_fields'].append((md_file.name, missing))
            else:
                print(f"  [OK] Valid YAML with {field_count} fields")

            # Show key fields
            print(f"       title: {metadata.get('title', 'N/A')}")
            print(f"       category: {metadata.get('category', 'N/A')}")
            print(f"       contact_emails: {metadata.get('contact_emails', 'N/A')}")

            stats['valid_yaml'] += 1

        except yaml.YAMLError as e:
            print(f"  [FAIL] YAML parsing error: {str(e)[:100]}")
            stats['invalid_yaml'] += 1

        print()

    # Summary
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total files:        {stats['total']}")
    print(f"Valid YAML:         {stats['valid_yaml']}")
    print(f"Invalid YAML:       {stats['invalid_yaml']}")
    print(f"No YAML:            {stats['no_yaml']}")
    print()

    if stats['missing_fields']:
        print(f"Files with missing required fields: {len(stats['missing_fields'])}")
        for filename, missing in stats['missing_fields']:
            print(f"  - {filename}: {', '.join(missing)}")
        print()

    if stats['valid_yaml'] == stats['total']:
        print("[SUCCESS] All files have valid YAML!")
    else:
        print(f"[WARNING] {stats['invalid_yaml'] + stats['no_yaml']} files need attention")

    print()


if __name__ == "__main__":
    validate_all_files()
