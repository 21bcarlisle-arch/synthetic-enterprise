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

A NON-POSITIVE VALUE IS NOT A START, ON EITHER SIDE (2026-09-04, in two passes). `0` passed
`_is_num`, so on a LOW-water field it beat every later value forever -- and the repair at the
writer that stopped ADOPTING a persisted zero was, measured, a complete no-op, because this guard
wrote the zero straight back. `_is_start_to_remember` states the screen once.

The first pass screened the PRIOR only, and left the PROPOSAL as today on the stated ground that
screening it "could turn a data-dependent value into a silent field-clear". Measured, that ground
was backwards: because `since_fields` is LOW-water, an unrecordable proposal is the EARLIEST value
orderable, so it did not survive the guard, it WON -- `guard_episode({"t": 1.7e9}, {"t": 0})`
returned `0`, dating a live 2026 episode to 1970 in one write. Screening the proposal is therefore
the opposite of a clear: with a start on the prior side the prior now stands. `_asserts_no_start`
carries the full argument and the measurements.

AND THE ORDER CLAIM THAT SENTENCE ENDED ON WAS FALSE, kept here beside its correction (2026-09-04,
third pass). It read: "the proposal is type-checked first and a misdeclared field still raises."
The proposal was type-checked *last* -- both loops screened the PRIOR and `continue`d before they
ever looked at the proposal's type -- so the refusal was silent in exactly the state a newly wired
field is in. Measured, before this pass:

    guard_episode({"t": None},   {"t": "banana"}, since_fields=("t",))   -> {"t": "banana"}
    guard_episode({"t": 1.7e9},  {"t": "banana"}, since_fields=("t",))   -> RAISES
    guard_episode({"c": None},   {"c": "banana"}, streak_fields=("c",))  -> {"c": "banana"}

That is the reachability of a guard running exactly backwards: quiet while the field is new and
unproven, loud only once it has been working long enough to have a recorded prior. A cold state
file is not an edge case for a just-wired field -- it is the definition of one, so "the first test
run surfaces it" was never true of the run that mattered. `_check_proposal_is_orderable` now runs
at the top of BOTH loops and the sentence above is finally a description of the code.

Pure functions only -- no I/O, no imports from the modules it guards (the census audits those).
Used by: `process_run_complete._write_publish_gate_state`.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

__all__ = ["guard_episode", "episode_age_seconds", "recorded_instant_seconds",
           "EpisodeFieldTypeError"]


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


def _is_start_to_remember(key: tuple[str, float] | None) -> bool:
    """Does this key name an instant an episode could actually have STARTED at?

    Asked of BOTH sides, and the asymmetry that remains is only about what happens next
    (2026-09-04, second pass -- see `_asserts_no_start`). The two sides are asked different
    questions in this order. Of the proposal the guard asks first *can I order this?* -- a property
    of the call site, and a misdeclared field must still raise. Of both sides it then asks *is
    there an episode start here?* -- and an instant at or before the epoch answers **no**. It is
    the same fact as `None`: nobody recorded a start. Screening it here rather than in
    `_episode_key` keeps `_refuse` firing on genuine type errors alone, so this cannot raise inside
    the failure path of the pipeline it monitors.

    WHY IT NEEDED SAYING. `_is_num` already refuses `bool` because `True` "would silently become
    1970 and read as a 56-year episode" -- and `0` walked through the branch written to stop
    exactly that. A persisted `wedge_since: 0.0` therefore beat every honest restamp: this is a
    LOW-water field, `0.0 <= anything`, so the guard wrote the zero back forever and the repair at
    the writer (`process_run_complete.record_publish_gate_failure`) was a measured no-op without
    this. See PREREG_WHETHER_THE_FIXTURE_PIN_IS_ACTUALLY_THE_BLOCKER_ON_THE_ZERO_ADOPTION_2026-09-04.

    Positive, not merely non-zero: the wall clock is 2026 and the simulation is 2016-2025, so no
    writer in this repository can mean an instant at or before 1970-01-01.

    This cannot under-report an episode, which is the failure mode the class exists to cure: the
    only value it declines to remember is one that dates the episode to before anything here ran.
    """
    return key is not None and key[1] > 0


