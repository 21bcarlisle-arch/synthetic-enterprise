"""Boot-recovery announce — OPS1 sub-step 4, guarantee G-R3 (reconcile before act).
docs/design/OPERATIONAL_LAYER_DESIGN.md §2.5, SUBSTEP4_SUPERVISOR_HYBRID.md §5.

PURPOSE
    On boot, RECONCILE the declared set (process_manifest + schedule_manifest) against the
    machine's ACTUAL systemd/tmux state and REPORT the result once -- BEFORE any autonomous
    work advances (G-R3). The blackout's anti-pattern was "cron resurrects whatever was there"
    with no one ever seeing the drift; this makes a boot state a stated, single, transition
    notification, never a silent mask.

GUARANTEES
    - ONE NTFY per boot (G-N1 transition-only, self-contained payload). Idempotent within a
      boot: a re-run in the same boot is a no-op (marker keyed to the kernel boot time). A new
      boot re-announces.
    - REPORT ONLY. It reconciles and notifies; it NEVER starts, stops, enables, or reaps
      anything (G-R4: recovery reports, it does not self-advance gated work). Bringing daemons
      up is systemd's job under the declared holds; advancing work is the governed supervisor's.
    - Typed by source (G-N2): tagged `rotating_light` (warning) when any drift alarm is present,
      `white_check_mark` when the boot came up clean.

WIRING
    Runs as the systemd oneshot `boot-announce.service` (Type=oneshot, WantedBy=default.target),
    declared in schedule_manifest.yaml and installed by install_schedule.sh -- so "announce the
    boot state" is committed IaC, reconstructable from the repo, not a hand-run habit.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import process_reconciler as _proc  # noqa: E402
from background import schedule_reconciler as _sched  # noqa: E402

MARKER = PROJECT_DIR / "docs" / "observability" / ".boot_announced"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "boot-announce-log.md"


def _boot_id() -> str:
    """A stable identifier for the current kernel boot (btime = boot epoch seconds from
    /proc/stat). Distinct per boot, identical across re-runs within a boot -- the idempotency
    key. Unknown/unreadable -> a constant so a re-run still de-dupes rather than double-paging."""
    try:
        for line in (Path("/proc") / "stat").read_text().splitlines():
            if line.startswith("btime"):
                return line.split()[1]
    except OSError:
        pass
    return "unknown-boot"


def already_announced_this_boot() -> bool:
    try:
        return MARKER.read_text().strip() == _boot_id()
    except OSError:
        return False


def _mark_announced() -> None:
    try:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_text(_boot_id())
    except OSError:
        pass


def build_summary(proc_results: list[dict] | None = None,
                  sched_results: list[dict] | None = None) -> tuple[str, bool]:
    """Format the one-shot reconcile summary. Returns (text, has_alarm). Results are
    injectable for tests; production reads live systemd/tmux state."""
    if proc_results is None:
        proc_results = _proc.reconcile(_proc._live_unit_states(), _proc._seat_active())
    if sched_results is None:
        sched_results = _sched.reconcile()

    proc_alarms = _proc.drift(proc_results)
    sched_alarms = _sched.drift(sched_results)
    has_alarm = bool(proc_alarms or sched_alarms)

    lines = ["[BOOT] Synthetic Enterprise came up — reconcile summary (report-only, G-R3):"]
    if has_alarm:
        lines.append(f"  DRIFT: {len(proc_alarms)} process + {len(sched_alarms)} schedule alarm(s):")
        for r in proc_alarms:
            lines.append(f"    ✗ {r['session']}: {r['status']}")
        for r in sched_alarms:
            lines.append(f"    ✗ [{r['kind']}] {r['item']}: {r['status']}")
    else:
        lines.append(f"  CLEAN: no drift ({len(proc_results)} declared processes, "
                     f"{len(sched_results)} schedule entries all as declared).")
    # Always show the held/dark posture so a boot states, not hides, what is deliberately down.
    held = [r["session"] for r in proc_results if r["status"] in ("HELD", "DARK")]
    if held:
        lines.append("  Declared-down (held/dark, expected): " + ", ".join(sorted(held)))
    return "\n".join(lines), has_alarm


def _log(msg: str) -> None:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"\n- [{ts}] {msg}")
    except OSError:
        pass


def announce(force: bool = False) -> bool:
    """Send the one boot NTFY if not already announced this boot. Returns True if it sent.
    Idempotent per boot unless `force`."""
    if not force and already_announced_this_boot():
        _log("boot already announced this boot — no-op")
        return False
    text, has_alarm = build_summary()
    from background.ntfy_utils import send_ntfy
    send_ntfy(text, headers={
        "X-Tags": "rotating_light" if has_alarm else "white_check_mark",
        "X-Priority": "high" if has_alarm else "default",
    })
    _mark_announced()
    _log(f"boot announced (alarm={has_alarm})")
    return True


def main(argv: list[str]) -> int:
    force = "--force" in argv
    announce(force=force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
