"""A catch-up is one line per VAT rate, each at the rate its side of the correction was charged at.

VAT Notice 700 s16.3.1 asks a VAT invoice for "the rate of VAT, and the amount payable excluding
VAT" on each line; s18.2.3-18.2.5 ask a credit or debit note for the rate and VAT at the original
supply's rate. C5-INV113's catch-up is a 20% credit (August's estimate, over the 33 kWh/day business
de minimis) and a 5% debit (August as read), and it printed as one line at no rate.
Knowledge: docs/market_research/back_billing_and_liability.md section 15 (the seat finding of
2026-11-13 that asked for this is retired by the commit that adds this test).
"""

from __future__ import annotations

import pytest

from company.billing.monthly_bill_assembly import _resolve_catchup
from tests.company.billing.test_an_actual_bill_carries_the_meters_register import _bills
from tests.company.billing.test_back_billing_follows_the_payment_method import DEMAND, _run

# C5/113 on the 0a6391d186 book (the same figures as test_a_catch_ups_vat_is_on_the_vat_line.py).
C5_AUGUST = {"period_start": "2016-08-01", "period_end": "2016-08-31",
             "total_amount_gbp": 189.01, "vat_gbp": 31.50, "vat_rate": 0.2,
             "true_total_amount_gbp": 118.11, "true_vat_gbp": 5.62, "true_vat_rate": 0.05}


def test_c5_inv113_is_a_20pc_credit_and_a_5pc_debit_that_sum_to_its_one_line():
    """MUTATION: key the true side by the billed rate and the two lines collapse into one at 20%
    carrying 5% VAT on 112.49 inside it, and this reds."""
    catchup = _resolve_catchup("C5", "SME", [dict(C5_AUGUST)], "2016-10-05", "on_receipt")
    lines = catchup["lines_by_rate"]
    assert lines == [{"rate": 0.2, "net_gbp": -157.51, "vat_gbp": -31.5},
                     {"rate": 0.05, "net_gbp": 112.49, "vat_gbp": 5.62}]
    assert sum(ln["vat_gbp"] for ln in lines) == pytest.approx(catchup["chargeable_vat_gbp"], abs=1e-9)
    net = round(catchup["chargeable_gbp"] - catchup["chargeable_vat_gbp"], 2)
    assert sum(ln["net_gbp"] for ln in lines) == pytest.approx(net, abs=1e-9)
    for ln in lines:  # each line's VAT is its own rate of its own net, to the penny
        assert abs(ln["net_gbp"] * ln["rate"] - ln["vat_gbp"]) <= 0.01


def test_a_barred_correction_splits_by_rate_and_still_sums_to_the_printed_figures_to_the_penny():
    """The bar scales every line by the same share; the rounding penny goes to the largest line, so
    the sums are the printed `catchup_adjustment_gbp` and `catchup_vat_gbp` exactly. The run is
    domestic so the bar bites; its mixed rates are synthetic and exercise only the split's sums."""
    run = _run(true_gbp=105.0, billed_gbp=63.0, collected_gbp=None)
    for n, p in enumerate(run):
        p.update(true_vat_gbp=5.0, vat_gbp=3.0, true_vat_rate=0.05,
                 vat_rate=0.2 if n % 3 == 0 else 0.05)
    catchup = _resolve_catchup("C1", "resi", run, DEMAND)
    assert 0 < catchup["written_off_gbp"] < catchup["raw_delta_gbp"], "no partial bar: branch untaken"
    lines = catchup["lines_by_rate"]
    assert [ln["rate"] for ln in lines] == [0.2, 0.05]
    assert round(sum(ln["vat_gbp"] for ln in lines), 2) == catchup["chargeable_vat_gbp"]
    assert round(sum(ln["net_gbp"] for ln in lines), 2) == round(
        catchup["chargeable_gbp"] - catchup["chargeable_vat_gbp"], 2)


def test_the_assembled_domestic_catch_up_is_one_line_at_5pc_and_is_its_printed_line():
    """Through `build_monthly_bills`: the pending run records each side's rate, so a domestic
    catch-up is one 5% line equal to the bill's own catch-up line and VAT. Fails if the run stops
    carrying the rates (the bill then has no `catchup_lines_by_rate`)."""
    november = _bills()["2023-11"]
    assert november["catchup_applied"], "the branch under test was not taken"
    assert november["catchup_lines_by_rate"] == [{
        "rate": 0.05, "net_gbp": november["catchup_adjustment_gbp"],
        "vat_gbp": november["catchup_vat_gbp"]}]


def test_a_run_handed_over_without_rates_has_no_lines_rather_than_a_guessed_rate():
    run = [{k: v for k, v in C5_AUGUST.items() if k not in ("vat_rate", "true_vat_rate")}]
    assert _resolve_catchup("C5", "SME", run, "2016-10-05", "on_receipt")["lines_by_rate"] is None
