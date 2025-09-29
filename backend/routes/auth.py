from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.db import get_session
from backend.models import User, UserRole
from backend.schemas import RegisterIn, LoginIn, TokenOut
from backend.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, session: Session = Depends(get_session)) -> TokenOut:
    """
    Register a new user. Returns a JWT token if successful.
    """
    stmt = select(User).where(User.email == payload.email.lower())
    existing: Optional[User] = session.exec(stmt).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name or "",
        hashed_password=hash_password(payload.password),
        is_staff=payload.is_staff or False,
        role=UserRole.staff if payload.is_staff else UserRole.resident,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(
        data={"sub": str(user.id), "role": "staff" if user.is_staff else "resident"}
    )
    return TokenOut(
        access_token=token,
        token_type="bearer",
        is_staff=user.is_staff,
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, session: Session = Depends(get_session)) -> TokenOut:
    """
    Authenticate a user and return a JWT token.
    """
    stmt = select(User).where(User.email == payload.email.lower())
    user: Optional[User] = session.exec(stmt).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(
        data={"sub": str(user.id), "role": "staff" if user.is_staff else "resident"}
    )
    return TokenOut(
        access_token=token,
        token_type="bearer",
        is_staff=user.is_staff,
    )
