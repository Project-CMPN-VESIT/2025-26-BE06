import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
VECTOR_DIR = PROJECT_ROOT / "vectorstore" / "faiss_index"
CHUNKS_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"

index = faiss.read_index(str(VECTOR_DIR / "index.faiss"))

with open(VECTOR_DIR / "metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

SYSTEM_PROMPT = """
You are a MahaRERA legal assistant.
Answer ONLY using the provided context.
If the answer is not present, say you do not know.
Always cite source and page number.
"""

def ask(question, k=5):
    q_emb = model.encode([question])
    D, I = index.search(np.array(q_emb), k)

    context = ""
    sources = []

    for idx in I[0]:
        context += chunks[idx]["content"] + "\n\n"
        sources.append(metadata[idx])

    response = ollama.chat(
        model="deepseek-r1:1.5b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )

    return response["message"]["content"], sources

while True:
    q = input("\nAsk MahaRERA chatbot (type 'exit'): ")
    if q.lower() == "exit":
        break

    answer, srcs = ask(q)
    print("\nAnswer:\n", answer)
    print("\nSources:")
    for s in srcs:
        print(f"- {s['source']} | Page {s['page']}")
