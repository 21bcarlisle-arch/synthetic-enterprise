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
import time
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
    # THE CLOCK IS A POSSIBLE CLOCK (2026-09-04). This fixture used to open the episode at
    # `wedge_since: 0.0` against `now=1800`, and pin `persisted["wedge_since"] == 0.0` as the
    # "not disturbed" half. But `0.0` is 1970, the wall clock here is 2026 and the simulation is
    # 2016-2025, so no writer in this repository can stamp it -- and a control whose fixture
    # states an impossible value teaches the next reader that it is possible. It did: that zero
    # reached `site/data/director_reserved.json` and rendered as an established episode on the
    # director's own surface (SEAT_FINDING_A_ZERO_START_TIME_RENDERED_AS_AN_ESTABLISHED_1970_
    # EPISODE_ON_THE_DIRECTORS_OWN_SURFACE_2026-09-04.md), and a persisted zero is now RESTAMPED
    # rather than adopted.
    #
    # What this test is actually about -- the blocking node id surviving into the state file the
    # RUNG-1 draw reads -- is untouched by that. The episode half keeps its meaning and gains a
    # start the writer could really have written, so it now asserts "an open episode is not
    # disturbed" instead of "an impossible value is preserved".
    # The clock is `time.time()` and not a chosen constant, because the OTHER half of this test
    # is age-bounded: `last_blocking_tests` compares the payload's real recording time against
    # `now`, and any fixed future clock ages the node id out and empties the assertion above. The
    # small fake clocks elsewhere in this file only survive that bound by going NEGATIVE.
    now = time.time()
    episode_start = now - 1800                 # three failures, all inside the 1h window
    state = {
        "failures": [{"ts": episode_start + t, "reason": "rc=1 on a marker", "rc": 1,
                      "kind": "test_regression", "git_hash": "abc1234"}
                     for t in (0, 600, 1200)],
        "alerted_at": episode_start, "wedge_since": episode_start, "episode_failures": 91,
        "cited_findings": ["WORKER_FINDING_IRRELEVANT_2026-08-09.md"],
    }
    node_id = ("FAILED tests/background/test_forward_attachment_register.py"
               "::test_live_rendering_is_current")
    prc.PUBLISH_GATE_STATE_FILE.write_text(json.dumps(state))
    prc._log_gate_failure_payload(_gate_result(1, RED_OUTPUT), git_hash="abc1234")
    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, now=now, send_ntfy_fn=_Sink())

    persisted = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert node_id in persisted["blocking_tests"]
    # The episode fields the draw also reads are not disturbed by carrying the new one.
    assert persisted["wedge_since"] == episode_start
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


