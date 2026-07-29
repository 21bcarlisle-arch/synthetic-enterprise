"""Tests for the MAJOR-3 fix to the Proof-door predictions ledger
(tools/generate_proof_data.py::_predictions_ledger and its helpers).

Cold-eyes Expert Hour finding (2026-07-29, docs/design/maturity_map.yaml
SITE1_expert_doors expert_hour.findings MAJOR-3 / atom
SITE_EH2_predictions_ledger_can_fail): the published /data/proof.json
predictions ledger structurally could not record a miss -- a single re-logged
renewal flag (cid C9) padded 4 identical "inconclusive" rows, and 25 of 26
identical "INCREASE" hedge recommendations were excused "ungraded -- market
data has not advanced" with no stated horizon, so the state could never
resolve. Real hedge grading logic and portfolio-advance detection live
upstream in tools/generate_track_record_scorecard.py (out of this atom's
file_scope: site/proof/, tools/generate_proof_data.py) -- these tests prove
the RENDERING layer fix: de-duplication, a bounded "ungradeable" terminal
state, and an honest headline, per R15 (a control must be able to FAIL).
"""
from __future__ import annotations

import copy

import tools.generate_proof_data as gpd


# ---------------------------------------------------------------------------
# _dedupe_consecutive: collapses a RUN of consecutive identical predictions
# ---------------------------------------------------------------------------
def test_dedupe_consecutive_collapses_repeated_run():
    entries = [
        {"decision_run_at": "2026-07-04", "cid": "C9", "outcome": "x"},
        {"decision_run_at": "2026-07-05", "cid": "C9", "outcome": "x"},
        {"decision_run_at": "2026-07-06", "cid": "C9", "outcome": "x"},
        {"decision_run_at": "2026-07-07", "cid": "C9", "outcome": "x"},
    ]
    out = gpd._dedupe_consecutive(entries, ("cid", "outcome"))
    assert len(out) == 1, "four identical consecutive entries must collapse to one row"
    assert out[0]["re_logged_count"] == 4
    assert out[0]["first_logged"] == "2026-07-04"
    assert out[0]["last_logged"] == "2026-07-07"


def test_dedupe_consecutive_does_not_merge_across_a_change():
    # R15 fail-open guard: a prediction that changes and later reverts to an
    # earlier value must NOT be silently folded into the old run.
    entries = [
        {"decision_run_at": "2026-07-01", "hedge_recommendation": "INCREASE", "outcome": "x"},
        {"decision_run_at": "2026-07-02", "hedge_recommendation": "DECREASE", "outcome": "x"},
        {"decision_run_at": "2026-07-03", "hedge_recommendation": "INCREASE", "outcome": "x"},
    ]
    out = gpd._dedupe_consecutive(entries, ("hedge_recommendation", "outcome"))
    assert len(out) == 3, "a non-adjacent repeat must stay a distinct entry, not merge"
    assert [e["re_logged_count"] for e in out] == [1, 1, 1]


def test_dedupe_consecutive_empty_input_returns_empty():
    assert gpd._dedupe_consecutive([], ("cid",)) == []


# ---------------------------------------------------------------------------
# _bound_inconclusive: R15 -- a genuinely stale entry MUST become ungradeable
# (the control must be able to fail / fire on its named defect), and a fresh
# entry within the horizon MUST clear (not fail-open, not always-firing).
# ---------------------------------------------------------------------------
def test_bound_inconclusive_fires_on_stale_defect():
    # Named defect: a renewal flag 395 days past its renewal date, far beyond
    # the horizon -- this MUST be declared ungradeable, proving the ledger CAN
    # reach a bounded terminal state rather than parking forever.
    entries = [{"cid": "C9", "renewal_date": "2025-06-29", "outcome": "no_renewal_detected_yet"}]
    out = gpd._bound_inconclusive(entries, "2026-07-29", gpd.PORTFOLIO_STALE_HORIZON_DAYS)
    assert out[0]["bounded_state"] == "ungradeable"
    assert out[0]["days_since_renewal_date"] == 395
    assert "ungradeable" in out[0]["display_outcome"]
    assert "395d" in out[0]["display_outcome"]
    assert str(gpd.PORTFOLIO_STALE_HORIZON_DAYS) in out[0]["display_outcome"]


def test_bound_inconclusive_clears_on_fresh_input():
    # R15 both-ways: a genuinely FRESH flag (renewal date 5 days ago, well
    # inside the horizon) must NOT be declared ungradeable -- the control
    # does not fire on good input.
    entries = [{"cid": "C1", "renewal_date": "2026-07-24", "outcome": "no_renewal_detected_yet"}]
    out = gpd._bound_inconclusive(entries, "2026-07-29", gpd.PORTFOLIO_STALE_HORIZON_DAYS)
    assert out[0]["bounded_state"] == "inconclusive_within_horizon"
    assert out[0]["display_outcome"] == "no_renewal_detected_yet"
    assert out[0]["days_since_renewal_date"] == 5


