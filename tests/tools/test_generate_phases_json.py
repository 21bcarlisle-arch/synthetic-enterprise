"""Tests for tools/generate_phases_json.py.

Regression coverage for the R-A violation this generator fixes:
site/data/phases.json used to be hand-curated and went stale (frozen at
latest_phase "OL" from 2026-07-03 while the real build had moved dozens of
phases on, PROJECT_TAB_OVERHAUL.md critique). These tests exercise the
Section-4 header parser and the date-dedup/sort behaviour that fixes the
Project tab's duplicate-x-axis-label chart bug.
"""
from tools.generate_phases_json import _parse_build_history, _extract_test_count, _total_commits


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


def test_header_without_phase_code_still_counts_with_synthetic_id():
    """2026-07-10: a header with no 'Phase XY' code at all (the drifted
    convention this whole session used) must still be counted and dated,
    not silently dropped -- gets a synthetic 'H<n>' id instead."""
    text = "### Tenure archetype -- Layer 2 dimension 3 (2026-07-10, note)\n50 tests collected\n"
    entries = _parse_build_history(text)
    assert len(entries) == 1
    phase_id, date, tc = entries[0]
    assert phase_id == "H0"
    assert date == "2026-07-10"
    assert tc == 50


def test_mixed_old_and_new_style_headers_both_counted():
    text = (
        "### Fuel-poverty archetype -- Layer 2 dimension 2 (2026-07-09, note)\n24 tests collected\n"
        "### Phase RC -- Old Style (2026-07-05)\n5 collected\n"
    )
    entries = _parse_build_history(text)
    assert len(entries) == 2
    assert entries[0] == ("H0", "2026-07-09", 24)
    assert entries[1] == ("RC", "2026-07-05", 5)


def test_extract_test_count_handles_tests_collected_phrasing():
    assert _extract_test_count("16,373 tests collected (full suite), up from 16,358.") == 16373


def test_extract_test_count_prefers_total_line_over_collected():
    body = "some prose 999 collected more prose\n**Total:** 15,342 tests\n"
    assert _extract_test_count(body) == 15342


def test_extract_test_count_returns_none_when_unparseable():
    assert _extract_test_count("no numbers relevant here") is None


def test_extract_test_count_handles_tests_passing_phrasing():
    assert _extract_test_count("182 tests passing in the suite") == 182


def test_total_commits_returns_positive_int_from_real_repo():
    count = _total_commits()
    assert isinstance(count, int)
    assert count > 0



def test_extract_title_strips_trailing_dated_metadata():
    from tools.generate_phases_json import _extract_title
    header = "### Phase RF -- Project Tab: Company Dedup, Chart Cosmetics (2026-07-05, Tier 2 -- notes)"
    assert _extract_title(header) == "Project Tab: Company Dedup, Chart Cosmetics"


def test_extract_title_preserves_internal_parens_not_containing_a_date():
    from tools.generate_phases_json import _extract_title
    header = "### Phase RE -- Shadow Mirror (WEBSITE_AS_SHOWCASE.md Part 0 CLOSED) + Data Layer (2026-07-06, Tier 2)"
    assert _extract_title(header) == "Shadow Mirror (WEBSITE_AS_SHOWCASE.md Part 0 CLOSED) + Data Layer"


def test_extract_title_handles_split_phase_parenthetical():
    from tools.generate_phases_json import _extract_title
    header = "### Phase QW (part 1) -- Consistency Fix: total_net_gbp (2026-07-05)"
    assert _extract_title(header) == "Consistency Fix: total_net_gbp"


def test_extract_title_without_double_dash_now_returns_the_bare_header():
    """2026-07-10: _HEADER_RE/_TITLE_RE were broadened after discovering the
    strict 'Phase XY -- Title' requirement silently dropped 38 of 496 real
    Section 4 entries (every one written since the header convention
    drifted to bare descriptive titles) -- a header without the old
    double-dash structure now still yields a usable title (the whole
    header, with only a real ISO-date parenthetical stripped) instead of
    None. "early June 2026" isn't an ISO date, so it's left intact here --
    only the digit-dated parenthetical case is stripped (see the sibling
    test below)."""
    from tools.generate_phases_json import _extract_title
    assert _extract_title("### Phase 0 Prove the Machine (early June 2026)") == \
        "Phase 0 Prove the Machine (early June 2026)"


def test_extract_title_strips_real_date_parenthetical_without_double_dash():
    from tools.generate_phases_json import _extract_title
    assert _extract_title("### Tenure archetype -- Layer 2 dimension 3 (2026-07-10, director note)") == \
        "Tenure archetype -- Layer 2 dimension 3"


def test_extract_findings_strips_prefix_and_returns_line_tail():
    from tools.generate_phases_json import _extract_findings
    body = "some prose\nKEY FINDING: the classifier missed 3 of 6 departures.\nmore prose\n"
    assert _extract_findings(body) == ["the classifier missed 3 of 6 departures."]


def test_extract_findings_handles_multiple_and_no_colon():
    from tools.generate_phases_json import _extract_findings
    body = "KEY FINDING (live run): first thing happened.\nKEY FINDING second thing happened.\n"
    findings = _extract_findings(body)
    assert findings == ["(live run): first thing happened.", "second thing happened."]


def test_extract_findings_returns_empty_list_when_none_present():
    from tools.generate_phases_json import _extract_findings
    assert _extract_findings("nothing notable here") == []


def test_build_timeline_emits_phase_and_discovery_rows_sorted_by_date():
    from tools.generate_phases_json import _build_timeline
    chronological = [
        ("AA", "2026-07-01", 100, "First Thing", "### Phase AA -- First Thing (2026-07-01)\nKEY FINDING: alpha happened.\n"),
        ("AB", "2026-07-02", 110, "Second Thing", "### Phase AB -- Second Thing (2026-07-02)\nno findings here.\n"),
    ]
    timeline = _build_timeline(chronological)
    assert [e["date"] for e in timeline] == ["2026-07-01", "2026-07-01", "2026-07-02"]
    assert timeline[0]["type"] == "phase"
    assert timeline[0]["phase_id"] == "AA"
    assert timeline[0]["label"] == "First Thing"
    assert timeline[0]["detail"] == "Phase AA -- 100 tests"
    assert timeline[1]["type"] == "discovery"
    assert timeline[1]["detail"] == "alpha happened."
    assert timeline[2]["type"] == "phase"
    assert timeline[2]["phase_id"] == "AB"


def test_build_timeline_falls_back_to_phase_id_label_when_no_title():
    from tools.generate_phases_json import _build_timeline
    chronological = [("ZZ", "2026-07-01", None, None, "### Phase ZZ (early) (2026-07-01)\n")]
    timeline = _build_timeline(chronological)
    assert timeline[0]["label"] == "Phase ZZ"
    assert timeline[0]["detail"] == "Phase ZZ"


def test_iter_phase_entries_matches_parse_build_history_ids_and_dates():
    from tools.generate_phases_json import _iter_phase_entries, _parse_build_history
    text = (
        "### Phase RC -- Newest (2026-07-05)\n5 collected\n"
        "### Phase RB -- Older (2026-07-04)\n4 collected\n"
    )
    full = list(_iter_phase_entries(text))
    old = _parse_build_history(text)
    assert [(pid, date, tc) for pid, date, tc, _t, _b in full] == old
    assert full[0][3] == "Newest"
    assert full[1][3] == "Older"