# ── THE PAYLOAD MUST NAME A TEST THE GATE ACTUALLY RAN (2026-08-12, eighteenth wedge) ────────
#
# WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN. The mechanism above closed
# "the alarm cites documents linked to the failure by nothing at all" and replaced it with a
# list parsed from the gate's own output -- but the parser scanned the WHOLE combined stream
# for any line starting "FAILED "/"ERROR ". Tests in the blocking scope run nested pytest
# invocations, and pytest replays their stdout inside a `--- Captured stdout call ---` block
# where a `startswith` check cannot tell them from the outer run's own summary.
#
# Measured, 2026-08-12 01:24Z: the payload named five `test_supervisor.py` tests carrying a
# module-level `pytest.mark.operational` -- DESELECTED by the gate's own `-m` expression (186
# deselected, 0 collected) and absent from the resolved 134-file scope, i.e. tests the gate is
# structurally incapable of running. The real blocker, an ENOSPC from a full tmpfs, was not in
# the list. The wrong names then reached `paused_reason` on the PUBLIC provenance endpoint.
#
# The fix is ordering, not heuristics: captured-output blocks live in the FAILURES section,
# which always precedes the outer run's "short test summary info" header, so the LAST such
# header in the stream begins the only summary that is the gate's own.
NESTED_CONTAMINATED_OUTPUT = (
    "........F\n"
    "=================================== FAILURES ===================================\n"
    "____________ test_stall_alarm_fires_when_commit_stale_and_work_queued ____________\n"
    "----------------------------- Captured stdout call -----------------------------\n"
    "Operational-layer signal: running the complement marker set\n"
    "=========================== short test summary info ============================\n"
    "FAILED tests/background/test_supervisor.py::test_harden_suppression_is_content_driven_not_only_filename\n"
    "FAILED tests/background/test_supervisor.py::test_harden_suppression_ignores_parked_and_archived_rulings\n"
    "FAILED tests/background/test_supervisor.py::test_harden_suppression_ignores_daemon_markers\n"
    "FAILED tests/background/test_supervisor.py::test_ruling_mint_instruction_mints_from_block_and_flags_missing_block\n"
    "FAILED tests/background/test_supervisor.py::test_ruling_steer_missing_work_block_lists_only_blockless_rulings\n"
    "5 failed, 181 deselected in 5.00s\n"
    "E   OSError: [Errno 28] No space left on device\n"
    "=========================== short test summary info ============================\n"
    "FAILED tests/controls/test_daemon_loop_mutation.py::test_stall_alarm_fires_when_commit_stale_and_work_queued\n"
    "1 failed, 945 passed, 192 deselected, 1 xfailed in 624.44s\n"
)

THE_REAL_BLOCKER = (
    "FAILED tests/controls/test_daemon_loop_mutation.py"
    "::test_stall_alarm_fires_when_commit_stale_and_work_queued")


def test_a_nested_runs_failures_never_reach_the_payload():
    """R15 MUTATION arm: the whole-stream parser returns SIX here, five of them tests the gate
    cannot run. The summary-scoped parser returns exactly the one the gate itself reported.

    This is the assertion that fails before the fix and passes after -- the property R15
    requires of any control offered as evidence."""
    node_ids = prc._parse_failed_node_ids(NESTED_CONTAMINATED_OUTPUT)

    assert node_ids == [THE_REAL_BLOCKER], (
        "the payload must contain the gate's own blocker and nothing from a nested run; got "
        "{}".format(node_ids))
    assert not any("test_supervisor.py" in n for n in node_ids), (
        "test_supervisor.py is module-level `operational` -- deselected by the gate's own -m "
        "expression, so it can never be a blocker and must never be named as one")


def test_the_contaminated_names_do_not_reach_the_state_file_or_the_alarm():
    """The parser is not the surface that hurt: the wrong names reached `.publish_gate_state.
    json`, the RUNG-1 doorbell, and `paused_reason` on the public provenance endpoint. Assert at
    the surface, not just at the function (a control must grade the artefact its consumer reads).
    """
    prc._log_gate_failure_payload(_gate_result(1, NESTED_CONTAMINATED_OUTPUT),
                                  git_hash="deadbee")

    node_ids, gh = prc.last_blocking_tests()
    assert gh == "deadbee"
    assert node_ids == [THE_REAL_BLOCKER]

    recorded = json.loads(prc.GATE_BLOCKING_TESTS_FILE.read_text())
    assert not any("test_supervisor" in n for n in recorded["node_ids"])


def test_no_summary_section_reads_as_absent_rather_than_falling_back_to_the_stream():
    """FAIL-SILENT is the trap in this shape (R15). A crash/OOM transcript has FAILED lines from
    nested output but NO summary of its own -- the honest answer is "I don't know", which the
    caller already renders as UNRECORDED. Degrading to the old whole-stream scan would put the
    wrong names back on the public surface by a different route."""
    crashed = (
        "----------------------------- Captured stdout call -----------------------------\n"
        "FAILED tests/background/test_supervisor.py::test_harden_suppression_ignores_daemon_markers\n"
        "Killed\n")

    assert prc._parse_failed_node_ids(crashed) == []
