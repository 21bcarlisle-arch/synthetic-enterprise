"""Durable "waiting on Rich" register + daily re-ping (2026-07-11, director
rule, from_rich_20260711_051508.md): "anything waiting on ME gets its own
dedicated [ACTION NEEDED] ntfy -- stating exactly what I must do, how, and
why -- never a line inside a status message. Re-ping daily while open, per
the blocked-alert rule."

Distinct from background/deadmans_switch.py's [BLOCKED] class (which detects
a STALLED PROCESS -- no commit/observability activity + queued staging work)
-- this is a NAMED register of specific open questions/decisions genuinely
needing Rich's own input, independent of whether the daemon stack itself is
healthy. An item here can sit open for days while everything else runs fine;
deadmans_switch.py would never catch that on its own.

Each entry is deliberately structured (what/how/why), not free text, so a
re-ping never degrades into a vague nag -- it always restates the concrete
ask.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REGISTER_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs" / "observability" / "action_needed_register.json"
)

RE_PING_SECONDS = 24 * 60 * 60  # daily, per the director's own rule


def _resolve_path(path: Path | None) -> Path:
    """Looks up REGISTER_PATH at CALL time, not function-definition time --
    see company/compliance/sanity_adjudication.py's identical fix for why a
    plain default-argument value would silently ignore a test's
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path)."""
    return path if path is not None else REGISTER_PATH


def load_register(path: Path | None = None) -> dict[str, dict]:
    path = _resolve_path(path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_register(register: dict[str, dict], path: Path | None = None) -> None:
    path = _resolve_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(register, indent=2, sort_keys=True))


def format_action_needed(item_id: str, what: str, how: str, why: str) -> str:
    """The one canonical message shape -- every [ACTION NEEDED] NTFY and
    every re-ping uses exactly this, so a re-ping restates the concrete ask
    rather than degrading into a vague nag."""
    return f"[ACTION NEEDED] {item_id}\nWhat: {what}\nHow: {how}\nWhy: {why}"


def register_item(
    item_id: str, what: str, how: str, why: str,
    path: Path | None = None, now: str | None = None,
) -> dict:
    """Add (or re-register, e.g. updated details) an open item. Does NOT
    send the NTFY itself -- the caller sends it once via
    format_action_needed(), then calls this to start/reset the daily
    re-ping clock."""
    ts = now or datetime.now(timezone.utc).isoformat()
    register = load_register(path)
    register[item_id] = {
        "item_id": item_id, "what": what, "how": how, "why": why,
        "first_asked_at": register.get(item_id, {}).get("first_asked_at", ts),
        "last_pinged_at": ts,
        "resolved": False,
    }
    save_register(register, path)
    return register[item_id]


def resolve_item(item_id: str, path: Path | None = None) -> None:
    """Rich answered it -- stop re-pinging. Kept in the register (not
    deleted) so there's a durable record of what was asked and when it
    closed."""
    register = load_register(path)
    if item_id in register:
        register[item_id]["resolved"] = True
        save_register(register, path)


def open_items(path: Path | None = None) -> list[dict]:
    return [e for e in load_register(path).values() if not e["resolved"]]


def due_for_reping(path: Path | None = None, now: str | None = None) -> list[dict]:
    """Open items whose last ping is >= RE_PING_SECONDS old -- what a daily
    daemon cycle should re-alert on."""
    now_dt = datetime.fromisoformat(now) if now else datetime.now(timezone.utc)
    due = []
    for entry in open_items(path):
        last_pinged = datetime.fromisoformat(entry["last_pinged_at"])
        if (now_dt - last_pinged).total_seconds() >= RE_PING_SECONDS:
            due.append(entry)
    return due
