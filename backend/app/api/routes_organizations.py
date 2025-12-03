from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=List[OrganizationRead], dependencies=[Depends(require_roles("platformAdmin"))])
async def list_organizations(db: AsyncSession = Depends(get_db)) -> List[OrganizationRead]:
    result = await db.execute(select(Organization))
    orgs = result.scalars().all()
    return [OrganizationRead.from_orm(org) for org in orgs]


@router.get("/me", response_model=Optional[OrganizationRead])
async def read_my_organization(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Optional[OrganizationRead]:
    if not current_user.organization_id:
        return None
    result = await db.execute(select(Organization).where(Organization.id == current_user.organization_id))
    org = result.scalars().first()
    return OrganizationRead.from_orm(org) if org else None


@router.put("/me", response_model=OrganizationRead)
async def update_my_org(
    payload: OrganizationCreate,
    current_user: User = Depends(require_roles("orgAdmin", "platformAdmin")),
    db: AsyncSession = Depends(get_db),
) -> OrganizationRead:
    org_id = current_user.organization_id
    if current_user.role == "orgAdmin" and not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No organization assigned")

    target_org_id = org_id or payload.dict().get("id")
    if not target_org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not found")

    result = await db.execute(select(Organization).where(Organization.id == target_org_id))
    org = result.scalars().first()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    org.name = payload.name
    org.slug = payload.slug
    org.primary_domain = payload.primary_domain
    await db.commit()
    await db.refresh(org)
    return OrganizationRead.from_orm(org)


@router.post("/", response_model=OrganizationRead, dependencies=[Depends(require_roles("platformAdmin"))])
async def create_organization(payload: OrganizationCreate, db: AsyncSession = Depends(get_db)) -> OrganizationRead:
    org = Organization(name=payload.name, slug=payload.slug, primary_domain=payload.primary_domain)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return OrganizationRead.from_orm(org)
