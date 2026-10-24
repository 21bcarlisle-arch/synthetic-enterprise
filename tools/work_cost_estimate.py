"""What the work still to come will cost, in the director's points, fitted from what landed work cost.

THE DIRECTOR'S STEER (2026-10-24, 11:09 and 11:13 BST): *"Do we estimate the token cost of work to
come?"* -- then *"Yes"* to a cost on every drawable item, a rolling forecast of the backlog in weeks,
and estimates checked against what landed. The steer is
`docs/staging/advisor/DIRECTOR_STEER_ESTIMATE_THE_COST_OF_WORK_TO_COME_2026-10-24.md`.

THE MEASURED SIDE. A session that LANDED is one whose tool results carry the landing door's own
line, `[surgical-land] landed <sha>`. Its cost is its transcript plus its subagents, priced by
`tools.tick_burn_rate` and converted to points by that module's `usd_per_point` (the director's own
readings, never typed in). Its WORK CLASS is read from the paths its landed commits touched.

THE SAME CLASSIFIER READS AN OPEN ATOM'S `file_scope`, so a class's fitted cost prices the atoms of
that class. What it cannot see: how many landed sessions one level step takes. That is bounded,
not guessed: at least one, and at most every landed session in the window divided by the level
steps recorded in it (`docs/observability/gate_authorizations.jsonl`) -- an over-count, because
much landed work is not an atom's level step. The backlog in weeks is printed as that range.

A POINT is one percent of the director's weekly allowance, so the week holds 100 by definition.

WHAT THIS IS NOT. It decides nothing: priority stays the director's (P1, P3), and this only says
what the order costs. It does not ration work by his allowance -- he ruled that hitting the limit
is better than stopping short.

REUSE: tools/work_cost_estimate.py
CLASS: CUSTOM
INDEX: searched "work cost estimate", "backlog forecast" -- no existing row covers this;
       `tools.tick_burn_rate` prices a turn by its kind and route and never by the work it landed,
       and is imported here for its pricing, its point conversion and its readings rather than
       re-implemented; `tools.model_tier_report` reports which tier was drawn, not a cost.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import time
from collections import defaultdict
from pathlib import Path

from tools import tick_burn_rate as burn

PROJECT = Path(__file__).resolve().parent.parent
LEVEL_LEDGER = PROJECT / "docs" / "observability" / "gate_authorizations.jsonl"
ADVISOR_DIR = PROJECT / "docs" / "staging" / "advisor"

_LANDED = re.compile(r"\[surgical-land\] landed ([0-9a-f]{7,40})")

#: The classes, in precedence order: a commit touching any path of an earlier class is that class.
#: Code before documents, because a build that also writes its record is a build.
CLASSES = (
    ("world_build", ("sim/", "simulation/")),
    ("supplier_build", ("company/", "saas/")),
    ("grading_run", ("docs/staging/records/",)),
    ("knowledge_page", ("site/knowledge/", "docs/market_research/", "docs/domain_artefact_library/")),
    ("site_page", ("site/",)),
    ("harness", ("background/", "tools/", "tests/", ".claude/")),
)
OTHER = "record"
#: An open atom whose `file_scope` names no code (an idle atom's scope is often just `docs/design`) is
#: priced by its lane instead, or every idle world atom would be priced as the cheapest class.
LANE_CLASS = (("W", "world_build"), ("H", "harness"), ("A", OTHER), ("G", "harness"))
LANE_DEFAULT = "supplier_build"
WEEK_POINTS = 100.0
#: Below this many landed sessions a class's spread is printed as its full min-max, and called thin.
THIN = 8
#: The allowance resets on Monday at 03:00 UK time (director, 23 Oct). Read here as 02:00 UTC, the
#: BST instant; in GMT the reset is an hour later, and a reading inside that hour is the only one misread.
RESET_WEEKDAY, RESET_HOUR_UTC = 0, 2


def last_reset(now: float) -> float:
    t = time.gmtime(now)
    midnight = now - (t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec)
    at = midnight - ((t.tm_wday - RESET_WEEKDAY) % 7) * 86400 + RESET_HOUR_UTC * 3600
    return at if at <= now else at - 7 * 86400


def classify(paths) -> str:
    paths = [p for p in paths if p]
    for name, prefixes in CLASSES:
        if any(p.startswith(prefixes) for p in paths):
            return name
    return OTHER


def _session_cost_and_landings(path: Path) -> tuple[float, list[str]]:
    """Weighted USD for one session (main transcript + its subagents) and the shas it landed."""
    usd, shas, seen = 0.0, [], set()
    files = [path] + sorted(path.parent.glob(f"{path.stem}/subagents/*.jsonl"))
    for i, f in enumerate(files):
        for line in f.read_text(errors="replace").splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if i == 0 and row.get("type") == "user":
                content = (row.get("message") or {}).get("content")
                for block in content if isinstance(content, list) else ():
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        body = block.get("content")
                        for sha in _LANDED.findall(body if isinstance(body, str) else json.dumps(body)):
                            if sha not in shas:
                                shas.append(sha)
            if row.get("type") != "assistant":
                continue
            msg = row.get("message") or {}
            if not msg.get("usage") or msg.get("model") == "<synthetic>" or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            usd += burn._priced(msg["usage"], msg.get("model"))
    return usd, shas


def _paths_of(shas: list[str]) -> dict[str, list[str]]:
    """sha -> paths it touched, for the shas this repository knows; an unknown sha is left out."""
    out: dict[str, list[str]] = {}
    for sha in shas:
        r = subprocess.run(["git", "-C", str(PROJECT), "show", "--no-renames", "--name-only",
                            "--format=", sha], capture_output=True, text=True)
        if r.returncode == 0:
            out[sha] = [p for p in r.stdout.splitlines() if p]
    return out


def landed_sessions(days: float, now: float | None = None, root: Path = burn.PROJECTS) -> tuple[list[dict], float]:
    """The sessions that landed, each with its cost and class, and the USD every session spent."""
    cutoff = (now or time.time()) - days * 86400
    rows, total = [], 0.0
    for path in root.glob("*/*.jsonl"):
        if path.stat().st_mtime < cutoff:
            continue
        usd, shas = _session_cost_and_landings(path)
        total += usd
        if shas:
            rows.append({"session": path.stem, "usd": usd, "shas": shas})
    known = _paths_of([s for r in rows for s in r["shas"]])
    for r in rows:
        r["shas"] = [s for s in r["shas"] if s in known]
        r["class"] = classify([p for s in r["shas"] for p in known[s]])
    return [r for r in rows if r["shas"]], total


def fit(sessions: list[dict], usd_per_point: float, overhead: float = 1.0) -> dict[str, dict]:
    """Points per landed session by class. `overhead` charges the spend of sessions that landed
    nothing (orientation, refused landings, waits) to the work that did land, pro rata."""
    by = defaultdict(list)
    for s in sessions:
        by[s["class"]].append(s["usd"] * overhead / usd_per_point)
    out = {}
    for cls, pts in by.items():
        pts.sort()
        thin = len(pts) < THIN
        lo, hi = (pts[0], pts[-1]) if thin else statistics.quantiles(pts, n=4)[0::2]
        out[cls] = {"n": len(pts), "median": statistics.median(pts), "low": lo, "high": hi, "thin": thin}
    return out


def level_steps_since(cutoff: float, ledger: Path = LEVEL_LEDGER) -> int:
    n = 0
    for line in ledger.read_text().splitlines() if ledger.exists() else ():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if str(r.get("action", "")).startswith("LEVEL_UP") and float(r.get("ts") or 0) >= cutoff:
            n += 1
    return n


def atom_class(atom: dict) -> str:
    cls = classify(atom.get("file_scope") or [])
    if cls != OTHER:
        return cls
    lane = atom.get("lane") or ""
    return next((c for prefix, c in LANE_CLASS if lane.startswith(prefix)), LANE_DEFAULT)


def open_atom_steps() -> dict[str, int]:
    from tools import maturity_map_store as store
    steps: dict[str, int] = defaultdict(int)
    for a in store.load_live_atoms():
        gap = (a.get("level_target") or 0) - (a.get("level_current") or 0)
        if gap > 0:
            steps[atom_class(a)] += gap
    return dict(steps)


def forecast(days: float = 14.0, now: float | None = None) -> dict:
    now = now or time.time()
    per = burn.usd_per_point()
    if per is None:
        return {"refused": "no point conversion: fewer than two of the director's readings on this tier"}
    sessions, total_usd = landed_sessions(days, now)
    landed_usd = sum(s["usd"] for s in sessions)
    overhead = total_usd / landed_usd if landed_usd else 1.0
    classes = fit(sessions, per, overhead)
    pooled = statistics.median([s["usd"] * overhead / per for s in sessions]) if sessions else None
    steps_done = level_steps_since(now - days * 86400)
    per_step_max = len(sessions) / steps_done if steps_done else None
    atoms = open_atom_steps()
    low = high = 0.0
    for cls, n in atoms.items():
        c = classes.get(cls) or {"median": pooled or 0.0}
        low += n * c["median"]
        high += n * c["median"] * (per_step_max or 1.0)
    advisor = sorted(p.name for p in ADVISOR_DIR.glob("DIRECTOR_*.md"))
    last_t, last_p = burn.POINT_READINGS[-1]
    read_at = time.mktime(time.strptime(last_t, "%Y-%m-%dT%H:%M")) - time.timezone
    used = None
    if read_at >= last_reset(now):
        used = last_p + burn.weighted_usd_between(last_t, time.strftime("%Y-%m-%dT%H:%M", time.gmtime(now))) / per
    return {"days": days, "usd_per_point": per, "landed_sessions": len(sessions), "classes": classes,
            "overhead": overhead, "total_points": total_usd / per,
            "pooled_median": pooled, "level_steps_in_window": steps_done,
            "sessions_per_step_max": per_step_max, "open_steps_by_class": atoms,
            "atom_backlog_points": (low, high), "atom_backlog_weeks": (low / WEEK_POINTS, high / WEEK_POINTS),
            "advisor_files": advisor, "advisor_points_each": pooled,
            "week_used_points": used, "last_reading": (last_t, last_p)}


def render(days: float = 14.0, now: float | None = None) -> str:
    f = forecast(days, now)
    if "refused" in f:
        return f"NOT ESTIMATED -- {f['refused']}"
    lines = [f"Cost of work to come, fitted from {f['landed_sessions']} landed sessions over {days:g} days "
             f"(one point = USD {f['usd_per_point']:.1f} weighted; the week holds {WEEK_POINTS:g}). Each "
             f"landed session carries its share of the spend that landed nothing: every session spent "
             f"{f['total_points']:.0f} points, {f['overhead']:.2f}x what the landed sessions alone spent.", "",
             "| work class | landed sessions | median points | range | open level steps |",
             "|---|---|---|---|---|"]
    for cls in [c for c, _ in CLASSES] + [OTHER]:
        c = f["classes"].get(cls)
        steps = f["open_steps_by_class"].get(cls, 0)
        if c:
            rng = f"{c['low']:.2f}-{c['high']:.2f}" + (" (thin: min-max)" if c["thin"] else " (quartiles)")
            lines.append(f"| {cls} | {c['n']} | {c['median']:.2f} | {rng} | {steps} |")
        else:
            lines.append(f"| {cls} | 0 | no history -- priced at the pooled median | | {steps} |")
    lo, hi = f["atom_backlog_points"]
    wlo, whi = f["atom_backlog_weeks"]
    spm = f["sessions_per_step_max"]
    lines += ["", f"**Atom backlog:** {sum(f['open_steps_by_class'].values())} open level steps, "
              f"{lo:.0f}-{hi:.0f} points, **{wlo:.1f}-{whi:.1f} weeks** at the full allowance. The low "
              f"end is one landed session per level step; the high end is "
              + (f"{spm:.1f} sessions per step ({f['landed_sessions']} landed sessions over "
                 f"{f['level_steps_in_window']} recorded level steps), an over-count because much landed "
                 f"work is not an atom's step." if spm else "unmeasured: no level step was recorded in the window."),
              f"**Advisor queue:** {len(f['advisor_files'])} director file(s), each priced at the pooled "
              f"median of {f['pooled_median']:.2f} points until its class is known.",
              (f"**This week:** about {f['week_used_points']:.0f} of {WEEK_POINTS:g} points used (his reading "
               f"of {f['last_reading'][1]:g}% at {f['last_reading'][0]} UTC plus spend since), so about "
               f"{max(0.0, WEEK_POINTS - f['week_used_points']):.0f} remain." if f["week_used_points"] is not None
               else f"**This week:** no reading since Monday's reset (last: {f['last_reading'][1]:g}% at "
                    f"{f['last_reading'][0]} UTC), so what remains is not known."),
              "**Not yet estimated:** open findings and direction items (no classifier reads them yet); "
              "estimate-against-actual per landed item (no estimate was recorded before these landed)."]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=float, default=14.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    print(json.dumps(forecast(args.days), indent=2, default=list) if args.json else render(args.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
