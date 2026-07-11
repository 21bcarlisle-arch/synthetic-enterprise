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


# NOTE: make_records() deliberately produces the *fallback* record shape -- a
# pure-commodity `revenue_gbp` with NO settlement-derived standing-charge field.
# This exercises generate_bill()'s fallback path (flat saas.non_commodity rate),
# which is what synthetic/legacy pre-Phase-62 records look like. The REAL
# settlement-record shape (year-calibrated standing charge folded into
# revenue_gbp AND exposed as its own field) is exercised by the
# test_*_real_settlement / test_*_sc_field integration tests below -- that path
# was the coverage gap that let the standing-charge double-count ship.
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
    # non-commodity: £80/MWh resi electricity (2023 year-indexed rate)
    expected_nc = (kwh / 1000) * 80.0
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


# --- days_in_period / standing_charge_gbp_per_day (2026-07-10, director page
# comment: "Days x standing charges... we need to be able to explain the
# maths properly") ---

def test_generate_bill_exposes_days_in_period():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 20.0, "2023-01-03": 5.0})
    bill = generate_bill("C1", records, "fixed_1yr")
    assert bill["days_in_period"] == 3


def test_generate_bill_days_times_daily_rate_equals_standing_charge():
    records = make_records({"2023-01-01": 10.0, "2023-01-02": 20.0})
    bill = generate_bill("C1", records, "fixed_1yr")
    assert bill["days_in_period"] * bill["standing_charge_gbp_per_day"] == pytest.approx(
        bill["standing_charge_gbp"]
    )


def test_generate_bill_standing_charge_gbp_per_day_matches_real_rate_table():
    records = make_records({"2023-01-01": 10.0})
    bill = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")
    assert bill["standing_charge_gbp_per_day"] == pytest.approx(
        STANDING_CHARGE_GBP_PER_DAY["electricity"]["resi"]
    )


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
    expected_nc = (kwh / 1000) * 16.0  # gas rate (2023 year-indexed)
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


# ---------------------------------------------------------------------------
# Standing-charge double-count fix (2026-07-11) -- REAL settlement integration.
#
# The bug: generate_bill() recomputed a flat standing charge from
# saas.non_commodity and added it a SECOND time, on top of the year-calibrated
# standing charge that hedged_settlement.py / gas_settlement.py already fold
# into revenue_gbp. Synthetic fixtures (make_records above) never carried the
# settlement standing-charge field, so the unit suite passed while the real
# integration double-charged every resi/SME bill. These tests feed the REAL
# settlement-engine output through generate_bill() -- the path that was never
# exercised -- and assert the standing charge is billed EXACTLY ONCE, equal to
# the settlement engine's own value, with commodity_amount_gbp genuinely pure.
# ---------------------------------------------------------------------------

_JAN_2023_DAYS = 31


def _elec_price_records(dates, spot=80.0):
    return [
        {"settlementDate": d, "settlementPeriod": sp, "systemSellPrice": spot}
        for d in dates
        for sp in range(1, 49)
    ]


def _jan_2023_dates():
    return [f"2023-01-{day:02d}" for day in range(1, _JAN_2023_DAYS + 1)]


def test_generate_bill_does_not_double_count_standing_charge_real_settlement():
    """Resi electricity: bill standing charge == settlement engine's own SC
    (billed once), and commodity_amount_gbp excludes it entirely."""
    from simulation.hedged_settlement import run_hedged_term
    from simulation.policy_costs import get_electricity_standing_charge_per_day

    dates = _jan_2023_dates()
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2023-01-01",
        term_end_date="2023-02-01",
        fixed_tariff_rate_gbp_per_mwh=180.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [250.0] * 48,
        system_price_records=_elec_price_records(dates),
        segment="resi",
    )

    settlement_sc = sum(r["standing_charge_gbp"] for r in records)
    raw_revenue = sum(r["revenue_gbp"] for r in records)

    bill = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")

    # SC billed exactly once, equal to the settlement engine's own year-calibrated value.
    expected_daily_sc = get_electricity_standing_charge_per_day("2023-01-15", "resi")
    assert settlement_sc == pytest.approx(_JAN_2023_DAYS * expected_daily_sc)
    assert bill["standing_charge_gbp"] == pytest.approx(settlement_sc)

    # It is NOT the old flat 2019 rate (0.27/day) -- proves the year-calibrated
    # value now drives the bill, not the superseded flat table.
    assert bill["standing_charge_gbp"] != pytest.approx(_JAN_2023_DAYS * 0.27)

    # commodity_amount_gbp is pure commodity: it excludes the SC that revenue_gbp
    # carried, and commodity + SC reconstructs the raw settlement revenue exactly
    # (no third copy, no missing copy).
    assert bill["commodity_amount_gbp"] == pytest.approx(raw_revenue - settlement_sc)
    assert bill["commodity_amount_gbp"] + bill["standing_charge_gbp"] == pytest.approx(raw_revenue)

    # Per-day breakdown stays internally consistent.
    assert bill["days_in_period"] * bill["standing_charge_gbp_per_day"] == pytest.approx(
        bill["standing_charge_gbp"]
    )


