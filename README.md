# Municipality Knowledge Transfer System - RAG

A RAG (Retrieval-Augmented Generation) system for capturing and querying municipal employee knowledge during transitions.

---

## 🎯 Project Goal

Build a system where departing municipal employees document their responsibilities in a structured format, and new employees can query this knowledge base using natural language questions in Hebrew.

---

## 🏗️ System Architecture - 3 Stages

```
Stage 1: DATA CREATION
    Input files (.md) → Generated via LLM (POC) OR Real employee input (Production)
    ↓
Stage 2: DATA PROCESSING
    Raw .md → YAML fixes → Validation → Chunking → Vector DB
    ↓
Stage 3: DATA QUERYING
    User question → Semantic search → LLM synthesis → Answer with sources
```

---

## 📁 Project Structure

```
municipality-rag/
│
├── config/                          # Global configuration
│   └── models_config.yaml           # LLM model settings (all stages)
│
├── 1_data_creation/                 # STAGE 1: Create input data
│   ├── config/
│   │   ├── responsibility_graph.yaml          # English POC definitions
│   │   └── responsibility_graph_hebrew.yaml   # Hebrew POC definitions
│   └── scripts/
│       ├── generate_documents.py              # Generate English docs (POC)
│       └── generate_documents_hebrew.py       # Generate Hebrew docs (POC)
│
├── 2_data_processing/               # STAGE 2: Process data → Vector DB
│   ├── core/                        # Core processing modules
│   │   ├── parser.py                # Extract YAML + markdown
│   │   ├── yaml_fixer.py            # Fix broken YAML
│   │   ├── chunker.py               # Split by semantic sections
│   │   ├── validator.py             # Validate chunks
│   │   └── core.md                  # Module documentation
│   ├── scripts/                     # Processing pipeline scripts
│   │   ├── preprocessing.py         # Apply YAML fixes
│   │   ├── validate_preprocessed.py # Verify quality
│   │   ├── indexing.py              # Index to ChromaDB
│   │   └── scripts.md               # Script documentation
│   └── templates/                   # Validation templates
│       ├── input_template_english.md
│       └── input_template_hebrew.md
│
├── 3_data_querying/                 # STAGE 3: Query system
│   └── query_system.py              # Interactive Q&A
│
├── data/                            # Data storage
│   ├── raw/                         # Input .md files (before processing)
│   ├── processed/                   # YAML-fixed .md files (ready for indexing)
│   └── generated/                   # POC-generated files (temporary)
│
├── database/                        # Vector database
│   └── chroma/                      # ChromaDB storage
│
├── logs/                            # System logs
│   ├── indexing_*.log               # Text logs
│   └── indexing_*.jsonl             # Structured JSON logs
│
└── old/                             # One-time helpers (not continuous use)
```

---

## 🚀 Quick Start

### **Stage 1: Data Creation (POC)**

```bash
# Generate Hebrew documents using configured model
python 1_data_creation/scripts/generate_documents_hebrew.py

# Output: data/generated/markdown-hebrew/*.md
```

### **Stage 2: Data Processing**

```bash
# Step 1: Fix YAML in raw documents
python 2_data_processing/scripts/preprocessing.py
# Input:  data/raw/*.md
# Output: data/processed/*.md

# Step 2: Validate processed documents
python 2_data_processing/scripts/validate_preprocessed.py
# Input:  data/processed/*.md
# Output: Console report

# Step 3: Index to vector database
python 2_data_processing/scripts/indexing.py
# Input:  data/processed/*.md
# Output: database/chroma/
```

### **Stage 3: Querying**

```bash
# Interactive Q&A
python 3_data_querying/query_system.py
```

---

## 📊 Data Formats & Flow

| Stage | Input Format | Output Format | Location |
|-------|-------------|---------------|----------|
| **1. Creation** | responsibility_graph.yaml | .md with YAML frontmatter | data/generated/ |
| **2. Processing** | Raw .md files | ChromaDB vector database | database/chroma/ |
| **3. Querying** | User question (text) | Answer + sources (text) | Console/UI |

### **Data Flow:**

```
responsibility_graph_hebrew.yaml
    ↓
generate_documents_hebrew.py
    ↓
data/raw/*.md (raw input)
    ↓
preprocessing.py (YAML fixes via yaml_fixer.py)
    ↓
data/processed/*.md (clean YAML)
    ↓
validate_preprocessed.py (quality check)
    ↓
indexing.py (parser → chunker → validator → ChromaDB)
    ↓
database/chroma/ (vector DB)
    ↓
query_system.py
    ↓
User gets answer with sources
```

---

## 🔧 Configuration

### **Models Configuration** (`config/models_config.yaml`)

Choose which LLM model to use for Hebrew generation:

```yaml
active_model:
  hebrew: "qwen2.5:7b"  # Options: llama3.1, qwen2.5:7b, mistral-nemo, aya:8b
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Ollama (Qwen/Mistral/Aya) | Hebrew document generation |
| **Vector DB** | ChromaDB | Semantic search |
| **Embeddings** | ChromaDB default | Multilingual support |
| **Framework** | Custom pipeline | Modular processing |
| **Storage** | Markdown + YAML | Human-readable, versionable |

---

## 📖 Documentation

- **2_data_processing/core/core.md** - Core module documentation (input/output)
- **2_data_processing/scripts/scripts.md** - Processing scripts documentation
- **PROJECT_STRUCTURE.md** - Detailed project structure
- **STATUS.md** - Current status and roadmap

---

## 🎯 Current Status

- ✅ English system complete (30 documents)
- ✅ Hebrew models installed (Qwen, Mistral, Aya)
- 🔄 Hebrew model comparison in progress (3×5 documents)
- ⏳ Hebrew full system (15 documents) - pending
- ⏳ Production validation templates - pending

---

## 🔮 Production vs POC

### **POC (Current):**
- Documents generated by LLM from responsibility graphs
- Used for testing and development
- Located in `data/generated/`

### **Production (Future):**
- Real employee input via forms/templates
- Validated against templates in `2_data_processing/templates/`
- Stored in `data/raw/` → processed → indexed
- Same processing pipeline as POC

---

## 📝 License

[Add your license]

---

**Note:** This is a research system for Hebrew municipal knowledge transfer.
