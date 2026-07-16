"""Resilient launcher for the self-continuing headless build loop — THE autonomy milestone
(2026-07-16, director: "the executor/headless loop must continuously draw-and-execute with NO
human nudge and NO stopping at boundaries, until a genuine wall (NTFY'd) or the kill flag").

WHY THIS EXISTS (the bug it fixes). `executor_governor.run_loop` self-continues WITHIN one run
(draw -> dispatch a `claude -p` subprocess -> gate -> immediately draw the next; mutation-tested
by `test_loop_runs_N_turns_unattended_zero_input`). But nothing launched it or kept it alive, so
in practice an *interactive* session drove the work turn-by-turn and STOPPED at every boundary —
a Stop hook cannot re-drive an attached interactive session. This daemon closes that gap at the
PROCESS level: it keeps run_loop running with zero human nudge, so continuation is a MECHANISM,
not a rule that decays. It never touches the interactive pane.

WHAT STOPS IT (and only these):
  - kill flag OFF (`executor_governor.kill_switch_enabled()` False) -> clean exit (the director
    turned it off; DARK by default so a bare launch is a safe no-op).
  - a genuine WALL run_loop already NTFY'd and cannot self-resolve (map UNRECONCILED needs a human
    fold; R3 repeated-failure needs a human diagnosis) -> stay DOWN, do not hammer.
  - budget window exhausted -> WAIT for the window to slide, then re-enter (not a real stop).
  - run_loop itself CRASHED (unexpected exception) -> log and RESTART (resilience).

Note (ESCALATION_IS_NTFY): a one-way-door escalation no longer stops run_loop at all — it NTFYs
and keeps drawing other atoms — so `wall_escalated` is not among run_loop's terminal reasons here.
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Callable

# Standalone entrypoint bootstrap: launched as `python3 background/executor_daemon.py`
# (start_worker.sh, like every sibling daemon), Python puts THIS file's dir
# (background/) on sys.path, not the repo root -- so `from background import ...`
# raises ModuleNotFoundError and the process dies at import before run_forever is
# ever reached. Every other daemon (supervisor/staging_watcher/dispatcher) carries
# the same insert; this one lacked it, so it could only ever be imported by pytest,
# never launched as a real process (2026-07-16: "proven in a 3-turn test but never
# launched as a persistent process").
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from background import build_executor, executor_governor  # noqa: E402

# run_loop stop_reasons that are TERMINAL for the daemon (a human must act; do not restart).
_TERMINAL_STOPS = frozenset({"kill_switch_off", "map_unreconciled", "repeated_failure"})

# SELF-STALENESS GUARD (R2 mechanised / MAKE_IT_STICK). The modules whose in-memory
# imported code this daemon actually RUNS each turn -- the draw (supervisor), the loop
# (executor_governor), the gated dispatch (build_executor), and this launcher itself.
# When any of their ON-DISK source changes after launch, the running process holds STALE
# code (committed != running) and must re-exec into the fresh source. This is the terminal
# mechanism behind the frame-saturation stale-draw treadmill: PID 704593 imported the draw
# code at 18:27Z, a saturation-detection fix landed at 19:36Z, and the daemon kept drawing
# already-FRAME-saturated atoms off its stale in-process import for the ~104 minutes after
# -- a decayed "restart the daemon after a draw-logic change" exhortation, now a mechanism.
_WATCHED_MODULES = (
    "background.executor_daemon",
    "background.executor_governor",
    "background.build_executor",
    "background.supervisor",
)


def source_fingerprint() -> str:
    """A content hash of the on-disk source of every module this daemon runs each turn.
    Compared against a baseline captured at launch: any drift => the imported code is
    stale. Reads the CURRENT file bytes (never the loaded module object), so it observes
    edits the running process has not picked up. Unreadable/absent files fold in as a fixed
    sentinel so a transient read error can't masquerade as 'unchanged'."""
    h = hashlib.sha256()
    for modname in _WATCHED_MODULES:
        mod = sys.modules.get(modname)
        path = getattr(mod, "__file__", None) if mod is not None else None
        h.update(modname.encode())
        try:
            h.update(Path(path).read_bytes() if path else b"<no-file>")
        except OSError:
            h.update(b"<unreadable>")
    return h.hexdigest()


