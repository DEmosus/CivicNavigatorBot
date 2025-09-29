from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy import desc

from backend.db import get_session
from backend.models import Incident, IncidentHistory, IncidentStatus, KBDoc
from backend.schemas import (
    StaffIncidentListItem,
    StaffIncidentUpdateIn,
    KBSearchOut,
    KBSearchResultItem,
)
from backend.deps import require_staff
from backend.utils.search import score_text, best_snippet

router = APIRouter(prefix="/api/staff", tags=["staff"])


# ---- Incidents ----
@router.get("/incidents", response_model=list[StaffIncidentListItem])
def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    staff_user: Any = Depends(require_staff),  # keep staff context for audit/logging
) -> list[StaffIncidentListItem]:
    """List all incidents with their latest update timestamp, paginated."""
    offset = (page - 1) * page_size
    rows = session.exec(
        select(Incident).offset(offset).limit(page_size)
    ).all()

    out: list[StaffIncidentListItem] = []

    for inc in rows:
        # find latest history item for last_update
        h = session.exec(
            select(IncidentHistory)
            .where(IncidentHistory.incident_id == inc.id)
            .order_by(desc(IncidentHistory.timestamp))
        ).first()

        last_ts = h.timestamp if h else inc.updated_at

        out.append(
            StaffIncidentListItem(
                incident_id=inc.public_id,
                title=inc.title,
                category=inc.category,
                description=inc.description,
                status=inc.status.value
                if isinstance(inc.status, IncidentStatus)
                else str(inc.status),
                created_at=inc.created_at,
                last_update=last_ts,
            )
        )
    return out


@router.patch("/incidents/{public_id}")
def update_incident(
    public_id: str,
    payload: StaffIncidentUpdateIn,
    session: Session = Depends(get_session),
    staff_user: Any = Depends(require_staff),
) -> dict[str, str]:
    """Update an incident’s status and record the change in history."""
    inc = session.exec(select(Incident).where(Incident.public_id == public_id)).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Unknown incident ID")

    try:
        new_status = IncidentStatus(payload.status)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid status")

    inc.status = new_status
    inc.updated_at = datetime.now(timezone.utc)

    # record history
    hist = IncidentHistory(
        incident_id=inc.id,
        status=new_status,
        note=f"Status changed to {new_status.value}",
        actor_user_id=getattr(staff_user, "id", None),
        timestamp=inc.updated_at,
    )
    session.add(hist)
    session.commit()

    return {
        "incident_id": inc.public_id,
        "status": inc.status.value,
        "last_update": inc.updated_at.isoformat(),
    }


# ---- KB ----
@router.get("/kb/search", response_model=KBSearchOut)
def kb_search(
    query: str = Query("", description="Search query string"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session),
    _: Any = Depends(require_staff),
) -> dict[str, list[KBSearchResultItem]]:
    """Search the staff knowledge base using a simple scoring algorithm, paginated."""
    q = query.strip()
    if not q:
        return {"results": []}

    results: list[tuple[str, str, float, str | None]] = []
    docs = session.exec(select(KBDoc)).all()

    for d in docs:
        # score whole doc
        text = f"{d.title}\n{d.body}"
        score = score_text(q, text)
        if score > 0:
            results.append((str(d.id), d.title, score, d.source_url))

        # score chunks if present
        for ch in getattr(d, "chunks", []) or []:
            cscore = score_text(q, ch.text)
            if cscore > 0:
                results.append((str(d.id), d.title, cscore, d.source_url))

    results.sort(key=lambda r: r[2], reverse=True)

    out: list[KBSearchResultItem] = []
    seen: set[tuple[str, str]] = set()

    start = (page - 1) * page_size
    end = start + page_size

    for doc_id, title, score, src in results[start:end]:
        if (doc_id, title) in seen:
            continue
        seen.add((doc_id, title))

        doc = next((x for x in docs if str(x.id) == doc_id), None)
        snippet_source = (doc.body if doc else "")[:2000]

        out.append(
            KBSearchResultItem(
                doc_id=doc_id,
                title=title,
                snippet=best_snippet(snippet_source, q),
                score=float(score),
                source_url=src,
            )
        )

    return {"results": out}
