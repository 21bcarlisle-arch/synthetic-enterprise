"""R15 proofs for the commit-time wall-crossing check — the tool mode and its caller.

WHAT IS UNDER TEST, AND WHY IT EXISTS
--------------------------------------
`tools/wall_crossing_dispositions.py --at-head` compares the register's CLAIMS
against the COMMITTED code. It was built on 2026-08-10 after the third instance
in two days of a `cut` row that no commit contained, it is proven against real
history — and it had NO AUTOMATED CALLER, so the class recurred one KNIFE step
later with five files of step 21 sitting untracked while the atom's own record
said LANDED (`WORKER_FINDING_THE_CLOSE_TIME_CHECK_THAT_CATCHES_THIS_HAS_NO_CALLER_2026-08-13`).

Two things are proven here, and they are different claims:

  1. THE TOOL'S NEW MODE (`--at-tree` / `run_at_tree`) genuinely measures ONE
     NAMED TREE on BOTH sides — register AND code — rather than the desk. The
     falsifiers are REAL TREES from this repo's own history, not synthetic
     fixtures: a tree where the register and the code disagree must red, and
     HEAD must not. A mode that could only ever return OK is the fail-open shape
     this whole family of controls exists to refuse.
  2. THE CALLER in `tools/pre_commit_test_gate.py` is wired FAIL-CLOSED and in
     scope for the commits that carry the defect. Each refusal path has a
     mutation showing the gate reds on it and nothing else.

WHY `--at-tree` AND NOT `--at-head` AT COMMIT TIME
---------------------------------------------------
`--at-head` is asymmetric by design: working-tree register vs HEAD's code. At
pre-commit time HEAD is the tree the commit REPLACES, so gating on it reds the
commit that REPAIRS a divergence and passes the one that creates it. The caller
therefore passes `git write-tree` — the tree the commit would create — which is
the same subject `tools/surgical_land.py` gates on.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402
from tools.wall_crossing_dispositions import (  # noqa: E402
    REGISTER_DOC,
    RegisterError,
    load_register,
    load_register_at,
    run_at_tree,
)

# A REAL commit of this repo whose own tree carries three live crossings its own
# register never ruled on (KNIFE3 step 2 landed the register; these three edges
# arrived through a bridge package and were disposed later). Used as the
# can-it-fail witness, because a control proven only against a fixture it wrote
# itself is proven against its author's imagination.
DIVERGENT_TREE = "d06df9514"
# The commit that ADDED the register; its parent therefore does not contain it.
REGISTER_ADDED = "8c1337a09"


# ── 1. THE TOOL: the mode measures a named tree, and it can fail ─────────────

def test_at_tree_reds_on_a_real_historical_tree():
    """CAN IT FAIL? On a real tree of this repo, yes — three unexamined edges."""
    findings, report = run_at_tree(DIVERGENT_TREE)
    assert findings, "a tree with three unruled live crossings must not reconcile"
    assert all("LIVE CROSSING WITH NO DISPOSITION" in f for f in findings)
    assert report["measured_crossings"] == 82


def test_at_tree_is_green_at_head():
    """And the other way: the tree the repo actually publishes reconciles.

    Without this, `test_at_tree_reds_on_a_real_historical_tree` is satisfied by a
    checker that reds on everything.
    """
    findings, _ = run_at_tree("HEAD")
    assert findings == [], f"HEAD does not reconcile: {findings}"


def test_the_measurement_follows_THE_REV_and_not_the_desk():
    """The code side is read from the named tree, not from the working tree.

    82 crossings at the historical tree against 22 today: if the mode were
    quietly measuring the desk, these two numbers would be equal.
    """
    _, old = run_at_tree(DIVERGENT_TREE)
    _, now = run_at_tree("HEAD")
    assert old["measured_crossings"] != now["measured_crossings"]


def test_the_register_is_read_from_the_rev_and_not_the_desk():
    """The RULED side too — the half a `--at-head` run deliberately does not do.

    This is the property that makes the commit-time mode a statement about the
    commit: on this shared working tree the register on disk routinely carries
    other lanes' half-finished edits, and a gate that read it would be judging
    the desk while claiming to judge the tree.
    """
    old_rows, _ = load_register_at(DIVERGENT_TREE)
    desk_rows, _ = load_register(REGISTER_DOC)
    assert len(old_rows) != len(desk_rows)


def test_the_report_names_which_tree_and_which_source():
    """Independence must be auditable, not promised (R15 TAUTOLOGY)."""
    _, report = run_at_tree("HEAD")
    assert "would create" in report["measured_tree"]
    assert report["measured_source"].startswith("tools.epistemic_wall.crossings_at_head")
    assert report["ruled_source"].endswith("HEAD")
    assert "WALL_CROSSING_DISPOSITION_REGISTER.md" in report["ruled_source"]


def test_a_record_first_commit_is_refused_by_its_own_tree(tmp_path):
    """THE CLASS, END TO END, on a REAL tree object — the record without the code.

    A temporary index is built from HEAD, one live `owed` edge is flipped to
    `cut` in the register blob, and `git write-tree` turns that into a real tree:
    exactly the tree a commit would create if someone wrote down a cut and did
    not land it. The check must red on THAT tree, naming the row.

    This is the mutation the whole finding is about, and it is deliberately not a
    fixture the test wrote for itself: the code side is this repo's real code at
    HEAD, and the only thing that changed is the claim.
    """
    import os as _os
    idx = tmp_path / "record-first-index"
    env = {**dict(_os.environ), "GIT_INDEX_FILE": str(idx)}
    subprocess.run(["git", "read-tree", "HEAD"], cwd=str(ROOT), check=True, env=env)

    text = subprocess.run(["git", "show", "HEAD:docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md"],
                          cwd=str(ROOT), capture_output=True, text=True, check=True).stdout
    live_owed = [ln for ln in text.splitlines() if ln.startswith("edge: ") and "disposition=owed" in ln]
    assert live_owed, "no `owed` row to flip — this test needs a live crossing to lie about"
    victim = live_owed[0]
    lie = victim.replace("disposition=owed", "disposition=cut").split(" | design=")[0] + (
        " | reason=cut in this very commit, allegedly, which is the claim under test")
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=str(ROOT), check=True,
                          input=text.replace(victim, lie), capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "update-index", "--cacheinfo",
                    f"100644,{blob},docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md"],
                   cwd=str(ROOT), check=True, env=env)
    tree = subprocess.run(["git", "write-tree"], cwd=str(ROOT), capture_output=True,
                          text=True, check=True, env=env).stdout.strip()

    findings, _ = run_at_tree(tree)
    assert any("ruled `cut` but the import IS STILL IN" in f for f in findings), findings
    assert run_at_tree("HEAD") == ([], run_at_tree("HEAD")[1]), "and HEAD itself still reconciles"


# ── 2. THE TOOL: fail-closed on every unreadable tree ────────────────────────

def test_load_register_at_fails_closed_on_a_bogus_rev():
    with pytest.raises(RegisterError):
        load_register_at("not-a-real-rev-at-all")


def test_load_register_at_fails_closed_when_the_tree_predates_the_register():
    """"Could not read it" must never arrive as "nothing to check"."""
    with pytest.raises(RegisterError):
        load_register_at(f"{REGISTER_ADDED}^")


def test_the_two_modes_are_mutually_exclusive():
    """One instrument per run — a mixed invocation is a silent third semantics."""
    with pytest.raises(SystemExit):
        from tools.wall_crossing_dispositions import main
        main(["--at-head", "--at-tree", "HEAD"])


# ── 3. THE CALLER: scope ─────────────────────────────────────────────────────

def test_a_pure_docs_commit_is_out_of_scope_and_never_even_imports(monkeypatch):
    """A docs/data commit must not be refusable by this step.

    MUTATION: `_index_tree` is made to explode. If the scope test were wrong the
    commit would be refused for a reason that has nothing to do with it.
    """
    monkeypatch.setattr(gate, "_index_tree", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    ok, detail = gate._wall_crossing_landed_check(["docs/status/LATEST.md", "README.md"])
    assert ok and detail == ""


def test_any_staged_py_is_in_scope(monkeypatch):
    """Not just wall-side dirs: `tools/` and `background/` are BRIDGE packages the
    walker routes indirect crossings through, so a tools-only edit can create one."""
    called = {}
    monkeypatch.setattr(gate, "_index_tree", lambda: "a" * 40)

    def fake(tree):
        called["tree"] = tree
        return [], {"measured_crossings": 22, "rows": 91}
    monkeypatch.setitem(sys.modules, "tools.wall_crossing_dispositions",
                        _stub_module(fake))
    ok, detail = gate._wall_crossing_landed_check(["tools/whatever.py"])
    assert ok and called["tree"] == "a" * 40
    assert "22 live" in detail


def test_the_register_alone_is_in_scope(monkeypatch):
    """The record-without-the-code commit is the entire class. It carries no .py."""
    monkeypatch.setattr(gate, "_index_tree", lambda: "b" * 40)
    monkeypatch.setitem(sys.modules, "tools.wall_crossing_dispositions",
                        _stub_module(lambda tree: ([], {"measured_crossings": 1, "rows": 1})))
    ok, _ = gate._wall_crossing_landed_check([gate.WALL_REGISTER_PATH])
    assert ok


# ── 4. THE CALLER: fail-closed, one mutation per path ────────────────────────

def _stub_module(run_at_tree_impl):
    import types
    m = types.ModuleType("tools.wall_crossing_dispositions")
    m.run_at_tree = run_at_tree_impl
    return m


def test_findings_refuse_the_commit(monkeypatch):
    monkeypatch.setattr(gate, "_index_tree", lambda: "c" * 40)
    monkeypatch.setitem(sys.modules, "tools.wall_crossing_dispositions",
                        _stub_module(lambda tree: (["x -> y: ruled `cut` but the import IS STILL IN"], {})))
    ok, detail = gate._wall_crossing_landed_check(["company/billing/x.py"])
    assert not ok and "still in" in detail.lower()


def test_an_unimportable_checker_refuses(monkeypatch):
    """R15 FAIL-SILENT: a check that is unavailable is a check that FAILED."""
    monkeypatch.setitem(sys.modules, "tools.wall_crossing_dispositions", None)
    ok, detail = gate._wall_crossing_landed_check(["company/billing/x.py"])
    assert not ok and "UNAVAILABLE" in detail


def test_a_raising_checker_refuses(monkeypatch):
    monkeypatch.setattr(gate, "_index_tree", lambda: "d" * 40)

    def boom(tree):
        raise ValueError("the walker died")
    monkeypatch.setitem(sys.modules, "tools.wall_crossing_dispositions", _stub_module(boom))
    ok, detail = gate._wall_crossing_landed_check(["simulation/x.py"])
    assert not ok and "RAISED" in detail and "the walker died" in detail


def test_an_unusable_index_refuses(monkeypatch):
    monkeypatch.setitem(sys.modules, "tools.wall_crossing_dispositions",
                        _stub_module(lambda tree: ([], {"measured_crossings": 1, "rows": 1})))
    monkeypatch.setattr(gate, "_index_tree",
                        lambda: (_ for _ in ()).throw(RuntimeError("unmerged entries")))
    ok, detail = gate._wall_crossing_landed_check(["saas/x.py"])
    assert not ok and "would create" in detail


def test_main_returns_1_and_says_why(monkeypatch, capsys):
    monkeypatch.setattr(gate, "staged_files", lambda: ["company/billing/x.py"])
    monkeypatch.setattr(gate, "_wall_crossing_landed_check", lambda staged: (False, "  - a finding"))
    assert gate.main() == 1
    err = capsys.readouterr().err
    assert "WALL-CROSSING REGISTER DISAGREES" in err
    assert "--at-tree $(git write-tree)" in err, "a refusal must be reproducible by hand"


# ── 5. THE SUBTLE ONE: which index the tree comes from ───────────────────────

def test_index_tree_honours_GIT_INDEX_FILE(tmp_path, monkeypatch):
    """`git commit -- <pathspec>` hands the hook a TEMPORARY index in GIT_INDEX_FILE.

    Every other subprocess in the gate scrubs `GIT_*` deliberately. This one must
    NOT: scrubbing here would serialise the REAL index — the whole shared tree's
    staged state — instead of the pathspec the committer actually chose, and the
    gate would judge a tree nobody is about to create.

    MUTATION: this test fails if `_index_tree` is given a scrubbed environment,
    because the temporary index below is read from an OLD commit and its tree sha
    cannot equal the current index's.
    """
    idx = tmp_path / "tmp-index"
    old_tree = subprocess.run(["git", "rev-parse", f"{REGISTER_ADDED}^{{tree}}"],
                              cwd=str(ROOT), capture_output=True, text=True, check=True
                              ).stdout.strip()
    subprocess.run(["git", "read-tree", old_tree], cwd=str(ROOT), check=True,
                   env={**dict(__import__("os").environ), "GIT_INDEX_FILE": str(idx)})
    monkeypatch.setenv("GIT_INDEX_FILE", str(idx))
    assert gate._index_tree() == old_tree

    monkeypatch.delenv("GIT_INDEX_FILE")
    assert gate._index_tree() != old_tree, "the real index must not equal a 2026-08-09 tree"


def test_index_tree_survives_a_held_index_lock(tmp_path):
    """THE DEFECT THIS GATE FOUND IN ITSELF, and the reason `_index_tree` copies.

    `git write-tree` takes `index.lock` to write back the cache-tree extension,
    and during a plain `git commit` GIT ALREADY HOLDS THAT LOCK while the hook
    runs. Called on the live index it dies `rc=128 ... index.lock: File exists`,
    and a fail-closed step that dies would REFUSE EVERY COMMIT of that shape —
    the same environmental-refusal defect `surgical_land` caught when the
    finding-class checker was wired hours earlier. It was found here the same
    way: the gate refused its own commit.

    A throwaway repo, not this one: locking the shared tree's real index to
    prove a point is the kind of test that becomes an incident.

    MUTATION: point `_index_tree` at the live index instead of a copy and this
    goes red with exactly the rc=128 above.
    """
    import os as _os
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "a.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "a.py"], cwd=repo, check=True,
                   env={k: v for k, v in _os.environ.items() if not k.startswith("GIT_")})
    (repo / ".git" / "index.lock").write_text("")          # git commit, mid-flight

    tree = gate._index_tree(repo)
    assert len(tree) == 40 and int(tree, 16) >= 0
    assert (repo / ".git" / "index.lock").exists(), "and the real lock was left untouched"


def test_the_checker_imports_from_a_foreign_cwd():
    """Run as a script by the hook, `sys.path[0]` is `tools/`, not the repo root.

    That exact defect refused every staging commit when the finding-class checker
    was wired two hours earlier (`f4b504e6c`), and `surgical_land` caught it by
    running the gate in a scratch checkout. Reproduced here for real: import the
    gate the way a script import sees it, from a cwd that is not the repo.
    """
    code = (
        "import sys; sys.path.insert(0, %r); "
        "import pre_commit_test_gate as g; "
        "ok, detail = g._wall_crossing_landed_check(['tools/x.py']); "
        "print('OK' if ok else 'REFUSED:' + detail)" % str(ROOT / "tools")
    )
    out = subprocess.run([sys.executable, "-c", code], cwd="/tmp",
                         capture_output=True, text=True)
    assert "UNAVAILABLE" not in out.stdout, out.stdout
    assert out.stdout.strip().endswith(("OK", "OK\n")) or "OK" in out.stdout, out.stdout + out.stderr
