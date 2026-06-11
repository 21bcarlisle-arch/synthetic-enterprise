"""One-off prefetch of full-window demand and AGWS wind/solar generation
records, cached to sim/cache/ for reuse by Phase 3b regression and any
future calibration work.

Historical Ground Truth law: real Elexon data only. Window matches the
data-availability boundary documented in generation_demand_history.py
(~2016-03-01 onward) through the simulation window end (2025-06-07).

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import json
from pathlib import Path

from sim.generation_demand_history import (
    get_demand_outturn_range,
    get_wind_solar_generation_range,
)

CACHE_DIR = Path("sim/cache")
START_DATE = "2016-03-01"
END_DATE = "2025-06-07"


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching demand/outturn {START_DATE}..{END_DATE} ...")
    demand = get_demand_outturn_range(START_DATE, END_DATE)
    print(f"  {len(demand):,} records")
    (CACHE_DIR / "elexon_demand_full.json").write_text(json.dumps(demand))

    print(f"Fetching AGWS wind/solar {START_DATE}..{END_DATE} ...")
    agws = get_wind_solar_generation_range(START_DATE, END_DATE)
    print(f"  {len(agws):,} records")
    (CACHE_DIR / "elexon_agws_full.json").write_text(json.dumps(agws))


if __name__ == "__main__":
    main()
