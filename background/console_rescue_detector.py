"""Console-rescue stall detector -- HX2 event E1.

Source: `docs/staging/done/DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27.md`
§3 event 1: "an emergency console rescue -- a granted turn at the terminal because the
machine could not recover otherwise. Arguably the single strongest stall signal
available; the proposed set names 'the director hand-typing the next atom', which may
not cover it." Real historical instances of this class: the 2026-07-14 6h blackout
(`docs/retrospectives/2026-07-14-tmux-injection-third-strike-and-fail-silent-deadman.md`),
the 2026-07-19 worker-seat identity deadlock ("the director bounced the seat himself",
`docs/retrospectives/2026-07-19-worker-seat-identity-drift.md`), and the 2026-07-20
death-on-a-transient-API-error 6h outage -- all real rescues, none produced a durable,
per-incident, machine-readable "a rescue happened" record at the time.

WHY THIS SHAPE (not a new always-on log): `background/director_input_log.py` already
channel-tags console input ("window") but mirrors it to the PRIVATE
`synthetic-enterprise-ops` repo (its own stated privacy amendment) -- unreadable from
this public-repo detector, and not something HX2 may widen (CLAUDE.md's routine-creation
/ platform-administration doors). `background/console.sh` / `director_console.sh` write
no console-open log of their own. Rather than accrete a new logging surface to patch this
one gap (CLAUDE.md's OPS1 "DON'T ACCRETE" rule -- a mechanism needs a stated purpose/fit
to the whole, not a bolt-on), this correlates TWO primary-state artefacts that already
exist for unrelated purposes:

  - `background/console_sanctity.py`'s registry (`.sanctified_consoles.json`) -- every
    interactive console records ITS OWN pid + `marked_at` the moment it starts (OPS1
    guarantee G-L1, built so the watchdog can never reap it -- not built for this).
  - `background/supervisor.py`'s `STUCK_STATE_FILE` (`.supervisor_stuck_state.json`) --
    `first_seen_at` (when the current stuck streak began) + `escalated` (whether the
    STUCK_THRESHOLD_SECONDS alarm already fired), built for the R3 idle-turn escalation
    (`_check_stuck_escalation`) -- not built for this either.

DEFINITION: a RESCUE is a console sanctified AFTER the current stuck streak began
(`marked_at > first_seen_at`) while that streak has ALREADY escalated (`escalated is
True`, i.e. the autonomous loop had already declared itself unable to proceed on its
own before this console opened). A console that PREDATES the stall (was already running
before `first_seen_at`) is the benign look-alike this must NOT trip -- a routine
long-lived director session that happens to still be open when the loop later gets
stuck is not a rescue of anything; see `test_console_rescue_detector.py`.

INDEPENDENCE (R15 anti-tautology): both inputs are written by OTHER mechanisms for
OTHER purposes -- this module derives its verdict from neither's self-report about
"was this a rescue".
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path


class StallDetectorUnavailable(Exception):
    """The check itself could not run -- a state file EXISTS but is corrupt/unreadable,
    or a required field is malformed. Distinct from a clean 'nothing to correlate'
    (`None`). Per R15 FAIL-SILENT doctrine: an unavailable check must never be read as
    a pass by the caller (see `background/stall_class_register.py`)."""


def _load_json_or_none(path: Path) -> dict | None:
    """Missing file -> None (legitimately 'never happened yet' -- the existing
    codebase convention, e.g. `supervisor._publish_gate_wedge_active`). A file that
    EXISTS but fails to parse, or does not hold a JSON object, -> raises
    StallDetectorUnavailable (a corrupt state file must not silently read as clear --
    the FAIL-OPEN pattern R15 forbids)."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise StallDetectorUnavailable(
            f"{path.name} exists but is unreadable/corrupt: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise StallDetectorUnavailable(f"{path.name} does not contain a JSON object")
    return data


def _parse_iso_to_epoch(value) -> float | None:
    """Best-effort ISO-8601 -> epoch seconds. Malformed/missing -> None (that single
    entry is skipped, not fatal -- one bad registry row must not hide every other
    entry; the sanctity registry is self-pruning elsewhere so a truly bad row is rare
    and transient)."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def console_rescue_active(
    now: float | None = None,
    sanctity_registry_path: Path | None = None,
    stuck_state_path: Path | None = None,
) -> str | None:
    """Returns a stall-class message if a console was sanctified DURING an
    already-escalated STUCK streak, else None (no signal). Raises
    StallDetectorUnavailable if a state file that EXISTS cannot be read/parsed, or if
    an escalated stuck-state carries no usable `first_seen_at` -- the caller
    (the stall-class register) must classify that as unavailable, not clear.
    """
    now = time.time() if now is None else now

    if sanctity_registry_path is None or stuck_state_path is None:
        # Import lazily: background.supervisor is a large module and this keeps a
        # bare `console_rescue_active()` call cheap for callers that always pass
        # explicit paths (e.g. every test), while still reusing the SAME constants
        # the writers use (single source of truth, no duplicated path literal).
        from background.console_sanctity import REGISTRY_PATH as _SANCTITY_PATH
        from background.supervisor import STUCK_STATE_FILE as _STUCK_PATH
        sanctity_registry_path = sanctity_registry_path or _SANCTITY_PATH
        stuck_state_path = stuck_state_path or _STUCK_PATH

    stuck = _load_json_or_none(stuck_state_path)
    if not stuck or not stuck.get("escalated"):
        return None  # no active, already-escalated stuck streak -- nothing to correlate

    first_seen_at = stuck.get("first_seen_at")
    if not isinstance(first_seen_at, (int, float)):
        raise StallDetectorUnavailable(
            "stuck state is escalated=True but carries no numeric first_seen_at"
        )

    registry = _load_json_or_none(sanctity_registry_path)
    if not registry:
        return None  # escalated, but no console has ever been sanctified

    for pid, entry in sorted(registry.items()):
        if not isinstance(entry, dict):
            continue
        marked_epoch = _parse_iso_to_epoch(entry.get("marked_at"))
        if marked_epoch is None:
            continue
        if marked_epoch > first_seen_at:
            age_min = int((now - first_seen_at) // 60)
            return (
                "CONSOLE RESCUE (HX2 E1): console pid {} was sanctified at {} -- AFTER "
                "the current STUCK streak began ('{}'), which is already ~{}min old and "
                "escalated. The autonomous loop had already declared itself unable to "
                "proceed before this console opened -- a rescue, not a routine "
                "check-in.".format(pid, entry.get("marked_at"), stuck.get("key", "?"), age_min)
            )
    return None
