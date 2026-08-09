"""PW2 -- R15 on the episode guard: it must FIRE on its own named defect, and stay silent otherwise.

The named defect (director, DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09): a check's failure
path writes the state its own alarm reads, so the failure shortens the episode it is about to be
measured by. The headline test here is `test_replays_20260809_and_reports_the_real_episode`, which
replays the actual recorded sequence and asserts the alarm would now say ~10h, not ~14min.

Both directions, per R15:
  * FIRES  -- the guard changes the reported episode on the real 2026-08-09 sequence.
  * SILENT -- it never lengthens an episode beyond the evidence, and an evidenced close still
              closes (a guard that could only refuse to clear would wedge the alarm permanently,
              which is the always-red failure mode: as ignored as a blind one).
"""
from __future__ import annotations

import json

import pytest

from background.episode_monotonic import episode_age_seconds, guard_episode

# The two REAL recorded anchors of the 2026-08-09 publish outage.
#   04:03:22Z -- `wedge_since` in .publish_gate_state.json, quoted mid-episode in
#                docs/staging/WORKER_FINDING_EPISODE_MEMORY_WIPED_MID_EPISODE_2026-08-09.md
#   14:30:09Z -- `wedge_since` of the LAST fresh episode the wipe manufactured, read off the live
#                state file during the PW2 build.
# The span between them is the episode the director called "~10h"; the alarm reported the tail.
EPISODE_START = 1786248202.8       # 2026-08-09T04:03:22Z
LAST_FRESH_START = 1786285809.38   # 2026-08-09T14:30:09Z
ALARM_AT = LAST_FRESH_START + 14 * 60   # the 14-minute reading the alarm actually gave

SINCE = ("wedge_since",)
STREAK = ("episode_failures",)


def _failure_write(prev, now, n):
    """One failure round, exactly as record_publish_gate_failure composes it."""
    return guard_episode(prev, {"wedge_since": now, "episode_failures": n},
                         since_fields=SINCE, streak_fields=STREAK, episode_closed=False)


def _unevidenced_clear(prev):
    """The 'Publish gate recovered' write that published nothing -- the defect's actual mechanism.
    Four of these are in docs/observability/sim-runner-log.md for 2026-08-09 alone (13:30, 13:56,
    14:23, and the 04:54 one the worker finding caught), each followed within minutes by
    'Publish-gate failure #1' -- the counter restarting at one is the wipe made visible."""
    return guard_episode(prev, {"wedge_since": None, "episode_failures": 0},
                         since_fields=SINCE, streak_fields=STREAK, episode_closed=False)


# --------------------------------------------------------------------------- FIRES

def test_replays_20260809_and_reports_the_real_episode():
    """THE named defect. Replay the observed clear-and-refail cycle across the whole outage and
    assert the reported episode is the real ~10h26m, not the ~14min the alarm gave."""
    state = {"wedge_since": EPISODE_START, "episode_failures": 1}
    # The outage as the log records it: rounds of failures, punctuated by 'recovered' writes that
    # published nothing, right through to the last fresh episode at 14:30:09Z.
    t = EPISODE_START
    n = 1
    while t < LAST_FRESH_START:
        t += 5 * 60
        n += 1
        state = _failure_write(state, t, n)
        if n % 4 == 0:                      # the periodic unevidenced 'recovered' write
            state = _unevidenced_clear(state)
    state = _failure_write(state, LAST_FRESH_START, n + 1)

    age_h = episode_age_seconds(state, "wedge_since", ALARM_AT) / 3600.0
    assert 10.0 < age_h < 11.0, f"expected the real ~10h26m episode, got {age_h:.2f}h"
    assert state["wedge_since"] == pytest.approx(EPISODE_START), \
        "the episode start moved -- a failure shortened its own episode"


def test_without_the_guard_the_same_replay_reports_fourteen_minutes():
    """THE MUTATION (R15). Same sequence, guard removed -- the last write wins, and the alarm
    reports the fresh tail. If this ever stops showing ~14min, the replay above has stopped
    reproducing the defect and its pass means nothing."""
    state = {"wedge_since": EPISODE_START, "episode_failures": 1}
    t, n = EPISODE_START, 1
    while t < LAST_FRESH_START:
        t += 5 * 60
        n += 1
        state = {"wedge_since": t, "episode_failures": n}       # unguarded
        if n % 4 == 0:
            state = {"wedge_since": None, "episode_failures": 0}
    state = {"wedge_since": LAST_FRESH_START, "episode_failures": n + 1}

    age_min = episode_age_seconds(state, "wedge_since", ALARM_AT) / 60.0
    assert 13 < age_min < 15, f"the unguarded replay should report ~14min, got {age_min:.1f}min"


def test_a_failure_cannot_move_the_start_forward():
    out = _failure_write({"wedge_since": 1000.0, "episode_failures": 3}, 9999.0, 1)
    assert out["wedge_since"] == 1000.0
    assert out["episode_failures"] == 3, "the streak counter went backwards"


