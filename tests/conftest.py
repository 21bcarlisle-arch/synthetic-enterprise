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
