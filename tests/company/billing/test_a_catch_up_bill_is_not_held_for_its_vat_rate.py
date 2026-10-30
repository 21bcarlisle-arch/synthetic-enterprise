"""A catch-up bill is not held because its catch-up's VAT is not one rate.

Defect (pre-launch tests at e83e2de665, 2026-10-30): after 789d0a6d20 put a catch-up's VAT on the
VAT line, the pre-bill VAT-rate check graded the whole VAT line over the month's lines plus the
catch-up line. The catch-up's VAT is each corrected month's VAT at that month's own rate, summed
and rounded, so over its line it reads 0.0494 on a small domestic credit and -0.2773 on an SME
bill whose estimates crossed the de minimis line. The gate held 38 such bills on the dual-fuel
test's two-year run (3 before), and a held final credit bill is a credit never given or refunded:
SYN-2016-145g's 3.44 and SYN-2016-557g's 6.01 closing credits went to 0, so
test_a_dual_fuel_household_is_one_account_across_both_fuels's refund branch was unreachable.

The month's own VAT is what one rate must explain, and that is what the check grades now. The
two bills below are the run's own, field for field.
"""
from __future__ import annotations

from company.billing.pre_bill_validation import validate_bill

# SYN-2016-145g's final gas bill: a credit, its catch-up an overcharge returned with its VAT.
FINAL_CREDIT = {
    "customer_id": "SYN-2016-145g", "segment": "resi", "commodity": "gas",
    "period_start": "2017-03-01", "period_end": "2017-03-19",
    "total_consumption_kwh": 1289.4122, "commodity_amount_gbp": 24.7193401,
    "non_commodity_amount_gbp": 12.2494159, "standing_charge_gbp": 3.99722,
    "vat_gbp": -0.1617012, "catchup_applied": True, "catchup_adjustment_gbp": -44.25,
    "catchup_vat_gbp": -2.21, "catchup_direction": "overcharge", "total_amount_gbp": -3.45,
    "billing_basis": "actual",
}

# C5, SME electricity: its estimates were billed above de minimis (20%) and its reads were below
# it (5%), so the correction returns more VAT than any one rate on its line would.
SME_ACROSS_DE_MINIMIS = {
    "customer_id": "C5", "segment": "SME", "commodity": "electricity",
    "period_start": "2016-09-01", "period_end": "2016-09-30",
    "total_consumption_kwh": 925.0195192307693, "commodity_amount_gbp": 71.46691910057665,
    "non_commodity_amount_gbp": 37.03778155, "standing_charge_gbp": 8.7183,
    "vat_gbp": -20.018849967471166, "catchup_applied": True, "catchup_adjustment_gbp": -45.02,
    "catchup_vat_gbp": -25.88, "catchup_direction": "overcharge", "total_amount_gbp": 52.18,
    "billing_basis": "actual",
}


def test_a_final_credit_bill_with_a_catch_up_is_issued():
    assert validate_bill(FINAL_CREDIT).reasons == []


def test_an_sme_catch_up_across_the_de_minimis_line_is_issued():
    assert validate_bill(SME_ACROSS_DE_MINIMIS).reasons == []


def test_the_months_own_vat_at_the_wrong_rate_is_still_held():
    """The control can still fire: the same final bill with its own month's VAT at 20%."""
    own_subtotal = 24.7193401 + 12.2494159 + 3.99722
    wrong = dict(FINAL_CREDIT, vat_gbp=round(own_subtotal * 0.20, 4) - 2.21)
    assert any(r.startswith("vat_by_segment") for r in validate_bill(wrong).reasons)
