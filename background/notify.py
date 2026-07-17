"""The ONE notification contract (OPS1 sub-step 6 — the notification model, §2.3).

Every director-paging notification is meant to go through `notify()` — ONE designed contract,
not the ~20 independently-patched `send_ntfy` paths that each re-implement transition-dedup and
spam-suppression their own way (the deadman's three hand-rolled `_last_*_ts`, sanity's
per-finding-set memory, …). This centralises the two properties the design requires:

  G-N1  transition-only (R5): a keyed alarm sends only when its STATE changes; an unchanged
        status never re-pages. One persisted transition store instead of a global-per-daemon.
  G-N2  typed by source: every notification declares a `kind` — real_alarm | digest |
        director_echo | test_fixture — and the type is STRUCTURAL (a tag the director sees), so
        a test fixture can never masquerade as a real alarm.

`background.ntfy_utils.send_ntfy` stays the low-level POST primitive (with its hard pytest guard);
this is the contract layer over it. MIGRATION: existing direct `send_ntfy` callers are grandfathered
and tracked as a SHRINKING allowlist in tests/background/test_notify_contract.py — new code must use
notify() (the guard fails otherwise), and the allowlist is the migration checklist.

Re-escalation (e.g. the deadman's hourly re-ping while still stuck) is NOT special-cased: a caller
that wants it varies `state` with a coarse time bucket (e.g. state=f"{status}:{hour}"), so a new
bucket is a new transition. Transition-only stays the one rule.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from background import ntfy_utils

_HERE = Path(__file__).resolve().parent
TRANSITIONS_FILE = _HERE.parent / "docs" / "observability" / ".notify_transitions.json"

# G-N2: the closed set of notification kinds, each with a structural tag the director sees.
KINDS = ("real_alarm", "digest", "director_echo", "test_fixture")
_KIND_TAG = {
    "real_alarm": "rotating_light",
    "digest": "bar_chart",
    "director_echo": "speech_balloon",
    "test_fixture": "test_tube",
}


def _read_transitions() -> dict:
    try:
        return json.loads(TRANSITIONS_FILE.read_text())
    except Exception:
        return {}


def _write_transitions(d: dict) -> None:
    try:
        TRANSITIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        TRANSITIONS_FILE.write_text(json.dumps(d))
    except Exception:
        pass


def notify(message: str, *, kind: str, transition_key: str | None = None,
           state: object | None = None, re_escalate_after: float | None = None,
           headers: dict[str, str] | None = None, _allow_real_send: bool = False) -> str | None:
    """Send a notification through the one contract.

    kind: one of KINDS (G-N2, required — an untyped page is forbidden).
    transition_key + state: if given, transition-only (G-N1/R5) — SUPPRESS unless `state` changed
      since the last send for this key. Returns a "suppressed:unchanged:<key>" sentinel then.
    re_escalate_after: with a transition_key, RE-SEND an unchanged state once this many seconds have
      elapsed since the last send (the deadman's "re-alert hourly while still stuck" pattern). None
      (default) = pure transition-only, never re-send an unchanged state. A CHANGED state always
      sends immediately regardless.
    Returns the send id (or a sentinel string for suppressed / test_fixture / pytest)."""
    if kind not in KINDS:
        raise ValueError(f"notify kind must be one of {list(KINDS)}, got {kind!r}")

    if transition_key is not None:
        trans = _read_transitions()
        cur = str(state)
        prev = trans.get(transition_key)  # {"state": str, "ts": float} (or None; legacy str -> changed)
        if isinstance(prev, dict) and prev.get("state") == cur:
            if re_escalate_after is None or (time.time() - float(prev.get("ts", 0))) < re_escalate_after:
                return f"suppressed:unchanged:{transition_key}"   # R5: unchanged (and not yet due)
        trans[transition_key] = {"state": cur, "ts": time.time()}
        _write_transitions(trans)

    h = dict(headers or {})
    h.setdefault("Tags", _KIND_TAG.get(kind, ""))

    # A test fixture must be STRUCTURALLY unable to page the director (G-N2), independent of the
    # send_ntfy pytest guard — so even a non-pytest process can never send a test_fixture page.
    if kind == "test_fixture" and not _allow_real_send:
        return "test_fixture:not-sent"

    # Call via the module (not a bound import) so the conftest pytest guard and caller-test mocks
    # that patch ntfy_utils.send_ntfy are honoured, and the real send's own PYTEST guard applies.
    return ntfy_utils.send_ntfy(message, headers=h, _allow_real_send=_allow_real_send)


def clear_transition(transition_key: str) -> None:
    """Forget a key's last state, so the next send for it always fires (e.g. after a resolved
    alarm, to re-arm)."""
    trans = _read_transitions()
    if transition_key in trans:
        del trans[transition_key]
        _write_transitions(trans)
