"""
Preprocessing Pipeline
Applies YAML fixes to all markdown files and saves to preprocessed directory
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.yaml_fixer import YAMLFixer


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "data/generated/markdown"
TARGET_DIR = PROJECT_ROOT / "data/preprocessed/markdown"


def preprocess_all_documents():
    """
    Apply YAML fixes to all markdown documents
    Save corrected versions to preprocessed directory
    """

    print("="*80)
    print("PREPROCESSING PIPELINE - YAML Correction")
    print("="*80)
    print()

    # Check source directory
    if not SOURCE_DIR.exists():
        print(f"[ERROR] Source directory not found: {SOURCE_DIR}")
        sys.exit(1)

    # Get all markdown files
    md_files = sorted(SOURCE_DIR.glob("*.md"))
    print(f"Found {len(md_files)} markdown files in: {SOURCE_DIR}")
    print()

    # Create target directory
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {TARGET_DIR}")
    print()

    # Initialize fixer
    fixer = YAMLFixer()

    # Statistics
    stats = {
        'total_files': len(md_files),
        'successful': 0,
        'failed': 0,
        'total_corrections': 0
    }

    # Process each file
    print("="*80)
    print("PROCESSING FILES")
    print("="*80)
    print()

    for md_file in md_files:
        print(f"Processing: {md_file.name}")

        try:
            # Read original
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Fix YAML
            fixed_content, corrections = fixer.fix_document(original_content)

            # Write to preprocessed directory
            target_file = TARGET_DIR / md_file.name
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            # Report
            print(f"  [OK] {len(corrections)} corrections applied")
            for correction in corrections:
                print(f"       - {correction}")

            stats['successful'] += 1
            stats['total_corrections'] += len(corrections)

        except Exception as e:
            print(f"  [FAIL] {e}")
            stats['failed'] += 1

        print()

    # Summary
    print("="*80)
    print("PREPROCESSING SUMMARY")
    print("="*80)
    print(f"Total files:        {stats['total_files']}")
    print(f"Successfully fixed: {stats['successful']}")
    print(f"Failed:             {stats['failed']}")
    print(f"Total corrections:  {stats['total_corrections']}")
    print(f"Average per file:   {stats['total_corrections'] / stats['total_files']:.1f}")
    print()
    print(f"Preprocessed files saved to: {TARGET_DIR}")
    print()


if __name__ == "__main__":
    preprocess_all_documents()
