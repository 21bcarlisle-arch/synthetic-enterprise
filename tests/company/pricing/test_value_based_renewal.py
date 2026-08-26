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
# The licence, read rather than recalled -- and the floor that is gone         #
# --------------------------------------------------------------------------- #

def test_the_FLOOR_is_gone_and_a_struggling_household_can_be_priced_on_its_cost():
    """THE CORRECTION THE DIRECTOR ASKED FOR, and reading SLC 27 is what settled it.

    This arm used to refuse to price a household in payment difficulty above the flat rule. The
    licence does not say that. SLC 27.8 requires ability to pay to be ascertained and used "when
    CALCULATING INSTALMENTS" -- a debt-repayment duty, not a pricing one -- and the register
    quotes it verbatim. What replaces the floor is the cost itself: a customer with a higher
    expected default costs more to serve, and the arithmetic now says so.

    MUTATION (must fire): reinstate a floor at TARGET_MARGIN_GBP_PER_MWH for distressed accounts.
    """
    priced = _decide(vbr.VALUE_BASED, credit_risk="vulnerable", payment_delay_days=45,
                     bill_shock_count=3, max_offered_rate_gbp_per_mwh=250.0)

    assert priced.margin_gbp_per_mwh > TARGET_MARGIN_GBP_PER_MWH, (
        "a household in payment difficulty is still floored at the flat rule, which is a "
        "stronger rule than SLC 27 supports"
    )
    assert priced.withheld_reason is None


def test_expected_cost_RISES_with_credit_risk_and_that_is_what_replaces_the_floor():
    """Director: "pricing follows expected cost -- and default risk, collections cost and bad
    debt are part of that cost. Put them inside the EV arithmetic and let the answer emerge."

    The flat 2.00 was never neutral. It was a cross-subsidy from reliable payers to unreliable
    ones, invisible because nobody had put the cost in the sum."""
    low = _decide(vbr.FLAT_RULES, credit_risk="low", payment_delay_days=5).costs
    bad = _decide(vbr.FLAT_RULES, credit_risk="vulnerable", payment_delay_days=45).costs

    assert bad.total_gbp > low.total_gbp * 1.5, (
        f"expected cost barely moves with credit risk ({low.total_gbp:.2f} -> {bad.total_gbp:.2f})"
    )
    assert bad.bad_debt_gbp > low.bad_debt_gbp and bad.carrying_gbp > low.carrying_gbp


def test_bad_debt_is_taken_on_the_WHOLE_BILL_and_not_on_the_margin():
    """THE ENTIRE ECONOMICS OF A RISKY CUSTOMER. A default on a 1,700 GBP annual bill costs the
    supplier the wholesale, network and policy cost it has already paid -- not the six pounds of
    margin it hoped to make. Charging the loss against the margin would make default look like a
    rounding error.

    MUTATION (must fire): pass the margin instead of the revenue to `bad_debt_provision_gbp`.
    """
    costs = vbr.expected_annual_costs(
        cost_to_serve_gbp_per_year=0.0, annual_revenue_gbp=1700.0, credit_risk="high")

    assert costs.bad_debt_gbp > 50.0, (
        f"a 5% default probability on a 1,700 GBP bill produced {costs.bad_debt_gbp:.2f} -- that "
        "is a rate applied to something much smaller than the bill"
    )


def test_an_UNSOURCED_cost_term_is_NAMED_rather_than_counted_as_zero():
    """No per-contact or per-dunning-step cost exists anywhere in this tree. The term is in the
    arithmetic and its absence is legible, because a silent zero here understates exactly the
    customers this decision is about."""
    costs = vbr.expected_annual_costs(cost_to_serve_gbp_per_year=55.0, annual_revenue_gbp=1700.0)

    assert any("collections cost" in u for u in costs.unsourced)
    assert costs.collections_gbp == 0.0


