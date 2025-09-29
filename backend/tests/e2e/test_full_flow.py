import uuid
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlmodel import select, Session

from backend.models import Incident, IncidentStatus


# -------------------------
# Helpers
# -------------------------
def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_user(client: TestClient, email: str, password: str):
    payload: Dict[str, Any] = {
        "email": email,
        "password": password,
        "full_name": "E2E Resident",
        "is_staff": False,
    }
    return client.post("/api/auth/register", json=payload)


def login_user(client: TestClient, email: str, password: str):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def send_message(client: TestClient, message: str, session_id: str | None = None):
    payload: Dict[str, Any] = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    return client.post("/api/chat/message", json=payload)


# -------------------------
# E2E Happy Path
# -------------------------
def test_full_happy_path(client: TestClient, session: Session, staff_token: str):
    # --- 1. Resident registers & logs in ---
    email = f"resident_{uuid.uuid4()}@example.com"
    password = "StrongPass!1"

    r1 = register_user(client, email, password)
    assert r1.status_code == 200

    r2 = login_user(client, email, password)
    assert r2.status_code == 200
    resident_token = r2.json()["access_token"]
    assert resident_token

    # --- 2. Resident reports incident via chat ---
    r3 = send_message(client, "I want to report an incident")
    session_id = r3.json()["session_id"]

    send_message(client, "chat", session_id=session_id)
    send_message(client, "Broken streetlight", session_id=session_id)
    send_message(client, "street_lighting", session_id=session_id)
    send_message(client, "Main Street", session_id=session_id)
    send_message(client, "user@example.com", session_id=session_id)
    r_last = send_message(client, "It has been out for days", session_id=session_id)

    reply_text = r_last.json()["reply"].lower()
    assert "incident" in reply_text

    # Verify incident persisted
    incident = session.exec(select(Incident).order_by(Incident.created_at.desc())).first()
    assert incident is not None
    assert incident.title == "Broken streetlight"
    assert incident.status == IncidentStatus.open

    # --- 3. Resident checks incident status ---
    r_status = client.get(f"/api/incidents/{incident.public_id}/status")
    assert r_status.status_code == 200
    status_data = r_status.json()
    assert status_data["status"] == IncidentStatus.open.value

    # --- 4. Staff updates incident ---
    payload = {"status": "resolved"}
    r_update = client.patch(
        f"/api/staff/incidents/{incident.public_id}",
        json=payload,
        headers=auth_headers(staff_token),
    )
    assert r_update.status_code == 200
    assert r_update.json()["status"] == "resolved"

    # Verify DB updated
    session.refresh(incident)
    assert incident.status == IncidentStatus.resolved

    # --- 5. Resident checks status again ---
    r_status2 = client.get(f"/api/incidents/{incident.public_id}/status")
    assert r_status2.status_code == 200
    assert r_status2.json()["status"] == "resolved"

    # --- 6. Staff indexes and searches KB ---
    from backend.models import KBDoc

    doc = KBDoc(
        title="Garbage Collection",
        body="Trash is collected every Monday.",
        source_url="http://kb.local/doc1"
    )
    session.add(doc)
    session.commit()

    r_search = client.get("/api/staff/kb/search?query=trash", headers=auth_headers(staff_token))
    assert r_search.status_code == 200
    data = r_search.json()
    assert "results" in data
    assert any("trash" in r["title"].lower() or "trash" in r["snippet"].lower() for r in data["results"])
