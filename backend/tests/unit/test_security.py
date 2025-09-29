import pytest
import time
from datetime import timedelta
from jose import JWTError
from _pytest.monkeypatch import MonkeyPatch

from backend.utils import security
from backend.models import UserRole
from backend.settings import Settings


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def settings() -> Settings:
    """Provide a fresh Settings instance with test secrets."""
    return Settings(
        ENV="development",
        JWT_SECRET_KEY="testsecret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRE_MINUTES=1,  # default 1 minute
    )


# -------------------------
# Password hashing
# -------------------------
def test_password_hash_and_verify():
    password = "StrongPass!1"
    hashed = security.hash_password(password)
    assert hashed != password
    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrongpass", hashed) is False


# -------------------------
# JWT creation & decoding
# -------------------------
def test_create_and_decode_jwt(settings: Settings):
    token = security.create_access_token(
        data={"sub": "user123", "role": UserRole.resident.value},
        settings=settings,
    )
    decoded = security.decode_access_token(token, settings=settings)
    assert decoded["sub"] == "user123"
    assert decoded["role"] == UserRole.resident.value


def test_jwt_missing_sub_claim(settings: Settings):
    token = security.create_access_token(
        data={"role": UserRole.staff.value}, settings=settings
    )
    decoded = security.decode_access_token(token, settings=settings)
    assert "sub" not in decoded


def test_jwt_invalid_signature(settings: Settings):
    token = security.create_access_token(
        data={"sub": "user123"}, settings=settings
    )
    # Tamper with token
    tampered = token + "abc"
    with pytest.raises(JWTError):
        security.decode_access_token(tampered, settings=settings)


# -------------------------
# Expiry handling
# -------------------------
def test_jwt_expiry(settings: Settings):
    # Create a token that expires in 1 second
    token = security.create_access_token(
        data={"sub": "user123"}, settings=settings, expires_delta=timedelta(seconds=1)
    )
    time.sleep(2)  # wait until expired
    with pytest.raises(JWTError):
        security.decode_access_token(token, settings=settings)


def test_jwt_future_expiry(settings: Settings):
    token = security.create_access_token(
        data={"sub": "user123"}, settings=settings, expires_delta=timedelta(minutes=5)
    )
    decoded = security.decode_access_token(token, settings=settings)
    assert decoded["sub"] == "user123"


# -------------------------
# Role enforcement
# -------------------------
def test_extract_role_from_token(settings: Settings):
    token = security.create_access_token(
        data={"sub": "user123", "role": UserRole.staff.value}, settings=settings
    )
    decoded = security.decode_access_token(token, settings=settings)
    role = decoded.get("role")
    assert role == UserRole.staff.value


def test_invalid_role_in_token(settings: Settings):
    token = security.create_access_token(
        data={"sub": "user123", "role": "invalid_role"}, settings=settings
    )
    decoded = security.decode_access_token(token, settings=settings)
    assert decoded["role"] == "invalid_role"  # schema doesn’t enforce enum here


# -------------------------
# Edge cases
# -------------------------
def test_missing_jwt_secret_key(monkeypatch: MonkeyPatch):
    """Ensure error is raised if JWT_SECRET_KEY is missing."""
    bad_settings = Settings(
        ENV="development",
        JWT_SECRET_KEY=None,
        JWT_ALGORITHM="HS256",
        JWT_EXPIRE_MINUTES=1,
    )
    with pytest.raises(RuntimeError):
        security.create_access_token(data={"sub": "user123"}, settings=bad_settings)


def test_unsupported_algorithm(settings: Settings):
    """Ensure error is raised if algorithm mismatch occurs."""
    # Encode with HS256 (default settings)
    token = security.create_access_token(data={"sub": "user123"}, settings=settings)

    # Try decoding with a settings object that expects HS512
    bad_settings = Settings(
        ENV="development",
        JWT_SECRET_KEY="testsecret",
        JWT_ALGORITHM="HS512",  # mismatch
        JWT_EXPIRE_MINUTES=1,
    )

    with pytest.raises(JWTError):
        security.decode_access_token(token, settings=bad_settings)
