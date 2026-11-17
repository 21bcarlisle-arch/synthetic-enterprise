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
import math
import random
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
_BOUND = re.compile(r"delivery_lane --landed ([a-z0-9](?:[a-z0-9.-]*[a-z0-9])?)")

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
#: "flag any item expected to take more than about 10% of a week before it starts" (director, 24 Oct).
FLAG_POINTS = 0.10 * WEEK_POINTS
#: The draw's estimates and the landings bound to them, beside the delivery lane's own claim store
#: (gitignored runtime state, like the draw ledger), and the last fit the draw prices from. The
#: draw runs every two minutes and must not re-read a month of transcripts, so it reads the fit
#: the last forecast wrote.
def _shared_obs() -> Path:
    try:
        from background.seat_continuation import shared_tree_dir
        return shared_tree_dir() / "docs" / "observability"
    except Exception:  # noqa: BLE001 -- outside the repo's own layout, this tree's copy
        return PROJECT / "docs" / "observability"


COST_LEDGER = _shared_obs() / ".delivery_lane_claims.costs.jsonl"
FIT_CACHE = _shared_obs() / ".work_cost_fit.json"
#: An estimate is BADLY WRONG, and a finding, when the actual is outside this factor of it.
BADLY_WRONG = 3.0
_PATH_TOKEN = re.compile(r"(?<![\w./-])((?:sim|simulation|company|saas|site|docs|background|tools|tests|\.claude)/[\w./-]+)")
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


def _session_cost_and_landings(path: Path) -> tuple[float, list[str], list[str]]:
    """Weighted USD for one session (main transcript + its subagents), the shas it landed, and the
    Lane 0 ids it bound a landing to (`delivery_lane --landed <id>`, run by it or a subagent)."""
    usd, shas, ids, seen = 0.0, [], [], set()
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
            for block in msg.get("content") if isinstance(msg.get("content"), list) else ():
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    for fid in _BOUND.findall(str((block.get("input") or {}).get("command") or "")):
                        if fid not in ids:
                            ids.append(fid)
            if not msg.get("usage") or msg.get("model") == "<synthetic>" or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            usd += burn._priced(msg["usage"], msg.get("model"))
    return usd, shas, ids


def _commits(shas: list[str]) -> dict[str, dict]:
    """sha -> {paths, at, message}, for the shas this repository knows; an unknown sha is left out."""
    out: dict[str, dict] = {}
    for sha in dict.fromkeys(shas):
        r = subprocess.run(["git", "-C", str(PROJECT), "show", "--no-renames", "--name-only",
                            "--format=%ct%x00%B%x00", sha], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.count("\0") >= 2:
            at, message, names = r.stdout.split("\0", 2)
            out[sha] = {"paths": [p for p in names.splitlines() if p], "at": float(at or 0),
                        "message": message}
    return out


def landed_sessions(days: float, now: float | None = None, root: Path = burn.PROJECTS) -> tuple[list[dict], float]:
    """The sessions that landed, each with its cost and class, and the USD every session spent."""
    cutoff = (now or time.time()) - days * 86400
    rows, total = [], 0.0
    for path in root.glob("*/*.jsonl"):
        if path.stat().st_mtime < cutoff:
            continue
        usd, shas, ids = _session_cost_and_landings(path)
        total += usd
        if shas or ids:
            rows.append({"session": path.stem, "usd": usd, "shas": shas, "bound_ids": ids,
                         "mtime": path.stat().st_mtime})
    known = _commits([s for r in rows for s in r["shas"]])
    for r in rows:
        r["shas"] = [s for s in r["shas"] if s in known]
        r["commits"] = [known[s] for s in r["shas"]]
        r["class"] = classify([p for c in r["commits"] for p in c["paths"]])
    return [r for r in rows if r["shas"] or r["bound_ids"]], total


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


def level_steps(ledger: Path = LEVEL_LEDGER) -> list[dict]:
    """Every recorded level step, `{atom, ts}`, oldest first."""
    out = []
    for line in ledger.read_text().splitlines() if ledger.exists() else ():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if str(r.get("action", "")).startswith("LEVEL_UP") and r.get("atom"):
            out.append({"atom": str(r["atom"]), "ts": float(r.get("ts") or 0)})
    return sorted(out, key=lambda r: r["ts"])


def level_steps_since(cutoff: float, ledger: Path = LEVEL_LEDGER) -> int:
    return sum(1 for r in level_steps(ledger) if r["ts"] >= cutoff)


def _short(atom: str) -> str:
    m = re.match(r"[A-Z]+[0-9]+(?:_[0-9]+)?", atom)
    return m.group(0) if m else atom


def _atom_pattern(atom: str) -> re.Pattern:
    """The atom's full id, or the short key commits call it by (`D48`, `W2_42`), as a whole token:
    `W2_4` must not match `W2_42`, and `B1` must not match `B12`."""
    keys = [re.escape(atom)] + ([re.escape(_short(atom))] if _short(atom) != atom else [])
    return re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(keys) + r")(?![0-9]|_[0-9])")