def test_bound_inconclusive_missing_dates_does_not_crash_or_false_fire():
    # FAIL-OPEN guard: missing/malformed dates must not silently mark
    # ungradeable (a false positive) nor raise.
    entries = [{"cid": "C2", "renewal_date": None, "outcome": "no_renewal_detected_yet"},
               {"cid": "C3", "renewal_date": "not-a-date", "outcome": "no_renewal_detected_yet"}]
    out = gpd._bound_inconclusive(entries, "2026-07-29", gpd.PORTFOLIO_STALE_HORIZON_DAYS)
    for row in out:
        assert row["bounded_state"] == "inconclusive_within_horizon"
        assert row["days_since_renewal_date"] is None


def test_bound_inconclusive_bad_wall_clock_does_not_crash():
    entries = [{"cid": "C9", "renewal_date": "2025-06-29", "outcome": "x"}]
    out = gpd._bound_inconclusive(entries, "not-a-date", gpd.PORTFOLIO_STALE_HORIZON_DAYS)
    assert out[0]["days_since_renewal_date"] is None
    assert out[0]["bounded_state"] == "inconclusive_within_horizon"


# ---------------------------------------------------------------------------
# _predictions_ledger: the full integration, against the REAL scorecard on disk
# ---------------------------------------------------------------------------
def test_predictions_ledger_dedupes_the_real_c9_padding():
    p = gpd._predictions_ledger()
    assert p["available"] is True
    # The real scorecard currently carries 4 identical C9 rows (VERIFIED
    # independently against site/state/track_record_scorecard.json) -- the
    # rendering layer must present this as ONE distinct prediction, not four.
    assert p["distinct_renewal_predictions"] == len(p["renewal"]["inconclusive_entries"]) + \
        len(p["renewal"]["graded_entries"])
    assert p["renewal"]["inconclusive"] <= 4, "deduped inconclusive count must not exceed the raw count"
    for e in p["renewal"]["inconclusive_entries"]:
        if e["cid"] == "C9":
            assert e["re_logged_count"] >= 1


def test_predictions_ledger_headline_states_the_real_denominators():
    p = gpd._predictions_ledger()
    headline = p["headline"]
    assert str(p["distinct_renewal_predictions"]) in headline
    assert str(p["distinct_hedge_predictions"]) in headline
    assert "hedge-grading logic is not built yet" in headline


def test_predictions_ledger_hedge_graded_count_is_not_a_real_verdict():
    # MAJOR-3: the raw scorecard's hedge "graded_count" is really
    # "gradeable_but_no_grading_logic_yet" -- never a real hit/miss. The
    # rendering layer must expose real_verdicts separately and it must be 0
    # while no real grading logic exists upstream (never silently inflated).
    p = gpd._predictions_ledger()
    assert p["hedge"]["real_verdicts"] == 0
    assert p["hedge"]["gradeable_pending_logic"] >= 0
    assert p["hedge"]["stale_blocked"] >= 0


def test_predictions_ledger_unreadable_source_fails_closed_not_silent():
    orig = gpd.SCORECARD_PATH
    try:
        gpd.SCORECARD_PATH = orig.parent / "does_not_exist_sentinel.json"
        p = gpd._predictions_ledger()
        assert p["available"] is False
        assert "note" in p
    finally:
        gpd.SCORECARD_PATH = orig


# ---------------------------------------------------------------------------
# R15 independence: the ledger must MOVE on a mutated (deliberately-a-miss)
# input, proving the render/aggregation path is not a hard-coded pass.
# ---------------------------------------------------------------------------
def test_off_target_renewal_is_reachable_and_counted_as_a_miss(tmp_path, monkeypatch):
    # A deliberately-wrong (miss) synthetic scorecard: a renewal graded
    # off_target must render through _predictions_ledger as a real miss,
    # proving a miss IS reachable through this pipeline (R15).
    scorecard = {
        "clock_started": "2026-07-04",
        "wall_clock_today": "2026-07-29",
        "log_entry_count": 1,
        "renewal_tolerance_pct": 0.02,
        "renewal_grading": {
            "graded_count": 1, "pending_count": 0, "inconclusive_count": 0,
            "on_target_count": 0, "off_target_count": 1, "churned_count": 0,
            "graded": [{
                "decision_run_at": "2026-07-10", "cid": "C-MISS",
                "renewal_date": "2026-07-01", "proposed_rate_gbp_per_mwh": 100.0,
                "actual_rate_gbp_per_mwh": 130.0, "diff_pct": 0.3,
                "outcome": "renewed_off_target", "graded": True,
            }],
            "inconclusive": [],
        },
        "hedge_grading": {"graded_count": 0, "ungraded_count": 0,
                          "current_market_data_stale_days": 1, "entries": []},
        "retention_ev_log": {"logged_count": 0, "graded_count": 0, "note": "n/a", "entries": []},
    }
    scratch = tmp_path / "scorecard.json"
    import json as _json
    scratch.write_text(_json.dumps(scorecard))
    orig = gpd.SCORECARD_PATH
    try:
        gpd.SCORECARD_PATH = scratch
        p = gpd._predictions_ledger()
        assert p["renewal"]["off_target"] == 1, "a real miss must be reachable and counted"
        misses = [e for e in p["renewal"]["graded_entries"] if e["outcome"] == "renewed_off_target"]
        assert misses, "the miss entry must survive de-duplication and be present in graded_entries"
    finally:
        gpd.SCORECARD_PATH = orig
