"""Figures publish once a week, from Monday 04:00 London -- a schedule, not a sentence.

Director, 2026-09-26: *"weekly publishing isn't in effect ... Make it real, and anchor it to Monday
rather than a rolling seven days."* `publish_freshness.PUBLISH_CADENCE_SECONDS` had declared a
weekly cadence since 2026-09-04 and nothing read it as a schedule: the publisher committed figures
after every sim run, six times between Fri 09-25 afternoon and Sat 09-26 morning.

The window is a guard that exists to be taken most of the week and NOT taken on Monday, so the
first control is over the whole partition: both verdicts, and the owed-past-Monday case, must be
reachable before anything is asserted about what each does.
"""

import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import background.process_run_complete as prc
from background import publish_freshness as pf

LONDON = ZoneInfo("Europe/London")


def _t(s):
    return datetime.fromisoformat(s).replace(tzinfo=LONDON).timestamp()


def _window(now, last):
    return pf.content_publish_window(_t(now), published_ts_fn=lambda: None if last is None else _t(last))


def test_every_verdict_of_the_window_is_reachable():
    """MUTATION: make the window always open, or always closed, and this reds."""
    closed = _window("2026-09-30 10:00", "2026-09-28 05:10")   # published this Monday
    monday = _window("2026-09-28 04:30", "2026-09-27 12:32")   # Monday, last week's figures
    owed = _window("2026-09-30 10:00", "2026-09-27 12:32")     # Monday's publish never landed
    assert not closed["open"] and monday["open"] and owed["open"]


@pytest.mark.parametrize("now, week_start", [
    ("2026-09-27 16:00", "2026-09-21T04:00:00+01:00"),  # Sunday belongs to the week begun Monday
    ("2026-09-28 03:59", "2026-09-21T04:00:00+01:00"),  # Monday before the reset: still last week
    ("2026-09-28 04:00", "2026-09-28T04:00:00+01:00"),
    ("2026-10-26 05:00", "2026-10-26T04:00:00+00:00"),  # first Monday after the clocks go back
])
def test_the_week_starts_at_monday_0400_london_not_seven_days_ago(now, week_start):
    """MUTATION: anchor to `now - 7 days` (the rolling week the director ruled out) and the
    Sunday and Monday-03:59 rows red; drop the hour and the 03:59 row reds."""
    assert pf.publish_week_start(_t(now)).isoformat() == week_start


def test_a_publish_later_in_the_week_does_not_move_the_anchor():
    """A Wednesday catch-up publish closes THAT week; the next window is still Monday."""
    w = _window("2026-10-01 12:00", "2026-09-30 11:00")
    assert not w["open"]
    assert w["next_opens"] == "2026-10-05T04:00:00+01:00"


def test_an_unknown_publish_time_opens_the_window_and_says_why():
    """Fail-open by decision: skipping the week silently costs more than publishing once too often."""
    w = _window("2026-09-30 10:00", None)
    assert w["open"] and "unknown" in w["reason"]


# ── the publisher honours it ─────────────────────────────────────────────────────────────────


@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "done")
    monkeypatch.setattr(prc, "_record_archived_marker", lambda dest: None)
    liveness = []
    monkeypatch.setattr(prc, "_refresh_published_liveness_on_skip", liveness.append)
    regenerated = []

    def _stop(json_path):  # the first step of a real publish; reaching it is the observation
        regenerated.append(json_path)
        return False

    monkeypatch.setattr(prc, "regenerate_report", _stop)

    def _make(window_open, administration_event=False):
        monkeypatch.setattr(prc, "_content_publish_window",
                            lambda: {"open": window_open, "reason": "test"})
        out = tmp_path / "run_output.json"
        out.write_text(json.dumps({"total_net_gbp": 1.0,
                                   "administration_event": administration_event}))
        marker = tmp_path / "staging" / "run_complete_20260930T090000Z.md"
        marker.parent.mkdir(exist_ok=True)
        marker.write_text("Simulation Run Complete\n\nGit: abc1234\nJSON: {}\n".format(out))
        rc = prc._process(str(marker))
        return rc, marker, regenerated, liveness

    return _make


def test_outside_the_window_nothing_is_regenerated_or_committed(run):
    """MUTATION: delete the window gate in `_process` and this reds -- the report regenerates."""
    rc, marker, regenerated, liveness = run(window_open=False)
    assert regenerated == []
    assert rc == prc.EXIT_NOTHING_PUBLISHED, "a hold published nothing and must say so, not rc=0"
    assert not marker.exists() and (prc.DONE_DIR / marker.name).exists(), (
        "a held marker must be archived, or the backlog grows all week and reads as a wedge")
    assert liveness == ["abc1234"], "liveness is not content and must keep flowing"


def test_inside_the_window_the_publish_proceeds(run):
    """BOTH WAYS: a gate that holds everything passes the test above."""
    _rc, _marker, regenerated, _ = run(window_open=True)
    assert len(regenerated) == 1


def test_an_administration_event_is_never_held(run):
    """Its NTFY path is why it bypasses the change-detection gate; the window may not hold it either."""
    _rc, _marker, regenerated, _ = run(window_open=False, administration_event=True)
    assert len(regenerated) == 1


def test_the_live_seam_asks_the_real_window(monkeypatch):
    """The conftest default opens `_content_publish_window`; this proves the seam it replaces
    reaches `publish_freshness` and is not itself a stub."""
    monkeypatch.undo()
    seen = []
    monkeypatch.setattr(pf, "content_publish_window", lambda: seen.append(1) or {"open": False})
    assert prc._content_publish_window() == {"open": False} and seen == [1]
