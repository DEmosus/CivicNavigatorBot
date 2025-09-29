from fastapi.testclient import TestClient
from sqlmodel import Session, select
import re
import uuid

from backend.models import Incident, IncidentHistory, IncidentStatus


# -------------------------
# Helpers
# -------------------------
def is_valid_public_id(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]{8}", value))


# -------------------------
# Tests
# -------------------------
def test_create_incident_success(client: TestClient, session: Session):
    payload = {
        "title": "Broken pipe",
        "description": "Water leaking on the street",
        "category": "water_supply",
        "location_text": "Main Street",
        "contact_email": "user@example.com",
    }
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Validate response
    assert "incident_id" in data
    assert is_valid_public_id(data["incident_id"])
    assert data["status"] == IncidentStatus.new.value

    # Validate DB
    inc = session.exec(select(Incident).where(Incident.public_id == data["incident_id"])).first()
    assert inc is not None
    assert inc.title == "Broken pipe"
    assert inc.status == IncidentStatus.new

    # History should be created
    hist = session.exec(select(IncidentHistory).where(IncidentHistory.incident_id == inc.id)).all()
    assert len(hist) == 1
    assert hist[0].note == "Incident created"


def test_create_incident_validation_error(client: TestClient):
    # Missing required fields (description)
    payload = {
        "title": "Incomplete incident",
        "category": "road_maintenance",
    }
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 422  # validation error


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
    hist = IncidentHistory(
        incident_id=inc.id,
        status=IncidentStatus.open,
        note="Initial report",
    )
    session.add(hist)
    session.commit()

    response = client.get(f"/api/incidents/{inc.public_id}/status")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == IncidentStatus.open.value
    assert len(data["history"]) >= 1
    assert data["history"][0]["note"] == "Initial report"


def test_get_status_unknown_incident(client: TestClient):
    response = client.get("/api/incidents/UNKNOWN123/status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown incident ID"
