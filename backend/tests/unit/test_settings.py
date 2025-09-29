import pytest
from pydantic import ValidationError
from _pytest.monkeypatch import MonkeyPatch

from backend.settings import Settings


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture(autouse=True)
def clear_env(monkeypatch: MonkeyPatch):
    """
    Ensure environment variables are cleared between tests
    so each test starts fresh.
    """
    for key in [
        "ENV",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "JWT_EXPIRE_MINUTES",
        "CORS_ORIGINS",
        "SENTRY_DSN",
        "AI_PROVIDER",
        "AI_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)
    yield


# -------------------------
# Default values
# -------------------------
def test_defaults_load_in_development(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENV", "development")
    s = Settings()
    assert s.ENV == "development"
    assert s.JWT_ALGORITHM == "HS256"
    assert s.JWT_EXPIRE_MINUTES == 60 * 24
    assert isinstance(s.CORS_ORIGINS, list)


# -------------------------
# CORS_ORIGINS parsing
# -------------------------
def test_cors_origins_parses_comma_separated(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com,http://b.com")
    s = Settings()
    assert s.CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_parses_json_list(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("CORS_ORIGINS", '["http://a.com", "http://b.com"]')
    s = Settings()
    assert s.CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_accepts_list_direct(monkeypatch: MonkeyPatch):
    # Simulate passing a list directly (rare, but supported)
    s = Settings(CORS_ORIGINS=["http://a.com", "http://b.com"])
    assert s.CORS_ORIGINS == ["http://a.com", "http://b.com"]


# -------------------------
# JWT_SECRET_KEY enforcement
# -------------------------
def test_jwt_secret_required_in_production(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_jwt_secret_optional_in_development(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    s = Settings()
    assert s.JWT_SECRET_KEY is None


# -------------------------
# DATABASE_URL enforcement
# -------------------------
def test_database_url_required_in_production(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./dev.db")  # fallback dev DB
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    with pytest.raises(ValidationError):
        Settings()


def test_database_url_allows_custom_in_production(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@host:5432/db")
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    s = Settings()
    assert "postgresql" in str(s.DATABASE_URL)


# -------------------------
# Optional values
# -------------------------
def test_optional_values_load(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("SENTRY_DSN", "")
    monkeypatch.setenv("AI_PROVIDER", "none")
    s = Settings()
    assert s.SENTRY_DSN in (None, "")
    assert s.AI_PROVIDER == "none"
