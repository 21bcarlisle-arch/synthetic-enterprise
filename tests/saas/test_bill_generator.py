import pytest

from saas.bill_generator import (
    BILL_SHOCK_PENALTY_FACTOR,
    CONSUMPTION_CV_PENALTY_FACTOR,
    consumption_coefficient_of_variation,
    generate_bill,
)
from saas.non_commodity import (
    NON_COMMODITY_RATE_GBP_PER_MWH,
    STANDING_CHARGE_GBP_PER_DAY,
    VAT_RATE,
)


def make_records(daily_kwh: dict[str, float], unit_rate_gbp_per_mwh: float = 200.0):
    records = []
    for settlement_date, kwh in daily_kwh.items():
        records.append({
            "customer_id": "C1",
            "settlement_date": settlement_date,
            "settlement_period": 1,
            "consumption_kwh": kwh,
            "unit_rate_gbp_per_mwh": unit_rate_gbp_per_mwh,
            "revenue_gbp": (kwh / 1000) * unit_rate_gbp_per_mwh,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        })
    return records


def _expected_total(consumption_kwh, rate, days, segment="resi", commodity="electricity"):
    """Compute expected total_amount_gbp for test assertions."""
    nc_rate = NON_COMMODITY_RATE_GBP_PER_MWH[segment]
    sc_rate = STANDING_CHARGE_GBP_PER_DAY[commodity][segment]
    vat = VAT_RATE[segment]
    commodity_amt = (consumption_kwh / 1000) * rate
    non_commodity_amt = (consumption_kwh / 1000) * nc_rate
    standing_amt = days * sc_rate
    subtotal = commodity_amt + non_commodity_amt + standing_amt
    return subtotal * (1 + vat)


def test_generate_bill_empty_raises():
    with pytest.raises(ValueError):
        generate_bill("C1", [], "fixed_1yr")


def test_generate_bill_commodity_amount():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 20.0})
    bill = generate_bill("C1", records, "fixed_1yr")

    assert bill["customer_id"] == "C1"
    assert bill["period_start"] == "2023-01-01"
    assert bill["period_end"] == "2023-01-02"
    assert bill["total_consumption_kwh"] == pytest.approx(30.0)
    # commodity_amount_gbp is the settlement-derived revenue only
    assert bill["commodity_amount_gbp"] == pytest.approx((30.0 / 1000) * 200.0)
    assert bill["average_unit_rate_gbp_per_mwh"] == pytest.approx(200.0)


def test_generate_bill_phase9a_components():
    """Phase 9a: non-commodity, standing charge, and VAT appear as separate fields."""
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 20.0})
    bill = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")

    kwh = 30.0
    # non-commodity: £55/MWh resi electricity
    expected_nc = (kwh / 1000) * 55.0
    # standing charge: 2 days × £0.27/day
    expected_sc = 2 * 0.27
    expected_subtotal = (kwh / 1000) * 200.0 + expected_nc + expected_sc
    expected_vat = expected_subtotal * 0.05
    expected_total = expected_subtotal + expected_vat

    assert bill["non_commodity_amount_gbp"] == pytest.approx(expected_nc)
    assert bill["standing_charge_gbp"] == pytest.approx(expected_sc)
    assert bill["vat_gbp"] == pytest.approx(expected_vat)
    assert bill["total_amount_gbp"] == pytest.approx(expected_total)
    assert bill["segment"] == "resi"
    assert bill["commodity"] == "electricity"


def test_generate_bill_sme_uses_higher_vat():
    """SME customers pay 20% VAT, domestic 5%."""
    records = make_records({"2023-06-01": 100.0, "2023-06-02": 100.0})
    resi = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")
    sme = generate_bill("C2", records, "fixed_1yr", segment="SME", commodity="electricity")

    # SME bill should be larger due to higher VAT (20% vs 5%)
    assert sme["vat_gbp"] > resi["vat_gbp"]
    # Check specific VAT rate applied
    assert sme["vat_gbp"] == pytest.approx(
        (sme["commodity_amount_gbp"] + sme["non_commodity_amount_gbp"] + sme["standing_charge_gbp"]) * 0.20
    )


