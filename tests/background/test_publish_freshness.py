"""Content-publish freshness — the number that tells a frozen site from a live one.

Written from the 2026-08-13 freeze: eighteen hours of `verdict: drew`, a heartbeat landing on
origin every thirty minutes, and a site serving the previous day's figures. Nothing was red.
Every test here is about the property that was missing, not about the tick that was fine.
"""
from __future__ import annotations

import json
import types

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


def test_the_eighteen_hour_freeze_reads_as_stale():
    """The incident itself, as a measurement: the last verified publish is 18h old.

    MUTATION: widen STALE_AFTER_SECONDS past 18h, or make `snapshot` read the TICK's clock
    instead of the publish clock, and this fails.
    """
    eighteen_hours = 18 * 3600
    pf.record_published(now=NOW - eighteen_hours)
    snap = pf.snapshot(now=NOW, _run=_git(ct=NOW - eighteen_hours))
    assert snap["state"] == "stale"
    assert pf.is_publishing_down(snap)
    assert "DOWN" in pf.describe(snap)
    assert "18.0h" in pf.describe(snap)


def test_a_healthy_tick_does_not_make_a_frozen_publish_look_fresh():
    """THE WHOLE POINT (director, 2026-08-13): 'alive-but-unchanged and alive-and-publishing must
    not look the same'. The freshness answer must be derived from the publish clock alone, so no
    amount of tick activity can move it."""
    pf.record_published(now=NOW - 18 * 3600)
    # Time passes, ticks keep running, the heartbeat keeps landing -- and this does not move.
    for later in (NOW, NOW + 600, NOW + 3600):
        assert pf.snapshot(now=later, _run=_git(ct=NOW - 18 * 3600))["state"] == "stale"


def test_content_moving_by_luck_is_not_a_publishing_pipeline():
    """The shape measured on 2026-08-13, and the one that hides best.

    The publish path had not landed for 21.7h, yet `site/data/dashboard.json` still reached origin
    twice in that window, swept along by unrelated worker commits. A blended freshness number
    would have read those two accidents as health, so the disagreement gets its own field and its
    own sentence."""
    pf.record_published(now=NOW - 20 * 3600)
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
