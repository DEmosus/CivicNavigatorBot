def score_text(query: str, text: str) -> float:
    """Naive scoring: overlap of query words in text."""
    q_tokens = set(query.lower().split())
    t_tokens = set(text.lower().split())
    if not q_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


def best_snippet(query: str, text: str, window: int = 20) -> str:
    """Return a small snippet around the first query word match."""
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in query.lower():
            start = max(0, i - window // 2)
            end = min(len(words), i + window // 2)
            return " ".join(words[start:end])
    return " ".join(words[:window])
