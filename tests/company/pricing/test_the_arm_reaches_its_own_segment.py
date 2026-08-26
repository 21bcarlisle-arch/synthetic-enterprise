"""R15 proofs that the renewal arm can reach every segment its own churn model branches on.

THE DEFECT (2026-08-26,
`docs/staging/done/WORKER_FINDING_THE_VALUE_ARMS_WHOLE_LOSS_IS_ONE_INDUSTRIAL_ACCOUNT_PRICED_AS_A_HOUSEHOLD_2026-08-26.md`).
`renewal_margin_uplift` computed `segment = "resi" if is_domestic else "SME"` and handed the
result to BOTH the cost tables and the churn model. The stated reason was sound about costs --
`cost_to_serve_for_period` accepts exactly two segments, so one vocabulary beats two that can
disagree -- and wrong about churn: `estimate_churn_probability` branches THREE ways, and its I&C
arm exists precisely to switch bill-size-driven churn OFF for industrial customers.

So the branch was unreachable from the only production caller, and on a 3.9 GWh account the SME
path returns P(leave) = 1.0000 at EVERY candidate margin -- including margins below what the
company already charges. With `p_retain` flat at zero the optimiser has nothing to maximise and
falls to the floor, £0.50/MWh under the control's £2.00. Realised cost: -£94,314 on C_IC3, which
was 99.5% of the value arm's entire measured loss.

WHAT THESE TESTS PIN, and the order matters:

  1. the SATURATION is real and is a property of volume, not of the account being industrial --
     otherwise "use the I&C branch" is a preference rather than a correction;
  2. the segment REACHES the model through every link (run -> chain -> arm -> estimator);
  3. the fallback still works, so a caller that does not know a segment is unchanged;
  4. and a vocabulary MISMATCH cannot be silent, which is how this happened -- there are THREE
     segment vocabularies in this company and nothing checked that a caller's matched a callee's.

These are not tests that the arm earns more. Whether the repair moves the A/B is a measurement,
taken separately, with the expected direction recorded before the run (R12).
"""

import inspect

import pytest

from company.crm.churn_model import (
    CHURN_SEGMENTS,
    IC_BILL_STRESS_SENSITIVITY,
    IC_SEGMENT,
    RESI_SEGMENT,
    SME_SEGMENT,
)
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.pricing.renewal_rate_chain import decide_renewal_rate
from company.pricing.value_based_renewal import renewal_margin_uplift, segments_for

#: C_IC3's actual consumption, the account that carried the loss.
INDUSTRIAL_KWH = 3_936_105.0
DOMESTIC_KWH = 4_004.0
BASE_RATE = 60.0


def _p_leave(segment, margin, kwh):
    return enriched_churn_estimate(
        BASE_RATE, BASE_RATE + margin,
        tenure_years=4.0, annual_consumption_kwh=kwh,
        bill_shock_count=0, renewal_year=2021, segment=segment,
    )


# ---------------------------------------------------------------------------
# 1. the defect itself, characterised
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("margin", [0.5, 2.0, 8.0, 20.0, 46.0, 80.0])
def test_the_sme_path_saturates_at_industrial_volume(margin):
    """The measured defect. Every candidate margin returns certainty of leaving, so the
    curve carries no information for the optimiser to use."""
    assert _p_leave(SME_SEGMENT, margin, INDUSTRIAL_KWH) == pytest.approx(1.0)


def test_the_saturation_covers_a_margin_BELOW_what_the_company_already_charges():
    """The sharpest form of it, and the reason the arm went to the FLOOR rather than
    merely mispricing: the model says a discount does not help either, so there is no
    margin at which the customer is worth keeping."""
    control_margin, floor_margin = 2.0, 0.5
    assert _p_leave(SME_SEGMENT, control_margin, INDUSTRIAL_KWH) == pytest.approx(1.0)
    assert _p_leave(SME_SEGMENT, floor_margin, INDUSTRIAL_KWH) == pytest.approx(1.0)


