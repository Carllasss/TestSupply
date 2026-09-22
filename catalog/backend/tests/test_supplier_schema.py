from app.schemas.supplier import ConfirmCandidateRequest, DiscoverCandidate, SupplierCreate


def _minimal(**overrides):
    base = dict(name="Тест", category="сыр", region="Москва")
    base.update(overrides)
    return base


def test_website_with_javascript_uri_is_dropped():
    supplier = SupplierCreate(**_minimal(website="javascript:alert(1)"))
    assert supplier.website is None


def test_website_with_data_uri_is_dropped():
    supplier = SupplierCreate(**_minimal(website="data:text/html,<script>alert(1)</script>"))
    assert supplier.website is None


def test_website_with_plain_https_is_kept():
    supplier = SupplierCreate(**_minimal(website="https://example.com"))
    assert supplier.website == "https://example.com"


def test_website_is_optional():
    supplier = SupplierCreate(**_minimal())
    assert supplier.website is None


def test_confirm_candidate_source_url_with_javascript_uri_is_dropped():
    candidate = ConfirmCandidateRequest(**_minimal(source_url="javascript:alert(1)"))
    assert candidate.source_url is None


def test_discover_candidate_url_with_javascript_uri_becomes_empty_string():
    candidate = DiscoverCandidate(
        url="javascript:alert(1)", title="x", domain="x.com", already_in_catalog=False,
    )
    assert candidate.url == ""


def test_discover_candidate_url_with_plain_https_is_kept():
    candidate = DiscoverCandidate(
        url="https://example.com/page", title="x", domain="example.com", already_in_catalog=False,
    )
    assert candidate.url == "https://example.com/page"
