import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.cache import cache_delete_prefix, cache_get, cache_set
from app.db.models import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import FacetsOut, SupplierCreate, SupplierOut
from app.services import vector_store
from app.services.embedding_service import embed_passage, embed_query


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


def supplier_embedding_text(data: SupplierCreate) -> str:
    parts = [data.name, data.category, data.region, data.product_lines or "", data.description, data.notes or ""]
    return ". ".join(p for p in parts if p)


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
            vector = embed_query(query)
            ids = vector_store.semantic_search_ids(vector, limit=50)
            semantic_matches = self.repo.get_many(ids)
            seen_ids = {s.id for s in literal_matches}
            suppliers = literal_matches + [s for s in semantic_matches if s.id not in seen_ids]
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
