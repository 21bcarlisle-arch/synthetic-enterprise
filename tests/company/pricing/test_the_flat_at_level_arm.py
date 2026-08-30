"""R15 proofs for the level-without-selection arm.

WHY IT EXISTS. The value arm beat flat rules by £7,066 with `belief_vs_outcome.discrimination_auc`
at **0.4653**. The advantage cannot be attributed to inference. What the arm demonstrably did was
price HIGH: a median £44.50/MWh against the flat rule's £2.00.

RESTATED 2026-08-30, CONCLUSION UNCHANGED. This said 0.4653 was "below a coin flip". It is not: on
that run's 16 retentions and 9 departures the exact Mann-Whitney null runs 0.264..0.736, so 0.4653
is two-sided p 0.80 — indistinguishable from a coin flip rather than worse than one. The reason
this arm exists is stronger for it, not weaker: an advantage cannot be attributed to a ranking the
run could not show exists. The bound now ships beside the figure
(`tools/generate_value_arms_data._auc_null`).

`flat_at_level` applies ONE uplift to every renewal it prices — the SAME renewals `value_based`
prices, through the same guards, under the same lawful ceiling. So the two arms differ by the
CHOOSING and by nothing else, and the £7,066 can be split into level and selection.

WHAT IT IS NOT, and both were tried first:

  * NOT `flat_rules` at a bigger constant. `flat_rules` applies no uplift at all; its £2.00 lives
    in the base rate of every contract. Raising that constant raises the price for every customer
    on every contract, not for the 25 renewals the arm priced — a whole-book price rise, which on
    2026-08-27 returned a 9.4× artefact and was withdrawn.
  * NOT the ladder. `renewal_margin_ladder_multiplier` delivers `flat + k × (chosen − flat)`, a
    fraction of the arm's OWN per-customer answer, so it varies the SLOPE and never removes the
    choosing. At k=0 it is the flat rule at £2.00, not at the arm's level.

THE THREE PROPERTIES THAT MAKE IT A CONTROL, and each has a test below:
  1. it prices the SAME POPULATION as the value arm (same guards, no early return);
  2. it is CLAMPED to the lawful ceiling, exactly as the value arm's search is;
  3. it applies ONE level, so nothing about the customer reaches the price.
"""
from __future__ import annotations

import pytest

from company.pricing.value_based_renewal import (
    ARMS,
    FLAT_AT_LEVEL,
    FLAT_RULES,
    VALUE_BASED,
    MarginDecisionUnavailable,
    decide_margin,
)

BASE = dict(current_rate_gbp_per_mwh=100.0, base_rate_gbp_per_mwh=100.0, eac_kwh=3000.0,
            tenure_years=3.0, cost_to_serve_gbp_per_year=60.0, expected_periods=3.0,
            segment="resi")


# ---------------------------------------------------------------------------
# 1. one level, and nothing about the customer reaches the price
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("eac,tenure,shocks", [
    (1_000.0, 1.0, 0), (3_000.0, 3.0, 2), (25_000.0, 9.0, 5),
])
def test_the_same_level_is_charged_whatever_the_customer_looks_like(eac, tenure, shocks):
    """THE DEFINING PROPERTY. If any customer attribute moved the price this would not be a
    control for selection — it would be a second, quieter value arm."""
    kw = {**BASE, "eac_kwh": eac, "tenure_years": tenure, "bill_shock_count": shocks}
    d = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5, **kw)
    assert d.margin_gbp_per_mwh == pytest.approx(44.5)


def test_the_value_arm_on_the_SAME_inputs_does_vary():
    """THE PARTNER. Without it, "the level does not vary" could be true because nothing varies
    on this fixture — which would make every test above vacuous."""
    chosen = {
        decide_margin(customer_id="C1", arm=VALUE_BASED,
                      **{**BASE, "eac_kwh": eac, "tenure_years": ten}).margin_gbp_per_mwh
        for eac, ten in ((1_000.0, 1.0), (25_000.0, 9.0))
    }
    assert len(chosen) > 1, "the value arm priced two very different customers identically"


