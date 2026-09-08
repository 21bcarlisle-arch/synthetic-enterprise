"""The substring-scan census is able to fire, and the floor it holds is the real tree's.

WHAT THIS GUARDS. `tools/python_code_text.py` is the remedy for a control that reads Python source
as TEXT; nothing made a new control use it. Ten instances were fixed one at a time across three
sweeps, and the eleventh would have passed every gate in this repository.

THE POISON ROUND COMES FIRST, and the order is the whole point. "The floor holds" means two
opposite things -- the tree grew no new substring scan, or the detector cannot see one -- and a
census whose taint rule has gone blind reports a clean tree while every mutation of it survives.
So the first test plants a tree containing each shape and asserts each is SEEN, before any test
asserts the real tree is clean. `tools/launch_shape_census.py` is the precedent and the reason:
the same ordering caught its detector reporting 20 where the hand pass found 8.

ONE CONTROL OVER THE PARTITION, not a leg per shape. A detector that fires on everything passes
every "does it see this one" leg, so the poison round asserts the found set EQUALS the planted
members -- the four clean shapes beside them are half of that single assertion, not a separate
courtesy.

WHY THE FLOOR IS 117 AND NOT 0. Three hand passes over this same class converged on nine members
and called the population closed. The census returns 117 scan sites in `tests/` alone. They are
not 117 defects -- most are a test reading one named module for one token, where the prose hazard
is small -- but the number is the finding: the population was never enumerable by hand, and every
attempt to enumerate it exhibited the class. The floor freezes what exists so the 118th is
refused, and shrinks as rows are routed through the remedy.
"""
from __future__ import annotations

import functools
from pathlib import Path

from tools import substring_source_scan_census as census

REPO = Path(__file__).resolve().parents[2]


@functools.lru_cache(maxsize=1)
def _real_tree() -> tuple:
    """The real tree's census, walked ONCE per session and shared by the floor tests."""
    return tuple(census.census(REPO))


def _poison_tree(tmp_path: Path) -> Path:
    """A tree holding each member shape, and each shape the census must NOT flag.

    Every file is written as real source and parsed by the real detector; a fixture that handed
    the census a list of pre-classified scans would leave the classification -- the part that can
    silently return nothing -- untested.
    """
    # The package directories are REAL, because the census derives "is this literal a tree path"
    # from the tree's own top-level directories rather than from a typed list. A fixture with only
    # `tests/` in it would leave that derivation untested and the bare-literal member unseen --
    # which is exactly how this fixture failed on its first run.
    for package in ("tests", "saas", "background", "tools", "simulation"):
        (tmp_path / package).mkdir()
    root = "from pathlib import Path\nR = Path(__file__).resolve().parents[2]\n"

    # MEMBERS.
    (tmp_path / "tests" / "test_named_py.py").write_text(
        root + 'def test_a():\n'
        '    src = (R / "background" / "worker.py").read_text()\n'
        '    assert "os.kill(" not in src\n', encoding="utf-8")
    (tmp_path / "tests" / "test_unfiltered_walk.py").write_text(
        root + 'def test_b():\n'
        '    for p in R.rglob("*"):\n'
        '        assert "pgrep" not in p.read_text()\n', encoding="utf-8")
    (tmp_path / "tests" / "test_regex_over_source.py").write_text(
        root + "import re\n"
        'def test_c():\n'
        '    text = (R / "tools" / "thing.py").read_text()\n'
        '    assert not re.search(r"sleep", text)\n', encoding="utf-8")
    (tmp_path / "tests" / "test_taint_through_a_join.py").write_text(
        root + 'def test_d():\n'
        '    parts = [p.read_text() for p in R.glob("saas/*.py")]\n'
        '    blob = "\\n".join(parts)\n'
        '    assert "TODO" not in blob\n', encoding="utf-8")
    (tmp_path / "tests" / "test_bare_package_literal.py").write_text(
        "import pathlib\n"
        'def test_e():\n'
        '    src = pathlib.Path("saas/twin.py").read_text()\n'
        '    assert "import simulation" not in src\n', encoding="utf-8")

    # NOT MEMBERS, and each is a different reason.
    (tmp_path / "tests" / "test_routed.py").write_text(
        root + "from tools.python_code_text import searchable\n"
        'def test_f():\n'
        '    code = searchable((R / "background" / "worker.py").read_text())\n'
        '    assert "os.kill(" not in code\n', encoding="utf-8")
    (tmp_path / "tests" / "test_markdown_only.py").write_text(
        root + 'def test_g():\n'
        '    for p in R.rglob("*.md"):\n'
        '        assert "TODO" not in p.read_text()\n', encoding="utf-8")
    (tmp_path / "tests" / "test_own_fixture.py").write_text(
        "def test_h(tmp_path):\n"
        '    f = tmp_path / "planted.py"\n'
        '    f.write_text("import os\\n")\n'
        '    assert "import os" in f.read_text()\n', encoding="utf-8")
    (tmp_path / "tests" / "test_reads_but_never_matches.py").write_text(
        root + 'def test_i():\n'
        '    src = (R / "tools" / "thing.py").read_text()\n'
        '    assert len(src) > 10\n', encoding="utf-8")
    return tmp_path


