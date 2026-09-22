"""The defect: the landing door's per-path classifier reaches the worker who DRAWS an item and
never the seat that WRITES it.

`delivery_lane.path_note` landed at `dca82c164` and prints a verdict for every path a Lane 0 item
names. That closes the reader's half. Measured on the four live focus items at 07:40 on 2026-09-22,
every file path the focus list named graded `already landed` -- nothing to land on any of them --
and the list had been authored blind to that, because the orientation never asked. The draw can only
annotate prose that already exists; the focus list is where a spent ask becomes an item.

EVERY TEST HERE NAMES THE SPECIFIC WAY THIS CHECK COULD BE USELESS. The first is the one that
matters: a checker that fires on EVERY item passes any per-class assertion written on its own, so
the partition is asserted in one control before anything is asserted about a leg of it.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from background import direction_path_check as dpc

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
    """A real git repo carrying one file of each state this check distinguishes.

    NOT A FAKE, for `test_the_draw_classifies_the_paths_it_names`'s reason: the subject is
    working-tree bytes against git history, and a fake reader here would be more permissive than
    the thing it stands in for.
    """
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "tools").mkdir()
    (root / "docs").mkdir()
    (root / "docs" / "staging").mkdir()
    for name in ("spent.py", "revert.py", "live.py"):
        (root / "tools" / name).write_text("def alpha():\n    return 1\n")
    (root / "docs" / "staging" / "a_note.md").write_text("a note\n")
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "base")

    for name in ("revert.py", "live.py"):
        (root / "tools" / name).write_text(LANDED)
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "another lane lands a helper")

    # `tools/spent.py` is left identical to HEAD -- nothing to land.
    (root / "tools" / "revert.py").write_text(STALE_PURE_REVERT)
    (root / "tools" / "live.py").write_text(LANDED + "\n\ndef ordinary_edit():\n    return 3\n")
    return root


#: One record holding every shape at once. The ids say what each is FOR, so a failure names the
#: leg rather than an index.
RECORD = {
    "focus": [
        {"id": "spent-ask",
         "what": "Rewrite the reading in `tools/spent.py` so the window is read from the constant.",
         "why": "it is wrong"},
        {"id": "reverting-remedy",
         "what": "Land the pile in `tools/revert.py` with `tools/isolate_hunks.py` then "
                 "`surgical_land --content`.",
         "why": "the work is finished and uncommitted"},
        {"id": "real-work",
         "what": "Rewrite the reading in `tools/live.py`.",
         "why": "it is wrong"},
        {"id": "directory-subject",
         "what": "Rewrite the reading in `tools/spent.py`, then commit the archival under "
                 "`docs/staging/` in batches by pathspec.",
         "why": "the census is fiction"},
    ],
}


def test_the_check_separates_the_partition_rather_than_firing_on_everything(tree: Path) -> None:
    """THE CONTROL OVER THE WHOLE PARTITION, and it is first on purpose.

    A checker that returns a concern for every item satisfies every per-class assertion below on
    its own, and one that returns none satisfies the `real-work` leg. Both are asserted here in
    one place, over one record carrying all four shapes, so neither degenerate checker can pass.
    """
    by_id: dict[str, set[str]] = {}
    for row in dpc.concerns(RECORD, tree):
        by_id.setdefault(row["id"], set()).add(row["class"])

    assert by_id.get("spent-ask") == {dpc.NOTHING_TO_LAND}
    assert dpc.REVERTING_REMEDY in by_id.get("reverting-remedy", set())
    assert "real-work" not in by_id, (
        "an item whose change path has real uncommitted work drew a concern -- this check fires "
        "on everything and tells the authoring seat nothing")
    assert by_id.get("directory-subject") == {dpc.NOTHING_TO_LAND}


def test_a_path_named_only_to_read_is_not_a_spent_ask(tree: Path) -> None:
    """The defect: grading the union of the roles. `already landed` is the ordinary state of a
    file, so an item read-only-naming a landed path would be reported spent on the strength of a
    path it never asked to change -- and a note that fires on nearly every item is read by nobody.

    BOTH FIXTURES ARE HERE BECAUSE ONE OF THEM DOES NOT DISCRIMINATE, and that was established by
    mutation rather than assumed. The first draft used only the mixed sentence below: under the
    union reading its change set becomes {live, spent}, which is not all-spent, so no concern
    fires EITHER WAY and the mutation was silent. The union's actual reachable error is an item
    with NO change path at all -- every path it names is one it only reads -- where the correct
    reading has nothing to grade and the union reports the ask spent. That is the first case.
    """
    reads_only = {"focus": [{
        "id": "reads-a-landed-constant",
        "what": "Read the window from the constant declared in `tools/spent.py`.",
        "why": "it is wrong"}]}
    assert dpc.concerns(reads_only, tree) == [], (
        "an item that only READS a landed path was reported as having nothing to land -- which is "
        "the ordinary state of every committed file in the tree, so this would fire on nearly "
        "every item ever written")

    mixed = {"focus": [{
        "id": "changes-one-reads-another",
        "what": "Rewrite the reading in `tools/live.py`, from the constant declared in "
                "`tools/spent.py`.",
        "why": "it is wrong"}]}
    assert dpc.concerns(mixed, tree) == []


def test_the_spent_concern_carries_the_directory_count_that_would_overturn_it(tree: Path) -> None:
    """The defect: publishing `every path is landed` as a verdict that the ask is spent.

    `docs/staging/` is a directory, git tracks no directories, so an item whose real subject is a
    tree full of deletions can never have that subject reach the role split at all. The live
    staging-archival item is exactly this shape. The count travels with the concern; without it
    the sentence is a measurement wearing a verdict's clothes.
    """
    rows = [r for r in dpc.concerns(RECORD, tree) if r["id"] == "directory-subject"]
    assert len(rows) == 1
    assert "1 bare directory token(s)" in rows[0]["says"]

    plain = [r for r in dpc.concerns(RECORD, tree) if r["id"] == "spent-ask"]
    assert "0 bare directory token(s)" in plain[0]["says"], (
        "the count is not read from the item at all -- it would say the same thing about an item "
        "that named no directory, and could not distinguish the two cases it exists to separate")


def test_the_reverting_remedy_needs_both_legs(tree: Path) -> None:
    """The defect: reporting every stale copy, or reporting the remedy vocabulary alone.

    `predates landing` on its own is often the right work -- restoring that very revert was focus
    item 1 on the record that commissioned this. The dangerous shape is the stale path AND a
    prose remedy that lands hunks by author, which is what `isolate_hunks`/`--content` do.
    """
    stale_only = {"focus": [{"id": "x", "what": "Restore `tools/revert.py` from HEAD.",
                             "why": "it reverts a landing"}]}
    classes = {r["class"] for r in dpc.concerns(stale_only, tree)}
    assert dpc.REVERTING_REMEDY not in classes

    remedy_only = {"focus": [{
        "id": "y",
        "what": "Land `tools/live.py` with `tools/isolate_hunks.py` and `surgical_land --content`.",
        "why": "it is finished"}]}
    classes = {r["class"] for r in dpc.concerns(remedy_only, tree)}
    assert dpc.REVERTING_REMEDY not in classes


def test_an_unreadable_tree_yields_no_concerns_rather_than_a_raise(tmp_path: Path) -> None:
    """The defect: a check that wedges the orientation. Direction is advice; `background/
    direction.py`'s whole fail-soft argument is that advice which stops the draw when git hiccups
    is worse than no advice. A directory that is not a git repo is the cheapest real instance."""
    assert dpc.concerns(RECORD, tmp_path) == []
    assert dpc.note(RECORD, tmp_path) == ""


def test_the_note_is_empty_when_there_is_nothing_to_say(tree: Path) -> None:
    """The defect: a block that prints `no concerns` into a prompt already at its truncation
    limit, every stretch, until the reader skips the block on the stretch it says something."""
    clean = {"focus": [{"id": "real-work", "what": "Rewrite the reading in `tools/live.py`.",
                        "why": "it is wrong"}]}
    assert dpc.note(clean, tree) == ""
    assert "nothing to land" in dpc.note(RECORD, tree)


def test_the_orientation_brief_carries_the_verdicts_into_the_prompt(monkeypatch) -> None:
    """The defect this whole module exists for, asserted at the seam rather than in the unit: the
    verdicts exist and never reach the seat that writes the next record. A key in the brief that
    `_prompt` does not render is the same as the check not existing."""
    from background import delivery_seat

    rendered = delivery_seat._prompt({
        "live_direction_path_concerns": [
            {"id": "spent-ask", "class": dpc.NOTHING_TO_LAND, "paths": ["tools/spent.py"],
             "says": "a distinctive sentence about tools/spent.py"}],
        "shape": {"available": True, "rendered": ""},
        "divergence": {"says": ""},
    })
    assert "a distinctive sentence about tools/spent.py" in rendered
    assert "background.direction_path_check" in rendered, (
        "the seat is shown the verdicts and not the command that re-runs them against a draft, "
        "so it can read the last record's grades and never grade the one it is writing")
