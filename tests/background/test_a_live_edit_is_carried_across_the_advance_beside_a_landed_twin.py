"""A live edit and an advance coexist: the twin beside it advances, the edit is carried (2026-10-10).

THE DEFECT, measured on the shared tree 2026-10-10, 25-31 commits behind origin. Nineteen paths
held the fast-forward. Ten were byte-identical to origin, and the reconciler cleared none of them
because (1) two unlanded archive moves -- deleted here, kept by origin -- made
`identical_tracked_twins` answer "could not be established" for the WHOLE set, so no later class
was asked; (2) the delivery seat's module, whose HEAD->disk change was wholly on origin, was held
as "19 lines not on origin" because the line count read HEAD lines origin rewrote as the lane's;
and (3) every class ends with the copy leaving the disk, so any live edit held everything.

Real git in a throwaway origin and clone: the subject is git's own merge and fast-forward. The
classes with no reader for `.md` are injected as refusing so only the classes under test act.

WHAT EACH CONTROL WOULD CATCH:

  * `test_the_twin_advances_and_the_live_edit_survives_onto_origins_copy` -- the DONE criterion in
    one tree. MUTATION: drop `carried_set` from `held` -> held, not advanced. MUTATION: write back
    `plan["local"]` on success -> the file reverts origin's change and this reds.
  * `test_a_conflicting_edit_holds_and_nothing_is_touched` -- the safety property. MUTATION: carry
    a plan whatever `merged[0]` says -> the conflict markers reach the lane's file and this reds.
  * `test_a_lane_deletion_does_not_void_the_comparison_and_is_carried` -- defect (1). MUTATION:
    restore `return None` for the absent-here case -> refused as unread, this reds.
  * `test_a_delta_already_on_origin_is_superseded_though_head_lines_differ` -- defect (2).
    MUTATION: delete the three-way leg in `_superseded_verdict` -> False, this reds.
  * `test_a_staged_edit_is_carried_and_restaged` and
    `test_a_refused_fast_forward_puts_the_carried_edit_back_exactly` -- the lane's index and the
    failure path.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc

_TWIN = "docs/staging/A_NOTE_ORIGIN_LANDED.md"
_LIVE = "docs/staging/A_NOTE_A_LANE_IS_EDITING.md"
_LINES = "".join("line {}\n".format(i) for i in range(1, 21))


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout.strip()


def _put(root: Path, rel: str, text: str) -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text)


def _commit(seed: Path, files: dict[str, str | None], msg: str) -> None:
    for rel, text in files.items():
        if text is None:
            _git(seed, "rm", "-q", rel)
        else:
            _put(seed, rel, text)
            _git(seed, "add", rel)
    _git(seed, "commit", "-q", "-m", msg)
    _git(seed, "push", "-q", "origin", "HEAD:main")


@pytest.fixture
def world(tmp_path, monkeypatch):
    """`(seed, shared)`: origin holds base files; the shared clone sits at that base."""
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"),
                 ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(k, v)
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", "-q", str(origin), str(seed))
    _git(seed, "checkout", "-q", "-b", "main")
    _commit(seed, {_TWIN: "draft\n", _LIVE: _LINES}, "base")
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", "-q", "-b", "main", str(origin), str(shared))
    return seed, shared


def _advance(shared: Path, **overrides) -> dict:
    refuse = lambda _project, paths: {p: (False, "fixture: no reader") for p in paths}  # noqa: E731
    kwargs = dict(stale_fn=refuse, generated_fn=refuse, orphans_fn=refuse,
                  locker=contextlib.nullcontext)
    kwargs.update(overrides)
    _git(shared, "fetch", "-q", "origin")
    return orc.advance_shared_tree(shared, **kwargs)


def _at_origin(shared: Path) -> bool:
    return _git(shared, "rev-parse", "HEAD") == _git(shared, "rev-parse", "origin/main")


def test_the_twin_advances_and_the_live_edit_survives_onto_origins_copy(world):
    seed, shared = world
    origin_live = _LINES.replace("line 2\n", "line 2 -- origin's revision\n")
    _commit(seed, {_TWIN: "landed\n", _LIVE: origin_live}, "origin lands the twin, revises live")
    _put(shared, _TWIN, "landed\n")                                   # equal to origin's
    _put(shared, _LIVE, _LINES.replace("line 18\n", "line 18 -- the lane's edit\n"))

    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert _at_origin(shared)
    assert (shared / _TWIN).read_text() == "landed\n"
    assert (shared / _LIVE).read_text() == origin_live.replace(
        "line 18\n", "line 18 -- the lane's edit\n"), \
        "the lane's edit must sit on origin's copy: origin's revision kept, the lane's line kept"
    assert _git(shared, "diff", "--name-only") == _LIVE, \
        "after the advance the only working-tree change is the lane's own"
    assert orc.CARRIED_PRESERVED_PREFIX in out["reason"]
    ref = _git(shared, "for-each-ref", "--format=%(refname)", orc.CARRIED_PRESERVED_PREFIX)
    assert "line 18 -- the lane's edit" in _git(shared, "show", "{}:{}".format(ref, _LIVE))


def test_a_conflicting_edit_holds_and_nothing_is_touched(world):
    seed, shared = world
    _commit(seed, {_TWIN: "landed\n",
                   _LIVE: _LINES.replace("line 18\n", "line 18 -- origin's\n")}, "origin")
    _put(shared, _TWIN, "landed\n")
    mine = _LINES.replace("line 18\n", "line 18 -- the lane's, differently\n")
    _put(shared, _LIVE, mine)
    head = _git(shared, "rev-parse", "HEAD")

    out = _advance(shared)

    assert out["advanced"] is False
    assert "conflict" in out["reason"] and _LIVE in out["reason"], out["reason"]
    assert _git(shared, "rev-parse", "HEAD") == head
    assert (shared / _LIVE).read_text() == mine, "a conflicting live edit is never written over"
    assert (shared / _TWIN).read_text() == "landed\n"


def test_a_lane_deletion_does_not_void_the_comparison_and_is_carried(world):
    seed, shared = world
    _commit(seed, {_TWIN: "landed\n", _LIVE: _LINES + "origin's addendum\n"}, "origin")
    _put(shared, _TWIN, "landed\n")
    _git(shared, "rm", "-q", _LIVE)                                   # a staged archive move

    _git(shared, "fetch", "-q", "origin")
    assert orc.identical_tracked_twins(
        shared, [{"path": _LIVE, "kind": orc.FF_MODIFIED},
                 {"path": _TWIN, "kind": orc.FF_MODIFIED}]) == [_TWIN], \
        "a lane's deletion is an ANSWERED not-a-twin, never 'git would not answer'"

    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert _at_origin(shared)
    assert not (shared / _LIVE).exists(), "the lane's deletion is carried across"
    assert _git(shared, "diff", "--cached", "--name-status") == "D\t{}".format(_LIVE), \
        "and it is still staged, as the lane left it"


def test_a_delta_already_on_origin_is_superseded_though_head_lines_differ(world):
    seed, shared = world
    lane = _LINES.replace("line 18\n", "line 18 -- landed by the lane\n")
    origin_copy = lane.replace("line 2\n", "line 2 -- rewritten on origin later\n")
    _commit(seed, {_LIVE: origin_copy}, "the lane's change lands, origin moves on")
    _put(shared, _LIVE, lane)
    _git(shared, "fetch", "-q", "origin")

    ok, why = orc._superseded_verdict(shared, _LIVE)

    assert ok, why
    assert "changes nothing" in why


def test_a_staged_edit_is_carried_and_restaged(world):
    seed, shared = world
    _commit(seed, {_LIVE: _LINES.replace("line 2\n", "line 2 -- origin\n")}, "origin")
    _put(shared, _LIVE, _LINES.replace("line 18\n", "line 18 -- lane\n"))
    _git(shared, "add", _LIVE)

    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert _git(shared, "diff", "--name-only") == "", "index and disk agree, as the lane had them"
    staged = _git(shared, "show", ":{}".format(_LIVE))
    assert "line 18 -- lane" in staged and "line 2 -- origin" in staged


def test_a_refused_fast_forward_puts_the_carried_edit_back_exactly(world):
    seed, shared = world
    _commit(seed, {_LIVE: _LINES.replace("line 2\n", "line 2 -- origin\n")}, "origin")
    mine = _LINES.replace("line 18\n", "line 18 -- lane\n")
    _put(shared, _LIVE, mine)
    head = _git(shared, "rev-parse", "HEAD")
    refused = subprocess.CompletedProcess([], 1, "", "fixture: git refused")

    out = _advance(shared, ff_fn=lambda: refused)

    assert out["advanced"] is False
    assert _git(shared, "rev-parse", "HEAD") == head
    assert (shared / _LIVE).read_text() == mine
    assert "put back as they were" in out["reason"], out["reason"]
