from app.core.query_terms import significant_terms


def test_strips_generic_wholesale_word():
    assert significant_terms("мясо оптом") == ["мясо"]


def test_strips_inflected_forms_by_stem():
    # "доставки"/"доставкой" aren't literally "доставка" — must match by stem.
    assert significant_terms("упаковка для доставки") == ["упаковка"]
    assert significant_terms("отправка доставкой") == ["отправка"]


def test_keeps_query_unchanged_when_nothing_generic():
    assert significant_terms("моцарелла для пиццы") == ["моцарелла", "пиццы"]


def test_falls_back_to_original_words_if_everything_is_generic():
    # If stripping would leave nothing, keep the original words rather than
    # returning an empty list (an empty list would match everything/nothing
    # unpredictably downstream).
    assert significant_terms("оптом для доставки") == ["оптом", "для", "доставки"]


def test_single_word_query():
    assert significant_terms("сыр") == ["сыр"]
