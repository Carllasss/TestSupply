from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _http_url_or_none(value: str | None) -> str | None:
    """Drop anything that isn't a plain http(s) link (blocks javascript:/data: URIs
    reaching an <a href> on the frontend)."""
    if not value:
        return value
    if not value.lower().startswith(("http://", "https://")):
        return None
    return value


class SupplierBase(BaseModel):
    name: str
    category: str
    region: str
    description: str = ""
    contact_phone: str | None = None
    contact_email: str | None = None
    website: str | None = None
    product_lines: str | None = None
    moq: str | None = None
    price_note: str | None = None
    certificates: str | None = None
    delivery_terms: str | None = None
    notes: str | None = None

    @field_validator("website")
    @classmethod
    def _validate_website(cls, value: str | None) -> str | None:
        return _http_url_or_none(value)


class SupplierCreate(SupplierBase):
    pass


class ConfirmCandidateRequest(SupplierBase):
    source_url: str | None = None

    @field_validator("source_url")
    @classmethod
    def _validate_source_url(cls, value: str | None) -> str | None:
        return _http_url_or_none(value)


class SupplierOut(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_url: str | None = None
    created_via: str
    status: str
    created_at: datetime


class ExtractFromUrlRequest(BaseModel):
    url: str = Field(min_length=5)


class ExtractFromTextRequest(BaseModel):
    text: str = Field(min_length=20)


class FacetsOut(BaseModel):
    categories: list[str]
    regions: list[str]


class DiscoverRequest(BaseModel):
    query: str = Field(min_length=3)


class DiscoverCandidate(BaseModel):
    url: str
    title: str
    snippet: str = ""
    domain: str
    already_in_catalog: bool
    preview: SupplierCreate | None = None
    error: str | None = None

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        return _http_url_or_none(value) or ""


class DiscoverResponse(BaseModel):
    search_query: str
    candidates: list[DiscoverCandidate]


class UnifiedSearchResponse(BaseModel):
    catalog: list[SupplierOut]
    web: list[DiscoverCandidate]
    recommendation: str | None = None
    recommended_supplier_id: int | None = None
    recommended_candidate_url: str | None = None


class WebSearchResponse(BaseModel):
    web: list[DiscoverCandidate]
    recommendation: str | None = None
    recommended_supplier_id: int | None = None
    recommended_candidate_url: str | None = None


class CompareRequest(BaseModel):
    ids: list[int] = Field(min_length=2, max_length=4)
    query: str | None = None


class CompareResponse(BaseModel):
    suppliers: list[SupplierOut]
    recommendation: str | None = None
    recommended_supplier_id: int | None = None
