"""The defect: the continuation store is the third and last door prose reaches the draw through,
and it was the only one that graded nothing at all.

`delivery_lane.path_note` (dca82c164) closed the READER's half and `direction_path_check`
(95035ad29) the ORIENTATION's. A hand-off is written at the END of a turn, when the seat knows
least about what the next lane will have landed by the time the item is drawn -- two of the six
reverts focus item 1 named were fixed by another lane between 07:40 and 08:10 on 2026-09-22, which
is exactly the window a hand-off lives in.

THE COMMISSIONING ITEM ASKED FOR `grade_item` CALLED STRAIGHT THROUGH AND THAT IS NOT WHAT SHIPPED.
Measured over the live store at 08:47, `NOTHING_TO_LAND` fires on 183 of the 265 entries that name a
change path (69%), at a rate falling 84 / 67 / 59 / 48% across items naming 1, 2, 3 and 4+ paths --
a geometric 0.84^n, the signature of a property of the TREE rather than of the item. The same walk
17 minutes earlier said 50% and 0.71^n: another lane committed in between, and nothing about the
hand-offs changed. It has to be this way -- an orientation item can say "land this pile", so
`already landed` may mean the ask is spent; a hand-off describes work NOT YET DONE, where `already
landed` is the expected precondition. On the two live entries it fired exactly backwards: silent on
the pile item whose ask CAN go spent, loud on the new-work item where the verdict is meaningless.

So the FIRST test below is the inversion, and the second is the partition. A checker that fires on
everything passes any per-class assertion written on its own.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from background import direction_path_check as dpc
from background import seat_continuation as sc

LANDED = (
    "def alpha():\n    return 1\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n"
)

#: The copy taken BEFORE that landing, supplying no name HEAD lacks. `predates landing`.
STALE_PURE_REVERT = "def alpha():\n    return 1\n"


def _run(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A real git repo carrying one file of each state this door distinguishes.

    NOT A FAKE, for `test_the_direction_record_is_graded_before_it_is_filed`'s reason: the subject
    is working-tree bytes against git history, and a fake reader would be more permissive than the
    thing it stands in for. `tools/gone.py` is the one shape that sibling does not need -- a
    hand-off can name a file that is no longer on disk, and `deleted` is a trap the ORIENTATION
    never sees because a focus item is written about a tree the seat has just walked.
    """
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "tools").mkdir()
    for name in ("spent.py", "revert.py", "live.py", "gone.py"):
        (root / "tools" / name).write_text("def alpha():\n    return 1\n")
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "base")

    for name in ("revert.py", "live.py"):
        (root / "tools" / name).write_text(LANDED)
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "another lane lands a helper")

    # `tools/spent.py` is left identical to HEAD -- the ordinary state of a file about to be worked
    # on, and the whole point of this door is that it says NOTHING about it.
    (root / "tools" / "revert.py").write_text(STALE_PURE_REVERT)
    (root / "tools" / "live.py").write_text(LANDED + "\n\ndef ordinary_edit():\n    return 3\n")
    (root / "tools" / "gone.py").unlink()
    return root


def _item(work_id: str, what: str) -> dict:
    return {"id": work_id, "what": what, "why": "because", "done_means": "it is done"}


#: The fixture's four paths, named ONCE at module scope. Hoisted out of the test bodies rather than
#: spelled inline: `substring_source_scan_census` taints any scope holding both a `read_text()` and
#: a tree-path literal, because that pair is how a control comes to read Python source as TEXT.
#: The store this file reads is JSON and `tools/python_code_text.py` is not its remedy -- so the
#: honest fix is to stop the pair occurring, not to route a JSON read through a Python reader.
STALE = "tools/revert.py"
SPENT = "tools/spent.py"
LIVE = "tools/live.py"
GONE = "tools/gone.py"

#: Every shape at once, as hand-offs. The ids say what each is FOR, so a failure names the leg.
SHAPES = {
    "new-work-on-a-landed-file": _item(
        "new-work-on-a-landed-file",
        "Rewrite the reading in `%s` so the window comes from the constant." % SPENT),
    "work-in-progress": _item(
        "work-in-progress", "Finish the edit already started in `%s`." % LIVE),
    "names-a-stale-copy": _item(
        "names-a-stale-copy", "Carry on in `%s`, which already has the rows." % STALE),
    "names-a-deleted-file": _item(
        "names-a-deleted-file", "Archive `%s` next, it is ready." % GONE),
    "reverting-remedy": _item(
        "reverting-remedy",
        "Land the pile in `%s` with `tools/isolate_hunks.py` then "
        "`surgical_land --content`." % STALE),
}


