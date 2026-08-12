"""The SITE SURFACE half of the pre-commit test gate, proven able to FAIL (R15).

WHY THIS FILE EXISTS (2026-08-12, DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_NAV_AND_STAMPS,
item 1). The director read the live site and found the Knowledge section had no route in
from the main nav: nine pages that exist, render and pass their tests, eight of which no
reader could reach. His ask was for the CONTROL, not the fix — "If a control could make 'a
published page with no route in' fail at build time rather than be found by the director
looking at the site, that is worth more than the fix."

A control alone would not have done it. `site/` is deliberately absent from the gate's
CODE_PREFIXES, whose comment says "site/data ... is pure data and cannot break a control".
That was true when the only thing under `site/` was rendered data and is not true of the
pages: adding `site/knowledge/<topic>/index.html` with nothing linking to it touches no
`.py` at all, so before this wiring the gate skipped the commit entirely as pure docs, and
`tests_for()` maps an `.html` to zero tests in any case. The page reached the live site and
the director found it with his eyes. That is the loop this closes.

THE SAME THREE LAYERS as the canon-surface file beside it, for the same stated reason — "a
gate extension that passes on everything is the fail-open pattern this project already
names", so asserting a string is in a list is not where this stops:

  1. SELECTION — a `site/**/*.html` commit selects the reachability control.
     Mutation: drop SITE_SURFACE_TESTS, or the `.html` predicate -> layer 1 fails.
  2. LIVE CONTROL — the selected test, run against a tree carrying an unreachable page,
     actually goes RED and red for THIS reason (its output names the orphan). This is what
     makes layer 1 mean something: the gate selects a control that BITES.
  3. ANTI-TAUTOLOGY + NARROW TRIGGER — the same run against the unmutated tree passes (so
     layer 2's red is the orphan, not the harness), and neither an unrelated docs commit
     nor a `site/data/*.json` commit selects anything (the gate's cadence is deliberately
     narrow, and rendered data under site/ is still pure data).

Layer 2 runs against a MINIMAL COPY of the tree in tmp_path, never the real one — the
discipline the canon-surface file sets, and necessary here for the same reason: the real
`site/` is written by process_run_complete and the auto-processor, so mutating it in place
would race writers this repo explicitly warns about.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import pre_commit_test_gate as gate

REPO_ROOT = Path(__file__).resolve().parents[2]
REACHABILITY_TEST = "tests/tools/test_site_reachability.py"
#: The one test layer 2 runs: it needs only `site/` and the tool module, so the tmp copy
#: stays small and the red is unambiguous.
ORPHAN_TEST = "test_the_LIVE_SITE_has_no_published_page_without_a_route_in"


# --- Layer 1: the gate SELECTS the control -----------------------------------

def test_a_site_page_commit_selects_the_reachability_control():
    """The wiring itself — the exact state measured on 2026-08-12, when it selected NOTHING."""
    targets = gate.select_targets(["site/knowledge/carbon-price/index.html"])
    assert REACHABILITY_TEST in targets, (
        "a commit adding a site page does not run the control that measures whether pages "
        f"are reachable — an orphan page cannot fail this gate. selected: {targets}"
    )


def test_the_front_door_itself_selects_it_too():
    """The nav is where a route is REMOVED, which strands a section without adding a file."""
    assert REACHABILITY_TEST in gate.select_targets(["site/index.html"])


def test_the_declared_control_exists_on_disk():
    """A surface wired to a test file that does not exist is a fail-silent gate extension."""
    for rel in gate.SITE_SURFACE_TESTS:
        assert (REPO_ROOT / rel).is_file(), f"{rel} is declared but missing"


# --- Layer 2: the selected control BITES -------------------------------------

@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A minimal copy: the site, the tool, the test, and the packages they import through."""
    root = tmp_path / "repo"
    (root / "tools").mkdir(parents=True)
    (root / "tests" / "tools").mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "site", root / "site")
    for pkg in ("tools", "tests", "tests/tools"):
        src = REPO_ROOT / pkg / "__init__.py"
        if src.is_file():
            shutil.copy(src, root / pkg / "__init__.py")
    shutil.copy(REPO_ROOT / "tools" / "site_reachability.py", root / "tools")
    shutil.copy(REPO_ROOT / REACHABILITY_TEST, root / REACHABILITY_TEST)
    return root


def _run(tree: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", f"{REACHABILITY_TEST}::{ORPHAN_TEST}", "-q"],
        cwd=str(tree), capture_output=True, text=True, timeout=300,
    )


def test_the_selected_control_goes_RED_on_a_tree_with_an_orphan_page(tree: Path):
    """THE R15 PROOF. The defect in the shape it actually arrives: a page is added and
    nothing links to it."""
    orphan = tree / "site" / "knowledge" / "brand-new-topic" / "index.html"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("<html><body><a href='../'>up</a></body></html>")

    result = _run(tree)

    assert result.returncode != 0, (
        "the gate's own control passed on a site carrying an unreachable page — this is the "
        f"director's defect, undetected.\n{result.stdout}"
    )
    assert "NO ROUTE IN" in result.stdout, (
        f"it failed, but not for being unreachable — wrong reason:\n{result.stdout}"
    )
    assert "brand-new-topic" in result.stdout, (
        f"the failure does not name the orphan it found:\n{result.stdout}"
    )


def test_the_same_control_is_GREEN_on_the_unmutated_tree(tree: Path):
    """ANTI-TAUTOLOGY. Without this, the red above could be the harness rather than the
    orphan — and the whole file would prove nothing."""
    result = _run(tree)

    assert result.returncode == 0, (
        f"the reachability control is red on the real site with no mutation applied:\n"
        f"{result.stdout}\n{result.stderr}"
    )


# --- Layer 3: the trigger stayed NARROW --------------------------------------

def test_an_unrelated_docs_commit_still_runs_nothing():
    """The gate's cadence is deliberately fast; this must not tax every docs commit."""
    assert gate.select_targets(["docs/status/LATEST.md"]) == []


def test_rendered_site_DATA_is_still_pure_data():
    """`site/data/*.json` is regenerated on every sim run. Selecting the control there would
    put a test on the auto-processor's commit path for a file that cannot strand a page."""
    assert gate.select_targets(["site/data/capabilities.json"]) == []
