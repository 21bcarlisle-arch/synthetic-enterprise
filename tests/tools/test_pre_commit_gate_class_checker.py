"""R15 proofs for the finding-class checker's pre-commit caller.

Closes `WORKER_FINDING_THE_CLASS_CHECKER_HAS_NO_AUTOMATED_CALLER_2026-08-12`, which
recorded that `background/finding_classes.py::check()` had NO automated caller and
named three things a repair had to decide. This file is where those three are proven
rather than asserted:

  1. WHERE -- the pre-commit gate, scoped to commits touching `docs/staging/**`, and
     running BEFORE the pure-docs early return (the finding's own preference: it
     "fires on the write that would cause the rot"). Proven by
     `test_staging_only_commit_still_runs_the_checker`, which is the case the
     obvious wiring would have missed.
  2. WHAT A FAILURE DOES -- refuses the commit, rc 1, with the failures on stderr.
     Proven both ways: it returns 0 when the tree is clean and 1 when it is not.
  3. FAIL-CLOSED ON ITS OWN UNAVAILABILITY -- R15's third killer pattern. A checker
     skipped because its module did not import is a checker that passed. Proven by
     injecting an unimportable module and an exploding `check()`.

A control that cannot fail is worse than none, so every proof here injects a defect
and asserts the gate goes red on it -- none of them merely assert today's green tree.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402

# ── 1. WHERE: the staging scope, and the early-return trap ───────────────────

def test_staging_only_commit_still_runs_the_checker(monkeypatch, capsys):
    """THE REGRESSION THIS FILE EXISTS FOR.

    A commit touching only `docs/staging/**` selects NO test targets, so it hits
    `main()`'s `return 0` for pure-docs commits. If the checker were wired after
    that return it would never run on precisely the commits that break
    consolidation. Assert it runs, on a commit with no test targets at all.
    """
    monkeypatch.setattr(gate, "staged_files", lambda: ["docs/staging/WORKER_FINDING_X.md"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    called = []
    monkeypatch.setattr(gate, "_class_consolidation_check",
                        lambda: (called.append(1), (True, "ok"))[1])
    assert gate.main() == 0
    assert called, "staging-only commit did not run the class checker (early-return trap)"
    assert "finding-class consolidation holds" in capsys.readouterr().out


def test_non_staging_commit_does_not_run_the_checker(monkeypatch):
    """MUTATION (the other direction): the scope is real, not 'always on'.

    A commit that touches no staging file must not pay for the filesystem walk.
    Without this, 'scoped to docs/staging' would be an unproven claim.
    """
    monkeypatch.setattr(gate, "staged_files", lambda: ["saas/customers.py"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    called = []
    monkeypatch.setattr(gate, "_class_consolidation_check",
                        lambda: (called.append(1), (True, "ok"))[1])
    assert gate.main() == 0
    assert not called, "checker ran on a commit touching no staging file"


# ── 2. WHAT A FAILURE DOES: refuse the commit ────────────────────────────────

def test_broken_consolidation_refuses_the_commit(monkeypatch, capsys):
    """R15 both-ways: a real `check()` failure must REFUSE, not warn."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["docs/staging/WORKER_FINDING_X.md"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    monkeypatch.setattr(gate, "_class_consolidation_check",
                        lambda: (False, "  - class no_caller_and_never_runs prints 2, lists 3"))
    assert gate.main() == 1, "broken consolidation did not refuse the commit"
    err = capsys.readouterr().err
    assert "COMMIT REFUSED" in err
    assert "prints 2, lists 3" in err, "the reason was swallowed -- an unactionable refusal"


# ── 3. FAIL-CLOSED: R15's third killer pattern ───────────────────────────────

def test_unimportable_checker_fails_closed(monkeypatch):
    """An unavailable check is a FAILED check. Inject an import that explodes."""
    import builtins
    real_import = builtins.__import__

    def _boom(name, *a, **kw):
        if name == "background.finding_classes":
            raise ImportError("simulated: module gone")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", _boom)
    ok, detail = gate._class_consolidation_check()
    assert ok is False, "an unimportable checker reported SUCCESS (fail-silent)"
    assert "UNAVAILABLE" in detail and "simulated: module gone" in detail


