# Iterative Improvement Prompt Template

Generic prompt template for refining documents that don't meet quality criteria.

---

## Purpose

After enforcement, if document doesn't meet threshold (e.g., <80% completeness), use this prompt to guide the model to improve content while maintaining structure.

---

## Base Prompt Template

```
You are improving a Hebrew document about municipal responsibilities.

DOCUMENT TO IMPROVE:
{document_content}

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
{responsibility_context}

Generate the improved document now.
```

---

## Variables for Function

- `{document_content}` - The enforced document
- `{responsibility_context}` - Context about the responsibility (name, area, focus)

---

## Implementation

```python
def build_improvement_prompt(document_content, responsibility_context):
    """Build improvement prompt from template"""
    template = load_prompt_template("creation_iteration_prompt.md")

    return template.format(
        document_content=document_content,
        responsibility_context=responsibility_context
    )
```

---

## Optional Additions

For multiple iterations, functions can append:
- Weak sections list
- Previous metrics
- Iteration count

Keep base template generic, add specifics programmatically.
