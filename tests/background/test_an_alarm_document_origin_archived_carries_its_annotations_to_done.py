"""An alarm document origin moved to done/ no longer wedges the shared fast-forward (2026-11-16).

THE DEFECT. `alarm_repetition` writes dated lines into a staging alarm document in the shared tree
and never commits them. When an archiver moved that document to `done/` on origin, the dirty path
was one origin no longer held, so the carried class refused it ("HEAD and origin must both hold
the path"), and `merge --ff-only` refused every five minutes until a lane landed the shared tree's
bytes first by hand: 759fac9831, then 06235c81f + 2f23ad063 for the same document.

Real git in a throwaway origin and clone; the classes with no reader for `.md` refuse.

WHAT EACH CONTROL WOULD CATCH:

  * `test_the_annotations_follow_the_document_to_where_origin_moved_it` -- the DONE criterion.
    MUTATION: drop the move leg in `_carry_plan` -> held, not advanced, this reds (measured: it
    is the pre-fix behaviour). MUTATION: write the merged bytes back at `path` instead of
    `plan["target"]` -> the root copy reappears untracked and done/ lacks the lines.
    MUTATION: drop `--no-renames` from `_arriving_paths` -> git reports the move by its new name
    only, the blocker is "NOTHING local collides", and this reds (that was the live log's shape).
  * `test_a_document_origin_deleted_outright_still_holds` -- the move leg is keyed to git's rename
    detection, not to absence: a deletion has nowhere to carry the lines, so it holds untouched.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc

_DOC = "docs/staging/WORKER_FINDING_REPEATING_ALARM_X_2026-11-08.md"
_DONE = "docs/staging/done/WORKER_FINDING_REPEATING_ALARM_X_2026-11-08.md"
_BODY = "# alarm\n\n" + "".join("context line {}\n".format(i) for i in range(1, 21)) + \
        "\n## Observations\n\n- 2026-11-08: first\n"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture
def world(tmp_path, monkeypatch):
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"),
                 ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(k, v)
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", "-q", str(origin), str(seed))
    _git(seed, "checkout", "-q", "-b", "main")
    (seed / _DOC).parent.mkdir(parents=True)
    (seed / _DOC).write_text(_BODY)
    _git(seed, "add", _DOC)
    _git(seed, "commit", "-q", "-m", "base")
    _git(seed, "push", "-q", "origin", "HEAD:main")
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", "-q", "-b", "main", str(origin), str(shared))
    # the alarm daemon's in-place, never-committed annotations
    (shared / _DOC).write_text(_BODY + "- 2026-11-15: still firing\n- 2026-11-16: still firing\n")
    return seed, shared


def _advance(shared: Path) -> dict:
    refuse = lambda _project, paths: {p: (False, "fixture: no reader") for p in paths}  # noqa: E731
    _git(shared, "fetch", "-q", "origin")
    return orc.advance_shared_tree(shared, stale_fn=refuse, generated_fn=refuse,
                                   orphans_fn=refuse, locker=contextlib.nullcontext)


def test_the_annotations_follow_the_document_to_where_origin_moved_it(world):
    seed, shared = world
    (seed / _DONE).parent.mkdir(parents=True)
    _git(seed, "mv", _DOC, _DONE)
    (seed / _DONE).write_text("**Resolved by abc1234.**\n\n" + _BODY)
    _git(seed, "add", _DONE)
    _git(seed, "commit", "-q", "-m", "archive the alarm")
    _git(seed, "push", "-q", "origin", "HEAD:main")

    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert _git(shared, "rev-parse", "HEAD") == _git(shared, "rev-parse", "origin/main")
    assert not (shared / _DOC).exists(), "the root copy goes where origin sent it"
    text = (shared / _DONE).read_text()
    assert text.startswith("**Resolved by abc1234.**"), "origin's archive note is kept"
    assert text.endswith("- 2026-11-15: still firing\n- 2026-11-16: still firing\n"), \
        "the daemon's uncommitted lines are carried onto the archived copy"
    assert _git(shared, "status", "--porcelain") == "M {}".format(_DONE)
    assert orc.CARRIED_PRESERVED_PREFIX in out["reason"]


def test_a_document_origin_deleted_outright_still_holds(world):
    seed, shared = world
    _git(seed, "rm", "-q", _DOC)
    _git(seed, "commit", "-q", "-m", "delete the alarm")
    _git(seed, "push", "-q", "origin", "HEAD:main")
    head = _git(shared, "rev-parse", "HEAD")
    before = (shared / _DOC).read_text()

    out = _advance(shared)

    assert out["advanced"] is False
    assert _DOC in out["reason"], out["reason"]
    assert _git(shared, "rev-parse", "HEAD") == head
    assert (shared / _DOC).read_text() == before
