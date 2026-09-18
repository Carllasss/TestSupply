from functools import lru_cache

from openai import OpenAI

from app.core.config import get_settings


@lru_cache
def get_llm_client() -> OpenAI:
    settings = get_settings()
    if settings.llm_provider == "openai":
        return OpenAI(api_key=settings.openai_api_key)
    return OpenAI(base_url=settings.llm_base_url, api_key="local")


def get_llm_model() -> str:
    settings = get_settings()
    return settings.openai_model if settings.llm_provider == "openai" else settings.llm_model
