"""The cure reader grades the desk on the account the desk works: one fuel's credit meets the
other fuel's debt, on level and off-level legs alike (LEVEL_DD_AREA_MAP_2026-11-11 s.7 cause A).

Defect each test names: a reader that clamps a level leg's credit at zero before summing holds a
cure the billing account does not owe (35 of 71 on the 87e00e1458 book)."""

from tools.level_dd_cure_reader import account_owed, leg_position


def _leg(balance, level, requested=0.0, received=0.0, d="2019-04-01"):
    entries = [{"date": "2019-03-01", "type": "invoice_raised", "amount_gbp": requested,
                "running_balance_gbp": requested},
               {"date": "2019-03-18", "type": "payment_received", "amount_gbp": -received,
                "running_balance_gbp": balance}]
    cust = {"invoices": [{"invoice_number": 1, "issue_date": "2019-03-01", "due_date": "2019-03-15",
                          "total_amount_gbp": requested}],
            "payments": [{"invoice_number": 1, "payment_date": "2019-03-18", "amount_gbp": requested,
                          "outcome": "success", **({"level_dd": True} if level else {})}]}
    return leg_position(entries, cust, d)


def test_the_reader_can_hold_a_cure_at_all():
    # A guard that refuses everything passes every other test here: the hold branch must be reachable.
    assert account_owed([(30.0, True), (0.0, True)]) > 0.005
    assert account_owed([(30.0, False), (-10.0, False)]) > 0.005


def test_a_level_legs_credit_meets_its_siblings_debt():
    parts = [(-100.0, True), (30.0, True)]
    assert account_owed(parts) <= 0.005
    assert account_owed(parts, legacy=True) > 0.005  # the scratch rule's misread, kept visible


def test_a_level_leg_owes_no_more_than_its_schedule_shortfall():
    # Debit balance 200 under level DD, schedule fully met: nothing is past due on the schedule.
    x, level = _leg(balance=200.0, level=True, requested=50.0, received=50.0)
    assert level and abs(x) < 0.005
    # Off level, the same balance is owed.
    x, level = _leg(balance=200.0, level=False, requested=50.0, received=50.0)
    assert not level and x > 0


def test_a_level_leg_in_credit_carries_its_credit():
    x, level = _leg(balance=-40.0, level=True, requested=50.0, received=90.0)
    assert level and x < -39.99
