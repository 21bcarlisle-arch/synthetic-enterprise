"""`background/ops_repo.py` had THREE callers, ZERO test importers, and no refusal at the write.

THE DEFECT THIS NAMES (delivery seat, 2026-09-05, generalising `38871422b`). `ops_repo` is a
converged shared mechanism: `ntfy_mirror.py`, `director_input_log.py` and
`backup_company_data.py` all reach the private ops repo through `commit_and_push`. Nothing in
`tests/` imported `ops_repo` at all -- the callers' suites patch `commit_and_push` *by name* in
the caller's namespace, so the shared function's own body was executed by no test, ever, and its
contracts stood on nothing.

Two of the three callers hand-rolled the same refusal at their own call site
(`os.environ.get("PYTEST_CURRENT_TEST") is not None`). `backup_company_data.backup_once()` had
none: it reached `commit_and_push` with nothing between a test process and `git push origin main`
on the real private repo, and escaped only because all four of its tests happen to patch the
name. That is discipline at every call site, which is exactly what a class fix replaces.

WHAT THIS FILE MUST NOT BECOME. A file of refusal legs alone would pass against a
`commit_and_push` that raised unconditionally, which would silently disable the ntfy mirror, the
director input log and the company-data backup all at once. So the load-bearing test here is
`test_the_push_actually_works_when_it_is_not_a_test_process` -- it drives the real function body
against a real local remote and proves the refusal is the ONLY thing stopping it. Delete that leg
and the rest of the file stops being able to fail.
"""
from __future__ import annotations

import subprocess

import pytest

from background import ops_repo


def _git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


@pytest.fixture()
def ops_clone(tmp_path, monkeypatch):
    """A real git repo with a real remote, standing in for the private ops checkout."""
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "--bare", "--initial-branch=main")

    clone = tmp_path / "ops"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)
    _git(clone, "config", "user.email", "seat@example.invalid")
    _git(clone, "config", "user.name", "seat")
    _git(clone, "symbolic-ref", "HEAD", "refs/heads/main")

    monkeypatch.setattr(ops_repo, "OPS_REPO_DIR", clone)
    monkeypatch.setattr(ops_repo, "_LOCK_FILE", clone / ".ops.lock")
    return clone


def test_a_test_process_cannot_commit_and_push_to_the_private_ops_repo(ops_clone):
    """The refusal exists at all. Before 2026-09-05 this call pushed."""
    (ops_clone / "note.md").write_text("from a test run\n")

    with pytest.raises(ops_repo.OpsRepoWriteUnderTest):
        ops_repo.commit_and_push(["note.md"], "should never reach origin")


def test_the_refusal_names_what_it_refused_and_what_to_do(ops_clone):
    """A refusal that cannot say why is the fail-silent shape this project keeps finding.
    Whoever hits this is reading a traceback from a test they did not write."""
    (ops_clone / "note.md").write_text("x\n")

    with pytest.raises(ops_repo.OpsRepoWriteUnderTest) as caught:
        ops_repo.commit_and_push(["note.md"], "a message worth echoing")

    message = str(caught.value)
    assert "note.md" in message, "the refusal does not say WHICH paths it stopped"
    assert "a message worth echoing" in message, "the refusal does not echo the commit message"
    assert str(ops_clone) in message, "the refusal does not name the repo it protected"


