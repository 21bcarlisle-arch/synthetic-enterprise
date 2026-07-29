import json
import os
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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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


# --- Inbound-as-instruction guard (2026-07-29, responder_inbound_not_instruction_guard) ---
# R15 both-ways: the guard must FIRE on the ntfy-app self-test (mutation catch) and
# must PASS THROUGH a genuine director steer (fires on the defect only).

# The exact machine bodies observed 2026-07-29 (from docs/staging/done/from_rich_*.md).
_ANDROID_SELFTEST = (
    "This is a test notification from the ntfy Android app. It has a level 3 "
    "priority. If you send another, it may look different."
)
_IOS_SELFTEST = (
    "This is a test notification from the ntfy iOS app. It has a level 1 priority."
)


def test_app_selftest_not_staged(tmp_path, monkeypatch):
    """MUTATION-CATCH half: the ntfy-app self-test notification must NOT be staged
    (staging = a supervisor turn = a model load). Neuter the guard (drop the
    `if _is_app_selftest(...)` return in _write_to_staging) and this reds -- the
    self-test stages a from_rich_*.md exactly as the 2026-07-29 incident did."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    assert responder._is_app_selftest(_ANDROID_SELFTEST) is True
    assert responder._is_app_selftest(_IOS_SELFTEST) is True
    assert responder._write_to_staging(_ANDROID_SELFTEST) is None
    assert responder._write_to_staging(_IOS_SELFTEST) is None
    # And nothing reached the scanned staging root.
    staging_root = tmp_path / "docs" / "staging"
    assert list(staging_root.glob("from_rich_*.md")) == [] if staging_root.exists() else True


def test_check_once_selftest_not_staged_and_classified_ping(tmp_path, monkeypatch):
    """End-to-end: an app self-test arriving via check_once is NOT staged and is
    NOT classified [instruction] -- so it can never re-grant a supervisor turn. The
    reply (if any) is a harmless status ack, never 'queued for Claude Code'."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)

    sent = []
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

    _feed(monkeypatch, "selftest-1", 700_000, _ANDROID_SELFTEST)
    responder.check_once(0, [])

    staging_root = tmp_path / "docs" / "staging"
    assert [p for p in staging_root.glob("from_rich_*.md")] == []
    assert not any("queued for Claude Code" in m for m in sent)
    assert not any("[instruction]" in m for m in sent)