def test_forgetting_the_STANDING_CHARGE_makes_the_arm_OVER_PRICE():
    """THIS TEST CORRECTED ME, WHICH IS WHAT IT IS FOR.

    Without fixed revenue every customer came out value-negative -- 2.00 GBP/MWh on 3.1 MWh is
    6.20 GBP a year against 66 to 98 of cost -- reading as "this company loses money on every
    domestic customer", an artefact of omitting a 0.27 GBP/day standing charge the customer
    really pays.

    I then wrote this test asserting the standing charge merely raised the LEVEL and cancelled
    between the arms. It does not, and the assertion caught it: the value-maximising margin FELL
    from 80.00 to 60.00. Fixed revenue is only earned from a customer who STAYS, so it sits
    inside the retention term -- making retention more valuable makes losing the customer more
    expensive, and the optimiser charges LESS to keep them.

    A supplier that forgets its standing charge therefore over-prices its commodity. That is a
    result, not a caveat, and it would have been asserted away.

    THE GRID IS A £1 ONE HERE AND THAT IS NOT A WEAKENING (2026-08-25). On the shipped
    16-point grid this comparison ran on until today, both arms landed on the same rung
    (60.00) once the churn model's captive floor was removed and its rate response was put
    on the supplier-specific move -- the optimum shifts, the SIZE of the effect being
    measured does not, and a grid whose gaps are wider than the effect measures the grid.
    Resolved to £1 the property is exactly as it was: 86.00 without the standing charge,
    70.00 with it. Asserting the mechanism, at a resolution that can see it.
    """
    fine = tuple(float(m) for m in range(1, 161))
    without = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0, candidates=fine)
    with_sc = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0,
                      fixed_revenue_gbp_per_year=98.55, candidates=fine)

    assert with_sc.margin_gbp_per_mwh < without.margin_gbp_per_mwh, (
        "counting revenue the customer really pays did not make retention more valuable"
    )
    assert any("fixed revenue" in u for u in without.costs.unsourced)
    assert not any("fixed revenue" in u for u in with_sc.costs.unsourced)


def test_SLC_7_4_binds_a_DEEMED_contract_and_does_not_reach_a_negotiated_one():
    """The comparative test that IS in the licence, against the floor that was not. SLC 7.4 makes
    a deemed-contract class margin significantly above the book's general margin unduly onerous;
    it reaches a negotiated contract not at all, and flattening that difference would be
    inventing an obligation -- the same error as the floor, in the other direction.

    MUTATION (must fire): apply the class-margin test regardless of `is_deemed_contract`.
    """
    deemed = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0,
                     is_deemed_contract=True, book_general_margin_gbp_per_mwh=2.0)
    negotiated = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0,
                         is_deemed_contract=False, book_general_margin_gbp_per_mwh=2.0)

    assert deemed.withheld_reason and "SLC 7.4" in deemed.withheld_reason
    assert deemed.margin_gbp_per_mwh <= TARGET_MARGIN_GBP_PER_MWH
    assert negotiated.withheld_reason is None
    assert negotiated.margin_gbp_per_mwh > TARGET_MARGIN_GBP_PER_MWH


def test_an_UNKNOWN_book_margin_on_a_deemed_contract_FAILS_the_check_rather_than_passing_it():
    """R15 fail-silent, with a regulator on the other end. A comparative test that cannot find
    its comparator has not been satisfied."""
    unknown = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0,
                      is_deemed_contract=True, book_general_margin_gbp_per_mwh=None)

    assert unknown.withheld_reason and "cannot be run" in unknown.withheld_reason


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


# ═══════════════════════════════════════════════════════════════════════════════════════
# 2026-08-25: the maximiser is BOUNDED BY ITS BELIEF, not by the guard bolted in front of it.
#
# `max_supported_rate_increase_pct` (+83.1%, the largest published cap step) still stands and
# is still right -- a decision must not extrapolate past its evidence. But it was doing a
# second job it should never have had to do: hiding the fact that expected value rose forever
# behind it. These tests DISABLE the guard on purpose, so what they measure is the belief.
# ═══════════════════════════════════════════════════════════════════════════════════════

#: Deliberately absurd at the top end -- £5,000/MWh is roughly forty times a domestic unit
#: rate. If the optimum is interior on THIS grid it is interior anywhere.
_ABSURD_GRID = (0.5, 2.0, 10.0, 40.0, 60.0, 100.0, 200.0, 500.0, 1200.0, 5000.0)


def _decide_unguarded(monkeypatch, **overrides):
    monkeypatch.setattr(vbr, "max_supported_rate_increase_pct", lambda: 1.0e9)
    kwargs = dict(
        customer_id="PROBE", arm=vbr.VALUE_BASED,
        current_rate_gbp_per_mwh=120.0, base_rate_gbp_per_mwh=118.0,
        eac_kwh=3100.0, tenure_years=4.0, cost_to_serve_gbp_per_year=80.0,
        expected_periods=6.0, segment="resi", renewal_year=2025,
        fixed_revenue_gbp_per_year=99.0, candidates=_ABSURD_GRID,
    )
    kwargs.update(overrides)
    return vbr.decide_margin(**kwargs)


