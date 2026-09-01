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


@pytest.fixture(scope="module", autouse=True)
def _the_publisher_log_goes_to_tmp(tmp_path_factory):
    """THIS FILE DRIVES THE REAL PUBLISHER, so its diagnostics must not reach the real record.

    `prc.log()` appends to `docs/observability/sim-runner-log.md` -- the file the PUBLISHING
    DOWN alarm sends a human to. Every test here calls a publisher entry point that logs, so
    without this the fixture rows land beside the genuine sim-runner rows and read as real gate
    verdicts (observed 2026-08-21 20:49-20:51 UTC, six fabricated "could NOT materialise a clean
    HEAD checkout" lines during a 26-hour publishing outage).

    MODULE-scoped because `head_checkout` is: a function-scoped fixture cannot isolate a write
    that happens during module-scoped setup, which is why four tests here ERRORED rather than
    failed."""
    dest = tmp_path_factory.mktemp("publisher-log") / "sim-runner-log.md"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(prc, "LOG_FILE", dest)
        yield dest


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


def test_the_checkout_is_either_reused_or_removed_never_leaked(monkeypatch):
    """Was `test_the_checkout_is_removed_afterwards`. Since OPS2 the gate REUSES one checkout
    between cycles so `__pycache__` survives, and removal is no longer the property that keeps
    /tmp from filling -- BOUNDEDNESS is. Two shapes are legitimate and nothing else is: the one
    reused directory, which persists by design, or a throwaway, which must not outlive its cycle.

    Which one this process gets depends on whether a live publisher holds the reuse lock, so this
    asserts the disjunction rather than picking a branch. The branch-specific behaviour --
    bytecode survives a refresh; a throwaway is removed even when the run raises; abandoned
    checkouts are swept -- is pinned deterministically in test_publish_gate_subject_is_head.py.

    WHY THE TREE COPY IS STUBBED (2026-08-10, episode-4 wedge cause -- the tenth failure at
    HEAD 88181441a was this test, and it was a RESOURCE failure, not a false property).

    When this module runs INSIDE the publish gate, the gate itself holds the reuse lock, so
    `_head_checkout()` here can only take the THROWAWAY branch: a full 190MB extraction of HEAD
    on top of the 190MB the gate is already running from, on a `/tmp` that is tmpfs, i.e. RAM.
    Measured at the failure: 15.9GB total, 3.0GB available, swap 4074/4096MB used, two full
    suites live -- and `git read-tree` in that second materialisation exceeded its 120s timeout,
    so `_make_checkout_a_repo` returned False, `_head_checkout()` correctly yielded None (R15
    fail-closed), and `assert path is not None` failed. Nothing about HEAD was unpublishable.

    The property under test is the CONTEXTMANAGER's lifecycle -- sweep, disk pre-flight, SHA,
    lock, mkdtemp, `finally: rmtree`, and the reused-vs-throwaway naming branch. None of that is
    a property of the extracted TREE, so the tree is stubbed to a bare directory and the whole
    branch/cleanup path stays real. The module fixture above still pays ONE real materialisation,
    which is what the tree-shaped assertions (rev-parse, blame, clean) actually need; this halves
    the gate's tmpfs high-water and removes the timeout-prone second read-tree entirely.

    R15: the mutation this still catches is deleting `shutil.rmtree(tmp)` from `_head_checkout`'s
    `finally` -- the throwaway then survives and the else-branch below fails. The stub is asserted
    to have been used, so a silent regression to the expensive form cannot pass unnoticed."""
    calls = []

    def _stub_materialise(dest, head_sha):
        """Everything `_head_checkout` needs downstream, minus the 190MB: a directory that
        exists. `_overlay_untracked_data` symlinks into it unchanged."""
        calls.append((Path(dest), head_sha))
        Path(dest).mkdir(parents=True, exist_ok=True)
        return True

    monkeypatch.setattr(prc, "_materialise_head_into", _stub_materialise)

    with prc._head_checkout() as path:
        assert path is not None
        assert path.exists()
    if path.name == prc.REUSED_HEAD_CHECKOUT_NAME:
        assert path.exists(), "the reused checkout must survive between cycles"
    else:
        assert not path.exists(), "the gate leaked a throwaway HEAD checkout directory"
        assert calls, ("the throwaway branch materialised a real 190MB tree instead of the stub "
                       "-- the second full extraction is back and so is the wedge")


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


# ── THE OBJECT STORE IS NOT ALWAYS `<project>/.git/objects` (2026-09-01) ─────────────────────────
# The alternates line is what lends the checkout the real repo's history. It was assembled from
# `PROJECT_DIR / ".git" / "objects"`, which is a DIRECTORY only in the main working tree: in a
# linked worktree `.git` is a FILE, so the path does not exist, `git read-tree` refuses with
# "unable to normalize alternate object path", and `_head_checkout` returns None.
#
# That made the publish gate unable to materialise HEAD from ANY worktree -- so every landing from
# an isolated writer (`tools/surgical_land` from `background/seat_executor`, promoted by
# `tools/promote_worktree_landing`) hit a gate that could not run. Found on 2026-09-01 by a merge
# commit refusing inside the worktree it was being reconciled in, four tests of THIS module being
# the thing that refused it.

def test_the_object_store_is_asked_of_git_not_assembled_from_the_project_path():
    """MUTATION (must fire): return `PROJECT_DIR / ".git" / "objects"` from `_object_store()`.

    Asserted as "git's answer" rather than "the string ends in .git/objects", because the whole
    defect is that the assembled string LOOKS right and names a path that is not there.
    """
    asked = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"], cwd=str(REPO),
        capture_output=True, text=True, timeout=30)
    assert asked.returncode == 0, "this test needs a git repo to be meaningful"
    common = Path(asked.stdout.strip())
    if not common.is_absolute():
        common = (REPO / common).resolve()

    assert prc._object_store() == common / "objects", (
        "the alternates path must be the COMMON object store git names, not one built by "
        "appending '.git/objects' to the working-tree root -- those differ in every worktree"
    )


def test_the_alternates_path_exists_as_a_directory():
    """The property the defect actually violated, stated without reference to how it is computed.

    `git read-tree` refuses an alternates line naming a path that is not a directory, and that
    refusal is silent in the gate's verdict: it becomes `checkout -> None`, which reads as
    "the gate could not run" and never as "the alternates line was wrong".
    """
    store = prc._object_store()
    assert store.is_dir(), f"the alternates line would name {store}, which is not a directory"


def test_a_worktrees_dot_git_is_a_file_which_is_why_the_assembled_path_was_wrong():
    """THE REACHABILITY LEG -- it proves the defect above is a real shape, not a story.

    Without this, the two tests above pass in the main tree forever and say nothing about the
    case that broke. Skips rather than passes where worktrees cannot be made, because a
    vacuous pass is exactly what this module exists to refuse.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        wt = Path(tmp) / "probe"
        made = subprocess.run(
            ["git", "worktree", "add", "--detach", str(wt), "HEAD"], cwd=str(REPO),
            capture_output=True, text=True, timeout=120)
        if made.returncode != 0:
            pytest.skip(f"could not make a probe worktree: {made.stderr.strip()[:200]}")
        try:
            assert (wt / ".git").is_file(), "a linked worktree's .git is a file, not a directory"
            assert not (wt / ".git" / "objects").exists(), (
                "the assembled path must NOT exist in a worktree -- that absence is the defect"
            )
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           cwd=str(REPO), capture_output=True, text=True, timeout=120)
