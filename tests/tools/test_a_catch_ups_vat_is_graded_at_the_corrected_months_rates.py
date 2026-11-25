"""A catch-up's VAT is graded at the rates of the months it corrects, not at the carrying bill's rate.

C5 invoice 110 (SME, June 2016, 31.0 kWh/day, under the 33 kWh/day de minimis) carries a GBP 187.08
before-VAT catch-up for February to May, months billed at 20%. Its VAT line is 5.88 on its own month
plus 37.41 on the catch-up, which is 43.29. The comparison graded the whole 304.75 at this month's 5%
(15.24) and filed +28.05 as a biller defect for 21 days. The biller was right: VAT Notice 700
s18.2.5 puts a credit or debit note at the original supply's rate (back_billing_and_liability.md
s15). The figures below are that bill's.
"""
from __future__ import annotations

from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as validator


def _c5_110(vat=43.29):
    return {"invoice_number": 110, "period_start": "2016-06-01", "period_end": "2016-06-30",
            "total_amount_gbp": 348.04, "parts_sum_gbp": 348.04,
            "lines": [
                {"label": "Energy", "amount_gbp": 71.76, "inputs": {"consumption_kwh": 928.8}},
                {"label": "Standing charge", "amount_gbp": 8.72, "inputs": {}},
                {"label": "Network and policy costs", "amount_gbp": 37.19, "inputs": {}},
                {"label": "VAT", "amount_gbp": vat, "inputs": {}},
                {"label": "Catch-up correction (bills already issued, restated)",
                 "amount_gbp": 187.08,
                 "inputs": {"vat_basis": "before_vat", "catchup_vat_gbp": 37.41}},
            ]}


def _rebuilt():
    return {"period_start": "2016-06-01", "period_end": "2016-06-30", "lines": [
        {"label": "Energy", "status": validator.RECONSTRUCTED, "amount_gbp": 71.76, "how": "x"},
        {"label": "Standing charge", "status": validator.RECONSTRUCTED, "amount_gbp": 8.72},
        {"label": "Network and policy costs", "status": validator.UNCHECKABLE, "why": "no rate"},
    ]}


def _claims(bill, why):
    claims = cmp.compare_bill(_rebuilt(), bill, statutory_vat={"rate": 0.05, "why": "de minimis"},
                              read_volume_kwh=928.8, catchup_vat_why=why)
    return {c["claim"]: c for c in claims}


def test_the_month_is_graded_on_its_own_lines_and_the_catch_up_by_the_run_check():
    """MUTATION (must fire): grade the VAT line over a base that includes the catch-up line (the
    pre-2026-11-25 shape, expected 15.24), or compare the whole VAT line rather than the line less
    `catchup_vat_gbp`."""
    claims = _claims(_c5_110(), lambda: None)
    assert claims["vat_gbp"]["verdict"] == cmp.AGREED
    assert claims["vat_gbp"]["validator_says"] == 5.88
    assert claims["vat_gbp"]["biller_says"] == 5.88
    assert claims["catchup_vat_gbp"]["verdict"] == cmp.BOUNDED


def test_every_verdict_on_the_catch_up_can_be_reached_and_the_month_still_files_a_penny():
    """A guard that never refuses passes every test of what it refuses, so the whole partition is
    asserted at once. MUTATION (must fire): make the catch-up claim always BOUNDED, or drop the run
    check's reason; widen PENNY so the month's own penny is forgiven."""
    verdicts = {
        _claims(_c5_110(), lambda: None)["catchup_vat_gbp"]["verdict"],
        _claims(_c5_110(), lambda: "outside 5%-20%")["catchup_vat_gbp"]["verdict"],
        _claims(_c5_110(), None)["catchup_vat_gbp"]["verdict"],
    }
    assert verdicts == {cmp.BOUNDED, cmp.DISAGREED, cmp.UNCHECKABLE}
    assert _claims(_c5_110(), lambda: "outside 5%-20%")["catchup_vat_gbp"]["why"] == "outside 5%-20%"
    assert _claims(_c5_110(vat=43.30), lambda: None)["vat_gbp"]["verdict"] == cmp.DISAGREED
