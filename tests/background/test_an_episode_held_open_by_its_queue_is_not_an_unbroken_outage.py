"""A clean publish INSIDE an open wedge episode must be recorded, and must change the sentence.

THE INCIDENT (2026-09-04). `docs/observability/.publish_gate_state.json` read `wedge_since`
2026-09-04T05:57Z and `episode_failures: 8`, and `_episode_phrase` rendered that as

    EPISODE: wedged since 2026-09-04T05:57 UTC -- 5h37m and 8 consecutive failures in THIS
    episode (not a fresh hour).

`docs/observability/sim-runner-log.md` records "Publish gate recovered" at 02:22Z, 05:20Z and
**10:53Z** — the last of those forty minutes before the reading. They were not consecutive: a
clean publish sat among them. A delivery turn opened on "the path has been down about four hours"
and the path had published forty minutes earlier.

NOTHING WAS LYING AND THAT IS THE POINT. `record_publish_gate_success` preserves the episode
fields when markers are still pending, and that is correct and load-bearing (PW2, 2026-08-09: a
success that drains nothing may not close an episode, or a 10h26m outage pages as a fresh 14
minutes). The defect is that the state carried NO field for "the gate passed inside this episode",
so two different faults rendered as one sentence:

  * THE GATE CANNOT PASS -> fix the red.
  * THE GATE PASSES AND ITS QUEUE OUTRUNS IT -> a ~45-min cycle against a marker every ~13 min,
    so `pending == 0` is never observed at a success instant and the episode can never close.
    Fixing reds will never close this one.

MUTATION SENSITIVITY (R15) — each proven by reverting the fix, not asserted:
  * drop `episode_clean_publishes`/`last_clean_publish` from `record_publish_gate_success`'s
    write -> `test_a_clean_publish_inside_an_open_episode_is_recorded` red.
  * drop the `last_clean_publish` carry from `_write_publish_gate_state` (or remove
    `episode_clean_publishes` from PUBLISH_GATE_STREAK_FIELDS) ->
    `test_the_next_failure_cannot_forget_the_publish_that_happened` red.
  * restore the single unconditional "consecutive failures" phrase ->
    `test_the_alarm_stops_calling_a_broken_streak_consecutive` red.
  * make the new branch unconditional (delete the `clean_publishes > 0` test) ->
    `test_a_genuinely_unbroken_outage_still_reads_as_one` red. THIS IS THE NULL CONTROL: without
    it, deleting the word "consecutive" everywhere would pass every other test in this file while
    destroying the distinction the file exists to draw.
  * pass `episode_closed=True` on a drained queue without clearing -> `test_draining_the_queue_
    to_zero_closes_the_episode_and_forgets_the_publishes` red.

TWO OF THOSE MUTATIONS FIRST SURVIVED, and the reason is recorded here rather than quietly fixed.
The failure write originally ALSO passed both fields explicitly, read from the prior state. That
duplicated the two real mechanisms — the `episode_monotonic` class guard for the counter, and the
carry-through in `_write_publish_gate_state` for the timestamp — so deleting EITHER real mechanism
left all seven controls green. Not a missing test: an equivalence, and one that made both
safeguards unprovable. The duplicate is gone and each mechanism is now the only thing holding its
field, which is what makes the two mutations above fire at all.
"""
from __future__ import annotations

import json

import pytest

import background.process_run_complete as prc

T0 = 1_800_000_000.0


@pytest.fixture
def gate(tmp_path, monkeypatch):
    """A real state file and a real staging directory — the queue is the independent evidence."""
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    return tmp_path, staging


def _queue(staging, n):
    """n unpublished run_complete markers, exactly as the sim runner leaves them."""
    for existing in staging.glob("run_complete_*.md"):
        existing.unlink()
    for i in range(n):
        (staging / "run_complete_2026090{}T00000{}Z.md".format(i % 9, i % 9)).write_text("x\n")


def _state(tmp_path):
    return json.loads((tmp_path / ".publish_gate_state.json").read_text())


def _open_an_episode(staging, failures=8, start=T0):
    """The real shape: a streak of reds with markers piling up behind them."""
    _queue(staging, failures)
    for i in range(failures):
        prc.record_publish_gate_failure(
            "rc=1 marker {}".format(i), rc=1, git_hash="abc123def",
            now=start + i * 600, send_ntfy_fn=lambda *a, **k: None)


# ── the state must carry the fact at all ────────────────────────────────────────────────

def test_a_clean_publish_inside_an_open_episode_is_recorded(gate):
    tmp_path, staging = gate
    _open_an_episode(staging)
    assert _state(tmp_path)["wedge_since"] == T0, "premise: the episode is open"

    # The 10:53Z shape: the gate passes, publishes, and markers minted during the ~45-minute
    # cycle are still queued behind it.
    _queue(staging, 8)
    prc.record_publish_gate_success(now=T0 + 5 * 3600)

    st = _state(tmp_path)
    assert st["episode_clean_publishes"] == 1, (
        "a clean publish inside the episode left no trace in the state file — this is the "
        "2026-09-04 reading, where nothing downstream could tell a wedge from a backlog"
    )
    assert st["last_clean_publish"] == T0 + 5 * 3600
    # ...and the PW2 guard is untouched: the episode itself must NOT have been closed.
    assert st["wedge_since"] == T0, "a success that drained nothing closed the episode (PW2)"
    assert st["episode_failures"] == 8


