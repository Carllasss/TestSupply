# Generic B2B filler words ("оптом", "для", ...) show up in almost every
# supplier's text, so on their own they don't discriminate anything — they'd
# either match everyone (literal search) or dominate a short query's
# embedding and drag in unrelated results (semantic search). Stripped out of
# search queries; never touches the text stored for a supplier.
#
# Stems, not whole words: Russian inflects endings ("доставка"/"доставки"/
# "доставкой"), so an exact-word stopword list misses most real query forms.
GENERIC_QUERY_STEMS = (
    "опт", "для", "нужн", "ищ", "недорог", "дешев", "дёшев", "доставк",
    "купит", "поставщик", "продаж", "закупк", "крупн", "мелк",
)


def significant_terms(query: str) -> list[str]:
    words = [w.strip(".,!?") for w in query.split()]
    significant = [w for w in words if w and not w.lower().startswith(GENERIC_QUERY_STEMS)]
    return significant or [w for w in words if w]
