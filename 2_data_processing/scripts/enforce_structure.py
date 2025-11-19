"""
Structure Enforcement Pipeline
Enforces template structure on all generated markdown files
Ensures all sections exist in template order, fills missing with placeholders
Includes quality metrics: Hebrew %, completeness, text quality
"""

import sys
import re
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Paths - Explicitly defined in main
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_FOLDER = "data/generated"
SOURCE_SUBFOLDERS = ["markdown-hebrew-claude", "markdown-hebrew-mistral", "markdown-hebrew-qwen", "markdown-hebrew-aya"]  # Input subfolders - all Hebrew model folders
TARGET_FOLDER = "data/structured"
TARGET_SUBFOLDER = "hebrew"  # Output subfolder - single folder for all structured files
TEMPLATE_PATH = "2_data_processing/templates/input_template_hebrew.md"


def calculate_hebrew_percentage(text: str) -> float:
    """Calculate percentage of Hebrew characters in text"""
    hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    total_chars = sum(1 for c in text if c.isalpha())
    return (hebrew_chars / total_chars * 100) if total_chars > 0 else 0.0


def calculate_text_quality_metrics(text: str) -> Dict[str, float]:
    """Calculate text quality metrics"""
    # Remove YAML frontmatter for metrics
    _, body = extract_yaml_frontmatter(text)

    # Word count (split by whitespace)
    words = body.split()
    word_count = len(words)

    # Sentence count (approximate - by periods, question marks, exclamation marks)
    sentences = re.split(r'[.!?]+', body)
    sentence_count = len([s for s in sentences if s.strip()])

    # Average sentence length
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

    # Character count (excluding whitespace)
    char_count = len(body.replace(' ', '').replace('\n', ''))

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_sentence_length': round(avg_sentence_length, 2),
        'char_count': char_count
    }


def calculate_completeness_score(sections: Dict[str, str], total_sections: int) -> Dict[str, float]:
    """Calculate completeness and connectivity metrics"""
    # Count filled sections (non-empty and not just placeholder)
    filled_sections = sum(
        1 for content in sections.values()
        if content.strip() and content.strip() != "[לא מולא]"
    )

    completeness_percentage = (filled_sections / total_sections * 100) if total_sections > 0 else 0

    # Cross-reference density: count section references (##)
    all_text = ' '.join(sections.values())
    cross_references = len(re.findall(r'##', all_text))

    # Content richness: average words per filled section
    total_words = sum(len(content.split()) for content in sections.values() if content.strip())
    avg_words_per_section = total_words / filled_sections if filled_sections > 0 else 0

    return {
        'filled_sections': filled_sections,
        'total_sections': total_sections,
        'completeness_percentage': round(completeness_percentage, 2),
        'cross_references': cross_references,
        'avg_words_per_section': round(avg_words_per_section, 2)
    }


def extract_yaml_frontmatter(content: str) -> Tuple[str, str]:
    """Extract YAML frontmatter and body from markdown content"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return "", content


def normalize_section_name(section_name: str) -> str:
    """Normalize section name by removing number prefixes and extra whitespace"""
    # Remove number prefixes like "1.", "2.", "10.", etc.
    normalized = re.sub(r'^\d+\.\s*', '', section_name.strip())
    return normalized


def extract_sections(body: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Extract all ## sections from markdown body
    Returns: (sections_with_normalized_names, original_names_map)
    """
    sections = {}
    original_names = {}  # maps normalized -> original

    # Split by ## headers
    parts = re.split(r'\n## ', body)

    for i, part in enumerate(parts):
        if i == 0 and not part.startswith('## '):
            # Skip anything before first section
            continue

        # Get section name (first line)
        lines = part.strip().split('\n', 1)
        original_section_name = lines[0].strip()
        section_content = lines[1] if len(lines) > 1 else ""

        # Normalize section name (remove numbers)
        normalized_name = normalize_section_name(original_section_name)

        sections[normalized_name] = section_content.strip()
        original_names[normalized_name] = original_section_name  # Track original

    return sections, original_names