def sessions_per_step(sessions: list[dict], steps: list[dict], cutoff: float) -> dict:
    """THE JOIN the backlog's range was waiting on: for each level step recorded since `cutoff`,
    the landed sessions whose landed commits NAME that atom (its id or short key, in the message)
    and were committed after the atom's previous step and no later than this one.

    A step no landed commit names is UNJOINED and kept out of the measure rather than counted as
    zero -- a step taken through a commit that never names its atom is common, and zero would be
    the flattering answer. Biased LOW for the window's earliest steps, whose work may predate the
    window's transcripts, and for any session that landed by a route other than the landing door."""
    prev: dict[str, float] = {}
    per, unjoined = [], 0
    for st in steps:
        start = prev.get(st["atom"], 0.0)
        prev[st["atom"]] = st["ts"]
        if st["ts"] < cutoff:
            continue
        pat = _atom_pattern(st["atom"])
        n = sum(1 for se in sessions
                if any(max(start, cutoff) < c["at"] <= st["ts"] and pat.search(c["message"])
                       for c in se.get("commits") or ()))
        if n:
            per.append(n)
        else:
            unjoined += 1
    if not per:
        return {"n": 0, "unjoined": unjoined, "median": None, "low": None, "high": None,
                "reason": f"no level step of the {unjoined} recorded in the window is named by a "
                          f"landed commit, so landed sessions per step cannot be measured"}
    per.sort()
    lo, hi = (per[0], per[-1]) if len(per) < THIN else statistics.quantiles(per, n=4)[0::2]
    return {"n": len(per), "unjoined": unjoined, "median": statistics.median(per),
            "low": lo, "high": hi, "thin": len(per) < THIN, "counts": per}


def item_class(text: str) -> str:
    """A drawn item's class, from the paths its own prose names; a direction item that names none
    is a record."""
    return classify(_PATH_TOKEN.findall(text or ""))


def estimate(cls: str, fit_: dict | None, sessions: float | None = None) -> dict:
    """Points for one piece of work of class `cls`: the class's per-session cost times the landed
    sessions such work takes. `{"refused": reason}` when the fit cannot price it."""
    if not fit_:
        return {"refused": "no fit has been written yet (run `python3 -m tools.work_cost_estimate`)"}
    c = (fit_.get("classes") or {}).get(cls)
    if c is None and fit_.get("pooled_median") is None:
        return {"refused": f"class {cls} has no landed history and there is no pooled median"}
    c = c or {"median": fit_["pooled_median"], "low": fit_["pooled_median"],
              "high": fit_["pooled_median"]}
    sp = fit_.get("sessions_per_step") or {}
    if sessions is None and sp.get("median") is None:
        return {"refused": sp.get("reason") or "landed sessions per piece of work is unmeasured"}
    k, k_lo, k_hi = ((sessions,) * 3 if sessions is not None
                     else (sp["median"], sp["low"], sp["high"]))
    return {"class": cls, "points": c["median"] * k, "low": c["low"] * k_lo, "high": c["high"] * k_hi}


def flag_note(item_text: str, fit_: dict | None = None) -> str:
    """The draw's warning, before the work starts, on an item expected above 10% of a week; "" else."""
    fit_ = load_fit() if fit_ is None else fit_
    est = estimate(item_class(item_text), fit_)
    if "refused" in est or est["points"] <= FLAG_POINTS:
        return ""
    return (f"COST FLAG -- this item is estimated at about {est['points']:.0f} points ({est['low']:.0f}-"
            f"{est['high']:.0f}, class {est['class']}), above {FLAG_POINTS:g} points, a tenth of the "
            f"week. Split it before starting, or say plainly in the record why it cannot be split. ")