# ---------------------------------------------------------------------------
# 2. clamped to the lawful ceiling, exactly as the value arm is
# ---------------------------------------------------------------------------

def test_it_is_clamped_to_the_lawful_ceiling():
    d = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                      max_offered_rate_gbp_per_mwh=105.0, **BASE)
    assert d.offered_rate_gbp_per_mwh == pytest.approx(105.0)
    assert d.margin_gbp_per_mwh == pytest.approx(5.0)


def test_it_clamps_to_the_SAME_rate_the_value_arm_is_held_to():
    """The comparison is void if one arm may price where the other may not. This is the confound
    that made the whole-book attempt return 9.4× — `flat_rules` is NOT clamped, and comparing an
    unbounded level against a bounded selection measures the bound."""
    ceiling = 105.0
    flat = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                         max_offered_rate_gbp_per_mwh=ceiling, **BASE)
    value = decide_margin(customer_id="C1", arm=VALUE_BASED,
                          max_offered_rate_gbp_per_mwh=ceiling, **BASE)
    assert flat.offered_rate_gbp_per_mwh <= ceiling + 1e-9
    assert value.offered_rate_gbp_per_mwh <= ceiling + 1e-9


def test_an_unclamped_level_is_still_delivered_when_no_ceiling_binds():
    """`None` means what it says: a non-domestic or non-capped product genuinely has no ceiling,
    and inventing one here would be the company checking its homework against a rule that does
    not apply to it."""
    d = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                      max_offered_rate_gbp_per_mwh=None, **BASE)
    assert d.margin_gbp_per_mwh == pytest.approx(44.5)


# ---------------------------------------------------------------------------
# 3. selecting the arm without a level REFUSES
# ---------------------------------------------------------------------------

def test_no_level_is_a_refusal_and_not_a_zero():
    """A level silently defaulting to 0.0 would reproduce the flat rule and be reported as a
    level comparison — a run that measured nothing and said it measured something."""
    with pytest.raises(MarginDecisionUnavailable, match="no level set"):
        decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, **BASE)


def test_the_refusal_says_why_a_zero_default_would_be_wrong():
    try:
        decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, **BASE)
    except MarginDecisionUnavailable as exc:
        assert "reproduce the flat rule" in str(exc)


# ---------------------------------------------------------------------------
# 4. the arm is registered, and the adapter no longer hardcodes the value arm
# ---------------------------------------------------------------------------

def test_the_arm_is_in_ARMS():
    assert FLAT_AT_LEVEL in ARMS
    assert set(ARMS) == {FLAT_RULES, VALUE_BASED, FLAT_AT_LEVEL}


def test_the_adapter_passes_the_ARM_THROUGH_rather_than_hardcoding_one():
    """THE DEFECT A THIRD ARM EXPOSED. `renewal_margin_uplift` called `decide_margin(arm=
    VALUE_BASED)` — invisible while the only other arm returned early, and a live defect the
    moment a third exists: `flat_at_level` renewals would have been priced by the value arm and
    the comparison would have compared the arm with itself.

    THE FIRST VERSION GREPPED FOR THE TEXT and failed on the COMMENT that explains the fix --
    "a mention is not a use", the fifth instance of that shape in one day and this one inside the
    test written to guard against it. It reads the CALL now.
    """
    import ast
    import inspect
    import textwrap

    from company.pricing.value_based_renewal import renewal_margin_uplift

    tree = ast.parse(textwrap.dedent(inspect.getsource(renewal_margin_uplift)))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and (getattr(n.func, "id", None) or getattr(n.func, "attr", None)) == "decide_margin"]
    assert calls, "the adapter no longer calls decide_margin -- this test's subject is gone"
    for call in calls:
        arm_kw = next((k for k in call.keywords if k.arg == "arm"), None)
        assert arm_kw is not None, "decide_margin called with no arm at all"
        assert isinstance(arm_kw.value, ast.Name) and arm_kw.value.id == "arm", (
            "the adapter hardcodes an arm instead of passing the one it was given: "
            f"arm={ast.unparse(arm_kw.value)}")


