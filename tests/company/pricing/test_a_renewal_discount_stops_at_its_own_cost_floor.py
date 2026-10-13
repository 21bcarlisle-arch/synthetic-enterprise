"""A renewal discount may cost margin; it may never take the rate under the cost the desk struck over.

THE DEFECT (`SEAT_FINDING_B8_Q5_WHY_THE_RENEWAL_FIX_SITS_BELOW_ITS_OWN_COST_FLOOR_2026-10-12.md`):
the rate chain's writer 1, the portfolio learning premium, multiplied the struck rate by down to
-5% while the desk had struck it only ~2% above `company_fwd + locked_policy + locked_network`.
15 of 18 electricity renewals to 2017-03-31 left the chain below that floor, and nothing re-floored.

THE SECOND DEFECT (`SEAT_FINDING_WRITER_ONE_DISCOUNTS_INTO_THE_CAPITAL_CHARGE_2026-10-13.md`): that
floor left out the capital charge the strike prices in, so writer 1 still cut 496 of 698 renewals
on seed 61001 into the band between it and the term's own cost. The floor is now the term cost.

Each test names the defect it fires on. Through the typed record and the SEAM DOOR the run calls, because an adapter that
forwards named fields drops a new one silently unless the control goes through it.
"""

from __future__ import annotations

import pytest

import company.pricing.renewal_rate_chain as desk
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR,
    DiscretionaryRateBelowOwnCostFloorError,
    check_discretionary_rate_not_below_own_cost_floor,
)
from company.interfaces.renewal_decision_inputs import RenewalDecisionInputs
from company.interfaces.renewal_rate_chain import decide_renewal, decide_renewal_rate
from company.pricing.renewal_desk import pre_margin_unit_rate
from company.pricing.tariff_engine import (
    PORTFOLIO_PREMIUM_HALF_LIFE,
    PORTFOLIO_PREMIUM_MIN,
    PORTFOLIO_TARGET_MARGIN_RATE,
    compute_portfolio_premium,
)

# The item's own example: 2017-01-09 electricity, struck 139.15 over forward + locked costs of
# 136.27, plus a capital charge of 1.11 (1.645 x 0.50 x 0.15 x 10% WACC x 90): a term cost of 137.38.
FWD, POLICY, NETWORK = 90.0, 14.27, 32.0
COST_WITHOUT_CAPITAL = FWD + POLICY + NETWORK
FLOOR = pre_margin_unit_rate(FWD, "2017-01-09", POLICY, NETWORK)
STRUCK = 139.15
#: A book running far above target: the premium clamps at its floor, -5%.
BOOK_FAR_ABOVE_TARGET = [0.30] * 5
#: A book just above target: a -1% premium, inside the desk's headroom.
BOOK_JUST_ABOVE_TARGET = [PORTFOLIO_TARGET_MARGIN_RATE + 0.01 / PORTFOLIO_PREMIUM_HALF_LIFE] * 5


def _rate(book, *, struck=STRUCK, floor_known=True):
    """A non-domestic fixed renewal, so only writer 1 can move it: no cap, no stayer default,
    no prior-term loss, no settled records for the uplift."""
    costs = dict(company_forward_per_mwh=FWD, locked_policy_cost_per_mwh=POLICY,
                 locked_network_cost_per_mwh=NETWORK) if floor_known else {}
    return decide_renewal(RenewalDecisionInputs(
        customer_id="C1", billing_account="C1", commodity="electricity",
        term_start="2017-01-09", tariff_type="fixed", term_index=1,
        struck_unit_rate_per_mwh=struck, portfolio_margin_rates=book,
        prior_term_margin=None, prior_term_revenue=0.0, is_domestic=False,
        settled_records=[], customer={"metering": "NHH", "smart_meter": False}, **costs))


def test_the_two_books_put_the_premium_either_side_of_the_desks_headroom():
    """Control on the fixtures, so the tests below cannot pass on a premium that never crossed."""
    assert compute_portfolio_premium(BOOK_FAR_ABOVE_TARGET) == PORTFOLIO_PREMIUM_MIN
    assert STRUCK * (1 + PORTFOLIO_PREMIUM_MIN) < FLOOR
    assert FLOOR < STRUCK * (1 + compute_portfolio_premium(BOOK_JUST_ABOVE_TARGET)) < STRUCK


