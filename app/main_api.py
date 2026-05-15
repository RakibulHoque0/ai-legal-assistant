from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import shutil
import os
from dotenv import load_dotenv
from app.ocr_engine import OCREngine
from app.vector_store import VectorStore
from app.llm_client import LLMClient
from app.preferences import PreferenceManager

app = FastAPI()

# Initialize engines
load_dotenv()
tess_path = os.getenv("TESSERACT_PATH")
ocr = OCREngine(tesseract_path=tess_path)
vstore = VectorStore()
llm = LLMClient()
pref = PreferenceManager()

# Temp directory for uploads
UPLOAD_DIR = ".tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SummaryRequest(BaseModel):
    query: str

class EditRequest(BaseModel):
    original_draft: str
    final_edit: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process document
    result = ocr.extract_from_pdf(file_path)
    chunks = result["chunks"]
    
    # Store in FAISS
    vstore.create_index(chunks)
    vstore.save(".tmp/vector_db")
    
    return {
        "message": "Document processed", 
        "page_count": result["page_count"],
        "low_confidence_pages": result["low_confidence_pages"],
        "structured_fields": result["structured_fields"]
    }

@app.post("/summarize")
async def summarize(request: SummaryRequest):
    # Retrieve relevant chunks
    relevant_chunks = vstore.search(request.query, top_k=10)
    
    # Hallucination Control: Filter out very low relevance chunks if needed
    # (Distance logic can be added here if vstore.search is updated to return distances)
    
    if not relevant_chunks:
        return {"draft": "Insufficient evidence found in document to generate summary.", "chunks": []}
    
    # Generate draft
    draft = llm.generate_grounded_summary(relevant_chunks, pref.get_context_string())
    
    return {"draft": draft, "chunks": relevant_chunks}

@app.post("/learn")
async def learn_preferences(request: EditRequest):
    learning = llm.extract_preferences(request.original_draft, request.final_edit)
    pref.update_from_learning(learning)
    return {"message": "Preferences updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
