from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.services.extraction_service import ExtractionError, extract_supplier_fields, fetch_page_text
from app.services.supplier_service import KnownIdentity

BLOCKED_DOMAINS = {
    "avito.ru", "wildberries.ru", "ozon.ru", "market.yandex.ru",
    "vk.com", "youtube.com", "youtu.be", "wikipedia.org", "ru.wikipedia.org",
    "2gis.ru", "facebook.com", "instagram.com", "t.me", "dzen.ru",
    "habr.com", "yandex.ru", "google.com", "flamp.ru", "zoon.ru",
    "profi.ru", "pulscen.ru", "tiu.ru",
}


def _domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def _unwrap_redirect(url: str) -> str:
    try:
        parsed = urlparse(url if "://" in url else f"https:{url}")
    except ValueError:
        return url
    if "duckduckgo.com" in parsed.netloc and parsed.path == "/l/":
        target = parse_qs(parsed.query).get("uddg")
        if target:
            return target[0]
    return url


def build_web_query(user_query: str, region: str | None = None) -> str:
    query = user_query.strip()
    lowered = query.lower()
    parts = [query]
    if "оптом" not in lowered and "поставщик" not in lowered:
        parts.append("поставщик оптом")
    if region and region.lower() not in lowered:
        parts.append(region)
    return " ".join(parts)


def duckduckgo_search(query: str, max_results: int = 10) -> list[dict]:
    proxy = get_settings().outbound_proxy_url or None
    try:
        with httpx.Client(proxy=proxy, timeout=10.0) as client:
            response = client.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("a.result-link")
    snippets = soup.select(".result-snippet")

    results = []
    for i, link in enumerate(links):
        url = link.get("href")
        title = link.get_text(strip=True)
        if not url or not title:
            continue
        results.append({
            "url": _unwrap_redirect(url),
            "title": title,
            "snippet": snippets[i].get_text(strip=True) if i < len(snippets) else "",
        })
        if len(results) >= max_results:
            break
    return results


def _preview_candidate(candidate: dict) -> dict:
    try:
        page_text = fetch_page_text(candidate["url"])
        fields = extract_supplier_fields(page_text)
        candidate["preview"] = fields.model_dump()
        candidate["error"] = None
    except ExtractionError as exc:
        candidate["preview"] = None
        candidate["error"] = str(exc)
    except Exception as exc:
        candidate["preview"] = None
        candidate["error"] = f"Не получилось разобрать страницу: {exc}"
    return candidate


def discover_suppliers(
    user_query: str,
    known_identity: KnownIdentity,
    region: str | None = None,
    max_candidates: int = 6,
) -> dict:
    search_query = build_web_query(user_query, region)
    raw_results = duckduckgo_search(search_query, max_results=15)

    seen_domains: set[str] = set()
    candidates = []
    for item in raw_results:
        domain = _domain(item["url"])
        if not domain or domain in BLOCKED_DOMAINS or domain in seen_domains:
            continue
        seen_domains.add(domain)
        item["domain"] = domain
        item["already_in_catalog"] = known_identity.matches(domain=domain)
        candidates.append(item)
        if len(candidates) >= max_candidates:
            break

    to_preview = [c for c in candidates if not c["already_in_catalog"]]
    if to_preview:
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(_preview_candidate, c): c for c in to_preview}
            for future in as_completed(futures):
                future.result()

    for candidate in candidates:
        preview = candidate.get("preview")
        if not preview or candidate["already_in_catalog"]:
            continue
        if known_identity.matches(name=preview.get("name"), phone=preview.get("contact_phone")):
            candidate["already_in_catalog"] = True

    return {"search_query": search_query, "candidates": candidates}
