"""The publish failure count survives every episode close except a publish that reached origin.

THE DEFECT (2026-10-05). `episode_failures` resets whenever an episode closes, and an episode closes
on things that are not a publish: a cause re-asked and found cleared, a green gate over nothing, and
a deferred delivery from a week earlier graded REACHED. That last one stamped `last_clean_publish`
at 04:28Z on 2026-10-05 and restarted the streak, so the record read one failure, two hours old,
while the figures on origin dated from 2026-09-28T04:46Z.

ONE PARTITION CONTROL over the record, driven through the real writers: a failure counts, an
episode close that is not a landing does NOT reset it, and a landing does. A writer that reset on
the close, or never reset at all, reds the final assert.

MUTATIONS, RUN 2026-10-05, all red:
  * a moved landing keeps the prior count instead of resetting to 0 -> 2 red.
  * `failure=True` dropped from `record_publish_gate_failure`'s write -> 1 red.
  * the anchored branch skipped, so every write re-seeds from `episode_failures` (the old
    per-episode key) -> 3 red.
"""
from __future__ import annotations

import json

import pytest

import background.process_run_complete as prc

T0 = 1_800_000_000.0
LANDED = T0 - 7 * 86400


@pytest.fixture
def gate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    origin = {"ts": LANDED}
    monkeypatch.setattr(prc, "_landed_publish_ts", lambda: origin["ts"])
    return tmp_path / ".publish_gate_state.json", origin


def _refuse(now):
    prc.record_publish_gate_failure(
        "the publish COMMIT did not land", rc=77, git_hash="abc123def", now=now,
        kind="commit_did_not_land", cause="behind_origin", cause_evidence="origin is 3 AHEAD",
        send_ntfy_fn=lambda *a, **k: None)


def _read(path):
    st = json.loads(path.read_text())
    return st["last_landed_publish"], st["failures_since_landed_publish"]


def test_only_a_landed_publish_resets_the_count(gate):
    path, origin = gate
    seen = {}

    _refuse(T0)
    _refuse(T0 + 60)
    seen["counted"] = _read(path)

    # Not a landing: the episode closes because its cause re-asks as cleared.
    assert prc.close_episode_if_cause_cleared(now=T0 + 120, fork_fn=lambda: (0, 0)) == "cleared"
    _refuse(T0 + 180)
    seen["closed"] = _read(path)

    # A landing: git's date for the figures on origin moves.
    origin["ts"] = T0 + 200
    _refuse(T0 + 240)
    seen["landed"] = _read(path)

    assert seen == {"counted": (LANDED, 2), "closed": (LANDED, 3), "landed": (T0 + 200, 1)}


def test_the_first_write_seeds_only_from_an_episode_that_began_after_the_landing():
    after = {"wedge_since": LANDED + 10, "episode_failures": 2}
    before = {"wedge_since": LANDED - 10, "episode_failures": 2}
    assert prc.landed_publish_count({}, after, failure=False, landed=LANDED) == (LANDED, 2)
    # Failures over a span nobody counted are not a count, and stay None until a landing.
    assert prc.landed_publish_count({}, before, failure=True, landed=LANDED) == (LANDED, None)
    unknown = {"last_landed_publish": LANDED, "failures_since_landed_publish": None}
    assert prc.landed_publish_count(unknown, {}, failure=True, landed=LANDED) == (LANDED, None)
    assert prc.landed_publish_count(unknown, {}, failure=True, landed=LANDED + 5) == (LANDED + 5, 1)


def test_an_unreadable_origin_keeps_the_anchor_and_never_resets():
    prior = {"last_landed_publish": LANDED, "failures_since_landed_publish": 4}
    assert prc.landed_publish_count(prior, {}, failure=True, landed=None) == (LANDED, 5)
