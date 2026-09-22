import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.cache import cache_delete_prefix, cache_get, cache_set
from app.db.models import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import FacetsOut, SupplierCreate, SupplierOut
from app.services import vector_store
from app.core.query_terms import significant_terms
from app.services.embedding_service import embed_passage, embed_passages, embed_query


def _domain(url: str) -> str:
    try:
        host = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def normalize_name(name: str) -> str:
    cleaned = re.sub(r'[«»"\'.,]', "", name.lower())
    cleaned = re.sub(r'\b(ооо|зао|оао|ип|group|групп)\b', "", cleaned)
    return re.sub(r"[^a-zа-я0-9]+", "", cleaned)


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits


@dataclass
class KnownIdentity:
    domains: set[str] = field(default_factory=set)
    names: set[str] = field(default_factory=set)
    phones: set[str] = field(default_factory=set)

    def matches(self, *, domain: str | None = None, name: str | None = None, phone: str | None = None) -> bool:
        if domain and domain in self.domains:
            return True
        if name and normalize_name(name) in self.names:
            return True
        if phone and normalize_phone(phone) in self.phones:
            return True
        return False


FACETS_CACHE_KEY = "facets:v1"
SEARCH_CACHE_PREFIX = "suppliers:search:"
SEMANTIC_EXTRA_CAP = 6


def supplier_embedding_text(data: SupplierCreate) -> str:
    parts = [data.name, data.category, data.region, data.product_lines or "", data.description, data.notes or ""]
    return ". ".join(p for p in parts if p)


def supplier_embedding_chunks(data: SupplierCreate) -> list[str]:
    """Short standalone phrases, one per product line — indexed as separate
    vectors so a short query ("сыр", "пицца") can match a short chunk
    directly instead of getting diluted against one long passage. The
    category is deliberately excluded: it's shared by many suppliers, so
    indexing it as its own chunk drags in the whole category for any
    loosely-related query."""
    return [item.strip() for item in (data.product_lines or "").split(",") if item.strip()]


class SupplierService:
    def __init__(self, db: Session):
        self.repo = SupplierRepository(db)

    def search(
        self,
        category: str | None,
        region: str | None,
        query: str | None,
        has_price: bool | None = None,
        has_moq: bool | None = None,
    ) -> list[SupplierOut]:
        cache_key = f"{SEARCH_CACHE_PREFIX}{category or ''}:{region or ''}:{query or ''}:{has_price}:{has_moq}"
        cached = cache_get(cache_key)
        if cached is not None:
            return [SupplierOut(**item) for item in cached]

        suppliers = self._search_uncached(category, region, query, has_price, has_moq)
        cache_set(cache_key, [SupplierOut.model_validate(s).model_dump(mode="json") for s in suppliers])
        return suppliers

    def _search_uncached(
        self,
        category: str | None,
        region: str | None,
        query: str | None,
        has_price: bool | None,
        has_moq: bool | None,
    ) -> list[Supplier]:
        if not query:
            return self.repo.list_suppliers(category=category, region=region, has_price=has_price, has_moq=has_moq)

        # A literal substring match on name/description is always relevant by
        # construction (the word is right there), so union it with the
        # semantic hits instead of relying on one similarity cutoff to work
        # for both short single-word queries and longer descriptive ones.
        literal_matches = self.repo.list_suppliers(category=category, region=region, query=query, has_price=has_price, has_moq=has_moq)

        try:
            # This embedding model doesn't reliably separate "relevant" from
            # "not" for short catalog phrases — for broad single-concept
            # words the whole catalog can land in a tight, high score band
            # with no real gap (observed: "выпечка" scored 0.75-0.89 for
            # over half the suppliers, packaging and drinks included). No
            # threshold fixes that, so on top of the score cutoff, cap how
            # many *extra* (non-literal) picks semantic search is allowed to
            # contribute — it's a supplement to literal matching, not a
            # second independent search.
            vector = embed_query(" ".join(significant_terms(query)))
            ids = vector_store.semantic_search_ids(vector, limit=50)
            semantic_matches = self.repo.get_many(ids)
            seen_ids = {s.id for s in literal_matches}
            extra = [s for s in semantic_matches if s.id not in seen_ids][:SEMANTIC_EXTRA_CAP]
            suppliers = literal_matches + extra
        except Exception:
            suppliers = literal_matches

        if category:
            suppliers = [s for s in suppliers if s.category == category]
        if region:
            suppliers = [s for s in suppliers if s.region == region]
        if has_price is not None:
            suppliers = [s for s in suppliers if bool(s.price_note) == has_price]
        if has_moq is not None:
            suppliers = [s for s in suppliers if bool(s.moq) == has_moq]
        return suppliers

    def get(self, supplier_id: int) -> Supplier | None:
        return self.repo.get(supplier_id)

    def create(self, data: SupplierCreate, created_via: str, source_url: str | None = None, status: str = "found") -> Supplier:
        supplier = self.repo.create(data, created_via=created_via, source_url=source_url, status=status)
        try:
            vector = embed_passage(supplier_embedding_text(data))
            vector_store.upsert_supplier_vector(supplier.id, vector)
            chunks = supplier_embedding_chunks(data)
            if chunks:
                vector_store.upsert_supplier_chunk_vectors(supplier.id, embed_passages(chunks))
        except Exception:
            pass
        cache_delete_prefix(FACETS_CACHE_KEY)
        cache_delete_prefix(SEARCH_CACHE_PREFIX)
        return supplier

    def get_many(self, ids: list[int]) -> list[Supplier]:
        return self.repo.get_many(ids)

    def known_domains(self) -> set[str]:
        return {_domain(url) for url in self.repo.known_websites() if url}

    def known_identity(self) -> KnownIdentity:
        return KnownIdentity(
            domains=self.known_domains(),
            names={normalize_name(n) for n in self.repo.known_names() if n},
            phones={normalize_phone(p) for p in self.repo.known_phones() if p},
        )

    def facets(self) -> FacetsOut:
        cached = cache_get(FACETS_CACHE_KEY)
        if cached is not None:
            return FacetsOut(**cached)

        facets = FacetsOut(categories=self.repo.categories(), regions=self.repo.regions())
        cache_set(FACETS_CACHE_KEY, facets.model_dump())
        return facets
