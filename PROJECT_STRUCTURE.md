# Municipality RAG - Project Structure

## Directory Layout

```
municipality-rag/
│
├── README.md                          # Project overview and quick start
├── PROJECT_STRUCTURE.md               # This file - explains what everything does
├── general_guidelines.md              # High-level implementation guidelines
├── requirements.txt                   # Python dependencies
├── .env.example                       # Example environment variables
├── .env                              # Actual API keys (gitignored)
├── .gitignore                        # Git ignore file
│
├── config/                           # Configuration files
│   ├── responsibility_graph.yaml     # Master graph of all responsibilities
│   └── generation_config.yaml        # Settings for document generation
│
├── templates/                        # Document templates
│   ├── input_template.md             # Markdown template with instructions
│   ├── input_template.yaml           # YAML structured template
│   ├── input_template.json           # JSON structured template
│   └── input_example.md              # Full example (Building Permit)
│
├── data/                             # Generated and source data
│   ├── generated/                    # LLM-generated documents
│   │   ├── raw_yaml/                # Generated YAML files
│   │   └── markdown/                # Converted to markdown for RAG
│   ├── manual/                      # Manually created/edited documents
│   └── source/                      # Original documents (if converting existing)
│
├── scripts/                         # Python scripts
│   ├── generate_documents.py       # Main generation script (reads graph, calls LLM)
│   ├── validate_documents.py       # Validates generated docs against schema
│   ├── convert_to_markdown.py      # Converts YAML/JSON → Markdown
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── llm_client.py          # Ollama/OpenAI connection wrapper
│       ├── template_loader.py     # Load and parse templates
│       └── graph_parser.py        # Parse responsibility graph
│
├── rag_system/                     # RAG implementation
│   ├── indexing.py                # Index documents into vector DB
│   ├── query_system.py            # Query and retrieval
│   ├── app.py                     # Streamlit web UI (optional)
│   └── config.py                  # RAG system configuration
│
├── database/                       # Database files (gitignored)
│   ├── chroma_db/                 # ChromaDB vector database
│   └── municipal_knowledge.db     # SQLite metadata (if needed)
│
├── tests/                          # Test files
│   ├── test_generation.py         # Test document generation
│   ├── test_rag_retrieval.py      # Test RAG quality
│   ├── test_dependencies.py       # Test if dependencies work in RAG
│   └── test_queries.txt           # Sample queries for testing
│
├── notebooks/                      # Jupyter notebooks (optional)
│   ├── explore_data.ipynb         # Explore generated documents
│   └── test_rag.ipynb             # Interactive RAG testing
│
├── docs/                           # Documentation
│   ├── setup_guide.md             # How to set up the project
│   ├── generation_guide.md        # How to generate documents
│   └── rag_usage_guide.md         # How to use the RAG system
│
└── outputs/                        # Generated outputs and reports
    ├── logs/                      # Generation and indexing logs
    ├── reports/                   # Quality reports, statistics
    └── exports/                   # Exported data for sharing
```

---

## File Descriptions

### **Root Level Files**

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start guide, installation instructions |
| `PROJECT_STRUCTURE.md` | This file - navigation guide |
| `general_guidelines.md` | High-level POC guidelines and implementation approach |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for environment variables (API keys) |
| `.env` | Actual API keys (never commit!) |
| `.gitignore` | Files to exclude from git (API keys, databases, generated files) |

---

### **`config/` - Configuration Files**

| File | Purpose |
|------|---------|
| `responsibility_graph.yaml` | Master definition of 30 responsibilities with all relationships |
| `generation_config.yaml` | Settings for LLM generation (model, temperature, prompts) |

**Example `generation_config.yaml`:**
```yaml
llm:
  backend: "ollama"  # ollama/openai/anthropic
  model: "llama3.1"
  temperature: 0.7
  max_tokens: 4000

generation:
  output_format: "markdown"  # yaml/json/markdown
  batch_size: 5  # Generate 5 docs at a time

paths:
  template: "templates/input_template.yaml"
  graph: "config/responsibility_graph.yaml"
  output_dir: "data/generated/markdown"
```

---

### **`templates/` - Document Templates**

| File | Purpose |
|------|---------|
| `input_template.md` | Human-readable Markdown template with inline instructions |
| `input_template.yaml` | Machine-readable YAML structure |
| `input_template.json` | Machine-readable JSON structure |
| `input_example.md` | Fully filled example (Building Permit) for reference |

---

### **`data/` - All Document Data**

#### **`data/generated/`**
Generated documents from LLM

- **`raw_yaml/`** - Original YAML output from LLM
  - `res_permit_intake_001.yaml`
  - `res_building_permit_002.yaml`
  - etc.

- **`markdown/`** - Converted to Markdown for RAG indexing
  - `res_permit_intake_001.md`
  - `res_building_permit_002.md`
  - etc.

#### **`data/manual/`**
Manually created or edited documents (if you want to refine LLM output)

#### **`data/source/`**
Original documents if converting from existing municipal docs

---

