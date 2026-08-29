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
import statistics
import sys
from pathlib import Path


def _points(payload: dict) -> dict[str, dict]:
    return {f"{float(p['multiplier']):.1f}": p
            for p in payload.get("slopes", {}).get("points", [])}


def _decisions(payload: dict) -> dict[tuple, dict]:
    return {(d["account"], d["term_start"]): d
            for d in payload.get("world_curve_vs_belief", {}).get("per_decision", [])}


def per_rung_paired(on: dict, off: dict) -> list[dict]:
    """The between-arm comparison on EACH RUNG'S OWN paired population.

    THE JOIN IS THE FINDING (2026-08-29). The first two live pairs took this comparison over
    `slopes.common_population` -- the decisions priced AND rolled at EVERY rung. That set exists
    for the SLOPE, which has to run along one x-axis over one population, and it is the wrong
    population for a between-arm question at a FIXED rung.

    What it costs is not a rounding difference. The top rung prices the book so aggressively that
    it has nothing left after 2019, so the cross-rung intersection can never contain a late-window
    decision -- on the 2021-window founder-book pair it was 16 decisions with term starts of
    2016-2018 only, out of 99 priced. But the company's competitive-pressure ledger accumulates
    FORWARD: it reads years strictly earlier than the renewal it is pricing, so its evidence is
    thinnest exactly where that intersection sits and richest in the years the intersection
    excludes. The measurement was looking at the one part of the window where the channel it was
    testing had almost nothing to read, and reported "one rung in four" for two runs running.

    On its own population each rung is a paired test: both arms priced it, both arms' worlds
    rolled it, and exactly one declared parameter differs. FOUR INDEPENDENT PAIRED TESTS, NOT A
    CURVE -- the four populations are different sizes and different decisions, so reading a trend
    ACROSS the rows here would be reading a population change as a price effect. The intersection
    table above remains the only place a slope may be read.
    """
    rows = []
    for rung in sorted(set(on.get("decisions", {})) & set(off.get("decisions", {})), key=float):
        a = {(d["account"], d["term_start"]): d
             for d in on["decisions"][rung] if d["world_rolled"]}
        b = {(d["account"], d["term_start"]): d
             for d in off["decisions"][rung] if d["world_rolled"]}
        common = sorted(set(a) & set(b))
        if not common:
            rows.append({"rung": rung, "n": 0, "why_not": "no decision was priced and rolled in "
                                                          "both arms at this rung"})
            continue
        moves = [a[k]["believed_p_leave"] - b[k]["believed_p_leave"] for k in common]
        world = [a[k]["world_realized_p_leave"] - b[k]["world_realized_p_leave"] for k in common]
        moved = [m for m in moves if m != 0.0]
        rows.append({
            "rung": rung,
            "n": len(common),
            "term_start_years": sorted({k[1][:4] for k in common}),
            "belief_on": statistics.mean(a[k]["believed_p_leave"] for k in common),
            "belief_off": statistics.mean(b[k]["believed_p_leave"] for k in common),
            "belief_move": statistics.mean(moves),
            "world_move": statistics.mean(world),
            "decisions_moved": len(moved),
            # §5 component 2 is about DIRECTION, and a mean can be positive while decisions move
            # the wrong way underneath it. Counted per decision, never inferred from the mean.
            "moved_up": sum(1 for m in moved if m > 0),
            "moved_down": sum(1 for m in moved if m < 0),
            "moved_years": sorted({k[1][:4] for k in common
                                   if a[k]["believed_p_leave"] != b[k]["believed_p_leave"]}),
        })
    return rows


def _print_per_rung(rows: list[dict]) -> None:
    print()
    print("BETWEEN-ARM COMPARISON ON EACH RUNG'S OWN PAIRED POPULATION")
    print("  four independent paired tests, NOT a curve -- the four populations differ, so a "
          "trend read DOWN this table would be a population change")
    print(f"  {'rung':>5} {'n':>4} {'years':>10} | {'belief ON':>9} {'belief OFF':>10}"
          f" {'MOVE':>11} | {'world MOVE':>10} {'tracked':>8} | {'moved':>7} {'up/down':>8}")
    print("  " + "-" * 104)
    for r in rows:
        if r["n"] == 0:
            print(f"  {r['rung']:>5} {0:>4} -- {r['why_not']}")
            continue
        yrs = f"{r['term_start_years'][0]}-{r['term_start_years'][-1]}"
        tracked = (f"{r['belief_move'] / r['world_move'] * 100:>7.1f}%"
                   if abs(r["world_move"]) > 1e-12 else "    n/a")
        print(f"  {r['rung']:>5} {r['n']:>4} {yrs:>10} | {r['belief_on']:>9.4f} "
              f"{r['belief_off']:>10.4f} {r['belief_move']:>+11.6f} | {r['world_move']:>+10.4f} "
              f"{tracked:>8} | {r['decisions_moved']:>3}/{r['n']:<3} "
              f"{str(r['moved_up']) + '/' + str(r['moved_down']):>8}")
        if r["moved_years"]:
            print(f"        moved at term starts in {', '.join(r['moved_years'])}")