def test_the_ic_path_is_not_saturated_and_responds_to_price():
    """The branch that was unreachable. It must both start low AND move, or routing to it
    would just be swapping one uninformative curve for another."""
    at_floor = _p_leave(IC_SEGMENT, 0.5, INDUSTRIAL_KWH)
    at_high = _p_leave(IC_SEGMENT, 46.0, INDUSTRIAL_KWH)
    assert at_floor < 0.1
    assert at_high > 0.5
    assert at_high > at_floor


def test_the_saturation_is_caused_by_VOLUME_not_by_the_segment_label():
    """R4 -- the nearest working analogue, stated as a test. The resi path at DOMESTIC
    volume gives the same answer as the I&C path at industrial volume, so the curve is
    correct for households and is being applied outside its calibrated domain. Without
    this, "use the I&C branch" would be a preference rather than a correction."""
    domestic = _p_leave(RESI_SEGMENT, 0.5, DOMESTIC_KWH)
    industrial_on_its_own_branch = _p_leave(IC_SEGMENT, 0.5, INDUSTRIAL_KWH)
    assert domestic == pytest.approx(industrial_on_its_own_branch, rel=1e-6)
    assert _p_leave(RESI_SEGMENT, 0.5, INDUSTRIAL_KWH) == pytest.approx(1.0)


def test_the_ic_branch_exists_precisely_to_switch_bill_stress_off():
    """The constant that makes the fix correct rather than convenient, asserted so that
    turning it back on reds this file instead of silently restoring the defect."""
    assert IC_BILL_STRESS_SENSITIVITY == 0.0


# ---------------------------------------------------------------------------
# 2. the segment reaches the model through every link
# ---------------------------------------------------------------------------

def test_the_arm_accepts_a_segment():
    assert "segment" in inspect.signature(renewal_margin_uplift).parameters


def test_the_chain_carries_a_segment_through_to_the_arm():
    """The link that did not exist: the chain only ever had `is_domestic`, so no caller
    COULD have supplied a segment however much it knew."""
    assert "segment" in inspect.signature(decide_renewal_rate).parameters


def test_the_DOOR_carries_the_segment_too_and_not_only_the_desk_behind_it():
    """R11 — NO ORPHAN TRANSITIONS, and this one nearly shipped.

    `simulation/run_phase2b.py` imports `decide_renewal_rate` from
    `company/interfaces/renewal_rate_chain.py` — the DOOR — not from the desk. The first
    draft of this repair added `segment` to the desk and to the world's call site and
    stopped there. The parameter would have reached nothing, and the world passing it
    would have raised TypeError on the first renewal of a ten-year run.

    So the two signatures are compared as SETS rather than the door being spot-checked for
    one name: any future desk parameter that does not cross the door fails here, which is
    the class rather than this instance.
    """
    from company.interfaces.renewal_rate_chain import decide_renewal_rate as door
    from company.pricing.renewal_rate_chain import decide_renewal_rate as desk

    door_params = set(inspect.signature(door).parameters)
    desk_params = set(inspect.signature(desk).parameters)
    assert "segment" in door_params
    assert desk_params - door_params == set(), (
        f"the desk takes {sorted(desk_params - door_params)} that the door cannot pass; "
        "a parameter the door does not carry is a release whose effect is nothing"
    )
    assert door_params - desk_params == set(), (
        f"the door takes {sorted(door_params - desk_params)} that the desk does not "
        "accept; the world calling it would raise TypeError"
    )


def test_the_world_supplies_the_segment_it_already_had():
    """`_SEGMENT_OF` existed in `run_phase2b` for the Triad carve-out the whole time, so
    the fact the renewal desk was missing was three lines away. This asserts the wiring
    rather than the intent -- a comment saying it is passed is not a test that it is."""
    source = inspect.getsource(
        __import__("simulation.run_phase2b", fromlist=["run_phase2b"]))
    assert "segment=_SEGMENT_OF.get(cid" in source


