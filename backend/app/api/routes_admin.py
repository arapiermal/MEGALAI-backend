from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.core.config import get_settings
from app.core.security import hash_password
from app.models.allowed_email_domain import AllowedEmailDomain
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()


def _user_to_read(user: User) -> UserRead:
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


@router.post("/organizations", response_model=OrganizationRead, dependencies=[Depends(require_roles("platformAdmin"))])
async def create_organization(payload: OrganizationCreate, db: AsyncSession = Depends(get_db)) -> OrganizationRead:
    org = Organization(name=payload.name, slug=payload.slug, primary_domain=payload.primary_domain)
    db.add(org)
    await db.commit()
    await db.refresh(org)

    if payload.primary_domain:
        existing_domain = await db.execute(
            select(AllowedEmailDomain).where(AllowedEmailDomain.domain == payload.primary_domain)
        )
        if not existing_domain.scalars().first():
            domain_entry = AllowedEmailDomain(domain=payload.primary_domain, organization_id=org.id)
            db.add(domain_entry)
            await db.commit()

    return OrganizationRead.from_orm(org)


@router.post("/org-admins", response_model=UserRead, dependencies=[Depends(require_roles("platformAdmin"))])
async def create_org_admin(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserRead:
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    if not payload.organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization required")

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="orgAdmin",
        organization_id=payload.organization_id,
        current_organization_id=payload.organization_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _user_to_read(user)


def _resolve_org_id(payload_org: Optional[str], current_user: User) -> Optional[str]:
    if payload_org:
        return payload_org
    if current_user.role == "orgAdmin":
        return current_user.organization_id
    return None


@router.post(
    "/professors", response_model=UserRead, dependencies=[Depends(require_roles("orgAdmin", "platformAdmin"))]
)
async def create_professor(
    payload: RegisterRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> UserRead:
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    org_id = _resolve_org_id(payload.organization_id, current_user)
    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="professor",
        organization_id=org_id,
        current_organization_id=org_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _user_to_read(user)


@router.post(
    "/students", response_model=UserRead, dependencies=[Depends(require_roles("orgAdmin", "platformAdmin"))]
)
async def create_student(
    payload: RegisterRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> UserRead:
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    org_id = _resolve_org_id(payload.organization_id, current_user)
    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="student",
        organization_id=org_id,
        current_organization_id=org_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _user_to_read(user)


@router.get("/organizations", response_model=List[dict], dependencies=[Depends(require_roles("platformAdmin"))])
async def admin_list_orgs(db: AsyncSession = Depends(get_db)) -> List[dict]:
    result = await db.execute(select(Organization))
    orgs = result.scalars().all()
    response: List[dict] = []
    for org in orgs:
        response.append(
            {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "primary_domain": org.primary_domain,
                "user_count": 0,
            }
        )
    return response


@router.get("/users", response_model=List[UserRead], dependencies=[Depends(require_roles("orgAdmin", "platformAdmin"))])
async def admin_list_users(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> List[UserRead]:
    stmt = select(User)
    if current_user.role == "orgAdmin":
        stmt = stmt.where(User.organization_id == current_user.organization_id)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [_user_to_read(user) for user in users]
