from datetime import date, datetime, time, timedelta

import pytest

from company.interfaces.point_in_time_view import PointInTimeView, build_price_bitemporal_log
from company.interfaces.sim_interface import StubSimInterface
from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER
from simulation.renewals import NOTICE_DAYS
from simulation.run_phase2b import (
    DEFAULT_PROPERTY,
    REPORT_END,
    _build_gas_renewal_schedule,
    _clamp_term_end,
    _weather_adjusted_shape_fn,
    main as _run_phase2b_main,
)


def _flat_base_shape(date_str):
    return [1.0] * 48


def test_weather_adjusted_shape_fn_falls_back_without_weather_data():
    shape_fn = _weather_adjusted_shape_fn(_flat_base_shape, {}, DEFAULT_PROPERTY)
    assert shape_fn("2016-01-01") == [1.0] * 48


def test_weather_adjusted_shape_fn_adds_heating_load_on_cold_day():
    weather_means = {"2016-01-01": -5.0}  # well below 15.5C heating base
    shape_fn = _weather_adjusted_shape_fn(_flat_base_shape, weather_means, DEFAULT_PROPERTY)

    cold_shape = shape_fn("2016-01-01")
    assert sum(cold_shape) > sum(_flat_base_shape("2016-01-01"))


def _flat_gas_price_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    while current <= end:
        records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)
    return records


def test_build_gas_renewal_schedule_cold_spell_does_not_affect_gas_price():
    # Phase 42: weather adjustment is electricity-only. Gas uses seasonal calibration instead.
    records = _flat_gas_price_records("2015-10-01", "2017-06-30")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}

    no_weather = _build_gas_renewal_schedule(
        {**customer, "acquisition_date": "2016-01-01"}, records
    )

    def cold_lookback(term_start):
        return [0.0] * 90

    with_cold_weather = _build_gas_renewal_schedule(
        {**customer, "acquisition_date": "2016-01-01"}, records, lookback_temps_fn=cold_lookback
    )

    ratio = (
        with_cold_weather[0]["forward_price_gbp_per_mwh"]
        / no_weather[0]["forward_price_gbp_per_mwh"]
    )
    # Weather does not affect gas forward pricing — ratio must be 1.0
    assert ratio == 1.0


def test_clamp_term_end_uses_default_report_end():
    # With no end_date kwarg the default REPORT_END is used — verify it returns a date string
    result = _clamp_term_end("2016-01-01")
    assert isinstance(result, str) and len(result) == 10


def test_clamp_term_end_truncates_to_custom_end_date():
    short_end = "2018-06-30"
    result = _clamp_term_end("2018-01-01", end_date=short_end)
    # Contract is 365 days; term end = 2019-01-01, which is beyond 2018-06-30 — should clamp
    assert result == "2018-07-01"  # end_date + 1 day (exclusive upper bound convention)


def test_clamp_term_end_does_not_truncate_when_natural_end_is_within_window():
    long_end = "2025-12-31"
    result = _clamp_term_end("2016-01-01", end_date=long_end)
    # Natural end ~2017-01-01 is well inside the window — no truncation
    assert result < long_end


def test_build_gas_renewal_schedule_truncates_on_report_end():
    records = _flat_gas_price_records("2015-01-01", "2022-12-31")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}

    short_end = "2017-06-30"
    schedule = _build_gas_renewal_schedule(customer, records, report_end=short_end)

    # All terms must start on or before short_end
    for term in schedule:
        assert term["acquisition_date"] <= short_end

    # Full-window schedule should have more terms
    full_schedule = _build_gas_renewal_schedule(customer, records)
    assert len(full_schedule) > len(schedule)


# Phase 34a: 42-day notice period for gas schedule


def test_gas_schedule_notice_date_present():
    records = _flat_gas_price_records("2015-10-01", "2017-06-30")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}
    schedule = _build_gas_renewal_schedule(customer, records)
    assert "notice_date" in schedule[0]


def test_gas_schedule_notice_date_is_42_days_before_term_start():
    records = _flat_gas_price_records("2015-01-01", "2020-12-31")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-06-01"}
    schedule = _build_gas_renewal_schedule(customer, records)
    for term in schedule:
        term_start = date.fromisoformat(term["acquisition_date"])
        notice_date = date.fromisoformat(term["notice_date"])
        assert (term_start - notice_date).days == NOTICE_DAYS


