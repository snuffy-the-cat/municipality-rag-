# Municipal Knowledge Transfer System - RAG Implementation Guidelines

> **IMPORTANT NOTE FOR FUTURE IMPLEMENTATIONS:**
> This document contains general guidelines and a suggested approach for building this POC.
> These are NOT rigid requirements. As you work through implementation, feel free to:
> - Adjust the technical stack based on what works best
> - Modify the architecture if you find better approaches
> - Change time estimates based on actual progress
> - Skip or add steps as needed
> - Iterate on the document template structure
> - Use different tools/libraries if they're more suitable
>
> **Treat this as a roadmap, not a rulebook.** The goal is a working POC, not perfect adherence to this plan.

---

## Project Overview

**Goal:** Build a RAG-based system where departing municipal employees document their responsibilities, and new employees can query this knowledge base using natural language.

### Core Value Proposition

1. Departing employees create structured departure documents
2. System indexes and embeds this knowledge
3. New employees ask questions naturally ("How do I process a building permit?")
4. System retrieves relevant information and synthesizes answers with source attribution

### Architecture Summary

```
INPUT → INDEXING → STORAGE → RETRIEVAL → SYNTHESIS → OUTPUT
  ↓         ↓          ↓          ↓           ↓         ↓
Markdown   Chunk   Vector DB   Semantic   LLM      Structured
Docs     + Embed   + SQL DB    Search   Response   Answer
```

### Two AI Components

1. **Embedding Model** (OpenAI text-embedding-3-small): Converts text to vectors for semantic search
2. **LLM** (GPT-4/Claude): Synthesizes retrieved chunks into coherent answers

---

## Phase 1: Input Document Design

### 1.1 Create Structured Template

File: `departure_document_template.md`

```markdown
---
metadata:
  responsibility_id: "building_permit_processing"
  category: "Permits & Licensing"
  department: "Planning & Development"
  documented_by:
    name: "John Smith"
    email: "john.smith@municipality.gov"
    role: "Senior Permit Coordinator"
    departure_date: "2024-01-15"
  version: 1
  status: "active"
  document_type: "departure_documentation"
  key_contacts:
    - name: "Sarah Chen"
      role: "Zoning Manager"
      email: "sarah.chen@municipality.gov"
      phone: "555-0123"
      when_to_contact: "For zoning interpretation questions"
  systems:
    - name: "PermitTrack"
      url: "https://internal.municipality.gov/permittrack"
      description: "Primary permit processing system"
      login_info: "Use municipal SSO"
  documents:
    - title: "Permit Application Form"
      url: "https://docs.municipality.gov/forms/permit-app"
      description: "Standard residential permit application"
---

# [Responsibility Name]

## Overview
**What is this responsibility?**
[2-3 sentence description]

**Why does it matter?**
[Impact and importance]

**When does this happen?**
[Frequency, triggers, deadlines]

## Step-by-Step Procedure

### Step 1: [Action Name]
[Detailed description of what to do]

**Tools needed**: [System names]
**Common issues**: [What can go wrong]
**Tips**: [Helpful shortcuts or context]

### Step 2: [Next Action]
[Continue...]

## Decision Points

**If [condition occurs]:**
- Then: [action to take]
- Contact: [relevant person]

## Troubleshooting

**Problem**: [Common issue]
- **Symptoms**: [How to recognize it]
- **Solution**: [How to resolve]
- **Escalation**: [When/who to contact if unsolved]

## Resources & References
- [Document name]: [Link and description]
- [System name]: [Link and description]

## Tips & Tribal Knowledge
[Unwritten rules, shortcuts, context that helps]
```

**Key Design Principles:**
- ✅ Clear section headers (enables semantic chunking)
- ✅ Self-contained sections (each can stand alone)
- ✅ Rich metadata (enables filtering and attribution)
- ✅ Structured format (consistent across all docs)

---

## Phase 2: Generate Training Data

### 2.1 Create Sample Documents (20-30 minimum for demo)

**Recommended Responsibilities to Document:**
1. Building permit processing (residential)
2. Building permit processing (commercial)
3. Noise complaint handling
4. Business license renewal
5. Zoning variance requests
6. Tree removal permits
7. Block party permit approval
8. Fire inspection scheduling
9. Property tax assessment appeals
10. Sidewalk repair requests
11. Dog license registration
12. Food truck permits
13. Special event permits
14. Parking ticket appeals
15. Water/sewer connection applications
16. Demolition permits
17. Sign permits
18. Home occupation permits
19. Fence permit processing
20. Pool permit applications

