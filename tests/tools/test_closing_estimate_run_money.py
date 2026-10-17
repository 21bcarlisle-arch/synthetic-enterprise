"""The closing-run money probe: which runs it prices, and the sign it gives them."""

import pytest

from tools.closing_estimate_run_money import closing_accounts, summarise


def _bill(cid, end, basis, billed, true=None, commodity="electricity"):
    bill = {"customer_id": cid, "period_end": end, "commodity": commodity, "billing_basis": basis,
            "total_amount_gbp": billed, "total_consumption_kwh": billed * 4,
            "payment_channel": "direct_debit"}
    if basis == "estimated":
        bill.update(true_total_amount_gbp=true, true_consumption_kwh=true * 4)
    return bill


def _read(bill, forced=False):
    return {"customer_id": bill["customer_id"], "period_end": bill["period_end"],
            "meter_type": "traditional", "forced_catch_up": forced}


def _run_output(pairs, churned=("C1", "C2", "C3")):
    return {"bills": [b for b, _ in pairs], "meter_read_log": [r for _, r in pairs],
            "churned_billing_accounts": list(churned), "home_move_outs": []}


def _book():
    c1 = [_bill("C1", "2020-01-31", "actual", 50), _bill("C1", "2020-02-29", "estimated", 40, 55),
          _bill("C1", "2020-03-31", "estimated", 30, 32)]
    c2 = [_bill("C2", "2020-01-31", "estimated", 60, 45), _bill("C2", "2020-02-29", "actual", 70)]
    stayer = [_bill("C9", "2020-01-31", "estimated", 10, 99)]
    pairs = [(b, _read(b)) for b in c1 + stayer]
    pairs += [(c2[0], _read(c2[0])), (c2[1], _read(c2[1], forced=True))]
    return _run_output(pairs)


def test_an_estimated_last_bill_leaves_its_whole_trailing_run_open_and_a_stayer_is_never_priced():
    """Defect named: the open run omits its own last bill, stops at the wrong place, or a stayer leaks in."""
    rows = {r["customer_id"]: r for r in closing_accounts(_book())}
    assert set(rows) == {"C1", "C2"}
    assert rows["C1"]["outcome"] == "open" and rows["C1"]["run_bills"] == 2
    assert rows["C1"]["gbp"] == pytest.approx(17.0)


def test_an_actual_last_bill_prices_the_run_before_it_and_keeps_the_overcharge_sign():
    """Defect named: the settling bill is counted in its own run, or an overcharge is signed as recovered."""
    rows = {r["customer_id"]: r for r in closing_accounts(_book())}
    assert rows["C2"]["outcome"] == "settled" and rows["C2"]["forced"]
    assert rows["C2"]["run_bills"] == 1 and rows["C2"]["gbp"] == pytest.approx(-15.0)


def test_the_summary_can_reach_every_outcome_and_direction():
    """The partition first: a summary that only ever filed one cell would pass the two tests above."""
    table = summarise(closing_accounts(_book()))["by_outcome_fuel_direction"]
    assert table["open"]["electricity"]["undercharge"]["accounts"] == 1
    assert table["settled_forced"]["electricity"]["overcharge"]["accounts"] == 1


def test_a_gas_leg_of_a_departed_household_is_a_closing_supply_point():
    """Defect named: the closing set is the household roster, so every gas leg reads as a stayer."""
    gas = _bill("C1g", "2020-03-31", "estimated", 20, 26, commodity="gas")
    rows = closing_accounts(_run_output([(gas, _read(gas))], churned=("C1",)))
    assert [r["customer_id"] for r in rows] == ["C1g"]


def test_a_read_log_out_of_step_with_the_bills_is_refused_by_name():
    book = _book()
    book["meter_read_log"] = book["meter_read_log"][::-1]
    with pytest.raises(ValueError, match="out of step"):
        closing_accounts(book)