def load_fit(path: Path = FIT_CACHE) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def record(event: dict, path: Path = COST_LEDGER) -> None:
    """Append one draw or landing row. Never raises: it is called from inside the draw."""
    try:
        with path.open("a") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
    except OSError:
        return


def estimates_against_actuals(sessions: list[dict], path: Path = COST_LEDGER) -> list[dict]:
    """Every item the draw estimated that has since had a landing bound: its first estimate, and
    its actual -- every session that bound a landing to it, subagents included, in points."""
    if path.suffix != ".jsonl":
        raise ValueError(f"{path} is not a .jsonl cost ledger")
    drawn, landed = {}, set()
    for line in path.read_text().splitlines() if path.exists() else ():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "drawn" and r.get("id") not in drawn and "points" in (r.get("estimate") or {}):
            drawn[r["id"]] = r
        elif r.get("event") == "landed":
            landed.add(r.get("id"))
    out = []
    for fid, r in drawn.items():
        spent = [se["usd"] for se in sessions if fid in (se.get("bound_ids") or ())]
        if fid in landed and spent:
            out.append({"id": fid, "class": r["estimate"]["class"], "estimate": r["estimate"]["points"],
                        "actual_usd": sum(spent), "sessions": len(spent)})
    return out


def error_by_class(rows: list[dict], usd_per_point: float) -> dict[str, dict]:
    """Actual over estimate, by class: the median ratio, and the items outside BADLY_WRONG."""
    by = defaultdict(list)
    for r in rows:
        r["actual"] = r["actual_usd"] / usd_per_point
        by[r["class"]].append(r)
    out = {}
    for cls, rs in by.items():
        ratios = [r["actual"] / r["estimate"] for r in rs if r["estimate"] > 0]
        out[cls] = {"n": len(rs), "median_ratio": statistics.median(ratios) if ratios else None,
                    "badly_wrong": [r["id"] for r in rs if r["estimate"] > 0 and not
                                    1 / BADLY_WRONG <= r["actual"] / r["estimate"] <= BADLY_WRONG]}
    return out


def atom_class(atom: dict) -> str:
    cls = classify(atom.get("file_scope") or [])
    if cls != OTHER:
        return cls
    lane = atom.get("lane") or ""
    return next((c for prefix, c in LANE_CLASS if lane.startswith(prefix)), LANE_DEFAULT)


def open_atoms() -> list[dict]:
    from tools import maturity_map_store as store
    out = []
    for a in store.load_live_atoms():
        gap = (a.get("level_target") or 0) - (a.get("level_current") or 0)
        if gap > 0:
            out.append({"id": a["id"], "class": atom_class(a), "steps": gap})
    return out


def open_atom_steps(atoms: list[dict] | None = None) -> dict[str, int]:
    steps: dict[str, int] = defaultdict(int)
    for a in open_atoms() if atoms is None else atoms:
        steps[a["class"]] += a["steps"]
    return dict(steps)


PRIORITY_ORDER = PROJECT / "docs" / "direction" / "priority_order.yaml"


def priority_fit(atoms: list[dict], fit_: dict, remaining: float | None,
                 path: Path = PRIORITY_ORDER) -> list[dict]:
    """The priority order's open atoms in its own order, each priced, with whether it fits in what
    the week has left once everything ahead of it is paid for. Priority is the director's; this
    reads it and never reorders it."""
    import yaml
    if path.suffix not in (".yaml", ".yml"):
        raise ValueError(f"{path} is not the priority order's .yaml")
    try:
        steps = (yaml.safe_load(path.read_text()) or {}).get("steps") or {}
    except (OSError, ValueError):
        return []
    live = {a["id"]: a for a in atoms}
    rows, spent = [], 0.0
    for n in sorted(steps, key=int):
        for aid in (steps[n] or {}).get("atoms") or ():
            a = live.get(aid)
            if a is None:
                continue
            est = estimate(a["class"], fit_)
            if "refused" in est:
                rows.append({"step": int(n), "id": aid, "refused": est["refused"]})
                continue
            pts = est["points"] * a["steps"]
            spent += pts
            rows.append({"step": int(n), "id": aid, "points": pts, "high": est["high"] * a["steps"],
                         "fits": remaining is not None and spent <= remaining,
                         "split": pts > FLAG_POINTS})
    return rows


