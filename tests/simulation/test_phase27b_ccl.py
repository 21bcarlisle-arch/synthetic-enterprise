"""Phase 27b: CCL (Climate Change Levy) for business electricity customers."""

import pytest
from simulation.policy_costs import (
    get_ccl_per_mwh,
    _CCL_ELECTRICITY_RATE_BY_YEAR,
)


def test_ccl_resi_exempt():
    """Domestic (resi) electricity is exempt from CCL."""
    assert get_ccl_per_mwh("2021-06-01", segment="resi") == 0.0
    assert get_ccl_per_mwh("2016-01-01", segment="resi") == 0.0
    assert get_ccl_per_mwh("2024-01-01", segment="resi") == 0.0


def test_ccl_business_segments_pay_main_rate():
    """SME and I&C customers pay the main CCL rate."""
    rate_2021 = get_ccl_per_mwh("2021-06-01", segment="SME")
    assert rate_2021 == pytest.approx(7.17)
    rate_ic = get_ccl_per_mwh("2021-06-01", segment="I&C")
    assert rate_ic == pytest.approx(7.17)


def test_ccl_april_2020_step_change():
    """CCL electricity rate increased significantly from April 2020."""
    rate_pre = get_ccl_per_mwh("2019-12-01", segment="SME")  # OY 2019-20
    rate_post = get_ccl_per_mwh("2020-04-01", segment="SME")  # OY 2020-21
    assert rate_pre == pytest.approx(6.11)
    assert rate_post == pytest.approx(7.17)
    assert rate_post > rate_pre


def test_ccl_2016_rate():
    """CCL electricity rate for 2016-17 obligation year."""
    assert get_ccl_per_mwh("2016-06-01", segment="SME") == pytest.approx(5.44)


def test_ccl_uses_obligation_year_not_calendar_year():
    """CCL year is Apr-Mar. Jan 2020 is in OY 2019-20 (key 2019), not 2020."""
    jan_2020 = get_ccl_per_mwh("2020-01-15", segment="SME")  # OY 2019-20 → key 2019
    assert jan_2020 == pytest.approx(6.11)  # 2019 rate, not 2020 rate (7.17)


def test_ccl_all_years_defined():
    """All years 2016-2024 have CCL rates defined."""
    for year in range(2016, 2025):
        assert year in _CCL_ELECTRICITY_RATE_BY_YEAR


def test_ccl_settlement_record_has_ccl_field():
    """Settlement records for business customers include ccl_gbp field."""
    from unittest.mock import patch
    from simulation.hedged_settlement import run_hedged_term

    # Simple 1-day price record
    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def flat_shape(date_str):
        return [10.0] * 48  # 10 kWh per period

    records = run_hedged_term(
        "C_IC1", "2021-06-01", "2021-06-02",
        100.0, 80.0, 0.85, 0.0, flat_shape, price_records,
        segment="I&C",
    )
    assert len(records) > 0
    assert "ccl_gbp" in records[0]
    assert records[0]["ccl_gbp"] > 0  # I&C pays CCL


def test_ccl_resi_settlement_record_ccl_zero():
    """Settlement records for resi customers have ccl_gbp = 0."""
    from simulation.hedged_settlement import run_hedged_term as rht
    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def flat_shape(date_str):
        return [10.0] * 48

    records = rht(
        "C1", "2021-06-01", "2021-06-02",
        100.0, 80.0, 0.85, 0.0, flat_shape, price_records,
        segment="resi",
    )
    assert len(records) > 0
    assert "ccl_gbp" in records[0]
    assert records[0]["ccl_gbp"] == pytest.approx(0.0)


def test_ccl_included_in_policy_cost():
    """policy_cost_gbp includes CCL for business customers."""
    from simulation.hedged_settlement import run_hedged_term as rht
    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def flat_shape(date_str):
        return [10.0] * 48

    records = rht(
        "C_IC1", "2021-06-01", "2021-06-02",
        100.0, 80.0, 0.85, 0.0, flat_shape, price_records,
        segment="I&C",
    )
    rec = records[0]
    expected_policy = (
        rec["ro_levy_gbp"] + rec["cfd_levy_gbp"] + rec["ccl_gbp"]
        + rec.get("cm_levy_gbp", 0.0) + rec.get("fit_levy_gbp", 0.0)
        + rec.get("mutualization_levy_gbp", 0.0)
    )
    assert rec["policy_cost_gbp"] == pytest.approx(expected_policy)


def test_ccl_increases_after_2020():
    rate_2019 = get_ccl_per_mwh("2019-06-01", segment="I&C")
    rate_2020 = get_ccl_per_mwh("2020-06-01", segment="I&C")
    assert rate_2020 > rate_2019


def test_ccl_sme_equals_ic_rate():
    rate_sme = get_ccl_per_mwh("2022-01-01", segment="sme")
    rate_ic = get_ccl_per_mwh("2022-01-01", segment="I&C")
    assert rate_sme == pytest.approx(rate_ic)


def test_ccl_rate_positive_for_all_business_years():
    for year in range(2016, 2025):
        rate = get_ccl_per_mwh(f"{year}-06-01", segment="I&C")
        assert rate > 0


# 13. CCL rate for electricity is positive for I&C 2023
def test_ccl_ic_2023_positive():
    from simulation.policy_costs import get_ccl_per_mwh
    rate = get_ccl_per_mwh("2023-06-01", segment="I&C")
    assert rate > 0.0


# 14. CCL electricity dict has at least one year entry
def test_ccl_electricity_rate_table_nonempty():
    from simulation.policy_costs import _CCL_ELECTRICITY_RATE_BY_YEAR
    assert len(_CCL_ELECTRICITY_RATE_BY_YEAR) > 0


# 15. CCL rate for 2016 is non-negative
def test_ccl_2016_nonnegative():
    from simulation.policy_costs import get_ccl_per_mwh
    rate = get_ccl_per_mwh("2016-01-01", segment="I&C")
    assert rate >= 0.0
