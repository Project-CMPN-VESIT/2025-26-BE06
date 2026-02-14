from sentence_transformers import SentenceTransformer
from pathlib import Path

# Paths from your code
PROJECT_ROOT = Path(__file__).parent
MODEL_PATH = PROJECT_ROOT / "models" / "models--sentence-transformers--all-MiniLM-L6-v2"

print("Loading model to re-save...")
# Load the model (this will trigger the warning one last time)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

print(f"Saving clean model to {MODEL_PATH}...")
# This re-saves the model in the format your current library version expects
model.save(str(MODEL_PATH))

print("Model successfully updated. You can delete this script.")