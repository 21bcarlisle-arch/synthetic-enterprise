"""Tests for sim/gas_prices_history.py -- pure data-processing functions.

Tests only the pure functions (parse_fred_csv, expand_to_daily) that have no
network or file I/O dependencies. fetch_fred_csv and load_nbp_history are omitted
(they require external resources).
"""

import pytest

from sim.gas_prices_history import (
    GBPUSD,
    MWH_PER_MMBTU,
    expand_to_daily,
    parse_fred_csv,
)

# ── parse_fred_csv ──────────────────────────────────────────────────────────

def test_parse_fred_csv_returns_dict():
    raw = "DATE,PNGASEUUSDM\n2024-01-01,10.0\n2024-02-01,12.0\n"
    result = parse_fred_csv(raw)
    assert isinstance(result, dict)


def test_parse_fred_csv_keys_are_year_month():
    raw = "DATE,PNGASEUUSDM\n2024-01-01,10.0\n"
    result = parse_fred_csv(raw)
    assert "2024-01" in result


def test_parse_fred_csv_converts_usd_mmbtu_to_gbp_mwh():
    # 10 USD/MMBtu -> 10 / (1.28 * 0.29307) = ~26.67 GBP/MWh
    raw = "DATE,PNGASEUUSDM\n2024-01-01,10.0\n"
    result = parse_fred_csv(raw)
    expected = round(10.0 / (GBPUSD * MWH_PER_MMBTU), 4)
    assert abs(result["2024-01"] - expected) < 0.01


def test_parse_fred_csv_skips_non_numeric_values():
    raw = "DATE,PNGASEUUSDM\n2024-01-01,10.0\n2024-02-01,.\n"
    result = parse_fred_csv(raw)
    assert "2024-01" in result
    assert "2024-02" not in result


def test_parse_fred_csv_empty_data_returns_empty_dict():
    raw = "DATE,PNGASEUUSDM\n"
    result = parse_fred_csv(raw)
    assert result == {}


def test_parse_fred_csv_multiple_months():
    raw = "DATE,PNGASEUUSDM\n2024-01-01,10.0\n2024-02-01,12.0\n2024-03-01,8.0\n"
    result = parse_fred_csv(raw)
    assert len(result) == 3
    assert "2024-01" in result
    assert "2024-02" in result
    assert "2024-03" in result


# ── expand_to_daily ─────────────────────────────────────────────────────────

def test_expand_to_daily_one_month():
    prices = {"2024-01": 25.0}
    records = expand_to_daily(prices, "2024-01-01", "2024-01-31")
    assert len(records) == 31


def test_expand_to_daily_record_structure():
    prices = {"2024-01": 25.0}
    records = expand_to_daily(prices, "2024-01-01", "2024-01-01")
    assert len(records) == 1
    assert records[0]["settlementDate"] == "2024-01-01"
    assert records[0]["systemSellPrice"] == 25.0


def test_expand_to_daily_skips_days_without_monthly_price():
    prices = {"2024-01": 25.0}  # no 2024-02 data
    records = expand_to_daily(prices, "2024-01-01", "2024-02-29")
    # Only January days (31) should appear
    assert all(r["settlementDate"].startswith("2024-01") for r in records)
    assert len(records) == 31


def test_expand_to_daily_all_same_price_in_month():
    prices = {"2024-01": 30.0}
    records = expand_to_daily(prices, "2024-01-01", "2024-01-31")
    assert all(r["systemSellPrice"] == 30.0 for r in records)


def test_expand_to_daily_sorted_by_date():
    prices = {"2024-01": 25.0, "2024-02": 27.0}
    records = expand_to_daily(prices, "2024-01-01", "2024-02-29")
    dates = [r["settlementDate"] for r in records]
    assert dates == sorted(dates)


# ── Constants ───────────────────────────────────────────────────────────────

def test_gbpusd_reasonable():
    assert 1.0 < GBPUSD < 2.0


def test_mwh_per_mmbtu_correct():
    # 1 MMBtu = 0.29307 MWh (standard conversion)
    assert abs(MWH_PER_MMBTU - 0.29307) < 0.00001


# ── the record reaches back far enough to price the first day (2026-10-06) ─────

def test_a_day_one_gas_contract_prices_off_history_it_could_have_held():
    """A founder acquired on the simulation's first day prices off the 90 days BEFORE it. The
    record used to start that same day, so the lookback was empty and `generate_forward_price`
    raised (and `run_phase2b` fell back to pricing the term off the 90 days AFTER it). Keyed to
    the founders' own acquisition year, not to a literal, so a world that starts earlier
    re-asks the question rather than passing on today's answer."""
    import datetime as dt

    from sim.forward_curve import generate_forward_price
    from sim.gas_prices_history import RECORD_START, load_nbp_history
    from simulation.live_population import FOUNDER_ACQUISITION_YEAR

    first_day = dt.date(FOUNDER_ACQUISITION_YEAR, 1, 1)
    records = load_nbp_history()
    assert records[0]["settlementDate"] == RECORD_START, (
        "the committed record and its generator disagree about where history starts")
    assert dt.date.fromisoformat(RECORD_START) <= first_day - dt.timedelta(days=90)

    price = generate_forward_price(first_day.isoformat(), records, fuel="gas")
    before_only = [r for r in records if r["settlementDate"] < first_day.isoformat()]
    assert price == generate_forward_price(first_day.isoformat(), before_only, fuel="gas"), (
        "the day-one price read a record on or after its own day")
