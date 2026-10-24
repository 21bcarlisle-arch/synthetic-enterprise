"""The fresh-run grade counts a default-tariff bill over the household's ceiling, and only that.

Defect it exists to catch: a grade that counts by "before the first renewal" or ignores the
recorded tariff type, so a fixed bill priced above the cap is counted as an SVT breach (185 such
bills on 8b6fea024), or a grade that refuses everything and reports 0 of N.
"""

from tools.grade_svt_invoices_over_ceiling import epg_receipt, grade


def _bill(cid: str, start: str, p_per_kwh_inc_vat: float) -> dict:
    net = 100 * p_per_kwh_inc_vat / 1.05 / 100.0
    return {"customer_id": cid, "period_start": start, "commodity": "electricity",
            "total_consumption_kwh": 100.0, "commodity_amount_gbp": net,
            "non_commodity_amount_gbp": 0.0, "vat_gbp": net * 0.05,
            "total_amount_gbp": net * 1.05, "billing_basis": "estimated"}


def _term(cid: str, tariff_type: str) -> dict:
    return {"customer_id": cid, "billing_account": cid, "term_start": "2019-01-01",
            "term_end": "2019-04-01", "tariff_type": tariff_type}


def test_the_partition():
    run = {
        "account_state_log": [_term("over", "svt"), _term("within", "svt"), _term("fix", "fixed")],
        "bills": [_bill("over", "2019-02-01", 99.0), _bill("within", "2019-02-01", 10.0),
                  _bill("fix", "2019-02-01", 99.0), _bill("no-term", "2019-02-01", 99.0)],
    }
    g = grade(run)
    # Both verdicts reachable, and the fixed and unrecorded bills are outside the denominator.
    assert g["default_tariff_invoices_graded"] == 2
    assert g["above_household_ceiling"] == 1
    assert g["households_above"] == 1
    assert g["outside_epg_windows"] == 1
    assert g["by_year"] == {"2019": 1}


def test_the_epg_receipt_grade_sees_a_carve_outside_the_window_and_a_ledger_that_lost_one():
    """Defect: a receipt carved off a bill outside Oct 2022-Jun 2023, or carved and never booked.

    Both leaks must be reachable, and a clean run must read clean, or a grade that always says
    "leaking" (or never does) passes.
    """
    # 100 kWh billed at the EPG; the receipt is the Treasury's (cap - EPG) share, ex-VAT like the bill.
    receipt = round(100 * (0.6747 - 0.34) / 1.05, 2)
    inside = {**_bill("a", "2023-01-01", 34.0), "hmt_epg_receipt_gbp": receipt}
    outside = {**_bill("b", "2019-02-01", 10.0), "hmt_epg_receipt_gbp": 5.0}
    clean = epg_receipt({"bills": [inside], "ledger_pnl": {"epg_receipt_gbp": receipt}})
    assert clean["carved_gbp"] == clean["booked_gbp"] == receipt
    assert clean["carved_outside_epg_windows"] == 0
    # 33.47p removed from a 67.47p unit charge: Q1 2023's (cap - EPG) / cap.
    assert clean["unit_charge_fall"] == {"2023-Q1 electricity": 0.496}
    leaky = epg_receipt({"bills": [inside, outside], "ledger_pnl": {"epg_receipt_gbp": receipt}})
    assert leaky["carved_outside_epg_windows"] == 1
    assert leaky["carved_gbp"] != leaky["booked_gbp"]
    assert epg_receipt({"bills": [inside]})["booked_gbp"] is None
