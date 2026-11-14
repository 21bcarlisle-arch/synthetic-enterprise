"""The learning loop's measures, read from the commit record where the draw is made.

Design: docs/design/THE_LEARNING_LOOP_ON_HOW_WE_WORK.md §6 and §9. Insights: docs/institutional/
ways_of_working.md. The orienting seat's brief (`delivery_seat.build_brief`) carries `measures()`
under `learning_loop`, so the measures steer the next draw rather than sitting on a page.

Two trailers feed it. Nothing else is stored: the commit that grades is the record.

    Graded: <area> held=<n> missed=<n> [code=<n>] [reader=<n>] [regressed=<n>] [width=<x>]
    Cold-read: <surface> new-classes=<n>

`code` and `reader` count the misses whose cause was our model of our own code, or the reader
that measured it -- the two causes W1's stop condition counts. `regressed` counts graded rows
where the fix moved its target the wrong way. `width` is the median filed range width, as a
fraction of its centre, so a hit rate is never read without the widths that bought it.

A trailer that does not parse is returned under `unparsed` with its reason, never dropped:
a malformed grade read as "no grade" would make the hit rate look better than it is.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from statistics import median

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: W1's stop condition (ways_of_working.md): three code-or-reader misses in one area in seven days
#: stop fixes in that area until its map exists. Lane 0's draw applies it
#: (`delivery_lane._area_stops`).
STOP_MISSES = 3
WINDOW_DAYS = 7

_GRADED = re.compile(r"^Graded:\s*(\S+)\s+(.*)$", re.M)
_COLD = re.compile(r"^Cold-read:\s*(\S+)\s+(.*)$", re.M)
_KV = re.compile(r"(\w[\w-]*)=(\S+)")
_INT_KEYS = ("held", "missed", "code", "reader", "regressed")


def parse(body: str) -> tuple[list[dict], list[dict], list[str]]:
    """(grades, cold reads, refusals) from one commit message."""
    grades, colds, bad = [], [], []
    for area, rest in _GRADED.findall(body):
        kv = dict(_KV.findall(rest))
        if "held" not in kv or "missed" not in kv:
            bad.append(f"Graded: {area} -- needs held= and missed=")
            continue
        try:
            row = {"area": area.lower(), **{k: int(kv.get(k, 0)) for k in _INT_KEYS}}
            row["width"] = float(kv["width"]) if "width" in kv else None
        except ValueError:
            bad.append(f"Graded: {area} -- a count is not a whole number: {rest.strip()[:80]}")
            continue
        if row["code"] + row["reader"] > row["missed"]:
            bad.append(f"Graded: {area} -- code+reader {row['code'] + row['reader']} exceeds "
                       f"missed {row['missed']}")
            continue
        grades.append(row)
    for surface, rest in _COLD.findall(body):
        kv = dict(_KV.findall(rest))
        try:
            colds.append({"surface": surface, "new_classes": int(kv["new-classes"])})
        except (KeyError, ValueError):
            bad.append(f"Cold-read: {surface} -- needs new-classes=<n>")
    return grades, colds, bad


def _log(rev: str, days: int) -> str:
    r = subprocess.run(["git", "log", rev, f"--since={days}.days", "--format=%x00%h%x01%B"],
                       cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"git log {rev} failed: {r.stderr.strip()[:200]}")
    return r.stdout


def measures(rev: str = "origin/main", days: int = WINDOW_DAYS, log_text: str | None = None) -> dict:
    """Per-area hit rate with widths and the stop condition's count, regressions per fix,
    escapes per cold read. Raises nothing: an unreadable log is reported as such."""
    try:
        text = _log(rev, days) if log_text is None else log_text
    except Exception as exc:  # noqa: BLE001 - the brief must still be written; say why it is blank
        return {"unreadable": str(exc)[:200]}
    areas: dict[str, dict] = {}
    colds, unparsed = [], []
    fixes = regressed = 0
    for chunk in text.split("\x00"):
        if "\x01" not in chunk:
            continue
        sha, body = chunk.split("\x01", 1)
        grades, cold, bad = parse(body)
        unparsed += [f"{sha} {b}" for b in bad]
        colds += [{**c, "sha": sha} for c in cold]
        for g in grades:
            a = areas.setdefault(g["area"], {"held": 0, "missed": 0, "code_or_reader": 0,
                                             "widths": [], "grades": []})
            a["held"] += g["held"]
            a["missed"] += g["missed"]
            a["code_or_reader"] += g["code"] + g["reader"]
            if g["width"] is not None:
                a["widths"].append(g["width"])
            a["grades"].append(sha)
            fixes += 1
            regressed += g["regressed"]
    for a in areas.values():
        n = a["held"] + a["missed"]
        a["hit_rate"] = round(a["held"] / n, 3) if n else None
        widths = a.pop("widths")
        a["median_width"] = median(widths) if widths else None
        a["stop_condition_met"] = a["code_or_reader"] >= STOP_MISSES
    return {
        "window_days": days,
        "rev": rev,
        "by_area": areas,
        "regressions_per_fix": round(regressed / fixes, 3) if fixes else None,
        "fixes_graded": fixes,
        "escapes_per_cold_read": [c["new_classes"] for c in colds],
        "cold_reads": colds,
        "unparsed": unparsed,
        "repeat_failures": None,  # needs each insight's change date; ways_of_working.md, by hand
        "how_to_feed": "a grading commit carries `Graded: <area> held=<n> missed=<n> code=<n> "
                       "reader=<n> regressed=<n> width=<x>`; a cold read carries `Cold-read: "
                       "<surface> new-classes=<n>`. Baseline before the trailer: W1, level-dd "
                       "45 held of 80, 26 code-or-reader misses, 8-10 Nov.",
    }