def test_generate_bill_does_not_double_count_standing_charge_real_gas():
    """Resi gas: bill standing charge == run_gas_term's own gas SC (billed once)."""
    from simulation.gas_settlement import run_gas_term
    from simulation.policy_costs import get_gas_standing_charge_per_day

    gas_records = run_gas_term(
        customer_id="C1g",
        term_start="2023-01-01",
        term_end="2023-02-01",
        aq_kwh=12_000,
        unit_rate_gbp_mwh=60.0,
        hedge_fraction=1.0,
        forward_price=55.0,
        monthly_cost_of_capital_gbp=0.0,
        gas_price_records=[
            {"settlementDate": d, "systemSellPrice": 55.0} for d in _jan_2023_dates()
        ],
        segment="resi",
    )

    settlement_sc = sum(r["gas_standing_charge_gbp"] for r in gas_records)
    raw_revenue = sum(r["revenue_gbp"] for r in gas_records)

    bill = generate_bill("C1g", gas_records, "fixed_1yr", segment="resi", commodity="gas")

    expected_daily_sc = get_gas_standing_charge_per_day("2023-01-15", "resi")
    assert settlement_sc == pytest.approx(_JAN_2023_DAYS * expected_daily_sc)
    assert bill["standing_charge_gbp"] == pytest.approx(settlement_sc)
    assert bill["commodity_amount_gbp"] == pytest.approx(raw_revenue - settlement_sc)
    assert bill["commodity_amount_gbp"] + bill["standing_charge_gbp"] == pytest.approx(raw_revenue)


def test_generate_bill_ic_charges_zero_standing_charge_real_settlement():
    """I&C electricity: settlement engine returns SC=0; the bill must too --
    not the silent resi-rate fallback the old code applied."""
    from simulation.hedged_settlement import run_hedged_term

    dates = _jan_2023_dates()
    records = run_hedged_term(
        customer_id="C_IC1",
        term_start_date="2023-01-01",
        term_end_date="2023-02-01",
        fixed_tariff_rate_gbp_per_mwh=180.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=1.0,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [5000.0] * 48,
        system_price_records=_elec_price_records(dates),
        segment="I&C",
    )
    raw_revenue = sum(r["revenue_gbp"] for r in records)

    bill = generate_bill("C_IC1", records, "fixed_1yr", segment="I&C", commodity="electricity")

    assert bill["standing_charge_gbp"] == pytest.approx(0.0)
    assert bill["standing_charge_gbp_per_day"] == pytest.approx(0.0)
    # No SC to subtract -- commodity is the full (SC-free) settlement revenue.
    assert bill["commodity_amount_gbp"] == pytest.approx(raw_revenue)


def test_generate_bill_subtracts_sc_from_commodity_when_field_present():
    """Focused unit check of the primary path with a minimal synthetic record
    that carries the settlement standing-charge field (SC folded into revenue,
    matching real settlement output shape), without a full settlement run."""
    records = [
        {
            "customer_id": "C1",
            "settlement_date": "2023-03-01",
            "settlement_period": 1,
            "consumption_kwh": 100.0,
            "unit_rate_gbp_per_mwh": 200.0,
            # revenue = pure commodity (100/1000*200 = 20.0) + folded SC (0.53)
            "revenue_gbp": 20.0 + 0.53,
            "standing_charge_gbp": 0.53,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        }
    ]
    bill = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")
    assert bill["standing_charge_gbp"] == pytest.approx(0.53)
    assert bill["commodity_amount_gbp"] == pytest.approx(20.0)  # SC subtracted back out
    assert bill["average_unit_rate_gbp_per_mwh"] == pytest.approx(200.0)  # pure commodity rate
