from fastapi.testclient import TestClient
from sqlmodel import Session, select
from typing import Dict, Any, Optional

from backend.models import User

# -------------------------
# Helpers
# -------------------------
def register_user(client: TestClient, email: str, password: str, full_name: str = "Test User"):
    payload: Dict[str, Any] = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "is_staff": False,
    }
    return client.post("/api/auth/register", json=payload)


def login_user(client: TestClient, email: str, password: str):
    payload: Dict[str, Any] = {"email": email, "password": password}
    return client.post("/api/auth/login", json=payload)


# -------------------------
# Tests
# -------------------------
def test_register_user_success(client: TestClient, session: Session):
    response = register_user(client, "newuser@example.com", "ValidPass1!")
    assert response.status_code == 200
    data = response.json()

    # Response should match TokenOut schema
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["is_staff"] is False

    # User should exist in DB
    db_user: Optional[User] = session.exec(select(User).where(User.email == "newuser@example.com")).first()
    assert db_user is not None
    assert db_user.full_name == "Test User"
    assert db_user.is_staff is False


def test_register_user_password_validation(client: TestClient):
    # Too short password
    response = register_user(client, "shortpass@example.com", "Ab1!")
    assert response.status_code == 422

    # Missing uppercase
    response = register_user(client, "noupper@example.com", "lowercase1!")
    assert response.status_code == 422

    # Missing lowercase
    response = register_user(client, "nolower@example.com", "UPPERCASE1!")
    assert response.status_code == 422

    # Missing digit
    response = register_user(client, "nodigit@example.com", "NoDigits!")
    assert response.status_code == 422

    # Missing special char
    response = register_user(client, "nospecial@example.com", "NoSpecial1")
    assert response.status_code == 422


def test_register_existing_user_conflict(client: TestClient, session: Session):
    # First registration
    r1 = register_user(client, "dupe@example.com", "ValidPass1!")
    assert r1.status_code == 200

    # Second registration with same email
    r2 = register_user(client, "dupe@example.com", "ValidPass1!")
    assert r2.status_code == 409  # Conflict


def test_login_success(client: TestClient, session: Session):
    email = "loginuser@example.com"
    password = "ValidPass1!"

    # Register first
    register_user(client, email, password)

    # Login
    response = login_user(client, email, password)
    assert response.status_code == 200
    data = response.json()

    # Should return a valid token
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    # Wrong password
    register_user(client, "wrongpass@example.com", "ValidPass1!")
    response = login_user(client, "wrongpass@example.com", "WrongPass1!")
    assert response.status_code == 401

    # Unknown email
    response = login_user(client, "unknown@example.com", "ValidPass1!")
    assert response.status_code == 401
