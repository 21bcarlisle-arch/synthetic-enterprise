"""Periodic reconcile watch — OPS1 sub-step 4, G-L2/G-R3 made LIVE (not boot-only).

PURPOSE
    The reconcile (process_manifest + schedule_manifest + gap-ledger declared-vs-actual) is a
    DRIFT CONTROL.
    A control with no live consumer is fail-silent theatre (R15): boot_announce runs the reconcile
    once at boot, so between boots drift is UNWATCHED — exactly why a live worker-seat declared
    `held` produced no HELD_VIOLATED (found 2026-07-17 at the worker-seat gate). This closes that
    gap: run the reconcile on a systemd timer and make drift LOUD the moment it appears.

GUARANTEES
    - LIVE + PERIODIC: fired by reconcile-watch.timer (committed IaC), every RECONCILE_INTERVAL.
    - TRANSITION-ONLY NTFY (R5): pages only when the drift set CHANGES (appears / changes / clears),
      carrying the full payload — never a heartbeat. A clean run is logged, not paged.
    - REPORT-ONLY (G-R3): it reconciles and notifies; it starts/stops/enables/reaps NOTHING.
    - Typed by source (G-N2): `rotating_light` when drift is present, `white_check_mark` when it
      clears back to clean.

WIRING
    reconcile-watch.service (Type=oneshot) + reconcile-watch.timer, declared in schedule_manifest,
    installed+armed by install_schedule.sh — so "watch for drift" is committed, reconstructable IaC.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import gap_ledger_reconciler as _gap  # noqa: E402
from background import process_reconciler as _proc  # noqa: E402
from background import schedule_reconciler as _sched  # noqa: E402
from background import seat_work_in_hand as _seat  # noqa: E402

# How many gap-drift lines the human summary spells out before counting the rest. The SIGNATURE
# always carries every item (so no transition can hide behind the cap) and the overflow is stated,
# never silently dropped.
_GAP_SUMMARY_CAP = 5

STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".reconcile_watch_state.json"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "reconcile-watch-log.md"


def drift_signature(proc_results: list[dict], sched_results: list[dict],
                    gap_results: list[dict] | None = None) -> list[str]:
    """A stable, order-independent signature of the CURRENT drift set — the thing whose CHANGE is
    the transition worth paging on (R5). Clean == []."""
    return sorted(
        [f"P:{r['session']}:{r['status']}" for r in _proc.drift(proc_results)]
        + [f"S:{r['item']}:{r['status']}" for r in _sched.drift(sched_results)]
        + [f"G:{r['item']}:{r['status']}" for r in _gap.drift(gap_results or [])]
    )


def build_report(proc_results: list[dict], sched_results: list[dict],
                 gap_results: list[dict] | None = None) -> tuple[list[str], str]:
    """(drift_signature, human_summary). Injectable results for tests; production reads live."""
    gap_results = gap_results or []
    sig = drift_signature(proc_results, sched_results, gap_results)
    if not sig:
        summary = ("[RECONCILE] clean — no drift "
                   f"({len(proc_results)} declared processes, {len(sched_results)} schedule entries, "
                   f"{len(gap_results)} gap-ledger entries all as declared).")
    else:
        lines = [f"[RECONCILE] DRIFT — {len(sig)} item(s) diverge from the manifests:"]
        for r in _proc.drift(proc_results):
            lines.append(f"    ✗ {r['session']}: {r['status']}")
        for r in _sched.drift(sched_results):
            lines.append(f"    ✗ [{r['kind']}] {r['item']}: {r['status']}")
        gap_drift = _gap.drift(gap_results)
        for r in gap_drift[:_GAP_SUMMARY_CAP]:
            lines.append(f"    ✗ [gap:{r['status']}] {r['item']}")
        if len(gap_drift) > _GAP_SUMMARY_CAP:
            lines.append(f"    … and {len(gap_drift) - _GAP_SUMMARY_CAP} further gap-ledger "
                         "entr(ies) — full set in the drift signature")
        summary = "\n".join(lines)
    return sig, summary


def _load_last() -> list[str]:
    """Last-seen drift signature. Missing/unreadable => [] (clean baseline), so a FIRST clean run
    is NOT a false transition (it matches the clean baseline) while a first run that is already in
    drift correctly pages (drift != the clean baseline)."""
    try:
        data = json.loads(STATE_FILE.read_text())
        drift = data.get("drift") if isinstance(data, dict) else None
        return drift if isinstance(drift, list) else []
    except (OSError, ValueError):
        return []


def _save(sig: list[str]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"drift": sig,
                                          "at": datetime.now(timezone.utc).isoformat()}))
    except OSError:
        pass


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"\n- [{ts}] {msg}")
    except OSError:
        pass


def _digest_class():
    """The G-N3 class this daemon's pages carry. Imported lazily so a test injecting `notify`
    never has to have the digest module wired, and so this file stays importable on its own."""
    from background import notification_digest
    return notification_digest.DIVERGENCE


#: How many CHANGED LOADED MODULES make a daemon meaningfully stale rather than merely behind
#: today's churn. SET FROM THE MEASURED DISTRIBUTION on 2026-08-21, not chosen: immediately after
#: a restart every daemon sat at 1-2 (this tree takes ~20 commits a day, so "anything changed
#: since you booted" is true within minutes and is NOT a fault); the genuinely stale ones sat at
#: 57, 63 and 65. Nothing lives between 2 and 57, so the threshold is a real gap in the data and
#: not a tuned parameter.
#:
#: A count of 1-2 must never report, or this becomes an always-red detector and gets ignored --
#: which is precisely how the drift went unseen for four days while a correct control computed it.
DRIFT_MODULE_THRESHOLD = 10


def _drift_report(evaluate=None) -> list[str]:
    """['session (N modules behind)'] for daemons past the threshold. REPORT ONLY -- it never
    restarts anything. Redeploying a daemon mid-work is a decision with its own blast radius,
    and a reconcile that silently restarted things would be the accretion OPS1 forbids."""
    if evaluate is None:
        from background.process_reconciler import evaluate_boot_sha_drift as evaluate
    detail = (evaluate() or {}).get("stale_detail") or {}
    return [f"{s} ({len(f)} modules behind)"
            for s, f in sorted(detail.items(), key=lambda kv: -len(kv[1]))
            if len(f) >= DRIFT_MODULE_THRESHOLD]


def run(proc_results: list[dict] | None = None,
        sched_results: list[dict] | None = None,
        notify=None,
        gap_results: list[dict] | None = None) -> bool:
    """Run one reconcile, log it, and NTFY only on a drift-set TRANSITION. Returns True if it
    paged. `notify` and results are injectable for tests; production reads live + uses send_ntfy."""
    if proc_results is None:
        proc_results = _proc.reconcile(_proc._live_unit_states(), _proc._seat_active(),
                                       _proc._live_tmux_running())
    if sched_results is None:
        sched_results = _sched.reconcile()
    if gap_results is None:
        gap_results = _gap.reconcile()

    # Claimed-but-not-moving work goes back to the draw. It rides THIS timer rather than one
    # of its own because it is the same question the rest of this module asks -- what was
    # declared, versus what is actually true -- applied to work in hand instead of to
    # processes and units. It is deliberately NOT part of the drift signature and never pages:
    # a stalled claim is not an emergency, and the correct outcome is that the work moves, not
    # that a phone buzzes. See background/seat_work_in_hand.py for the 4h23m stall that every
    # existing watcher, including this one, reported as clean.
    try:
        released = _seat.sweep()
        if released:
            _log(f"seat claims released back to the draw: {', '.join(released)}")
    except Exception as exc:                                   # noqa: BLE001
        # A failure here must never stop the reconcile that this module exists to run.
        _log(f"seat-claim sweep failed (reconcile continues): {exc!r}")

    # DAEMONS RUNNING CODE THAT IS NO LONGER HEAD. R2 -- "committed != running" -- is one of
    # this repo's permanent rules, and on 2026-08-21 three daemons were 57, 63 and 65 changed
    # loaded modules behind, four days stale. The supervisor was making draw decisions on
    # four-day-old logic and a publishing-down alarm fixed that morning was inert in the process
    # that runs it.
    #
    # THE CONTROL WAS NOT MISSING. `process_reconciler.evaluate_boot_sha_drift()` computes this
    # precisely, and `health_check.py` phrases the fault well ("daemon(s) running an OLD copy of
    # a module they import (restart to deploy)"). Its only caller is `start_worker.sh`, at stack
    # startup -- so it ran at the single moment drift CANNOT exist and never during the four days
    # it accumulated. `health-check-log.md`'s last entry is 2026-07-29. Same shape as the seam
    # ratchet that wedged publishing for 27 hours the same day: a control that only fires when it
    # cannot.
    #
    # It rides this timer for the same reason the seat-claim sweep does -- declared-versus-actual
    # is the question this module already asks, and a fix's WORTH is exactly its deployment.
    try:
        drift = _drift_report()
        if drift:
            _log("boot-sha drift: " + "; ".join(drift))
    except Exception as exc:                                   # noqa: BLE001
        _log(f"boot-sha drift check failed (reconcile continues): {exc!r}")

    sig, summary = build_report(proc_results, sched_results, gap_results)
    last = _load_last()
    changed = sig != last

    _log(f"reconcile {'DRIFT' if sig else 'clean'} ({len(sig)} alarm(s)); "
         f"{'transition -> paging' if changed else 'unchanged -> log only'}")

    if changed:
        if notify is None:
            # THE CONTRACT, not the raw POST (2026-08-13). This called `send_ntfy` directly, so it
            # sat OUTSIDE `background.notify` and therefore outside G-N3 routing entirely -- which
            # is why a drift report the director cannot act on within the hour reached his phone
            # roughly twelve times on 2026-08-13, most of them the same five gap-ledger rows. Its
            # own name is the classification: manifest DIVERGENCE is the first category he listed
            # for batching.
            from background.notify import notify as notify
        cleared = not sig and last
        notify(summary, headers={
            "X-Tags": "white_check_mark" if cleared else "rotating_light",
            "X-Priority": "default" if cleared else "high",
        }, kind="real_alarm", topic_class=_digest_class())
        _save(sig)
    return changed


def main(argv: list[str]) -> int:
    run()
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/reconcile_watch.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("reconcile_watch")
    raise SystemExit(main(sys.argv))
