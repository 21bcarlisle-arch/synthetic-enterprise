"""A catch-up's VAT is on the bill's VAT line, not inside the catch-up line.

Defect (9553d403b7 book, 3,705 bills): the catch-up was the difference of two VAT-inclusive totals,
added to the bill gross, and `vat_gbp` never moved. The bill printed too little VAT and its
before-VAT amount counted the rest as the supplier's charge.
Finding: docs/staging/SEAT_FINDING_A_CATCH_UP_IS_ADDED_TO_THE_BILL_GROSS_AND_ITS_VAT_NEVER_REACHES_THE_VAT_LINE_2026-10-29.md;
knowledge: docs/market_research/back_billing_and_liability.md section 15.
Harness as test_an_actual_bill_carries_the_meters_register.py (Sep read, Oct unread, Nov read).
"""

from __future__ import annotations

import pytest

from company.billing.monthly_bill_assembly import _resolve_catchup
from company.billing.pre_bill_validation import validate_bill
from company.compliance.domain_invariants import check_bill_foots
from tests.company.billing.test_an_actual_bill_carries_the_meters_register import _bills
from tests.company.billing.test_back_billing_follows_the_payment_method import DEMAND, _run


def test_the_catch_up_bill_charges_vat_on_its_month_and_on_the_correction():
    """MUTATION: drop `bill["vat_gbp"] = ... + catchup_vat` and the first assert fails; fold the
    VAT back into the catch-up line and the second does. The total must not move either way."""
    bills = _bills()
    october, november = bills["2023-10"], bills["2023-11"]
    assert november["catchup_applied"], "the branch under test was not taken"
    own_month = (november["commodity_amount_gbp"] + november["non_commodity_amount_gbp"]
                 + november["standing_charge_gbp"])
    correction_vat = october["true_vat_gbp"] - october["vat_gbp"]
    assert correction_vat > 1.0  # a VAT difference big enough to see
    assert november["vat_gbp"] == pytest.approx(own_month * 0.05 + correction_vat, abs=0.01)
    # The catch-up line is the correction before VAT, so VAT is 5% of everything above it.
    assert november["vat_gbp"] == pytest.approx(
        0.05 * (own_month + november["catchup_adjustment_gbp"]), abs=0.01)
    # The customer is charged what they were before: the month gross plus the whole correction.
    assert november["total_amount_gbp"] == pytest.approx(
        own_month * 1.05 + november["catchup_raw_delta_gbp"], abs=0.01)
    assert check_bill_foots(november)
    assert not validate_bill(november).held


def test_a_barred_share_of_the_correction_takes_the_same_share_of_its_vat():
    """Seventeen pay-on-bill months to the demand date: SLC 21BA bars the five oldest, so part of
    the correction is written off and the VAT charged must shrink with it."""
    run = _run(true_gbp=105.0, billed_gbp=63.0, collected_gbp=None)
    for p in run:
        p["true_vat_gbp"], p["vat_gbp"] = 5.0, 3.0
    catchup = _resolve_catchup("C1", "resi", run, DEMAND)
    assert 0 < catchup["written_off_gbp"] < catchup["raw_delta_gbp"], "no partial bar: branch untaken"
    share = catchup["chargeable_gbp"] / catchup["raw_delta_gbp"]
    assert catchup["chargeable_vat_gbp"] == pytest.approx(17 * 2.0 * share, abs=0.01)


def test_a_run_handed_over_without_vat_keeps_the_whole_correction_on_one_line():
    """A caller that predates the split gets None, not a zero that reads as "no VAT on it"."""
    catchup = _resolve_catchup("C1", "resi", _run(105.0, 63.0, None)[-3:], DEMAND)
    assert catchup["chargeable_vat_gbp"] is None