### **`scripts/` - Python Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_documents.py` | Main script - generates all 30 docs from graph | `python scripts/generate_documents.py` |
| `validate_documents.py` | Validates generated docs have required fields | `python scripts/validate_documents.py` |
| `convert_to_markdown.py` | Converts YAML/JSON → Markdown | `python scripts/convert_to_markdown.py` |

#### **`scripts/utils/`** - Helper modules
- `llm_client.py` - Wrapper for Ollama/OpenAI/Anthropic
- `template_loader.py` - Load and parse template files
- `graph_parser.py` - Parse responsibility graph and dependencies

---

### **`rag_system/` - RAG Implementation**

| File | Purpose | Usage |
|------|---------|-------|
| `indexing.py` | Indexes markdown docs into ChromaDB | `python rag_system/indexing.py` |
| `query_system.py` | Query interface (CLI) | `python rag_system/query_system.py` |
| `app.py` | Streamlit web UI | `streamlit run rag_system/app.py` |
| `config.py` | RAG configuration (chunk size, embeddings, etc.) | - |

---

### **`database/` - Generated Databases**

| Directory | Purpose |
|-----------|---------|
| `chroma_db/` | ChromaDB vector database (auto-generated by indexing) |
| `municipal_knowledge.db` | SQLite for metadata (optional) |

**Note:** This directory is gitignored - databases are generated locally

---

### **`tests/` - Testing**

| File | Purpose |
|------|---------|
| `test_generation.py` | Tests document generation works |
| `test_rag_retrieval.py` | Tests RAG returns relevant documents |
| `test_dependencies.py` | Tests if dependency connections work in RAG |
| `test_queries.txt` | Sample test queries like "How do I process a permit?" |

---

### **`notebooks/` - Jupyter Notebooks (Optional)**

For interactive exploration and testing

| Notebook | Purpose |
|----------|---------|
| `explore_data.ipynb` | Browse generated documents, check quality |
| `test_rag.ipynb` | Interactive RAG testing with visualizations |

---

### **`docs/` - Documentation**

| File | Purpose |
|------|---------|
| `setup_guide.md` | Step-by-step setup instructions |
| `generation_guide.md` | How to generate documents |
| `rag_usage_guide.md` | How to use the RAG system |

---

### **`outputs/` - Generated Outputs**

| Directory | Purpose |
|-----------|---------|
| `logs/` | Generation logs, error logs, timing stats |
| `reports/` | Quality reports, statistics about generated docs |
| `exports/` | Exported datasets for sharing or backup |

---

## Typical Workflow

### **1. Initial Setup**
```bash
cd municipality-rag
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Generate Documents**
```bash
# Generate all 30 documents from graph
python scripts/generate_documents.py

# Output: data/generated/markdown/*.md (30 files)
```

### **3. Index Documents**
```bash
# Create vector database
python rag_system/indexing.py

# Output: database/chroma_db/
```

### **4. Query System**
```bash
# CLI interface
python rag_system/query_system.py

# OR Web UI
streamlit run rag_system/app.py
```

### **5. Test RAG Quality**
```bash
# Run automated tests
python tests/test_rag_retrieval.py
python tests/test_dependencies.py
```

---

## Key Design Decisions

### **Why separate `data/generated/raw_yaml/` and `data/generated/markdown/`?**
- Keep original LLM output (YAML) for debugging
- Markdown versions are optimized for RAG (with proper frontmatter)
- Can regenerate markdown without calling LLM again

### **Why `config/` separate from `templates/`?**
- `config/` - Runtime settings (can change frequently)
- `templates/` - Document structure (stable, version controlled)

### **Why `scripts/utils/` for helpers?**
- Keeps main scripts clean
- Reusable across different scripts
- Easier to test

### **Why separate `rag_system/` from `scripts/`?**
- `scripts/` - Data generation (one-time or periodic)
- `rag_system/` - Runtime system (always running)
- Clear separation of concerns

---

## What Gets Committed to Git?

### **✅ Commit:**
- All Python scripts
- Templates and examples
- Configuration files (except API keys)
- Documentation
- `.env.example` (template)
- Empty directory placeholders

### **❌ Don't Commit (gitignored):**
- `.env` (contains API keys)
- `data/generated/` (generated files)
- `database/` (vector databases)
- `outputs/logs/` (log files)
- `__pycache__/` (Python cache)
- `venv/` (virtual environment)
- `.ipynb_checkpoints/` (Jupyter)

---

## Next Steps

1. **Create directory structure** - Set up all folders
2. **Create requirements.txt** - List dependencies
3. **Create .gitignore** - Protect sensitive files
4. **Implement generation script** - Build the document generator
5. **Test with 2-3 docs** - Verify before full generation
6. **Generate all 30 docs** - Run full generation
7. **Build RAG system** - Implement indexing and querying
8. **Test RAG quality** - Verify dependency retrieval works

---

## Questions?

This structure is designed for:
- ✅ Clear organization
- ✅ Easy navigation
- ✅ Scalability (can add more responsibilities later)
- ✅ Clean separation of concerns
- ✅ Easy testing and debugging

Adjust as needed for your specific workflow!
