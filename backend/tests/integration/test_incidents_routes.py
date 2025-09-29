from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlmodel import Session, select
import uuid

from backend.models import Incident, IncidentHistory, IncidentStatus


# -------------------------
# Helpers
# -------------------------
def create_incident_payload(**overrides: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "title": "Broken pipe",
        "description": "Water leaking on the street",
        "category": "water_supply",
        "location_text": "Main Street",
        "contact_email": "user@example.com",
    }
    payload.update(overrides)
    return payload


# -------------------------
# Tests
# -------------------------
def test_create_incident_success(client: TestClient, session: Session):
    payload = create_incident_payload()
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Response fields
    assert "incident_id" in data
    assert len(data["incident_id"]) == 8  # public_id length
    assert data["status"] == IncidentStatus.new.value

    # DB check
    inc = session.exec(select(Incident).where(Incident.public_id == data["incident_id"])).first()
    assert inc is not None
    assert inc.title == "Broken pipe"
    assert inc.status == IncidentStatus.new

    # History check
    hist = session.exec(select(IncidentHistory).where(IncidentHistory.incident_id == inc.id)).all()
    assert len(hist) == 1
    assert hist[0].note == "Incident created"


def test_create_incident_validation_error(client: TestClient):
    # Missing required description
    payload = create_incident_payload()
    del payload["description"]

    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 422


def test_get_status_existing_incident(client: TestClient, session: Session):
    # Create incident manually
    inc = Incident(
        public_id=f"TEST_{uuid.uuid4().hex[:8]}",
        title="Streetlight out",
        description="Lamp not working",
        category="street_lighting",
        status=IncidentStatus.open,
    )
    session.add(inc)
    session.commit()

    # Add history
    hist = IncidentHistory(incident_id=inc.id, status=IncidentStatus.open, note="Initial report")
    session.add(hist)
    session.commit()

    response = client.get(f"/api/incidents/{inc.public_id}/status")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == IncidentStatus.open.value
    assert len(data["history"]) >= 1
    assert data["history"][0]["note"] == "Initial report"


def test_get_status_unknown_incident(client: TestClient):
    response = client.get("/api/incidents/UNKNOWN99/status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown incident ID"
