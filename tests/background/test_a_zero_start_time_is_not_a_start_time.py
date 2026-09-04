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

THE ONE THING NOT FIXED HERE, named rather than left for the reader: `record_publish_gate_failure`
carries the same `isinstance`-accepts-0 shape when it ADOPTS a persisted `wedge_since`, so a zero
that reaches the state file is kept rather than restamped. That is a live control's pinned
behaviour (`test_publish_gate_blocking_payload` asserts `persisted["wedge_since"] == 0.0`), so
changing it is a decision with a cost and not a free repair. Filed as a finding beside this commit.
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
def test_a_persisted_zero_does_not_reach_the_alarm_text(monkeypatch):
    """END TO END, in the exact shape observed: a state file carrying `wedge_since: 0.0` is
    ADOPTED by `record_publish_gate_failure` (its own guard has the same accepts-0 shape), so the
    renderer is the last thing standing between a fixture's zero and the director's page.

    This is the leg that would have caught the live defect, and it is deliberately driven through
    the real writer rather than by calling `_episode_phrase` again.
    """
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps({
        "failures": [{"ts": float(t), "reason": "rc=1 on a marker", "rc": 1,
                      "kind": "test_regression", "git_hash": "abc1234"}
                     for t in (0, 600, 1200)],
        "alerted_at": None, "wedge_since": 0.0, "episode_failures": 3,
    }))
    sink = _Sink()

    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, git_hash="abc1234",
                                    now=1800, send_ntfy_fn=sink)

    assert sink.messages, "premise: the alarm must have fired, or this control proves nothing"
    msg = sink.messages[-1]
    assert "1970" not in msg, (
        f"the epoch date reached the alarm the director reads: {msg}")
    assert UNRECORDED in msg, msg
