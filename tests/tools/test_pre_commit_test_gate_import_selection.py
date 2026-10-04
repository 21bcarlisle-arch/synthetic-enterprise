"""The gate selects the tests that IMPORT a changed module, not only the ones named for it.

`docs/staging/done/WORKER_FINDING_THE_HEAD_REDS_TURNING_COMMITS_AND_WHY_THE_GATE_DID_NOT_SELECT_THEM_2026-10-04.md`:
7 of 17 commits that turned a test red at origin changed a module whose consumer test was named
for its aspect. The gate ran and passed on every one; the red test was simply not in what it ran.
"""
from __future__ import annotations

import subprocess

from tools import pre_commit_test_gate as g

# S4 of the finding: named `test_policy_cost_coverage`, so the stem glob for `policy_costs` never
# reaches it, and it imports the module as `from simulation import policy_costs as pc`.
MODULE = "simulation/policy_costs.py"
ASPECT_NAMED = "tests/simulation/test_policy_cost_coverage.py"


def test_the_aspect_named_consumer_is_selected_and_the_stem_glob_alone_misses_it():
    """The control leg first: if `tests_for` already found it, this selection added nothing."""
    assert ASPECT_NAMED not in g.tests_for(MODULE)
    assert ASPECT_NAMED in g.importing_tests(MODULE)
    assert ASPECT_NAMED not in g.select_targets([MODULE])  # the bounded run's, not the main one's
    assert ASPECT_NAMED in g.import_derived_extras([MODULE], g.select_targets([MODULE]))


def test_from_package_import_module_is_an_import_of_the_module():
    """The shape all four standing stem reds used. A regex on `from <dotted> import` misses it."""
    assert g._imports_module("from simulation import policy_costs as pc\n", "simulation.policy_costs")
    assert g._imports_module("from simulation import (a, policy_costs)\n", "simulation.policy_costs")
    assert g._imports_module("import simulation.policy_costs as pc\n", "simulation.policy_costs")
    assert g._imports_module("from simulation.policy_costs import X\n", "simulation.policy_costs")
    assert g._imports_module("def f():\n    from simulation import policy_costs\n",
                             "simulation.policy_costs")


def test_a_mention_or_a_neighbour_is_not_an_import():
    """`-w` on the grep finds the stem in prose too; the AST is what refuses it."""
    dotted = "simulation.policy_costs"
    assert not g._imports_module('"""see simulation/policy_costs.py"""\n', dotted)
    assert not g._imports_module("from simulation import policy_costs_v2\n", dotted)
    assert not g._imports_module("from company import policy_costs\n", dotted)
    assert not g._imports_module("import simulation\n", dotted)


def test_out_of_scope_paths_select_nothing():
    """A package `__init__` would select the whole package's suite; a test file is its own
    selection; a non-code path has no importers."""
    assert g.importing_tests("simulation/__init__.py") == []
    assert g.importing_tests(ASPECT_NAMED) == []
    assert g.importing_tests("docs/design/README.md") == []


def _fake_pytest(monkeypatch, verdicts: dict, clock: list):
    """`verdicts[file]` is a return code, or "slow" for a run past the per-file cap. Each call
    advances a fake monotonic clock by `clock[0]` seconds."""
    now = [0.0]

    def run(argv, **kw):
        f = argv[3]
        now[0] += clock[0]
        if verdicts[f] == "slow":
            raise subprocess.TimeoutExpired(argv, kw["timeout"])
        return subprocess.CompletedProcess(argv, verdicts[f])
    monkeypatch.setattr(g.subprocess, "run", run)
    monkeypatch.setattr(g.time, "monotonic", lambda: now[0])


def test_every_branch_of_the_bounded_run_can_be_taken(monkeypatch):
    """The partition, asserted whole: green, red, over the cap, past the budget. A run that
    refused everything, or graded nothing, passes any one of these alone."""
    files = ["a", "b", "c", "d"]
    _fake_pytest(monkeypatch, dict(a=0, b=5, c="slow", d=0), [1.0])
    assert g.run_import_derived(files, {}) == (True, ["c"], [])

    _fake_pytest(monkeypatch, dict(a=0, b=1, c=0, d=0), [1.0])
    assert g.run_import_derived(files, {})[0] is False, "a red importer did not refuse"

    _fake_pytest(monkeypatch, dict(a=0, b=0, c=0, d=0), [g.IMPORT_DERIVED_BUDGET_S / 2])
    green, over, unreached = g.run_import_derived(files, {})
    assert green and over == [] and unreached == ["c", "d"]


def test_main_refuses_on_a_red_importer_after_a_green_main_run(monkeypatch):
    """The wiring: a green named selection is not the end of the gate. The sibling checks are
    neutralised as in `test_pytest_subprocess_env_strips_GIT_star`, which says why for each."""
    for name in ("_wall_crossing_landed_check", "_symbol_landing_check",
                 "_wall_channel_census_check"):
        monkeypatch.setattr(g, name, lambda staged: (True, ""))
    monkeypatch.setattr(g, "staged_files", lambda: [MODULE])
    monkeypatch.setattr(g, "selection_paths", lambda staged: (staged, ""))
    monkeypatch.setattr(g, "select_targets", lambda files: ["tests/simulation/test_policy_costs.py"])
    monkeypatch.setattr(g.subprocess, "run",
                        lambda *a, **kw: subprocess.CompletedProcess(a, 0, "", ""))
    asked = []
    monkeypatch.setattr(g, "import_derived_extras", lambda files, already: [ASPECT_NAMED])
    monkeypatch.setattr(g, "run_import_derived",
                        lambda extras, env: asked.append(extras) or (False, [], []))
    assert g.main() == 1
    assert asked == [[ASPECT_NAMED]]
    monkeypatch.setattr(g, "run_import_derived", lambda extras, env: (True, [ASPECT_NAMED], []))
    assert g.main() == 0
