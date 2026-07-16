"""executor_daemon.run_forever — the PROCESS-level keep-alive that makes headless continuation
automatic (2026-07-16, director milestone). Every branch is behaviour-tested with injected
collaborators (no real dispatch, no real clock, no enable flag on the real repo)."""
from background import executor_daemon, executor_governor


def _summary(reason, cycles=1):
    return executor_governor.LoopSummary(stop_reason=reason, cycles=cycles)


def test_dark_by_default_no_run_loop_when_kill_switch_off():
    """DARK: with the kill flag off, the daemon does NOT enter run_loop at all (safe no-op)."""
    called = {"n": 0}
    reason = executor_daemon.run_forever(
        kill_switch=lambda: False,
        run_loop_fn=lambda **k: called.__setitem__("n", called["n"] + 1) or _summary("x"),
        sleep=lambda _s: None,
    )
    assert called["n"] == 0
    assert reason == "kill_switch_off"


def test_reenters_run_loop_after_budget_exhausted_window_slides():
    """A budget-exhausted return is NOT terminal: the daemon waits and RE-ENTERS run_loop so the
    loop keeps drawing across window slides — continuation survives the budget boundary."""
    entries = {"n": 0}
    slept = []

    def _run_loop(**k):
        entries["n"] += 1
        return _summary("budget_exhausted")

    reason = executor_daemon.run_forever(
        kill_switch=lambda: True,
        run_loop_fn=_run_loop,
        sleep=lambda s: slept.append(s),
        max_supervisions=3,   # bound the test; real daemon is unbounded
    )
    assert entries["n"] == 3, "daemon must re-enter run_loop after each budget-exhausted return"
    assert slept and all(s == executor_daemon.RESTART_BACKOFF_SECONDS for s in slept)
    assert reason == "max_supervisions"


def test_exits_on_terminal_wall_does_not_hammer():
    """A genuine wall run_loop already NTFY'd (map unreconciled / R3 repeated failure) is TERMINAL:
    the daemon exits and stays down — it must NOT restart into the same wall."""
    for wall in ("map_unreconciled", "repeated_failure"):
        entries = {"n": 0}

        def _run_loop(**k):
            entries["n"] += 1
            return _summary(wall)

        reason = executor_daemon.run_forever(
            kill_switch=lambda: True, run_loop_fn=_run_loop, sleep=lambda _s: None,
        )
        assert entries["n"] == 1, f"{wall}: must not re-enter a terminal wall"
        assert reason == wall


def test_restarts_run_loop_on_crash():
    """A run_loop CRASH (unexpected exception) must RESTART, never kill the daemon (resilience)."""
    seq = iter([RuntimeError("boom"), _summary("kill_switch_off")])
    flips = {"n": 0}

    def _run_loop(**k):
        v = next(seq)
        if isinstance(v, Exception):
            raise v
        return v

    # kill switch stays on for the crash + one restart, then run_loop returns kill_switch_off
    reason = executor_daemon.run_forever(
        kill_switch=lambda: True, run_loop_fn=_run_loop, sleep=lambda _s: None,
    )
    assert reason == "kill_switch_off"  # survived the crash and re-entered


def test_daemon_importable_as_a_standalone_script():
    """Regression (2026-07-16): launched as `python3 background/executor_daemon.py`
    (start_worker.sh, like every sibling daemon), Python puts background/ on
    sys.path, NOT the repo root -- so `from background import ...` raised
    ModuleNotFoundError and the process died at import before run_forever ran.
    The daemon MUST carry the same sys.path bootstrap every sibling daemon has.
    Proven functionally: run the file in a subprocess from a NON-repo cwd with a
    clean env, importing it as a module (so main() does not run) -- it must import
    with returncode 0."""
    import subprocess
    import sys
    from pathlib import Path

    daemon = Path(__file__).resolve().parents[2] / "background" / "executor_daemon.py"
    # exec_module with __name__ != "__main__" so run_forever/main never fires;
    # cwd=/tmp and no PYTHONPATH so ONLY the file's own bootstrap can satisfy the
    # `from background import ...` at module load.
    code = (
        "import importlib.util,sys;"
        f"spec=importlib.util.spec_from_file_location('ed',r'{daemon}');"
        "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
        "assert hasattr(m,'run_forever');print('OK')"
    )
    r = subprocess.run([sys.executable, "-c", code], cwd="/tmp",
                       capture_output=True, text=True, timeout=30,
                       env={"PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, f"daemon not importable as a script: {r.stderr}"
    assert "OK" in r.stdout