def recorded_instant_seconds(v: Any) -> float | None:
    """Seconds since the epoch for a value that names an instant SOMETHING HERE ACTUALLY RECORDED,
    else None. Accepts an epoch number or an ISO-8601 string, the two representations this module
    orders everywhere else.

    THE VALUE-LEVEL DOOR (2026-09-04). `episode_age_seconds` answers this question for a named
    field of a state mapping. Its callers were not the only ones asking it: `supervisor
    ._publish_gate_wedge_active` had to ask it of `failures[].ts` -- a per-failure timestamp inside
    a list, which is not a field of a mapping and has no episode-start reading at all -- and so
    hand-rolled `isinstance(v, (int, float))` with no screen behind it. That is how a fourth copy
    of one question gets written: not out of carelessness, but because the centralised form only
    fitted three of the four shapes. This is the shape the fourth needed.

    WHY ONE SCREEN SERVES BOTH, STATED AS TWO ARGUMENTS RATHER THAN ONE BORROWED ONE -- because
    the readings differ and only the verdict coincides, and a borrowed argument is how a clause
    written about one field silently acquires authority over another:

      * Of an EPISODE START, `_is_start_to_remember` already says it: an instant at or before the
        epoch is not a start, it is the same fact as `None` -- nobody recorded one.
      * Of a FAILURE TIMESTAMP the reading is different and the verdict is the same. `0` there does
        not mean "this failure was observed in 1970"; no observer in this repository has a clock
        that could produce it. It means the stamp is MISSING, and a missing stamp is not evidence
        about when anything happened. The harm is specific: these values are fed to a `min()` that
        dates a wedge, so one of them dates the outage to 1970 -- older than any threshold, so the
        alarm fires forever at priority zero on a gate that is fine.

    NON-FINITE IS THE ONE THAT BITES HARDEST, and `json.loads` accepts the bare `NaN`/`Infinity`
    tokens, so it arrives from a FILE rather than from a caller's mistake. `NaN` fails every
    comparison, so it walks straight through an age threshold; `min()` returns it or not depending
    on list order; and `int(NaN // 60)` and `time.gmtime(NaN)` both RAISE. A detector that promised
    its callers it would never raise into the draw ladder therefore had a crash whose reachability
    turned on dict iteration order.

    BUT NOT, AS THIS DOCSTRING FIRST CLAIMED, the reason to prefer this function over a hand-rolled
    `v > 0` -- the mutation run refuted that. `NaN > 0` is False, so a bare positivity test screens
    NaN too, by accident of IEEE semantics. The reasons that survive measurement are duller and
    real: `+Infinity` PASSES `v > 0` and turns an age into `-inf`, which reads as "too young" and
    suppresses the alarm silently; an ISO-8601 value -- which `guard_episode` may write back,
    because the winner is returned in its own representation -- is dropped entirely by a numeric
    test; and a fifth copy is a fifth thing to keep in step. Kept here beside the claim it
    corrects, per the rule about predictions filed before their answers.

    Returns the ORDERED NUMBER, not the value: a caller doing arithmetic wants seconds, and making
    it re-parse an ISO string itself is how the representations drift apart again."""
    key = _episode_key(v)
    return key[1] if _is_start_to_remember(key) else None


def _absent(v: Any) -> bool:
    """Absent means "no value", which is never a type error -- it is the clear/cold-start case."""
    return v is None


def _asserts_no_start(v: Any) -> bool:
    """Does this PROPOSED value assert that no episode start is recorded?

    Two values assert it and the guard used to hear only one. `None` says it in words. A
    non-positive epoch -- or a `1970-01-01` ISO string, which is the same instant in the other
    representation -- says it in numbers, because no writer in this repository has a clock that
    could mean an instant at or before 1970. `episode_age_seconds` has answered `None` to both
    since the read side was screened; this is the write side finally agreeing with the read side.

    WHY THE PROPOSAL NEEDED THIS AND NOT JUST THE PRIOR (2026-09-04, closing the half the
    timestamp-screen sweep deliberately left out). Screening only the prior read as the lax half of
    a safe asymmetry. It was not lax, it was inverted: `since_fields` is LOW-water, so `0` is the
    EARLIEST instant orderable and therefore *wins*. Measured, before the change:

        guard_episode({"t": 1.7e9}, {"t": 0},                    ...) -> {"t": 0}
        guard_episode({"t": "2026-09-04T10:00:00"},
                      {"t": "1970-01-01T00:00:00"},              ...) -> {"t": "1970-01-01..."}

    A single bad write did not merely survive the guard; the guard PREFERRED it over a healthy
    2026 start and dated a live episode to 1970. The three carriers that echo their own proposal
    off disk (`ntfy_utils.since_epoch`, `sim_runner.first_failure_ts`,
    `process_run_complete.wedge_since`) then re-proposed it forever. All three now screen what they
    echo with `recorded_instant_seconds` before offering it, which is what makes the hoisted type
    check below safe -- see `_check_proposal_is_orderable`.

    WHY TREATING IT AS ABSENT CANNOT UNDER-REPORT, which is the failure mode this whole class
    exists to cure. The value declined is one that dates the episode to before anything here ran,
    and the two outcomes are the two the absent case already has:

      * with a start on the prior side, the PRIOR STANDS -- strictly more remembering than today,
        where the unrecordable proposal took the field.
      * with no start on the prior side, the field is written as the `None` it means. Nothing
        rendered changes: `episode_age_seconds` and `recorded_instant_seconds` already answer
        "no start recorded" to `0`. What changes is that the carrier stops re-proposing a value
        that reads as an established 1970 episode to the next hand-rolled `isinstance` test that
        meets it -- and there were three of those, one of them on a PRIORITY ZERO page.

    AND WHY IT IS NOT A REFUSAL. This screen is asked only of values `_episode_key` could already
    order, so it neither adds nor removes a raise. `bool` and `NaN` are not in this set at all --
    they are unorderable, and are refused by `_check_proposal_is_orderable` before this is asked.
    """
    if _absent(v):
        return True
    key = _episode_key(v)
    return key is not None and not _is_start_to_remember(key)