def test_generate_bill_gas_uses_gas_nc_rate():
    """Gas bills use the gas non-commodity rate (£10/MWh resi), not electricity."""
    records = make_records({"2023-01-01": 100.0})
    gas_bill = generate_bill("C1g", records, "fixed_1yr", segment="resi", commodity="gas")

    kwh = 100.0
    expected_nc = (kwh / 1000) * 10.0  # gas rate
    assert gas_bill["non_commodity_amount_gbp"] == pytest.approx(expected_nc)


def test_steady_consumption_fixed_tariff_is_maximally_clear():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 10.0, "2023-01-03": 10.0})
    bill = generate_bill("C1", records, "fixed_1yr")
    assert bill["clarity_score"] == pytest.approx(1.0)
    assert bill["bill_shock_pct"] is None


def test_volatile_consumption_reduces_clarity():
    steady = make_records({"2023-01-01": 10.0, "2023-01-02": 10.0})
    volatile = make_records({"2023-01-01": 1.0, "2023-01-02": 19.0})

    bill_steady = generate_bill("C1", steady, "fixed_1yr")
    bill_volatile = generate_bill("C1", volatile, "fixed_1yr")

    assert bill_volatile["clarity_score"] < bill_steady["clarity_score"]


def test_unknown_contract_type_uses_default_base_clarity():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 10.0})
    bill = generate_bill("C1", records, "tou_smart")
    assert bill["clarity_score"] == pytest.approx(0.7)


def test_bill_shock_zero_when_previous_equals_total():
    """No shock when previous bill matches current total (including non-commodity + VAT)."""
    records = make_records({"2023-02-01": 10.0, "2023-02-02": 10.0})
    # First generate to get the actual total
    first_bill = generate_bill("C1", records, "fixed_1yr")
    actual_total = first_bill["total_amount_gbp"]
    # Then generate with that as previous — expect zero shock
    bill = generate_bill("C1", records, "fixed_1yr", previous_bill_total_gbp=actual_total)
    assert bill["bill_shock_pct"] == pytest.approx(0.0)


def test_bill_shock_reduces_clarity():
    """Large bill shock (>100%) is capped at 1.0 for the clarity penalty."""
    records = make_records({"2023-02-01": 10.0, "2023-02-02": 10.0})
    # previous_bill_total_gbp much smaller than actual → large shock
    bill_with_shock = generate_bill("C1", records, "fixed_1yr", previous_bill_total_gbp=0.01)
    bill_no_shock = generate_bill("C1", records, "fixed_1yr")

    assert bill_with_shock["clarity_score"] < bill_no_shock["clarity_score"]
    # shock_pct > 1.0 so penalty is capped at BILL_SHOCK_PENALTY_FACTOR
    assert bill_with_shock["clarity_score"] == pytest.approx(
        bill_no_shock["clarity_score"] - 1.0 * BILL_SHOCK_PENALTY_FACTOR
    )


def test_clarity_score_floored_at_zero():
    volatile = make_records({"2023-01-01": 0.1, "2023-01-02": 100.0})
    bill = generate_bill("C1", volatile, "tou_smart", previous_bill_total_gbp=0.01)
    assert bill["clarity_score"] == pytest.approx(0.0)


def test_consumption_cv_single_day_is_zero():
    records = make_records({"2023-01-01": 10.0})
    assert consumption_coefficient_of_variation(records) == 0.0


def test_consumption_cv_matches_manual_calc():
    records = make_records({"2023-01-01": 5.0, "2023-01-02": 15.0})
    # mean=10, pstdev=5 -> cv=0.5
    assert consumption_coefficient_of_variation(records) == pytest.approx(0.5)
    bill = generate_bill("C1", records, "fixed_1yr")
    assert bill["clarity_score"] == pytest.approx(1.0 - 0.5 * CONSUMPTION_CV_PENALTY_FACTOR)
