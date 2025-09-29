import os
# Mark environment as testing
os.environ["TESTING"] = "1"
os.environ["JWT_SECRET_KEY"] = "testsecret"

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.engine import Engine
from collections.abc import Generator

from backend.db import get_session
from backend.settings import Settings
from backend.utils.security import create_access_token, hash_password
from backend.models import User, UserRole
from backend.main import app


# -------------------------
# Test Database Setup
# -------------------------
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        ENV="test",
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="testsecret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRE_MINUTES=5,
    )


@pytest.fixture(scope="session")
def engine(test_settings: Settings) -> Engine:
    connect_args = {"check_same_thread": False}
    engine: Engine = create_engine(
        "sqlite:///./test.db",
        connect_args=connect_args,
        echo=False,
    )
    from backend import models
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    # Create pure SQLAlchemy tables (like KnowledgeBaseArticle)
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# -------------------------
# FastAPI Test Client
# -------------------------
@pytest.fixture
def client(engine: Engine, session: Session):
    def _get_test_session():
        yield session

    # Ensure schema exists for this session
    SQLModel.metadata.create_all(engine)
    from backend import models
    models.Base.metadata.create_all(engine)

    app.dependency_overrides[get_session] = _get_test_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# -------------------------
# Test Data Fixtures
# -------------------------
@pytest.fixture
def test_user(session: Session) -> User:
    user = User(
        email=f"resident_{uuid.uuid4()}@example.com",
        hashed_password=hash_password("Password!1"),
        full_name="Resident One",
        role=UserRole.resident,
        is_staff=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_staff(session: Session) -> User:
    user = User(
        email=f"staff_{uuid.uuid4()}@example.com",
        hashed_password=hash_password("Password!1"),
        full_name="Staff One",
        role=UserRole.staff,
        is_staff=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# -------------------------
# JWT Fixtures
# -------------------------
@pytest.fixture
def resident_token(test_user: User, test_settings: Settings) -> str:
    return create_access_token(
        data={"sub": str(test_user.id), "role": UserRole.resident.value},
        settings=test_settings,
    )


@pytest.fixture
def staff_token(test_staff: User, test_settings: Settings) -> str:
    return create_access_token(
        data={"sub": str(test_staff.id), "role": UserRole.staff.value},
        settings=test_settings,
    )