def _found(tmp_path: Path) -> set[str]:
    tree = _poison_tree(tmp_path)
    paths = sorted((tree / "tests").glob("*.py"))
    return {Path(s.path).name for s in census.census(tree, paths)}


def test_the_poison_tree_fires_every_member_shape_and_no_other(tmp_path):
    """One assertion over the whole partition: a detector that fires on everything, or on
    nothing, fails here rather than passing five separate quiet-on-clean legs."""
    assert _found(tmp_path) == {
        "test_named_py.py",
        "test_unfiltered_walk.py",
        "test_regex_over_source.py",
        "test_taint_through_a_join.py",
        "test_bare_package_literal.py",
    }


def test_a_scan_is_attributed_to_the_TEST_and_not_to_the_FILE(tmp_path):
    """The defect the second hand pass shipped: a file-level verdict is blind to WHICH test in it
    scans. A file with one scanning test and one innocent test must yield exactly one row, named
    for the scanning one."""
    tree = _poison_tree(tmp_path)
    mixed = tree / "tests" / "test_mixed.py"
    mixed.write_text(
        "from pathlib import Path\n"
        "R = Path(__file__).resolve().parents[2]\n"
        "def test_innocent():\n"
        "    assert 1 == 1\n"
        "def test_the_scanner():\n"
        '    assert "x" not in (R / "tools" / "thing.py").read_text()\n', encoding="utf-8")
    rows = [s for s in census.census(tree, [mixed])]
    assert [s.function for s in rows] == ["test_the_scanner"]


def test_source_that_will_not_parse_is_REPORTED_and_not_skipped(tmp_path):
    """Fail-closed. A file the census could not read is not evidence that it holds no scan, and a
    census that skips what it cannot parse goes quiet exactly where a reader most needs it loud."""
    tree = _poison_tree(tmp_path)
    broken = tree / "tests" / "test_broken.py"
    broken.write_text("def f(:\n", encoding="utf-8")
    rows = census.census(tree, [broken])
    assert [s.evidence for s in rows] == [("UNPARSEABLE",)]


def test_the_taint_answer_does_not_depend_on_STATEMENT_ORDER(tmp_path):
    """The census's own first draft lost this, and the member it lost was one found by hand.

    `_walk_own` yields in stack order, not source order, so a single taint pass could visit
    `body = src.split(...)` before `src = path.read_text()` and conclude `body` was never file
    text. Both orderings must give the same answer; a control keyed to only the easy one would go
    green on the day someone reorders two lines.
    """
    tree = _poison_tree(tmp_path)
    head = "from pathlib import Path\nR = Path(__file__).resolve().parents[2]\n"
    forward = tree / "tests" / "test_forward.py"
    forward.write_text(
        head + "def test_x():\n"
        '    src = (R / "tools" / "thing.py").read_text()\n'
        "    body = src.split('x')[-1]\n"
        '    assert "Popen" not in body\n', encoding="utf-8")
    nested = tree / "tests" / "test_nested.py"
    nested.write_text(
        head + "def test_y():\n"
        "    def inner():\n"
        '        return (R / "tools" / "thing.py").read_text()\n'
        "    src = inner()\n"
        '    text = src\n'
        '    assert "Popen" not in text\n', encoding="utf-8")
    assert {s.function for s in census.census(tree, [forward])} == {"test_x"}
    # The nested case is the honest limit and is asserted as such: the read happens in a nested
    # function, so `_walk_own` does not carry the taint out of it. Pinned so that a future widening
    # is a deliberate change to this leg rather than a silent one.
    assert {s.function for s in census.census(tree, [nested])} == set()