def forecast(days: float = 30.0, now: float | None = None, write_fit: bool = True) -> dict:
    now = now or time.time()
    per = burn.usd_per_point()
    if per is None:
        return {"refused": "no point conversion: fewer than two of the director's readings on this tier"}
    cutoff = now - days * 86400
    every, total_usd = landed_sessions(days, now)
    sessions = [s for s in every if s["shas"]]
    landed_usd = sum(s["usd"] for s in sessions)
    overhead = total_usd / landed_usd if landed_usd else 1.0
    classes = fit(sessions, per, overhead)
    pooled = statistics.median([s["usd"] * overhead / per for s in sessions]) if sessions else None
    sp = sessions_per_step(sessions, level_steps(), cutoff)
    fit_ = {"written_at": now, "days": days, "usd_per_point": per, "classes": classes,
            "pooled_median": pooled, "sessions_per_step": sp}
    atoms = open_atoms()
    by_class = open_atom_steps(atoms)
    pts = {cls: (estimate(cls, fit_) if sp["median"] is not None else None) for cls in by_class}
    if sp["median"] is not None:
        low = sum(n * pts[c]["low"] for c, n in by_class.items())
        mid = sum(n * pts[c]["points"] for c, n in by_class.items())
        high = sum(n * pts[c]["high"] for c, n in by_class.items())
    else:
        low = mid = high = None
    advisor = sorted(p.name for p in ADVISOR_DIR.glob("DIRECTOR_*.md"))
    last_t, last_p = burn.POINT_READINGS[-1]
    read_at = time.mktime(time.strptime(last_t, "%Y-%m-%dT%H:%M")) - time.timezone
    used = None
    if read_at >= last_reset(now):
        used = last_p + burn.weighted_usd_between(last_t, time.strftime("%Y-%m-%dT%H:%M", time.gmtime(now))) / per
    remaining = None if used is None else max(0.0, WEEK_POINTS - used)
    misses = estimates_against_actuals(every)
    out = {"days": days, "usd_per_point": per, "landed_sessions": len(sessions), "classes": classes,
            "overhead": overhead, "total_points": total_usd / per,
            "pooled_median": pooled, "sessions_per_step": sp, "open_steps_by_class": by_class,
            "atom_backlog_points": (low, mid, high),
            "atom_backlog_weeks": tuple(None if x is None else x / WEEK_POINTS for x in (low, mid, high)),
            "advisor_files": advisor, "week_used_points": used, "week_remaining_points": remaining,
            "last_reading": (last_t, last_p), "priority": priority_fit(atoms, fit_, remaining),
            "estimate_vs_actual": misses, "error_by_class": error_by_class(misses, per)}
    if write_fit:
        fit_["plain"] = plain_words(out)
        try:
            FIT_CACHE.write_text(json.dumps(fit_, indent=1, sort_keys=True, default=list) + "\n")
        except OSError:
            pass
    return out


def plain_words(f: dict) -> str:
    """The forecast as the pace section of How it's built says it: four sentences, no table."""
    if "refused" in f:
        return f"not estimated: {f['refused']}"
    out = []
    rem = f["week_remaining_points"]
    out.append(f"the rest of this week can afford about {rem:.0f} of its {WEEK_POINTS:g} points"
               if rem is not None else "what is left of this week is not known: no usage reading since the reset")
    pr = [r for r in f["priority"] if "points" in r]
    if pr and rem is not None:
        fits = [r for r in pr if r["fits"]]
        nxt = next((r for r in pr if not r["fits"]), None)
        out.append(f"{len(fits)} of the {len(pr)} open atoms in the priority order fit in that, in order, "
                   f"at about {sum(r['points'] for r in fits):.0f} points"
                   + (f"; the first that does not is {_short(nxt['id'])} in step {nxt['step']}" if nxt else ""))
    wl, wm, wh = f["atom_backlog_weeks"]
    sp = f["sessions_per_step"]
    out.append(f"the atom backlog is about {wm:.1f} weeks at the full allowance ({wl:.1f} to {wh:.1f}), "
               f"from {sp['median']:g} landed sessions per level step measured over {sp['n']} steps"
               if wm is not None else f"the backlog in weeks is not measured: {sp['reason']}")
    split = [r for r in pr if r["split"]]
    out.append("items to split before they start, each above a tenth of a week: " + ", ".join(
        f"{_short(r['id'])} (about {r['points']:.0f} points)" for r in split)
        if split else "no item in the priority order is estimated above a tenth of a week")
    return "; ".join(out)


