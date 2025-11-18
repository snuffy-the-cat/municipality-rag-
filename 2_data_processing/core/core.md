# Core Processing Modules

This folder contains the core processing modules used in Stage 2 (Data Processing).

---

## **parser.py**

**Purpose**: Extract YAML metadata and markdown content from files

**Input**:
- File path to .md file with YAML frontmatter
- Format:
```markdown
---
title: "Building Manager"
category: "Infrastructure"
---
# Content here
```

**Output**:
- `ParsedDocument` object containing:
  - `metadata`: dict (YAML fields)
  - `content`: str (markdown body)
  - `parse_success`: bool
  - `parse_error`: str or None

**Used by**:
- `indexing.py` (scripts folder)

---

## **yaml_fixer.py**

**Purpose**: Fix broken YAML in markdown files

**Input**:
- Markdown file content as string (may have invalid YAML)

**Output**:
- Fixed markdown content (valid YAML)
- List of corrections applied

**Common fixes**:
- Quote emails/URLs with special characters
- Strip code block wrappers (```yml)
- Add missing closing ---
- Flatten nested structures

**Used by**:
- `preprocessing.py` (scripts folder)

---

## **chunker.py**

**Purpose**: Split markdown content into semantic sections by headers

**Input**:
- Markdown content (string)
- Default header name (optional)

**Output**:
- List of `Chunk` objects:
  - `header`: str (section header)
  - `content`: str (section text)
  - `chunk_index`: int
  - `chunk_type`: str

**Used by**:
- `indexing.py` (scripts folder)

---

## **validator.py**

**Purpose**: Validate chunks before indexing, enrich metadata with fallbacks

**Input**:
- `Chunk` object
- `ParsedDocument` object

**Output**:
- `ValidationResult`:
  - `is_valid`: bool
  - `severity`: str ('info', 'warning', 'critical')
  - `issues`: list of strings
  - `enriched_metadata`: dict (filled with defaults)

**Validation checks**:
- YAML parsed correctly
- Chunk has sufficient content (>10 chars)
- Required metadata fields present
- Fills missing fields with defaults

**Used by**:
- `indexing.py` (scripts folder)

---

## **Data Flow Through Core Modules**

```
Raw .md file
    ↓
parser.py → ParsedDocument (metadata + content)
    ↓
chunker.py → List of Chunks (sections)
    ↓
validator.py → ValidationResult for each chunk
    ↓
Valid chunks → Ready for ChromaDB indexing
```
