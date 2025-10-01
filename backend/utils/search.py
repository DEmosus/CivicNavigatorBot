# backend/utils/search.py

import json
from typing import List, Optional
import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

# Load the embedding model once
_embedder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(vec_a: NDArray[np.float32], vec_b: NDArray[np.float32]) -> float:
    """Compute cosine similarity between two vectors."""
    denom: float = float(np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def score_text(query: str, embeddings_json: List[Optional[str]]) -> float:
    """
    Compute the maximum semantic similarity between the query
    and a list of KB chunk embeddings (JSON-encoded).
    """
    if not query.strip():
        return 0.0

    # Explicitly cast to NDArray[np.float32] for type checker
    query_vec: NDArray[np.float32] = np.array(
        _embedder.encode(query, convert_to_numpy=True, normalize_embeddings=False),
        dtype=np.float32,
    )


    max_score: float = 0.0
    for emb_json in embeddings_json:
        if not emb_json:
            continue
        try:
            vec: NDArray[np.float32] = np.array(json.loads(emb_json), dtype=np.float32)
            sim = cosine_similarity(query_vec, vec)
            max_score = max(max_score, sim)
        except Exception:
            continue

    return max_score


def best_snippet(query: str, text: str, window: int = 20) -> str:
    """
    Return a snippet of text around the most relevant word in the KB entry.
    Falls back to the first `window` words if no match is found.
    """
    words = text.split()
    query_tokens = {tok.strip(".,?!") for tok in query.lower().split()}

    for i, word in enumerate(words):
        if word.lower().strip(".,?!") in query_tokens:
            start = max(0, i - window // 2)
            end = min(len(words), i + window // 2)
            return " ".join(words[start:end])

    return " ".join(words[:window])