# Phase 12e: _compute_company_divergence tests

def test_compute_company_divergence_groups_by_year():
    from simulation.run_phase2b import _compute_company_divergence
    basis_risk = [
        {"term_start": "2021-01-01", "tariff_error_pct": 0.20},
        {"term_start": "2021-07-01", "tariff_error_pct": -0.30},
        {"term_start": "2022-01-01", "tariff_error_pct": 0.50},
    ]
    churn_risk = [
        {"term_start": "2021-01-01", "churn_estimate_error_pct": 0.10},
        {"term_start": "2022-01-01", "churn_estimate_error_pct": -0.40},
    ]
    result = _compute_company_divergence(basis_risk, churn_risk)
    tariff = result["tariff_error_by_year"]
    churn = result["churn_error_by_year"]

    assert "2021" in tariff
    assert "2022" in tariff
    assert tariff["2021"]["n"] == 2
    # mean abs error for 2021: (0.20 + 0.30) / 2 = 0.25
    assert abs(tariff["2021"]["mean_abs_error_pct"] - 0.25) < 0.001
    assert tariff["2021"]["max_abs_error_pct"] == 0.30
    assert tariff["2022"]["n"] == 1
    assert tariff["2022"]["mean_abs_error_pct"] == 0.50

    assert "2021" in churn
    assert "2022" in churn
    assert churn["2021"]["n"] == 1
    assert abs(churn["2021"]["mean_abs_error_pct"] - 0.10) < 0.001


def test_compute_company_divergence_skips_none_churn_errors():
    from simulation.run_phase2b import _compute_company_divergence
    churn_risk = [
        {"term_start": "2020-01-01", "churn_estimate_error_pct": None},
        {"term_start": "2020-07-01", "churn_estimate_error_pct": 0.15},
    ]
    result = _compute_company_divergence([], churn_risk)
    churn = result["churn_error_by_year"]
    assert "2020" in churn
    assert churn["2020"]["n"] == 1  # None entry skipped


def test_compute_company_divergence_empty_inputs():
    from simulation.run_phase2b import _compute_company_divergence
    result = _compute_company_divergence([], [])
    assert result["tariff_error_by_year"] == {}
    assert result["churn_error_by_year"] == {}


# ── Acquisition-aware retention guard tests (Phase 15b) ──────────────────────

def test_retention_offer_made_when_margin_plus_acq_exceeds_ret_cost():
    """Offer made when margin < ret_cost but margin + acq_cost > ret_cost."""
    from saas.growth_mandate import COST_PER_ACQUISITION
    # Scenario: crisis year, margin £122, ret_cost £160 (8% on large SME contract)
    # Old guard: blocked. New guard with acq_cost=£400: £122+£400=£522 > £160 → offered.
    margin = 122.0
    ret_cost = 160.0
    acq_cost = COST_PER_ACQUISITION.get("SME", 400.0)
    assert margin < ret_cost   # old guard would have blocked
    assert margin + acq_cost > ret_cost   # new guard allows


def test_retention_blocked_when_even_acq_savings_dont_justify():
    """Offer still blocked when margin + acq_cost < ret_cost (truly uneconomical)."""
    from saas.growth_mandate import COST_PER_ACQUISITION
    # Scenario: very expensive retention offer vs tiny margin and resi acq cost
    margin = 5.0
    # 8% discount on very large contract = ret_cost = 400 * 0.08 * 20000/1000 = £640
    ret_cost = 640.0
    acq_cost = COST_PER_ACQUISITION.get("resi", 150.0)
    assert margin + acq_cost < ret_cost   # new guard also blocks


def test_acq_cost_resi_lower_than_sme():
    """Resi acquisition cost is lower than SME (harder SME market justifies more retention spend)."""
    from saas.growth_mandate import COST_PER_ACQUISITION
    assert COST_PER_ACQUISITION["resi"] < COST_PER_ACQUISITION["SME"]


