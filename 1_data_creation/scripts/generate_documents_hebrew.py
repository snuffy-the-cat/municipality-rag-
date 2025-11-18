# -*- coding: utf-8 -*-
"""
Hebrew Document Generation Script
Generates Hebrew municipal departure documents using Ollama
Based on client's 15-section structure
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import ollama
from tqdm import tqdm
from loguru import logger

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add(PROJECT_ROOT / "outputs/logs/generation_hebrew_{time}.log", rotation="10 MB")

# Paths
GRAPH_PATH = PROJECT_ROOT / "config/responsibility_graph_hebrew.yaml"
TEMPLATE_PATH = PROJECT_ROOT / "templates/input_template_hebrew.md"
MODELS_CONFIG_PATH = PROJECT_ROOT / "config/models_config.yaml"

# Load model configuration
def load_model_config() -> Dict:
    """Load model configuration from YAML"""
    with open(MODELS_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Get active model and settings
MODEL_CONFIG = load_model_config()
OLLAMA_MODEL = MODEL_CONFIG['active_model']['hebrew']
MODEL_SETTINGS = MODEL_CONFIG['models'][OLLAMA_MODEL]

# Output directory based on model
OUTPUT_DIR = PROJECT_ROOT / "data/generated" / MODEL_CONFIG['output_dirs'].get(OLLAMA_MODEL, 'markdown-hebrew')


def load_graph() -> Dict:
    """Load the Hebrew responsibility graph"""
    logger.info(f"Loading Hebrew graph from: {GRAPH_PATH}")
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)

    total_resp = graph.get('statistics', {}).get('total_responsibilities', 0)
    logger.info(f"Loaded graph with {total_resp} responsibilities across {len(graph['clusters'])} clusters")
    return graph


def build_generation_prompt_hebrew(responsibility: Dict, cluster: Dict) -> str:
    """Build Hebrew prompt for document generation"""

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

אנשי קשר משותפים באשכול:
{', '.join([c['name'] + ' (' + c['role'] + ')' for c in shared_contacts]) if shared_contacts else 'אין'}

מערכות משותפות באשכול:
{', '.join([s['name'] for s in shared_systems]) if shared_systems else 'אין'}

צור מסמך תיעוד עזיבה עירוני ריאליסטי ומפורט בעברית בפורמט MARKDOWN עם YAML frontmatter.

דרישות:
1. השתמש ב-YAML frontmatter בראש המסמך (בין --- למרקרים)
2. כתוב בעברית ברורה ומקצועית
3. השתמש באנשי הקשר והמערכות מהאשכול
4. כלול פרטים עירוניים ריאליסטיים (טפסים, קודים, נהלים, מספרי טלפון)
5. כתוב בגוף ראשון בחלק "הערות מסירה"
6. הפוך את זה למעשי ושימושי לעובד חדש אמיתי
7. כלול דוגמאות ספציפיות, טעויות נפוצות וטיפים
8. השתמש בשמות בדויים ריאליסטיים, אימיילים (פורמט: name@city.gov.il), מספרי טלפון (03-555xxxx)

מבנה המסמך - מלא לפחות 3-5 פריטים בכל קטגוריה רלבנטית:

1. ממשקי עבודה ואנשי קשר - לפחות 3 אנשי קשר עם פרטים מלאים
2. הדרכות, השתלמויות והכשרות - לפחות 2 הדרכות רלבנטיות
3. חוזי התקשרות שנוהלו עם ספקים - לפחות 1-2 התקשרויות
4. ועדות - לפחות 1 ועדה רלבנטית
5. כפיפים - אם רלוונטי
6. ממשקי עבודה - ארגונים - לפחות 2 ממשקים
7. מערכות מידע - לפחות 2-3 מערכות
8. מסמכים חשובים - לפחות 3 מסמכים
9. נהלים עירוניים - לפחות 2 נהלים
10. נושאים פתוחים - 1-2 נושאים
11. רגולציה - אם רלוונטי
12. שגרות עבודה - לפחות 3 שגרות
13. קולות קוראים ומקורות מימון - אם רלוונטי
14. תהליכי עבודה - לפחות 2 תהליכים מפורטים
15. תכנית עבודה - לפחות 4-5 פעילויות

פורמט פלט:
החזר רק את מסמך ה-markdown עם YAML frontmatter. ללא הסברים, ללא בלוקים של קוד, רק ה-markdown הגולמי.

צור את המסמך המלא כעת:
"""

    return prompt


def generate_document_with_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Generate document using Ollama"""

    try:
        logger.debug(f"Calling Ollama with model: {model}")

        # Get model-specific settings or use defaults
        settings = MODEL_CONFIG['models'].get(model, {})
        temperature = settings.get('temperature', 0.7)
        num_predict = settings.get('num_predict', 6000)

        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "num_predict": num_predict,
            }
        )

        content = response['response']
        logger.debug(f"Generated {len(content)} characters")

        return content

    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        raise


def save_markdown_hebrew(content: str, responsibility_id: str) -> Path:
    """Save generated Hebrew content as markdown file"""

    # Clean filename
    safe_name = responsibility_id.replace('/', '_').replace('\\', '_')
    filename = f"{safe_name}.md"
    filepath = OUTPUT_DIR / filename

    # Ensure directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save file with UTF-8 encoding
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Saved: {filename}")
    return filepath


def generate_all_hebrew_documents(graph: Dict, model: str = OLLAMA_MODEL) -> List[Path]:
    """Generate all Hebrew documents from the graph"""

    logger.info("="*80)
    logger.info("Starting Hebrew document generation")
    logger.info(f"Active model: {model} ({MODEL_SETTINGS.get('name', model)})")
    logger.info(f"Description: {MODEL_SETTINGS.get('description', 'N/A')}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
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
    with tqdm(total=total_responsibilities, desc="Generating Hebrew documents", unit="doc") as pbar:
        for cluster in graph['clusters']:
            logger.info(f"\nProcessing cluster: {cluster['name']}")

            for responsibility in cluster['responsibilities']:
                resp_id = responsibility['id']
                resp_name = responsibility['name']

                logger.info(f"Generating: {resp_id} - {resp_name}")

                # Build prompt
                prompt = build_generation_prompt_hebrew(responsibility, cluster)

                # Generate document
                try:
                    content = generate_document_with_ollama(prompt, model)

                    # Save document
                    filepath = save_markdown_hebrew(content, resp_id)
                    generated_files.append(filepath)

                    pbar.update(1)

                except Exception as e:
                    logger.error(f"Failed to generate {resp_id}: {e}")
                    pbar.update(1)
                    continue

    logger.info("="*80)
    logger.success(f"Generated {len(generated_files)} / {total_responsibilities} Hebrew documents")
    logger.info("="*80)

    return generated_files


def main():
    """Main function"""

    logger.info("Municipality RAG - Hebrew Document Generator")
    logger.info(f"Project root: {PROJECT_ROOT}")

    # Load Hebrew graph
    graph = load_graph()

    # Generate all documents
    generated_files = generate_all_hebrew_documents(graph, model=OLLAMA_MODEL)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("GENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Total Hebrew documents generated: {len(generated_files)}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Log saved to: outputs/logs/")

    # List files by cluster
    logger.info("\nGenerated Hebrew files by cluster:")
    for cluster in graph['clusters']:
        cluster_files = [f for f in generated_files if any(r['id'] in f.name for r in cluster['responsibilities'])]
        logger.info(f"\n{cluster['name']}: {len(cluster_files)} files")
        for f in cluster_files:
            logger.info(f"  - {f.name}")


if __name__ == "__main__":
    main()
