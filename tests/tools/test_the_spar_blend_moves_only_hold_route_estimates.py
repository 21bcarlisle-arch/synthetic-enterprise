"""The D48 SPAR sweep's counterfactual (tools/d48_spar_blend_counterfactual.py).

Defects named: a SPAR-0 control that is not today's book (every table column would carry a shift no
blend made), and a blend that never moves a hold-route bill (every SPAR would equal the control and
the E1 column would read "unchanged" for the wrong reason).
"""
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
