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

Pure functions only -- no I/O, no imports from the modules it guards (the census audits those).
Used by: `process_run_complete._write_publish_gate_state`.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

__all__ = ["guard_episode", "episode_age_seconds"]


def _is_num(v: Any) -> bool:
    """Numeric and not a bool. `True` is an int in Python and would otherwise sail through a
    min()/max() as the number 1 -- which, on an epoch timestamp field, would silently become
    1970 and read as a 56-year episode."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


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

    The write is never blocked and never raises: every other field in `new` passes through
    untouched. A guard that could refuse a write would be a new way to wedge the publish
    pipeline, which is the failure this whole atom exists downstream of.
    """
    out = dict(new)
    if episode_closed:
        return out
    if not isinstance(prev, Mapping):
        return out

    for field in since_fields:
        old, proposed = prev.get(field), out.get(field)
        if not _is_num(old):
            continue                      # no episode was open; whatever `new` says stands
        if not _is_num(proposed):
            out[field] = old              # a failure tried to CLEAR an open episode
        else:
            out[field] = min(float(old), float(proposed))   # ...or to move its start later

    for field in streak_fields:
        old, proposed = prev.get(field), out.get(field)
        if not _is_num(old):
            continue
        out[field] = max(old, proposed) if _is_num(proposed) else old

    return out


def episode_age_seconds(state: Mapping[str, Any], since_field: str, now: float) -> float | None:
    """How long the open episode has been running, or None if no start is recorded.

    Exists so the census's real hits measure episode length ONE way. `_episode_phrase` and the
    supervisor's wedge draw each derived this separately, which is how the same outage could be
    described as 10h by one surface and 14min by another (feedback: one name, two numbers)."""
    start = state.get(since_field)
    if not _is_num(start):
        return None
    return max(0.0, float(now) - float(start))
