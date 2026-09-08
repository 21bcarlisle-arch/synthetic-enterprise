"""The census must name the commit that CHOSE a deletion, not the merge that adopted it.

THE DEFECT THIS OWNS. While `stale_copy_refusal` had no channel for the merge ref it refused a merge
over a path this side never touched, and the only route through was `--drops` -- which credits the
deletion to the landing that declared it. So the record contains merges credited with deletions
another lane chose, and nothing said so. `22df46614` is the receipt and it is asserted below against
real history, because that commit is immutable and the claim cannot rot.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import merge_attribution_census as mac
from tools import stale_copy_refusal as scr

REPO_ROOT = Path(__file__).resolve().parents[2]

#: PADDED ON PURPOSE. Leg 2 needs this side's edit and the other lane's deletion to be a REAL
#: auto-merge, so they must fall in different hunks. Without the padding git conflicts, and the only
#: ways out are a hand-built result tree (a fake more permissive than its subject) or resolving the
#: conflict myself (which makes the merge MY choice and destroys the very thing under test).
def _pad(tag: str) -> str:
    return "".join("# {} padding line {}\n".format(tag, i) for i in range(12))


DISTINCTIVE = '"""A line distinctive enough to anchor rule 1."""'
HELPER = ("def helper_the_other_lane_deletes(argument):\n"
          "    " + DISTINCTIVE + "\n"
          "    return argument * 3\n\n\n")


def _module(helper: bool, omega_body: str = "    return 2\n") -> str:
    return ("def alpha():\n    return 1\n\n\n"
            + _pad("upper") + "\n"
            + (HELPER if helper else "")
            + _pad("lower") + "\n"
            + "def omega():\n" + omega_body)


BASE = _module(True)
WITHOUT_HELPER = _module(False)
OURS_EDIT = _module(True, "    return 99\n")


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)
    assert out.returncode == 0, "git {} failed: {}".format(" ".join(args), out.stderr)
    return out.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo with real merge commits. NOT a fake: the subject is what git records as a
    merge's parents and trees, and a hand-built stand-in would be `a fake more permissive than its
    subject` -- the shape that turns a fail-open into a green suite."""
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "m.py").write_text(BASE)
    _run(root, "add", "m.py")
    _run(root, "commit", "-qm", "the base both sides share")
    return root


def _commit(root: Path, path: str, text: str, message: str) -> str:
    (root / path).write_text(text)
    _run(root, "add", path)
    _run(root, "commit", "-qm", message)
    return _run(root, "rev-parse", "HEAD").strip()


def _diverge_and_merge(root: Path, ours: str | None) -> tuple[str, str]:
    """Build a real merge. The other lane always deletes the helper; `ours` is what THIS side does
    to `m.py` first -- `None` meaning it never opens the file. Returns (merge sha, chooser sha)."""
    _run(root, "branch", "other")
    if ours is None:
        _commit(root, "elsewhere.py", "def ours():\n    return 'worked elsewhere'\n",
                "this side never opens m.py")
    else:
        _commit(root, "m.py", ours, "this side edits m.py too")
    _run(root, "checkout", "-q", "other")
    chooser = _commit(root, "m.py", WITHOUT_HELPER,
                      "the other lane deliberately drops the helper and declares it")
    _run(root, "checkout", "-q", "main")
    _run(root, "merge", "--no-ff", "-q", "-m", "merge other", "other")
    return _run(root, "rev-parse", "HEAD").strip(), chooser


def test_the_census_names_the_lane_that_chose_the_deletion_not_the_merge_that_adopted_it(
        repo: Path) -> None:
    """LEG 1. This side never opened `m.py`, so the merge is credited with a deletion it adopted."""
    merge, chooser = _diverge_and_merge(repo, None)

    rows = mac.census(repo)
    assert [(r.merge, r.path) for r in rows] == [(merge, "m.py")], (
        "the census must find the one adopted name loss in this history; finding none is the "
        "failure mode that made 22df46614's misattribution invisible for as long as it was")
    assert rows[0].choosers == {"helper_the_other_lane_deletes": chooser}, (
        "the row must name the commit that CHOSE the deletion, not the merge that adopted it -- "
        "attributing it to the merge is the defect, restated")
    assert rows[0].unattributed() == ()


def test_a_path_this_side_also_edited_is_not_a_misattribution_and_is_still_a_loss(
        repo: Path) -> None:
    """LEG 2, AND ITS POISON ROUND. The census's subject is exactly the population the guard now
    exempts. A path this side edited stays refused -- the lane is made to look at it -- so it is
    NOT a misattribution, and the empty census below must be that and not an empty subject."""
    merge, _ = _diverge_and_merge(repo, OURS_EDIT)

    first = mac._parents(repo, merge)[0]
    paths = mac._changed(repo, first, merge)
    assert [loss.path for loss in scr.violations(repo, first, merge, paths)] == ["m.py"], (
        "POISON ROUND FIRST: the guard must still see a name loss on this merge, or the empty "
        "census below is green for want of anything to find rather than because the rule holds")

    assert mac.census(repo) == [], (
        "a path this side edited is this lane's own decision to answer for; exempting it here "
        "would launder exactly the reverts the guard exists to refuse")


