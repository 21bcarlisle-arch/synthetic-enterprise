"""Content-publish freshness — the number that tells a frozen site from a live one.

Written from the 2026-08-13 freeze: eighteen hours of `verdict: drew`, a heartbeat landing on
origin every thirty minutes, and a site serving the previous day's figures. Nothing was red.
Every test here is about the property that was missing, not about the tick that was fine.
"""
from __future__ import annotations

import json
import types
from datetime import datetime, timezone

import pytest

from background import publish_freshness as pf


@pytest.fixture(autouse=True)
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(pf, "STATE_FILE", tmp_path / ".last_content_publish.json")
    monkeypatch.setattr(pf, "PROJECT_DIR", tmp_path)


def _git(ct=None, rc=0):
    """A fake `git log -1 --format=%ct` returning `ct` (or failing)."""
    def run(cmd, **kwargs):
        return types.SimpleNamespace(
            returncode=rc, stdout="" if ct is None else f"{ct}\n", stderr="")
    return run


NOW = 1_786_600_000.0


def test_a_fresh_publish_reads_as_publishing():
    pf.record_published(now=NOW - 60)
    snap = pf.snapshot(now=NOW, _run=_git(ct=NOW - 60))
    assert snap["state"] == "publishing"
    assert snap["published_age_seconds"] == 60.0
    assert not pf.is_publishing_down(snap)


# ── SCENARIOS ARE EXPRESSED RELATIVE TO THE CADENCE, NOT IN ABSOLUTE HOURS ───────────────────────
#
# Every incident below was measured under a HALF-HOURLY publishing cadence, where 18 and 20.8 hours
# were self-evidently frozen. On 2026-09-04 the director moved numbers and runs to a WEEKLY cadence
# for cost, so those same absolute figures are now a site doing exactly what it was told.
#
# The PROPERTY each test owns is unchanged and is not about hours: a freeze that EXCEEDS THE
# DECLARED CADENCE reads as stale, a healthy tick cannot make it look fresh, and the verdict quotes
# the clock it rests on. Re-expressing the scenarios against `pf.STALE_AFTER_SECONDS` keeps every
# one of those properties and makes them survive the next cadence change too -- which is the
# difference between a control keyed to a property and one keyed to today's answer.
#
# `FROZEN` is one hour past whatever the current threshold is; `WELL_FROZEN` is a day past it.
FROZEN = pf.STALE_AFTER_SECONDS + 3600
WELL_FROZEN = pf.STALE_AFTER_SECONDS + 24 * 3600


def test_the_eighteen_hour_freeze_reads_as_stale():
    """The incident itself, as a measurement: the last verified publish is 18h old.

    MUTATION: widen STALE_AFTER_SECONDS past 18h, or make `snapshot` read the TICK's clock
    instead of the publish clock, and this fails.
    """
    pf.record_published(now=NOW - FROZEN)
    snap = pf.snapshot(now=NOW, _run=_git(ct=NOW - FROZEN))
    assert snap["state"] == "stale"
    assert pf.is_publishing_down(snap)
    assert "DOWN" in pf.describe(snap)
    assert f"{FROZEN / 3600:.1f}h" in pf.describe(snap), (
        "the summary must quote the age the verdict rests on, whatever the cadence is")


def test_a_healthy_tick_does_not_make_a_frozen_publish_look_fresh():
    """THE WHOLE POINT (director, 2026-08-13): 'alive-but-unchanged and alive-and-publishing must
    not look the same'. The freshness answer must be derived from the publish clock alone, so no
    amount of tick activity can move it."""
    pf.record_published(now=NOW - FROZEN)
    # Time passes, ticks keep running, the heartbeat keeps landing -- and this does not move.
    for later in (NOW, NOW + 600, NOW + 3600):
        assert pf.snapshot(now=later, _run=_git(ct=NOW - FROZEN))["state"] == "stale"


