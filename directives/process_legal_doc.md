# Directive: Legal Document Processing

## Goal
Transform messy, scanned, or digital legal PDFs into clean, indexed text chunks ready for vector storage.

## Input
- PDF files (scanned or digital)
- Image files (notices, photos of documents)

## Steps

### 1. Extraction (Layer 3: `ocr_engine.py`)
- Attempt digital extraction using `PyMuPDF`.
- If text is missing or garbled, use `pytesseract` OCR.
- For blurry images, apply OpenCV pre-processing:
    - Grayscale conversion
    - Noise reduction (Gaussian Blur)
    - Thresholding (Otsu's binarization)

### 2. Cleanup
- Remove excessive whitespace and page numbers.
- Preserve case numbers, dates, and party names.
- Identify "low confidence" OCR zones.

### 3. Chunking
- Use a sliding window approach.
- Chunk size: ~500 tokens (or ~1500 characters).
- Overlap: ~10% (50 tokens).
- Each chunk MUST retain metadata: `original_page`, `chunk_index`, `source_file`.

## Outputs
- `processed_text`: Full cleaned text.
- `chunks`: List of metadata-tagged text segments.
- `ocr_confidence`: Confidence scores for UI display.

## Edge Cases
- **Handwritten notes**: Tesseract may fail; flag as "Manual Review Needed".
- **Multi-column documents**: Ensure extraction reads top-to-bottom, left-to-right correctly.
- **Redacted text**: Preserve [REDACTED] markers.
