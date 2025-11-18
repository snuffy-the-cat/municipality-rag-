"""
Document Generation Script
Generates 30 municipal departure documents from responsibility_graph.yaml using Ollama
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import ollama
from tqdm import tqdm
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add(PROJECT_ROOT / "outputs/logs/generation_{time}.log", rotation="10 MB")

# Paths
GRAPH_PATH = PROJECT_ROOT / "config/responsibility_graph.yaml"
TEMPLATE_PATH = PROJECT_ROOT / "templates/input_template.yaml"
OUTPUT_DIR = PROJECT_ROOT / "data/generated/markdown"

# Ollama settings
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT = 120  # seconds


def load_graph() -> Dict:
    """Load the responsibility graph"""
    logger.info(f"Loading graph from: {GRAPH_PATH}")
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)

    total_resp = graph.get('statistics', {}).get('total_responsibilities', 0)
    logger.info(f"Loaded graph with {total_resp} responsibilities across {len(graph['clusters'])} clusters")
    return graph


def load_template() -> Dict:
    """Load the YAML template structure"""
    logger.info(f"Loading template from: {TEMPLATE_PATH}")
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = yaml.safe_load(f)
    return template


def build_generation_prompt(responsibility: Dict, cluster: Dict, graph: Dict) -> str:
    """Build a detailed prompt for generating a departure document"""

    # Get related responsibilities info
    related_info = []

    # Direct dependencies
    if 'direct_dependencies' in responsibility:
        for dep_type, deps in responsibility['direct_dependencies'].items():
            for dep in deps:
                related_info.append(f"- {dep_type.upper()}: {dep['id']} ({dep.get('connection_description', '')})")

    # Indirect dependencies
    if 'indirect_dependencies' in responsibility:
        for dep in responsibility['indirect_dependencies']:
            related_info.append(f"- RELATED: {dep['id']} ({dep.get('relationship', '')} via {dep.get('shared_element', '')})")

    # Shared resources from cluster
    shared_contacts = cluster.get('shared_resources', {}).get('contacts', [])
    shared_systems = cluster.get('shared_resources', {}).get('systems', [])

    # Data completeness instructions
    completeness = responsibility.get('data_completeness', 'full')
    missing_sections = responsibility.get('missing_sections', [])

    completeness_instructions = ""
    if completeness == "partial":
        completeness_instructions = f"""
IMPORTANT - PARTIAL DOCUMENT:
This document should be INCOMPLETE. You must omit these sections entirely:
{', '.join(missing_sections)}
Do NOT include these sections at all. Leave them completely absent from the document.
"""
    elif completeness == "minimal":
        completeness_instructions = f"""
IMPORTANT - MINIMAL DOCUMENT:
This document should be VERY BRIEF with only:
- Overview (2-3 sentences)
- 2-3 basic steps in the procedure
- 1-2 key contacts
You must omit these sections entirely: {', '.join(missing_sections)}
Keep it very short and simple.
"""

    prompt = f"""You are documenting a municipal employee's departure knowledge for: {responsibility['name']}

RESPONSIBILITY DETAILS:
- Category: {responsibility.get('category', 'N/A')}
- Subcategory: {responsibility.get('subcategory', 'N/A')}
- Frequency: {responsibility.get('frequency', 'N/A')}
- Priority: {responsibility.get('priority_level', 'N/A')}
- Cluster: {cluster['name']} - {cluster['description']}

RELATED RESPONSIBILITIES:
{chr(10).join(related_info) if related_info else '- None'}

SHARED RESOURCES IN THIS CLUSTER:
Contacts: {', '.join([c['name'] + ' (' + c['role'] + ')' for c in shared_contacts]) if shared_contacts else 'None'}
Systems: {', '.join([s['name'] for s in shared_systems]) if shared_systems else 'None'}

{completeness_instructions}

Generate a realistic, detailed municipal departure document in MARKDOWN format with YAML frontmatter.