def test_the_profit_maximising_price_is_interior_with_the_support_guard_removed(monkeypatch):
    """The finding's headline, tested as arithmetic rather than argued. With nothing bounding
    the search, expected value must TURN OVER and fall away -- otherwise the arm's answer is
    whatever ceiling it happened to be given, which is not a decision."""
    d = _decide_unguarded(monkeypatch)
    assert not d.endpoint_bound, "the winner is still the largest candidate offered"
    evs = [ev for _, ev in d.considered]
    peak = max(range(len(evs)), key=lambda i: evs[i])
    assert 0 < peak < len(evs) - 1, "the peak must be strictly inside the grid"
    assert evs[-1] < evs[peak] / 100.0, (
        "expected value must COLLAPSE at an absurd price, not merely grow more slowly -- a "
        "supplier priced forty times the market keeps nobody"
    )


def test_null_control_the_old_ceiling_makes_it_unbounded_again(monkeypatch):
    """THE MUTATION (R15). Put back the single constant -- the company churn model's 0.95
    ceiling -- and the same maximiser on the same account runs away to the top of any grid it
    is given, with expected value still climbing. If this control ever stops failing that way,
    the test above is not measuring what it claims to."""
    import company.crm.churn_model as cm
    monkeypatch.setattr(cm, "MAX_CHURN_PROBABILITY", 0.95)
    d = _decide_unguarded(monkeypatch)
    assert d.endpoint_bound
    assert d.margin_gbp_per_mwh == _ABSURD_GRID[-1]
    evs = [ev for _, ev in d.considered]
    assert evs[-1] > evs[-2] > 0.0, "expected value was still rising at £5,000/MWh"


def test_the_market_wide_half_of_a_rate_move_reaches_the_decision(monkeypatch):
    """The decision path must actually SEE the supplier-specific/market-wide split -- a
    correction that stops at the model and never reaches the maximiser is a dark fix.

    2022's published cap step is +66.7%; 2026's is flat. Pricing the same customer at the
    same rate in those two worlds must give different answers, and the direction is the one
    the world's own history dictates: in a year when everybody's price moved, the customer
    has nowhere to go, so the company may charge more."""
    in_a_moving_market = _decide_unguarded(monkeypatch, renewal_year=2022)
    in_a_still_market = _decide_unguarded(monkeypatch, renewal_year=2026)
    assert in_a_moving_market.margin_gbp_per_mwh > in_a_still_market.margin_gbp_per_mwh
    assert in_a_moving_market.p_retain > in_a_still_market.p_retain


# ═══════════════════════════════════════════════════════════════════════════════════════
# 2026-08-25, delivery seat: THE CHOICE WAS THE GRID'S, NOT THE CUSTOMER'S.
#
# Run over the real 263-account book, this arm returned exactly 130.00 GBP/MWh for 107 accounts
# and exactly 100.00 for 83 more -- two of its own constants carrying 72% of the book -- while
# 165 accounts were flagged support-bound. Both readings were wrong in the same direction: the
# optima were per-customer all along (180 distinct on a 0.25 lattice, every one interior), the
# grid was rounding them onto four rungs thirty pounds apart, and the bound that looked like the
# cause was binding on NONE of them.
# ═══════════════════════════════════════════════════════════════════════════════════════

def test_the_chosen_margin_is_the_CUSTOMERS_optimum_and_not_a_RUNG_of_the_grid():
    """THE HEADLINE, as arithmetic. If the grid were still deciding, the chosen margin would be
    a member of `CANDIDATE_MARGINS_GBP_PER_MWH` and no margin off it could score better.

    MUTATION (must fire): delete the refinement and return the grid's argmax.
    """
    decision = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0)

    assert decision.margin_gbp_per_mwh not in vbr.CANDIDATE_MARGINS_GBP_PER_MWH, (
        f"the answer is {decision.margin_gbp_per_mwh}, which is a rung of this module's own grid"
    )
    on_the_grid = max(
        v for m, v in decision.considered if m in vbr.CANDIDATE_MARGINS_GBP_PER_MWH)
    assert decision.expected_value_gbp > on_the_grid, (
        "the refined answer is worth no more than the best grid rung, so the refinement is "
        "decoration"
    )


