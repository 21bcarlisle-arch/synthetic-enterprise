"""The HEAD-red census keeps each red's crash line, so a pollution bisect does not start blind.

THE DEFECT (H40, 2026-10-07). The register kept a red's node id, run count and dates, and a
per-run histogram of exception TYPES. The journal printed `NEW RED <node>` and nothing more. A
red that is green in isolation is pollution, and the first thing a bisect needs is which
assertion fired: H40 could not tell an empty drawn book (`assert drawn`) from a broken identity
(`not_shared`) for two nodes without a 58-minute batch and a six-minute probe.

The property: **every red a run observes carries THAT run's first crash line on its record, on
the register and beside `NEW RED`; a red re-observed without one carries none.**
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

from background import head_red_register as reg
from tools import head_green_census as hgc

T0 = datetime(2026, 11, 26, 4, 0, tzinfo=timezone.utc)

_SUITE = (
    "import pytest\n\n"
    "@pytest.fixture\ndef broken():\n    yield\n    raise RuntimeError('teardown too')\n\n"
    "@pytest.fixture\ndef dead():\n    raise RuntimeError('no roster')\n\n"
    "def test_drawn():\n    drawn = []\n    assert drawn\n\n"
    "def test_setup_dies(dead):\n    pass\n\n"
    "def test_call_then_teardown(broken):\n    assert 1 == 2\n\n"
    "def test_ok():\n    pass\n")


def test_a_complete_run_streams_each_reds_own_crash_line(tmp_path, monkeypatch):
    """END TO END through a real pytest and the census's own runner, on a run that FINISHES --
    the path every nightly census takes when it completes, whose reds come from stdout.

    MUTATIONS (each fires here): stop appending the crash field in the plugin -- `crash` is
    empty; drop the complete-run `observed["crash"]` read -- it is absent; keep the LAST failing
    phase's line instead of the first -- the teardown line replaces the assertion; drop the
    relative-path strip -- the line names the throwaway checkout.
    """
    (tmp_path / "test_a.py").write_text(_SUITE)
    monkeypatch.setattr(hgc, "pytest_argv", lambda: [
        sys.executable, "-m", "pytest", "-q", "--tb=line", "-p", "tools.head_census_progress",
        "-p", "no:cacheprovider", "test_a.py"])
    monkeypatch.setattr(hgc, "first_modules", lambda: [])
    env = dict(os.environ, PYTHONPATH=str(hgc.PROJECT_DIR), TMPDIR=str(tmp_path))
    observed: dict = {}
    out = hgc._run_admitted_suite(tmp_path, env, 120, observed)

    assert "1 passed" in out and "partial" not in observed, "this leg is the COMPLETE run"
    assert observed["crash"] == {
        "test_a.py::test_drawn": "test_a.py:14: assert []",
        "test_a.py::test_setup_dies": "test_a.py:10: RuntimeError: no roster",
        "test_a.py::test_call_then_teardown": "test_a.py:20: assert 1 == 2",
    }


def test_progress_lines_without_a_crash_field_still_parse():
    """A stream written before this change (three fields) must still count its reds."""
    got = hgc.parse_progress("call\tfailed\ttests/a.py::old\ncall\tpassed\ttests/a.py::ok\n")
    assert got["failures"] == ["tests/a.py::old"] and got["crash"] == {}


def test_the_record_carries_this_runs_line_and_drops_a_stale_one(tmp_path):
    """MUTATIONS: never store `crash` -- the first leg fires; keep the old line when a later run
    re-observes the red without one -- the second leg fires (a stale cause beside a fresh
    `last_seen` names a line that run never printed)."""
    node = "tests/a.py::test_drawn"
    store = reg.record([node], head_sha="aaa", passed=10, now=T0, store={"runs": [], "tests": {}},
                       crash={node: "tests/a.py:13: assert []"})
    first = store["tests"][node].get("crash")
    reg.record([node], head_sha="bbb", passed=10, now=T0 + timedelta(days=1), store=store)
    assert first == "tests/a.py:13: assert []"
    assert "crash" not in store["tests"][node]


def test_the_register_and_the_new_red_line_show_it(monkeypatch, capsys):
    """MUTATIONS: drop the register's crash column -- the first assertion fires; drop the crash
    suffix from the `NEW RED` print -- the second fires."""
    node = "tests/a.py::test_drawn"
    line = "tests/a.py:13: assert drawn | not_shared"
    store = reg.record([node], head_sha="aaa", passed=10, now=T0, store={"runs": [], "tests": {}},
                       crash={node: line})
    assert "assert drawn / not_shared |" in reg.render(store, set(), now=T0), (
        "the pipe must not split the cell")

    def fake_run_suite(observed=None):
        observed["crash"] = {node: line}
        return "FAILED {}\n1 failed, 3 passed in 1.0s\n".format(node)
    monkeypatch.setattr(hgc, "run_suite", fake_run_suite)
    monkeypatch.setattr(hgc, "load_baseline", lambda *a, **k: set())
    monkeypatch.setattr(hgc, "_record_observation", lambda result: "register: not written here")
    hgc.main([])
    assert "  NEW RED  {}   -- {}".format(node, line) in capsys.readouterr().out
