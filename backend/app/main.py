import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import routes_admin, routes_ai, routes_auth, routes_organizations, routes_settings, routes_topics, routes_users
from app.core.config import get_settings
from app.db.base import Base, import_models
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


def _normalize_allowed_domains(raw_domains: object) -> list[str]:
    if raw_domains is None:
        return []
    if isinstance(raw_domains, str):
        try:
            raw_domains = json.loads(raw_domains)
        except json.JSONDecodeError:
            raw_domains = [item.strip() for item in raw_domains.split(",")]
    if not isinstance(raw_domains, list):
        return []
    normalized = [str(domain).strip().lower() for domain in raw_domains if str(domain).strip()]
    return normalized


@app.on_event("startup")
async def on_startup() -> None:
    import_models()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    default_domains = _normalize_allowed_domains(settings.DEFAULT_ALLOWED_DOMAINS)
    if not default_domains:
        return

    async with AsyncSessionLocal() as session:  # type: AsyncSession
        existing = await session.execute(select(AllowedEmailDomain.domain))
        existing_domains = {row[0].lower() for row in existing if row[0]}
        missing = [d for d in default_domains if d not in existing_domains]
        if missing:
            session.add_all([AllowedEmailDomain(domain=domain) for domain in missing])
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to seed default allowed domains")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}
