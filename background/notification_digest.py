"""Periodic digest routing for the escalation channel — the notification model, §2.3 extension.

PURPOSE (director, NTFY 2026-08-12, `docs/staging/from_rich_20260812_165141.md`):

    "keep ntfy, stay on the free tier, cut the volume to fit it. Batch and summarise
    everything that isn't action-needed into periodic digests — divergence, drift, routine
    landings, finding announcements. Instant sends reserved for things I actually need to
    act on or know immediately: action-needed alarms, blocked work, a decision waiting on
    me, publishing down."

WHY THIS SHAPE, and why it is not another daemon. `background.notify.notify()` is already THE
one notification contract (G-N1 transition-only, G-N2 typed-by-source). Volume is a property of
that contract, not a new concern, so this is a ROUTING layer inside it rather than a parallel
path — a second sender would be exactly the accretion OPERATIONAL_LAYER_DESIGN forbids. It adds
no process: the flush rides the deadman's existing periodic cycle, the same self-throttled
timer that already hosts the operational-layer signal.

Volume is cut by ROUTING, never by dropping.

GUARANTEES

  G-N3  ROUTING.  The instant set is CLOSED and is the director's own four classes:
        ACTION_NEEDED, BLOCKED_WORK, DECISION_WAITING, PUBLISHING_DOWN. Everything else
        defers into the digest. An UNCLASSIFIED notification is INSTANT — the classifier
        fails toward paging him, because a wrongly-batched alarm costs an incident and a
        wrongly-instant one costs a message. (Same fail-closed direction as the model-tier
        classifier: cheap mistakes only.)

  G-N4  NOTHING IS LOST BY BEING BATCHED.  A deferred notification is appended to an
        APPEND-ONLY queue (`QUEUE_FILE`) BEFORE notify() returns, and its entry is NEVER
        deleted or rewritten — a digested item stays findable by grep forever, which is the
        director's first requirement. "Digested" is a high-water mark in a SEPARATE state
        file, so the record of what was said and the record of what was sent cannot corrupt
        each other. If the digest text has to elide items, it says so and names the file.

  G-N5  A DROPPED OR RATE-LIMITED SEND IS NEVER RECORDED AS SENT.  The director's second
        requirement, applied to both halves:
          * a deferred item is reported to its caller as `deferred:<seq>` — a sentinel, never
            an id, so no caller can read a batched item as delivered;
          * a digest flush advances the high-water mark ONLY on a CONFIRMED delivery. ntfy
            returning 429, curl failing, or any sentinel (pytest / suppressed / test_fixture)
            leaves the mark where it was, so the same items ride the next digest rather than
            evaporating. `_was_delivered` enumerates the sentinels as NOT-delivered rather
            than pattern-matching for success, so a new sentinel added upstream cannot be
            mistaken for an id.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_OBS = _HERE.parent / "docs" / "observability"

# The append-only record of every deferred notification (G-N4). Never rewritten.
QUEUE_FILE = _OBS / "ntfy_digest_queue.jsonl"
# The high-water mark of what a CONFIRMED digest has carried (G-N5). Separate on purpose.
STATE_FILE = _OBS / ".ntfy_digest_state.json"

# G-N3: the CLOSED instant set — the director's four classes, verbatim from his message.
ACTION_NEEDED = "action_needed"
BLOCKED_WORK = "blocked_work"
DECISION_WAITING = "decision_waiting"
PUBLISHING_DOWN = "publishing_down"
INSTANT_CLASSES = (ACTION_NEEDED, BLOCKED_WORK, DECISION_WAITING, PUBLISHING_DOWN)

# The categories he named for batching. Not a closed set: any unknown-but-declared class
# defers. Naming them buys grouped digest sections and nothing else.
DIVERGENCE = "divergence"
DRIFT = "drift"
ROUTINE_LANDING = "routine_landing"
FINDING_ANNOUNCEMENT = "finding_announcement"
DEFERRABLE_CLASSES = (DIVERGENCE, DRIFT, ROUTINE_LANDING, FINDING_ANNOUNCEMENT)

# How often the digest may go out. The flush is throttled, not scheduled: it rides whatever
# periodic cycle calls maybe_flush(), so a stopped daemon delays a digest and never loses one.
DIGEST_INTERVAL_SECONDS = 6 * 60 * 60

# Sentinels that are NOT a delivered id (G-N5). Enumerated as failures, never inferred.
_NOT_AN_ID_PREFIXES = ("deferred:", "suppressed:", "test_fixture:", "pytest-")

_MAX_DIGEST_LINES = 25


def _queue_ref() -> str:
    """The pointer the digest prints so an elided item stays findable (G-N4). Repo-relative
    when it can be, absolute otherwise -- a digest must never fail to send because its own
    breadcrumb could not be formatted."""
    try:
        return str(QUEUE_FILE.relative_to(_HERE.parent))
    except ValueError:
        return str(QUEUE_FILE)


def is_instant(topic_class: str | None) -> bool:
    """G-N3. None/unrecognised => INSTANT (fail toward paging him)."""
    if topic_class is None:
        return True
    return topic_class in INSTANT_CLASSES or topic_class not in DEFERRABLE_CLASSES


def _was_delivered(result: object) -> bool:
    """True only for a real ntfy message id. Every sentinel is a NON-delivery (G-N5)."""
    if not isinstance(result, str) or not result:
        return False
    return not result.startswith(_NOT_AN_ID_PREFIXES)


def _read_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def _write_state(d: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(d))


def _read_queue() -> list[dict]:
    try:
        text = QUEUE_FILE.read_text()
    except Exception:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a torn line is skipped, never fatal -- the rest still digests
    return out


def defer(message: str, *, kind: str, topic_class: str | None) -> str:
    """Append a non-urgent notification to the digest queue and return a DEFERRED sentinel.

    Never returns an id: a batched item has not been sent, and G-N5 forbids any record or
    caller reading it as if it had.
    """
    entries = _read_queue()
    seq = (entries[-1].get("seq", len(entries)) + 1) if entries else 1
    row = {
        "seq": seq,
        "ts": time.time(),
        "kind": kind,
        "class": topic_class or "unclassified",
        "message": message,
    }
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return f"deferred:{seq}"


def pending() -> list[dict]:
    """Queued entries no CONFIRMED digest has carried yet."""
    mark = int(_read_state().get("digested_through_seq", 0))
    return [e for e in _read_queue() if int(e.get("seq", 0)) > mark]


def compose(entries: list[dict]) -> str:
    """The digest text. Groups by class, and when it elides it SAYS SO and names the file
    that still holds every line (G-N4 -- a summary that hides its own truncation is how a
    batched item becomes a lost one)."""
    if not entries:
        return ""
    by_class: dict[str, list[dict]] = {}
    for e in entries:
        by_class.setdefault(str(e.get("class", "unclassified")), []).append(e)

    lines = [f"[DIGEST] {len(entries)} batched item(s) since the last digest."]
    budget = _MAX_DIGEST_LINES
    shown = 0
    for cls in sorted(by_class):
        rows = by_class[cls]
        lines.append(f"— {cls} ({len(rows)}):")
        for e in rows:
            if budget <= 0:
                break
            first = str(e.get("message", "")).strip().splitlines()
            lines.append(f"   #{e.get('seq')} {(first[0] if first else '')[:120]}")
            budget -= 1
            shown += 1
    if shown < len(entries):
        lines.append(
            f"… {len(entries) - shown} more not shown. EVERY item, in full, is in "
            f"{_queue_ref()} (seq {entries[0].get('seq')}–{entries[-1].get('seq')})."
        )
    else:
        lines.append(f"Full text of each: {_queue_ref()}")
    return "\n".join(lines)


def flush(*, _send=None) -> str | None:
    """Send one digest of everything pending. Returns the send result, or None if nothing
    was pending.

    G-N5: the high-water mark advances ONLY on a confirmed delivery. A 429, a curl failure
    or any sentinel leaves every item pending, so the next digest carries them again.
    """
    entries = pending()
    if not entries:
        return None
    text = compose(entries)

    if _send is None:                      # imported lazily: notify imports this module
        from background.notify import notify as _notify

        def _send(msg):
            # kind="digest" is instant BY CONSTRUCTION in notify() -- the digest is the
            # batch, so routing it back through the queue would be the obvious infinite
            # regress. Asserted there, not assumed here.
            return _notify(msg, kind="digest")

    result = _send(text)
    if _was_delivered(result):
        state = _read_state()
        state["digested_through_seq"] = max(int(e.get("seq", 0)) for e in entries)
        state["last_digest_ts"] = time.time()
        _write_state(state)
    return result


def _due(now: float | None = None) -> bool:
    now = time.time() if now is None else now
    last = float(_read_state().get("last_digest_ts", 0) or 0)
    return (now - last) >= DIGEST_INTERVAL_SECONDS


def maybe_flush(*, _send=None) -> str | None:
    """Throttled flush for a periodic caller (the deadman cycle). No-op until due."""
    if not _due():
        return None
    return flush(_send=_send)
