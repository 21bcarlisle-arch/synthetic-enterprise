"""The defect: a paired floor whose ONE VARIABLE reached no call site reports a spread of zero.

THE DEFECT, NAMED. `tools/size_term_paired_floor` compares the churn belief blind to household size
against the same belief seeing it, by rebinding two module constants. If that rebind reaches no call
site -- the constant renamed, the term moved behind a different guard, the module re-imported under
another name -- then the "blind" and "seeing" legs run the SAME world. Every per-seed difference is
then exactly zero, the spread is zero, and the artefact says the instrument resolves the contrast
perfectly. That is the most flattering possible answer arrived at by measuring nothing, and it is
the failure this file exists to make impossible. It is the same shape `noise_floor`'s own
`calls["n"] == 0` guard serves, one level up: there the patch is a draw, here it is a belief.

AND THE MIRROR, which is the half a single fail-silent guard misses. A blind leg that is not
actually blind -- a rebind that took on one fuel and not the other, say -- produces a NON-zero
spread and looks healthy. It is a third configuration wearing the blind label, and its difference
from the seeing leg is not the contrast anyone asked for. `test_a_blind_leg_that_still_scales_is_
refused` is that leg.

THE PARTITION CONTROL IS THE FIRST TEST AND IT IS DELIBERATELY FIRST. Three of the four legs below
assert a REFUSAL, and a tool that refused everything would pass all three. So the whole partition is
asserted in one place: the same harness must ACCEPT a well-formed run and refuse each malformed one,
and the accepting leg carries the others.

WHY THE RUNNER IS INJECTED AND THE BELIEF IS NOT. The runner is a stub -- three full decade passes
per seed pair is not a test. `company.crm.churn_model.estimate_churn_probability` is the REAL
function, called through the real module attribute, because it is the subject: a control that stubbed
the belief would prove the stub, and the rebind's reach is precisely the thing under test.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from company.crm import churn_model
from tools import size_term_paired_floor as floor

#: A spread of consumptions that straddles the reference. `MAX_SIZE_SCALE` caps the top, so these
#: must differ BELOW the cap or the seeing leg is flat and refuses for the right reason at the wrong
#: time.
CONSUMPTIONS_KWH = (1200.0, 2500.0, 4200.0, 6100.0)


def _believe_across_the_book() -> float:
    """Take the real belief at several household sizes, as a renewal pass would."""
    return sum(
        churn_model.estimate_churn_probability(
            100.0, 130.0, 2.0, annual_consumption_kwh=kwh, segment="resi")
        for kwh in CONSUMPTIONS_KWH)


def _roll_a_few(rolls: int = 3) -> None:
    """Reach the re-rolled draw, so the floor's own `redrawn == 0` guard is satisfied."""
    import simulation.customer_events as customer_events
    for index in range(rolls):
        customer_events.churn_roll_for_renewal("ACCT{}".format(index), "2020-01-01")


def _result(value: float) -> dict:
    return {
        "realised_delta": {row: value for row in floor.DELTA_ROWS},
        "renewal_funnel": {"value_arm": {"accounts_the_arm_priced": ["A", "B"]}},
        "book_identity": {"control_arm": {"billing_accounts_settled_in_window": 154}},
    }


def _well_formed_runner(_report_end):
    """A runner that takes the real belief across a real spread of sizes and reports it.

    The returned figure is a FUNCTION of the belief, which is what makes the blind and seeing legs
    differ at all: a runner returning a constant would make every difference zero and the accepting
    leg below would pass for the same reason the defect does.
    """
    _roll_a_few()
    return _result(_believe_across_the_book() * 1000.0)


