"""Grade the company's ratio screen against the world's voids and thefts on one population (W2_36).

REUSE: tools/theft_void_screen_probe.py
CLASS: CUSTOM
INDEX: searched "theft void screen probe", "void theft screen" -- no existing row covers this.
       `simulation.meter_reads.premise_theft_study` generates a theft and stops; nothing puts the
       world's voids beside it or asks the company's screen which of the two it flags.

WHY. A theft that hides all of a home's use registers 0, and so does a void, so a ratio screen
cannot tell them apart by the ratio. What it can be told apart by is LENGTH: a void runs 0.7-1.15
months, a theft about two years. So the answer turns on the window the ratio is taken over, and
the probe measures a calendar month (a smart read) and a calendar year (an annualised read) apart.
Pre-registration: docs/staging/records/WORKER_PREREG_W2_36_WHAT_A_RATIO_SCREEN_FINDS_AMONG_VOIDS_AND_THEFTS_2026-10-16.md.

THE HARNESS READS THE WORLD'S TRUTH; THE SCREEN DOES NOT. `classify_anomaly` is handed registered
kWh and the EAC only. The cause each flag is filed under is the world's, and stays here.

NAMED SIMPLIFICATION: occupied use is flat at the EAC, so the only flags are voids and thefts. A
low-use household flags too, and that source is not priced. Owner-occupier voids are a GAP and are
printed as none, which is not a finding that owners have none.
"""

from __future__ import annotations

import calendar
import datetime as dt
from collections import Counter

from company.billing.theft_indicator import classify_anomaly
from sim.customer_state_layer import Occupancy, TenureType, draw_home_move, void_end
from simulation.meter_reads import THEFT_UNREGISTERED_SHARE, premise_theft_months

FIRST_YEAR, LAST_YEAR = 2016, 2025
MONTHS = [(y, m) for y in range(FIRST_YEAR, LAST_YEAR + 1) for m in range(1, 13)]
CUTS = (0.05, 0.4, 0.65, 0.9)


def _void_span(tenure: TenureType, setting: str) -> tuple[dt.timedelta, str | None]:
    # The world's void is a fixed length per tenure (void_months says why), and void_end re-reads
    # the register on every call, so it is asked once per tenure for the span. void_end is in the
    # key so a substituted one is never answered from the cache.
    key = (tenure, setting, void_end)
    if key not in _SPANS:
        ref = dt.date(FIRST_YEAR, 1, 1)
        end, gap = void_end(ref, tenure, setting)
        _SPANS[key] = (end - ref, gap)
    return _SPANS[key]


_SPANS: dict = {}


def _empty_days_by_month(premise_id: str, tenure: TenureType, base_seed: int,
                         setting: str) -> tuple[list[int], str | None]:
    """Days in each month of MONTHS the premise stands empty, from the world's own moves and voids."""
    occupancy = Occupancy.of_customer(f"{premise_id}-occ0", tenure, premise_id=premise_id)
    span, gap = _void_span(tenure, setting)
    empty: set[dt.date] = set()
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        move = draw_home_move(occupancy, year, base_seed)
        if move is None:
            continue
        day = move.move_date
        while day < move.move_date + span:
            empty.add(day)
            day += dt.timedelta(days=1)
        occupancy = Occupancy(premise_id, move.incoming.occupancy_id, tenure)
    counts = Counter((d.year, d.month) for d in empty)
    return [counts.get(ym, 0) for ym in MONTHS], gap


def _cause(stolen: bool, emptied: bool) -> str | None:
    if stolen and emptied:
        return "both"
    return "theft" if stolen else "void" if emptied else None


def premise_windows(premise_id: str, tenure: TenureType, base_seed: int = 42,
                    setting: str = "default",
                    unregistered_share: float = THEFT_UNREGISTERED_SHARE) -> dict:
    """Each window's registered/EAC ratio and the world's cause for any shortfall."""
    empty, gap = _empty_days_by_month(premise_id, tenure, base_seed, setting)
    stealing = premise_theft_months(premise_id, len(MONTHS))
    monthly = []
    for (year, month), empty_days, stole in zip(MONTHS, empty, stealing):
        days = calendar.monthrange(year, month)[1]
        ratio = (1.0 - empty_days / days) * ((1.0 - unregistered_share) if stole else 1.0)
        monthly.append({"year": year, "days": days, "ratio": ratio,
                        "cause": _cause(stole, empty_days > 0)})
    annual = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        rows = [r for r in monthly if r["year"] == year]
        days = sum(r["days"] for r in rows)
        causes = {r["cause"] for r in rows if r["cause"]}
        annual.append({
            "year": year,
            "ratio": sum(r["ratio"] * r["days"] for r in rows) / days,
            "cause": ("both" if len(causes) > 1 or "both" in causes else next(iter(causes), None)),
        })
    return {"monthly": monthly, "annual": annual, "void_gap": gap}


def _flagged(ratio: float, cut: float) -> bool:
    # The screen is asked with registered kWh and EAC only; the 3,100 kWh EAC is a scale and cancels.
    status = classify_anomaly(ratio * 3100.0, 3100.0, investigate_below=cut, watch_below=cut)
    return status["status"] == "investigate"


def screen_table(tenure: TenureType, n_premises: int, base_seed: int = 42,
                 setting: str = "default") -> dict:
    """Flags per 10,000 premise-years, by window, cut and the world's cause."""
    counts = {w: {c: Counter() for c in CUTS} for w in ("monthly", "annual")}
    gap = None
    for i in range(n_premises):
        windows = premise_windows(f"PREM-{tenure.value}-{i}", tenure, base_seed, setting)
        gap = gap or windows["void_gap"]
        for w in ("monthly", "annual"):
            for row in windows[w]:
                for cut in CUTS:
                    if _flagged(row["ratio"], cut):
                        counts[w][cut][row["cause"] or "neither"] += 1
    scale = 10_000 / (n_premises * (LAST_YEAR - FIRST_YEAR + 1))
    return {
        "tenure": tenure.value, "setting": setting, "void_gap": gap,
        "per_10k_premise_years": {
            w: {cut: {k: round(v * scale, 1) for k, v in sorted(c.items())} for cut, c in by.items()}
            for w, by in counts.items()
        },
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--premises", type=int, default=5000)
    parser.add_argument("--setting", default="default")
    args = parser.parse_args()
    for t in TenureType:
        print(json.dumps(screen_table(t, args.premises, setting=args.setting), indent=1))
