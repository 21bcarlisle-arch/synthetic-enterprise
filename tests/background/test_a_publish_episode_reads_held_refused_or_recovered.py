"""Held, refused and recovered are three readings, each reachable, and a cleared cause closes.

THE DEFECT (2026-09-28). An episode opened on `behind_origin` could only be closed by a clean
publish with the queue drained. Inside a closed weekly window no publish is attempted, so the
surface read FAILING for ~12h on a cause that had already cleared: a real refusal and a stale one
looked identical, and a hold was invisible.

ONE PARTITION CONTROL. The reading of the same state file, driven through the real writers, must
take all three values and they must be distinct. A reader that collapsed any two -- or a closer
that never fired, leaving every path on `failing` -- reds the final assert.

MUTATIONS, RUN 2026-09-28, both red:
  * `recorded_cause_standing` returns `"holds"` where it returns `"cleared"` (the old behaviour:
    the recorded refusal is believed, never re-asked) -> red at the recovered arm's close.
  * `publisher_refusal` maps a hold to `no_open_episode` (the old two-word vocabulary) -> red at
    the partition assert, `{'held': 'no_open_episode', ...}`.
"""
from __future__ import annotations

import pytest

import background.process_run_complete as prc
from background import publish_cause, publish_freshness

T0 = 1_800_000_000.0


@pytest.fixture
def gate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    return tmp_path / ".publish_gate_state.json"


def _refuse(cause):
    prc.record_publish_gate_failure(
        "the publish COMMIT did not land", rc=77, git_hash="abc123def", now=T0,
        kind="commit_did_not_land", cause=cause, cause_evidence="origin/main is 2 AHEAD",
        send_ntfy_fn=lambda *a, **k: None)


def _reading(path):
    return publish_freshness.publisher_refusal(now=T0 + 600, path=path)["state"]


def test_held_refused_and_recovered_are_each_reachable_and_distinct(gate):
    readings = {}

    # REFUSED: the recorded cause is re-asked and still holds, so the episode stays open.
    _refuse(publish_cause.BEHIND_ORIGIN)
    assert prc.close_episode_if_cause_cleared(now=T0 + 60, fork_fn=lambda: (2, 2)) == "holds"
    readings["refused"] = _reading(gate)

    # RECOVERED: the next cycle re-asks origin, finds HEAD contains it, and closes by that rule.
    assert prc.close_episode_if_cause_cleared(now=T0 + 120, fork_fn=lambda: (0, 2)) == "cleared"
    readings["recovered"] = _reading(gate)
    closed_by = publish_freshness.publisher_refusal(now=T0 + 600, path=gate)["episode_closed_by"]

    # HELD: the weekly window held the next cycle, and it says when it opens.
    prc.record_publish_hold("this week's figures reached origin", "2026-10-05T04:00:00+01:00",
                            now=T0 + 180)
    readings["held"] = _reading(gate)
    held = publish_freshness.publisher_refusal(now=T0 + 600, path=gate)

    assert readings == {"refused": "failing", "recovered": "recovered", "held": "held"}, readings
    assert closed_by == "cause_cleared", "the close must name the rule, not pass for a publish"
    assert held["hold_next_opens"] == "2026-10-05T04:00:00+01:00"
    assert "HELD by the weekly window" in publish_freshness.describe(
        {"state": "publishing", "published_age_seconds": 3600, "publisher": held})


def test_a_cause_git_cannot_reask_never_closes_the_episode(gate):
    """The fail-closed leg: a red test is not re-askable here, so no fork reading may close it."""
    _refuse(publish_cause.SCOPED_SUITE_RED)
    assert prc.close_episode_if_cause_cleared(now=T0 + 60, fork_fn=lambda: (0, 0)) == "unknown"
    assert _reading(gate) == "failing"
