"""Run ONE arm of the chase-on/chase-off ladder pair, in its own process.

Separate process per arm, not a loop: `aggression()` reads a module-level path and the two arms
need different ones, so running them in one interpreter would make the second arm's world depend
on whether the first had already imported anything. The override is asserted to have TAKEN before
the run starts -- an override that silently failed would report the chase as costing nothing,
which is the fail-silent shape that turns the whole comparison into a confident null.

Usage: python3 -m tools._ladder_chase_arm <on|off> <out.json>
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    arm, out = sys.argv[1], sys.argv[2]

    import simulation.competitor_reference as cr

    if arm == "off":
        cr.AGGRESSION_PATH = REPO / "docs" / "observability" / "aggression_chase_off.yaml"

    chase = cr.aggression()["chase_per_quarter"]
    expected = 0.0 if arm == "off" else 0.5
    if chase != expected:
        print(f"REFUSED: arm={arm} expected chase_per_quarter={expected}, got {chase}")
        return 2
    print(f"[{arm}] chase_per_quarter={chase} CONFIRMED before the run")

    from tools.run_price_ladder import main as ladder_main

    return ladder_main(
        ["--end-year", "2019", "--rungs", "0,0.5,1,2", "--out", out]) or 0


if __name__ == "__main__":
    raise SystemExit(main())
