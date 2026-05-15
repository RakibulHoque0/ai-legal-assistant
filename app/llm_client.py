import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_grounded_summary(self, chunks, preferences=None):
        """Generate a summary based ONLY on the provided chunks with page traceability."""
        
        # Format chunks for the prompt
        context = ""
        for i, chunk in enumerate(chunks):
            page = chunk.get("metadata", {}).get("page", "Unknown")
            context += f"--- CHUNK {i} (Page {page}) ---\n{chunk['text']}\n\n"
        
        # Inject preferences if available
        pref_str = ""
        if preferences:
            pref_str = f"\nUser Preferences:\n{preferences}\n"

        prompt = f"""
You are a legal assistant at Pearson Specter Litt. Generate a grounded case summary.

RULES:
1. Use ONLY the information in the context below.
2. If information is missing, say "Information not found in provided documents."
3. Cite every claim using the chunk index AND page number in brackets, e.g., [Chunk 14, Page 2].
4. Follow user terminology preferences if provided.{pref_str}

CONTEXT:
{context}

TASK:
Summarize the case facts including Parties, Key Events, and Important Clauses.
"""
        response = self.model.generate_content(prompt)
        return response.text

    def extract_preferences(self, ai_draft, user_edit):
        """Analyze the difference between draft and edit to learn preferences."""
        prompt = f"""
Compare the AI's draft with the User's final edit. Extract preferred terminology and formatting patterns.

AI DRAFT:
{ai_draft}

USER EDIT:
{user_edit}

Return a JSON object with:
"preferred_terms": {{ "old_term": "new_term" }},
"formatting_notes": ["note 1", "note 2"]
"""
        response = self.model.generate_content(prompt)
        return response.text

if __name__ == "__main__":
    print("LLM Client Initialized")