def test_the_next_failure_cannot_forget_the_publish_that_happened(gate):
    """A failure knows nothing about publishes and must not be able to erase one.

    This is the field's whole working life: the alarm fires on a FAILURE write, so if the red
    that follows the publish drops the evidence, the sentence is wrong exactly when it is read.
    """
    tmp_path, staging = gate
    _open_an_episode(staging)
    _queue(staging, 8)
    prc.record_publish_gate_success(now=T0 + 5 * 3600)

    prc.record_publish_gate_failure("rc=1 the next red", rc=1, git_hash="deadbeef1",
                                    now=T0 + 5.5 * 3600, send_ntfy_fn=lambda *a, **k: None)

    st = _state(tmp_path)
    assert st["episode_clean_publishes"] == 1, (
        "the failure write forgot the clean publish — the alarm that fires on this very write "
        "is then back to claiming an unbroken outage"
    )
    assert st["last_clean_publish"] == T0 + 5 * 3600


def test_draining_the_queue_to_zero_closes_the_episode_and_forgets_the_publishes(gate):
    """The null control for the memory: episode-scoped means it MUST reset on a real close.

    A field that only ever accumulates would make every later episode read as intermittent.
    """
    tmp_path, staging = gate
    _open_an_episode(staging)
    _queue(staging, 8)
    prc.record_publish_gate_success(now=T0 + 5 * 3600)
    assert _state(tmp_path)["episode_clean_publishes"] == 1, "premise"

    _queue(staging, 0)  # the queue really drained — the evidenced close
    prc.record_publish_gate_success(now=T0 + 6 * 3600)

    st = _state(tmp_path)
    assert st["wedge_since"] is None and st["episode_failures"] == 0, "premise: episode closed"
    assert st["episode_clean_publishes"] == 0, "the memory outlived the episode it was scoped to"
    assert st["last_clean_publish"] is None


# ── the sentence the director actually reads ────────────────────────────────────────────

def test_the_alarm_stops_calling_a_broken_streak_consecutive(gate):
    """THE named defect, on the real recorded numbers rather than an invented shape."""
    phrase = prc._episode_phrase(T0, 8, T0 + 5 * 3600 + 37 * 60,
                                 clean_publishes=1, last_clean_publish=T0 + 5 * 3600)

    assert "consecutive" not in phrase, (
        "the alarm still calls them consecutive failures while a clean publish sits among "
        "them: {}".format(phrase)
    )
    assert "clean publish" in phrase, "the publish that broke the streak is not mentioned"
    assert "THROUGHPUT" in phrase, (
        "the reader is not told which of the two faults this is, so the remedy is a guess — "
        "and fixing a red cannot close a throughput episode"
    )
    # The fact that lets a reader check it against the log, not just believe the adjective.
    assert "5h00m" in phrase or "5h37m" in phrase, phrase


def test_a_genuinely_unbroken_outage_still_reads_as_one(gate):
    """THE NULL CONTROL (R15 reachability). The old sentence must still be REACHABLE and still
    be used — otherwise "delete the word consecutive" passes this file and the alarm loses the
    ability to say the thing that is true when the gate really cannot pass."""
    phrase = prc._episode_phrase(T0, 8, T0 + 5 * 3600, clean_publishes=0)

    assert "consecutive failures in THIS episode" in phrase, (
        "the unbroken-outage branch is unreachable — every episode now reads as intermittent, "
        "which is the same defect wearing the other coat"
    )
    assert "THROUGHPUT" not in phrase
    # Both branches must be reachable from ONE partition, asserted together (CLAUDE.md: write
    # one control over the whole partition, not a leg per branch).
    intermittent = prc._episode_phrase(T0, 8, T0 + 5 * 3600, clean_publishes=1,
                                       last_clean_publish=T0 + 4 * 3600)
    unrecorded = prc._episode_phrase(None, 8, T0)
    assert ("consecutive" in phrase
            and "THROUGHPUT" in intermittent
            and "unrecorded" in unrecorded), (
        "all three readings must be reachable: unbroken, intermittent, and unknown-start"
    )


def test_an_unrecorded_publish_time_is_declared_not_guessed(gate):
    """FAIL-CLOSED: a count with no timestamp says so rather than implying a fresh publish."""
    phrase = prc._episode_phrase(T0, 8, T0 + 5 * 3600,
                                 clean_publishes=2, last_clean_publish=None)
    assert "time unrecorded" in phrase
    assert "1970" not in phrase, "an absent timestamp rendered as the epoch"


def test_the_alarm_payload_carries_the_distinction_end_to_end(gate):
    """The seam, not just the helper: the fields must reach the NTFY body the director reads.

    A helper that renders correctly while the caller passes nothing is this project's
    unwired-module shape, and it would leave the live alarm exactly as wrong as it was.
    """
    tmp_path, staging = gate
    sent = []
    _open_an_episode(staging)
    _queue(staging, 8)
    prc.record_publish_gate_success(now=T0 + 5 * 3600)

    # Enough failures after the publish to re-arm and fire the alarm.
    for i in range(prc.PUBLISH_GATE_FAILURE_THRESHOLD + 1):
        prc.record_publish_gate_failure(
            "rc=1 post-publish red {}".format(i), rc=1, git_hash="deadbeef1",
            now=T0 + 6 * 3600 + i * 600, send_ntfy_fn=lambda *a, **k: sent.append(a))

    assert sent, "no alarm fired, so this proves nothing about the payload"
    body = " ".join(str(part) for part in sent[-1])
    assert "clean publish" in body and "THROUGHPUT" in body, (
        "the alarm body still describes an unbroken outage: {}".format(body)
    )
