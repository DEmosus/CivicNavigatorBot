# populate_kb.py
import json
from typing import Generator, List, cast
import numpy as np
from numpy.typing import NDArray
from backend.db import engine, init_db, Session
from backend.models import KBDoc, KBChunk
from sentence_transformers import SentenceTransformer

# Init DB + embedding model
init_db()
db: Session = Session(engine)
embedder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

# Example civic knowledge entries
entries: List[dict[str, str]] = [
    {
        "title": "Trash Collection Schedule",
        "body": "Trash collection happens every Monday and Thursday at 8am in residential areas.",
    },
    {
        "title": "Water Service Outages",
        "body": "Residents can expect scheduled water maintenance on the first Saturday of every month between 10am and 4pm.",
    },
    {
        "title": "Streetlight Repairs",
        "body": "Report broken or flickering streetlights through the incident reporting system. Repairs are usually done within 5 working days.",
    },
    {
        "title": "Noise Complaints",
        "body": "Noise complaints can be filed through the city hotline or the incident report form online.",
    },
]

def chunk_text(text: str, max_len: int = 300) -> Generator[str, None, None]:
    """Naive chunker to split long text into smaller pieces for embeddings."""
    words: List[str] = text.split()
    for i in range(0, len(words), max_len):
        yield " ".join(words[i : i + max_len])

for entry in entries:
    doc = KBDoc(title=entry["title"], body=entry["body"])
    db.add(doc)
    db.commit()
    db.refresh(doc)

    for chunk in chunk_text(entry["body"]):
        embedding_vector: NDArray[np.float32] = cast(
            NDArray[np.float32],
            embedder.encode(chunk, convert_to_numpy=True)  # type: ignore
        )
        embedding_json: str = json.dumps(embedding_vector.tolist())
        kb_chunk = KBChunk(doc_id=doc.id, text=chunk, embedding=embedding_json)
        db.add(kb_chunk)

db.commit()
db.close()
print("✅ KB populated with civic service entries")
