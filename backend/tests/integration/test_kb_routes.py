from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from backend import models


# -------------------------
# Helpers
# -------------------------
def create_kb_entry_payload(**overrides: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "question": "When is trash collected?",
        "answer": "Trash is collected every Monday.",
    }
    payload.update(overrides)
    return payload


# -------------------------
# Tests
# -------------------------
def test_kb_health(client: TestClient):
    response = client.get("/api/kb/health")
    assert response.status_code == 200
    assert response.json() == {"status": "KB router OK"}


def test_index_kb_entry(client: TestClient, session: Session):
    payload = create_kb_entry_payload()
    response = client.post("/api/kb/index", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Response should contain the KB entry
    assert data["id"] is not None
    assert data["question"] == payload["question"]
    assert data["answer"] == payload["answer"]

    # DB check
    db_entry = session.exec(
        select(models.KnowledgeBaseArticle).where(models.KnowledgeBaseArticle.id == data["id"])
    ).first()
    assert db_entry is not None
    assert db_entry.question == payload["question"]
    assert db_entry.answer == payload["answer"]


def test_search_kb_success(client: TestClient, session: Session):
    # Insert KB entry directly
    article = models.KnowledgeBaseArticle(
        question="How to pay water bill?",
        answer="You can pay your water bill online or at the city office."
    )
    session.add(article)
    session.commit()

    response = client.get("/api/kb/search?q=water")
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert len(data["results"]) >= 1
    assert any("water" in r["question"].lower() or "water" in r["answer"].lower() for r in data["results"])


def test_search_kb_no_results(client: TestClient):
    response = client.get("/api/kb/search?q=nonexistenttopic")
    assert response.status_code == 404
    assert response.json()["detail"] == "No KB articles found"
