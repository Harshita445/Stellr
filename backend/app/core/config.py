from pydantic import BaseModel, HttpUrl, PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class DatabaseConfig(BaseModel):
    URL: PostgresDsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/constellation"
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 80
    ECHO: bool = False


class RedisConfig(BaseModel):
    URL: RedisDsn = "redis://localhost:6379/0"
    POOL_SIZE: int = 10


class AuthConfig(BaseModel):
    JWT_SECRET: str = "dev-secret-change-in-production-32bytes!"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 15
    REFRESH_EXPIRY_DAYS: int = 30
    DEVICE_FINGERPRINT_SALT: str = "dev-salt-change-in-production"
    ENUMERATION_PREVENTION_DELAY: float = 0.05
    MAX_DEVICES_PER_USER: int = 5


class RateLimitConfig(BaseModel):
    ENABLED: bool = True
    REDIS_PREFIX: str = "ratelimit"


class Settings(BaseSettings):
    """Application configuration.
    All values come from environment variables prefixed with CONSTELLATION_.
    """

    model_config = SettingsConfigDict(
        env_prefix="CONSTELLATION_",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    DATABASE: DatabaseConfig = DatabaseConfig()
    REDIS: RedisConfig = RedisConfig()
    AUTH: AuthConfig = AuthConfig()
    RATE_LIMIT: RateLimitConfig = RateLimitConfig()

    FRONTEND_URL: HttpUrl = "http://localhost:3000"  # type: ignore[assignment]
    CORS_ORIGINS: list[str] = []

    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str | None = None

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.DATABASE.ECHO:
            raise ValueError("Cannot enable SQL echo in production")
        return self


settings = Settings()
