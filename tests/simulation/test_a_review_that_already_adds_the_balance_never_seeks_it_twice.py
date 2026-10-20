"""`own_forecast_plus_balance` adds the debit balance to the debit it sets; seeking it again at the
same review would recover it twice (`SEAT_FINDING_D48_A_THIRD_OF_DD_ACCOUNTS_..._2026-10-14.md`,
"Guard it before anyone does"). The defect: a book that steps the debit up twice, on the rule that
already carries the balance."""
from __future__ import annotations

import pytest

import company.billing.dd_review as dd_review
from simulation.dd_balance_book import build_dd_balance_book
from tests.simulation.test_dd_back_billing_at_charge_recovery_actions import OPENING, SHORT

RULE = "own_forecast_plus_balance"


def test_the_seek_branch_is_reachable_and_the_forecast_rule_never_takes_it(monkeypatch):
    # The company's switch on, so a default left to it would seek.
    monkeypatch.setattr(dd_review, "REVIEW_SEEKS_BALANCE", True)

    # The branch the guard keeps the forecast rule out of can be taken: the ordinary rule seeks.
    plain = build_dd_balance_book(SHORT, OPENING, set())
    assert plain.seek_balance_at_review and plain.review_step_ups

    # Left to the switch, the rule that already adds the balance does not step up as well.
    forecast = build_dd_balance_book(SHORT, OPENING, set(), review_rule=RULE)
    assert forecast.seek_balance_at_review is False
    assert forecast.review_step_ups == []

    # Asked for explicitly, the pair is refused, and the refusal says why.
    with pytest.raises(ValueError, match="twice"):
        build_dd_balance_book(SHORT, OPENING, set(), seek_balance_at_review=True, review_rule=RULE)
