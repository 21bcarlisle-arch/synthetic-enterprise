"""The defect: a Lane 0 item names a file list and calls it a pile, and the draw that hands it over
has no opinion about what those bytes actually are.

`land-the-weather-hdd-pile-written-twice-and-committed-never` named ten paths. Five were already on
origin, three were pure reverts of a landed fix, two were another lane's -- wrong in every category
-- and its prescribed remedy (`isolate_hunks` + `surgical_land --content`) separates hunks by AUTHOR
rather than by AGE, so applied as written it would have landed the reverting hunks over the landing
they reverted. The classifier that says so shipped at `028ab23d9` and the draw never asked it.

Each test names the specific way this note could be useless rather than merely exercising it.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from background import delivery_lane as dl


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


#: A landing whose distinctive line appears exactly once, so "contains not one of them" is a
#: statement about THIS commit and not about python in general.
LANDED = (
    "def alpha():\n    return 1\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n"
)

#: The copy taken BEFORE that landing which also carries its own new name. NOT a strict symbol
#: subset, which is why the author-based door passes it and the age-based one does not.
STALE_WITH_OWN_WORK = (
    "def alpha():\n    return 2\n\n\n"
    "def my_own_new_function():\n    return 'mine'\n"
)

#: The same copy WITHOUT any new name: it supplies nothing HEAD lacks, so no door may land it.
STALE_PURE_REVERT = "def alpha():\n    return 1\n"


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A real git repo holding one file of every shape this note has a tag for.

    NOT A FAKE. The subject is git trees and working-tree bytes, and a fake reader here would be
    `a fake more permissive than its subject` -- the shape that turns a fail-open into a green
    suite. `shared_tree_dir` is redirected because that is the seam `path_note` grades through.
    """
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    # UNDER A DIRECTORY, AND NOT AT THE ROOT, because `_NAMED_PATH` requires a `/` and a fixture
    # of bare filenames would grade nothing while every per-path leg below still passed --
    # `_path_verdict` is reachable directly and `path_note` is not. That is precisely the
    # `a control that stubs its own subject proves the stub` shape, and it is what the first draft
    # of this file did.
    (root / "pile").mkdir()
    (root / "pile" / "adir").mkdir()
    for name in ("already.py", "revert.py", "holder.py", "plain.py", "gone.py"):
        (root / "pile" / name).write_text("def alpha():\n    return 1\n")
    (root / "pile" / "adir" / "inner.py").write_text("x = 1\n")
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "base")

    for name in ("revert.py", "holder.py", "plain.py"):
        (root / "pile" / name).write_text(LANDED)
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "another lane lands a helper")

    (root / "pile" / "revert.py").write_text(STALE_PURE_REVERT)
    (root / "pile" / "holder.py").write_text(STALE_WITH_OWN_WORK)
    (root / "pile" / "plain.py").write_text(LANDED + "\n\ndef ordinary_edit():\n    return 3\n")
    (root / "pile" / "untracked.py").write_text("def brand_new():\n    return 4\n")
    (root / "pile" / "gone.py").unlink()

    monkeypatch.setattr(dl.seat_continuation, "shared_tree_dir", lambda *a, **k: root)
    return root


#: Every shape at once, which is how this item's own lesson says to write it: a note that refuses
#: to grade ANYTHING passes a per-tag test suite leg by leg and fails this one.
ALL_SHAPES = {"what": (
    "Land the pile: pile/already.py, pile/revert.py, pile/holder.py, pile/plain.py, "
    "pile/untracked.py, pile/gone.py, pile/adir/inner.py, pile/adir, pile/nope/missing.py -- "
    "run `python3 -m tools.surgical_land` on it."
)}


def test_the_note_reaches_every_verdict_its_own_prose_explains(tree: Path) -> None:
    """THE CONTROL OVER THE WHOLE PARTITION, and the reason it is one assert rather than six.

    Every tag this note prints is a branch taken rarely, and a classifier that returned `dirty` for
    everything -- or `""` for everything -- passes a per-tag test that only ever asks "does it
    refuse correctly". This repo holds one file of each shape simultaneously, so the note must
    distinguish them IN ONE READING or this fails. It is the trap CLAUDE.md records being entered
    three times in one afternoon through three different doors.
    """
    note = dl.path_note(ALL_SHAPES)
    for tag in ("already landed", "predates landing", "holder work", "dirty", "untracked",
                "deleted", "directory"):
        assert "[{}]".format(tag) in note, (
            "the note never reached the `{}` verdict, so that branch is unreachable and every "
            "other leg here is passing on a classifier that cannot classify".format(tag))


def test_each_verdict_lands_on_the_right_file(tree: Path) -> None:
    """A note that reaches every tag but attaches them at random is worse than no note: the reader
    picks a door per path. Pinned to the PROPERTY each file was built to have, not to today's
    wording -- the tag, not the sentence after it."""
    got = {p: dl._path_verdict(tree, p)[0] for p in
           ("pile/already.py", "pile/revert.py", "pile/holder.py", "pile/plain.py",
            "pile/untracked.py", "pile/gone.py", "pile/adir")}
    assert got == {
        "pile/already.py": "already landed",
        "pile/revert.py": "predates landing",
        "pile/holder.py": "holder work",
        "pile/plain.py": "dirty",
        "pile/untracked.py": "untracked",
        "pile/gone.py": "deleted",
        "pile/adir": "directory",
    }, got


