"""Tests for background/ntfy_mirror.py -- ADVISOR_VISIBILITY.md."""
from unittest.mock import patch

import pytest

from background import ntfy_mirror


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(ntfy_mirror, "MIRROR_FILE", tmp_path / "ntfy-mirror.md")
    # 2026-07-11 relocation (DIRECTOR_INPUT_LOG.md): append_mirror_entry()
    # now also commits+pushes to the private ops repo. Mocked here so no
    # test run ever touches the real synthetic-enterprise-ops repo --
    # matches the stricter isolation background/director_input_log.py's
    # own tests use, and avoids relying on "nothing to commit" being a
    # silent no-op (it isn't: `git add` on a path that was never created
    # in OPS_REPO_DIR at all -- because MIRROR_FILE is mocked to tmp_path
    # above -- fails loudly with exit 128, not silently).
    with patch("background.ntfy_mirror.commit_and_push"):
        yield


def test_scrub_secrets_removes_known_topic():
    result = ntfy_mirror.scrub_secrets("check the secret-topic-xyz for updates", topic="secret-topic-xyz")
    assert "secret-topic-xyz" not in result
    assert "[topic-scrubbed]" in result


def test_scrub_secrets_removes_hex_digest():
    result = ntfy_mirror.scrub_secrets(
        "wake signed with 1650f1781210d13f20009e6ac12d054b1a589c18da912f43b5afa14510911cd7"
    )
    assert "1650f1781210d13f20009e6ac12d054b1a589c18da912f43b5afa14510911cd7" not in result
    assert "[hex-scrubbed]" in result


def test_scrub_secrets_leaves_normal_text_untouched():
    result = ntfy_mirror.scrub_secrets("Phase 3 done, 25 new tests passing")
    assert result == "Phase 3 done, 25 new tests passing"


def test_scrub_secrets_short_hex_like_words_not_scrubbed():
    # A short id like a commit SHA prefix (7-8 chars) is not a secret and
    # must survive -- only long (32+) hex runs are stripped.
    result = ntfy_mirror.scrub_secrets("committed as d3a731b4")
    assert "d3a731b4" in result


def test_append_mirror_entry_noop_under_pytest():
    """The core guarantee (same pattern as tmux_relay.py's own guard test):
    since this whole suite runs under pytest, PYTEST_CURRENT_TEST is
    genuinely set right now -- this call must be a real, unmocked no-op,
    proving the structural guard works even for a test that never touches
    PYTEST_CURRENT_TEST itself."""
    import os
    assert os.environ.get("PYTEST_CURRENT_TEST") is not None
    ntfy_mirror.append_mirror_entry("out", "this must never actually be written")
    assert not ntfy_mirror.MIRROR_FILE.exists()


def test_append_mirror_entry_creates_file_with_header(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    ntfy_mirror.append_mirror_entry("out", "Phase 1 done")
    content = ntfy_mirror.MIRROR_FILE.read_text()
    assert "# NTFY Message Mirror" in content
    assert "[OUT] Phase 1 done" in content


def test_append_mirror_entry_direction_inbound(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    ntfy_mirror.append_mirror_entry("in", "please check the website")
    content = ntfy_mirror.MIRROR_FILE.read_text()
    assert "[IN] please check the website" in content


def test_append_mirror_entry_scrubs_topic(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    ntfy_mirror.append_mirror_entry("out", "posted to my-secret-topic-123 successfully", topic="my-secret-topic-123")
    content = ntfy_mirror.MIRROR_FILE.read_text()
    assert "my-secret-topic-123" not in content
    assert "[topic-scrubbed]" in content


def test_append_mirror_entry_scrubs_hex_signature(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    signed = "hello|1234567890|1650f1781210d13f20009e6ac12d054b1a589c18da912f43b5afa14510911cd7"
    ntfy_mirror.append_mirror_entry("out", signed)
    content = ntfy_mirror.MIRROR_FILE.read_text()
    assert "1650f1781210d13f20009e6ac12d054b1a589c18da912f43b5afa14510911cd7" not in content


def test_append_mirror_entry_appends_not_overwrites(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    ntfy_mirror.append_mirror_entry("out", "first message")
    ntfy_mirror.append_mirror_entry("in", "second message")
    content = ntfy_mirror.MIRROR_FILE.read_text()
    assert "first message" in content
    assert "second message" in content


def test_append_mirror_entry_rotates_at_max_entries(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(ntfy_mirror, "MAX_MIRROR_ENTRIES", 5)
    for i in range(10):
        ntfy_mirror.append_mirror_entry("out", f"message {i}")
    content = ntfy_mirror.MIRROR_FILE.read_text()
    assert "message 0" not in content  # rotated out
    assert "message 9" in content  # most recent survives
    entry_lines = [l for l in content.splitlines() if l.startswith("- [")]
    assert len(entry_lines) == 5


def test_append_mirror_entry_flattens_multiline_messages(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    ntfy_mirror.append_mirror_entry("out", "line one\nline two")
    content = ntfy_mirror.MIRROR_FILE.read_text()
    # Must not introduce a stray line that breaks the one-entry-per-line format.
    entry_lines = [l for l in content.splitlines() if l.startswith("- [")]
    assert len(entry_lines) == 1
    assert "line one" in entry_lines[0] and "line two" in entry_lines[0]
