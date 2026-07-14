"""H15_publish_gate_failure_alert -- mutation tests for the silent-wedge
detector in background/process_run_complete.py.

The worked incident (2026-07-14): the publish gate (fast-test suite) was
OOM-killed (rc=-9 -> "Tests FAILED - not committing") every ~10-min cycle for
~45min with run_complete markers piling up and NO alert. This suite proves the
control CAN FAIL on its own named defect (R15): it FIRES on N consecutive
failures, does NOT fire on a single transient failure or after recovery, is
re-armed by a cooldown (no spam), fails CLOSED on an unreadable gate-state, and
distinguishes an OOM/resource kill from a real test regression in the payload.
"""
import json

import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    # Redirect the durable action_needed register to a temp path so a fired
    # alert's best-effort register_item() never touches the real file.
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


class _Sink:
    def __init__(self):
        self.messages = []

    def __call__(self, msg, *a, **k):
        self.messages.append(msg)


# ── the control FIRES on its own named defect ────────────────────────────────

def test_fires_on_n_consecutive_failures(tmp_path):
    sink = _Sink()
    # Two failures: below threshold, silent.
    r1 = prc.record_publish_gate_failure("tests failed", rc=-9, now=0, send_ntfy_fn=sink)
    r2 = prc.record_publish_gate_failure("tests failed", rc=-9, now=10, send_ntfy_fn=sink)
    assert (r1["fired"], r2["fired"]) == (False, False)
    assert sink.messages == []
    # The third consecutive failure trips the alarm -- exactly ONCE.
    r3 = prc.record_publish_gate_failure("tests failed", rc=-9, now=20, send_ntfy_fn=sink)
    assert r3["fired"] is True
    assert len(sink.messages) == 1
    assert "[ACTION NEEDED]" in sink.messages[0]
    assert "WEDGED" in sink.messages[0]


def test_mutation_a_broken_threshold_would_be_caught(tmp_path):
    """If the counter never incremented (the fail-silent mutation), three
    failures would still show count==1 and never fire -- this asserts the
    opposite, so that mutation dies here."""
    sink = _Sink()
    for t in (0, 10, 20):
        res = prc.record_publish_gate_failure("x", rc=1, now=t, send_ntfy_fn=sink)
    assert res["count"] == 3
    assert res["fired"] is True


# ── the control does NOT fire on transient noise ─────────────────────────────

def test_single_transient_failure_does_not_fire(tmp_path):
    sink = _Sink()
    res = prc.record_publish_gate_failure("one blip", rc=1, now=0, send_ntfy_fn=sink)
    assert res["fired"] is False
    assert sink.messages == []


def test_does_not_fire_after_recovery(tmp_path):
    """Two failures, then a clean publish CLEARS the streak; a subsequent
    failure is only #1 again and stays silent."""
    sink = _Sink()
    prc.record_publish_gate_failure("f", rc=1, now=0, send_ntfy_fn=sink)
    prc.record_publish_gate_failure("f", rc=1, now=10, send_ntfy_fn=sink)
    prc.record_publish_gate_success(now=20)          # a run published cleanly
    res = prc.record_publish_gate_failure("f", rc=1, now=30, send_ntfy_fn=sink)
    assert res["count"] == 1
    assert res["fired"] is False
    assert sink.messages == []


def test_failures_outside_the_window_do_not_count(tmp_path):
    """Two failures long in the past fall out of the window, so a fresh
    failure is #1, not #3 -- a slow trickle over days is not a wedge."""
    sink = _Sink()
    w = prc.PUBLISH_GATE_WINDOW_SECONDS
    prc.record_publish_gate_failure("old", rc=1, now=0, send_ntfy_fn=sink)
    prc.record_publish_gate_failure("old", rc=1, now=1, send_ntfy_fn=sink)
    res = prc.record_publish_gate_failure("new", rc=1, now=2 * w, send_ntfy_fn=sink)
    assert res["count"] == 1
    assert res["fired"] is False


# ── re-arm / cooldown: no spam ───────────────────────────────────────────────

def test_cooldown_suppresses_repeat_alerts_then_re_arms(tmp_path):
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("f", rc=1, now=t, send_ntfy_fn=sink)
    assert len(sink.messages) == 1                    # fired at t=2
    # A further failure inside the cooldown window must NOT re-alert.
    res = prc.record_publish_gate_failure("f", rc=1, now=100, send_ntfy_fn=sink)
    assert res["threshold_met"] is True and res["fired"] is False
    assert len(sink.messages) == 1
    # After the cooldown elapses it re-arms and fires again (still wedged).
    later = 2 + prc.PUBLISH_GATE_COOLDOWN_SECONDS
    res = prc.record_publish_gate_failure("f", rc=1, now=later, send_ntfy_fn=sink)
    assert res["fired"] is True
    assert len(sink.messages) == 2


# ── FAIL-CLOSED on an unavailable gate-state (R15 fail-silent killer) ─────────

def test_unreadable_state_fails_closed_and_fires_immediately(tmp_path):
    prc.PUBLISH_GATE_STATE_FILE.write_text("{ this is not valid json")
    sink = _Sink()
    res = prc.record_publish_gate_failure("f", rc=1, now=0, send_ntfy_fn=sink)
    assert res["threshold_met"] is True
    assert res["fired"] is True
    assert len(sink.messages) == 1
    assert "fail-closed" in sink.messages[0]


def test_state_roundtrips_and_prunes_on_disk(tmp_path):
    prc.record_publish_gate_failure("f", rc=1, now=0)
    prc.record_publish_gate_failure("f", rc=1, now=10)
    on_disk = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert len(on_disk["failures"]) == 2
    assert on_disk["alerted_at"] is None


# ── OOM vs regression distinction in the payload ─────────────────────────────

def test_classify_resource_kill_vs_regression():
    assert prc._classify_gate_failure(-9) == "resource_kill"
    assert prc._classify_gate_failure(-15) == "signal_kill"
    assert prc._classify_gate_failure(1) == "test_regression"
    assert prc._classify_gate_failure(0) == "pass"
    assert prc._classify_gate_failure(None) == "unknown"


def test_payload_names_oom_for_sigkill(tmp_path):
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("tests OOM-killed", rc=-9, now=t, send_ntfy_fn=sink)
    assert "OOM" in sink.messages[0]
    assert "rc=-9" in sink.messages[0]


def test_payload_names_regression_for_positive_rc(tmp_path):
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("tests failed", rc=1, now=t, send_ntfy_fn=sink)
    assert "regression" in sink.messages[0].lower()


# ── recovery clears a durable action_needed item ─────────────────────────────

def test_success_resolves_open_action_needed_item(tmp_path):
    import background.action_needed as an
    sink = _Sink()
    for t in (0, 1, 2):
        prc.record_publish_gate_failure("f", rc=1, now=t, send_ntfy_fn=sink)
    # The fired alert registered a durable open item.
    assert any(i["item_id"] == prc.PUBLISH_GATE_ITEM_ID for i in an.open_items())
    prc.record_publish_gate_success(now=100)
    assert not any(i["item_id"] == prc.PUBLISH_GATE_ITEM_ID for i in an.open_items())