def _census(artefact_path: str) -> dict | None:
    """The per-year ledger census `_ladder_chase_arm` wrote beside the artefact, if any."""
    p = Path(artefact_path).with_suffix(".ledger_census.json")
    return json.loads(p.read_text()) if p.exists() else None


def _by_year(run: dict, field: str) -> dict[int, float]:
    """One counter of a census run, with its years as ints -- JSON stringifies integer keys."""
    return {int(y): v for y, v in (run.get(field) or {}).items()}


def _wasted(run: dict) -> tuple[int, int]:
    """(losses that could be evidence, losses that could not), for one run's ledger.

    A departure in year Y is only ever read by a renewal priced in a year STRICTLY LATER than Y
    (`CompetitivePressureLedger._closed_window`). So a departure in the last year anything was
    priced in is not weak evidence -- it is no evidence, and counting it as available is how the
    2026-08-28 pair's three silent rungs got mistaken for a book too thin to move the belief.
    """
    priced = list(_by_year(run, "decisions_by_year"))
    last_priced = max(priced) if priced else None
    usable = wasted = 0
    for year, n in _by_year(run, "realised_losses_by_year").items():
        if last_priced is not None and year < last_priced:
            usable += int(n)
        else:
            wasted += int(n)
    return usable, wasted


def tree_identity_verdict(cen_on: dict, cen_off: dict) -> tuple[bool, str]:
    """Did the two arms measure ONE tree? Returns (comparable, why).

    THE CLAIM THIS PAIR MAKES is "one tree, identical book and seeds, exactly one declared
    parameter differing". The arms must now run SEQUENTIALLY -- the ladder retains every rung's
    settlement records and two arms at once exhaust the guest -- which opens a window of tens of
    minutes for another lane to land work in this shared worktree between them. Nothing in the
    ladder artefacts would show it: both would still report a null rung reproducing their own
    control, because each arm is internally consistent with whatever tree it ran on.

    So the fingerprints are compared, and a mismatch REFUSES rather than annotating. A between-arm
    difference is the entire subject here; a difference that might be another lane's commit is not
    a measurement of the chase, and publishing it with a caveat attached is how a caveat gets
    dropped on the way to a headline.
    """
    a, b = cen_on.get("tree_before"), cen_off.get("tree_before")
    if not a or not b:
        return False, ("these artefacts carry no tree fingerprint, so nothing can say the two "
                       "arms ran against the same source -- re-run both arms")
    for cen, side in ((cen_on, "ON"), (cen_off, "OFF")):
        before, after = cen.get("tree_before"), cen.get("tree_after")
        if after and before and before["subject_sha256"] != after["subject_sha256"]:
            return False, (f"the {side} arm's own source changed DURING its run "
                           f"({before['subject_sha256'][:12]} -> {after['subject_sha256'][:12]}): "
                           "another lane landed work mid-measurement")
    if a["subject_sha256"] != b["subject_sha256"]:
        return False, (f"the two arms ran against DIFFERENT trees "
                       f"(ON {a['subject_sha256'][:12]} at {a['head'][:9]}, "
                       f"OFF {b['subject_sha256'][:12]} at {b['head'][:9]})")
    if a.get("missing") or b.get("missing"):
        return False, (f"the fingerprint could not read {sorted(set(a.get('missing') or []) | set(b.get('missing') or []))}"
                       " -- a fingerprint over a file that is not there is not a fingerprint")
    return True, f"both arms ran against subject {a['subject_sha256'][:12]} at {a['head'][:9]}"


