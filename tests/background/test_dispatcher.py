"""Tests for background/dispatcher.py — intelligent message classifier and router."""

import json
from pathlib import Path

import pytest

from background import dispatcher


def _make_staging_file(staging_dir: Path, name: str, message: str) -> Path:
    path = staging_dir / name
    path.write_text(f"# Inbound NTFY message from Rich\n\n{message}\n")
    return path


def _reset_pending_urgent():
    dispatcher._pending_urgent.clear()


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


def test_urgent_routing_sends_ntfy_and_queues_wake(tmp_path, monkeypatch):
    """route_message() classifies/headers/NTFYs immediately, but only
    QUEUES the wake -- the actual idle-gated, verified send happens in
    main()'s loop via _attempt_pending_urgent(), so it can retry across
    cycles if the session is busy (root-cause fix, 2026-07-08)."""
    _reset_pending_urgent()
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "SESSION_NAME", "test_session")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "urgent")

    sent = []
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    path = _make_staging_file(tmp_path, "from_rich_001.md", "the P&L is completely wrong")

    seen = dispatcher.check_once({})

    assert "from_rich_001.md" in seen
    assert seen["from_rich_001.md"] == "urgent"
    assert len(sent) == 1
    assert "URGENT" in sent[0]
    assert "from_rich_001.md" in dispatcher._pending_urgent
    assert "the P&L is completely wrong" in dispatcher._pending_urgent["from_rich_001.md"]
    # File should still be in staging (not moved) but with urgency header
    assert path.exists()
    assert "URGENT" in path.read_text()


# ── Idle-gated verified relay + retry (root-cause fix, docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md, 2026-07-08) ──

def test_relay_to_claude_calls_send_keys_when_idle(monkeypatch):
    calls = []
    monkeypatch.setattr(
        dispatcher, "send_keys_when_idle",
        lambda session, text, marker: calls.append((session, text, marker)) or True,
    )
    result = dispatcher._relay_to_claude("urgent message")
    assert result is True
    assert len(calls) == 1
    session, text, marker = calls[0]
    assert session == dispatcher.SESSION_NAME
    assert "urgent message" in text
    assert marker


def test_relay_to_claude_returns_false_when_busy(monkeypatch):
    monkeypatch.setattr(dispatcher, "send_keys_when_idle", lambda session, text, marker: False)
    assert dispatcher._relay_to_claude("urgent message") is False


def test_attempt_pending_urgent_noop_when_empty(monkeypatch):
    _reset_pending_urgent()
    calls = []
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: calls.append(msg) or True)
    dispatcher._attempt_pending_urgent()
    assert calls == []


def test_attempt_pending_urgent_clears_on_success(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    _make_staging_file(tmp_path, "from_rich_010.md", "message text")
    _reset_pending_urgent()
    dispatcher._pending_urgent["from_rich_010.md"] = "message text"
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: True)
    monkeypatch.setattr(dispatcher, "log", lambda msg: None)

    dispatcher._attempt_pending_urgent()

    assert dispatcher._pending_urgent == {}


def test_attempt_pending_urgent_retains_on_failure(tmp_path, monkeypatch):
    """Session busy, file still staged (not yet archived) -- must stay
    queued for the next cycle's retry, never silently dropped (this is the
    exact live failure mode: an urgent message classified and queued, but
    the session was busy, so nothing should be marked delivered until it
    actually is)."""
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    _make_staging_file(tmp_path, "from_rich_011.md", "message text")
    _reset_pending_urgent()
    dispatcher._pending_urgent["from_rich_011.md"] = "message text"
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: False)
    monkeypatch.setattr(dispatcher, "log", lambda msg: None)

    dispatcher._attempt_pending_urgent()

    assert dispatcher._pending_urgent == {"from_rich_011.md": "message text"}


def test_attempt_pending_urgent_retries_independently_per_file(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    _make_staging_file(tmp_path, "A.md", "msg a")
    _make_staging_file(tmp_path, "B.md", "msg b")
    _reset_pending_urgent()
    dispatcher._pending_urgent["A.md"] = "msg a"
    dispatcher._pending_urgent["B.md"] = "msg b"
    # A succeeds, B stays busy
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: msg == "msg a")
    monkeypatch.setattr(dispatcher, "log", lambda msg: None)

    dispatcher._attempt_pending_urgent()

    assert dispatcher._pending_urgent == {"B.md": "msg b"}


def test_attempt_pending_urgent_drops_stale_entry_when_file_already_archived(tmp_path, monkeypatch):
    """2026-07-10 real observed bug: a file already fully actioned and
    moved to docs/staging/done/ (no longer present at its original
    STAGING_DIR path) must be dropped from the in-memory retry queue
    without needing a wake-delivery confirmation at all -- otherwise it
    retries "URGENT wake not yet delivered" forever, since a busy session
    (mid-turn, exactly the state that caused it to still be pending) never
    confirms delivery, producing an infinite loop of repeated identical
    doorbell text for an already-answered question (observed live: the
    same message retried every ~60s for 20+ minutes after being answered)."""
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    # Deliberately do NOT create the file -- simulates it having already
    # been moved to docs/staging/done/ by the session that answered it.
    _reset_pending_urgent()
    dispatcher._pending_urgent["from_rich_already_done.md"] = "message text"
    relay_calls = []
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: relay_calls.append(msg) or True)
    monkeypatch.setattr(dispatcher, "log", lambda msg: None)

    dispatcher._attempt_pending_urgent()

    assert dispatcher._pending_urgent == {}
    assert relay_calls == []  # never even attempted a wake for an already-resolved item


def test_attempt_pending_urgent_mixed_archived_and_still_pending(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    _make_staging_file(tmp_path, "still_pending.md", "msg pending")
    # "already_done.md" deliberately not created -- already archived.
    _reset_pending_urgent()
    dispatcher._pending_urgent["already_done.md"] = "msg done"
    dispatcher._pending_urgent["still_pending.md"] = "msg pending"
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: False)
    monkeypatch.setattr(dispatcher, "log", lambda msg: None)

    dispatcher._attempt_pending_urgent()

    assert dispatcher._pending_urgent == {"still_pending.md": "msg pending"}


def test_fyi_routing_moves_file_to_fyi_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "fyi")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda *a: None)

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
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda *a: None)

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
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda *a: None)

    _make_staging_file(tmp_path, "from_rich_004.md", "test message")

    already_seen = {"from_rich_004.md": "normal"}
    seen = dispatcher.check_once(already_seen)

    # Should not change the classification
    assert seen.get("from_rich_004.md") == "normal"


def test_seen_state_persisted_across_calls(tmp_path, monkeypatch):
    state_file = tmp_path / "seen.json"
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", state_file)
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dispatcher, "_call_qwen", lambda p, max_tokens=100: "normal")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda *a: None)

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
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda msg: None)

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
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda *a: None)
    (tmp_path / "some_config.json").write_text("{}")
    seen = dispatcher.check_once({})
    assert "some_config.json" not in seen


def test_check_once_empty_staging_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatcher, "_SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(dispatcher, "STAGING_DIR", tmp_path)
    monkeypatch.setattr(dispatcher, "FYI_DIR", tmp_path / "fyi")
    monkeypatch.setattr(dispatcher, "send_ntfy", lambda *a, **k: None)
    monkeypatch.setattr(dispatcher, "_relay_to_claude", lambda *a: None)
    seen = dispatcher.check_once({})
    assert seen == {}
