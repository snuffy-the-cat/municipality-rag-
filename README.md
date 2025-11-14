# Municipality Knowledge Transfer System - RAG POC

A proof-of-concept RAG (Retrieval-Augmented Generation) system for capturing and querying municipal employee knowledge during transitions.

## 🎯 Project Goal

Build a system where departing municipal employees document their responsibilities in a structured format, and new employees can query this knowledge base using natural language questions.

## 📋 Features

- **Structured Documentation**: Standardized templates for capturing procedural knowledge
- **Dependency Tracking**: Links between related responsibilities and shared resources
- **Vector Search**: Semantic search using embeddings to find relevant information
- **LLM Synthesis**: Coherent answers with source attribution
- **30 Sample Documents**: Pre-generated municipal responsibilities for testing

## 🏗️ Architecture

```
Input Documents → Indexing → Vector DB → Semantic Search → LLM Synthesis → Answer
     (Markdown)    (Chunks)   (ChromaDB)   (Embeddings)      (Ollama/GPT)
```

## 📁 Project Structure

```
municipality-rag/
├── config/                  # Configuration files
│   └── responsibility_graph.yaml
├── templates/               # Document templates
├── data/                   # Generated documents
├── scripts/                # Generation scripts
├── rag_system/             # RAG implementation
├── database/               # Vector database
└── tests/                  # Test files
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed layout.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to project
cd municipality-rag

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama (Free Local LLM)

**Option A: Download from website**
- Visit: https://ollama.ai
- Download for your OS
- Install and run

**Option B: Command line**
```bash
# Mac/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Use installer from website
```

**Download a model:**
```bash
ollama pull llama3.1
```

### 3. Generate Documents

```bash
# Generate all 30 documents from the responsibility graph
python scripts/generate_documents.py

# Output: data/generated/markdown/*.md
```

### 4. Index Documents

```bash
# Create vector database
python rag_system/indexing.py

# Output: database/chroma_db/
```

### 5. Query the System

```bash
# CLI interface
python rag_system/query_system.py

# OR Web UI
streamlit run rag_system/app.py
```

## 💡 Example Queries

- "How do I process a building permit?"
- "Who do I contact about zoning issues?"
- "What systems do I need access to for permit intake?"
- "What happens if a permit application is incomplete?"
- "How are building permits and inspections connected?"

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test RAG retrieval quality
python tests/test_rag_retrieval.py

# Test dependency connections
python tests/test_dependencies.py
```

## 📊 Sample Data

The project includes 30 pre-defined responsibilities organized in 5 clusters:

1. **Permits Processing** (8 docs) - Building permits, inspections, certificates
2. **Business Licensing** (6 docs) - Business licenses, food trucks, events
3. **Code Enforcement** (8 docs) - Complaints, violations, public services
4. **Utilities** (4 docs) - Water, sewer, infrastructure
5. **Finance** (4 docs) - Fees, payments, accounting

Data completeness varies to test RAG robustness:
- 57% fully complete
- 30% partially complete (missing 1-2 sections)
- 13% minimally complete (basic info only)

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Optional: If using OpenAI instead of Ollama
OPENAI_API_KEY=your_key_here

# Optional: If using Anthropic Claude
ANTHROPIC_API_KEY=your_key_here
```

### Generation Settings

Edit `config/generation_config.yaml` to adjust:
- LLM backend (ollama/openai/anthropic)
- Model name
- Temperature
- Output format

## 📖 Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed project organization
- [general_guidelines.md](general_guidelines.md) - Implementation guidelines
- `docs/setup_guide.md` - Setup instructions (coming soon)
- `docs/generation_guide.md` - Document generation guide (coming soon)

## 🛠️ Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Embeddings | OpenAI text-embedding-3-small | High quality, low cost |
| Vector DB | ChromaDB | Simple, local, free |
| LLM | Ollama (Llama 3.1) | Free, private, local |
| Framework | LangChain | Standard RAG toolkit |
| UI | Streamlit | Quick web interface |
| Storage | Markdown + YAML | Human-readable, versionable |

## 💰 Cost Estimate

**Using Ollama (Recommended):**
- Generation: $0 (local)
- Indexing: $0 (local)
- Queries: $0 (local)
- **Total: FREE**

**Using OpenAI:**
- Generation: ~$1-2 (30 docs)
- Indexing: ~$0.01
- Queries: ~$0.07 each
- **Total: ~$2-5 for POC**

## 🎯 POC Success Criteria

- ✅ Generate 30 interconnected documents
- ✅ Index into vector database
- ✅ Answer natural language queries
- ✅ Retrieve related responsibilities
- ✅ Handle incomplete data gracefully
- ✅ Provide source attribution

## 🔮 Future Enhancements

- Document versioning and deprecation
- Conflict detection between documents
- User feedback collection
- Query analytics
- Role-based access control
- Integration with existing municipal systems

## 📝 License

[Add your license here]

## 🤝 Contributing

This is a POC project. Contributions and suggestions welcome!

## 📧 Contact

[Add contact information]

---

**Note:** This is a proof-of-concept system for testing RAG capabilities. Not production-ready.
