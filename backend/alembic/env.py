from logging.config import fileConfig
from alembic import context
import os
import sys
from pathlib import Path

# --- Ensure backend/ is on sys.path ---
BASE_DIR = Path(__file__).resolve().parent.parent  # points to backend/
sys.path.append(str(BASE_DIR))

# --- Project imports ---
from backend.db import engine  # our SQLModel engine
import backend.models as models
from sqlmodel import SQLModel
from backend.settings import settings

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use SQLModel metadata so Alembic can autogenerate migrations
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection)."""
    url = str(settings.DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with DB connection)."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# --- Entry point ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
