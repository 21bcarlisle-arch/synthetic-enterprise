"""The defect: the advance could prove a blocker lossless in exactly two ways, and the blocker this
tree actually GROWS was neither of them.

`tools/surgical_land --content` does not write the working tree -- deliberately, because that is
what makes it safe on a file two lanes hold -- so every correct landing through that door leaves a
working copy strictly BEHIND its own commit. That copy is not byte-identical to origin, so neither
twin sweep can take it, and it refused the fast-forward until a human cleared it by hand. Cleared
by hand on 2026-09-15; refilled in three hours. A refusal whose remedy is provable and which
nothing automatically applies, standing in front of a queue that refills once per landing, is a
wedge with no exit.

THE DANGER IN THE FIX IS THE MIRROR IMAGE, and it is the one this file is mostly about. A reconciler
that writes HEAD's bytes over a working copy has become `git checkout <path>` -- a wall here -- the
moment its proof is weaker than its act. So the reachability control comes first (a sweep that
refuses everything passes every refusal test while clearing none of the queue it exists to drain),
and every other test names a way a lane's real work could be destroyed.

KEYED TO THE PROPERTY, NEVER TO TODAY'S EIGHT PATHS: *a blocker this tool can prove costs the
holding lane nothing does not reach the refusal list, and one it cannot prove always does.*
"""
from __future__ import annotations

import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from background import origin_reconcile as orc

#: What HEAD holds. `landed_helper` is the name the rival copy will be missing.
V1 = (
    "def alpha():\n    return 1\n\n\n"
    "def landed_helper(argument):\n"
    '    """A line distinctive enough to be found by -S, and long enough not to be trivial."""\n'
    "    return argument * 41 + 7\n"
)

#: What ORIGIN holds: HEAD's names plus one more. Origin must touch the path or it is not a
#: blocker at all -- `FF_MODIFIED` means "modified here, AND origin changes it too".
V2 = V1 + (
    "\n\ndef landed_on_origin_after_this_head(argument):\n"
    '    """Origin moved past HEAD at this path, which is what makes HEAD a stale base."""\n'
    "    return argument - 3\n"
)

#: THE REFILL. The lane's bytes as they were before its own landing went in through
#: `surgical_land --content`: it supplies no name origin lacks and it has LOST one, which is
#: exactly what `stale_copy_refusal.judge` refuses.
STALE_RIVAL = "def alpha():\n    return 1\n"

#: HOLDER WORK, and the thing that must SURVIVE. It carries a name nothing upstream has. A run that
#: sweeps this has become `git checkout` and is a failure of the whole mechanism, not a success.
HOLDER_WORK = V1 + (
    "\n\ndef only_this_lane_has_ever_had_this(argument):\n"
    "    return 'unlanded work that exists nowhere else'\n"
)

TWIN_BYTES = "# a staging note origin adds its own identical copy of\n\nprose\n"


