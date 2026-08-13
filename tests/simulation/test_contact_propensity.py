"""The world's contact rate is the WORLD's, and the control proves it can fail.

Guards the cut recorded in `simulation/contact_propensity.py` and in
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3k: until 2026-08-13
`simulation/contact_centre.py` drew the world's ACTUAL contact events off
`saas.contact_model`'s `contact_probability` -- the supplier's own estimate --
so the company's belief about how often it would be contacted CONSTITUTED how
often it was contacted.

WHAT IS ASSERTED, AND WHAT DELIBERATELY IS NOT
----------------------------------------------
NOT asserted: that `WORLD_BASE_CONTACT_PROPENSITY == saas.contact_model.
BASE_CONTACT_PROBABILITY`, nor the same for the confusion/shock terms. The three
pairs are equal today and pinning them equal would restore in the suite exactly
the coupling the cut removes from the code -- the refusal recorded at §3g (the
churn ceiling) and at B7 (the hedge floor), for the same reason each time. They
MAY drift; drift is a finding for the harness to report, never a gate (R12).

Asserted instead -- INDEPENDENCE, by mutation, which is the property the cut
actually bought:

  * mutating the COMPANY's constants does not move the world's contact events,
  * mutating the WORLD's constants DOES move them (the vacuity guard on the
    line above -- without it, "the company's mutation did not reach the log"
    would pass just as happily against a log nothing drives at all), and
  * the same company mutation demonstrably DOES move the COMPANY's own answer
    (the second vacuity guard: prove the mutation bites somewhere before "it did
    not bite here" means anything -- the `donated residual is not a control`
    shape).

And the structural claim that is the actual gain: belief and truth can now
DISAGREE, because the world keys on a dimension the company cannot read.
"""
import pytest

import saas.contact_model
import simulation.contact_propensity as contact_propensity
from simulation.contact_centre import generate_contact_centre_log
from simulation.household_segments import (
    EngagementLevel,
    engagement_level_for_customer,
)


def _customer_of(level: EngagementLevel) -> str:
    """First synthetic id that lands in `level` -- resolved, never hardcoded, so
    a re-draw of the archetype assignment does not silently make these tests
    about a different archetype than they name."""
    for index in range(2000):
        customer_id = f"CP{index:04d}"
        if engagement_level_for_customer(customer_id) == level:
            return customer_id
    raise AssertionError(f"no synthetic customer resolved to {level}")


def _bill(customer_id: str, period_end: str = "2020-01-31", clarity: float = 0.2,
          shock: float | None = 0.6) -> dict:
    return {
        "customer_id": customer_id,
        "period_end": period_end,
        "clarity_score": clarity,
        "bill_shock_pct": shock,
    }


def _bills() -> list[dict]:
    """A book spanning all three archetypes over several periods, sized so the
    log below is comfortably non-empty (see the emptiness guard)."""
    return [
        _bill(_customer_of(level), f"2020-{month:02d}-28")
        for level in EngagementLevel
        for month in range(1, 13)
    ]


def test_the_world_propensity_is_a_probability():
    assert 0.0 <= contact_propensity.contact_propensity("CP0001", 0.2, 0.6) <= 1.0


def test_the_log_is_not_empty():
    """Vacuity guard for every mutation test below.

    A log that is empty whatever anyone does would make "mutating the company's
    constant did not change the log" a statement about nothing.
    """
    assert generate_contact_centre_log(_bills()), (
        "the fixture book produced no contact events at all; the mutation "
        "tests below would prove nothing"
    )


