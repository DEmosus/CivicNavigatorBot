from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.db import get_session
from backend.utils.helpers import generate_public_id
from backend.models import Incident, IncidentHistory, IncidentStatus
from backend.schemas import (
    IncidentCreate,
    IncidentCreated,
    IncidentStatusOut,
    IncidentHistoryItem,
)

router = APIRouter(prefix="/api", tags=["incidents"])


@router.post("/incidents", response_model=IncidentCreated)
def create_incident(payload: IncidentCreate, session: Session = Depends(get_session)):
    public_id = generate_public_id()
    now = datetime.now(timezone.utc)

    inc = Incident(
        public_id=public_id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        location_text=payload.location_text,
        contact_email=payload.contact_email,
        status=IncidentStatus.new,
        created_at=now,
        updated_at=now,
    )
    session.add(inc)
    session.flush()  # need inc.id for history

    hist = IncidentHistory(
        incident_id=inc.id,
        status=IncidentStatus.new,
        note="Incident created",
        actor_user_id=None,
        timestamp=now,
    )
    session.add(hist)
    session.commit()
    session.refresh(inc)

    return IncidentCreated(
        incident_id=inc.public_id,
        status=inc.status.value,
        created_at=inc.created_at,
    )


@router.get("/incidents/{public_id}/status", response_model=IncidentStatusOut)
def get_status(public_id: str, session: Session = Depends(get_session)):
    # ✅ Modern SQLModel query
    inc = session.exec(select(Incident).where(Incident.public_id == public_id)).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Unknown incident ID")

    history = (
        session.exec(
            select(IncidentHistory)
            .where(IncidentHistory.incident_id == inc.id)
            .order_by(IncidentHistory.timestamp)
        ).all()
    )

    items = [
        IncidentHistoryItem(
            note=h.note,
            status=h.status.value,
            timestamp=h.timestamp,
        )
        for h in history
    ]

    last_update = items[-1].timestamp if items else inc.updated_at

    return IncidentStatusOut(
        status=inc.status.value,
        last_update=last_update,
        history=items,
    )
