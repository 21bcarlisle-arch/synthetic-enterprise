"""Tests for tools/generate_phases_json.py.

Regression coverage for the R-A violation this generator fixes:
site/data/phases.json used to be hand-curated and went stale (frozen at
latest_phase "OL" from 2026-07-03 while the real build had moved dozens of
phases on, PROJECT_TAB_OVERHAUL.md critique). These tests exercise the
Section-4 header parser and the date-dedup/sort behaviour that fixes the
Project tab's duplicate-x-axis-label chart bug.
"""
from tools.generate_phases_json import _parse_build_history, _extract_test_count, _total_commits, _monotonic_test_progression, cumulative_commits_by_day


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


# --- _monotonic_test_progression (2026-07-10, real director-reported chart
# regression: a phase entry's partial/scoped "N tests passing" count got
# accepted as the running total, crashing the Home page chart from 16,358 to
# 221 on a single day) ---

def _entry(phase_id, date, tc):
    return (phase_id, date, tc, "title", "body")


def test_monotonic_test_progression_basic_increase():
    chrono = [_entry("A", "2026-01-01", 100), _entry("B", "2026-01-02", 150)]
    assert _monotonic_test_progression(chrono) == [["2026-01-01", 100], ["2026-01-02", 150]]


def test_monotonic_test_progression_rejects_a_lower_partial_count():
    """The exact regression: a later entry reports a small scoped count
    ("221 tests passing across two touched files") -- must not overwrite the
    running total with a lower number."""
    chrono = [
        _entry("A", "2026-07-09", 16358),
        _entry("B", "2026-07-10", 221),
    ]
    result = _monotonic_test_progression(chrono)
    assert result == [["2026-07-09", 16358]]


def test_monotonic_test_progression_accepts_equal_or_higher_same_day():
    chrono = [
        _entry("A", "2026-07-10", 100),
        _entry("B", "2026-07-10", 200),
    ]
    assert _monotonic_test_progression(chrono) == [["2026-07-10", 200]]


def test_monotonic_test_progression_skips_none_counts():
    chrono = [_entry("A", "2026-01-01", 100), _entry("B", "2026-01-02", None)]
    assert _monotonic_test_progression(chrono) == [["2026-01-01", 100]]


def test_monotonic_test_progression_empty_input():
    assert _monotonic_test_progression([]) == []


def test_monotonic_test_progression_a_real_valid_later_higher_count_still_lands():
    """After a rejected lower/partial count, a genuine subsequent higher
    total must still be accepted (the filter isn't a one-way lockout)."""
    chrono = [
        _entry("A", "2026-07-09", 16358),
        _entry("B", "2026-07-10", 221),
        _entry("C", "2026-07-11", 16500),
    ]
    result = _monotonic_test_progression(chrono)
    assert result == [["2026-07-09", 16358], ["2026-07-11", 16500]]


def test_monotonic_test_progression_stays_monotonic_when_input_out_of_date_order():
    """R15 (2026-07-27, G1 HARDEN): the published series must be monotonic BY
    DATE even when the caller passes entries out of chronological order --
    `chronological` is reversed FILE order of the hand-maintained, concurrently
    edited PROJECT_OVERVIEW.md, so a single out-of-newest-first entry is a real
    hazard, not a hypothetical.

    Here the later date (07-11) is iterated BEFORE the earlier date (07-10)
    which carries a higher count. Applying the running max in iteration order
    (the pre-hardening behaviour) retained BOTH -- yielding a date-sorted
    output that DROPS from 200 on 07-10 to 100 on 07-11, i.e. the single-day
    crash this function exists to prevent, re-entering FAIL-OPEN. The guard
    must instead operate in date order: the lower later-date value is refused.
    """
    chrono = [
        _entry("A", "2026-07-11", 100),  # later date, but listed first
        _entry("B", "2026-07-10", 200),  # earlier date, higher count
    ]
    result = _monotonic_test_progression(chrono)
    # Never decreasing between adjacent published dates.
    counts = [c for _d, c in result]
    assert counts == sorted(counts), f"published series must be non-decreasing by date, got {result}"
    # Concretely: 07-10 anchors the running max at 200; the lower 07-11 value
    # (100) is refused rather than published as a drop.
    assert result == [["2026-07-10", 200]]