**Generation Method:**
```
Option A: Use Claude/GPT to generate synthetic documents
- Prompt: "Generate a realistic departure document using the template for [responsibility]"
- Takes ~2 minutes per document
- Estimate: ~1-2 hours for 20-30 documents

Option B: Mix real + synthetic
- Find 2-3 real municipal procedures online
- Reformat into template
- Generate variations using Claude
```

### 2.2 File Organization

```
project/
├── departure_docs/           # Raw markdown files
│   ├── john_smith_permits.md
│   ├── mary_jones_licenses.md
│   └── ...
├── chroma_db/               # Vector database (generated)
└── municipal_knowledge.db   # SQLite database (generated)
```

---

## Phase 3: Indexing & Storage Setup

### 3.1 Install Dependencies

```bash
pip install openai chromadb langchain langchain-community langchain-openai python-dotenv pyyaml
```

### 3.2 Indexing Script

File: `indexing.py`

```python
import os
import yaml
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader

DOCS_DIR = "./departure_docs"
CHROMA_DB_DIR = "./chroma_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def parse_document_with_metadata(file_path):
    """Extract YAML metadata and content"""
    with open(file_path, 'r') as f:
        content = f.read()

    if content.startswith('---'):
        parts = content.split('---', 2)
        metadata = yaml.safe_load(parts[1])
        main_content = parts[2]
    else:
        metadata = {}
        main_content = content

    metadata['source'] = str(file_path)
    return metadata, main_content

def create_chunks_with_metadata(file_path, text_splitter):
    """Create chunks preserving metadata"""
    metadata, content = parse_document_with_metadata(file_path)

    chunks = text_splitter.create_documents(
        texts=[content],
        metadatas=[metadata]
    )

    for i, chunk in enumerate(chunks):
        chunk.metadata['chunk_index'] = i
        chunk.metadata.update(metadata)

    return chunks

def main():
    print("=== Starting Indexing ===")

    # Initialize text splitter (semantic chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )

    # Process all documents
    all_chunks = []
    for doc_file in Path(DOCS_DIR).glob("*.md"):
        print(f"Processing: {doc_file.name}")
        chunks = create_chunks_with_metadata(doc_file, text_splitter)
        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks from {len(list(Path(DOCS_DIR).glob('*.md')))} documents")

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )

    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
        collection_name="municipal_knowledge"
    )

    print(f"✅ Indexing complete! Vector DB saved to {CHROMA_DB_DIR}")
    print(f"Cost estimate: ~$0.001-0.01 for {len(all_chunks)} chunks")

if __name__ == "__main__":
    main()
```

**What This Does:**
1. Reads all `.md` files from `departure_docs/`
2. Extracts YAML metadata from each
3. Chunks content by headers (semantic boundaries)
4. Generates embeddings for each chunk (API call to OpenAI)
5. Stores in Chroma vector database with metadata

**Cost:** ~$0.001-0.01 for 20-30 documents

---

## Phase 4: Query & Retrieval System

### 4.1 Query Script

File: `query_system.py`

```python
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

CHROMA_DB_DIR = "./chroma_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_vectorstore():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )

    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name="municipal_knowledge"
    )
    return vectorstore

def create_qa_chain(vectorstore):
    prompt_template = """You are a municipal knowledge assistant for new employees.
Use the context to answer the question. Each context chunk has metadata with contact info, systems, and documents.

Context documents:
{context}

Question: {question}

Instructions:
1. Provide a clear, actionable answer
2. Include step-by-step procedures if applicable
3. **Always include a "Key Contacts" section** with name, role, email, when to contact
4. **Always include a "Systems & Tools" section** with system names and URLs
5. **Always include a "Related Documents" section** with document titles and links
6. **Always include source attribution** showing who documented this (name, role, date)
7. If information conflicts between sources, note the conflict and recommend the most recent
8. If information is incomplete, explicitly state what's missing

Format with clear headers and markdown.

Answer:"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # or "gpt-4" for better quality
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 5}  # Retrieve top 5 chunks
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain

def query(question, qa_chain):
    result = qa_chain({"query": question})

    print("\n" + "="*80)
    print(f"QUESTION: {question}")
    print("="*80)
    print(f"\n{result['result']}")
    print("\n" + "-"*80)
    print("SOURCE CHUNKS:")
    for i, doc in enumerate(result['source_documents'], 1):
        print(f"\n[{i}] {doc.metadata.get('source', 'Unknown')}")
        print(f"    Author: {doc.metadata.get('documented_by', {}).get('name', 'N/A')}")
        print(f"    Date: {doc.metadata.get('documented_by', {}).get('departure_date', 'N/A')}")
    print("="*80 + "\n")

    return result

def interactive_mode():
    print("Loading system...")
    vectorstore = load_vectorstore()
    qa_chain = create_qa_chain(vectorstore)

    print("\n" + "="*80)
    print("Municipal Knowledge Assistant Ready!")
    print("Type 'quit' to exit")
    print("="*80 + "\n")

    while True:
        question = input("Your question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        if question:
            query(question, qa_chain)

if __name__ == "__main__":
    interactive_mode()
```

