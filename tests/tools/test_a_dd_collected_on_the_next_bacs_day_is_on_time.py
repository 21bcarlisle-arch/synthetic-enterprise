"""A direct debit due on a weekend or bank holiday is collected on the next Bacs processing day, and
that collection is on time (`payments_and_direct_debit_2026-10-25.md`, "The day a collection lands").

C1's bill fell due on Sunday 8 May 2016 and its DD landed on Monday 9 May (75f66f6521 rolled it).
The household record counted it "missed DD without a return": all 194 of
INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE's breaches on the e50e7b8f68 book were this case.
Red on b97dcf8e15: the first test reads 0 of 1 paid, 1 missed."""
from tools.generate_explore_cast import payment_record

BILL = [{"invoice_number": 1, "due_date": "2016-05-08", "document_type": "bill"}]  # a Sunday


def _dd(on, kind="payment_received", method="direct_debit"):
    return [{"type": kind, "invoice_number": 1, "date": on, "method": method}]


def test_c1s_sunday_dd_collected_on_monday_is_paid_not_missed():
    rec = payment_record(_dd("2016-05-09"), BILL, "2016-06-30")
    assert (rec["due"], rec["payments"], rec["missed"], rec["missed_dd"]) == (1, 1, 0, 0), rec


def test_a_dd_two_working_days_late_still_reads_late():
    """The control: the roll is to the FIRST processing day, not any later one. Wed 11 May is two
    working days after the due date's roll to Monday."""
    rec = payment_record(_dd("2016-05-11"), BILL, "2016-06-30")
    assert (rec["payments"], rec["missed"], rec["missed_dd"]) == (0, 1, 1), rec


def test_the_rolled_bill_is_not_missable_until_the_day_after_the_collection_day():
    """Both sides of the partition: on Monday the bill is not yet due for counting; on Tuesday it is
    counted, paid if Monday's collection landed and missed if it was returned. (A bill with no ledger
    row has no method on record and keeps its own due date.)"""
    returned = _dd("2016-05-09", kind="payment_failed")
    assert payment_record(returned, BILL, "2016-05-09")["due"] == 0
    assert payment_record(returned, BILL, "2016-05-10")["missed_dd"] == 1
    assert payment_record(_dd("2016-05-09"), BILL, "2016-05-10")["payments"] == 1


def test_a_bank_holiday_rolls_too_and_pay_on_receipt_does_not():
    """Mon 2 May 2016 was the Early May bank holiday, so a DD due then lands Tue 3 May on time. A
    pay-on-receipt payment keeps its due date: no source read says it rolls (the page's GAP)."""
    bh = [{"invoice_number": 1, "due_date": "2016-05-02", "document_type": "bill"}]
    assert payment_record(_dd("2016-05-03"), bh, "2016-06-30")["missed"] == 0
    assert payment_record(_dd("2016-05-09", method="standard_credit"), BILL, "2016-06-30")["missed"] == 1
