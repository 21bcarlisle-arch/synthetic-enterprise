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

**CLAIM 1 IS SUPERSEDED AS OF 2026-09-23, corrected here beside it rather than over it.** The
saturation was REAL when it was measured and it is now GONE, and neither the routing repair nor
this file caused that: `bill_stress` was unbounded in consumption, so a 3.9 GWh account carried a
£236,166 previous-year bill and the term alone asserted 19.5 of churn uplift. That is what pinned
the SME path at 1.0000 at every candidate margin. `BILL_STRESS_MAX_RATIO` now bounds the term to
the only published measurement of distress-driven switching (Ofgem CIM w6 Table 56, arrears
1.28x), and at that bound the SME path at C_IC3's volume spreads 0.063 -> 0.968 across the same
margins. **Three tests in section 1 were keyed to the literal 1.0 and went red when the model
became more honest, which is exactly backwards; they are re-keyed to the property below.**

AND THE CORRECTION GOES FURTHER THAN THE NUMBER: claim 1 said the saturation was *a property of
volume, not of the account being industrial*. Measured under the bound, that is no longer true.
The SME/I&C gap at C_IC3's volume (-0.085 at a £8/MWh margin) is essentially the same as the gap
at a household's volume (-0.101), so what now separates the two branches is the SEGMENT LABEL --
the I&C arm's higher rate sensitivity -- and not the volume at all. **The routing repair is still
correct and its mechanism has changed**: an industrial account on the SME branch is no longer
given an uninformative curve, it is given one that materially UNDERSTATES its price response, and
an arm that underestimates churn overprices. What has NOT been re-measured is whether the
£94,314 realised loss is still attributable to the routing rather than to the runaway; that is an
A/B, it is not this file, and it is filed with the ceiling's own record.
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
def test_the_sme_path_no_longer_saturates_at_industrial_volume(margin):
    """The measured defect, and the bound that retired it (2026-09-23).

    This assertion read `== pytest.approx(1.0)` from 2026-08-26 until the `bill_stress` term was
    bounded. It was pinned to the answer of the day, so it went RED when the model stopped
    claiming that a large bill alone makes an industrial account certain to leave.

    MUTATION (must fire): delete the `min(..., bill_stress_uplift_ceiling(base_rate))` in
    `estimate_churn_probability` and every margin here returns 1.0000 again. The certainty was
    the unbounded knee, not the segment.
    """
    p = _p_leave(SME_SEGMENT, margin, INDUSTRIAL_KWH)
    assert p < 1.0, (
        f"the SME path returned certainty of leaving at a £{margin}/MWh margin on a "
        f"{INDUSTRIAL_KWH:,.0f} kWh account — the unbounded bill-size knee is back"
    )


def test_the_industrial_curve_carries_information_for_the_optimiser():
    """What the defect actually cost, re-keyed to the property rather than to 1.0000.

    The arm fell to the FLOOR because `p_retain` was flat at zero across every candidate margin:
    with nothing to maximise, the optimiser has no reason to prefer one price to another. That is
    a statement about the SPREAD of the curve, and it stays true however the calibration moves.

    MUTATION (must fire): remove the ceiling and the spread collapses to 0.0 — flat at certainty,
    including at a margin BELOW what the company already charges, which is the sharpest form of
    the original finding (the model said a discount does not help either).
    """
    floor_margin, control_margin, high_margin = 0.5, 2.0, 80.0
    at_floor = _p_leave(SME_SEGMENT, floor_margin, INDUSTRIAL_KWH)
    at_control = _p_leave(SME_SEGMENT, control_margin, INDUSTRIAL_KWH)
    at_high = _p_leave(SME_SEGMENT, high_margin, INDUSTRIAL_KWH)
    assert at_high - at_floor > 0.5, (
        f"the SME curve spans only {at_high - at_floor:.4f} across the candidate margins on an "
        "industrial account; a curve this flat is what sent the arm to the floor"
    )
    assert at_control < at_high, "raising the margin must not reduce the modelled churn"


def test_the_ic_path_is_not_saturated_and_responds_to_price():
    """The branch that was unreachable. It must both start low AND move, or routing to it
    would just be swapping one uninformative curve for another."""
    at_floor = _p_leave(IC_SEGMENT, 0.5, INDUSTRIAL_KWH)
    at_high = _p_leave(IC_SEGMENT, 46.0, INDUSTRIAL_KWH)
    assert at_floor < 0.1
    assert at_high > 0.5
    assert at_high > at_floor