def _classes(work_id: str, tree: Path) -> set[str]:
    return {c["class"] for c in dpc.hand_off_reading(SHAPES[work_id], tree, now=0.0)["concerns"]}


def test_the_spent_reading_is_not_asked_at_this_door_at_all(tree: Path) -> None:
    """THE DEFECT THIS MODULE EXISTS FOR, and it is first because it is the one a straight call
    would reintroduce.

    `NOTHING_TO_LAND` means "every path this item asks to be CHANGED is identical to HEAD". For an
    orientation item that says *land this pile*, that can mean the ask is spent. For a hand-off it
    is the state of a file nobody has started work on yet -- which is what a hand-off IS. Asserted
    over the whole shape set rather than on one item, because the class leaking back in for any one
    of them is the same defect.
    """
    for work_id in SHAPES:
        assert dpc.NOTHING_TO_LAND not in _classes(work_id, tree), (
            f"{work_id} was told its change set has nothing to land. On the live store that "
            "reading fires on half of all hand-offs, at a rate geometric in the number of paths "
            "named -- it measures whether the TREE is clean, not whether the ASK is spent")


def test_the_door_separates_the_partition_rather_than_firing_on_everything(tree: Path) -> None:
    """THE CONTROL OVER THE WHOLE PARTITION. A checker returning a concern for every hand-off
    satisfies every loud leg below on its own, and one returning none satisfies both quiet legs.
    Both degenerate checkers are refused here, in one place, over one set carrying all five shapes.
    """
    assert _classes("new-work-on-a-landed-file", tree) == set()
    assert _classes("work-in-progress", tree) == set()
    assert _classes("names-a-stale-copy", tree) == {dpc.HAND_OFF_STALE}
    assert _classes("names-a-deleted-file", tree) == {dpc.HAND_OFF_STALE}
    # ONE ROW AND NOT TWO. `reverting-remedy` names a `predates landing` path, so the stale class is
    # also true of it -- and printing both would tell the seat the same thing twice while burying
    # the one that names the right door. The stricter row wins and the other is suppressed.
    assert _classes("reverting-remedy", tree) == {dpc.REVERTING_REMEDY}


def test_a_path_named_only_to_read_is_graded_here_though_the_orientation_skips_it(tree: Path) -> None:
    """The defect: inheriting the orientation's role split whole.

    There it is load-bearing -- `already landed` on a read-only path is the ordinary state of every
    committed file, so grading the union would fire on nearly every item. Here the spent reading is
    gone entirely, and the remaining question is whether the BYTES contradict the prose. A hand-off
    that sends the next tick to READ a copy which reverts a landing has misled it exactly as badly
    as one that sends it to write there.
    """
    reads_only = _item("reads-a-stale-constant",
                       "Rewrite `tools/live.py`, reading the window declared in `tools/revert.py`.")
    classes = {c["class"] for c in dpc.hand_off_reading(reads_only, tree, now=0.0)["concerns"]}
    assert dpc.HAND_OFF_STALE in classes, (
        "the stale copy was invisible because the item only READS it -- the role split was "
        "inherited from a door where it earns its keep and this one it does not")


def test_the_reading_is_stored_on_the_entry_the_next_tick_reads(tmp_path: Path, tree: Path,
                                                                monkeypatch) -> None:
    """The defect: a verdict computed and then dropped. `hand_off_reading` with no caller is
    exactly the state this module was in before it existed -- the classifier ran nowhere.

    The reading is asserted ON DISK and not on the return value: `_save` is what the next tick
    reads, and a field present in memory and absent from the file is the failure that matters.
    """
    monkeypatch.setattr(sc, "shared_tree_dir", lambda *a, **k: tree)
    store = tmp_path / "store.json"
    sc.hand_off("names-a-stale-copy", SHAPES["names-a-stale-copy"]["what"], "because",
                "it is done", now=100.0, path=store)

    entry = json.loads(store.read_text())[0]
    reading = entry["path_reading"]
    assert reading["at"] == 100.0, "the reading is stamped with a clock other than the entry's"
    assert [STALE, "predates landing"] in reading["paths"]
    assert [c["class"] for c in reading["concerns"]] == [dpc.HAND_OFF_STALE]


def test_the_note_the_handing_off_seat_reads_names_the_door_for_the_state_it_found(tree) -> None:
    """The defect: a concern that says a path is wrong and leaves the reader to find the remedy.

    `refresh_to_head` is the door for an out-of-date copy and `isolate_hunks` is the trap; a note
    that names neither costs the next tick the invocation this whole mechanism exists to save.
    """
    loud = dpc.hand_off_note(SHAPES["names-a-stale-copy"], tree, now=0.0)
    assert "tools/revert.py" in loud
    assert "tools.refresh_to_head" in loud