def _print_census(cen_on: dict, cen_off: dict) -> None:
    """Realised loss counts per arm per year, beside the rung table they explain."""
    runs_on, runs_off = cen_on.get("runs", []), cen_off.get("runs", [])
    if not runs_on or len(runs_on) != len(runs_off):
        print("ledger census: the two arms recorded different numbers of runs -- not comparable")
        return
    # `_ladder_chase_arm` records the flat-rules control first, then one run per rung in order.
    rungs = [None] + [f"{r:.1f}" for r in cen_on.get("rungs") or [0.0, 0.5, 1.0, 2.0]]
    years = sorted({y
                    for runs in (runs_on, runs_off) for r in runs
                    for field in ("realised_losses_by_year", "decisions_by_year")
                    for y in _by_year(r, field)})
    print()
    print("REALISED LOSS COUNTS BY YEAR, per arm, book-wide (what the company's channel actually "
          "observes)")
    print(f"  window ends {cen_on.get('end_year')}; a loss in year Y is read only by a renewal "
          "priced in a year > Y")
    header = "  " + f"{'run':>8} {'armed':>6} | " + " ".join(f"{y:>9}" for y in years) + \
             f" | {'evidence':>8} {'WASTED':>7}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for i, (a, b) in enumerate(zip(runs_on, runs_off)):
        label = "control" if i == 0 else f"rung {rungs[i]}" if i < len(rungs) else f"run {i}"
        armed = "yes" if (a.get("armed") and b.get("armed")) else "NO"
        loss_a, loss_b = _by_year(a, "realised_losses_by_year"), _by_year(b, "realised_losses_by_year")
        cells = []
        for y in years:
            la, lb = int(loss_a.get(y, 0)), int(loss_b.get(y, 0))
            mark = "*" if la != lb else " "
            cells.append(f"{la:>3}/{lb:<3}{mark}".rjust(9))
        ua, wa = _wasted(a)
        ub, wb = _wasted(b)
        print(f"  {label:>8} {armed:>6} | " + " ".join(cells)
              + f" | {ua:>3}/{ub:<4} {wa:>3}/{wb:<3}")
    print("  cells are ON/OFF; * marks a year where the chase changed the count. An unarmed "
          "ledger reports the prior and no belief move is attributable to it.")
    print("  'evidence' counts losses in years something is priced AFTER; 'WASTED' counts losses "
          "no renewal is ever priced after.")


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

    print("THE CROSS-RUNG INTERSECTION -- the SLOPE's population. Read the per-rung table below "
          "for the between-arm question: this set is confined to the start of the window by the "
          "top rung's own attrition, which is where the company's ledger has least to read.")
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

    rung_rows = per_rung_paired(on, off)
    _print_per_rung(rung_rows)

    cen_on, cen_off = _census(sys.argv[1]), _census(sys.argv[2])
    if cen_on and cen_off:
        ok, why = tree_identity_verdict(cen_on, cen_off)
        print()
        print(("TREE IDENTITY: one tree -- " if ok else "TREE IDENTITY REFUSED -- ") + why)
        _print_census(cen_on, cen_off)
        if not ok:
            print()
            print("REFUSING A VERDICT. Everything above is printed because a reader who has to "
                  "re-run this deserves to see how far it got, but no line of it is a "
                  "measurement of the chase.")
            return 3
    else:
        print()
        print("no ledger census beside these artefacts -- re-run the arms with "
              "`tools._ladder_chase_arm`, which writes one. Without it a silent rung cannot be "
              "told apart from a rung whose evidence landed in a year nothing is priced after.")

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
    print(f"on the CROSS-RUNG INTERSECTION, rungs whose mean belief differs: "
          f"{len(rungs_moved)}/{len(rung_moves)}; largest move "
          f"{max((abs(m) for m in rung_moves), default=0.0):.6f}")

    # THE VERDICT IS TAKEN OVER EACH RUNG'S OWN PAIRED POPULATION. Taking it over the cross-rung
    # intersection reports the company blind at three rungs in four on this book -- not because
    # the belief did not move there, but because that set holds no decision the top rung churned
    # away, which is every decision after the third year of the window. Two consecutive findings
    # published "one rung in four" from it.
    live = [r for r in rung_rows if r["n"]]
    moved_rungs = [r for r in live if r["decisions_moved"]]
    total_moved = sum(r["decisions_moved"] for r in live)
    total_n = sum(r["n"] for r in live)
    down = sum(r["moved_down"] for r in live)
    print(f"on EACH RUNG'S OWN PAIRED POPULATION, rungs whose mean belief differs: "
          f"{len(moved_rungs)}/{len(live)}; decisions that moved: {total_moved}/{total_n}, "
          f"{down} of them in the WRONG direction")
    print()
    if moved_rungs and len(moved_rungs) == len(live):
        # THE WORDING IS KEYED TO THE COUNT, not to the answer that was true when it was written.
        # The first live pair moved at one rung in four and this summary said "SPARSE"; a summary
        # that keeps saying sparse after the response reaches every rung is pinned to today's
        # answer, which goes stale in exactly the flattering direction.
        print("VERDICT: the company's belief responds at EVERY rung, in the correct direction, "
              "inferred entirely from its own realised losses -- a rival it cannot see and never "
              f"names. {total_moved} of {total_n} paired decisions moved"
              + (", all upward." if not down else
                 f", {down} of them DOWNWARD -- read those first: §5 component 2 names a wrong "
                 "SIGN as the worse failure, and a delivered-price difference between the arms "
                 "is the other thing that can produce one.")
              + " These are four independent paired tests, one per rung, on four different "
                "populations -- not a curve in the rung.")
    elif moved_rungs:
        print(f"VERDICT: the company's belief RESPONDS to a rival it cannot see and never names, "
              f"inferred entirely from its own realised losses, at {len(moved_rungs)} of "
              f"{len(live)} rungs ({total_moved}/{total_n} paired decisions). The year-table "
              "constant is gone. Where it is silent, the channel observes an INTEGER departure "
              "count and the chase did not change that count in a year early enough to be "
              "evidence for those decisions -- the census above says which years those are.")
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
