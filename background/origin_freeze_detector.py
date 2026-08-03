"""Origin-freeze / push-failure stall detector -- HX2 event E3.

Source: `docs/staging/done/DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27.md`
§3 event 3: "an origin freeze or push failure over thirty minutes -- the phantom-push
incident froze origin for 3.5 hours while the machine believed itself healthy." The real
fixture: `background/process_run_complete.py::_push_reached_origin` (2026-07-24) --
"[[feedback_self_verifying_push]]" -- a bare `git push` returning rc=0 without advancing
origin (a phantom "Everything up-to-date" against a stale remote-tracking ref) froze
origin for 3.5h; 15 real commits piled up locally, invisible to the advisor bridge.

WHAT ALREADY EXISTS vs THE GAP: `_push_reached_origin` (ground-truth ls-remote check) and
its caller in `git_commit_push` PREVENT a phantom success from being mistaken for a real
one, and fire a per-cycle `[SIM] PUSH DID NOT REACH ORIGIN` real_alarm NTFY on every failed
push. Neither is a DURATION-based stall detector: there is no persisted "origin has been
behind local HEAD for N minutes" state and no draw-rung analogous to
`supervisor._publish_gate_wedge_active()` for this class -- so an origin freeze produces
repeated alarms but never itself becomes drawable priority-zero work the way a publish-gate
wedge does. This module is that missing piece. Per the fork-brief's scope pins, this does
NOT touch `background/process_run_complete.py` (a concurrent sibling fork's fix
`869c8e57c` just landed there for the adjacent publish-gate-wedge class; editing it again
here was explicitly out of scope) -- it is self-contained and reads GIT HISTORY DIRECTLY,
which is independent primary state regardless of what process_run_complete's own internal
bookkeeping says.

DEFINITION: origin is FROZEN when local HEAD carries one or more commits that `origin/main`
does not have (`git rev-list --count origin/main..HEAD` > 0), AND THE OLDEST such commit's
COMMITTER TIMESTAMP is more than `ORIGIN_FREEZE_MIN_AGE_SECONDS` (30 min, per the ruling) in
the past. This is GROUND TRUTH from git object history, not a self-reported flag -- the same
independence property `_push_reached_origin` itself relies on (ls-remote, not the local
tracking ref). It self-heals: the moment a push actually reaches origin, `rev-list --count`
drops back toward zero on its own, with no separate 'clear' bookkeeping required.

Whichever process (`sim_runner.py`, `background_worker.py`, the interactive console, or a
worker-tick spawn) leaves unpushed commits sitting on local HEAD, this detects it -- it does
not care WHY origin is behind, only THAT it has been for too long, which is what makes it a
stall-class signal independent of any one publisher's internal state.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
ORIGIN_FREEZE_MIN_AGE_SECONDS = 30 * 60  # director ruling §3 event 3: "over thirty minutes"
_GIT_TIMEOUT_SECONDS = 30


class StallDetectorUnavailable(Exception):
    """The check itself could not run -- a git command errored/timed out, or its output
    could not be parsed as expected. Distinct from a clean 'origin is not frozen' (`None`).
    Per R15 FAIL-SILENT doctrine: an unavailable check must never be read as a pass by the
    caller (see `background/stall_class_register.py`)."""


def _run_git(args: list[str], project_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git"] + args, cwd=str(project_dir), capture_output=True, text=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StallDetectorUnavailable(f"git {' '.join(args)} failed to run: {exc}") from exc
    if result.returncode != 0:
        raise StallDetectorUnavailable(
            f"git {' '.join(args)} exited {result.returncode}: {result.stderr.strip()[:300]}"
        )
    return result.stdout


def origin_freeze_active(
    now: float | None = None,
    project_dir: Path | None = None,
    min_age_seconds: int = ORIGIN_FREEZE_MIN_AGE_SECONDS,
) -> str | None:
    """Returns a stall-class message if `origin/main` is behind local HEAD by an unpushed
    commit older than `min_age_seconds`, else None. Raises StallDetectorUnavailable if the
    git commands themselves fail (missing repo, git not on PATH, a real non-zero exit) --
    the caller must classify that as unavailable, never as 'origin is fine'.

    Deliberately does NOT `git fetch` -- fetching on every stall-class evaluation would add
    network I/O + latency to what should be a cheap, frequent check, and every caller in
    this codebase already fetches origin at least once per supervisor tick
    (`supervisor._sync_origin_staging`) or per publish cycle, so `origin/main` is never
    stale by more than one cycle. A caller that needs a guaranteed-fresh view may fetch
    first and pass a `project_dir` whose `origin/main` it already just updated.
    """
    now = time.time() if now is None else now
    pd = project_dir or PROJECT_DIR

    count_out = _run_git(["rev-list", "--count", "origin/main..HEAD"], pd)
    try:
        count = int(count_out.strip())
    except ValueError as exc:
        raise StallDetectorUnavailable(
            f"git rev-list --count returned non-numeric output: {count_out!r}"
        ) from exc
    if count <= 0:
        return None  # origin is caught up (or ahead) -- no freeze

    ts_out = _run_git(["log", "origin/main..HEAD", "--format=%ct"], pd)
    timestamps = [ln.strip() for ln in ts_out.splitlines() if ln.strip()]
    if not timestamps:
        # rev-list said N>0 unpushed commits exist but log returned none -- a genuine
        # parse mismatch (e.g. a shallow clone, or origin/main moved between the two
        # calls), not "no unpushed commits". FAIL-OPEN guard: this must not silently
        # read as clear.
        raise StallDetectorUnavailable(
            f"rev-list reports {count} unpushed commit(s) but `git log` returned none"
        )
    try:
        oldest_ts = min(float(t) for t in timestamps)
    except ValueError as exc:
        raise StallDetectorUnavailable(f"git log --format=%ct returned non-numeric output") from exc

    age = now - oldest_ts
    if age < min_age_seconds:
        return None

    age_min = int(age // 60)
    return (
        "ORIGIN FREEZE (HX2 E3): {} commit(s) sit on local HEAD that origin/main does not "
        "have; the oldest is ~{}min old (threshold {}min). The advisor bridge and any "
        "external reader of this repo are BLIND to this work until a push actually "
        "advances origin -- diagnose why pushes are not reaching origin (auth, "
        "remote-tracking ref, network) rather than retrying blind.".format(
            count, age_min, min_age_seconds // 60
        )
    )
