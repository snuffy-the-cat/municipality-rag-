"""
YAML Fixer Module
Extracts and flattens YAML metadata into searchable fields
"""

import re
import yaml
from typing import Dict, Tuple, List


class YAMLFixer:
    """
    Fixes YAML and extracts all data into flat, searchable fields

    Strategy:
    - Tier 1: Essential fields (title, category, priority)
    - Tier 2: Extract values from complex nested structures
    - All data becomes searchable (embedded in text + stored in metadata)
    """

    def __init__(self):
        self.corrections_made = []

    def fix_document(self, content: str) -> Tuple[str, List[str]]:
        """
        Fix and flatten YAML in markdown document

        Returns: (fixed_content, corrections_list)
        """
        self.corrections_made = []

        # Extract YAML region
        yaml_text, body, has_yaml = self._extract_yaml_region(content)

        if not has_yaml:
            return content, ["No YAML frontmatter found"]

        # Clean YAML text
        cleaned_yaml = self._clean_yaml_text(yaml_text)

        # Try to parse
        parsed_data = self._safe_parse_yaml(cleaned_yaml)

        # Extract and flatten to simple fields
        flat_metadata = self._extract_all_fields(parsed_data, yaml_text)

        # Serialize to clean YAML
        clean_yaml = yaml.dump(flat_metadata, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Reconstruct
        fixed_content = f"---\n{clean_yaml}---\n\n{body}"

        return fixed_content, self.corrections_made

    def _extract_yaml_region(self, content: str) -> Tuple[str, str, bool]:
        """Extract YAML, handling code blocks and missing markers"""

        # Remove code block wrapper
        if content.startswith('```yml') or content.startswith('```yaml'):
            content = re.sub(r'^```ya?ml\s*\n', '', content)
            content = re.sub(r'\n```\s*\n', '\n', content, count=1)
            self.corrections_made.append("Removed code block wrapper")

        # Try standard
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if match:
            return match.group(1), match.group(2), True

        # Try missing closing
        match = re.match(r'^---\s*\n(.*?)\n(#.*)$', content, re.DOTALL)
        if match:
            self.corrections_made.append("Added missing closing ---")
            return match.group(1), match.group(2), True

        return "", content, False

    def _clean_yaml_text(self, yaml_text: str) -> str:
        """Apply text-level corrections"""

        # Quote emails
        yaml_text = re.sub(
            r'(\s+email:\s+)([^\s"\']+@[^\s"\']+)',
            lambda m: f'{m.group(1)}"{m.group(2)}"',
            yaml_text
        )

        # Quote URLs
        yaml_text = re.sub(
            r'(\s+url:\s+)(https?://[^\s"\']+)',
            lambda m: f'{m.group(1)}"{m.group(2)}"',
            yaml_text
        )

        # Remove Markdown links [text](url) → "text"
        yaml_text = re.sub(
            r'\[([^\]]+)\]\([^\)]+\)',
            lambda m: f'"{m.group(1)}"',
            yaml_text
        )

        return yaml_text

    def _safe_parse_yaml(self, yaml_text: str) -> Dict:
        """Try to parse YAML, return empty dict if fails"""

        try:
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                return parsed
        except:
            self.corrections_made.append("YAML parsing failed, extracting with regex")

        return {}

    def _extract_all_fields(self, parsed: Dict, raw_yaml: str) -> Dict:
        """
        Extract all useful data into flat fields

        Tier 1: Essential
        Tier 2: Extracted from nested structures
        """

        flat = {}

        # Tier 1: Essential fields (try parsed first, then regex fallback)
        flat['title'] = self._get_field(parsed, raw_yaml, 'title', '')
        flat['category'] = self._get_field(parsed, raw_yaml, 'category', '')
        flat['subcategory'] = self._get_field(parsed, raw_yaml, 'subcategory', '')
        flat['priority'] = self._get_field(parsed, raw_yaml, 'priority', '')
        flat['frequency'] = self._get_field(parsed, raw_yaml, 'frequency', '')
        flat['cluster'] = self._get_field(parsed, raw_yaml, 'cluster', '')

        # Tier 2: Extract from nested structures
        flat['contact_names'] = self._extract_contact_names(parsed, raw_yaml)
        flat['contact_emails'] = self._extract_contact_emails(raw_yaml)
        flat['system_names'] = self._extract_system_names(parsed, raw_yaml)
        flat['related_doc_ids'] = self._extract_related_docs(parsed, raw_yaml)

        return flat

    def _get_field(self, parsed: Dict, raw_yaml: str, field: str, default: str) -> str:
        """Get field from parsed dict or extract with regex"""

        # Try parsed dict first
        if field in parsed:
            return str(parsed[field])

        # Try nested in responsibility_details
        if 'responsibility_details' in parsed:
            details = parsed['responsibility_details']
            if isinstance(details, dict) and field in details:
                return str(details[field])

        # Fallback: regex extraction from raw YAML (handles both top-level and indented)
        # Try top-level first
        pattern = rf'^{field}:\s*(.+)$'
        match = re.search(pattern, raw_yaml, re.MULTILINE)
        if match:
            value = match.group(1).strip().strip('"\'')
            self.corrections_made.append(f"Extracted '{field}' via regex")
            return value

        # Try indented (under responsibility_details or other sections)
        pattern = rf'^\s+{field}:\s*(.+)$'
        match = re.search(pattern, raw_yaml, re.MULTILINE)
        if match:
            value = match.group(1).strip().strip('"\'')
            self.corrections_made.append(f"Extracted '{field}' via regex (indented)")
            return value

        return default

    def _extract_contact_names(self, parsed: Dict, raw_yaml: str) -> str:
        """Extract all contact names from nested structures"""

        names = []

        # Try to find in parsed structure
        if 'shared_resources_in_this_cluster' in parsed:
            resources = parsed['shared_resources_in_this_cluster']
            if isinstance(resources, dict) and 'contacts' in resources:
                contacts = resources['contacts']
                if isinstance(contacts, list):
                    for contact in contacts:
                        if isinstance(contact, str):
                            names.append(contact.split('(')[0].strip())
                        elif isinstance(contact, dict) and 'name' in contact:
                            names.append(contact['name'])

        # Fallback: regex to find name patterns
        if not names:
            # Pattern: "John Doe (Role)" or just "John Doe"
            name_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
            found_names = re.findall(name_pattern, raw_yaml)
            names = list(set(found_names))[:5]  # Limit to 5 unique names

        return ', '.join(names) if names else ''

    def _extract_contact_emails(self, raw_yaml: str) -> str:
        """Extract all email addresses"""

        # Find all email patterns
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_yaml)
        return ', '.join(set(emails))  # Unique emails

    def _extract_system_names(self, parsed: Dict, raw_yaml: str) -> str:
        """Extract system names"""

        systems = []

        # Common system name patterns (CamelCase or capitalized)
        system_patterns = [
            r'([A-Z][a-z]+(?:[A-Z][a-z]+)+)',  # CamelCase: PermitTrack
            r'([A-Z]{2,})',  # All caps: BH
        ]

        for pattern in system_patterns:
            found = re.findall(pattern, raw_yaml)
            systems.extend(found)

        # Filter out common words
        exclude = {'None', 'Step', 'Section', 'Overview', 'Title', 'Code', 'High', 'Low'}
        systems = [s for s in set(systems) if s not in exclude]

        return ', '.join(systems[:10]) if systems else ''  # Limit to 10

    def _extract_related_docs(self, parsed: Dict, raw_yaml: str) -> str:
        """Extract related document IDs (res_*)"""

        # Find all res_* patterns
        doc_ids = re.findall(r'(res_[a-z_]+_\d{3})', raw_yaml)
        return ', '.join(set(doc_ids))  # Unique IDs


def main():
    """Test fixer"""
    import sys
    from pathlib import Path

    filepath = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not filepath or not filepath.exists():
        print("Usage: python yaml_fixer.py <file.md>")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fixer = YAMLFixer()
    fixed, corrections = fixer.fix_document(content)

    print(f"Corrections: {len(corrections)}")
    for c in corrections:
        print(f"  - {c}")

    # Show fixed YAML
    match = re.match(r'^---\n(.*?)\n---', fixed, re.DOTALL)
    if match:
        print("\nFixed YAML:")
        print(match.group(1))

        # Validate
        try:
            parsed = yaml.safe_load(match.group(1))
            print("\n[OK] YAML parses successfully!")
            print(f"Fields: {len(parsed)}")
            for k, v in parsed.items():
                print(f"  {k}: {v[:80] if isinstance(v, str) and len(v) > 80 else v}")
        except Exception as e:
            print(f"\n[FAIL] {e}")


if __name__ == "__main__":
    main()
