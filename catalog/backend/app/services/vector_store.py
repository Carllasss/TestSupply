from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import get_settings

VECTOR_SIZE = 384


def _ensure_collection(client: QdrantClient) -> None:
    settings = get_settings()
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


@lru_cache
def get_client() -> QdrantClient:
    settings = get_settings()
    client = QdrantClient(url=settings.qdrant_url)
    _ensure_collection(client)
    return client


def upsert_supplier_vector(supplier_id: int, vector: list[float]) -> None:
    settings = get_settings()
    client = get_client()
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[PointStruct(id=supplier_id, vector=vector, payload={"supplier_id": supplier_id})],
    )


def semantic_search_ids(vector: list[float], limit: int = 50, score_threshold: float = 0.6) -> list[int]:
    settings = get_settings()
    client = get_client()
    hits = client.query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=limit,
        score_threshold=score_threshold,
    ).points
    return [int(hit.id) for hit in hits]
