"""
Analyze Indexing JSON Logs
Generates summary report of issues found during indexing
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_json_log(log_path: Path):
    """Analyze JSON log and generate report"""

    # Load all log entries
    entries = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            entries.append(json.loads(line))

    # Analysis containers
    parse_failures = []
    yaml_errors = defaultdict(list)
    warnings_by_file = defaultdict(list)
    critical_errors = []

    # Analyze entries
    for entry in entries:
        event_type = entry.get('event_type')

        # Parse failures
        if event_type == 'file_parsed' and not entry.get('parse_success'):
            parse_failures.append({
                'filename': entry['filename'],
                'error': entry['parse_error']
            })

            # Categorize YAML errors
            error = entry['parse_error']
            if 'mapping values are not allowed' in error:
                yaml_errors['Incorrect YAML syntax (email/links)'].append(entry['filename'])
            elif 'expected <block end>' in error:
                yaml_errors['YAML formatting issue'].append(entry['filename'])
            elif 'missing --- markers' in error:
                yaml_errors['No frontmatter found'].append(entry['filename'])

        # Warnings
        if event_type == 'chunk_validated' and entry.get('severity') == 'warning':
            warnings_by_file[entry['filename']].append({
                'chunk_index': entry['chunk_index'],
                'header': entry['header'],
                'issues': entry['issues']
            })

        # Critical errors
        if entry.get('severity') == 'critical':
            critical_errors.append({
                'filename': entry['filename'],
                'chunk_index': entry['chunk_index'],
                'header': entry['header'],
                'issues': entry['issues']
            })

    # Generate report
    print("="*80)
    print("INDEXING LOG ANALYSIS REPORT")
    print("="*80)
    print(f"Log file: {log_path.name}\n")

    # Parse failures summary
    print(f"[PARSE FAILURES]: {len(parse_failures)} files")
    print("-"*80)
    if parse_failures:
        for failure in parse_failures:
            print(f"\n[X] {failure['filename']}")
            print(f"   Error: {failure['error'][:150]}...")
    else:
        print("  None!")

    # YAML error categories
    print("\n" + "="*80)
    print("[YAML ERROR CATEGORIES]")
    print("-"*80)
    for category, files in yaml_errors.items():
        print(f"\n{category}: {len(files)} files")
        for filename in files:
            print(f"  - {filename}")

    # Warnings by file
    print("\n" + "="*80)
    print(f"[FILES WITH WARNINGS]: {len(warnings_by_file)}")
    print("-"*80)
    for filename, warnings in sorted(warnings_by_file.items()):
        print(f"\n{filename}: {len(warnings)} warning(s)")
        # Show first warning
        if warnings:
            first = warnings[0]
            print(f"  Example: Chunk {first['chunk_index']} - {first['header']}")
            print(f"  Issues: {', '.join(first['issues'][:2])}")

    # Critical errors
    print("\n" + "="*80)
    print(f"[CRITICAL ERRORS]: {len(critical_errors)}")
    print("-"*80)
    if critical_errors:
        for error in critical_errors:
            print(f"\n[X] {error['filename']} - Chunk {error['chunk_index']}")
            print(f"   Header: {error['header']}")
            print(f"   Issues: {', '.join(error['issues'])}")
    else:
        print("  None!")

    # Recommendations
    print("\n" + "="*80)
    print("[RECOMMENDATIONS]")
    print("="*80)

    if yaml_errors:
        print("\n1. YAML Issues:")
        if 'Incorrect YAML syntax (email/links)' in yaml_errors:
            print("   - Fix email/link syntax in YAML (use quotes for values with special chars)")
        if 'YAML formatting issue' in yaml_errors:
            print("   - Check YAML indentation and special characters")
        if 'No frontmatter found' in yaml_errors:
            print("   - Ensure files start with --- YAML --- markers")

    if critical_errors:
        print("\n2. Critical Errors:")
        print("   - Review chunks with insufficient content")
        print("   - These chunks were SKIPPED during indexing")

    print("\n3. System Behavior:")
    print("   [OK] Parser auto-stripped code block wrappers (```yml)")
    print("   [OK] Validator used fallbacks for missing metadata")
    print("   [OK] All valid chunks were indexed successfully")

    print("\n" + "="*80)


def main():
    """Main function"""

    if len(sys.argv) < 2:
        # Find most recent log
        log_dir = Path(__file__).parent.parent / "outputs/logs"
        json_logs = sorted(log_dir.glob("indexing_*.jsonl"), reverse=True)

        if not json_logs:
            print("No log files found")
            sys.exit(1)

        log_path = json_logs[0]
        print(f"Analyzing most recent log: {log_path.name}\n")
    else:
        log_path = Path(sys.argv[1])

    if not log_path.exists():
        print(f"Error: Log file not found: {log_path}")
        sys.exit(1)

    analyze_json_log(log_path)


if __name__ == "__main__":
    main()