def test_a_failure_cannot_clear_an_open_episode():
    assert _unevidenced_clear({"wedge_since": 1000.0, "episode_failures": 7}) == {
        "wedge_since": 1000.0, "episode_failures": 7}


def test_bool_is_not_a_timestamp():
    """`True` is an int in Python; through an unguarded min() it becomes 1 -- epoch 1970, which
    would report a 56-year episode and read as obvious nonsense on the phone."""
    out = guard_episode({"wedge_since": True}, {"wedge_since": 5000.0}, since_fields=SINCE)
    assert out["wedge_since"] == 5000.0


# --------------------------------------------------------------------------- SILENT

def test_an_evidenced_close_still_clears():
    """A guard that could only refuse to clear would pin the alarm permanently red -- and an
    always-red detector is as ignored as a blind one. The evidenced close must work."""
    out = guard_episode({"wedge_since": 1000.0, "episode_failures": 9},
                        {"wedge_since": None, "episode_failures": 0},
                        since_fields=SINCE, streak_fields=STREAK, episode_closed=True)
    assert out == {"wedge_since": None, "episode_failures": 0}


def test_an_earlier_start_is_accepted():
    """Monotonic means low-water, not frozen: evidence that the episode began EARLIER is the one
    direction that is never under-reporting."""
    out = _failure_write({"wedge_since": 5000.0, "episode_failures": 1}, 1000.0, 2)
    assert out["wedge_since"] == 1000.0


def test_no_open_episode_means_the_new_write_stands():
    out = _failure_write({"wedge_since": None, "episode_failures": 0}, 4242.0, 1)
    assert out["wedge_since"] == 4242.0 and out["episode_failures"] == 1


def test_a_missing_or_corrupt_prior_never_shortens_and_never_raises():
    """Fail toward remembering: an unreadable prior degrades to today's behaviour, not a crash in
    the pipeline this monitors."""
    for prev in (None, {}, "not-a-mapping", 17):
        out = guard_episode(prev, {"wedge_since": 77.0, "episode_failures": 2},
                            since_fields=SINCE, streak_fields=STREAK)
        assert out["wedge_since"] == 77.0

    assert episode_age_seconds({}, "wedge_since", 100.0) is None
    assert episode_age_seconds({"wedge_since": "nope"}, "wedge_since", 100.0) is None


def test_untouched_fields_pass_through():
    out = guard_episode({"wedge_since": 1.0}, {"wedge_since": 2.0, "cited_findings": ["a.md"]},
                        since_fields=SINCE)
    assert out["cited_findings"] == ["a.md"]


# --------------------------------------------------------------------------- WIRED, not just built

def test_the_publish_gate_actually_uses_the_guard(tmp_path, monkeypatch):
    """MAKE_IT_STICK: a guard that exists but is not on the write path is prose. Drive the real
    `record_publish_gate_failure` and prove a second failure cannot restart the episode."""
    import background.process_run_complete as prc

    state_file = tmp_path / ".publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state_file)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path)

    prc.record_publish_gate_failure("first", rc=1, now=1000.0, send_ntfy_fn=lambda m: "id")
    prc.record_publish_gate_failure("second", rc=1, now=40000.0, send_ntfy_fn=lambda m: "id")

    state = json.loads(state_file.read_text())
    assert state["wedge_since"] == 1000.0, "the second failure restarted the episode clock"
    assert state["episode_failures"] == 2


def test_an_unevidenced_success_preserves_the_episode_but_clears_the_alarm(tmp_path, monkeypatch):
    """The exact 2026-08-09 mechanism, end to end: 'recovered' with markers STILL QUEUED must not
    zero the episode -- while still clearing `failures`, so no phantom rung-1 draw fires."""
    import background.process_run_complete as prc

    state_file = tmp_path / ".publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state_file)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path)
    (tmp_path / "run_complete_20260809T141527Z.md").write_text("still queued")

    prc.record_publish_gate_failure("first", rc=1, now=1000.0, send_ntfy_fn=lambda m: "id")
    prc.record_publish_gate_success(now=2000.0)

    state = json.loads(state_file.read_text())
    assert state["wedge_since"] == 1000.0, "an unevidenced 'recovery' wiped the episode"
    assert state["failures"] == [] and state["alerted_at"] is None, \
        "the alarm must still re-arm -- an always-red gate is as ignored as a blind one"


def test_a_drained_queue_does_close_the_episode(tmp_path, monkeypatch):
    """The other direction: markers drained IS the evidence, and the episode must genuinely end."""
    import background.process_run_complete as prc

    state_file = tmp_path / ".publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", state_file)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path)

    prc.record_publish_gate_failure("first", rc=1, now=1000.0, send_ntfy_fn=lambda m: "id")
    prc.record_publish_gate_success(now=2000.0)

    state = json.loads(state_file.read_text())
    assert state["wedge_since"] is None and state["episode_failures"] == 0
