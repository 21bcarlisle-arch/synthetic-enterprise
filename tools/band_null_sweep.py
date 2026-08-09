#!/usr/bin/env python3
"""Run the H33 band-null sweep on the population the bands are ACTUALLY judged on.

    python3 tools/band_null_sweep.py            # the table
    python3 tools/band_null_sweep.py --json     # machine-readable
    python3 tools/band_null_sweep.py --persist  # write the ledger artefact

The population comes from `tools/couple_fabric.py` — the same panel, the same
window, the same generator that the live coupling run judges. Measuring the null
on a convenient fixture instead would answer a question nobody asked: a band's
null is a property of the band AND the window it is applied at, and the only
window that matters is the one in production.

Exit status is 1 when any band is INSIDE its own null, so a scheduled run of this
is an alarm and not a report. SAME_ORDER and UNMEASURABLE are findings, reported
and not fatal — they are dispositioned in
`docs/design/BAND_NULL_SWEEP.md`, not silently tolerated.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from background import band_null_sweep as bns  # noqa: E402
from background import fabric_gap_ledger as fgl  # noqa: E402

LEDGER = Path(__file__).resolve().parents[1] / "docs" / "observability" / "band_null_sweep.json"


def live_population() -> fgl.PopulationTraces:
    from tools import couple_fabric as cf

    weather = cf.load_weather()
    panel = cf.build_panel(weather)
    return fgl.premise_trace_population([entry[2] for entry in panel], weather)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    ap.add_argument("--persist", action="store_true", help=f"write {LEDGER.name}")
    ap.add_argument("--replications", type=int, default=bns.DEFAULT_REPLICATIONS)
    args = ap.parse_args()

    measurements = bns.sweep(live_population(), replications=args.replications)
    payload = bns.to_json(measurements)

    if args.persist:
        LEDGER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        homes, days = bns.applied_window()
        print(f"BAND NULL SWEEP — {len(measurements)} anchored bands, "
              f"applied window {homes} homes x {days} days")
        print(f"  {'band':<44}{'dir':<9}{'n':>3}{'threshold':>11}"
              f"{'null(best)':>12}{'null spread':>13}{'margin':>10}  verdict")
        for m in measurements:
            print(f"  {m.band:<44}{m.direction:<9}{m.homes_judged:>3}{m.threshold:>11.4g}"
                  f"{m.null_best:>12.4g}{m.null_spread:>13.4g}{m.margin:>10.4g}"
                  f"  {m.verdict.value}")
        for m in measurements:
            if m.is_hit:
                print(f"\n  {m.band}: {m.note}")
            if m.caveat:
                print(f"\n  {m.band} [caveat]: {m.caveat}")
        print(f"\n  excluded from the sweep ({len(bns.excluded_bands())}):")
        for name, reason in sorted(bns.excluded_bands().items()):
            print(f"    {name}: {reason}")

    defects = [m for m in measurements if m.verdict is bns.NullVerdict.INSIDE_NULL]
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
