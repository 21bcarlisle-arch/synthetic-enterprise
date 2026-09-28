"""The balance-at-close write-off rule (`simulation.arrears_engine.balance_write_offs`).

Design: docs/staging/SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md.
"""
from datetime import date, timedelta

from simulation.arrears_engine import (
    BAD_DEBT_BASIS,
    LEG_CLOSE,
    LEG_STATUTE_BAR,
    LIVE_ARREARS_PROVISION_RATES,
    STAYER_FAILED_DD_BUCKET_ENV,
    apply_emergent_bad_debt,
    balance_settlement_from_outcomes,
    balance_write_offs_from_outcomes,
    compute_emergent_bad_debt,
    stayer_failed_dd_bucket,
    stayer_provision_charges,
)


def _row(cid, period_end, outcome, amount=100.0, days_late=0):
    return {"customer_id": cid, "period_end": period_end, "commodity": "electricity",
            "amount_gbp": amount, "due_date": date.fromisoformat(period_end) + timedelta(days=14),
            "method": "direct_debit", "outcome": outcome, "days_late": days_late}


def _monthly(cid, start_year, months, first_outcome, rest_outcome):
    rows = []
    for i in range(months):
        y, m = start_year + i // 12, i % 12 + 1
        rows.append(_row(cid, f"{y}-{m:02d}-28", first_outcome if i == 0 else rest_outcome))
    return rows


def _book():
    return (
        _monthly("LEAVER_WITH_BALANCE", 2016, 24, "failed", "success")
        + _monthly("LEAVER_CLEARED", 2016, 24, "success", "success")
        # Stayers run past six years, so only the payments stand between them and the bar.
        + _monthly("STAYER_PAYING", 2016, 90, "failed", "success")
        + _monthly("STAYER_NEVER_PAYS", 2016, 90, "failed", "failed")
    )


def test_the_statute_bar_leg_can_fire_and_every_fate_in_the_partition_is_reached():
    """A rule that never bars anything, or bars everything, fails here: the rare leg is asserted
    reachable before what it does is asserted, and one control covers the whole partition."""
    wo = balance_write_offs_from_outcomes(_book(), {"LEAVER_WITH_BALANCE", "LEAVER_CLEARED"})
    legs_by_cid = {}
    for (cid, _pe, _c), v in wo.items():
        legs_by_cid.setdefault(cid, set()).add(v["leg"])
    assert LEG_STATUTE_BAR in legs_by_cid.get("STAYER_NEVER_PAYS", set())
    fates = {
        "close_with_balance": legs_by_cid.get("LEAVER_WITH_BALANCE") == {LEG_CLOSE},
        "close_cleared": "LEAVER_CLEARED" not in legs_by_cid,
        "stayer_with_balance": "STAYER_PAYING" not in legs_by_cid,
        "stayer_statute_barred": legs_by_cid.get("STAYER_NEVER_PAYS") == {LEG_STATUTE_BAR},
    }
    assert all(fates.values()), fates


def test_a_payment_restarts_the_limitation_clock_so_a_paying_stayer_is_never_barred():
    wo = balance_write_offs_from_outcomes(_monthly("S", 2016, 90, "failed", "success"), set())
    assert wo == {}


def test_the_bar_falls_six_years_after_the_debt_accrued_when_nothing_is_paid():
    wo = balance_write_offs_from_outcomes(_monthly("S", 2016, 90, "failed", "failed"), set())
    first = wo[("S", "2016-01-28", "electricity")]
    assert first["date"] == date(2022, 2, 11)  # due 2016-02-11 + 6y
    assert not any(v["leg"] == LEG_CLOSE for v in wo.values())


def test_a_leavers_write_off_is_its_balance_at_close_dated_at_the_final_bills_due_date():
    rows = _monthly("L", 2016, 24, "failed", "success")
    rows[5]["outcome"] = "failed"
    wo = balance_write_offs_from_outcomes(rows, {"L"})
    assert sum(v["amount_gbp"] for v in wo.values()) == 200.0
    assert {v["date"] for v in wo.values()} == {date(2017, 12, 28) + timedelta(days=14)}


