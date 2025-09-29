from fastapi.testclient import TestClient
from sqlmodel import Session, select, desc
from typing import Optional
import uuid

from backend.models import Conversation, Message, Incident, KBDoc, IncidentStatus


# -------------------------
# Helper
# -------------------------
def send_message(client: TestClient, message: str, session_id: Optional[str] = None):
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    return client.post("/api/chat/message", json=payload)


# -------------------------
# Tests
# -------------------------
def test_new_conversation_creates_convo_and_messages(client: TestClient, session: Session):
    response = send_message(client, "Hello there!")
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "session_id" in data

    # Verify conversation persisted
    convo = session.exec(select(Conversation).where(Conversation.session_id == data["session_id"])).first()
    assert convo is not None

    # Verify messages persisted (user + bot)
    msgs = session.exec(select(Message).where(Message.conversation_id == convo.id)).all()
    assert len(msgs) == 2


def test_incident_report_flow_creates_incident(client: TestClient, session: Session):
    # Start incident report intent
    r1 = send_message(client, "I want to report an incident")
    session_id = r1.json()["session_id"]

    # Choose chat flow
    r2 = send_message(client, "chat", session_id=session_id)
    assert "title" in r2.json()["reply"].lower()

    # Provide title
    r3 = send_message(client, "Broken streetlight", session_id=session_id)
    assert "category" in r3.json()["reply"].lower()

    # Provide category
    r4 = send_message(client, "streetlight", session_id=session_id)
    assert "location" in r4.json()["reply"].lower()

    # Provide location
    r5 = send_message(client, "Main Street", session_id=session_id)
    assert "email" in r5.json()["reply"].lower()

    # Provide email
    r6 = send_message(client, "user@example.com", session_id=session_id)
    assert "description" in r6.json()["reply"].lower()

    # Provide description (final step)
    r7 = send_message(client, "It has been out for days", session_id=session_id)
    reply_text = r7.json()["reply"].lower()

    # Assert on the final reply
    assert "incident report" in reply_text or "incident id" in reply_text

    # Verify incident persisted
    incident = session.exec(
        select(Incident).order_by(desc(Incident.created_at))
    ).first()
    assert incident is not None
    assert incident.title == "Broken streetlight"
    assert incident.status == IncidentStatus.open


def test_status_check_flow(client: TestClient, session: Session):
    # Create an incident manually
    incident = Incident(
        public_id=f"TEST_{uuid.uuid4().hex[:8]}",
        title="Pothole",
        description="Large pothole",
        category="road",
        status=IncidentStatus.open,
    )
    session.add(incident)
    session.commit()

    # Ask for status
    r1 = send_message(client, "Check status")
    session_id = r1.json()["session_id"]
    r2 = send_message(client, "TEST123", session_id=session_id)

    assert "status of incident" in r2.json()["reply"]


def test_kb_query_returns_citations(client: TestClient, session: Session):
    # Add KB doc
    kb = KBDoc(title="Garbage Collection", body="Trash is collected every Monday.", source_url="http://kb.local/doc1")
    session.add(kb)
    session.commit()

    r = send_message(client, "When is trash collected?")
    data = r.json()
    assert "found" in data["reply"].lower()
    assert len(data["citations"]) >= 1
    assert data["citations"][0]["title"] == "Garbage Collection"


def test_fallback_reply_when_unclear(client: TestClient):
    r = send_message(client, "asldkfjweoiru")  # gibberish
    data = r.json()
    assert "clarify" in data["reply"].lower()
