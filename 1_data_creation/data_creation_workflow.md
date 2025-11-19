# Data Creation Workflow

Complete workflow for generating and iteratively improving Hebrew municipality documents.

---

## Process Flow

```
Step 1: Initial Generation
  ↓
Step 2: Structure Enforcement & Quality Analysis
  ↓
Step 3: Identify Low-Quality Files (<80% threshold)
  ↓
Step 4: Iterative Improvement
  ↓
Step 5: Re-run Enforcer on Improved Files
  ↓
Step 6: Repeat if needed (max 3 iterations)
```

---

## Step 1: Initial Document Generation

**Script**: `1_data_creation/scripts/generate_documents_hebrew.py` (graph-driven)

**Input**:
- `1_data_creation/config/responsibility_graph_hebrew.yaml` (single source of truth)
- `2_data_processing/templates/input_template_hebrew.md`

**How it works**:
- Reads graph YAML with document specifications (model, min_completeness per doc)
- Generates 3 documents per responsibility (one per model: mistral, qwen, aya)
- Filename format: `res_{responsibility}_{model}.md`

**Output**: `data/generated/markdown-hebrew-{model}/`

**Run**: `python 1_data_creation/scripts/generate_documents_hebrew.py`

**Example**: Responsibility `res_building_permit` generates:
- `res_building_permit_mistral.md` → `markdown-hebrew-mistral/`
- `res_building_permit_qwen.md` → `markdown-hebrew-qwen/`
- `res_building_permit_aya.md` → `markdown-hebrew-aya/`

---

## Step 2: Structure Enforcement

**Script**: `2_data_processing/scripts/enforce_structure.py`

**Input**: `data/generated/markdown-hebrew-{model}/`

**Output**:
- Structured files: `data/structured/hebrew/`
- Logs: `logs/structure_enforcement_{timestamp}.jsonl`

**Run**: `python 2_data_processing/scripts/enforce_structure.py`

**Metrics**:
- Completeness % (target: ≥80%)
- Hebrew % (target: ≥90%)
- Section status (yes/handled/no)

---

## Step 3: Review Enforcer Logs

Check `logs/structure_enforcement_{timestamp}_summary.txt` for files with:
- Completeness <80%
- Hebrew % <90%

---

## Step 4: Iterative Improvement

**Script**: `1_data_creation/scripts/iterative_generation.py`

**Input**:
- Enforcer logs: `logs/structure_enforcement_{timestamp}.jsonl`
- Structured files: `data/structured/hebrew/`
- `1_data_creation/config/creation_iteration_prompt.md`

**Output**: `data/generated/markdown-hebrew-{model}-improved/`

**Run**: `python 1_data_creation/scripts/iterative_generation.py`

---

## Step 5: Re-enforce Improved Files

Update `enforce_structure.py` configuration:
```python
SOURCE_SUBFOLDERS = ["markdown-hebrew-{model}-improved"]
```

Run enforcer again to validate improvements.

---

## Step 6: Iterate if Needed

If still <80% completeness: repeat Steps 4-5 (max 3 iterations)

---

## Quality Thresholds

| Metric | Threshold |
|--------|-----------|
| Completeness | ≥80% |
| Hebrew % | ≥90% |
| Sections | 15/15 |

---

## File Structure

```
1_data_creation/
├── config/
│   ├── responsibility_graph_hebrew.yaml       # SINGLE SOURCE OF TRUTH
│   │                                          # Defines responsibilities + documents + models
│   ├── prompt_for_data_generation.md         # Generation rules
│   └── creation_iteration_prompt.md          # Improvement rules
├── scripts/
│   ├── generate_documents_hebrew.py          # Graph-driven generator
│   └── iterative_generation.py               # Quality improvement
└── data_creation_workflow.md

data/generated/
├── markdown-hebrew-mistral/                  # Mistral-generated docs
├── markdown-hebrew-qwen/                     # Qwen-generated docs
├── markdown-hebrew-aya/                      # Aya-generated docs
├── markdown-hebrew-{model}-improved/         # After iteration
└── (files named: res_{responsibility}_{model}.md)

data/structured/hebrew/                       # Enforced structure
logs/                                         # Quality metrics
```
