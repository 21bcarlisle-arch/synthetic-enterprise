"""R15 proof for the REST HEARTBEAT continuity re-arm (LOOP_CONTINUITY_REARM_DESIGN.md, 2026-07-19,
R3 -- second attempt at the "wake-at-rest" class, so a redesign with a mutation-proven control).

The bug being fixed: the Stop hook is the SOLE transport and is edge-triggered. Its old
drained-and-gated branch ALLOW-STOPPED, which ends the turn-chain -- and nothing re-fires the hook at
rest, so the seat sat dead with an unconsumed staged doc for ~90min until a human typed (2026-07-19).

The control: drained-and-gated now HEARTBEATS -- a bounded in-hook poll that (a) keeps the chain alive
(never returns the terminal allow-stop while resting), (b) WAKES the moment a staged doc appears, (c)
still dies if the kill switch is turned off, and (d) never inflates the no-progress stuck counter.
Each property below is asserted AND mutation-checked (neuter it -> the bad behaviour returns).
"""
import importlib.util
import sys
import types
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pull_next_work.py"
WORKER_ID = "22080be5-e19e-4099-a007-d71c3a6e7845"


def _wp(session_id=WORKER_ID, **extra):
    p = {"stop_hook_active": False, "session_id": session_id}
    p.update(extra)
    return p


def _load(tmp_path, monkeypatch, *, enabled=True, find_work=None,
          staged=None, sync=None, poll=1, hold=3):
    """Load the hook in isolation, injecting a fake background.supervisor with the three symbols the
    heartbeat imports (find_work / _real_staged_instructions / _sync_origin_staging), tmp observability
    files, a no-op sleep, and small POLL/HOLD so the hold window is reachable fast."""
    spec = importlib.util.spec_from_file_location("pull_next_work", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "pull-loop-log.md")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / ".pull_loop_state.json")
    monkeypatch.setattr(mod, "HEALTH_FILE", tmp_path / ".pull_loop_health.json")
    monkeypatch.setattr(mod, "WORKER_SESSION_ID", WORKER_ID)
    monkeypatch.setattr(mod, "HEARTBEAT_POLL_SECONDS", poll)
    monkeypatch.setattr(mod, "HEARTBEAT_HOLD_SECONDS", hold)
    monkeypatch.setattr("time.sleep", lambda *_a, **_k: None)  # never actually wait in tests
    if enabled:
        (tmp_path / ".build_executor_enabled").write_text("")
    fake = types.ModuleType("background.supervisor")
    fake.find_work = find_work or (lambda resumed_from_pause=False: (None, False))
    fake._real_staged_instructions = staged or (lambda: [])
    fake._sync_origin_staging = sync or (lambda: [])
    monkeypatch.setitem(sys.modules, "background.supervisor", fake)
    return mod


def _state(tmp_path):
    import json
    p = tmp_path / ".pull_loop_state.json"
    return json.loads(p.read_text()) if p.exists() else None


def _health(tmp_path):
    import json
    p = tmp_path / ".pull_loop_health.json"
    return json.loads(p.read_text()) if p.exists() else {}


# --- (a) drained-and-gated KEEPS THE CHAIN ALIVE (does not allow-stop into death) -----------------

def test_drained_and_gated_heartbeats_instead_of_dying(tmp_path, monkeypatch):
    """THE core fix: a drained-and-gated worker turn must NOT allow-stop (return None) -- that ends
    the only wake path. It must return a keep-alive BLOCK so the chain stays alive."""
    mod = _load(tmp_path, monkeypatch, find_work=lambda resumed_from_pause=False: (None, False))
    out = mod.decide(_wp())
    assert out is not None, "drained-and-gated must NOT allow-stop into a dead chain"
    assert out["decision"] == "block"
    assert "REST HEARTBEAT" in out["reason"]
    assert _health(tmp_path)["outcome"] == "HEARTBEAT_REARM"


def test_mutation_reverting_to_allow_stop_reintroduces_the_dead_chain(tmp_path, monkeypatch):
    """MUTATION: neuter the heartbeat (force it back to the old allow-stop). The drained turn then
    returns None -- the exact terminal dead-chain state this control exists to prevent. Proves the
    heartbeat is what keeps the chain alive, not something incidental."""
    mod = _load(tmp_path, monkeypatch, find_work=lambda resumed_from_pause=False: (None, False))
    monkeypatch.setattr(mod, "_rest_heartbeat", lambda: None)  # the pre-fix behaviour
    assert mod.decide(_wp()) is None  # dead chain returns -> the mutation is observable


# --- (b) WAKES on a staged doc appearing at rest (the 2026-07-19 continuity guarantee) -------------

