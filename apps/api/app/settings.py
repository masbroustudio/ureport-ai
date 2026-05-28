from pydantic import model_validator
from pydantic_settings import BaseSettings

_JWT_SECRET_DEFAULT = "change-me-in-production-min-32-chars"


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_NAME: str = "uReport AI API"
    APP_VERSION: str = "0.1.0"
    CORS_ORIGINS: str = "http://localhost:3000"
    DATABASE_URL: str = "postgresql+asyncpg://ureport:ureport_secret@localhost:5432/ureport_ai"
    REDIS_URL: str = "redis://localhost:6379/0"
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET_NAME: str = "ureport-files"
    QDRANT_URL: str = "http://localhost:6333"
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    JWT_SECRET_KEY: str = _JWT_SECRET_DEFAULT
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    GROQ_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    SUMOPOD_API_KEY: str = ""
    SUMOPOD_BASE_URL: str = ""
    FILE_STORAGE_PATH: str = "./storage/uploads"
    DATA_SANDBOX_TIMEOUT_SECONDS: int = 30
    MAX_UPLOAD_SIZE_MB: int = 50
    SENTRY_DSN: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def _check_jwt_secret(self) -> "Settings":
        if self.APP_ENV != "development" and self.JWT_SECRET_KEY == _JWT_SECRET_DEFAULT:
            raise ValueError(
                "JWT_SECRET_KEY must be changed from the default value "
                "in non-development environments"
            )
        return self


settings = Settings()