def render(days: float = 30.0, now: float | None = None) -> str:
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
    sp = f["sessions_per_step"]
    lo, mid, hi = f["atom_backlog_points"]
    if mid is not None:
        wl, wm, wh = f["atom_backlog_weeks"]
        lines += ["", f"**Landed sessions per level step:** median {sp['median']:g}, range {sp['low']:g}-"
                  f"{sp['high']:g} ({'thin: min-max' if sp['thin'] else 'quartiles'}), measured over {sp['n']} "
                  f"level steps named by a landed commit; {sp['unjoined']} step(s) no landed commit names "
                  f"are left out, not counted as zero. Biased LOW: work toward a step in a commit that "
                  f"does not name the atom is not counted.",
                  f"**Atom backlog:** {sum(f['open_steps_by_class'].values())} open level steps, about "
                  f"{mid:.0f} points ({lo:.0f}-{hi:.0f}), **{wm:.1f} weeks ({wl:.1f}-{wh:.1f})** at the full allowance."]
    else:
        lines += ["", f"**Atom backlog:** not measured -- {sp['reason']}."]
    lines.append(f"**Advisor queue:** {len(f['advisor_files'])} director file(s).")
    lines.append(f"**This week:** about {f['week_used_points']:.0f} of {WEEK_POINTS:g} points used (his reading "
                 f"of {f['last_reading'][1]:g}% at {f['last_reading'][0]} UTC plus spend since), so about "
                 f"{f['week_remaining_points']:.0f} remain." if f["week_used_points"] is not None
                 else f"**This week:** no reading since Monday's reset (last: {f['last_reading'][1]:g}% at "
                      f"{f['last_reading'][0]} UTC), so what remains is not known.")
    pr = f["priority"]
    if pr:
        lines += ["", "| step | atom | points | fits this week | split first |", "|---|---|---|---|---|"]
        for r in pr:
            if "refused" in r:
                lines.append(f"| {r['step']} | {_short(r['id'])} | not estimated: {r['refused']} | | |")
            else:
                lines.append(f"| {r['step']} | {_short(r['id'])} | {r['points']:.1f} (to {r['high']:.1f}) | "
                             f"{'yes' if r['fits'] else 'no'} | {'yes' if r['split'] else ''} |")
    err = f["error_by_class"]
    if err:
        lines += ["", "**Estimate against actual, by class** (actual over estimate; an item outside "
                  f"{BADLY_WRONG:g}x either way is a finding):"]
        for cls, e in sorted(err.items()):
            ratio = f"{e['median_ratio']:.2f}x" if e["median_ratio"] is not None else "no ratio"
            lines.append(f"- {cls}: {e['n']} item(s), median {ratio}"
                         + (f"; BADLY WRONG: {', '.join(e['badly_wrong'])}" if e["badly_wrong"] else ""))
    else:
        lines += ["", "**Estimate against actual:** no item drawn with an estimate has landed yet; the draw "
                  "records one on every Lane 0 item from now on."]
    lines.append("**Not yet estimated:** open findings (no classifier reads them yet).")
    return "\n".join(lines)


# COST PER RESULT AND REWORK RATE (director, 17 Nov 2026, 06:24 GMT: "Yes. But ideally I don't want to
# have to get involved in detailed results just steer strategy, direction and big goals."). Two standing
# lines in the Friday review, for the machine to act on; the definitions are fixed by
# docs/staging/records/SEAT_PREREG_COST_PER_RESULT_AND_REWORK_RATE_2026-11-17.md and change only by a
# dated amendment there. A result is one of three distinct experiences, never summed.

