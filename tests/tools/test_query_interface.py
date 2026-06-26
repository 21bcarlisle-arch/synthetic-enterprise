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
