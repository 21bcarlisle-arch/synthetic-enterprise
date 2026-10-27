"""An unnamed occupier's deemed account carries the EBSS credit, once per month, and only when it
held the account at 00:00 on the 1st (EBSS supplier guidance 5.4 and Annex C, "Occupier Accounts";
`docs/market_research/energy_bills_support_scheme_delivery.md`).

Before this, the world booked the occupier window's whole revenue as `occupier_debt_gbp` through
the crisis winter, and the ledger recorded the occupier as paying the credit: 22 OCC- bills on
4ae8da9b0f (the 2026-10-27 occupier finding).
"""
import simulation.arrears_engine as ae
from simulation.run_phase2b import occupier_scheme_credit
from tests.tools.test_generate_billing_ledger_pw import _resi_bill


def _month(cid, days, owed_per_day, segment="resi", commodity="electricity", month="2023-01"):
    left = {}
    return [occupier_scheme_credit(left, cid, f"{month}-{d:02d}", owed_per_day, segment, commodity)
            for d in days]


def test_every_branch_of_the_occupier_credit_is_taken():
    """Partition control: a month that credits, one that credits nothing, and one the credit
    outruns. A helper that never credits, or always does, fails one of the three."""
    whole = _month("OCC-1", range(1, 32), 5.0)
    void_on_the_first = _month("OCC-2", range(3, 32), 5.0)
    small = _month("OCC-3", range(1, 11), 2.0)
    assert sum(whole) == 67.0 and whole[:13] == [5.0] * 13 and whole[13] == 2.0 and not any(whole[14:])
    assert not any(void_on_the_first)
    assert sum(small) == 20.0  # the credit beyond the debt is the account's, not a gain


def test_no_credit_outside_the_scheme():
    assert not any(_month("OCC-4", range(1, 32), 5.0, commodity="gas"))
    assert not any(_month("OCC-5", range(1, 32), 5.0, segment="sme"))
    assert not any(_month("OCC-6", range(1, 32), 5.0, month="2023-04"))


def test_a_named_payer_is_not_given_the_credit_the_occupier_took():
    """A month split between the occupier window and the named payer: one credit per account per
    month (guidance 5.3). Unmarked, the named payer nets it; marked, the occupier already had it.
    MUTATIONS: drop the `occupier_scheme_credit_gbp` guard in `_resolve_bills` and this fails.
    """
    bill = dict(_resi_bill("OCC-7", "2023-01-31", 150.0), occupier_share=0.5)
    plain, = ae._resolve_bills([bill], {}, 42)
    marked, = ae._resolve_bills([dict(bill, occupier_scheme_credit_gbp=67.0)], {}, 42)
    assert plain["amount_gbp"] == 75.0 - 67.0
    assert marked["amount_gbp"] == 75.0


def test_the_dd_desk_draws_the_bill_the_occupier_took_the_credit_on():
    """`dd_collection_book` draws the same bill `_resolve_bills` draws, so it carries the same guard.
    Half of £100 is £50, which the £67 credit would cover whole: unmarked, there is nothing to draw.
    MUTATIONS: drop the guard in `_paid_on_receipt_by_due_date` and the marked bill owes nothing.
    """
    from simulation.dd_collection_book import _paid_on_receipt_by_due_date
    bill = dict(_resi_bill("OCC-8", "2023-01-31", 100.0), occupier_share=0.5)
    assert _paid_on_receipt_by_due_date(bill, {}, 42) is None
    assert _paid_on_receipt_by_due_date(dict(bill, occupier_scheme_credit_gbp=67.0), {}, 42) is not None


def test_the_account_holds_the_whole_month_credit_not_the_part_the_debt_used():
    """A window of ten days at £2 owes £20, so the debt draws £20 of the £67; the account still
    RECEIVED £67 on the 1st (guidance 5.4), and that is what the ledger and the named payer's guard
    must see. Sized by the debt, the record read £20 and a window with no debt at all read nothing.
    """
    left, opened = {}, {}
    drawn = [occupier_scheme_credit(left, "OCC-9", f"2023-01-{d:02d}", 2.0, "resi", "electricity", opened)
             for d in range(1, 11)]
    assert sum(drawn) == 20.0 and opened == {("OCC-9", "2023-01"): 67.0}
    free, free_opened = {}, {}
    assert occupier_scheme_credit(free, "OCC-10", "2023-01-01", 0.0, "resi", "electricity", free_opened) == 0.0
    assert free_opened == {("OCC-10", "2023-01"): 67.0}
    late, late_opened = {}, {}
    occupier_scheme_credit(late, "OCC-11", "2023-01-03", 5.0, "resi", "electricity", late_opened)
    assert not late_opened  # a home void on the 1st opens nothing


def test_the_guards_see_a_month_credit_the_debt_did_not_draw():
    """MUTATIONS: key either guard on `occupier_scheme_credit_gbp` alone and the named payer is
    given the second credit the account already held."""
    from simulation.dd_collection_book import _paid_on_receipt_by_due_date
    bill = dict(_resi_bill("OCC-12", "2023-01-31", 150.0), occupier_share=0.5,
                occupier_scheme_month_credit_gbp=67.0)
    marked, = ae._resolve_bills([bill], {}, 42)
    assert marked["amount_gbp"] == 75.0
    dd = dict(_resi_bill("OCC-13", "2023-01-31", 100.0), occupier_share=0.5,
              occupier_scheme_month_credit_gbp=67.0)
    assert _paid_on_receipt_by_due_date(dd, {}, 42) is not None
