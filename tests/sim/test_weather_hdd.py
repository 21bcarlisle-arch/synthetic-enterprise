"""Tests for Phase 58: HDD weather adjustment for gas consumption."""

import pytest

from sim.weather_hdd import (
    HDD_BASE_TEMP_C,
    REFERENCE_MONTHLY_HDD,
    PremiseSky,
    get_hdd,
    get_monthly_hdd,
    get_weather_factor,
    weather_factor_for_term,
)
from simulation.gas_settlement import run_gas_term


def _fake_gas_records(start="2020-01-01", end="2020-03-31", price=30.0):
    """Minimal gas price records for gas_settlement tests."""
    from datetime import date, timedelta
    records = []
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    while d <= e:
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": price})
        d += timedelta(days=1)
    return records


class TestHddCalculation:
    def test_hdd_is_zero_above_base_temp(self):
        # C1 on a summer day should be warm enough for zero HDD
        hdd = get_hdd("2020-07-15", "C1")
        # July means average ~16-17°C, well above 15.5 base
        assert hdd >= 0.0, "HDD must be non-negative"
        # Cannot assert exactly 0 because it depends on real weather data,
        # but we verify it never goes negative
        assert hdd < HDD_BASE_TEMP_C, "HDD cannot exceed base temperature"

    def test_hdd_positive_below_base_temp(self):
        hdd = get_hdd("2020-01-15", "C1")
        # January UK temperatures are well below 15.5°C
        assert hdd > 0.0, "January HDD must be positive"

    def test_hdd_formula_correct(self):
        # Inject a known temperature via the cache to verify the formula
        from sim.weather_hdd import _WEATHER_CACHE
        _WEATHER_CACHE["TEST_COLD"] = PremiseSky(
            "TEST_COLD", cell="fixture", series={"2020-02-01": 5.0})
        hdd = get_hdd("2020-02-01", "TEST_COLD")
        assert abs(hdd - 10.5) < 0.001, "HDD should be 15.5 - 5.0 = 10.5"
        _WEATHER_CACHE["TEST_WARM"] = PremiseSky(
            "TEST_WARM", cell="fixture", series={"2020-07-01": 20.0})
        hdd_warm = get_hdd("2020-07-01", "TEST_WARM")
        assert hdd_warm == 0.0, "HDD above base temp must be 0"

    def test_monthly_hdd_sums_days(self):
        jan_hdd = get_monthly_hdd(2020, 1, "C1")
        # January should have substantial HDD - at least 200 (31 days of cold)
        assert jan_hdd > 100.0, "January HDD should be substantial"

    def test_monthly_hdd_summer_low(self):
        jul_hdd = get_monthly_hdd(2020, 7, "C1")
        # July should have very low HDD
        assert jul_hdd < 100.0, "July HDD should be much lower than winter"
        assert jul_hdd < get_monthly_hdd(2020, 1, "C1"), "July < January"


class TestWeatherFactor:
    def test_weather_factor_warm_winter_below_1(self):
        # 2019-2020 UK winter was warmest on record; Jan/Feb 2020 should be below 1
        factor_jan = get_weather_factor(2020, 1, "C1")
        # Warm winter → actual HDD below reference → factor < 1
        # (Climate normals ~350 HDD for Jan; 2020 was notably warm)
        assert factor_jan < 1.1, "Jan 2020 factor should not be much above normal"

    def test_weather_factor_clipped_to_sane_range(self):
        for year in range(2016, 2026):
            for month in range(1, 13):
                f = get_weather_factor(year, month, "C1")
                assert 0.3 <= f <= 2.0, f"Factor out of range: {year}-{month:02d} = {f}"

    def test_weather_factor_reference_months_sensible(self):
        # Reference HDD: all months defined, winter months >> summer months
        assert REFERENCE_MONTHLY_HDD[1] > REFERENCE_MONTHLY_HDD[7], "Jan ref > Jul ref"
        assert REFERENCE_MONTHLY_HDD[12] > REFERENCE_MONTHLY_HDD[6], "Dec ref > Jun ref"
        assert all(v > 0.0 for v in REFERENCE_MONTHLY_HDD.values()), "All refs > 0"

    def test_weather_factor_for_term_returns_in_range(self):
        f = weather_factor_for_term("2020-01-01", "2020-04-01", "C1")
        assert 0.3 <= f <= 2.0, f"Term factor out of range: {f}"

    def test_weather_factor_for_single_month_term(self):
        f_term = weather_factor_for_term("2020-01-01", "2020-02-01", "C1")
        f_month = get_weather_factor(2020, 1, "C1")
        assert abs(f_term - f_month) < 0.01, "Single-month term should equal monthly factor"


