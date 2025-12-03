import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import routes_admin, routes_ai, routes_auth, routes_organizations, routes_settings, routes_topics, routes_users
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.models.allowed_email_domain import AllowedEmailDomain

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_users.router)
app.include_router(routes_organizations.router)
app.include_router(routes_topics.router)
app.include_router(routes_ai.router)
app.include_router(routes_settings.router)
app.include_router(routes_admin.router)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:  # type: AsyncSession
        existing = await session.execute(select(AllowedEmailDomain.domain))
        existing_domains = {row[0] for row in existing}
        missing = [d for d in settings.DEFAULT_ALLOWED_DOMAINS if d not in existing_domains]
        if missing:
            session.add_all([AllowedEmailDomain(domain=domain) for domain in missing])
            await session.commit()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}
