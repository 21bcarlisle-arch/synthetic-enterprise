"""The D48 SPAR sweep's counterfactual (tools/d48_spar_blend_counterfactual.py).

Defects named: a SPAR-0 control that is not today's book (every table column would carry a shift no
blend made), and a blend that never moves a hold-route bill (every SPAR would equal the control and
the E1 column would read "unchanged" for the wrong reason).
"""
from datetime import date

import pytest

from company.billing.unread_month_estimate import profile_weight
from tools.d48_spar_blend_counterfactual import counterfactual_kwh


def _bill(end, start, basis, kwh):
    return {"period_start": start, "period_end": end, "billing_basis": basis,
            "total_consumption_kwh": kwh, "commodity": "electricity", "profile_class": 1,
            "account_held_from": "2016-01-01"}


# One actual read after a month, then estimates on the registry figure (the hold route), at
# twice what the meter is doing.
BILLS = [
    _bill("2016-01-31", "2016-01-01", "actual", 300.0),
    _bill("2016-02-29", "2016-02-01", "estimated", 600.0),
    _bill("2016-03-31", "2016-03-01", "estimated", 600.0),
    _bill("2016-04-30", "2016-04-01", "actual", 300.0),
    _bill("2016-05-31", "2016-05-01", "estimated", 600.0),
]
TRUE = {b["period_end"]: 300.0 for b in BILLS}


def test_the_sweep_can_move_a_bill_and_its_control_moves_none():
    control, _ = counterfactual_kwh(BILLS, TRUE, 0.0)
    assert control == {}
    low, seen = counterfactual_kwh(BILLS, TRUE, 1.0)
    high, _ = counterfactual_kwh(BILLS, TRUE, float("inf"))
    assert set(low) == {"2016-02-29", "2016-03-31", "2016-05-31"} and seen["hold_bills"] == 3
    # The blend pulls each hold estimate toward the meter, and further as SPAR grows.
    assert all(high[k] < low[k] < 600.0 for k in low)


def test_a_book_built_with_the_blend_is_read_back_to_the_hold_and_to_itself():
    """Defect: on a book built with the switch on, the figure read back off its first hold-route
    bill already carries the earlier advances, so `--ends` would blend them a second time and
    publish a range no policy produced. Un-blended at the book's SPAR, the hold is recovered and
    the book's own SPAR is the book."""
    built, _ = counterfactual_kwh(BILLS, TRUE, 0.5)
    book = [dict(b, total_consumption_kwh=built.get(b["period_end"], b["total_consumption_kwh"]))
            for b in BILLS]
    assert built and all(book[i]["total_consumption_kwh"] != BILLS[i]["total_consumption_kwh"]
                         for i in (1, 2, 4))
    hold, seen = counterfactual_kwh(book, TRUE, 0.0, book_spar=0.5)
    assert seen["hold_bills"] == 3
    # The hold bills the opening figure read off the first hold-route bill, on the profile shape.
    eac0 = 600.0 / profile_weight("electricity", date(2016, 2, 1), date(2016, 2, 29))
    assert hold == {b["period_end"]: pytest.approx(eac0 * profile_weight(
        "electricity", date.fromisoformat(b["period_start"]), date.fromisoformat(b["period_end"])))
        for b in BILLS if b["period_end"] in built}
    assert counterfactual_kwh(book, TRUE, 0.5, book_spar=0.5)[0] == {}
    other, _ = counterfactual_kwh(book, TRUE, 3.0, book_spar=0.5)
    direct, _ = counterfactual_kwh(BILLS, TRUE, 3.0)
    assert other == {k: pytest.approx(v) for k, v in direct.items()}