def test_a_predates_landing_row_is_traceable_because_its_token_is_a_line_not_a_symbol(
        repo: Path) -> None:
    """THE DEFECT THE FIRST DRAFT SHIPPED, kept as a control because it was silent, not loud.

    `strict_symbol_subset` details are symbol names; `predates_landing` details are distinctive
    LINES. Reading both as symbol names never matches a line, so every `predates_landing` row
    reported "chooser not established" -- 113 of 120 on real history -- in a voice indistinguishable
    from history genuinely not containing the answer. This drives the line reader directly."""
    line = DISTINCTIVE
    assert mac._carries(BASE, "m.py", line, scr.PREDATES) is True
    assert mac._carries(WITHOUT_HELPER, "m.py", line, scr.PREDATES) is False
    assert mac._carries(BASE, "m.py", line, scr.SUBSET) is False, (
        "read as a SYMBOL name a distinctive line is absent from every file including the one it "
        "is written in -- that asymmetry is the whole defect, so it is asserted and not described")

    _run(repo, "branch", "other")
    _commit(repo, "elsewhere.py", "def ours():\n    return 1\n", "this side never opens m.py")
    _run(repo, "checkout", "-q", "other")
    chooser = _commit(repo, "m.py", WITHOUT_HELPER, "the other lane rewrites m.py")
    _run(repo, "checkout", "-q", "main")
    base = _run(repo, "merge-base", "main", "other").strip()
    assert mac.chose_the_deletion(repo, base, chooser, "m.py", line, scr.PREDATES) == chooser
    assert mac.chose_the_deletion(repo, base, chooser, "m.py", line, scr.SUBSET) == "", (
        "the same call under the wrong rule must find nothing -- proving the rule argument is "
        "load-bearing and not decoration")


def test_a_name_deleted_re_added_and_deleted_again_is_charged_to_the_LAST_deletion(
        repo: Path) -> None:
    """THE RE-ADD IS WHY THE WALK RUNS NEWEST-FIRST, and this test exists because reversing the walk
    changed no result until it was written -- a mutation surviving on a rule that was simply wrong.

    After the re-add the name is PRESENT, so the earliest deletion is not what the merge adopts; it
    was undone. Charging it there would name a lane whose choice the history reversed."""
    _run(repo, "branch", "other")
    _commit(repo, "elsewhere.py", "def ours():\n    return 1\n", "this side never opens m.py")
    _run(repo, "checkout", "-q", "other")
    first_delete = _commit(repo, "m.py", WITHOUT_HELPER, "the helper goes")
    _commit(repo, "m.py", BASE, "the helper comes back -- the first deletion is undone")
    last_delete = _commit(repo, "m.py", WITHOUT_HELPER, "the helper goes again, and stays gone")
    _run(repo, "checkout", "-q", "main")
    _run(repo, "merge", "--no-ff", "-q", "-m", "merge other", "other")

    rows = mac.census(repo)
    assert len(rows) == 1 and rows[0].path == "m.py"
    assert rows[0].choosers == {"helper_the_other_lane_deletes": last_delete}, (
        "the deletion the merge adopts is the one that STANDS; crediting {} would name a choice "
        "this history reversed two commits later".format(first_delete[:9]))
    assert first_delete != last_delete


def test_an_unparseable_row_gets_no_chooser_from_a_live_walk(repo: Path) -> None:
    """A parser error message is not a token of the source, so no commit can carry it and the
    ordinary walk returns nothing. That is a real property, but the first version of this test
    asserted it over a rev range that DOES NOT EXIST -- so the walk was empty and "" came back for
    want of anything to look at. It passed against every mutation, which is how the early return it
    was meant to protect was shown to be an equivalence and deleted.

    The poison round is the second assertion: the SAME base..ref walk finds a real chooser for a
    real symbol, so the "" above is the token being absent and not the history being empty."""
    _run(repo, "branch", "other")
    _commit(repo, "elsewhere.py", "def ours():\n    return 1\n", "this side never opens m.py")
    _run(repo, "checkout", "-q", "other")
    chooser = _commit(repo, "m.py", WITHOUT_HELPER, "the other lane rewrites m.py")
    _run(repo, "checkout", "-q", "main")
    base = _run(repo, "merge-base", "main", "other").strip()

    assert mac.chose_the_deletion(
        repo, base, chooser, "m.py", "m.py: invalid syntax", scr.UNPARSEABLE) == ""
    assert mac.chose_the_deletion(
        repo, base, chooser, "m.py", "helper_the_other_lane_deletes", scr.SUBSET) == chooser, (
        "POISON ROUND: this walk must be capable of returning a sha, or the empty answer above "
        "says nothing about unparseable rows and everything about an empty rev range")


def test_the_census_finds_the_receipt_it_was_built_from() -> None:
    """AGAINST REAL HISTORY, and keyed to immutable commits rather than to today's tree.

    `22df46614` is the merge that had to declare `d3e0e408b`'s deletion of `_staged` as its own.
    Both are ancestors of main and neither can change, so this control cannot rot -- and it goes
    red the moment the census stops finding the one case it was built from."""
    if _run(REPO_ROOT, "rev-parse", "--is-shallow-repository").strip() == "true":
        pytest.skip("shallow clone: the cited commits are not present to census")

    rows = mac.misattributions(REPO_ROOT, "22df46614")
    staged = [r for r in rows
              if r.path == "tests/background/test_the_publish_commit_carries_only_its_own_work.py"]
    assert len(staged) == 1, (
        "the census must find the receipt the finding was written from; if it does not, it is "
        "aimed somewhere other than the defect it claims to measure")
    assert staged[0].rule == scr.SUBSET
    assert list(staged[0].choosers) == ["_staged"]
    chosen = staged[0].choosers["_staged"]
    assert chosen.startswith("d3e0e408b"), (
        "the deletion was chosen by d3e0e408b and declared by 22df46614; naming the merge here "
        "would be the census reproducing the misattribution it exists to expose, got " + chosen)
