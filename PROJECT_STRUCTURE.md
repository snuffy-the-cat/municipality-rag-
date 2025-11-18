# Project Structure

Complete structure of the Municipality RAG system organized in 3 stages.

---

## 3-Stage Architecture

1. **Data Creation** - Generate/receive input documents
2. **Data Processing** - Process and index to vector DB  
3. **Data Querying** - Query knowledge base

---

## Directory Tree

```
municipality-rag/
├── config/models_config.yaml           # Global LLM settings
├── 1_data_creation/
│   ├── config/
│   │   ├── responsibility_graph.yaml
│   │   └── responsibility_graph_hebrew.yaml
│   └── scripts/
│       ├── generate_documents.py
│       └── generate_documents_hebrew.py
├── 2_data_processing/
│   ├── core/
│   │   ├── parser.py
│   │   ├── yaml_fixer.py
│   │   ├── chunker.py
│   │   ├── validator.py
│   │   └── core.md
│   ├── scripts/
│   │   ├── preprocessing.py
│   │   ├── validate_preprocessed.py
│   │   ├── indexing.py
│   │   └── scripts.md
│   └── templates/
│       ├── input_template_english.md
│       └── input_template_hebrew.md
├── 3_data_querying/
│   └── query_system.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── generated/
├── database/chroma/
├── logs/
└── old/
```

See README.md for detailed explanations.
