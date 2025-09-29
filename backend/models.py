from enum import Enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, Integer, String, Text, event
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.engine import Connection
from sqlalchemy.orm import DeclarativeBase, Mapper  # type: ignore
from sqlmodel import Field, Relationship, SQLModel  # type: ignore


# ---------- Pure SQLAlchemy Base ----------
class Base(DeclarativeBase):  # type: ignore
    """Base class for pure SQLAlchemy models (non-SQLModel)."""
    __abstract__ = True


# ---------- Pure SQLAlchemy Table ----------
class KnowledgeBaseArticle(Base):
    """Legacy knowledge base article table (pure SQLAlchemy)."""
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)


# ---------- Enums ----------
class UserRole(str, Enum):
    resident = "resident"
    staff = "staff"


class IncidentStatus(str, Enum):
    new = "new"
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class Sender(str, Enum):
    resident = "resident"
    staff = "staff"
    system = "system"
    bot = "bot"


# ---------- User ----------
class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = Field(default=None)
    is_staff: bool = False
    role: UserRole = UserRole.resident
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    conversations: List["Conversation"] = Relationship(back_populates="user")


# ---------- Chat ----------
class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="user.id", index=True)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pending_intent: Optional[str] = Field(default=None)

    state: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )

    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


# ---------- Messages ----------
class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    sender: Sender
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    conversation: "Conversation" = Relationship(back_populates="messages")


# ---------- Incidents ----------
class Incident(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    public_id: str = Field(index=True, unique=True)
    title: str
    description: str
    category: str
    location_text: Optional[str] = Field(default=None)
    contact_email: Optional[str] = Field(default=None)
    priority: Optional[str] = Field(default=None)
    status: IncidentStatus = Field(default=IncidentStatus.new)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    history: List["IncidentHistory"] = Relationship(back_populates="incident")


# ---------- Auto-update `updated_at` ----------
@event.listens_for(Incident, "before_update", propagate=True)  # type: ignore
def update_timestamp(mapper: Mapper, connection: Connection, target: Incident) -> None:
    target.updated_at = datetime.now(timezone.utc)


# ---------- Incident History ----------
class IncidentHistory(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    incident_id: str = Field(foreign_key="incident.id", index=True)
    status: IncidentStatus
    note: Optional[str] = Field(default=None)
    actor_user_id: Optional[str] = Field(default=None, foreign_key="user.id", index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    incident: "Incident" = Relationship(back_populates="history")


# ---------- Knowledge Base Docs ----------
class KBDoc(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    body: str
    source_url: Optional[str] = Field(default=None)

    chunks: List["KBChunk"] = Relationship(back_populates="doc")


class KBChunk(SQLModel, table=True):
    """
    A chunk of text from a knowledge base document, with its embedding stored
    as a JSON-encoded list of floats.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    doc_id: str = Field(foreign_key="kbdoc.id", index=True)
    text: str
    embedding: Optional[str] = Field(
        default=None,
        description="JSON-encoded list[float] representing the embedding vector"
    )

    doc: "KBDoc" = Relationship(back_populates="chunks")

    # --- Helper methods ---
    def set_embedding(self, vector: List[float]) -> None:
        """Serialize and store an embedding vector."""
        import json
        self.embedding = json.dumps(vector)

    def get_embedding(self) -> Optional[List[float]]:
        """Deserialize the stored embedding JSON string."""
        import json
        return json.loads(self.embedding) if self.embedding else None
