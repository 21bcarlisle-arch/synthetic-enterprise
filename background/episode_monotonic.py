"""PW2 -- the guard for the self-clearing-alarm class: a failure may not shorten its own episode.

WHAT THE CLASS IS: `background/self_clearing_alarm_census.py` enumerates, by derivation, every
control whose FAILURE path writes a state file its own ALARM reads. Where that state carries an
EPISODE-SCOPED field -- the timestamp an outage started, or the count of consecutive failures --
the failure write can move it FORWARD, and the alarm then truthfully reports a fresh episode
inside an old one. On 2026-08-09 a 10h26m publish outage paged as "wedged 14 minutes", because
each round of failures rewrote `wedge_since`.

THE INVARIANT, stated once: **while an episode is open, its start may only move EARLIER and its
counters may only go UP.** An episode start is a low-water mark; an episode counter is a
high-water mark. Only an explicit, evidenced CLOSE may reset either. "Append-or-monotonic", in the
steer's words.

WHY THAT IS THE RIGHT SHAPE AND NOT JUST A BIGGER NUMBER: the failure mode being cured is
UNDER-reporting -- an episode that reads shorter than it was. Monotonicity is directional on
purpose. It cannot make an episode look longer than the evidence, because the only value it ever
keeps is one that was already written by a real earlier failure; it simply refuses to forget it.

WHY `episode_closed` IS A CALLER'S ASSERTION AND NOT INFERRED HERE: this module cannot see whether
a publish actually happened. Making the caller pass the claim keeps the evidence where the
evidence lives, and makes "who closed this episode, and what proved it?" a question with exactly
one answer per call site. R15: `episode_closed=True` from a path that did not demonstrate a close
is still a defect -- it is just now a NAMED, greppable, testable one rather than an accident of
which function happened to write last.

FAIL DIRECTION: toward REMEMBERING. A malformed/absent previous state cannot shorten anything --
`guard_episode` keeps whatever the new write proposes rather than raising, so a corrupt state file
degrades to today's behaviour instead of crashing the pipeline it monitors. An unreadable prior is
the one case where the guard genuinely cannot know, and it says so by leaving the value alone.

WHY THE FIELD IS TYPED, AND WHY THE CALLER'S SIDE OF IT IS LOUD (2026-08-12, closing
WORKER_FINDING_THE_MONOTONIC_GUARD_IS_NUMERIC_ONLY_2026-08-10, BLOCKING): the field test used to be
`_is_num`, so an episode start stored as an ISO-8601 string -- which is how
`site/data/publish_provenance.json` stores `paused_since`, because the banner renders it verbatim
-- fell straight through. Declaring `since_fields=("paused_since",)` READ as protection in review,
passed any test asserting only that the call happens, and protected nothing: a failure moving the
start 27h later was a silent no-op. That is the fail-silent pattern R15 names, and an unavailable
check is a FAILED check. Two changes, and the split between them is the whole design:

  * ORDERABLE now means epoch-numeric OR ISO-8601 (naive read as UTC), so the natural wiring works.
  * A value the guard CANNOT order raises `EpisodeFieldTypeError` -- but only when it is the
    CALLER'S OWN PROPOSED value, or when the two sides disagree on representation. Both are
    deterministic properties of the call site that the first test run surfaces, never a
    data-dependent production surprise, so this does not re-open the wedge the fail direction above
    exists to prevent. A corrupt PERSISTED prior still degrades silently and provably harmlessly:
    with no readable earlier value there is nothing to remember, so keeping the proposal is exactly
    the unguarded behaviour and cannot under-report an episode. `None`/absent is not corruption --
    it is either "no episode was open" (prior side) or "a failure tried to CLEAR one" (proposed
    side), and both are repaired, not refused.
  * The winning value is returned in ITS OWN representation. A field whose low-water mark came back
    as an epoch float into a banner that prints it verbatim would be this finding's own defect
    wearing the other coat.

Pure functions only -- no I/O, no imports from the modules it guards (the census audits those).
Used by: `process_run_complete._write_publish_gate_state`.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

__all__ = ["guard_episode", "episode_age_seconds", "EpisodeFieldTypeError"]


class EpisodeFieldTypeError(TypeError):
    """A declared episode field carries a value this guard cannot order.

    Raised, never swallowed: the alternative is a call site that reads as guarded and is not, which
    is the defect this class of guard exists to make impossible."""


def _is_num(v: Any) -> bool:
    """Numeric and not a bool. `True` is an int in Python and would otherwise sail through a
    min()/max() as the number 1 -- which, on an epoch timestamp field, would silently become
    1970 and read as a 56-year episode."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _episode_key(v: Any) -> tuple[str, float] | None:
    """`(representation, seconds-since-epoch)` for an orderable episode start, else None.

    The representation is carried alongside the number so two sides of a comparison can be checked
    for AGREEMENT. A naive ISO timestamp is read as UTC -- stated, because assuming it silently
    would be one more thing this module knew and never said."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return ("epoch", float(v)) if math.isfinite(v) else None
    if isinstance(v, str):
        try:
            parsed = datetime.fromisoformat(v.strip())
        except ValueError:
            return None                   # includes "1786285809.38": an epoch spelled as a string
        if parsed.tzinfo is None:         # ...is NOT silently reinterpreted as a number
            parsed = parsed.replace(tzinfo=timezone.utc)
        return ("iso", parsed.timestamp())
    return None


def _absent(v: Any) -> bool:
    """Absent means "no value", which is never a type error -- it is the clear/cold-start case."""
    return v is None


def _refuse(field: str, side: str, value: Any) -> None:
    raise EpisodeFieldTypeError(
        f"episode field {field!r}: the {side} value {value!r} ({type(value).__name__}) is not an "
        f"orderable episode start -- expected an epoch number or an ISO-8601 timestamp. "
        f"Guarding it silently is how a call site reads as protected and is not."
    )


def guard_episode(
    prev: Mapping[str, Any] | None,
    new: Mapping[str, Any],
    *,
    since_fields: Iterable[str] = (),
    streak_fields: Iterable[str] = (),
    episode_closed: bool = False,
) -> dict[str, Any]:
    """Return `new` with its episode-scoped fields repaired against `prev`.

    `since_fields`  -- episode START timestamps. LOW-water: once set, they may only move earlier.
    `streak_fields` -- episode COUNTERS. HIGH-water: they may only go up.
    `episode_closed` -- the caller asserts, on evidence, that the episode has genuinely ended.
                        This is the ONLY way a start clears or a counter resets.

    A start may be an epoch number OR an ISO-8601 string; the two may not be mixed within one
    field, and the winner is returned in its own representation.

    Data never blocks the write: every other field in `new` passes through untouched, and a
    corrupt or absent PRIOR degrades to today's unguarded behaviour rather than crashing the
    pipeline this monitors. The one refusal is `EpisodeFieldTypeError` on a MISDECLARED field --
    a proposed value the guard cannot order, or two sides in different representations. That is a
    property of the call site, not of the data, so it cannot wedge a running pipeline; and it is
    the only thing standing between "wired this field in" and a no-op that reviews as protection.
    """
    out = dict(new)
    if episode_closed:
        return out
    if not isinstance(prev, Mapping):
        return out

    for field in since_fields:
        old, proposed = prev.get(field), out.get(field)
        old_key = _episode_key(old)
        if old_key is None:
            continue                      # no episode was open, or an unreadable prior: nothing
                                          # to remember, so whatever `new` says stands
        if _absent(proposed):
            out[field] = old              # a failure tried to CLEAR an open episode
            continue
        new_key = _episode_key(proposed)
        if new_key is None:
            _refuse(field, "proposed", proposed)
        if new_key[0] != old_key[0]:
            raise EpisodeFieldTypeError(
                f"episode field {field!r}: the previous value {old!r} is {old_key[0]} and the "
                f"proposed value {proposed!r} is {new_key[0]}. Ordering them is well defined but "
                f"the winner is written back, so a field that changes representation mid-episode "
                f"would publish the other one; fix the writer, do not guess here."
            )
        out[field] = old if old_key[1] <= new_key[1] else proposed   # low-water, own representation

    for field in streak_fields:
        old, proposed = prev.get(field), out.get(field)
        if not _is_num(old):
            continue                      # no episode was open, or an unreadable prior
        if _absent(proposed):
            out[field] = old              # a failure tried to RESET an open counter
            continue
        if not _is_num(proposed):
            _refuse(field, "proposed", proposed)   # a counter is a number, and only a number
        out[field] = max(old, proposed)

    return out


def episode_age_seconds(state: Mapping[str, Any], since_field: str, now: float) -> float | None:
    """How long the open episode has been running, or None if no start is recorded.

    Exists so the census's real hits measure episode length ONE way. `_episode_phrase` and the
    supervisor's wedge draw each derived this separately, which is how the same outage could be
    described as 10h by one surface and 14min by another (feedback: one name, two numbers).

    Reads the same two representations `guard_episode` orders -- a read side that could not see an
    ISO start would report the guarded episode as no episode at all."""
    key = _episode_key(state.get(since_field))
    if key is None:
        return None
    return max(0.0, float(now) - key[1])
