from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel, ConfigDict
from typing import List

from backend.db import get_session
from backend import models

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])


# --- Schemas ---
class KBEntry(BaseModel):
    id: int | None = None
    question: str
    answer: str

    model_config = ConfigDict(from_attributes=True)


class KBSearchResponse(BaseModel):
    results: List[KBEntry]


# --- Routes ---

@router.get("/health")
def kb_health() -> dict[str, str]:
    return {"status": "KB router OK"}


@router.get("/search", response_model=KBSearchResponse)
def search_kb(q: str, session: Session = Depends(get_session)) -> KBSearchResponse:
    """
    Naive search in SQLite (LIKE query).
    Later we’ll swap in embeddings.
    """
    results = session.exec(
        select(models.KnowledgeBaseArticle).where(
            models.KnowledgeBaseArticle.question.ilike(f"%{q}%")
            | models.KnowledgeBaseArticle.answer.ilike(f"%{q}%")
        )
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No KB articles found")

    return KBSearchResponse(results=results)


@router.post("/index", response_model=KBEntry)
def index_kb(entry: KBEntry, session: Session = Depends(get_session)) -> KBEntry:
    """
    Insert KB entry into the database.
    """
    article = models.KnowledgeBaseArticle(
        question=entry.question,
        answer=entry.answer,
    )
    session.add(article)
    session.commit()
    session.refresh(article)
    return article