def test_content_moving_by_luck_is_not_a_publishing_pipeline():
    """The shape measured on 2026-08-13, and the one that hides best.

    The publish path had not landed for 21.7h, yet `site/data/dashboard.json` still reached origin
    twice in that window, swept along by unrelated worker commits. A blended freshness number
    would have read those two accidents as health, so the disagreement gets its own field and its
    own sentence."""
    pf.record_published(now=NOW - WELL_FROZEN)
    snap = pf.snapshot(now=NOW, _run=_git(ct=NOW - 60))   # committed a minute ago, by someone else
    assert snap["state"] == "stale"
    assert snap["committed_but_unpublished"] is True
    assert "PUBLISH PATH is what stopped" in pf.describe(snap)


def test_an_unmeasurable_age_is_UNKNOWN_and_never_fresh():
    """R15 FAIL-SILENT. A freshness module that answers '0 seconds' when it cannot find its own
    state would manufacture the false all-clear it exists to end. Missing state and a broken git
    are separate answers, and neither is `publishing`."""
    assert pf.snapshot(now=NOW, _run=_git(ct=None))["state"] == "unpublished"

    pf.STATE_FILE.write_text("{ this is not json")
    snap = pf.snapshot(now=NOW, _run=_git(rc=128))
    assert snap["state"] == "unknown"
    assert snap["published_age_seconds"] is None
    assert snap["committed_age_seconds"] is None
    assert "UNKNOWN" in pf.describe(snap)

    # `unknown` is not reported as down (no measurement = no evidence of a fault) but an absent
    # record IS, because "we have never published" needs somebody to look.
    assert pf.is_publishing_down(snap) is False
    pf.STATE_FILE.unlink()
    assert pf.is_publishing_down(pf.snapshot(now=NOW, _run=_git(ct=None))) is True


def test_only_a_verified_push_may_stamp_the_clock():
    """R15 INDEPENDENCE. The stamp is worth nothing if any code path can advance it, so its one
    caller must sit downstream of the ls-remote check -- not next to it, and not before it.

    MUTATION: move `_record_content_published()` above the `_push_reached_origin` branch in
    `git_commit_push` and this fails.
    """
    import ast
    import inspect

    from background import process_run_complete as prc

    src = inspect.getsource(prc.git_commit_push)
    calls = [n for n in ast.walk(ast.parse(src.lstrip()))
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_record_content_published"]
    assert len(calls) == 1, "the content-publish clock must have exactly one writer"

    # And that one call is inside the branch guarded by the ground-truth push check.
    guarded = [
        n for n in ast.walk(ast.parse(src.lstrip()))
        if isinstance(n, ast.If)
        and "_push_reached_origin" in ast.unparse(n.test)
        and "_record_content_published" in ast.unparse(n)
    ]
    assert guarded, (
        "_record_content_published is not inside the `if _push_reached_origin(...)` branch -- a "
        "stamp written on an unverified push makes this module agree with the bookkeeping it "
        "exists to be independent of"
    )


def test_the_heartbeat_carries_the_freshness_block(tmp_path, monkeypatch):
    """The consumer half: the block has to reach the file the site and the advisor fetch, or the
    measurement is real and invisible (R11, no orphan transitions).

    HEARTBEAT_FILE is re-pointed at a sandbox FIRST. `site/data/tick_heartbeat.json` is a
    PUBLISHED file that `_refresh_published_liveness_on_skip` commits to origin, so a test that
    drives `_write_heartbeat` against the real path puts its own fixture on the live site -- the
    ghost-writer class that already sent `run_verified.json` to origin once (see the seat guard in
    process_run_complete). The first draft of this test did exactly that.
    """
    from background import worker_tick

    monkeypatch.setattr(worker_tick, "HEARTBEAT_FILE", tmp_path / "tick_heartbeat.json")

    assert "state" in worker_tick._content_publish_block()

    worker_tick._write_heartbeat(types.SimpleNamespace(outcome="REST_NO_WORK", detail=""),
                                 "enumeration line")

    written = json.loads((tmp_path / "tick_heartbeat.json").read_text())
    assert "content_publish" in written, (
        "the heartbeat reports the tick verdict and says nothing about content -- which is "
        "exactly the state in which eighteen hours of frozen figures looked healthy"
    )
    assert written["content_publish"]["state"]
    # The tick verdict is still there: this ADDS a subject, it does not replace one.
    assert written["verdict"] == "rested"


# ── THE WEDGE THAT SILENCED ITS OWN ALARM (2026-08-21) ──────────────────────────────────────
# Publishing was down 28 hours and nothing paged. `state` was derived from the state-file clock
# alone, and that clock is stamped on any push where the remote advanced -- including the
# `chore(provenance): verification paused banner` commit the publish path pushes EVERY CYCLE
# WHILE WEDGED (ten of twenty-five consecutive commits that day). So each cycle of the outage
# reset the freshness clock, `is_publishing_down()` answered False, the deadman's content check
# cleared its transition, and the director found it by hand.
#
# The cross-check was already computed and already in the snapshot. It just was not consulted.

def test_a_recent_push_does_not_mask_figures_that_have_not_moved(monkeypatch):
    """THE INCIDENT. Push clock 13 minutes old (a banner commit), figures frozen past the cadence.

    Measured at 20.8 hours under the half-hourly cadence; expressed against the threshold so the
    property -- a fresh PUSH must never mask frozen FIGURES -- survives the cadence change that
    made 20.8 hours unremarkable."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    frozen = pf.STALE_AFTER_SECONDS + 3600
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 780)          # banner, 13 min
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - frozen)   # figures, past cadence
    snap = pf.snapshot(now=now)
    assert snap["state"] == "stale", (
        "a push that moved no figures reported publishing as live -- this is the 28-hour outage"
    )
    assert pf.is_publishing_down(snap) is True


def test_the_summary_quotes_the_number_that_made_the_verdict(monkeypatch):
    """"DOWN -- last published 0.2h ago" argues against itself and reads as a glitch."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    frozen = pf.STALE_AFTER_SECONDS + 3600      # past the cadence, whatever the cadence is
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 780)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - frozen)
    line = pf.describe(pf.snapshot(now=now))
    assert "DOWN" in line and f"{frozen / 3600:.1f}h" in line, line


