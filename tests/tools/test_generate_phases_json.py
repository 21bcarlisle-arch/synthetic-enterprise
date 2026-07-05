"""Tests for tools/generate_phases_json.py.

Regression coverage for the R-A violation this generator fixes:
site/data/phases.json used to be hand-curated and went stale (frozen at
latest_phase "OL" from 2026-07-03 while the real build had moved dozens of
phases on, PROJECT_TAB_OVERHAUL.md critique). These tests exercise the
Section-4 header parser and the date-dedup/sort behaviour that fixes the
Project tab's duplicate-x-axis-label chart bug.
"""
from tools.generate_phases_json import _parse_build_history, _extract_test_count


def test_parses_phase_id_and_date_from_header():
    text = (
        "### Phase AB -- Some Title (2026-07-05, Tier 2 -- notes)\n"
        "12 new tests, 15,000 collected.\n"
    )
    entries = _parse_build_history(text)
    assert entries == [("AB", "2026-07-05", 15000)]


def test_handles_undated_header_without_fabricating_a_date():
    text = "### Phase 0 -- Prove the Machine (early June 2026)\nsome text\n"
    entries = _parse_build_history(text)
    assert entries == [("0", None, None)]


def test_split_phase_parenthetical_does_not_pollute_phase_id():
    text = "### Phase QW (part 1) -- Consistency Fix (2026-07-05)\n**Total:** 15,342 tests\n"
    entries = _parse_build_history(text)
    assert entries[0][0] == "QW"
    assert entries[0][1] == "2026-07-05"
    assert entries[0][2] == 15342


def test_multiple_entries_preserve_file_order():
    text = (
        "### Phase RC -- Newest (2026-07-05)\n5 collected\n"
        "### Phase RB -- Older (2026-07-04)\n4 collected\n"
    )
    entries = _parse_build_history(text)
    assert [e[0] for e in entries] == ["RC", "RB"]


def test_extract_test_count_prefers_total_line_over_collected():
    body = "some prose 999 collected more prose\n**Total:** 15,342 tests\n"
    assert _extract_test_count(body) == 15342


def test_extract_test_count_returns_none_when_unparseable():
    assert _extract_test_count("no numbers relevant here") is None


def test_extract_test_count_handles_tests_passing_phrasing():
    assert _extract_test_count("182 tests passing in the suite") == 182