def test_a_directory_is_not_reported_as_a_deletion(tree: Path) -> None:
    """THE DEFECT THIS LEG WAS WRITTEN FOR, found by running the note on the live record the first
    time it existed. `blob_at` is `git show HEAD:path`, which SUCCEEDS on a tree and hands back its
    listing, so `is not None` vouched for every directory -- and `is_file()` is False for one. The
    first live run graded `docs/staging`, `docs/staging/done` and `site/data` as
    "tracked at HEAD and NOT on disk -- a deletion", three false alarms in the loudest category
    this note has, on three separate live focus items. The object TYPE is what separates them.
    """
    tag, detail = dl._path_verdict(tree, "pile/adir")
    assert tag == "directory" and "deletion" not in detail, (
        "a directory named in prose was graded `{}` -- a reader told a directory is a deletion "
        "goes looking for work that does not exist".format(tag))


def test_a_dotted_module_name_is_not_read_as_a_path(tree: Path) -> None:
    """Every item on this lane carries `python3 -m tools.surgical_land` in its standing text. A
    reader that took a dotted module as a path would grade this lane's own vocabulary and report
    unresolved rows on every single item, which trains the reader to skip the whole note."""
    note = dl.path_note(ALL_SHAPES)
    assert "tools.surgical_land" not in note, (
        "a dotted module name was matched as a path; the `/` requirement in `_NAMED_PATH` is what "
        "stops it and it has stopped being required")


def test_a_token_that_resolves_to_nothing_is_counted_and_never_dropped_in_silence(
        tree: Path) -> None:
    """`pile/nope/missing.py` is in the prose and is no file. A path-shaped token that names nothing is
    sometimes a RENAMED subject, so dropping it silently is exactly the class this note exists to
    close, one level down: the reader is told the list was graded and never told part of it was
    not."""
    note = dl.path_note(ALL_SHAPES)
    assert "resolve to no file on disk" in note, (
        "an unresolvable token vanished from the note; silence here reads as `all graded`")


def test_the_cap_says_how_much_of_the_pile_it_did_not_grade(
        tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """NO SILENT CAPS. A table that stops at N and says nothing reads as the whole pile, which is
    the same fail-silent shape as the flat phrase this note replaces."""
    monkeypatch.setattr(dl, "_MAX_GRADED_PATHS", 2)
    note = dl.path_note(ALL_SHAPES)
    assert "WERE NOT GRADED" in note and "a sample and not the whole pile" in note, (
        "the note truncated its own table without saying so")


def test_an_item_naming_no_path_gets_no_note(tree: Path) -> None:
    """The note must not fire on the majority of items, which name no file at all. A line printed
    on every item is a line nobody reads by the time it matters."""
    assert dl.path_note({"what": "Settle why the two runs disagree.", "why": "It is the thesis."}) \
        == ""


def test_the_doorbell_actually_carries_it(tree: Path) -> None:
    """THE WIRING, and it is a separate question from the classifier being right. This whole note
    was commissioned because a classifier that WORKED reached no reader for two weeks; a green
    `path_note` with nothing calling it would reproduce that exactly."""
    text = dl.doorbell(dict(ALL_SHAPES, id="an-id", why=""))
    assert "PATH CHECK" in text and "[predates landing]" in text, (
        "`doorbell` composed an item whose named paths include a live revert and said nothing "
        "about it -- which is the state this work was drawn to end")
    assert text.index("PATH CHECK") < text.index("LANE 0 DELIVERY"), (
        "the path check was printed after the work; a check a reader meets after starting is a "
        "check that did not happen")


def test_an_unreadable_tree_costs_the_note_and_never_the_draw(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """FAIL-OPEN, DELIBERATELY, and the same direction as the three sibling notes. A missing
    annotation is visible to the tick that then does the work anyway; an item withheld because git
    hiccuped is visible to nobody. The thing that must NOT happen is `doorbell` raising, because
    then the draw emits nothing and the lane walks over."""
    monkeypatch.setattr(dl.seat_continuation, "shared_tree_dir", lambda *a, **k: tmp_path / "nope")
    assert dl.path_note(ALL_SHAPES) == ""
    assert "LANE 0 DELIVERY" in dl.doorbell(dict(ALL_SHAPES, id="an-id", why=""))


def test_a_classifier_that_cannot_decide_says_so_rather_than_saying_dirty(
        tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`we cannot tell` is a result and belongs on the surface. Collapsing an ungraded path into
    `dirty` is the flattering branch, and `dirty` is the tag that tells a reader to go ahead."""
    def _boom(*a, **k):
        raise RuntimeError("the door fell over")
    from tools import stale_copy_refusal as door
    monkeypatch.setattr(door, "judge", _boom)
    tag, detail = dl._path_verdict(tree, "pile/revert.py")
    assert tag == "ungraded" and "the door fell over" in detail, (
        "a classifier that raised was reported as `{}`; a reader cannot tell a verdict from a "
        "crash".format(tag))
