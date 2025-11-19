"""
Iterative Document Improvement Pipeline

Reads enforcer results, identifies low-quality documents (<80% completeness),
and runs improvement iterations on them.

Flow:
1. Read enforcer logs (JSON) to find files needing improvement
2. Load structured files from data/structured/
3. Load original responsibility brief
4. Generate improved version with LLM
5. Save to data/generated/{model}-improved/
6. Run enforcer again on improved files
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directories to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "1_data_creation"))
sys.path.insert(0, str(PROJECT_ROOT / "2_data_processing"))

from scripts.enforce_structure import read_template_structure


# Configuration
COMPLETENESS_THRESHOLD = 80.0  # Minimum % to accept document
MAX_ITERATIONS = 3  # Maximum improvement iterations
TEMPLATE_PATH = PROJECT_ROOT / "2_data_processing/templates/input_template_hebrew.md"
STRUCTURED_DIR = PROJECT_ROOT / "data/structured/hebrew"
LOGS_DIR = PROJECT_ROOT / "logs"


def load_prompt_template(template_name):
    """Load prompt template from config folder"""
    template_path = PROJECT_ROOT / "1_data_creation/config" / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_enforcer_logs(log_file_path):
    """Read enforcer JSONL logs and return list of file metrics"""
    metrics_list = []

    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                metrics = json.loads(line)
                metrics_list.append(metrics)

    return metrics_list


def find_files_needing_improvement(metrics_list, threshold=COMPLETENESS_THRESHOLD):
    """
    Find files that need improvement (<threshold% completeness)
    Returns: list of (filename, model, metrics) tuples
    """
    needs_improvement = []

    for metrics in metrics_list:
        if metrics.get('status') != 'success':
            continue

        completeness = metrics.get('completeness', {}).get('completeness_percentage', 0)

        if completeness < threshold:
            needs_improvement.append({
                'original_file': metrics.get('original_file'),
                'output_file': metrics.get('output_file'),
                'model': metrics.get('model'),
                'subfolder': metrics.get('subfolder'),
                'completeness': completeness,
                'metrics': metrics
            })

    return needs_improvement


def load_responsibility_brief(original_filename):
    """
    Extract responsibility info from filename
    Format: res_{responsibility}_{model}_{number}.md
    """
    # Parse filename
    parts = original_filename.replace('.md', '').split('_')

    # Try to reconstruct responsibility name
    if len(parts) >= 2:
        responsibility = ' '.join(parts[1:-2])  # Skip 'res' and last two (model/number)
    else:
        responsibility = "Unknown"

    return {
        'name': responsibility.replace('_', ' ').title(),
        'area': 'Municipal Services',
        'context': f'Responsibility from {original_filename}'
    }


def build_improvement_prompt(structured_doc, responsibility_info):
    """Build improvement prompt from structured document"""

    prompt = f"""
You are improving a Hebrew document about municipal responsibilities.

DOCUMENT TO IMPROVE:
{structured_doc}

YOUR TASK:
Improve this document by filling empty sections and enriching content.

RULES:
1. KEEP section headers exactly as shown
2. KEEP section order
3. KEEP the "---" separators
4. Write ONLY in Hebrew
5. Fill sections marked [לא מולא]
6. Expand sections with thin content

DO NOT:
- Change section headers
- Reorder sections
- Add/remove sections
- Write in English

CONTEXT:
Responsibility: {responsibility_info['name']}
Area: {responsibility_info.get('area', 'N/A')}

