"""Foreground/background pre-fetch of the full Elexon SSP history into sim/cache/.

Populates sim/cache/elexon_ssp_full.json so simulation/run_phase2b.py (and the
2a/2a_repriced scripts) get a cache hit instead of re-fetching ~3,500 days of
settlement-price data one HTTP request at a time during the live run.

Range matches simulation/run_phase2b.py's fetch_start/REPORT_END derivation:
EARLIEST_SSP_DATE (2015-11-07) to REPORT_END (2025-06-07).
"""

from datetime import datetime, timedelta

from sim.cache_store import write_cached_prices
from sim.system_prices_history import get_system_prices_range

FETCH_START = "2015-11-07"
FETCH_END = "2025-06-07"
PROGRESS_EVERY_DAYS = 100


def main():
    start = datetime.strptime(FETCH_START, "%Y-%m-%d")
    end = datetime.strptime(FETCH_END, "%Y-%m-%d")
    total_days = (end - start).days + 1

    print(f"Pre-fetching Elexon SSP records: {FETCH_START} to {FETCH_END} ({total_days} days)...")

    records = []
    current = start
    day_index = 0
    while current <= end:
        chunk_end = min(current + timedelta(days=PROGRESS_EVERY_DAYS - 1), end)
        chunk = get_system_prices_range(current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d"))
        records.extend(chunk)
        day_index += (chunk_end - current).days + 1
        print(f"  ... {day_index}/{total_days} days fetched, {len(records):,} records so far")
        current = chunk_end + timedelta(days=1)

    write_cached_prices(records, "elexon_ssp_full.json")
    print(f"Done. Wrote {len(records):,} records to sim/cache/elexon_ssp_full.json")


if __name__ == "__main__":
    main()
