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

# STARTING size-band anchors (hours), docs/design/EFFORT_SIZING_DESIGN.md
# section 2/4 -- derived from this repo's own real per-lane calibration run
# (2026-07-16: H_harness median ~28h, A_strategy_governance 2-22h,
# W2_customer_generator median ~0.27h), rounded to simple round-number
# anchors so they read as approximations, not false precision. These are a
# FALLBACK, used by expected_hours_for_atom() only until real `size`-tagged
# actuals exist for a band (calibration_by_size status "ok" with n>0) -- once
# they do, the real distribution wins (see expected_hours_for_atom). XL
# deliberately has NO anchor: XL is a decompose SIGNAL (section 3), not a
# quantity to forecast against -- sizing an XL atom would reward leaving it
# undecomposed.
SIZE_BAND_ANCHOR_HOURS: dict[str, float] = {
    "S": 1.0,
    "M": 12.0,
    "L": 28.0,
}


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
    """atom id -> {'lane', 'size', 'size_basis', 'level_current',
    'level_target', 'loop_stage', 'depends_on'} for every atom currently in
    the map. `size`/`size_basis` are None for every atom today (the fields do
    not exist yet -- see docs/design/EFFORT_SIZING_DESIGN.md); reading them
    here means the per-size calibration in `calibration_by_size` (and the
    remaining-effort / estimate-vs-actual / XL-decompose functions below)
    activate automatically the day FRAME starts populating them, with no
    change to this tool. The extra fields are additive -- existing callers
    that only read 'lane'/'size' are unaffected."""
    data = yaml.safe_load(map_path.read_text()) or []
    registry: dict[str, dict] = {}
    for atom in data:
        aid = atom.get("id")
        if not aid:
            continue
        registry[aid] = {
            "lane": atom.get("lane"),
            "size": atom.get("size"),
            "size_basis": atom.get("size_basis"),
            "level_current": atom.get("level_current"),
            "level_target": atom.get("level_target"),
            "loop_stage": atom.get("loop_stage"),
            "depends_on": atom.get("depends_on") or [],
        }
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
# L2 SIZING half -- remaining-effort, estimate-vs-actual, XL soft gate
# (docs/design/EFFORT_SIZING_DESIGN.md sections 2-5). All three read the
# registry + calibration output already built above; none of them mutate
# maturity_map.yaml or block anything on their own -- DIAL not a WALL (R12).
# ---------------------------------------------------------------------------
def expected_hours_for_atom(
    atom_id: str, registry: dict, by_lane: dict, by_size: dict
) -> tuple[Optional[float], str]:
    """Best-available expected-hours estimate for one atom, plus the basis
    used -- an honest fallback chain that never invents precision it doesn't
    have:
      1. a REAL calibrated actual for this atom's `size` band (by_size, once
         any atom has recorded one -- see calibration_by_size).
      2. the STARTING `SIZE_BAND_ANCHOR_HOURS` anchor for its size (design
         doc sections 2/4), used only until (1) has data.
      3. the REAL calibrated actual for this atom's `lane` (by_lane) -- used
         when the atom has no `size` at all yet.
      4. unknown (`None`, basis 'no_data') -- never guessed as zero.
    An atom sized `XL` never receives an hours figure (basis
    'xl_decompose_signal'): XL is a decomposition SIGNAL (design section 3),
    not a quantity to forecast -- giving it a number would reward leaving it
    undecomposed instead of splitting it."""
    info = registry.get(atom_id, {})
    size = info.get("size")
    lane = info.get("lane")
    if size == "XL":
        return None, "xl_decompose_signal"
    if size and by_size.get("status") == "ok":
        dist = by_size.get("bands", {}).get(size)
        if dist and dist.get("n"):
            return dist["mean_hours"], "calibrated_size_band:{}".format(size)
    if size and size in SIZE_BAND_ANCHOR_HOURS:
        return SIZE_BAND_ANCHOR_HOURS[size], "size_band_anchor:{}".format(size)
    if lane and by_lane.get(lane, {}).get("n"):
        return by_lane[lane]["mean_hours"], "lane_actual_fallback:{}".format(lane)
    return None, "no_data"