RESULT_KINDS = ("staging_closed", "level_move", "steer_done")
REWORK_DAYS = 14
_Z90 = 1.645


def results_of(sha: str, repo: Path = PROJECT) -> dict[str, int]:
    """The results one landed commit produced, by kind. A move is read as a delete in the source room
    plus an add of the same name in its done/ room, so a copy that leaves the original is not one."""
    out = dict.fromkeys(RESULT_KINDS, 0)
    r = subprocess.run(["git", "-C", str(repo), "show", "--no-renames", "--diff-merges=first-parent",
                        "--numstat", "--format=", sha], capture_output=True, text=True)
    s = subprocess.run(["git", "-C", str(repo), "show", "--no-renames", "--diff-merges=first-parent",
                        "--name-status", "--format=", sha], capture_output=True, text=True)
    if r.returncode or s.returncode:
        return out
    added, deleted = set(), set()
    for line in s.stdout.splitlines():
        status, _, path = line.partition("\t")
        (added if status == "A" else deleted if status == "D" else set()).add(path)
    for path in added:
        name = path.rsplit("/", 1)[-1]
        if path == f"docs/staging/done/{name}" and f"docs/staging/{name}" in deleted:
            out["staging_closed"] += 1
        elif path == f"docs/staging/advisor/done/{name}" and f"docs/staging/advisor/{name}" in deleted:
            out["steer_done"] += 1
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[2] == "docs/observability/gate_authorizations.jsonl" and parts[0].isdigit():
            out["level_move"] += int(parts[0])
    return out


def _mean_bound(xs: list[float], seed: int = 0) -> tuple[float, float]:
    """A 90% percentile-bootstrap bound on the mean, seeded so a re-render prints the same figure."""
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(xs, k=len(xs))) for _ in range(2000))
    return means[100], means[1899]


def _spend_once(since: float, root: Path = burn.PROJECTS) -> tuple[dict[str, float], dict[str, float], list[tuple[float, float]]]:
    """Every priced message since `since`, ONCE across all transcripts: a fork or a resumed session
    carries its parent's messages under the same ids, so a per-session sum counts them again (it read
    245 points for a week `tick_burn_rate.weighted_usd_between` puts at 87). A duplicated message goes
    to the transcript that started first. Returns usd by session, last activity by session, and every
    (timestamp, usd) so a week's whole spend is read by message time, as the point readings are."""
    def started(path: Path) -> str:
        with path.open(errors="replace") as fh:
            for line in fh:
                m = re.search(r'"timestamp":\s*"([^"]+)"', line)
                if m:
                    return m.group(1)
        return "9"
    cut = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(since))
    mains = [p for p in root.glob("*/*.jsonl") if p.stat().st_mtime >= since]
    files = [(p, p.stem) for p in mains] + [(q, p.stem) for p in mains for q in p.parent.glob(f"{p.stem}/subagents/*.jsonl")]
    files.sort(key=lambda f: started(f[0]))
    seen: set = set()
    usd: dict[str, float] = defaultdict(float)
    last: dict[str, float] = {}
    stamped: list[tuple[float, float]] = []
    for path, session in files:
        for line in path.read_text(errors="replace").splitlines():
            if '"assistant"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            msg, ts = row.get("message") or {}, row.get("timestamp") or ""
            if row.get("type") != "assistant" or not msg.get("usage") or ts < cut:
                continue
            if msg.get("model") == "<synthetic>" or msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            x = burn._priced(msg["usage"], msg.get("model"))
            t = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            usd[session] += x
            last[session] = max(last.get(session, 0.0), t)
            stamped.append((t, x))
    return usd, last, stamped


