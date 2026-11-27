"""A change that weakens a gate must not be judged by its own weakened copy.

Each test builds a throwaway repo whose HEAD carries a gate that refuses any staged `*.bad` file,
stages a change, and runs the observer the way the hook does: its source on stdin to `python3 -P -`,
cwd at the repo root. The defect each test names is the one it fails on.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

OBSERVER = Path(__file__).resolve().parents[2] / "tools" / "base_judged_gates.py"

GATE = '''import subprocess, sys
from tools.gate_helper import refuses

staged = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True,
                        text=True).stdout.split()
found = [p for p in staged if refuses(p)]
sys.exit(1 if found else 0)
'''
HELPER = "def refuses(path):\n    return path.endswith('.bad')\n"
HOOK = "#!/bin/sh\npython3 -m tools.bad_gate --staged || exit 1\n"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for rel, text in {"tools/__init__.py": "", "tools/bad_gate.py": GATE,
                      "tools/gate_helper.py": HELPER, "tools/git-hooks/pre-commit": HOOK,
                      "tools/unrelated.py": "X = 1\n"}.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    return tmp_path


def _stage(repo: Path, rel: str, text: str) -> None:
    (repo / rel).write_text(text)
    _git(repo, "add", rel)


def _observe(repo: Path) -> tuple[int, list[dict]]:
    r = subprocess.run([sys.executable, "-P", "-"], cwd=repo, input=OBSERVER.read_text(),
                       capture_output=True, text=True)
    log = repo / ".git" / "base_judged_gates.jsonl"
    records = [json.loads(ln) for ln in log.read_text().splitlines()] if log.exists() else []
    return r.returncode, records


def _results(records: list[dict]) -> list[dict]:
    return [res for rec in records for res in rec["results"]]


def test_a_weakened_gate_passes_its_own_change_when_run_from_the_change(repo):
    """The CONTROL for the gap itself: if the change's copy refused, nothing here would be shown."""
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/bad_gate.py", GATE.replace("if found else 0", "if False else 0"))
    rc = subprocess.run([sys.executable, "-m", "tools.bad_gate"], cwd=repo).returncode
    assert rc == 0


def test_a_weakened_gate_inside_the_change_is_caught(repo):
    """Defect: the observer reads the gate from the change, so the weakening judges itself."""
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/bad_gate.py", GATE.replace("if found else 0", "if False else 0"))
    rc, records = _observe(repo)
    (res,) = _results(records)
    assert (res["base"]["rc"], res["change"]["rc"], res["would_refuse"]) == (1, 0, True)
    assert rc == 0, "observe mode refuses nothing"


def test_a_weakened_imported_module_is_caught(repo):
    """Defect: the closure stops at the gate's own file, so weakening what it imports is unseen."""
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/gate_helper.py", "def refuses(path):\n    return False\n")
    _, records = _observe(repo)
    (res,) = _results(records)
    assert res["touched"] == ["tools/gate_helper.py"] and res["would_refuse"] is True


def test_a_gate_line_removed_from_the_hook_is_caught(repo):
    """Defect: only the change's hook is read, so deleting a gate's line deletes its judgement."""
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/git-hooks/pre-commit", "#!/bin/sh\n")
    _, records = _observe(repo)
    (res,) = _results(records)
    assert res["dropped_from_change_hook"] and res["would_refuse"] is True


def test_every_branch_of_the_partition_can_be_taken(repo):
    """Defect: a rerun that fires on everything, or on nothing. An untouched gate is not rerun; an
    honest edit to the gate is rerun and agrees; a weakening is rerun and disagrees."""
    _stage(repo, "tools/unrelated.py", "X = 2\n")
    _, untouched = _observe(repo)
    _stage(repo, "tools/bad_gate.py", GATE + "# a comment\n")
    _stage(repo, "x.bad", "")
    _, honest = _observe(repo)
    _stage(repo, "tools/bad_gate.py", GATE.replace("if found else 0", "if False else 0"))
    _, weakened = _observe(repo)
    assert _results(untouched) == []
    assert [r["would_refuse"] for r in _results(honest)] == [False]
    assert [r["would_refuse"] for r in _results(weakened)][-1] is True


