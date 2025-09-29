from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select # pyright: ignore[reportUnknownVariableType]

from backend.db import get_session
from backend.models import User
from backend.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Decode JWT and return the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        key = settings.JWT_SECRET_KEY
        assert key is not None, "JWT_SECRET_KEY is not set"
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        pass

    
    stmt = select(User).where(User.id == user_id) # pyright: ignore[reportUnknownMemberType]
    user = session.exec(stmt).first() # pyright: ignore[reportUnknownMemberType]
    if user is None:
        raise credentials_exception
    return user


def require_staff(user: User = Depends(get_current_user)) -> User:
    """Require that the user is staff."""
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required",
        )
    return user
