from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://f1lm:f1lm@localhost:5433/f1lm"

    openf1_base_url: str = "https://api.openf1.org/v1"
    openf1_timeout_seconds: float = 10.0
    openf1_max_retries: int = 3
    openf1_max_requests_per_second: float = 3.0
    openf1_max_requests_per_minute: float = 30.0

    log_level: str = "INFO"

    # Comma-separated list of origins allowed to call the API from a browser.
    cors_allowed_origins: str = "http://localhost:3000"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
