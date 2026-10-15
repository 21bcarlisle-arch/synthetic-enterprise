"""A run stamped with a commit is published only if the code it imported WAS that commit's bytes.

The 2026-10-13 13:44Z run was stamped 2248e3baf and published as that commit's figures, while the
shared tree it ran in held imported files that were on no commit. Defect named by this file: a
dirty imported path is published under a clean stamp.

The chain is three hops -- `sim_runner` reads the closure at launch, `run_annual_report` writes the
reading into `producing_commit`, `process_run_complete` refuses on it -- and the controls below
walk it with each hop's real code, so a field renamed on one side reds here rather than going
quietly fail-open.
"""

import json
import subprocess
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

import background.process_run_complete as prc
import background.sim_runner as sim_runner
from background import code_closure
from tools import run_annual_report as rar


def _header(reading, commit="abc1234"):
    """The producer's own header, so the key the publisher reads is the key the run writes."""
    return rar._run_identity_header(
        {"total_net_gbp": 1.0}, datetime(2026, 10, 14, tzinfo=timezone.utc), commit,
        {"digest": "w"}, {"risk_committee": "mock"}, from_launch=True,
        imports_off_commit=rar._imports_off_commit_record(reading, commit))


# ── the reading ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def git(*a):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "pkg").mkdir()
    for name in ("a.py", "b.py"):
        (tmp_path / "pkg" / name).write_text("x = 1\n")
    (tmp_path / "pkg" / "elsewhere.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=tmp_path,
                          capture_output=True, text=True, check=True).stdout.strip()
    closure = {"pkg/a.py", "pkg/b.py", "pkg/c.py"}
    monkeypatch.setattr(code_closure, "import_closure",
                        lambda entry, r=None: {p for p in closure if (tmp_path / p).exists()})
    return tmp_path, head


def test_the_reading_names_modified_and_untracked_imports_and_only_those(repo):
    """MUTATION: drop the `ls-files --others` leg and `pkg/c.py` goes unnamed; diff the whole tree
    instead of the closure and `pkg/elsewhere.py` is named."""
    root, head = repo
    assert code_closure.imports_off_commit("pkg/a.py", head, root)["paths"] == [], (
        "a clean tree must read as a MEASURED empty list, the one value that may publish")
    (root / "pkg" / "b.py").write_text("x = 2\n")
    (root / "pkg" / "c.py").write_text("x = 3\n")
    (root / "pkg" / "elsewhere.py").write_text("x = 4\n")
    assert code_closure.imports_off_commit("pkg/a.py", head, root)["paths"] == [
        "pkg/b.py", "pkg/c.py"]


def test_a_comment_or_docstring_edit_is_named_prose_only_and_a_code_edit_is_not(repo):
    """Comments do not run. MUTATION: treat every diff as prose-only and `pkg/b.py`'s code change
    goes unnamed; drop the docstring strip and `pkg/a.py` is named for its docstring."""
    root, head = repo
    (root / "pkg" / "a.py").write_text('"""A new docstring."""\n# a comment\nx = 1\n')
    (root / "pkg" / "b.py").write_text("x = 1  # same code\ny = 2\n")
    r = code_closure.imports_off_commit("pkg/a.py", head, root)
    assert r["paths"] == ["pkg/b.py"] and r["prose_only"] == ["pkg/a.py"]


def test_a_reading_that_cannot_be_taken_is_none_with_its_reason_never_empty(repo):
    root, _head = repo
    for commit in ("unknown", "", "0000000"):
        r = code_closure.imports_off_commit("pkg/a.py", commit, root)
        assert r["paths"] is None and r["unavailable_because"], commit


# ── the publisher ────────────────────────────────────────────────────────────────────────────


def test_every_verdict_of_the_refusal_is_reachable():
    """The partition first: a refusal that refuses everything passes every leg below but this."""
    clean = prc.imports_off_commit_refusal(_header({"commit": "abc1234", "paths": []}))
    dirty = prc.imports_off_commit_refusal(_header({"commit": "abc1234", "paths": ["saas/x.py"]}))
    unmeasured = prc.imports_off_commit_refusal(_header(None))
    legacy = prc.imports_off_commit_refusal({"producing_commit": {"commit": "abc1234"}})
    assert clean is None and legacy is None and dirty and unmeasured


def test_a_reading_taken_against_another_commit_does_not_describe_this_run():
    """MUTATION: drop the commit match in `_imports_off_commit_record` and a clean reading of an
    older tree licenses a run stamped with a newer one."""
    why = prc.imports_off_commit_refusal(_header({"commit": "fff9999", "paths": []}))
    assert why and "fff9999" in why


@pytest.fixture
def publish(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "done")
    monkeypatch.setattr(prc, "_record_archived_marker", lambda dest: None)
    monkeypatch.setattr(prc, "_content_publish_window", lambda: {"open": True, "reason": "test"})
    regenerated, logged = [], []
    monkeypatch.setattr(prc, "log", logged.append)
    monkeypatch.setattr(prc, "regenerate_report", lambda p: regenerated.append(p) or False)

    def _make(data):
        out = tmp_path / "run_output.json"
        out.write_text(json.dumps(data))
        marker = tmp_path / "staging" / "run_complete_20261014T000000Z.md"
        marker.parent.mkdir(exist_ok=True)
        marker.write_text("Simulation Run Complete\n\nGit: abc1234\nJSON: {}\n".format(out))
        return prc._process(str(marker)), marker, regenerated, logged

    return _make


