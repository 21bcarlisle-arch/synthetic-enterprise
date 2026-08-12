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


# ── Delivery is observable (R15 both ways) ─────────────────────────────────────
# WORKER_FINDING_THE_ESCALATION_CHANNEL_IS_FAILING_SILENTLY_2026-08-10 +
# WORKER_FINDING_THE_ONLY_ESCALATION_CHANNEL_FAILS_SILENTLY_2026-08-10, part 1.
# The named defect: an HTTP 429 body parses as valid JSON with no `id`, so send_ntfy
# returned a bare None, logged nothing, and both audit trails recorded "out" anyway.
# Every test below reds if the failure branch is deleted or made unconditional.

_QUOTA_429_BODY = (
    '{"code":42908,"http":429,"error":"limit reached: daily message quota reached; '
    'increase your limits with a paid plan, see https://ntfy.sh"}'
)


def _fake_run_full(stdout, returncode=0, stderr=""):
    return lambda cmd, **kw: type(
        "R", (), {"stdout": stdout, "returncode": returncode, "stderr": stderr}
    )()


def _isolate_delivery(tmp_path, monkeypatch):
    """Redirect BOTH delivery paths -- record_delivery_outcome is a no-op under
    pytest until they are, so a test that forgets cannot pollute the real files."""
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", tmp_path / "sent.json")
    monkeypatch.setattr(ntfy_utils, "DELIVERY_LOG_FILE", tmp_path / "delivery-log.md")
    monkeypatch.setattr(ntfy_utils, "DELIVERY_STATE_FILE", tmp_path / "delivery-state.json")
    return tmp_path / "delivery-log.md", tmp_path / "delivery-state.json"


@pytest.mark.real_ntfy
def test_quota_drop_is_recorded_not_silent(tmp_path, monkeypatch):
    """THE finding, reproduced: a real ntfy daily-quota response. It must leave a
    record saying the director was NOT told, with the response body verbatim."""
    log, state = _isolate_delivery(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full(_QUOTA_429_BODY + "\n429"))

    assert ntfy_utils.send_ntfy("escalation", _allow_real_send=True) is None

    recorded = json.loads(state.read_text())
    assert recorded["delivered"] is False
    assert recorded["consecutive_failures"] == 1
    body = log.read_text()
    assert "NOT DELIVERED" in body
    assert "429" in body, "the HTTP status of the POST TO THE TOPIC must be recorded"
    assert "daily message quota reached" in body, "the diagnostic was in the body all along"


@pytest.mark.real_ntfy
def test_undelivered_message_is_not_recorded_as_sent(tmp_path, monkeypatch):
    """The second half of the defect: the mirror and the director-input log both
    appended an "out" entry regardless, so the audit trail claimed a delivery that
    did not happen. A dropped message must be recorded as dropped."""
    _isolate_delivery(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full(_QUOTA_429_BODY + "\n429"))
    seen = []
    monkeypatch.setattr(
        "background.ntfy_mirror.append_mirror_entry",
        lambda direction, message, topic=None: seen.append(("mirror", direction)))
    monkeypatch.setattr(
        "background.director_input_log.append_entry",
        lambda channel, content, direction="in", hmac_verified=None: seen.append(
            ("dlog", direction)))

    ntfy_utils.send_ntfy("escalation", _allow_real_send=True)

    assert seen == [("mirror", "out-undelivered"), ("dlog", "out-undelivered")]


@pytest.mark.real_ntfy
def test_a_healthy_send_stays_quiet(tmp_path, monkeypatch):
    """The other direction (R15): a control that fires on a GOOD send is noise. A
    delivered message records delivery in the state file and writes NO log line."""
    log, state = _isolate_delivery(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full('{"id": "abc123"}\n200'))

    assert ntfy_utils.send_ntfy("all fine", _allow_real_send=True) == "abc123"

    assert json.loads(state.read_text())["delivered"] is True
    assert not log.exists(), "a healthy send must not write a delivery-log line"


