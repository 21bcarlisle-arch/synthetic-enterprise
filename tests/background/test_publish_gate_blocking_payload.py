"""The publish-gate alarm must carry the BLOCKING TEST -- R5's diagnostic payload, mechanised.

THE DEFECT THIS CLOSES (2026-08-10, eighth publish wedge). `_log_gate_failure_payload` has
always extracted the failing pytest node ids from the gate's own output -- and written them to a
log file that the alarm cannot read, because `record_publish_gate_failure` runs in a DIFFERENT
process (background_worker shells out to the publisher and sees only an exit code). The alarm was
therefore handed `reason="process_run_complete rc=1 on run_complete_<stamp>.md"`, which identifies
nothing, and filled the hole with `filed_findings()`: the eight most recently modified
WORKER_FINDING_*.md in staging, ranked by mtime, linked to the failure by nothing at all.

Measured outcome across the four preceding episodes (WORKER_REPORT_{PUBLISH,FIFTH,SIXTH}_WEDGE_*
and this one): 0/8, 0/8, 0/8, 0/8. The list was near-identical every time while the cause differed
every time. Meanwhile the drawn worker read "FILED FINDINGS ALREADY HOLDING THE SUSPECTS -- draw
these FIRST" as an instruction and spent the opening of every unwedge tick disposing of eight
irrelevant documents.

R15, both directions, driven rather than asserted:
  * FIRES   -- a red gate's node ids reach the state file and the NTFY the director reads.
  * CLEARS  -- a green gate retires them, so a stale red cannot be cited against a later failure.
  * FAIL-SAFE -- absent / malformed / stale reads as UNRECORDED and SAYS so. It never degrades to
    a guess: fabricating a plausible suspect is the defect being closed, so the one thing this
    must never do is look confident when it does not know.
"""
import json
import types

import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", tmp_path / ".blocking.json")
    monkeypatch.setattr(prc, "WEDGE_SUSPECT_HIT_RATE_FILE", tmp_path / ".hit_rate.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.action_needed as an
    monkeypatch.setattr(an, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    yield


class _Sink:
    def __init__(self):
        self.messages = []

    def __call__(self, msg, *a, **k):
        self.messages.append(msg)
        return "sent-id"


def _gate_result(rc, stdout):
    return types.SimpleNamespace(returncode=rc, stdout=stdout, stderr="")


RED_OUTPUT = (
    "........F\n"
    "=========================== short test summary info ============================\n"
    "FAILED tests/background/test_forward_attachment_register.py::test_live_rendering_is_current\n"
    "1 failed, 343 passed\n"
)


# ── FIRES: the node id survives the process boundary ────────────────────────────────────────

def test_a_red_gate_records_its_blocking_node_ids():
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")

    node_ids, gh = prc.last_blocking_tests()
    assert node_ids == [
        "FAILED tests/background/test_forward_attachment_register.py::test_live_rendering_is_current"]
    assert gh == "abc1234"


def test_the_recorded_node_ids_reach_the_wedge_state_file():
    """The RUNG-1 draw reads the state file, not the NTFY -- so the state file must carry it."""
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")
    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, now=100, send_ntfy_fn=_Sink())

    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert any("test_live_rendering_is_current" in b for b in state["blocking_tests"])


def test_the_fired_alert_names_the_blocking_test():
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")
    sink = _Sink()
    for t in (0, 10, 20):
        prc.record_publish_gate_failure("rc=1 on a marker", rc=1, now=t, send_ntfy_fn=sink)

    assert len(sink.messages) == 1
    msg = sink.messages[0]
    assert "BLOCKING TEST" in msg
    assert "test_live_rendering_is_current" in msg


def test_the_state_the_supervisor_draw_reads_carries_the_blocking_test(tmp_path):
    """The RUNG-1 draw's ONLY input is this state file, so the evidence must survive in it.

    HALF LANDED, DELIBERATELY (2026-08-10). The other half -- `supervisor.py::
    _publish_gate_wedge_active` printing the node id into the draw text and demoting the
    recency list to "backlog, not suspects" -- is written but NOT committed with this change:
    `background/supervisor.py` carries ~4h of another lane's in-flight H41 work, and committing
    the file would sweep it. So this asserts the contract at the seam the two halves share, and
    the draw-text half is filed for the H41 lane's landing rather than smuggled through here.
    """
    state = {
        "failures": [{"ts": float(t), "reason": "rc=1 on a marker", "rc": 1,
                      "kind": "test_regression", "git_hash": "abc1234"}
                     for t in (0, 600, 1200)],
        "alerted_at": 0.0, "wedge_since": 0.0, "episode_failures": 91,
        "cited_findings": ["WORKER_FINDING_IRRELEVANT_2026-08-09.md"],
    }
    node_id = ("FAILED tests/background/test_forward_attachment_register.py"
               "::test_live_rendering_is_current")
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps(state))
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")
    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, now=1800, send_ntfy_fn=_Sink())

    persisted = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert node_id in persisted["blocking_tests"]
    # The episode fields the draw also reads are not disturbed by carrying the new one.
    assert persisted["wedge_since"] == 0.0
    assert persisted["episode_failures"] >= 91


