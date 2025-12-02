from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.settings import UserSettingsRead, UserSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _build_response(settings: UserSettings) -> UserSettingsRead:
    return UserSettingsRead(
        id=str(settings.id),
        user_id=str(settings.user_id),
        provider=settings.provider,
        model=settings.model,
        created_at=settings.created_at,
        updated_at=settings.updated_at,
        has_openai_api_key=bool(settings.openai_api_key),
        has_google_api_key=bool(settings.google_api_key),
        has_anthropic_api_key=bool(settings.anthropic_api_key),
        has_local_api_key=bool(settings.local_api_key),
    )


@router.get("/me", response_model=UserSettingsRead)
async def read_my_settings(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserSettingsRead:
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == current_user.id))
    settings = result.scalars().first()
    if settings is None:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return _build_response(settings)


@router.put("/me", response_model=UserSettingsRead)
async def update_my_settings(
    payload: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsRead:
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == current_user.id))
    settings = result.scalars().first()
    if settings is None:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return _build_response(settings)