def test_mutating_the_companys_constants_does_not_move_the_worlds_contacts(monkeypatch):
    """THE CUT. Fails if the world draws off the supplier's estimate again."""
    before = generate_contact_centre_log(_bills())

    monkeypatch.setattr(saas.contact_model, "BASE_CONTACT_PROBABILITY", 0.99)
    monkeypatch.setattr(saas.contact_model, "LOW_CLARITY_CONTACT_PENALTY", 0.0)
    monkeypatch.setattr(saas.contact_model, "BILL_SHOCK_CONTACT_PENALTY", 0.0)
    after = generate_contact_centre_log(_bills())

    assert after == before, (
        "the world's contact events moved when the COMPANY's contact constants "
        "were mutated -- the company's belief is constituting the world's "
        "outcome again (register §3k, the B2/B3 inversion)"
    )


def test_the_same_mutation_does_move_the_companys_own_answer(monkeypatch):
    """VACUITY GUARD for the test above: prove the mutation bites somewhere."""
    before = saas.contact_model.contact_probability(0.2, 0.6)

    monkeypatch.setattr(saas.contact_model, "BASE_CONTACT_PROBABILITY", 0.99)
    monkeypatch.setattr(saas.contact_model, "LOW_CLARITY_CONTACT_PENALTY", 0.0)
    monkeypatch.setattr(saas.contact_model, "BILL_SHOCK_CONTACT_PENALTY", 0.0)
    after = saas.contact_model.contact_probability(0.2, 0.6)

    assert after != pytest.approx(before), (
        "mutating the company's contact constants did not move the company's "
        "own estimate -- this control is measuring nothing"
    )


def test_mutating_the_worlds_constants_does_move_the_worlds_contacts(monkeypatch):
    """VACUITY GUARD: the log really is driven by the constants under test.

    Without this, a `generate_contact_centre_log` that had been accidentally
    reduced to a constant would satisfy the independence test above perfectly.
    """
    before = generate_contact_centre_log(_bills())

    monkeypatch.setattr(contact_propensity, "WORLD_BASE_CONTACT_PROPENSITY", 0.0)
    monkeypatch.setattr(contact_propensity, "WORLD_CONFUSION_SENSITIVITY", 0.0)
    monkeypatch.setattr(contact_propensity, "WORLD_SHOCK_SENSITIVITY", 0.0)
    after = generate_contact_centre_log(_bills())

    assert after != before, (
        "zeroing the WORLD's own contact constants left its contact events "
        "unchanged -- the log is not being driven by the physics it claims"
    )
    assert after == [], "a zero propensity should produce no contacts at all"


def test_belief_and_truth_can_disagree_on_an_identical_bill():
    """THE GAIN, and the reason the gap is no longer zero by construction.

    The world keys on the household's engagement archetype; the company has no
    such field to estimate with. So two customers can receive the SAME bill,
    draw the SAME belief out of the supplier's model, and carry DIFFERENT
    truths. That difference is what `tools/couple_contact.py` scores.
    """
    active = _customer_of(EngagementLevel.ACTIVE)
    disengaged = _customer_of(EngagementLevel.DISENGAGED)

    belief_active = saas.contact_model.contact_probability(0.2, 0.6)
    belief_disengaged = saas.contact_model.contact_probability(0.2, 0.6)
    assert belief_active == pytest.approx(belief_disengaged), (
        "the company's estimate should depend only on the bill -- if it has "
        "grown a per-customer term, this test is no longer about the gap"
    )

    truth_active = contact_propensity.contact_propensity(active, 0.2, 0.6)
    truth_disengaged = contact_propensity.contact_propensity(disengaged, 0.2, 0.6)

    assert truth_active != pytest.approx(truth_disengaged)
    assert truth_disengaged != pytest.approx(belief_disengaged), (
        "belief and truth are identical for a disengaged household -- the gap "
        "this cut exists to open is closed again"
    )


def test_generate_contact_centre_log_no_longer_accepts_the_companys_model():
    """The signature IS the control here.

    `contact_centre.py` never imported `saas.contact_model` -- the estimate was
    PASSED in, so no import-level wall check could ever have seen this crossing.
    Removing the parameter is what makes the old call unrepresentable, and this
    is what fails if someone restores it for compatibility.
    """
    with pytest.raises(TypeError):
        generate_contact_centre_log([], {"by_customer": {}})


