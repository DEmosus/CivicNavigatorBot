# backend/schemas.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
import re
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field, field_validator

# Import Sender enum for consistency with models
from backend.models import Sender  

# ---------- Shared ----------
class Citation(BaseModel):
    title: str
    snippet: str
    source_link: Optional[str] = None


# ---------- Auth ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = ""          # frontend may send empty string
    is_staff: Optional[bool] = False       # frontend checkbox
    
    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_staff: bool


class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_staff: bool
    created_at: datetime


# ---------- Chat ----------
class ChatIn(BaseModel):
    message: str = Field(min_length=1)
    role: Optional[Sender] = Sender.resident
    session_id: Optional[str] = None          


class ChatOut(BaseModel):
    reply: str
    citations: List["Citation"] = Field(default_factory=list)
    confidence: float = 0.0
    session_id: str 


# ---------- Incidents ----------
class IncidentCategory(str, Enum):
    ROAD_MAINTENANCE = "road_maintenance"
    WASTE_MANAGEMENT = "waste_management"
    WATER_SUPPLY = "water_supply"
    ELECTRICITY = "electricity"
    STREET_LIGHTING = "street_lighting"
    DRAINAGE = "drainage"
    OTHER = "other"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    category: IncidentCategory
    location_text: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class IncidentCreated(BaseModel):
    incident_id: str
    status: str
    created_at: datetime


class IncidentHistoryItem(BaseModel):
    note: str
    status: str
    timestamp: datetime


class IncidentStatusOut(BaseModel):
    status: str
    last_update: datetime
    history: List["IncidentHistoryItem"] = Field(default_factory=list)


class StaffIncidentListItem(BaseModel):
    incident_id: str
    title: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    last_update: datetime


class StaffIncidentUpdateIn(BaseModel):
    status: str
    note: Optional[str] = None


# ---------- KB ----------
class KBSearchResultItem(BaseModel):
    doc_id: str
    title: str
    snippet: str
    score: float
    source_url: Optional[str] = None


class KBSearchOut(BaseModel):
    results: List["KBSearchResultItem"] = Field(default_factory=list)


# ---------- Health ----------
class HealthLive(BaseModel):
    ok: bool = True


class HealthReady(BaseModel):
    ok: bool = True
    deps: Dict[str, bool] = Field(default_factory=lambda: {"db": True, "rag": True})
