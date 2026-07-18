import json

import pytest

from background import ntfy_utils

# send_ntfy() mirrors every call (ADVISOR_VISIBILITY.md's background/ntfy_mirror.py)
# -- no per-file isolation needed here: ntfy_mirror.append_mirror_entry() has its
# own structural PYTEST_CURRENT_TEST guard (same pattern as tmux_relay.py), so it's
# a no-op under this whole suite regardless of what any individual test mocks.


def _fake_run(stdout):
    return lambda cmd, **kw: type("R", (), {"stdout": stdout})()


@pytest.mark.real_ntfy
def test_send_ntfy_records_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"id": "abc123"}'))

    msg_id = ntfy_utils.send_ntfy("hello", _allow_real_send=True)

    assert msg_id == "abc123"
    assert json.loads(sent_ids_file.read_text()) == ["abc123"]


@pytest.mark.real_ntfy
def test_send_ntfy_handles_unparseable_response(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run("not json"))

    msg_id = ntfy_utils.send_ntfy("hello", _allow_real_send=True)

    assert msg_id is None
    assert not sent_ids_file.exists()


def test_was_sent_by_us_true_for_recorded_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    sent_ids_file.write_text(json.dumps(["id1", "id2"]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    assert ntfy_utils.was_sent_by_us("id1") is True
    assert ntfy_utils.was_sent_by_us("id3") is False


def test_was_sent_by_us_false_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", tmp_path / "missing.json")
    assert ntfy_utils.was_sent_by_us("id1") is False


def test_was_sent_by_us_false_for_none_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    sent_ids_file.write_text(json.dumps(["id1"]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    assert ntfy_utils.was_sent_by_us(None) is False


def test_record_sent_id_caps_at_max_entries(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils, "MAX_SENT_IDS", 3)

    for i in range(5):
        ntfy_utils.record_sent_id(f"id{i}")

    assert json.loads(sent_ids_file.read_text()) == ["id2", "id3", "id4"]


@pytest.mark.real_ntfy
def test_send_ntfy_appends_to_existing_ids(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    import json as _json
    sent_ids_file.write_text(_json.dumps(["existing"]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"id": "new123"}'))

    ntfy_utils.send_ntfy("hello", _allow_real_send=True)

    ids = _json.loads(sent_ids_file.read_text())
    assert "existing" in ids
    assert "new123" in ids


def test_record_sent_id_creates_file_if_missing(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "missing.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    ntfy_utils.record_sent_id("newid")

    import json as _json
    assert _json.loads(sent_ids_file.read_text()) == ["newid"]


def test_was_sent_by_us_empty_file(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "empty.json"
    import json as _json
    sent_ids_file.write_text(_json.dumps([]))
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)

    assert ntfy_utils.was_sent_by_us("id1") is False


@pytest.mark.real_ntfy
def test_send_ntfy_no_id_key_returns_none(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"error": "bad"}'))

    msg_id = ntfy_utils.send_ntfy("hello", _allow_real_send=True)

    assert msg_id is None


def test_max_sent_ids_constant_exists():
    assert hasattr(ntfy_utils, "MAX_SENT_IDS")
    assert ntfy_utils.MAX_SENT_IDS > 0


def test_record_sent_id_stores_single_id(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    ntfy_utils.record_sent_id("test-id-001")
    import json as _json
    ids = _json.loads(sent_ids_file.read_text())
    assert "test-id-001" in ids


def test_was_sent_by_us_returns_bool(tmp_path, monkeypatch):
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    result = ntfy_utils.was_sent_by_us("any-id")
    assert isinstance(result, bool)


@pytest.mark.real_ntfy
def test_daemon_sent_message_is_recognised_as_ours(tmp_path, monkeypatch):
    """Part A tagging invariant (2026-07-15): a message a daemon sends via
    send_ntfy must be was_sent_by_us()==True end to end, so the responder never
    captures our own [ACTION NEEDED]/[HEALTH CHECK] outbound as inbound (echo
    loop). Both calls read the SAME SENT_IDS_FILE."""
    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _fake_run('{"id": "daemon-xyz"}'))

    msg_id = ntfy_utils.send_ntfy("[HEALTH CHECK] Stack OK", _allow_real_send=True)

    assert msg_id == "daemon-xyz"
    assert ntfy_utils.was_sent_by_us(msg_id) is True


def test_record_sent_id_concurrent_writes_lose_no_ids(tmp_path, monkeypatch):
    """R15 mutation test for Part A: the tagging control's named defect is a
    LOST id from a read-modify-write race between concurrent daemon senders --
    an unrecorded id makes was_sent_by_us() return False for our own outbound,
    the exact echo-loop cause. The flock in record_sent_id closes it.

    Mutant check: this test FAILS (loses ids) if the flock is removed and the
    read-append-write runs unserialised."""
    import threading

    sent_ids_file = tmp_path / "sent.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", sent_ids_file)
    monkeypatch.setattr(ntfy_utils, "MAX_SENT_IDS", 10_000)

    n = 120
    barrier = threading.Barrier(n)

    def worker(i: int) -> None:
        barrier.wait()  # maximise overlap on the critical section
        ntfy_utils.record_sent_id(f"id-{i}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    ids = json.loads(sent_ids_file.read_text())
    assert len(ids) == n
    assert len(set(ids)) == n
    for i in range(n):
        assert ntfy_utils.was_sent_by_us(f"id-{i}") is True


def test_ntfy_topic_raises_at_import_if_unset():
    """SE_NTFY_TOPIC has no committed fallback (2026-07-08 rotation,
    docs/staging/NTFY_CHANNEL_HARDENING.md) -- importing the module with the
    env var absent must fail loudly, not silently talk over a stale or
    absent topic.

    Runs in a clean subprocess rather than deleting+reimporting
    background.ntfy_utils in this process: an earlier version of this test
    did that in-process via monkeypatch.delitem(sys.modules, ...), which
    left the `background` PACKAGE's `.ntfy_utils` attribute (a side effect
    of the plain `importlib.import_module` calls used to restore state,
    which monkeypatch's sys.modules-dict-only undo does not touch) pointing
    at an orphaned module object for the rest of the test session --
    silently breaking every later `import background.ntfy_utils as nu`
    style patch (e.g. tests/tools/test_ntfy_digest.py), a real instance of
    the local-test-pollution failure class this session's incident note
    (docs/retrospectives/2026-07-08-test-suite-tmux-leak.md) already
    documented once. A subprocess can't contaminate this process's state."""
    import os
    import subprocess
    import sys

    env = {k: v for k, v in os.environ.items() if k != "SE_NTFY_TOPIC"}
    result = subprocess.run(
        [sys.executable, "-c", "import background.ntfy_utils"],
        cwd=str(__import__("pathlib").Path(__file__).resolve().parents[2]),
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert "SE_NTFY_TOPIC is not set" in result.stderr


def test_sign_wake_message_round_trips():
    signed = ntfy_utils.sign_wake_message("hello world", timestamp=1000)
    assert signed == (
        "hello world|1000|"
        + __import__("hmac").new(
            ntfy_utils.WAKE_HMAC_KEY.encode(), b"hello world|1000", __import__("hashlib").sha256
        ).hexdigest()
    )
    assert ntfy_utils.verify_wake_message(signed, max_age_seconds=float("inf")) == "hello world"


def test_verify_wake_message_rejects_tampered_signature():
    signed = ntfy_utils.sign_wake_message("real instruction", timestamp=1000)
    tampered = signed[:-1] + ("0" if signed[-1] != "0" else "1")
    assert ntfy_utils.verify_wake_message(tampered, max_age_seconds=float("inf")) is None


def test_verify_wake_message_rejects_tampered_text():
    signed = ntfy_utils.sign_wake_message("real instruction", timestamp=1000)
    text, ts, digest = signed.rsplit("|", 2)
    forged = f"{text} but with extra malicious content|{ts}|{digest}"
    assert ntfy_utils.verify_wake_message(forged, max_age_seconds=float("inf")) is None


def test_verify_wake_message_rejects_stale_timestamp():
    import time

    signed = ntfy_utils.sign_wake_message("old instruction", timestamp=int(time.time()) - 10_000)
    assert ntfy_utils.verify_wake_message(signed, max_age_seconds=300) is None


def test_verify_wake_message_rejects_malformed_input():
    assert ntfy_utils.verify_wake_message("not-a-signed-message") is None


def test_sign_wake_message_raises_without_hmac_key(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", None)
    import pytest as _pytest

    with _pytest.raises(RuntimeError, match="SE_WAKE_HMAC_KEY is not set"):
        ntfy_utils.sign_wake_message("hello")


def test_verify_wake_message_returns_none_without_hmac_key(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", None)
    assert ntfy_utils.verify_wake_message("anything|123|abc") is None


@pytest.mark.real_ntfy
def test_send_ntfy_is_a_no_op_under_pytest(monkeypatch):
    """THE test-spam class fix (2026-07-16): under pytest, send_ntfy must NEVER POST a
    real NTFY to the director's phone, even if a test forgets to mock it. PYTEST_CURRENT_
    TEST is set during every test; the guard returns a sentinel and no curl runs."""
    import background.ntfy_utils as nu
    called = {"curl": False}
    monkeypatch.setattr(nu.subprocess, "run", lambda *a, **k: called.__setitem__("curl", True))
    # PYTEST_CURRENT_TEST is set by pytest right now; assert the guard fires.
    result = nu.send_ntfy("[RETRO CADENCE] Retro cadence STALE: fake reason")
    assert result == "pytest-suppressed"
    assert called["curl"] is False, "send_ntfy must not run curl (real POST) under pytest"

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