# ── CLEARS: a stale red must not be citable against a later failure ─────────────────────────

def test_a_green_gate_retires_the_previous_reds_node_ids():
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")
    assert prc.last_blocking_tests()[0], "precondition: the red was recorded"

    prc._clear_blocking_tests()

    assert prc.last_blocking_tests() == ([], None)


# ── FAIL-SAFE: unknown must read as unknown, never as a guess ───────────────────────────────

def test_an_absent_record_reads_as_unrecorded():
    assert prc.last_blocking_tests() == ([], None)


def test_a_malformed_record_reads_as_unrecorded():
    prc.GATE_BLOCKING_TESTS_FILE.write_text("{not json")
    assert prc.last_blocking_tests() == ([], None)


def test_a_record_missing_its_timestamp_reads_as_unrecorded():
    """No clock means no way to know it describes THIS failure -- so it does not."""
    prc.GATE_BLOCKING_TESTS_FILE.write_text(json.dumps({"node_ids": ["FAILED x::y"]}))
    assert prc.last_blocking_tests() == ([], None)


def test_a_stale_record_is_not_cited():
    """R15 MUTATION: yesterday's red must not be quoted as today's cause.

    Without the age bound, a repaired cause would keep being named for the whole of the next,
    unrelated episode -- the exact class of error (a confident, wrong suspect) this mechanism
    exists to end.
    """
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")
    fresh_now = json.loads(prc.GATE_BLOCKING_TESTS_FILE.read_text())["ts"]

    assert prc.last_blocking_tests(now=fresh_now + 60)[0], "a fresh record must be citable"
    stale_now = fresh_now + prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS + 1
    assert prc.last_blocking_tests(now=stale_now) == ([], None)


def test_the_alert_says_UNRECORDED_rather_than_guessing():
    """The fail-safe direction, at the surface a human reads.

    The mutation that matters is not "the clause is missing" but "the clause quietly falls back
    to the recency list and reads like evidence". So this asserts the alarm SAYS it does not know.
    """
    sink = _Sink()
    for t in (0, 10, 20):
        prc.record_publish_gate_failure("rc=1 on a marker", rc=1, now=t, send_ntfy_fn=sink)

    msg = sink.messages[0]
    assert "UNRECORDED" in msg
    assert "do NOT infer a cause" in msg


def test_a_red_gate_that_printed_no_summary_line_records_an_empty_list_not_nothing():
    """"The gate was red and named no test" is itself diagnostic, and is distinguishable from
    "no red gate has run" only if the empty case is still WRITTEN."""
    prc._log_gate_failure_payload(_gate_result(-9, "Killed\n"), git_hash="abc1234")

    assert prc.GATE_BLOCKING_TESTS_FILE.exists()
    node_ids, gh = prc.last_blocking_tests()
    assert node_ids == []
    assert gh == "abc1234"