def read_template_structure(template_path: Path) -> List[str]:
    """Read template and extract section names in order"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    _, body = extract_yaml_frontmatter(content)

    # Extract section names from template (## headers)
    section_names = []
    for line in body.split('\n'):
        if line.startswith('## '):
            section_name = line[3:].strip()
            # Skip first header if it's the title placeholder
            if not section_name.startswith('['):
                section_names.append(section_name)

    return section_names


def enforce_structure(content: str, template_sections: List[str]) -> Tuple[str, Dict]:
    """
    Enforce template structure on document content
    Returns: (structured_content, enforcement_report)
    """

    # Extract YAML and body
    yaml_front, body = extract_yaml_frontmatter(content)

    # Extract existing sections (normalized) and original names
    existing_sections, original_names = extract_sections(body)

    # Track what happened - with detailed section-level status
    enforcement_report = {
        'matched_sections': [],
        'missing_sections': [],
        'extra_sections': [],
        'discarded_content': [],
        'section_status': {},  # section_name -> "yes"/"no"/"handled"
        'original_names': original_names  # Store original section names for "handled" cases
    }

    # Rebuild document with EXACT template structure
    rebuilt_body_parts = []

    # Add title if exists
    title_match = re.search(r'^# (.+)$', body, re.MULTILINE)
    if title_match:
        rebuilt_body_parts.append(f"# {title_match.group(1)}")
        rebuilt_body_parts.append("")

    # Add each section in EXACT template order
    for section_name in template_sections:
        # Use EXACT template section name (no numbers)
        rebuilt_body_parts.append(f"## {section_name}")
        rebuilt_body_parts.append("")

        # Match with normalized existing sections
        if section_name in existing_sections and existing_sections[section_name].strip():
            # Section exists with content
            rebuilt_body_parts.append(existing_sections[section_name])
            enforcement_report['matched_sections'].append(section_name)

            # Determine if exact match or handled
            original_name = original_names.get(section_name, section_name)
            if original_name == section_name:
                enforcement_report['section_status'][section_name] = "yes"  # Exact match
            else:
                enforcement_report['section_status'][section_name] = "handled"  # Normalized match
        else:
            # Section missing or empty - add placeholder
            rebuilt_body_parts.append("[לא מולא]")
            enforcement_report['missing_sections'].append(section_name)
            enforcement_report['section_status'][section_name] = "no"  # Missing

        rebuilt_body_parts.append("")
        rebuilt_body_parts.append("---")
        rebuilt_body_parts.append("")

    # Find extra sections not in template
    for section_name in existing_sections:
        if section_name not in template_sections:
            enforcement_report['extra_sections'].append(section_name)
            enforcement_report['discarded_content'].append({
                'section': section_name,
                'content': existing_sections[section_name][:200]  # First 200 chars
            })

    rebuilt_body = '\n'.join(rebuilt_body_parts)

    # Reconstruct document with EXACT format
    if yaml_front:
        final_content = f"---\n{yaml_front}\n---\n\n{rebuilt_body}"
    else:
        final_content = rebuilt_body

    return final_content, enforcement_report


def enforce_structure_all():
    """
    Enforce template structure on all generated documents
    Save structured versions to output directory
    Collect quality metrics and save logs
    """

    print("="*80)
    print("STRUCTURE ENFORCEMENT PIPELINE")
    print("="*80)
    print()

    # Initialize logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"structure_enforcement_{timestamp}.jsonl"
    summary_file = log_dir / f"structure_enforcement_{timestamp}_summary.txt"

    all_file_metrics = []

    # Read template structure
    template_path = PROJECT_ROOT / TEMPLATE_PATH
    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return

    template_sections = read_template_structure(template_path)
    print(f"Template loaded: {len(template_sections)} sections")
    print()

    # Process each source subfolder
    for source_subfolder in SOURCE_SUBFOLDERS:
        SOURCE_DIR = PROJECT_ROOT / SOURCE_FOLDER / source_subfolder
        TARGET_DIR = PROJECT_ROOT / TARGET_FOLDER / TARGET_SUBFOLDER

        # Extract model name from subfolder (e.g., "markdown-hebrew-claude" -> "claude")
        model_name = source_subfolder.split('-')[-1] if '-' in source_subfolder else source_subfolder

        print()
        print("="*80)
        print(f"GENERATED BY MODEL: {model_name.upper()}")
        print("="*80)
        print(f"Source folder: {source_subfolder}")
        print(f"Source path: {SOURCE_DIR}")
        print(f"Target path: {TARGET_DIR}")
        print()

        # Check source directory
        if not SOURCE_DIR.exists():
            print(f"[ERROR] Source directory not found: {SOURCE_DIR}")
            continue

        # Get all markdown files
        md_files = sorted(SOURCE_DIR.glob("*.md"))
        print(f"Found {len(md_files)} markdown files")
        print()

        # Create target directory
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

        # Statistics
        stats = {
            'total_files': len(md_files),
            'successful': 0,
            'failed': 0,
            'avg_hebrew_percentage': 0.0,
            'avg_completeness': 0.0,
            'total_metrics': []
        }

        # Process each file
        print("="*80)
        print("ENFORCING STRUCTURE")
        print("="*80)
        print()

        for md_file in md_files:
            print(f"Processing: {md_file.name}")

            try:
                # Read original
                with open(md_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                # Calculate metrics on original
                hebrew_pct = calculate_hebrew_percentage(original_content)
                quality_metrics = calculate_text_quality_metrics(original_content)

                # Extract sections for completeness
                _, body = extract_yaml_frontmatter(original_content)
                existing_sections, _ = extract_sections(body)  # Unpack tuple, ignore original_names
                completeness = calculate_completeness_score(existing_sections, len(template_sections))

                # Enforce structure
                structured_content, enforcement_report = enforce_structure(original_content, template_sections)

                # Write to structured directory with model name in filename
                # Extract base filename without extension
                base_name = md_file.stem  # e.g., "res_building_permit_001"
                extension = md_file.suffix  # e.g., ".md"
                # Add model name: res_building_permit_001_claude.md
                target_filename = f"{base_name}_{model_name}{extension}"
                target_file = TARGET_DIR / target_filename

                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(structured_content)

                # Compile metrics
                file_metrics = {
                    'original_file': md_file.name,
                    'output_file': target_filename,
                    'model': model_name,
                    'subfolder': source_subfolder,
                    'timestamp': datetime.now().isoformat(),
                    'hebrew_percentage': round(hebrew_pct, 2),
                    'quality': quality_metrics,
                    'completeness': completeness,
                    'enforcement': enforcement_report,
                    'status': 'success'
                }

                # Log to file
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(file_metrics, ensure_ascii=False) + '\n')

                all_file_metrics.append(file_metrics)
                stats['total_metrics'].append(file_metrics)
                stats['avg_hebrew_percentage'] += hebrew_pct
                stats['avg_completeness'] += completeness['completeness_percentage']

                # Report
                print(f"  [OK] Structure enforced (template expects {len(template_sections)} sections)")
                print(f"       Hebrew %: {hebrew_pct:.1f}% (percentage of Hebrew characters)")
                print(f"       Completeness: {completeness['completeness_percentage']:.1f}% (filled sections before enforcement)")
                print(f"       Matched: {len(enforcement_report['matched_sections'])} (sections found matching template)")
                print(f"       Missing: {len(enforcement_report['missing_sections'])} (sections not found, filled with placeholder)")
                print(f"       Extra: {len(enforcement_report['extra_sections'])} (non-template sections discarded)")
                if enforcement_report['extra_sections']:
                    print(f"       → Discarded content logged for review")

                # Section-by-section breakdown
                print(f"\n       Section Status (all 15 template sections):")
                section_status = enforcement_report.get('section_status', {})
                original_names_map = enforcement_report.get('original_names', {})
                status_counts = {'yes': 0, 'handled': 0, 'no': 0}

                # Print each section with its status
                for i, section in enumerate(template_sections, 1):
                    status = section_status.get(section, 'no')
                    status_counts[status] += 1
                    status_symbol = "✓" if status == "yes" else ("~" if status == "handled" else "✗")
                    status_text = "YES" if status == "yes" else ("HANDLED" if status == "handled" else "NO")

                    # Try to print Hebrew section name, fallback to number if encoding fails
                    try:
                        base_text = f"         [{i:2d}] {status_symbol} {status_text:7s} - {section}"
                        # If handled, show original name
                        if status == "handled":
                            original = original_names_map.get(section, section)
                            base_text += f"    (was: \"{original}\")"
                        print(base_text)
                    except UnicodeEncodeError:
                        print(f"         [{i:2d}] {status_symbol} {status_text:7s} - [Section {i}]")

                print(f"\n       Summary:")
                print(f"         ✓ Exact matches: {status_counts['yes']}")
                print(f"         ~ Handled (normalized): {status_counts['handled']}")
                print(f"         ✗ Missing: {status_counts['no']}")

                # Additional sections (not in template)
                extra_sections = enforcement_report.get('extra_sections', [])
                if extra_sections:
                    print(f"\n       Additional Sections (not in template, discarded):")
                    for extra in extra_sections:
                        try:
                            print(f"         [+] {extra}")
                        except UnicodeEncodeError:
                            print(f"         [+] [Extra section]")

                stats['successful'] += 1

            except Exception as e:
                print(f"  [FAIL] {e}")

                # Log failure
                file_metrics = {
                    'original_file': md_file.name,
                    'model': model_name,
                    'subfolder': source_subfolder,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'failed',
                    'error': str(e)
                }
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(file_metrics, ensure_ascii=False) + '\n')

                stats['failed'] += 1

            print()

        # Calculate averages
        if stats['successful'] > 0:
            stats['avg_hebrew_percentage'] /= stats['successful']
            stats['avg_completeness'] /= stats['successful']

        # Summary for this subfolder
        print()
        print("="*80)
        print(f"SUMMARY - MODEL: {model_name.upper()}")
        print("="*80)
        print(f"Template sections: {len(template_sections)} (all output files have exactly this structure)")
        print(f"Total files:       {stats['total_files']}")
        print(f"Successfully done: {stats['successful']}")
        print(f"Failed:            {stats['failed']}")
        print()
        print(f"Quality Metrics (averaged across files):")
        print(f"  Avg Hebrew %:     {stats['avg_hebrew_percentage']:.1f}% (Hebrew character ratio)")
        print(f"  Avg Completeness: {stats['avg_completeness']:.1f}% (original fill rate)")
        print()
        print(f"Output files saved to: {TARGET_DIR}")
        print(f"Filename format: [original]_{model_name}.md")
        print(f"All files enforced to exact template structure")
        print("="*80)
        print()

    # Write summary log
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("STRUCTURE ENFORCEMENT SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Template: {TEMPLATE_PATH}\n")
        f.write(f"Expected sections: {len(template_sections)} (all outputs enforced to this)\n")
        f.write(f"Total files processed: {len(all_file_metrics)}\n\n")

        f.write("METRICS EXPLANATION:\n")
        f.write("-" * 80 + "\n")
        f.write("Hebrew %:      Percentage of Hebrew characters in text\n")
        f.write("Completeness:  Percentage of template sections filled in original\n")
        f.write("Matched:       Number of sections that matched template\n")
        f.write("Missing:       Number of sections not found (filled with placeholder)\n")
        f.write("Extra:         Number of non-template sections (discarded)\n\n")

        # Overall statistics
        successful = [m for m in all_file_metrics if m.get('status') == 'success']
        if successful:
            avg_hebrew = sum(m['hebrew_percentage'] for m in successful) / len(successful)
            avg_completeness = sum(m['completeness']['completeness_percentage'] for m in successful) / len(successful)

            f.write(f"Overall Hebrew %:    {avg_hebrew:.1f}%\n")
            f.write(f"Overall Completeness: {avg_completeness:.1f}%\n\n")

            # Per-file details grouped by model
            f.write("PER-FILE DETAILS (GROUPED BY MODEL):\n")
            f.write("=" * 80 + "\n\n")

            # Group by model
            by_model = {}
            for m in all_file_metrics:
                model = m.get('model', 'unknown')
                if model not in by_model:
                    by_model[model] = []
                by_model[model].append(m)

            # Write each model group
            for model, files in sorted(by_model.items()):
                f.write(f"\n{'='*80}\n")
                f.write(f"MODEL: {model.upper()}\n")
                f.write(f"{'='*80}\n")

                for m in files:
                    f.write(f"\nOriginal: {m.get('original_file', m.get('file', 'unknown'))}\n")
                    if m.get('status') == 'success':
                        f.write(f"Output:   {m.get('output_file', 'N/A')}\n")
                    f.write(f"  Hebrew %: {m['hebrew_percentage']:.1f}%\n")
                    f.write(f"  Completeness: {m['completeness']['completeness_percentage']:.1f}%\n")
                    f.write(f"  Words: {m['quality']['word_count']}\n")
                    f.write(f"  Original sections: {m['completeness']['filled_sections']}/{m['completeness']['total_sections']}\n")
                    if 'enforcement' in m:
                        f.write(f"  Enforcement:\n")
                        f.write(f"    - Matched: {len(m['enforcement']['matched_sections'])} sections\n")
                        f.write(f"    - Missing: {len(m['enforcement']['missing_sections'])} sections (now have placeholder)\n")
                        f.write(f"    - Extra: {len(m['enforcement']['extra_sections'])} sections (discarded)\n")
                        if m['enforcement']['extra_sections']:
                            f.write(f"    - Discarded section names:\n")
                            for extra in m['enforcement']['extra_sections'][:5]:  # Show first 5
                                f.write(f"        • {extra}\n")

                        # Add section-level status summary
                        section_status = m['enforcement'].get('section_status', {})
                        if section_status:
                            status_counts = {'yes': 0, 'handled': 0, 'no': 0}
                            for status in section_status.values():
                                status_counts[status] = status_counts.get(status, 0) + 1

                            # Detailed section breakdown - SAME AS CONSOLE OUTPUT
                            f.write(f"  Section Status (all 15 template sections):\n")
                            original_names_map = m['enforcement'].get('original_names', {})
                            for i, section_name in enumerate(template_sections, 1):
                                status = section_status.get(section_name, 'no')
                                status_symbol = "[✓]" if status == "yes" else ("[~]" if status == "handled" else "[✗]")
                                status_text = "YES" if status == "yes" else ("HANDLED" if status == "handled" else "NO")
                                base_text = f"    [{i:2d}] {status_symbol} {status_text:7s} - {section_name}"
                                # If handled, show original name
                                if status == "handled":
                                    original = original_names_map.get(section_name, section_name)
                                    base_text += f"    (was: \"{original}\")"
                                f.write(base_text + "\n")

                            f.write(f"\n  Summary:\n")
                            f.write(f"    - Exact matches (yes): {status_counts['yes']}\n")
                            f.write(f"    - Handled/normalized (handled): {status_counts['handled']}\n")
                            f.write(f"    - Missing (no): {status_counts['no']}\n")

                        # Additional sections (not in template)
                        extra_sections = m['enforcement'].get('extra_sections', [])
                        if extra_sections:
                            f.write(f"\n  Additional Sections (not in template, discarded):\n")
                            for extra in extra_sections:
                                f.write(f"    [+] {extra}\n")

                        # Add quality metrics details
                        quality = m.get('quality', {})
                        f.write(f"  Quality Metrics:\n")
                        f.write(f"    - Word count: {quality.get('word_count', 0)}\n")
                        f.write(f"    - Sentence count: {quality.get('sentence_count', 0)}\n")
                        f.write(f"    - Avg words/sentence: {quality.get('avg_words_per_sentence', 0):.1f}\n")

                        # Add timestamp and subfolder
                        f.write(f"  Metadata:\n")
                        f.write(f"    - Timestamp: {m.get('timestamp', 'N/A')}\n")
                        f.write(f"    - Source subfolder: {m.get('subfolder', 'N/A')}\n")
                else:
                    f.write(f"  Status: FAILED - {m.get('error', 'Unknown error')}\n")

    # Create CSV output with section-level detail
    csv_file = log_dir / f"structure_enforcement_{timestamp}_sections.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(['filename', 'model', 'section_title', 'status'])

        # Write rows for each file and section
        for metrics in all_file_metrics:
            if metrics.get('status') == 'success':
                filename = metrics.get('original_file', 'unknown')
                model = metrics.get('model', 'unknown')
                section_status = metrics.get('enforcement', {}).get('section_status', {})

                # Write one row per section
                for section, status in section_status.items():
                    writer.writerow([filename, model, section, status])

    print("="*80)
    print("LOGS SAVED")
    print("="*80)
    print(f"Detailed log: {log_file}")
    print(f"Summary log:  {summary_file}")
    print(f"Section CSV:  {csv_file}")
    print()


if __name__ == "__main__":
    enforce_structure_all()