def test_monotonic_test_progression_dateless_entry_with_count_does_not_crash_publish():
    """R15 (2026-07-27, G1 HARDEN sibling-half red-team): a Section-4 header
    with NO date parenthetical yields date=None from _iter_phase_entries, yet
    its body can still carry a test count -> entry (None, tc). Left in
    max_by_date, `sorted(max_by_date)` raises TypeError ('<' not supported
    between NoneType and str), propagating up through generate() and wedging
    the whole site publish -- the same FAIL-CRASH-on-malformed-record class the
    sibling half (cumulative_tests_executed non-int guard) was hardened
    against. Before the `date is None: continue` guard this raised; it must now
    skip the dateless entry AND still publish the genuine dated one."""
    chrono = [
        _entry("A", "2026-07-10", 16000),
        _entry("H7", None, 16358),  # dateless header carrying a real count
    ]
    result = _monotonic_test_progression(chrono)
    assert result == [["2026-07-10", 16000]], "dateless entry skipped, dated entry still lands"


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


# --- Director page comment 2026-07-12 (/project/ timeline): "just a long
# list... no filters or sort. No details behind. No link to epochs" ---

def test_epoch_for_extracts_epoch_number():
    from tools.generate_phases_json import _epoch_for
    assert _epoch_for("Epoch-2 bounded start") == 2
    assert _epoch_for("some text mentioning Epoch 3 midway") == 3
    assert _epoch_for("no epoch mention here") is None


def test_body_summary_returns_first_paragraph_not_header():
    from tools.generate_phases_json import _body_summary
    body = "### Phase AA -- Title (2026-07-01)\n\nThis is the real substance of the phase.\n\nSecond paragraph."
    assert _body_summary(body) == "This is the real substance of the phase."


def test_body_summary_empty_when_no_body_text():
    from tools.generate_phases_json import _body_summary
    assert _body_summary("### Phase AA (2026-07-01)\n") == ""


def test_body_summary_truncates_long_paragraphs():
    from tools.generate_phases_json import _body_summary
    long_para = "x" * 600
    body = "### Phase AA (2026-07-01)\n\n" + long_para
    summary = _body_summary(body)
    assert len(summary) == 503  # 500 + "..."
    assert summary.endswith("...")


def test_build_timeline_carries_epoch_and_summary():
    from tools.generate_phases_json import _build_timeline
    chronological = [
        ("AA", "2026-07-01", 100, "Epoch-2 bounded start",
         "### Phase AA -- Epoch-2 bounded start (2026-07-01)\n\nReal substance here.\n\nKEY FINDING: alpha happened.\n"),
    ]
    timeline = _build_timeline(chronological)
    phase_row = next(e for e in timeline if e["type"] == "phase")
    assert phase_row["epoch"] == 2
    assert phase_row["summary"] == "Real substance here."
    discovery_row = next(e for e in timeline if e["type"] == "discovery")
    assert discovery_row["epoch"] == 2, "discovery rows inherit their phase's epoch"


def test_build_timeline_epoch_none_when_not_mentioned():
    from tools.generate_phases_json import _build_timeline
    chronological = [("AA", "2026-07-01", 100, "Ordinary Title", "### Phase AA -- Ordinary Title (2026-07-01)\nno epoch mention.\n")]
    timeline = _build_timeline(chronological)
    assert timeline[0]["epoch"] is None


def test_build_timeline_emits_one_marker_per_epoch_at_first_mention():
    from tools.generate_phases_json import _build_timeline
    chronological = [
        ("AA", "2026-07-01", 100, "Epoch-1 kickoff", "### Phase AA -- Epoch-1 kickoff (2026-07-01)\nbody.\n"),
        ("AB", "2026-07-02", 110, "Ordinary phase", "### Phase AB -- Ordinary phase (2026-07-02)\nbody.\n"),
        ("AC", "2026-07-03", 120, "Epoch-2 bounded start", "### Phase AC -- Epoch-2 bounded start (2026-07-03)\nbody.\n"),
        ("AD", "2026-07-04", 130, "Epoch-2 continues", "### Phase AD -- Epoch-2 continues (2026-07-04)\nbody.\n"),
        ("AE", "2026-07-05", 140, "Epoch-3 starts", "### Phase AE -- Epoch-3 starts (2026-07-05)\nbody.\n"),
    ]
    timeline = _build_timeline(chronological)
    markers = [e for e in timeline if e["type"] == "epoch_marker"]
    assert len(markers) == 2, "one marker per epoch >= 2, at first mention only -- not one per phase, and not epoch 1"
    assert {m["epoch"] for m in markers} == {2, 3}
    marker2 = next(m for m in markers if m["epoch"] == 2)
    assert marker2["date"] == "2026-07-03"
    assert "Epoch-2 bounded start" in marker2["detail"]


