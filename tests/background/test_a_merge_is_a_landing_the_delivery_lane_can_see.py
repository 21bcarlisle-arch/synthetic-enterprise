"""A MERGE commit delivers paths, and the delivery lane must be able to bind them.

THE DEFECT THIS EXISTS TO CATCH, measured 2026-09-03. `_commit_facts` read every commit with
`git show --name-only`. For a merge, `git show` prints a COMBINED diff — only files that differ
from every parent — so a clean merge lists no files at all and the function returned
`(when, [])`. `record_landing` cannot tell that from an empty commit, so it bound nothing and
returned `[]`, and the claim went back in the pool 100 minutes later however much had landed.

Why that is not a harmless corner: `tools.surgical_land --merge` is the route CLAUDE.md
SANCTIONS when a dirty shared tree makes `git merge` unsafe. So the sanctioned way to resolve a
divergence was precisely the way to produce a landing this lane could not see. It fired for real
on merge `0e0d17fcc`, which delivered `site/data/value_arms.json` and the floor-leg
pre-registration and bound none of it.

The fix reads a merge as `first-parent..commit` — what the branch GAINED. The paths still come
straight out of git and never from the caller, so the 2026-08-21 shared-tree hole (a caller
naming a broad directory and being credited with other lanes' commits) stays closed.
"""

from __future__ import annotations

import subprocess
import time

import pytest

from background import delivery_lane, seat_work_in_hand


def _git(repo, *args):
    subprocess.run(("git",) + args, cwd=repo, check=True,
                   capture_output=True, text=True)


def _commit(repo, name, body):
    (repo / name).write_text(body)
    _git(repo, "add", name)
    _git(repo, "commit", "-m", f"add {name}")
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A real repository with a real merge. The subject is git's own behaviour, so it cannot be
    faked out: a stub returning the paths we want would prove nothing about `git show`."""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    _commit(r, "base.txt", "base\n")

    _git(r, "checkout", "-q", "-b", "side")
    _commit(r, "only_on_side.txt", "side\n")

    _git(r, "checkout", "-q", "main")
    _commit(r, "only_on_main.txt", "main\n")
    _git(r, "merge", "--no-ff", "-m", "merge side", "side")

    monkeypatch.setattr(delivery_lane, "PROJECT_DIR", r)
    return r


def test_a_merge_binds_the_paths_it_delivered(repo):
    """The whole defect, on a real merge.

    MUTATION: restore the single `git show --no-renames --name-only` read for every commit and
    this fires — `git show` prints a combined diff for a merge, `only_on_side.txt` differs from
    only ONE parent, so the path list comes back EMPTY and the assertion below fails.
    """
    when, paths = delivery_lane._commit_facts("HEAD")

    assert paths == ["only_on_side.txt"], (
        "a merge must bind what it brought in (first-parent..commit). Empty here means the "
        "combined-diff read is back and a sanctioned --merge landing binds nothing."
    )
    assert when > 0.0


def test_a_merge_is_distinguishable_from_an_empty_commit(repo):
    """`(when, [])` is the signal `record_landing` refuses on. A merge must never produce it.

    MUTATION: return `(when, [])` for any commit with more than one parent and this fires. This
    is the leg that names the CONSEQUENCE rather than the mechanism -- the two are separable,
    because a fix could read the merge and still drop the paths on the floor.
    """
    _, merge_paths = delivery_lane._commit_facts("HEAD")
    _, empty_paths = delivery_lane._commit_facts("HEAD~1^{tree}")

    assert merge_paths, "a merge that delivered a file must not read as touching nothing"
    assert not empty_paths, "a tree-ish that is not a commit must still read as unbindable"


def test_an_ordinary_commit_is_read_exactly_as_before(repo):
    """The non-merge path is the one every existing caller depends on. It must not have moved.

    MUTATION: send ordinary commits down the `first-parent..commit` branch as well and this
    still passes -- which is WHY it is not the only leg here. It is a regression guard on the
    untouched majority, not a proof of the fix; `test_a_merge_binds_the_paths_it_delivered` is
    the sole witness for that.
    """
    head_1 = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=repo, check=True,
                            capture_output=True, text=True).stdout.strip()

    when, paths = delivery_lane._commit_facts(head_1)

    assert paths == ["only_on_main.txt"]
    assert when > 0.0


def test_an_unknown_ref_still_binds_nothing(repo):
    """Fail-closed is preserved: the new parent-count read must not turn an unreadable ref into
    a readable one.

    MUTATION: drop the `parents is None` guard and this fires with a crash rather than a clean
    refusal -- an unavailable check has to stay a failed check (R15).
    """
    assert delivery_lane._commit_facts("deadbeefdeadbeefdeadbeef") == (0.0, [])


def test_record_landing_binds_a_merge_end_to_end(repo, tmp_path, monkeypatch):
    """The defect was only ever visible one layer up, so grade it there too.

    `_commit_facts` returning paths is necessary and not sufficient: `record_landing` is what the
    doorbell tells every tick to call, and it is what returned `[]` on 2026-09-03.

    MUTATION: make `_commit_facts` return `(when, [])` for a merge and this fires on the
    `bound` assertion -- the same way the live lane failed, at the layer that reported it.
    """
    store = tmp_path / "claims.json"
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", store)
    # Claimed BEFORE the merge landed, which is the real order and the only one `record_landing`
    # will credit: it refuses a commit older than the claim's first draw, so a fixture that
    # claims after committing tests that guard instead of this one.
    seat_work_in_hand.claim("land-a-merge", "test", [], path=store,
                            now=time.time() - 3600)

    bound = delivery_lane.record_landing("land-a-merge", commit="HEAD", path=store)

    assert "only_on_side.txt" in bound, (
        "the paths a sanctioned --merge landing delivered must reach the claim's file_scope"
    )
