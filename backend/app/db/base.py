from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models to ensure they are registered with SQLAlchemy metadata
from app.models.user import User  # noqa: E402,F401
from app.models.organization import Organization  # noqa: E402,F401
from app.models.allowed_email_domain import AllowedEmailDomain  # noqa: E402,F401
from app.models.user_settings import UserSettings  # noqa: E402,F401
from app.models.topic import Topic  # noqa: E402,F401
