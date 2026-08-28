"""Did the company's belief move between the chase-on and chase-off worlds?

THE QUESTION THIS ANSWERS, and it is B10's remaining L3 leg. A chase-on/chase-off pair run on one
tree with identical book and seeds moves the WORLD's churn probability at every rung. Before
2026-08-28 it moved the COMPANY's `believed_p_leave` by `max |ON - OFF| = 0.0` -- bit-identical,
because the company's only competitive channel was
`market_conditions.market_conditions_multiplier(renewal_year)`, a lookup keyed on the calendar
year and therefore structurally incapable of responding to anything a rival does inside one. This
prints the same comparison against the derived channel that replaced it
(`company/crm/competitive_pressure.py`).

REPORTS THE GAP, NOT ONLY THE MOVE. `docs/design/COMPETITOR_FIELD_FRAME.md` §5 says a large
persistent gap between belief and truth is the expected signature of a real epistemic limit, and
that the defect is a gap that never MOVES in response to new observations. So a belief that moves
by less than the world did is a result and not a failure -- provided the amount is stated against
the gap it is trying to close, which is what the last two columns do.

READS THE PAIRED POPULATIONS EACH ARTEFACT DECLARES. `slopes.points` is taken over the
`common_population` -- decisions priced AND rolled at every rung -- and the two arms can select
different such sets, because a rung that churns an account earlier removes its later renewals.
Where the two arms' populations differ, that is PRINTED rather than averaged over: a mean over one
population beside a mean over another is exactly the shape that reads a population difference as
a price effect.

Usage: python3 -m tools.compare_chase_belief <on.json> <off.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _points(payload: dict) -> dict[str, dict]:
    return {f"{float(p['multiplier']):.1f}": p
            for p in payload.get("slopes", {}).get("points", [])}


def _decisions(payload: dict) -> dict[tuple, dict]:
    return {(d["account"], d["term_start"]): d
            for d in payload.get("world_curve_vs_belief", {}).get("per_decision", [])}


def main() -> int:
    on = json.loads(Path(sys.argv[1]).read_text())
    off = json.loads(Path(sys.argv[2]).read_text())
    p_on, p_off = _points(on), _points(off)

    n_on = on.get("slopes", {}).get("common_population")
    n_off = off.get("slopes", {}).get("common_population")
    print(f"common population: ON={n_on}  OFF={n_off}"
          + ("" if n_on == n_off else "   <-- DIFFERENT: rung-driven attrition differs between "
                                      "the arms, so per-rung means below are not paired"))
    print()

    print(f"{'rung':>5} {'n':>3} | {'belief ON':>9} {'belief OFF':>10} {'BELIEF MOVE':>12}"
          f" | {'world ON':>8} {'world OFF':>9} {'WORLD MOVE':>10}"
          f" | {'gap ON':>7} {'tracked':>8}")
    print("-" * 100)
    rung_moves: list[float] = []
    for rung in sorted(set(p_on) & set(p_off), key=float):
        a, b = p_on[rung], p_off[rung]
        bon, boff = a["believed_non_renewal_rate"], b["believed_non_renewal_rate"]
        won, woff = a["world_p_leave_mean"], b["world_p_leave_mean"]
        if None in (bon, boff, won, woff):
            print(f"{rung:>5} {a['n']:>3} | a leg is missing at this rung -- not comparable")
            continue
        bmove, wmove = bon - boff, won - woff
        rung_moves.append(bmove)
        # How much of the world's own move the company tracked. NOT a score out of 100: over 100
        # is an over-reaction and a negative value is a belief moving the wrong way.
        tracked = f"{bmove / wmove * 100:>7.1f}%" if abs(wmove) > 1e-12 else "    n/a"
        print(f"{rung:>5} {a['n']:>3} | {bon:>9.4f} {boff:>10.4f} {bmove:>+12.6f}"
              f" | {won:>8.4f} {woff:>9.4f} {wmove:>+10.4f}"
              f" | {bon - won:>+7.4f} {tracked:>8}")

    d_on, d_off = _decisions(on), _decisions(off)
    shared = sorted(set(d_on) & set(d_off))
    diffs = []
    for k in shared:
        for field in ("believed_p_leave_at_lowest_rung", "believed_p_leave_at_highest_rung"):
            if d_on[k].get(field) is not None and d_off[k].get(field) is not None:
                diffs.append(abs(d_on[k][field] - d_off[k][field]))

    print()
    print(f"paired decisions carried by BOTH artefacts: {len(shared)}")
    if diffs:
        moved = sum(1 for d in diffs if d > 0.0)
        print(f"per-decision belief observations at the ENDPOINT rungs only: {len(diffs)}, "
              f"{moved} of which differ; max |ON - OFF| = {max(diffs):.10f}")

    # THE VERDICT IS TAKEN OVER THE PER-RUNG TABLE, NOT THE PER-DECISION ENDPOINTS. The
    # artefact's `per_decision` block carries only each decision's LOWEST and HIGHEST rung, so a
    # move confined to an interior rung is invisible to it -- and on the first live pair that is
    # exactly where the move was: rung 0.5 moved +0.0132 while rungs 0.0, 1.0 and 2.0 did not,
    # so an endpoints-only reading printed "bit-identical" directly beneath a table showing the
    # opposite. A summary that contradicts the table above it is worse than no summary.
    rungs_moved = [m for m in rung_moves if m != 0.0]
    print(f"rungs whose mean belief differs between the two worlds: "
          f"{len(rungs_moved)}/{len(rung_moves)}")
    print(f"largest per-rung belief move: {max((abs(m) for m in rung_moves), default=0.0):.6f}")
    print()
    if rungs_moved:
        print("VERDICT: the company's belief RESPONDS to a rival it cannot see and never "
              "names, inferred entirely from its own realised losses. The year-table constant "
              "is gone. The response is SPARSE ACROSS RUNGS because the channel observes an "
              "INTEGER departure count: it fires at a rung where the chase changed that count "
              "in a year early enough to be evidence, and is silent where it did not.")
    else:
        print("VERDICT: the belief is bit-identical between the two worlds at every rung. The "
              "channel is wired and CAN move -- its controls prove it against mutation -- but "
              "on this book the chase did not change the realised loss COUNT anywhere, which "
              "is the granularity a company-observable channel resolves at. That is a "
              "different finding from 'the belief cannot move': it is 'this book is too thin "
              "to move it'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
