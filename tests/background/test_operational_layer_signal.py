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
    assert _marker_expr(op_argv) == "operational"
    assert _marker_expr(gate_argv) == "not operational"
    assert op_argv != gate_argv


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
    assert prc.PUBLISH_GATE_MARKER_EXPR == "not operational"
    gate_argv = prc.publish_gate_pytest_argv()
    assert _marker_expr(gate_argv) == "not operational"


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
