"""The cure reader reads a direct debit bill due on a non-working day as due on the next Bacs day,
as the desk does (`company.billing.collections_journey.last_day_to_pay`).

Defect each test names: read from the due date alone, the reader held the desk's Sunday cure of
ACC-SYN-2016-015 (15 Apr 2018) over a gas bill due Saturday 14 Apr and collected, on time, on
Monday 16 Apr (LEVEL_DD_AREA_MAP_2026-11-11 s.9.4)."""

from tools.level_dd_cure_reader import leg_position

SUNDAY = "2018-04-15"


def _leg(method: str, due: str = "2018-04-14"):
    entries = [{"date": "2018-03-31", "type": "invoice_raised", "amount_gbp": 71.37,
                "running_balance_gbp": 71.37}]
    cust = {"invoices": [{"invoice_number": 7, "issue_date": "2018-03-31", "due_date": due,
                          "total_amount_gbp": 71.37}],
            "payments": [{"invoice_number": 7, "payment_date": "2018-04-16", "amount_gbp": 71.37,
                          "method": method, "outcome": "success"}]}
    return leg_position(entries, cust, SUNDAY)


def test_a_bill_unpaid_past_its_due_date_is_still_held():
    # The hold branch must stay reachable: a pay-on-receipt bill does not roll (no source says it
    # does, collections_journey.last_day_to_pay), and a DD bill due on a weekday does not either.
    assert _leg("standard_credit")[0] > 71.36
    assert _leg("direct_debit", due="2018-04-13")[0] > 71.36


def test_a_dd_bill_due_saturday_is_not_owed_on_sunday():
    assert abs(_leg("direct_debit")[0]) < 0.005