def test_a_well_formed_paired_run_is_accepted_and_reports_a_nonzero_contrast(tmp_path: Path):
    """THE PARTITION'S OTHER SIDE. Without this the three refusals below are satisfied by a
    harness that refuses everything, which is the guard-that-refuses-everything trap."""
    report = floor.run([9001, 9002], runner=_well_formed_runner,
                       out=tmp_path / "floor.json")
    assert len(report["seeds"]) == 2
    reconciliation = report["reconciliation_leg"]
    assert reconciliation is not None, "the production-roll leg is the only tie to the published figures"
    # The contrast is REAL: blind and seeing disagree, and the witness saw the term reach the book.
    move = reconciliation["difference_seeing_minus_blind"]["net_margin_gbp"]
    assert move != 0.0, "blind and seeing produced the same number -- the rebind changed nothing"
    assert reconciliation["blind"]["size_term_distinct_scales"] == 0
    assert reconciliation["seeing"]["size_term_distinct_scales"] >= 2
    assert reconciliation["blind"]["size_term_reached_calls"] == len(CONSUMPTIONS_KWH)
    # And the artefact is on disk after every pair, not only at the end.
    written = json.loads((tmp_path / "floor.json").read_text(encoding="utf-8"))
    assert written["the_one_variable"]["names_rebound"] == list(floor.SIZE_REFERENCE_NAMES)


def test_a_variable_that_reaches_no_call_site_is_refused(tmp_path: Path):
    """THE NAMED DEFECT. Nothing asks the belief, so blind and seeing are one world."""
    def runner(_report_end):
        _roll_a_few()
        return _result(1.0)

    with pytest.raises(AssertionError, match="reached NO call site"):
        floor.run([9001, 9002], runner=runner, out=tmp_path / "floor.json")


def test_a_belief_that_is_flat_across_the_book_is_refused(tmp_path: Path):
    """One household size is not a contrast: the term reaches the book and says the same thing."""
    def runner(_report_end):
        _roll_a_few()
        churn_model.estimate_churn_probability(
            100.0, 130.0, 2.0, annual_consumption_kwh=2500.0, segment="resi")
        return _result(1.0)

    with pytest.raises(AssertionError, match="distinct scale"):
        floor.run([9001, 9002], runner=runner, out=tmp_path / "floor.json")


def test_a_blind_leg_that_still_scales_is_refused(monkeypatch, tmp_path: Path):
    """THE MIRROR, and the leg a single zero-reach guard cannot catch.

    Here the rebind takes on electricity and NOT on gas -- the partial-application shape -- so the
    blind leg still scales gas households. It produces a healthy non-zero spread and a plausible
    artefact, and it is not the contrast the artefact claims.
    """
    original = floor._install_references

    def only_electricity(module, blind, originals):
        tally = original(module, blind, originals)
        if blind:  # the gas reference is put back, which is the defect
            setattr(module, "SIZE_REFERENCE_KWH_GAS",
                    floor._WitnessedReference(originals["SIZE_REFERENCE_KWH_GAS"], tally))
        return tally

    monkeypatch.setattr(floor, "_install_references", only_electricity)

    def runner(_report_end):
        _roll_a_few()
        total = _believe_across_the_book()
        total += sum(
            churn_model.estimate_churn_probability(
                100.0, 130.0, 2.0, annual_consumption_kwh=kwh, fuel="gas", segment="resi")
            for kwh in (7000.0, 9500.0, 14000.0))
        return _result(total * 1000.0)

    with pytest.raises(AssertionError, match="not blind"):
        floor.run([9001, 9002], runner=runner, out=tmp_path / "floor.json")


def test_a_single_pair_is_not_reported_as_a_spread(tmp_path: Path):
    """A floor built from one pair would restate the single-seed figure it exists to bound."""
    report = floor.run([9001], runner=_well_formed_runner, out=tmp_path / "floor.json",
                       include_reconciliation=False)
    net = report["paired_difference"]["net_margin_gbp"]
    assert net["n"] == 1
    assert "at least two paired seeds" in net["unavailable_because"]
    assert "paired_mean" not in net, "a one-pair family must publish no centre at all"
