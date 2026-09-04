"""A non-positive episode start must degrade, not render as 1970 with a plausible age.

THE DEFECT (2026-09-04, found on the director's own reserved surface).
`process_run_complete._episode_phrase` guarded its start time with:

    if not isinstance(wedge_since, (int, float)):

which refuses `None` correctly and **accepts 0, because 0 is an int**. The alarm then rendered
`datetime.fromtimestamp(0)` as an established fact:

    EPISODE: wedged since 1970-01-01T00:00 UTC -- 0h00m and 3 consecutive failures in THIS
    episode (not a fresh hour). Markers pending: 0.

That exact sentence was observed in `site/data/director_reserved.json` — the queue reserved for
the four classes nothing here may decide — where it had **evicted** the director's live one-way-door
escalation (the mirror replaces the item list; the caller-side hole is fixed in 33b54b3ee).

WHY THIS IS WORSE THAN A MISSING FIGURE, which is the whole reason it gets its own control: the
`None` branch beside it says *"start time unrecorded (this alarm cannot bound the episode)"*, and a
reader can act on that. `1970-01-01T00:00 UTC -- 0h00m` cannot be told apart from a real reading.
It is a confident answer built from a value nobody recorded, on the one surface where the reader is
a person who cannot check it.

WHERE THE ZERO CAME FROM — RESEARCHED, NOT ASSUMED, because "a fixture or a real write path"
have opposite remedies. It is **fixture-origin, and no production path can stamp it**:

  * `record_publish_gate_failure(now=None)` resolves `now = time.time()`, and the episode stamp is
    `wedge_since = prev if isinstance(prev, (int, float)) else now`. A live publisher therefore
    stamps a 2026 clock or adopts an already-persisted value; it has no branch that produces 0.
  * `"wedge_since": 0.0` appears verbatim in publish-gate **test fixtures**, beside
    `git_hash="abc1234"` — and `git=abc1234` is what the observed alarm carried.
  * `0h00m` is the corroborating tell. The age is `now - wedge_since`, so an epoch start against a
    real clock reads as ~500,000h. Both fields at zero means the CLOCK was a fixture's too.

So the class is "a test's state reached a production surface", and it is being closed at three
levels rather than one: the caller (33b54b3ee), the sink (`site/data/director_reserved.json` added
to `tests/production_surface_guard.PROTECTED_FILES` in this commit), and here — the renderer, which
must not present a non-positive epoch as an established start whatever wrote it.

THE ONE THING NOT FIXED HERE -- CLOSED 2026-09-04, in the second half of this file. The original
note said `record_publish_gate_failure` carried the same accepts-0 shape when it ADOPTS a persisted
`wedge_since`, and that the cost was a pinned fixture in `test_publish_gate_blocking_payload`.

**That account was wrong and the correction is kept here beside it**, because a prediction filed
after the answer is not a prediction. The pinned fixture was never the blocker: repairing the
adoption clause alone left the persisted value at `0.0`, and that fixture GREEN. The real blocker
was `episode_monotonic.guard_episode`, which treats an episode start as LOW-water -- so a persisted
`0.0` beat every honest restamp forever, and the writer-side repair measured as a complete no-op.
Two changes are load-bearing (the writer's screen and the guard's), and each is dead without the
other. Pre-registered before the measurement, with what would refute it:
`docs/staging/records/PREREG_WHETHER_THE_FIXTURE_PIN_IS_ACTUALLY_THE_BLOCKER_ON_THE_ZERO_ADOPTION_2026-09-04.md`
"""
from __future__ import annotations

import json

import pytest

import background.process_run_complete as prc

UNRECORDED = "start time unrecorded"
REAL_WEDGE = 1_800_000_000.0          # a 2027 clock: an ordinary, positive episode start


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    yield


class _Sink:
    def __init__(self):
        self.messages = []

    def __call__(self, *args, **kwargs):
        self.messages.append(" ".join(str(a) for a in args) + " " + str(kwargs))
        return True


# --------------------------------------------------------------------------- #
# The renderer
# --------------------------------------------------------------------------- #
def test_a_zero_start_time_does_not_render_as_1970():
    """THE DEFECT ITSELF. Zero is an int, so the old guard waved it through."""
    phrase = prc._episode_phrase(0, 3, now=0)

    assert UNRECORDED in phrase, phrase
    assert "1970" not in phrase, (
        "a zero start time still names an epoch date -- the guard is accepting 0 because 0 is "
        f"an int: {phrase}")


def test_a_zero_start_time_does_not_render_a_plausible_age():
    """The age is the half that made it READ as a real measurement, so it is asserted apart.

    A fix that degraded the DATE but still printed `0h00m` beside it would pass the test above
    and leave the director exactly as misled.
    """
    phrase = prc._episode_phrase(0, 3, now=0)
    assert "h00m" not in phrase and "0h" not in phrase, phrase


