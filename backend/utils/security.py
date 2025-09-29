from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from backend.settings import Settings, settings
from backend.models import UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# Password utilities
# -------------------------
def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(password, hashed)


# -------------------------
# JWT utilities
# -------------------------
def create_access_token(
    data: dict[str, Any],
    settings: Settings = settings,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT access token from arbitrary claims.
    - data: dict of claims (e.g. {"sub": user_id, "role": "resident"})
    - settings: Settings instance (allows test injection)
    - expires_delta: optional timedelta override
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    key = settings.JWT_SECRET_KEY
    if not key:
        raise RuntimeError("JWT_SECRET_KEY is not set")
    return jwt.encode(to_encode, key, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str, settings: Settings = settings) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError if invalid or expired.
    """
    try:
        key = settings.JWT_SECRET_KEY
        assert key is not None, "JWT_SECRET_KEY is not set"
        payload = jwt.decode(token, key, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise JWTError("Token has expired")
    except JWTError as e:
        raise JWTError(f"Invalid token: {e}")


def get_user_id_from_token(token: str, settings: Settings = settings) -> str:
    """Extract user ID (sub) from a JWT token."""
    payload = decode_access_token(token, settings=settings)
    sub = payload.get("sub")
    if not sub:
        raise JWTError("Token missing subject claim")
    return sub


def get_user_role_from_token(token: str, settings: Settings = settings) -> UserRole:
    """Extract user role from a JWT token."""
    payload = decode_access_token(token, settings=settings)
    role = payload.get("role")
    if not role:
        raise JWTError("Token missing role claim")
    try:
        return UserRole(role)
    except ValueError:
        raise JWTError(f"Invalid role claim: {role}")