def test_the_floor_is_the_term_cost_with_its_capital_charge():
    """DEFECT: the floor omits capital, so a discount stops above forward + locked costs and still
    under what the term costs to carry. Pinned at the fixture's own numbers."""
    assert FLOOR == pytest.approx(137.380375)
    assert FLOOR - COST_WITHOUT_CAPITAL == pytest.approx(1.645 * 0.50 * 0.15 * 0.10 * FWD)
    deep = _rate(BOOK_FAR_ABOVE_TARGET)
    assert deep.unit_rate_gbp_per_mwh > COST_WITHOUT_CAPITAL + 1.0


def test_a_deep_discount_stops_at_the_floor_and_a_shallow_one_is_untouched():
    """DEFECT: writer 1 discounts below cost. Both branches over one partition: a floor that
    caught everything would fail the shallow leg, and no floor at all fails the deep one."""
    deep, shallow = _rate(BOOK_FAR_ABOVE_TARGET), _rate(BOOK_JUST_ABOVE_TARGET)
    assert deep.unit_rate_gbp_per_mwh == pytest.approx(FLOOR)
    shallow_expected = STRUCK * (1 + compute_portfolio_premium(BOOK_JUST_ABOVE_TARGET))
    assert shallow.unit_rate_gbp_per_mwh == pytest.approx(shallow_expected)
    floored = [c.dynamic_pricing_entries[0]["floored_at_cost"] for c in (deep, shallow)]
    assert floored == [True, False]
    assert deep.dynamic_pricing_entries[0]["cost_floor"] == pytest.approx(FLOOR)


def test_with_no_floor_to_check_against_a_discount_is_withheld_and_a_surcharge_is_not():
    """DEFECT: an unknown floor read as no floor (fail open). A book below target still rises."""
    assert _rate(BOOK_FAR_ABOVE_TARGET, floor_known=False).unit_rate_gbp_per_mwh == STRUCK
    under_target = [0.0] * 5
    assert compute_portfolio_premium(under_target) > 0
    assert _rate(under_target, floor_known=False).unit_rate_gbp_per_mwh > STRUCK


def test_a_rate_that_entered_below_the_floor_is_not_lifted_by_a_writer_that_only_cuts():
    """DEFECT: the re-floor turned into a price rise. Entered at 130 against a floor of 136.27, the
    discount may take it no lower than it came in -- and no higher either."""
    out = _rate(BOOK_FAR_ABOVE_TARGET, struck=130.0)
    assert out.unit_rate_gbp_per_mwh == pytest.approx(130.0)


def test_the_keyword_door_carries_the_floor_too():
    """DEFECT: the keyword door (kept for older callers) drops the floor, so its callers decide with
    none and (fail closed) every discount is withheld."""
    out = decide_renewal_rate(
        customer_id="C1", billing_account="C1", commodity="electricity",
        term_start="2017-01-09", tariff_type="fixed", term_index=1,
        struck_unit_rate_gbp_per_mwh=STRUCK, portfolio_margin_rates=BOOK_FAR_ABOVE_TARGET,
        prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0, is_domestic=False,
        settled_records=[], customer={"metering": "NHH", "smart_meter": False},
        company_forward_per_mwh=FWD, locked_policy_cost_per_mwh=POLICY,
        locked_network_cost_per_mwh=NETWORK)
    assert out.unit_rate_gbp_per_mwh == pytest.approx(FLOOR)


def test_the_chain_refuses_at_its_return_whichever_writer_crossed(monkeypatch):
    """DEFECT: the class is guarded only inside writer 1, so a future writer reopens the gap. With
    writer 1's own floor knocked out, the check where the chain returns must refuse on its own."""
    monkeypatch.setattr(desk, "_floor_a_discount", lambda before, discounted, floor: discounted)
    with pytest.raises(DiscretionaryRateBelowOwnCostFloorError, match="below what"):
        _rate(BOOK_FAR_ABOVE_TARGET)


def test_the_invariant_allows_only_what_entered_low_or_what_the_cap_put_there():
    """DEFECT: the predicate refuses a lawful cap clamp, or passes a discount under cost."""
    assert DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR in ALL_INVARIANTS
    check = check_discretionary_rate_not_below_own_cost_floor
    assert not check(132.19, entered=139.15, cost_floor=FLOOR)
    assert check(FLOOR, entered=139.15, cost_floor=FLOOR)
    assert check(130.0, entered=130.0, cost_floor=FLOOR)
    assert check(120.0, entered=139.15, cost_floor=FLOOR, cap=120.0)
    assert not check(119.0, entered=139.15, cost_floor=FLOOR, cap=120.0)
    assert check(1.0, entered=139.15, cost_floor=None)


