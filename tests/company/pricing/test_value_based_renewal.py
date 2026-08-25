"""R15 contract for the per-customer renewal margin, and for the control it has to beat.

THE THESIS THIS IS TESTED AGAINST (director, 2026-08-25): a supplier that decides
customer-by-customer on lifetime value, *using only what it can actually know*, beating an
average player *precisely to the degree it predicts the truth better than average*. Two
constraints follow and both are tests here rather than paragraphs:

  THE ADVANTAGE MUST COME FROM INFERENCE, NEVER FROM ACCESS -- so the module may not import the
  world, and a BLIND churn model must buy it nothing.
  THERE MUST BE A BASELINE TO BEAT -- so the flat rule is a first-class arm, scored by the same
  function, and it must be able to WIN.

The most dangerous test in this file is `test_a_BLIND_churn_model_gives_the_value_arm_NO_
advantage`. Without it "value-based beats flat" is unfalsifiable: the value arm maximises the
company's own expected value, so on that number it wins by construction whatever the model
believes. An arm that wins against a coin is not making decisions.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from company.crm.payment_behaviour_analytics import BehaviourScore
from company.pricing import value_based_renewal as vbr
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

REPO = Path(__file__).resolve().parents[3]
MODULE = REPO / "company" / "pricing" / "value_based_renewal.py"

#: One ordinary domestic renewal. Every field is something a supplier reads off its own systems.
BASE = dict(
    customer_id="C1",
    current_rate_gbp_per_mwh=120.0,
    base_rate_gbp_per_mwh=118.0,
    eac_kwh=3100,
    tenure_years=4.0,
    cost_to_serve_gbp_per_year=55.0,
    expected_periods=3.0,
    segment="resi",
    renewal_year=2024,
)


def _decide(arm, **over):
    return vbr.decide_margin(arm=arm, **{**BASE, **over})


# --------------------------------------------------------------------------- #
# It is a DECISION: the same world, two customers, two answers                 #
# --------------------------------------------------------------------------- #

def test_two_customers_worth_different_amounts_get_different_prices():
    """THE WHOLE POINT, and the sentence the flat rule cannot say. If this ever fails, the module
    is a rule with extra steps."""
    cheap_and_loyal = _decide(vbr.VALUE_BASED, eac_kwh=18000,
                              cost_to_serve_gbp_per_year=25.0, expected_periods=6.0)
    dear_and_brief = _decide(vbr.VALUE_BASED, eac_kwh=2000,
                             cost_to_serve_gbp_per_year=140.0, expected_periods=1.1)

    assert cheap_and_loyal.margin_gbp_per_mwh != dear_and_brief.margin_gbp_per_mwh, (
        "two customers of very different worth were priced identically -- this is a flat rule "
        "wearing a decision's clothes"
    )


def test_MUTATION_the_FLAT_arm_prices_them_the_SAME_which_is_the_control():
    """The null that gives the test above its meaning: the control must be unable to tell those
    two customers apart, because that is exactly what makes it the control."""
    a = _decide(vbr.FLAT_RULES, eac_kwh=18000, cost_to_serve_gbp_per_year=25.0)
    b = _decide(vbr.FLAT_RULES, eac_kwh=2000, cost_to_serve_gbp_per_year=140.0)

    assert a.margin_gbp_per_mwh == b.margin_gbp_per_mwh == TARGET_MARGIN_GBP_PER_MWH


def test_the_control_IS_what_the_company_does_today_and_is_imported_not_restated():
    """A baseline that drifts is not a baseline. `TARGET_MARGIN_GBP_PER_MWH` is imported from the
    pricer the company actually uses, so the control cannot be quietly nudged toward the arm it
    is supposed to judge -- changing the company's real margin changes the control with it."""
    source = MODULE.read_text(encoding="utf-8")

    assert "from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH" in source
    assert _decide(vbr.FLAT_RULES).margin_gbp_per_mwh == TARGET_MARGIN_GBP_PER_MWH


# --------------------------------------------------------------------------- #
# Inference, never access                                                      #
# --------------------------------------------------------------------------- #

