from typing import Literal

from pydantic import field_validator
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: Literal["development", "test", "production"] = "production"
    DEBUG: bool = False

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    GROQ_API_KEY: str | None = None
    PEXELS_API_KEY: str | None = None
    GOOGLE_MAPS_API_KEY: str | None
    OFFERS_ENABLED: bool = False
    OFFERS_DEMO_MODE: bool = False

    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    ADMIN_FIRST_NAME: str | None = None
    ADMIN_LAST_NAME: str | None = None

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        normalized = str(value or "").strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "dev", "development"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
            return False
        return value

    @model_validator(mode="after")
    def validate_offers_mode(self):
        if self.OFFERS_DEMO_MODE and self.APP_ENV != "development":
            raise ValueError("OFFERS_DEMO_MODE is allowed only when APP_ENV=development")
        if self.OFFERS_DEMO_MODE and self.OFFERS_ENABLED:
            raise ValueError("OFFERS_DEMO_MODE and OFFERS_ENABLED cannot both be enabled")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
