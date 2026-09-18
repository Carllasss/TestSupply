import ipaddress
import json
import re
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.categories import CATEGORY_OPTIONS
from app.core.config import get_settings
from app.schemas.supplier import SupplierCreate
from app.services.llm_client import get_llm_client, get_llm_model


def _assert_public_http_url(url: str) -> None:
    """Block SSRF: reject non-http(s) schemes and hosts that resolve to
    private/loopback/link-local addresses (internal services, docker network)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ExtractionError("Разрешены только http/https ссылки")

    try:
        addrinfo = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror as exc:
        raise ExtractionError(f"Не удалось разрешить адрес: {exc}") from exc

    for *_, sockaddr in addrinfo:
        ip = ipaddress.ip_address(sockaddr[0])
        if not ip.is_global:
            raise ExtractionError("Ссылки на внутренние/локальные адреса запрещены")


def _extract_json_block(text: str) -> str:
    match = re.search(r"\{.*\}", text or "", re.DOTALL)
    return match.group(0) if match else (text or "")

SYSTEM_PROMPT = f"""Ты помогаешь заполнить карточку поставщика продуктов питания
для B2B-каталога ресторанов доставки. По присланному тексту (сайт, описание,
прайс) верни строго JSON со следующими полями:

name (строка, обязательно), category (одно значение из {CATEGORY_OPTIONS}),
region (город или регион работы компании), description (краткое описание, 1-2
предложения), product_lines (конкретные товарные позиции через запятую, например
"моцарелла, сливки, творог" — не общие слова вроде "продукты", а именно то, что
поставляют, или null), contact_phone, contact_email, website (или null, если не
найдено), moq (минимальный объём заказа текстом или null), price_note (примерная
цена текстом или null — валюту всегда пиши символом ₽, а не "руб." или "р."),
certificates (какие сертификаты/документы есть или null), delivery_terms
(география и условия доставки или null), notes (любые важные детали или null).

Если данных для поля нет — верни null, не выдумывай факты и не подставляй точные
цифры (цену, сертификаты), если они не написаны в тексте прямо. Ответ — только
JSON, без пояснений."""


class ExtractionError(Exception):
    pass


def fetch_page_text(url: str, max_chars: int = 6000) -> str:
    _assert_public_http_url(url)
    try:
        with httpx.Client(follow_redirects=False, timeout=10.0) as client:
            headers = {"User-Agent": "Mozilla/5.0 (supplier-catalog-bot)"}
            for _ in range(5):
                response = client.get(url, headers=headers)
                if response.is_redirect:
                    url = str(response.next_request.url)
                    _assert_public_http_url(url)
                    continue
                break
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ExtractionError(f"Не удалось загрузить страницу: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    body_text = " ".join(soup.get_text(separator=" ").split())
    combined = f"{title}\n{body_text}"[:max_chars]

    if len(combined.strip()) < 30:
        raise ExtractionError("На странице почти нет текста для анализа")

    return combined


def extract_supplier_fields(raw_text: str) -> SupplierCreate:
    settings = get_settings()
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        raise ExtractionError("OPENAI_API_KEY не задан на бэкенде")

    kwargs = {"response_format": {"type": "json_object"}} if settings.llm_provider == "openai" else {}
    completion = get_llm_client().chat.completions.create(
        model=get_llm_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.1,
        **kwargs,
    )

    payload = completion.choices[0].message.content
    if settings.llm_provider != "openai":
        payload = _extract_json_block(payload)
    try:
        data = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ExtractionError("Модель вернула невалидный JSON") from exc

    if data.get("category") not in CATEGORY_OPTIONS:
        data["category"] = CATEGORY_OPTIONS[-1]
    if not data.get("region"):
        data["region"] = "не указан"
    if not data.get("name"):
        raise ExtractionError("Не удалось определить название поставщика")

    try:
        return SupplierCreate(**data)
    except Exception as exc:
        raise ExtractionError(f"Не хватает обязательных полей: {exc}") from exc
