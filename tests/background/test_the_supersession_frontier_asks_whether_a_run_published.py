"""THE DEFECT: the supersession frontier asked WHERE a marker was filed, not whether its
run published -- and retired queued snapshots on the strength of runs that published nothing.

REUSE: tests/background/test_the_supersession_frontier_asks_whether_a_run_published.py
CLASS: CUSTOM
INDEX: searched "supersession", "newest_published", "classify_markers", "retire_superseded",
       "publish outcome". The nearest existing homes were rejected on subject:
       `test_background_worker.py` owns the SWEEP's ordering properties (newest-first, the
       stall alarm, drain-supersession) and `test_staging_archive_policy.py` owns the union
       view over done/ + exhaust. Neither owns the seam this module is about, which crosses
       two modules: the publisher STATES an outcome and the worker's frontier READS it. A
       control that lived in either file would exercise one half and stub the other, which is
       the shape that proves the stub (R15).

WHAT HAPPENED, on real disk, 2026-09-24
---------------------------------------
07:39  `process_run_complete` logged "Done, but THE PUBLISH DID NOT LAND (outcome:
       behind_origin) -- the surfaces this process regenerated are still local ... the marker
       is archived". The marker moves to done/ BEFORE the commit, deliberately, so that the
       archive lands in the same commit as the run it documents.
08:06  `background_worker.retire_superseded_marker()` appended to
       `docs/staging/done/run_complete_20260924T045831Z.md`: "A strictly later run
       (20260924T064310Z) had already completed its publish pipeline, so this snapshot was
       overtaken on every published surface." Run 064310Z is the rc=77 `commit_did_not_land`
       recorded in `.publish_gate_state.json`. It reached no surface at all.

So the instrument that would have shown a sixty-hour publishing outage was clearing the
backlog it should have been raising, and telling an auditor in writing that figures had
reached pages they never reached.

THE ONE CASE THAT DISTINGUISHES THE TWO READINGS, and why it is one control and not two
---------------------------------------------------------------------------------------
"A failed publish must not retire a queued snapshot" is passed in full by a frontier that
retires NOTHING, ever -- and that frontier reopens `OPS_run_marker_sweep_livelock`
(2026-08-03), where the sweep retries stale snapshots for ever and republishes figures over
current ones. The refusal leg and the reachability leg are therefore asserted TOGETHER, over
the whole partition, with the SAME queue and the SAME frontier marker: the only thing that
differs between the two arms is whether that marker says its publish landed. A guard that
always refuses fails the second arm; a guard that never refuses fails the first.
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from background import background_worker, staging_archive_policy
from background import process_run_complete as prc

#: The run that did NOT publish (rc=77, `behind_origin`) and was read as the frontier anyway.
FRONTIER = "run_complete_20260924T064310Z.md"
#: The snapshot it wrongly retired, still queued in staging/ at the moment of the defect.
QUEUED = "run_complete_20260924T045831Z.md"
#: A genuinely published run, older than the queued one, so it can never retire it. Present so
#: that the frontier is non-empty in BOTH arms -- an empty frontier classifies everything as
#: pending for a reason that has nothing to do with this control.
OLDER_PUBLISHED = "run_complete_20260923T221011Z.md"

BODY = "# Simulation Run Complete\n\nGit: e664b5720\n"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Every write here is a tmp write. `docs/staging/` is a protected production surface
    (tests/production_surface_guard.py) and these functions write markers for a living."""
    staging = tmp_path / "staging"
    (staging / "done").mkdir(parents=True)
    monkeypatch.setattr(background_worker, "STAGING_DIR", staging)
    monkeypatch.setattr(background_worker, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(background_worker, "SWEEP_STATE_FILE", tmp_path / ".sweep.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    monkeypatch.setattr(prc, "DONE_DIR", staging / "done")
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    yield


def _archive(staging: Path, name: str) -> Path:
    path = staging / "done" / name
    path.write_text(BODY)
    return path


def _queue(staging: Path, name: str) -> Path:
    path = staging / name
    path.write_text(BODY)
    return path


def _stamp_as_failed(name: str, reason: str = prc.BEHIND_ORIGIN) -> bool:
    """Stamp through the PUBLISHER's own function, not by writing the tag by hand.

    Typing the tag here would make this a test of a string literal I chose. The whole subject
    of this module is that two modules agree about a fact, so the writer has to be the real
    writer and the reader the real reader."""
    return prc._stamp_publish_outcome_on_archived_marker(name, reason, done_dir=prc.DONE_DIR)


def test_a_failed_publish_cannot_retire_a_queued_snapshot_and_a_real_one_still_can(monkeypatch):
    """THE PARTITION, both arms, one queue, one differing fact.

    ARM 1 (the defect): the newest archived run says its publish did not land, so it is not
    the frontier and the snapshot queued behind it stays queued and gets published.
    ARM 2 (the livelock guard): the same run with its publish landed IS the frontier, and the
    same queued snapshot is retired -- terminally, naming the run that overtook it.

    MUTATION 1: make `staging_archive_policy.publish_did_not_land` return False always (i.e.
    revert the repair) and ARM 1 fails -- the queued marker is retired by a run that published
    nothing, and never reaches the publisher.
    MUTATION 2: make it return True always (a frontier that retires nothing, which passes
    every refusal-only test) and ARM 2 fails on both the retirement and the note.
    """
    staging = background_worker.STAGING_DIR

    # ── ARM 1: the frontier run's publish did not land ────────────────────────────────────
    _archive(staging, OLDER_PUBLISHED)
    _archive(staging, FRONTIER)
    assert _stamp_as_failed(FRONTIER), "the publisher must have stamped the failed outcome"
    queued = _queue(staging, QUEUED)

    published = []

    def _run(*a, **k):
        argv = a[0]
        if any("process_run_complete" in str(x) for x in argv):
            published.append(Path(argv[-1]).name)
        return MagicMock(returncode=1, stderr="")

    monkeypatch.setattr(background_worker.subprocess, "run", _run)
    background_worker.process_leftover_run_markers()

    assert queued.exists(), (
        f"{QUEUED} was retired as superseded by {FRONTIER}, whose publish did not land. A run "
        "that reached no surface overtakes nothing."
    )
    assert published == [QUEUED], (
        f"the queued snapshot must still be handed to the publisher, got {published}"
    )
    retired = staging / "done" / QUEUED
    assert not retired.exists(), "nothing may be filed into done/ by a failed frontier"

    # ── ARM 2: the SAME frontier run, with its publish landed ─────────────────────────────
    # Rewritten clean, which is exactly what a landed publish leaves behind: no tag, because
    # on the landed path the archive's own implication is true and nothing needs stating.
    _archive(staging, FRONTIER)
    assert not _stamp_as_failed(FRONTIER, prc.PUBLISHED), (
        "a landed publish must not stamp a did-not-land tag"
    )
    published.clear()
    background_worker.process_leftover_run_markers()

    assert not queued.exists(), (
        f"{QUEUED} must be RETIRED once a strictly later run genuinely published -- a "
        "supersession that is not terminal is OPS_run_marker_sweep_livelock (2026-08-03)"
    )
    assert published == [], "a retired snapshot must not also be republished over current figures"
    body = (staging / "done" / QUEUED).read_text()
    assert "# Simulation Run Complete" in body, "R10: retiring keeps the marker's own content"
    assert "20260924T064310Z" in body, "the retirement note must NAME the run that overtook it"


def test_the_publisher_states_the_outcome_and_the_frontier_reads_that_statement(monkeypatch):
    """THE SEAM, asserted directly: the writer is `process_run_complete`, the reader is
    `background_worker._newest_published_stamp`, and nothing between them is stubbed.

    Two modules agreeing via a constant they both import is a tautology; two modules agreeing
    because one wrote a real file the other read is not. This fails if either side changes the
    tag, the note's shape, or which outcomes count as landed.

    MUTATION: drop the `_stamp_publish_outcome_on_archived_marker` call from `_process` and
    this still passes (it calls the stamper directly) -- which is why the sweep-level control
    above exists and this one does not stand alone.
    """
    done = prc.DONE_DIR
    _archive(background_worker.STAGING_DIR, OLDER_PUBLISHED)
    _archive(background_worker.STAGING_DIR, FRONTIER)

    assert background_worker._newest_published_stamp(done) == "20260924T064310Z", \
        "before the outcome is stated, the archive is all there is to read"

    _stamp_as_failed(FRONTIER)

    assert background_worker._newest_published_stamp(done) == "20260923T221011Z", \
        "once the publisher says the publish did not land, the frontier steps back to a run " \
        "that did"


def test_an_unstamped_marker_still_counts_as_published(monkeypatch):
    """FAIL-SAFE DIRECTION (R15), and it is the opposite of the intuitive one.

    Every one of the ~4,300 markers already in done/ and the exhaust tree predates this tag.
    Reading absence as "did not publish" would empty the frontier, classify the whole corpus
    as pending, and let the sweep republish stale snapshots over current figures for ever --
    a worse failure than the one being repaired, and the one supersession exists to prevent.
    """
    done = prc.DONE_DIR
    legacy = _archive(background_worker.STAGING_DIR, OLDER_PUBLISHED)
    assert staging_archive_policy.PUBLISH_DID_NOT_LAND_TAG not in legacy.read_text()
    assert background_worker._newest_published_stamp(done) == "20260923T221011Z"

    unreadable = _archive(background_worker.STAGING_DIR, FRONTIER)
    unreadable.write_bytes(b"\xff\xfe not valid utf-8 \x00")
    assert not staging_archive_policy.publish_did_not_land(unreadable), \
        "an unreadable marker may not empty the frontier"


def test_a_delivery_deferred_commit_is_landed_for_supersession_and_not_for_the_fingerprint():
    """THE ONE MEMBER THE TWO CLOSED SETS DISAGREE ON, pinned so the disagreement is a
    decision rather than a drift.

    `COMMITTED_DELIVERY_DEFERRED` means the content IS committed and its delivery to origin is
    with `origin_reconcile`. It must NOT be retryable -- the verdict is still owed -- and it
    must count as landed for supersession, because republishing an older snapshot over
    committed current figures is the clock-rewind supersession exists to stop.

    MUTATION: define `PUBLISH_LANDED_OUTCOMES = RETRYABLE_PUBLISH_OUTCOMES` and this fails.
    """
    assert prc.COMMITTED_DELIVERY_DEFERRED in prc.PUBLISH_LANDED_OUTCOMES
    assert prc.COMMITTED_DELIVERY_DEFERRED not in prc.RETRYABLE_PUBLISH_OUTCOMES
    for failed in (prc.BEHIND_ORIGIN, prc.COMMIT_REFUSED, prc.COMMIT_TIMEOUT,
                   prc.PUSH_DID_NOT_REACH_ORIGIN, prc.PROVENANCE_REFUSED,
                   prc.TREE_LOCK_UNAVAILABLE, None, "a_branch_added_next_month"):
        assert failed not in prc.PUBLISH_LANDED_OUTCOMES, (
            f"{failed!r} leaves the published surfaces unchanged, so it may not make this run "
            "the frontier"
        )


def test_the_note_cannot_pin_the_marker_into_the_record_partition():
    """The note is appended to a file the archive sweep later classifies. `classify()` forces
    RECORD on any body carrying a `RECORD_MARKERS` string -- and RECORD means it never leaves
    done/. A note containing, say, the word this project uses for the person it reports to
    would silently pin every failed-publish marker into done/ for ever.

    MUTATION: add any RECORD_MARKERS string to `publish_outcome_note` and this fails.
    """
    note = staging_archive_policy.publish_outcome_note(prc.BEHIND_ORIGIN, when="2026-09-24T07:39Z")
    assert staging_archive_policy.classify(FRONTIER, BODY + note) == staging_archive_policy.EXHAUST
    offenders = [m for m in staging_archive_policy.RECORD_MARKERS if m in note]
    assert offenders == [], f"the note carries record markers {offenders}"