def test_a_corrupt_clarity_reading_is_refused_not_defaulted():
    """R15 fail-open: the failure direction that hides itself.

    A missing or NaN clarity score clamped to "perfectly clear" would SUPPRESS
    contacts and read as a quiet, healthy book.
    """
    with pytest.raises(TypeError):
        contact_propensity.contact_propensity("CP0001", None)
    with pytest.raises(ValueError):
        contact_propensity.contact_propensity("CP0001", float("nan"))
    with pytest.raises(ValueError):
        contact_propensity.contact_propensity("CP0001", 1.5)


def test_the_gap_runner_scores_both_directions():
    """`tools/couple_contact.py` reports per-archetype, not just an aggregate.

    An aggregate alone averages the over- and under-estimated archetypes against
    each other and reports a smaller gap than the supplier is actually running.
    """
    from tools.couple_contact import measure

    result = measure(_bills())
    assert result["aggregate"]["n"] == len(_bills())
    assert set(result["by_engagement_archetype"]) == {
        level.value for level in EngagementLevel
    }
    signs = {
        row["mean_signed_error"] > 0
        for row in result["by_engagement_archetype"].values()
    }
    assert len(signs) > 1, (
        "every archetype's belief errs in the same direction -- the aggregate "
        "would then be a fair summary and this runner's split buys nothing; "
        "check the multipliers still straddle 1.0"
    )


def test_the_runner_can_write_the_gap_ledger_and_the_row_names_the_pair(tmp_path):
    """The family-membership control's other half.

    `background.gap_ledger_reconciler` takes its producer population from the
    `tools/couple_*.py` GLOB, so a family member that cannot write is one the
    reconciler can never attribute a stale row to. The commit that added this
    runner deferred the write and left that control RED at HEAD; this asserts the
    capability exists rather than that a marker string is present, which is what
    the reconciler's regex alone would have accepted.
    """
    import json

    from background.gap_metric import write_gap_entry
    from tools.couple_contact import TWIN_ATOM_ID, WORLD_ATOM_ID, gap_result

    ledger_path = tmp_path / "coupled_gap_ledger.json"
    ledger = write_gap_entry(
        WORLD_ATOM_ID, TWIN_ATOM_ID, gap_result(_bills()),
        measured_at="2026-08-13T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=ledger_path,
    )
    row = ledger[WORLD_ATOM_ID]
    assert row["twin_atom_id"] == TWIN_ATOM_ID
    assert 0.0 <= row["gap"]
    assert json.loads(ledger_path.read_text())[WORLD_ATOM_ID]["gap"] == row["gap"]


def test_the_headline_is_normalised_to_a_no_skill_baseline_and_can_say_worthless():
    """The gap has to be able to report BOTH outcomes, or it reports neither.

    A raw mean-absolute-error would be a number nobody can read: 0.15 is neither
    good nor bad without knowing what guessing would have scored. Normalising to
    the no-skill baseline is what makes gap==1 mean "worth nothing over predicting
    the average". Both directions are driven here -- a belief that IS the truth
    must score 0, and a belief that is the blind mean must score ~1 -- so a
    formula swapped for an unnormalised one fails this test rather than silently
    changing what every published gap means.
    """
    from background.gap_metric import prediction_gap
    from tools.couple_contact import _pairs

    rows = _pairs(_bills())
    truth = [t for _, _, t in rows]

    perfect = prediction_gap(truth, truth)
    assert perfect.gap == pytest.approx(0.0), "belief == truth must score a leak"

    blind = [sum(truth) / len(truth)] * len(truth)
    assert prediction_gap(truth, blind).gap == pytest.approx(1.0), (
        "predicting the climatological mean must score exactly the no-skill "
        "baseline -- if it does not, the normalisation is not the one claimed"
    )
