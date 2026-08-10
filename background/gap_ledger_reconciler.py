"""ONE reconciliation for the whole couple_*/gap-tool FAMILY — declared vs actual, report-only.

PURPOSE
    `H_GAP_fabric_belief_truth_gap` has registered the same residual on three consecutive ticks:
    *"THE RUNNER IS STILL MANUAL ... nothing re-runs tools/couple_fabric.py, so these rows go
    stale unless a tick re-runs them, and the durable fix remains ONE reconciliation for the whole
    couple_*/gap-tool family (eleven tools, none with a production caller) rather than a patch to
    this one."* This is that reconciliation. It is deliberately NOT a patch to one tool, and it is
    deliberately NOT a runner: it makes the family's staleness OBSERVABLE, which is the half that
    generalises. Which surface should re-run a gap tool (publish path vs archive path) is the
    design pass `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09` explicitly
    refuses to guess at, and guessing it here would be the accretion
    `OPERATIONAL_COHERENCE_DESIGN_PASS` forbids.

WHY STALENESS IS THE MEASURABLE HALF
    A gap ledger row is a NUMBER ON A PUBLIC DOOR (site/data/proof.json renders every pair). The
    row records the commit it was measured at. So there is a mechanical, non-arbitrary question
    with a yes/no answer: **has the code that produced this number changed since?** If it has, the
    door is showing a reading taken by a program we no longer run. That is not a judgement call, a
    threshold, or a score (R12) — it is a fact about git, and it is the same fact for all thirteen
    rows, which is what makes one reconciliation possible where eleven patches were not.

GUARANTEES
    - REPORT-ONLY, like `process_reconciler` (G-R3). It reconciles and reports; it runs no gap
      tool, rewrites no ledger, and has no repair path by construction.
    - FAIL-CLOSED (R15). A row whose `run_git_commit` is missing, malformed, or unknown to git is
      DRIFT (`unattributable`) — never silently `current`. An unavailable check is a failed check.
    - DISCOVERED, NOT HAND-LISTED. Producers are found by reading source: a file that both
      performs a ledger WRITE and names the atom. A twelfth couple tool inherits this for free;
      an index that had to be edited would be fail-open (`feedback_index_is_a_fail_open_control`).
    - NO SECOND LIST. The declared pair set comes from `background.coupled_triad.build_coupling`,
      the coupling authority that already exists.

WIRING
    `background/reconcile_watch.py` (reconcile-watch.timer, committed IaC) folds this into the
    drift signature it already pages on, so the family's staleness reaches a human on a TRANSITION
    (R5) rather than sitting in a file nobody opens — which is the very failure mode being fixed.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "coupled_gap_ledger.json"

# Directories scanned for gap-ledger WRITERS. Both, because the family is not only `tools/`:
# `background/fabric_gap_ledger.py` and `background/weather_*_triad.py` write rows too, and a
# scan that missed them would attribute their rows to nothing and call that "no producer".
_WRITER_DIRS = ("tools", "background")

# The FAMILY named in the residual: the couple_* tools. Discovered by glob, so a new one joins
# automatically. Used only for the `never_landed` check below -- attribution uses _WRITER_DIRS.
_FAMILY_GLOB = "couple_*.py"

# A WRITE, not a mention. `background/coupled_triad.py` names half these atoms in its coupling
# table and `tools/generate_premise_demand_data.py` reads the ledger for the site -- neither
# produces a row, and attributing a row to its reader would make staleness meaningless.
_WRITE_MARKER = re.compile(r"write_gap_entry\s*\(|write_fabric_gap_entries\s*\(|--write-ledger")

CURRENT = "current"


def discover_writers(project_dir: Path | None = None) -> dict:
    """{repo-relative path: source text} for every module that WRITES the gap ledger."""
    root = Path(project_dir or PROJECT_DIR)
    found = {}
    for d in _WRITER_DIRS:
        for p in sorted((root / d).glob("*.py")):
            try:
                text = p.read_text(errors="ignore")
            except OSError:
                continue
            if _WRITE_MARKER.search(text):
                found[str(p.relative_to(root))] = text
    return found


def family_members(project_dir: Path | None = None) -> list:
    """The couple_* tool family, by glob (repo-relative, sorted)."""
    root = Path(project_dir or PROJECT_DIR)
    return sorted(str(p.relative_to(root)) for p in (root / "tools").glob(_FAMILY_GLOB))


def producers_for(atom_id: str, writers: dict) -> list:
    """Every ledger-writing module that names this atom. Sorted; possibly empty."""
    return sorted(path for path, text in writers.items() if atom_id and atom_id in text)


def commits_since(sha: str, paths: list, project_dir: Path | None = None):
    """Number of commits touching `paths` since `sha`. None => CANNOT TELL (unknown sha, no
    paths, git unavailable) -- the caller must treat None as drift, never as clean."""
    if not sha or not paths:
        return None
    root = str(project_dir or PROJECT_DIR)
    try:
        proc = subprocess.run(["git", "-C", root, "log", "--format=%H", f"{sha}..HEAD", "--"]
                              + list(paths), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return len([ln for ln in proc.stdout.splitlines() if ln.strip()])


def load_ledger(path=None) -> dict:
    try:
        data = json.loads(Path(path or LEDGER_PATH).read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _row_status(atom_id: str, row, writers: dict, since_fn) -> dict:
    """Reconcile ONE ledger row. Every non-`current` branch is a fact about the row or about
    git, never an inference about intent (R9)."""
    out = {"item": atom_id, "kind": "row", "producers": []}
    if not isinstance(row, dict):
        return {**out, "status": "unattributable", "detail": "row is not an object"}
    producers = producers_for(atom_id, writers)
    out["producers"] = producers
    if not producers:
        return {**out, "status": "no_producer",
                "detail": "no ledger-writing module names this atom -- nothing can refresh it"}
    sha = row.get("run_git_commit")
    if not isinstance(sha, str) or not sha.strip():
        return {**out, "status": "unattributable", "detail": "row carries no run_git_commit"}
    if not isinstance(row.get("measured_at"), str) or not row["measured_at"].strip():
        return {**out, "status": "unattributable", "detail": "row carries no measured_at"}
    n = since_fn(sha, producers)
    if n is None:
        return {**out, "status": "unattributable",
                "detail": f"run_git_commit {sha[:9]} is unknown to git -- freshness ungradeable"}
    if n > 0:
        return {**out, "status": "stale",
                "detail": (f"{n} commit(s) touched {', '.join(producers)} since {sha[:9]}; "
                           "the published number was produced by code that has changed")}
    return {**out, "status": CURRENT, "detail": f"producers unchanged since {sha[:9]}"}


def reconcile(ledger=None, writers=None, declared=None, family=None, since_fn=None) -> list:
    """DECLARED (the coupling authority + the discovered family) vs ACTUAL (the ledger on disk).
    Every argument is injectable so tests pin their own world and never read live disk."""
    ledger = load_ledger() if ledger is None else ledger
    writers = discover_writers() if writers is None else writers
    family = family_members() if family is None else family
    if since_fn is None:
        def since_fn(sha, paths):
            return commits_since(sha, paths)
    if declared is None:
        declared = _declared_pairs()

    results = [_row_status(atom_id, row, writers, since_fn)
               for atom_id, row in sorted(ledger.items())]
    for world_id in sorted(declared):
        if world_id not in ledger:
            results.append({"item": world_id, "kind": "pair", "producers": [],
                            "status": "never_measured",
                            "detail": "coupled pair declared in the map with no ledger row"})
    for path in family:
        if not any(path in r["producers"] for r in results):
            results.append({"item": path, "kind": "tool", "producers": [path],
                            "status": "never_landed",
                            "detail": "family gap tool whose output appears in no ledger row"})
    return results


def _declared_pairs() -> set:
    """World atoms the map says are coupled. Import failure => empty (this reconcile then reports
    only what the ledger itself shows), never a crash that would take the whole watch down."""
    try:
        from background.coupled_triad import _load_map_atoms, build_coupling
        return set(build_coupling(_load_map_atoms()).keys())
    except Exception:
        return set()


def drift(results: list) -> list:
    """The rows that diverge. Clean == []."""
    return [r for r in results if r.get("status") != CURRENT]


def summary_lines(results: list) -> list:
    d = drift(results)
    if not d:
        return [f"[GAP-LEDGER] clean -- all {len(results)} gap rows measured by current code."]
    lines = [f"[GAP-LEDGER] DRIFT -- {len(d)} of {len(results)} gap entries diverge:"]
    lines += [f"    x [{r['status']}] {r['item']}: {r['detail']}" for r in d]
    return lines


# --- THE WORK LIST -----------------------------------------------------------------------------
# The reconcile above says WHICH rows are stale. This says WHICH OF THOSE A RE-RUN COULD CLEAR,
# and by running what. It is the drain the drift set needs: a ratchet with no drain is a cleanup,
# not a control (feedback_a_ratchet_with_no_drain_is_a_cleanup_not_a_control), and a drift set no
# lane can act on is the shape that let a red operational signal page for 13 hours with no draw
# rung behind it. Ownership of the re-run is decided in docs/design/GAP_TOOL_RERUN_OWNERSHIP.md:
# the DRAW LADDER owns it, not this module and not the watcher -- so this stays REPORT-ONLY by
# construction (G-R3). It prints commands; it has never run one.

# A row is refreshable iff RE-MEASURING IT would change its verdict. `stale` and `unattributable`
# both describe a row whose recorded measurement is not gradeable against current code, and both
# are cleared by taking the measurement again. `never_measured` (a declared pair with no row) and
# `never_landed` (a tool whose output lands nowhere) are NOT: re-running changes nothing, because
# the defect is that no row exists to refresh. Keeping them out is what stops the draw rung
# WEDGING on an item it can never drain (feedback_control_that_can_only_fail_wedges).
REFRESHABLE_STATUSES = ("stale", "unattributable")

# An INVOCABLE producer: it writes the ledger (already true of every producer) AND can be run as a
# program with the write flag. `background/fabric_gap_ledger.py` writes rows through a function and
# has no `__main__` -- it is a producer but not a runner, and offering it as the refresh command
# would be a command that cannot be typed. The runner for its rows is the tool that imports it.
_RUNNER_MARKER = re.compile(r"--write-ledger")
_INVOCABLE_MARKER = re.compile(r"__main__")


def runners_for(producers: list, writers: dict) -> list:
    """The producers of this row that can actually be RUN to re-take its measurement."""
    return sorted(
        p for p in producers
        if _RUNNER_MARKER.search(writers.get(p, "") or "")
        and _INVOCABLE_MARKER.search(writers.get(p, "") or "")
    )


def refresh_command(runners: list) -> str | None:
    """The command a tick would run to re-measure the row. None when nothing is invocable.

    `-m dotted.module`, NOT `python3 path/to/tool.py`: every one of these tools imports
    `simulation.*` / `background.*`, so the path form dies on `ModuleNotFoundError` before it
    measures anything. Found by RUNNING one rather than reading it -- `python3
    tools/couple_w2_4_c6.py --write-ledger` failed in 0.2s, `python3 -m tools.couple_w2_4_c6
    --write-ledger` wrote the row in 0.5s.

    Deliberately the BASE invocation and nothing cleverer: some tools take an optional
    `--population`, and inventing arguments here would be a second, drifting copy of each tool's
    CLI. The acceptance test for the re-run is NOT that this exact string ran -- it is that the
    row reads CURRENT afterwards, which `reconcile()` decides independently of this string.
    """
    if not runners:
        return None
    module = runners[0][:-3].replace("/", ".") if runners[0].endswith(".py") else runners[0]
    return f"python3 -m {module} --write-ledger"


def refresh_work(results: list, writers=None) -> list:
    """[{item, status, runners, command, detail}] for every row a re-run could clear.

    FAIL-CLOSED: a refreshable row whose producers are all un-invocable stays IN this list with
    `command: None` and `no_runner: True`. It is a worse defect than a stale row (a published
    number with no way to re-take it), so it must not be the one entry that silently vanishes --
    that is the exclusion-shaped fail-open this project already has memory of
    (feedback_coverage_derived_from_exclusion_source_is_failopen).
    """
    writers = discover_writers() if writers is None else writers
    work = []
    for r in results:
        if r.get("status") not in REFRESHABLE_STATUSES:
            continue
        runners = runners_for(r.get("producers") or [], writers)
        work.append({
            "item": r["item"],
            "status": r["status"],
            "runners": runners,
            "command": refresh_command(runners),
            "no_runner": not runners,
            "detail": r.get("detail", ""),
        })
    return work


def refresh_lines(work: list) -> list:
    if not work:
        return ["[GAP-LEDGER] no refreshable rows -- nothing a re-run would clear."]
    lines = [f"[GAP-LEDGER] {len(work)} row(s) a re-run would clear:"]
    for w in work:
        how = w["command"] or "NO INVOCABLE PRODUCER -- this row cannot be re-taken (defect)"
        lines.append(f"    -> {w['item']} [{w['status']}]: {how}")
    return lines


def main(argv: list) -> int:
    results = reconcile()
    print("\n".join(summary_lines(results)))
    if "--refresh-work" in (argv or []):
        print("\n".join(refresh_lines(refresh_work(results))))
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/gap_ledger_reconciler.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("gap_ledger_reconciler")
    raise SystemExit(main(sys.argv))
