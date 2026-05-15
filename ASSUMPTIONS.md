# Assumptions & Tradeoffs

## 🔍 Assumptions
1. **Document Integrity**: Assumes documents are not password-protected or encrypted.
2. **Standard Legal Language**: Assumes standard Latin-character based English.
3. **Hardware**: Assumes a standard Windows workstation environment for Tesseract execution.

## ⚖️ Tradeoffs

### 1. FAISS vs. Hosted Vector DBs (Pinecone/Weaviate)
- **Tradeoff**: FAISS is local/memory-resident; Pinecone is cloud-based.
- **Decision**: Chose **FAISS**.
- **Rationale**: Legal documents are highly sensitive. Keeping the vector index local ensures that firm data never resides on third-party vector servers, satisfying strict compliance and security requirements.

### 2. SentenceTransformers vs. OpenAI Embeddings
- **Tradeoff**: Local inference vs. API-based embeddings.
- **Decision**: **SentenceTransformers (all-MiniLM-L6-v2)**.
- **Rationale**: Local embedding generation is free, works offline, and keeps the extraction pipeline entirely within the firm's infrastructure until the final drafting stage.

### 3. Heuristic vs. LLM-Based Field Extraction
- **Tradeoff**: Precision vs. Speed.
- **Decision**: **Heuristic Regex**.
- **Rationale**: For common fields like "Case No" and "Date", regex is 100x faster and 100% deterministic. This frees up the LLM's "thinking time" for the complex task of drafting the case summary.

### 4. Rule-Based Learning vs. RLHF
- **Tradeoff**: Simplicity of implementation vs. deep neural adaptation.
- **Decision**: **Rule-Based Preference Extraction**.
- **Rationale**: For an MVP, we need to show immediate improvement from edits. Rule-based preference extraction (LLM analyzing the diff) provides a visible, inspectable `preferences.json` that the user can verify, whereas an RLHF approach would be opaque and require massive data.
