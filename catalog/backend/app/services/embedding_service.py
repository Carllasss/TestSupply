from functools import lru_cache

from fastembed import TextEmbedding

from app.core.config import get_settings


@lru_cache
def get_embedder() -> TextEmbedding:
    settings = get_settings()
    return TextEmbedding(model_name=settings.embedding_model, cache_dir="/root/.cache/fastembed_cache")


def embed_passage(text: str) -> list[float]:
    vector = next(get_embedder().embed([text]))
    return vector.tolist()


def embed_passages(texts: list[str]) -> list[list[float]]:
    return [v.tolist() for v in get_embedder().embed(texts)]


def embed_query(text: str) -> list[float]:
    vector = next(get_embedder().query_embed([text]))
    return vector.tolist()
