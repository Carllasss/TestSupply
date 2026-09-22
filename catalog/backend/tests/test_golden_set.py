"""Golden-set regression check for catalog search relevance.

Runs against a *live* backend (real Postgres + Qdrant + seeded data) rather
than mocks — search relevance is exactly the kind of thing that only shows
up with real embeddings and real data. Point it at any running instance via
GOLDEN_SET_BASE_URL (defaults to the mint tunnel on localhost:8080). Skips
instead of failing if nothing is listening there, so it doesn't break a
plain `pytest` run on a machine with no backend up.

Standalone use (nicer output than pytest's):
    python3 tests/test_golden_set.py [base_url]
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"
DEFAULT_BASE_URL = "http://localhost:8080"


def _base_url() -> str:
    return os.environ.get("GOLDEN_SET_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _load_cases() -> list[dict]:
    return json.loads(GOLDEN_SET_PATH.read_text())


def _search(base_url: str, query: str) -> list[str]:
    qs = urllib.parse.urlencode({"q": query})
    with urllib.request.urlopen(f"{base_url}/api/suppliers?{qs}", timeout=10) as resp:
        data = json.load(resp)
    return [s["name"] for s in data]


def _backend_reachable(base_url: str) -> bool:
    try:
        urllib.request.urlopen(f"{base_url}/api/suppliers/facets", timeout=3)
        return True
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return False


@pytest.fixture(scope="module")
def base_url():
    url = _base_url()
    if not _backend_reachable(url):
        pytest.skip(f"no backend reachable at {url} (set GOLDEN_SET_BASE_URL to point at one)")
    return url


@pytest.mark.parametrize("case", _load_cases(), ids=lambda c: c["query"])
def test_golden_set_case(base_url, case):
    names = _search(base_url, case["query"])

    for expected in case.get("expect_any", []):
        assert any(expected.lower() in n.lower() for n in names), (
            f"query {case['query']!r}: expected a result containing {expected!r}, got {names}"
        )

    for unwanted in case.get("expect_none", []):
        assert not any(unwanted.lower() in n.lower() for n in names), (
            f"query {case['query']!r}: unexpected irrelevant result containing {unwanted!r} in {names}"
        )

    max_results = case.get("max_results")
    if max_results is not None:
        assert len(names) <= max_results, (
            f"query {case['query']!r}: got {len(names)} results (max {max_results}): {names}"
        )


def _run_standalone(base_url: str) -> int:
    if not _backend_reachable(base_url):
        print(f"no backend reachable at {base_url}")
        return 1

    failures = 0
    for case in _load_cases():
        names = _search(base_url, case["query"])
        problems = []
        for expected in case.get("expect_any", []):
            if not any(expected.lower() in n.lower() for n in names):
                problems.append(f"missing {expected!r}")
        for unwanted in case.get("expect_none", []):
            if any(unwanted.lower() in n.lower() for n in names):
                problems.append(f"unexpected {unwanted!r}")
        max_results = case.get("max_results")
        if max_results is not None and len(names) > max_results:
            problems.append(f"{len(names)} results > max {max_results}")

        status = "FAIL" if problems else "ok"
        print(f"[{status}] {case['query']!r} -> {len(names)} results: {names}")
        if problems:
            failures += 1
            for p in problems:
                print(f"        - {p}")

    total = len(_load_cases())
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else _base_url()
    sys.exit(_run_standalone(url))
