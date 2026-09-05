"""Tests for Remote Staging Bridge in staging_watcher.py."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def _run_returns(rc, stdout, stderr=""):
    return (rc, stdout, stderr)


# ---- _extract_advisor_staging_files ----

def test_extract_no_advisor_commits_returns_empty():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "Auto-process run complete", ""),
        ]
        result = _extract_advisor_staging_files("abc1234")
    assert result == []


def test_extract_advisor_commit_returns_staging_files():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "[ADVISOR-STAGED] Add phase OP proposal", ""),
            (0, "docs/staging/PHASE_OP_proposal.md\ndocs/README.md", ""),
        ]
        result = _extract_advisor_staging_files("abc1234")
    assert result == ["PHASE_OP_proposal.md"]


def test_extract_ignores_done_subdirectory():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "[ADVISOR-STAGED] Archive and add new", ""),
            (0, "docs/staging/done/old_phase.md\ndocs/staging/NEW_PHASE.md", ""),
        ]
        result = _extract_advisor_staging_files("abc1234")
    assert "old_phase.md" not in result
    assert "NEW_PHASE.md" in result


def test_extract_git_log_failure_returns_empty():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [(1, "", "fatal: bad object")]
    result = _extract_advisor_staging_files("abc1234")
    assert result == []


def test_extract_git_diff_failure_returns_empty():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "[ADVISOR-STAGED] something", ""),
            (1, "", "fatal"),
        ]
        result = _extract_advisor_staging_files("abc1234")
    assert result == []


def test_extract_ignores_gitkeep():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "[ADVISOR-STAGED] setup", ""),
            (0, "docs/staging/.gitkeep\ndocs/staging/NEW_PHASE.md", ""),
        ]
        result = _extract_advisor_staging_files("abc1234")
    assert ".gitkeep" not in result
    assert "NEW_PHASE.md" in result


def test_extract_multiple_advisor_files():
    from background.staging_watcher import _extract_advisor_staging_files
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "[ADVISOR-STAGED] Add two phases", ""),
            (0, "docs/staging/PHASE_A.md\ndocs/staging/PHASE_B.md", ""),
        ]
        result = _extract_advisor_staging_files("abc1234")
    assert "PHASE_A.md" in result and "PHASE_B.md" in result


# ---- check_remote ----

def test_check_remote_fetch_failure_returns_seen_unchanged():
    from background.staging_watcher import check_remote
    seen = {"existing.md"}
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.return_value = (1, "", "network error")
        result = check_remote(seen)
    assert result == seen


def test_check_remote_already_up_to_date():
    from background.staging_watcher import check_remote
    seen = {"existing.md"}
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "", ""),
            (0, "abc1234", ""),
            (0, "0", ""),
        ]
        result = check_remote(seen)
    assert result == seen


def test_check_remote_new_non_advisor_commits_returns_unchanged():
    from background.staging_watcher import check_remote
    seen = {"existing.md"}
    with patch("background.staging_watcher._run") as mock_run:
        mock_run.side_effect = [
            (0, "", ""),
            (0, "abc1234", ""),
            (0, "2", ""),
        ]
        with patch("background.staging_watcher._extract_advisor_staging_files", return_value=[]):
            result = check_remote(seen)
    assert result == seen


def _bridge(tmp_path, blob: bytes, *, names=("PHASE_OP.md",), rc=0, stderr=b""):
    """Drive `check_remote` through one extraction and return what `git show` handed the writer.

    The blob is delivered through `subprocess.run` and NOT through `_run`, because that is the
    seam the writer actually reads from: `_run` returns `stdout.strip()`, which is right for
    every caller that parses it and wrong for the one that writes bytes to a file.
    """
    from background.staging_watcher import check_remote

    def fake_raw(cmd, **kwargs):
        return MagicMock(returncode=rc, stdout=blob, stderr=stderr)

    with patch("background.staging_watcher._run") as mock_run, \
         patch("background.staging_watcher._extract_advisor_staging_files",
               return_value=list(names)), \
         patch("background.staging_watcher.STAGING_DIR", tmp_path), \
         patch("background.staging_watcher.subprocess.run", fake_raw), \
         patch("background.staging_watcher.log"):
        mock_run.side_effect = [(0, "", ""), (0, "abc1234", ""), (0, "3", "")]
        check_remote(set())


def test_check_remote_extracts_and_writes_advisor_file(tmp_path):
    file_content = b"# Phase OP proposal\n"
    _bridge(tmp_path, file_content)

    written = tmp_path / "PHASE_OP.md"
    assert written.exists()
    assert written.read_bytes() == file_content


def test_the_bridge_writes_origins_bytes_and_not_a_stripped_copy(tmp_path):
    """THE DEFECT (2026-09-05). The bridge read `_run`, whose contract is `stdout.strip()`, and
    wrote that to disk -- so every resurrected document differed from origin's blob by its
    trailing newline.

    ONE BYTE IS THE WHOLE COST. `origin_reconcile.identical_untracked_twins` clears a blocking
    path only when it is BYTE-IDENTICAL to what origin brings, and `advance_shared_tree` is
    all-or-nothing, so a single near-twin refuses the entire fast-forward. Measured live on
    2026-09-05: six documents this line had resurrected, each one newline short, and the advance
    naming all six in "10 of 18 blocking path(s) are NOT byte-identical".

    KEYED TO EQUALITY WITH THE BLOB, not to "ends with a newline" -- the second is today's
    symptom and would go green if the strip were replaced by a different mangling.
    """
    blob = b"# A staged document\n\nwith a body.\n"
    _bridge(tmp_path, blob)
    assert (tmp_path / "PHASE_OP.md").read_bytes() == blob, \
        "the local copy must be origin's blob byte-for-byte, or the twin sweep cannot clear it"


def test_a_blob_that_genuinely_has_no_trailing_newline_is_not_given_one(tmp_path):
    """THE NULL BESIDE IT. A writer that "fixes" the symptom by appending a newline passes the
    test above and fails here, and would create exactly the same one-byte divergence in the
    other direction for any blob origin stores without one.
    """
    blob = b"# No newline at the end of this one"
    _bridge(tmp_path, blob)
    assert (tmp_path / "PHASE_OP.md").read_bytes() == blob


def test_a_failed_extraction_writes_nothing(tmp_path):
    """FAIL CLOSED. A `git show` that could not read the blob must leave no file at all -- an
    empty document in the staging root rings the doorbell and wins draws.
    """
    _bridge(tmp_path, b"", rc=128, stderr=b"fatal: bad object")
    assert not (tmp_path / "PHASE_OP.md").exists()


@pytest.mark.parametrize("room", ["done", "in_progress", "records"])
def test_a_document_consumed_into_any_room_is_not_resurrected(tmp_path, room):
    """THE SECOND DEFECT AT THE SAME SITE. The guard listed `done/` and `in_progress/` as two
    hardcoded instances. `records/` -- the room whose whole claim is THIS IS NOT WORK AND NEVER
    WAS -- landed 2026-09-03 and reached neither, so every pre-registration dispositioned out of
    the work channel was written back into it on the next poll, at a 90-second cadence.

    PARAMETRISED OVER THE ROOMS THE GUARD CLAIMS TO COVER, so a fourth room added to
    `finding_classes.ROOM_DIRNAMES` without widening the guard reds here rather than being found
    in a wedge. The negative leg below is what stops a guard that refuses everything passing.
    """
    consumed = tmp_path / room
    consumed.mkdir()
    (consumed / "PHASE_OP.md").write_bytes(b"consumed here\n")

    _bridge(tmp_path, b"resurrected\n")
    assert not (tmp_path / "PHASE_OP.md").exists(), \
        f"a document consumed into {room}/ must not be written back into the work channel"


def test_the_room_guard_covers_every_room_the_frozen_tuple_names():
    """The parametrisation above is a list; this is the property. It reds when a room is added to
    `ROOM_DIRNAMES` and the cases above are not widened with it -- which is the way the previous
    two instance-fixes rotted.
    """
    from background import finding_classes
    assert set(finding_classes.ROOM_DIRNAMES) == {"done", "in_progress", "records"}, \
        ("ROOM_DIRNAMES gained or lost a room -- widen "
         "test_a_document_consumed_into_any_room_is_not_resurrected to match")


def test_a_document_in_no_room_IS_resurrected(tmp_path):
    """THE NULL. Without this, a guard that skipped every name -- or a bridge that had stopped
    writing at all -- would pass every assertion above. This is the branch the bridge exists for.
    """
    _bridge(tmp_path, b"resurrected\n")
    assert (tmp_path / "PHASE_OP.md").read_bytes() == b"resurrected\n"


def test_check_remote_skips_existing_file(tmp_path):
    from background.staging_watcher import check_remote

    existing = tmp_path / "PHASE_OP.md"
    existing.write_text("already here")

    with patch("background.staging_watcher._run") as mock_run, \
         patch("background.staging_watcher._extract_advisor_staging_files", return_value=["PHASE_OP.md"]), \
         patch("background.staging_watcher.STAGING_DIR", tmp_path), \
         patch("background.staging_watcher.log"):

        mock_run.side_effect = [
            (0, "", ""),
            (0, "abc1234", ""),
            (0, "1", ""),
        ]
        result = check_remote(set())

    assert existing.read_text() == "already here"
    assert mock_run.call_count == 3

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
