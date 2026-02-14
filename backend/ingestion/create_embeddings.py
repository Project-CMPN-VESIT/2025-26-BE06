import json
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

CHUNKS_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"
VECTOR_DIR = PROJECT_ROOT / "vectorstore" / "faiss"

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=str(PROJECT_ROOT / "models")
)

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["content"] for c in chunks]

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    normalize_embeddings=True,
    convert_to_numpy=True
)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

VECTOR_DIR.mkdir(parents=True, exist_ok=True)
faiss.write_index(index, str(VECTOR_DIR / "index.faiss"))

with open(VECTOR_DIR / "metadata.json", "w", encoding="utf-8") as f:
    json.dump([c["metadata"] for c in chunks], f, indent=2)

print("FAISS index created.")