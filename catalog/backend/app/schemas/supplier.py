from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class SupplierCreate(SupplierBase):
    pass


class ConfirmCandidateRequest(SupplierBase):
    source_url: str | None = None


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
