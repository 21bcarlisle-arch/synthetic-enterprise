"""EBSS goes to whoever held the account at 00:00 on the month's 1st (supplier guidance 5.4, 5.8).
One predicate, `held_at_midnight_on_the_first`, answers it for the named household and the
unnamed occupier alike: PROS-2022-0356 joined 12 Nov 2022 and the named path credited it £66.
"""
import simulation.arrears_engine as ae
from company.regulatory.energy_bill_support import ebss_credit_gbp, held_at_midnight_on_the_first
from simulation.dd_collection_book import _paid_on_receipt_by_due_date
from simulation.run_phase2b import occupier_scheme_credit
from tests.tools.test_generate_billing_ledger_pw import _resi_bill


def test_the_predicate_can_be_taken_both_ways():
    """Partition control: held on the 1st, joined on the 12th, joined on the 1st, unknown."""
    assert held_at_midnight_on_the_first("2022-10-03", "2022-11")
    assert not held_at_midnight_on_the_first("2022-11-12", "2022-11")
    assert held_at_midnight_on_the_first("2022-11-01", "2022-11")
    assert held_at_midnight_on_the_first(None, "2022-11")
    assert ebss_credit_gbp("resi", "electricity", "2022-11", "2022-11-12") == 0.0
    assert ebss_credit_gbp("resi", "electricity", "2022-11", "2022-10-03") == 66.0


def test_a_named_joiner_owes_the_whole_bill_for_the_month_they_joined():
    """MUTATION: drop `account_held_from` from the three amount paths and both owe less."""
    bill = _resi_bill("PROS-2022-0356", "2022-11-30", 150.0)
    held, = ae._resolve_bills([dict(bill, account_held_from="2022-10-03")], {}, 42)
    joined, = ae._resolve_bills([dict(bill, account_held_from="2022-11-12")], {}, 42)
    assert held["amount_gbp"] == 150.0 - 66.0 and joined["amount_gbp"] == 150.0
    assert _paid_on_receipt_by_due_date(dict(bill, account_held_from="2022-11-12"), {}, 42) is not None


def test_an_occupier_row_not_on_the_first_opens_no_credit():
    left, opened = {}, {}
    assert occupier_scheme_credit(left, "OCC-1", "2022-11-12", 5.0, "resi", "electricity", opened) == 0.0
    assert not left and not opened
    assert occupier_scheme_credit(left, "OCC-2", "2022-11-01", 5.0, "resi", "electricity", opened) == 5.0