def test_the_stayer_provision_is_a_declared_gap_and_the_bad_debt_line_says_write_offs_only(monkeypatch):
    monkeypatch.delenv(STAYER_FAILED_DD_BUCKET_ENV, raising=False)
    assert stayer_failed_dd_bucket() is None
    assert BAD_DEBT_BASIS.startswith("write-offs only")
    assert "declared gap" in BAD_DEBT_BASIS


def test_a_stayers_failed_bills_are_never_booked_on_the_real_engine(monkeypatch):
    monkeypatch.delenv(STAYER_FAILED_DD_BUCKET_ENV, raising=False)
    # Bills the pre-bill gate issues: the engine resolves nothing it holds (they foot, and 600 kWh).
    bills = [{"customer_id": "C1", "period_start": f"2022-{m:02d}-01", "period_end": f"2022-{m:02d}-28",
              "total_amount_gbp": 199.92, "commodity_amount_gbp": 150.0,
              "non_commodity_amount_gbp": 25.0, "standing_charge_gbp": 15.4, "vat_gbp": 9.52,
              "total_consumption_kwh": 600.0,
              "segment": "resi", "commodity": "electricity"} for m in range(1, 13)]
    beh = {"C1": {"income_stress_trajectory": [{"year": 2022, "stress": "HIGH"}]}}
    assert compute_emergent_bad_debt(bills, beh, set()) == {}
    booked = compute_emergent_bad_debt(bills, beh, {"C1"})
    assert set(booked) == {("C1", 2023)}  # the final bill (2022-12-28) is due 2023-01-11


def test_a_write_off_dated_after_the_accounts_last_record_books_on_it_rather_than_vanishing():
    records = [
        {"customer_id": "C1", "settlement_date": "2022-06-01", "bad_debt_gbp": 0.0,
         "net_margin_gbp": 50.0, "treasury_cash_balance_gbp": 1000.0},
        {"customer_id": "C1", "settlement_date": "2022-12-31", "bad_debt_gbp": 0.0,
         "net_margin_gbp": 50.0, "treasury_cash_balance_gbp": 1050.0},
    ]
    apply_emergent_bad_debt(records, {("C1", 2023): 40.0, ("C1", 2021): 7.0})
    assert records[1]["bad_debt_gbp"] == 40.0
    assert records[1]["treasury_cash_balance_gbp"] == 1010.0
    # A year BEFORE the account's first record is not folded forward.
    assert records[0]["bad_debt_gbp"] == 0.0


def test_a_held_bill_and_a_credit_bill_are_never_written_off():
    """Defect (real book, 6ba548633): the engine wrote off bills its pre-bill gate held -- never
    issued, so never due -- and credit bills as NEGATIVE bad debt. The ledger issued neither."""
    good = {"customer_id": "C1", "period_start": "2022-01-01", "period_end": "2022-01-28",
            "total_amount_gbp": 199.92, "commodity_amount_gbp": 150.0,
            "non_commodity_amount_gbp": 25.0, "standing_charge_gbp": 15.4, "vat_gbp": 9.52,
            "total_consumption_kwh": 600.0, "segment": "resi", "commodity": "electricity"}
    beh = {"C1": {"income_stress_trajectory": [{"year": 2022, "stress": "HIGH"}]}}
    # Held because the total does not foot. It was 0 kWh until b33f08d2e dropped the resi
    # consumption floor, after which that fixture was issued and the held leg tested nothing.
    held = [dict(good, period_start=f"2022-{m:02d}-01", period_end=f"2022-{m:02d}-28",
                 total_amount_gbp=250.0) for m in range(1, 13)]
    from company.billing.pre_bill_validation import validate_bills
    assert not validate_bills(held)[0], "the held fixture is issued -- it tests nothing"
    # A credit the gate ISSUES: the real book's credits are catch-up overcharge refunds, not
    # negative line items (which the gate holds, and which would test the held leg twice).
    credit = [dict(good, period_start=f"2022-{m:02d}-01", period_end=f"2022-{m:02d}-28",
                   catchup_applied=True, catchup_direction="overcharge", catchup_adjustment_gbp=-400.0,
                   total_amount_gbp=-200.08)
              for m in range(1, 13)]
    assert len(validate_bills(credit)[0]) == 12, "the credit fixture is held -- it tests nothing"
    issued = [dict(good, period_start=f"2022-{m:02d}-01", period_end=f"2022-{m:02d}-28")
              for m in range(1, 13)]
    # Control: the same account on issued positive bills IS written off, so the refusals below
    # are about the bills, not an engine that writes off nothing.
    assert compute_emergent_bad_debt(issued, beh, {"C1"})
    assert compute_emergent_bad_debt(held, beh, {"C1"}) == {}
    assert compute_emergent_bad_debt(credit, beh, {"C1"}) == {}


