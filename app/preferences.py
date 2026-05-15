import json
import os

class PreferenceManager:
    def __init__(self, file_path="preferences.json"):
        self.file_path = file_path
        self.preferences = self.load()

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {"preferred_terms": {}, "formatting_notes": []}

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.preferences, f, indent=2)

    def update_from_learning(self, learning_json_str):
        """Update preferences with new insights from the LLM."""
        try:
            # Clean LLM response if it includes markdown blocks
            clean_json = learning_json_str.replace("```json", "").replace("```", "").strip()
            new_data = json.loads(clean_json)
            
            # Update terms
            self.preferences["preferred_terms"].update(new_data.get("preferred_terms", {}))
            
            # Add unique formatting notes
            for note in new_data.get("formatting_notes", []):
                if note not in self.preferences["formatting_notes"]:
                    self.preferences["formatting_notes"].append(note)
            
            self.save()
        except Exception as e:
            print(f"Error updating preferences: {e}")

    def get_context_string(self):
        """Return a string suitable for prompt injection."""
        return json.dumps(self.preferences)

if __name__ == "__main__":
    print("Preference Manager Initialized")
