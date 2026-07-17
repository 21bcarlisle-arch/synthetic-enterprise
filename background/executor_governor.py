#!/usr/bin/env python3
"""Executor governor — the tripwire + self-continuing LOOP over build_executor.run_once
(AUTONOMOUS_EXECUTOR_SPEC.md §C.1 L2 deliverable; loop scoped 2026-07-15, director).

`build_executor.run_once` lands ONE gated turn and returns. This module wraps it in the
UNATTENDED loop the director asked for: turn lands -> gate -> next headless turn, until
the kill switch is off or a WALL is hit -- with the durable kill switch and (externally)
the dead-man's switch over the top.

SAFETY — this module is DARK by default and cannot self-activate:
  * `run_loop` refuses to run unless the director's durable enable-flag is present. That
    flag (`docs/observability/.build_executor_enabled`, DIRECTOR_ANSWERS_C7 #6) is the ONE
    kill switch for ALL autonomous execution -- console-only, director-reserved. This
    module READS it (reusing the pull-loop hook's fail-closed predicate VERBATIM so there
    is one definition, not two that drift) and NEVER creates or modifies it. No code here
    writes that path.
  * No launcher wiring (`start_worker.sh` entry stays absent/commented — a director step,
    §C.5) and no `health_check.EXPECTED_PANES` entry (added only while enabled). Importing
    this module starts nothing; only an explicit `run_loop()` call under an ON flag runs.
  * `run_loop` REFUSES to run unbounded — a caller must pass a TurnBudget or a max_cycles;
    an accidental bare invocation cannot become an uncapped overnight spender (the exact
    A.2 #1/#2 defect that retired the predecessor).

The dead-man's switch (`background/deadmans_switch.py`) sits OVER this loop externally: it
is keyed on the MEANINGFUL git-commit clock, which only a landed turn moves and which this
loop cannot itself refresh — so a wedged loop that stops landing work alarms the director
regardless of what this process reports. This loop does not, and structurally cannot,
suppress that watchdog.
"""
from __future__ import annotations

import hashlib
import importlib.util
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

PROJECT_DIR = Path(__file__).resolve().parent.parent

from background import action_needed, build_executor  # noqa: E402

# ntfy_utils is imported LAZILY inside _alert_wall: it hard-requires SE_NTFY_TOPIC at
# import time, and importing the governor / running `--once` must not require the ntfy
# env to be loaded. The loop only needs ntfy when it actually alerts on a self-stop.

# --- Loop tuning -------------------------------------------------------------
# Back-off when the draw genuinely returns None (a true WALL). Rule 0 + the
# rule0-harden widen tier should make this ~never happen while any atom exists,
# so this is a spin-guard, not a normal path.
IDLE_BACKOFF_SECONDS = 60
# R3 two-strike: never spend the night retrying a wedged atom. Consecutive
# non-landing cycles (failed/error) at this count STOP the loop and alert.
MAX_CONSECUTIVE_FAILURES = 2

# Stop reasons that are CLEAN (a dial, not a wall) — heartbeat idle, no anomaly.
# code_stale is a BENIGN self-healing stop (the daemon's own source changed on disk
# since launch; run_forever re-execs into fresh code) -- heartbeat it "idle", never
# "blocked". See executor_daemon's staleness guard (R2 mechanised / MAKE_IT_STICK).
_CLEAN_STOPS = frozenset({"kill_switch_off", "budget_exhausted", "max_cycles", "code_stale"})


