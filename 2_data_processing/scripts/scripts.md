# Processing Scripts

This folder contains scripts that orchestrate the data processing pipeline in Stage 2.

---

## **preprocessing.py**

**Purpose**: Apply YAML fixes to all markdown files in batch

**Input**:
- Directory: `data/raw/` (raw .md files with potentially broken YAML)
- Format: .md files

**Process**:
1. Read each .md file
2. Apply `yaml_fixer.py` (core module)
3. Save fixed version to output directory

**Output**:
- Directory: `data/processed/` (YAML-corrected .md files)
- Format: .md files with valid YAML

**Related modules**:
- Uses: `yaml_fixer.py` (core)
- Next step: `validate_preprocessed.py`

**Run**: `python 2_data_processing/scripts/preprocessing.py`

---

## **validate_preprocessed.py**

**Purpose**: Verify all preprocessed files have valid YAML

**Input**:
- Directory: `data/processed/` (.md files after preprocessing)
- Format: .md files

**Process**:
1. Extract YAML from each file
2. Attempt to parse with `yaml.safe_load()`
3. Check required fields (title, category)
4. Report success/failures

**Output**:
- Console report showing:
  - Total files processed
  - Valid YAML count
  - Invalid YAML count
  - Missing required fields
- Format: Text summary (not saved to file)

**Related modules**:
- Follows: `preprocessing.py`
- Next step: `indexing.py`

**Run**: `python 2_data_processing/scripts/validate_preprocessed.py`

---

## **indexing.py**

**Purpose**: Main pipeline that indexes processed documents into ChromaDB

**Input**:
- Directory: `data/processed/` (validated .md files)
- Format: .md files with valid YAML

**Process**:
1. For each .md file:
   - `parser.py` → Extract metadata + content
   - `chunker.py` → Split into sections
   - `validator.py` → Validate each chunk
   - ChromaDB.add() → Index valid chunks
2. Log all operations to JSON and console

**Output**:
- ChromaDB vector database in `database/chroma/`
- Logs in `logs/` (JSON and text format)

**Related modules**:
- Uses: `parser.py`, `chunker.py`, `validator.py` (all core modules)
- Follows: `validate_preprocessed.py`
- Next step: Stage 3 (querying)

**Run**: `python 2_data_processing/scripts/indexing.py`

---

## **Processing Pipeline Flow**

```
data/raw/*.md (broken YAML, raw input)
    ↓
preprocessing.py (uses yaml_fixer.py)
    ↓
data/processed/*.md (fixed YAML)
    ↓
validate_preprocessed.py (verify quality)
    ↓
indexing.py (uses parser, chunker, validator)
    ↓
database/chroma/ (vector database)
```

---

## **Script Dependencies**

| Script | Uses Core Modules | Input Format | Output Format |
|--------|-------------------|--------------|---------------|
| preprocessing.py | yaml_fixer.py | .md (raw) | .md (fixed) |
| validate_preprocessed.py | None | .md (fixed) | Console report |
| indexing.py | parser.py, chunker.py, validator.py | .md (fixed) | ChromaDB database |
