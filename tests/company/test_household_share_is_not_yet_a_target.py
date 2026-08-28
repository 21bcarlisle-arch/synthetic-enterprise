"""HOUSEHOLD_SHARE_IS_NOT_YET_A_TARGET — atom `A47`, R12 + R13.

`company/analytics/household_value_share.py` measures what a household kept. It
is a DIAGNOSTIC today and no decision surface may read it.

WHY, AND THE REASON IS NOT THE USUAL ONE. Carbon is barred from decision
surfaces permanently (`test_carbon_not_a_target.py`, CARBON_NOT_A_TARGET_CONSTRAINT):
a metric a decision surface cannot import is a metric it cannot optimise, and
£/tCO₂e must never become a thing the company games. **Household saving is
different: it is half of the objective the director's 2026-08-28 mission
describes**, and it is EXPECTED to enter the score. What bars it today is R13,
not R12's anti-goal-seeking: wiring a household-side term into a decision
surface changes what the company does, a difficulty change is the director's,
named and versioned, and the agent controls both sides of that wall.

**WHAT RELEASES THIS GUARD (a hold whose release triggers nothing is a defect,
R11):** a director decision on the two-sided objective. On that decision the
first entry appears in `DECLARED_READERS` below with its written reason, and
`test_declaring_a_reader_forces_the_control_to_become_reachability_based`
turns this file red until the control is upgraded — because a direct-import
scan is only sufficient while nothing imports the module at all.

WHY A DIRECT SCAN IS SUFFICIENT *TODAY*, STATED SO IT CAN BE CHECKED. A module
cannot be reached transitively without SOMETHING importing it directly first.
While the direct-importer set inside the decision tree is empty, reachability
and adjacency are the same relation, so the cheaper scan is not a weaker
control — it is the same control. That equivalence dies the moment the set is
non-empty, and the test named above is what stops it dying quietly.

REPORTING IS NOT DECIDING. `tools/` and `tests/` may read the module freely:
the harness scoring a run and a report printing a figure are exactly the
diagnostic use R12 protects. The bar is on `company/`, `saas/`, `simulation/`,
`sim/` and `background/` — the company's own organs, the world, and the
machine's own draw.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBJECT = "company.analytics.household_value_share"
SUBJECT_PATH = REPO_ROOT / "company" / "analytics" / "household_value_share.py"

#: Trees whose modules MAY NOT read the household figure. `tools/` and `tests/`
#: are deliberately absent — see the module docstring.
BARRED_TREES = ("company", "saas", "simulation", "sim", "background")

#: Every module inside a barred tree permitted to import the subject, each with
#: the written reason it is permitted. EMPTY, and empty is the strongest state:
#: it makes reachability and adjacency the same relation.
DECLARED_READERS: dict[str, str] = {}


def _production_files() -> tuple[Path, ...]:
    out: list[Path] = []
    for tree in BARRED_TREES:
        root = REPO_ROOT / tree
        if not root.is_dir():
            continue
        out += [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]
    return tuple(sorted(out))


def _imports_the_subject(source: str) -> bool:
    """True if `source` imports the household-share module by any spelling."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    leaf = SUBJECT.rsplit(".", 1)[1]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name == SUBJECT or a.name.startswith(SUBJECT + ".")
                   for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == SUBJECT or node.module.startswith(SUBJECT + "."):
                return True
            # `from company.analytics import household_value_share`
            if node.module == SUBJECT.rsplit(".", 1)[0] and any(
                    a.name == leaf for a in node.names):
                return True
    return False


# ── the detector can fail, in both directions (R15) ─────────────────────────

@pytest.mark.parametrize("source", [
    "import company.analytics.household_value_share",
    "from company.analytics.household_value_share import build_household_value_share",
    "from company.analytics import household_value_share",
    "import company.analytics.household_value_share as hvs",
])
def test_the_detector_fires_on_every_spelling(source):
    assert _imports_the_subject(source), source


@pytest.mark.parametrize("source", [
    "from company.analytics.customer_value_view import build_customer_value_view",
    "from company.analytics import clv_three_horizon",
    "household_value_share = 3  # a name, not an import",
    "# from company.analytics.household_value_share import x",
])
def test_the_detector_is_quiet_on_code_that_does_not_import_it(source):
    assert not _imports_the_subject(source), source


# ── the live control ────────────────────────────────────────────────────────

def test_the_scanned_population_is_not_empty():
    """POPULATION FLOOR. A guard that scans zero files passes forever. This
    fires the day a tree is renamed or the glob stops matching — the class of
    defect found five times on 2026-08-28."""
    files = _production_files()
    assert len(files) > 500, (
        "the barred-tree scan found only {} file(s) -- the population moved and this "
        "control went quiet rather than loud".format(len(files)))


def test_no_barred_module_reads_the_household_figure_undeclared():
    """THE CONTROL. Fires on: any company organ, world module or draw importing
    the household saving, which is what turns a diagnostic into a target."""
    readers = sorted(
        str(p.relative_to(REPO_ROOT))
        for p in _production_files()
        if p != SUBJECT_PATH and _imports_the_subject(p.read_text(encoding="utf-8"))
    )
    undeclared = [r for r in readers if r not in DECLARED_READERS]
    assert not undeclared, (
        "these modules read the household-share figure and are not declared: "
        + ", ".join(undeclared)
        + " -- half the objective is not yet the objective; see this file's docstring "
          "for what releases the guard")


def test_declaring_a_reader_forces_the_control_to_become_reachability_based():
    """NO ORPHAN TRANSITION. The direct-import scan above is only equivalent to
    a reachability scan while nothing imports the subject at all. The day the
    first reader is declared, that equivalence dies and this test says so
    LOUDLY rather than letting a weaker control keep the same name."""
    assert not DECLARED_READERS, (
        "a reader has been declared ({}), so a direct-import scan no longer covers "
        "transitive reach -- upgrade this control to the import-graph form used by "
        "tests/company/test_carbon_not_a_target.py before landing the declaration"
        .format(", ".join(sorted(DECLARED_READERS))))


def test_the_subject_exists_where_this_control_thinks_it_does():
    """An unresolvable subject is a FAILED check, never a silent skip — the
    defect `test_carbon_not_a_target.py` found on its own first run."""
    assert SUBJECT_PATH.is_file(), SUBJECT_PATH