def test_the_module_cannot_reach_the_world():
    """The epistemic wall, checked on imports rather than promised in prose. An advantage that
    came from reading `sim_churn_probability` would be worthless and this is the cheap half of
    proving it did not."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    offenders = sorted(m for m in imported if m.split(".")[0] in ("sim", "simulation"))
    assert offenders == [], f"the decision imports {offenders} -- that is access, not inference"


def test_no_parameter_can_carry_the_worlds_answer():
    """The other half: an import ban is defeated by a caller HANDING IN the truth. Every
    parameter is checked by name against the world's own vocabulary, the same shape
    `growth_desk` holds for the acquisition gate."""
    import inspect

    params = set(inspect.signature(vbr.decide_margin).parameters)
    forbidden = {"sim_churn_probability", "true_churn_probability", "cohort", "green_stance",
                 "will_churn", "actual_churn", "sim_", "ground_truth"}
    leaks = {p for p in params if any(f in p for f in forbidden)}

    assert not leaks, f"the decision accepts {leaks} -- the world could hand it the answer"


def test_a_BLIND_churn_model_gives_the_value_arm_NO_advantage(monkeypatch):
    """THE TEST THAT MAKES THE WHOLE THING FALSIFIABLE.

    The value arm maximises the company's own expected value, so on that number it wins by
    construction -- whatever it believes. The claim it actually makes is narrower and much
    stronger: it beats flat *to the degree the churn model predicts better than chance*.

    So blind the model. With P(leave) constant, no candidate margin changes retention, expected
    value rises monotonically with margin, and the "decision" collapses to "charge the maximum" --
    identical for every customer, however different they are. That is what an arm with no
    predictive power looks like, and it looks nothing like a decision.

    MUTATION (must fire): make the churn estimate ignore the offered rate.
    """
    monkeypatch.setattr(vbr, "enriched_churn_estimate", lambda *a, **k: 0.10)

    rich = _decide(vbr.VALUE_BASED, eac_kwh=18000, cost_to_serve_gbp_per_year=25.0,
                   expected_periods=6.0)
    poor = _decide(vbr.VALUE_BASED, eac_kwh=2000, cost_to_serve_gbp_per_year=140.0,
                   expected_periods=1.1)

    assert rich.margin_gbp_per_mwh == poor.margin_gbp_per_mwh, (
        "a blind model still produced a per-customer answer, so the differentiation is coming "
        "from somewhere other than prediction"
    )
    # THE HIGHEST MARGIN STILL AVAILABLE, not the highest in the grid: the model's own support
    # bound clips the top of the grid before the search sees it (see
    # `max_supported_rate_increase_pct`), so a blind arm runs to that edge rather than to the
    # constant. Asserting the constant here was the first version of this test and it started
    # failing the moment the support bound landed -- correctly, because the claim is "an arm with
    # no predictive power charges the most it is allowed to", not "it charges £200".
    assert rich.margin_gbp_per_mwh == max(m for m, _ in rich.considered)
    assert rich.endpoint_bound, "a blind arm's choice sits at the grid edge and must say so"


# --------------------------------------------------------------------------- #
# A choice made by a constant is not a choice                                  #
# --------------------------------------------------------------------------- #

def test_an_argmax_at_the_EDGE_of_the_grid_is_reported_as_such():
    """MEASURED, ON THE FIRST PROBE. The first grid was 0.50..8.00 and every customer shape came
    back at exactly 8.00, because £2 to £8 on a 3,100 kWh account is about one percent of the
    bill and the DESNZ-calibrated switching curve rightly shrugs at one percent. The "decision"
    was this module's own constant read back, and nothing said so."""
    narrow = (0.5, 1.0, 2.0)
    clipped = _decide(vbr.VALUE_BASED, candidates=narrow)

    assert clipped.margin_gbp_per_mwh in (narrow[0], narrow[-1])
    assert clipped.endpoint_bound, "a clipped argmax was reported as an optimum"


def test_the_full_grid_finds_an_INTERIOR_optimum_for_an_ordinary_customer():
    """The null: if the shipped grid also clipped, the flag above would be permanently on and
    would stop meaning anything. It does not -- the model genuinely turns over."""
    decision = _decide(vbr.VALUE_BASED)

    assert not decision.endpoint_bound, (
        f"the shipped grid still clips at {decision.margin_gbp_per_mwh}; widen it or the "
        "decision is a constant"
    )


def test_a_lawful_ceiling_binds_BEFORE_the_search_and_is_reported():
    """A value-maximising supplier is still one that obeys the cap. Scoring an unlawful candidate
    and clamping the winner afterwards would report an expected value nobody can earn."""
    capped = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=130.0)

    assert capped.margin_gbp_per_mwh <= 130.0 - BASE["base_rate_gbp_per_mwh"] + 1e-9
    assert capped.ceiling_bound, "the ceiling removed candidates and the decision did not say so"
    assert all(BASE["base_rate_gbp_per_mwh"] + m <= 130.0 + 1e-9 for m, _ in capped.considered), (
        "an unlawful candidate was scored"
    )


