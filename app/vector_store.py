import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []

    def create_index(self, chunks):
        """Convert text chunks to embeddings and store in FAISS."""
        # chunks is now a list of dicts: [{"text": "...", "metadata": {...}}, ...]
        texts = [c["text"] for c in chunks]
        embeddings = self.model.encode(texts)
        dimension = embeddings.shape[1]
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store metadata (entire dicts) for retrieval
        self.metadata = chunks

    def search(self, query, top_k=5):
        """Retrieve the most relevant chunks with their metadata."""
        if self.index is None:
            return []
        
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                res = self.metadata[idx].copy()
                res["chunk_index"] = int(idx)
                res["distance"] = float(distances[0][i])
                results.append(res)
        return results

    def save(self, path):
        """Save the index and metadata to disk."""
        if not os.path.exists(path):
            os.makedirs(path)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self, path):
        """Load the index and metadata from disk."""
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "metadata.pkl"), "rb") as f:
            self.metadata = pickle.load(f)

if __name__ == "__main__":
    # Test script
    print("Vector Store Initialized")