REQUIREMENTS:
1. Use YAML frontmatter at the top (between --- markers) with all metadata
2. If this responsibility has dependencies, reference them naturally in the procedures
3. Use the shared contacts and systems from the cluster
4. Include realistic municipal details (forms, codes, procedures, phone extensions)
5. Write in first person for the "Handoff Notes" section
6. Make it practical and helpful for a real new employee
7. Include specific examples, common mistakes, and tips
8. Use realistic fictional names, emails (format: name@municipality.gov), phone numbers (555-0xxx)

OUTPUT FORMAT:
Return ONLY the markdown document with YAML frontmatter. No explanations, no code blocks, just the raw markdown.

Generate the complete document now:
"""

    return prompt


def generate_document_with_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Generate document using Ollama"""

    try:
        logger.debug(f"Calling Ollama with model: {model}")

        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 4000,  # Max tokens
            }
        )

        content = response['response']
        logger.debug(f"Generated {len(content)} characters")

        return content

    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        raise


def save_markdown(content: str, responsibility_id: str, responsibility_name: str) -> Path:
    """Save generated content as markdown file"""

    # Clean filename
    safe_name = responsibility_id.replace('/', '_').replace('\\', '_')
    filename = f"{safe_name}.md"
    filepath = OUTPUT_DIR / filename

    # Ensure directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Saved: {filename}")
    return filepath


def generate_all_documents(graph: Dict, model: str = OLLAMA_MODEL) -> List[Path]:
    """Generate all documents from the graph"""

    logger.info("="*80)
    logger.info("Starting document generation")
    logger.info("="*80)

    generated_files = []
    total_responsibilities = sum(len(cluster['responsibilities']) for cluster in graph['clusters'])

    # Check if Ollama is available
    try:
        logger.info(f"Testing Ollama connection with model: {model}")
        ollama.generate(model=model, prompt="test", options={"num_predict": 1})
        logger.success(f"Ollama model '{model}' is ready")
    except Exception as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        logger.error(f"Make sure Ollama is running and model '{model}' is installed")
        logger.error(f"Run: ollama pull {model}")
        sys.exit(1)

    # Process each cluster
    with tqdm(total=total_responsibilities, desc="Generating documents", unit="doc") as pbar:
        for cluster in graph['clusters']:
            logger.info(f"\nProcessing cluster: {cluster['name']}")

            for responsibility in cluster['responsibilities']:
                resp_id = responsibility['id']
                resp_name = responsibility['name']

                logger.info(f"Generating: {resp_id} - {resp_name}")

                # Build prompt
                prompt = build_generation_prompt(responsibility, cluster, graph)

                # Generate document
                try:
                    content = generate_document_with_ollama(prompt, model)

                    # Save document
                    filepath = save_markdown(content, resp_id, resp_name)
                    generated_files.append(filepath)

                    pbar.update(1)

                except Exception as e:
                    logger.error(f"Failed to generate {resp_id}: {e}")
                    pbar.update(1)
                    continue

    logger.info("="*80)
    logger.success(f"Generated {len(generated_files)} / {total_responsibilities} documents")
    logger.info("="*80)

    return generated_files


def main():
    """Main function"""

    logger.info("Municipality RAG - Document Generator")
    logger.info(f"Project root: {PROJECT_ROOT}")

    # Load graph and template
    graph = load_graph()

    # Generate all documents
    generated_files = generate_all_documents(graph, model=OLLAMA_MODEL)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("GENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Total documents generated: {len(generated_files)}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Log saved to: outputs/logs/")

    # List files by cluster
    logger.info("\nGenerated files by cluster:")
    for cluster in graph['clusters']:
        cluster_files = [f for f in generated_files if any(r['id'] in f.name for r in cluster['responsibilities'])]
        logger.info(f"\n{cluster['name']}: {len(cluster_files)} files")
        for f in cluster_files[:3]:  # Show first 3
            logger.info(f"  - {f.name}")
        if len(cluster_files) > 3:
            logger.info(f"  ... and {len(cluster_files) - 3} more")


if __name__ == "__main__":
    main()
