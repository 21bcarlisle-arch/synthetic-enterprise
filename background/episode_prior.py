"""The seam above `episode_monotonic`: ABSENT and PRESENT-BUT-UNREADABLE are opposite facts.

`background/episode_monotonic.py` argues the distinction at length and turns on it in code -- a
prior that is not a Mapping is *present and unreadable*, data the guard cannot know, so it degrades;
`None` is *absent*, nothing came off disk, so nothing can be an echo. On 2026-09-04 that door was
fixed twice by two lanes and was still half a fix after both, because `prev=None` had been grouped
with a non-Mapping prior above the loops.

THIS MODULE EXISTS BECAUSE THE SAME CONFLATION WAS ONE LEVEL UP, IN EVERY CARRIER, AND THERE IT WAS
NOT HALF A FIX BUT A WHOLE ONE MISSING. Measured across the whole partition of prior states, five of
the eight paths the self-clearing-alarm census calls `real` answered a corrupt or truncated state
file exactly as they answered no state file at all:

    sim_runner.record_run_outcome(ok=False)      missing file -> streak=1 outage=0.00h
                                                 truncated    -> streak=1 outage=0.00h
                                                 OPEN EPISODE -> streak=8 outage=10.00h
    background_worker._check_zero_progress       missing file -> cycles=1
                                                 truncated    -> cycles=1
                                                 OPEN EPISODE -> cycles=9
    ntfy_utils.record_delivery_outcome(False)    missing file -> failures=1 deaf_for=0.00h
                                                 truncated    -> failures=1 deaf_for=0.00h
                                                 OPEN EPISODE -> failures=6

A ten-hour open episode collapsing to a fresh one because its own state file could not be read is
the 2026-08-09 shape verbatim -- the failure silencing its own alarm -- and it is the shape the
whole census was built to enumerate. `sim_runner`'s guard comment names "a truncated read" as
precisely what its `guard_episode` call protects against. Measured, it does not and cannot: the
loader had already flattened the truncated read to an absent prior one level above the guard, so
the guard's argued degrade door is not reachable from that call site at all. A branch that is
mutation-proved and unreachable in production is R15's own subject.

AND FOUR MEMBERS OF THE PARTITION DID NOT REACH A GUARD AT ALL, THEY RAISED. `json.loads` accepts
`null` and `[1, 2, 3]`, so both sail straight through an `except (json.JSONDecodeError, OSError)`
and out of a loader annotated `-> dict`. The next line is `state.get(...)`:

    supervisor._record_atom_draw_and_check_stall   json null -> AttributeError
    background_worker._check_zero_progress         json null -> AttributeError
    ntfy_utils.record_delivery_outcome             json null -> AttributeError

Those run on the supervisor's tick, the run-marker sweep, and EVERY ntfy send -- including the send
that carries the failure notification. The alarm's own writer crashed on the state it keeps its
alarm in.

WHAT THIS MODULE DOES, AND THE ONE THING IT DELIBERATELY DOES NOT. It classifies, once, and hands
the caller both halves: a mapping it can index without crashing, and the verdict on where that
mapping came from. It does NOT choose an escalation. What a given alarm should DO about a lost
episode memory is a per-control judgement -- the same judgement PW4 refused to make by reflex when
it chose close conditions one at a time -- and guessing it here would produce five controls that
escalate for a reason nobody picked. What the caller MUST NOT do is what all five did: record a
fresh episode, silently, on evidence it never had.

The verdicts are the partition, and they are exhaustive by construction (`classify_prior` returns
one of exactly these three for every input, which is what `test_episode_prior_partition.py` pins):

    ABSENT      -- no file on disk. Nothing was ever recorded; a new episode genuinely starts here.
    READABLE    -- a mapping came off disk. Today's behaviour, unchanged.
    UNREADABLE  -- the file EXISTS and its contents cannot be trusted: empty, unparseable, or
                   parsed to something that is not a mapping (`null` and `[1, 2, 3]` are both in
                   here -- they parse, which is exactly why they escaped every except-clause).

Pure classification plus one file read, and no imports from any module it serves: the census audits
those, and `episode_monotonic` states the same independence for the same reason.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

__all__ = ["ABSENT", "READABLE", "UNREADABLE", "PRIOR_VERDICTS",
           "classify_prior", "load_episode_prior", "prior_unreadable"]

ABSENT = "absent"
READABLE = "readable"
UNREADABLE = "unreadable"

#: Exhaustive. A fourth verdict added without a partition row is the silent narrowing this whole
#: sweep is about, so the control asserts the instrument covers exactly this set.
PRIOR_VERDICTS = (ABSENT, READABLE, UNREADABLE)


def classify_prior(raw: str | None) -> tuple[dict[str, Any], str]:
    """Classify the raw bytes of a state file. `raw is None` means NO FILE EXISTS.

    Returns `(state, verdict)`. `state` is always a plain dict, so a caller that ignores the
    verdict gets today's behaviour rather than an AttributeError three lines later -- the crash
    half of this fix is in that sentence. It is `{}` for both ABSENT and UNREADABLE **and the two
    are still told apart by the verdict**, which is the whole point: laundering them into one
    return value is how the distinction was lost the first time.

    Why an EMPTY file is unreadable and not absent: a zero-length file is what a truncated or
    interrupted write leaves behind, and the file existing is the evidence that something was
    there to truncate.
    """
    if raw is None:
        return {}, ABSENT
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}, UNREADABLE
    if not isinstance(parsed, Mapping):
        # `null` and `[1, 2, 3]` land here. They PARSE -- which is why an except-clause never saw
        # them -- and a `-> dict` annotation is not enforcement.
        return {}, UNREADABLE
    return dict(parsed), READABLE


def load_episode_prior(path: Path | str) -> tuple[dict[str, Any], str]:
    """`classify_prior` over a path. An existing file that cannot be READ is UNREADABLE, not absent.

    The `exists()`/`read_text()` split is deliberate and is the only place the two OSError readings
    are separable: a missing file raises the same `FileNotFoundError` as a vanished one, and
    collapsing them is the conflation this module is named after. A file that disappears between
    the two calls is reported ABSENT, which is what it now is.
    """
    p = Path(path)
    try:
        if not p.exists():
            return {}, ABSENT
    except OSError:
        return {}, UNREADABLE       # cannot even stat it: present for all we can tell
    try:
        return classify_prior(p.read_text())
    except FileNotFoundError:
        return {}, ABSENT           # raced away between exists() and read: absent now
    except OSError:
        return {}, UNREADABLE       # permissions, I/O error, a directory: present, unreadable


def prior_unreadable(verdict: str) -> bool:
    """Named rather than inlined as `== UNREADABLE`, so every carrier asks the question one way and
    a grep for the question finds all of them."""
    return verdict == UNREADABLE
