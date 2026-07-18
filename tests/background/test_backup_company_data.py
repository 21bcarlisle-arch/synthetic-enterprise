"""Tests for background/backup_company_data.py -- closes the
"unrecoverable canonical data" gap PRODUCTION_READINESS_EVIDENCE_PASS.md's
Part A found. Mocks commit_and_push throughout, matching this session's
established stricter isolation for anything touching the real ops repo."""
from unittest.mock import patch

from background import backup_company_data as bcd


def test_backs_up_existing_files_only(tmp_path, monkeypatch):
    src_dir = tmp_path / "source"
    src_dir.mkdir()
    (src_dir / "invoices.db").write_bytes(b"fake invoices data")
    (src_dir / "registry.db").write_bytes(b"fake registry data")
    # direct_debit.db and service_log.db deliberately absent

    backup_dir = tmp_path / "ops" / "backups" / "company_data"
    monkeypatch.setattr(bcd, "SOURCE_DIR", src_dir)
    monkeypatch.setattr(bcd, "BACKUP_DIR", backup_dir)

    with patch("background.backup_company_data.commit_and_push") as mock_push:
        result = bcd.backup_once()

    assert set(result) == {"invoices.db", "registry.db"}
    assert (backup_dir / "invoices.db").read_bytes() == b"fake invoices data"
    assert (backup_dir / "registry.db").read_bytes() == b"fake registry data"
    mock_push.assert_called_once()
    relpaths = mock_push.call_args[0][0]
    assert set(relpaths) == {"backups/company_data/invoices.db", "backups/company_data/registry.db"}


def test_no_source_files_backs_up_nothing(tmp_path, monkeypatch):
    src_dir = tmp_path / "empty_source"
    src_dir.mkdir()
    backup_dir = tmp_path / "ops" / "backups" / "company_data"
    monkeypatch.setattr(bcd, "SOURCE_DIR", src_dir)
    monkeypatch.setattr(bcd, "BACKUP_DIR", backup_dir)

    with patch("background.backup_company_data.commit_and_push") as mock_push:
        result = bcd.backup_once()

    assert result == []
    mock_push.assert_not_called()


def test_binary_content_preserved_exactly(tmp_path, monkeypatch):
    """SQLite files are binary -- confirms shutil.copy2 doesn't corrupt
    non-text bytes (e.g. a null byte, which a naive text-mode copy would mangle)."""
    src_dir = tmp_path / "source"
    src_dir.mkdir()
    binary_content = bytes([0, 1, 2, 255, 254, 0, 128])
    (src_dir / "direct_debit.db").write_bytes(binary_content)

    backup_dir = tmp_path / "ops" / "backups" / "company_data"
    monkeypatch.setattr(bcd, "SOURCE_DIR", src_dir)
    monkeypatch.setattr(bcd, "BACKUP_DIR", backup_dir)

    with patch("background.backup_company_data.commit_and_push"):
        bcd.backup_once()

    assert (backup_dir / "direct_debit.db").read_bytes() == binary_content


def test_creates_backup_dir_if_missing(tmp_path, monkeypatch):
    src_dir = tmp_path / "source"
    src_dir.mkdir()
    (src_dir / "service_log.db").write_bytes(b"log data")
    backup_dir = tmp_path / "does" / "not" / "exist" / "yet"
    monkeypatch.setattr(bcd, "SOURCE_DIR", src_dir)
    monkeypatch.setattr(bcd, "BACKUP_DIR", backup_dir)

    with patch("background.backup_company_data.commit_and_push"):
        bcd.backup_once()

    assert backup_dir.is_dir()
    assert (backup_dir / "service_log.db").is_file()

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