def test_a_zero_start_time_with_a_real_clock_is_still_refused():
    """The zero that is NOT accompanied by a zero clock -- ~500,000h, absurd on its face.

    Included because the absurd rendering is the easy case to notice and therefore the easy case
    to leave unfixed: the guard must key on the START being unrecorded, never on whether the
    resulting age happens to look silly.
    """
    phrase = prc._episode_phrase(0, 3, now=REAL_WEDGE)
    assert UNRECORDED in phrase, phrase
    assert "1970" not in phrase, phrase


def test_a_negative_start_time_is_refused_too():
    """Keyed to the PROPERTY (a start time is a positive instant), not to the observed value 0."""
    phrase = prc._episode_phrase(-1.0, 3, now=REAL_WEDGE)
    assert UNRECORDED in phrase, phrase
    assert "1969" not in phrase and "1970" not in phrase, phrase


def test_a_real_start_time_still_names_its_date_and_age():
    """REACHABILITY / null control -- assert the reporting branch CAN still be taken.

    Without this, `return UNRECORDED` unconditionally satisfies every assertion above while
    silently blinding every real episode the alarm exists to describe. That is this project's
    most-repeated control failure and it gets its own leg, not a comment.
    """
    phrase = prc._episode_phrase(REAL_WEDGE, 8, now=REAL_WEDGE + 7 * 3600)

    assert UNRECORDED not in phrase, phrase
    assert "7h00m" in phrase, phrase
    assert "8" in phrase


def test_the_whole_partition_is_reachable():
    """ONE control over the whole partition, per CLAUDE.md: a guard that refuses EVERYTHING
    passes every 'does it refuse correctly' leg above. This asserts the three outcomes are
    distinct and each attainable, so the refusing branch cannot swallow the reporting one."""
    unrecorded = prc._episode_phrase(None, 3, now=REAL_WEDGE)
    zeroed = prc._episode_phrase(0, 3, now=REAL_WEDGE)
    reported = prc._episode_phrase(REAL_WEDGE, 3, now=REAL_WEDGE + 3600)

    assert UNRECORDED in unrecorded and UNRECORDED in zeroed
    assert UNRECORDED not in reported
    assert unrecorded == zeroed, (
        "a recorded-as-zero start reads differently from an unrecorded one -- the reader can "
        "tell apart two states that are the same fact")


# --------------------------------------------------------------------------- #
# The surface: the sentence that actually reached the director
# --------------------------------------------------------------------------- #
def _wedged_state(wedge_since, now):
    """A three-failure open episode ending at `now`, carrying `wedge_since` verbatim."""
    return json.dumps({
        "failures": [{"ts": float(now - 1800 + t), "reason": "rc=1 on a marker", "rc": 1,
                      "kind": "test_regression", "git_hash": "abc1234"}
                     for t in (0, 600, 1200)],
        "alerted_at": None, "wedge_since": wedge_since, "episode_failures": 3,
    })


def test_a_persisted_zero_does_not_reach_the_alarm_text():
    """END TO END, in the exact shape observed, and now closed one level EARLIER than it was.

    When this file was written the writer ADOPTED the persisted zero and the renderer was the last
    thing standing. It is not any more (see the restamp legs below), so this leg asserts the
    OUTCOME rather than which layer produced it: whatever the state file carries, no epoch date
    reaches the director. That is the property; which layer catches it is an implementation detail
    and pinning it here would be keying a control to today's answer.

    Driven through the real writer, on a REAL clock -- the original used `now=1800`, so an honest
    restamp of a fake clock rendered an honest `1970-01-01T00:30` and the leg failed for a reason
    that had nothing to do with the defect. A fixture's clock has to be a possible clock.
    """
    prc.PUBLISH_GATE_STATE_FILE.write_text(_wedged_state(0.0, REAL_WEDGE))
    sink = _Sink()

    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, git_hash="abc1234",
                                    now=REAL_WEDGE, send_ntfy_fn=sink)

    assert sink.messages, "premise: the alarm must have fired, or this control proves nothing"
    msg = sink.messages[-1]
    assert "1970" not in msg, (
        f"the epoch date reached the alarm the director reads: {msg}")


# --------------------------------------------------------------------------- #
# The writer: a zero must not SURVIVE in the state file either
# --------------------------------------------------------------------------- #
# The renderer above stops the bad value being READ. It does nothing about the bad value being
# KEPT, and `.publish_gate_state.json` has other consumers -- `supervisor.
# _publish_gate_wedge_active` reads `wedge_since` with its own `isinstance` test and would date a
# wedge to 1970, i.e. always older than any threshold. Every new consumer inherits it until the
# writer stops persisting it.
#
# MEASURED, NOT ASSUMED, and the finding that filed this got it wrong: the blocker was never the
# pinned fixture in `test_publish_gate_blocking_payload`. Repairing the adoption clause alone left
# `persisted["wedge_since"] == 0.0` exactly as it was, because `episode_monotonic.guard_episode`
# treats the start as LOW-water and `0.0 <= anything` wins forever. Two changes are load-bearing
# and each is dead without the other. Pre-registered before the run:
# docs/staging/records/PREREG_WHETHER_THE_FIXTURE_PIN_IS_ACTUALLY_THE_BLOCKER_ON_THE_ZERO_ADOPTION_2026-09-04.md

