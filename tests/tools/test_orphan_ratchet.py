"""R15 on the orphan ratchet, both ways, on a REAL synthetic repo rather than on mocks.

The class: `docs/staging/done/WORKER_REPORT_NO_CALLER_CLASS_CENSUS_2026-08-09.md` -- 13 instances
in 13 days, 8 found by accident. The control has to fire on the 14th at the moment it is created.

WHY A SYNTHETIC TREE AND NOT MONKEYPATCHED ROWS. The thing under test is a reachability claim over
files on disk. A test that hands the ratchet a hand-built row list proves the set arithmetic and
nothing about whether the tree is read correctly -- and every real instance in the census was a
misreading of the tree, never bad arithmetic.

  * FIRES   -- a new module nothing runs; a CLI with `__main__` that no unit schedules (census
              instance #10, the one the current index structurally cannot report).
  * SILENT  -- a module a unit runs; a module imported by one; a module reached only BY PATH
              (subprocess), which is how most of this machine actually runs.
  * FAIL-CLOSED -- a broken schedule parser (vacuity) and a truncated index walk (coverage) both
              REFUSE rather than certify.
  * RATCHET -- the standing backlog does not fail the build; only growth does.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import capability_index as ci
from tools import orphan_ratchet as orat


def _repo(tmp_path: Path, *, unit: str, modules: dict[str, str]) -> Path:
    """A minimal tree with a committed systemd unit and some modules."""
    root = tmp_path / "repo"
    (root / "background").mkdir(parents=True)
    (root / "background" / "demo.service").write_text(
        "[Unit]\nDescription=demo\n\n[Service]\nExecStart={}\n".format(unit))
    for rel, body in modules.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return root


def _orphans(root: Path) -> set[str]:
    return set(orat.compute(root)["orphans"])


def _workflow(root: Path, body: str, name: str = "deploy.yml") -> None:
    d = root / ".github" / "workflows"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(body)


# ------------------------------------------------- CI WORKFLOWS ARE RUNNERS TOO
# Added 2026-08-20. A deploy-time checker that runs on every push was reported as an
# orphan, and the only way to clear that was `--freeze` marking it "deliberately
# dormant" -- recording something untrue to satisfy a control. A false positive whose
# remedy is a lie corrupts the record the ratchet exists to keep honest.

def test_a_module_a_ci_workflow_runs_is_not_an_orphan(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "tools/deploy_check.py": "def main():\n    return 2\n",
    })
    _workflow(root, """
name: Deploy
on: {push: {branches: [main]}}
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: python3 tools/deploy_check.py
""")
    assert "tools.deploy_check" not in _orphans(root)


def test_the_module_form_in_a_workflow_counts_too(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "tools/deploy_check.py": "def main():\n    return 2\n",
    })
    _workflow(root, """
name: Deploy
on: {push: {}}
jobs:
  deploy:
    steps:
      - run: python3 -m tools.deploy_check
""")
    assert "tools.deploy_check" not in _orphans(root)


def test_prose_in_a_workflow_is_not_an_entrypoint(tmp_path):
    """The `Description=` failure, restated for YAML. Workflows are mostly comments and
    step names; if those counted, a module could be certified as run by being MENTIONED,
    and the vacuity floor would stop meaning anything."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "tools/deploy_check.py": "def main():\n    return 2\n",
    })
    _workflow(root, """
name: Deploy
on: {push: {}}
jobs:
  deploy:
    steps:
      # historical note: this step used to call tools/deploy_check.py
      - name: something about tools/deploy_check.py
        run: echo hello
""")
    assert "tools.deploy_check" in _orphans(root)


def test_an_unparseable_workflow_cannot_wedge_every_commit(tmp_path):
    """It must degrade to "this workflow runs nothing I can see" -- which surfaces as a
    loud false orphan -- rather than raising and blocking the whole repo."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
    })
    _workflow(root, "this: is: not: valid: yaml:\n  - [unclosed\n")
    assert orat._workflow_run_lines(root) == []
    _orphans(root)      # must not raise


# ------------------------------------------------------------------ FIRES

def test_a_module_nothing_runs_is_an_orphan(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "background/nobody_calls_me.py": "def f():\n    return 2\n",
    })
    orphans = _orphans(root)
    assert "background.nobody_calls_me" in orphans
    assert "background.runner" not in orphans


def test_a_cli_with_a_main_block_that_nothing_schedules_is_an_orphan(tmp_path):
    """CENSUS INSTANCE #10, and the reason the entrypoint set is the schedule and not `__main__`.

    `forward_attachment_register --write` is a regeneration step nothing ever runs. It has a
    `__main__` block, so `capability_index._is_entrypoint` returns True for it and it can never
    be reported as an orphan by that index. Here it must be."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "background/regen.py": (
            "def write():\n    return 1\n\n\n"
            'if __name__ == "__main__":\n    raise SystemExit(write())\n'),
    })
    assert "background.regen" in _orphans(root), \
        "a __main__ block made it look scheduled -- this is census instance #10"


def test_the_gate_returns_nonzero_when_a_new_orphan_appears(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
    })
    base = tmp_path / "baseline.json"
    orat.freeze(root, base)
    assert orat.run(root, base) == 0

    (root / "background" / "fresh_orphan.py").write_text("def f():\n    return 1\n")
    assert orat.run(root, base) == 1, "a NEW orphan did not fail the gate"


# ------------------------------------------------------------------ SILENT

