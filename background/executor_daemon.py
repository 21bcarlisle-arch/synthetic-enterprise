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
) -> str:
    """Keep the headless loop running until a terminal stop. Returns the terminal stop_reason.

    `budget_factory` builds a FRESH TurnBudget each time run_loop is (re-)entered so a slid window
    starts clean. `max_supervisions` bounds how many times run_loop is (re-)entered — None means
    unbounded (the real daemon); tests pass a small integer. All collaborators are injected so the
    supervision policy is unit-testable with NO real dispatch and NO real clock.
    """
    kill_switch = kill_switch or executor_governor.kill_switch_enabled
    run_loop_fn = run_loop_fn or executor_governor.run_loop

    supervisions = 0
    build_executor.log("executor_daemon.run_forever: starting (DARK-gated — no-op if kill flag absent)")
    while kill_switch():
        if max_supervisions is not None and supervisions >= max_supervisions:
            return "max_supervisions"
        supervisions += 1
        budget = budget_factory() if budget_factory is not None else None
        try:
            summary = run_loop_fn(budget=budget, max_cycles=None)
        except Exception as exc:  # noqa: BLE001 — a run_loop crash must RESTART, never kill the daemon
            build_executor.log(f"executor_daemon: run_loop CRASHED ({exc!r}) — restarting after backoff")
            sleep(CRASH_BACKOFF_SECONDS)
            continue

        reason = summary.stop_reason
        build_executor.log(f"executor_daemon: run_loop returned stop_reason={reason} after {summary.cycles} cycle(s)")
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
