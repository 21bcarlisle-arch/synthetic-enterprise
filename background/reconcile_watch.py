"""Periodic reconcile watch — OPS1 sub-step 4, G-L2/G-R3 made LIVE (not boot-only).

PURPOSE
    The reconcile (process_manifest + schedule_manifest declared-vs-actual) is a DRIFT CONTROL.
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

from background import process_reconciler as _proc  # noqa: E402
from background import schedule_reconciler as _sched  # noqa: E402

STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".reconcile_watch_state.json"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "reconcile-watch-log.md"


def drift_signature(proc_results: list[dict], sched_results: list[dict]) -> list[str]:
    """A stable, order-independent signature of the CURRENT drift set — the thing whose CHANGE is
    the transition worth paging on (R5). Clean == []."""
    return sorted(
        [f"P:{r['session']}:{r['status']}" for r in _proc.drift(proc_results)]
        + [f"S:{r['item']}:{r['status']}" for r in _sched.drift(sched_results)]
    )


def build_report(proc_results: list[dict], sched_results: list[dict]) -> tuple[list[str], str]:
    """(drift_signature, human_summary). Injectable results for tests; production reads live."""
    sig = drift_signature(proc_results, sched_results)
    if not sig:
        summary = ("[RECONCILE] clean — no drift "
                   f"({len(proc_results)} declared processes, {len(sched_results)} schedule entries "
                   "all as declared).")
    else:
        lines = [f"[RECONCILE] DRIFT — {len(sig)} item(s) diverge from the manifests:"]
        for r in _proc.drift(proc_results):
            lines.append(f"    ✗ {r['session']}: {r['status']}")
        for r in _sched.drift(sched_results):
            lines.append(f"    ✗ [{r['kind']}] {r['item']}: {r['status']}")
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


def run(proc_results: list[dict] | None = None,
        sched_results: list[dict] | None = None,
        notify=None) -> bool:
    """Run one reconcile, log it, and NTFY only on a drift-set TRANSITION. Returns True if it
    paged. `notify` and results are injectable for tests; production reads live + uses send_ntfy."""
    if proc_results is None:
        proc_results = _proc.reconcile(_proc._live_unit_states(), _proc._seat_active(),
                                       _proc._live_tmux_running())
    if sched_results is None:
        sched_results = _sched.reconcile()
    sig, summary = build_report(proc_results, sched_results)
    last = _load_last()
    changed = sig != last

    _log(f"reconcile {'DRIFT' if sig else 'clean'} ({len(sig)} alarm(s)); "
         f"{'transition -> paging' if changed else 'unchanged -> log only'}")

    if changed:
        if notify is None:
            from background.ntfy_utils import send_ntfy
            notify = send_ntfy
        # cleared back to clean vs appeared/changed -> typed by source (G-N2)
        cleared = not sig and last
        notify(summary, headers={
            "X-Tags": "white_check_mark" if cleared else "rotating_light",
            "X-Priority": "default" if cleared else "high",
        })
        _save(sig)
    return changed


def main(argv: list[str]) -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
