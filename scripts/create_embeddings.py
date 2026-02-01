import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
model = SentenceTransformer("all-MiniLM-L6-v2", token=hf_token)

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"
VECTOR_DIR = PROJECT_ROOT / "vectorstore" / "faiss_index"

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["content"] for c in chunks]
embeddings = model.encode(texts, show_progress_bar=True)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

VECTOR_DIR.mkdir(parents=True, exist_ok=True)
faiss.write_index(index, str(VECTOR_DIR / "index.faiss"))

with open(VECTOR_DIR / "metadata.json", "w", encoding="utf-8") as f:
    json.dump([c["metadata"] for c in chunks], f, indent=2)

print("FAISS index created.")