def _credit(cid, period_end, amount, commodity="electricity"):
    return dict(_row(cid, period_end, "credit", amount=-amount), commodity=commodity, method=None)


def test_a_credit_nets_against_the_same_contracts_arrears_and_every_fate_is_reachable():
    """SLC 27.16: Credit exists only net of the charges due under that Domestic Supply Contract.
    Defect: a catch-up credit sat beside unpaid arrears on the same account and the arrears were
    still written off in full at close. One control over the partition: cleared in full, netted in
    part, carried forward to later arrears, and left alone on the other fuel."""
    rows = (
        [_row("FULL", "2016-01-28", "failed"), _credit("FULL", "2016-03-28", 150.0)]
        + [_row("PART", "2016-01-28", "failed"), _credit("PART", "2016-03-28", 30.0)]
        + [_credit("CARRY", "2016-01-28", 40.0), _row("CARRY", "2016-03-28", "failed")]
        + [_row("OTHER_FUEL", "2016-01-28", "failed"),
           _credit("OTHER_FUEL", "2016-03-28", 150.0, commodity="gas")]
    )
    cids = {"FULL", "PART", "CARRY", "OTHER_FUEL"}
    wo, credited = balance_settlement_from_outcomes(rows, cids)
    owed = {cid: sum(v["amount_gbp"] for (c, _pe, _f), v in wo.items() if c == cid) for cid in cids}
    fates = {
        "cleared_in_full": owed["FULL"] == 0 and credited[("FULL", "2016-01-28", "electricity")],
        "netted_in_part": owed["PART"] == 70.0,
        "carried_forward": owed["CARRY"] == 60.0,
        "never_across_fuels": owed["OTHER_FUEL"] == 100.0,
    }
    assert all(fates.values()), fates
    # Only the surplus is used: FULL's 150 credit clears 100, and the 50 left over nets nothing else.
    assert sum(a["amount_gbp"] for a in credited[("FULL", "2016-01-28", "electricity")]) == 100.0


def test_the_oldest_arrears_are_discharged_first():
    rows = [_row("L", "2016-01-28", "failed"), _row("L", "2016-02-28", "failed"),
            _credit("L", "2016-04-28", 100.0)]
    wo = balance_write_offs_from_outcomes(rows, {"L"})
    assert list(wo) == [("L", "2016-02-28", "electricity")]


def test_a_credit_is_not_a_payment_so_it_does_not_restart_the_limitation_clock():
    rows = _monthly("S", 2016, 90, "failed", "failed")
    rows.append(_credit("S", "2016-06-28", 10.0))
    first = balance_write_offs_from_outcomes(rows, set())[("S", "2016-01-28", "electricity")]
    assert first["date"] == date(2022, 2, 11) and first["amount_gbp"] == 90.0