def test_a_ceiling_that_forbids_EVERY_candidate_raises_rather_than_defaulting():
    """R15 fail-silent. Falling back to the flat rule here would report "no lawful offer" and
    "no gain from deciding" as the same thing."""
    with pytest.raises(vbr.MarginDecisionUnavailable):
        _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=100.0)


# --------------------------------------------------------------------------- #
# The harm surface, and the weight that is not mine                            #
# --------------------------------------------------------------------------- #

def test_the_arm_WANTS_to_charge_a_struggling_household_more_and_is_stopped():
    """MEASURED, AND IT IS THE UNCOMFORTABLE RESULT THIS MODULE EXISTS TO SURFACE.

    Unconstrained, the value arm priced the flighty, expensive-to-serve, three-bill-shock
    household HIGHEST of the three probed -- £100/MWh against £80 for the loyal one. The logic is
    impeccable: a customer who is leaving anyway should be extracted from while they are here.
    It is also what a regulator fines a real supplier for.

    The weight that would settle it is `A7_harm_cost_weights_ratio`, an R13 curriculum value,
    open in the action register and unsigned. So the arm may price DOWN from flat for a
    household in difficulty and never UP, and it RECORDS that it wanted to -- because "no
    different from flat" must not mean both "nothing to gain" and "refused to take it".

    MUTATION (must fire): drop the distress branch and let the maximiser through.
    """
    distressed = _decide(vbr.VALUE_BASED, bill_shock_count=3)

    assert distressed.margin_gbp_per_mwh <= TARGET_MARGIN_GBP_PER_MWH
    assert distressed.withheld_reason, "the arm held back and left no record that it had"
    assert "A7_harm_cost_weights_ratio" in distressed.withheld_reason, (
        "the refusal does not name the reserved value that would settle it, so the next reader "
        "cannot tell a policy from a bug"
    )


def test_a_CRITICAL_payment_score_is_distress_even_with_no_bill_shocks():
    scored = _decide(vbr.VALUE_BASED, behaviour_score=BehaviourScore.CRITICAL)

    assert scored.withheld_reason and scored.margin_gbp_per_mwh <= TARGET_MARGIN_GBP_PER_MWH


def test_MUTATION_a_healthy_payer_is_NOT_withheld():
    """The null. Without it, "protects the vulnerable" is also satisfied by an arm that never
    prices above flat at all -- which is the control."""
    healthy = _decide(vbr.VALUE_BASED, behaviour_score=BehaviourScore.EXCELLENT,
                      eac_kwh=18000, cost_to_serve_gbp_per_year=25.0, expected_periods=6.0)

    assert healthy.withheld_reason is None
    assert healthy.margin_gbp_per_mwh > TARGET_MARGIN_GBP_PER_MWH


# --------------------------------------------------------------------------- #
# The arithmetic                                                               #
# --------------------------------------------------------------------------- #

def test_cost_to_serve_is_only_paid_on_a_customer_who_STAYS():
    """The whole economics of a bad customer. Outside the retained branch, a loss-making account
    looks equally bad at every margin and the model prices it as though nothing could be done;
    inside, raising the margin until they leave is a legitimate outcome the arithmetic can reach."""
    kept = vbr.expected_value_gbp(margin_gbp_per_mwh=5.0, eac_mwh=3.1,
                                  cost_to_serve_gbp_per_year=55.0, p_retain=1.0,
                                  expected_periods=1.0, discount_rate=0.0)
    gone = vbr.expected_value_gbp(margin_gbp_per_mwh=5.0, eac_mwh=3.1,
                                  cost_to_serve_gbp_per_year=55.0, p_retain=0.0,
                                  expected_periods=1.0, discount_rate=0.0)

    assert kept == pytest.approx(5.0 * 3.1 - 55.0)
    assert gone == 0.0, "a departed customer still cost something to serve"


def test_both_arms_are_scored_by_the_SAME_function():
    """Any difference between the arms must be the DECISION and never the scorer. The control
    does not search; it prices the constant and is then valued identically."""
    flat = _decide(vbr.FLAT_RULES)
    value = _decide(vbr.VALUE_BASED, candidates=(TARGET_MARGIN_GBP_PER_MWH,))

    assert flat.expected_value_gbp == pytest.approx(value.expected_value_gbp)
    assert flat.p_retain == pytest.approx(value.p_retain)


def test_an_account_with_NO_consumption_raises_rather_than_being_priced():
    with pytest.raises(vbr.MarginDecisionUnavailable):
        _decide(vbr.VALUE_BASED, eac_kwh=0)


def test_an_unknown_arm_is_refused_rather_than_defaulted():
    with pytest.raises(vbr.MarginDecisionUnavailable):
        _decide("whatever_seems_best")
