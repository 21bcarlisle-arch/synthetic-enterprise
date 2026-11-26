"""The billing ledger the invariant gate grades is written by the world the run ran.

The defect these name (26 Nov 2026): `process_run_complete` regenerated the ledger in the shared
tree, which held an uncommitted issue-order edit to `simulation/arrears_engine.py`, and the gate
refused the 001e4f680a book on PROS-2019-0305, a breach committed code does not produce.

  * `..._a_dirty_world_writer_is_regenerated_on_the_run_commit` -- write the ledger in-process
    whatever the reading says (the old step) and the ledger reads the DIRTY bytes: fires.
  * `..._every_route_can_be_taken` -- the partition control: a router that always refuses, or
    always takes the shared tree, cannot pass it.
  * `..._the_gate_does_not_grade_an_unproven_ledger` -- drop the provenance check from
    `_domain_invariant_gate_permits_publish` and the gate grades the book on disk: fires.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import background.process_run_complete as prc

_WRITER = '''
from simulation.arrears_engine import ISSUE

def generate(run_json_path=None, out_path=None):
    open(out_path, "w").write(ISSUE)
'''


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()


def _repo(tmp_path):
    repo = tmp_path / "shared"
    (repo / "tools").mkdir(parents=True)
    (repo / "simulation").mkdir()
    (repo / "tools" / "__init__.py").write_text("")
    (repo / "simulation" / "__init__.py").write_text("")
    (repo / "tools" / "generate_billing_ledger.py").write_text(_WRITER)
    (repo / "simulation" / "arrears_engine.py").write_text('ISSUE = "committed"\n')
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "run commit")
    return repo, _git(repo, "rev-parse", "HEAD")


def test_a_dirty_world_writer_is_regenerated_on_the_run_commit(tmp_path, monkeypatch):
    """The shared tree's world file says "dirty"; the run's commit says "committed". The ledger
    must say what the run's world said."""
    repo, commit = _repo(tmp_path)
    (repo / "simulation" / "arrears_engine.py").write_text('ISSUE = "dirty"  # in flight\n')
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)
    monkeypatch.setattr(prc, "HEAD_CHECKOUT_ROOT", tmp_path / "checkouts")
    monkeypatch.setattr(prc, "_machine_data_dir", lambda: repo)
    from background import code_closure
    monkeypatch.setattr(code_closure, "_GRAPH_CACHE", {})

    def shared_tree(json_path, out_path):  # what the step did before: the shared tree's bytes
        Path(out_path).write_text("dirty")

    out = tmp_path / "ledger.json"
    record = prc.generate_ledger_on_run_commit(tmp_path / "run.json", commit, out_path=out,
                                               in_process_fn=shared_tree)
    assert record["off_commit_paths"] == ["simulation/arrears_engine.py"], record
    assert record["refused"] is None, record
    assert out.read_text() == "committed", (
        "the ledger was written by a world the run never ran: " + str(record))
    assert prc.ledger_provenance_refusal(commit[:10], record) is None


def test_every_route_can_be_taken():
    """Clean -> shared tree; off commit -> checkout; unmeasured or failed -> refused, by name."""
    seen = []

    def run(paths, checkout_fails=False):
        return prc.generate_ledger_on_run_commit(
            "run.json", "abc1234", out_path="ledger.json",
            reading_fn=lambda c: {"paths": paths, "unavailable_because": "git said no"},
            in_process_fn=lambda j, o: seen.append("shared"),
            in_checkout_fn=lambda j, c, o: (seen.append("checkout"),
                                            "boom" if checkout_fails else None)[1])

    clean, off, unmeasured, failed = (run([]), run(["simulation/arrears_engine.py"]), run(None),
                                      run(["simulation/arrears_engine.py"], checkout_fails=True))
    assert clean["route"].startswith("shared tree") and not clean["refused"]
    assert off["route"].startswith("clean checkout") and not off["refused"]
    assert "git said no" in unmeasured["refused"] and unmeasured["route"] is None
    assert "boom" in failed["refused"] and "simulation/arrears_engine.py" in failed["refused"]
    assert seen == ["shared", "checkout", "checkout"]
    assert all(prc.ledger_provenance_refusal("abc1234", r) is None for r in (clean, off))
    assert prc.ledger_provenance_refusal("abc1234", None)
    assert "not abc1234" in prc.ledger_provenance_refusal("abc1234", dict(clean, commit="fff9999"))


def test_the_gate_does_not_grade_an_unproven_ledger(tmp_path, monkeypatch):
    from tools import domain_invariant_runner as runner
    monkeypatch.setattr(prc, "DOMAIN_INVARIANT_TABLE", tmp_path / "DOMAIN_INVARIANTS.md")
    monkeypatch.setattr(prc, "log", lambda m: None)
    monkeypatch.setattr(runner, "load_exceptions", lambda p: {"enforce": True})

    def graded(**kw):
        raise AssertionError("the gate read the book")
    monkeypatch.setattr(runner, "load_book", graded)
    monkeypatch.setattr(prc, "_LEDGER_PROVENANCE", {
        "commit": "abc1234", "route": None, "off_commit_paths": ["simulation/arrears_engine.py"],
        "refused": "1 world-writer file(s) differ from abc1234 (simulation/arrears_engine.py)"})
    ok, reason = prc._domain_invariant_gate_permits_publish("abc1234")
    assert ok is False
    assert "not that run's world" in reason and "simulation/arrears_engine.py" in reason, reason
    assert (tmp_path / "DOMAIN_INVARIANTS.md").is_file(), "the table must still be written"
