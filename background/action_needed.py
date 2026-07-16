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


def resolve_item(
    item_id: str, answer: str, path: Path | None = None, now: str | None = None,
) -> None:
    """Rich answered it -- record the ANSWER verbatim and stop re-pinging.

    `answer` is REQUIRED and non-empty: resolving without recording WHAT was
    decided is the exact defect that let the W2_2 curriculum answer evaporate
    (2026-07-14 retro, docs/retrospectives/2026-07-14-evaporated-director-
    decision.md). The old signature flipped a boolean and stored nothing, so
    even the happy path lost the decision content. Kept in the register (not
    deleted) as a durable record of what was asked, what was decided, and when."""
    if not answer or not answer.strip():
        raise ValueError(
            "resolve_item requires a non-empty answer -- a resolved item with no "
            "recorded decision content is the evaporation defect this argument closes."
        )
    register = load_register(path)
    if item_id in register:
        register[item_id]["resolved"] = True
        register[item_id]["answer"] = answer
        register[item_id]["resolved_at"] = now or datetime.now(timezone.utc).isoformat()
        save_register(register, path)


def confirm_and_resolve(
    item_id: str, answer: str, path: Path | None = None,
    send_ntfy_fn=None, now: str | None = None,
) -> bool:
    """Record a director decision AND confirm it back, so a silent drop is
    impossible (2026-07-14 landed-verification class: alarms and injections
    both verify they landed at their destination; decisions must too).

    Resolves the item (storing the answer) then sends a [RECORDED] confirmation
    the director can see -- the receipt that closes the loop. Returns True if a
    confirmation was sent. `send_ntfy_fn` is injectable for tests (defaults to
    background.ntfy_utils.send_ntfy); a send failure never rolls back the
    durable record -- the answer is stored first, confirmation is best-effort."""
    resolve_item(item_id, answer, path=path, now=now)
    if send_ntfy_fn is None:
        from background.ntfy_utils import send_ntfy as send_ntfy_fn  # lazy: keep zero-dep footprint
    try:
        send_ntfy_fn(
            f"[RECORDED] {item_id}\nDecision: {answer}",
            headers={"X-Tags": "white_check_mark"},
        )
        return True
    except Exception:
        return False


def pin_for(item_id: str) -> str:
    """A short, DETERMINISTIC reply-PIN for an escalation, computed the same way
    on both sides (executor emits it in the NTFY; ntfy_responder recovers the
    item_id by matching an inbound PIN against each open item's pin_for). Lets a
    phone reply CLOSE the exact escalation it answers instead of being re-ingested
    as a fresh urgent command (the answer-re-dispatch bug, 2026-07-16)."""
    import hashlib
    return hashlib.sha1(item_id.encode("utf-8")).hexdigest()[:4].upper()


def resolve_by_pin(pin: str, answer: str, path: Path | None = None,
                   send_ntfy_fn=None, now: str | None = None) -> str | None:
    """Resolve whichever OPEN item matches this reply PIN. Returns the resolved
    item_id, or None if no open item matches (so the caller can fall back to
    treating the message as a fresh instruction). Sends the [RECORDED] receipt."""
    pin = (pin or "").strip().upper()
    if not pin:
        return None
    for entry in open_items(path):
        if pin_for(entry["item_id"]) == pin:
            confirm_and_resolve(entry["item_id"], answer or "(no text)",
                                path=path, send_ntfy_fn=send_ntfy_fn, now=now)
            return entry["item_id"]
    return None