def test_pass_through_real_directive_resembling_a_test(tmp_path, monkeypatch):
    """FIRES-ON-DEFECT-ONLY half: a genuine director steer that merely mentions the
    word 'test' is NOT caught by the guard -- it still stages. Guards the class
    against becoming a broad 'looks non-directive' filter that drops real steers."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    import background.action_needed as an
    monkeypatch.setattr(an, "open_items", lambda *a, **k: [])
    steer = "Add a mutation test for the notification guard and land it, thanks."
    assert responder._is_app_selftest(steer) is False
    path = responder._write_to_staging(steer)
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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: None)

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))

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

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


# ── PHONE-NATIVE AUTHORITY: responder ledgers a HMAC-verified RULING (director ratification 2026-07-22)
def test_maybe_ledger_director_ruling_writes_on_valid_signature(tmp_path, monkeypatch):
    import background.ntfy_utils as ntfy_utils
    from background import director_authority_channels as dac
    from background import gate_authorization as G
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", "test-key-responder")
    led = tmp_path / "gate_authorizations.jsonl"
    monkeypatch.setattr(G, "LEDGER_PATH", led)
    signed = ntfy_utils.sign_wake_message(dac._bound_signed_text("BUILD_OPEN", "AtomX"))
    entry = responder._maybe_ledger_director_ruling(signed)
    assert entry is not None and entry["action"] == "BUILD_OPEN" and entry["atom"] == "AtomX"
    assert entry["channel"] == dac.DIRECTOR_NTFY
    assert len(G.read_ledger(led)) == 1


def test_maybe_ledger_director_ruling_ignores_ordinary_message(tmp_path, monkeypatch):
    import background.ntfy_utils as ntfy_utils
    from background import gate_authorization as G
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", "test-key-responder")
    led = tmp_path / "gate_authorizations.jsonl"
    monkeypatch.setattr(G, "LEDGER_PATH", led)
    # An ordinary human message is not a signed RULING → nothing ledgered, no crash.
    assert responder._maybe_ledger_director_ruling("hey can you check the dashboard") is None
    assert G.read_ledger(led) == []


# --- At-most-once EXECUTION (2026-07-29, DIRECTOR_RULING_FIX_DOUBLE_MESSAGING) ---
# CAUSE, observed with evidence: two live ntfy_responder.py processes (PIDs
# 266098 and 419021). The responder log shows the SAME ntfy message id acked
# twice -- 'AK0UhbkAV2Ko' at 17:37:31 and again at 17:37:42, each staged as its
# own from_rich_*.md. Both pre-existing guards (`since`, `seen_hashes`) are
# per-process in-memory state, so neither could ever see a sibling consumer.

_DIRECTOR_MSG = (
    "Your backlog is in a document but the thing that picks your next job reads the map."
)


def _consumer_env(tmp_path, monkeypatch):
    """Wire one responder 'consumer' against the tmp project dir, capturing the
    replies it sends. Each check_once() call here stands for one process: it is
    handed a FRESH empty seen_hashes and a stale watermark, which is precisely
    the cross-process blindness that let the duplicate through."""
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(responder, "was_sent_by_us", lambda msg_id: False)
    sent = []
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))
    return sent


def test_same_message_delivered_twice_executes_exactly_once(tmp_path, monkeypatch):
    """R15 MUTATION-CATCH half: ONE director message read by TWO consumers must
    execute ONCE. Neuter the claim (drop the `if not claim_message(...)` guard in
    check_once) and this reds -- the message is staged twice and acked twice,
    reproducing the 2026-07-29 incident exactly."""
    sent = _consumer_env(tmp_path, monkeypatch)
    _feed(monkeypatch, "AK0UhbkAV2Ko", 700_000, _DIRECTOR_MSG)

    responder.check_once(0, [])  # consumer A
    responder.check_once(0, [])  # consumer B: same stale watermark, same message

    staged = list((tmp_path / "docs" / "staging").glob("from_rich_*.md"))
    assert len(staged) == 1, f"one message must stage once, got {[p.name for p in staged]}"
    assert len([m for m in sent if "[instruction]" in m]) == 1


def test_two_distinct_messages_with_identical_text_both_execute(tmp_path, monkeypatch):
    """R15 FIRES-ON-DEFECT-ONLY half: the guard must key on the ntfy message ID,
    not the body. Two genuinely different messages that happen to read the same
    (the director repeating himself deliberately) must BOTH execute. Swap
    _message_identity to a body hash and this reds -- the second is swallowed."""
    sent = _consumer_env(tmp_path, monkeypatch)

    _feed(monkeypatch, "msg-id-one", 700_000, _DIRECTOR_MSG)
    responder.check_once(0, [])
    _feed(monkeypatch, "msg-id-two", 700_001, _DIRECTOR_MSG)
    responder.check_once(0, [])

    staged = list((tmp_path / "docs" / "staging").glob("from_rich_*.md"))
    assert len(staged) == 2, f"two distinct messages must both stage, got {[p.name for p in staged]}"
    assert len([m for m in sent if "[instruction]" in m]) == 2


def test_claim_message_is_atomic_test_and_set(tmp_path, monkeypatch):
    """The primitive itself: exactly one caller wins a given identity."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    assert responder.claim_message("abc123") is True
    assert responder.claim_message("abc123") is False
    assert responder.claim_message("abc124") is True


