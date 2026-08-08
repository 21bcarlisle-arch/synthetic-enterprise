"""H23_publish_gate_scope_marker (L3) -- mutation tests for the independent-
cadence green signal that covers the operational layer the content publish
gate deliberately DESELECTS (PUBLISH_GATE_MARKER_EXPR = "not operational").

R11 no-orphan-transitions: deselected from the content gate must not mean
uncovered by any gate. This proves the substitute signal (background.
process_run_complete.run_operational_layer_signal, driven from the deadman's
existing timer) CAN FAIL on its own named defect (R15):
  - a PERSISTENT red (>= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD consecutive
    checks) pages exactly once (transition-only, no double-page while it stays
    red);
  - a single red followed by green (a flake) is LOGGED but never pages;
  - recovery (red -> green) after a persistent-red page is itself a
    transition and pages exactly once;
  - the throttle actually throttles (no re-run before the interval elapses,
    `force=True` bypasses it);
  - an unreadable state file fails CLOSED (treated as due, not silently
    skipped forever);
and, in both directions, that this signal is fully DECOUPLED from the content
publish gate: a red operational result never touches PUBLISH_GATE_STATE_FILE,
never changes PUBLISH_GATE_MARKER_EXPR/publish_gate_pytest_argv(), and the
content gate's own argv is provably the complement of this signal's argv.

Uses the REAL notify() contract (only the low-level send_ntfy is captured),
so the transition-only/re-escalate dedup exercised here is the actual
production behaviour -- matching how every other deadmans_switch.py check is
tested, not a hand-rolled stand-in for it.
"""
import json

import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "OPERATIONAL_LAYER_STATE_FILE", tmp_path / ".operational_layer_signal.json")
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    import background.notify as notify_mod
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    yield


class _Runner:
    """Injectable stub for the pytest subprocess -- returns a canned rc without
    ever running the real (slow) operational suite."""
    def __init__(self, rc):
        self.rc = rc
        self.argv_seen = []

    def __call__(self, argv):
        self.argv_seen.append(argv)
        return type("Result", (), {"returncode": self.rc})()


@pytest.fixture
def sent(monkeypatch):
    """Captures every real send_ntfy call (what notify() calls once it decides
    a page is due) -- the same capture point test_deadmans_switch.py uses."""
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    return calls


def _run(rc, now, force=True):
    return prc.run_operational_layer_signal(now=now, runner=_Runner(rc), force=force)


def _marker_expr(argv):
    """The value following the LAST '-m' in argv -- the marker expression flag,
    distinct from the earlier `python -m pytest` module flag."""
    idx = len(argv) - 1 - argv[::-1].index("-m")
    return argv[idx + 1]


# ── argv scope: this signal's argv is the complement of the content gate's ──

def test_operational_layer_argv_is_marker_complement_of_content_gate():
    op_argv = prc.operational_layer_pytest_argv()
    gate_argv = prc.publish_gate_pytest_argv()
    assert _marker_expr(op_argv) == "operational or join_report_only"
    assert _marker_expr(gate_argv) == "not operational and not join_report_only"
    assert op_argv != gate_argv


