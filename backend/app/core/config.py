from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
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

    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    ADMIN_FIRST_NAME: str | None = None
    ADMIN_LAST_NAME: str | None = None

    STORAGE_BACKEND: str = "local"
    GCS_BUCKET_NAME: str | None = None
    GCS_MEDIA_PREFIX: str = "media"
    GCS_SIGNED_URL_EXPIRATION_MINUTES: int = 60
    GCP_SERVICE_ACCOUNT_EMAIL: str | None = None
    USE_GCS_STORAGE: bool = False

    DEFAULT_RESTAURANT_IMAGE_URL: str | None = None
    DEFAULT_ACTIVITY_IMAGE_URL: str | None = None
    DEFAULT_PLACE_IMAGE_URL: str | None = None

    @field_validator("DEBUG", "USE_GCS_STORAGE", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        normalized = str(value or "").strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "dev", "development"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
            return False
        return value

    @field_validator("STORAGE_BACKEND", mode="before")
    @classmethod
    def normalize_storage_backend(cls, value):
        normalized = str(value or "").strip().lower()
        return normalized or "local"

    @model_validator(mode="after")
    def apply_storage_backend_compatibility(self):
        if self.STORAGE_BACKEND not in {"local", "gcs"}:
            raise ValueError("STORAGE_BACKEND must be either 'local' or 'gcs'")
        if self.USE_GCS_STORAGE:
            self.STORAGE_BACKEND = "gcs"
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
