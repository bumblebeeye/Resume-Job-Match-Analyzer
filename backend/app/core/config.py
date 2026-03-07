import json
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/resume_matcher"
    )
    cors_origins: str = "http://localhost:3000"
    resume_storage_path: str = "storage/resumes"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value: str | list[str]) -> str:
        # Keep environment parsing resilient across local/dev/prod formats.
        # Accepted examples:
        # - "http://localhost:3000,http://127.0.0.1:3000"
        # - '["https://app.vercel.app","http://localhost:3000"]'
        if isinstance(value, str):
            return value.strip()
        return ",".join(origin.strip() for origin in value if origin.strip())

    def get_cors_origins(self) -> list[str]:
        raw = self.cors_origins.strip()
        if not raw:
            return []

        if raw.startswith("["):
            try:
                loaded = json.loads(raw)
                if isinstance(loaded, list):
                    return [str(origin).strip() for origin in loaded if str(origin).strip()]
            except json.JSONDecodeError:
                pass

        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
