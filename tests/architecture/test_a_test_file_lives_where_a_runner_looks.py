"""A file that DEFINES tests must live where some runner actually collects it.

THE DEFECT THIS EXISTS FOR, measured 2026-09-05 (SEAT_FINDING_FORTY_TWO_TESTS_LIVE_WHERE_NO_
RUNNER_LOOKS_AND_ONE_OF_THEM_HAS_BEEN_RED_FOR_SEVEN_WEEKS). Four real suites carrying 42 tests
lived in `tools/` instead of `tests/tools/`. They were not stubs -- R15 in their docstrings, the
defect named per test. Nothing had ever run them. One of them,
`test_live_cache_matches_regeneration`, was a control written for exactly the drift that was live
(`site/data/regulatory.json` stale at 63 regulatory modules against a working 67, for seven
weeks) and it had never once been in a position to report it.

WHY NOTHING NOTICED, AND WHY THIS HAD TO BE A CONTROL RATHER THAN A HABIT. This repository has
NO pytest configuration -- no pyproject.toml, pytest.ini, setup.cfg, tox.ini or root conftest.py,
and `testpaths` appears in no ini/cfg/toml anywhere. Collection is decided ENTIRELY by the path
each runner passes. So a misplaced suite is not a warning, a skip, or a slow test: it is silence,
and silence is what every instrument reports as success. A test count says 42 more tests exist.
A "does a suite exist for this module?" grep says yes. A coverage figure says the lines are
executed, because some other suite reaches them transitively. Every question a reader would
think to ask returns the reassuring answer.

WHAT IT IS KEYED TO, and why that is the property and not today's answer. NOT "the tree contains
exactly these files" -- that goes red the moment anyone adds a legitimate test and green when a
runner is deleted, which is backwards. The subject is derived twice over:

  * the COLLECTED ROOTS come from the runners themselves -- `head_green_census.pytest_argv()`
    (the `pytest tests/` census and the pre-commit gate) and `site_lane_gate.SITE_PREFIX`
    (`pytest site/`). Delete a runner or repoint it and this control follows, rather than
    asserting against a root nobody runs any more.
  * a file is a SUITE because it DEFINES a test, read from its AST -- not because of its name.
    `tools/test_execution_metric.py` matches pytest's default `test_*.py` pattern and is a
    production module that measures test execution; `company/risk/stress_test.py` matches
    `*_test.py` and models collateral stress. Neither is a misplaced suite and a name-keyed
    control would have called both defects, which is how a control earns its way to being
    switched off.

FAIL-CLOSED, EXPLICITLY. If the runner derivation yields no roots, or a root that would swallow
the whole tree, the scan REFUSES rather than returning an empty list of problems -- an empty
result from a broken scan is indistinguishable from a clean tree, and this project has published
that mistake before. A `test_*.py` that cannot be parsed is likewise a refusal naming the file,
never a silent skip.

THE SYNTHETIC LEGS NEVER READ THIS REPOSITORY. Every leg below except `test_the_live_tree_has_no
_uncollected_suite` builds its own tree in tmp_path, so a mutation of this module's logic cannot
be masked -- or faked -- by what another lane happened to land. The partition leg asserts all
four kinds of file exist in one tree BEFORE any leg asserts what the detector does with a single
one of them, because a detector that reports NOTHING passes every individual negative leg.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

PROJECT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

# pytest's default `python_files`. Both patterns, because this repo sets neither.
_TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")

_SKIP_DIR_PARTS = frozenset({"__pycache__", ".git", "node_modules", ".venv", "venv"})


def collected_roots(project_dir: pathlib.Path) -> tuple[str, ...]:
    """The directories some runner in this repo actually points pytest at.

    Derived from the runners rather than declared here, so that repointing or deleting a runner
    moves this control with it instead of leaving it asserting against a path nobody runs.
    """
    roots: set[str] = set()

    from tools.head_green_census import pytest_argv

    # `pytest_argv()` is [python, -m, pytest, <root>, ...flags]. Take the positional paths.
    for arg in pytest_argv()[3:]:
        if arg.startswith("-"):
            continue
        if (project_dir / arg).is_dir():
            roots.add(arg.strip("/"))

    from tools.site_lane_gate import SITE_PREFIX

    if (project_dir / SITE_PREFIX).is_dir():
        roots.add(SITE_PREFIX.strip("/"))

    return tuple(sorted(roots))


def _defines_a_test(path: pathlib.Path) -> bool:
    """Does this module define something pytest would collect as a test?

    Module-level `def test_*` / `async def test_*`, or a `class Test*`. Read from the AST: a
    substring search would count the word in a docstring or a string table, which is the
    upper-bound failure this project has filed before.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="strict"))
    except (SyntaxError, UnicodeDecodeError, OSError) as exc:
        raise AssertionError(
            "{} matches pytest's collection pattern and could not be parsed, so this scan cannot "
            "say whether it is a misplaced suite: {}. Refusing rather than skipping it -- a "
            "control over what runs must not go green because it could not find out.".format(
                path, exc
            )
        ) from exc

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            return True
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            return True
    return False


