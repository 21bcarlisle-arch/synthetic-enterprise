"""THE PAUSED BANNER IS GATED ON THE COMMIT IT MAKES, NOT ON THE SHARED WORKING COPY.

DEFECT (9 Nov, docs/staging/SEAT_FINDING_THE_PAUSED_BANNER_WAS_REFUSED_BY_THE_BOOK_IT_REPORTS_
2026-11-09.md): the banner was a pathspec `git commit` in the shared tree, and the hook chain runs
its tests on the files on disk. On a red cycle those files are the refused book, so the site lane
graded the refused Explore feed and refused the one-file banner whose job is to say the feed was
refused. poesys.net said "Verified 3 Nov" through three refusals on 8-9 Nov.

The property: the banner goes through `surgical_land.land` (a clean extract of HEAD plus the named
paths), and never through a `git commit` in the shared tree. Then the partition of what a landing
can come back with, asserted whole before any leg: published, steady-state no-op, gate NO, and
every attempt lost -- four outcomes, three records.
"""
from __future__ import annotations

import pytest

from background import process_run_complete as prc
from background import publish_cause as pc
from tests.background.test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line import (
    _drive,
    _record,
)
from tools import surgical_land


@pytest.fixture
def state_file(tmp_path, monkeypatch):
    path = tmp_path / ".publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    return path


def test_the_banner_never_commits_in_the_shared_tree(state_file, tmp_path, monkeypatch):
    """`_drive`'s subprocess fake models `git add` and `git commit` no longer, and RAISES on any
    git command it does not model, so this publishes only if the commit came from the landing.

    MUTATION: put back `subprocess.run(["git", "commit", ...])` in `_commit_and_push_paths` and
    this raises -- that call is what let a refused book's files grade the banner. Drop the
    landing instead and nothing produces a sha, so the publish leg reds."""
    assert _drive(monkeypatch, tmp_path, local_head="land1111", remote_head="land1111") is True
    assert _record(state_file) is None


@pytest.fixture
def landings(monkeypatch):
    calls = []
    outcome = {"sha": "landed11", "raise": None, "lose": 0}

    def fake_land(root, paths, message, attempts=1, on_lost=None, **kwargs):
        calls.append(list(paths))
        for attempt in range(1, outcome["lose"] + 1):
            if on_lost is not None:
                on_lost(attempt, surgical_land.BaseMoved("moved", "a" * 40, "b" * 40))
        if outcome["raise"] is not None:
            raise outcome["raise"]
        return outcome["sha"]

    monkeypatch.setattr(surgical_land, "land", fake_land)
    monkeypatch.setattr(prc, "_record_commit_refusal_reds", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_record_commit_hook_pass", lambda *a, **k: None)
    return calls, outcome


def test_every_landing_outcome_is_reachable_and_told_apart(state_file, tmp_path, monkeypatch,
                                                          landings):
    """THE PARTITION. MUTATIONS: catch `NothingToLand` as a refusal -> the no-op leg records;
    record GATE_REFUSAL on exhaustion -> the race leg reds; return "" on success -> leg one reds."""
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    target = [str(tmp_path / "site" / "data" / "publish_provenance.json")]
    _, outcome = landings
    seen = {}
    for name, raise_, lose in (
            ("published", None, 1),
            ("no_op", surgical_land.NothingToLand("the named paths are already at HEAD"), 0),
            ("gate_no", surgical_land.LandingRefused("pre-commit hook refused: 1 failed"), 0),
            ("every_race_lost", surgical_land.LandingRefused("HEAD moved on every attempt"),
             prc.PUBLISH_LAND_ATTEMPTS)):
        state_file.unlink(missing_ok=True)
        outcome.update({"raise": raise_, "lose": lose})
        sha = prc._land_liveness_surface(target, "msg", label="Provenance banner", git_hash="abc")
        record = _record(state_file)
        seen[name] = (sha, record["cause"] if record else None)
    assert seen == {
        "published": ("landed11", None),
        "no_op": ("", None),
        "gate_no": ("", pc.GATE_REFUSAL),
        "every_race_lost": ("", pc.LOST_COMMIT_RACE),
    }, seen
    assert pc.LOST_COMMIT_RACE in pc.NO_TEST_JUDGED_CAUSES
