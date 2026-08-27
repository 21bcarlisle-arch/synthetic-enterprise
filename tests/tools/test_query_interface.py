"""Tests for the NL query context generation used by the Talk-to-Data interface."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest


def _latest_run_json():
    reports = Path("docs/reports")
    candidates = sorted(
        reports.glob("run_output_*[0-9Z].json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


@pytest.fixture
def run_data():
    path = _latest_run_json()
    if path is None:
        pytest.skip("No run output JSON available")
    with open(path) as f:
        return json.load(f)


def test_extract_query_context_returns_string(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert isinstance(result, str)


def test_extract_query_context_non_empty(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert len(result) > 200


def test_extract_query_context_under_size_limit(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert len(result) < 8000, "Query context must be compact for API context window"


def test_extract_query_context_contains_portfolio_section(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert "PORTFOLIO" in result


def test_extract_query_context_contains_year_data(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert any(str(yr) in result for yr in range(2016, 2026))


def test_extract_query_context_contains_customer_data(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert "CUSTOMER" in result


def test_extract_query_context_handles_empty_data():
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context({})
    assert isinstance(result, str)
    assert result == ""


def test_extract_query_context_handles_none_data():
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(None)
    assert result == ""


def test_dashboard_json_contains_query_context(tmp_path, run_data):
    """generate() should write query_context into dashboard.json."""
    from tools.generate_dashboard_data import generate
    from tools import generate_dashboard_data as gdd

    out = tmp_path / "dashboard.json"
    path = _latest_run_json()
    if path is None:
        pytest.skip("No run output JSON available")

    with patch.object(gdd, "OUTPUT_PATH", out):
        generate(path)

    d = json.loads(out.read_text())
    assert "query_context" in d
    assert isinstance(d["query_context"], str)
    assert len(d["query_context"]) > 100


def test_extract_query_context_contains_financial_data(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert "FINANCIAL" in result or "financial" in result.lower() or "net" in result.lower()


def test_extract_query_context_contains_trading_data(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert "TRADING" in result or "hedge" in result.lower()


def test_extract_query_context_is_ascii_safe(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    result.encode("ascii", errors="strict")


def test_extract_query_context_starts_with_section_header(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert result.startswith("=") or result[:3].isupper() or "PORTFOLIO" in result[:100]


def test_extract_query_context_has_net_figure(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert "net" in result.lower() or "margin" in result.lower()


def test_extract_query_context_has_year_range(run_data):
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(run_data)
    assert "2016" in result or "2017" in result


# ---------------------------------------------------------------------------
# THE BOUND HOLDS AS THE BOOK GROWS (2026-08-27)
# ---------------------------------------------------------------------------
# `test_extract_query_context_under_size_limit` above measures the LIVE run output, so it only
# reds once a book big enough has actually been produced -- which is what happened: the
# per-account block reached 24,833 of 26,368 characters (94%) after the drawn population and a
# gas leg per dual-fuel home, in a function whose docstring promises "~2-4k chars".
#
# That test cannot distinguish "the bound works" from "today's book happens to be small". These
# two do: they drive the builder with a synthetic book far larger than any real one.

def _book(n):
    return {"ledger_pnl": {"revenue_gbp": 1.0}, "years": {},
            "per_customer_lifetime": {
                "ACC-{:06d}".format(i): {"net_gbp": float(i), "revenue_gbp": float(i) * 2,
                                         "segment": "resi", "commodity": "electricity"}
                for i in range(n)}}


def test_the_context_stays_compact_for_a_book_far_larger_than_todays():
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(_book(10_000))
    assert len(result) < 8000, (
        "the per-account block is unbounded again: {} chars on a 10,000-account book"
        .format(len(result)))


def test_the_omitted_accounts_are_COUNTED_and_pointed_at_rather_than_silently_dropped():
    """Bounded, never dropped. A summary that silently truncates reads as a complete list, and
    the reader has no way to know a number came from part of the book."""
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(_book(500))
    assert "500 accounts" in result
    assert "further accounts omitted" in result
    assert "per_customer_lifetime" in result, "the pointer to the full book must survive"


def test_the_accounts_kept_are_the_EXTREMES_not_the_alphabetical_head():
    """A question worth asking this context is "who makes and loses the money". A `sorted()`
    prefix would return whichever ids happen to sort first, which answers nothing."""
    from tools.generate_dashboard_data import QUERY_CONTEXT_NAMED_CUSTOMERS, extract_query_context
    result = extract_query_context(_book(500))
    assert "ACC-000499" in result, "the best account by net margin is missing"
    assert "ACC-000000" in result, "the worst account by net margin is missing"
    assert "ACC-000250" not in result, "a mid-book account should not have survived the bound"
    named = [ln for ln in result.splitlines() if ln.startswith("  ACC-")]
    assert len(named) == 2 * QUERY_CONTEXT_NAMED_CUSTOMERS


def test_a_small_book_is_shown_WHOLE_and_carries_no_omission_line():
    """The partner. The bound must not truncate a book that fits, nor claim an omission that
    did not happen."""
    from tools.generate_dashboard_data import extract_query_context
    result = extract_query_context(_book(5))
    assert "omitted" not in result
    for i in range(5):
        assert "ACC-{:06d}".format(i) in result