def test_the_wrong_branch_now_UNDERSTATES_an_industrial_accounts_price_response():
    """WHY THE ROUTING IS STILL A CORRECTION, AND MY OWN PREDICTION HERE WAS WRONG (2026-09-23).

    This test used to assert the opposite of its own name: that the saturation was caused by
    VOLUME and not by the segment label, evidenced by the resi path at industrial volume reading
    1.0000. Under the bound that reading is 0.0630, and the measurement says the old claim was an
    artefact of the runaway. The SME/I&C gap at C_IC3's volume is -0.085 at a £8/MWh margin; at a
    household's volume it is -0.101. **Nearly the same gap. It is the label, not the volume.**

    So the correction is now a different one, and it is the one that survives: an industrial
    account scored on the SME branch is not handed an uninformative curve, it is handed one that
    materially understates how much price moves it — and an arm that underestimates churn
    overprices. The load-bearing claim is the SIGN and the MATERIALITY of that gap, across the
    margins where the curve is live.

    MUTATION, RUN RATHER THAN ASSERTED, AND THE FIRST TWO I NAMED WERE BOTH WRONG.
    `IC_BASE_CHURN_RATE = BASE_CHURN_RATE` fires here; so does `IC_TENURE_DISCOUNT_PER_YEAR =
    TENURE_DISCOUNT_PER_YEAR`. Those two constants, not the rate sensitivity, are what hold the
    branches apart at a renewal. Collapsing `segments_for` does NOT fire here -- this test calls
    the two branches directly, so it is about the branches DISAGREEING and not about the routing
    reaching them, and section 2 is what covers the routing. Setting `IC_RATE_SENSITIVITY` to the
    SME value does not fire here either, and that one is a MISSING TEST rather than an
    equivalence: the gap merely stops widening with the margin instead of closing.
    `test_the_ic_branch_is_the_STEEPER_curve_and_not_merely_the_higher_one` is that missing test.
    """
    live_margins = [8.0, 20.0, 46.0]
    for margin in live_margins:
        on_sme = _p_leave(SME_SEGMENT, margin, INDUSTRIAL_KWH)
        on_own_branch = _p_leave(IC_SEGMENT, margin, INDUSTRIAL_KWH)
        assert on_sme < on_own_branch - 0.05, (
            f"at a £{margin}/MWh margin the SME branch scores C_IC3 at {on_sme:.4f} against "
            f"{on_own_branch:.4f} on its own branch — the branches have stopped disagreeing, so "
            "routing by segment has become a preference rather than a correction"
        )

    # And the gap is the LABEL: the same two branches disagree by a comparable amount at a
    # household's volume, which is what refutes the volume explanation this test used to carry.
    gap_industrial = (_p_leave(IC_SEGMENT, 8.0, INDUSTRIAL_KWH)
                      - _p_leave(SME_SEGMENT, 8.0, INDUSTRIAL_KWH))
    gap_domestic = (_p_leave(IC_SEGMENT, 8.0, DOMESTIC_KWH)
                    - _p_leave(SME_SEGMENT, 8.0, DOMESTIC_KWH))
    assert gap_domestic > 0.0 and gap_industrial > 0.0
    assert abs(gap_industrial - gap_domestic) < 0.5 * max(gap_industrial, gap_domestic), (
        f"the branch gap is {gap_industrial:.4f} at industrial volume and {gap_domestic:.4f} at "
        "domestic volume; if these have diverged, volume is doing the work again and the "
        "paragraph above this test is the thing that is now wrong"
    )


def test_the_ic_branch_is_the_STEEPER_curve_and_not_merely_the_higher_one():
    """The leg the mutation sweep said was missing (2026-09-23).

    `IC_RATE_SENSITIVITY = 1.5` is the constant that says an industrial account punishes a rise
    HARDER, not just that it shops more often — and halving it to the SME value reddened nothing
    in this file. Every other leg here compares LEVELS, and the I&C branch keeps a higher level
    from `IC_BASE_CHURN_RATE` alone, so the sensitivity could be quietly retuned to the household
    value while the file stayed green and the arm's whole reason for routing rotted underneath it.

    So this asks about the SLOPE: across the live margins the I&C curve must RISE FASTER than the
    SME curve, which is what a higher rate sensitivity means and what a higher base rate cannot
    fake.

    MUTATION (run, fires): `IC_RATE_SENSITIVITY = RATE_SENSITIVITY` — the I&C rise falls to
    0.5550 against SME's 0.5779, so the branch stops being the steeper one at all.
    """
    low, high = 8.0, 46.0
    ic_rise = _p_leave(IC_SEGMENT, high, INDUSTRIAL_KWH) - _p_leave(IC_SEGMENT, low, INDUSTRIAL_KWH)
    sme_rise = _p_leave(SME_SEGMENT, high, INDUSTRIAL_KWH) - _p_leave(SME_SEGMENT, low, INDUSTRIAL_KWH)
    assert ic_rise > sme_rise, (
        f"over £{low}–£{high}/MWh the I&C curve rises {ic_rise:.4f} against the SME curve's "
        f"{sme_rise:.4f}; the branch is no longer the more price-sensitive one, so "
        "IC_RATE_SENSITIVITY has stopped doing the job it is named for"
    )


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
