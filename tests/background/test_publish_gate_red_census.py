"""The wedge draw must see the WHOLE red set, not the first one (control 2 of
`WORKER_FINDING_THE_WEDGE_WAS_FIVE_INSTANCES_OF_ONE_CLASS_AND_pytest_x_SERVED_THEM_ONE_AT_A_TIME`).

THE DEFECT THIS CLOSES (2026-08-14). The publish gate runs under `-x`, so a red gate names
exactly ONE failing node id however many are red. Measured: RED at every HEAD since `19d8f94da`,
252 consecutive failures, ~7,163 min -- and that was five separate instances of one mechanism
stacked behind fail-fast, served one per tick. Each tick fixed the layer it was shown and handed
the next to the next tick. The doorbell's node id carried no information about DEPTH, and depth
is the whole question when deciding whether an unwedge tick is the last one.

R15, both directions, DRIVEN rather than asserted -- and the finding wrote this test itself:
"inject two independent reds and assert the doorbell names both; a version that names one fails."

  * FIRES     -- two independent reds behind one fail-fast verdict reach the record, the alarm
                 and the RUNG-1 draw, and the draw says STACK.
  * MUTATION  -- the pre-repair behaviour (no census: the fail-fast id alone) is re-created and
                 asserted to FAIL the fires-test's own assertion. A control that passes on the
                 code it was built to reject is not a control.
  * FAIL-SAFE -- census timeout / crash / no-summary / no-budget each degrade to EXACTLY the
                 old payload, never to a smaller one, and each SAYS "depth unknown". Claiming
                 completeness you cannot substantiate is this finding one level up.
  * NEVER THE VERDICT -- the census's return code cannot move the publish verdict, and its
                 budget can never push the publish path past its caller's own bound (the
                 41h-wedge defect recorded at PUBLISH_PATH_ALLOWANCE_SECONDS).
"""
import json
import subprocess
import types

import pytest

import background.process_run_complete as prc
import background.supervisor as sup


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


def _result(rc, stdout):
    return types.SimpleNamespace(returncode=rc, stdout=stdout, stderr="")


def _summary(*node_ids):
    body = "".join("FAILED {}\n".format(n) for n in node_ids)
    return ("=========================== short test summary info "
            "============================\n" + body
            + "{} failed, 300 passed\n".format(len(node_ids)))


# The two INDEPENDENT reds the finding asks for: different modules, different mechanisms.
RED_A = "tests/architecture/test_static_quality_ratchet.py::test_ruff_violations_do_not_grow"
RED_B = "tests/background/test_forward_attachment_register.py::test_live_rendering_is_current"

FAIL_FAST_OUTPUT = _summary(RED_A)          # what `-x` shows: one red, whatever the truth is
CENSUS_OUTPUT = _summary(RED_A, RED_B)      # what the report-only re-run shows


def _census_runner(stdout, rc=1):
    def _run(argv, cwd, env, timeout):
        return types.SimpleNamespace(returncode=rc, stdout=stdout, stderr="")
    return _run


# ── FIRES: two reds behind one fail-fast verdict reach every consumer ────────────────────────

def test_the_census_names_both_reds_behind_one_fail_fast_verdict():
    census = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A],
        runner=_census_runner(CENSUS_OUTPUT), budget=600)

    ids, status = census
    assert status == prc.CENSUS_COMPLETE
    assert RED_A in "".join(ids) and RED_B in "".join(ids), (
        "the census must name BOTH independent reds -- naming one is the defect")
    assert len(ids) == 2


def test_both_reds_reach_the_record_the_alarm_reads():
    census = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A],
        runner=_census_runner(CENSUS_OUTPUT), budget=600)
    prc._log_gate_failure_payload(_result(1, FAIL_FAST_OUTPUT), git_hash="abc1234", census=census)

    node_ids, gh = prc.last_blocking_tests()
    assert gh == "abc1234"
    joined = "".join(node_ids)
    assert RED_A in joined and RED_B in joined
    assert prc.last_red_census() == (prc.CENSUS_COMPLETE, 2)


def test_both_reds_reach_the_state_file_the_rung_1_draw_reads():
    census = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A],
        runner=_census_runner(CENSUS_OUTPUT), budget=600)
    prc._log_gate_failure_payload(_result(1, FAIL_FAST_OUTPUT), git_hash="abc1234", census=census)
    prc.record_publish_gate_failure("rc=1 on a marker", rc=1, now=100, send_ntfy_fn=_Sink())

    state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    joined = "".join(state["blocking_tests"])
    assert RED_A in joined and RED_B in joined
    assert state["red_census"] == prc.CENSUS_COMPLETE
    assert state["total_red"] == 2


