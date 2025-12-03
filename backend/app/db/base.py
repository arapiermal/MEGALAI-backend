from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def import_models() -> None:
    """Import all model modules to register them with SQLAlchemy metadata."""

    from app.models import (  # noqa: F401
        allowed_email_domain,
        organization,
        topic,
        user,
        user_settings,
    )


__all__ = ["Base", "import_models"]
