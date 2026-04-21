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
    TWOGIS_API_KEY: str | None = None
    TWOGIS_PLACES_BASE_URL: str = "https://catalog.api.2gis.com/3.0/items"
    TWOGIS_ROUTING_BASE_URL: str = "https://routing.api.2gis.com/routing/7.0.0/global"
    TWOGIS_MATRIX_BASE_URL: str = "https://routing.api.2gis.com/get_dist_matrix"
    PEXELS_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
