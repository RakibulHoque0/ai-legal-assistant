import fitz  # PyMuPDF
import pytesseract
import re
from PIL import Image
import cv2
import numpy as np
import io
import os

class OCREngine:
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.lang = "eng" 

    def preprocess_image(self, image_bytes):
        """Enhance image for better OCR results."""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Noise reduction
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Thresholding (Otsu's binarization)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def extract_from_pdf(self, pdf_path):
        """Extract text and preserve page-level metadata."""
        doc = fitz.open(pdf_path)
        full_text = []
        page_chunks = []
        low_confidence_pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            is_ocr = False
            
            if len(text.strip()) < 50:
                is_ocr = True
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                processed_img = self.preprocess_image(img_bytes)
                data = pytesseract.image_to_data(processed_img, lang=self.lang, output_type=pytesseract.Output.DICT)
                text = " ".join([word for i, word in enumerate(data['text']) if int(data['conf'][i]) > -1])
                confidences = [int(c) for c in data['conf'] if int(c) > -1]
                avg_conf = sum(confidences) / len(confidences) if confidences else 0
                if avg_conf < 70:
                    low_confidence_pages.append(page_num + 1)
            
            # Create chunks for THIS page specifically
            chunks = self.chunk_text(text, page_num + 1)
            page_chunks.extend(chunks)
            full_text.append(text)
            
        combined_text = "\n".join(full_text)
        structured_fields = self.extract_structured_fields(combined_text)
        
        return {
            "full_text": combined_text,
            "chunks": page_chunks,
            "page_count": len(doc),
            "low_confidence_pages": low_confidence_pages,
            "structured_fields": structured_fields
        }

    def extract_structured_fields(self, text):
        """Robust extraction of legal fields."""
        fields = {
            "case_number": re.search(r"(Case No[:.]?\s?)([A-Z0-9\-]+)", text, re.I),
            "date": re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|([A-Z][a-z]+ \d{1,2}, \d{4})", text),
            "parties": re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text)
        }
        return {k: (v.group(0) if v else "Not found") for k, v in fields.items()}

    def chunk_text(self, text, page_number, chunk_size=1000, overlap=100):
        """Split text into chunks with page metadata and noise filtering."""
        # Filter out common web-print noise and garbled noscript tags
        garbage_patterns = [
            r"enable JavaScript", r"Jovatcsigt", r"ran Gis app",
            r"noscript", r"browser supports"
        ]
        for pattern in garbage_patterns:
            text = re.sub(pattern, "", text, flags=re.I)

        text = re.sub(r'\s+', ' ', text).strip()
        
        # Skip chunks that are just garbage or too short
        if len(text) < 20:
            return []

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            if len(chunk_text.strip()) > 50: # Only keep substantial chunks
                chunks.append({
                    "text": chunk_text,
                    "metadata": {"page": page_number}
                })
            start += chunk_size - overlap
        return chunks

if __name__ == "__main__":
    # Test script (placeholder)
    print("OCR Engine Initialized")
