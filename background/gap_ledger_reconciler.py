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

# A row re-measured on disk and never committed. Drift (the door still shows the old number), but
# NOT `stale`: the repair is to land the measurement, not to take it again. See `landed_ledger`.
MEASURED_NOT_LANDED = "measured_not_landed"


# THE GRADER IS NOT A PRODUCER, and excluding it is not cosmetic (2026-08-11).
# This module quotes `--write-ledger` (in `_RUNNER_MARKER` and in the commands it prints), so it
# matches `_WRITE_MARKER` and has ALWAYS been discovered as a ledger writer. That was latent only
# because its text happened to name no atom id: `producers_for` attributes a row to any writer
# whose SOURCE CONTAINS THE ATOM ID, so the first comment, docstring or evidence note here that
# mentions one silently makes this module a "producer" of that row -- and every commit to the
# GRADER then marks the row it grades as stale. That is the module's own stated tautology
# ("attributing a row to its READER would make freshness true by construction") pointing at
# itself, and it fails in the direction that manufactures work rather than hiding it.
# Caught the same tick it was armed, by reading the producer list in the module's own output.
_SELF = "background/gap_ledger_reconciler.py"


def discover_writers(project_dir: Path | None = None) -> dict:
    """{repo-relative path: source text} for every module that WRITES the gap ledger.

    Excludes this module itself -- see `_SELF`. A grader that can appear in its own producer set
    grades its own commits, which is not a fact about any measurement.
    """
    root = Path(project_dir or PROJECT_DIR)
    found = {}
    for d in _WRITER_DIRS:
        for p in sorted((root / d).glob("*.py")):
            rel = str(p.relative_to(root))
            if rel == _SELF:
                continue
            try:
                text = p.read_text(errors="ignore")
            except OSError:
                continue
            if _WRITE_MARKER.search(text):
                found[rel] = text
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


def ledger_is_readable(path=None) -> bool:
    """Whether the ledger FILE could be read and parsed at all.

    Separate from "the ledger has no rows", and the distinction is load-bearing (2026-08-10).
    `load_ledger` fails open to `{}` for a file that is absent or malformed, and every verdict
    downstream is then computed as though the ledger legitimately held nothing: every declared
    pair reads `never_measured` and every family tool reads `never_landed`. Those are not eleven
    orphaned tools, they are ONE missing file, and reporting them per-item would be an artefact of
    the read failing rather than a fact about any tool (feedback_population_defined_at_as_of_is_an
    _artefact). Caught by tests/background/test_rest_ladder_isolation.py, which pins the path at an
    absent file and got eleven work items back.
    """
    try:
        json.loads(Path(path or LEDGER_PATH).read_text())
    except (OSError, ValueError):
        return False
    return True