def scan(project_dir: pathlib.Path, roots: tuple[str, ...]) -> tuple[list[str], int]:
    """(misplaced suites, number of candidate files examined).

    The second element exists so a caller can prove the walk found anything at all: an empty
    problem list from a scan that examined zero files is not a clean tree, it is a broken scan.
    """
    if not roots:
        raise AssertionError(
            "No collected root could be derived from any runner. Refusing: with no roots every "
            "file in the tree is 'uncollected' or none is, and either answer is meaningless."
        )
    for root in roots:
        if root in ("", ".", "/"):
            raise AssertionError(
                "Derived collected root {!r} covers the whole tree, which would make every "
                "misplaced suite invisible. Refusing.".format(root)
            )

    candidates: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for pattern in _TEST_FILE_PATTERNS:
        for path in project_dir.rglob(pattern):
            if not path.is_file() or path in seen:
                continue
            rel = path.relative_to(project_dir)
            if _SKIP_DIR_PARTS & set(rel.parts):
                continue
            if rel.parts and rel.parts[0] in roots:
                continue
            seen.add(path)
            candidates.append(path)

    misplaced = sorted(
        str(p.relative_to(project_dir)) for p in candidates if _defines_a_test(p)
    )
    return misplaced, len(candidates)


# ─────────────────────────────────────────────── synthetic trees (never this repo)
def _tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """A tree holding all four kinds of file at once."""
    root = tmp_path / "repo"
    (root / "tests" / "tools").mkdir(parents=True)
    (root / "tools").mkdir(parents=True)
    (root / "company" / "risk").mkdir(parents=True)

    # (a) a MISPLACED suite -- defines tests, lives in a production root
    (root / "tools" / "test_generate_thing.py").write_text(
        "def test_the_thing_is_derived():\n    assert True\n"
    )
    # (b) a production module that merely MATCHES the pattern
    (root / "tools" / "test_execution_metric.py").write_text(
        "def count_executed_tests(stats):\n    return len(stats)\n"
    )
    # (c) a properly placed suite
    (root / "tests" / "tools" / "test_placed.py").write_text("def test_ok():\n    assert True\n")
    # (d) a production module matching the OTHER default pattern
    (root / "company" / "risk" / "stress_test.py").write_text(
        "class StressTest:\n    pass\n"
    )
    return root


ROOTS = ("tests", "site")


def test_all_four_kinds_are_present_before_any_leg_asserts_what_one_branch_does(tmp_path):
    """The partition control. A detector that reports NOTHING passes every negative leg below,
    so establish first that the tree really does contain a misplaced suite, a pattern-matching
    production module, a correctly placed suite and an `*_test.py` production module -- and that
    the scan reached all of the uncollected ones."""
    root = _tree(tmp_path)
    misplaced, examined = scan(root, ROOTS)

    assert (root / "tools" / "test_generate_thing.py").is_file()
    assert (root / "tools" / "test_execution_metric.py").is_file()
    assert (root / "tests" / "tools" / "test_placed.py").is_file()
    assert (root / "company" / "risk" / "stress_test.py").is_file()

    # three uncollected candidates examined; the collected one excluded before parsing
    assert examined == 3, examined
    assert misplaced == ["tools/test_generate_thing.py"], misplaced