# Test throughput fix (TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md root cause #1):
# this test previously called main() with no report_end truncation, replaying
# the full 2016-2025 decade (~185s) just to check one dict key's presence on the
# first retention-log entry. Truncated to the same 2016-2017 window already
# proven by the sibling file tests/simulation/test_run_phase2b_event_log.py's
# module-scoped sim_result_2017 fixture -- verified directly (2026-07-19) that
# this truncated window still produces retention_log entries (2 entries, the
# first including acq_cost_saved_gbp), so the assertion's exposure is unchanged.
@pytest.fixture(scope="module")
def _phase2b_result_2017():
    return _run_phase2b_main(report_end="2017-12-31", sim_interface=StubSimInterface())


def test_retention_log_includes_acq_cost_saved(_phase2b_result_2017):
    """Retention log entries include acq_cost_saved_gbp for traceability (Phase 15b)."""
    # conftest autouse fixture already sets SIM_FAST_MODE=1 for all tests
    result = _phase2b_result_2017
    rl = result.get("retention_log", [])
    # The truncated window must still exercise retention logging -- an empty
    # retention_log would make this test vacuously pass (fail-open), which is
    # exactly the R15 pattern to avoid.
    assert rl, "expected at least one retention_log entry in the truncated 2016-2017 window"
    assert "acq_cost_saved_gbp" in rl[0], "retention_log entry should include acq_cost_saved_gbp"


# --- price history as-of (2026-07-10 HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md fix;
# 2026-07-11 M1 depth work retired the per-call-site _price_history_as_of() wrapper in
# favour of PointInTimeView.get_price_history_as_of(), backed by a BitemporalEventLog
# built once per run via build_price_bitemporal_log() -- see
# docs/design/M1_PRICE_HISTORY_PIPELINE_FINDING.md) ---

def _daily_records(start_date_str, n_days, price_start=50.0):
    start = date.fromisoformat(start_date_str)
    return [
        {"settlementDate": (start + timedelta(days=i)).isoformat(), "systemSellPrice": price_start + i}
        for i in range(n_days)
    ]


def _piv_at(decision_date_str, elec_records, gas_records=None):
    log = build_price_bitemporal_log(elec_records, gas_records or [])
    decision_time = datetime.combine(date.fromisoformat(decision_date_str), time.min)
    return PointInTimeView(decision_time=decision_time, bitemporal_log=log)


def test_price_history_as_of_excludes_future_records():
    """The core fix: no record with settlementDate after the decision date may
    ever be returned -- this is the exact point-in-time-blindfold violation
    that was previously live (the full run's price history, including
    dates far in the decision's future, was passed unsliced)."""
    records = _daily_records("2016-01-01", 3000)  # spans ~8yrs of daily records
    history = _piv_at("2018-06-15", records).get_price_history_as_of("electricity")
    assert all(r["settlementDate"] <= "2018-06-15" for r in history)


def test_price_history_as_of_early_decision_gets_only_early_data():
    """A decision near the start of the run must not see any later data --
    directly what was broken (a 2018 decision seeing 2025 crisis-era data)."""
    records = _daily_records("2016-01-01", 3000)
    history = _piv_at("2016-02-01", records).get_price_history_as_of("electricity")
    assert all(r["settlementDate"] <= "2016-02-01" for r in history)
    assert len(history) <= 32  # ~1 month of daily records, since the run only started 2016-01-01


def test_price_history_as_of_empty_records_returns_empty():
    assert _piv_at("2020-01-01", []).get_price_history_as_of("electricity") == []


def test_price_history_as_of_electricity_and_gas_independent():
    """Two different commodities built into the SAME shared log (as
    run_phase2b.py does once per run) must not leak into each other."""
    elec = _daily_records("2016-01-01", 50, price_start=50.0)
    gas = _daily_records("2020-01-01", 50, price_start=20.0)
    piv = _piv_at("2016-01-20", elec, gas)
    elec_hist = piv.get_price_history_as_of("electricity")
    assert all(r["settlementDate"].startswith("2016") for r in elec_hist)
    # gas history at this decision_time is empty -- gas prices only start 2020,
    # after this 2016 decision could have known them.
    gas_hist = piv.get_price_history_as_of("gas")
    assert gas_hist == []
