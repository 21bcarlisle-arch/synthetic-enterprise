"""R15 for the publish commit's SCOPE (BLOCKING, 2026-08-18).

THE DEFECT. `background/process_run_complete.py::git_commit_push` did two independent things
that made its commit carry work it knew nothing about:

  * it staged `docs/staging/done` as a DIRECTORY, so `git add` swept every file underneath --
    including a finding document another lane had moved there seconds earlier;
  * it ran `git commit -m msg` with NO pathspec, which commits the whole INDEX, so anything
    another writer had already staged went out under the publish's own message.

Commit `96c665098` did exactly that to two BLOCKING findings from two other lanes and carried
NEITHER of their repairs. Archiving to `done/` is the step that ENDS a document's drawability
(the staging scanners read the root, not `done/`), so the sweep performed the one irreversible
bookkeeping move in this system on documents it did not author.

The `tree_lock()` around the add/commit pair carried a comment claiming it prevented this. It
could not: the lock closes the window between THIS writer's add and commit, and the paths at
risk were staged before the lock was ever taken. That is why these are tests and not a comment.

WHAT EACH TEST KILLS (R15 -- a control that cannot fail is worse than none):

  * `..._does_not_stage_the_archive_directory`   -- restore `files.append(str(DONE_DIR))`
  * `..._own_marker_is_still_committed`          -- THE DIFFERENTIAL: delete the marker record
                                                    and the capability the directory add existed
                                                    for is gone, so this fails too
  * `..._names_its_paths_rather_than_the_index`  -- drop the `"--"` + pathspec
  * `..._drops_a_path_git_cannot_match`          -- include unmatched paths; git rejects the
                                                    WHOLE commit and the publish stops
  * `..._an_empty_pathspec_is_a_refusal`         -- return `[]` and let the caller run
                                                    `git commit -m msg --`, i.e. the bare index
                                                    commit again, reached by degradation
  * `..._a_refusal_does_not_fingerprint`         -- classify the refusal as NOTHING_TO_COMMIT
                                                    and the run is recorded as done forever
"""
from __future__ import annotations

import contextlib
import subprocess

import pytest

from background import process_run_complete as prc


