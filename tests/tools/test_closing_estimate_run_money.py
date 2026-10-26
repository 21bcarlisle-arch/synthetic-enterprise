"""The closing-run money probe: which runs it prices, and the sign it gives them."""

import pytest

from tools.closing_estimate_run_money import (
    closing_accounts,
    cos_read_settlement,
    summarise,
    what_closure_shows,
)


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


def _month(cid, i, basis, billed, true=None):
    year, month = 2019 + (i // 12), i % 12 + 1
    bill = _bill(cid, f"{year}-{month:02d}-28", basis, billed, true)
    bill["period_start"] = f"{year}-{month:02d}-01"
    return bill


def test_every_disposition_of_open_money_is_reachable():
    """The partition first: a pricing that sent all money to one disposition passes each leg below."""
    shown = [what_closure_shows([_month("A", i, "estimated", 10, 20) for i in range(24)], 24),
             what_closure_shows([_month("B", 0, "estimated", 10, 20)], 1)["new_demand_gbp"],
             what_closure_shows([_month("C", 0, "estimated", 10, 20)], 1, [10.0], 50.0)]
    assert shown[0]["added_bar_gbp"] > 0 and shown[1] > 0 and shown[2]["absorbed_gbp"] > 0


def test_an_undercharge_older_than_twelve_months_is_barred_and_the_rest_is_asked_for():
    """Defect named: the bar is skipped, or it bars the energy inside the window as well."""
    bills = [_month("A", i, "estimated", 10, 20) for i in range(24)]
    shown = what_closure_shows(bills, 24)
    assert shown["gbp"] == pytest.approx(240.0)
    assert shown["added_bar_gbp"] == pytest.approx(120.0, abs=2.0)
    assert shown["new_demand_gbp"] == pytest.approx(shown["gbp"] - shown["added_bar_gbp"])


def test_a_direct_debit_credit_absorbs_an_undercharge_and_only_the_excess_is_a_new_demand():
    """Defect named: the balance is ignored, so a smaller refund is reported as a bill after leaving."""
    bills = [_month("C", 0, "estimated", 10, 70)]
    shown = what_closure_shows(bills, 1, [10.0], 50.0)
    assert shown["absorbed_gbp"] == pytest.approx(50.0)
    assert shown["new_demand_gbp"] == pytest.approx(10.0)


def test_an_overcharge_on_a_settled_account_is_owed_in_full_and_never_barred():
    """Defect named: 21BA is applied to a credit owed, which it does not bar."""
    bills = [_month("D", i, "estimated", 20, 10) for i in range(24)]
    shown = what_closure_shows(bills, 24)
    assert shown["gbp"] == pytest.approx(-240.0)
    assert shown["added_bar_gbp"] == 0 and shown["new_demand_gbp"] == 0
    assert shown["absorbed_gbp"] == pytest.approx(-240.0)


def _run_of_estimates(cid, n, channel="direct_debit"):
    bills = [_bill(cid, f"{2020 + i // 12}-{i % 12 + 1:02d}-28", "estimated", 10, 20) for i in range(n)]
    for i, b in enumerate(bills):
        b.update(consecutive_estimated_count=i + 1, payment_channel=channel)
    return bills


def _year_dates(bills):
    from tools.closing_estimate_run_money import duty_year_dates
    return duty_year_dates(bills)


def test_a_run_past_the_licence_year_splits_at_its_twelfth_bill_and_a_shorter_one_does_not():
    """The partition first: a split that never found the year, or found it everywhere, passes either
    leg alone. Defect named: the money up to the year is not bills 1-12."""
    from tools.closing_estimate_run_money import year_split
    long_run, short_run = _run_of_estimates("L", 15), _run_of_estimates("S", 11)
    dates = _year_dates(long_run + short_run)
    assert year_split(long_run, dates) == (11, pytest.approx(120.0))
    assert year_split(short_run, dates) == (None, 0.0)


def test_a_prepayment_run_past_the_year_is_outside_the_duty_and_never_splits():
    """Defect named: the split counts a run SLC 21B.4 does not apply to."""
    from tools.closing_estimate_run_money import year_split
    run = _run_of_estimates("P", 15, channel="prepayment")
    assert year_split(run, _year_dates(run)) == (None, 0.0)


def test_the_must_read_grade_counts_gas_attempts_only_and_the_ceiling_leaves_the_tail_after_its_read():
    """Defect named: an attempt counted on electricity or a smart meter, an offset of one, or a ceiling
    that clears the whole open run rather than the 24 estimates before its read."""
    from tools.closing_estimate_run_money import must_read_reach

    pairs = []
    for cid, commodity, meter in (("C1g", "gas", "traditional"), ("C1", "electricity", "traditional"),
                                  ("C2g", "gas", "smart")):
        for i in range(30):
            bill = _month(cid, i, "estimated", 10.0, 11.0)
            bill["commodity"] = commodity
            read = _read(bill)
            read["meter_type"] = meter
            pairs.append((bill, read))
    view = must_read_reach(_run_output(pairs, churned=("C1", "C2")))
    assert view["register_attempts_by_fuel"] == {"gas": 6, "electricity": 0}
    (row,) = view["accounts"]
    assert row["customer_id"] == "C1g" and row["ceiling_reads"] == 1
    assert row["first_attempt"] == pairs[24][0]["period_end"]
    assert row["open_gbp"] == pytest.approx(30.0)
    assert row["open_gbp_after_ceiling"] == pytest.approx(5.0)


def test_the_grade_places_the_instructed_visit_where_the_billing_run_does():
    """Defect named: the grade's visits one bill early or late against `build_monthly_bills`
    (read_instruction_due on the estimates before the bill), once per run instead of once a year,
    or on prepayment."""
    from tools.closing_estimate_run_money import _instruction_visits

    def account(channel):
        return [{"billing_basis": "actual", "payment_channel": channel}] + [
            {"billing_basis": "estimated", "payment_channel": channel}] * 30

    assert (_instruction_visits(account("direct_debit")), _instruction_visits(account("prepayment"))) == (
        [12, 24], [])


def test_a_leaver_closed_on_an_estimate_is_settled_on_its_read_spread_by_the_profile():
    """C1 closes on two estimates billing 160 + 120 kWh against 220 + 128 true. The deemed advance,
    280 kWh, is settled over February and March by the electricity profile (8.87 : 9.12), not by
    the household's own shape: 138.05 and 141.95 kWh. With gross 100 a month and no standing
    charge, February moves by 100 x (138.05/220 - 1) and March by 100 x (141.95/128 - 1).
    MUTATIONS this catches: one scale over the whole run (true shape kept) gives -39.08, and a flat
    day count in place of the profile gives -25.46, against the profile's -26.35; either reds the
    approx. C2 closed on an actual read and C9 never left, so neither carries an entry: both halves
    of the partition are reached.
    """
    run = _book()
    run["years"] = {"2020": {"per_customer_monthly": {
        "C1": {"2020-02": {"gross_gbp": 100.0}, "2020-03": {"gross_gbp": 100.0}},
        "C2": {"2020-02": {"gross_gbp": 100.0}},
        "C9": {"2020-01": {"gross_gbp": 100.0}},
    }}}
    moved = cos_read_settlement(run)
    weights = (8.87 / 29 * 29, 9.12 / 31 * 31)
    feb = 280 * weights[0] / sum(weights)
    expected = 100 * (feb / 220 - 1) + 100 * ((280 - feb) / 128 - 1)
    assert moved[("C1", 2020)] == pytest.approx(expected, abs=0.01)
    assert moved[("C1", 2020)] < 0
    assert set(moved) == {("C1", 2020)}


def test_net_settles_the_levies_with_the_energy_and_refuses_a_month_that_has_none():
    """The same C1 span with policy 30 and network 20 inside each month's gross: net's volume
    part is 100 - 30 - 20, so net moves by exactly half of gross's move. MUTATIONS this catches:
    net taken as gross's move (the levies left unscaled) gives 2x; levies subtracted from net
    but not scaled gives a move unrelated to the scale. A month without the entries returns
    None, never gross's move standing in for net's: both legs reached.
    """
    from tools.closing_estimate_run_money import cos_read_settlement_net, settlement_view

    run = _book()
    month = {"gross_gbp": 100.0, "policy_cost_gbp": 30.0, "network_cost_gbp": 20.0}
    run["years"] = {"2020": {"per_customer_monthly": {
        "C1": {"2020-02": dict(month), "2020-03": dict(month)},
        "C2": {"2020-02": dict(month)},
    }}}
    gross = cos_read_settlement(run)[("C1", 2020)]
    assert cos_read_settlement_net(run)[("C1", 2020)] == pytest.approx(gross / 2)
    view = settlement_view(run)
    assert view["formed"] and view["by_year"]["2020"]["supply_point_years"] == 1
    assert view["net_gbp"] == pytest.approx(round(gross / 2, 2), abs=0.01)
    del run["years"]["2020"]["per_customer_monthly"]["C1"]["2020-03"]["network_cost_gbp"]
    assert cos_read_settlement_net(run) is None and settlement_view(run)["net_gbp"] is None

