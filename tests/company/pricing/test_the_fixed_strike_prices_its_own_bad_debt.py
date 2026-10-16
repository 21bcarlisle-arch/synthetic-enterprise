"""A fixed strike carries the bad-debt charge the company has learned off its own ledger, and so does
its cost floor (B12).

The defect each test names: the strike priced no bad debt, so every fixed term lost its charge off a
margin priced as if there were none, 2.49 points of unit revenue on the median 2016-19 electricity
term (`docs/staging/records/PREREG_B12_THE_PREMIUM_LOOKBACK_READS_FIXED_TERMS_ONLY_2026-10-15.md`,
grade of D). The allowance is `default_belief_rate`, the company's own charge per GBP billed, never the
settled lines' `bad_debt_gbp`, which is the world's incidence. Knowledge: the renewal-decision page,
"What a fixed strike carries for levies and bad debt".
"""
from __future__ import annotations

import pytest

from company.interfaces.renewal_decision_inputs import RenewalDecisionInputs
from company.interfaces.renewal_rate_chain import decide_renewal
from company.pricing.renewal_desk import pre_margin_unit_rate

FWD, POLICY, NETWORK, STRUCK = 45.0, 26.0, 43.0, 139.15
FLOOR = pre_margin_unit_rate(FWD, "2017-01-09", POLICY, NETWORK)
SHARE = 0.02


def _rate(tariff_type="fixed", belief=None, book=(), struck=STRUCK):
    return decide_renewal(RenewalDecisionInputs(
        customer_id="C1", billing_account="C1", commodity="electricity", term_start="2017-01-09",
        tariff_type=tariff_type, term_index=1, struck_unit_rate_per_mwh=struck,
        portfolio_margin_rates=list(book), prior_term_margin=None, prior_term_revenue=0.0,
        is_domestic=False, settled_records=[], customer={"metering": "NHH", "smart_meter": False},
        company_forward_per_mwh=FWD, locked_policy_cost_per_mwh=POLICY,
        locked_network_cost_per_mwh=NETWORK, default_belief_rate=belief))


def test_a_fixed_strike_carries_its_believed_loss_and_other_products_do_not():
    """DEFECT: the strike priced no bad debt. The control: a flat product is not the fixed strike,
    and a belief the company does not hold (`None`) adds nothing rather than a guessed zero-or-two."""
    assert _rate().unit_rate_gbp_per_mwh == pytest.approx(STRUCK)
    priced = _rate(belief=SHARE)
    assert priced.unit_rate_gbp_per_mwh == pytest.approx(STRUCK * (1 + SHARE))
    assert priced.bad_debt_allowance_gbp_per_mwh == pytest.approx(STRUCK * SHARE)
    assert _rate("svt", belief=SHARE).unit_rate_gbp_per_mwh == pytest.approx(STRUCK)


def test_a_discount_stops_at_the_floor_with_the_allowance_on_it():
    """DEFECT: the allowance on the rate but not the floor lets writer 1 discount it straight off
    again. A book far above target takes the full cut, so the rate lands on the floor itself."""
    far_above, struck = [0.30] * 5, FLOOR + 1.0  # a -5% cut would take it 4.7 under the floor
    without = _rate(book=far_above, struck=struck).unit_rate_gbp_per_mwh
    assert without == pytest.approx(FLOOR)  # the discount can reach the floor: the branch is live
    with_it = _rate(book=far_above, struck=struck, belief=SHARE).unit_rate_gbp_per_mwh
    assert with_it == pytest.approx(FLOOR + struck * SHARE)
