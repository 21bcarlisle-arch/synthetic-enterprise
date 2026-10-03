"""The forward price feed starts the day after the record ends, not on the next 1 January.

The record ends 2025-06-07. The synthetic series used to start at `latest.year + 1`, so a forward
run had no electricity price from 8 June to 31 December 2025 -- a seven-month hole its first
forward bill would land in. The control is on DAYS, both fuels, so a feed that starts a month late
fails it as surely as one that starts seven months late.
"""
from __future__ import annotations

import datetime as dt

from simulation.run_scenario import build_extended_price_feeds

RECORD_END = dt.date(2025, 6, 7)


def _history():
    elec, gas = [], []
    day = dt.date(2025, 5, 1)
    while day <= RECORD_END:
        elec += [{"settlementDate": day.isoformat(), "settlementPeriod": p, "systemSellPrice": 80.0}
                 for p in range(1, 49)]
        gas.append({"settlementDate": day.isoformat(), "systemSellPrice": 30.0})
        day += dt.timedelta(days=1)
    return elec, gas


def test_every_day_after_the_record_has_a_full_electricity_day_and_a_gas_price():
    elec, gas = build_extended_price_feeds(*_history(), year_from=2026, year_to=2026)
    elec_days: dict[str, int] = {}
    for r in elec:
        elec_days[r["settlementDate"]] = elec_days.get(r["settlementDate"], 0) + 1
    gas_days = {r["settlementDate"] for r in gas}
    day = RECORD_END + dt.timedelta(days=1)
    missing = []
    while day <= dt.date(2026, 12, 31):
        if elec_days.get(day.isoformat()) != 48 or day.isoformat() not in gas_days:
            missing.append(day.isoformat())
        day += dt.timedelta(days=1)
    assert not missing, f"{len(missing)} forward days lack a price, first {missing[:3]}"


def test_the_record_is_not_overwritten_by_the_synthetic_series():
    elec, _ = build_extended_price_feeds(*_history(), year_from=2026, year_to=2026)
    on_record = [r for r in elec if r["settlementDate"] <= RECORD_END.isoformat()]
    assert all(r["systemSellPrice"] == 80.0 for r in on_record)
    assert len(on_record) == 48 * ((RECORD_END - dt.date(2025, 5, 1)).days + 1)
