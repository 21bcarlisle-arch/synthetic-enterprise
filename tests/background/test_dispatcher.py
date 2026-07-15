"""Tests for background/dispatcher.py — intelligent message classifier and router.

PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md): the dispatcher no
longer types URGENT messages into the live pane. The _relay_to_claude /
_pending_urgent / _attempt_pending_urgent injection path is DELETED. URGENT now
means: prepend a header + send a high-priority NTFY + leave the file in staging
for the pull-loop draw. Classification and routing are unchanged.
"""
from pathlib import Path

from background import dispatcher


def _make_staging_file(staging_dir: Path, name: str, message: str) -> Path:
    path = staging_dir / name
    path.write_text(f"# Inbound NTFY message from Rich\n\n{message}\n")
    return path


def test_dispatcher_has_no_pane_injection_api():
    """The injection path is structurally gone."""
    for removed in ("_relay_to_claude", "_pending_urgent", "_attempt_pending_urgent",
                    "send_keys_when_idle"):
        assert not hasattr(dispatcher, removed), f"dispatcher.{removed} must be deleted"


def test_classify_message_returns_urgent_for_correctness_problem(monkeypatch):
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "urgent")
    result = dispatcher.classify_message("gross margin looks completely wrong")
    assert result == "urgent"


def test_classify_message_returns_fyi_for_acknowledgement(monkeypatch):
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "fyi")
    result = dispatcher.classify_message("ok")
    assert result == "fyi"


def test_classify_message_returns_normal_for_instruction(monkeypatch):
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "normal")
    result = dispatcher.classify_message("run the phase 9b simulation when GPU is free")
    assert result == "normal"


def test_classify_message_falls_back_to_normal_on_qwen_unavailable(monkeypatch):
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "")
    result = dispatcher.classify_message("anything")
    assert result == "normal"


def test_urgent_routing_sends_ntfy_headers_and_leaves_file_in_staging(tmp_path, monkeypatch):
    """route_message() classifies, prepends the URGENT header, and sends one
    high-priority NTFY -- then LEAVES the file in staging for the pull-loop draw.
    No pane injection, no in-memory relay queue."""
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "urgent")

    sent = []
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    path = _make_staging_file(tmp_path, "from_rich_001.md", "the P&L is completely wrong")

    seen = dispatcher.check_once({})

    assert seen.get("from_rich_001.md") == "urgent"
    assert len(sent) == 1
    assert "URGENT" in sent[0]
    # File still in staging (served by the pull-loop draw), with URGENT header.
    assert path.exists()
    assert "URGENT" in path.read_text()


def test_fyi_routing_moves_file_to_fyi_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "fyi")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)

    path = _make_staging_file(tmp_path, "from_rich_002.md", "ok thanks")

    seen = dispatcher.check_once({})

    assert seen.get("from_rich_002.md") == "fyi"
    assert not path.exists()
    assert (tmp_path / "fyi" / "from_rich_002.md").exists()


def test_normal_routing_leaves_file_in_staging_with_header(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "normal")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)

    path = _make_staging_file(tmp_path, "from_rich_003.md", "start phase 10 when ready")

    seen = dispatcher.check_once({})

    assert seen.get("from_rich_003.md") == "normal"
    assert path.exists()
    assert "NORMAL" in path.read_text()


def test_already_seen_files_not_reclassified(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "urgent")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)

    _make_staging_file(tmp_path, "from_rich_004.md", "test message")

    already_seen = {"from_rich_004.md": "normal"}
    seen = dispatcher.check_once(already_seen)

    assert seen.get("from_rich_004.md") == "normal"


def test_seen_state_persisted_across_calls(tmp_path, monkeypatch):
    state_file = tmp_path / "seen.json"
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", state_file)
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "normal")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)

    _make_staging_file(tmp_path, "from_rich_005.md", "build something new")

    seen = dispatcher.check_once({})
    assert "from_rich_005.md" in seen

    loaded = dispatcher._load_seen()
    assert "from_rich_005.md" in loaded


def test_already_processed_files_skipped_on_restart(tmp_path, monkeypatch):
    """Files that already have a Dispatcher header should not be re-classified or re-notified."""
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "urgent")
    sent = []
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    path = tmp_path / "from_rich_006.md"
    path.write_text(
        "<!-- Dispatcher: URGENT (classified 2026-06-29 11:00 UTC) -->\n"
        "# Inbound NTFY message from Rich\n\nsome old urgent message\n"
    )

    seen = dispatcher.check_once({})

    assert seen.get("from_rich_006.md") == "already-processed"
    assert len(sent) == 0  # no NTFY re-sent


def test_classify_message_strips_whitespace_from_qwen_output(monkeypatch):
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "  urgent  ")
    result = dispatcher.classify_message("something is wrong")
    assert result in ("urgent", "normal", "fyi")


def test_check_once_ignores_non_md_files(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "normal")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)
    (tmp_path / "some_config.json").write_text("{}")
    seen = dispatcher.check_once({})
    assert "some_config.json" not in seen


def test_check_once_empty_staging_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)
    seen = dispatcher.check_once({})
    assert seen == {}
