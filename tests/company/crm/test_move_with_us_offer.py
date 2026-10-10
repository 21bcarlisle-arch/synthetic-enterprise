"""The move-with-us decision: offered on the company's own margin belief, never less to a known-vulnerable
household than to its twin."""
from __future__ import annotations

import datetime as dt

from company.crm.move_with_us_offer import (
    NO_MARGIN,
    NO_POLICY,
    NOT_FIXED,
    decide_move_with_us,
)
from interface.contracts.move_out_notice_seam import MoveOutNotice

_NOTICE = MoveOutNotice("C1", dt.date(2023, 3, 16), dt.date(2023, 3, 14))


def _ask(**kw):
    args = dict(offers_on=True, tariff_type="fixed", unit_rate_per_mwh=250.0,
                cost_per_mwh=200.0, annual_kwh=3000.0)
    args.update(kw)
    return decide_move_with_us(_NOTICE, **args)


def test_the_offer_branch_can_be_taken_and_carries_the_tariff_in_force():
    """Defect: a rule that never offers (every refusal test would still pass), or an offer at a price
    other than the one the household pays."""
    offer, reason = _ask()
    assert offer is not None and reason is None
    assert offer.carried_unit_rate == 250.0 and offer.exit_fee_waived
    assert offer.move_out_date == "2023-03-16"


def test_no_offer_where_the_company_expects_to_lose_money_carrying_the_household():
    """Defect: offering on a carried tariff the company's own estimate prices at or below cost."""
    assert _ask(unit_rate_per_mwh=200.0) == (None, NO_MARGIN)


def test_no_offer_without_the_policy_or_off_a_fixed_tariff():
    """Defect: an offer made while the policy is off (the run would not be inert), or a default tariff
    'carried'."""
    assert _ask(offers_on=False) == (None, NO_POLICY)
    assert _ask(tariff_type="svt") == (None, NOT_FIXED)


def test_a_known_vulnerable_household_is_never_offered_less_than_its_twin():
    """Defect: vulnerability narrowing the offer. Swept over margins either side of zero, both arms."""
    for rate in (150.0, 200.0, 200.01, 250.0):
        plain, _ = _ask(unit_rate_per_mwh=rate)
        vuln, _ = _ask(unit_rate_per_mwh=rate, vulnerable=True)
        assert (vuln is not None) >= (plain is not None)
        if plain is not None:
            assert vuln.carried_unit_rate <= plain.carried_unit_rate
