"""FORK SALVAGE — make the bounded-invocation kill NON-LOSSY (director console, 2026-08-03).

PURPOSE. A fork's built work must survive the death of the process that dispatched it. Today it
does not, and that is the actual defect behind "forks die without merging".

WHY THIS EXISTS (observed, not inferred — R9). `worker-tick.service` is `Type=oneshot` with
`TimeoutStartSec=1800`, and its own comment reasons that the 30-minute SIGTERM makes a hang "a
skipped tick ... never a wedge". That reasoning is wrong in one specific way: systemd tears down
the WHOLE cgroup, so the kill takes the `claude -p` invocation AND every Agent fork it dispatched,
and each fork's work is still UNCOMMITTED in its worktree at that moment. On 2026-08-03 the unit
was timeout-killed 10 times — roughly 37% of the invocations that carried real work. The result is
a standing population of half-built worktrees, hand-rescued by later ticks: 8 branches / 13 commits,
6 of them literally titled "RESCUE: preserve this dead fork's uncommitted build", and a 10:37 audit
commit recording "2,566 lines of built work were uncommitted in dying worktrees". The same day, a
fresh instance recurred within hours (Item E: three forks dispatched 09:36, ZERO landed).

THE REAL ROOT CAUSE IS THAT "COME HOME" IS PROSE. `supervisor.py`'s doorbell STATES the lifecycle
("each fork MUST come home: on success merge its branch to main via tree_lock, on failure reap it")
but nothing enforces it: fork lifetime is coupled to parent lifetime, the merge step runs LAST, and
the parent is under a hard wall-clock kill. So the step most likely to be cut off is exactly the one
that would have saved the work. CLAUDE.md's own MAKE_IT_STICK rule names this failure in advance —
"every rule that DECAYED was an exhortation; every rule that HELD was a MECHANISM". This module is
the mechanism for the half that can be mechanised.

WHAT IT GUARANTEES. Run from `ExecStopPost=`, i.e. AFTER the main process is gone, on EVERY exit
path — clean exit, crash, and the SIGTERM timeout kill alike. For each dirty agent worktree it
commits the work to THAT WORKTREE'S OWN BRANCH. After it runs, "work exists but is uncommitted" is
no longer a reachable state, so a kill costs wall-clock, never built work.

WHAT IT DELIBERATELY DOES NOT DO.
  - NEVER merges anything to main. Landing stays the worker's in-turn GATED job; auto-merging
    unreviewed work would route around the gate-wall ("output looks sound, land it" is the forbidden
    reasoning). This is the same REAP-ONLY policy A that `fork_reconciler.py` already follows.
  - NEVER deletes a branch or a worktree. Salvage strictly PRECEDES any reaping, and reaping stays
    behind `fork_reconciler`'s own director-armed flags.
  - NEVER touches the main worktree. Concurrent writers share that tree (CLAUDE.md), so a blind
    `git add -A` there would sweep another writer's staged-but-uncommitted files into this commit.
    Dirty main is REPORTED, never committed.

WHY `--no-verify` IS CORRECT HERE, narrowly. The salvage commit lands on the fork's own branch and
nowhere else, so it puts no untested code on a shared surface; the gate still applies in full at the
merge decision, which stays deferred and human/worker-owned. This is the same reasoning the existing
hand-written RESCUE commits recorded. Running the real gate here would be self-defeating: it takes
minutes, and this hook runs in the seconds after a kill, so a gated salvage would itself be killed
and preserve nothing. R16 is unaffected — a salvage commit never moves `level_current`; it only
preserves whatever the fork had already written.

FAIL-SAFE. Never raises: a salvage that cannot run must not break the tick's shutdown path. Every
failure is reported and the next dirty worktree is still attempted.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = PROJECT_DIR / "docs" / "observability" / "fork-salvage-log.md"

# The main worktree is NEVER salvaged (concurrent writers -- see module docstring).
PROTECTED_BRANCHES = {"main"}

# Bound every git call: this hook runs on a shutdown path that systemd itself is timing.
GIT_TIMEOUT_SECONDS = 30


def _git(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess:
    """Run one git command. Never raises -- callers inspect returncode."""
    try:
        return subprocess.run(
            ["git", *args], cwd=str(cwd or PROJECT_DIR),
            capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:      # pragma: no cover - defensive
        return subprocess.CompletedProcess(args, returncode=124, stdout="", stderr=str(exc))


def scan_worktrees() -> list[dict]:
    """Every worktree except the main one, as {path, branch}. The main worktree is the first
    record `git worktree list --porcelain` emits, and is dropped by path comparison rather than by
    position so a future git that reorders the listing cannot make us salvage main by accident."""
    out = _git("worktree", "list", "--porcelain")
    if out.returncode != 0:
        return []
    main_path = str(PROJECT_DIR.resolve())
    worktrees, current = [], {}
    for line in out.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[len("worktree "):].strip(), "branch": None}
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):].strip().replace("refs/heads/", "")
        elif line.startswith("bare") or line.startswith("detached"):
            current[line.split()[0]] = True
    if current:
        worktrees.append(current)
    return [w for w in worktrees
            if str(Path(w["path"]).resolve()) != main_path
            and w.get("branch") not in PROTECTED_BRANCHES
            and not w.get("bare")
            and not _is_a_live_writers_worktree(w["path"])]


def _is_a_live_writers_worktree(path: str) -> bool:
    """Delegates to `seat_executor.worktree_is_live`, which OWNS this question.

    SALVAGE IS FOR ABANDONED WORK, and this module's own name says so: it rescues what a dead fork
    left behind. A worktree with a LIVE process in it is not abandoned, and committing into it makes
    this daemon a second writer in the one place isolation was supposed to guarantee there is only
    ever one -- which is what it did, four minutes into the seat executor's first unattended turn on
    2026-08-31.

    NOT REIMPLEMENTED HERE. `fork_reconciler` needs the same answer for its reaper, and two modules
    that do not import each other each carrying their own liveness rule is the ontology defect this
    project has been paying for all month. One question, one home, two readers.

    Nothing is lost by skipping a live worktree: `seat_executor.ensure_worktree` resets it to
    `origin/main` at the start of every turn, so anything it did not land was, by its own design,
    not finished.
    """
    try:
        from background.seat_executor import worktree_is_live
    except Exception:  # noqa: BLE001 - never let this import take the salvage sweep down
        return False
    return worktree_is_live(path)


def is_dirty(path: str) -> bool:
    """True if the worktree has ANY uncommitted state, tracked or untracked. Untracked counts:
    the 2026-08-03 rescues found NEW files (`background/stall_class_register.py` and its test) that
    existed nowhere else -- one `rm -rf` from being lost entirely. Fail-SAFE: an unreadable tree
    reads as dirty, so an unknown state is salvaged rather than silently skipped."""
    r = _git("status", "--porcelain", "--untracked-files=all", cwd=path)
    if r.returncode != 0:
        return True
    return bool(r.stdout.strip())


def salvage_worktree(worktree: dict, *, now: float | None = None) -> dict:
    """Commit one dirty worktree's work to ITS OWN branch. Returns a result dict; never raises.

    `git add -A` is safe HERE (and only here) precisely because this is not the shared main tree:
    a fork's worktree has exactly one writer, so there is no other writer's work to sweep in."""
    path, branch = worktree["path"], worktree.get("branch")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now if now is not None else time.time()))
    if branch in PROTECTED_BRANCHES:
        return {"path": path, "branch": branch, "action": "REFUSED", "reason": "protected branch"}

    add = _git("add", "-A", cwd=path)
    if add.returncode != 0:
        return {"path": path, "branch": branch, "action": "FAILED",
                "reason": f"git add failed: {add.stderr.strip()[:200]}"}

    message = (
        f"SALVAGE(auto): preserve this fork's uncommitted work at {stamp}\n\n"
        "Written by background/fork_salvage.py from worker-tick.service's ExecStopPost, i.e. AFTER\n"
        "the bounded invocation exited or was SIGTERM-killed at TimeoutStartSec. Without this the\n"
        "work below would have died uncommitted in a worktree, which is how this project kept\n"
        "producing hand-written RESCUE commits.\n\n"
        "On the fork's OWN branch only -- NOT merged to main, so --no-verify lands no untested code\n"
        "on a shared surface. The gate applies in full at the merge decision, which is deferred.\n"
    )
    commit = _git("commit", "--no-verify", "-m", message, cwd=path)
    if commit.returncode != 0:
        low = (commit.stdout + commit.stderr).lower()
        if "nothing to commit" in low:
            return {"path": path, "branch": branch, "action": "NOOP", "reason": "nothing to commit"}
        return {"path": path, "branch": branch, "action": "FAILED",
                "reason": f"git commit failed: {(commit.stderr or commit.stdout).strip()[:200]}"}

    sha = _git("rev-parse", "--short", "HEAD", cwd=path).stdout.strip()
    return {"path": path, "branch": branch, "action": "SALVAGED", "sha": sha}


def main_tree_dirty_report() -> dict | None:
    """Dirty MAIN is reported, never committed (concurrent writers). This is not paranoia: on
    2026-08-03 Item E's HDD work sat uncommitted in the main tree with an untracked test file, so
    the loss mode exists here too -- but blind-committing a shared tree would sweep other writers'
    staged files, which is a worse defect than the one being fixed."""
    r = _git("status", "--porcelain", "--untracked-files=all")
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return {"dirty_paths": len(r.stdout.strip().splitlines())}


def salvage_all(*, worktrees: list[dict] | None = None, now: float | None = None) -> dict:
    """Salvage every dirty non-main worktree. THE entry point; never raises."""
    try:
        candidates = scan_worktrees() if worktrees is None else worktrees
        results = [salvage_worktree(w, now=now) for w in candidates if is_dirty(w["path"])]
        salvaged = [r for r in results if r["action"] == "SALVAGED"]
        failed = [r for r in results if r["action"] == "FAILED"]
        return {
            "scanned": len(candidates),
            "salvaged": len(salvaged),
            "failed": len(failed),
            "results": results,
            "main_tree": main_tree_dirty_report(),
        }
    except Exception as exc:                                  # pragma: no cover - defensive
        return {"scanned": 0, "salvaged": 0, "failed": 0, "results": [], "error": str(exc)}


def format_report(summary: dict) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    if summary.get("error"):
        return f"- [{stamp}] FORK-SALVAGE ERROR: {summary['error']}"
    if not summary["scanned"]:
        return f"- [{stamp}] FORK-SALVAGE: no non-main worktrees to check"
    if not summary["salvaged"] and not summary["failed"]:
        return f"- [{stamp}] FORK-SALVAGE: {summary['scanned']} worktrees, all clean — nothing at risk"
    lines = [f"- [{stamp}] FORK-SALVAGE: {summary['salvaged']} salvaged, "
             f"{summary['failed']} failed, of {summary['scanned']} worktrees"]
    for r in summary["results"]:
        if r["action"] == "SALVAGED":
            lines.append(f"    SALVAGED {r['branch']} -> {r.get('sha', '?')}  ({r['path']})")
        elif r["action"] == "FAILED":
            lines.append(f"    FAILED   {r['branch']}: {r['reason']}")
    main = summary.get("main_tree")
    if main:
        lines.append(f"    NOTE: main worktree has {main['dirty_paths']} uncommitted paths "
                     "— reported, never auto-committed (concurrent writers)")
    return "\n".join(lines)


def main() -> int:
    summary = salvage_all()
    report = format_report(summary)
    print(report)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a") as fh:
            fh.write(report + "\n")
    except OSError:
        pass          # logging must never break the shutdown path
    return 0          # ExecStopPost must never fail the unit


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/fork_salvage.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("fork_salvage")
    raise SystemExit(main())
