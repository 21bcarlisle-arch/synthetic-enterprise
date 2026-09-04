"""THE DEFECT: a pathspec stages the WORKING-TREE copy, so another lane's in-place edits ride in.

`CLAUDE.md`'s "commit by pathspec, never -A" protects against sweeping other FILES. It does nothing
about a file another lane has edited in place. On 2026-09-04 that landed another lane's unfinished
key rename inside two of this seat's commits, cost two full gate cycles, and then several hours of
waiting for the other lane to finish -- when `surgical_land --content` had been the door all along
and only the bytes were missing.

Every leg here is about the ONE direction that cannot be undone by the gate: keeping a hunk that is
not yours puts another lane's half-finished work in the record under your name, and nothing
downstream can tell. Forgetting one of your own is caught by your own tests. So the selection is
default-deny and the refusals are loud, and that asymmetry is what these legs check.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import isolate_hunks as ih

_BASE = [f"line {i}\n" for i in range(1, 41)]


def _work(edits: dict[int, str]) -> list[str]:
    out = list(_BASE)
    for idx, text in edits.items():
        out[idx] = text
    return out


def _split(base, work):
    ops, groups = ih.group_opcodes(base, work)
    return ops, groups


def test_two_edits_far_apart_are_two_separately_selectable_hunks():
    """The whole mechanism rests on this: if a foreign edit and mine collapse into one hunk there
    is no selection that separates them. MUTATION: raise the context to swallow the gap and this
    fires."""
    work = _work({2: "MINE\n", 30: "THEIRS\n"})
    _ops, groups = _split(_BASE, work)
    assert len(groups) == 2


def test_keeping_mine_leaves_theirs_exactly_as_head_had_it():
    """THE DEFECT ITSELF. MUTATION: take `work` for an unkept hunk and this fires -- the foreign
    line appears in bytes that are about to be committed under your name."""
    work = _work({2: "MINE\n", 30: "THEIRS\n"})
    ops, groups = _split(_BASE, work)
    out = ih.reconstruct(_BASE, work, ops, groups, keep={0})
    assert "MINE\n" in out
    assert "THEIRS\n" not in out, "another lane's edit rode into the reconstruction"
    assert out[30] == _BASE[30]


def test_keeping_every_hunk_reproduces_the_working_copy_exactly():
    """SOUNDNESS, and it is checked at every live run too, not only here. If all-in is not the
    working copy the reconstruction is wrong somewhere, and every partial selection is wrong in a
    way that would land silently."""
    work = _work({2: "MINE\n", 30: "THEIRS\n", 31: "THEIRS TOO\n"})
    ops, groups = _split(_BASE, work)
    assert ih.reconstruct(_BASE, work, ops, groups, set(range(len(groups)))) == work


def test_keeping_no_hunk_reproduces_head_exactly():
    """The other end of the same invariant."""
    work = _work({2: "MINE\n", 30: "THEIRS\n"})
    ops, groups = _split(_BASE, work)
    assert ih.reconstruct(_BASE, work, ops, groups, set()) == _BASE


def test_an_inserted_hunk_and_a_deleted_hunk_are_both_isolatable():
    """Replacements are the easy case. A pure insert has no base lines and a pure delete has no
    work lines, and an off-by-one in either direction silently drops or duplicates a line."""
    work = list(_BASE)
    work[5:5] = ["INSERTED\n"]          # pure insert
    del work[31]                        # pure delete, far enough away to be its own hunk
    ops, groups = _split(_BASE, work)
    assert len(groups) == 2
    only_insert = ih.reconstruct(_BASE, work, ops, groups, keep={0})
    assert "INSERTED\n" in only_insert
    assert len(only_insert) == len(_BASE) + 1, "the delete leaked into an insert-only selection"
    only_delete = ih.reconstruct(_BASE, work, ops, groups, keep={1})
    assert "INSERTED\n" not in only_delete
    assert len(only_delete) == len(_BASE) - 1


# ── the refusals, which are the safety argument ─────────────────────────────────────────────────

def _repo_file(tmp_path: Path, base: str, work: str) -> tuple[Path, str]:
    """A real one-file git repo, because the base comes from `git show HEAD:` and a fake would test
    the fake."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "f.py").write_text(base)
    subprocess.run(["git", "add", "f.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base", "--no-gpg-sign"], cwd=tmp_path, check=True)
    (tmp_path / "f.py").write_text(work)
    return tmp_path, "f.py"


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    base = "".join(_BASE)
    work = "".join(_work({2: "MINE marker\n", 30: "THEIRS marker\n"}))
    root, _ = _repo_file(tmp_path, base, work)
    monkeypatch.setattr(ih, "_REPO", root)
    return root


def test_nothing_is_kept_unless_it_is_named(repo, tmp_path):
    """DEFAULT-DENY. MUTATION: default to keeping everything -- the convenient default -- and this
    fires. Convenience in this direction is exactly the defect: an unreviewed hunk lands."""
    with pytest.raises(SystemExit) as e:
        ih.build("f.py", [], tmp_path / "out.py")
    assert "no hunk selected" in str(e.value)