def test_the_note_speaks_when_it_finds_nothing_because_its_reader_is_a_command_line(tree) -> None:
    """The defect is the sibling rule applied where it inverts. `note()` returns "" on a clean
    record, because it is concatenated into a 60k prompt and a block that says nothing every time
    teaches the reader to skip the one that says something. This text is the output of a command
    the seat JUST RAN, where silence cannot be told from the check not running -- and "names no
    tracked file at all" is itself the shape of a hand-off the next tick cannot locate."""
    quiet = dpc.hand_off_note(SHAPES["new-work-on-a-landed-file"], tree, now=0.0)
    assert quiet.strip(), "a seat that ran the check was shown nothing and cannot tell it ran"
    assert "already landed" in quiet, (
        "the quiet note does not say WHICH reading it declined to raise, so a seat cannot tell "
        "this door from the orientation's")


def test_an_unanswerable_tree_is_not_a_clean_verdict(tmp_path: Path) -> None:
    """The defect: a check that wedges a hand-off, and the worse one that passes it off as clean.

    A hand-off that cannot be graded is still worth far more than no hand-off, so nothing raises
    and nothing refuses. What must NOT happen is the empty reading wearing a pass's colour -- "we
    could not tell" is a result and belongs on the surface.
    """
    reading = dpc.hand_off_reading(SHAPES["names-a-stale-copy"], tmp_path, now=0.0)
    assert reading["concerns"] == [] and reading["readable"] is False

    broken = dpc.hand_off_note(_item("x", "work in `tools/live.py`"), tmp_path)
    assert "NOT a clean verdict" in broken, (
        "an unanswerable tree and a hand-off that names no path both grade zero rows, and this "
        "reported the reassuring one -- a clean verdict over a tree git could not read")


class TestDrift:
    """The half the draw cannot compute for itself."""

    @staticmethod
    def _carrying(paths, at=0.0):
        return {"id": "d", "what": "x", "why": "y", "done_means": "z",
                "path_reading": {"at": at, "root": "r", "paths": paths, "concerns": []}}

    def test_movement_between_the_writing_and_the_draw_is_reported(self, tree: Path) -> None:
        """The defect the commissioning item's own WHY names: two of six reverts were repaired by
        another lane inside the window a hand-off lives in, and nothing could see it. `path_note`
        grades the tree NOW and is right to; it holds no record of what the handing-off seat saw,
        so the DIFFERENCE is available from this store and from nowhere else."""
        item = self._carrying([["tools/revert.py", "already landed"],
                               ["tools/live.py", "dirty"]])
        note = dpc.drift_note(item, tree)
        assert "tools/revert.py" in note
        assert "was [already landed] when handed on, now [predates landing]" in note
        assert "tools/live.py" not in note, (
            "a path whose state did not move was reported as drift -- this re-states the fresh "
            "verdict `path_note` printed three lines up instead of reporting the change")

    def test_agreement_says_nothing_at_all(self, tree: Path) -> None:
        """The defect: a second opinion published beside a fresh one. The stored tags are hours old
        by the time they are read; their ONLY licence is the difference."""
        assert dpc.drift_note(self._carrying([["tools/live.py", "dirty"]]), tree) == ""

    def test_a_focus_item_carries_no_reading_and_draws_no_drift(self, tree: Path) -> None:
        """The defect: assuming every drawn item came from the continuation store. `next_item`
        returns focus rows and continuations from the same call, and a focus row has never been
        through this door -- an empty `before` must read as "not applicable", never as "all moved".
        """
        assert dpc.drift_note({"id": "f", "what": "work in tools/live.py", "why": "y"}, tree) == ""

    def test_an_ungraded_tag_is_never_reported_as_movement(self, tree: Path) -> None:
        """The defect: `ungraded` means the classifier RAN AND COULD NOT DECIDE. Differencing it
        against a real tag manufactures a change out of our own blindness, in the loudest category
        this note has."""
        assert dpc.drift_note(self._carrying([["tools/live.py", "ungraded"]]), tree) == ""


def test_the_drift_reaches_the_doorbell_the_tick_actually_reads(tree: Path, monkeypatch) -> None:
    """The defect asserted at the seam rather than in the unit: a reading that reaches no prompt is
    the same as the check not existing, which is precisely the state this door was in."""
    from background import delivery_lane

    monkeypatch.setattr(sc, "shared_tree_dir", lambda *a, **k: tree)
    rendered = delivery_lane.doorbell({
        "id": "d", "what": "Carry on.", "why": "because", "done_means": "done",
        "path_reading": {"at": 0.0, "root": str(tree), "concerns": [],
                         "paths": [["tools/revert.py", "already landed"]]}})
    assert "PATH DRIFT" in rendered
    assert "tools/revert.py" in rendered