def test_exploding_check_fails_closed(monkeypatch):
    """`check()` itself raising must refuse, not fall through to success."""
    import background.finding_classes as fc

    def _boom(*a, **kw):
        raise RuntimeError("simulated: staging root vanished mid-walk")

    monkeypatch.setattr(fc, "check", _boom)
    ok, detail = gate._class_consolidation_check()
    assert ok is False, "an exploding check() reported SUCCESS (fail-silent)"
    assert "RAISED" in detail and "staging root vanished" in detail


@pytest.mark.parametrize("failures", [[], ["one failure"], ["a", "b", "c"]])
def test_verdict_tracks_the_result_not_the_call(monkeypatch, failures):
    """TAUTOLOGY guard (R15's first pattern): the verdict must come from
    `check()`'s RESULT, not from the fact that it was reached without error."""
    import background.finding_classes as fc

    class _Result:
        def __init__(self, f):
            self.failures = f

        @property
        def ok(self):
            return not self.failures

    monkeypatch.setattr(fc, "check", lambda *a, **kw: _Result(failures))
    ok, _ = gate._class_consolidation_check()
    assert ok is (not failures)


# ── The live tree: this must hold at HEAD, or the gate wedges every commit ───

def test_the_real_tree_passes_the_checker():
    """Wiring a caller to a checker the tree already fails would wedge publishing.

    This is the one test here that asserts today's green -- deliberately, because
    the cost of being wrong about it is every staging commit refused.
    """
    ok, detail = gate._class_consolidation_check()
    assert ok, f"live tree fails the class checker; wiring the gate would wedge commits:\n{detail}"


def test_checker_imports_from_a_foreign_cwd(tmp_path):
    """THE REGRESSION `surgical_land` CAUGHT WHILE LANDING THIS FILE.

    The gate's own legal committer runs it against a scratch CHECKOUT of the tree
    the commit would create -- different cwd, `background` not on the default path.
    The first draft imported without putting ROOT on `sys.path`, so the fail-closed
    branch fired on ModuleNotFoundError and REFUSED every staging commit while
    blaming the class checker. Fail-closed is correct; firing environmentally is not.

    Run the check in a subprocess from an unrelated cwd with a scrubbed PYTHONPATH --
    the conditions the scratch checkout actually creates. In-process assertions cannot
    see this: pytest has already put ROOT on the path.
    """
    # Load the module the way `sh tools/git-hooks/pre-commit` does -- as a SCRIPT, so
    # sys.path[0] is `<root>/tools`, NOT the repo root. Handing the subprocess ROOT
    # ourselves is a tautology: it makes `background` importable regardless of the
    # fix, and an earlier draft of this test passed against the unfixed source.
    snippet = (
        "import sys, importlib.util\n"
        # Keep the stdlib; drop only the repo root and cwd, then prepend `tools/` --
        # exactly the sys.path that `python3 tools/pre_commit_test_gate.py` produces.
        "sys.path[:] = [p for p in sys.path if p not in ('', r'%s')]\n"
        "sys.path.insert(0, r'%s')\n"
        "spec = importlib.util.spec_from_file_location('g', r'%s')\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "ok, detail = m._class_consolidation_check()\n"
        "print('OK' if ok else 'FAIL:' + detail)\n"
    ) % (ROOT, ROOT / "tools", ROOT / "tools" / "pre_commit_test_gate.py")
    r = subprocess.run(
        [sys.executable, "-c", snippet],
        cwd=str(tmp_path),
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        capture_output=True, text=True, timeout=300,
    )
    assert "UNAVAILABLE" not in r.stdout, (
        "the checker reported itself UNAVAILABLE from a foreign cwd -- this refuses "
        f"every staging commit:\n{r.stdout}\n{r.stderr}"
    )
    assert r.stdout.startswith("OK"), f"checker failed from a foreign cwd:\n{r.stdout}\n{r.stderr}"


def test_checker_is_reachable_as_a_module_too():
    """The documented `python3 -m background.finding_classes --check` must keep
    working -- the class documents tell every reader to run it."""
    r = subprocess.run(
        [sys.executable, "-m", "background.finding_classes", "--check"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"documented CLI failed:\n{r.stdout}\n{r.stderr}"
    assert "check: PASS" in r.stdout
