"""In the gate's extract, `HEAD:` is the PARENT and the INDEX is the parent for every path the
landing did not name. Pinned against the real builder, because believing otherwise cost three
cycles twice.

THE DEFECT THIS FAILS ON, and it is a whole class rather than one site. A control that reads
`git show HEAD:<path>` and means *the bytes of the commit being graded* is green in every working
tree by construction -- there, `HEAD` IS the checkout -- and can only ever red inside
`tools/surgical_land`'s gate, on a commit that legitimately changes that path, naming an innocent
subject to a lane that did not cause it. One instance wedged the only door `origin_reconcile` has
for three cycles (`tests/tools/test_generate_value_arms_data.py`, repaired 2026-09-24).

WHY THIS IS A CONTROL AND NOT A COMMENT. The class is invisible everywhere it happens to be green,
which is everywhere except the gate, so no amount of reading a control's own file tells you which
revision it got. Two prior invocations reached for "stale working copy" first. What a reader needs is
one runnable statement of what the three revisions in that extract actually hold -- driven through
`materialise` itself, so it cannot drift from the gate the way a restated copy would.

AND THE THIRD LEG IS THE ONE THAT WAS WRONG IN THE RECORD. `docs/staging/done/SEAT_FINDING_THE_
GATES_EXTRACT_POINTS_HEAD_AT_THE_PARENT_...md` wrote that the extract offers "parent (`HEAD`),
result (index), result (working tree)". The index is NOT the result tree: `_make_standalone_repo`
does `read-tree <parent>`, and `materialise` then stages only the landing's own pathspec over it.
For a path absorbed by a MERGE -- which is precisely the path that wedged the value-arms leg -- the
index still carries the PARENT. Only disk holds the result tree throughout.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

from tools import surgical_land as sl

#: `materialise` refuses below this much free disk, which is a refusal about the machine and not
#: about the property here. Read from the module so a change to the threshold cannot silently turn
#: this control into a skip that nobody notices.
_NEEDS_MB = sl.MIN_FREE_MB


def _git(cwd: Path, *args: str) -> str:
    """A git command whose environment cannot be inherited from the test runner's own repo."""
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                          env={**sl._gitless_env(), "GIT_AUTHOR_NAME": "t",
                               "GIT_AUTHOR_EMAIL": "t@example.invalid",
                               "GIT_COMMITTER_NAME": "t",
                               "GIT_COMMITTER_EMAIL": "t@example.invalid"})
    assert done.returncode == 0, "git {} failed: {}".format(" ".join(args), done.stderr.strip())
    return done.stdout.strip()


def _resolves(cwd: Path, spec: str) -> str | None:
    """The bytes at `spec`, or None where that revision does not carry the path at all."""
    done = subprocess.run(["git", "-C", str(cwd), "show", spec], capture_output=True, text=True,
                          env=sl._gitless_env())
    return done.stdout if done.returncode == 0 else None


