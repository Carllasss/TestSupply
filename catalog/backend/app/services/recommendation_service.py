from dataclasses import dataclass

from app.schemas.supplier import SupplierOut
from app.services.llm_client import get_llm_client, get_llm_model

SYSTEM_PROMPT = (
    "Ты помогаешь менеджеру ресторана выбрать поставщика продуктов питания. "
    "По запросу пользователя и списку вариантов (часть уже в каталоге, часть "
    "найдена в интернете) в 2-3 предложениях скажи, какой вариант лучше подходит "
    "и почему. Рекомендуй СТРОГО одну компанию из списка ниже, дословно как она "
    "там названа — никогда не упоминай никакие другие компании, даже если "
    "знаешь их. Начни ответ с точного названия компании, затем объяснение. "
    "Пиши по-русски, без markdown."
)

COMPARE_SYSTEM_PROMPT = (
    "Ты помогаешь менеджеру ресторана сравнить несколько поставщиков по запросу. "
    "Опирайся только на факты из карточек (MOQ, цена, ассортимент, регион, документы). "
    "Если у поставщика чего-то не указано — так и скажи, не выдумывай. "
    "В 2-4 предложениях скажи, какой вариант лучше подходит под запрос и почему, "
    "со ссылкой на конкретные известные факты. Рекомендуй СТРОГО одну компанию из "
    "списка ниже, дословно как она там названа — никогда не упоминай никакие "
    "другие компании. Начни ответ с точного названия компании, затем объяснение. "
    "Пиши по-русски, без markdown."
)


def _item_line(name: str, category: str, region: str, moq: str | None, price_note: str | None, description: str, source: str) -> str:
    bits = [f"{name} ({source})", f"категория: {category}", f"регион: {region}"]
    if moq:
        bits.append(f"MOQ: {moq}")
    if price_note:
        bits.append(f"цена: {price_note}")
    bits.append((description or "")[:160])
    return "- " + "; ".join(bits)


def _find_winner_name(text: str, names: list[str]) -> str | None:
    """Return the candidate name that appears earliest in the recommendation text."""
    lowered = text.lower()
    best_name, best_pos = None, len(text) + 1
    for name in names:
        if not name:
            continue
        pos = lowered.find(name.lower())
        if pos != -1 and pos < best_pos:
            best_name, best_pos = name, pos
    return best_name


@dataclass
class Recommendation:
    text: str | None = None
    winner_supplier_id: int | None = None
    winner_candidate_url: str | None = None


def _build_recommend_prompt(query: str, catalog: list[SupplierOut], web_candidates: list[dict]):
    catalog_items = [(s, "в каталоге") for s in catalog[:6]]
    web_items = [(c, "найдено в интернете") for c in web_candidates[:6] if c.get("preview")]

    lines = [
        _item_line(s.name, s.category, s.region, s.moq, s.price_note, s.description, source)
        for s, source in catalog_items
    ]
    for c, source in web_items:
        p = c["preview"]
        lines.append(_item_line(p["name"], p["category"], p["region"], p.get("moq"), p.get("price_note"), p["description"], source))

    names = [s.name for s, _ in catalog_items] + [c["preview"]["name"] for c, _ in web_items]
    user_content = f"Запрос: {query}\n\nВарианты:\n" + "\n".join(lines) if lines else None
    return catalog_items, web_items, names, user_content


def _resolve_winner(text: str, names: list[str], catalog_items, web_items) -> Recommendation:
    winner_name = _find_winner_name(text, names)
    if not winner_name:
        # Модель не назвала дословно ни один из переданных вариантов — похоже на
        # галлюцинацию. Не показываем непроверяемую рекомендацию.
        return Recommendation()

    winner_supplier_id = None
    winner_candidate_url = None
    for s, _ in catalog_items:
        if s.name == winner_name:
            winner_supplier_id = s.id
            break
    else:
        for c, _ in web_items:
            if c["preview"]["name"] == winner_name:
                winner_candidate_url = c["url"]
                break

    return Recommendation(text=text, winner_supplier_id=winner_supplier_id, winner_candidate_url=winner_candidate_url)


def recommend_supplier(query: str | None, catalog: list[SupplierOut], web_candidates: list[dict]) -> Recommendation:
    if not query:
        return Recommendation()

    catalog_items, web_items, names, user_content = _build_recommend_prompt(query, catalog, web_candidates)
    if not user_content:
        return Recommendation()

    try:
        completion = get_llm_client().chat.completions.create(
            model=get_llm_model(),
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        text = completion.choices[0].message.content.strip() or None
    except Exception:
        return Recommendation()

    if not text:
        return Recommendation()

    return _resolve_winner(text, names, catalog_items, web_items)


def recommend_supplier_stream(query: str | None, catalog: list[SupplierOut], web_candidates: list[dict]):
    """Yields {"type": "chunk", "text": "..."} deltas as the recommendation is
    generated, then returns the validated Recommendation (same rules as
    recommend_supplier: an unverifiable/hallucinated pick is suppressed
    entirely) via StopIteration.value — callers should drive this with
    `yield from` or manually catch the return value."""
    if not query:
        return Recommendation()

    catalog_items, web_items, names, user_content = _build_recommend_prompt(query, catalog, web_candidates)
    if not user_content:
        return Recommendation()

    chunks: list[str] = []
    try:
        stream = get_llm_client().chat.completions.create(
            model=get_llm_model(),
            temperature=0.2,
            stream=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        for event in stream:
            delta = event.choices[0].delta.content if event.choices else None
            if delta:
                chunks.append(delta)
                yield {"type": "chunk", "text": delta}
    except Exception:
        return Recommendation()

    text = "".join(chunks).strip() or None
    if not text:
        return Recommendation()

    return _resolve_winner(text, names, catalog_items, web_items)


def compare_suppliers(query: str | None, suppliers: list[SupplierOut]) -> Recommendation:
    lines = [
        _item_line(s.name, s.category, s.region, s.moq, s.price_note, s.description, s.status)
        for s in suppliers
    ]
    if not lines:
        return Recommendation()

    try:
        completion = get_llm_client().chat.completions.create(
            model=get_llm_model(),
            temperature=0.2,
            messages=[
                {"role": "system", "content": COMPARE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Запрос: {query or 'не указан'}\n\nСравниваем:\n" + "\n".join(lines)},
            ],
        )
        text = completion.choices[0].message.content.strip() or None
    except Exception:
        return Recommendation()

    if not text:
        return Recommendation()

    winner_name = _find_winner_name(text, [s.name for s in suppliers])
    if not winner_name:
        return Recommendation()

    winner_supplier_id = next((s.id for s in suppliers if s.name == winner_name), None)
    return Recommendation(text=text, winner_supplier_id=winner_supplier_id)
