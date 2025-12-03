from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "MEGALAI Backend"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/megalai"

    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key",
        description="Secret key for signing access tokens. Override in production via env.",
    )
    JWT_REFRESH_SECRET_KEY: str = Field(
        default="dev-refresh-secret-key",
        description="Secret key for signing refresh tokens. Override in production via env.",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://megalai-frontend.netlify.app",
        ]
    )

    ENABLE_DOMAIN_RESTRICTION: bool = False
    DEFAULT_ALLOWED_DOMAINS: List[str] = Field(
        default_factory=lambda: ["umt.edu.al", "uniel.edu.al", "example.edu"]
    )

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