def test_the_flat_at_level_arm_does_NOT_return_before_the_guards():
    """It must reach the same term-index, commodity, tariff-type and observed-state guards the
    value arm passes, or it prices a different population and the comparison confounds selection
    with book membership."""
    import inspect

    from company.pricing.value_based_renewal import renewal_margin_uplift
    src = inspect.getsource(renewal_margin_uplift)
    early = src[: src.index("if arm not in ARMS")]
    assert FLAT_AT_LEVEL not in early, (
        "flat_at_level returns before the guards, so it no longer prices the value arm's "
        "population")


def test_the_policy_carries_the_level():
    from company.policy.decision_policy import CURRENT_POLICY
    assert CURRENT_POLICY.renewal_margin_flat_level_gbp_per_mwh is None, (
        "the default must be None so every existing run is unchanged")


# ---------------------------------------------------------------------------
# 5. the clamp REPORTS ITSELF — R15 FAIL-SILENT
# ---------------------------------------------------------------------------
#
# FOUND IN THIS ARM'S OWN FIRST DECADE RUN. It reported `distinct_margins: 4` for an arm that
# applies ONE level, and `endpoint_at_ceiling: 0`, and both described the same run. Clamping is
# the only mechanism that can vary a single constant, so the cap HAD bound four ways and the
# shape said it never bound at all — because `arm_decision_shape` reads `endpoint_side`, which
# the value arm's search sets and this branch did not. A zero that means "nobody wrote this
# field", presented as "this did not happen".


def test_a_clamped_decision_reports_the_ceiling_as_the_decider():
    d = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                      max_offered_rate_gbp_per_mwh=105.0, **BASE)
    assert d.margin_gbp_per_mwh == pytest.approx(5.0), "the clamp did not bite; test is vacuous"
    assert d.endpoint_bound is True
    assert d.endpoint_side == "ceiling", (
        "the cap decided this price and the decision does not say so — `arm_decision_shape` "
        "would report endpoint_at_ceiling=0 for a book the cap had bound")


def test_an_UNCLAMPED_decision_does_NOT_claim_the_ceiling_bound():
    """THE PARTNER, and the half that makes the one above mean something. A branch that always
    said "ceiling" would pass the test above and be just as wrong."""
    d = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                      max_offered_rate_gbp_per_mwh=None, **BASE)
    assert d.margin_gbp_per_mwh == pytest.approx(44.5)
    assert d.endpoint_bound is False
    assert d.endpoint_side is None


def test_a_ceiling_that_does_not_bite_is_not_reported_as_binding():
    """A ceiling PRESENT but ABOVE the level is the case a `max_offered is not None` test would
    get wrong — the original code clamped unconditionally with `min()` and could not tell these
    apart."""
    d = decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                      max_offered_rate_gbp_per_mwh=1_000.0, **BASE)
    assert d.margin_gbp_per_mwh == pytest.approx(44.5)
    assert d.endpoint_bound is False, "a ceiling far above the level was reported as binding"


def test_the_clamp_is_what_makes_a_FLAT_arm_show_several_margins():
    """THE MECHANISM BEHIND THE DEFECT, pinned so the explanation cannot rot. Two customers on
    different base rates under the same cap receive DIFFERENT margins from a single level — which
    is why `distinct_margins` exceeded 1 and why that was correct rather than a broken arm."""
    margins = {
        decide_margin(customer_id="C1", arm=FLAT_AT_LEVEL, flat_level_gbp_per_mwh=44.5,
                      max_offered_rate_gbp_per_mwh=105.0,
                      **{**BASE, "base_rate_gbp_per_mwh": base}).margin_gbp_per_mwh
        for base in (100.0, 90.0)
    }
    assert len(margins) > 1, (
        "the clamp produced one margin across two base rates, so it cannot explain the four "
        "distinct margins the decade run reported")