def test_build_timeline_epoch_1_never_gets_a_marker():
    """Epoch 1 is the project's own foundational period -- marking it at
    the date it happens to be first NAMED (long after the true start) would
    be more misleading than no marker at all."""
    from tools.generate_phases_json import _build_timeline
    chronological = [
        ("AA", "2026-06-07", 5, "Project start", "### Phase AA -- Project start (2026-06-07)\nbody.\n"),
        ("AZ", "2026-07-10", 500, "Epoch 1 retrospective note", "### Phase AZ -- Epoch 1 retrospective note (2026-07-10)\nbody.\n"),
    ]
    timeline = _build_timeline(chronological)
    assert [e for e in timeline if e["type"] == "epoch_marker"] == []


def test_build_timeline_no_markers_when_no_epoch_ever_mentioned():
    from tools.generate_phases_json import _build_timeline
    chronological = [("AA", "2026-07-01", 100, "Ordinary", "### Phase AA -- Ordinary (2026-07-01)\nno epoch here.\n")]
    timeline = _build_timeline(chronological)
    assert [e for e in timeline if e["type"] == "epoch_marker"] == []


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


# --- cumulative_commits_by_day (2026-07-10, director page comment, 4th
# repeat of "these graphs look flat/decelerating": "I want to pick metrics,
# such as cumulative ones that show the growth we creating") ---

def test_cumulative_commits_by_day_basic():
    lines = ["2026-07-01", "2026-07-01", "2026-07-02"]
    assert cumulative_commits_by_day(lines) == [["2026-07-01", 2], ["2026-07-02", 3]]


def test_cumulative_commits_by_day_is_monotonic_non_decreasing():
    lines = ["2026-07-03", "2026-07-01", "2026-07-01", "2026-07-02", "2026-07-03", "2026-07-03"]
    result = cumulative_commits_by_day(lines)
    values = [v for _, v in result]
    assert values == sorted(values)


def test_cumulative_commits_by_day_ignores_blank_lines():
    lines = ["2026-07-01", "", "  ", "2026-07-01"]
    assert cumulative_commits_by_day(lines) == [["2026-07-01", 2]]


def test_cumulative_commits_by_day_empty_input():
    assert cumulative_commits_by_day([]) == []


def test_cumulative_commits_by_day_sorted_by_date_not_input_order():
    lines = ["2026-07-03", "2026-07-01", "2026-07-02"]
    result = cumulative_commits_by_day(lines)
    assert [d for d, _ in result] == ["2026-07-01", "2026-07-02", "2026-07-03"]


# --- R15 hardening (2026-07-29, G1_test_progression_metrics HARDEN): the
# COMMITS half of this atom's guarantee. The two test-count halves were
# hardened 2026-07-27; this half had never been red-teamed. `_total_commits()`
# and `_commits_per_day_lines()` swallow every exception and return None/[],
# and generate() runs inside the publish path -- so a git timeout or non-zero
# rc silently publishes `total_commits: null` / `commits_by_day: []` to the
# live Project page, where renderBuildStats() gates on `if(commits)` and the
# figure vanishes. FAIL-SILENT + FAIL-OPEN on a metric whose entire declared
# property is MONOTONIC growth. Every test below asserts BOTH that the defect
# is neutralised AND that the honest path still measures normally, so the
# guard is proven to fire on its own named defect rather than pinning a
# blanket freeze. ---

def _prev(total=6000, last_date="2026-07-28"):
    return {"total_commits": total, "commits_by_day": [["2026-07-01", 10], [last_date, total]]}