def _persisted_after_failure(wedge_since, now=REAL_WEDGE):
    prc.PUBLISH_GATE_STATE_FILE.write_text(_wedged_state(wedge_since, now))
    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, git_hash="abc1234",
                                    now=now, send_ntfy_fn=_Sink())
    return json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())["wedge_since"]


def test_a_persisted_zero_is_restamped_rather_than_adopted():
    """THE DEFECT. `wedge_since = prev if isinstance(prev, (int, float)) else now` accepted 0."""
    assert _persisted_after_failure(0.0) == REAL_WEDGE, (
        "the zero survived the write -- it is now this episode's permanent start, and every "
        "consumer of the state file inherits a 1970 nobody recorded")


def test_a_persisted_negative_is_restamped_too():
    """Keyed to the PROPERTY -- a start is a positive instant -- not to the observed value 0."""
    assert _persisted_after_failure(-1.0) == REAL_WEDGE


def test_a_persisted_true_is_not_a_start_time():
    """`True` is an int and `True > 0`, so a bare positivity test would adopt it as epoch+1s.
    `episode_monotonic._is_num` already refuses bools for exactly this reason; the writer's own
    screen must agree with the guard's, or the two disagree about what a start is."""
    assert _persisted_after_failure(True) == REAL_WEDGE


def test_a_real_persisted_start_is_still_remembered():
    """REACHABILITY / null control, and the one that matters most here.

    `wedge_since = now` unconditionally passes all three legs above and DELETES the PW2 episode
    guarantee -- every failure would restamp the clock and a 10h outage would page as a fresh
    minute, which is the 2026-08-09 defect the whole monotonic guard exists to cure. Restamping
    must be reachable ONLY for values that were never start times.
    """
    real_start = REAL_WEDGE - 7 * 3600
    assert _persisted_after_failure(real_start) == real_start, (
        "a real episode start was restamped to now -- the episode clock is forwardable again")


def test_the_whole_writer_partition_is_reachable():
    """ONE control over the partition: restamped and remembered must be DIFFERENT outcomes."""
    restamped = _persisted_after_failure(0.0)
    remembered = _persisted_after_failure(REAL_WEDGE - 7 * 3600)
    cold = _persisted_after_failure(None)

    assert restamped == cold == REAL_WEDGE
    assert remembered != restamped


def test_the_alarm_text_reports_the_open_episodes_real_age_not_a_fresh_one():
    """FOUND BY MUTATION, and it was a MISSING TEST rather than an equivalence (2026-09-04).

    Replacing the writer's whole adoption clause with `wedge_since = now` left all ten legs above
    GREEN, because the PERSISTED field has a second guard: `episode_monotonic.guard_episode` is
    LOW-water and restores the real start. So the state file is protected twice.

    THE ALARM TEXT IS PROTECTED ONCE. `_episode_phrase` is handed the writer's LOCAL variable, not
    the guarded persisted one, so under that mutation a seven-hour wedge pages as:

        EPISODE: wedged since 2027-01-15T08:00 UTC -- 0h00m and 4 consecutive failures

    That is the 2026-08-09 defect verbatim -- a 10h26m outage reading as 14 minutes -- on the one
    path where a person acts on the number, and every control in this repository walked past it.
    The legs above assert what is WRITTEN; this one asserts what is SENT, and they are different
    values from different variables.
    """
    start = REAL_WEDGE - 7 * 3600
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps({
        # The failures sit inside the 1h trim window; the episode START is seven hours older.
        # That gap IS the subject: it is the only thing `wedge_since` exists to carry.
        "failures": [{"ts": REAL_WEDGE - t, "reason": "rc=1 on a marker", "rc": 1,
                      "kind": "test_regression", "git_hash": "abc1234"}
                     for t in (1500, 900, 300)],
        "alerted_at": None, "wedge_since": start, "episode_failures": 3,
    }))
    sink = _Sink()

    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, git_hash="abc1234",
                                    now=REAL_WEDGE, send_ntfy_fn=sink)

    assert sink.messages, "premise: the alarm must have fired, or this control proves nothing"
    msg = sink.messages[-1]
    assert "7h00m" in msg, (
        "the alarm reported a FRESH episode inside a seven-hour-old one -- the writer restamped "
        f"the local start the phrase is built from: {msg}")
    assert "0h00m" not in msg, msg
