"""A household that stays pays at most its default, so the value arm never prices a fix above it.

A domestic fix cannot auto-renew (SLC 22C.2/22C.5); doing nothing lands on the default (22C.7/
22C.8). A stayer offered more than the default refuses and is billed the default, which is the
world's own decline rule (`customer_events.renewal_outcome`). The value scorer credited the
offer instead, and on the 2025 probes it priced ~90% of renewals above the default.
"""
from __future__ import annotations

import company.pricing.value_based_renewal as vbr

_KW = dict(customer_id="C1", arm=vbr.VALUE_BASED, current_rate_gbp_per_mwh=160.0,
           base_rate_gbp_per_mwh=150.0, eac_kwh=3_000.0, tenure_years=3.0,
           cost_to_serve_gbp_per_year=60.0, renewal_year=2021,
           published_default_rate_gbp_per_mwh=180.0)


def test_without_the_rule_the_arm_can_and_does_price_above_the_default():
    """The control over the rare branch: if the arm never priced above the default anyway, the
    test below would pass with the rule doing nothing."""
    assert vbr.decide_margin(**_KW).offered_rate_gbp_per_mwh > 180.0


def test_knowing_a_stayer_pays_the_default_the_arm_never_offers_above_it():
    on = vbr.decide_margin(**_KW, stayer_default_rate_gbp_per_mwh=180.0)
    assert on.offered_rate_gbp_per_mwh <= 180.0 + 1e-6


def test_a_stayer_above_the_default_is_scored_at_the_default_and_its_churn_at_the_offer():
    """An offer above the default earns what the default earns, with the churn of the offer: never
    more than the default itself."""
    level_kw = {**_KW, "arm": vbr.FLAT_AT_LEVEL}
    at_default = vbr.decide_margin(**level_kw, flat_level_gbp_per_mwh=30.0,
                                   stayer_default_rate_gbp_per_mwh=180.0)
    above = vbr.decide_margin(**level_kw, flat_level_gbp_per_mwh=60.0,
                              stayer_default_rate_gbp_per_mwh=180.0)
    assert above.p_retain < at_default.p_retain
    assert above.expected_value_gbp < at_default.expected_value_gbp


def _chain_rate_2017(own_default_inc_vat):
    """A 2017 domestic fixed renewal through the whole rate chain: before the cap, so the only
    default the company can know is its own default tariff."""
    # THE SEAM DOOR, which is what the run calls: a door that forwards named arguments drops a
    # new one silently unless the control goes through it.
    from company.interfaces.renewal_rate_chain import decide_renewal_rate
    from company.policy.decision_policy import VALUE_ARM_CAPPED_POLICY, policy_scope
    settled = [{"customer_id": "C0001", "commodity": "electricity",
                "settlement_date": f"2016-{m:02d}-15", "term_start": "2016-01-01",
                "consumption_kwh": 250.0, "revenue_gbp": 30.0, "net_margin_gbp": 1.0,
                "margin_gbp": 5.0, "settlement_periods_folded": 48} for m in range(1, 13)]
    with policy_scope(VALUE_ARM_CAPPED_POLICY):
        return decide_renewal_rate(
            customer_id="C0001", billing_account="C0001", commodity="electricity",
            term_start="2017-01-01", tariff_type="fixed", term_index=1,
            struck_unit_rate_gbp_per_mwh=110.0, portfolio_margin_rates=[],
            prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0, is_domestic=True,
            settled_records=settled, customer={"metering": "NHH", "smart_meter": False},
            own_default_tariff_inc_vat_gbp_per_mwh=own_default_inc_vat,
        ).unit_rate_gbp_per_mwh


def test_before_the_cap_the_companys_own_default_is_what_a_stayer_pays():
    """Before 2019 there is no published ceiling, but a household that refuses still rolls onto
    the company's default tariff. Without that price the switch cannot act (the control); with
    it the chain never offers above it."""
    own_inc_vat = 140.0
    own_ex_vat = own_inc_vat / 1.05
    assert _chain_rate_2017(None) > own_ex_vat
    assert _chain_rate_2017(own_inc_vat) <= own_ex_vat + 0.5