# ---------------------------------------------------------------------------
# 3. the fallback, so an uninformed caller is unchanged
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("is_domestic, expected", [(True, RESI_SEGMENT), (False, SME_SEGMENT)])
def test_a_caller_that_supplies_no_segment_keeps_the_old_two_valued_mapping(
        is_domestic, expected):
    """Backward compatibility is the reason `segment` is optional, and it is EXERCISED
    rather than restated: a fix that silently changed every existing caller's behaviour
    would be a second defect shipped to repair the first.

    (The first draft of this test asserted `expected == expected` — a tautology, in a file
    about R15. `segments_for` exists as a named function so the mapping can be called.)
    """
    assert segments_for(None, is_domestic) == (expected, expected)


def test_the_industrial_segment_reaches_churn_while_costs_still_see_two_categories():
    """The whole repair in one assertion: the churn model gets the account's real segment,
    the cost tables keep the two-valued vocabulary they were built for, and neither is
    made to use the other's."""
    assert segments_for(IC_SEGMENT, False) == (IC_SEGMENT, SME_SEGMENT)


def test_the_mapping_never_hands_the_cost_tables_a_segment_they_do_not_know():
    """`cost_to_serve_for_period` and `standing_charge_rate` accept exactly two. Mapping
    DOWN is lossless; mapping up would have to invent an industrial cost curve nobody
    calibrated."""
    for segment in list(CHURN_SEGMENTS) + [None, "i_and_c", ""]:
        for is_domestic in (True, False):
            _, cost_segment = segments_for(segment, is_domestic)
            assert cost_segment in (RESI_SEGMENT, SME_SEGMENT)


def test_the_vocabulary_the_arm_checks_against_is_the_one_the_model_branches_on():
    """THE FAILURE MODE THAT MADE THIS SUBTLE. There are THREE segment vocabularies in
    this company: the churn model's (`resi`/`SME`/`I&C`), `segment_profitability`'s
    (`residential_credit`/`residential_ppm`/`sme`/`i_and_c`), and the cost tables' two.
    An arm that validated against the wrong one would match NOTHING and fall back for
    every account -- indistinguishable from the original defect, and silent.

    So the arm imports its vocabulary from the module that BRANCHES on it, and this test
    holds those two together.
    """
    from company.pricing import segment_profitability

    assert IC_SEGMENT in CHURN_SEGMENTS
    assert set(CHURN_SEGMENTS).isdisjoint(segment_profitability.KNOWN_SEGMENTS), (
        "the churn vocabulary and the profitability vocabulary now overlap; if they are "
        "being unified that is fine, but this test is the place that has to say so"
    )
    source = inspect.getsource(segments_for)
    assert "CHURN_SEGMENTS" in source, (
        "the mapping must validate against the churn model's own vocabulary; validating "
        "against any other set matches nothing and falls back silently"
    )
    # And the behavioural half, so this does not rest on reading source text: every value
    # the churn model branches on must survive the mapping unchanged.
    for known in CHURN_SEGMENTS:
        churn_segment, _ = segments_for(known, is_domestic=(known == RESI_SEGMENT))
        assert churn_segment == known


@pytest.mark.parametrize("bogus", ["i_and_c", "sme", "residential_credit", "", "IC", None])
def test_an_unrecognised_segment_falls_back_rather_than_reaching_the_wrong_branch(bogus):
    """A value from ANOTHER of this company's three vocabularies must not be passed
    through to the churn model, where it would take the `else` branch and reintroduce the
    defect for industrial accounts while LOOKING like it had been fixed.

    Note what this test does NOT assert: that `i_and_c` is mapped to `I&C`. Guessing
    across vocabularies is how a silent mismatch becomes a silent mistranslation. The safe
    answer is the documented fallback, and a caller that means I&C must say `I&C`.
    """
    churn_segment, _ = segments_for(bogus, is_domestic=False)
    assert churn_segment == SME_SEGMENT
    assert churn_segment in CHURN_SEGMENTS


def test_the_fallback_is_distinguishable_from_a_real_industrial_answer():
    """R15. If the fallback and the fixed path produced the same segment for a
    non-domestic account, this whole file would pass on the unrepaired code."""
    fallback, _ = segments_for(None, is_domestic=False)
    repaired, _ = segments_for(IC_SEGMENT, is_domestic=False)
    assert fallback != repaired, (
        "the repair is indistinguishable from the defect it fixes; these tests would "
        "pass against the collapsed mapping"
    )
