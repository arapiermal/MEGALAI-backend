from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.allowed_email_domain import AllowedEmailDomain
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    Token,
)
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _build_user_read(user: User) -> UserRead:
    return UserRead(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
        current_organization_id=str(user.current_organization_id)
        if user.current_organization_id
        else None,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/register", response_model=UserRead)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> Any:
    domain = request.email.split("@")[-1]
    if settings.ENABLE_DOMAIN_RESTRICTION:
        result = await db.execute(
            select(AllowedEmailDomain).where(
                AllowedEmailDomain.domain == domain, AllowedEmailDomain.active.is_(True)
            )
        )
        allowed = result.scalars().first()
        if not allowed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email domain not allowed")

    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    new_user = User(
        email=request.email,
        name=request.name,
        password_hash=hash_password(request.password),
        role="student",
        organization_id=request.organization_id,
        current_organization_id=request.organization_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return _build_user_read(new_user)


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "org": str(user.current_organization_id) if user.current_organization_id else None,
    }
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_build_user_read(user),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Any:
    token_payload = decode_token(body.refresh_token, is_refresh=True)
    result = await db.execute(select(User).where(User.id == token_payload.sub))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "org": str(user.current_organization_id) if user.current_organization_id else None,
    }
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return Token(access_token=access_token, refresh_token=refresh_token, user=_build_user_read(user))


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return _build_user_read(current_user)