def cost_per_result(weeks: int = 4, now: float | None = None) -> dict:
    """Per week (0 = the last seven days), per kind: results, points per result with its bound, and the
    share of ALL spend in sessions that landed no result. A session landing several results splits its
    cost equally across them; spend that produced nothing is published beside, never spread over. A
    session belongs to the week of its last message."""
    now = now or time.time()
    per = burn.usd_per_point()
    if per is None:
        return {"refused": "no point conversion: fewer than two of the director's readings on this tier"}
    since = now - 7 * 86400 * weeks
    usd, last, stamped = _spend_once(since)
    totals = [0.0] * weeks
    for t, x in stamped:
        w = int((now - t) // (7 * 86400))
        if 0 <= w < weeks:
            totals[w] += x
    every, _ = landed_sessions(7.0 * weeks, now)
    claimed: set[str] = set()
    buckets = [{"costs": {k: [] for k in RESULT_KINDS}, "result_usd": 0.0} for _ in range(weeks)]
    for row in sorted(every, key=lambda r: last.get(r["session"], 0.0)):
        w = int((now - last.get(row["session"], now)) // (7 * 86400))
        if not 0 <= w < weeks:
            continue
        got = dict.fromkeys(RESULT_KINDS, 0)
        for sha in row["shas"]:
            if sha not in claimed:
                claimed.add(sha)
                for k, n in results_of(sha).items():
                    got[k] += n
        n_all = sum(got.values())
        if not n_all:
            continue
        cost = usd.get(row["session"], 0.0)
        buckets[w]["result_usd"] += cost
        for k, n in got.items():
            buckets[w]["costs"][k] += [cost / n_all / per] * n
    out = {"usd_per_point": per, "weeks": []}
    for w, b in enumerate(buckets):
        kinds = {}
        for k, xs in b["costs"].items():
            lo, hi = _mean_bound(xs)
            kinds[k] = {"n": len(xs), "points": statistics.fmean(xs) if xs else None, "low": lo, "high": hi}
        out["weeks"].append({"week": w, "total_points": totals[w] / per, "kinds": kinds,
                             "no_result_share": max(0.0, 1 - b["result_usd"] / totals[w]) if totals[w] else None})
    return out


def wilson(k: int, n: int, z: float = _Z90) -> tuple[float, float]:
    if not n:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def _is_code(path: str) -> bool:
    return path.endswith(".py") and not path.startswith("tests/")


def rework_of_commit(sha: str, tip: str, repo: Path = PROJECT) -> dict:
    """Of the code lines `sha` added, how many a later commit up to `tip` changed or deleted, read by
    `git blame --reverse`: a line that survives is last seen at `tip`, any other line died earlier."""
    added = changed = 0
    paths = [ln.split("\t")[2] for ln in _git(repo, "show", "--no-renames", "--numstat", "--format=", sha).splitlines()
             if ln.count("\t") == 2 and ln.split("\t")[0] not in ("0", "-") and _is_code(ln.split("\t")[2])]
    tip_full = _git(repo, "rev-parse", tip).strip()
    for path in paths:
        ranges = []
        for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", _git(repo, "diff", "-U0", f"{sha}^", sha, "--", path), re.M):
            start, count = int(m.group(1)), int(m.group(2) or 1)
            if count:
                ranges += ["-L", f"{start},{start + count - 1}"]
        if not ranges:
            continue
        blame = _git(repo, "blame", "--reverse", "-s", "-l", *ranges, f"{sha}..{tip}", "--", path)
        for line in blame.splitlines():
            if not line:
                continue
            added += 1
            changed += not line.lstrip("^").startswith(tip_full)
    return {"paths": paths, "added": added, "changed": changed}


def rework_rate(since: float, until: float, now: float | None = None, ref: str = "origin/main",
                repo: Path = PROJECT) -> dict:
    """Code commits landed on `ref` in [since, until), each read only once its 14 days have passed.
    An UPPER bound on rework: it cannot tell a correction from a follow-up planned in the result's own
    done-test, a reformat, or a sibling step of one planned chain."""
    now = now or time.time()
    until = min(until, now - REWORK_DAYS * 86400)
    rows, by_class = [], defaultdict(lambda: [0, 0])
    if until <= since:
        return {"commits": 0, "reworked": 0, "rows": rows, "by_class": {}, "matured_until": until}
    for line in _git(repo, "log", "--no-merges", "--format=%H %ct", f"--since={int(since)}",
                     f"--until={int(until)}", ref).splitlines():
        sha, ct = line.split()
        tip = _git(repo, "rev-list", "-1", "--first-parent", f"--until={int(ct) + REWORK_DAYS * 86400}", ref).strip()
        if not tip or subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, tip]).returncode:
            continue
        r = rework_of_commit(sha, tip, repo)
        if not r["added"]:
            continue
        r.update(sha=sha[:10], cls=classify(r["paths"]))
        rows.append(r)
        by_class[r["cls"]][0] += 1
        by_class[r["cls"]][1] += bool(r["changed"])
    k = sum(bool(r["changed"]) for r in rows)
    return {"commits": len(rows), "reworked": k, "bound": wilson(k, len(rows)),
            "lines_added": sum(r["added"] for r in rows), "lines_changed": sum(r["changed"] for r in rows),
            "by_class": {c: {"commits": n, "reworked": m, "bound": wilson(m, n)} for c, (n, m) in by_class.items()},
            "rows": rows, "matured_until": until}