def _check_proposal_is_orderable(field: str, proposed: Any, is_orderable) -> None:
    """Refuse a proposed value this guard cannot order -- asked BEFORE the prior is consulted.

    WHY IT MOVED (2026-09-04). Both loops used to screen the prior first and `continue` on an
    unrecordable one, so the refusal never ran when the state file was cold. The module docstring
    above carries the measurements and the correction of the claim this contradicted.

    WHY THAT IS SAFE, WHICH IS THE WHOLE OF THE DECISION AND WAS PRE-COMMITTED AS A SEPARATE ONE.
    The stated risk of widening where `_refuse` fires is that a value ECHOED OFF DISK reaches a
    raise inside the failure path of the pipeline this guard monitors -- which is the harm the
    module's fail direction exists to prevent. That risk is specific and checkable, so it was
    checked rather than argued. Every live `since_fields` carrier derives its proposal like this:

      * `supervisor._check_stuck_escalation` -- `first_seen_at = now`. Never off disk.
      * `sim_runner.record_run_outcome`      -- `first if recorded_instant_seconds(first) is not
                                                None else stamp`.
      * `ntfy_utils`                         -- `_carry_epoch`, same screen, else `now`.
      * `process_run_complete`               -- `prev if _is_episode_start(prev) else now`, and
                                                `_is_episode_start` delegates here.

    Every carrier that echoes disk already vets what it echoes, with THIS MODULE'S OWN screen, so
    no live call site can reach `_refuse` with a data-dependent value on either path. The raise is
    therefore what the docstring always claimed it was: a property of the call site.

    THE RESIDUAL, NAMED RATHER THAN GLOSSED. A future carrier that echoes its prior UNSCREENED
    would meet this raise on exactly the cold path -- because for such a carrier `proposed is old`,
    so a corrupt disk value makes the prior unrecordable and the proposal unorderable in one move.
    A provenance test (`proposed is old` -> degrade, else refuse) would exempt it, and was
    rejected: it buys protection for a carrier class that does not exist and whose three former
    members' own comments record being fixed AWAY from that shape, at the price of a second
    mechanism keyed to a proxy for where a value came from. The smaller mechanism is the one that
    fires, plus the four screens above that make firing unreachable from real data.
    """
    if _absent(proposed):
        return                      # a clear/cold-start, never a type error (`_absent`)
    if not is_orderable(proposed):
        _refuse(field, "proposed", proposed)


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
                        This is the ONLY way a RECORDED start clears or a counter resets. A start
                        nobody recorded -- `None`, or an epoch at/before 1970, which is the same
                        fact spelled in numbers -- needs no close to go, because there is nothing
                        there to close (`_asserts_no_start`).

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
        _check_proposal_is_orderable(       # BEFORE the prior screen: a cold state file is the
            field, proposed,                # state a just-wired field is IN, and it used to be
            lambda v: _episode_key(v) is not None)   # the one state that could not raise.
        old_key = _episode_key(old)
        if not _is_start_to_remember(old_key):
            # No episode was open, an unreadable prior, or a start at/before the epoch -- which is
            # the same fact as no start at all. Nothing to remember, so `new` stands... except that
            # a proposal asserting no start is written as the `None` it means rather than persisted
            # as a number the next reader will mistake for one. Both sides say "nobody recorded a
            # start"; the field should say it too.
            if _asserts_no_start(proposed):
                out[field] = None
            continue
        if _asserts_no_start(proposed):
            out[field] = old              # a failure tried to CLEAR an open episode -- in words
            continue                      # (`None`) or in numbers (a 1970 epoch). Same assertion,
                                          # same answer: the recorded start stands.
        new_key = _episode_key(proposed)    # non-None: absent and unorderable both left above
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
        _check_proposal_is_orderable(     # a counter is a number, and only a number -- and the
            field, proposed, _is_num)     # same hoist, for the same reason, one loop over
        if not _is_num(old):
            continue                      # no episode was open, or an unreadable prior
        if _absent(proposed):
            out[field] = old              # a failure tried to RESET an open counter
            continue
        out[field] = max(old, proposed)

    return out


def episode_age_seconds(state: Mapping[str, Any], since_field: str, now: float) -> float | None:
    """How long the open episode has been running, or None if no start is recorded.

    Exists so the census's real hits measure episode length ONE way. `_episode_phrase` and the
    supervisor's wedge draw each derived this separately, which is how the same outage could be
    described as 10h by one surface and 14min by another (feedback: one name, two numbers).

    Reads the same two representations `guard_episode` orders -- a read side that could not see an
    ISO start would report the guarded episode as no episode at all.

    It applies the SAME `_is_start_to_remember` screen as the write side (2026-09-04), for the same
    reason the two live in one module: a reader that answered "500,000 hours" to a non-positive
    start would be publishing a confident figure from a value nobody recorded, which is the defect
    this screen was added to close. `None` here means what the first line says -- no start is
    recorded -- and that is precisely what a zero is."""
    started = recorded_instant_seconds(state.get(since_field))
    if started is None:
        return None
    return max(0.0, float(now) - started)
