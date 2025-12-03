from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.topic import Topic
from app.models.user import User
from app.schemas.topic import TopicCreate, TopicRead, TopicListResponse

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/", response_model=TopicListResponse)
async def list_topics(
    organization_id: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)
) -> TopicListResponse:
    stmt = select(Topic)
    if organization_id:
        stmt = stmt.where(Topic.organization_id == organization_id)
    result = await db.execute(stmt)
    topics = result.scalars().all()
    return TopicListResponse(topics=[TopicRead.from_orm(topic) for topic in topics])


@router.post("/", response_model=TopicRead)
async def create_topic(
    payload: TopicCreate,
    current_user: User = Depends(require_roles("professor", "orgAdmin", "platformAdmin")),
    db: AsyncSession = Depends(get_db),
) -> TopicRead:
    org_id = payload.organization_id or current_user.organization_id
    topic = Topic(
        title=payload.title,
        description=payload.description,
        organization_id=org_id,
        created_by_user_id=current_user.id,
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return TopicRead.from_orm(topic)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: str,
    current_user: User = Depends(require_roles("orgAdmin", "platformAdmin")),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalars().first()
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    if current_user.role == "orgAdmin" and current_user.organization_id != topic.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete topic outside your org")
    await db.delete(topic)
    await db.commit()
    return None