def test_the_same_file_under_a_collected_root_is_not_a_finding(tmp_path):
    """Keyed to LOCATION, not to the file. Move the identical bytes under a collected root and
    the finding must disappear -- otherwise the control is flagging a name, and every legitimate
    suite in tests/ would be a defect."""
    root = _tree(tmp_path)
    src = root / "tools" / "test_generate_thing.py"
    body = src.read_text()
    assert scan(root, ROOTS)[0] == ["tools/test_generate_thing.py"]

    src.unlink()
    (root / "tests" / "tools" / "test_generate_thing.py").write_text(body)
    assert scan(root, ROOTS)[0] == []


def test_a_production_module_named_like_a_test_is_not_a_finding_until_it_defines_one(tmp_path):
    """Keyed to DEFINING a test, not to the filename. `tools/test_execution_metric.py` is the
    live instance: a real production module whose name matches pytest's pattern. A name-keyed
    control calls it a defect, gets argued with, and is switched off."""
    root = _tree(tmp_path)
    metric = root / "tools" / "test_execution_metric.py"
    assert "tools/test_execution_metric.py" not in scan(root, ROOTS)[0]

    metric.write_text(metric.read_text() + "\n\ndef test_counts_are_cumulative():\n    assert True\n")
    assert "tools/test_execution_metric.py" in scan(root, ROOTS)[0]


def test_a_test_class_counts_as_defining_a_test(tmp_path):
    """pytest collects `class Test*` as well as `def test_*`. A control that saw only functions
    would let a whole misplaced class-based suite through."""
    root = _tree(tmp_path)
    (root / "tools" / "test_by_class.py").write_text(
        "class TestTheDerivation:\n    def test_it(self):\n        assert True\n"
    )
    assert "tools/test_by_class.py" in scan(root, ROOTS)[0]

    # ...and a production class whose name merely CONTAINS Test does not count
    (root / "company" / "risk" / "collateral_death_test.py").write_text(
        "class DeathTestHarness:\n    pass\n"
    )
    assert "company/risk/collateral_death_test.py" not in scan(root, ROOTS)[0]


def test_the_scan_refuses_rather_than_returning_a_clean_tree_it_could_not_measure(tmp_path):
    """FAIL-CLOSED. No roots, or a root that swallows the tree, must REFUSE. Returning [] there
    reads exactly like 'nothing is misplaced', which is the failure mode this whole control
    exists to stop being silent."""
    root = _tree(tmp_path)
    with pytest.raises(AssertionError, match="No collected root"):
        scan(root, ())
    for swallowing in (".", "", "/"):
        with pytest.raises(AssertionError, match="whole tree"):
            scan(root, (swallowing,))


def test_an_unparseable_candidate_is_refused_not_skipped(tmp_path):
    """A `test_*.py` this scan cannot read is an unknown, and an unknown must not be counted as
    clean."""
    root = _tree(tmp_path)
    (root / "tools" / "test_broken.py").write_text("def test_(:\n")
    with pytest.raises(AssertionError, match="could not be parsed"):
        scan(root, ROOTS)


# ─────────────────────────────────────────────── the live tree
def test_the_runner_derivation_finds_both_lanes():
    """If this ever returns one root, the OTHER lane's runner has moved and the live leg below
    has quietly stopped covering it -- which would read as a pass."""
    roots = collected_roots(PROJECT)
    assert "tests" in roots, roots
    assert "site" in roots, roots


def test_the_live_tree_has_no_uncollected_suite():
    misplaced, examined = scan(PROJECT, collected_roots(PROJECT))

    # Population guard: this repo genuinely contains production modules matching pytest's
    # patterns outside the collected roots (tools/test_execution_metric.py, the company/risk
    # *_test.py models). If the walk examines none of them it is broken, and its empty problem
    # list means nothing.
    assert examined > 0, (
        "the scan examined no candidate files at all -- the walk is broken, and an empty finding "
        "list from a broken walk is not a clean tree"
    )

    assert misplaced == [], (
        "These files define tests and live where no runner collects them, so they have never "
        "run and never will:\n  "
        + "\n  ".join(misplaced)
        + "\n\nCollection here is decided entirely by the path each runner passes -- there is no "
        "pytest config in this repo to rescue a misplaced file. Move each one under a collected "
        "root ({}), correcting any `Path(__file__).parent.parent` repo-root arithmetic for the "
        "new depth.".format(", ".join(collected_roots(PROJECT)))
    )
