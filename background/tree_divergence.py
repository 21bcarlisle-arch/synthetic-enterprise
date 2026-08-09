"""Tree divergence — how much uncommitted work is squatting in the shared tree, and whose.

THE RULING (director, DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09): the publish gate's
subject became a clean checkout of HEAD, so a lane's uncommitted work can no longer halt
publishing. That removes the punishment; this module supplies the accountability that replaces
it. Verbatim: *"squatting gets named daily, never punished via the public site."*

WHY IT IS NEEDED. Once the gate stops reading the working tree, uncommitted work becomes free —
and unmeasured. On 2026-08-09 KNIFE2 left 19 source files in the tree, committed nowhere on any
ref, while its atom was certified L2; the machine only noticed because those files reddened the
gate. Under the new gate nothing would have noticed at all. So the cost has to be MEASURED and
NAMED instead of enforced.

WHAT IT MEASURES (report-only, always):
  * COUNT   — source files diverging from HEAD. Generated artefacts are excluded, because the
              publish path rewrites ~180 of them every cycle and a measure that counts those
              reads as noise no matter how carefully anyone looks at it.
  * AGE     — how long the oldest divergence has sat, from file mtime.
  * BY LANE — attributed through `maturity_map.yaml`'s `file_scope`, where the map declares one.

TWO HONEST LIMITS, stated because a measure that hides its own error bars invites false
confidence:
  1. ATTRIBUTION IS PARTIAL. Many atoms carry `file_scope: []`, so a diverging file often maps to
     no atom at all. Those are reported as `unattributed:<top-dir>` rather than guessed at. The
     number of unattributed files is itself published — if it dominates, the measure is weak and
     says so.
  2. AGE IS MTIME, AND MTIME LIES UNDER MERGE. A merge rewrites every file it touches, so all 19
     KNIFE2 files shared one mtime (15:31:46Z) that was hours younger than the work. Age is
     therefore a FLOOR on how long something has squatted, never the true age. Treated as a
     signal, not a clock.

NEVER PUNISHES. Nothing here returns a value the publish path can block on. `--check` exits
non-zero for a human/cron caller, but the publish path only ever calls `write_artifact()`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_PATH = PROJECT_DIR / "docs" / "observability" / "tree_divergence.json"
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

# Paths the machine REWRITES every publish cycle. Divergence here is the pipeline breathing, not
# a lane squatting, and counting it would bury the signal (~180 of 236 changed paths on the day
# this was written).
GENERATED_PREFIXES = (
    "docs/observability/",
    "docs/reports/",
    "docs/market_data/",
    "docs/snapshots/",
    "docs/shadow/",
    "docs/state/",
    "site/",
    "node_modules/",
)

# Runtime state, excluded by CONVENTION rather than by list: in this repo a dotfile is machine
# state (`.tree.lock`, `.maintenance_reminder_sent.json`, `.publish_gate_state.json`,
# `.dispatcher_seen.json`), while source never starts with a dot. Both of the first two took the
# "oldest divergence" slot on this module's first runs -- i.e. the measure was reporting its own
# machinery, and `.tree.lock` is literally the lock the publish path holds while being measured.
# A directory dotted at some level (`.claude/hooks/foo.py`) is NOT caught, which is correct: that
# is real source.
def _is_runtime_state(rel: str) -> bool:
    return rel.rsplit("/", 1)[-1].startswith(".")

# Thresholds. Chosen against the measured KNIFE2 episode (19 files, >1h) so that episode would
# have paged; deliberately not tighter, because a daily naming that fires every day names nothing.
FILE_COUNT_THRESHOLD = 15
AGE_HOURS_THRESHOLD = 4.0


def _is_generated(rel: str) -> bool:
    return rel.startswith(GENERATED_PREFIXES) or _is_runtime_state(rel)


def changed_paths(project_dir: Path | None = None) -> list[str]:
    """Repo-relative paths differing from HEAD (tracked modifications AND untracked files),
    generated artefacts excluded. Untracked counts: KNIFE2's new seam module was untracked, and
    an untracked file is the most invisible squat of all."""
    root = project_dir or PROJECT_DIR
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=str(root), capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        return []
    paths = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].strip()
        if " -> " in rel:            # rename: take the destination
            rel = rel.split(" -> ", 1)[1]
        rel = rel.strip('"')
        if not _is_generated(rel):
            paths.append(rel)
    return sorted(set(paths))


def _file_scope_index(map_path: Path | None = None) -> dict[str, str]:
    """path -> lane, from the map's declared `file_scope`. Best-effort and cheap: a line scan
    rather than a YAML load, because this runs every publish cycle and the map is ~400KB."""
    p = map_path or MAP_PATH
    index: dict[str, str] = {}
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return index
    lane = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("lane:"):
            lane = s.split(":", 1)[1].strip()
        elif s.startswith("file_scope:") and lane:
            inner = s.split(":", 1)[1].strip().lstrip("[").rstrip("]")
            for item in inner.split(","):
                item = item.strip().strip("'\"")
                if item:
                    index[item] = lane
    return index


def lane_for(rel: str, index: dict[str, str]) -> str:
    """The lane that declared this path, or an explicit `unattributed:` label. Never guesses."""
    if rel in index:
        return index[rel]
    return "unattributed:" + (rel.split("/", 1)[0] if "/" in rel else rel)


def measure(project_dir: Path | None = None, now: float | None = None,
            map_path: Path | None = None) -> dict:
    """The whole measure. PURE-ish: reads git + mtimes, writes nothing."""
    root = project_dir or PROJECT_DIR
    now = time.time() if now is None else now
    index = _file_scope_index(map_path)
    by_lane: dict[str, dict] = {}
    oldest_age = 0.0
    oldest_path = None
    paths = changed_paths(root)
    for rel in paths:
        try:
            age = max(0.0, now - (root / rel).stat().st_mtime)
        except OSError:
            age = 0.0
        lane = lane_for(rel, index)
        row = by_lane.setdefault(lane, {"count": 0, "oldest_age_hours": 0.0, "oldest_path": None})
        row["count"] += 1
        if age > row["oldest_age_hours"] * 3600:
            row["oldest_age_hours"] = round(age / 3600, 2)
            row["oldest_path"] = rel
        if age > oldest_age:
            oldest_age, oldest_path = age, rel
    attributed = sum(v["count"] for k, v in by_lane.items() if not k.startswith("unattributed:"))
    return {
        "measured_at": now,
        "total_files": len(paths),
        "attributed_files": attributed,
        "unattributed_files": len(paths) - attributed,
        "oldest_age_hours": round(oldest_age / 3600, 2),
        "oldest_path": oldest_path,
        "by_lane": dict(sorted(by_lane.items(), key=lambda kv: -kv[1]["count"])),
        "thresholds": {"files": FILE_COUNT_THRESHOLD, "age_hours": AGE_HOURS_THRESHOLD},
    }


def breaches(m: dict) -> list[str]:
    """Threshold breaches, as sentences. PURE (mutation-testable). Empty == nothing to name."""
    out = []
    if m["total_files"] > FILE_COUNT_THRESHOLD:
        out.append(
            "{} source files diverge from HEAD (threshold {})".format(
                m["total_files"], FILE_COUNT_THRESHOLD))
    if m["oldest_age_hours"] > AGE_HOURS_THRESHOLD:
        out.append(
            "the oldest has sat {}h (threshold {}h): {}".format(
                m["oldest_age_hours"], AGE_HOURS_THRESHOLD, m["oldest_path"]))
    return out


def top_squatters(m: dict, n: int = 3) -> str:
    rows = [(k, v) for k, v in m["by_lane"].items()][:n]
    return "; ".join("{} ({} files, oldest {}h)".format(k, v["count"], v["oldest_age_hours"])
                     for k, v in rows) or "none"


def write_artifact(m: dict, path: Path | None = None) -> Path:
    """Publish the measure. Called from the publish path; must never raise into it."""
    p = path or ARTIFACT_PATH
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:  # noqa: BLE001 -- an observer that can raise into the publish path it
        pass           # observes is itself a defect; the artefact is never load-bearing.
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Measure uncommitted divergence from HEAD, by lane.")
    ap.add_argument("--json", action="store_true", help="print the artefact")
    ap.add_argument("--check", action="store_true", help="exit 1 on a threshold breach")
    ap.add_argument("--write", action="store_true", help="write the artefact")
    args = ap.parse_args(argv)

    m = measure()
    if args.write:
        write_artifact(m)
    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
    else:
        print("tree divergence: {} source file(s) vs HEAD, oldest {}h ({} attributed, "
              "{} unattributed)".format(m["total_files"], m["oldest_age_hours"],
                                        m["attributed_files"], m["unattributed_files"]))
        print("  top: " + top_squatters(m))
        for b in breaches(m):
            print("  BREACH: " + b)
    return 1 if (args.check and breaches(m)) else 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/tree_divergence.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("tree_divergence")
    raise SystemExit(main())
