from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://suppliers:suppliers@localhost:5432/suppliers"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    llm_provider: str = "openai"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen2.5:7b"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "suppliers"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