**What This Does:**
1. User asks question in natural language
2. Query converted to embedding (automatic)
3. Vector DB returns 5 most similar chunks
4. Chunks + metadata sent to GPT-3.5/GPT-4
5. LLM synthesizes answer with contacts, systems, sources
6. Displays structured response

**Cost per query:** ~$0.07-0.30

---

## Phase 5: Simple Web UI (Optional)

File: `app.py`

```python
import streamlit as st
from query_system import load_vectorstore, create_qa_chain

st.set_page_config(page_title="Municipal Knowledge Assistant", page_icon="🏛️")

@st.cache_resource
def init_system():
    vectorstore = load_vectorstore()
    qa_chain = create_qa_chain(vectorstore)
    return qa_chain

st.title("🏛️ Municipal Knowledge Assistant")
st.markdown("Ask questions about your new responsibilities")

qa_chain = init_system()

question = st.text_input("Your question:", placeholder="How do I process a building permit?")

if st.button("Ask") and question:
    with st.spinner("Searching knowledge base..."):
        result = qa_chain({"query": question})

        st.markdown("### Answer")
        st.write(result['result'])

        st.markdown("### Sources")
        for i, doc in enumerate(result['source_documents'], 1):
            with st.expander(f"Source {i}: {doc.metadata.get('source', 'Unknown')}"):
                st.text(doc.page_content)
                st.json(doc.metadata.get('documented_by', {}))
```

**Run:** `streamlit run app.py`

---

## Key Issues & Solutions

### Issue 1: Multiple Versions of Same Role

**Problem:** 3 people document "Building Permit Coordinator" over 3 years

**Solution:**
```python
# Add to metadata
metadata:
  version: 3
  effective_date: "2024-01-15"
  replaces_document: "previous_person_2023.md"
  status: "active"  # vs "superseded"

# Retrieval with recency boost
def retrieve_with_recency(query):
    results = vectorstore.similarity_search(query, k=20)
    # Boost recent docs, filter out "superseded" status
    return rerank_by_date(results)[:5]
```

**LLM Prompt Addition:**
```
"If multiple documents cover the same topic, ALWAYS prefer the most recent.
Note when procedures have changed over time."
```

### Issue 2: Contradictory Information

**Problem:** John says "contact fire marshal always", Mary says "only for buildings >5000 sq ft"

**Solution:**
```python
# Conflict detection prompt
conflict_detection_prompt = """
Analyze these retrieved chunks for contradictions.
If found, identify:
- What contradicts
- Which documents (with dates)
- Recommend following most recent guidance
"""

# LLM will output
"⚠️ Conflicting information detected:
- John (2022): Always contact fire marshal
- Mary (2023): Only for >5000 sq ft buildings
Recommendation: Follow Mary's guidance (more recent)"
```

### Issue 3: Poor Document Quality

**Problem:** Later documents don't follow template structure

**Solution:**
```python
def validate_document(doc_path):
    """Quality gate before indexing"""
    checks = {
        'has_metadata': check_yaml_frontmatter(doc),
        'has_headers': count_headers(doc) >= 3,
        'min_length': len(doc) > 500,
        'has_procedures': 'step' in doc.lower(),
    }

    score = sum(checks.values()) / len(checks)

    if score < 0.6:
        return False, "Document rejected - doesn't meet quality standards"
    return True, "OK"
```

### Issue 4: Off-Topic Documents

**Problem:** "Best lunch spots" document gets indexed alongside official procedures

**Solution:**
```python
# Document classification
metadata:
  document_type: "departure_documentation"  # vs "tips", "misc"
  scope: "role_responsibilities"  # vs "general_info"

# Filter at query time
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {
            "document_type": "departure_documentation",
            "status": "active"
        }
    }
)
```

### Issue 5: Outdated Information

**Problem:** 2-year-old document still marked "active"

**Solution:**
```python
# Periodic audit script
def flag_old_documents():
    old_docs = db.query("""
        SELECT * FROM documents
        WHERE status='active'
        AND effective_date < DATE('now', '-2 years')
    """)

    for doc in old_docs:
        send_alert(f"Document may be outdated: {doc['filename']}")
        # Optionally auto-flag for review
```

