# Directive: Grounded Legal Drafting

## Goal
Generate a case summary based EXCLUSIVELY on retrieved evidence. Prevent hallucinations and ensure every claim is traceable.

## Inputs
- `retrieved_chunks`: Top N relevant segments from FAISS.
- `user_query`: The specific summary request (e.g., "Summarize the key events").
- `preferences`: User terminology and formatting rules.

## Generation Rules

### 1. Strict Grounding
- Use ONLY information from the `retrieved_chunks`.
- If a fact is requested but not present in the chunks, explicitly state: "Evidence for [fact] not found in the provided documents."
- NEVER use external knowledge (e.g., "In typical legal cases...").

### 2. Citations
- Every statement must be followed by a citation in brackets, e.g., `[Chunk 14]`.
- If multiple chunks support a claim, list them: `[Chunk 14, Chunk 22]`.

### 3. Formatting
- Use Markdown headers (`##`).
- Use bullet points for facts.
- Apply user preferences from `preferences.json` (e.g., "executed" instead of "signed").

## Output
- `legal_summary`: The structured, cited summary.
- `citation_map`: A mapping of citations to original text snippets for the UI "Inspect" feature.

## Hallucination Check
- Before returning, cross-reference each bullet point against the `retrieved_chunks`.
- If a bullet point cannot be mapped back to a specific chunk, it must be removed or flagged.
