# db.py
from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from backend.settings import settings

# SQLite needs special connect args
connect_args = {"check_same_thread": False} if str(settings.DATABASE_URL).startswith("sqlite") else {}

# Engine
engine = create_engine(
    str(settings.DATABASE_URL),
    connect_args=connect_args,
    echo=(getattr(settings, "ENV", "development") == "development"),
)

# Session factory
SessionLocal = Session  # ✅ alias for type hints

def get_session() -> Generator[Session, None, None]:
    """Yields a SQLModel session (FastAPI dependency)."""
    with Session(engine) as session:
        yield session

def init_db() -> None:
    """
    Create tables (can be called from anywhere).
    Importing models ensures all SQLModel tables are registered before create_all().
    """
    from backend import models   # type: ignore  # intentional import for table registration
    SQLModel.metadata.create_all(bind=engine)
