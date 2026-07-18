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


def test_check_remote_extracts_and_writes_advisor_file(tmp_path):
    file_content = "# Phase OP proposal"
    from background.staging_watcher import check_remote
    seen = set()

    with patch("background.staging_watcher._run") as mock_run, \
         patch("background.staging_watcher._extract_advisor_staging_files", return_value=["PHASE_OP.md"]), \
         patch("background.staging_watcher.STAGING_DIR", tmp_path), \
         patch("background.staging_watcher.log"):

        mock_run.side_effect = [
            (0, "", ""),
            (0, "abc1234", ""),
            (0, "3", ""),
            (0, file_content, ""),
        ]
        result = check_remote(seen)

    written = tmp_path / "PHASE_OP.md"
    assert written.exists()
    assert written.read_text() == file_content


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