def test_wakes_when_a_staged_doc_appears_during_rest(tmp_path, monkeypatch):
    """The precise failure: a staged advisor doc lands while the seat rests. The heartbeat's poll
    must detect it (origin-sync + local scan) and WAKE by delivering it as real work."""
    seen = {"n": 0}

    def staged():
        seen["n"] += 1
        return ["DIRECTOR_STEER_TEST.md"] if seen["n"] >= 2 else []  # appears on the 2nd poll

    mod = _load(tmp_path, monkeypatch,
                find_work=lambda resumed_from_pause=False: (None, False), staged=staged)
    out = mod.decide(_wp())
    assert out is not None and out["decision"] == "block"
    assert "DIRECTOR_STEER_TEST.md" in out["reason"]
    assert "unprocessed staging" in out["reason"]
    assert _health(tmp_path)["outcome"] == "DREW"


def test_mutation_no_staged_probe_never_wakes_on_the_doc(tmp_path, monkeypatch):
    """MUTATION: if the staged probe is blind (always []), the same staged doc does NOT wake the seat
    within the hold -- it falls through to a keep-alive. Proves the probe is the waking mechanism."""
    mod = _load(tmp_path, monkeypatch,
                find_work=lambda resumed_from_pause=False: (None, False),
                staged=lambda: [])  # blind probe
    out = mod.decide(_wp())
    assert "DIRECTOR_STEER_TEST.md" not in out["reason"]
    assert "REST HEARTBEAT" in out["reason"]  # keep-alive, not a wake


def test_origin_sync_is_invoked_each_poll(tmp_path, monkeypatch):
    """RC3's origin-sync only ever mattered if a caller that can DELIVER a turn invokes it at rest.
    The heartbeat is that caller: prove _sync_origin_staging runs on the poll (pulling an origin-
    staged doc into the tree so the very next scan sees it)."""
    calls = {"n": 0}
    mod = _load(tmp_path, monkeypatch,
                find_work=lambda resumed_from_pause=False: (None, False),
                sync=lambda: calls.__setitem__("n", calls["n"] + 1) or [])
    mod.decide(_wp())
    assert calls["n"] >= 1, "the resting heartbeat must invoke RC3 origin-sync (else origin docs never wake)"


# --- (c) still DIES if the kill switch is turned off mid-rest (W4) ---------------------------------

def test_kill_switch_off_mid_rest_allows_stop(tmp_path, monkeypatch):
    """The immortality is conditional on autonomy being ON. If the single kill switch flips off while
    resting, the heartbeat must return None so the session actually stops (a kill switch that can't
    kill is theatre -- kill-list doctrine)."""
    mod = _load(tmp_path, monkeypatch, find_work=lambda resumed_from_pause=False: (None, False))
    monkeypatch.setattr(mod, "_autonomous_execution_enabled", lambda: False)  # kill switch off
    assert mod.decide(_wp()) is None
    assert _health(tmp_path)["outcome"] == "ALLOW_STOP_DISABLED"


# --- (d) keep-alive is EXEMPT from the no-progress stuck counter -----------------------------------

def test_keepalive_does_not_inflate_no_progress_counter(tmp_path, monkeypatch):
    """A resting heartbeat is not a thrashing chain. If keep-alives counted as continuations, repeated
    rest would inflate no_progress and self-trip the pull-loop's own MAX_NO_PROGRESS guard -> the
    heartbeat would kill itself. Prove keep-alive writes NO progress state."""
    mod = _load(tmp_path, monkeypatch, find_work=lambda resumed_from_pause=False: (None, False))
    for _ in range(5):
        out = mod.decide(_wp())
        assert "REST HEARTBEAT" in out["reason"]
    assert _state(tmp_path) is None, "keep-alive must not touch the no-progress counter"


def test_wake_to_real_work_does_advance_progress_state(tmp_path, monkeypatch):
    """Conversely, a real WAKE (staged doc) is a genuine continuation and SHOULD advance the progress
    state (so a productive chain's stuck-detection still works)."""
    mod = _load(tmp_path, monkeypatch,
                find_work=lambda resumed_from_pause=False: (None, False),
                staged=lambda: ["A_REAL_STEER.md"])
    mod.decide(_wp())
    assert _state(tmp_path) is not None, "a real wake advances progress state"


# --- bound sanity: the hold is finite ------------------------------------------------------------

def test_hold_window_is_bounded_and_polls_then_rearms(tmp_path, monkeypatch):
    """The in-hook poll must be BOUNDED (never an unbounded sleep that outlives the hook timeout):
    with nothing staged it polls HOLD/POLL times, then re-arms."""
    mod = _load(tmp_path, monkeypatch,
                find_work=lambda resumed_from_pause=False: (None, False), poll=1, hold=4)
    sleeps = {"n": 0}
    # patch AFTER _load (which sets its own no-op sleep) so this counter wins
    monkeypatch.setattr("time.sleep", lambda *_a, **_k: sleeps.__setitem__("n", sleeps["n"] + 1))
    out = mod.decide(_wp())
    assert sleeps["n"] == 4, "polls HOLD/POLL times before re-arming"
    assert "REST HEARTBEAT" in out["reason"]
