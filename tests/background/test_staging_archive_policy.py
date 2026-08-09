"""Tests for background/staging_archive_policy.py (atom AO10).

The atom named its own two failure modes and both are tested here as controls
that can FAIL, not as assertions that the happy path works:

  1. MASS LOSS -- this policy moves thousands of files, so a bug is the loss
     of the run record. Count conservation, content identity, conflict
     reporting and `verify()` (mutated by deleting a moved file) cover it.
  2. AN INSTRUCTION MISCLASSIFIED AS EXHAUST -- the classifier is put on trial
     against the REAL corpus on disk, and against an adversarial file that
     wears a marker's name while carrying a director's words.

The real-corpus test carries its own vacuity guard: it asserts both classes
are present in the corpus before believing the classifications, because a
corpus that happened to contain no instructions would pass a "no instruction
is exhaust" assertion while proving nothing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from background import staging_archive_policy as policy

MARKER_BODY = """# Simulation Run Complete

Finished: 2026-08-08T23:59:45.922700+00:00
Git: fa9a73c72
JSON: /home/rich/synthetic-enterprise/docs/reports/run_output_fa9a73c72_20260808T235122Z.json
Duration: 504s | Size: 3906 KB

## Action required

1. Regenerate docs/reports/ANNUAL_REPORT.md from this run's data.
"""


@pytest.fixture
def staging(tmp_path):
    """An isolated staging tree: done/ with markers + instructions."""
    done = tmp_path / "staging" / "done"
    done.mkdir(parents=True)
    for stamp in ("20260618T052611Z", "20260719T101112Z", "20260808T235122Z"):
        (done / f"run_complete_{stamp}.md").write_text(MARKER_BODY)
    (done / "from_rich_20260729_182313.md").write_text(
        "never ask without recommending, and default to acting on your own recommendation"
    )
    (done / "ADVISOR_STEER_M2_OPEN.md").write_text("[ADVISOR-STAGED] open M2 please")
    return done


def _sweep(done, apply=True):
    moves = policy.plan_sweep(done_dir=done)
    return moves, policy.apply_sweep(moves, dry_run=not apply, done_dir=done)


# --------------------------------------------------------------------------
# The classifier, on trial
# --------------------------------------------------------------------------

def test_a_director_doc_wearing_a_markers_name_is_never_exhaust():
    """THE named failure: a real instruction filed as exhaust. Prefix alone
    must not be enough -- the body decides."""
    body = "# Simulation Run Complete\n\n[DIRECTOR-RULING] stop the presses\n\n## Action required\n"
    assert policy.classify("run_complete_20260808T235122Z.md", body) == policy.RECORD


def test_a_real_marker_is_exhaust():
    assert policy.classify("run_complete_20260808T235122Z.md", MARKER_BODY) == policy.EXHAUST


@pytest.mark.parametrize("name,body", [
    ("ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md", "scope brief"),      # no exhaust prefix
    ("from_rich_20260729_182313.md", "go"),                        # director channel
    ("run_complete_20260808T235122Z.txt", MARKER_BODY),            # not .md
    ("run_complete_20260808T235122Z.md", "arbitrary prose"),       # no marker shape
    ("run_complete_20260808T235122Z.md", None),                    # unreadable
])
def test_everything_uncertain_defaults_to_record(name, body):
    assert policy.classify(name, body) == policy.RECORD


def test_an_unreadable_file_on_disk_is_record(tmp_path):
    """FAIL-SAFE: a read error must never authorise a move out of the record."""
    p = tmp_path / "run_complete_20260808T235122Z.md"
    p.write_text(MARKER_BODY)
    p.chmod(0o000)
    try:
        if p.read_text(errors="replace"):  # running as root: the chmod is not a real denial
            pytest.skip("filesystem permissions not enforced for this user")
    except OSError:
        pass
    assert policy.classify_path(p) == policy.RECORD
    p.chmod(0o644)


def test_classifier_against_the_real_corpus_on_disk():
    """Put the criterion on trial with real inputs, not fixtures.

    Every real director/advisor/worker doc in the record must classify RECORD,
    and every real marker (wherever it is now filed) must classify EXHAUST.
    The vacuity guard is the point: without it this passes on an empty corpus.
    """
    if not policy.DONE_DIR.is_dir():
        pytest.fail("docs/staging/done/ is missing -- the corpus this control needs is gone")

    instructions = [
        p for p in policy.DONE_DIR.iterdir()
        if p.is_file() and p.suffix == ".md"
        and not any(p.name.startswith(x) for x in policy.EXHAUST_PREFIXES)
    ]
    markers = list(policy.iter_marker_paths("run_complete_"))

    assert len(instructions) >= 20, f"vacuity guard: only {len(instructions)} instructions in the corpus"
    assert len(markers) >= 20, f"vacuity guard: only {len(markers)} markers in the corpus"

    misfiled = [p.name for p in instructions if policy.classify_path(p) == policy.EXHAUST]
    assert misfiled == [], f"instructions classified as exhaust: {misfiled[:10]}"

    unmoved = [p.name for p in markers[:200] if policy.classify_path(p) != policy.EXHAUST]
    assert unmoved == [], f"real markers the policy would leave in the record: {unmoved[:10]}"


# --------------------------------------------------------------------------
# The move: nothing lost
# --------------------------------------------------------------------------

def test_sweep_moves_only_exhaust_and_conserves_the_count(staging):
    moves, report = _sweep(staging)
    assert sorted(m["name"] for m in moves) == [
        "run_complete_20260618T052611Z.md",
        "run_complete_20260719T101112Z.md",
        "run_complete_20260808T235122Z.md",
    ]
    assert report["count_before"] == report["count_after"] == 5
    assert len(report["moved"]) == 3
    assert report["conflicts"] == []
    # The record keeps exactly the instructions.
    assert sorted(p.name for p in staging.iterdir()) == [
        "ADVISOR_STEER_M2_OPEN.md", "from_rich_20260729_182313.md",
    ]


def test_moved_files_are_partitioned_by_their_own_stamp(staging):
    _sweep(staging)
    exhaust = staging.parent / "exhaust"
    assert (exhaust / "2026-06" / "run_complete_20260618T052611Z.md").is_file()
    assert (exhaust / "2026-07" / "run_complete_20260719T101112Z.md").is_file()
    assert (exhaust / "2026-08" / "run_complete_20260808T235122Z.md").is_file()


def test_content_survives_the_move_byte_for_byte(staging):
    _sweep(staging)
    moved = staging.parent / "exhaust" / "2026-08" / "run_complete_20260808T235122Z.md"
    assert moved.read_text() == MARKER_BODY


def test_an_unparseable_stamp_still_lands_somewhere_findable(staging):
    (staging / "run_complete_garbage.md").write_text(MARKER_BODY)
    _sweep(staging)
    assert (staging.parent / "exhaust" / "undated" / "run_complete_garbage.md").is_file()
    assert policy.locate("run_complete_garbage.md", done_dir=staging) is not None


def test_dry_run_moves_nothing(staging):
    moves, report = _sweep(staging, apply=False)
    assert len(moves) == 3 and report["moved"] == []
    assert (staging / "run_complete_20260808T235122Z.md").is_file()
    assert not (staging.parent / "exhaust").exists()


def test_a_destination_collision_is_reported_not_overwritten(staging):
    exhaust = staging.parent / "exhaust" / "2026-08"
    exhaust.mkdir(parents=True)
    (exhaust / "run_complete_20260808T235122Z.md").write_text("DIFFERENT CONTENT")
    moves, report = _sweep(staging)
    assert report["conflicts"] == ["run_complete_20260808T235122Z.md"]
    assert (exhaust / "run_complete_20260808T235122Z.md").read_text() == "DIFFERENT CONTENT"
    assert (staging / "run_complete_20260808T235122Z.md").is_file()  # source kept, not deleted
    assert report["count_before"] == report["count_after"]


def test_an_identical_file_already_filed_is_not_a_conflict(staging):
    exhaust = staging.parent / "exhaust" / "2026-08"
    exhaust.mkdir(parents=True)
    (exhaust / "run_complete_20260808T235122Z.md").write_text(MARKER_BODY)
    _moves, report = _sweep(staging)
    assert report["already_there"] == ["run_complete_20260808T235122Z.md"]
    assert report["conflicts"] == []


# --------------------------------------------------------------------------
# The manifest and findability -- the mirror risk the atom named
# --------------------------------------------------------------------------

def test_manifest_records_the_old_path_for_every_move(staging):
    _sweep(staging)
    manifest = staging.parent / "exhaust" / policy.MANIFEST_NAME
    entries = policy.read_manifest(manifest)
    assert len(entries) == 3
    for e in entries:
        assert e["old_path"].endswith(e["name"]) and "done" in e["old_path"]
        assert e["new_path"].endswith(e["name"]) and "exhaust" in e["new_path"]
        assert e["classified"] == policy.EXHAUST and e["moved_at"].endswith("Z")


def test_manifest_is_append_only_across_sweeps(staging):
    _sweep(staging)
    manifest = staging.parent / "exhaust" / policy.MANIFEST_NAME
    first = manifest.read_text()
    (staging / "run_complete_20260809T010101Z.md").write_text(MARKER_BODY)
    _sweep(staging)
    assert manifest.read_text().startswith(first)
    assert len(policy.read_manifest(manifest)) == 4


def test_a_malformed_manifest_line_does_not_hide_the_rest(staging):
    _sweep(staging)
    manifest = staging.parent / "exhaust" / policy.MANIFEST_NAME
    manifest.write_text("{not json\n" + manifest.read_text())
    assert len(policy.read_manifest(manifest)) == 3


def test_locate_finds_a_marker_after_it_moved(staging):
    _sweep(staging)
    found = policy.locate("run_complete_20260808T235122Z.md", done_dir=staging)
    assert found is not None and found.parent.name == "2026-08"
    assert policy.locate("ADVISOR_STEER_M2_OPEN.md", done_dir=staging) == staging / "ADVISOR_STEER_M2_OPEN.md"
    assert policy.locate("never_existed.md", done_dir=staging) is None


def test_iter_marker_paths_spans_done_and_exhaust(staging):
    before = {p.name for p in policy.iter_marker_paths("run_complete_", done_dir=staging)}
    _sweep(staging)
    after = {p.name for p in policy.iter_marker_paths("run_complete_", done_dir=staging)}
    assert before == after and len(after) == 3


# --------------------------------------------------------------------------
# verify() and the retention trigger: controls that can fail
# --------------------------------------------------------------------------

def test_verify_is_clean_after_a_sweep(staging):
    _sweep(staging)
    exhaust = staging.parent / "exhaust"
    assert policy.verify(exhaust / policy.MANIFEST_NAME, exhaust) == []


def test_verify_fires_when_a_moved_file_disappears(staging):
    """MUTATION: delete one moved file. A verifier that still reports clean is
    not a record-integrity control at all."""
    _sweep(staging)
    exhaust = staging.parent / "exhaust"
    (exhaust / "2026-08" / "run_complete_20260808T235122Z.md").unlink()
    problems = policy.verify(exhaust / policy.MANIFEST_NAME, exhaust)
    assert [p["name"] for p in problems] == ["run_complete_20260808T235122Z.md"]


def test_verify_fires_on_an_entry_with_no_new_path(staging):
    _sweep(staging)
    exhaust = staging.parent / "exhaust"
    manifest = exhaust / policy.MANIFEST_NAME
    manifest.write_text(manifest.read_text() + json.dumps({"name": "orphan.md"}) + "\n")
    assert any(p["name"] == "orphan.md" for p in policy.verify(manifest, exhaust))


def test_retention_review_fires_both_ways(staging, monkeypatch):
    _sweep(staging)
    exhaust = staging.parent / "exhaust"
    assert policy.retention_review_due(exhaust) == []
    monkeypatch.setattr(policy, "REVIEW_PARTITION_FILES", 0)
    assert policy.retention_review_due(exhaust) == ["2026-06", "2026-07", "2026-08"]


def test_partition_counts_reports_the_tree(staging):
    _sweep(staging)
    assert policy.partition_counts(staging.parent / "exhaust") == {
        "2026-06": 1, "2026-07": 1, "2026-08": 1,
    }


def test_the_exhaust_tree_is_derived_from_the_given_done_dir(tmp_path):
    """Test isolation: a redirected staging root must NEVER reach the real
    docs/staging/exhaust -- that is the leak that makes a tmp-dir fixture
    quietly assert on live state."""
    done = tmp_path / "staging" / "done"
    assert policy._exhaust_dir_for(done) == tmp_path / "staging" / "exhaust"
    assert policy._exhaust_dir_for(done) != policy.EXHAUST_DIR


# --------------------------------------------------------------------------
# The consumers: the move must not wind a published clock backwards
# --------------------------------------------------------------------------

def test_background_worker_finds_the_supersession_frontier_in_exhaust(staging):
    """background_worker's frontier used to glob done/. After the sweep done/
    holds no markers -- a frontier of None would classify every leftover
    marker as PENDING and republish a stale snapshot over current figures."""
    from background import background_worker
    assert background_worker._newest_published_stamp(staging) == "20260808T235122Z"
    _sweep(staging)
    assert background_worker._newest_published_stamp(staging) == "20260808T235122Z"


def test_process_run_complete_still_sees_a_duplicate_after_the_sweep(staging, monkeypatch):
    from background import process_run_complete
    monkeypatch.setattr(process_run_complete, "DONE_DIR", staging)
    _sweep(staging)
    rc = process_run_complete._process(str(staging.parent / "run_complete_20260808T235122Z.md"))
    assert rc == 0  # recognised as an already-processed duplicate, not an error
