"""The publish gate's HEAD checkout must be a real git repo (R10 class closure, 2026-08-09).

WHY THIS MODULE EXISTS. `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` moved the gate's
subject from the shared working tree to a clean checkout of HEAD. The minimal implementation
materialised it with `git archive HEAD | tar -x`, which produces the right FILES and no history
at all -- so every test that asks git a question died in it with `fatal: not a git repository`,
which is not an answer about whether HEAD is publishable.

Two instances appeared the same evening and the first was patched at the instance (576105747,
the ghost-pusher tripwire taught not to shell out). The second --
`test_blocked_atom_visibility.py::test_the_real_staleness_clocks_...`, which reads AO11's own
`git blame` of the map -- wedged the publish gate at HEAD. R10 forbids closing an
absurdity-class defect one instance at a time, and the population is open-ended: any test that
reads history, blame or a SHA is a future instance. The subject is fixed instead, and this
module is that fix's control.

R15, both directions:
  * the defect is REACHABLE -- an extraction without the repo step cannot answer `rev-parse`
    (`test_an_archive_only_extraction_cannot_answer_git_at_all`), so the property below is not
    vacuously true of any directory;
  * the control FAILS CLOSED -- a checkout whose repo cannot be made yields None and the gate
    does not run (`test_the_checkout_is_unavailable_when_the_repo_cannot_be_made`).
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from background import process_run_complete as prc  # noqa: E402


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=120)


@pytest.fixture(scope="module")
def head_checkout():
    """One materialisation for the whole module -- it is ~130MB and ~0.5s, so paying for it
    per-test would be a real cost for no extra evidence."""
    with prc._head_checkout() as path:
        assert path is not None, "the gate could not materialise HEAD at all"
        yield path


def test_the_checkout_can_answer_which_commit_it_is(head_checkout):
    """The property the archive-only form did not have: the checkout knows its own SHA, and it
    is the SHA the gate believes it tested."""
    inside = _git(["rev-parse", "HEAD"], head_checkout)
    assert inside.returncode == 0, inside.stderr
    outside = _git(["rev-parse", "HEAD"], REPO)
    assert inside.stdout.strip() == outside.stdout.strip()


def test_the_checkout_can_be_blamed(head_checkout):
    """The exact question that wedged publishing: AO11's staleness clocks blame the map."""
    blame = _git(["blame", "--line-porcelain", "--", "docs/design/maturity_map.yaml"],
                 head_checkout)
    assert blame.returncode == 0, blame.stderr
    assert "author " in blame.stdout


def test_the_checkout_reads_as_tracked_and_clean(head_checkout):
    """`git read-tree` fills the index, so a test asking 'is this tree clean?' gets the true
    answer for HEAD -- yes -- rather than 8,444 files reading as untracked. Untracked entries
    (`??`) are allowed: the DATA overlay is deliberately not in HEAD."""
    status = _git(["status", "--porcelain"], head_checkout)
    assert status.returncode == 0, status.stderr
    dirty = [ln for ln in status.stdout.splitlines() if ln[:2].strip() and not ln.startswith("??")]
    assert not dirty, "the HEAD checkout is not clean against HEAD: {}".format(dirty[:10])


def test_nothing_is_registered_in_the_real_repo(head_checkout):
    """Why this is not `git worktree add`: no state may survive this process being SIGKILLed.
    The real repo must not know the checkout exists."""
    listing = _git(["worktree", "list"], REPO)
    assert listing.returncode == 0, listing.stderr
    assert str(head_checkout) not in listing.stdout


def test_the_checkout_is_removed_afterwards():
    with prc._head_checkout() as path:
        assert path is not None
        assert path.exists()
    assert not path.exists(), "the gate leaked a HEAD checkout directory"


# ── R15 direction 1: the defect is reachable ─────────────────────────────────

def test_an_archive_only_extraction_cannot_answer_git_at_all(tmp_path):
    """The pre-fix subject, reconstructed: files without history. If this ever passes,
    every assertion above has become vacuous."""
    archive = subprocess.run(["git", "archive", "HEAD", "docs/design/maturity_map.yaml"],
                             cwd=str(REPO), capture_output=True, timeout=120)
    assert archive.returncode == 0
    subprocess.run(["tar", "-x", "-C", str(tmp_path)], input=archive.stdout,
                   capture_output=True, timeout=120, check=True)
    assert (tmp_path / "docs" / "design" / "maturity_map.yaml").exists()
    assert not (tmp_path / ".git").exists()
    naked = _git(["rev-parse", "HEAD"], tmp_path)
    assert naked.returncode != 0
    assert "not a git repository" in naked.stderr


# ── R15 direction 2: the control fails CLOSED ────────────────────────────────

def test_the_checkout_is_unavailable_when_the_repo_cannot_be_made(monkeypatch):
    """An unavailable check is a FAILED check: if committed truth cannot be made answerable,
    the gate must not run on it."""
    monkeypatch.setattr(prc, "_make_checkout_a_repo", lambda checkout, head_sha: False)
    with prc._head_checkout() as path:
        assert path is None


def test_the_repo_step_reports_failure_rather_than_raising(tmp_path, monkeypatch):
    """`_make_checkout_a_repo` converts a broken git into a False, never an exception into the
    publish path -- the caller's fail-closed branch is what decides, not a traceback."""
    def _boom(*a, **kw):
        raise OSError("git is not installed")

    monkeypatch.setattr(prc.subprocess, "run", _boom)
    assert prc._make_checkout_a_repo(tmp_path, "deadbeef") is False


def test_a_failed_init_is_reported_as_failure(tmp_path, monkeypatch):
    class _Result:
        returncode = 128
        stdout = ""
        stderr = "fatal: cannot mkdir"

    monkeypatch.setattr(prc.subprocess, "run", lambda *a, **kw: _Result())
    assert prc._make_checkout_a_repo(tmp_path, "deadbeef") is False