@pytest.fixture
def extract(tmp_path_factory):
    """A gate-shaped extract of a two-commit repo, built by `surgical_land.materialise` itself.

    The commit being graded does three different things, because the three revisions only tell
    themselves apart across all three:
      * `named.txt`  -- changed AND in the landing's pathspec (the ordinary case)
      * `absorbed.txt` -- changed in the result tree and NOT in the pathspec (a merge absorption)
      * `added.txt`  -- created by this commit, in the pathspec (the presence case)
    """
    if (sl._free_mb(str(tmp_path_factory.getbasetemp())) or _NEEDS_MB) < _NEEDS_MB:
        pytest.skip("less than {}MB free: `materialise` refuses on disk, not on code".format(
            _NEEDS_MB))

    root = tmp_path_factory.mktemp("root")
    _git(root, "init", "-q")
    for name in ("named.txt", "absorbed.txt"):
        (root / name).write_text("parent\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "the parent")
    parent = _git(root, "rev-parse", "HEAD")

    for name in ("named.txt", "absorbed.txt", "added.txt"):
        (root / name).write_text("this commit\n")
    _git(root, "add", "-A")
    result_tree = _git(root, "write-tree")
    # Back the shared index out again: the landing stages its own pathspec inside the extract, and
    # leaving `root`'s index dirty would let this fixture pass by accident.
    _git(root, "read-tree", parent)

    checkout = Path(tempfile.mkdtemp(dir=str(tmp_path_factory.getbasetemp())))
    sl.materialise(root, checkout, result_tree, parent, ["named.txt", "added.txt"])
    return checkout


def test_HEAD_in_the_extract_is_the_PARENT_and_not_the_commit_being_graded(extract):
    """The whole class in one assertion: `HEAD:` is the previous commit's bytes.

    A control keyed to this and meaning "this commit" is red by construction here and green in
    every working tree, which is the asymmetry that makes the class undiagnosable from outside.
    """
    assert _resolves(extract, "HEAD:named.txt") == "parent\n", (
        "the extract's `HEAD:` no longer holds the parent's bytes. If `_make_standalone_repo` was "
        "changed deliberately, every control that reads `HEAD:` as a BASELINE (the level gate, the "
        "orphan ratchet, canon drift) now measures against something else -- that is the finding, "
        "not this assertion"
    )
    assert (extract / "named.txt").read_text() == "this commit\n", (
        "the extract's working tree is not the tree the commit would create, so the gate is not "
        "grading this commit at all"
    )


def test_the_extract_HAS_a_resolvable_HEAD_so_a_no_HEAD_skip_is_DEAD(extract):
    """A branch keyed to "the landing checkout has no commit" never runs, and never says so.

    Several controls carry `if not _head_resolves(): ...` with a comment reading *"the landing
    checkout does not have a commit"*. That was true before `_make_standalone_repo` gave the
    extract a history; it is false now, and a dead skip is worse than an absent one because it
    reads like a handled case. Whoever repairs that family deletes the branch on this evidence.
    """
    assert _git(extract, "rev-parse", "--verify", "HEAD"), (
        "the extract has no resolvable HEAD after all -- then the `_head_resolves()` skips are "
        "live again and this control is what is stale"
    )


def test_the_INDEX_is_the_commit_ONLY_for_the_paths_the_landing_NAMED(extract):
    """Refutes the record: the index is not the result tree, it is the parent plus the pathspec.

    This is the leg that decides whether `:<path>` is a sound repair for a control that means "this
    commit". It is sound for a path the landing names and UNSOUND for one a merge absorbed -- and
    the value-arms wedge was an absorbed path, so a blanket "read the index instead" would have
    reproduced the wedge on exactly the commits that hit it.
    """
    assert _resolves(extract, ":named.txt") == "this commit\n", (
        "a path in the landing's own pathspec is not staged from the result tree -- then no git "
        "revision in this extract carries this commit's bytes for it"
    )
    assert _resolves(extract, ":absorbed.txt") == "parent\n", (
        "the index now carries the result tree for a path the landing did NOT name. If that is "
        "deliberate, `:<path>` has become a sound `this commit` oracle for every path and the "
        "class above narrows -- say so in the record rather than deleting this leg"
    )
    assert (extract / "absorbed.txt").read_text() == "this commit\n", (
        "disk does not carry the absorbed path's new bytes, so the extract is not the result tree"
    )


def test_a_path_the_commit_ADDS_is_absent_at_HEAD_and_present_in_the_INDEX(extract):
    """The presence flavour of the class, which is the one that survived into 2026-09-24.

    `git cat-file -e HEAD:<path>` written to mean *is this artefact in the commit* answers NO for
    every path the commit creates. A control that cites a measurement artefact and requires it to
    be committed -- `site/test_the_book_is_bounded_by_compute_reaches_the_reader` -- therefore
    refuses the commit that writes the artefact and its citation together, which is the only way
    that pair is ever written.
    """
    assert _resolves(extract, "HEAD:added.txt") is None, (
        "a path created by the commit being graded now resolves at `HEAD:`, which would mean the "
        "extract's HEAD is the commit and not its parent"
    )
    assert _resolves(extract, ":added.txt") == "this commit\n", (
        "a created path in the landing's pathspec is not in the extract's index either -- then "
        "presence cannot be asked of git here at all, and the honest oracle is disk"
    )


def test_the_three_revisions_are_genuinely_DISTINCT_here(extract):
    """THE PARTITION CONTROL. Every leg above compares one revision against one expected string,
    so all of them pass if two of the three revisions collapsed onto the same bytes -- which is
    exactly what a fixture that forgot to make the commit change anything produces, and it would
    read as the mechanism working. This requires the extract to actually distinguish them.
    """
    seen = {
        "HEAD": _resolves(extract, "HEAD:absorbed.txt"),
        "index": _resolves(extract, ":named.txt"),
        "disk": (extract / "absorbed.txt").read_text(),
    }
    assert seen["HEAD"] != seen["index"], (
        "HEAD and the index agree on this fixture, so the legs above cannot tell them apart: "
        "{!r}".format(seen)
    )
    assert seen["HEAD"] != seen["disk"], (
        "HEAD and disk agree on this fixture, so nothing here measures the class: {!r}".format(seen)
    )
    assert _resolves(extract, "HEAD:added.txt") is None and (extract / "added.txt").is_file(), (
        "the created path is not distinguishing absence-at-HEAD from presence-on-disk: the "
        "presence leg above would pass for the wrong reason"
    )
