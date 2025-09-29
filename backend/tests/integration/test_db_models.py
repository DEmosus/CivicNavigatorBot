from sqlmodel import Session, select
import time

from backend.models import (
    User,
    Conversation,
    Message,
    Incident,
    IncidentHistory,
    IncidentStatus,
    Sender,
    UserRole,
    KBDoc,
    KBChunk,
)


def test_user_and_conversation_relationship(session: Session):
    user = User(email="user@example.com", hashed_password="hashed", role=UserRole.resident)
    convo = Conversation(user=user, pending_intent="incident_report_flow", state={"step": "title"})
    session.add(user)
    session.add(convo)
    session.commit()

    # Reload and check relationship
    db_user = session.exec(select(User).where(User.email == "user@example.com")).first()
    assert db_user is not None
    assert len(db_user.conversations) == 1
    assert db_user.conversations[0].pending_intent == "incident_report_flow"

    # JSON state should persist
    assert db_user.conversations[0].state["step"] == "title"


def test_message_relationship(session: Session):
    convo = Conversation()
    msg1 = Message(conversation_id=convo.id, sender=Sender.resident, text="Hello")
    msg2 = Message(conversation_id=convo.id, sender=Sender.bot, text="Hi there!")
    session.add(convo)
    session.add(msg1)
    session.add(msg2)
    session.commit()

    db_convo = session.exec(select(Conversation).where(Conversation.id == convo.id)).first()
    assert db_convo is not None
    assert len(db_convo.messages) == 2
    assert {m.sender for m in db_convo.messages} == {Sender.resident, Sender.bot}


def test_incident_and_history(session: Session):
    inc = Incident(
        public_id="TEST123",
        title="Broken pipe",
        description="Water leak",
        category="water_supply",
        status=IncidentStatus.new,
    )
    session.add(inc)
    session.commit()

    hist = IncidentHistory(incident_id=inc.id, status=IncidentStatus.new, note="Created")
    session.add(hist)
    session.commit()

    db_inc = session.exec(select(Incident).where(Incident.public_id == "TEST123")).first()
    assert db_inc is not None
    assert db_inc.status == IncidentStatus.new
    assert len(db_inc.history) == 1
    assert db_inc.history[0].note == "Created"


def test_incident_updated_at_auto_updates(session: Session):
    inc = Incident(
        public_id="TEST456",
        title="Streetlight out",
        description="Lamp not working",
        category="street_lighting",
        status=IncidentStatus.open,
    )
    session.add(inc)
    session.commit()

    old_updated = inc.updated_at
    time.sleep(0.01)  # ensure timestamp difference
    inc.status = IncidentStatus.resolved
    session.add(inc)
    session.commit()

    db_inc = session.exec(select(Incident).where(Incident.public_id == "TEST456")).first()
    assert db_inc.updated_at > old_updated


def test_kbdoc_and_chunks(session: Session):
    doc = KBDoc(title="Garbage Collection", body="Trash is collected weekly.")
    chunk = KBChunk(doc_id=doc.id, text="Trash is collected every Monday.")
    chunk.set_embedding([0.1, 0.2, 0.3])
    session.add(doc)
    session.add(chunk)
    session.commit()

    db_doc = session.exec(select(KBDoc).where(KBDoc.id == doc.id)).first()
    assert db_doc is not None
    assert len(db_doc.chunks) == 1
    db_chunk = db_doc.chunks[0]
    assert db_chunk.get_embedding() == [0.1, 0.2, 0.3]
