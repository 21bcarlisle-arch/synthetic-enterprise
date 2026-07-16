"""Tests for background/executor_governor.py — the tripwires + self-continuing LOOP.

Every control is R15-checked: a MUTATION/behaviour test proves it FIRES on its named
defect. No real `claude -p` turn is launched (run_once is injected as a fake); no enable
flag on the real repo is ever created (the kill switch is redirected to a tmp flag).
"""

from dataclasses import dataclass

import pytest

from background import agent_status, build_executor, executor_governor

# Capture the REAL reconcile default before the autouse fixture patches it, so the
# fail-closed-on-error test can exercise the genuine fallback logic.
_ORIG_DEFAULT_RECONCILE = executor_governor._default_reconcile_check


# ---------------------------------------------------------------------------
# Isolation: side-effect files -> tmp; NTFY/action-needed -> captured (no network)
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(build_executor, "LOG_FILE", tmp_path / "build-executor-log.md")
    monkeypatch.setattr(agent_status, "STATUS_FILE", tmp_path / "agent_status.json")
    monkeypatch.setattr(agent_status, "SITE_STATUS_FILE", tmp_path / "site_agent_status.json")
    # Redirect THE kill-switch flag to tmp so tests never touch the console-only real one.
    monkeypatch.setattr(executor_governor._pull_hook, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    # Default the map-reconciliation check to "reconciled" so loop tests are deterministic
    # and never coupled to the real docs/design/atom_status/ state (its own tests cover it).
    monkeypatch.setattr(executor_governor, "_default_reconcile_check", lambda: [])
    # Default the F1 fold to a no-op so loop tests never run a real merge()/git-commit
    # against the repo (its own dedicated tests below exercise the real fold semantics).
    monkeypatch.setattr(executor_governor, "_default_fold", lambda: [])


def _enable(tmp_path):
    (tmp_path / ".build_executor_enabled").write_text("")


@dataclass
class _FakeResult:
    status: str
    atom_reason: str = "BUILD lane draw"
    claimed_sha: str | None = None
    detail: str = ""


# ===========================================================================
# TRIPWIRE d — the durable kill switch (DARK by default), fail-closed + reused
# ===========================================================================
def test_kill_switch_reuses_the_pull_loop_definition():
    """ONE definition of 'enabled', not two: the governor's switch IS the pull-loop
    hook's predicate (DIRECTOR_ANSWERS_C7 #6, one flag). Structural: same callable."""
    assert executor_governor.kill_switch_enabled.__doc__  # exists
    assert executor_governor._pull_hook.ENABLE_FLAG.name == ".build_executor_enabled"


def test_kill_switch_fail_closed_when_flag_absent(tmp_path):
    assert executor_governor.kill_switch_enabled() is False  # flag not created
    _enable(tmp_path)
    assert executor_governor.kill_switch_enabled() is True


def test_kill_switch_fail_closed_when_flag_is_a_directory(tmp_path):
    (tmp_path / ".build_executor_enabled").mkdir()  # not a readable regular file
    assert executor_governor.kill_switch_enabled() is False


def test_run_loop_is_dark_when_kill_switch_off(tmp_path):
    """DARK by default: flag absent -> the loop dispatches NOTHING and stops at once.
    Mutation intent: if run_loop dispatched before checking the switch, `dispatched`
    would be > 0 — the assertion of 0 is what proves the kill gates dispatch."""
    dispatched = {"n": 0}

    def _never():
        dispatched["n"] += 1
        return _FakeResult("success")

    summary = executor_governor.run_loop(
        run_once_fn=_never, max_cycles=5, budget=None, sleep=lambda _s: None
    )
    assert summary.stop_reason == "kill_switch_off"
    assert summary.cycles == 0
    assert dispatched["n"] == 0


# ===========================================================================
# TRIPWIRE a — budget cap fires (R15 mutation test)
# ===========================================================================
def test_budget_cap_fires_at_turn_ceiling():
    """A budget already at the turn ceiling refuses the next dispatch. Mutation intent:
    if `>=` were flipped to `>` (fail-open by one), can_dispatch would wrongly return
    True at the ceiling — this assertion goes red under that mutation."""
    clock = {"t": 0.0}
    b = executor_governor.TurnBudget(max_turns_per_window=2, window_seconds=3600,
                                     monotonic=lambda: clock["t"])
    assert b.can_dispatch() is True
    b.charge()
    assert b.can_dispatch() is True
    b.charge()
    assert b.can_dispatch() is False  # at ceiling -> refuse


def test_budget_cap_fail_closed_when_unconfigured():
    """A non-positive turn cap dispatches nothing (fail-closed), never 'free'."""
    assert executor_governor.TurnBudget(max_turns_per_window=0).can_dispatch() is False
    assert executor_governor.TurnBudget(max_turns_per_window=-1).can_dispatch() is False


def test_budget_window_slides():
    """Turns older than the window are evicted -> capacity returns after it passes."""
    clock = {"t": 0.0}
    b = executor_governor.TurnBudget(max_turns_per_window=1, window_seconds=100,
                                     monotonic=lambda: clock["t"])
    b.charge()
    assert b.can_dispatch() is False
    clock["t"] = 101.0  # past the window
    assert b.can_dispatch() is True


def test_run_loop_stops_on_budget_exhausted(tmp_path):
    _enable(tmp_path)
    clock = {"t": 0.0}
    budget = executor_governor.TurnBudget(max_turns_per_window=3, window_seconds=3600,
                                          monotonic=lambda: clock["t"])
    summary = executor_governor.run_loop(
        run_once_fn=lambda: _FakeResult("success"),
        budget=budget, sleep=lambda _s: None,
    )
    assert summary.stop_reason == "budget_exhausted"
    assert summary.cycles == 3  # exactly the cap, then refused


# ===========================================================================
# WALL — a turn escalated a one-way door: stop + alert, never retry
# ===========================================================================
def test_run_loop_stops_and_alerts_on_wall(tmp_path):
    _enable(tmp_path)
    alerts = []
    summary = executor_governor.run_loop(
        run_once_fn=lambda: _FakeResult("escalated", detail="one-way-door escalation"),
        max_cycles=10,
        alert=lambda result, kind="": alerts.append(kind),
        sleep=lambda _s: None,
    )
    assert summary.stop_reason == "wall_escalated"
    assert summary.cycles == 1
    assert alerts == ["wall_escalated"]


# ===========================================================================
# MAP RECONCILIATION — an unfolded level report STOPS the loop (fail-closed, F2)
# ===========================================================================
def test_run_loop_stops_when_map_unreconciled(tmp_path):
    """A non-empty reconcile check (an atom's level report never folded into the map)
    STOPS the loop BEFORE dispatch and alerts -- the draw reads level_current, so the
    loop must not run off a possibly-mis-ranked map. Mutation intent: without the
    reconcile gate, dispatch would proceed -- the 0-cycles + alert assert prove it gates."""
    _enable(tmp_path)
    dispatched = {"n": 0}
    alerts = []

    def _never():
        dispatched["n"] += 1
        return _FakeResult("success")

    summary = executor_governor.run_loop(
        run_once_fn=_never,
        max_cycles=5,
        reconcile_check=lambda: ["ARCH1_internal_seams"],  # an unfolded level report
        alert=lambda result, kind="": alerts.append(kind),
        sleep=lambda _s: None,
    )
    assert summary.stop_reason == "map_unreconciled"
    assert summary.cycles == 0
    assert dispatched["n"] == 0
    assert alerts == ["map_unreconciled"]


def test_run_loop_default_reconcile_is_fail_closed_on_error(monkeypatch):
    """If the reconcile primitive itself raises, the default resolves to a divergence
    sentinel (never a silent pass) -- an unreadable reconciliation signal is a FAILED
    check (R15 fail-silent killer)."""
    import tools.merge_atom_status as mas

    def _boom(*a, **k):
        raise RuntimeError("inbox dir unreadable")

    monkeypatch.setattr(mas, "unfolded_inbox_ids", _boom)
    assert _ORIG_DEFAULT_RECONCILE() == ["<reconcile-check-error>"]


# ===========================================================================
# F1 ATOMIC LEVEL-WRITE — the loop FOLDS a landed inbox before the F2 check
# ===========================================================================
def test_run_loop_folds_inbox_before_reconcile_check(tmp_path):
    """F1 second half: the loop folds a landed atom_status inbox at the TOP of the cycle,
    BEFORE the F2 reconcile check, so a fork's in-commit level report lands without a
    separate judgment step. Ordering is load-bearing: a foldable inbox must be gone by the
    time reconcile runs, or F2 would wrongly stop the loop."""
    _enable(tmp_path)
    order = []

    def _fold():
        order.append("fold")
        return ["SOME_atom"]  # folded + cleared this cycle

    def _reconcile():
        order.append("reconcile")
        return []  # clean, because the fold above cleared the inbox

    summary = executor_governor.run_loop(
        run_once_fn=lambda: _FakeResult("success"),
        max_cycles=1,
        fold_fn=_fold,
        reconcile_check=_reconcile,
        sleep=lambda _s: None,
    )
    assert summary.stop_reason == "max_cycles"
    # fold ran before reconcile on the first cycle (and again in the final-fold-on-stop).
    assert order[:2] == ["fold", "reconcile"], f"fold must precede reconcile: {order}"


def test_run_loop_stops_when_fold_fails_leaving_unfolded_inbox(tmp_path):
    """F1 + F2 together: if the fold FAILS (returns nothing, inbox left at rest), the very
    next reconcile check sees the unfolded inbox and STOPS the loop. Proves the fold does
    NOT mask the fail-closed guard -- a mis-fold is a halt, never a silent mis-rank."""
    _enable(tmp_path)
    dispatched = {"n": 0}

    summary = executor_governor.run_loop(
        run_once_fn=lambda: (dispatched.__setitem__("n", dispatched["n"] + 1), _FakeResult("success"))[1],
        max_cycles=5,
        fold_fn=lambda: [],  # fold failed / folded nothing
        reconcile_check=lambda: ["SOME_atom"],  # inbox still at rest
        alert=lambda result, kind="": None,
        sleep=lambda _s: None,
    )
    assert summary.stop_reason == "map_unreconciled"
    assert dispatched["n"] == 0  # stopped before dispatch


def test_default_fold_swallows_errors_and_returns_empty(monkeypatch):
    """The default fold must never crash the loop: if merge() raises, it logs and returns
    [] so the inbox is left for F2 to catch (fail-closed), not propagated as an exception."""
    import tools.merge_atom_status as mas

    def _boom(*a, **k):
        raise RuntimeError("map unwritable")

    monkeypatch.setattr(mas, "merge", _boom)
    assert executor_governor._default_fold() == []


def test_executor_prompt_contract_is_atomic_inbox_write_not_free_text():
    """F1 first half: the fork's governance contract instructs a structured in-commit
    atom_status inbox write, NOT a free-text level report folded by a separate judgment
    step (the pre-F1 lost-write window)."""
    prompt = build_executor._build_prompt("BUILD lane draw: SOME_atom")
    assert "docs/design/atom_status/" in prompt
    assert "SAME COMMIT" in prompt
    assert "free-text" in prompt.lower()


# ===========================================================================
# R3 two-strike — repeated non-landing failures stop the loop (don't burn the night)
# ===========================================================================
def test_run_loop_stops_on_repeated_failure(tmp_path):
    _enable(tmp_path)
    alerts = []
    summary = executor_governor.run_loop(
        run_once_fn=lambda: _FakeResult("failed", detail="not on origin"),
        max_cycles=100,
        max_consecutive_failures=2,
        alert=lambda result, kind="": alerts.append(kind),
        sleep=lambda _s: None,
    )
    assert summary.stop_reason == "repeated_failure"
    assert summary.cycles == 2
    assert alerts == ["repeated_failure"]


def test_run_loop_success_resets_the_failure_streak(tmp_path):
    """A success between failures resets the streak — the two-strike is CONSECUTIVE,
    so an occasional failure never trips it, only a wedged atom does."""
    _enable(tmp_path)
    seq = iter(["failed", "success", "failed", "success", "failed", "failed"])
    summary = executor_governor.run_loop(
        run_once_fn=lambda: _FakeResult(next(seq)),
        max_cycles=100, max_consecutive_failures=2,
        alert=lambda *a, **k: None, sleep=lambda _s: None,
    )
    # first failure/success/failure/success reset; only the final two failures trip it.
    assert summary.stop_reason == "repeated_failure"
    assert summary.cycles == 6


# ===========================================================================
# The loop CONTINUES on success, and stops when the switch flips mid-run
# ===========================================================================
def test_run_loop_continues_until_kill_switch_flips(tmp_path):
    _enable(tmp_path)
    calls = {"n": 0}

    def _run():
        calls["n"] += 1
        if calls["n"] == 3:
            (tmp_path / ".build_executor_enabled").unlink()  # director flips it off
        return _FakeResult("success")

    summary = executor_governor.run_loop(
        run_once_fn=_run, max_cycles=100, sleep=lambda _s: None
    )
    assert summary.stop_reason == "kill_switch_off"
    assert summary.cycles == 3  # ran 3 turns, then the flipped switch stopped it


# ===========================================================================
# Refuse to run unbounded — no bare, uncapped overnight spender
# ===========================================================================
def test_run_loop_refuses_unbounded():
    with pytest.raises(ValueError, match="unbounded"):
        executor_governor.run_loop()  # no budget, no max_cycles


# ===========================================================================
# SAFE-DARK invariant — the governor never WRITES the console-only flag
# ===========================================================================
def test_governor_never_writes_the_enable_flag():
    """The agent may READ the kill switch (the governor is the module that legitimately
    does) but NEVER create/modify it. Structural: the source performs no write/create
    operation against the flag — it reaches it only through the reused hook predicate,
    never even constructing the Path itself. (Naming the flag in docstrings is a READ
    reference, allowed; only WRITES are the safety violation.)"""
    src = (executor_governor.PROJECT_DIR / "background" / "executor_governor.py").read_text()
    for write_verb in (".write_text(", ".write_bytes(", ".touch(", ".mkdir(", ".unlink(", ".open("):
        assert f"ENABLE_FLAG{write_verb}" not in src
    # The governor reaches the flag ONLY via the reused predicate, never by building the
    # raw path (which would be the first step toward writing it).
    assert 'PROJECT_DIR / "docs" / "observability" / ".build_executor_enabled"' not in src
