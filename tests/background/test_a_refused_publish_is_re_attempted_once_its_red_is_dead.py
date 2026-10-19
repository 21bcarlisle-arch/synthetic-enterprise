"""THE DEFECT: a publish refused at the commit, whose red was answered at HEAD hours later, was
never re-attempted -- its marker sits in done/ and the sweep globbed staging/ alone. Twice (13 Oct,
19 Oct) a human re-drove it by hand. Design: docs/design/PUBLISH_DECOUPLING.md, "A REFUSED PUBLISH
WHOSE RED IS LATER ANSWERED".

REUSE: tests/background/test_a_refused_publish_is_re_attempted_once_its_red_is_dead.py
CLASS: CUSTOM
INDEX: searched "publish_did_not_land", "citation_at_head", "process_leftover_run_markers",
       "rearm". `test_the_supersession_frontier_asks_whether_a_run_published.py` owns the
       frontier's reading of the did-not-land tag; this module owns what the sweep DOES with a
       did-not-land marker whose citation is dead, which no existing control asks.

The marker is stamped through the publisher's own writer, so the tag the selector reads is the
real one. The rare branch is asserted reachable first (the partition control), then each guard
is asserted to refuse with everything else held at the reachable fixture: one variable per arm.
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from background import background_worker as bw
from background import process_run_complete as prc

REFUSED = "run_complete_20261019T033010Z.md"
GIT = "8b6fea024"
FAILED_AT = 1792391719.0


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
    yield


def _world(tmp_path, *, citation="dead", landed=None, git=GIT, outputs_same=True,
           name=REFUSED, published_after=None):
    """The 19 Oct state: one refused marker in done/, its run JSON on disk, latest equal to it."""
    done = bw.STAGING_DIR / "done"
    run_json = tmp_path / f"run_output_{git}.json"
    run_json.write_text('{"total_net_gbp": 555900}')
    bw.RUN_OUTPUT_LATEST.write_text(run_json.read_text() if outputs_same else '{"other": 1}')
    (done / name).write_text(f"# Simulation Run Complete\n\nGit: {git}\nJSON: {run_json}\n")
    assert prc._stamp_publish_outcome_on_archived_marker(name, prc.COMMIT_REFUSED,
                                                         done_dir=done)
    if published_after:
        (done / published_after).write_text("# Simulation Run Complete\n\nGit: abc\n")
    bw.PUBLISH_GATE_STATE_FILE.write_text(__import__("json").dumps({
        "last_landed_publish": landed,
        "failures": [{"git_hash": GIT, "ts": FAILED_AT, "citation_at_head": citation,
                      "kind": "commit_did_not_land", "rc": 77}],
    }))
    return done / name


def _sweep(monkeypatch, rc=77):
    invoked = []

    def _run(argv, **_):
        if any("process_run_complete" in str(x) for x in argv):
            invoked.append(Path(argv[-1]))
        return MagicMock(returncode=rc, stdout="", stderr="")

    monkeypatch.setattr(bw.subprocess, "run", _run)
    bw.process_leftover_run_markers()
    return invoked


def test_a_refused_marker_whose_red_is_dead_is_re_attempted_from_done(tmp_path, monkeypatch):
    """THE BRANCH CAN BE TAKEN. Asserted before any refusal, because a selector that refuses
    everything passes every refusal below.

    MUTATION: make `refused_marker_to_rearm` return `(None, "")` unconditionally -> red (nothing
    invoked). MUTATION: delete the `markers + [rearm]` line in the sweep -> red (selected, never
    handed to the publisher)."""
    marker = _world(tmp_path)
    picked, why = bw.refused_marker_to_rearm(bw.STAGING_DIR / "done", None)
    assert picked == marker, why
    assert _sweep(monkeypatch) == [marker], "the publisher must be handed the done/ marker"
    assert bw.PUBLISH_REARMED_TAG in marker.read_text(), "the one attempt must be recorded"


def test_a_re_attempt_that_fails_again_is_not_re_queued(tmp_path, monkeypatch):
    """The livelock leg (OPS_run_marker_sweep_livelock). Same world, a second sweep.

    MUTATION: drop `_stamp_rearmed(marker)` from the sweep -> red (re-invoked every cycle)."""
    marker = _world(tmp_path)
    assert _sweep(monkeypatch) == [marker]
    assert _sweep(monkeypatch) == [], "a marker re-attempted once must not be re-attempted again"


@pytest.mark.parametrize("arm, kwargs, reason_word", [
    # MUTATION: drop the `!= "dead"` check -> red.
    ("citation still live", {"citation": "live"}, "not 'dead'"),
    # MUTATION: drop the `landed >= failed_at` check -> red.
    ("a publish landed after the refusal", {"landed": FAILED_AT + 60}, "landed since"),
    # MUTATION: drop the frontier check -> red. A later run without a did-not-land tag published.
    ("overtaken by a later published run",
     {"published_after": "run_complete_20261020T010101Z.md"}, "overtaken"),
    # MUTATION: replace the filecmp with `same = bool(run_json)` -> red.
    ("outputs overwritten by a later run", {"outputs_same": False}, "mix of two runs"),
])
def test_each_guard_refuses_with_its_reason(tmp_path, monkeypatch, arm, kwargs, reason_word):
    """One variable per arm against the reachable fixture above, so each red names one guard."""
    _world(tmp_path, **kwargs)
    newest = bw._newest_published_stamp(bw.STAGING_DIR / "done")
    picked, why = bw.refused_marker_to_rearm(bw.STAGING_DIR / "done", newest)
    assert picked is None, f"{arm}: must not be re-attempted"
    assert reason_word in why, f"{arm}: the refusal must name its reason, got {why!r}"
    assert _sweep(monkeypatch) == [], f"{arm}: the sweep must not invoke the publisher"

