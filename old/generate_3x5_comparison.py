# -*- coding: utf-8 -*-
"""
Generate 3x5 Hebrew Documents - Model Comparison
Generates 5 documents with each of 3 models (Qwen, Mistral, Aya)
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import ollama
from loguru import logger
import time

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add(PROJECT_ROOT / "outputs/logs/3x5_comparison_{time}.log", rotation="10 MB")

# Paths
GRAPH_PATH = PROJECT_ROOT / "config/responsibility_graph_hebrew.yaml"
OUTPUT_BASE = PROJECT_ROOT / "data/generated"

# Models to test (in priority order)
MODELS = [
    {'name': 'qwen2.5:7b', 'folder': 'markdown-hebrew-qwen', 'description': 'Qwen 2.5 (7B)'},
    {'name': 'mistral-nemo', 'folder': 'markdown-hebrew-mistral', 'description': 'Mistral-Nemo'},
    {'name': 'aya:8b', 'folder': 'markdown-hebrew-aya', 'description': 'Aya (8B)'},
]

# Number of documents per model
DOCS_PER_MODEL = 5


def load_graph() -> Dict:
    """Load the Hebrew responsibility graph"""
    logger.info(f"Loading Hebrew graph from: {GRAPH_PATH}")
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        graph = yaml.safe_load(f)

    total_resp = graph.get('statistics', {}).get('total_responsibilities', 0)
    logger.info(f"Loaded graph with {total_resp} responsibilities")
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


def list_available_models() -> List[str]:
    """List models available in Ollama"""
    try:
        result = ollama.list()
        available = [model['name'] for model in result.get('models', [])]
        logger.info(f"Available Ollama models: {', '.join(available) if available else 'None'}")
        return available
    except Exception as e:
        logger.warning(f"Could not list Ollama models: {e}")
        return []


def check_model_available(model_name: str, available_models: List[str]) -> bool:
    """Check if a model is available"""
    # Check exact match or partial match (for version tags)
    for available in available_models:
        if available.startswith(model_name) or available == model_name:
            return True
    return False


def generate_document_with_ollama(prompt: str, model: str) -> str:
    """Generate document using Ollama"""

    try:
        logger.debug(f"Calling Ollama with model: {model}")

        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 6000,
            }
        )

        content = response['response']
        logger.debug(f"Generated {len(content)} characters")

        return content

    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        raise


def calculate_hebrew_percentage(text: str) -> float:
    """Calculate percentage of Hebrew characters in text"""
    hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    total_chars = len(text.strip())
    if total_chars == 0:
        return 0.0
    return (hebrew_chars / total_chars) * 100


def save_markdown_hebrew(content: str, responsibility_id: str, output_dir: Path) -> Path:
    """Save generated Hebrew content as markdown file"""

    # Clean filename
    safe_name = responsibility_id.replace('/', '_').replace('\\', '_')
    filename = f"{safe_name}.md"
    filepath = output_dir / filename

    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save file with UTF-8 encoding
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    # Calculate stats
    hebrew_pct = calculate_hebrew_percentage(content)
    size_kb = len(content.encode('utf-8')) / 1024

    logger.info(f"  Saved: {filename} ({size_kb:.1f}KB, {hebrew_pct:.1f}% Hebrew)")
    return filepath


def generate_batch_for_model(model_info: Dict, graph: Dict, num_docs: int = 5) -> List[Dict]:
    """Generate a batch of documents for a specific model"""

    model_name = model_info['name']
    output_folder = model_info['folder']
    description = model_info['description']

    logger.info("=" * 80)
    logger.info(f"Model: {description} ({model_name})")
    logger.info(f"Generating {num_docs} documents...")
    logger.info("=" * 80)

    output_dir = OUTPUT_BASE / output_folder
    results = []

    # Get first num_docs responsibilities
    docs_generated = 0
    for cluster in graph['clusters']:
        if docs_generated >= num_docs:
            break

        for responsibility in cluster['responsibilities']:
            if docs_generated >= num_docs:
                break

            resp_id = responsibility['id']
            resp_name = responsibility['name']

            logger.info(f"\n[{docs_generated + 1}/{num_docs}] {resp_name}")

            # Build prompt
            prompt = build_generation_prompt_hebrew(responsibility, cluster)

            # Generate document
            try:
                start_time = time.time()
                content = generate_document_with_ollama(prompt, model_name)
                end_time = time.time()
                generation_time = end_time - start_time

                # Save document
                filepath = save_markdown_hebrew(content, resp_id, output_dir)

                # Calculate stats
                hebrew_pct = calculate_hebrew_percentage(content)
                size_bytes = len(content.encode('utf-8'))

                results.append({
                    'model': model_name,
                    'responsibility_id': resp_id,
                    'responsibility_name': resp_name,
                    'filepath': str(filepath),
                    'size_bytes': size_bytes,
                    'hebrew_percentage': hebrew_pct,
                    'generation_time': generation_time
                })

                logger.success(f"  Completed in {generation_time:.1f}s")
                docs_generated += 1

            except Exception as e:
                logger.error(f"  Failed: {e}")
                continue

    logger.success(f"\nGenerated {docs_generated} documents with {model_name}")
    return results


def generate_comparison_report(all_results: Dict[str, List[Dict]]) -> str:
    """Generate a comparison report of all models"""

    report = ["# Hebrew Model Comparison Report - 3x5 Generation\n\n"]
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Documents per model**: {DOCS_PER_MODEL}\n\n")

    # Summary Statistics
    report.append("## Summary Statistics\n\n")
    report.append("| Model | Docs | Avg Size (KB) | Avg Hebrew % | Avg Time (s) |\n")
    report.append("|-------|------|---------------|--------------|-------------|\n")

    for model_name, results in all_results.items():
        if not results:
            report.append(f"| {model_name} | 0 | - | - | - |\n")
            continue

        avg_size = sum(r['size_bytes'] for r in results) / len(results) / 1024
        avg_hebrew = sum(r['hebrew_percentage'] for r in results) / len(results)
        avg_time = sum(r['generation_time'] for r in results) / len(results)

        report.append(f"| {model_name} | {len(results)} | {avg_size:.1f} | {avg_hebrew:.1f}% | {avg_time:.1f} |\n")

    # Detailed Results
    report.append("\n## Detailed Results\n\n")

    for model_name, results in all_results.items():
        if not results:
            continue

        report.append(f"### {model_name}\n\n")
        report.append("| Document | Size (KB) | Hebrew % | Time (s) |\n")
        report.append("|----------|-----------|----------|----------|\n")

        for r in results:
            size_kb = r['size_bytes'] / 1024
            report.append(f"| {r['responsibility_name']} | {size_kb:.1f} | {r['hebrew_percentage']:.1f}% | {r['generation_time']:.1f} |\n")

        report.append("\n")

    # Recommendations
    report.append("## Analysis\n\n")

    if all_results:
        best_hebrew = max(all_results.items(), key=lambda x: sum(r['hebrew_percentage'] for r in x[1]) / len(x[1]) if x[1] else 0)
        fastest = min(all_results.items(), key=lambda x: sum(r['generation_time'] for r in x[1]) / len(x[1]) if x[1] else 999)
        largest = max(all_results.items(), key=lambda x: sum(r['size_bytes'] for r in x[1]) / len(x[1]) if x[1] else 0)

        report.append(f"- **Best Hebrew Quality**: {best_hebrew[0]}\n")
        report.append(f"- **Fastest Generation**: {fastest[0]}\n")
        report.append(f"- **Most Detailed**: {largest[0]}\n\n")

    report.append("## Recommendations\n\n")
    report.append("1. **Hebrew Quality**: Choose model with highest Hebrew percentage (target >85%)\n")
    report.append("2. **Content Detail**: Larger documents typically mean more comprehensive coverage\n")
    report.append("3. **Speed**: Consider generation time if batch processing many documents\n")
    report.append("4. **Manual Review**: Read sample outputs to assess actual quality beyond metrics\n\n")

    report.append("## Next Steps\n\n")
    report.append("1. Review sample documents from each model\n")
    report.append("2. Check Hebrew quality and coherence\n")
    report.append("3. Update `config/models_config.yaml` with best model\n")
    report.append("4. Run full generation with chosen model\n")

    return ''.join(report)


def main():
    """Main function"""

    logger.info("Municipality RAG - 3x5 Hebrew Model Comparison")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info("")

    # Load Hebrew graph
    graph = load_graph()

    # Check available models
    logger.info("\nChecking available Ollama models...")
    available_models = list_available_models()

    if not available_models:
        logger.error("\nNo Ollama models found!")
        logger.error("Please install models first:")
        logger.error("  ollama pull qwen2.5:7b")
        logger.error("  ollama pull mistral-nemo")
        logger.error("  ollama pull aya:8b")
        logger.error("\nOr run: python scripts/setup_hebrew_models.py")
        return

    # Check which models are available
    logger.info("\nModel availability check:")
    models_to_use = []
    for model_info in MODELS:
        if check_model_available(model_info['name'], available_models):
            logger.success(f"  [OK] {model_info['description']} ({model_info['name']})")
            models_to_use.append(model_info)
        else:
            logger.warning(f"  [SKIP] {model_info['description']} ({model_info['name']}) - not installed")
            logger.info(f"         Install with: ollama pull {model_info['name']}")

    if not models_to_use:
        logger.error("\nNone of the target models are installed!")
        logger.error("Please install at least one model and try again.")
        return

    logger.info(f"\nWill generate documents with {len(models_to_use)} model(s)")
    logger.info("")

    # Store all results
    all_results = {}

    # Generate documents for each available model
    for model_info in models_to_use:
        results = generate_batch_for_model(model_info, graph, DOCS_PER_MODEL)
        all_results[model_info['name']] = results

    # Generate comparison report
    logger.info("\n" + "=" * 80)
    logger.info("Generating comparison report...")
    logger.info("=" * 80)

    report = generate_comparison_report(all_results)

    # Save report
    report_path = OUTPUT_BASE / "model_comparison_3x5_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.success(f"Report saved to: {report_path}")

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("GENERATION COMPLETE")
    logger.info("=" * 80)

    for model_name, results in all_results.items():
        if results:
            avg_hebrew = sum(r['hebrew_percentage'] for r in results) / len(results)
            avg_size = sum(r['size_bytes'] for r in results) / len(results) / 1024
            logger.info(f"\n{model_name}:")
            logger.info(f"  Documents: {len(results)}")
            logger.info(f"  Avg Hebrew: {avg_hebrew:.1f}%")
            logger.info(f"  Avg Size: {avg_size:.1f}KB")

    logger.info(f"\n\nOutput folders:")
    for model_info in models_to_use:
        folder_path = OUTPUT_BASE / model_info['folder']
        logger.info(f"  {model_info['folder']}/ ({model_info['name']})")

    logger.info(f"\nComparison report: {report_path}")
    logger.info("\nNext: Review outputs and update config/models_config.yaml")


if __name__ == "__main__":
    main()
