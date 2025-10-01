import json
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from backend.models import Incident, IncidentHistory, IncidentStatus, KBDoc, KBChunk
from backend.utils.search import _embedder  # reuse the same embedder


# -------------------------
# Helpers
# -------------------------
def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# -------------------------
# Tests
# -------------------------
def test_list_incidents_returns_results(client: TestClient, session: Session, staff_token: str):
    # Create sample incidents
    inc1 = Incident(public_id="STAFF1", title="Pothole", description="Large pothole", category="road")
    inc2 = Incident(public_id="STAFF2", title="Streetlight", description="Broken light", category="lighting")
    session.add(inc1)
    session.add(inc2)
    session.commit()

    response = client.get("/api/staff/incidents", headers=auth_headers(staff_token))
    assert response.status_code == 200
    data: List[Dict[str, Any]] = response.json()

    assert isinstance(data, list)
    assert any(inc["incident_id"] == "STAFF1" for inc in data)
    assert any(inc["incident_id"] == "STAFF2" for inc in data)


def test_update_incident_status_success(client: TestClient, session: Session, staff_token: str):
    inc = Incident(
        public_id="UPD123",
        title="Water leak",
        description="Pipe burst",
        category="water",
        status=IncidentStatus.open,
    )
    session.add(inc)
    session.commit()

    payload = {"status": "resolved"}
    response = client.patch(
        f"/api/staff/incidents/{inc.public_id}",
        json=payload,
        headers=auth_headers(staff_token),
    )
    assert response.status_code == 200
    data = response.json()

    assert data["incident_id"] == "UPD123"
    assert data["status"] == "resolved"

    # DB check
    db_inc = session.exec(select(Incident).where(Incident.public_id == "UPD123")).first()
    assert db_inc.status == IncidentStatus.resolved

    # History check
    hist = session.exec(select(IncidentHistory).where(IncidentHistory.incident_id == db_inc.id)).all()
    assert any(h.status == IncidentStatus.resolved for h in hist)


def test_update_incident_invalid_status(client: TestClient, session: Session, staff_token: str):
    inc = Incident(
        public_id="BADSTATUS",
        title="Graffiti",
        description="Wall painted",
        category="cleaning",
        status=IncidentStatus.open,
    )
    session.add(inc)
    session.commit()

    payload = {"status": "not_a_real_status"}
    response = client.patch(
        f"/api/staff/incidents/{inc.public_id}",
        json=payload,
        headers=auth_headers(staff_token),
    )
    assert response.status_code == 422


def test_update_incident_not_found(client: TestClient, staff_token: str):
    payload = {"status": "resolved"}
    response = client.patch(
        "/api/staff/incidents/UNKNOWN",
        json=payload,
        headers=auth_headers(staff_token),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown incident ID"


def test_staff_kb_search_returns_results(client: TestClient, session: Session, staff_token: str):
    # Create KB doc
    doc = KBDoc(
        title="Garbage Collection",
        body="Trash is collected every Monday.",
        source_url="http://kb.local/doc1"
    )
    session.add(doc)
    session.commit()

    # Add a chunk with embedding so search can find it
    vec = _embedder.encode(doc.body, convert_to_numpy=True).tolist()
    chunk = KBChunk(doc_id=doc.id, text=doc.body, embedding=json.dumps(vec))
    session.add(chunk)
    session.commit()

    response = client.get("/api/staff/kb/search?query=trash", headers=auth_headers(staff_token))
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert len(data["results"]) >= 1
    assert any("Garbage Collection" in r["title"] for r in data["results"])


def test_staff_kb_search_no_results(client: TestClient, staff_token: str):
    response = client.get("/api/staff/kb/search?query=nonexistent", headers=auth_headers(staff_token))
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