def test_the_floor_holds_and_no_row_is_stale():
    """The real tree, against the frozen baseline. Shrink-only in both directions."""
    new, stale = census.check(REPO)
    assert not new, (
        f"a control reads Python source as text: {sorted(new)} -- route it through "
        f"tools/python_code_text.py, or freeze the row with a stated reason"
    )
    assert not stale, (
        f"the baseline claims rows the tree no longer has: {sorted(stale)} -- delete them; "
        f"a dead exemption is a pre-authorised re-entry"
    )


def test_the_baseline_is_not_empty_and_the_walk_reaches_the_tree():
    """VACUITY GUARD. Every leg above passes trivially if the census returns nothing on the real
    tree -- a bad pathspec, an `ls-files` that errored, a scope typo. This is the leg that says
    the walk happened at all."""
    assert len(_real_tree()) > 50, "the census walked the real tree and found almost nothing"
    assert census.load_baseline(), "the frozen baseline is empty"


def test_a_scope_with_NO_evidence_of_its_own_is_unknown_and_never_the_MODULE_s_subject(tmp_path):
    """THE FALLBACK THAT HID `tools/canon_drift_check.probe_text_in_file`.

    A scan whose own scope says nothing about what it reads is `unknown`, and rule 3 in this
    module's docstring reports it. Answering with the enclosing MODULE's path evidence answers a
    question the scope never asked, and the borrow is not symmetric: an empty scope verdict is
    already a member, so inheriting can only ever turn a member INTO a non-member. Measured on the
    real tree the day it was removed -- 12 rows gained in `tests/`, 29 in `tools`/`background`,
    none lost anywhere.

    The subject here is deliberately named by a PARAMETER, because that is the shape that made it
    matter: `probe_text_in_file` reads a path out of `docs/design/canon_claims.yaml`, so no
    source-level evidence will ever say what it reads and `unknown` is the whole of the right
    answer.

    KILLS `evidence = _path_evidence(scope) or module_evidence`: restore it and the module's
    markdown literals make this row `non-python` and it disappears.
    """
    tree = _poison_tree(tmp_path)
    borrowed = tree / "tests" / "test_borrowed_evidence.py"
    borrowed.write_text(
        "from pathlib import Path\n"
        "R = Path(__file__).resolve().parents[2]\n"
        'DOC = R / "docs" / "design" / "notes.md"\n'
        'REGISTER = R / "docs" / "observability" / "state.json"\n'
        "def test_reads_whatever_the_register_named(named):\n"
        "    assert named not in (R / named).read_text()\n", encoding="utf-8")
    rows = census.census(tree, [borrowed])
    assert [(s.function, s.subject) for s in rows] == [
        ("test_reads_whatever_the_register_named", census.UNKNOWN)], (
        "a scope carrying no path evidence of its own inherited the module's and was dismissed")


def test_the_MODULE_s_evidence_is_still_PRINTED_when_the_scope_has_none(tmp_path):
    """The other half, so the fix is a change of VERDICT and not a loss of information.

    Module evidence still reaches the row a reader sees; it just no longer decides membership.
    Without this leg, deleting `evidence = own or module_evidence` outright is a silent
    equivalence and nothing says the reader was left worse off.
    """
    tree = _poison_tree(tmp_path)
    borrowed = tree / "tests" / "test_borrowed_evidence.py"
    borrowed.write_text(
        "from pathlib import Path\n"
        "R = Path(__file__).resolve().parents[2]\n"
        'DOC = R / "docs" / "design" / "notes.md"\n'
        "def test_reads_whatever_the_register_named(named):\n"
        "    assert named not in (R / named).read_text()\n", encoding="utf-8")
    (row,) = census.census(tree, [borrowed])
    assert "notes.md" in row.evidence, (
        "the module's evidence stopped reaching the printed row, so the reason a row was "
        "reported is no longer legible")