def test_THREE_CUSTOMERS_ON_ONE_GRID_RUNG_GET_THREE_ANSWERS():
    """The population defect in miniature -- 107 accounts on one rung, reproduced at n=3.

    A 4 MWh, a 6 MWh and a 9 MWh account all sit on the 60.00 rung of the shipped grid, and the
    grid alone therefore prices them identically. Their own optima are 67.25, 65.00 and 63.25:
    the bigger the account, the less margin it takes to be worth keeping, which is a sentence
    about customers and not about candidate lists.

    THE FIRST VERSION OF THIS TEST WAS WRONG AND SAID SO. It used 3,100 vs 3,160 kWh, and after
    the lattice snap was fixed both correctly returned 69.25 -- a 2% difference in consumption
    moves the optimum by less than 25p/MWh, so demanding two answers there was demanding
    precision the decision does not have. Separating the customers by more than the resolution
    and less than the grid's spacing is what actually tests the claim.

    MUTATION (must fire): return the grid's argmax instead of refining it -- all three collapse
    to 60.00.
    """
    wide = dict(max_offered_rate_gbp_per_mwh=250.0)
    chosen = [_decide(vbr.VALUE_BASED, eac_kwh=kwh, **wide).margin_gbp_per_mwh
              for kwh in (4000, 6000, 9000)]

    assert len(set(chosen)) == 3, (
        f"three different customers on one rung of the grid were given {sorted(set(chosen))} -- "
        "the answer is being quantised onto something other than the customer"
    )
    assert chosen == sorted(chosen, reverse=True), (
        f"the bigger account is not the keener-priced one ({chosen}), so the ordering is not the "
        "economics"
    )


def test_a_bound_that_TRIMMED_the_grid_but_did_not_change_the_answer_is_not_reported_as_binding():
    """WHAT MADE THE SEAT READ THE RECORD WRONG. `extrapolation_bound` used to mean "candidates
    were removed", and a reader -- correctly -- reads a bound flag as a statement that the bound
    decided the price. On the real book it fired on 165 accounts and decided none of them.

    MUTATION (must fire): report the flags as `len(allowed) < len(candidates)` again.
    """
    trimmed = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=250.0)

    assert trimmed.candidates_removed > 0, "nothing was trimmed, so this proves nothing"
    assert not trimmed.ceiling_bound, (
        "a ceiling that removed only candidates the arm would never have chosen is reported as "
        "having decided the price"
    )
    assert not trimmed.endpoint_bound


def test_the_NULL_a_ceiling_that_really_does_decide_still_says_so():
    """The other half of the mutation above: narrowing the meaning must not empty it."""
    binding = _decide(vbr.VALUE_BASED, max_offered_rate_gbp_per_mwh=130.0)

    assert binding.ceiling_bound, "the ceiling chose the price and the record did not say so"
    assert binding.endpoint_bound and binding.endpoint_side == "ceiling"


def test_a_FLOOR_bound_choice_is_not_reported_as_the_arm_STRAINING_UPWARD():
    """MEASURED ON THE REAL BOOK: five accounts of 190-340 kWh/year, whose 98.55 GBP standing
    charge is the entire relationship and whose profit-maximising COMMODITY margin is negative --
    the arm would sell them electricity below cost to keep the standing charge, and cannot,
    because the lowest candidate is 0.50. The published verdict called that "chose the highest
    margin available to it", which is the opposite of what happened.

    MUTATION (must fire): collapse `endpoint_side` back to a single boolean.
    """
    tiny = _decide(vbr.VALUE_BASED, eac_kwh=200, cost_to_serve_gbp_per_year=6.0,
                   expected_periods=1.0, fixed_revenue_gbp_per_year=98.55,
                   max_offered_rate_gbp_per_mwh=250.0)

    assert tiny.endpoint_side == "floor", (
        f"a micro-consumption account chose {tiny.margin_gbp_per_mwh} and the record calls that "
        f"{tiny.endpoint_side}"
    )
    assert tiny.margin_gbp_per_mwh == min(vbr.CANDIDATE_MARGINS_GBP_PER_MWH)


def test_the_MARGINAL_pound_carries_its_own_default_risk():
    """Expected cost used to be computed once, off the bill the customer is on TODAY, and held
    fixed across every candidate -- so a 50% price rise was scored as carrying the default risk
    of the old price. Bad debt is a fraction of the bill; a bigger bill is a bigger loss.

    MUTATION (must fire): compute `expected_annual_costs` once, outside `_score`.
    """
    from saas.payment_behaviour import bad_debt_provision_gbp

    priced = _decide(vbr.VALUE_BASED, credit_risk="high", annual_revenue_gbp=1700.0,
                     max_offered_rate_gbp_per_mwh=250.0)
    offered_bill = 1700.0 + (priced.margin_gbp_per_mwh - 2.0) * priced.eac_mwh

    assert priced.margin_gbp_per_mwh > 2.0, "this customer was not repriced, so nothing is proven"
    assert priced.costs.bad_debt_gbp == pytest.approx(
        bad_debt_provision_gbp("high", offered_bill)), (
        "the provision is {:.2f}, which is the rate applied to the bill this customer is on "
        "today rather than the one they are being offered".format(priced.costs.bad_debt_gbp)
    )
    assert priced.costs.bad_debt_gbp > bad_debt_provision_gbp("high", 1700.0)
