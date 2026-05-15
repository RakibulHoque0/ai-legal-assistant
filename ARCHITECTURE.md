# Architecture Overview: Pearson Specter Litt Legal Assistant

## 1. Data Ingestion & OCR Layer (Layer 3)
The system employs a **Hybrid Extraction Strategy**:
- **Digital Parsing**: `PyMuPDF` attempts to extract text from the PDF's digital layer.
- **Visual OCR**: If digital text density is low (< 50 chars), the system triggers `pytesseract`.
- **Pre-processing**: Raw page images are processed via `OpenCV` to improve OCR accuracy:
    - `cv2.cvtColor`: Gray-scaling.
    - `cv2.GaussianBlur`: Noise reduction.
    - `cv2.threshold`: Otsu's binarization for high-contrast text.
- **Traceability Metadata**: During extraction, each page is assigned a sequential ID. This ID is attached to every downstream chunk.

## 2. Retrieval Layer (The Heart of Grounding)
- **Chunking**: Text is split into 1000-character segments with 100-character overlap to preserve semantic context.
- **Embeddings**: Uses `all-MiniLM-L6-v2` via `SentenceTransformers`. This model was chosen for its excellent balance of speed and legal-domain semantic understanding.
- **Vector Storage**: `FAISS` stores the embedded chunks locally.
- **Grounding Check**: The system uses a similarity distance threshold to filter out irrelevant material, ensuring the LLM only sees high-confidence evidence.

## 3. Edit-Learning Mechanism (The Intelligence Loop)
The system learns in 3 stages:
1. **Capture**: The UI sends both the `original_draft` and the user's `final_edit` to the backend.
2. **Analysis**: The LLM compares the two texts and identifies **Terminology** and **Style** shifts (e.g., from "agreed" to "undertook").
3. **Persistence**: Learned rules are saved to `preferences.json`.
4. **Injection**: On subsequent drafting tasks, these preferences are injected into the System Prompt to force stylistic alignment.

## 4. System Topology
- **Backend**: FastAPI (Async endpoints for non-blocking ingestion).
- **Frontend**: Streamlit (Reactive state management for the editing workflow).
