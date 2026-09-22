from app.services.recommendation_service import _find_winner_name


def test_finds_exact_name_mentioned_in_text():
    text = "Лучший вариант — ООО «Ромашка», у них есть нужный объём."
    names = ["ООО «Ромашка»", "ЗАО Вектор"]
    assert _find_winner_name(text, names) == "ООО «Ромашка»"


def test_returns_none_when_no_name_is_literally_present():
    # This is the hallucination guard: if the model names a company that
    # isn't one of the given candidates, we must not "find" a winner.
    text = "Рекомендую GFC-Russia, у них своя логистика."
    names = ["ООО «Ромашка»", "ЗАО Вектор"]
    assert _find_winner_name(text, names) is None


def test_picks_the_earliest_mentioned_name_when_several_appear():
    text = "ЗАО Вектор тоже неплох, но лучше ООО «Ромашка»."
    names = ["ООО «Ромашка»", "ЗАО Вектор"]
    assert _find_winner_name(text, names) == "ЗАО Вектор"


def test_ignores_empty_names_in_the_candidate_list():
    text = "Рекомендую ООО «Ромашка»."
    names = ["", None, "ООО «Ромашка»"]
    assert _find_winner_name(text, names) == "ООО «Ромашка»"


def test_case_insensitive_match():
    text = "лучший вариант — ооо «ромашка»."
    names = ["ООО «Ромашка»"]
    assert _find_winner_name(text, names) == "ООО «Ромашка»"
