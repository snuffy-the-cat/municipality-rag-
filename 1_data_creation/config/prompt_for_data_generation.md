# Prompt Instructions for Hebrew Document Generation

Generation rules and quality requirements for LLM document generation.

**Note**: The template structure (sections, order) is defined in `2_data_processing/templates/input_template_hebrew.md`. Generation scripts should load the template dynamically.

---

## Issues Discovered from Enforcement Analysis

Based on analysis of generated documents from 4 models (19 documents total):

**Structure violations:**
- Models adding number prefixes: "1. ממשקי עבודה" instead of "ממשקי עבודה"
- Models creating extra sections not in template (16-18 sections instead of 15)
- Models skipping required sections

**Content quality:**
- Hebrew percentage dropping below 90% (Qwen: 68.2%)
- Empty sections without placeholders
- Mixed language content

**Formatting:**
- Inconsistent section separators
- Missing YAML frontmatter
- Wrong header levels

---

## Generation Rules (for LLM Prompts)

### 1. Structure Compliance

**Section headers:**
```
✓ CORRECT:   ## ממשקי עבודה ואנשי קשר
✗ WRONG:     ## 1. ממשקי עבודה ואנשי קשר
✗ WRONG:     ### ממשקי עבודה ואנשי קשר
```

**Section separators:**
- After each section's content: empty line + `---` + empty line
- Example:
  ```markdown
  ## ממשקי עבודה ואנשי קשר

  [content]

  ---

  ## הדרכות, השתלמויות והכשרות
  ```

**Critical rules:**
- Use EXACTLY the section names from the template (character-for-character)
- Do NOT add number prefixes (1., 2., etc.)
- Do NOT skip sections - if not applicable, write `[לא רלוונטי לתפקיד זה]`
- Do NOT create additional sections beyond the template
- Do NOT change section order

### 2. Hebrew Quality

**Language requirements:**
- Write ONLY in Hebrew (עברית)
- Target: >95% Hebrew characters
- No English words except: proper nouns, technical terms with no Hebrew equivalent
- No mixed-language sentences

**If section not applicable:**
```
✓ CORRECT:   [לא רלוונטי לתפקיד זה]
✗ WRONG:     (leave empty)
✗ WRONG:     Not applicable
```

### 3. YAML Frontmatter

**Required format:**
```yaml
---
title: [Title in Hebrew]
category: [Category in Hebrew]
responsibility_type: [Type in Hebrew]
---
```

**Must be:**
- First thing in document
- Enclosed by `---` delimiters
- All values in Hebrew

### 4. Content Completeness

**Each section should include:**
- Minimum 2-3 sentences
- Specific details relevant to the responsibility
- Concrete examples when possible

**Avoid:**
- Generic/vague content
- Repetitive text across sections
- Copy-pasted boilerplate

---

## Prompt Template Structure

Generation scripts should build prompts like this:

```python
# 1. Load template from file
template_path = "2_data_processing/templates/input_template_hebrew.md"
with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()

# 2. Extract section names dynamically
sections = extract_sections_from_template(template_content)

# 3. Build prompt
prompt = f"""
You are generating a Hebrew document about: {responsibility_name}

TEMPLATE PROVIDED:
The exact template structure is shown below. You MUST follow this structure exactly.

{template_content}

CRITICAL RULES:
1. Use section headers EXACTLY as shown in the template (no numbers, no modifications)
2. Include ALL sections in the same order
3. Use "---" separators between sections
4. Write ONLY in Hebrew
5. If a section is not applicable, write: [לא רלוונטי לתפקיד זה]

WHAT NOT TO DO:
❌ Add numbers before headers (e.g., "1. ממשקי עבודה")
❌ Skip any sections
❌ Create additional sections
❌ Write in English
❌ Leave sections empty

Now generate the document with real content for: {responsibility_name}
Context: {context_info}
"""
```

---

## Model-Specific Adjustments

### Claude API
- Generally follows instructions well
- Emphasize: "Do NOT add number prefixes"
- May need reminder about Hebrew-only

### Mistral (Ollama)
- Poor structure adherence (16% completeness observed)
- Emphasize: "YOU MUST USE THE EXACT TEMPLATE STRUCTURE"
- Consider providing a good example
- May need stronger language in rules

### Qwen (Ollama)
- Poor Hebrew quality (68.2% observed)
- Emphasize: "WRITE ONLY IN HEBREW - עברית בלבד"
- Explicitly state: "No English words except proper nouns"

### Aya (Ollama)
- Better multilingual handling
- Generally good compliance
- Standard rules sufficient

---

## Validation After Generation

Scripts should validate generated documents:

```python
# Check structure
assert count_sections(doc) == len(template_sections)
assert all_sections_match_template(doc, template_sections)

# Check quality
assert calculate_hebrew_percentage(doc) > 90
assert no_empty_sections(doc)
assert has_yaml_frontmatter(doc)

# Check formatting
assert all_headers_level_2(doc)  # "##" not "###"
assert no_number_prefixes(doc)
assert proper_separators(doc)
```

---

## Implementation Example

```python
from pathlib import Path

def build_generation_prompt(responsibility_name, context, template_path):
    """Build prompt that references template, doesn't duplicate it"""

    # Load template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Extract just the section names for emphasis
    sections = extract_section_names(template)

    prompt = f"""
You are generating a Hebrew municipality responsibility document.

TEMPLATE:
{template}

The template above shows the EXACT structure you must follow.

RULES:
1. Section headers: Use EXACTLY as shown (e.g., "## ממשקי עבודה ואנשי קשר")
   - Do NOT add numbers: "## 1. ממשקי עבודה" is WRONG
2. Write ONLY in Hebrew (עברית)
3. Include ALL {len(sections)} sections
4. Use "---" separators between sections
5. If section not applicable: write "[לא רלוונטי לתפקיד זה]"

DO NOT:
- Add numbers to headers
- Skip sections
- Create extra sections
- Write in English
- Leave sections empty

Generate document for: {responsibility_name}
Context: {context}
"""

    return prompt
```

---

## Version History

- v1.0 (2025-01-19): Initial version based on enforcement analysis
  - Focuses on rules and quality, not structure
  - Template structure loaded dynamically from file
  - Avoids duplication of section definitions
