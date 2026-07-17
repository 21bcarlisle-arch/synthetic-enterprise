import os

# background.ntfy_utils raises at import time if SE_NTFY_TOPIC isn't set
# (2026-07-08 topic rotation, docs/staging/NTFY_CHANNEL_HARDENING.md — no
# committed default topic any more). setdefault so a real background/.env.ntfy
# already sourced in the shell (e.g. this session's own tmux env) still wins;
# this is only a harmless fallback so collection doesn't fail for a dev/CI
# shell that hasn't loaded it. Must run before any test module imports
# background.ntfy_utils, so it lives here at conftest.py's top level, not
# inside a fixture (fixtures run too late for collection-time imports).
os.environ.setdefault("SE_NTFY_TOPIC", "pytest-fallback-topic-not-a-real-secret")
os.environ.setdefault("SE_WAKE_HMAC_KEY", "pytest-fallback-hmac-key-not-a-real-secret")

import numpy as np
import pandas as pd
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "real_ntfy: test exercises the REAL send_ntfy POST/parse internals (curl is "
        "mocked, so still no network) -- exempt from the global no-send autouse guard.",
    )
    config.addinivalue_line(
        "markers",
        "real_subprocess: test genuinely needs to spawn a tmux/claude/systemctl process "
        "-- exempt from the G-T1 no-real-session-spawn guard (OPS1 sub-step 7).",
    )
    config.addinivalue_line(
        "markers",
        "real_state_write: test genuinely needs to write a production state path "
        "-- exempt from the G-T2 no-real-state-write guard (OPS1 sub-step 7).",
    )


# ── OPS1 sub-step 7 — test/isolation boundary (§2.4): test code CANNOT touch production ──────
# The NTFY guard above closes one channel; these close the other two the design names (G-T1
# session spawn, G-T2 state writes), each by CONSTRUCTION (an autouse guard) rather than by every
# test remembering to stub -- MAKE_IT_STICK: mechanism, not discipline. The leak that already bit
# (a test wrote the REAL .pull_loop_health.json) is exactly the G-T2 class.
_BLOCKED_SPAWN = {"tmux", "claude", "systemctl"}
# G-T2 protects the high-danger RUNTIME CONTROL STATE — files a live daemon READS to make a
# control decision, where a test writing a fake value corrupts live behaviour (the kill switch;
# the transport-health signal the deadman alarms on — the .pull_loop_health.json leak that already
# bit us; the notify dedup store; the boot-SHA records). It deliberately does NOT (yet) protect
# derived-artifact generators (site/data/**, agent_status.json, docs/reports/**): ~40 tests
# legitimately regenerate those in-process, and a daemon/generator overwrites them anyway, so that
# is cosmetic isolation-debt to remediate incrementally — tracked, not rushed on this rung.
_PROTECTED_WRITE_PATHS = (
    "docs/observability/.build_executor_enabled",   # THE kill switch — a test must never set it
    "docs/observability/.pull_loop_health.json",    # deadman alarms on this (the proven leak)
    "docs/observability/.notify_transitions.json",  # notify() transition-dedup store
    "docs/observability/.daemon_boot",              # boot-SHA drift records (dir)
)


@pytest.fixture(autouse=True)
def _no_real_session_spawn(request, monkeypatch):
    """G-T1: a test may NOT spawn a real session/lifecycle process (tmux / claude / systemctl).
    subprocess.run/call/check_output all go through subprocess.Popen; patching Popen catches every
    spawn. Ordinary tools (git, python3, curl-already-mocked) pass. Opt in with @real_subprocess."""
    if request.node.get_closest_marker("real_subprocess"):
        return
    import subprocess as _sp
    real_popen = _sp.Popen

    def guarded_popen(args, *a, **k):
        if isinstance(args, str):
            first = args.split()[0] if args.split() else ""
        elif isinstance(args, (list, tuple)) and args:
            first = str(args[0])
        else:
            first = ""
        base = os.path.basename(first)
        if base in _BLOCKED_SPAWN:
            raise RuntimeError(
                f"TEST ISOLATION (G-T1): a test tried to spawn a real '{base}' process. "
                "Stub it, or mark @pytest.mark.real_subprocess if you genuinely need it."
            )
        return real_popen(args, *a, **k)

    monkeypatch.setattr(_sp, "Popen", guarded_popen)


