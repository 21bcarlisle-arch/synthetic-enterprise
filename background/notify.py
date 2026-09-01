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

# G-N4 (director, 2026-08-20). Imported from the module that owns the escalation rather than
# redeclared, so the threshold in the filed work item and the threshold that files it are the
# same number -- two copies of one constant is how the document ends up citing a bar that is
# no longer the bar.
from background.alarm_repetition import (  # noqa: E402
    EPISODE_GAP_SECONDS as _EPISODE_GAP,
    ESCALATE_AFTER_REPEATS as _ESCALATE_AFTER,
)

# G-N2: the closed set of notification kinds, each with a structural tag the director sees.
#
# `work_done` was added 2026-09-01, and the gap it fills is the director's complaint: *"the channel
# under-reports you. Eight commits this evening produced no message, while divergence and publishing
# alarms filled the mirror. I've read that as a stall twice today when you were working normally."*
#
# The routing layer had a class for routine landings from the day it was written -- it is one of the
# four categories he named himself -- and in three weeks it took ONE entry, from a health check. The
# KINDS set is why nothing else could use it: every member is a thing that went wrong, a batch of
# things that went wrong, a reply, or a fixture. There was no kind meaning "the machine finished a
# piece of work", so a landing had to masquerade as an alarm or not be sent, and it was not sent.
#
# It must NOT be `real_alarm`: an unkeyed real_alarm auto-keys on its own message with numbers
# normalised away (G-N4), so two landings with similar subjects would dedup each other and the
# second would vanish. Work done is never a repeat of other work done.
KINDS = ("real_alarm", "digest", "director_echo", "test_fixture", "work_done")
_KIND_TAG = {
    "real_alarm": "rotating_light",
    "digest": "bar_chart",
    "director_echo": "speech_balloon",
    "test_fixture": "test_tube",
    "work_done": "hammer_and_wrench",
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
           headers: dict[str, str] | None = None, topic_class: str | None = None,
           _allow_real_send: bool = False) -> str | None:
    """Send a notification through the one contract.

    kind: one of KINDS (G-N2, required — an untyped page is forbidden).
    topic_class: G-N3 (director, 2026-08-12) — WHY he is being told, from the closed instant
      set (action_needed | blocked_work | decision_waiting | publishing_down) or a deferrable
      category (divergence | drift | routine_landing | finding_announcement). A deferrable
      class is BATCHED into the periodic digest instead of sent, and returns a
      "deferred:<seq>" sentinel — never an id, because it has not been sent (G-N5).
      Omitted/unrecognised = INSTANT: the classifier fails toward paging him.
    transition_key + state: if given, transition-only (G-N1/R5) — SUPPRESS unless `state` changed
      since the last send for this key. Returns a "suppressed:unchanged:<key>" sentinel then.
    re_escalate_after: with a transition_key, RE-SEND an unchanged state once this many seconds have
      elapsed since the last send (the deadman's "re-alert hourly while still stuck" pattern). None
      (default) = pure transition-only, never re-send an unchanged state. A CHANGED state always
      sends immediately regardless.
    Returns the send id (or a sentinel string for suppressed / test_fixture / pytest)."""
    if kind not in KINDS:
        raise ValueError(f"notify kind must be one of {list(KINDS)}, got {kind!r}")

    # G-N4 (director, 2026-08-20): AN UNKEYED real_alarm KEYS ITSELF.
    #
    # R5 was never engaged for the alarm that woke him six times overnight, because
    # sim_runner.py called notify() with no transition_key at all -- the contract's central
    # rule was opt-in, and the one caller that most needed it had not opted in. Fixing that
    # caller would leave every other unkeyed real_alarm free to do the same (R10: the class,
    # not the instance), so the default moved instead.
    #
    # The key is derived from the message with elapsed times, counters, hashes and timestamps
    # normalised away, because the six pages were not byte-identical -- "after 252s" vs
    # "after 255s" -- and an exact-text dedup would have let all six through.
    #
    # Only real_alarm. A digest is a batch and re-sends by design; a director_echo is a reply
    # and must never be suppressed as a repeat of itself.
    if transition_key is None and kind == "real_alarm":
        from background import alarm_repetition
        transition_key = alarm_repetition.alarm_signature(message)
        if state is None:
            state = transition_key  # unchanged condition == unchanged state

    _pending_commit = None   # written only once a send is CONFIRMED (see below)
    if transition_key is not None:
        now = time.time()
        trans = _read_transitions()
        cur = str(state)
        prev = trans.get(transition_key)  # {"state": str, "ts": float} (or None; legacy str -> changed)
        unchanged = isinstance(prev, dict) and prev.get("state") == cur

        # A NEW EPISODE after a long quiet gap. An auto-keyed alarm derives its state from its
        # own message, so the state can never change and "the condition cleared" is not
        # expressible -- without this, the third repetition would silence that alarm forever.
        # A hand-keyed caller passes a real state and needs none of this, so it is scoped to
        # auto keys only and never overrides an explicit caller's intent.
        if (unchanged and str(transition_key).startswith("auto:")
                and (now - float(prev.get("last_seen", prev.get("ts", now)))) > _EPISODE_GAP):
            unchanged = False

        if unchanged:
            repeats = int(prev.get("repeats") or 1) + 1
            first_ts = float(prev.get("first_ts") or prev.get("ts") or now)
            escalated = bool(prev.get("escalated"))
            # THE ESCALATION (director, 2026-08-20: "make a repeating alert escalate itself
            # into the draw instead of re-telling me"). On its own thread, in the contract
            # every alarm already goes through -- deliberately NOT in an observer that has to
            # be ticking, because the observer that should have caught the overnight repeat
            # (RUNG 1d) was structurally sound, correctly fed, and simply not running.
            #
            # Guarded whole: a failure to file the work item must never swallow the alarm that
            # prompted it, which would turn a loud outage into a silent one.
            if repeats >= _ESCALATE_AFTER and not escalated:
                try:
                    from background import alarm_repetition
                    if alarm_repetition.escalate(message, key=transition_key,
                                                 repeats=repeats, first_ts=first_ts):
                        escalated = True
                except Exception:
                    pass  # not escalated; the send/suppress decision below is unaffected
            # ONCE IT IS WORK, STOP RE-TELLING HIM. A caller that sets `re_escalate_after`
            # is asking to be re-pinged hourly while a condition persists -- which was the
            # right behaviour when the phone was the only channel. It is not once the
            # condition has become a drawable work item: the director's instruction was
            # "escalate itself into the draw INSTEAD of re-telling me", and doing both is
            # the noise with an extra step.
            #
            # MEASURED, 2026-08-20, from the outbound mirror over 24h: of the 21 messages
            # sent after the escalation went in, the dead-man's BLOCKED alarm accounted for
            # four -- all hourly re-pings of one unchanged condition that had already
            # escalated. Nothing about them told him anything the work item did not.
            due = (re_escalate_after is not None
                   and not escalated
                   and (now - float(prev.get("ts", 0))) >= re_escalate_after)
            # `ts` is the last time this key SENT, so it only moves when a send follows.
            record = {
                "state": cur, "ts": (now if due else float(prev.get("ts", now))),
                "repeats": repeats, "first_ts": first_ts, "escalated": escalated,
                "last_seen": now,   # every FIRING, unlike `ts` which is every SEND
            }
            if not due:
                # Nothing will be sent, so this IS the final record for this firing.
                trans[transition_key] = record
                _write_transitions(trans)
                return f"suppressed:unchanged:{transition_key}"   # R5: unchanged (and not yet due)
            if str(transition_key).startswith("auto:"):
                _pending_commit = record          # see the note on the changed-state branch
            else:
                trans[transition_key] = record
                _write_transitions(trans)
        else:
            # A CHANGED state is a NEW EPISODE: the repeat counter and the escalation latch
            # both reset, so a condition that returns next week escalates again rather than
            # being silently absorbed by the record of an old one. This is also the recovery
            # path -- an alarm that clears changes state, and the next fault pages immediately.
            #
            record = {"state": cur, "ts": now, "repeats": 1,
                      "first_ts": now, "escalated": False, "last_seen": now}
            # AUTO-KEYED ONLY: the record is DEFERRED to _commit() below and written only if
            # the send actually DELIVERS. `send_ntfy` returns None when a send fails without
            # raising, so stamping the store on an ATTEMPT remembers a page that never arrived
            # and suppresses its retry as a duplicate -- losing the single notification an
            # outage produces. That is the 2026-07-18 deadman incident, and auto-keying
            # reintroduced it until that incident's own R15 proof went red.
            #
            # An EXPLICITLY-keyed caller keeps the original commit-on-attempt semantics
            # untouched. Those callers already carry their own delivery bookkeeping (the
            # deadman's `action_needed` register is the one that caught this), and silently
            # changing when their transitions land would be a second, unasked-for change
            # riding along with this one.
            if str(transition_key).startswith("auto:"):
                _pending_commit = record
            else:
                trans[transition_key] = record
                _write_transitions(trans)

    # G-N3 ROUTING (director, 2026-08-12: "cut the volume to fit it"). Placed AFTER the
    # transition check so a batched item obeys R5 exactly as a paged one does — a deferred
    # duplicate would fill the digest with the noise transition-only exists to remove — and
    # BEFORE the send so a deferred item never reaches the wire. kind="digest" is instant by
    # construction: it IS the batch, so routing it back into the queue would never terminate.
    def _commit(result):
        """Record the transition ONLY on a confirmed delivery, then return the result.

        `send_ntfy` returns a falsy value when a send fails without raising, so committing
        before the send would remember a page that never arrived and suppress its retry as a
        duplicate -- losing the only notification an outage produces. A deferral into the
        digest IS a delivery: the item is queued and will reach him."""
        if result and _pending_commit is not None:
            trans[transition_key] = _pending_commit
            _write_transitions(trans)
        return result

    if kind != "digest":
        from background import notification_digest
        if not notification_digest.is_instant(topic_class):
            return _commit(notification_digest.defer(message, kind=kind, topic_class=topic_class))

    h = dict(headers or {})
    h.setdefault("Tags", _KIND_TAG.get(kind, ""))

    # A test fixture must be STRUCTURALLY unable to page the director (G-N2), independent of the
    # send_ntfy pytest guard — so even a non-pytest process can never send a test_fixture page.
    if kind == "test_fixture" and not _allow_real_send:
        return _commit("test_fixture:not-sent")

    # Call via the module (not a bound import) so the conftest pytest guard and caller-test mocks
    # that patch ntfy_utils.send_ntfy are honoured, and the real send's own PYTEST guard applies.
    return _commit(ntfy_utils.send_ntfy(message, headers=h, _allow_real_send=_allow_real_send))


def current_state(transition_key: str) -> str | None:
    """The last state SENT for this key, or None if the key has never fired.

    Added for the recovery half of an alarm (2026-08-13). A caller that pages on a bad state and
    wants to page once when it clears has to know whether it was ever bad -- and without this it
    has only two options, both wrong: keep a second copy of the state beside the contract's own
    (two records of one fact, which is how they drift), or fire the recovery unconditionally,
    which announces a recovery from a fault that never happened on the very first cycle after a
    restart. Read-only; it cannot send, suppress, or re-arm anything."""
    prev = _read_transitions().get(transition_key)
    if isinstance(prev, dict):
        return prev.get("state")
    return prev if isinstance(prev, str) else None  # legacy bare-string entries


def clear_transition(transition_key: str) -> None:
    """Forget a key's last state, so the next send for it always fires (e.g. after a resolved
    alarm, to re-arm)."""
    trans = _read_transitions()
    if transition_key in trans:
        del trans[transition_key]
        _write_transitions(trans)
