from fastapi.testclient import TestClient
from sqlmodel import Session, select
from typing import Dict, Any, Optional
import uuid

from backend.models import User
from backend.utils.security import verify_password


# -------------------------
# Registration
# -------------------------
def test_register_new_user(client: TestClient, session: Session):
    email = f"newuser_{uuid.uuid4()}@example.com"
    payload: Dict[str, Any] = {
        "email": email,
        "password": "StrongPass!1",
        "full_name": "New User",
        "is_staff": False,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["is_staff"] is False

    # SQLModel query
    stmt = select(User).where(User.email == payload["email"])
    user: Optional[User] = session.exec(stmt).first()

    assert user is not None
    assert user.full_name == "New User"
    assert verify_password("StrongPass!1", user.hashed_password)


def test_register_existing_user(client: TestClient, session: Session, test_user: User):
    payload: Dict[str, Any] = {
        "email": test_user.email,
        "password": "AnotherPass!1",
        "full_name": "Duplicate",
        "is_staff": False,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists."


def test_register_invalid_password(client: TestClient):
    payload: Dict[str, Any] = {
        "email": "weakpass@example.com",
        "password": "short",
        "full_name": "Weak Pass",
        "is_staff": False,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


# -------------------------
# Login
# -------------------------
def test_login_valid_credentials(client: TestClient, test_user: User):
    payload: Dict[str, Any] = {"email": test_user.email, "password": "Password!1"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_nonexistent_user(client: TestClient):
    payload: Dict[str, Any] = {"email": "ghost@example.com", "password": "DoesNotExist1!"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
