import json
import time

import pytest

from background import ntfy_responder as responder
from background import action_needed as _action_needed

# check_once() mirrors inbound (ntfy_mirror has its own PYTEST_CURRENT_TEST
# guard) -- BUT _write_to_staging() writes to PROJECT_DIR/docs/staging and reads
# the real action_needed register, and had NO such guard. 2026-07-15 incident:
# test_check_once_acks_messages_not_sent_by_us ran check_once against REAL
# staging every suite invocation, leaking a "Hello Rich" from_rich_*.md each
# time (a 90-file flood that re-granted supervisor turns) AND, once a wave-10
# change made short messages stage while an action_needed item is open, failing
# and wedging the publish gate. This autouse fixture makes that structurally
# impossible: every test here writes staging to a tmp dir and sees an EMPTY
# register (tests that need open items override it locally).
@pytest.fixture(autouse=True)
def _isolate_staging_and_register(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    (tmp_path / "docs" / "staging").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(_action_needed, "open_items", lambda *a, **k: [])


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


def test_write_to_staging_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    path = responder._write_to_staging("Hello from Rich - this is a long enough message")
    assert path is not None
    assert path.exists()
    assert "Hello from Rich" in path.read_text()


def test_write_to_staging_rejects_short_message_when_nothing_is_open(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    import background.action_needed as an
    monkeypatch.setattr(an, "open_items", lambda *a, **k: [])
    assert responder._write_to_staging("Hi") is None


def test_write_to_staging_keeps_short_reply_when_a_director_question_is_open(tmp_path, monkeypatch):
    """The evaporation fix: a terse answer (A/B/C/D, 'yes') to an OPEN
    [ACTION NEEDED] item must NOT be dropped by the <25-char filter."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    import background.action_needed as an
    monkeypatch.setattr(an, "open_items", lambda *a, **k: [{"item_id": "q"}])
    path = responder._write_to_staging("B")
    assert path is not None and path.exists()
    assert "B" in path.read_text()


def test_write_to_staging_long_message_always_staged(tmp_path, monkeypatch):
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    import background.action_needed as an
    monkeypatch.setattr(an, "open_items", lambda *a, **k: [])  # even with nothing open
    path = responder._write_to_staging("this is a sufficiently long steering message")
    assert path is not None and path.exists()


def test_content_hash_consistent():
    h1 = responder._content_hash("Hello world")
    h2 = responder._content_hash("Hello world")
    assert h1 == h2


def test_content_hash_different_messages():
    h1 = responder._content_hash("Hello")
    h2 = responder._content_hash("World")
    assert h1 != h2


# --- Part B: inbound flood guard (2026-07-15) ---

def _feed(monkeypatch, msg_id, msg_time, message):
    class FakeResponse:
        text = json.dumps(
            {"event": "message", "id": msg_id, "time": msg_time, "message": message}
        )

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())


def test_flood_of_identical_messages_quarantines_and_spares_staging_root(tmp_path, monkeypatch):
    """R15 MUTATION TEST (2026-07-15, inbound_tagging_and_rate_guard part B):
    a 90s-cadence identical-body flood must QUARANTINE itself (preserved in
    docs/staging/quarantine/, never dropped) and NOT reach the scanned staging
    root; the status reply (the echo-loop driver) is suppressed for flood
    messages. Mutant this catches: delete the flood guard -> the identical
    bodies either silently vanish via replay-dedup (no preservation) or, if
    bodies vary, restage forever and echo.

    A companion test (test_normal_low_rate_message_still_stages) proves a normal
    low-rate real message still stages -- the control fires on the defect only,
    not on legitimate traffic."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    body = "Please kick off the overnight reconciliation batch now, thanks."
    staging_root = tmp_path / "docs" / "staging"
    quarantine_dir = staging_root / "quarantine"

    seen = []
    since = 0
    base = 100_000
    for i in range(8):  # 8 identical messages, 90s apart
        _feed(monkeypatch, f"flood-{i}", base + i * 90, body)
        since, seen = responder.check_once(since, seen)

    root_files = [p for p in staging_root.glob("from_rich_*.md")]  # non-recursive
    quarantined = list(quarantine_dir.glob("*.md")) if quarantine_dir.exists() else []

    # The sustained flood is quarantined, not staged. At most the very first
    # message can legitimately reach the root before the flood is provable.
    assert len(root_files) <= 1
    assert len(quarantined) >= 3
    # Exactly one flood alert (cooldown), and NO status reply for quarantined
    # messages -- suppressing the reply is what breaks the echo loop.
    assert len([m for m in sent if "[FLOOD GUARD]" in m]) == 1
    assert len([m for m in sent if "Sim:" in m]) <= 1


def test_flood_of_distinct_bodies_quarantines_on_rate(tmp_path, monkeypatch):
    """Raw-rate arm: an echo loop of DISTINCT bodies (dedup can't catch them)
    still trips FLOOD_MAX_IN_WINDOW and quarantines."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: None)

    staging_root = tmp_path / "docs" / "staging"
    quarantine_dir = staging_root / "quarantine"

    seen = []
    since = 0
    base = 200_000
    for i in range(responder.FLOOD_MAX_IN_WINDOW + 3):
        # distinct body each time, fast cadence within the window
        _feed(monkeypatch, f"rate-{i}", base + i * 30, f"unique steering note number {i} here")
        since, seen = responder.check_once(since, seen)

    quarantined = list(quarantine_dir.glob("*.md")) if quarantine_dir.exists() else []
    root_files = [p for p in staging_root.glob("from_rich_*.md")]
    assert len(quarantined) >= 3
    # Below-threshold messages staged; the flood tail did not.
    assert len(root_files) < responder.FLOOD_MAX_IN_WINDOW + 3


def test_normal_low_rate_message_still_stages(tmp_path, monkeypatch):
    """Fail-fires-on-defect-only half of the R15 pair: a single normal message
    stages to the scanned root and is NOT quarantined."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    _feed(monkeypatch, "real-1", 300_000, "Start the full 2016-2025 run when GPU is free.")
    responder.check_once(0, [])

    staging_root = tmp_path / "docs" / "staging"
    root_files = [p for p in staging_root.glob("from_rich_*.md")]
    quarantine_dir = staging_root / "quarantine"
    quarantined = list(quarantine_dir.glob("*.md")) if quarantine_dir.exists() else []

    assert len(root_files) == 1
    assert quarantined == []
    assert not any("[FLOOD GUARD]" in m for m in sent)
    assert any("Sim:" in m for m in sent)  # normal status reply sent


def test_flood_alert_respects_cooldown_across_calls(tmp_path, monkeypatch):
    """Only ONE [FLOOD GUARD] alert per cooldown, even across many flood
    messages -- a flood must not itself become an alert flood."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)

    sent = []
    monkeypatch.setattr(responder, "send_ntfy", lambda msg, headers=None: sent.append(msg))

    body = "identical machine cadence body repeated over and over again"
    seen = []
    since = 0
    for i in range(12):
        _feed(monkeypatch, f"c-{i}", 400_000 + i * 60, body)
        since, seen = responder.check_once(since, seen)

    assert len([m for m in sent if "[FLOOD GUARD]" in m]) == 1


def test_register_inbound_detects_identical_body_flood():
    state = {"events": [], "last_alert": 0}
    now = 500_000
    flooding = False
    for i in range(responder.FLOOD_IDENTICAL_THRESHOLD):
        flooding, reason = responder._register_inbound_and_detect_flood("hhh", now + i * 90, state)
    assert flooding is True
    assert "identical" in reason


def test_register_inbound_no_flood_below_threshold():
    state = {"events": [], "last_alert": 0}
    flooding, reason = responder._register_inbound_and_detect_flood("hhh", 600_000, state)
    assert flooding is False
    assert reason is None


def test_register_inbound_prunes_outside_window():
    state = {"events": [], "last_alert": 0}
    # Two identical hits far in the past, then one now: the old ones fall out of
    # the window, so a single fresh hit is NOT a flood.
    responder._register_inbound_and_detect_flood("hhh", 100, state)
    responder._register_inbound_and_detect_flood("hhh", 200, state)
    flooding, _ = responder._register_inbound_and_detect_flood(
        "hhh", 100 + responder.FLOOD_WINDOW_SECONDS + 10_000, state
    )
    assert flooding is False
    assert len(state["events"]) == 1