def should_notify(item_id: str, path: Path | None = None, now: str | None = None) -> bool:
    """THE single fire-once-then-daily gate (2026-07-16, director: "notifications/
    escalations fire every cycle instead of once-on-transition -- fix it as ONE
    rule across ALL paths"). Every notification/escalation caller runs its send
    through this. Returns True ONLY on a genuine TRANSITION:
      * the item is NEW (never signalled)              -> fire once, and
      * the item is OPEN and past its daily re-ping     -> the daily restate,
    and False otherwise:
      * OPEN but not yet due (the per-cycle case)       -> SILENT (the whole bug),
      * RESOLVED (already answered)                     -> SILENT.
    A True caller then calls register_item() (which resets the re-ping clock) and
    sends exactly once; a False caller sends nothing. Because per-cycle callers
    invoke this every cycle, this ALSO provides the daily re-ping for free without
    a separate scheduler -- fire on raise, restate daily, never per-loop."""
    reg = load_register(path)
    item = reg.get(item_id)
    if item is None:
        return True  # first transition into the signalled state
    if item.get("resolved"):
        return False  # answered -- never re-notify a closed item
    last = item.get("last_pinged_at")
    if not last:
        return True
    try:
        now_dt = datetime.fromisoformat(now) if now else datetime.now(timezone.utc)
        return (now_dt - datetime.fromisoformat(last)).total_seconds() >= RE_PING_SECONDS
    except (ValueError, TypeError):
        return True


def clear_item(item_id: str, path: Path | None = None) -> None:
    """Remove an item entirely (the signalled state ended cleanly, e.g. a staged
    doc was archived) so a genuinely-new future occurrence of the same id fires
    again. Distinct from resolve_item (which keeps a director-answered record):
    clear is for transitions that end WITHOUT a director decision. Idempotent."""
    reg = load_register(path)
    if item_id in reg:
        del reg[item_id]
        save_register(reg, path)


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


def escalate_if_one_way_door(
    item_id: str,
    description: str,
    how: str,
    *,
    explicit_category=None,
    uncertain: bool = False,
    path: Path | None = None,
    send_ntfy_fn=None,
) -> "OneWayDoorVerdict":  # noqa: F821 -- imported lazily below, forward ref for typing only
    """ACTION_NEEDED_REDESIGN_AND_BOOTSTRAP.md (P0, 2026-07-13, director-
    decided, "the single least reliable mechanism in the harness... [ACTION
    NEEDED] fires IF AND ONLY IF the one-way-door predicate returns true.
    No judgement, no remembering, no separate heuristic. One code path.").

    Root cause of every prior failure of this rule (per
    .claude/hooks/flag_unregistered_blocking_question.py's own retired
    diagnosis): CLASSIFYING something as blocking and REGISTERING it were
    two separate steps, with nothing forcing the second to follow the
    first -- the agent could correctly judge "this needs Rich" in prose and
    still forget register_item(). This function is the fix: classification
    and registration+alerting happen in ONE atomic call, so there is no
    seam left for the second step to be forgotten. There is deliberately
    NO separate prose-heuristic safety net layered on top any more (that
    hook is retired, not just deprioritised) -- PROCEED_BY_DEFAULT already
    shrinks the genuine one-way-door surface to small and rare, which is
    exactly what the director's own diagnosis says makes a single, clean,
    testable code path sufficient at last.

    Delegates the actual classification to
    background.one_way_door.classify_action() (imported here, not at
    module level, to keep action_needed.py's own existing zero-dependency
    footprint for every caller that never needs the one-way-door check).
    Returns the verdict either way; registers + alerts ONLY when
    verdict.is_one_way_door is True -- everything else is a silent no-op
    matching PROCEED_BY_DEFAULT's own "everything else: proceed" rule.

    `send_ntfy_fn` is injectable for tests (defaults to the real
    background.ntfy_utils.send_ntfy) -- this function sends its own alert
    directly rather than returning a message for the caller to remember to
    send, which is precisely the seam being closed."""
    from background.one_way_door import classify_action

    verdict = classify_action(description, explicit_category=explicit_category, uncertain=uncertain)
    if not verdict.is_one_way_door:
        return verdict

    category_label = verdict.category.value if verdict.category else "uncertain"
    why = f"One-way-door category: {category_label} -- {verdict.reason}"
    register_item(item_id, what=description, how=how, why=why, path=path)

    if send_ntfy_fn is None:
        from background.ntfy_utils import send_ntfy as send_ntfy_fn
    send_ntfy_fn(format_action_needed(item_id, description, how, why))
    return verdict