def test_the_alarm_says_it_is_the_whole_set_and_says_how_many():
    census = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A],
        runner=_census_runner(CENSUS_OUTPUT), budget=600)
    prc._log_gate_failure_payload(_result(1, FAIL_FAST_OUTPUT), git_hash="abc1234", census=census)
    sink = _Sink()
    for i in range(prc.PUBLISH_GATE_FAILURE_THRESHOLD):
        prc.record_publish_gate_failure("rc=1", rc=1, now=100 + i, send_ntfy_fn=sink)

    msg = "\n".join(sink.messages)
    assert "WHOLE RED SET" in msg
    assert "2 test(s) red" in msg
    assert RED_A in msg and RED_B in msg


def test_the_rung_1_draw_says_stack_and_names_the_count():
    clause = sup._wedge_depth_clause("complete", 5, 5)
    assert "5 tests are red" in clause
    assert "STACK" in clause
    assert "TOGETHER" in clause


def test_a_genuine_single_red_is_stated_as_one_not_as_unknown():
    """The census's value is symmetric: it must also be able to say 'one, and that is all'."""
    clause = sup._wedge_depth_clause("complete", 1, 1)
    assert "ONE test" in clause
    assert "STACK" not in clause


# ── MUTATION: the pre-repair behaviour must FAIL the assertion above ─────────────────────────

def test_mutation_the_fail_fast_only_payload_fails_the_names_both_assertion():
    """Re-create the code this control replaces -- no census, the `-x` node id alone -- and
    assert it does NOT satisfy the fires-test. If this passes, the control is a tautology."""
    prc._log_gate_failure_payload(_result(1, FAIL_FAST_OUTPUT), git_hash="abc1234")  # no census

    node_ids, _ = prc.last_blocking_tests()
    joined = "".join(node_ids)
    assert RED_A in joined, "precondition: the fail-fast red is still recorded"
    assert RED_B not in joined, (
        "MUTATION FAILED TO BITE: the pre-repair payload must NOT name the second red -- if it "
        "does, the fires-test above proves nothing about the census")
    assert prc.last_red_census() == (prc.CENSUS_FAIL_FAST_ONLY, 1)


def test_mutation_a_record_without_the_census_field_reads_as_unknown_depth():
    """A record written by the OLD code (no `census` key) must not be read as a complete set."""
    prc.GATE_BLOCKING_TESTS_FILE.write_text(json.dumps(
        {"ts": 1000.0, "git_hash": "abc1234", "node_ids": [RED_A]}))

    assert prc.last_red_census(now=1001.0) == (prc.CENSUS_FAIL_FAST_ONLY, 0)
    assert "DEPTH UNKNOWN" in prc._blocking_clause([RED_A], "abc1234",
                                                   *prc.last_red_census(now=1001.0))


def test_mutation_an_unrecognised_census_word_reads_as_unknown_not_as_complete():
    """FAIL-CLOSED on vocabulary: only the three declared words may claim anything."""
    prc.GATE_BLOCKING_TESTS_FILE.write_text(json.dumps(
        {"ts": 1000.0, "git_hash": "abc1234", "node_ids": [RED_A],
         "census": "COMPLETE", "total_red": 9}))   # wrong case: not the declared constant

    assert prc.last_red_census(now=1001.0) == (prc.CENSUS_FAIL_FAST_ONLY, 0)


# ── FAIL-SAFE: every degradation lands on the old payload, and says so ───────────────────────

@pytest.mark.parametrize("runner,label", [
    (lambda *a, **k: (_ for _ in ()).throw(subprocess.TimeoutExpired("pytest", 1)), "timeout"),
    (lambda *a, **k: (_ for _ in ()).throw(OSError("no space left on device")), "crash"),
    (_census_runner("collected 0 items / 1 error\n", rc=2), "no summary section"),
])
def test_a_census_that_cannot_answer_degrades_to_the_fail_fast_payload(runner, label):
    ids, status = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A], runner=runner, budget=600)

    assert ids == [RED_A], "a failed census must never LOSE the red the verdict named ({})".format(label)
    assert status == prc.CENSUS_FAIL_FAST_ONLY
    assert "DEPTH UNKNOWN" in prc._blocking_clause(ids, "abc1234", status, len(ids))