def test_an_unavailable_cross_check_is_not_evidence_of_freshness(monkeypatch):
    """FAIL-SILENT, R15: if git cannot answer when the figures moved, that is UNKNOWN. Treating
    it as fresh would restore exactly the hole this closes, on any box where git is slow."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 10)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: None)
    assert pf.snapshot(now=now)["state"] == "unknown"


def test_both_clocks_fresh_still_reads_as_publishing(monkeypatch):
    """The control must not be always-red: a genuinely healthy publish still says live."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 60)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 120)
    snap = pf.snapshot(now=now)
    assert snap["state"] == "publishing"
    assert pf.is_publishing_down(snap) is False


# ── THE THIRD NUMBER: the queue behind the publisher (2026-09-03) ──────────────────────────────
# Both clocks answer "how long since something moved". Neither answers "is the pipeline keeping
# up with its input", and for nine hours on 2026-09-02/03 those had different answers: 62 markers
# produced, 27 consumed, and `describe()` said `live` the whole way through. Every leg below pins
# STAGING_DIR -- an unpinned real-disk read would make these pass or fail on whatever the actual
# queue happens to hold when the suite runs.

def _markers(d, n):
    """n queued run markers in `d`, named the way sim_runner names them (UTC stamps)."""
    for i in range(n):
        (d / f"run_complete_202609030{i:02d}000Z.md").write_text("x")
    return d


def test_a_live_line_names_the_queue_behind_the_publisher(monkeypatch, tmp_path):
    """DEFECT: `content publishing: live -- figures reached origin 0.7h ago` was quoted in three
    places while 35 completed runs sat unpublished behind it. The line was true; it was true
    about the wrong subject. A reader given the freshness verdict must also be given the depth.

    MUTATION: drop the `queued` clause from `describe`'s live branch (or make `queue_depth`
    return 0) and this leg fails -- it is the only one asserting the count reaches the line a
    human actually reads.
    """
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "STAGING_DIR", _markers(tmp_path, 35))
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 60)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 120)
    line = pf.describe(pf.snapshot(now=now))
    assert "live" in line, line
    assert "35 completed run(s) queued behind the publisher" in line, line