def remaining_effort_report(
    registry: Optional[dict] = None,
    *,
    map_path: Path = MATURITY_MAP_YAML,
    repo_root: Path = PROJECT,
    by_lane: Optional[dict] = None,
    by_size: Optional[dict] = None,
) -> dict:
    """Remaining-effort: below-target atoms (`level_current < level_target`,
    both fields present) sized via `expected_hours_for_atom`'s fallback
    chain, summed. This is the honest "sized" alternative to a plain
    below-target COUNT (an unsized count treats a 20-minute atom and a
    3-day atom as equal -- design doc section 1).

    `by_lane`/`by_size` are accepted directly (skipping the git walk) so
    callers/tests can supply a synthetic calibration without needing a real
    git repo -- when omitted, both are computed from `git_log_transitions`
    exactly as before (this is the path the CLI/digest use).

    GUARDRAIL: a forecast for prioritisation and decomposition, never a
    deadline or a completion criterion (R12 anti-goal-seek) -- carried in the
    returned dict so every consumer (digest, CLI, tests) sees it, not just
    this docstring."""
    registry = registry if registry is not None else load_atom_registry(map_path)
    if by_lane is None or by_size is None:
        transitions = git_log_transitions(map_path=map_path, repo_root=repo_root)
        durations = compute_durations(transitions)
        by_lane = by_lane if by_lane is not None else calibration_by_lane(durations)
        by_size = by_size if by_size is not None else calibration_by_size(durations)

    below_target = [
        aid
        for aid, info in registry.items()
        if info.get("level_current") is not None
        and info.get("level_target") is not None
        and info.get("level_current") < info.get("level_target")
    ]

    total_hours = 0.0
    sized_count = 0
    per_atom = []
    for aid in sorted(below_target):
        hours, basis = expected_hours_for_atom(aid, registry, by_lane, by_size)
        per_atom.append(
            {
                "atom_id": aid,
                "lane": registry[aid].get("lane"),
                "size": registry[aid].get("size"),
                "expected_hours": hours,
                "basis": basis,
            }
        )
        if hours is not None:
            total_hours += hours
            sized_count += 1

    return {
        "n_below_target": len(below_target),
        "n_sized": sized_count,
        "n_unsized": len(below_target) - sized_count,
        "total_expected_hours": round(total_hours, 2) if sized_count else None,
        "per_atom": per_atom,
        "guardrail": (
            "DIAL not a WALL -- a forecast for prioritisation/decomposition, "
            "never a deadline or completion criterion (R12 anti-goal-seek)."
        ),
    }


def estimate_vs_actual_by_lane(
    registry: Optional[dict] = None,
    *,
    map_path: Path = MATURITY_MAP_YAML,
    repo_root: Path = PROJECT,
    by_lane_actual: Optional[dict] = None,
    by_size: Optional[dict] = None,
) -> dict:
    """Per-lane estimate-vs-actual delta (design doc section 4's third use:
    "estimate-vs-actual as a LEARNING SIGNAL"). The ACTUAL side is the
    existing `calibration_by_lane` distribution (real git-timestamped
    durations); the ESTIMATE side is built from each lane's `size`-tagged
    atoms, using a real per-size calibrated mean once one exists and the
    `SIZE_BAND_ANCHOR_HOURS` starting anchor otherwise (XL excluded -- it has
    no anchor, see `expected_hours_for_atom`). A lane with either side empty
    reports `status: "insufficient_data"` rather than a misleading delta.

    `by_lane_actual`/`by_size` are accepted directly (skipping the git walk)
    so callers/tests can supply a synthetic calibration without needing a
    real git repo -- when omitted, both are computed from
    `git_log_transitions` exactly as before (the CLI/digest path).

    LEARNING SIGNAL, NOT A STICK (design section 5): a lane consistently
    running long/short against its own estimate says the LANE is poorly
    understood -- it is never evidence against a specific atom or the fork
    that built it."""
    registry = registry if registry is not None else load_atom_registry(map_path)
    if by_lane_actual is None or by_size is None:
        transitions = git_log_transitions(map_path=map_path, repo_root=repo_root)
        durations = compute_durations(transitions)
        by_lane_actual = (
            by_lane_actual if by_lane_actual is not None else calibration_by_lane(durations)
        )
        by_size = by_size if by_size is not None else calibration_by_size(durations)

    est_by_lane: dict[str, list[float]] = defaultdict(list)
    for info in registry.values():
        size = info.get("size")
        lane = info.get("lane")
        if not size or not lane or size == "XL":
            continue
        if by_size.get("status") == "ok":
            dist = by_size.get("bands", {}).get(size)
            if dist and dist.get("n"):
                est_by_lane[lane].append(dist["mean_hours"])
                continue
        if size in SIZE_BAND_ANCHOR_HOURS:
            est_by_lane[lane].append(SIZE_BAND_ANCHOR_HOURS[size])

    result: dict[str, dict] = {}
    for lane in sorted(set(by_lane_actual) | set(est_by_lane)):
        actual_dist = by_lane_actual.get(lane, {"n": 0})
        est_vals = est_by_lane.get(lane, [])
        if not est_vals or not actual_dist.get("n"):
            result[lane] = {
                "status": "insufficient_data",
                "n_estimates": len(est_vals),
                "n_actuals": actual_dist.get("n", 0),
            }
            continue
        est_mean = round(statistics.mean(est_vals), 2)
        actual_mean = actual_dist["mean_hours"]
        delta = round(actual_mean - est_mean, 2)
        direction = (
            "underestimated" if delta > 0 else ("overestimated" if delta < 0 else "on_target")
        )
        result[lane] = {
            "status": "ok",
            "estimate_mean_hours": est_mean,
            "actual_mean_hours": actual_mean,
            "delta_hours": delta,
            "direction": direction,
            "n_estimates": len(est_vals),
            "n_actuals": actual_dist["n"],
        }
    return result