def test_a_dirty_imported_path_is_not_published_under_a_clean_stamp(publish):
    """THE DEFECT. MUTATION: delete the refusal in `_process` and the report regenerates."""
    rc, marker, regenerated, log = publish(
        _header({"commit": "abc1234", "paths": ["simulation/churn_journey.py"]}))
    assert regenerated == []
    assert rc == prc.EXIT_PUBLISH_DID_NOT_LAND, "a refusal published nothing and must not read as 0"
    assert not marker.exists(), "a run that can never publish must not sit in the queue"
    assert any("REFUSED" in line and "simulation/churn_journey.py" in line for line in log), (
        "the refusal names the paths")


def test_a_measured_clean_run_proceeds_to_publish(publish):
    """BOTH WAYS."""
    _rc, _marker, regenerated, _log = publish(_header({"commit": "abc1234", "paths": []}))
    assert len(regenerated) == 1


# ── the launcher hands the reading to the run ────────────────────────────────────────────────


def test_the_launchers_reading_reaches_the_publisher_through_the_runs_argv(tmp_path, monkeypatch):
    """MUTATION: stop `run_simulation` passing `--imports-off-commit` and the header reads
    unmeasured, so this reds on the dirty path no longer being the reason named."""
    seen = {}
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "log", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "update_agent_status", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "record_run_outcome", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "run_budget_seconds", lambda: 1)
    monkeypatch.setattr(sim_runner, "imports_off_commit_at_launch", lambda head: {
        "commit": head, "paths": ["saas/x.py"], "unavailable_because": None})

    def _run(argv, **_kw):
        seen["argv"] = argv
        return SimpleNamespace(returncode=1, stderr="")

    monkeypatch.setattr(sim_runner.subprocess, "run", _run)
    sim_runner.run_simulation()
    argv = seen["argv"]
    assert "--imports-off-commit" in argv
    reading = json.loads(argv[argv.index("--imports-off-commit") + 1])
    why = prc.imports_off_commit_refusal(_header(reading))
    assert why and "saas/x.py" in why


# ---- the run itself, and the stamp against ORIGIN (2026-10-15) ---------------------------------
# The shared HEAD carried eight local commits origin lacked, so every run read clean against its
# own stamp while importing code on no published history.

def _quiet(monkeypatch):
    from background import sim_runner
    said = []
    monkeypatch.setattr(sim_runner, "log", lambda m: said.append(m))
    return sim_runner, said


def test_a_run_starts_only_on_code_that_is_origins_and_each_refusal_names_why(monkeypatch):
    """The whole partition, admitting branch first: a guard that defers everything passes every
    refusal leg. Fires on: the gate unwired from any leg, or deferring a clean origin tree."""
    sr, said = _quiet(monkeypatch)
    clean = {"commit": "abc1234", "paths": [], "unavailable_because": None, "prose_only": ["x.py"]}
    assert sr.code_admission("abc1234", off_commit=clean, on_origin=True)["admitted"] is True
    dirty = dict(clean, paths=["tools/demand_vector_coverage.py"])
    r = sr.code_admission("abc1234", off_commit=dirty, on_origin=True)
    assert r["admitted"] is False and "demand_vector_coverage" in r["reason"]
    unread = dict(clean, paths=None, unavailable_because="git said no")
    assert "could not be read" in sr.code_admission("abc1234", off_commit=unread, on_origin=True)["reason"]
    r = sr.code_admission("abc1234", off_commit=clean, on_origin=False)
    assert r["admitted"] is False and "not on origin/main" in r["reason"]
    assert "cannot tell" in sr.code_admission("abc1234", off_commit=clean, on_origin=None)["reason"]
    assert any(m.startswith("DEFERRED this cycle") for m in said)


def test_commit_on_origin_reads_git_for_all_three_answers(tmp_path):
    """True for an ancestor of origin/main, False for a local commit beyond it, None for a commit
    git does not know. Fires on: the rc mapping collapsed (False read as None or True)."""
    import subprocess

    from background import sim_runner

    def git(*a):
        return subprocess.run(["git", *a], cwd=tmp_path, capture_output=True, text=True,
                              check=True).stdout.strip()
    git("init", "-q")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "a")
    a = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/main", a)
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "b")
    b = git("rev-parse", "HEAD")
    assert sim_runner.commit_on_origin(a, tmp_path) is True
    assert sim_runner.commit_on_origin(b, tmp_path) is False
    assert sim_runner.commit_on_origin("0" * 40, tmp_path) is None


def test_the_publisher_refuses_a_stamp_origin_never_received():
    """Fires on: the backstop dropped from the refusal, or refusing a stamp that is on origin."""
    from background import process_run_complete as prc
    run = {"producing_commit": {"commit": "10e90b5c7"}}
    assert "not on origin/main" in prc.stamp_not_on_origin_refusal(run, on_origin=lambda c: False)
    assert prc.stamp_not_on_origin_refusal(run, on_origin=lambda c: True) is None
    assert prc.stamp_not_on_origin_refusal(run, on_origin=lambda c: None) is None


def test_the_runner_loop_consults_the_code_gate_before_it_runs():
    """Fires on: code_admission defined but never called, the rule with no production caller."""
    import ast
    import inspect

    from background import sim_runner
    calls = {n.func.id for n in ast.walk(ast.parse(inspect.getsource(sim_runner.main)))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "code_admission" in calls and "run_simulation" in calls