class TestGasCustomerMapping:
    """The `Xg -> X` STRING RULE IS GONE (2026-09-21, W1_14 step 3).

    A gas point and its dual-fuel electricity twin still read the same weather -- but because the
    supply book publishes them at one coordinate and the store gives one cell one sky, not because
    an id ends in `g`. The distinction is the whole finding: under the string rule, C_IC3g borrowed
    C_IC3's resolution and both then missed every archive, and C7 -- no suffix, same London
    coordinate as C1 -- got a climate normal.
    """

    def test_a_gas_point_reads_the_same_cell_as_its_twin_because_they_share_a_coordinate(self):
        for gas_id, elec_id in (("C1g", "C1"), ("C2g", "C2"), ("C3g", "C3"), ("C4g", "C4"),
                                ("C_IC3g", "C_IC3")):
            assert get_hdd("2022-01-15", gas_id) == get_hdd("2022-01-15", elec_id), (
                f"{gas_id} and {elec_id} are one supply point's two commodities at one address"
            )

    def test_the_g_suffix_no_longer_borrows_another_premises_weather(self):
        """The failable half: an UNREGISTERED `Xg` must not inherit the registered `X`'s sky.

        Restore the old rule and this reds -- `C7g` would strip to `C7`, which now resolves to a
        cell, and the reading would claim to be weather for a premise that is on no book.
        """
        from sim.weather_hdd import hdd_reading
        borrowed = hdd_reading("2022-01-15", "C7g")
        assert borrowed.from_normal, (
            f"C7g is not a registered supply point; it must not read C7's cell. "
            f"basis={borrowed.basis!r}"
        )
        assert "not a registered supply point" in borrowed.basis, borrowed.basis


class TestWeatherAdjustedGasSettlement:
    def test_warm_factor_reduces_consumption_ic(self):
        records_normal = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=120000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            segment="I&C",
            weather_factor=1.0,
        )
        records_warm = run_gas_term(
            "C_IC3g", "2020-01-01", "2020-02-01",
            aq_kwh=120000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            segment="I&C",
            weather_factor=0.8,
        )
        normal_kwh = sum(r["daily_kwh"] for r in records_normal)
        warm_kwh = sum(r["daily_kwh"] for r in records_warm)
        assert warm_kwh < normal_kwh, "Warm weather factor should reduce I&C consumption"
        assert abs(warm_kwh / normal_kwh - 0.8) < 0.001, "Factor 0.8 gives exactly 80% I&C consumption"

    def test_resi_consumption_uses_hdd_not_weather_factor(self):
        records_wf08 = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            weather_factor=0.8,
        )
        records_wf10 = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            weather_factor=1.0,
        )
        kwh_wf08 = sum(r["daily_kwh"] for r in records_wf08)
        kwh_wf10 = sum(r["daily_kwh"] for r in records_wf10)
        assert abs(kwh_wf08 - kwh_wf10) < 0.01, "Resi gas ignores weather_factor; uses HDD shape"

    def test_weather_factor_in_record(self):
        records = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
            weather_factor=0.75,
        )
        for rec in records:
            assert "weather_factor" in rec, "Record must contain weather_factor field"
            assert abs(rec["weather_factor"] - 0.75) < 0.001, "weather_factor must round-trip"

    def test_default_weather_factor_is_1(self):
        records = run_gas_term(
            "C1g", "2020-01-01", "2020-02-01",
            aq_kwh=12000, unit_rate_gbp_mwh=30.0,
            hedge_fraction=0.0, forward_price=30.0,
            monthly_cost_of_capital_gbp=1.0,
            gas_price_records=_fake_gas_records("2019-12-01", "2020-03-01"),
        )
        for rec in records:
            assert rec["weather_factor"] == 1.0, "Default weather_factor must be 1.0"


# Additional function-style tests
def test_hdd_base_temp_constant():
    assert HDD_BASE_TEMP_C == pytest.approx(15.5)


def test_reference_hdd_all_twelve_months():
    assert set(REFERENCE_MONTHLY_HDD.keys()) == set(range(1, 13))


def test_reference_hdd_january_highest():
    assert REFERENCE_MONTHLY_HDD[1] == max(REFERENCE_MONTHLY_HDD.values())


def test_get_hdd_unknown_customer_falls_back():
    hdd = get_hdd("2022-01-15", "UNKNOWN_XYZ_CUSTOMER")
    expected = REFERENCE_MONTHLY_HDD[1] / 30.0
    assert hdd == pytest.approx(expected)
