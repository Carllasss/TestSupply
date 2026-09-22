from unittest.mock import patch

import pytest

from app.services.extraction_service import ExtractionError, _assert_public_http_url


def _addrinfo_for(ip: str):
    return [(2, 1, 6, "", (ip, 0))]


@pytest.mark.parametrize("scheme_url", ["ftp://example.com", "javascript:alert(1)", "not-a-url"])
def test_rejects_non_http_schemes(scheme_url):
    with pytest.raises(ExtractionError):
        _assert_public_http_url(scheme_url)


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",       # loopback
        "10.0.0.5",        # private
        "192.168.1.50",    # private
        "172.18.0.2",      # docker bridge range (private)
        "169.254.169.254",  # link-local / cloud metadata
    ],
)
def test_blocks_hosts_resolving_to_non_public_ips(ip):
    with patch("socket.getaddrinfo", return_value=_addrinfo_for(ip)):
        with pytest.raises(ExtractionError):
            _assert_public_http_url("http://internal.example/path")


def test_allows_hosts_resolving_to_a_public_ip():
    with patch("socket.getaddrinfo", return_value=_addrinfo_for("93.184.216.34")):
        _assert_public_http_url("https://example.com/page")  # should not raise


def test_reports_unresolvable_host_as_extraction_error():
    import socket

    with patch("socket.getaddrinfo", side_effect=socket.gaierror("nope")):
        with pytest.raises(ExtractionError):
            _assert_public_http_url("https://does-not-resolve.invalid/")