class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture
def publish(tmp_path, monkeypatch):
    """Drive `git_commit_push` against a scratch tree, capturing the git argv it builds.

    Returns a callable; calling it runs the publish and yields the recorded calls. Everything
    the publish surface needs exists on disk so the pathspec filter keeps it.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "docs" / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "docs" / "staging" / "done")
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "docs" / "status" / "LATEST.md")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    # THE LIVE RECORD IS NOT A TEST FIXTURE (2026-08-30). `PUBLISH_CAUSE_FILE` is computed
    # at module import from the real PROJECT_DIR, so patching PROJECT_DIR afterwards does
    # not move it -- the same trap `LAST_PUSH_FILE` above is patched to avoid. Without this
    # line these tests drive the publisher into `publish_cause.record_cause` against the
    # repository's own `.last_publish_cause.json`, and `live_ledger_guard` refuses (it had
    # already let a fixture's git_hash "abc1234" reach that record before the guard landed).
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / ".last_publish_cause.json")
    monkeypatch.setattr(prc, "tree_lock", lambda: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_MARKERS_ARCHIVED_BY_THIS_RUN", [])

    for rel in ("docs/reports/ANNUAL_REPORT.md", "docs/status/LATEST.md",
                "site/data/dashboard.json"):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    (tmp_path / "docs" / "staging" / "done").mkdir(parents=True, exist_ok=True)

    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        # `rev-parse HEAD:<rel>` is the pathspec filter asking whether git has heard of a path
        # that is not on disk. In a tree with no history the honest answer is no.
        if cmd[:2] == ["git", "rev-parse"]:
            return _FakeCompleted(1)
        return _FakeCompleted(0)

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    def _run():
        prc.git_commit_push("abc1234", 1000.0)
        return calls

    return _run


def _staged(calls):
    return [arg for c in calls if c[:2] == ["git", "add"] for arg in c[2:]]


def _commit_argv(calls):
    for c in calls:
        if c[:2] == ["git", "commit"]:
            return c
    return None


# --- half one: the directory add ---------------------------------------------------------

def test_the_publish_does_not_stage_the_whole_archive_directory(publish, tmp_path):
    """MUTATION: restore `files.append(str(DONE_DIR))` in git_commit_push -> fails."""
    done = tmp_path / "docs" / "staging" / "done"
    foreign = done / "WORKER_FINDING_ANOTHER_LANES_BLOCKING_FINDING_2026-08-18.md"
    foreign.write_text("# a finding this process did not author\n")

    calls = publish()

    assert str(done) not in _staged(calls), (
        "the publish staged docs/staging/done as a DIRECTORY -- `git add` on a directory takes "
        "every file under it, which is how two other lanes' BLOCKING findings were archived by "
        "a commit that carried neither repair")
    assert str(foreign) not in _staged(calls)
    assert str(foreign) not in (_commit_argv(calls) or []), (
        "a document this process did not move into done/ reached the publish commit")


def test_the_runs_own_marker_is_still_committed(publish, tmp_path):
    """THE DIFFERENTIAL. Scoping the archive add must not throw away what it was FOR.

    The directory add existed because a `run_complete_*.md` moved to done/ and never committed
    sits untracked forever (observed 7+ times). So the run's OWN marker must still land.

    MUTATION: stop recording in `_record_archived_marker` (or drop the loop that reads
    `_MARKERS_ARCHIVED_BY_THIS_RUN`) -> fails, and the fix would be a silent regression to the
    orphaned-marker bug rather than a fix at all.
    """
    staging = tmp_path / "docs" / "staging"
    marker = staging / "run_complete_20260818_120000.md"
    marker.write_text("# Run Complete\n")

    assert prc._archive_marker(marker) is True
    archived = staging / "done" / marker.name
    assert archived.exists()

    calls = publish()

    assert str(archived) in _staged(calls), "this run's own marker was not staged"
    assert str(archived) in (_commit_argv(calls) or []), (
        "this run's own marker was staged but left out of the commit pathspec -- it would sit "
        "in done/, untracked, forever")


# --- half two: the pathspec ---------------------------------------------------------------

def test_the_publish_commit_names_its_paths_rather_than_committing_the_index(publish):
    """MUTATION: revert to `["git", "commit", "-m", msg]` -> fails.

    `git commit -m msg` commits the INDEX. Another writer's `git add` -- run BEFORE this process
    took the tree lock, which is why the lock was never the protection its comment claimed --
    goes out under the publish's message.
    """
    argv = _commit_argv(publish())
    assert argv is not None, "no commit was attempted"
    assert "--" in argv, (
        "the publish ran a bare `git commit`, which commits the whole index and therefore any "
        "other lane's staged work")
    assert argv[argv.index("--") + 1:], "the pathspec after `--` is empty"


def test_the_maturity_fold_is_named_in_the_pathspec(publish, tmp_path):
    """The `-A` add of maturity_map.yaml + atom_status only lands if those paths are NAMED.

    MUTATION: drop the `extra_relative` argument at the call site -> the fold is staged and
    never committed, i.e. a reconciled map dangles uncommitted, which is the wedge the `-A` add
    was built to prevent.
    """
    (tmp_path / "docs" / "design").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "design" / "maturity_map.yaml").write_text("atoms: []\n")

    argv = _commit_argv(publish())
    assert str(tmp_path / "docs" / "design" / "maturity_map.yaml") in argv


def test_the_pathspec_drops_a_path_git_cannot_match(tmp_path, monkeypatch):
    """FAIL-CLOSED THE OTHER WAY. An unmatched pathspec makes git reject the WHOLE commit
    ("did not match any file(s) known to git"), so one absent optional artefact would take the
    entire publish down -- trading a scoping defect for an availability one.

    MUTATION: return the candidates unfiltered -> fails.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(
        prc.subprocess, "run",
        lambda cmd, **kw: _FakeCompleted(1))  # git has never heard of anything here

    real = tmp_path / "on_disk.json"
    real.write_text("{}")
    ghost = tmp_path / "never_existed.json"

    spec = prc._commit_pathspec([str(real), str(ghost)])

    assert str(real) in spec
    assert str(ghost) not in spec, (
        "a path that is neither on disk nor known to git stayed in the pathspec; git rejects "
        "the whole commit on it and the publish stops")


