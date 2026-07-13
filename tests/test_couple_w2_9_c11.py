"""Tests for the W2_9 <-> C11 coupled-triad runner (tools/couple_w2_9_c11.py).

Closes the coupled pair: the WORLD answer key (segment_debt_obligation) vs the
COMPANY's applied T&C (C11 select_debt_terms) over a population, scored by the
belief-vs-truth misapplication gap.

The load-bearing properties:
  * DETERMINISM (C-S2): same population -> identical gap on replay.
  * NON-DEGENERATE gap: with real segment misclassification the gap is
    strictly between 0 and 1 (the company copes but is not perfect).
  * R15 INDEPENDENCE / not a tautology: if the observation channel were
    PERFECT (company always sees the true segment), the gap collapses to 0 --
    proving the measured gap is caused by the mislabel, not by the two sides
    trivially agreeing. A MUTATION that flips the company's applied class makes
    the gap fire large. Both directions confirm the control can move.
  * The ledger write matches the reader contract coupled_triad.gap_measured.
"""
from datetime import date

import pytest

from tools import couple_w2_9_c11 as run
from background import coupled_triad as ct
from background import gap_metric as gm
from simulation import segment_debt_obligation as w29
from company.compliance.segment_debt_policy import select_debt_terms


def test_scenario_gap_is_deterministic():
    r1, s1 = run.measure(n_customers=1500)
    r2, s2 = run.measure(n_customers=1500)
    assert r1.gap == r2.gap
    assert s1 == s2


def test_scenario_gap_is_non_degenerate():
    r, stats = run.measure(n_customers=4000)
    assert r.gap is not None
    assert 0.0 < r.gap < 1.0
    # Some customers are genuinely misrecorded -> the gap has real cause.
    assert stats["n_misrecorded_customers"] > 0
    assert 0.0 < stats["misrecord_rate"] < 0.15


def test_perfect_observation_collapses_gap_to_zero():
    # Independence proof: if the company always saw the TRUE segment, both sides
    # apply the same correct class -> gap 0. So the real gap is caused by the
    # misclassification channel, not by a tautological agreement.
    dates = [date(2020, 3, 15), date(2023, 9, 15)]
    truth, applied = [], []
    for i in range(500):
        cid = f"P{i:05d}"
        true_seg = run._pick_true_segment(cid)
        for as_of in dates:
            correct = w29.correct_obligation(true_seg, as_of)
            # Company sees the TRUE segment (perfect observation).
            terms = select_debt_terms(true_seg, as_of)
            truth.append(correct.terms_class)
            applied.append(run._terms_class_of(terms))
    r = gm.misapplication_gap(truth, applied, positive_class=w29.BUSINESS_TERMS)
    assert r.raw_gap == 0.0
    assert r.gap == 0.0


def test_mutation_wrong_class_makes_gap_fire_large():
    # If the company applied the OPPOSITE class everywhere, the gap must be
    # large (control can fail). This is the R15 mutation: a broken applier is
    # caught, not silently passed.
    dates = [date(2021, 3, 15)]
    truth, applied = [], []
    flip = {w29.BUSINESS_TERMS: w29.DOMESTIC_TERMS,
            w29.DOMESTIC_TERMS: w29.BUSINESS_TERMS}
    for i in range(500):
        cid = f"M{i:05d}"
        true_seg = run._pick_true_segment(cid)
        for as_of in dates:
            correct = w29.correct_obligation(true_seg, as_of)
            truth.append(correct.terms_class)
            applied.append(flip[correct.terms_class])   # deliberately wrong
    r = gm.misapplication_gap(truth, applied, positive_class=w29.BUSINESS_TERMS)
    assert r.raw_gap == pytest.approx(1.0)   # every case wrong
    assert r.gap is not None and r.gap > 1.0  # worse than blind majority


def test_wrong_direction_is_reported():
    # The dominant unlawful direction (a domestic account wrongly given business
    # terms) is counted separately from the withheld direction.
    r, _ = run.measure(n_customers=4000)
    assert r.components["wrongly_applied"] >= 0
    assert r.components["wrongly_withheld"] >= 0
    assert r.components["n_wrong"] == (
        r.components["wrongly_applied"] + r.components["wrongly_withheld"]
    )


def test_ledger_write_matches_reader_contract(tmp_path):
    r, _ = run.measure(n_customers=1000)
    path = tmp_path / "coupled_gap_ledger.json"
    ledger = gm.write_gap_entry(
        run.WORLD_ATOM_ID, run.TWIN_ATOM_ID, r,
        measured_at="2026-07-13T00:00:00Z", run_git_commit="cafe",
        ledger_path=path,
    )
    entry = ledger[run.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == run.TWIN_ATOM_ID
    assert isinstance(entry["gap"], float)
    reloaded = ct.load_gap_ledger(path)
    assert ct.gap_measured(run.WORLD_ATOM_ID, reloaded) is True
