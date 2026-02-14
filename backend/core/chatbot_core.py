import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

VECTOR_DIR = PROJECT_ROOT / "vectorstore" / "faiss"
CHUNKS_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"
MODEL_PATH = PROJECT_ROOT / "models" / "models--sentence-transformers--all-MiniLM-L6-v2"

index = faiss.read_index(str(VECTOR_DIR / "index.faiss"))

with open(VECTOR_DIR / "metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("Loading embedding model...")
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=str(PROJECT_ROOT / "models")
)
print("Embedding model loaded.")

SYSTEM_PROMPT = """
You are a MahaRERA legal assistant.
Answer ONLY using the provided context.
If the answer is not present, say you do not know.
Answer concisely using only the provided context.
Do not invent legal references or section numbers.
"""

def ask(question, history=None, k=2):

    if history is None:
        history = []

    q_emb = model.encode([question], normalize_embeddings=True)
    D, I = index.search(np.array(q_emb), k)

    if len(I[0]) == 0:
        return "Information not found in the provided documents.", []

    context = ""
    sources = []

    for idx in I[0]:
        if idx == -1:
            continue

        chunk_obj = chunks[idx]

        chunk_text = chunk_obj["content"]
        pdf_name = chunk_obj["metadata"]["source"]
        page_number = chunk_obj["metadata"]["page"]

        context += chunk_text + "\n"

        sources.append({
            "pdf": pdf_name,
            "page": page_number,
            "link": f"/pdfs/{pdf_name}#page={page_number}"
        })

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({
        "role": "user", 
        "content": f"Context:\n{context}\n\nFollow-up Question: {question}"
    })

    response = ollama.chat(
        model="deepseek-r1:1.5b",
        options={"temperature": 0.7},
        messages=messages
    )

    return response["message"]["content"], sources