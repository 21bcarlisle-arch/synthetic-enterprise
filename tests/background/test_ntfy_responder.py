import json
import time

from background import ntfy_responder as responder


def test_run_progress_summary_no_active_run(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    assert responder._run_progress_summary() == "no active background simulation run"


def test_run_progress_summary_ignores_stale_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    stale = tmp_path / "old_run.log"
    stale.write_text("progress: 100 settlement periods processed (latest: 2016-01-01 period 1, treasury £100.00)")
    old_time = time.time() - responder.RUN_LOG_FRESH_SECONDS - 60
    import os
    os.utime(stale, (old_time, old_time))

    assert responder._run_progress_summary() == "no active background simulation run"


def test_run_progress_summary_parses_latest_progress_line(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    log = tmp_path / "phase6c_run.log"
    log.write_text(
        "  ... progress: 100 settlement periods processed (latest: 2016-01-01 period 1, treasury £100.00)\n"
        "  ... progress: 200 settlement periods processed (latest: 2016-01-02 period 1, treasury £101.50)\n"
    )

    summary = responder._run_progress_summary()
    assert "phase6c_run.log" in summary
    assert "200 periods processed" in summary
    assert "2016-01-02 period 1" in summary
    assert "£101.50" in summary


def test_run_progress_summary_counts_risk_committee_wakeups(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    log = tmp_path / "phase6c_run.log"
    log.write_text(
        "  ... progress: 100 settlement periods processed (latest: 2016-01-01 period 1, treasury £100.00)\n"
        "  [RISK COMMITTEE] Woken at 2016-01-01 — treasury £100.00\n"
    )

    summary = responder._run_progress_summary()
    assert "risk-committee wake-up" in summary


def test_check_once_skips_own_messages_and_advances_watermark(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: True)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    class FakeResponse:
        text = json.dumps({"event": "message", "id": "abc", "time": 1000, "message": "hello"})

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())

    new_since, _ = responder.check_once(500, [])
    assert new_since == 1000
    assert sent == []


def test_check_once_acks_messages_not_sent_by_us(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    class FakeResponse:
        text = json.dumps({"event": "message", "id": "abc", "time": 1000, "message": "Hello Rich"})

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())

    new_since, _ = responder.check_once(500, [])
    assert new_since == 1000
    assert len(sent) == 1
    # Short message ("Hello Rich" < 25 chars) → [status ping] classification, no staging file
    assert "status ping" in sent[0].lower()
    assert "Sim:" in sent[0]


def test_check_once_stages_substantive_messages(tmp_path, monkeypatch):
    """Inbound messages >= 25 chars are written to docs/staging/ as from_rich_*.md."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    long_message = "Start the full 2016-2025 run when GPU is free."

    class FakeResponse:
        text = json.dumps({"event": "message", "id": "xyz", "time": 2000, "message": long_message})

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())

    responder.check_once(500, [])

    staging_dir = tmp_path / "docs" / "staging"
    staged_files = list(staging_dir.glob("from_rich_*.md"))
    assert len(staged_files) == 1
    assert long_message in staged_files[0].read_text()
    # Dispatcher ack shows classification and action without file link
    assert "instruction" in sent[0].lower()
    assert "queued for Claude Code" in sent[0]


def test_check_once_ignores_messages_at_or_before_watermark(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    class FakeResponse:
        text = json.dumps({"event": "message", "id": "abc", "time": 1000, "message": "old message"})

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())

    new_since, _ = responder.check_once(1000, [])
    assert new_since == 1000
    assert sent == []


def test_check_once_drops_duplicate_content(tmp_path, monkeypatch):
    """Messages with identical content are dropped even with a new timestamp."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    message = "Phase 7b complete — ledger events wired."

    # Pre-populate seen_hashes with this message's hash
    existing_hash = responder._content_hash(message)

    class FakeResponse:
        text = json.dumps({"event": "message", "id": "new-id", "time": 9999, "message": message})

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())

    new_since, hashes = responder.check_once(500, [existing_hash])
    # Watermark advances (time > since) but message is not processed
    assert new_since == 9999
    assert sent == []
    # Hash still in hashes list
    assert existing_hash in hashes
