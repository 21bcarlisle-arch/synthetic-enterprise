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

    Graded: none -- <reason>      the commit grades nothing, and says why; neither a grade nor a refusal
    Restates: <sha>               this commit restates <sha>'s grade in the form above

A commit cannot be amended once it is on origin, so a malformed grade is answered by a later commit
carrying `Restates:`. Its refusals then move from `unparsed` to `restated`, beside the restating sha,
rather than vanishing. The commit-msg gate runs `refuse_message` (this `parse`), so a new malformed
`Graded:` line is refused before it lands instead of being read here a week later.
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
_RESTATES = re.compile(r"^Restates:\s*([0-9a-f]{7,40})\b", re.M)
_KV = re.compile(r"(\w[\w-]*)=(\S+)")
_INT_KEYS = ("held", "missed", "code", "reader", "regressed")


def parse(body: str) -> tuple[list[dict], list[dict], list[str]]:
    """(grades, cold reads, refusals) from one commit message."""
    grades, colds, bad = [], [], []
    for area, rest in _GRADED.findall(body):
        if area.lower() == "none":
            if not rest.strip().startswith("--") or not rest.strip()[2:].strip():
                bad.append("Graded: none -- needs a reason after `--` saying why nothing is graded")
            continue
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


def area_map(area: str, rev: str = "origin/main") -> dict | None:
    """The area's map on `rev` -- {"path", "sha", "after"} -- or None. The convention is the one
    both landed maps follow (`delivery_lane._map_on_origin` reads the same stem):
    `docs/design/<AREA>_AREA_MAP*.md`. Where an area has several, the newest to be ADDED is the
    map; later edits to it do not re-land it. `after` is every commit on `rev` that descends from
    the landing (`%h`, as `_log` spells them): the only grades a map has not already answered."""
    stem = "docs/design/" + re.sub(r"[-_ ]+", "_", area).upper() + "_AREA_MAP"
    r = subprocess.run(["git", "log", rev, "--diff-filter=A", "-1", "--format=%h", "--",
                        stem + "*.md"], cwd=str(PROJECT_DIR), capture_output=True, text=True,
                       timeout=60)
    sha = r.stdout.strip() if r.returncode == 0 else ""
    if not sha:
        return None
    path = subprocess.run(["git", "show", "--format=", "--name-only", "--diff-filter=A", sha, "--",
                           stem + "*.md"], cwd=str(PROJECT_DIR), capture_output=True, text=True,
                          timeout=60).stdout.split()
    after = subprocess.run(["git", "log", "--format=%h", f"{sha}..{rev}"], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=60)
    if after.returncode != 0:
        raise RuntimeError(f"git log {sha}..{rev} failed: {after.stderr.strip()[:200]}")
    return {"path": path[0] if path else stem + "*.md", "sha": sha,
            "after": set(after.stdout.split())}


def measures(rev: str = "origin/main", days: int = WINDOW_DAYS, log_text: str | None = None,
             maps=None) -> dict:
    """Per-area hit rate with widths and the stop condition's count, regressions per fix,
    escapes per cold read. Raises nothing: an unreadable log is reported as such.

    W1 stops fixes in an area "until its map exists": once the area's map has landed on `rev`,
    the stop is spent, and the grades after the landing commit are counted apart
    (`misses_since_map` of `graded_since_map`) -- the numbers W1's own measure is judged on. `maps(area) -> area_map(...) | None` is
    injectable so the partition can be tested without git."""
    maps = maps or (lambda area: area_map(area, rev))
    try:
        text = _log(rev, days) if log_text is None else log_text
    except Exception as exc:  # noqa: BLE001 - the brief must still be written; say why it is blank
        return {"unreadable": str(exc)[:200]}
    areas: dict[str, dict] = {}
    colds, refused, restates = [], [], {}
    fixes = regressed = 0
    for chunk in text.split("\x00"):
        if "\x01" not in chunk:
            continue
        sha, body = chunk.split("\x01", 1)
        grades, cold, bad = parse(body)
        refused += [(sha, b) for b in bad]
        restates.update({r: sha for r in _RESTATES.findall(body)})
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
            a.setdefault("by_grade", []).append((sha, g["code"] + g["reader"],
                                                 g["held"] + g["missed"]))
            fixes += 1
            regressed += g["regressed"]
    unparsed, restated = [], []
    for sha, b in refused:
        by = next((v for k, v in restates.items() if k.startswith(sha) or sha.startswith(k)), None)
        if by:
            restated.append(f"{sha} {b} [restated by {by}]")
        else:
            unparsed.append(f"{sha} {b}")
    for name, a in areas.items():
        n = a["held"] + a["missed"]
        a["hit_rate"] = round(a["held"] / n, 3) if n else None
        widths = a.pop("widths")
        a["median_width"] = median(widths) if widths else None
        by_grade = a.pop("by_grade")
        try:
            m = maps(name)
        except Exception as exc:  # noqa: BLE001 - an unread map is said, and the stop stays armed
            m, a["map_unreadable"] = None, str(exc)[:200]
        if m:
            a["map"] = {"path": m["path"], "sha": m["sha"]}
            since = [(n, k) for sha, n, k in by_grade if sha in m["after"]]
            a["misses_since_map"] = sum(n for n, _ in since)
            a["graded_since_map"] = sum(k for _, k in since)
            # W1: the stop holds "until its map exists". What the map then has to earn is W1's
            # own filed measure on the grades after it, printed beside the line, not a new STOP.
            a["stop_condition_met"] = False
        else:
            a["map"] = None
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
        "restated": restated,
        "repeat_failures": None,  # needs each insight's change date; ways_of_working.md, by hand
        "how_to_feed": "a grading commit carries `Graded: <area> held=<n> missed=<n> code=<n> "
                       "reader=<n> regressed=<n> width=<x>`; a cold read carries `Cold-read: "
                       "<surface> new-classes=<n>`. Baseline before the trailer: W1, level-dd "
                       "45 held of 80, 26 code-or-reader misses, 8-10 Nov.",
    }



def check_message(text: str) -> list[str]:
    """The refusals `parse` gives one commit message, comment lines dropped as git drops them."""
    body = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
    return parse(body)[2]



def refuse_message(path: str) -> int:
    """The commit-msg gate's leg: 1, with each refusal named on stderr, if the message at `path`
    carries a trailer `parse` refuses; else 0. Called from the hook by `python3 -c`, not as a
    `__main__`, so this module stays a library."""
    import sys

    refusals = check_message(Path(path).read_text(encoding="utf-8", errors="replace"))
    for r in refusals:
        print(f"[learning-loop] trailer refused: {r}. The form is `Graded: <area> held=<n> "
              f"missed=<n>` or `Graded: none -- <reason>` (background/learning_loop.py).",
              file=sys.stderr)
    return 1 if refusals else 0