def test_a_census_that_somehow_misses_the_fail_fast_red_still_reports_it():
    """The result is a SUPERSET of the verdict's own node ids by construction -- a census that
    disagreed with the gate must not be able to quietly drop what the gate saw."""
    ids, status = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A],
        runner=_census_runner(_summary(RED_B)), budget=600)

    joined = "".join(ids)
    assert RED_A in joined and RED_B in joined
    assert status == prc.CENSUS_COMPLETE


def test_no_budget_skips_the_census_rather_than_running_it_unbounded():
    called = []

    def _runner(argv, cwd, env, timeout):
        called.append(timeout)
        return types.SimpleNamespace(returncode=1, stdout=CENSUS_OUTPUT, stderr="")

    ids, status = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A], runner=_runner, budget=0)

    assert called == [], "with no budget the census must not start at all"
    assert (ids, status) == ([RED_A], prc.CENSUS_FAIL_FAST_ONLY)


def test_the_censuss_budget_can_never_outlive_the_publish_paths_own_bound():
    """DERIVED, not hand-typed: the bound that killed a publish path mid-write for 41h was a
    wrapper number that drifted from the work it wrapped. Whatever has been spent, budget +
    spent + margin must stay inside PUBLISH_PATH_TIMEOUT_SECONDS."""
    for spent in (0, 60, 600, 3000, 4400, prc.PUBLISH_PATH_TIMEOUT_SECONDS):
        budget = prc.red_census_budget_seconds(now_monotonic=spent, started=0)
        assert budget >= 0
        if budget:
            assert spent + budget + prc.GATE_RED_CENSUS_PATH_MARGIN_SECONDS <= \
                prc.PUBLISH_PATH_TIMEOUT_SECONDS
            assert budget <= prc.GATE_RED_CENSUS_MAX_SECONDS


def test_a_late_red_gets_no_census_at_all_rather_than_a_useless_sliver():
    spent = prc.PUBLISH_PATH_TIMEOUT_SECONDS - prc.GATE_RED_CENSUS_PATH_MARGIN_SECONDS - 10
    assert prc.red_census_budget_seconds(now_monotonic=spent, started=0) == 0


# ── THE VERDICT IS NOT THE CENSUS'S TO MOVE ──────────────────────────────────────────────────

def test_the_census_argv_is_the_gates_own_argv_without_fail_fast():
    gate = prc.publish_gate_pytest_argv("tests/")
    census = prc.red_census_argv(gate)

    assert "-x" in gate, "precondition: the BLOCKING gate is still fail-fast"
    assert "-x" not in census
    assert "--maxfail={}".format(prc.GATE_RED_CENSUS_MAXFAIL) in census
    # Same suite, same deselection: a census over a different population would name reds the
    # verdict never had the chance to see.
    assert [a for a in gate if a != "-x"] == [a for a in census if not a.startswith("--maxfail")]


def test_the_blocking_gate_keeps_fail_fast():
    """`-x` stays on the verdict. A red suite run to completion near the timeout becomes a
    TIMEOUT, which carries no node ids at all -- trading a reliable one for a possible five is
    the wrong direction, and the census exists precisely so it need not be traded."""
    assert "-x" in prc.publish_gate_pytest_argv("tests/")


def test_a_partial_census_claims_at_least_never_the_whole_set():
    ids, status = prc.run_red_census(
        ["pytest", "tests/", "-x"], "/tmp", {}, [RED_A],
        runner=_census_runner(_summary(*[
            "tests/x/test_{}.py::test_it".format(i) for i in range(prc.GATE_RED_CENSUS_MAXFAIL)])),
        budget=600)

    assert status == prc.CENSUS_PARTIAL
    clause = prc._blocking_clause(ids[:3], "abc1234", status, len(ids))
    assert "AT LEAST" in clause
    assert "WHOLE RED SET" not in clause


def test_the_citation_cap_says_how_many_it_withheld():
    """A cap must never be able to look like the answer (this is the finding's own shape)."""
    many = ["tests/x/test_{}.py::test_it".format(i) for i in range(20)]
    clause = prc._blocking_clause(many[:prc.GATE_MAX_CITED_BLOCKING_TESTS], "abc1234",
                                  prc.CENSUS_COMPLETE, 20)
    assert "20 test(s) red" in clause
    assert "{} more withheld".format(20 - prc.GATE_MAX_CITED_BLOCKING_TESTS) in clause
