"""One-variable counterfactual for d9374ae9e: the book sited on the old household frame against the new.

ONE VARIABLE. The same code, seed, window and weather store, with `household_siting`'s two frame
paths pointed at a directory (`--frame-dir`) before anything imports them. `run_phase2b` binds its
roster at import, so each arm needs its own process. Run it once per frame and `--compare` the two
JSON files. The book's kWh comes from `tools.fabric_settlement_gap.measure`, the reader that tool
publishes from. Nothing here re-implements siting or demand.

Pre-registration: `docs/staging/records/SEAT_PREREG_WHAT_THE_SITING_FRAME_REBUILD_MOVES_IN_THE_BOOK_2026-09-27.md`.

    git show d9374ae9e^:sim/household_siting/region_household_frame.csv > /tmp/old/region_household_frame.csv
    git show d9374ae9e^:sim/household_siting/cell_output_area_frame.csv.gz > /tmp/old/cell_output_area_frame.csv.gz
    python3 -m tools.siting_frame_counterfactual --frame-dir /tmp/old --out /tmp/old.json
    python3 -m tools.siting_frame_counterfactual --frame-dir sim/household_siting --out /tmp/new.json
    python3 -m tools.siting_frame_counterfactual --compare /tmp/old.json /tmp/new.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _home(customer_id: str) -> str:
    """A dual-fuel `PROS-x` and its gas leg `PROS-xg` are one house with one siting draw."""
    return customer_id[:-1] if customer_id.startswith("PROS-") and customer_id.endswith("g") else customer_id


def run_arm(frame_dir: Path) -> dict:
    from simulation import household_siting as hs

    hs.FRAME_PATH = frame_dir / "region_household_frame.csv"
    hs.OUTPUT_AREA_FRAME_PATH = frame_dir / "cell_output_area_frame.csv.gz"
    for path in (hs.FRAME_PATH, hs.OUTPUT_AREA_FRAME_PATH):
        if not path.exists():
            raise FileNotFoundError(f"{path}: an arm with a missing frame is not an arm")

    from simulation import fabric_demand_path as fdp
    from simulation.household_physical_layer import people_count_for
    from simulation.live_population import live_drawn_households
    from simulation.run_phase2b import CUSTOMERS
    from tools.fabric_settlement_gap import measure

    households = live_drawn_households()
    weather = fdp.WeatherWorldSource.load()
    homes: dict[str, dict] = {}
    for customer in CUSTOMERS:
        cid = customer["customer_id"]
        if cid not in households:
            continue
        location = customer.get("location") or {}
        area = households[cid].output_area
        homes.setdefault(_home(cid), {
            "lat": location.get("lat"),
            "lon": location.get("lon"),
            "output_area": area,
            "store_cell": weather.site_for(customer),
            "headcount": people_count_for(cid, area, bedrooms=households[cid].bedrooms),
        })
    book = measure()
    return {
        "frame_dir": str(frame_dir),
        "account_ids": sorted(c["customer_id"] for c in CUSTOMERS),
        "homes": homes,
        "eligible": {r["customer_id"]: {"elec_kwh": r["fabric_annual_electricity_kwh"],
                                        "gas_kwh": r["fabric_annual_gas_kwh"]}
                     for r in book["eligible"]},
        "excluded": {r["customer_id"]: r["reason"] for r in book["excluded"]},
        "window": book["window"],
        "seed": book["seed"],
    }


def compare(old: dict, new: dict) -> dict:
    same_accounts = old["account_ids"] == new["account_ids"]
    shared = sorted(set(old["homes"]) & set(new["homes"]))
    n = len(shared)

    def share(pred) -> float | None:
        return round(sum(1 for h in shared if pred(old["homes"][h], new["homes"][h])) / n, 4) if n else None

    def sited(h):
        return h["lat"] is not None

    def total(arm, fuel):
        return sum(r[fuel] for r in arm["eligible"].values())

    both = sorted(set(old["eligible"]) & set(new["eligible"]))
    kwh = {}
    for fuel in ("elec_kwh", "gas_kwh"):
        o, w = total(old, fuel), total(new, fuel)
        kwh[fuel] = {
            "old_total": round(o), "new_total": round(w),
            "total_move_pct": round(100 * (w - o) / o, 2) if o else None,
            "old_mean_per_eligible": round(o / len(old["eligible"]), 1) if old["eligible"] else None,
            "new_mean_per_eligible": round(w / len(new["eligible"]), 1) if new["eligible"] else None,
            "stayers_move_pct": (round(100 * (sum(new["eligible"][c][fuel] for c in both)
                                              - sum(old["eligible"][c][fuel] for c in both))
                                       / sum(old["eligible"][c][fuel] for c in both), 2)
                                 if both and sum(old["eligible"][c][fuel] for c in both) else None),
        }
    heads = [(old["homes"][h]["headcount"], new["homes"][h]["headcount"]) for h in shared]
    return {
        "P0_same_accounts": same_accounts,
        "homes_compared": n,
        "homes_sited": sum(1 for h in shared if sited(old["homes"][h]) and sited(new["homes"][h])),
        "P1_share_frame_cell_changed": share(lambda a, b: (a["lat"], a["lon"]) != (b["lat"], b["lon"])),
        "P2_share_output_area_changed": share(lambda a, b: a["output_area"] != b["output_area"]),
        "P3_share_store_resolution_changed": share(lambda a, b: a["store_cell"] != b["store_cell"]),
        "eligible_premises": {"old": len(old["eligible"]), "new": len(new["eligible"]),
                              "in_both": len(both),
                              "left": sorted(set(old["eligible"]) - set(new["eligible"])),
                              "joined": sorted(set(new["eligible"]) - set(old["eligible"]))},
        "P4_mean_headcount": {"old": round(sum(a for a, _ in heads) / n, 4),
                              "new": round(sum(b for _, b in heads) / n, 4),
                              "share_of_homes_changed": share(lambda a, b: a["headcount"] != b["headcount"]),
                              "mean_abs_move": round(sum(abs(b - a) for a, b in heads) / n, 4)},
        "P5_book_kwh": kwh,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--frame-dir", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--compare", nargs=2, type=Path, metavar=("OLD", "NEW"))
    args = ap.parse_args(argv)
    if args.compare:
        old, new = (json.loads(p.read_text()) for p in args.compare)
        print(json.dumps(compare(old, new), indent=2))
        return 0
    if not (args.frame_dir and args.out):
        ap.error("an arm needs --frame-dir and --out")
    args.out.write_text(json.dumps(run_arm(args.frame_dir.resolve()), indent=1))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