def test_the_refusal_lands_before_anything_is_staged(ops_clone):
    """A refusal placed after the `git add` would already have staged a test's bytes in the
    real repo. This is why the check is the function's first statement."""
    (ops_clone / "note.md").write_text("x\n")

    with pytest.raises(ops_repo.OpsRepoWriteUnderTest):
        ops_repo.commit_and_push(["note.md"], "m")

    staged = subprocess.run(
        ["git", "-C", str(ops_clone), "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert staged == "", f"the refusal staged {staged!r} before refusing"


def test_the_push_actually_works_when_it_is_not_a_test_process(ops_clone, monkeypatch):
    """NON-VACUITY, and the leg the rest of this file rests on.

    Every other test here asserts a REFUSAL, and a `commit_and_push` that raised
    unconditionally -- or one whose body was broken in any way -- would pass all of them. This
    drives the real body end to end against a real remote with the guard's single input flipped,
    so it proves both that the function still works and that the guard is the only thing stopping
    it. It is deliberately keyed to `in_test_process`, the guard's input, and not to an env var:
    an env-var override would be a fail-open door in the shipped module.
    """
    monkeypatch.setattr(ops_repo, "in_test_process", lambda: False)
    (ops_clone / "note.md").write_text("a real daemon's write\n")

    ops_repo.commit_and_push(["note.md"], "a real commit")

    landed = subprocess.run(
        ["git", "-C", str(ops_clone), "log", "--format=%s", "-1", "origin/main"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert landed == "a real commit", f"nothing reached the remote; origin/main says {landed!r}"


def test_an_identical_rewrite_is_a_clean_no_op_and_not_an_exception(ops_clone, monkeypatch):
    """The docstring's "no-ops cleanly if there's nothing to commit" contract, which nothing
    proved. A repeated identical write is the ntfy mirror's normal case, so a raise here would
    page the director every time a message arrived unchanged."""
    monkeypatch.setattr(ops_repo, "in_test_process", lambda: False)
    (ops_clone / "note.md").write_text("same bytes\n")
    ops_repo.commit_and_push(["note.md"], "first")

    ops_repo.commit_and_push(["note.md"], "second, with nothing changed")

    count = subprocess.run(
        ["git", "-C", str(ops_clone), "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert count == "1", f"the no-op branch made a commit anyway ({count} commits)"


def test_a_real_commit_failure_still_raises_rather_than_passing_as_a_no_op(ops_clone, monkeypatch):
    """The other side of the same branch: "nothing to commit" is matched on the git output, so a
    commit that failed for ANY other reason must not be swallowed by it. Keyed to the property --
    a failing commit raises -- and not to today's git wording."""
    monkeypatch.setattr(ops_repo, "in_test_process", lambda: False)
    # No user identity: `git commit` fails with something that is NOT "nothing to commit".
    _git(ops_clone, "config", "--unset", "user.email")
    _git(ops_clone, "config", "--unset", "user.name")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(ops_clone / "absent.gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", str(ops_clone / "absent.gitconfig"))
    monkeypatch.delenv("EMAIL", raising=False)
    (ops_clone / "note.md").write_text("content\n")

    with pytest.raises(RuntimeError) as caught:
        ops_repo.commit_and_push(["note.md"], "will fail for a reason that is not emptiness")

    assert "ops repo commit failed" in str(caught.value)


def test_the_lock_can_be_taken_and_then_refuses_the_second_holder_in_bounded_time(ops_clone):
    """Both sides of the lock in one control, because a lock that refused EVERY acquisition
    would pass a timeout-only test. The partition is asserted whole: it can be taken, while it
    is held the next acquirer is refused by its named exception, and it is released afterwards.

    THE SECOND ACQUIRER RUNS IN A THREAD WITH A JOIN BOUND, and that is the point rather than a
    detail. Written the obvious way -- a nested `with` under `pytest.raises` -- deleting the
    deadline branch does not FAIL this test, it HANGS it: the acquisition loop simply sleeps for
    ever. Measured 2026-09-05, mutating `if time.monotonic() >= deadline:` to `if False:` ran for
    600s and was killed by the harness rather than reported. A control whose failure mode is an
    unbounded hang tells you nothing about which leg broke, and on a full gate run it looks
    exactly like a slow suite. The join bound converts that hang into a named assertion.
    """
    import threading

    outcome: dict[str, str] = {}

    def second_acquirer():
        try:
            with ops_repo.ops_tree_lock(timeout=0.5):
                outcome["result"] = "GRANTED WHILE ALREADY HELD"
        except ops_repo.OpsLockTimeout as exc:
            outcome["result"] = "refused"
            outcome["message"] = str(exc)
        except Exception as exc:  # noqa: BLE001 -- any other failure must not read as a refusal
            outcome["result"] = f"unexpected {type(exc).__name__}: {exc}"

    with ops_repo.ops_tree_lock(timeout=5.0):
        contender = threading.Thread(target=second_acquirer, daemon=True)
        contender.start()
        contender.join(timeout=10.0)
        assert not contender.is_alive(), (
            "the second acquirer never returned within 10s: the lock's deadline branch is "
            "unreachable, so contention HANGS instead of refusing"
        )

    assert outcome["result"] == "refused", outcome["result"]
    assert str(ops_repo._LOCK_FILE) in outcome["message"], (
        "the timeout does not name the lock file it could not take"
    )

    # ...and it is released afterwards, so the refusal above was the lock and not a dead file.
    with ops_repo.ops_tree_lock(timeout=5.0):
        pass


def test_the_guard_is_stronger_than_the_copies_the_callers_hand_rolled(monkeypatch):
    """`ntfy_mirror` and `director_input_log` each key their own refusal to PYTEST_CURRENT_TEST
    alone, which pytest leaves unset during collection and at module import -- a write at import
    time walks straight past both. The shared guard ORs in `"pytest" in sys.modules`, so it still
    refuses with that variable absent. This is the reason the choke-point fix is not just a
    tidier spelling of the two copies."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    assert ops_repo.in_test_process() is True, (
        "with PYTEST_CURRENT_TEST unset the shared guard fell back to the callers' weaker signal"
    )
