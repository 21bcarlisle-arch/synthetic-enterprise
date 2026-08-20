"""Falsifiers for `tools/couple_clv.py` -- EP1's belief-vs-outcome coupled gap.

R15: every control here is written so it CAN fail, and each one is aimed at a
NAMED defect rather than at the code as it happens to be written. The three killer
patterns are addressed explicitly:

  TAUTOLOGY    -- `test_belief_equal_to_truth_drives_the_gap_to_zero` plus its NULL
                  CONTROL: a mutation that moves the SAMPLE must NOT reproduce the
                  same reading as a mutation that moves the LAW, or the metric is
                  measuring its own construction.
  FAIL-OPEN    -- an empty population, a degenerate no-skill divisor, and a missing
                  realised total must each report UNDEFINED, never 0.0. A gap of
                  zero reads as "the company is perfect" on the Proof door.
  FAIL-SILENT  -- an unreadable run artefact must RAISE. A measurement that cannot
                  run is a failed measurement, not a clean one.

No test writes the live ledger: `write_gap_entry` is only ever called with a
`tmp_path` destination (`background/live_ledger_guard.py` refuses otherwise).
"""
from __future__ import annotations

import copy
import json
import math

import pytest

from background.gap_metric import NORMALISATION_DIVISOR, write_gap_entry
from tools import couple_clv


# --- Fixtures ----------------------------------------------------------------

def _run(counted=None, supplied=None):
    """A minimal run artefact in the shape the real one publishes.

    `counted` are ceased accounts as (id, belief, realised); `supplied` are
    still-supplied account ids, which must never reach the counted population.
    """
    counted = counted if counted is not None else [
        ("C1", 900.0, 200.0), ("C3", 600.0, 100.0), ("C4", 700.0, -200.0)]
    supplied = supplied if supplied is not None else ["C2", "C9"]

    accounts, snapshots, lifetimes = {}, {"2016": {}, "2017": {}}, {}
    for account, belief, realised in counted:
        accounts[account] = {"still_supplied": False}
        snapshots["2016"][account] = belief
        # A LATER, different snapshot: the module must take the EARLIEST.
        snapshots["2017"][account] = belief * 10.0
        lifetimes[account] = {"net_margin_after_cost_to_serve_gbp": realised}
    for account in supplied:
        accounts[account] = {"still_supplied": True}
        snapshots["2016"][account] = 5000.0
        lifetimes[account] = {"net_margin_after_cost_to_serve_gbp": 4321.0}
    return {
        "by_billing_account": accounts,
        "clv_snapshots": snapshots,
        "per_customer_lifetime": lifetimes,
        "churned_billing_accounts": [a for a, _, _ in counted],
    }


# --- The population is the whole argument ------------------------------------

def test_still_supplied_accounts_are_excluded_as_right_censored():
    """The defect: scoring a forward estimate against a truncated realised total.
    The censored accounts here carry a huge belief and a huge realised value; if
    they leaked into the population every figure below would move."""
    result, detail = couple_clv.measure(_run())
    counted = {r["account"] for r in detail["counted"]}
    assert counted == {"C1", "C3", "C4"}
    assert all(e["reason"] == couple_clv.EXCLUSION_CENSORED
               for e in detail["excluded"])
    assert result.components["excluded_right_censored"] == 2
    # The denominator USED and the one AVAILABLE are both on the entry.
    assert result.components["counted_accounts"] == 3
    assert result.components["available_accounts"] == 5


def test_a_leaking_population_filter_changes_the_headline():
    """Null-control companion to the test above: prove the exclusion is load
    bearing. If including censored accounts left the gap unchanged, the filter
    would be decorative and the test above would be vacuous."""
    kept, _ = couple_clv.measure(_run())
    leaked_run = _run()
    for account in ("C2", "C9"):
        leaked_run["by_billing_account"][account]["still_supplied"] = False
    leaked, leaked_detail = couple_clv.measure(leaked_run)
    assert len(leaked_detail["counted"]) == 5
    assert leaked.gap != pytest.approx(kept.gap)


