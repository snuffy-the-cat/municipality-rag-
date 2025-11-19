# -*- coding: utf-8 -*-
"""
Hebrew Document Generation Script - Graph-Driven
Reads responsibility_graph_hebrew.yaml and generates documents according to model specifications
Filename format: res_{responsibility}_{model}_{doc_id}.md
"""

import os
import sys
import yaml
import ollama
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from tqdm import tqdm

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directories to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "1_data_creation"))

# Paths
GRAPH_PATH = PROJECT_ROOT / "1_data_creation/config/responsibility_graph_hebrew.yaml"
TEMPLATE_PATH = PROJECT_ROOT / "2_data_processing/templates/input_template_hebrew.md"
PROMPT_TEMPLATE_PATH = PROJECT_ROOT / "1_data_creation/config/prompt_for_data_generation.md"

# Output directory
OUTPUT_BASE_DIR = PROJECT_ROOT / "data/generated"


def load_graph() -> Dict:
    """Load the Hebrew responsibility graph"""
    print(f"Loading graph from: {GRAPH_PATH}")
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)

    total_resp = graph.get('statistics', {}).get('total_responsibilities', 0)
    print(f"Loaded graph with {total_resp} responsibilities across {len(graph['clusters'])} clusters")
    return graph


def load_template() -> str:
    """Load the Hebrew template structure"""
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def build_generation_prompt(responsibility: Dict, cluster: Dict, min_completeness: int, template_structure: str) -> str:
    """Build prompt for document generation with completeness target"""

    # Get shared resources
    shared_contacts = cluster.get('shared_resources', {}).get('contacts', [])
    shared_systems = cluster.get('shared_resources', {}).get('systems', [])

    prompt = f"""אתה מתעד ידע של עובד עירייה עוזב עבור תפקיד: {responsibility['name']}

פרטי התפקיד:
- קטגוריה: {responsibility.get('category', 'לא צוין')}
- תת-קטגוריה: {responsibility.get('subcategory', 'לא צוין')}
- תדירות: {responsibility.get('frequency', 'לא צוין')}
- עדיפות: {responsibility.get('priority_level', 'לא צוין')}
- אשכול: {cluster['name']} - {cluster['description']}

יעד איכות: מסמך עם לפחות {min_completeness}% שלמות (מילוי מקסימלי של סעיפים)

אנשי קשר משותפים באשכול:
{', '.join([c['name'] + ' (' + c['role'] + ')' for c in shared_contacts]) if shared_contacts else 'אין'}

מערכות משותפות באשכול:
{', '.join([s['name'] for s in shared_systems]) if shared_systems else 'אין'}

צור מסמך תיעוד עזיבה עירוני ריאליסטי ומפורט בעברית בפורמט MARKDOWN עם YAML frontmatter.

דרישות:
1. עקוב אחר המבנה המדויק של התבנית (15 סעיפים)
2. השתמש ב-YAML frontmatter בראש המסמך (בין --- למרקרים)
3. כתוב בעברית ברורה ומקצועית (>95% תווים עבריים)
4. כותרות סעיפים: BEZ מספור (## ממשקי עבודה ואנשי קשר, לא ## 1. ממשקי עבודה...)
5. מלא את כל הסעיפים עם תוכן ריאליסטי
6. השתמש באנשי הקשר והמערכות מהאשכול
7. כלול פרטים עירוניים ריאליסטיים (טפסים, קודים, נהלים, מספרי טלפון)
8. כתוב בגוף ראשון בחלק "הערות מסירה"
9. כלול דוגמאות ספציפיות, טעויות נפוצות וטיפים
10. השתמש בשמות בדויים ריאליסטיים, אימיילים (פורמט: name@city.gov.il), מספרי טלפון (03-555xxxx)

מבנה המסמך - התבנית:
{template_structure}

כללי מילוי:
- מלא לפחות 3-5 פריטים בכל קטגוריה רלבנטית
- אם סעיף לא רלוונטי: כתוב [לא רלוונטי לתפקיד זה]
- אל תשאיר סעיפים ריקים
- אל תוסיף מספור לכותרות הסעיפים

פורמט פלט:
החזר רק את מסמך ה-markdown עם YAML frontmatter. ללא הסברים, ללא בלוקים של קוד, רק ה-markdown הגולמי.

צור את המסמך המלא כעת:
"""

    return prompt


def generate_with_ollama(prompt: str, model: str) -> str:
    """Generate document using Ollama library"""

    print(f"    Calling Ollama model: {model}...")

    try:
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 6000
            }
        )
        content = response['response']
        print(f"    Generated {len(content)} characters")
        return content
    except Exception as e:
        print(f"    [ERROR] Ollama generation failed: {e}")
        raise


def generate_with_claude(prompt: str, api_key: str = None) -> str:
    """Generate document using Claude API"""

    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("anthropic library not installed. Run: pip install anthropic")

    print(f"    Calling Claude API...")

    # Use environment variable if no API key provided
    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        raise ValueError("Claude API key not found. Set ANTHROPIC_API_KEY environment variable.")

    client = Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=6000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"    [ERROR] Claude API call failed: {e}")
        raise


