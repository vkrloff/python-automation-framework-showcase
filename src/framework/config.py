"""Typed runtime configuration, read from environment variables and an optional `.env` file."""

from functools import lru_cache

from pydantic import HttpUrl, PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the system under test. Override any field via env var (e.g. `BASE_URL`)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    base_url: HttpUrl = HttpUrl("http://localhost:3000")
    connect_timeout: PositiveFloat = 5.0
    read_timeout: PositiveFloat = 15.0

    @property
    def api_base_url(self) -> str:
        """Base URL without a trailing slash (`HttpUrl` always renders one for a bare host)."""
        return str(self.base_url).rstrip("/")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance (read once, immutable)."""
    return Settings()