def _pct(x: float | None) -> str:
    return "n/a" if x is None or x != x else f"{100 * x:.0f}%"


def render_results(weeks: int = 4, now: float | None = None) -> str:
    """The Friday review's two standing lines. For the machine to act on; the director gets only a
    strategic implication with a recommendation, never these numbers."""
    now = now or time.time()
    lines = ["**Cost per result** (points; a result is a staging item closed, a level move recorded, or a "
             "director steer moved to done -- three experiences, never summed). Week 0 is the last 7 days.", ""]
    c = cost_per_result(weeks, now)
    if "refused" in c:
        lines.append(f"NOT MEASURED -- {c['refused']}")
    else:
        lines += ["| week | spend | no-result share | " + " | ".join(RESULT_KINDS) + " |",
                  "|---|---|---|" + "---|" * len(RESULT_KINDS)]
        for w in c["weeks"]:
            cells = []
            for k in RESULT_KINDS:
                x = w["kinds"][k]
                if not x["n"]:
                    cells.append("0 results")
                elif x["low"] != x["low"]:
                    cells.append(f"{x['points']:.2f} (n=1, no bound)")
                else:
                    cells.append(f"{x['points']:.2f} ({x['low']:.2f}-{x['high']:.2f}, n={x['n']})")
            lines.append(f"| {w['week']} | {w['total_points']:.0f} | {_pct(w['no_result_share'])} | " + " | ".join(cells) + " |")
    lines += ["", f"**Rework rate** (code commits with any added line changed or deleted on the trunk within "
              f"{REWORK_DAYS} days; an upper bound -- planned follow-ups count). Each week is read once its "
              f"{REWORK_DAYS} days have passed, so the latest is the week ending {REWORK_DAYS} days ago.", "",
              "| week ending | code commits | reworked | 90% bound | lines changed | worst class |", "|---|---|---|---|---|---|"]
    end = now - REWORK_DAYS * 86400
    for w in range(weeks):
        hi, lo = end - 7 * 86400 * w, end - 7 * 86400 * (w + 1)
        r = rework_rate(lo, hi, now)
        if not r["commits"]:
            lines.append(f"| {time.strftime('%Y-%m-%d', time.gmtime(hi))} | 0 | | | | |")
            continue
        worst = max(((cl, v) for cl, v in r["by_class"].items() if v["commits"] >= 8),
                    key=lambda cv: cv[1]["reworked"] / cv[1]["commits"], default=None)
        lo_b, hi_b = r["bound"]
        lines.append(f"| {time.strftime('%Y-%m-%d', time.gmtime(hi))} | {r['commits']} | {_pct(r['reworked'] / r['commits'])} | "
                     f"{_pct(lo_b)}-{_pct(hi_b)} | {_pct(r['lines_changed'] / r['lines_added'] if r['lines_added'] else None)} | "
                     + (f"{worst[0]} {worst[1]['reworked']}/{worst[1]['commits']}" if worst else "none with 8+") + " |")
    lines += ["", "**Trust gates autonomy.** Where a class's rework rises for two read weeks with bounds that no "
              "longer overlap, add verification to that kind of work before widening its autonomy. Where cost "
              "per result moves, ask which kind moved and why before spending more there. Raise to the director "
              "only a strategic implication, as one line with a recommendation; never these numbers."]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=float, default=30.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--results", action="store_true",
                    help="cost per result and rework rate, the Friday review's two standing lines")
    args = ap.parse_args(argv)
    if args.results:
        print(render_results())
        return 0
    print(json.dumps(forecast(args.days), indent=2, default=list) if args.json else render(args.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
