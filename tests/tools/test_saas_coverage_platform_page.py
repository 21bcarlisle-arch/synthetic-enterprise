"""Regression tests for SAAS_COVERAGE_MAP.md's Platform-page rendering
(Phase RW): the SaaS Estate Coverage Map placeholder on site/platform/index.html
is replaced with a real fetch/render of saas_coverage.json."""
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parents[2]


def _read(rel):
    return (PROJECT / rel).read_text()


def test_platform_page_no_longer_says_queued_not_yet_built():
    html = _read("site/platform/index.html")
    assert "Queued, not yet built" not in html


def test_platform_page_fetches_saas_coverage_json():
    html = _read("site/platform/index.html")
    assert "saas_coverage.json" in html
    assert "renderSaasCoverage" in html


def test_architecture_doc_exists_and_is_referenced():
    doc = PROJECT / "docs" / "architecture" / "SAAS_COVERAGE_MAP.md"
    assert doc.exists()
    html = _read("site/platform/index.html")
    assert "docs/architecture/SAAS_COVERAGE_MAP.md" in html
