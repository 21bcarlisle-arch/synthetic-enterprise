"""THE DEFECT: a run that finished mid-week was HELD by the weekly window and its marker archived,
and nothing offered it again when the window opened at Mon 04:00 -- all four 904a091f7b runs of
24-25 Oct. A publish happened only if some run happened to finish after the window opened. Design:
docs/design/PUBLISH_DECOUPLING.md, "A HELD RUN WHEN THE WEEKLY WINDOW OPENS".

REUSE: tests/background/test_a_refused_publish_is_re_attempted_once_its_red_is_dead.py
CLASS: CUSTOM
INDEX: searched "publish_held", "HOLD (weekly publish window)", "process_leftover_run_markers",
       "refused_marker_to_rearm". The re-arm test owns a REFUSED marker whose red is dead; this
       module owns a HELD marker at the window, which no existing control asks.

The marker is stamped through the publisher's own hold writer, so the tag the selector reads is
the real one. The branch is asserted reachable first, then each guard refuses with everything
else held at the reachable fixture: one variable per arm.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from background import background_worker as bw
from background import process_run_complete as prc
from background import publish_freshness

HELD = "run_complete_20261025T031613Z.md"
OPEN = {"open": True, "reason": "this week's figures are owed"}
CLOSED = {"open": False, "reason": "the next publish opens Mon 2026-10-26 04:00 GMT"}


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    (staging / "done").mkdir(parents=True)
    monkeypatch.setattr(bw, "STAGING_DIR", staging)
    monkeypatch.setattr(bw, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(bw, "SWEEP_STATE_FILE", tmp_path / ".sweep.json")
    monkeypatch.setattr(bw, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(bw, "RUN_OUTPUT_LATEST", tmp_path / "run_output_latest.json")
    monkeypatch.setattr(bw, "_record_publish_gate_outcome", lambda *a, **k: None)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    monkeypatch.setattr(prc, "DONE_DIR", staging / "done")
    bw.PUBLISH_GATE_STATE_FILE.write_text(json.dumps({"failures": []}))
    yield


def _world(tmp_path, monkeypatch, *, window=OPEN, held=True, outputs_same=True, newer=None):
    done = bw.STAGING_DIR / "done"
    run_json = tmp_path / "run_output_904a091f7b.json"
    run_json.write_text('{"total_net_gbp": 555900}')
    bw.RUN_OUTPUT_LATEST.write_text(run_json.read_text() if outputs_same else '{"other": 1}')
    (done / HELD).write_text(f"# Simulation Run Complete\n\nGit: 904a091f7b\nJSON: {run_json}\n")
    if held:
        assert prc._stamp_held_on_archived_marker(HELD, CLOSED["reason"], done_dir=done)
    if newer:
        (done / newer).write_text("# Simulation Run Complete\n\nGit: abc\n")
    monkeypatch.setattr(publish_freshness, "content_publish_window", lambda: dict(window))
    return done / HELD


def _sweep(monkeypatch):
    invoked = []

    def _run(argv, **_):
        if any("process_run_complete" in str(x) for x in argv):
            invoked.append(Path(argv[-1]))
        return MagicMock(returncode=3, stdout="", stderr="")

    monkeypatch.setattr(bw.subprocess, "run", _run)
    bw.process_leftover_run_markers()
    return invoked


def test_a_held_run_is_offered_when_the_window_opens(tmp_path, monkeypatch):
    """THE BRANCH CAN BE TAKEN, asserted first: a selector that refuses everything passes every
    refusal below."""
    marker = _world(tmp_path, monkeypatch)
    assert _sweep(monkeypatch) == [marker]
    assert bw.PUBLISH_OFFERED_TAG in marker.read_text()


def test_it_is_offered_once_however_the_publish_ends(tmp_path, monkeypatch):
    marker = _world(tmp_path, monkeypatch)
    assert _sweep(monkeypatch) == [marker]
    assert _sweep(monkeypatch) == []


@pytest.mark.parametrize("arm, kwargs", [
    ("the window is closed", {"window": CLOSED}),
    ("the marker was not held", {"held": False}),
    ("latest is another run's output", {"outputs_same": False}),
    ("a later run has its own marker", {"newer": "run_complete_20261025T120000Z.md"}),
])
def test_each_guard_refuses_alone(tmp_path, monkeypatch, arm, kwargs):
    _world(tmp_path, monkeypatch, **kwargs)
    assert _sweep(monkeypatch) == [], arm
    offer, why = bw.held_marker_to_offer(bw.STAGING_DIR / "done")
    assert offer is None and why, arm


def test_a_pending_marker_in_staging_is_published_instead(tmp_path, monkeypatch):
    held = _world(tmp_path, monkeypatch)
    pending = bw.STAGING_DIR / "run_complete_20261026T050000Z.md"
    pending.write_text("# Simulation Run Complete\n\nGit: def\n")
    assert _sweep(monkeypatch) == [pending]
    assert bw.PUBLISH_OFFERED_TAG not in held.read_text()


def test_the_hold_path_writes_the_tag_the_offer_reads(tmp_path, monkeypatch):
    """The publisher's own HOLD branch, not a hand-written tag: the writer and reader meet."""
    run_json = tmp_path / "run.json"
    run_json.write_text('{"total_net_gbp": 1}')
    marker = bw.STAGING_DIR / HELD
    marker.write_text(f"# Simulation Run Complete\n\nGit: 904a091f7b\nJSON: {run_json}\n")
    monkeypatch.setattr(prc, "_content_publish_window", lambda: dict(CLOSED))
    monkeypatch.setattr(prc, "_run_fingerprint", lambda d: {"administration_event": False})
    monkeypatch.setattr(prc, "record_publish_hold", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_refresh_published_liveness_on_skip", lambda *a: None)
    monkeypatch.setattr(prc, "_record_archived_marker", lambda *a: None)
    assert prc._process(str(marker)) == prc.EXIT_NOTHING_PUBLISHED
    from background import staging_archive_policy
    archived = bw.STAGING_DIR / "done" / HELD
    assert staging_archive_policy.publish_was_held(archived)
    assert not staging_archive_policy.publish_did_not_land(archived)
