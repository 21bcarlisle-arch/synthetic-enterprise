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

WHY THE FLOOR IS LARGE AND NOT 0. Three hand passes over this same class converged on nine members
and called the population closed. The census returned 117 scan sites in `tests/` alone, then 187
once `tools/` and `background/` were added, and 352 once taint crossed a call boundary on
2026-09-09. They are not 352 defects -- most are one function reading one named module for one
token, where the prose hazard is small -- but the number is the finding: the population was never
enumerable by hand, and every attempt to enumerate it exhibited the class, the detector's own
per-scope blind spot included. The floor freezes what exists so the next one is refused, and
shrinks as rows are routed through the remedy.
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
    # THE SHAPE THE CENSUS WAS BLIND TO UNTIL 2026-09-09. The read is in one function and the
    # match is in a helper that takes the text as a PARAMETER -- and a parameter is never
    # assigned, so the per-scope taint rule could never reach it. `capability_index
    # ._wire_edges` -> `_path_references(text, ...)` is the live instance this stands for.
    (tmp_path / "tests" / "test_helper_matches_a_parameter.py").write_text(
        root + 'def _has_a_kill(text):\n'
        '    return "os.kill(" in text\n'
        'def test_j():\n'
        '    assert not _has_a_kill((R / "background" / "worker.py").read_text())\n',
        encoding="utf-8")
    # AND THE SAME BOUNDARY IN THE OTHER PREDICATE. Here the match and the read are in ONE scope,
    # so no taint has to cross anything -- but that scope is handed the repository root as a
    # parameter spelled `base`, and "does this read the REPOSITORY" was also answered per scope.
    # `_root_parameter` guesses at four names; the call graph knows. This is the shape of
    # `capability_index._wire_edges(base, ...)`, and without it the live instance the whole pass
    # was drawn for is invisible while every other leg here still passes.
    (tmp_path / "tests" / "test_root_arrives_as_an_argument.py").write_text(
        root + 'def _scan(base):\n'
        '    return "os.kill(" in (base / "background" / "worker.py").read_text()\n'
        'def test_m():\n'
        '    assert not _scan(R)\n', encoding="utf-8")

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
    # THE SAME BLIND SPOT RUNNING THE OTHER WAY, and it cost a FALSE POSITIVE rather than a
    # missed member. The remedy is applied in a helper defined in this same file, so matching
    # `ROUTERS` against the call names in the CALLER's expression saw `_names(...)` and nothing
    # else. `publisher_budget.declared_publisher_budget_seconds` was the live instance: what it
    # holds is a dict of parsed constants, and it was reported as reading Python by substring.
    (tmp_path / "tests" / "test_local_parse_helper.py").write_text(
        root + "import ast\n"
        'def _names(source):\n'
        '    return {n.id for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Name)}\n'
        'def test_k():\n'
        '    assert "os" not in _names((R / "background" / "worker.py").read_text())\n',
        encoding="utf-8")
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
        "test_helper_matches_a_parameter.py",
        "test_root_arrives_as_an_argument.py",
    }


def test_a_scope_handed_the_ROOT_by_a_caller_is_reading_the_tree(tmp_path):
    """`_reaches_the_tree` is per-scope too, and crossing one boundary without the other catches
    nothing. A function whose repository root arrives as an argument named `base` says nothing
    about the tree in its own body; the thing that calls it does.

    Written because the mutation that removes the call-graph clause survived every other leg in
    this file while losing `capability_index._path_references` -- the live instance the
    interprocedural pass was built for -- from the real tree.

    KILLS `_reaches_the_tree(scope, ...)` in place of the call-graph closure.
    """
    tree = _poison_tree(tmp_path)
    handed = tree / "tests" / "test_root_arrives_as_an_argument.py"
    assert [s.function for s in census.census(tree, [handed])] == ["_scan"]


def test_a_scan_in_a_HELPER_is_named_for_the_helper_and_not_for_its_caller(tmp_path):
    """WHERE the interprocedural row lands, which the partition leg above cannot see.

    The first draft attributed a helper's match to the CALLER, and on the real tree that was 152
    new rows in which every entry point transitively reaching a grep became a member and the
    function holding the match was named in none of them. A row is a specific control, so the
    control is the function the match is in -- reported once, however many callers hand it the
    tree.

    KILLS attributing to the caller: swap the two and this leg reads `test_j`.
    """
    tree = _poison_tree(tmp_path)
    helper = tree / "tests" / "test_helper_matches_a_parameter.py"
    assert [s.function for s in census.census(tree, [helper])] == ["_has_a_kill"]


def test_a_helper_called_with_NOTHING_tainted_is_not_handed_the_tree(tmp_path):
    """The other half of crossing the call: taint is seeded from the ARGUMENTS at the call site,
    not from the fact that a helper has parameters at all.

    Without this, every helper taking a string in a tree-reading module becomes a member and the
    census says nothing. KILLS seeding all parameters unconditionally.
    """
    tree = _poison_tree(tmp_path)
    clean = tree / "tests" / "test_clean_argument.py"
    clean.write_text(
        "from pathlib import Path\n"
        "R = Path(__file__).resolve().parents[2]\n"
        "def _mentions(text, token):\n"
        "    return token in text\n"
        "def test_l():\n"
        '    assert not _mentions("a literal, not the tree", "zzz")\n'
        '    assert len((R / "tools" / "thing.py").read_text()) > 1\n', encoding="utf-8")
    assert census.census(tree, [clean]) == []


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
