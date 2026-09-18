from functools import lru_cache

import httpx
from openai import OpenAI

from app.core.config import get_settings


@lru_cache
def get_llm_client() -> OpenAI:
    settings = get_settings()
    if settings.llm_provider == "openai":
        http_client = None
        if settings.openai_proxy_url:
            # OpenAI's API is blocked for Russian IPs; route just this client
            # through a SOCKS5 proxy (e.g. a shadowsocks-rust sidecar) when configured.
            http_client = httpx.Client(proxy=settings.openai_proxy_url)
        return OpenAI(api_key=settings.openai_api_key, http_client=http_client)
    return OpenAI(base_url=settings.llm_base_url, api_key="local")


def get_llm_model() -> str:
    settings = get_settings()
    return settings.openai_model if settings.llm_provider == "openai" else settings.llm_model