def test_a_staged_deletion_survives_the_pathspec_filter(tmp_path, monkeypatch):
    """The filter must not be "exists on disk". A path staged as a DELETION is gone from the
    worktree and MUST stay in the pathspec, or the deletion sits staged forever and the next
    writer commits it -- reintroducing the swept-index defect one file at a time.

    MUTATION: drop the `_git_knows_path` half of the disjunction -> fails.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)

    deleted = tmp_path / "docs" / "design" / "atom_status"

    def fake_run(cmd, **kw):
        if cmd[:2] == ["git", "rev-parse"] and cmd[-1].endswith("docs/design/atom_status"):
            return _FakeCompleted(0)  # HEAD carries this tree
        return _FakeCompleted(1)

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    assert not deleted.exists()
    assert str(deleted) in prc._commit_pathspec([str(deleted)])


def test_an_empty_pathspec_is_a_refusal_not_a_bare_commit(publish, tmp_path, monkeypatch):
    """`git commit -m msg --` with no paths is a bare INDEX commit -- the original defect,
    reached by degradation instead of by design. The publish must refuse.

    MUTATION: delete the `if not pathspec:` guard -> a commit is attempted with an empty
    pathspec and this fails.
    """
    monkeypatch.setattr(prc, "_commit_pathspec", lambda *a, **kw: [])

    calls = publish()

    assert _commit_argv(calls) is None, (
        "the publish committed with an empty pathspec, which is a bare index commit")


def test_a_pathspec_refusal_does_not_record_the_run_as_done(publish, monkeypatch):
    """The refusal must leave the run RETRYABLE. `NOTHING_TO_COMMIT` is in
    RETRYABLE_PUBLISH_OUTCOMES, which fingerprints the cycle as a genuine no-op -- so
    classifying a broken state as one would mean the run is never published again, only a change
    in the sim's own figures breaking the loop.

    MUTATION: classify the empty-pathspec refusal as NOTHING_TO_COMMIT -> fails.
    """
    monkeypatch.setattr(prc, "_commit_pathspec", lambda *a, **kw: [])
    outcome: dict = {}
    monkeypatch.setattr(prc, "git_commit_push", prc.git_commit_push)  # explicit: real function
    prc.git_commit_push("abc1234", 1000.0, outcome)

    assert outcome.get("reason") not in prc.RETRYABLE_PUBLISH_OUTCOMES, (
        "an empty-pathspec refusal was recorded as a retryable no-op, so the fingerprint marks "
        "this run processed and it is never published again")


def test_the_lock_comment_no_longer_claims_a_protection_the_code_lacks():
    """R15 wrong-subject, and the reason nobody looked for three weeks: the `tree_lock()`
    comment said the lock stopped another writer's staged work being swept in. It cannot -- the
    paths at risk are staged BEFORE the lock is acquired. The pathspec is what stops it, and the
    comment must say so or the next reader trusts the lock again.
    """
    import inspect
    src = inspect.getsource(prc.git_commit_push)
    assert "_commit_pathspec(" in src, "the publish no longer scopes its commit by pathspec"
    assert 'files.append(str(DONE_DIR))' not in src, (
        "the archive DIRECTORY add is back in the publish path")