def test_an_uncountable_queue_reads_unknown_and_never_empty(monkeypatch, tmp_path):
    """FAIL-SILENT (R15), the same discipline the two clocks already keep: a queue we could not
    count must not be reported as a queue that is empty. `0` here would manufacture the all-clear
    this field exists to end.

    MUTATION: `except OSError: return 0` in `queue_depth` -- this leg is the sole witness.
    """
    import background.publish_freshness as pf

    class _Boom:
        def glob(self, _pat):
            raise OSError("staging unreadable")

    monkeypatch.setattr(pf, "STAGING_DIR", _Boom())
    assert pf.queue_depth() is None
    assert pf.snapshot(now=1_000_000.0)["queue_depth"] is None


def test_a_deep_queue_does_not_change_the_publish_verdict(monkeypatch, tmp_path):
    """The depth is an OBSERVATION and must stay one. The queue is a stack, not a FIFO -- the
    drain clears a burst by RETIRING superseded markers (17/17 at 2026-09-03 01:56Z) -- so a
    threshold here would alarm on the mechanism working, and `_check_zero_progress` already pages
    on the property that matters (no progress on the oldest marker across cycles). Promoting a
    previously-unread field into a decision is what turned five tests red on 2026-09-02.

    MUTATION: fold depth into `state` (e.g. `backlogged` when depth > N) and this leg fails.
    """
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "STAGING_DIR", _markers(tmp_path, 200))
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 60)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 120)
    snap = pf.snapshot(now=now)
    assert snap["state"] == "publishing"
    assert pf.is_publishing_down(snap) is False
    assert snap["queue_depth"] == 200


def test_an_empty_queue_adds_nothing_to_the_line(monkeypatch, tmp_path):
    """The control must not be always-on: a drained queue leaves the line exactly as it was, so
    the clause means something when it appears."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 60)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 120)
    assert "queued behind" not in pf.describe(pf.snapshot(now=now))


def test_the_oldest_queued_run_is_aged_from_its_utc_name_not_its_mtime(monkeypatch, tmp_path):
    """DEFECT: the count cannot tell a burst from a stall -- 35 markers minted in ten minutes is a
    busy runner; 3 whose oldest has waited nine hours is a pipeline not reaching its input. And
    the age must come from the NAME: sim_runner stamps UTC, this box runs local BST, and the
    retirement path rewrites mtimes -- so an mtime-based age both gains a phantom hour and resets
    on a marker that has not moved.

    MUTATION: age from `p.stat().st_mtime` instead of the parsed stamp; the file is written now,
    so the measured age collapses to ~0 and this leg fails.
    """
    import background.publish_freshness as pf
    # 20260902T160532Z, the real oldest member of the measured backlog, read at 01:07Z next day.
    (tmp_path / "run_complete_20260902T160532Z.md").write_text("x")
    monkeypatch.setattr(pf, "STAGING_DIR", tmp_path)
    now = datetime(2026, 9, 3, 1, 7, 0, tzinfo=timezone.utc).timestamp()
    age = pf.queue_oldest_age_seconds(now)
    assert age is not None and 9.0 < age / 3600.0 < 9.1, age


def test_an_empty_or_unparseable_queue_reports_no_age_rather_than_zero(monkeypatch, tmp_path):
    """FAIL-SILENT again: `0.0` would read as "the oldest run has waited no time at all", i.e. a
    perfectly fresh queue, which is the all-clear this field exists to withhold.

    MUTATION: `return max(ages) if ages else 0.0` -- this leg is the sole witness.
    """
    import background.publish_freshness as pf
    monkeypatch.setattr(pf, "STAGING_DIR", tmp_path)
    assert pf.queue_oldest_age_seconds(1_000_000.0) is None
    (tmp_path / "run_complete_NOT_A_STAMP.md").write_text("x")
    assert pf.queue_oldest_age_seconds(1_000_000.0) is None
    assert pf.queue_depth() == 1  # counted, but contributing no age


# ── the cadence is the single source of truth, and two questions keep two clocks ─────────────────

def test_the_staleness_threshold_follows_the_declared_cadence():
    """THE PROPERTY, not today's number. An alarm calibrated for a cadence the site no longer keeps
    is the shape that had correct controls refusing correct work all week: at a weekly cadence a
    three-hour threshold reads "PUBLISHING IS DOWN" six days in seven while the machine does exactly
    what it was told.

    MUTATION: hard-code STALE_AFTER_SECONDS back to a constant and this fires -- the threshold stops
    moving when the cadence does.
    """
    import background.publish_freshness as pf

    assert pf.STALE_AFTER_SECONDS == pf.PUBLISH_CADENCE_SECONDS + pf.PUBLISH_GRACE_SECONDS
    assert pf.STALE_AFTER_SECONDS > pf.PUBLISH_CADENCE_SECONDS, (
        "a site that publishes exactly on cadence must never read as stale for doing so")


def test_a_site_publishing_on_cadence_is_not_stale(monkeypatch):
    """THE NULL CONTROL, and the whole point of the change: six days after a weekly publish the site
    is healthy, not broken. MUTATION: keep the old three-hour horizon and this fires."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    six_days = 6 * 24 * 3600
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - six_days)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - six_days)
    snap = pf.snapshot(now=now)
    assert snap["state"] == "publishing", "a site on cadence was called broken"
    assert pf.is_publishing_down(snap) is False