def xl_decompose_flags(
    registry: Optional[dict] = None, *, map_path: Path = MATURITY_MAP_YAML
) -> list[dict]:
    """XL -> decompose SOFT GATE (design doc section 3). Flags -- NEVER
    blocks -- any atom sized `XL` that is BUILD-eligible (`loop_stage` not
    "idle") and has neither (a) child atoms recorded via some other atom's
    `depends_on` pointing at it -- evidence it was already decomposed -- nor
    (b) a non-empty `size_basis` recording an explicit exception (e.g.
    "genuinely atomic, cannot be split without breaking the exit test", per
    the design doc's (b) option). A SIGNAL for FRAME to act on before BUILD
    starts; this function never halts anything -- it only returns the list of
    atoms a caller (digest, CLI, a future FRAME checklist) should look at."""
    registry = registry if registry is not None else load_atom_registry(map_path)

    has_children: dict[str, bool] = defaultdict(bool)
    for info in registry.values():
        for dep in info.get("depends_on") or []:
            has_children[dep] = True

    flags = []
    for aid in sorted(registry):
        info = registry[aid]
        if info.get("size") != "XL":
            continue
        if info.get("loop_stage") == "idle":
            continue  # not BUILD-eligible yet -- nothing to gate
        if has_children[aid]:
            continue  # decomposed: other atoms declare depends_on this one
        if (info.get("size_basis") or "").strip():
            continue  # explicit basis recorded (may state the exception)
        flags.append(
            {
                "atom_id": aid,
                "lane": info.get("lane"),
                "loop_stage": info.get("loop_stage"),
                "reason": (
                    "size=XL, BUILD-eligible, no recorded child atoms and no "
                    "size_basis -- decompose before BUILD or record an "
                    "explicit one-line exception basis (soft gate, not a "
                    "block)."
                ),
            }
        )
    return flags


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
    parser.add_argument(
        "--remaining-effort", action="store_true",
        help="emit remaining_effort_report() as JSON (sized below-target atoms)",
    )
    parser.add_argument(
        "--estimate-vs-actual", action="store_true",
        help="emit estimate_vs_actual_by_lane() as JSON (per-lane learning signal)",
    )
    parser.add_argument(
        "--xl-flags", action="store_true",
        help="emit xl_decompose_flags() as JSON (XL -> decompose soft gate)",
    )
    args = parser.parse_args(argv)

    if args.remaining_effort:
        print(json.dumps(remaining_effort_report(), indent=2))
        return 0
    if args.estimate_vs_actual:
        print(json.dumps(estimate_vs_actual_by_lane(), indent=2))
        return 0
    if args.xl_flags:
        print(json.dumps(xl_decompose_flags(), indent=2))
        return 0

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
