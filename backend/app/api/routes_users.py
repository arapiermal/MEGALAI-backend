from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


def _to_read(user: User) -> UserRead:
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


@router.get("/", response_model=List[UserRead], dependencies=[Depends(require_roles("platformAdmin"))])
async def list_users(db: AsyncSession = Depends(get_db)) -> List[UserRead]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [_to_read(user) for user in users]


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return _to_read(current_user)