def test_no_marker_is_deselected_by_BOTH_lanes():
    """The property the pair of constants exists to hold, checked as a PROPERTY
    rather than as two hardcoded strings agreeing with each other.

    Deselected from the content gate must never mean covered by no gate at all
    (R11, no orphan transitions). Evaluate both marker expressions over every
    combination of the markers they mention: each combination must be selected by
    at least one lane. Adding a third deselected class to the content gate without
    widening this signal fails here, which is exactly what happened when the join
    tier landed (AO3_join_test_tier, 2026-08-08).
    """
    import itertools
    import re

    gate = prc.PUBLISH_GATE_MARKER_EXPR
    op = prc.OPERATIONAL_LAYER_MARKER_EXPR
    markers = sorted(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", gate + " " + op)) - {"not", "and", "or"})
    assert markers, "no markers found in either expression — the census is vacuous"

    uncovered = []
    for combo in itertools.product([False, True], repeat=len(markers)):
        env = dict(zip(markers, combo))
        if not (eval(gate, {"__builtins__": {}}, env) or eval(op, {"__builtins__": {}}, env)):
            uncovered.append({m: v for m, v in env.items()})
    assert uncovered == [], (
        "a test carrying these markers would be deselected by the content gate AND by the "
        f"operational-layer signal — covered by NO gate: {uncovered}"
    )


# ── green result: no page ────────────────────────────────────────────────────

def test_single_green_result_is_clean_no_page(sent):
    res = _run(rc=0, now=0)
    assert res["ran"] is True and res["green"] is True
    assert sent == []
    state = json.loads(prc.OPERATIONAL_LAYER_STATE_FILE.read_text())
    assert state["consecutive_red"] == 0
    assert state["consecutive_green"] == 1
    assert state["last_result"] == "green"


# ── single red is a flake: logged, never paged ───────────────────────────────

def test_single_red_result_logs_but_does_not_page(sent):
    res = _run(rc=1, now=0)
    assert res["ran"] is True and res["green"] is False and res["paged"] is False
    assert sent == []  # R5: a single red must not page
    log_text = prc.LOG_FILE.read_text()
    assert "red" in log_text.lower()
    state = json.loads(prc.OPERATIONAL_LAYER_STATE_FILE.read_text())
    assert state["consecutive_red"] == 1


def test_red_then_green_flake_never_pages(sent):
    """A lone red followed by green (a flake, never reaching the persistent
    threshold) must never page in either direction."""
    _run(rc=1, now=0)
    res = _run(rc=0, now=10)
    assert res["green"] is True
    assert sent == []  # neither the red flake nor its recovery paged


# ── persistent red: pages exactly once, then stays suppressed while red ─────

def test_persistent_red_pages_exactly_once(sent):
    r1 = _run(rc=1, now=0)      # 1st consecutive red -- below threshold
    assert r1["paged"] is False
    assert sent == []
    r2 = _run(rc=1, now=10)     # 2nd consecutive red -- threshold met
    assert r2["paged"] is True
    assert len(sent) == 1
    msg = sent[0]
    assert "[OPERATIONAL LAYER RED]" in msg

    # A THIRD consecutive red, immediately after (well inside the re-escalate
    # window): same transition state -> notify() itself suppresses it. No
    # double-page for an unchanged, still-red condition.
    r3 = _run(rc=1, now=20)
    assert r3["consecutive_red"] == 3
    assert len(sent) == 1


def test_persistent_red_reescalates_after_window_elapses(sent):
    _run(rc=1, now=0)
    _run(rc=1, now=10)          # persistent -- pages (call #1)
    assert len(sent) == 1

    # Age the notify transition store's real timestamp past the re-escalate
    # window (notify() keys re-escalation on wall-clock time, not the
    # simulated `now` this module's own throttle uses -- same technique
    # test_deadmans_switch.py uses for its re-escalate test).
    import background.notify as _n
    store = json.loads(_n.TRANSITIONS_FILE.read_text())
    store[prc.OPERATIONAL_LAYER_TRANSITION_KEY]["ts"] -= (prc.OPERATIONAL_LAYER_RE_ESCALATE_SECONDS + 1)
    _n.TRANSITIONS_FILE.write_text(json.dumps(store))

    _run(rc=1, now=20)          # still red, window elapsed -- re-pages
    assert len(sent) == 2


# ── recovery after a persistent-red page is a transition: pages once ────────

def test_recovery_after_persistent_red_pages_once(sent):
    _run(rc=1, now=0)
    _run(rc=1, now=10)          # persistent -- pages (call #1)
    assert len(sent) == 1

    res = _run(rc=0, now=20)    # recovers
    assert res["green"] is True and res["paged"] is True
    assert len(sent) == 2
    assert "[OPERATIONAL LAYER RECOVERED]" in sent[-1]

    # Staying green afterwards must not re-page.
    res2 = _run(rc=0, now=30)
    assert res2["paged"] is False
    assert len(sent) == 2


# ── throttle: cost-aware, does not run every cycle ───────────────────────────

def test_throttle_skips_before_interval_elapses(sent):
    runner1 = _Runner(0)
    r1 = prc.run_operational_layer_signal(now=0, runner=runner1)
    assert r1["ran"] is True
    assert len(runner1.argv_seen) == 1

    runner2 = _Runner(1)  # would be RED, but should never even run
    r2 = prc.run_operational_layer_signal(now=1, runner=runner2)
    assert r2["ran"] is False and r2["reason"] == "throttled"
    assert runner2.argv_seen == []          # the slow suite genuinely did not run
    assert sent == []                       # and therefore nothing paged


def test_throttle_runs_again_after_interval_elapses(sent):
    prc.run_operational_layer_signal(now=0, runner=_Runner(0))
    later = prc.OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS + 1
    runner2 = _Runner(0)
    r2 = prc.run_operational_layer_signal(now=later, runner=runner2)
    assert r2["ran"] is True
    assert len(runner2.argv_seen) == 1


def test_force_bypasses_throttle(sent):
    prc.run_operational_layer_signal(now=0, runner=_Runner(0))
    runner2 = _Runner(0)
    r2 = prc.run_operational_layer_signal(now=1, runner=runner2, force=True)
    assert r2["ran"] is True
    assert len(runner2.argv_seen) == 1


# ── fail-closed on an unreadable state file ──────────────────────────────────

def test_unreadable_state_file_is_treated_as_due_not_silently_skipped(sent):
    prc.OPERATIONAL_LAYER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    prc.OPERATIONAL_LAYER_STATE_FILE.write_text("{ not valid json")
    runner = _Runner(0)
    res = prc.run_operational_layer_signal(now=0, runner=runner)
    assert res["ran"] is True                # ran despite corrupt prior state
    assert len(runner.argv_seen) == 1


# ── a monitoring failure must never raise into its caller ───────────────────

def test_runner_exception_is_swallowed_not_raised(sent):
    def _boom(argv):
        raise RuntimeError("subprocess exploded")
    res = prc.run_operational_layer_signal(now=0, runner=_boom, force=True)
    assert res["ran"] is False and res["reason"] == "error"
    assert sent == []


# ── DECOUPLING PROOF: a red operational result never touches the content gate ──

def test_persistent_red_never_touches_publish_gate_state_or_scope(sent):
    _run(rc=1, now=0)
    _run(rc=1, now=10)   # persistent red, pages
    assert len(sent) == 1

    # The content gate's own state file was never created/touched by this signal.
    assert not prc.PUBLISH_GATE_STATE_FILE.exists()
    # The content gate's blocking scope is untouched.
    assert prc.PUBLISH_GATE_MARKER_EXPR == "not operational and not join_report_only"
    gate_argv = prc.publish_gate_pytest_argv()
    assert _marker_expr(gate_argv) == "not operational and not join_report_only"


def test_persistent_red_does_not_block_a_simulated_content_publish(sent):
    """Simulates the two paths side by side: an operational red pages this
    signal, while a content-gate pass (rc=0 on `-m "not operational"`) is
    entirely unaffected and would still proceed to commit/publish -- the two
    are provably independent state machines."""
    _run(rc=1, now=0)
    _run(rc=1, now=10)   # operational persistent red

    # Simulate the content gate's own (separate) success bookkeeping.
    prc.record_publish_gate_success(now=20)
    gate_state = json.loads(prc.PUBLISH_GATE_STATE_FILE.read_text())
    assert gate_state["failures"] == []
    assert gate_state["alerted_at"] is None


# ── R5: THE RED PAGE MUST CARRY ITS OWN DIAGNOSTIC PAYLOAD ───────────────────
# Added 2026-08-08 (worker tick) after this signal paged RED four consecutive
# times carrying `rc=1` and nothing else. The transition logic above was
# correct throughout -- and still a whole diagnostic tick was spent
# rediscovering a cause the failing run had already printed and the runner
# discarded. R5 says an alert carries its diagnostic payload; these prove this
# one now CAN, and prove the ways it must not silently appear to.

_PYTEST_RED_OUTPUT = """\
tests/background/test_daemon_lifecycle.py .F                             [ 50%]
=========================== short test summary info ============================
FAILED tests/background/test_daemon_lifecycle.py::test_process_set_reconciles
ERROR tests/background/test_capability.py::test_capability_manifest_present
1 failed, 1 error, 400 passed in 61.20s
"""


class _OutputRunner:
    """Runner stub that behaves like the REAL capture_output=True subprocess:
    carries the child's streams, not just a return code."""
    def __init__(self, rc, stdout="", stderr=""):
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
        self.argv_seen = []

    def __call__(self, argv):
        self.argv_seen.append(argv)
        return type("Result", (), {"returncode": self.rc, "stdout": self.stdout,
                                   "stderr": self.stderr})()


def _run_with_output(rc, now, stdout="", stderr=""):
    return prc.run_operational_layer_signal(
        now=now, runner=_OutputRunner(rc, stdout, stderr), force=True)


def test_red_page_names_the_failing_tests_not_just_the_return_code(sent):
    """THE DEFECT THIS CONTROL EXISTS FOR: a page that says only `rc=1`."""
    _run_with_output(rc=1, now=0, stdout=_PYTEST_RED_OUTPUT)
    _run_with_output(rc=1, now=10, stdout=_PYTEST_RED_OUTPUT)   # persistent -> pages
    assert len(sent) == 1
    page = sent[0]
    # The specific failing tests are NAMED in the page a human receives.
    assert "test_process_set_reconciles" in page
    assert "test_capability_manifest_present" in page
    # ERROR lines count as failures too, not just FAILED.
    assert "ERROR tests/background/test_capability.py" in page


def test_digest_prefers_the_failure_summary_over_incidental_tail_noise():
    result = type("R", (), {"returncode": 1, "stdout": _PYTEST_RED_OUTPUT, "stderr": ""})()
    digest = prc.operational_layer_failure_digest(result)
    assert digest.startswith("FAILED tests/background/test_daemon_lifecycle.py")
    # Progress/among-noise lines are excluded when a real summary section exists.
    assert "[ 50%]" not in digest
    assert "400 passed" not in digest


def test_digest_falls_back_to_the_tail_when_there_is_no_summary_section():
    """A collection error or interpreter crash prints no `short test summary
    info` -- the payload must still carry something actionable, not go blank."""
    crash = "Traceback (most recent call last):\n  ImportError: no module named sim\n"
    result = type("R", (), {"returncode": 2, "stdout": "", "stderr": crash})()
    digest = prc.operational_layer_failure_digest(result)
    assert "ImportError: no module named sim" in digest


def test_digest_is_bounded_and_says_how_many_it_omitted():
    many = "=== short test summary info ===\n" + "".join(
        "FAILED tests/background/test_x.py::test_{}\n".format(i) for i in range(40))
    result = type("R", (), {"returncode": 1, "stdout": many, "stderr": ""})()
    digest = prc.operational_layer_failure_digest(result)
    lines = digest.splitlines()
    # Bounded (an NTFY is not a log file) ...
    assert len(lines) == prc.OPERATIONAL_LAYER_DIGEST_MAX_LINES + 1
    # ... but never SILENTLY bounded: truncation is stated, so a reader cannot
    # mistake 12 shown for 12 total.
    assert lines[-1] == "... and 28 more failing test(s)"


def test_absent_output_fails_LOUD_not_silent(sent):
    """FAIL-SILENT is the killer pattern here (R15): if the child produced no
    capturable output, the page must SAY the cause is unavailable rather than
    render an empty 'Failing tests:' section that reads as 'nothing to report'."""
    _run(rc=1, now=0)          # _Runner exposes returncode ONLY -- no streams
    _run(rc=1, now=10)
    assert len(sent) == 1
    assert "cause unavailable" in sent[0]


def test_green_page_carries_no_failure_payload(sent):
    """The digest must not leak into the RECOVERED page: a green run has no
    failing tests to name, and a stale payload there would be a false report."""
    _run_with_output(rc=1, now=0, stdout=_PYTEST_RED_OUTPUT)
    _run_with_output(rc=1, now=10, stdout=_PYTEST_RED_OUTPUT)   # persistent red, pages
    res = _run_with_output(rc=0, now=20)                        # recovery, pages
    assert res["digest"] == ""
    assert len(sent) == 2
    assert "FAILED" not in sent[1]


def test_the_real_runner_actually_captures_output(monkeypatch):
    """INDEPENDENCE (R15 tautology guard): every test above feeds the digest
    through an injected stub, which would keep passing even if the production
    runner still discarded the child's streams -- the exact defect being
    fixed. This asserts the DEFAULT runner (runner=None) invokes subprocess
    with capture_output, so the stubs above are testing a reachable path."""
    seen = {}

    def _fake_subprocess_run(argv, **kwargs):
        seen.update(kwargs)
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(prc.subprocess, "run", _fake_subprocess_run)
    prc.run_operational_layer_signal(now=0, runner=None, force=True)
    assert seen.get("capture_output") is True
    assert seen.get("text") is True
