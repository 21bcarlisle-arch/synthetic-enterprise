"""Tests for background/secrets_location.py -- Option 2 floor (secrets out
of the working tree, with a safe fallback during the transition)."""
from pathlib import Path

from background import secrets_location as sl


def test_prefers_new_location_when_file_exists_there(tmp_path, monkeypatch):
    new_dir = tmp_path / "new"
    old_dir = tmp_path / "old"
    new_dir.mkdir()
    old_dir.mkdir()
    (new_dir / ".env.test").write_text("new content")
    (old_dir / ".env.test").write_text("old content")
    monkeypatch.setattr(sl, "NEW_SECRETS_DIR", new_dir)
    monkeypatch.setattr(sl, "OLD_SECRETS_DIR", old_dir)

    result = sl.resolve_secret_file(".env.test")
    assert result == new_dir / ".env.test"


def test_falls_back_to_old_location_when_new_missing(tmp_path, monkeypatch):
    new_dir = tmp_path / "new"
    old_dir = tmp_path / "old"
    new_dir.mkdir()
    old_dir.mkdir()
    (old_dir / ".env.test").write_text("old content")
    monkeypatch.setattr(sl, "NEW_SECRETS_DIR", new_dir)
    monkeypatch.setattr(sl, "OLD_SECRETS_DIR", old_dir)

    result = sl.resolve_secret_file(".env.test")
    assert result == old_dir / ".env.test"


def test_returns_old_path_even_if_neither_exists(tmp_path, monkeypatch):
    """Never raises -- callers already handle a missing file (warning log,
    not a crash), so this just returns a plausible path for that existing
    error path to report."""
    new_dir = tmp_path / "new"
    old_dir = tmp_path / "old"
    monkeypatch.setattr(sl, "NEW_SECRETS_DIR", new_dir)
    monkeypatch.setattr(sl, "OLD_SECRETS_DIR", old_dir)

    result = sl.resolve_secret_file(".env.nonexistent")
    assert result == old_dir / ".env.nonexistent"


def test_real_new_secrets_dir_exists_and_is_properly_permissioned():
    """Confirms the actual Option 2 migration happened on this machine --
    not just that the resolution logic is correct in the abstract."""
    assert sl.NEW_SECRETS_DIR.is_dir()
    mode = oct(sl.NEW_SECRETS_DIR.stat().st_mode)[-3:]
    assert mode == "700"
