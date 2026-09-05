"""THE DEFECT THIS NAMES: a converged module reached by hundreds of suites and named by none reads
as well-covered by every count this project keeps.

`background/direction.py` is reached by 184 test files and imported by 4. `background/ops_repo.py`
was reached by every suite of its three callers and imported by none, and its shared function had
never been executed by a test (`befe26b7e`). The distinction between REACHING a module and NAMING
it is the entire content of `tools/converged_contract_screen.py`, so a screen that collapsed the
two would report the flattering number and be useless for choosing the next mutation battery --
which is the only thing it is for.

Hermetic: every leg builds its own synthetic tree and never reads the real repo, so these controls
cannot go green or red because another lane landed a module.
"""
from __future__ import annotations

import pytest

from tools.converged_contract_screen import screen


@pytest.fixture
def tree(tmp_path):
    """A tree with BOTH sides of every partition this screen splits on.

    `shared` -- 3 callers, a dedicated suite (named for it).
    `orphan` -- 3 callers, NO test importer at all, but reached through its callers.
    `pair`   -- 2 callers, below the convergence threshold.
    """
    (tmp_path / "background").mkdir()
    (tmp_path / "tests").mkdir()
    def w(p, s):
        (tmp_path / p).write_text(s, encoding="utf-8")

    w("background/shared.py", "VALUE = 1\n")
    w("background/orphan.py", "VALUE = 2\n")
    w("background/pair.py", "VALUE = 3\n")
    for i in (1, 2, 3):
        w(f"background/c{i}.py",
          "from background import shared\nfrom background import orphan\n"
          + ("from background import pair\n" if i <= 2 else ""))
    # names `shared` -- a dedicated suite
    w("tests/test_shared.py", "from background import shared\n")
    # names neither: it reaches `shared` and `orphan` only THROUGH c1
    w("tests/test_c1.py", "from background import c1\n")
    return tmp_path


def _by_module(rows):
    return {r["module"]: r for r in rows}


def test_the_partition_this_screen_splits_on_is_reachable_in_both_directions(tree):
    """The control over the whole partition, written before any leg asserts what a branch DOES.

    A screen that reported nothing, or that reported every module identically, would pass a
    per-branch assertion about the branch it happened to take. This fails unless a dedicated row,
    an undedicated row, a reached-but-unnamed row and an excluded row ALL exist at once.
    """
    rows = _by_module(screen(root=tree, converged_at=3))
    assert rows["background.shared"]["dedicated"], "no dedicated-suite row: partition unreachable"
    assert not rows["background.orphan"]["dedicated"], "no undedicated row: partition unreachable"
    assert rows["background.orphan"]["reaching"], "no reached-but-unnamed row"
    assert "background.pair" not in rows, "the below-threshold branch never excluded anything"


def test_a_module_no_suite_names_is_still_reached_through_its_callers(tree):
    """The load-bearing leg. `orphan` has zero direct importers and is REACHED by the suite of a
    caller -- the exact shape `ops_repo` was in. Collapsing `reaching` onto `direct` kills this.
    """
    orphan = _by_module(screen(root=tree, converged_at=3))["background.orphan"]
    assert orphan["direct"] == [], "orphan gained a direct importer the fixture did not write"
    assert "tests/test_c1.py" in orphan["reaching"], (
        "a suite that reaches the module only through its caller was not counted -- the screen "
        "cannot tell a named contract from an incidentally-executed one"
    )
    assert "tests/test_c1.py" not in orphan["direct"]


def test_reaching_is_strictly_wider_than_naming_for_a_module_that_has_both(tree):
    """`shared` is both named (test_shared.py) and reached (test_c1.py, via c1). If `reaching`
    were built from direct importers these two sets would be equal and the screen would report
    that nothing is exercised beyond what names it."""
    shared = _by_module(screen(root=tree, converged_at=3))["background.shared"]
    assert set(shared["direct"]) == {"tests/test_shared.py"}
    assert set(shared["reaching"]) > set(shared["direct"]), (
        "reaching did not exceed naming for a module with both -- the transitive walk is not "
        "walking"
    )
    assert "tests/test_c1.py" in shared["reaching"]


def test_a_test_file_is_never_counted_as_a_caller(tree):
    """Convergence is a claim about PRODUCTION callers. Counting suites as callers would make
    every well-tested module look converged and invert the ranking this screen exists to give."""
    shared = _by_module(screen(root=tree, converged_at=3))["background.shared"]
    assert shared["n_callers"] == 3
    assert all(not c.startswith("tests") for c in shared["callers"]), shared["callers"]


def test_the_threshold_is_the_only_thing_deciding_convergence(tree):
    """`pair` has 2 callers. It is absent at the declared threshold and present when the threshold
    is the one it meets -- so its exclusion is the threshold's doing and not a parse failure that
    dropped the file."""
    assert "background.pair" not in _by_module(screen(root=tree, converged_at=3))
    at_two = _by_module(screen(root=tree, converged_at=2))
    assert at_two["background.pair"]["n_callers"] == 2


def test_a_module_named_only_in_a_string_is_not_an_importer(tree):
    """The screen's stated UPPER-bound blindness, asserted rather than promised. `grep -rl
    background.direction tests/` returns a suite that carries the name only inside a parameterised
    table; that suite cannot execute a line of the module and must not be scored as evidence."""
    (tree / "tests" / "test_names_it_in_a_string.py").write_text(
        'CARRIERS = [("background.orphan", "VALUE")]\n', encoding="utf-8")
    orphan = _by_module(screen(root=tree, converged_at=3))["background.orphan"]
    assert "tests/test_names_it_in_a_string.py" not in orphan["direct"]
    assert "tests/test_names_it_in_a_string.py" not in orphan["reaching"]