def test_git_unavailable_must_not_zero_the_published_commit_total():
    """The named defect: git times out, _total_commits() returns None and
    _commits_per_day_lines() returns [] -- unguarded that publishes null/[]
    and the live "6,572 commits" stat disappears."""
    from tools.generate_phases_json import _retained_commit_metrics
    total, series, source = _retained_commit_metrics(None, [], _prev())
    assert total == 6000, "an unavailable source must not zero a monotonic metric"
    assert series == _prev()["commits_by_day"]
    assert source == "retained_previous", "a retained figure must never be labelled fresh"


def test_commit_total_going_backwards_is_refused():
    """A rewritten/detached/behind HEAD (this repo runs worktrees) reports a
    LOWER count -- the same single-day-collapse class the test-count series
    was hardened against (16,358 -> 221)."""
    from tools.generate_phases_json import _retained_commit_metrics
    total, series, source = _retained_commit_metrics(
        200, [["2026-07-29", 200]], _prev())
    assert total == 6000, "a monotonic metric may never decrease"
    assert series[-1][1] == 6000
    assert source == "retained_previous"


def test_genuine_growth_is_published_and_labelled_measured():
    """The guard is not a freeze: a real advance publishes verbatim."""
    from tools.generate_phases_json import _retained_commit_metrics
    fresh = [["2026-07-01", 10], ["2026-07-29", 6600]]
    total, series, source = _retained_commit_metrics(6600, fresh, _prev())
    assert (total, series, source) == (6600, fresh, "measured")


def test_no_previous_publish_reports_unavailable_never_fabricates():
    """First-ever run with git broken: nothing to retain, so we publish
    nothing and say so -- retaining is honest, inventing is not."""
    from tools.generate_phases_json import _retained_commit_metrics
    total, series, source = _retained_commit_metrics(None, [], {})
    assert total is None and series == []
    assert source == "unavailable"


def test_nan_previous_total_cannot_disarm_the_monotonic_guard():
    """json.loads accepts a bare NaN literal; every NaN comparison is False,
    so an unvalidated prev_total would make `measured < prev` never fire."""
    from tools.generate_phases_json import _retained_commit_metrics
    total, _series, source = _retained_commit_metrics(
        200, [["2026-07-29", 200]], {"total_commits": float("nan"), "commits_by_day": []})
    assert total == 200 and source == "measured", "unusable prior is ignored, not trusted"
    total, _series, source = _retained_commit_metrics(
        None, [], {"total_commits": True, "commits_by_day": []})
    assert total is None and source == "unavailable", "bool is not a commit count"


def test_previously_published_tolerates_missing_and_corrupt_file(tmp_path):
    from tools.generate_phases_json import _previously_published
    assert _previously_published(tmp_path / "nope.json") == {}
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert _previously_published(bad) == {}
    listy = tmp_path / "list.json"
    listy.write_text("[1,2]")
    assert _previously_published(listy) == {}, "a non-dict publish is not a usable prior"


def test_generate_end_to_end_retains_commits_when_git_fails(tmp_path, monkeypatch):
    """Consumer-level (R11-shaped): drive the real generate() with git broken
    and assert the WRITTEN phases.json still carries the prior figure."""
    import json as _json
    from tools import generate_phases_json as g
    out = tmp_path / "phases.json"
    out.write_text(_json.dumps(_prev()))
    monkeypatch.setattr(g, "OUT_PATH", out)
    monkeypatch.setattr(g, "_total_commits", lambda: None)
    monkeypatch.setattr(g, "_commits_per_day_lines", lambda: [])
    g.generate()
    written = _json.loads(out.read_text())
    assert written["total_commits"] == 6000, "publish collapsed a monotonic metric to null"
    assert written["commits_source"] == "retained_previous"


def test_cumulative_commits_by_day_drops_non_date_lines():
    """A stray non-date token becomes its own bucket and publishes a garbage
    x-axis point; real dates must still land."""
    lines = ["2026-07-01", "warning: something", "", "2026-07-02", "not-a-date"]
    assert cumulative_commits_by_day(lines) == [["2026-07-01", 1], ["2026-07-02", 2]]
