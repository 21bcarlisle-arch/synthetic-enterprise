"""N20: a household on a level direct debit pays the level amount, not each bill.

The eighth cold read found the page ledger collecting 96.3% of direct debits at exactly the bill
they settle (4669d77ddd book), while the balance book set a level amount for 934 accounts that no
payment record was ever sized by. The bars and the held credit were booked off a balance the cash
never carried. Design: docs/staging/records/SEAT_READING_WHICH_ORGAN_IS_THE_DIRECT_DEBIT_ON_THE_
4669D77DDD_BOOK_2026-11-04.md; knowledge: docs/market_research/payments_and_direct_debit_2026-10-25.md,
"What a level direct debit must be".

Red on the code before it: `level_dd_collections` did not exist, and the ledger paid every DD at
its bill.
"""
import json
from types import SimpleNamespace

import pytest

from saas.ledger import build_ledger
from simulation.dd_balance_book import build_dd_balance_book, dd_spells_from_run
from simulation.dd_level_collection_book import build_dd_level_collection_book, level_dd_collections
from simulation.household_segments import (
    PaymentChannel,
    payment_channel_for_customer,
    pays_a_level_direct_debit,
)
from tests.tools.test_generate_billing_ledger_pw import _resi_bill, _run
from tools.generate_billing_ledger import generate

N_HOUSEHOLDS = 30
# A seasonal electricity bill: winter four times summer, so a level amount and the bill differ.
_SEASON = {1: 120.0, 2: 110.0, 3: 90.0, 4: 70.0, 5: 50.0, 6: 35.0, 7: 30.0, 8: 32.0, 9: 45.0,
           10: 70.0, 11: 95.0, 12: 115.0}


@pytest.fixture(scope="module")
def book(tmp_path_factory):
    bills, opening = [], {}
    for i in range(N_HOUSEHOLDS):
        cid = f"N20-{i:02d}"
        opening[cid] = round(sum(_SEASON.values()) / 12, 2)
        bills += [_resi_bill(cid, f"{y}-{m:02d}-28", _SEASON[m]) for y in (2018, 2019)
                  for m in range(1, 13)]
    run = _run(bills)
    balance = build_dd_balance_book(bills, opening, set(), dd_spells=dd_spells_from_run(run))
    schedule = level_dd_collections(build_dd_level_collection_book(balance),
                                    pays_a_level_direct_debit)
    run["level_dd_collections"] = schedule
    scratch = tmp_path_factory.mktemp("n20")
    (scratch / "run.json").write_text(json.dumps(run))
    ledger = generate(scratch / "run.json", scratch / "ledger.json")["customers"]
    return SimpleNamespace(bills=bills, balance=balance, schedule=schedule, ledger=ledger)


def _dd_paid(ledger, cid):
    """{period_end month: (amount paid, invoice total)} over the account's successful DDs."""
    c = ledger[cid]
    inv = {i["invoice_number"]: i for i in c["invoices"]}
    return {inv[p["invoice_number"]]["period_end"][:7]: (p["amount_gbp"],
                                                        inv[p["invoice_number"]]["total_amount_gbp"])
            for p in c.get("payments", ())
            if p.get("method") == "direct_debit" and p.get("outcome") == "success"}


def _dd_accounts(book):
    return [cid for cid in book.balance.trajectories
            if payment_channel_for_customer(cid, "electricity") is PaymentChannel.DIRECT_DEBIT]


def test_both_kinds_of_direct_debit_are_in_the_book(book):
    """The partition first: a flag that put everyone on a level amount, or nobody, fails here."""
    dd = _dd_accounts(book)
    level = [cid for cid in dd if cid in book.schedule]
    assert level and len(level) < len(dd), (len(level), len(dd))


def test_a_level_account_pays_the_level_amount_every_month_and_builds_credit_in_summer(book):
    level = [cid for cid in _dd_accounts(book) if cid in book.schedule]
    checked = 0
    for cid in level:
        set_by_month = {p.month: p.collected_gbp for p in book.balance.trajectories[cid]}
        paid = _dd_paid(book.ledger, cid)
        for month, (amount, _bill) in paid.items():
            assert amount == pytest.approx(set_by_month[month], abs=0.005), (cid, month, amount)
            checked += 1
        # The balance the cash now carries: what was collected less what was billed.
        running, in_credit_in_summer = 0.0, False
        for month in sorted(paid):
            running += paid[month][0] - paid[month][1]
            in_credit_in_summer |= month[5:] in ("06", "07", "08", "09") and running > 0
        if len(paid) >= 12:
            assert in_credit_in_summer, (cid, sorted(paid.items())[:9])
    assert checked, "no level-DD account had a successful collection"


def test_a_variable_account_still_pays_its_bill(book):
    variable = [cid for cid in _dd_accounts(book) if cid not in book.schedule]
    paid = [(cid, m, a, b) for cid in variable for m, (a, b) in _dd_paid(book.ledger, cid).items()]
    assert paid
    assert all(a == pytest.approx(b, abs=0.005) for _, _, a, b in paid), [
        r for r in paid if abs(r[2] - r[3]) > 0.005][:3]


def test_the_books_collect_the_same_level_amounts_as_the_page_ledger(book):
    """Both cash records read one schedule: with no provision, the books' cash per level bill is
    the page ledger's payment, on the same day."""
    model = SimpleNamespace(CREDIT_RISK_BY_CUSTOMER={}, DEFAULT_CREDIT_RISK="LOW",
                            bad_debt_provision_gbp=lambda risk, total: 0.0,
                            expected_payment_date=lambda period_end, risk: period_end)
    cash = {(e["customer_id"], e["bill_period_end"][:7]): (e["amount_gbp"], e["timestamp"])
            for e in build_ledger([], book.bills, model, level_dd_collections=book.schedule)
            if e["event_type"] == "payment_received_event"}
    agreed = 0
    for cid in book.schedule:
        c = book.ledger[cid]
        inv = {i["invoice_number"]: i for i in c["invoices"]}
        for p in c.get("payments", ()):
            if p.get("level_dd") and p.get("outcome") == "success":
                month = inv[p["invoice_number"]]["period_end"][:7]
                assert cash[(cid, month)][0] == pytest.approx(p["amount_gbp"], abs=0.005)
                assert cash[(cid, month)][1] == p["payment_date"]
                agreed += 1
    assert agreed