def test_the_earliest_snapshot_is_the_belief_not_the_latest():
    """The defect: taking the most recent belief, which is formed closest to the
    outcome and is therefore the easiest one to be right about. The fixture's
    later snapshot is 10x the earlier one, so a reader of the wrong year cannot
    coincide with a reader of the right one."""
    _, detail = couple_clv.measure(_run())
    by_account = {r["account"]: r for r in detail["counted"]}
    assert by_account["C1"]["belief_year"] == "2016"
    assert by_account["C1"]["belief_gbp"] == pytest.approx(900.0)


# --- Tautology and its null control ------------------------------------------

def test_belief_equal_to_truth_drives_the_gap_to_zero():
    """Moves the LAW: a perfectly informed company must score 0."""
    perfect = _run(counted=[("C1", 200.0, 200.0), ("C3", 100.0, 100.0),
                            ("C4", -200.0, -200.0)])
    result, _ = couple_clv.measure(perfect)
    assert result.raw_gap == pytest.approx(0.0)
    assert result.gap == pytest.approx(0.0)


def test_null_control_moving_the_sample_alone_does_not_zero_the_gap():
    """Moves the SAMPLE, not the law -- the null control the perfect-belief test
    needs to mean anything. Relabelling which accounts are in the book, while
    leaving each belief as wrong as it was, must NOT produce the zero reading.
    Without this, an implementation that returned 0.0 whenever the population
    changed would pass the test above and tell us nothing."""
    baseline, _ = couple_clv.measure(_run())
    resampled, _ = couple_clv.measure(_run(counted=[
        ("C7", 900.0, 200.0), ("C8", 600.0, 100.0), ("C9x", 700.0, -200.0)]))
    assert resampled.gap == pytest.approx(baseline.gap)
    assert resampled.gap > 0.0


def test_the_declared_normalisation_relation_actually_holds():
    """D44: the entry declares `gap = raw_gap / g0`. Check the arithmetic rather
    than trusting the declaration -- an entry may be constructed under a relation
    that is false of its own numbers."""
    result, _ = couple_clv.measure(_run())
    assert result.normalisation == NORMALISATION_DIVISOR
    assert result.gap == pytest.approx(result.raw_gap / result.g0)
    assert not any(k in result.components for k in
                   ("gap", "raw_gap", "g0", "baseline", "note", "metric"))


# --- Fail-open: undefined must never read as zero ----------------------------

def test_an_empty_population_reports_undefined_not_zero():
    """The defect: a run with no completed lifetime publishing `gap = 0.0`, which
    the Proof door renders as a company with a perfect estimate."""
    result, detail = couple_clv.measure(_run(counted=[], supplied=["C2", "C9"]))
    assert detail["counted"] == []
    assert result.gap is None


def test_a_degenerate_no_skill_divisor_reports_undefined_not_infinite():
    """Every account realising the SAME value leaves no per-customer variation for
    skill to find. g0 = 0, and the ratio is undefined -- not infinity, and above
    all not zero."""
    flat = _run(counted=[("C1", 900.0, 100.0), ("C3", 400.0, 100.0)])
    result, _ = couple_clv.measure(flat)
    assert result.g0 == pytest.approx(0.0)
    assert result.gap is None


def test_an_account_with_no_realised_total_is_excluded_by_name():
    """The defect: a missing realised margin coerced to 0.0 and entering the
    aggregate as though the customer were worth nothing (the `84ae6bbeb` class)."""
    run = _run()
    run["per_customer_lifetime"]["C3"]["net_margin_after_cost_to_serve_gbp"] = None
    result, detail = couple_clv.measure(run)
    assert {r["account"] for r in detail["counted"]} == {"C1", "C4"}
    reasons = {e["account"]: e["reason"] for e in detail["excluded"]}
    assert reasons["C3"] == couple_clv.EXCLUSION_NO_REALISED
    assert result.components["counted_accounts"] == 2


