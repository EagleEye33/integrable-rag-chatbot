from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Website Chatbot API"
    environment: str = "development"
    api_prefix: str = "/api"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # Retrieval and content paths
    index_path: Path = Path("backend/data/index.json")
    content_sources_path: Path = Path("backend/data/content_sources.json")

    # Basic retrieval controls
    max_context_chunks: int = 4
    min_relevance_score: float = 0.08

    # CORS
    allow_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        if self.allow_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allow_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
