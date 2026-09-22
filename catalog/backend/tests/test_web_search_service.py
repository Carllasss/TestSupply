from app.services.web_search_service import _domain, _unwrap_redirect, build_web_query


def test_domain_strips_www_and_lowercases():
    assert _domain("https://WWW.Example.com/path") == "example.com"


def test_domain_without_www_prefix():
    assert _domain("https://shop.example.com/") == "shop.example.com"


def test_domain_returns_empty_string_for_garbage_url():
    assert _domain("") == ""


def test_unwrap_duckduckgo_redirect():
    wrapped = "//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage&rut=abc"
    assert _unwrap_redirect(wrapped) == "https://example.com/page"


def test_unwrap_leaves_plain_urls_alone():
    assert _unwrap_redirect("https://example.com/page") == "https://example.com/page"


def test_build_web_query_appends_wholesale_hint_when_missing():
    assert build_web_query("моцарелла") == "моцарелла поставщик оптом"


def test_build_web_query_does_not_duplicate_existing_wholesale_hint():
    query = build_web_query("сыр оптом")
    assert query.count("оптом") == 1


def test_build_web_query_appends_region_when_given_and_missing():
    query = build_web_query("сыр", region="Екатеринбург")
    assert "Екатеринбург" in query


def test_build_web_query_does_not_duplicate_region_already_in_query():
    query = build_web_query("сыр в Екатеринбурге", region="Екатеринбург")
    assert query.lower().count("екатеринбург") == 1
