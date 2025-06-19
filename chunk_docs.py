# chunk_docs.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import json

raw_dir = Path("./raw_docs")
chunk_dir = Path("./chunks")
chunk_dir.mkdir(exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len
)

metadata_list = []

for path in raw_dir.glob("doc_*.txt"):
    text = path.read_text(encoding="utf-8")
    chunks = splitter.split_text(text)
    for idx, chunk in enumerate(chunks):
        fn = chunk_dir / f"{path.stem}_chunk_{idx:03d}.txt"
        fn.write_text(chunk, encoding="utf-8")
        metadata_list.append({
            "id": fn.stem,
            "source": str(path),
            "chunk_index": idx
        })
# Save metadata
with open("./chunks/metadata.json", "w") as mf:
    json.dump(metadata_list, mf)