def test_a_selector_that_matches_nothing_refuses_rather_than_keeping_nothing(repo, tmp_path):
    """A typo'd regex silently selecting nothing produces HEAD's own bytes and a green gate: an
    empty change that reports as a landed one. MUTATION: return an empty set instead of raising."""
    with pytest.raises(SystemExit) as e:
        ih.build("f.py", ["/no-such-line/"], tmp_path / "out.py")
    assert "matched no hunk" in str(e.value)


def test_a_file_not_in_head_is_refused_with_its_reason(tmp_path, monkeypatch):
    """A wholly new file cannot be contested and has no base to isolate against. Refusing beats
    inventing an empty base, which would 'keep' the entire file as one hunk."""
    root, _ = _repo_file(tmp_path, "x\n", "y\n")
    monkeypatch.setattr(ih, "_REPO", root)
    with pytest.raises(SystemExit) as e:
        ih.head_lines("never_committed.py")
    assert "not in HEAD" in str(e.value)


def test_the_selection_can_be_made_by_regex_as_well_as_by_number(repo, tmp_path, capsys):
    """Hunk numbers move when the other lane edits again; a regex on your own line does not."""
    out = tmp_path / "out.py"
    ih.build("f.py", ["/MINE marker/"], out)
    text = out.read_text()
    assert "MINE marker" in text and "THEIRS marker" not in text


def test_every_disposition_is_reachable_and_each_is_reported(repo, tmp_path, capsys):
    """THE REACHABILITY LEG, and the rule this repo paid for three times in one afternoon: when a
    branch exists to be taken rarely, assert it CAN be taken before asserting what it does.

    Here the three are KEPT, dropped and refused. A build that could only ever keep everything, or
    only ever refuse, passes every other leg above -- and a dropped hunk that is never PRINTED is
    the same defect one step later, because "I landed only mine" then rests on nobody's reading.
    """
    out = tmp_path / "out.py"
    ih.build("f.py", ["1"], out)
    printed = capsys.readouterr().out
    assert "KEPT" in printed and "dropped" in printed
    assert "MINE marker" in printed and "THEIRS marker" in printed, (
        "a dropped hunk was not named, so nothing tells the reader what was left behind"
    )
    with pytest.raises(SystemExit):
        ih.build("f.py", [], out)


def test_the_survey_names_the_hunks_without_writing_anything(repo, capsys):
    """The two-second answer to "why did the gate refuse". Costing a second twenty-minute gate
    cycle to find out is what this exists to stop, and I paid that twice before writing it."""
    assert ih.survey("f.py") == 0
    printed = capsys.readouterr().out
    assert "2 hunk(s)" in printed
    assert "MINE marker" in printed and "THEIRS marker" in printed


def test_the_working_tree_is_never_written(repo, tmp_path):
    """The difference between this and `git checkout <path>`, which is forbidden here precisely
    because it DISCARDS the other lane's work. Theirs must be exactly as they left it."""
    before = (repo / "f.py").read_bytes()
    ih.build("f.py", ["1"], tmp_path / "out.py")
    ih.survey("f.py")
    assert (repo / "f.py").read_bytes() == before


# ── the pointer, which is what makes it a mechanism rather than a tool ───────────────────────────

def test_a_refusal_names_the_contested_path_and_the_route(repo, capsys):
    """THE REASON THIS IS WIRED INTO surgical_land AT ALL. `--content` existed for weeks and was
    not taken, because a refusal on another lane's in-place edit is indistinguishable from a
    refusal on your own bug. The seat waited hours for the other lane instead.

    A moved-out procedure nobody points at is a procedure nobody runs, so the pointer fires at the
    moment of the refusal. MUTATION: drop the call from the LandingRefused branch and this fires.
    """
    import io

    from tools import surgical_land

    out = io.StringIO()
    named = surgical_land.name_the_contested_paths(["f.py"], supplied=None, root=repo, out=out)
    assert named == ["f.py"]
    assert "2 separate hunks" in out.getvalue()
    assert "isolate_hunks --survey f.py" in out.getvalue()


def test_a_path_whose_bytes_were_supplied_is_not_named(repo):
    """A path landed via --content is not contested BY CONSTRUCTION -- the working-tree copy was
    never read. Naming it would send the reader back round a loop they have already closed."""
    import io

    from tools import surgical_land

    out = io.StringIO()
    named = surgical_land.name_the_contested_paths(
        ["f.py"], supplied={"f.py": b"x"}, root=repo, out=out)
    assert named == [] and out.getvalue() == ""


def test_the_pointer_never_raises_over_a_path_it_cannot_read(repo):
    """A diagnostic that can raise turns a refusal carrying its reason into a traceback carrying
    none. MUTATION: remove the except and this fires on the missing path."""
    import io

    from tools import surgical_land

    out = io.StringIO()
    assert surgical_land.name_the_contested_paths(
        ["no_such_file.py", "f.py"], root=repo, out=out) == ["f.py"]