def test_a_module_the_unit_runs_by_script_path_is_not_an_orphan(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 background/runner.py", modules={
        "background/runner.py": "def main():\n    return 1\n",
    })
    assert "background.runner" not in _orphans(root)


def test_an_asgi_app_is_not_an_orphan(tmp_path):
    """`-m uvicorn background.file_api:app` -- the captured module is the RUNNER, not the app.
    `background.file_api` was reported as an orphan until this form was handled."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m uvicorn background.api:app --port 8765",
                 modules={"background/api.py": "app = object()\n"})
    assert "background.api" not in _orphans(root)


def test_a_module_reached_only_by_subprocess_path_is_not_an_orphan(tmp_path):
    """HOW THIS MACHINE ACTUALLY RUNS. `sim_runner` shells out to `simulation/run_phase2b.py`;
    the publisher shells out to the generators. Those are not import edges, and dropping them
    reported 550 orphans of 904 modules -- a number alarming enough to be believed."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py":
            'import subprocess\n\n\ndef main():\n'
            '    subprocess.run(["python3", "background/worker.py"])\n',
        "background/worker.py": "def work():\n    return 1\n",
    })
    assert "background.worker" not in _orphans(root), \
        "a subprocess path-reference was dropped as an edge"


def test_an_imported_module_is_not_an_orphan(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "from background import helper\n\n\ndef main():\n"
                                "    return helper.f()\n",
        "background/helper.py": "def f():\n    return 1\n",
    })
    assert "background.helper" not in _orphans(root)


# ------------------------------------------------------------------ FAIL-CLOSED

def test_a_broken_schedule_parser_refuses_rather_than_certifies(tmp_path, monkeypatch):
    """With no entrypoints every module is 'unreachable'. The honest answer is that the PARSER
    is broken, not that the machine runs nothing -- and certifying either way would be the
    fail-open that authorises the thing this exists to prevent."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner",
                 modules={"background/runner.py": "def main():\n    return 1\n"})
    monkeypatch.setattr(orat, "SCHEDULE_GLOBS", ("background/*.nothing",))
    state = orat.compute(root)
    assert any("VACUITY" in p for p in state["problems"]), state["problems"]
    assert orat.run(root, tmp_path / "b.json") == 1


def test_a_truncated_index_walk_refuses_rather_than_certifies(tmp_path, monkeypatch):
    """A walk that stops early looks exactly like a small clean codebase. The oracle is GIT, a
    different substrate from the walk it is checking."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner",
                 modules={"background/runner.py": "def main():\n    return 1\n"})
    monkeypatch.setattr(orat, "_tracked_py_count", lambda r: 500)   # git says 500, walk sees 1
    state = orat.compute(root)
    assert any("COVERAGE" in p for p in state["problems"]), state["problems"]


def test_the_coverage_oracle_counts_the_same_population_it_measures(tmp_path):
    """THE CONTROL'S OWN FALSE POSITIVE, kept as a test because it nearly shipped.

    The first oracle asked git for every `*.py` in the repo and compared 904 indexed rows
    against 2202 tracked files -- the index excludes tests and non-declared roots by design, so
    it fired on every commit forever. An only-fail control wedges rather than protects, so the
    oracle must count tracked files under the SAME roots, minus the SAME evidence files."""
    counted = orat._tracked_py_count(orat.ROOT)
    indexed = len(ci.source_files(orat.ROOT))
    assert counted > 0, "the oracle found no tracked files -- it is measuring nothing"
    assert abs(counted - indexed) < indexed * 0.2, (
        "oracle counts {} but the index sees {} -- these are different populations and the "
        "gate would red forever".format(counted, indexed))


# ------------------------------------------------------------------ RATCHET

def test_the_standing_backlog_does_not_fail_the_build(tmp_path):
    """The design point. ~400 modules are unreachable today; nobody must fix them to commit.
    A control that reds on the existing pile is a control everyone learns to bypass."""
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "background/legacy_a.py": "def f():\n    return 1\n",
        "background/legacy_b.py": "def f():\n    return 1\n",
    })
    base = tmp_path / "baseline.json"
    data = orat.freeze(root, base)
    assert set(data["orphans"]) >= {"background.legacy_a", "background.legacy_b"}
    assert orat.run(root, base) == 0, "the frozen backlog failed its own gate"


def test_the_live_baseline_matches_the_live_tree():
    """The committed baseline must describe THIS repo. A stale baseline silently re-admits every
    orphan created since it was frozen."""
    state = orat.compute()
    assert state["problems"] == [], state["problems"]
    baseline = orat.load_baseline()
    assert orat.new_orphans(state, baseline) == [], \
        "the working tree carries orphans the baseline does not -- re-freeze or wire them"


def test_freezing_records_what_it_froze(tmp_path):
    root = _repo(tmp_path, unit="/usr/bin/python3 -m background.runner", modules={
        "background/runner.py": "def main():\n    return 1\n",
        "background/dormant.py": "def f():\n    return 1\n",
    })
    base = tmp_path / "b.json"
    orat.freeze(root, base)
    data = json.loads(base.read_text())
    assert "background.dormant" in data["orphans"]
    assert data["module_count"] >= 2
    assert "_doc" in data, "a baseline with no explanation is a number nobody can audit"


@pytest.mark.parametrize("caller,expected", [
    ("background.foo", "background.foo"),
    ("background.foo (by path)", "background.foo"),
])
def test_path_annotated_callers_are_normalised(caller, expected):
    """The bug that reported 550 orphans: `"x (by path)" in imports` is False for every module,
    so every subprocess edge was silently discarded."""
    assert orat._caller_module(caller) == expected