# =============================================================================
# THE KILL SWITCH — reused verbatim from the pull-loop hook (ONE definition)
# =============================================================================
def _load_pull_hook():
    """Load the pull-loop Stop hook by file path (it lives under .claude/hooks, not an
    importable package), mirroring build_executor's hook-predicate reuse. We reuse its
    `_autonomous_execution_enabled` so the headless executor and the in-session pull
    loop share ONE fail-closed definition of 'autonomous execution enabled' (DIRECTOR_
    ANSWERS_C7 #6: one flag, no second) — they cannot drift."""
    hook_path = PROJECT_DIR / ".claude" / "hooks" / "pull_next_work.py"
    spec = importlib.util.spec_from_file_location("_pull_next_work_hook", hook_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load pull-loop hook from {hook_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_pull_hook = _load_pull_hook()


def kill_switch_enabled() -> bool:
    """THE single durable kill switch, FAIL-CLOSED. TRUE only if the director's
    console-only enable flag is a readable regular file (missing / a directory /
    unreadable => DISABLED). Reused verbatim from the pull-loop hook. The agent may
    READ this; it may NEVER create or modify the flag (console-only, director-reserved).
    This module contains no code that writes it."""
    return _pull_hook._autonomous_execution_enabled()


# =============================================================================
# TRIPWIRE a — budget cap (turns/window; tokens/window when metered). Fail-closed.
# =============================================================================
class TurnBudget:
    """Sliding-window budget cap (primitive #4). Bounds turns per window and, when a
    real per-turn token count is available, tokens per window. Fail-closed: a
    non-positive/absent turn cap dispatches NOTHING.

    NOTE ON TOKENS (an overnight gap, see the gap report): `run_once` does not yet meter
    a turn's token cost (plain `claude -p`, no `--output-format json`), so `max_tokens_
    per_window` is None (turns-only) until token metering is wired. The turn-count cap is
    a real, enforced bound now; the token cap is inert until metered — stated plainly, not
    silently fail-open.
    """

    def __init__(
        self,
        *,
        max_turns_per_window: int,
        window_seconds: float = 3600.0,
        max_tokens_per_window: int | None = None,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_turns = max_turns_per_window
        self._window = window_seconds
        self._max_tokens = max_tokens_per_window
        self._monotonic = monotonic
        self._events: deque[tuple[float, int]] = deque()  # (ts, tokens)

    def _evict(self, now: float) -> None:
        while self._events and (now - self._events[0][0]) > self._window:
            self._events.popleft()

    def can_dispatch(self) -> bool:
        # FAIL-CLOSED: an unconfigured / non-positive turn cap dispatches nothing.
        if not self._max_turns or self._max_turns <= 0:
            return False
        now = self._monotonic()
        self._evict(now)
        if len(self._events) >= self._max_turns:
            return False
        if self._max_tokens is not None:
            if sum(tok for _, tok in self._events) >= self._max_tokens:
                return False
        return True

    def charge(self, *, tokens: int | None = None) -> None:
        """Record one dispatched turn. `tokens` None/negative (unmetered) -> 0 tokens
        charged (turns-only enforcement); the turn itself is always counted."""
        tok = tokens if (tokens is not None and tokens >= 0) else 0
        self._events.append((self._monotonic(), tok))

    def remaining_turns(self) -> int:
        now = self._monotonic()
        self._evict(now)
        return max(0, (self._max_turns or 0) - len(self._events))


# =============================================================================
# THE SELF-CONTINUING LOOP — turn lands -> gate -> next, until flag off / wall
# =============================================================================
@dataclass
class LoopSummary:
    stop_reason: str
    cycles: int


@dataclass
class _UnreconciledResult:
    """A shim so _alert_wall can render a map-reconciliation stop uniformly with the other
    self-stops (it reads .atom_reason / .detail)."""

    unfolded_ids: list[str]

    @property
    def atom_reason(self) -> str:
        return f"unfolded level report(s) for: {', '.join(self.unfolded_ids)}"

    @property
    def detail(self) -> str:
        return "map unreconciled — an atom's level never folded into maturity_map.yaml"


def _turn_tokens(result: Any) -> int | None:
    """Per-turn token cost for the budget, or None if unmetered. Unbuilt today (plain
    `claude -p` emits no usage) — wiring `--output-format json` + parsing usage is the
    named overnight gap. Returns None so TurnBudget stays turns-only until then."""
    return getattr(result, "tokens", None)


def _alert_wall(result: Any, *, kind: str = "wall_escalated") -> None:
    """Surface a self-stop that needs the director on the Director door + NTFY. A WALL
    (a turn escalated a one-way door) or an R3 repeated-failure stop are the only two
    things this loop cannot decide itself."""
    if kind == "wall_escalated":
        what = "Headless executor hit a one-way door (WALL) — NTFY'd, loop CONTINUING other atoms."
        how = (
            "Decide this one-way door at your cadence (reply via NTFY/PIN); the loop is NOT "
            "blocked — it is drawing other work meanwhile and will act on your answer at the "
            "next boundary. Details: the escalated item + docs/observability/build-executor-log.md. "
            "ESCALATION IS NTFY, NEVER THE WINDOW: nothing is waiting in the interactive pane."
        )
    elif kind == "map_unreconciled":
        what = "Headless executor STOPPED: map UNRECONCILED (a level report never folded)."
        how = (
            "An atom_status inbox is unfolded -- a fork's level_current never reached "
            "maturity_map.yaml (self-report vs external truth, MAP_TRUTH_RECONCILIATION.md). "
            "Run `python3 -m tools.merge_atom_status`, commit the map, then re-enable. Do "
            "NOT re-enable with the map unreconciled -- the draw would rank off a stale level."
        )
    else:
        what = "Headless executor STOPPED: repeated turn failures (R3 two-strike)."
        how = (
            "A drawn atom failed to land twice running. Diagnose it (R4), do NOT just "
            "re-enable — R3 says redesign the mechanism, not retry. See "
            "docs/observability/build-executor-log.md."
        )
    why = f"Unattended loop self-stopped and is awaiting a director decision. Draw: {getattr(result, 'atom_reason', None)}"
    # PER-WALL escalation identity (2026-07-16 HARDEN, red-team of this atom's own core
    # invariant): a WALL keeps the loop DRAWING, so TWO DISTINCT one-way doors can be open
    # at once. A constant `executor-wall_escalated` item coalesced them into ONE
    # action_needed item -> the fire-once gate SILENTLY SWALLOWED the second distinct door
    # (only the first was ever NTFY'd; the director never heard the second irreducible
    # core). That is the SILENT-DROP cousin of the silent-stall this atom exists to kill.
    # Fix: derive the item id from the escalated atom_reason so each distinct door gets its
    # own escalation, its own fire-once/daily gate, and its own reply-PIN. Singleton STOP
    # kinds (map_unreconciled / repeated_failure HALT the loop, so only one can be live)
    # keep the constant id.
    if kind == "wall_escalated":
        reason_key = hashlib.sha1((getattr(result, "atom_reason", None) or "").encode("utf-8")).hexdigest()[:8]
        item_id = f"executor-{kind}-{reason_key}"
    else:
        item_id = f"executor-{kind}"
    try:
        from background.notify import notify  # lazy: needs SE_NTFY_TOPIC only here

        # THE fire-once-then-daily gate (2026-07-16): a self-stop escalation is raised
        # ONCE and re-pinged at most daily -- NOT every run_loop re-entry. run_loop's
        # last_escalated_reason latch is in-memory, so run_forever re-entering each
        # budget window reset it and re-asked the SAME wall every few minutes; this
        # persistent gate is what actually stops that. A director reply resolves the
        # item (see ntfy_responder answer-correlation) -> should_notify goes False.
        if not action_needed.should_notify(item_id):
            build_executor.log(
                f"_alert_wall: {item_id} already open (awaiting answer, not due for daily "
                "re-ping) -- suppressing duplicate escalation NTFY (fire-once)"
            )
            return
        # PIN so a phone reply can CLOSE this exact escalation instead of being
        # re-ingested as a fresh urgent command (answer-correlation, path 2).
        pin = action_needed.pin_for(item_id)
        how_pinned = f"{how}\nReply to CLOSE: start your NTFY with PIN {pin} (e.g. 'PIN {pin} PROCEED')."
        action_needed.register_item(item_id, what, how_pinned, why)
        notify(action_needed.format_action_needed(item_id, what, how_pinned, why), kind="real_alarm")
    except Exception as exc:  # pragma: no cover - defensive: an alert failure never crashes the loop
        build_executor.log(f"_alert_wall failed ({kind}): {exc}")


def _default_fold() -> list[str]:
    """Loop-side fold (MAP_TRUTH_RECONCILIATION.md F1, the atomic level-write's second
    half). A fork writes its level into a narrow `docs/design/atom_status/<id>.yaml` inbox
    IN THE SAME COMMIT as its code (the executor contract, build_executor.py); the loop
    folds every landed inbox into the canonical map via `merge_atom_status.merge()` — which
    also CLEARS the folded inbox — then commits the map so the fold is durable. Run at the
    TOP of each cycle, BEFORE the F2 reconcile check: a foldable inbox is folded and the
    check then passes; an UNfoldable one (malformed / unknown atom) is left at rest and F2
    (fail-closed) stops the loop. Returns the folded atom ids (for the log).

    Fold errors are swallowed here on purpose: a failed fold leaves the inbox at rest, so
    the immediately-following reconcile check STOPS the loop — never a silent mis-fold."""
    try:
        from tools.merge_atom_status import merge
        from background.tree_lock import tree_lock

        with tree_lock():
            folded = merge()  # folds + clears inboxes, writes maturity_map.yaml in place
            if folded:
                import subprocess

                subprocess.run(
                    ["git", "add", "--", "docs/design/maturity_map.yaml", "docs/design/atom_status"],
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", f"Fold atom_status inbox -> map (F1): {', '.join(folded)}"],
                    check=True,
                    capture_output=True,
                )
        return folded
    except Exception as exc:  # noqa: BLE001 — fold failure must not crash the loop; F2 catches it
        build_executor.log(f"fold step errored -> leaving inbox at rest for F2 to catch: {exc}")
        return []


def _default_reconcile_check() -> list[str]:
    """Fail-closed map reconciliation (MAP_TRUTH_RECONCILIATION.md F2): atom ids whose
    level report never reached the canonical map (an unfolded inbox at rest). Reuses the
    control's ONE primitive. Any error resolves to a sentinel divergence so the loop
    STOPS -- an unreadable reconciliation signal is a failed check, never a silent pass."""
    try:
        from tools.merge_atom_status import unfolded_inbox_ids

        return unfolded_inbox_ids()
    except Exception as exc:  # unreadable signal -> treat as divergence (fail-closed)
        build_executor.log(f"reconcile check errored -> treating as unreconciled: {exc}")
        return ["<reconcile-check-error>"]


def run_loop(
    *,
    budget: TurnBudget | None = None,
    max_cycles: int | None = None,
    run_once_fn: Callable[[], Any] | None = None,
    kill_switch: Callable[[], bool] | None = None,
    alert: Callable[..., None] | None = None,
    reconcile_check: Callable[[], list[str]] | None = None,
    fold_fn: Callable[[], list[str]] | None = None,
    staleness_check: Callable[[], bool] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    idle_backoff_seconds: float = IDLE_BACKOFF_SECONDS,
    max_consecutive_failures: int = MAX_CONSECUTIVE_FAILURES,
) -> LoopSummary:
    """The self-continuing headless loop: while the kill switch is ON and the budget has
    room, draw -> dispatch ONE gated turn -> gate on landed evidence -> next, unattended.

    STOPS (and heartbeats the reason) on the FIRST of:
      * kill switch OFF        — the director removed the durable console flag (the kill);
      * map UNRECONCILED       — an atom's level report never reached the map (an unfolded
                                 inbox at rest); fail-closed, alert + stop (the draw reads
                                 level_current, so a mis-folded level would mis-rank work —
                                 MAP_TRUTH_RECONCILIATION.md F2);
      * budget exhausted       — TurnBudget window is full;
      * WALL (escalated)       — a turn hit an irreducible one-way door: NTFY the director
                                 (async) and KEEP DRAWING other atoms; it does NOT stop the
                                 loop and NEVER waits in the interactive window
                                 (ESCALATION_IS_NTFY_NEVER_WINDOW.md);
      * repeated failure       — R3 two-strike: an atom failed to land twice running;
      * code_stale             — the daemon's OWN SOURCE changed on disk since launch, so the
                                 in-memory imported draw/gate code is stale (R2: committed !=
                                 running). Stops so executor_daemon can re-exec into fresh code
                                 rather than keep dispatching off a stale in-process import — the
                                 mechanised terminal fix for the frame-saturation stale-draw
                                 treadmill (a running daemon that pre-dated a draw-logic fix kept
                                 re-offering already-FRAME-saturated atoms). Default no-op checker,
                                 so a bare/test call never trips it;
      * max_cycles             — a test / bounded-run guard.

    DARK by default: with the enable flag absent, `kill_switch()` is False on the first
    check and this returns having dispatched NOTHING. Refuses to run unbounded — a caller
    must pass a TurnBudget or max_cycles, so a bare call can never become an uncapped
    overnight spender.
    """
    if budget is None and max_cycles is None:
        raise ValueError(
            "run_loop refuses to run unbounded — pass a TurnBudget (director's budget "
            "numbers, C.7 #1) or an explicit max_cycles."
        )
    run_once_fn = run_once_fn or build_executor.run_once
    kill_switch = kill_switch or kill_switch_enabled
    alert = alert or _alert_wall
    reconcile_check = reconcile_check or _default_reconcile_check
    fold_fn = fold_fn or _default_fold
    # Default is a no-op (never stale): only the real daemon (executor_daemon.run_forever)
    # injects a live source-fingerprint comparator, so a bare call / every existing test is
    # unaffected and can never spuriously request a re-exec.
    staleness_check = staleness_check or (lambda: False)

    cycles = 0
    consecutive_failures = 0
    # ESCALATION_IS_NTFY: the SET of distinct walls NTFY'd this stint. A SET, not a scalar
    # last-reason: with a scalar, two DISTINCT walls re-drawn alternately (A,B,A,B — the
    # only drawable work being two one-way doors) never equalled the immediately-previous
    # reason, so the loop re-alerted needlessly AND never backed off (a hot busy-loop). The
    # set NTFYs once per newly-seen distinct wall and backs off on ANY already-seen wall.
    escalated_reasons: set = set()
    stop_reason = ""
    build_executor.log("run_loop: starting self-continuing headless loop (DARK-gated)")

    while True:
        if max_cycles is not None and cycles >= max_cycles:
            stop_reason = "max_cycles"
            break
        if not kill_switch():
            stop_reason = "kill_switch_off"
            break
        # SELF-STALENESS GUARD (R2 mechanised, MAKE_IT_STICK): if this process's OWN
        # source changed on disk since it was launched, the imported draw/gate code it
        # is about to run is STALE (committed != running). Checked BEFORE the draw so a
        # stale daemon never dispatches even one more turn off pre-fix logic. run_forever
        # turns this into a re-exec into fresh code. This is the terminal fix for the
        # frame-saturation stale-draw treadmill: a daemon that pre-dated a draw-logic fix
        # kept re-offering already-FRAME-saturated atoms turn after turn.
        if staleness_check():
            stop_reason = "code_stale"
            build_executor.log(
                "run_loop: OWN SOURCE changed on disk since launch -> stopping so the "
                "daemon re-execs into fresh code (R2: committed != running)"
            )
            break
        # F1 fold (atomic level-write, second half): fold any landed atom_status inbox into
        # the map BEFORE the reconcile check, so a fork's in-commit level report lands
        # deterministically (no free-text judgment step, no lost-write window). A foldable
        # inbox is cleared here; an unfoldable one is left for F2 to STOP on, just below.
        folded = fold_fn()
        if folded:
            build_executor.log(f"run_loop cycle: folded atom_status inbox(es) -> map: {folded}")
        # Fail-closed map reconciliation: an unfolded level report (self-report vs external
        # truth) STOPS the loop before it draws off a possibly-mis-ranked map (F2).
        unreconciled = reconcile_check()
        if unreconciled:
            stop_reason = "map_unreconciled"
            build_executor.log(f"run_loop: map UNRECONCILED (unfolded: {unreconciled}) — stopping")
            alert(_UnreconciledResult(unreconciled), kind="map_unreconciled")
            break
        if budget is not None and not budget.can_dispatch():
            stop_reason = "budget_exhausted"
            break

        result = run_once_fn()
        cycles += 1
        if budget is not None:
            budget.charge(tokens=_turn_tokens(result))
        build_executor.log(
            f"run_loop cycle {cycles}: status={getattr(result, 'status', '?')} "
            f"sha={getattr(result, 'claimed_sha', None)}"
        )

        status = getattr(result, "status", "error")
        if status == "escalated":
            # ESCALATION IS NTFY, NEVER THE WINDOW + ROUTE-AROUND (P0 WALL,
            # ESCALATION_IS_NTFY_NEVER_WINDOW.md / ROUTE_AROUND_BEFORE_STOPPING.md):
            # a turn hit an irreducible one-way door. NTFY the director the minimal
            # decision (alert -> _alert_wall -> send_ntfy, async + non-blocking) and
            # KEEP DRAWING other atoms — a blocked atom blocks ONLY ITSELF, it never
            # halts the loop and NEVER waits in the interactive window. The loop used to
            # `break` here (halt); that reintroduced the human-at-a-terminal dependency
            # the whole autonomy stack exists to remove.
            reason = getattr(result, "atom_reason", None)
            consecutive_failures = 0
            if reason not in escalated_reasons:
                # A newly-seen distinct wall: NTFY its irreducible core ONCE (async), record
                # it, and immediately keep drawing — a second distinct one-way door is NOT
                # coalesced away, it gets its own escalation (per-wall item id in _alert_wall).
                alert(result, kind="wall_escalated")
                escalated_reasons.add(reason)
            else:
                # Only already-seen walls are drawable (nothing new to do): back off
                # (deadman/health-check are the net) rather than busy-loop or re-NTFY.
                # Still no window prompt, still no hard stop. Holds for a single re-drawn
                # wall AND for several distinct walls cycling with nothing else drawable.
                sleep(idle_backoff_seconds)
            continue
        if status == "success":
            consecutive_failures = 0
            escalated_reasons.clear()  # real progress -> clear the nothing-else-drawable latch
        elif status in ("failed", "error"):
            consecutive_failures += 1
        elif status == "idle":
            # A genuine draw wall — back off and re-check the kill switch, don't spin.
            consecutive_failures = 0
            sleep(idle_backoff_seconds)

        if consecutive_failures >= max_consecutive_failures:
            stop_reason = "repeated_failure"
            alert(result, kind="repeated_failure")
            break

    # Final fold (F1): fold the last cycle's landed inbox so a clean stop leaves nothing
    # unfolded at rest — otherwise the next restart would immediately F2-STOP on it.
    if stop_reason != "map_unreconciled":
        final_folded = fold_fn()
        if final_folded:
            build_executor.log(f"run_loop: final fold on stop -> map: {final_folded}")

    build_executor.log(f"run_loop: stopped ({stop_reason}) after {cycles} cycle(s)")
    clean = stop_reason in _CLEAN_STOPS
    build_executor._heartbeat(
        "idle" if clean else "blocked",
        f"Loop stopped: {stop_reason} after {cycles} cycle(s)",
        anomaly=None if clean else stop_reason,
    )
    return LoopSummary(stop_reason=stop_reason, cycles=cycles)
