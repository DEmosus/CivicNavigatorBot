import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.schemas import (
    RegisterIn, LoginIn, TokenOut, UserOut,
    ChatIn, ChatOut,
    IncidentCreate, IncidentCategory, IncidentCreated,
    IncidentStatusOut, StaffIncidentUpdateIn,
    KBSearchOut, KBSearchResultItem,
    HealthLive, HealthReady
)
from backend.models import Sender


# -------------------------
# Auth Schemas
# -------------------------
def test_register_in_valid_password():
    data = RegisterIn(email="user@example.com", password="StrongPass!1")
    assert data.email == "user@example.com"
    assert data.password == "StrongPass!1"
    assert data.is_staff is False


@pytest.mark.parametrize("bad_password", [
    "short1!",          # too short
    "alllowercase1!",   # missing uppercase
    "ALLUPPERCASE1!",   # missing lowercase
    "NoDigits!",        # missing digit
    "NoSpecial123"      # missing special char
])
def test_register_in_invalid_passwords(bad_password: str):
    with pytest.raises(ValidationError):
        RegisterIn(email="user@example.com", password=bad_password)


def test_login_in_requires_fields():
    data = LoginIn(email="user@example.com", password="Secret123!")
    assert data.email == "user@example.com"
    assert data.password == "Secret123!"


def test_token_out_defaults():
    token = TokenOut(access_token="abc123", is_staff=True)
    assert token.token_type == "bearer"
    assert token.is_staff is True


def test_user_out_serialization():
    now = datetime.now(timezone.utc)
    user = UserOut(id="u1", email="user@example.com", is_staff=False, created_at=now)
    assert user.created_at == now


# -------------------------
# Chat Schemas
# -------------------------
def test_chat_in_defaults():
    chat = ChatIn(message="Hello")
    assert chat.role == Sender.resident
    assert chat.session_id is None


def test_chat_out_defaults():
    out = ChatOut(reply="Hi there", session_id="sess1")
    assert out.citations == []
    assert out.confidence == 0.0
    assert out.session_id == "sess1"


# -------------------------
# Incident Schemas
# -------------------------
def test_incident_create_valid():
    inc = IncidentCreate(
        title="Pothole",
        description="Large pothole on Main St",
        category=IncidentCategory.ROAD_MAINTENANCE,
        contact_email="reporter@example.com"
    )
    assert inc.category == IncidentCategory.ROAD_MAINTENANCE


def test_incident_create_invalid_category():
    with pytest.raises(ValidationError):
        IncidentCreate(
            title="Bad",
            description="Invalid category",
            category="not_a_category"  # type: ignore[arg-type]
        )


def test_incident_created_fields():
    now = datetime.now(timezone.utc)
    created = IncidentCreated(incident_id="i1", status="new", created_at=now)
    assert created.incident_id == "i1"
    assert created.status == "new"
    assert created.created_at == now


def test_incident_status_out_defaults():
    now = datetime.now(timezone.utc)
    status = IncidentStatusOut(status="open", last_update=now)
    assert status.history == []


def test_staff_incident_update_in():
    upd = StaffIncidentUpdateIn(status="resolved", note="Fixed")
    assert upd.status == "resolved"
    assert upd.note == "Fixed"


# -------------------------
# KB Schemas
# -------------------------
def test_kbsearchout_defaults():
    out = KBSearchOut()
    assert out.results == []


def test_kbsearchresultitem():
    item = KBSearchResultItem(doc_id="d1", title="Doc", snippet="Snippet", score=0.9)
    assert item.score == 0.9


# -------------------------
# Health Schemas
# -------------------------
def test_healthlive_defaults():
    h = HealthLive()
    assert h.ok is True


def test_healthready_defaults():
    h = HealthReady()
    assert h.ok is True
    assert h.deps == {"db": True, "rag": True}