def _provision_book():
    rows = _monthly("STAYER_TWO_FAILED", 2016, 40, "failed", "success")
    rows[5] = _row("STAYER_TWO_FAILED", rows[5]["period_end"], "failed")
    return rows + _monthly("LEAVER", 2016, 12, "failed", "failed") + \
        _monthly("STAYER_NEVER_PAYS", 2016, 90, "failed", "failed")


def _charges(rows, bucket):
    written_off, credited = balance_settlement_from_outcomes(rows, {"LEAVER"})
    return stayer_provision_charges(rows, {"LEAVER"}, written_off, credited, bucket), written_off


def test_leg_4b_has_no_default_and_refuses_a_bucket_it_cannot_name(monkeypatch):
    """C1 is unsourced, so no bucket may be assumed: unset is off, and a typo is refused with the
    reason rather than read as either row."""
    monkeypatch.setenv(STAYER_FAILED_DD_BUCKET_ENV, "dd")
    try:
        stayer_failed_dd_bucket()
    except ValueError as exc:
        assert "C1 is unsourced" in str(exc)
    else:
        raise AssertionError("an unnamed bucket was accepted")


def test_both_c1_buckets_are_reachable_and_differ_as_the_sourced_rows_do():
    """Both rows of the bracket fire, on stayers only, and the >90d rates are Centrica 2025's."""
    by = {b: _charges(_provision_book(), b)[0] for b in LIVE_ARREARS_PROVISION_RATES}
    assert set(by) == {"still_in_dd", "fallen_out_of_dd"}
    assert all(by.values())
    for charges in by.values():
        assert not any(c == "LEAVER" for c, _ in charges)
    # Two GBP 100 failed bills, both >90 days old at the first year-end.
    assert by["still_in_dd"][("STAYER_TWO_FAILED", 2016)] == 14.8
    assert by["fallen_out_of_dd"][("STAYER_TWO_FAILED", 2016)] == 100.6


def test_a_statute_barred_item_leaves_the_provision_stock_so_it_is_not_charged_twice():
    charges, wo = _charges(_provision_book(), "fallen_out_of_dd")
    barred_years = {v["date"].year for (c, _p, _f), v in wo.items() if c == "STAYER_NEVER_PAYS"}
    assert barred_years
    assert any(charges.get(("STAYER_NEVER_PAYS", y), 0.0) < 0 for y in barred_years)


def test_a_credit_netted_against_a_stayers_arrears_leaves_the_provision_stock():
    rows = _monthly("S", 2016, 24, "failed", "success") + [_credit("S", "2016-06-28", 100.0)]
    written_off, credited = balance_settlement_from_outcomes(rows, set())
    assert credited
    assert stayer_provision_charges(rows, set(), written_off, credited, "fallen_out_of_dd") == {}


def test_leg_4b_reaches_the_real_engine_only_when_a_bucket_is_named(monkeypatch):
    bills = [{"customer_id": "C1", "period_start": f"2022-{m:02d}-01", "period_end": f"2022-{m:02d}-28",
              "total_amount_gbp": 199.92, "commodity_amount_gbp": 150.0,
              "non_commodity_amount_gbp": 25.0, "standing_charge_gbp": 15.4, "vat_gbp": 9.52,
              "total_consumption_kwh": 600.0,
              "segment": "resi", "commodity": "electricity"} for m in range(1, 13)]
    beh = {"C1": {"income_stress_trajectory": [{"year": 2022, "stress": "HIGH"}]}}
    monkeypatch.delenv(STAYER_FAILED_DD_BUCKET_ENV, raising=False)
    assert compute_emergent_bad_debt(bills, beh, set()) == {}
    monkeypatch.setenv(STAYER_FAILED_DD_BUCKET_ENV, "still_in_dd")
    low = sum(compute_emergent_bad_debt(bills, beh, set()).values())
    monkeypatch.setenv(STAYER_FAILED_DD_BUCKET_ENV, "fallen_out_of_dd")
    high = sum(compute_emergent_bad_debt(bills, beh, set()).values())
    assert 0 < low < high
