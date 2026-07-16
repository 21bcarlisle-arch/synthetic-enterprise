#!/usr/bin/env python3
"""Effort calibration -- observed cost distributions per lane, computed from
git-timestamped level transitions (G5_effort_sizing_discipline, CALIBRATION
half; docs/staging/done/EFFORT_SIZING_DISCIPLINE.md).

The gap this closes: nothing in this project estimates effort BEFORE work
starts, and maturity levels (L0-L5) describe MATURITY not EFFORT. But we have
something most backlogs sizing by guesswork do not: every level transition is
already git-timestamped (the `<atom-id> -> L<n>` convention used in this
repo's own commit subjects -- see `git log --oneline -- docs/design/
maturity_map.yaml`). This tool mines that history to compute REAL observed
cost distributions, so a future size estimate (S/M/L/XL, see
docs/design/EFFORT_SIZING_DESIGN.md) can be checked against actuals instead of
argued from nothing.

Read-only. Two git subprocess calls (`git log`), no repo mutation, no edits to
maturity_map.yaml.

GUARDRAIL (dial, not a wall -- same law as every other diagnostic in this
project, R12 anti-goal-seek): this tool produces a DIAGNOSTIC distribution. It
is never a target, never a completion gate, and its output must never be used
to judge whether a specific atom "should" have been faster. See
docs/design/EFFORT_SIZING_DESIGN.md.

CLI:
    python3 -m tools.effort_calibration            # human-readable summary
    python3 -m tools.effort_calibration --json      # full report as JSON
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MATURITY_MAP_YAML = PROJECT / "docs" / "design" / "maturity_map.yaml"

# An atom's full id (e.g. "H10_worktree_isolation") is abbreviated to a short
# code (e.g. "H10") in this repo's own commit subjects. This regex derives
# that short code from the full id: leading letters+digits, plus any further
# "_<digits>" groups (so "W2_10_dd_attribution_confound" -> "W2_10").
_SHORT_CODE_RE = re.compile(r"^[A-Za-z]+\d+(?:_\d+)*")

# The transition arrow itself: "-> L3", "->L3", embedded as "L0->L2" etc.
# Only the TARGET level (after the arrow) is captured -- the FROM level, if
# present in the text, is redundant with the previous transition's TO level.
_ARROW_RE = re.compile(r"->\s*L(\d+)")


@dataclass
class LevelTransition:
    atom_id: str
    lane: Optional[str]
    size: Optional[str]
    to_level: int
    commit_sha: str
    timestamp: int  # unix epoch seconds, commit time (%ct)
    message: str


# ---------------------------------------------------------------------------
# Atom registry (current map state -- read-only)
# ---------------------------------------------------------------------------
def load_atom_registry(map_path: Path = MATURITY_MAP_YAML) -> dict[str, dict]:
    """atom id -> {'lane': ..., 'size': ...} for every atom currently in the
    map. `size` is None for every atom today (the field does not exist yet --
    see docs/design/EFFORT_SIZING_DESIGN.md); reading it here means the
    per-size calibration in `calibration_by_size` activates automatically the
    day FRAME starts populating it, with no change to this tool."""
    data = yaml.safe_load(map_path.read_text()) or []
    registry: dict[str, dict] = {}
    for atom in data:
        aid = atom.get("id")
        if not aid:
            continue
        registry[aid] = {"lane": atom.get("lane"), "size": atom.get("size")}
    return registry


def build_short_code_index(atom_ids) -> dict[str, list[str]]:
    """short-code -> list of full atom ids sharing it. len(list) > 1 means the
    short code is AMBIGUOUS in commit-message text (observed once in this
    repo's real history: "F5" is shared by F5_ofgem_licence_readiness and
    F5_vat_control_independent_signal) -- such codes are excluded from
    parsing rather than guessed."""
    index: dict[str, list[str]] = defaultdict(list)
    for aid in atom_ids:
        m = _SHORT_CODE_RE.match(aid)
        short = m.group(0) if m else aid
        index[short].append(aid)
    return dict(index)


# ---------------------------------------------------------------------------
# Commit-subject parsing
# ---------------------------------------------------------------------------
def _find_short_code_occurrences(
    message: str, short_codes: list[str]
) -> list[tuple[int, int, str]]:
    """[(start, end, short_code), ...] sorted by position in `message`. A
    short code must not be immediately preceded/followed by an alnum char
    (word-ish boundary) and must not be immediately followed by a digit
    (prevents "H1" false-matching inside "H10"); an underscore or letter
    immediately after IS allowed (e.g. "F6_rebuild" for atom "F6...")."""
    occurrences = []
    for code in short_codes:
        for m in re.finditer(re.escape(code), message):
            start, end = m.start(), m.end()
            before = message[start - 1] if start > 0 else ""
            after = message[end] if end < len(message) else ""
            if before.isalnum():
                continue
            if after.isdigit():
                continue
            occurrences.append((start, end, code))
    occurrences.sort(key=lambda t: t[0])
    return occurrences


def parse_transitions_from_message(
    message: str, short_codes: list[str]
) -> list[tuple[str, int]]:
    """Return [(short_code, to_level), ...] found in one commit subject. Each
    atom-code occurrence is paired with the nearest following "->L<n>" arrow
    that appears BEFORE the next atom-code occurrence starts -- a bounded
    window so one atom's arrow is never attributed to a neighbour when a
    single commit bundles several transitions (e.g. "C9->L3+W2_7->L3,
    C10->L3+W2_8->L3" -- a real subject from this repo's history)."""
    occ = _find_short_code_occurrences(message, short_codes)
    arrows = [(m.start(), int(m.group(1))) for m in _ARROW_RE.finditer(message)]
    results: list[tuple[str, int]] = []
    for i, (start, end, code) in enumerate(occ):
        window_end = occ[i + 1][0] if i + 1 < len(occ) else len(message)
        candidate = next(
            (lvl for pos, lvl in arrows if end <= pos < window_end), None
        )
        if candidate is not None:
            results.append((code, candidate))
    return results


# ---------------------------------------------------------------------------
# Git history walk
# ---------------------------------------------------------------------------
def git_log_transitions(
    map_path: Path = MATURITY_MAP_YAML, repo_root: Path = PROJECT
) -> list[LevelTransition]:
    """Walk `git log` on maturity_map.yaml, parse each commit subject for
    atom-level transitions per the repo's own "<id> -> L<n>" convention.
    Read-only (a single `git log`), never mutates the map."""
    registry = load_atom_registry(map_path)
    short_index = build_short_code_index(registry.keys())
    ambiguous = {c for c, ids in short_index.items() if len(ids) > 1}
    unambiguous_codes = [c for c in short_index if c not in ambiguous]

    rel = str(map_path.relative_to(repo_root))
    log = subprocess.run(
        ["git", "log", "--pretty=format:%H|%ct|%s", "--", rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    transitions: list[LevelTransition] = []
    for line in log.splitlines():
        if not line.strip():
            continue
        sha, ts, subject = line.split("|", 2)
        for code, level in parse_transitions_from_message(subject, unambiguous_codes):
            full_id = short_index[code][0]
            info = registry.get(full_id, {})
            transitions.append(
                LevelTransition(
                    atom_id=full_id,
                    lane=info.get("lane"),
                    size=info.get("size"),
                    to_level=level,
                    commit_sha=sha,
                    timestamp=int(ts),
                    message=subject,
                )
            )
    return transitions


# ---------------------------------------------------------------------------
# Duration / distribution computation
# ---------------------------------------------------------------------------
def compute_durations(transitions: list[LevelTransition]) -> list[dict]:
    """Real observed cost per transition: elapsed hours between an atom's
    consecutive level-transition commits, oldest -> newest. An atom's FIRST
    recorded transition has no prior anchor in this history and yields no
    duration -- we never guess a start time. Same-commit / non-positive gaps
    (two transitions landed in one commit, or the rare rebased/backdated
    commit) are dropped rather than counted as zero or negative cost."""
    by_atom: dict[str, list[LevelTransition]] = defaultdict(list)
    for t in transitions:
        by_atom[t.atom_id].append(t)

    durations: list[dict] = []
    for atom_id, events in by_atom.items():
        events_sorted = sorted(events, key=lambda t: t.timestamp)
        for prev, cur in zip(events_sorted, events_sorted[1:]):
            hours = (cur.timestamp - prev.timestamp) / 3600.0
            if hours <= 0:
                continue
            durations.append(
                {
                    "atom_id": atom_id,
                    "lane": cur.lane,
                    "size": cur.size,
                    "from_level": prev.to_level,
                    "to_level": cur.to_level,
                    "hours": round(hours, 2),
                    "from_sha": prev.commit_sha,
                    "to_sha": cur.commit_sha,
                }
            )
    return durations


def _distribution(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    values = sorted(values)
    dist = {
        "n": len(values),
        "mean_hours": round(statistics.mean(values), 2),
        "median_hours": round(statistics.median(values), 2),
        "min_hours": round(values[0], 2),
        "max_hours": round(values[-1], 2),
    }
    if len(values) > 1:
        dist["stdev_hours"] = round(statistics.stdev(values), 2)
    return dist


def calibration_by_lane(durations: list[dict]) -> dict[str, dict]:
    """Observed cost distribution per lane -- the CALIBRATION half of G5.
    Lane comes from each atom's CURRENT `lane` field in maturity_map.yaml
    (an atom cannot change lane, so this is safe to read at report time
    rather than needing to be captured per-commit)."""
    by_lane: dict[str, list[float]] = defaultdict(list)
    for d in durations:
        by_lane[d["lane"] or "unknown_lane"].append(d["hours"])
    return {lane: _distribution(vals) for lane, vals in sorted(by_lane.items())}


def calibration_by_size(durations: list[dict]) -> dict:
    """Observed cost distribution per S/M/L/XL band, per
    docs/design/EFFORT_SIZING_DESIGN.md's proposed `size` field. No atom
    carries that field yet (2026-07-16) -- this returns an explicit
    'no_size_data_yet' status rather than silently reporting empty bands, so a
    caller can tell "not measured yet" apart from "zero observed cost". Once
    FRAME starts setting `size:` on atoms in the map, this activates with no
    change to this function."""
    by_size: dict[str, list[float]] = defaultdict(list)
    for d in durations:
        if d["size"]:
            by_size[d["size"]].append(d["hours"])
    if not by_size:
        return {"status": "no_size_data_yet", "bands": {}}
    return {
        "status": "ok",
        "bands": {size: _distribution(vals) for size, vals in sorted(by_size.items())},
    }


# ---------------------------------------------------------------------------
# Top-level report
# ---------------------------------------------------------------------------
def build_report(repo_root: Path = PROJECT, map_path: Path = MATURITY_MAP_YAML) -> dict:
    registry = load_atom_registry(map_path)
    short_index = build_short_code_index(registry.keys())
    ambiguous_codes = sorted(c for c, ids in short_index.items() if len(ids) > 1)

    transitions = git_log_transitions(map_path=map_path, repo_root=repo_root)
    durations = compute_durations(transitions)

    return {
        "generated_from": "git log -- docs/design/maturity_map.yaml (commit subjects)",
        "n_transitions_parsed": len(transitions),
        "n_durations_computed": len(durations),
        "ambiguous_short_codes_excluded": ambiguous_codes,
        "by_lane": calibration_by_lane(durations),
        "by_size": calibration_by_size(durations),
        "guardrail": (
            "DIAL not a WALL -- diagnostic only, never a target or completion "
            "gate (R12 anti-goal-seek). See docs/design/EFFORT_SIZING_DESIGN.md."
        ),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="emit the full report as JSON"
    )
    args = parser.parse_args(argv)

    report = build_report()

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("Effort calibration -- observed cost from git-timestamped level transitions")
    print(
        f"  transitions parsed: {report['n_transitions_parsed']}, "
        f"durations computed: {report['n_durations_computed']}"
    )
    if report["ambiguous_short_codes_excluded"]:
        print(
            "  excluded ambiguous short codes: "
            + ", ".join(report["ambiguous_short_codes_excluded"])
        )
    print("  by lane:")
    any_lane = False
    for lane, dist in report["by_lane"].items():
        if dist.get("n"):
            any_lane = True
            print(
                f"    {lane}: n={dist['n']} mean={dist['mean_hours']}h "
                f"median={dist['median_hours']}h min={dist['min_hours']}h "
                f"max={dist['max_hours']}h"
            )
    if not any_lane:
        print("    (no durations computed)")
    print(f"  by size: {report['by_size']['status']}")
    print(f"  {report['guardrail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