Generate the improved document now.
"""
    return prompt


def improve_document(structured_file_path, original_filename, model_name, model_config):
    """
    Improve a single document that didn't meet quality threshold

    Args:
        structured_file_path: Path to structured .md file
        original_filename: Original filename for context
        model_name: LLM model to use
        model_config: Model configuration

    Returns:
        improved_document: String content
    """
    # Load structured document
    with open(structured_file_path, 'r', encoding='utf-8') as f:
        structured_doc = f.read()

    # Extract responsibility info
    responsibility_info = load_responsibility_brief(original_filename)

    # Build improvement prompt
    prompt = build_improvement_prompt(structured_doc, responsibility_info)

    # Generate improved version
    print(f"  Generating improved version with {model_name}...")
    improved_doc = generate_with_llm(prompt, model_name, model_config)

    return improved_doc


def generate_with_llm(prompt, model_name, model_config):
    """
    Call LLM to generate document
    Supports: Ollama (mistral, qwen, aya) and Claude API
    """
    import requests
    import json

    # Ollama models
    if model_name in ['mistral', 'qwen', 'aya']:
        print(f"Calling Ollama model: {model_name}...")

        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": model_config.get('temperature', 0.7),
                "num_predict": model_config.get('max_tokens', 4000)
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            raise

    # Claude API
    elif model_name == 'claude':
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic library not installed. Run: pip install anthropic")

        print("Calling Claude API...")

        client = Anthropic(api_key=model_config.get('api_key'))

        try:
            message = client.messages.create(
                model=model_config.get('model', 'claude-3-5-sonnet-20241022'),
                max_tokens=model_config.get('max_tokens', 4000),
                temperature=model_config.get('temperature', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise

    else:
        raise ValueError(f"Unknown model: {model_name}")


def run_improvement_pipeline(enforcer_log_path, model_configs):
    """
    Main pipeline: Read enforcer logs → Improve low-quality docs → Save

    Args:
        enforcer_log_path: Path to enforcer JSONL log file
        model_configs: Dict mapping model names to configuration dicts

    Returns:
        improvement_summary: Dict with statistics
    """
    print("="*80)
    print("ITERATIVE IMPROVEMENT PIPELINE")
    print("="*80)
    print(f"Reading enforcer logs from: {enforcer_log_path}")
    print(f"Threshold: {COMPLETENESS_THRESHOLD}% completeness")
    print()

    # Read enforcer logs
    metrics_list = read_enforcer_logs(enforcer_log_path)
    print(f"Loaded metrics for {len(metrics_list)} files")

    # Find files needing improvement
    needs_improvement = find_files_needing_improvement(metrics_list)
    print(f"Found {len(needs_improvement)} files below {COMPLETENESS_THRESHOLD}% threshold")
    print()

    if not needs_improvement:
        print("All files meet quality threshold!")
        return {'total': 0, 'improved': 0}

    # Group by model
    by_model = {}
    for file_info in needs_improvement:
        model = file_info['model']
        if model not in by_model:
            by_model[model] = []
        by_model[model].append(file_info)

    # Process each model
    improvement_summary = {'total': len(needs_improvement), 'improved': 0, 'failed': 0}

    for model_name, files in by_model.items():
        print("="*80)
        print(f"MODEL: {model_name.upper()} - {len(files)} files to improve")
        print("="*80)

        # Get model config
        model_config = model_configs.get(model_name, {'temperature': 0.7, 'max_tokens': 4000})

        # Create output directory
        output_dir = PROJECT_ROOT / "data/generated" / f"markdown-hebrew-{model_name}-improved"
        output_dir.mkdir(parents=True, exist_ok=True)

        for file_info in files:
            original_file = file_info['original_file']
            output_file = file_info['output_file']
            completeness = file_info['completeness']

            print(f"\nProcessing: {original_file}")
            print(f"  Current completeness: {completeness:.1f}%")

            # Find structured file
            structured_path = STRUCTURED_DIR / output_file

            if not structured_path.exists():
                print(f"  [ERROR] Structured file not found: {structured_path}")
                improvement_summary['failed'] += 1
                continue

            try:
                # Improve document
                improved_doc = improve_document(
                    structured_file_path=structured_path,
                    original_filename=original_file,
                    model_name=model_name,
                    model_config=model_config
                )

                # Save improved version
                output_path = output_dir / original_file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(improved_doc)

                print(f"  [OK] Saved improved version to: {output_path}")
                improvement_summary['improved'] += 1

            except Exception as e:
                print(f"  [FAIL] Error: {e}")
                improvement_summary['failed'] += 1

    # Summary
    print()
    print("="*80)
    print("IMPROVEMENT SUMMARY")
    print("="*80)
    print(f"Total files processed: {improvement_summary['total']}")
    print(f"Successfully improved: {improvement_summary['improved']}")
    print(f"Failed: {improvement_summary['failed']}")
    print()
    print("Next step: Run enforcer again on improved files to check quality")
    print()

    return improvement_summary


def main():
    """Run improvement pipeline on latest enforcer logs"""

    # Find latest enforcer log
    log_files = sorted(LOGS_DIR.glob("structure_enforcement_*.jsonl"))
    if not log_files:
        print("ERROR: No enforcer log files found in logs/")
        print("Run enforce_structure.py first!")
        return

    latest_log = log_files[-1]
    print(f"Using latest log: {latest_log.name}\n")

    # Model configurations
    model_configs = {
        'mistral': {'temperature': 0.7, 'max_tokens': 4000},
        'qwen': {'temperature': 0.7, 'max_tokens': 4000},
        'aya': {'temperature': 0.7, 'max_tokens': 4000},
        'claude': {
            'model': 'claude-3-5-sonnet-20241022',
            'temperature': 0.7,
            'max_tokens': 4000,
            # 'api_key': 'your-key'  # Add if using Claude
        }
    }

    # Run improvement pipeline
    summary = run_improvement_pipeline(latest_log, model_configs)


if __name__ == "__main__":
    main()
