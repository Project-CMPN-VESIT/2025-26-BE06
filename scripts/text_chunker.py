import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "documents.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    docs = json.load(f)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = []

for doc in docs:
    splits = splitter.split_text(doc["content"])
    for chunk in splits:
        chunks.append({
            "content": chunk,
            "metadata": doc["metadata"]
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"Created {len(chunks)} chunks.")