@pytest.fixture(autouse=True)
def _no_real_state_write(request, monkeypatch):
    """G-T2: a test may NOT write to a production state path. Patches Path.write_text/write_bytes/
    open(write-mode) to raise if the target resolves under a protected production root -- the exact
    class that leaked when a test wrote the real .pull_loop_health.json. Reads pass; tmp_path passes
    (it resolves under /tmp). Opt in with @real_state_write."""
    if request.node.get_closest_marker("real_state_write"):
        return
    import pathlib
    repo = pathlib.Path(__file__).resolve().parent.parent
    protected = [str((repo / r).resolve()) for r in _PROTECTED_WRITE_PATHS]

    def _is_protected(p) -> bool:
        try:
            rp = str(pathlib.Path(p).resolve())
        except Exception:
            return False
        return any(rp == pr or rp.startswith(pr + os.sep) for pr in protected)

    real_wt = pathlib.Path.write_text
    real_wb = pathlib.Path.write_bytes
    real_open = pathlib.Path.open

    def _blocked(target):
        raise RuntimeError(
            f"TEST ISOLATION (G-T2): a test tried to write production state {target}. "
            "Isolate to tmp_path (monkeypatch the path constant), or mark @pytest.mark.real_state_write."
        )

    def guarded_wt(self, *a, **k):
        if _is_protected(self):
            _blocked(self)
        return real_wt(self, *a, **k)

    def guarded_wb(self, *a, **k):
        if _is_protected(self):
            _blocked(self)
        return real_wb(self, *a, **k)

    def guarded_open(self, mode="r", *a, **k):
        if any(m in mode for m in ("w", "a", "x", "+")) and _is_protected(self):
            _blocked(self)
        return real_open(self, mode, *a, **k)

    monkeypatch.setattr(pathlib.Path, "write_text", guarded_wt)
    monkeypatch.setattr(pathlib.Path, "write_bytes", guarded_wb)
    monkeypatch.setattr(pathlib.Path, "open", guarded_open)


@pytest.fixture(autouse=True)
def _no_real_ntfy_from_tests(request, monkeypatch):
    """GLOBAL, AUTOUSE (2026-07-16, director: "my phone is spamming with test messages").
    NO test run -- the publish gate's, an auto-resumed session's recovery checklist, a
    ghost's, or an interactive `pytest` -- may POST a real NTFY to the director's phone.
    Every test gets send_ntfy replaced by a recording no-op. This is THE class fix (a
    forgotten mock previously buzzed the phone with synthetic 'fake reason' / 'atom X'
    content). Belt-and-suspenders with send_ntfy's own PYTEST_CURRENT_TEST guard. Tests
    that intentionally exercise send_ntfy's real internals mark themselves
    @pytest.mark.real_ntfy (curl mocked there, so still no network)."""
    if request.node.get_closest_marker("real_ntfy"):
        return
    import background.ntfy_utils as _nu
    monkeypatch.setattr(_nu, "send_ntfy", lambda *a, **k: "conftest-suppressed")


@pytest.fixture
def sample_customer():
    return {
        "customer_id": "C1",
        "eac_kwh": 3500,
        "acquisition_date": "2016-01-01",
        "commodity": "electricity",
        "segment": "resi",
        "hedge_fraction": 0.5,
        "contract_type": "fixed_1yr",
    }


@pytest.fixture
def sample_ssp_series():
    rng = np.random.default_rng(42)
    ssp_values = rng.uniform(30, 80, 48)
    index = range(1, 49)
    return pd.Series(ssp_values, index=index)


@pytest.fixture
def sample_date_range():
    return ("2016-01-01", "2016-03-31")

@pytest.fixture(autouse=True, scope="session")
def fast_mode():
    """Set SIM_FAST_MODE=1 for all tests by default (session-level).

    Session scope ensures this is set before any module-scoped fixtures
    (like sim_result_2017) run and call the simulation.
    Tests that need the real Ollama-backed risk committee use:
      monkeypatch.delenv("SIM_FAST_MODE", raising=False)
    """
    import os
    os.environ["SIM_FAST_MODE"] = "1"
    yield
    os.environ.pop("SIM_FAST_MODE", None)


# Cumulative tests EXECUTED metric (2026-07-10, director page comment:
# "Don't we want cumulative tests run, not the growth in the standard test
# set"). Forward-only instrumentation -- see tools/test_execution_metric.py
# module docstring for the full rationale (no historical log exists,
# fabricating one would violate the Anchored-noise/R-A no-fabrication rule).
def pytest_sessionfinish(session, exitstatus):
    from tools.test_execution_metric import record_execution

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter is None:
        return
    record_execution(reporter.stats)