def test_a_commit_that_touches_no_gate_still_leaves_a_record(repo):
    """Defect: the log is written only on a rerun, so an empty log after a week of commits cannot
    tell 'no change touched a gate' from 'the observer never ran', and its own cost goes unrecorded."""
    _stage(repo, "tools/unrelated.py", "X = 2\n")
    _, records = _observe(repo)
    (rec,) = records
    assert rec["results"] == [] and rec["staged"] == 1 and rec["observer_seconds"] >= 0


def test_a_broken_observer_never_reds_the_commit(repo):
    """Defect: observe mode turns into enforce mode by crashing."""
    (repo / ".git" / "base_judged_gates.jsonl").mkdir()  # unwritable log: the write raises
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/bad_gate.py", GATE.replace("if found else 0", "if False else 0"))
    rc, _ = (subprocess.run([sys.executable, "-P", "-"], cwd=repo, input=OBSERVER.read_text(),
                            capture_output=True, text=True).returncode, None)
    assert rc == 0


def _summarise():
    import importlib.util
    spec = importlib.util.spec_from_file_location("bjg", OBSERVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.summarise


def test_the_report_is_ready_only_after_a_week_of_commits_and_counts_what_enforce_reads():
    """Defect: the report calls the log ready on a busy afternoon, or drops a would-refuse."""
    summarise = _summarise()
    hit = {"gate": "g", "deferred": False, "would_refuse": True}
    deep = {"gate": "t", "deferred": True, "would_refuse": None}
    day0 = {"at": "2026-11-20T12:00:00Z", "results": [hit, deep], "gate_data_touched": ["x.mode"],
            "observer_seconds": 4.0}
    day7 = {"at": "2026-11-27T12:00:00Z", "results": [], "gate_data_touched": [],
            "observer_seconds": 3.0}
    busy = summarise([day0, dict(day7, at="2026-11-20T18:00:00Z")])
    week = summarise([day0, day7])
    assert not busy["ready"] and week["ready"]  # the branch can be taken, and is not taken early
    assert (week["would_refuse"], week["deferred"], week["gate_data_touched_commits"]) == (1, 1, 1)
    assert week["per_gate"]["g"]["would_refuse"] == 1 and week["observer_seconds"]["max"] == 4.0
    assert summarise([]) == {"commits": 0, "ready": False}


def _enforce(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-P", "-", "--enforce"], cwd=repo,
                          input=OBSERVER.read_text(), capture_output=True, text=True)


def test_enforce_refuses_a_weakened_gate_and_passes_the_rest_of_the_partition(repo):
    """Defect: enforce refuses nothing (the observe line left in place), or refuses everything.
    Untouched gate and honest gate edit pass; a weakened gate and a weakened import are refused."""
    _stage(repo, "tools/unrelated.py", "X = 2\n")
    untouched = _enforce(repo)
    _stage(repo, "tools/bad_gate.py", GATE + "# a comment\n")
    honest = _enforce(repo)
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/bad_gate.py", GATE.replace("if found else 0", "if False else 0"))
    weakened = _enforce(repo)
    _stage(repo, "tools/bad_gate.py", GATE)
    _stage(repo, "tools/gate_helper.py", "def refuses(path):\n    return False\n")
    weakened_import = _enforce(repo)
    assert [untouched.returncode, honest.returncode] == [0, 0]
    assert [weakened.returncode, weakened_import.returncode] == [1, 1]
    last = weakened.stdout.strip().splitlines()[-1]
    assert "REFUSED" in last and "tools.bad_gate" in last  # surgical_land names it from this line


def test_enforce_refuses_a_gate_line_deleted_from_the_changes_hook(repo):
    """Defect: enforce reads the change's hook, so dropping a gate's line drops its judgement."""
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/git-hooks/pre-commit", "#!/bin/sh\n")
    assert _enforce(repo).returncode == 1


def test_a_crashed_judge_fails_open_and_says_so(repo):
    """Defect: a judge read from HEAD that crashes into a refusal also refuses its own repair."""
    (repo / ".git" / "base_judged_gates.jsonl").mkdir()
    _stage(repo, "x.bad", "")
    _stage(repo, "tools/bad_gate.py", GATE.replace("if found else 0", "if False else 0"))
    r = _enforce(repo)
    assert r.returncode == 0 and "JUDGE FAILED" in r.stderr