def test_a_missed_publishing_window_is_still_caught(monkeypatch):
    """The other direction, so the widened threshold is not a blindfold. MUTATION: widen the grace
    to a second cadence and this fires."""
    import background.publish_freshness as pf
    now = 1_000_000.0
    overdue = pf.STALE_AFTER_SECONDS + 3600
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - overdue)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - overdue)
    assert pf.snapshot(now=now)["state"] == "stale"


def test_a_stuck_push_is_judged_on_its_own_short_clock(monkeypatch):
    """TWO QUESTIONS, TWO CLOCKS, and conflating them is what this separates.

    "Is the weekly publish overdue?" is answered on the cadence. "Is content being committed
    locally and never reaching origin?" is a different fault with a different fix, and nothing about
    a weekly cadence makes a stuck push less broken. If `committed_but_unpublished` had inherited
    the eight-day threshold it would have gone quiet for a week at a time.

    MUTATION: key `committed_but_unpublished` to STALE_AFTER_SECONDS and this fires.
    """
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - (pf.PUSH_LAG_AFTER_SECONDS + 3600))
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 60)   # committed a minute ago
    snap = pf.snapshot(now=now)
    assert snap["committed_but_unpublished"] is True, (
        "content is being committed and not pushed, and the weekly clock hid it")


def test_the_snapshot_carries_the_as_at_date_from_the_content_clock(monkeypatch):
    """The banner cannot state an as-at date it is not given, and it must be the age of the FIGURES,
    never of the last push -- the reader is asking how old the numbers are.

    MUTATION: derive `as_at_utc` from `published_age_seconds` and this fires, because a liveness
    heartbeat pushed minutes ago would date week-old figures to today.
    """
    import background.publish_freshness as pf
    now = 1_000_000.0
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 60)            # pushed a minute ago
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 3 * 86400)  # figures 3 days old
    snap = pf.snapshot(now=now)
    from datetime import datetime, timezone
    expected = datetime.fromtimestamp(now - 3 * 86400, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    assert snap["as_at_utc"] == expected, "the as-at date came from the push clock, not the figures"
    assert snap["cadence_seconds"] == pf.PUBLISH_CADENCE_SECONDS
