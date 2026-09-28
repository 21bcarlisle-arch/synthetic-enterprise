"""The balance-at-close write-off rule (`simulation.arrears_engine.balance_write_offs`).

Design: docs/staging/SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md.
"""
from datetime import date, timedelta

from simulation.arrears_engine import (
    BAD_DEBT_BASIS,
    LEG_CLOSE,
    LEG_STATUTE_BAR,
    STAYER_ARREARS_PROVISION_RATE,
    apply_emergent_bad_debt,
    balance_write_offs_from_outcomes,
    compute_emergent_bad_debt,
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


def test_the_stayer_provision_is_a_declared_gap_and_the_bad_debt_line_says_write_offs_only():
    assert STAYER_ARREARS_PROVISION_RATE is None
    assert BAD_DEBT_BASIS.startswith("write-offs only")
    assert "declared gap" in BAD_DEBT_BASIS


def test_a_stayers_failed_bills_are_never_booked_on_the_real_engine():
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
    held = [dict(good, period_start=f"2022-{m:02d}-01", period_end=f"2022-{m:02d}-28",
                 total_consumption_kwh=0.0) for m in range(1, 13)]
    # A credit the gate ISSUES: the real book's credits are catch-up overcharge refunds, not
    # negative line items (which the gate holds, and which would test the held leg twice).
    credit = [dict(good, period_start=f"2022-{m:02d}-01", period_end=f"2022-{m:02d}-28",
                   catchup_applied=True, catchup_direction="overcharge", catchup_adjustment_gbp=-400.0,
                   total_amount_gbp=-200.08)
              for m in range(1, 13)]
    from company.billing.pre_bill_validation import validate_bills
    assert len(validate_bills(credit)[0]) == 12, "the credit fixture is held -- it tests nothing"
    issued = [dict(good, period_start=f"2022-{m:02d}-01", period_end=f"2022-{m:02d}-28")
              for m in range(1, 13)]
    # Control: the same account on issued positive bills IS written off, so the refusals below
    # are about the bills, not an engine that writes off nothing.
    assert compute_emergent_bad_debt(issued, beh, {"C1"})
    assert compute_emergent_bad_debt(held, beh, {"C1"}) == {}
    assert compute_emergent_bad_debt(credit, beh, {"C1"}) == {}