---

## Implementation Timeline (POC)

> **Note:** These are rough estimates for a POC. Adjust based on your pace and complexity.

### Day 1: Setup & Data Preparation
- Design/refine document template
- Set up Python environment, install dependencies
- Generate 20-30 sample documents (using Claude/GPT)

### Day 2: Build Core System
- Implement indexing script with metadata extraction
- Run indexing, test embedding generation
- Build query system with structured prompts
- Test retrieval quality with sample queries

### Day 3: Quality & Testing
- Implement basic versioning logic (if time permits)
- Build Streamlit UI (optional)
- End-to-end testing with various queries
- Tune chunk size and retrieval parameters if needed

**Total POC Timeline: 2-3 days**

---

## Tech Stack (Free/Cheap Options)

| Component | Tool | Cost |
|-----------|------|------|
| Embedding | OpenAI text-embedding-3-small | ~$0.001-0.01 for indexing |
| Vector DB | Chroma (local) | Free |
| SQL DB | SQLite | Free |
| LLM | GPT-3.5-turbo | ~$0.07 per query |
| UI | Streamlit | Free (local) |
| **Total for demo** | | **<$1** |

---

## Environment Setup

```bash
# .env file
OPENAI_API_KEY=your_key_here

# requirements.txt
openai==1.12.0
chromadb==0.4.22
langchain==0.1.9
langchain-community==0.0.24
langchain-openai==0.0.6
streamlit==1.31.0
pyyaml==6.0.1
python-dotenv==1.0.1
```

---

## Testing Checklist

### Functional Tests
- [ ] Can index 20+ documents successfully
- [ ] Query returns relevant chunks (top-5)
- [ ] LLM synthesizes coherent answers
- [ ] Metadata (contacts, systems) appears in responses
- [ ] Source attribution works

### Quality Tests
- [ ] Synonym queries find same docs ("permit" vs "license")
- [ ] Multi-chunk synthesis works (combines info from 3+ sources)
- [ ] Recency preference (newest docs ranked higher)
- [ ] Conflict detection (flags contradictions)
- [ ] Gap identification (notes missing information)

### Edge Cases
- [ ] Query with no relevant docs (graceful "not found")
- [ ] Very broad query (returns general overview)
- [ ] Very specific query (returns detailed procedure)
- [ ] Query about deprecated doc (filters out properly)

---

## Success Metrics for Demo

- **Retrieval Quality:** Top-3 results relevant for 80%+ of test queries
- **Answer Quality:** Responses are actionable and include contacts/systems
- **Source Attribution:** Every answer cites sources correctly
- **Conflict Handling:** System identifies contradictions in test cases
- **User Experience:** <5 seconds from query to answer

---

## Next Steps After POC

### Phase 2 Enhancements
- SQL database for structured metadata queries
- Advanced versioning with deprecation workflows
- Automated conflict detection pipeline
- User feedback collection ("Was this helpful?")
- Query analytics dashboard

### Phase 3 Production
- Authentication & role-based access
- Document submission workflow with approval
- Periodic quality audits
- Integration with existing municipal systems
- Cloud deployment (AWS/Azure/GCP)

---

## Common Pitfalls to Avoid

- ❌ **Don't:** Split documents randomly (breaks context)
- ✅ **Do:** Use semantic splitting by headers

- ❌ **Don't:** Ignore document metadata (lose attribution)
- ✅ **Do:** Capture rich metadata upfront

- ❌ **Don't:** Index everything without filtering
- ✅ **Do:** Validate quality and classify document types

- ❌ **Don't:** Retrieve only 1 chunk (incomplete answers)
- ✅ **Do:** Retrieve 5-10 chunks for synthesis

- ❌ **Don't:** Forget about document evolution
- ✅ **Do:** Plan for versioning from day one

---

## Quick Start Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate sample docs (using Claude)
# [Manual step - use Claude to create 20 .md files]

# Index documents
python indexing.py

# Test queries (CLI)
python query_system.py

# Launch UI
streamlit run app.py
```

---

## Final Reminders for Implementation

- This is a **POC/Demo**, not production-ready
- Focus on getting something **working end-to-end** first
- **Iterate** on quality and features after core functionality works
- **Don't over-engineer** - simple solutions often work best
- **Test frequently** with real queries to validate approach
- **Document assumptions** and decisions as you go
- **Ask questions** if requirements are unclear - better to clarify than build the wrong thing
