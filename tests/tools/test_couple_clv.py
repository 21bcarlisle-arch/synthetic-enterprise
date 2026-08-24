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

def _run(counted=None, supplied=None, off_book=()):
    """A minimal run artefact in the shape the real one publishes.

    `counted` are ceased accounts as (id, belief, realised); `supplied` are
    still-supplied account ids, which must never reach the counted population.

    `off_book` are ceased accounts in the same (id, belief, realised) shape that
    get NO `by_billing_account` row -- the shape a DRAWN customer actually has on
    the live book, because that table is built from the seed roster only. The
    default is empty so the pre-existing controls below keep their original
    population; the tests that name this defect pass it explicitly.

    THE FINAL SNAPSHOT YEAR HOLDS ONLY THE SUPPLIED ACCOUNTS, which is what the
    real artefact looks like: `_build_clv_snapshots` drops an account once its own
    truncated window shows it ceased. That drop is the independent cross-check
    signal, so a fixture in which nobody ever leaves the snapshot series would
    make the cross-check untestable.
    """
    counted = counted if counted is not None else [
        ("C1", 900.0, 200.0), ("C3", 600.0, 100.0), ("C4", 700.0, -200.0)]
    supplied = supplied if supplied is not None else ["C2", "C9"]

    accounts = {}
    snapshots = {"2016": {}, "2017": {}, "2018": {}}
    lifetimes = {}
    for account, belief, realised in list(counted) + list(off_book):
        snapshots["2016"][account] = belief
        # A LATER, different snapshot: the module must take the EARLIEST.
        snapshots["2017"][account] = belief * 10.0
        lifetimes[account] = {"net_margin_after_cost_to_serve_gbp": realised}
    for account, _, _ in counted:
        accounts[account] = {"still_supplied": False}
    for account in supplied:
        accounts[account] = {"still_supplied": True}
        for year in snapshots.values():
            year[account] = 5000.0
        lifetimes[account] = {"net_margin_after_cost_to_serve_gbp": 4321.0}
    return {
        "by_billing_account": accounts,
        "clv_snapshots": snapshots,
        "per_customer_lifetime": lifetimes,
        "churned_billing_accounts": [a for a, _, _ in list(counted) + list(off_book)],
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
    leaked_run["churned_billing_accounts"] += ["C2", "C9"]
    leaked, leaked_detail = couple_clv.measure(leaked_run)
    assert len(leaked_detail["counted"]) == 5
    assert leaked.gap != pytest.approx(kept.gap)


# --- The population source: the defect pass 16 was drawn on -------------------

def test_a_ceased_account_with_no_billing_row_is_still_counted():
    """THE NAMED DEFECT (2026-08-24, pass 16). This module used to walk
    `by_billing_account`, which `saas/reporting/annual_report.py` builds from the
    SEED roster (`CUSTOMERS`) alone, while snapshots, lifetimes and the churn
    roster are built over `CUSTOMERS + SUCCESSOR_CUSTOMERS + DRAWN_CUSTOMERS`. A
    drawn customer who lived and left therefore had a belief, an outcome and a
    churn event -- and was invisible to the harness grading the estimator.

    Measured on the 2026-08-24 book: 5 counted where 19 were available."""
    run = _run(off_book=[("PROS-2019-0024", 1200.0, 300.0)])
    assert "PROS-2019-0024" not in run["by_billing_account"]
    _, detail = couple_clv.measure(run)
    assert "PROS-2019-0024" in {r["account"] for r in detail["counted"]}


def test_the_off_book_population_is_load_bearing_on_the_headline():
    """Null control for the test above: an account merely APPEARING in the
    counted list proves nothing if it does not reach the arithmetic. The off-book
    account here is wrong in a different direction from the seed accounts, so a
    headline that ignored it cannot coincide with one that did not."""
    without, _ = couple_clv.measure(_run())
    with_off_book, detail = couple_clv.measure(
        _run(off_book=[("PROS-2019-0024", 1200.0, 300.0)]))
    assert len(detail["counted"]) == 4
    assert with_off_book.gap != pytest.approx(without.gap)
    assert with_off_book.components["available_accounts"] == 6


def test_the_denominator_counts_the_whole_book_not_one_table():
    """`available` is the union of every source, so an account known ONLY to the
    lifetime table still shows up as available rather than vanishing from both
    the numerator and the denominator -- a silent drop that would leave the
    published population self-consistent and wrong."""
    run = _run()
    run["per_customer_lifetime"]["PROS-2020-0043"] = {
        "net_margin_after_cost_to_serve_gbp": -281.44}
    assert "PROS-2020-0043" in couple_clv.known_accounts(run)
    result, _ = couple_clv.measure(run)
    assert result.components["available_accounts"] == 6


@pytest.mark.parametrize("source, value", [
    ("by_billing_account", {"still_supplied": True}),
    ("clv_snapshots", None),                       # handled below
    ("per_customer_lifetime", {"net_margin_after_cost_to_serve_gbp": 12.0}),
    ("churned_billing_accounts", None),            # handled below
])
def test_every_source_contributes_to_the_denominator(source, value):
    """EACH of the four sources must be load bearing on its own.

    Written because the mutation that dropped ONE source from the union fired
    ZERO tests: the earlier fixtures give every extra account a row in three
    sources at once, so removing any one of them left the account reachable by
    the others and nothing could tell. That is the same blind-fixture shape this
    project keeps catching -- a control that only exercises the sources jointly
    cannot show that the union is a union.

    On the live book the snapshot source is currently REDUNDANT (every account it
    holds is also in `per_customer_lifetime`), so this is the only place its
    contribution is visible at all. A denominator that silently shrinks is the
    defect: it makes the counted fraction look better without anyone deciding to
    exclude anybody."""
    run = _run()
    before = len(couple_clv.known_accounts(run))
    if source == "clv_snapshots":
        run["clv_snapshots"]["2016"]["ONLY-HERE"] = 500.0
    elif source == "churned_billing_accounts":
        run["churned_billing_accounts"] = run["churned_billing_accounts"] + ["ONLY-HERE"]
    else:
        run[source]["ONLY-HERE"] = value
    assert "ONLY-HERE" in couple_clv.known_accounts(run), (
        f"an account known ONLY to {source} vanished from the denominator")
    assert len(couple_clv.known_accounts(run)) == before + 1


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

def test_the_crosscheck_agrees_when_the_two_derivations_agree():
    """The baseline the disagreement tests below are measured against. The roster
    (a churn EVENT) and the snapshot drop (a meter going QUIET) are two different
    derivations; on an ordinary book they name the same accounts."""
    result, detail = couple_clv.measure(_run())
    assert detail["roster_crosscheck"]["agrees"] is True
    assert result.components["roster_sources_agree"] is True
    assert result.components["crosscheck_snapshot_coverage"] == 5


def test_a_snapshot_drop_the_roster_does_not_name_is_reported():
    """An account the snapshot series dropped but no churn event names. Reported,
    never used to overrule the authority -- a disagreement between two fields
    that should agree is a finding, not something for this module to resolve."""
    run = _run()
    run["clv_snapshots"]["2018"].pop("C2")          # goes quiet, no churn event
    result, detail = couple_clv.measure(run)
    assert detail["roster_crosscheck"]["agrees"] is False
    assert detail["roster_crosscheck"]["only_in_snapshot_drop"] == ["C2"]
    # ...and the disagreement does NOT quietly change the population.
    assert {r["account"] for r in detail["counted"]} == {"C1", "C3", "C4"}
    assert result.components["roster_sources_agree"] is False


def test_an_account_that_churned_before_any_snapshot_is_not_a_disagreement():
    """COVERAGE IS DECLARED. The snapshot series can only speak about accounts it
    ever valued; three accounts on the live 2026-08-24 roster
    (PROS-2018-0002, PROS-2019-0082, PROS-2020-0081) left before their first
    year-end snapshot. Counting them as cross-check failures would make a
    correctly-reported blind spot look like a data defect."""
    run = _run()
    run["churned_billing_accounts"] = run["churned_billing_accounts"] + ["PROS-X"]
    run["per_customer_lifetime"]["PROS-X"] = {
        "net_margin_after_cost_to_serve_gbp": 114.10}
    result, detail = couple_clv.measure(run)
    assert detail["roster_crosscheck"]["never_snapshotted"] == ["PROS-X"]
    assert detail["roster_crosscheck"]["agrees"] is True
    # It is still excluded BY NAME rather than silently dropped.
    reasons = {e["account"]: e["reason"] for e in detail["excluded"]}
    assert reasons["PROS-X"] == couple_clv.EXCLUSION_NO_SNAPSHOT


def test_an_absent_roster_makes_the_measurement_unavailable_not_empty():
    """FAIL-OPEN, and the reason this changed shape in pass 16. The roster is now
    the ceased AUTHORITY, so without it nothing is known to have left -- and the
    tempting behaviour, letting every account fall through as right-censored, is
    exactly the fail-open pattern: it publishes a serene 'no completed lifetime
    to score' over a book full of them."""
    run = _run()
    run.pop("churned_billing_accounts")
    result, detail = couple_clv.measure(run)
    assert detail["unavailable"] == couple_clv.UNAVAILABLE_NO_ROSTER
    assert result.gap is None
    assert result.components["unavailable_reason"] == couple_clv.UNAVAILABLE_NO_ROSTER
    assert "UNAVAILABLE" in result.note
    # ...and it is distinguishable from a genuinely empty population, which is a
    # DIFFERENT state and says so.
    empty, empty_detail = couple_clv.measure(_run(counted=[]))
    assert empty_detail["unavailable"] is None
    assert empty.gap is None
    assert empty.note != result.note


def test_an_absent_crosscheck_reports_unavailable_not_agreement():
    """FAIL-SILENT: a cross-check that cannot run must not report success."""
    run = _run()
    run["clv_snapshots"] = {}
    result, detail = couple_clv.measure(run)
    assert detail["roster_crosscheck"]["available"] is False
    assert result.components["roster_sources_agree"] is None


def test_a_still_supplied_flag_contradicting_the_roster_is_reported():
    """The third, partial-coverage signal. `still_supplied` is the reporting
    layer's own reading and covers seed accounts only; where it contradicts the
    world's churn event the module says which account, rather than picking one."""
    run = _run()
    run["by_billing_account"]["C4"]["still_supplied"] = True   # roster says ceased
    result, detail = couple_clv.measure(run)
    assert detail["roster_crosscheck"]["still_supplied_disagrees"] == ["C4"]
    assert result.components["still_supplied_disagrees_with_roster"] == ["C4"]
    # The authority still decides the population.
    assert "C4" in {r["account"] for r in detail["counted"]}


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


# --- WHOSE ESTIMATOR THIS ROW GRADES (pass 17) --------------------------------
#
# THE NAMED DEFECT these controls exist for: the ledger row is keyed
# `EP1_clv_three_horizon` and the belief it grades is produced by
# `saas/clv_model.py::build_clv`, an estimator that is not EP1's and is not in
# EP1's `file_scope`. Measured on the live artefact 2026-08-24: zeroing or
# deleting EP1's ENTIRE published output leaves the headline bit-identical.
#
# That is a failure shape the three R15 names do not cover. The checker is
# correct, it can fail, and it fails honestly -- about the wrong subject. A
# mutation battery aimed at the checker cannot see it; only a mutation aimed at
# the SUBJECT can. So the mutations below are aimed at the subject.


def _producer_tree(tmp_path, body, imports="from saas.clv_model import build_clv"):
    """A throwaway repo root holding just the belief producer.

    `belief_provenance` reads the SOURCE, so a fake tree is the only way to
    mutate the wiring without touching the real reporting layer mid-suite.
    """
    producer = tmp_path / couple_clv.BELIEF_PRODUCER_FILE
    producer.parent.mkdir(parents=True, exist_ok=True)
    producer.write_text(
        f"{imports}\n\n\ndef {couple_clv.BELIEF_PRODUCER_FUNCTION}(records, risk, years):\n"
        f"{body}\n", encoding="utf-8")
    return tmp_path


def test_the_real_tree_resolves_the_declared_belief_producer():
    """The declaration is TRUE of the tree it ships in, or it is decoration."""
    prov = couple_clv.belief_provenance()
    assert prov["estimator_is_called"] is True
    assert prov["estimator_imported_from"] == couple_clv.BELIEF_ESTIMATOR_MODULE
    assert prov["verified"] is True


def test_the_ledger_entry_names_the_estimator_it_actually_grades():
    """A reader of the row must not have to infer whose number it is."""
    result, _ = couple_clv.measure(_run())
    prov = result.components["belief_provenance"]
    assert prov["produced_by"] == (
        f"{couple_clv.BELIEF_PRODUCER_FILE}::{couple_clv.BELIEF_PRODUCER_FUNCTION}")
    assert prov["estimator_callable"] == couple_clv.BELIEF_ESTIMATOR_CALLABLE
    assert result.components["grades_atom_estimator"] is False
    # The note must SAY it, not merely carry a field a reader may not open.
    assert "does NOT grade EP1" in result.note
    assert "clv_three_horizon" in result.note


def test_deleting_ep1s_entire_output_leaves_the_headline_identical():
    """THE MIS-SUBJECTION, PINNED.

    This is the mutation that exposed the defect, kept as a permanent control.
    It asserts the CURRENT, honest state: EP1's output is not an input here. The
    day someone wires EP1's estimator into the graded belief this test FAILS --
    which is the point. It fails loudly at the moment the declaration
    `GRADES_ATOM_ESTIMATOR = False` stops being true, instead of letting the row
    silently start meaning something new.
    """
    run = _run()
    run["three_horizon_clv"] = {
        "accounts": {"C1": {"tenure_expected": {"value_gbp": 12345.0}}},
        "portfolio": {"total_gbp": 999999.0},
    }
    with_ep1, _ = couple_clv.measure(run)

    zeroed = copy.deepcopy(run)
    zeroed["three_horizon_clv"]["accounts"]["C1"]["tenure_expected"]["value_gbp"] = 0.0
    zeroed["three_horizon_clv"]["portfolio"]["total_gbp"] = 0.0
    assert couple_clv.measure(zeroed)[0].gap == with_ep1.gap

    deleted = copy.deepcopy(run)
    deleted.pop("three_horizon_clv")
    assert couple_clv.measure(deleted)[0].gap == with_ep1.gap

    # NULL CONTROL. Without this the test above would also pass on a measurement
    # that is insensitive to EVERYTHING -- a headline pinned to a constant would
    # satisfy it. Moving the belief the row DOES grade must move the number.
    moved = copy.deepcopy(run)
    for snap in moved["clv_snapshots"].values():
        for account in snap:
            if isinstance(snap[account], (int, float)):
                snap[account] *= 1.01
    assert couple_clv.measure(moved)[0].gap != with_ep1.gap


def test_a_missing_belief_producer_raises_rather_than_grading_anyway(tmp_path):
    """FAIL-SILENT. Unable to say what it measures = a failed measurement."""
    with pytest.raises(FileNotFoundError):
        couple_clv.belief_provenance(repo_root=tmp_path)


def test_a_producer_missing_the_declared_function_raises(tmp_path):
    root = tmp_path / "r"
    producer = root / couple_clv.BELIEF_PRODUCER_FILE
    producer.parent.mkdir(parents=True, exist_ok=True)
    producer.write_text("def something_else():\n    return {}\n", encoding="utf-8")
    with pytest.raises(ValueError):
        couple_clv.belief_provenance(repo_root=root)


def test_a_producer_that_stopped_calling_the_declared_estimator_is_unverified(tmp_path):
    """MUTATION: the belief moves to a different estimator and nobody updates
    the declaration. `verified` must go False rather than the row carrying a
    stale claim about whose number it holds."""
    root = _producer_tree(tmp_path / "r", "    return some_other_model(records)")
    prov = couple_clv.belief_provenance(repo_root=root)
    assert prov["estimator_is_called"] is False
    assert prov["verified"] is False


def test_a_producer_importing_the_estimator_from_elsewhere_is_unverified(tmp_path):
    """MUTATION: same callable NAME, different module -- the shape a rename or a
    shim would take. Matching on the name alone would pass this."""
    root = _producer_tree(tmp_path / "r", "    return build_clv(records)",
                          imports="from saas.legacy_clv import build_clv")
    prov = couple_clv.belief_provenance(repo_root=root)
    assert prov["estimator_is_called"] is True
    assert prov["estimator_imported_from"] == "saas.legacy_clv"
    assert prov["verified"] is False


def test_wiring_ep1_into_the_producer_flips_grades_atom_estimator(tmp_path):
    """THE CONTROL FIRES THE OTHER WAY TOO.

    Without this, `grades_atom_estimator` could be hard-wired to False and every
    test above would still pass -- the FAIL-OPEN pattern inverted. Wiring EP1's
    estimator into the producer must flip it to True, and must then leave
    `verified` False until the module constant is updated with it.

    THE FIXTURE STILL CALLS `build_clv`, AND THAT IS THE WHOLE POINT (found by
    running the mutation, not by reading the assertion). The first version of
    this test had the producer call EP1's estimator INSTEAD of `build_clv`. That
    made `estimator_is_called` False, so `verified` came out False by a route
    that has nothing to do with the declaration -- and the mutation that deletes
    the declaration check from `verified` fired ZERO tests. This is the identical
    blind-fixture shape pass 16 recorded as its own M5. Blending both calls is
    what isolates the one condition under test: every other input to `verified`
    is now satisfied, so only the declaration comparison can make it False.
    """
    root = _producer_tree(
        tmp_path / "r",
        ("    base = build_clv(risk, records)\n"
         "    return clv_three_horizon.estimate_book(records) or base"),
        imports=("from saas.clv_model import build_clv\n"
                 "from company.analytics import clv_three_horizon"))
    prov = couple_clv.belief_provenance(repo_root=root)
    # Everything verified() looks at EXCEPT the declaration is satisfied here.
    assert prov["estimator_is_called"] is True
    assert prov["estimator_imported_from"] == couple_clv.BELIEF_ESTIMATOR_MODULE
    assert prov["grades_atom_estimator"] is True
    assert prov["verified"] is False, (
        "the wiring changed and GRADES_ATOM_ESTIMATOR still says False -- the "
        "declaration must be updated, not silently outvoted by the tree")


# --- THE ERROR DECOMPOSITION (R4) ---------------------------------------------


def test_a_pure_scale_error_is_attributed_to_the_scalar():
    """A belief that is exactly 3x the truth has PERFECT ranking and a terrible
    MAE ratio. The decomposition must say so, or `gap > 1` will keep being read
    as 'carries no information about the individual customer'."""
    counted = [{"belief_gbp": 3 * t, "realised_gbp": float(t)}
               for t in (100, 200, 400, 800, -300)]
    dec = couple_clv.magnitude_diagnostic(counted)
    assert dec["magnitude_inflated_accounts"] == len(counted)
    assert dec["best_single_scale"] == pytest.approx(1 / 3)
    assert dec["gap_after_best_single_scale"] == pytest.approx(0.0, abs=1e-9)


def test_null_control_an_unbiased_belief_is_not_attributed_to_a_scalar():
    """THE NULL CONTROL for the test above, and it is what makes it mean
    anything. A diagnostic that collapsed the gap for EVERY input would satisfy
    the scale test while distinguishing nothing. Here the errors are symmetric
    and there is no scale to find: the best scalar must stay near 1 and must NOT
    drive the gap to zero."""
    counted = [{"belief_gbp": t + e, "realised_gbp": float(t)} for t, e in
               ((100, 90), (200, -90), (400, 90), (800, -90), (-300, 90))]
    dec = couple_clv.magnitude_diagnostic(counted)
    assert dec["magnitude_inflated_accounts"] < len(counted)
    assert dec["best_single_scale"] == pytest.approx(1.0, abs=0.15)
    assert dec["gap_after_best_single_scale"] > 0.1


def test_the_decomposition_declares_itself_in_sample():
    """R12 / tautology guard: an in-sample fit reported as skill would be a
    number to steer by. The flag and the reading must travel with it."""
    dec = couple_clv.magnitude_diagnostic(
        [{"belief_gbp": 300.0, "realised_gbp": 100.0},
         {"belief_gbp": 600.0, "realised_gbp": 200.0}])
    assert dec["in_sample"] is True
    assert "never a correction" in dec["reading"]


def test_an_empty_population_still_reports_whose_estimator_it_would_grade():
    """The pass-16 lesson, applied to the new field: the branch where nothing
    can be scored is exactly where a dropped declaration hides longest."""
    empty = couple_clv.measure(_run(counted=[], supplied=["C2"]))[0]
    assert empty.gap is None
    assert empty.components["grades_atom_estimator"] is False
    assert empty.components["belief_provenance"]["produced_by"]

    run = _run()
    run.pop("churned_billing_accounts")
    unavailable = couple_clv.measure(run)[0]
    assert unavailable.components["unavailable_reason"]
    assert unavailable.components["grades_atom_estimator"] is False


def test_measure_propagates_an_unresolvable_provenance(monkeypatch):
    """FAIL-SILENT, at the wiring rather than the resolver. `belief_provenance`
    raising is only useful if `measure` lets it through: a caller that swallowed
    it would publish a headline while unable to say whose estimator produced it.
    """
    def _boom(repo_root=None):
        raise FileNotFoundError("producer gone")
    monkeypatch.setattr(couple_clv, "belief_provenance", _boom)
    with pytest.raises(FileNotFoundError):
        couple_clv.measure(_run())
