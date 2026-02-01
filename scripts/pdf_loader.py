import fitz
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "documents.json"

documents = []

for pdf_path in PDF_DIR.glob("*.pdf"):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()

        if not text:
            continue

        documents.append({
            "content": text,
            "metadata": {
                "source": pdf_path.name,
                "page": page_num + 1
            }
        })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(documents, f, indent=2, ensure_ascii=False)

print(f"Loaded {len(documents)} pages.")