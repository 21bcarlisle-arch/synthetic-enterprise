"""The MSC the world charges on a win reaches the company's books, and only as a levy.

Each test names its own defect.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.finance.double_entry import build_journal, income_statement
from company.interfaces.growth_desk import (
    book_acquisition_spend,
    book_market_stabilisation_charge,
)
from saas.ledger import derive_pnl
from simulation.market_stabilisation_charge import charge_gbp


def _peak_win() -> dict:
    charge = charge_gbp(dt.date(2023, 1, 11), "electricity", 2_900)
    return book_market_stabilisation_charge(
        billing_account="acct_9", event_date="2023-01-11",
        fuel="electricity", amount=charge["amount_gbp"])


def test_the_charge_lowers_operating_margin_by_its_own_amount_and_is_reported_apart():
    """Defect: the event is booked and then counted nowhere, or folded into acquisition spend."""
    spend = book_acquisition_spend(billing_account="acct_9", event_date="2023-01-11",
                                   amount_gbp=20.0, won=True, segment="resi")
    without = derive_pnl([spend])
    with_msc = derive_pnl([spend, _peak_win()])
    assert with_msc["market_stabilisation_charge_gbp"] == pytest.approx(214.14)
    assert with_msc["acquisition_spend_gbp"] == without["acquisition_spend_gbp"] == 20.0
    assert (without["operating_net_margin_gbp"] - with_msc["operating_net_margin_gbp"]
            == pytest.approx(214.14))


def test_the_journal_posts_it_to_acquisition_cost_and_balances():
    """Defect: an unmapped event type drops out of the journal, so the books and the P&L disagree."""
    journal = build_journal([_peak_win()])
    assert len(journal) == 1 and journal[0]["debit_account"] == "6300"
    assert income_statement(journal)["acquisition_spend_gbp"] == pytest.approx(214.14)


def test_a_charge_on_each_fuel_of_one_win_is_two_events_not_one():
    """Defect: the second fuel's charge overwrites the first on a shared transaction id."""
    elec = _peak_win()
    gas = book_market_stabilisation_charge(billing_account="acct_9", event_date="2023-01-11",
                                           fuel="gas", amount=280.44)
    assert elec["transaction_id"] != gas["transaction_id"]
