from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

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
    """Upserts the main one-paragraph passage vector for a supplier, keyed by
    its own id."""
    settings = get_settings()
    client = get_client()
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[PointStruct(id=supplier_id, vector=vector, payload={"supplier_id": supplier_id})],
    )


# Chunk points (one per product line, etc.) live in a disjoint id space from
# the plain supplier_id used by the main passage vector above, so both can
# coexist without collisions.
_CHUNK_ID_BASE = 10_000_000
_CHUNK_ID_STRIDE = 1_000


def upsert_supplier_chunk_vectors(supplier_id: int, vectors: list[list[float]]) -> None:
    """Replaces a supplier's short-text chunk vectors (e.g. one per product
    line) — short chunks match short queries ("сыр", "пицца") much better
    than one long diluted passage does."""
    settings = get_settings()
    client = get_client()
    base = _CHUNK_ID_BASE + supplier_id * _CHUNK_ID_STRIDE
    # Clear any previously indexed chunks for this supplier first, since it
    # may now have fewer/different product lines than last time.
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=PointIdsList(points=list(range(base, base + _CHUNK_ID_STRIDE))),
    )
    if not vectors:
        return
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[
            PointStruct(id=base + i, vector=v, payload={"supplier_id": supplier_id})
            for i, v in enumerate(vectors[:_CHUNK_ID_STRIDE])
        ],
    )


def rank_hits_by_supplier(
    hits: list[tuple[int, float]],
    limit: int = 50,
    relative_margin: float = 0.15,
) -> list[int]:
    """Pure ranking/dedup logic for semantic_search_ids, split out so it's
    unit-testable without a live Qdrant instance. `hits` is a list of
    (supplier_id, score) pairs, already restricted to points above the
    absolute score_threshold (multiple hits per supplier_id are expected —
    several chunks, or a chunk plus the main passage, can point at the same
    supplier).

    Absolute cosine similarity isn't a reliable cutoff on its own with this
    embedding model: for short Russian product phrases, scores for
    genuinely unrelated items and for genuinely relevant ones both land in a
    fairly narrow, overlapping band (observed: a plastic-wrap supplier
    scored 0.62 against "пицца моцарелла", while a real mozzarella producer
    scored 0.9). A per-query relative margin — keep only hits within
    `relative_margin` of the best score for THIS query — adapts to how
    strong the best match actually is, instead of using one fixed number
    that's simultaneously too loose for weak queries and too strict for
    queries with a clear best answer.
    """
    best_score: dict[int, float] = {}
    for supplier_id, score in hits:
        if score > best_score.get(supplier_id, -1.0):
            best_score[supplier_id] = score

    if not best_score:
        return []

    top_score = max(best_score.values())
    cutoff = top_score - relative_margin
    ranked = sorted(
        (item for item in best_score.items() if item[1] >= cutoff),
        key=lambda item: item[1],
        reverse=True,
    )
    return [supplier_id for supplier_id, _ in ranked[:limit]]


def semantic_search_ids(
    vector: list[float],
    limit: int = 50,
    score_threshold: float = 0.55,
    relative_margin: float = 0.15,
) -> list[int]:
    settings = get_settings()
    client = get_client()
    hits = client.query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=limit * 4,  # oversample: several hits (chunks + passage) can map to the same supplier
        score_threshold=score_threshold,
    ).points

    pairs = [
        (int(hit.payload.get("supplier_id", hit.id)) if hit.payload else int(hit.id), hit.score)
        for hit in hits
    ]
    return rank_hits_by_supplier(pairs, limit=limit, relative_margin=relative_margin)
