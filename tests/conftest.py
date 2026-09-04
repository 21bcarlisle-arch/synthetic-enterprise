import importlib.util as _il
import os
import pathlib

# background.ntfy_utils raises at import time if SE_NTFY_TOPIC isn't set
# (2026-07-08 topic rotation, docs/staging/NTFY_CHANNEL_HARDENING.md — no
# committed default topic any more). setdefault so a real background/.env.ntfy
# already sourced in the shell (e.g. this session's own tmux env) still wins;
# this is only a harmless fallback so collection doesn't fail for a dev/CI
# shell that hasn't loaded it. Must run before any test module imports
# background.ntfy_utils, so it lives here at conftest.py's top level, not
# inside a fixture (fixtures run too late for collection-time imports).
#
# PRESENT-BUT-EMPTY IS NOT SET, and `setdefault` cannot tell the difference. Measured 2026-09-04:
# this seat's own tmux environment exports `SE_WAKE_HMAC_KEY=` (empty), which is exactly what a
# partially-loaded `.env.ntfy` leaves behind. `setdefault` saw the name present, did nothing, and
# `ntfy_utils` captured `''` at import — falsy, so `sign_wake_message` raised and four tests failed.
#
# THE COST: every `surgical_land --merge` in the tree was refused for hours, and the publisher's
# commit with it, so nothing reached the site. It hid because a path-scoped commit never selects
# `tests/background/test_ntfy_utils.py` — only a MERGE runs the whole suite — so it read as "merges
# are broken" rather than "an empty secret is not a secret".
#
# So the fallback is keyed to USABILITY, not to presence. `or` also covers the absent case, so this
# strictly replaces `setdefault` rather than sitting beside it.
os.environ["SE_NTFY_TOPIC"] = (
    os.environ.get("SE_NTFY_TOPIC") or "pytest-fallback-topic-not-a-real-secret")
os.environ["SE_WAKE_HMAC_KEY"] = (
    os.environ.get("SE_WAKE_HMAC_KEY") or "pytest-fallback-hmac-key-not-a-real-secret")

import numpy as np
import pandas as pd
import pytest

# The sink guard's body, factored out 2026-08-21 so its coverage is inspectable rather than a
# closure inside a fixture. Loaded by explicit file location: `tests/` is not a package, and
# putting it on sys.path SHADOWS the repo root -- which broke `tools.*` resolution the first
# time I tried it, in this very file's sessionfinish hook.
_guard_spec = _il.spec_from_file_location(
    "production_surface_guard",
    pathlib.Path(__file__).resolve().parent / "production_surface_guard.py",
)
production_surface_guard = _il.module_from_spec(_guard_spec)
_guard_spec.loader.exec_module(production_surface_guard)


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
    config.addinivalue_line(
        "markers",
        "operational: this test validates pipeline MACHINERY (daemon/session/process "
        "lifecycle, scheduling, notification transport, reconciliation) -- NOT a published "
        "business surface. The publish gate runs `-m 'not operational'`, so a red operational "
        "test can ALARM (health_check / independent sweep) but can never wedge the live-site "
        "publish (R10 close of the 2026-07-16 overnight-wedge class). A test that asserts on / "
        "generates a published surface (LATEST.md, dashboard, report, site data, atom levels), "
        "or enforces a safety WALL, must NOT carry this marker -- it must stay blocking.",
    )
    config.addinivalue_line(
        "markers",
        "join_report_only: AO3_join_test_tier -- a SYSTEM/join test (tests/system/**) "
        "watching one of the five chain seams. The director pre-ruled the first landing "
        "REPORT-ONLY: join tests may be brittle at first and a red one would otherwise "
        "block publish, so the publish gate runs `-m 'not operational and not "
        "join_report_only'` and a red join test can ALARM but never wedge the live site. "
        "CONTAINED to tests/system/ -- this marker must never appear on a module outside "
        "that tier (it would silence a blocking content test), enforced by "
        "tests/system/test_report_only_landing.py. Removed from the gate's marker "
        "expression once the tier has run a stable week -- see docs/design/JOIN_TEST_TIER.md.",
    )
    config.addinivalue_line(
        "markers",
        "scale_report_only: AO4_scale_constraints_executable -- a standing check for one "
        "of the five production-readiness scale constraints C-S1..C-S5 (tests/system/**). "
        "Same report-only landing as the join tier and for a sharper reason: these checks "
        "MEASURE the tree as it is, and two are red on arrival by design (the "
        "money-in-duplicate drift the director cites by name, and C-S3's same-step "
        "residual). Softening a check because it went red would be R12, so the publish "
        "gate deselects them instead: `-m 'not operational and not join_report_only and "
        "not scale_report_only'`. The COMPLEMENT expression runs them, so a red still "
        "alarms. CONTAINED to tests/system/ -- enforced by "
        "tests/system/test_report_only_landing.py. Its own marker, not the join tier's, "
        "so the two promote on their own stable weeks. See "
        "docs/design/SCALE_CONSTRAINT_CHECKS.md.",
    )


# ── OPS1 sub-step 7 — test/isolation boundary (§2.4): test code CANNOT touch production ──────
# The NTFY guard above closes one channel; these close the other two the design names (G-T1
# session spawn, G-T2 state writes), each by CONSTRUCTION (an autouse guard) rather than by every
# test remembering to stub -- MAKE_IT_STICK: mechanism, not discipline. The leak that already bit
# (a test wrote the REAL .pull_loop_health.json) is exactly the G-T2 class.
_BLOCKED_SPAWN = {"tmux", "claude", "systemctl"}
# G-T2's PATH SET LIVES WITH THE SINK, NOT HERE (2026-08-21). It used to be a `_PROTECTED_WRITE_PATHS`
# tuple at this spot, and when the guard body moved to `tests/production_surface_guard.py` the tuple
# stayed behind with no consumer: adding a path to it protected nothing, and `test_isolation_guards.py`
# still instructed its R15 mutation against it -- a mutation that could no longer turn any test red.
# A guard with two path lists, one of them dead, is the FAIL-SILENT shape R15 names. There is one now:
# `production_surface_guard.PROTECTED_FILES` (individually-listed files) and `PROTECTED_SURFACES`
# (whole directories), both carrying the incident record for each entry.
#
# What it still deliberately does NOT protect: derived-artifact generators (site/data/**,
# agent_status.json, docs/reports/**). ~40 tests legitimately regenerate those in-process and a
# daemon/generator overwrites them anyway, so that is cosmetic isolation-debt to remediate
# incrementally — tracked, not rushed. `site/data/publish_provenance.json` is the named exception.


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
    """G-T2: a test may NOT write a production surface, WHATEVER PRIMITIVE IT USES.

    The body moved to `tests/production_surface_guard.py` on 2026-08-21 so its coverage is a
    testable surface rather than a closure, and so the two proven holes could be closed there
    with the evidence beside them: `builtins.open` walked past the old guard even for the
    explicitly-listed files, and `docs/staging/` -- the director's draw queue -- was not
    covered at all.

    Reads pass. tmp_path passes (it resolves under /tmp). Opt out with @real_state_write.
    """
    if request.node.get_closest_marker("real_state_write"):
        return
    production_surface_guard.install(monkeypatch)


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