def test_claim_message_fails_closed_when_ledger_unavailable(tmp_path, monkeypatch):
    """FAIL-CLOSED (R15): if the claim ledger cannot be written we CANNOT prove we
    won the claim, so we must NOT execute. A fail-OPEN here would restore
    double-execution the moment the disk misbehaves."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")

    def _boom(*a, **k):
        raise OSError("read-only filesystem")

    monkeypatch.setattr(responder.os, "open", _boom)
    assert responder.claim_message("whatever") is False


def test_message_identity_prefers_ntfy_id_and_is_filesystem_safe():
    assert responder._message_identity({"id": "AK0UhbkAV2Ko"}) == "AK0UhbkAV2Ko"
    # Distinct ids stay distinct even with an identical body.
    a = responder._message_identity({"id": "one", "message": "same"})
    b = responder._message_identity({"id": "two", "message": "same"})
    assert a != b
    # Path traversal in a hostile id can never escape the claims dir.
    assert "/" not in responder._message_identity({"id": "../../etc/passwd"})
    # No id -> deterministic body+time fallback, still distinguishing by time.
    c = responder._message_identity({"message": "same", "time": 1})
    d = responder._message_identity({"message": "same", "time": 2})
    assert c.startswith("h_") and c != d


def test_singleton_lock_admits_one_responder_only(tmp_path, monkeypatch):
    """R15: the ROOT cause was a second live daemon. The second acquirer must be
    refused. Delete the flock call and this reds."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    (tmp_path / "background").mkdir(parents=True, exist_ok=True)

    first = responder.acquire_singleton_lock()
    assert first is not None, "the first responder must get the lock"
    try:
        assert responder.acquire_singleton_lock() is None, "a second responder must be refused"
    finally:
        first.close()
    # Released on exit (the kernel drops flock when the holder dies) -> reusable.
    third = responder.acquire_singleton_lock()
    assert third is not None
    third.close()


def test_app_selftest_costs_nothing_at_all(tmp_path, monkeypatch):
    """The director's 'while you are in there': an ntfy-app self-test must be
    acknowledged-and-discarded without spawning anything -- no staging, no reply,
    and no claim-ledger entry. Move the guard back below the ledger/notify calls
    and the reply assertion reds."""
    sent = _consumer_env(tmp_path, monkeypatch)
    _feed(monkeypatch, "selftest-99", 700_000, _ANDROID_SELFTEST)
    responder.check_once(0, [])

    assert list((tmp_path / "docs" / "staging").glob("from_rich_*.md")) == []
    assert sent == [], f"a self-test must not even cost a reply, sent={sent}"
    assert not responder._claims_dir().exists() or list(responder._claims_dir().iterdir()) == []


def test_distinct_messages_in_the_same_second_do_not_overwrite(tmp_path, monkeypatch):
    """Dedup must never become message LOSS: two distinct instructions written in
    the same wall-clock second must both survive. Drop the collision uniquifier in
    _write_to_staging and this reds -- the second silently overwrites the first."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    first = responder._write_to_staging("First distinct director instruction, please act on it.")
    second = responder._write_to_staging("Second distinct director instruction, also act on it.")
    assert first != second
    assert first.exists() and second.exists()
    assert len(list((tmp_path / "docs" / "staging").glob("from_rich_*.md"))) == 2


def test_refused_instance_does_not_wipe_the_holders_pid_record(tmp_path, monkeypatch):
    """The lock file is the one artefact a human reads to ask WHO holds it. Opening it "w"
    truncated the holder's PID before the flock was even attempted, so a refused second
    instance left it empty -- the diagnostic lied. Restore `open(path, "w")` and this reds."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    (tmp_path / "background").mkdir(parents=True, exist_ok=True)
    holder = responder.acquire_singleton_lock()
    try:
        lock_file = tmp_path / "background" / responder.SINGLETON_LOCK_NAME
        assert lock_file.read_text().strip() == str(os.getpid())
        assert responder.acquire_singleton_lock() is None      # refused
        assert lock_file.read_text().strip() == str(os.getpid())  # record survived
    finally:
        holder.close()