@pytest.mark.real_ntfy
def test_consecutive_drops_accumulate_and_recovery_is_a_transition(tmp_path, monkeypatch):
    """Sustained deafness must be countable without sending on the channel under
    test -- the finding established the channel cannot be probed cheaply (a HEAD
    on the topic 404s whether healthy or limited)."""
    log, state = _isolate_delivery(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full(_QUOTA_429_BODY + "\n429"))
    ntfy_utils.send_ntfy("one", _allow_real_send=True)
    ntfy_utils.send_ntfy("two", _allow_real_send=True)

    assert ntfy_utils.delivery_state()["consecutive_failures"] == 2

    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full('{"id": "back"}\n200'))
    ntfy_utils.send_ntfy("three", _allow_real_send=True)

    assert ntfy_utils.delivery_state()["consecutive_failures"] == 0
    assert "DELIVERED" in log.read_text().splitlines()[-1], "recovery IS a transition (R5)"


@pytest.mark.real_ntfy
def test_an_open_deafness_episode_cannot_be_shortened(tmp_path, monkeypatch):
    """Self-clearing-alarm census (PW2/PW4): `since_epoch` and `consecutive_failures`
    are episode-scoped, so a write that has NOT demonstrated recovery must not move the
    start or lower the count -- the 25h outage that paged as '30 seconds ago'."""
    _, state = _isolate_delivery(tmp_path, monkeypatch)
    state.write_text(json.dumps({
        "delivered": False, "consecutive_failures": 7,
        "since_epoch": 1000.0, "since": "2026-08-11T00:00:00Z",
    }))
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full(_QUOTA_429_BODY + "\n429"))

    ntfy_utils.send_ntfy("still deaf", _allow_real_send=True)

    recorded = json.loads(state.read_text())
    assert recorded["since_epoch"] == 1000.0, "the episode START must not move"
    assert recorded["consecutive_failures"] == 8, "the episode LENGTH must not shrink"


@pytest.mark.real_ntfy
def test_a_real_delivery_does_close_the_episode(tmp_path, monkeypatch):
    """The other direction: the guard must be able to CLEAR, or the alarm can never
    stand down. The close condition is a server-assigned message id -- evidence from
    the SERVER's response, never derived from this state file (R15 anti-tautology)."""
    _, state = _isolate_delivery(tmp_path, monkeypatch)
    state.write_text(json.dumps({
        "delivered": False, "consecutive_failures": 7, "since_epoch": 1000.0,
    }))
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run", _fake_run_full('{"id": "real-id"}\n200'))

    ntfy_utils.send_ntfy("back up", _allow_real_send=True)

    recorded = json.loads(state.read_text())
    assert recorded["delivered"] is True
    assert recorded["consecutive_failures"] == 0
    assert recorded["since_epoch"] > 1000.0


@pytest.mark.real_ntfy
def test_curl_transport_failure_is_distinguished_from_a_quota_drop(tmp_path, monkeypatch):
    """A non-zero curl rc (no network) and a 429 are different outcomes; the record
    must carry enough to tell them apart."""
    log, _ = _isolate_delivery(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ntfy_utils.subprocess, "run",
        _fake_run_full("", returncode=6, stderr="curl: (6) Could not resolve host"))

    assert ntfy_utils.send_ntfy("escalation", _allow_real_send=True) is None

    body = log.read_text()
    assert "rc=6" in body and "Could not resolve host" in body


def test_delivery_recording_is_a_no_op_until_a_test_isolates_it(monkeypatch):
    """Structural isolation, WITHOUT making the mechanism unfalsifiable: under
    pytest the recorder no-ops while either path is still the real one, so no test
    can pollute the live files -- but a test that redirects both (above) exercises
    the real body. A blanket PYTEST_CURRENT_TEST guard would make this control
    untestable, which is the R15 defect class it exists to fix."""
    before = ntfy_utils.DELIVERY_STATE_FILE.read_text() if (
        ntfy_utils.DELIVERY_STATE_FILE.is_file()) else None
    ntfy_utils.record_delivery_outcome(False, "synthetic test detail, must not be written")
    after = ntfy_utils.DELIVERY_STATE_FILE.read_text() if (
        ntfy_utils.DELIVERY_STATE_FILE.is_file()) else None
    assert after == before


def test_trailing_status_split_tolerates_a_body_with_no_status():
    """An older fake subprocess.run returns a bare JSON body with no -w suffix; it
    must not be mangled into an unparseable string."""
    assert ntfy_utils._split_trailing_status('{"id": "x"}') == ('{"id": "x"}', None)
    assert ntfy_utils._split_trailing_status('{"id": "x"}\n200') == ('{"id": "x"}', "200")
    assert ntfy_utils._split_trailing_status("\n429") == ("", "429")


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