def _git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A real local tree BEHIND a real origin, with real blockers on disk.

    A fake is not available here: the subject is `git merge --ff-only`'s own refusal, git's
    tracked/untracked distinction, `git hash-object` against a remote blob, and a `refs/preserved/*`
    commit written through a throwaway index. Every one of those is git, and a fake more permissive
    than its subject is how a fail-open goes green.
    """
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(seed, "init", "-q", "-b", "main")
    _git(seed, "config", "user.email", "t@t")
    _git(seed, "config", "user.name", "t")
    (seed / "rival.py").write_text(V1)
    (seed / "holder.py").write_text(V1)
    _git(seed, "add", "rival.py", "holder.py")
    _git(seed, "commit", "-qm", "the base both sides share")
    _git(seed, "remote", "add", "origin", str(origin))
    _git(seed, "push", "-q", "origin", "main")

    local = tmp_path / "local"
    _git(tmp_path, "clone", "-q", str(origin), str(local))
    _git(local, "config", "user.email", "t@t")
    _git(local, "config", "user.name", "t")

    # Origin moves past this HEAD -- three paths, which is what makes all three blockers real.
    (seed / "rival.py").write_text(V2)
    (seed / "holder.py").write_text(V2)
    (seed / "twin.md").write_text(TWIN_BYTES)
    _git(seed, "add", "rival.py", "holder.py", "twin.md")
    _git(seed, "commit", "-qm", "origin moves on")
    _git(seed, "push", "-q", "origin", "main")
    _git(local, "fetch", "-q", "origin")

    (local / "rival.py").write_text(STALE_RIVAL)
    (local / "twin.md").write_text(TWIN_BYTES)
    return local


def _blockers(tree: Path) -> list[dict]:
    return orc.paths_blocking_fast_forward(tree)


@contextmanager
def _nolock():
    """The real lock lives at a production path the test-isolation guard refuses, and the lock is
    not this change's subject -- `test_a_second_reconciler_does_not_rebuild_the_worktree_under_a_
    running_merge` is. Substituting it here keeps the tree under test a real git tree."""
    yield


# ------------------------------------------------- the permissive branch must be REACHABLE first


def test_the_whole_partition_is_reachable_on_one_tree(tree: Path) -> None:
    """ONE CONTROL OVER THE WHOLE PARTITION, rather than a leg per branch.

    Three classes decide this tree -- an untracked twin, a stale rival copy origin supersedes, and
    holder work nobody may touch -- and a mechanism that collapsed any two of them into one would
    pass a test per class while being unable to tell them apart. So all three are asserted
    NON-EMPTY, over one tree, before anything asserts what any of them does.
    """
    (tree / "holder.py").write_text(HOLDER_WORK)
    blocking = _blockers(tree)
    assert blocking is not None
    paths = {b["path"] for b in blocking}
    assert {"rival.py", "twin.md", "holder.py"} <= paths, (
        "the fixture did not produce all three blocker classes, so every verdict below would be "
        "measured over a partition with a hole in it: {}".format(sorted(paths)))

    assert orc.identical_untracked_twins(tree, blocking) == ["twin.md"]
    assert orc.identical_tracked_twins(tree, blocking) == []
    verdicts = orc.stale_copy_verdicts(tree, ["rival.py", "holder.py"])
    assert verdicts["rival.py"][0] is True, verdicts["rival.py"][1]
    assert verdicts["holder.py"][0] is False, verdicts["holder.py"][1]


def test_a_stale_copy_origin_supersedes_is_refreshed_and_the_tree_advances(tree: Path) -> None:
    """THE DRAIN ITSELF. Without this the refill has no exit and every refusal test below is a
    test of a mechanism that clears nothing."""
    result = orc.advance_shared_tree(tree, locker=_nolock)

    assert result["advanced"] is True, result["reason"]
    assert set(result["cleared"]) == {"rival.py", "twin.md"}, result
    assert orc.commits_behind(tree) == 0
    assert (tree / "rival.py").read_text() == V2, (
        "the fast-forward did not install origin's bytes at the refreshed path, so the refresh "
        "moved the tree somewhere origin never was")
    assert (tree / "twin.md").read_text() == TWIN_BYTES


def test_the_refreshed_copys_own_bytes_survive_on_a_preserved_ref(tree: Path) -> None:
    """THE BYTES ARE DESTROYED, SO THE RECOVERY ROUTE IS THE WHOLE LICENCE.

    `refresh_to_head` verifies the route before it writes. What this asserts is the part only the
    caller can get wrong: that the ref the REASON names is the ref that exists. A preservation
    nobody can find by the name they were given is a preservation in name only, and the difference
    is invisible until someone needs it.
    """
    slug = orc.refresh_slug(tree)
    result = orc.advance_shared_tree(tree, locker=_nolock)
    assert result["advanced"] is True, result["reason"]

    ref = orc.REFRESH_PRESERVED_PREFIX + slug
    assert ref in result["reason"], (
        "the reason does not name the ref holding the only copy of the destroyed bytes: {}".format(
            result["reason"]))
    assert _git(tree, "show", "{}:rival.py".format(ref)) == STALE_RIVAL


def test_the_slug_is_keyed_to_head_so_one_advance_cannot_delete_anothers_preservation(
        tree: Path) -> None:
    """`git update-ref` REPLACES. A fixed slug would make each advance's preservation overwrite the
    previous one's -- the bytes go unreachable, `git log --all -S` stops finding them, and nothing
    is red until the run nobody has needed yet."""
    before = orc.refresh_slug(tree)
    orc.advance_shared_tree(tree, locker=_nolock)
    assert orc.refresh_slug(tree) != before, (
        "the preservation slug did not move when HEAD did, so the next advance writes over this "
        "one's only copy of a lane's discarded bytes")


# ------------------------------------------------------------------------------ what must SURVIVE


def test_holder_work_survives_and_is_refused_by_name_with_its_reason(tree: Path) -> None:
    """THE FAILURE THIS WOULD BE. A copy supplying a name nothing upstream has is a lane's real
    work; writing HEAD over it is `git checkout <path>`, which is a wall here. The refusal must
    also SAY WHY: 'not byte-identical to what origin brings' is equally true of holder work nobody
    may touch and of a file this tree has no reader for, and those want opposite acts."""
    (tree / "holder.py").write_text(HOLDER_WORK)

    result = orc.advance_shared_tree(tree, locker=_nolock)

    assert result["advanced"] is False
    assert result["cleared"] == []
    assert (tree / "holder.py").read_text() == HOLDER_WORK, (
        "the advance overwrote a working copy carrying a name nothing upstream has -- it has "
        "become `git checkout <path>`, which is the wall this mechanism exists under")
    assert "holder.py" in result["reason"]
    assert "SUPPLIES" in result["reason"], (
        "the refusal named the path but not the reason, which is the whole of what a reader needs "
        "to know whether the refusal is the right one: {}".format(result["reason"]))


def test_one_unprovable_blocker_holds_the_provable_ones_untouched(tree: Path) -> None:
    """ALL-OR-NOTHING, AND IT IS A SAFETY PROPERTY. A tree holding one unprovable path cannot
    fast-forward however many provable ones are cleared, so clearing them there would be bytes
    destroyed for no advance -- the one shape in which this could actually cost someone
    something."""
    (tree / "holder.py").write_text(HOLDER_WORK)

    orc.advance_shared_tree(tree, locker=_nolock)

    assert (tree / "rival.py").read_text() == STALE_RIVAL, (
        "the stale copy was refreshed behind a blocker that still refuses the advance: bytes "
        "destroyed for nothing")
    assert (tree / "twin.md").exists()
    assert orc.commits_behind(tree) != 0


def test_an_ordinary_edit_on_top_of_origin_is_not_a_stale_copy(tree: Path) -> None:
    """THE NARROWEST WAY THIS COULD BECOME `git checkout`: a copy that is simply AHEAD of origin
    in the ordinary way -- same names, changed values. Symbol-set granularity is blind to a changed
    constant, so `stale_copy_refusal.judge` having a complaint is the precondition that catches it,
    and this is the test that it is load-bearing rather than ornamental."""
    (tree / "rival.py").write_text(V2.replace("return argument * 41 + 7", "return argument * 41"))

    verdicts = orc.stale_copy_verdicts(tree, ["rival.py"])

    assert verdicts["rival.py"][0] is False, (
        "an ordinary value-level edit was judged a stale copy, which is `git checkout <path>` "
        "with a nicer name: {}".format(verdicts["rival.py"][1]))


def test_an_unreadable_judgement_refuses_rather_than_clearing(tree: Path) -> None:
    """FAIL-CLOSED, and the direction matters more than the mechanism. `{}` would mean 'nothing is
    refreshable' and is the correct answer to 'I looked and found none'; it is the WRONG answer to
    'I could not look', and a caller cannot tell them apart from the value alone -- so the
    unreadable case must produce a refusal that names every path it could not judge."""
    (tree / "holder.py").write_text(HOLDER_WORK)

    def _blind(project, paths):
        return None

    result = orc.advance_shared_tree(tree, locker=_nolock, stale_fn=_blind)

    assert result["advanced"] is False
    assert result["cleared"] == []
    assert "could not be established" in result["reason"]
    assert (tree / "rival.py").read_text() == STALE_RIVAL


def test_a_refresh_that_fails_stops_the_advance_and_touches_no_twin(tree: Path) -> None:
    """The refresh runs FIRST inside the lock and writes nothing unless every path it is handed is
    refreshable, so its failure must leave the twins beside it on disk -- not half a tree."""
    def _fails(paths):
        return "the stale-copy judgement changed under us"

    result = orc.advance_shared_tree(tree, locker=_nolock, refresher=_fails)

    assert result["advanced"] is False
    assert result["cleared"] == []
    assert "changed under us" in result["reason"]
    assert (tree / "twin.md").exists(), (
        "an untracked twin was removed after the refresh leg had already failed, which is a "
        "deletion bought for no advance")


# --------------------------------------------------------------- the base the judgement is asked of


def test_the_judgement_is_asked_of_origin_and_not_of_the_stale_head(tree: Path) -> None:
    """THE ITEM'S OWN CORRECTION, AND IT IS MEASURABLE. This tree is BEHIND origin by construction,
    so HEAD is exactly the stale base `stale_copy_refusal`'s banner warns its verdicts are unsafe
    against. Asked of HEAD, this copy reads as an ordinary edit and is refused; asked of origin --
    the bytes the tree is about to hold -- it is the rival copy it actually is. Two different
    answers about one file, and only the origin-keyed one is about the tree that will exist.
    """
    from tools.refresh_to_head import REFRESHABLE, judge_copy

    # A copy that LOSES only the name origin added after this HEAD. Against HEAD it supplies
    # nothing and loses nothing, so there is no complaint to refuse it with.
    (tree / "rival.py").write_text(V1)

    against_head = judge_copy(tree, "rival.py", base="HEAD")
    against_origin = judge_copy(tree, "rival.py", base="origin/main")

    assert against_head.state != REFRESHABLE, against_head.reason
    assert against_origin.state == REFRESHABLE, (
        "the copy is not judged against the tree it is about to be replaced by, so a landing that "
        "reached origin but not yet this HEAD cannot be seen at all: {}".format(
            against_origin.reason))
