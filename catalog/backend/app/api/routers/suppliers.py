from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.supplier import (
    CompareRequest,
    CompareResponse,
    ConfirmCandidateRequest,
    DiscoverRequest,
    DiscoverResponse,
    ExtractFromTextRequest,
    ExtractFromUrlRequest,
    FacetsOut,
    SupplierCreate,
    SupplierOut,
    UnifiedSearchResponse,
    WebSearchResponse,
)
from app.services.extraction_service import ExtractionError, extract_supplier_fields, fetch_page_text
from app.services.recommendation_service import Recommendation, compare_suppliers, recommend_supplier
from app.services.supplier_service import SupplierService
from app.services.web_search_service import discover_suppliers

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierOut])
def list_suppliers(
    category: str | None = None,
    region: str | None = None,
    q: str | None = None,
    has_price: bool | None = None,
    has_moq: bool | None = None,
    db: Session = Depends(get_db),
) -> list[SupplierOut]:
    service = SupplierService(db)
    return service.search(category=category, region=region, query=q, has_price=has_price, has_moq=has_moq)


@router.get("/facets", response_model=FacetsOut)
def get_facets(db: Session = Depends(get_db)) -> FacetsOut:
    return SupplierService(db).facets()


def _web_search_and_recommend(
    service: SupplierService,
    catalog: list[SupplierOut],
    q: str | None,
    category: str | None,
    region: str | None,
) -> tuple[list[dict], Recommendation]:
    web_candidates: list[dict] = []
    if q:
        result = discover_suppliers(q, known_identity=service.known_identity(), region=region, max_candidates=6)
        web_candidates = result["candidates"]
        if category:
            web_candidates = [
                c for c in web_candidates
                if not c.get("preview") or c["preview"]["category"] == category
            ]
    recommendation = recommend_supplier(q, catalog, web_candidates)
    return web_candidates, recommendation


@router.get("/search-all", response_model=UnifiedSearchResponse)
def search_all(
    q: str | None = None,
    category: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
) -> UnifiedSearchResponse:
    service = SupplierService(db)
    catalog = service.search(category=category, region=region, query=q)
    web_candidates, rec = _web_search_and_recommend(service, catalog, q, category, region)
    return UnifiedSearchResponse(
        catalog=catalog, web=web_candidates, recommendation=rec.text,
        recommended_supplier_id=rec.winner_supplier_id, recommended_candidate_url=rec.winner_candidate_url,
    )


@router.get("/web-search", response_model=WebSearchResponse)
def web_search(
    q: str | None = None,
    category: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
) -> WebSearchResponse:
    service = SupplierService(db)
    catalog = service.search(category=category, region=region, query=q)
    web_candidates, rec = _web_search_and_recommend(service, catalog, q, category, region)
    return WebSearchResponse(
        web=web_candidates, recommendation=rec.text,
        recommended_supplier_id=rec.winner_supplier_id, recommended_candidate_url=rec.winner_candidate_url,
    )


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)) -> SupplierOut:
    supplier = SupplierService(db).get(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return supplier


@router.post("", response_model=SupplierOut)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)) -> SupplierOut:
    return SupplierService(db).create(data, created_via="manual", status="verified")


@router.post("/confirm", response_model=SupplierOut)
def confirm_candidate(payload: ConfirmCandidateRequest, db: Session = Depends(get_db)) -> SupplierOut:
    data = SupplierCreate(**payload.model_dump(exclude={"source_url"}))
    return SupplierService(db).create(
        data, created_via="ai_scrape" if payload.source_url else "ai_text",
        source_url=payload.source_url, status="verified",
    )


@router.post("/compare", response_model=CompareResponse)
def compare(payload: CompareRequest, db: Session = Depends(get_db)) -> CompareResponse:
    service = SupplierService(db)
    suppliers = [SupplierOut.model_validate(s) for s in service.get_many(payload.ids)]
    rec = compare_suppliers(payload.query, suppliers)
    return CompareResponse(suppliers=suppliers, recommendation=rec.text, recommended_supplier_id=rec.winner_supplier_id)


@router.post("/scrape", response_model=SupplierOut)
def scrape_supplier(payload: ExtractFromUrlRequest, db: Session = Depends(get_db)) -> SupplierOut:
    try:
        page_text = fetch_page_text(payload.url)
        fields = extract_supplier_fields(page_text)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return SupplierService(db).create(fields, created_via="ai_scrape", source_url=payload.url)


@router.post("/extract", response_model=SupplierOut)
def extract_supplier(payload: ExtractFromTextRequest, db: Session = Depends(get_db)) -> SupplierOut:
    try:
        fields = extract_supplier_fields(payload.text)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return SupplierService(db).create(fields, created_via="ai_text")


@router.post("/discover", response_model=DiscoverResponse)
def discover_web_suppliers(payload: DiscoverRequest, db: Session = Depends(get_db)) -> DiscoverResponse:
    service = SupplierService(db)
    result = discover_suppliers(payload.query, known_identity=service.known_identity())
    return DiscoverResponse(**result)