def generate_document(prompt: str, model: str) -> str:
    """
    Generate document with appropriate LLM
    Supports: Ollama (mistral-nemo, qwen2.5:7b, aya:8b) and Claude API
    """

    # Map short names to full Ollama model names
    model_map = {
        'mistral': 'mistral-nemo',
        'qwen': 'qwen2.5:7b',
        'aya': 'aya:8b'
    }

    # Use mapped name if available
    ollama_model = model_map.get(model, model)

    if model in ['mistral', 'qwen', 'aya'] or ollama_model in ['mistral-nemo', 'qwen2.5:7b', 'aya:8b']:
        return generate_with_ollama(prompt, ollama_model)
    elif model == 'claude':
        # Check if API key is available
        if not os.environ.get('ANTHROPIC_API_KEY'):
            raise ValueError("Claude API key not found. Skipping Claude model. Set ANTHROPIC_API_KEY environment variable or remove Claude from graph.")
        return generate_with_claude(prompt)
    else:
        raise ValueError(f"Unknown model: {model}")


def count_documents_to_generate(graph: Dict) -> int:
    """Count total documents to be generated based on graph specifications"""
    total = 0
    for cluster in graph['clusters']:
        for responsibility in cluster['responsibilities']:
            total += len(responsibility.get('documents', []))
    return total


def generate_all_documents(graph: Dict, template_structure: str) -> Tuple[List[Path], Dict]:
    """
    Generate all documents according to graph specifications

    Returns:
        (generated_files, summary_stats)
    """

    print("="*80)
    print("HEBREW DOCUMENT GENERATION - GRAPH-DRIVEN")
    print("="*80)

    generated_files = []
    summary_stats = {
        'total_planned': count_documents_to_generate(graph),
        'generated': 0,
        'failed': 0,
        'by_model': {}
    }

    print(f"Total documents to generate: {summary_stats['total_planned']}")
    print()

    # Process each cluster
    with tqdm(total=summary_stats['total_planned'], desc="Generating documents", unit="doc") as pbar:
        for cluster in graph['clusters']:
            cluster_name = cluster['name']
            print(f"\n{'='*80}")
            print(f"CLUSTER: {cluster_name}")
            print(f"{'='*80}")

            for responsibility in cluster['responsibilities']:
                resp_id = responsibility['id']
                resp_name = responsibility['name']
                documents = responsibility.get('documents', [])

                print(f"\nResponsibility: {resp_id} - {resp_name}")
                print(f"  Documents to generate: {len(documents)}")

                # Generate each document
                for doc_spec in documents:
                    doc_id = doc_spec['doc_id']
                    model = doc_spec['model']
                    min_completeness = doc_spec.get('min_completeness', 80)

                    # Format filename: res_{responsibility}_{model}.md
                    filename = f"{resp_id}_{model}.md"

                    print(f"\n  [{doc_id}] Model: {model} | Target: {min_completeness}% | File: {filename}")

                    try:
                        # Build prompt
                        prompt = build_generation_prompt(
                            responsibility=responsibility,
                            cluster=cluster,
                            min_completeness=min_completeness,
                            template_structure=template_structure
                        )

                        # Generate document
                        content = generate_document(prompt, model)

                        # Create output directory for model
                        output_dir = OUTPUT_BASE_DIR / f"markdown-hebrew-{model}"
                        output_dir.mkdir(parents=True, exist_ok=True)

                        # Save document
                        filepath = output_dir / filename
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)

                        generated_files.append(filepath)
                        summary_stats['generated'] += 1
                        summary_stats['by_model'][model] = summary_stats['by_model'].get(model, 0) + 1

                        print(f"    [OK] Generated {len(content)} characters")

                        pbar.update(1)

                    except Exception as e:
                        print(f"    [FAIL] Error: {e}")
                        summary_stats['failed'] += 1
                        pbar.update(1)
                        continue

    return generated_files, summary_stats


def print_summary(generated_files: List[Path], summary_stats: Dict):
    """Print generation summary"""

    print()
    print("="*80)
    print("GENERATION SUMMARY")
    print("="*80)
    print(f"Total planned: {summary_stats['total_planned']}")
    print(f"Successfully generated: {summary_stats['generated']}")
    print(f"Failed: {summary_stats['failed']}")
    print()
    print("Files by model:")
    for model, count in sorted(summary_stats['by_model'].items()):
        print(f"  {model}: {count} documents")
    print()
    print(f"Output directory: {OUTPUT_BASE_DIR}")
    print()
    print("Next steps:")
    print("1. Run structure enforcer: python 2_data_processing/scripts/enforce_structure.py")
    print("2. Check logs for quality metrics")
    print("3. Run iterative improvement if needed: python 1_data_creation/scripts/iterative_generation.py")
    print()


def main():
    """Main generation function"""

    print("Municipality RAG - Hebrew Document Generator (Graph-Driven)")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    # Load graph
    graph = load_graph()

    # Load template structure
    template_structure = load_template()

    # Generate all documents
    generated_files, summary_stats = generate_all_documents(graph, template_structure)

    # Print summary
    print_summary(generated_files, summary_stats)


if __name__ == "__main__":
    main()