def test_an_account_with_no_recorded_belief_is_excluded_by_name():
    run = _run()
    for year in run["clv_snapshots"].values():
        year.pop("C4", None)
    _, detail = couple_clv.measure(run)
    reasons = {e["account"]: e["reason"] for e in detail["excluded"]}
    assert reasons["C4"] == couple_clv.EXCLUSION_NO_SNAPSHOT


# --- Fail-silent: an unavailable input is a failed measurement ---------------

def test_a_missing_run_artefact_raises_rather_than_measuring_nothing(tmp_path):
    with pytest.raises(OSError):
        couple_clv.load_run_output(tmp_path / "absent.json")


def test_an_unparseable_run_artefact_raises(tmp_path):
    bad = tmp_path / "run.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        couple_clv.load_run_output(bad)


# --- The independent roster cross-check --------------------------------------

def test_a_roster_disagreement_is_reported_not_silently_resolved():
    """Two independently-written fields say who left. When they disagree the
    module must SAY so -- resolving it silently would hide exactly the kind of
    population defect this atom's history is made of."""
    run = _run()
    run["churned_billing_accounts"] = ["C1", "C3"]          # drops C4
    result, detail = couple_clv.measure(run)
    assert detail["roster_crosscheck"]["agrees"] is False
    assert detail["roster_crosscheck"]["only_in_counted"] == ["C4"]
    assert result.components["roster_sources_agree"] is False
    # ...and the disagreement does NOT quietly change the population.
    assert {r["account"] for r in detail["counted"]} == {"C1", "C3", "C4"}


def test_an_absent_roster_field_reports_unavailable_not_agreement():
    """FAIL-SILENT: a cross-check that cannot run must not report success."""
    run = _run()
    run.pop("churned_billing_accounts")
    result, detail = couple_clv.measure(run)
    assert detail["roster_crosscheck"]["available"] is False
    assert result.components["roster_sources_agree"] is None


# --- The truth-window caveat is applied honestly ------------------------------

def test_only_positive_belief_against_negative_outcome_counts_as_robust():
    """The window bias can rescue a negative-belief/positive-outcome disagreement
    but never a positive-belief/negative-outcome one. Counting both as robust
    would overclaim; counting neither would discard the real finding."""
    run = _run(counted=[("C4", 700.0, -200.0),     # robust sign error
                        ("C6", -700.0, 2000.0),    # sign error, NOT robust
                        ("C1", 900.0, 200.0)])     # no sign error
    result, _ = couple_clv.measure(run)
    assert result.components["sign_disagreements"] == 2
    assert result.components["sign_errors_robust_to_window_bias"] == 1


# --- The live artefact, and the ledger write ---------------------------------

def test_the_live_run_artefact_yields_a_defined_measurable_gap():
    """The pair must actually be measurable on the real book -- the whole reason
    this harness exists is that the OBVIOUS formulation is not."""
    result, detail = couple_clv.measure(couple_clv.load_run_output())
    assert len(detail["counted"]) > 0
    assert result.gap is not None and math.isfinite(result.gap)
    assert result.components["excluded_right_censored"] > 0


def test_the_ledger_entry_round_trips_to_a_tmp_ledger(tmp_path):
    result, _ = couple_clv.measure(_run())
    ledger_path = tmp_path / "coupled_gap_ledger.json"
    ledger = write_gap_entry(couple_clv.LEDGER_KEY, couple_clv.TWIN_ATOM_ID,
                             result, measured_at="2026-08-19T00:00:00+00:00",
                             run_git_commit="deadbeef", ledger_path=ledger_path)
    entry = ledger[couple_clv.LEDGER_KEY]
    assert entry["twin_atom_id"] == couple_clv.TWIN_ATOM_ID
    assert entry["normalisation"] == NORMALISATION_DIVISOR
    assert entry["gap"] == pytest.approx(result.gap)
    on_disk = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert on_disk[couple_clv.LEDGER_KEY]["gap"] == pytest.approx(result.gap)


def test_measure_does_not_mutate_the_run_it_is_given():
    run = _run()
    before = copy.deepcopy(run)
    couple_clv.measure(run)
    assert run == before