def load_ledger(path=None) -> dict:
    try:
        data = json.loads(Path(path or LEDGER_PATH).read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


# --- THE GRADED SUBJECT IS THE COMMITTED LEDGER, NOT THE ONE ON DISK ---------------------------
# 2026-08-11. This module graded `LEDGER_PATH` -- the WORKING TREE file -- and that made it
# fail-open in the exact dimension it exists to watch. The door renders a COMMITTED artefact:
# `site/data/proof.json` is built from the ledger and both are committed and pushed. So a re-run
# that updates the file on disk and is never committed moves the checked value while leaving the
# published one untouched, and this control then reports `clean` over a stale public number.
#
# Observed, with evidence (2026-08-11, worker tick, the draw that found it):
#     working tree  -> [GAP-LEDGER] clean -- all 14 gap rows measured by current code.
#     HEAD          -> [GAP-LEDGER] DRIFT -- 1 of 14: W2_11_payment_behaviour_source,
#                      6 commit(s) touched tools/couple_w2_11_d5.py since e6402d536
# `site/data/proof.json` carries a `W2_11_payment_behaviour_source` entry, so the stale reading
# was on the door while the control read clean. This is the working-tree-subject class the repo
# already has memory of (feedback_capability_index_reads_the_working_tree,
# feedback_gate_lints_working_tree_so_uncommitted_wedges_everyone) landing on a gap control.
#
# It is also why RUNG 4b could not have drawn the work: `_is_drained_and_gated` mirrors this
# module so rest cannot be declared over a stale published number, and an uncommitted re-run
# silenced exactly that guarantee.
#
# The fix is NOT "read HEAD and stop there". A row can be stale at HEAD because the measurement
# was taken and not committed -- and there the work is to LAND it, not to take it again. Re-taking
# is not free: this atom's own record spent a paragraph on a 4th-decimal move it declined to
# attribute, and re-running republishes a changed public figure. So the two cases get two statuses
# and two commands.


def _repo_relative(path) -> str | None:
    """`path` as a repo-relative string, or None when it is outside the repo (test fixtures)."""
    try:
        return str(Path(path).resolve().relative_to(PROJECT_DIR))
    except (ValueError, OSError):
        return None


def landed_ledger(path=None, project_dir: Path | None = None):
    """The ledger AS COMMITTED AT HEAD -- the version the public door renders from.

    Returns the parsed dict, or None when it cannot be read at HEAD for ANY reason (path outside
    the repo, path untracked, malformed blob, git unavailable). None is NOT an empty ledger and
    the caller must never treat it as one: an unavailable check is a FAILED check (R15).
    """
    rel = _repo_relative(path or LEDGER_PATH)
    if rel is None:
        return None
    root = str(project_dir or PROJECT_DIR)
    try:
        proc = subprocess.run(["git", "-C", root, "show", f"HEAD:{rel}"],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


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


def reconcile(ledger=None, writers=None, declared=None, family=None, since_fn=None,
              unlanded=None) -> list:
    """DECLARED (the coupling authority + the discovered family) vs ACTUAL (the COMMITTED ledger).

    The graded subject is the ledger at HEAD, because that is what the public door renders -- see
    the block above `landed_ledger`. `unlanded` is the working-tree ledger, used ONLY to tell a
    row that was never re-measured from one that was re-measured and never committed.

    Every argument is injectable so tests pin their own world and never read live disk.
    """
    if ledger is None:
        # An UNREADABLE ledger is one defect, not one per declared pair and one per family tool.
        # Reported as itself and nothing else -- see `ledger_is_readable`. It is drift (an
        # unavailable check is a FAILED check, R15), and it is not refreshable: no gap tool
        # re-run repairs a file that cannot be read.
        if not ledger_is_readable():
            return [{"item": str(LEDGER_PATH), "kind": "ledger", "producers": [],
                     "status": "ledger_unreadable",
                     "detail": "the gap ledger is absent or malformed -- no row, pair or tool "
                               "verdict can be graded until it reads"}]
        ledger = landed_ledger()
        if ledger is None:
            # The file reads on disk but NOT at HEAD. Distinct from unreadable, and distinct from
            # stale: nothing about the numbers is known to be wrong, but nothing about them is
            # PUBLISHED either, so no row verdict here would describe the door. Drift, and not
            # refreshable by a gap tool -- the repair is to commit the ledger.
            return [{"item": str(LEDGER_PATH), "kind": "ledger", "producers": [],
                     "status": "ledger_not_committed",
                     "detail": "the gap ledger reads on disk but not at HEAD -- the published "
                               "door renders a committed ledger, so no row can be graded"}]
        if unlanded is None:
            unlanded = load_ledger()
    writers = discover_writers() if writers is None else writers
    family = family_members() if family is None else family
    if since_fn is None:
        def since_fn(sha, paths):
            return commits_since(sha, paths)
    if declared is None:
        declared = _declared_pairs()

    results = [_row_status(atom_id, row, writers, since_fn)
               for atom_id, row in sorted(ledger.items())]
    # A row that is not current AT HEAD may still have been re-measured on disk. That is a
    # different defect with a different repair, so it gets its own status rather than being
    # folded into `stale` (which would send a tick to re-run a tool whose measurement already
    # exists, republishing a figure that can move) or into `current` (the fail-open being fixed).
    if unlanded:
        for r in results:
            if r.get("kind") != "row" or r.get("status") in (CURRENT, "no_producer"):
                continue
            disk_row = unlanded.get(r["item"])
            if disk_row is None:
                continue
            if _row_status(r["item"], disk_row, writers, since_fn).get("status") == CURRENT:
                r["status"] = MEASURED_NOT_LANDED
                r["detail"] = (
                    f"HEAD's row is not current ({r['detail']}), but the working-tree ledger "
                    "holds a measurement taken by current code -- the number was re-taken and "
                    "never committed, so the door still shows the old one")
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
# are cleared by taking the measurement again.
#
# `never_landed` JOINED THEM on 2026-08-10, and the reason the first cut got it wrong is worth
# keeping. The original exclusion read "no re-run clears a row that does not exist" and swept
# `never_measured` and `never_landed` into one sentence. They are not the same fact:
#
#   never_measured -- a pair the MAP declares with no ledger row and no producer to point at.
#                     There is nothing to run. Genuinely un-drainable; still excluded.
#   never_landed   -- a tool that EXISTS, on disk, in the discovered family. If it is invocable
#                     it can be run right now and the run is exactly what lands the row.
#
# `tools/couple_cohort.py` was reported never_landed for two days as a permanent member of a
# drift set no rung could act on -- and `python3 -m tools.couple_cohort` runs clean in seconds.
# The exclusion was not protecting the ladder from a wedge, it was hiding the one item on the
# list that a single command would have closed (feedback_a_ratchet_with_no_drain_is_a_cleanup).
#
# The wedge concern was real, and it survives as a NARROWER rule below rather than as a status
# ban: a never_landed tool with no invocable runner is still excluded from the work list, because
# there the ITEM IS THE TOOL and no command exists that could ever land its row.
REFRESHABLE_STATUSES = ("stale", "unattributable", "never_landed")

# Statuses whose item is a TOOL (the thing to run) rather than a ROW (a number on a public door).
# The distinction decides what happens when nothing is invocable -- see `refresh_work`.
_TOOL_ITEM_STATUSES = ("never_landed",)

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

    FAIL-CLOSED FOR A ROW: a refreshable ROW whose producers are all un-invocable stays IN this
    list with `command: None` and `no_runner: True`. It is a worse defect than a stale row (a
    published number with no way to re-take it), so it must not be the one entry that silently
    vanishes -- that is the exclusion-shaped fail-open this project already has memory of
    (feedback_coverage_derived_from_exclusion_source_is_failopen).

    THE ASYMMETRY, and it is deliberate: a `never_landed` item is a TOOL, not a row. Nothing is
    published, so there is no number anyone could act on wrongly, and no command exists that
    could ever land one -- listing it would make the rung permanently non-empty, which is the
    wedge (feedback_control_that_can_only_fail_wedges). It stays in the DRIFT set, where it is
    reported and visible; it is only kept off the WORK list. A row hides a live public figure
    behind its absence; a dead tool hides nothing.
    """
    writers = discover_writers() if writers is None else writers
    work = []
    for r in results:
        status = r.get("status")
        if status == MEASURED_NOT_LANDED:
            # The measurement exists; the command is to LAND it, not to re-take it. Re-running
            # here would be the worst of both: it republishes a figure that can move, to fix a
            # problem that was only ever that the existing figure was never committed.
            work.append({
                "item": r["item"], "status": status, "runners": [],
                "command": (f"python3 -m tools.surgical_land -m 'chore(gap-ledger): land the "
                            f"{r['item']} measurement' -- {_repo_relative(LEDGER_PATH)}"),
                "no_runner": False, "detail": r.get("detail", ""),
            })
            continue
        if status not in REFRESHABLE_STATUSES:
            continue
        runners = runners_for(r.get("producers") or [], writers)
        if not runners and status in _TOOL_ITEM_STATUSES:
            continue
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
