#!/usr/bin/env python3
"""Generate real per-fuel consumption series for the customer portal USAGE panel.

CUSTOMER_360_REDESIGN.md item 1 (USAGE VIZ) -- "the missing core noun":
site/data/customers/{cid}.json previously carried only money (invoices),
never the underlying kWh. This module patches in a real "consumption" key,
sourced entirely from data the simulation already produces -- no new
consumption model, no fabrication:

- Monthly kWh per fuel leg: aggregated from docs/reports/run_output_latest.json's
  "bills" list (total_consumption_kwh per settlement period) -- the exact same
  real figure that already flows into site/state/billing_ledger.json invoices.
- Daily kWh + load-shape (weekday/weekend/seasonal average 48-period profile):
  derived from sim/hh_data/{cid}.csv, the simulation's real half-hourly
  settlement output, for the customers that actually have it.

Daily/HH detail is genuinely not available for every customer, and that is
not a plumbing gap to "fix" -- in the real UK market, gas is AQ/EAC-read
based and never HH-settled. Electricity is more nuanced than this module's
earlier docstring claimed (corrected 2026-07-10, director challenge --
docs/market_research/ASSUMPTIONS.md "Smart Meter Half-Hourly Data Access:
Billing vs. Settlement Consent"): a DCC-enrolled smart meter in smart mode
(~90% of installed smart meters, DESNZ Q4 2024) routinely sends reads to
its OWN supplier for billing purposes BY DEFAULT, not as a rarely-taken
opt-in -- the only real "opt-out" is losing/declining smart functionality
(traditional mode). A separate, genuinely narrower opt-in (domestic) /
opt-out (microbusiness) consent regime does exist for using HH-granularity
data for market-wide SETTLEMENT purposes (Ofgem, 25 Jun 2019), but its real
uptake rate is unpublished, and Ofgem/Elexon's MHHS programme is retiring
that mechanism entirely by migrating every customer to universal HH
settlement (began Sept 2025, due complete May 2027) -- not a per-customer
consent choice. sim/hh_data/ having a CSV for only C7/C8/C9 + every
HH-metered I&C account is therefore a SIMULATION DATA-AVAILABILITY choice
(not every customer's full half-hourly shape is simulated), not a modelled
real-world consent gate. Every other customer gets monthly bars only --
consumption["has_hh_data"] says which, honestly, rather than a fabricated
daily curve.

Output: patches a "consumption" key into each existing
site/data/customers/{cid}.json (same read-existing/patch-key pattern as
tools/generate_invoice_data.py).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"
HH_DATA_DIR = PROJECT / "sim" / "hh_data"

# Standard meteorological seasons (UK convention).
_SEASON_MONTHS = {
    "winter": {12, 1, 2},
    "spring": {3, 4, 5},
    "summer": {6, 7, 8},
    "autumn": {9, 10, 11},
}


def _monthly_from_bills(bills):
    """{cid: [{"month": "YYYY-MM", "kwh": x}, ...]}, sorted by month.

    Real settlement consumption, aggregated by calendar month of period_end.
    """
    by_cid = defaultdict(lambda: defaultdict(float))
    for b in bills:
        cid = b.get("customer_id")
        period_end = b.get("period_end")
        if not cid or not period_end:
            continue
        month = period_end[:7]
        by_cid[cid][month] += b.get("total_consumption_kwh", 0.0) or 0.0
    out = {}
    for cid, months in by_cid.items():
        out[cid] = [
            {"month": m, "kwh": round(months[m], 1)} for m in sorted(months)
        ]
    return out


def _read_hh_rows(cid):
    path = HH_DATA_DIR / (cid + ".csv")
    if not path.exists():
        return None
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        return list(reader)


def load_shape_and_daily(cid):
    """Real daily totals + weekday/weekend/seasonal average 48-period shape.

    Returns None if sim/hh_data/{cid}.csv does not exist (no HH data for
    this customer -- an honest gap, not computed here).
    """
    rows = _read_hh_rows(cid)
    if not rows:
        return None

    daily = {}
    weekday_sum = [0.0] * 48
    weekend_sum = [0.0] * 48
    weekday_n = 0
    weekend_n = 0
    season_sum = {s: [0.0] * 48 for s in _SEASON_MONTHS}
    season_n = {s: 0 for s in _SEASON_MONTHS}

    for row in rows:
        if len(row) < 49:
            continue
        date_str = row[0]
        try:
            periods = [float(v) for v in row[1:49]]
            d = date.fromisoformat(date_str)
        except ValueError:
            continue
        daily[date_str] = round(sum(periods), 2)

        if d.weekday() >= 5:
            weekend_sum = [a + b for a, b in zip(weekend_sum, periods)]
            weekend_n += 1
        else:
            weekday_sum = [a + b for a, b in zip(weekday_sum, periods)]
            weekday_n += 1
        for season, months in _SEASON_MONTHS.items():
            if d.month in months:
                season_sum[season] = [a + b for a, b in zip(season_sum[season], periods)]
                season_n[season] += 1
                break

    weekday_avg = [round(v / weekday_n, 4) for v in weekday_sum] if weekday_n else [0.0] * 48
    weekend_avg = [round(v / weekend_n, 4) for v in weekend_sum] if weekend_n else [0.0] * 48
    seasonal_avg = {
        s: ([round(v / season_n[s], 4) for v in season_sum[s]] if season_n[s] else [0.0] * 48)
        for s in _SEASON_MONTHS
    }

    return {
        "daily_kwh": daily,
        "weekday_avg_kwh": weekday_avg,
        "weekend_avg_kwh": weekend_avg,
        "seasonal_avg_kwh": seasonal_avg,
    }


def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    run = json.loads(path.read_text())
    bills = run.get("bills", [])
    monthly_by_cid = _monthly_from_bills(bills)

    updated = 0
    for cid, monthly in monthly_by_cid.items():
        cust_file = CUSTOMERS_DIR / (cid + ".json")
        if not cust_file.exists():
            continue
        existing = json.loads(cust_file.read_text())
        shape = load_shape_and_daily(cid)
        consumption = {
            "unit": "kWh",
            "monthly": monthly,
            "has_hh_data": shape is not None,
        }
        if shape is not None:
            consumption["daily_kwh"] = shape["daily_kwh"]
            consumption["load_shape"] = {
                "weekday_avg_kwh": shape["weekday_avg_kwh"],
                "weekend_avg_kwh": shape["weekend_avg_kwh"],
                "seasonal_avg_kwh": shape["seasonal_avg_kwh"],
            }
        existing["consumption"] = consumption
        cust_file.write_text(json.dumps(existing, indent=2))
        updated += 1

    print("Updated", updated, "customer files with consumption data")
    return updated


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