def _level_arm(level, *, floor_known=True):
    from dataclasses import replace

    from company.policy.decision_policy import CURRENT_POLICY, policy_scope
    from company.pricing.value_based_renewal import FLAT_AT_LEVEL

    settled = [{"customer_id": "C1", "commodity": "electricity",
                "settlement_date": f"2016-{m:02d}-15", "term_start": "2016-01-01",
                "consumption_kwh": 250.0, "revenue_gbp": 30.0, "net_margin_gbp": 1.0,
                "margin_gbp": 5.0, "settlement_periods_folded": 48} for m in range(1, 13)]
    costs = dict(company_forward_per_mwh=FWD, locked_policy_cost_per_mwh=POLICY,
                 locked_network_cost_per_mwh=NETWORK) if floor_known else {}
    policy = replace(CURRENT_POLICY, name="level_arm", renewal_margin_arm=FLAT_AT_LEVEL,
                     renewal_margin_flat_level_gbp_per_mwh=level)
    with policy_scope(policy):
        return decide_renewal(RenewalDecisionInputs(
            customer_id="C1", billing_account="C1", commodity="electricity",
            term_start="2017-01-09", tariff_type="fixed", term_index=1,
            struck_unit_rate_per_mwh=STRUCK, portfolio_margin_rates=BOOK_FAR_ABOVE_TARGET,
            prior_term_margin=None, prior_term_revenue=0.0, is_domestic=False,
            settled_records=settled, customer={"metering": "NHH", "smart_meter": False},
            **costs))


def test_the_arm_measures_its_margin_from_the_terms_own_cost_not_the_rate_writer_one_left():
    """DEFECT: the arm's base was `the rate writer 1 left - GBP 2`, so on a term writer 1 cut to
    the floor a level-L renewal earned L - 3.11 and the arm's belief was for a margin it never
    charged. Now the contracted rate is the term's pre-margin cost (forward + capital + locked
    costs) plus the level, whatever writer 1 did."""
    from company.pricing.renewal_desk import pre_margin_unit_rate

    base = pre_margin_unit_rate(FWD, "2017-01-09", POLICY, NETWORK)
    assert base > COST_WITHOUT_CAPITAL, "no capital charge in the base, so the arm reads it as margin"
    for level in (0.5, 5.0):
        out = _level_arm(level)
        entry = out.value_arm_entries[0]
        assert entry["arm_base_source"] == "term_cost"
        assert entry["arm_base_gbp_per_mwh"] == pytest.approx(base, abs=1e-4)
        assert out.unit_rate_gbp_per_mwh == pytest.approx(base + level)
        assert entry["offered_rate_gbp_per_mwh"] == pytest.approx(out.unit_rate_gbp_per_mwh,
                                                                  abs=1e-4)


def test_the_arm_may_cut_a_rate_no_further_than_cost_and_says_when_it_was_stopped(monkeypatch):
    """DEFECT: the base and the floor are now one number, so the arm's own floor binds only where
    they part, and a floor nobody can reach is not tested. The base alone, knocked GBP 4 under cost
    on its way into the arm, reaches it: 0.5 over it is floored, 0.5 over the true base is not."""
    from company.pricing.renewal_desk import pre_margin_unit_rate

    kept = _level_arm(0.5)
    real_uplift = desk.renewal_margin_uplift

    def base_knocked_under_cost(**kw):
        return real_uplift(**{**kw, "pre_margin_rate_gbp_per_mwh": FLOOR - 4.0})

    monkeypatch.setattr(desk, "renewal_margin_uplift", base_knocked_under_cost)
    cut = _level_arm(0.5)
    assert cut.unit_rate_gbp_per_mwh == pytest.approx(FLOOR)
    assert kept.unit_rate_gbp_per_mwh == pytest.approx(
        pre_margin_unit_rate(FWD, "2017-01-09", POLICY, NETWORK) + 0.5)
    assert [cut.value_arm_entries[0].get("floored_at_cost"),
            kept.value_arm_entries[0].get("floored_at_cost")] == [True, None]


def test_with_no_offer_components_the_arm_keeps_the_old_base_and_names_it():
    """DEFECT: a record with no forward or locked costs either crashes the arm or is priced off a
    base nobody can see. The old `handed rate - GBP 2` stands, labelled as the fallback."""
    out = _level_arm(5.0, floor_known=False)
    entry = out.value_arm_entries[0]
    assert entry["arm_base_source"] == "strike_less_flat_margin"
    assert entry["uplift_gbp_per_mwh"] == pytest.approx(3.0)