def _reexec() -> None:
    """Replace this process image with a fresh interpreter running the CURRENT source
    (same argv, same tmux pane, same PID). os.execv does not return on success."""
    os.execv(sys.executable, [sys.executable, *sys.argv])

# Wait between a budget-exhausted return and re-entering (the window slides).
RESTART_BACKOFF_SECONDS = 60.0
# Guard against a crash-loop pegging the CPU: pause after an unexpected run_loop exception.
CRASH_BACKOFF_SECONDS = 30.0


def run_forever(
    *,
    budget_factory: Callable[[], executor_governor.TurnBudget] | None = None,
    kill_switch: Callable[[], bool] | None = None,
    run_loop_fn: Callable[..., executor_governor.LoopSummary] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    max_supervisions: int | None = None,
    source_fingerprint_fn: Callable[[], str] | None = None,
    reexec_fn: Callable[[], None] | None = None,
) -> str:
    """Keep the headless loop running until a terminal stop. Returns the terminal stop_reason.

    `budget_factory` builds a FRESH TurnBudget each time run_loop is (re-)entered so a slid window
    starts clean. `max_supervisions` bounds how many times run_loop is (re-)entered — None means
    unbounded (the real daemon); tests pass a small integer. All collaborators are injected so the
    supervision policy is unit-testable with NO real dispatch and NO real clock.

    SELF-STALENESS GUARD: a baseline source fingerprint is captured at launch and a live
    comparator is passed INTO run_loop, which stops with `code_stale` the moment the daemon's own
    source drifts on disk. A re-entry in the SAME process would still hold the stale IMPORTED code,
    so `code_stale` is handled here by re-exec (a fresh interpreter picks up the new source) — NOT
    by the ordinary sleep-and-re-enter path. Both the fingerprint and the re-exec are injected so
    the branch is unit-testable with no real files and no real process replacement.
    """
    kill_switch = kill_switch or executor_governor.kill_switch_enabled
    run_loop_fn = run_loop_fn or executor_governor.run_loop
    source_fingerprint_fn = source_fingerprint_fn or source_fingerprint
    reexec_fn = reexec_fn or _reexec

    baseline_fingerprint = source_fingerprint_fn()
    supervisions = 0
    build_executor.log("executor_daemon.run_forever: starting (DARK-gated — no-op if kill flag absent)")
    while kill_switch():
        if max_supervisions is not None and supervisions >= max_supervisions:
            return "max_supervisions"
        supervisions += 1
        budget = budget_factory() if budget_factory is not None else None
        try:
            summary = run_loop_fn(
                budget=budget,
                max_cycles=None,
                staleness_check=lambda: source_fingerprint_fn() != baseline_fingerprint,
            )
        except Exception as exc:  # noqa: BLE001 — a run_loop crash must RESTART, never kill the daemon
            build_executor.log(f"executor_daemon: run_loop CRASHED ({exc!r}) — restarting after backoff")
            sleep(CRASH_BACKOFF_SECONDS)
            continue

        reason = summary.stop_reason
        build_executor.log(f"executor_daemon: run_loop returned stop_reason={reason} after {summary.cycles} cycle(s)")
        if reason == "code_stale":
            # The imported draw/gate code is stale (committed != running). A same-process
            # re-entry would NOT reload it — replace the process image with fresh source.
            build_executor.log(
                "executor_daemon: OWN SOURCE changed on disk since launch -> re-exec into fresh "
                "code (R2 mechanised / MAKE_IT_STICK: terminal fix for the stale-draw treadmill)"
            )
            reexec_fn()  # os.execv: does not return on success (only an injected test fake does)
            return "code_stale"
        if reason in _TERMINAL_STOPS:
            # run_loop already NTFY'd the wall (or the kill flag is off). Stay down; a human acts.
            return reason
        # budget_exhausted (or any non-terminal return): the window will slide — wait and re-enter.
        sleep(RESTART_BACKOFF_SECONDS)

    return "kill_switch_off"


def main() -> int:
    # Real entrypoint: a bounded-per-window budget so an enabled daemon can never become an
    # uncapped spender, restarted forever across window slides. DARK unless the enable flag is set.
    def _budget() -> executor_governor.TurnBudget:
        return executor_governor.TurnBudget(max_turns_per_window=20)

    reason = run_forever(budget_factory=_budget)
    build_executor.log(f"executor_daemon: exited ({reason})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
