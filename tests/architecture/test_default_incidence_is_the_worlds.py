"""KNIFE3 step 29 — the control on `B11_default_incidence_is_the_worlds`.

WHY THIS FILE EXISTS, AND WHY THE RATCHET IS NOT ENOUGH (R15)
--------------------------------------------------------------
The cut in register §3x removes one edge, `simulation.run_phase2b ->
saas.cost_to_serve`, carrying one name: `get_bad_debt_rate()`. The world's
settlement loop used it to accrue `bad_debt_gbp` period by period, before any
bill exists — so the fraction of revenue THIS SUPPLIER PROVIDED FOR was the
fraction that actually went bad. Deleting the ratchet tuple proves the import is
gone, and that is all it proves. Three things it cannot see:

  1. **Behaviour.** The accrual reduces `net_margin_gbp`, feeds the running
     treasury balance and reaches `is_administration_triggered(treasury)` — the
     world's decision about whether the supplier goes bust mid-run. The full
     pre-cut year x segment grid is pinned below as literals, transcribed from a
     run of `saas.cost_to_serve.get_bad_debt_rate` BEFORE the call site was
     switched.

  2. **That the world is actually asking itself.** A revert to the company
     import would leave every pinned value green — the two tables agree today,
     which is exactly why this cut is safe and exactly why a value test cannot
     police it. `test_no_sim_side_importer_of_the_suppliers_provision` names the
     import, not the number, and `test_the_accrual_still_calls_the_worlds_table`
     names the call, so deleting the accrual outright cannot pass as a cut
     either.

  3. **That the two are FREE TO DISAGREE.** This is the point of the cut and the
     one thing a test pinning them equal would destroy (the refusal recorded for
     `B3`, `B7` and `B10` — register §3g). There is no assertion anywhere in this
     file that the world's incidence equals the supplier's provision. The proof
     runs the other way:
     `test_the_worlds_incidence_does_not_route_through_the_supplier` rewrites the
     supplier's table at runtime and the world's answer is unchanged — with a
     vacuity guard asserting the supplier's OWN answer really did move, because
     a mutation that changes nothing proves nothing.

WHY THE CUT, IN ONE PARAGRAPH
------------------------------
How much of a supplier's billed revenue actually arrives is a fact about
customers and the economy. What the supplier PROVIDES FOR is its own commercial
judgement, and a real supplier is wrong about it routinely — Phase QD found this
very table overstated true bad debt ~30x against the emergent arrears model. While
the world accrued at the supplier's rate, that error was structurally impossible
to make and therefore impossible for the COUPLED TRIAD to score. Note the half
that was already right: the income-stress uplift multiplied onto this rate,
`simulation.payment_timing.stress_bad_debt_multiplier`, has always been
world-side. The world owned the modifier and borrowed the level.

THE THREE KILLER PATTERNS, ANSWERED
------------------------------------
TAUTOLOGY   — the expected rates are literals transcribed from the PRE-CUT
              company function. Nothing in this file derives them from
              `world_bad_debt_incidence`, and no test compares the two
              implementations to each other.
FAIL-OPEN   — `test_the_pin_is_not_one_flat_number` asserts the grid actually
              varies by year AND by segment. A table collapsed to a single
              constant would satisfy every "rate is a float in [0,1]" style
              assertion while destroying the crisis structure, and would make
              the year argument vacuous.
FAIL-SILENT — the world module and the call site are read from the real files by
              AST; a missing file or an unparsable module is a failure here,
              never a skip. The sim-side import sweep asserts it walked a
              non-empty file set before concluding "no importer".

MUTATION EVIDENCE — recorded in `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
§3x, which is where the counts live so they cannot drift from the register.
"""

import ast
from pathlib import Path

import pytest

from simulation.bad_debt_incidence import world_bad_debt_incidence

REPO_ROOT = Path(__file__).resolve().parents[2]
WORLD_MODULE_PATH = REPO_ROOT / "simulation" / "bad_debt_incidence.py"
# Named as a PATH so a module rename reds this control rather than silently
# exempting the file.
SWITCHED_CALL_SITE = REPO_ROOT / "simulation" / "run_phase2b.py"
SUPPLIERS_PROVISION_MODULE = "saas.cost_to_serve"

# ---------------------------------------------------------------------------
# The pin. Transcribed from a run of `saas.cost_to_serve.get_bad_debt_rate`
# BEFORE the call site was switched. Literals on purpose: rewriting
# `world_bad_debt_incidence` cannot move them, and neither can rewriting the
# supplier's table.
#
# The years span the settlement window `simulation/run_phase2b.py` actually runs
# (REPORT_START 2016-01-01 -> REPORT_END 2025-06-07) plus both fallback edges.
# "unknown" is the unrecognised-segment fallback, exercised at every year
# because the fallback chain reads two dicts and could regress at either.
# ---------------------------------------------------------------------------
_BASELINE = {"resi": 0.02, "SME": 0.01, "I&C": 0.005, "unknown": 0.02}
PRE_CUT_RATE = {
    2010: dict(_BASELINE),  # below the tabulated span — falls back
    2015: dict(_BASELINE),  # the year before it — falls back
    2016: dict(_BASELINE),
    2017: dict(_BASELINE),
    2018: dict(_BASELINE),
    2019: dict(_BASELINE),
    2020: dict(_BASELINE),
    2021: {"resi": 0.04, "SME": 0.015, "I&C": 0.005, "unknown": 0.02},
    2022: {"resi": 0.08, "SME": 0.03, "I&C": 0.01, "unknown": 0.02},
    2023: {"resi": 0.05, "SME": 0.02, "I&C": 0.005, "unknown": 0.02},
    2024: {"resi": 0.03, "SME": 0.012, "I&C": 0.005, "unknown": 0.02},
    # 2025 IS INSIDE THE RUN WINDOW AND IS NOT TABULATED — the last five months
    # of every full run accrue at the ordinary-year baseline. Pinned so the
    # gap is deliberate and visible rather than discovered again later; closing
    # it is a fidelity question about the world, not part of this cut.
    2025: dict(_BASELINE),
    2030: dict(_BASELINE),  # above the tabulated span — falls back
}


@pytest.mark.parametrize("year", sorted(PRE_CUT_RATE))
@pytest.mark.parametrize("segment", ("resi", "SME", "I&C", "unknown"))
def test_world_incidence_matches_the_pre_cut_rate(year, segment):
    assert world_bad_debt_incidence(year, segment) == pytest.approx(
        PRE_CUT_RATE[year][segment]
    ), (
        f"the cut moved {segment} bad-debt incidence in {year} — net margin, the "
        "running treasury balance and the administration trigger all move with it"
    )


def test_the_pin_is_not_one_flat_number():
    """FAIL-OPEN guard: a table collapsed to one constant proves nothing.

    Every per-cell assertion above stays green if `world_bad_debt_incidence`
    ignores both arguments and the pin is edited to match. The structure the
    table exists to carry is asserted directly instead: it varies BY YEAR (the
    crisis surge) and BY SEGMENT (credit-checked customers default less).
    """
    by_year = {world_bad_debt_incidence(y, "resi") for y in PRE_CUT_RATE}
    assert len(by_year) > 1, "residential incidence is flat across every year"

    by_segment = {
        world_bad_debt_incidence(2022, s) for s in ("resi", "SME", "I&C")
    }
    assert len(by_segment) == 3, "the three segments do not have three rates"

    assert world_bad_debt_incidence(2022, "resi") > world_bad_debt_incidence(
        2020, "resi"
    ), "the 2021-22 crisis surge is gone from the world's own table"
    assert world_bad_debt_incidence(2022, "I&C") < world_bad_debt_incidence(
        2022, "resi"
    ), "I&C is no longer the best-behaved segment"


def test_an_unrecognised_segment_is_never_the_cheapest():
    """A segment this world has no rate for must not be treated as low-risk.

    The fallback chain is two `.get()`s deep. A regression that returned 0.0,
    or the I&C rate, would be invisible in every headline figure and would
    quietly forgive an entire unrecognised book.
    """
    for year in (2020, 2022, 2030):
        fallback = world_bad_debt_incidence(year, "no_such_segment")
        assert fallback > 0.0, "an unknown segment defaults to no bad debt at all"
        assert fallback >= world_bad_debt_incidence(year, "I&C")


# ---------------------------------------------------------------------------
# The direction the cut exists to protect
# ---------------------------------------------------------------------------


def _imported_module_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def _sim_side_files() -> list[Path]:
    found: list[Path] = []
    for d in ("sim", "simulation"):
        root = REPO_ROOT / d
        if not root.is_dir():
            continue
        found.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return found


def test_no_sim_side_importer_of_the_suppliers_provision():
    """THE MUTATION THAT MATTERS MOST is the one this test catches.

    Re-adding `from saas.cost_to_serve import get_bad_debt_rate` to the world
    restores the defect in full while every pinned value above still agrees —
    the two tables carry the same numbers today. A control built only from
    values would pass with the crossing back in place.
    """
    files = _sim_side_files()
    assert len(files) > 20, (
        f"walked only {len(files)} sim-side files — the sweep is broken, and a "
        "sweep that finds nothing because it looked nowhere is a passing test "
        "with no subject"
    )

    offenders = sorted(
        str(p.relative_to(REPO_ROOT))
        for p in files
        if any(
            m == SUPPLIERS_PROVISION_MODULE or m.startswith(SUPPLIERS_PROVISION_MODULE + ".")
            for m in _imported_module_names(p)
        )
    )
    assert offenders == [], (
        "the world is reading the supplier's provisioning table again: "
        f"{offenders}. How much revenue actually arrives is not a supplier "
        "decision — see register §3x."
    )


def test_the_accrual_still_calls_the_worlds_table():
    """FAIL-SILENT guard: deleting the accrual must not read as a clean cut.

    The cheapest way to green every test above is to remove the bad-debt line
    from the settlement loop entirely. That is not this cut; it would be a
    behaviour change to `net_margin_gbp`, the treasury balance and the
    administration trigger. The call is asserted by AST against the real file.
    """
    tree = ast.parse(SWITCHED_CALL_SITE.read_text(encoding="utf-8"))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "world_bad_debt_incidence" in called, (
        f"{SWITCHED_CALL_SITE.name} no longer accrues bad debt from the world's "
        "own incidence table"
    )
    assert "stress_bad_debt_multiplier" in called, (
        "the income-stress uplift beside it is gone — it was always world-side "
        "and it is what makes the accrual respond to the world's own conditions"
    )


def test_the_worlds_incidence_does_not_route_through_the_supplier(monkeypatch):
    """Independence, proven by breaking the SUPPLIER and finding the world intact.

    There is deliberately no assertion that the two tables agree. The supplier
    stops providing for bad debt at all; the world's incidence must not move.
    The vacuity guard is the second half: if the mutation did not change the
    supplier's own answer, this test is asserting nothing.
    """
    import saas.cost_to_serve as cts

    before_world = {
        (y, s): world_bad_debt_incidence(y, s)
        for y in (2020, 2022, 2030)
        for s in ("resi", "SME", "I&C")
    }
    before_supplier = cts.get_bad_debt_rate(2022, "resi")

    monkeypatch.setattr(cts, "BAD_DEBT_RATE", {"resi": 0.0, "SME": 0.0, "I&C": 0.0})
    monkeypatch.setattr(cts, "_BAD_DEBT_RATE_BY_YEAR", {})

    after_supplier = cts.get_bad_debt_rate(2022, "resi")
    assert after_supplier != before_supplier, (
        "VACUITY: the mutation did not move the supplier's own provision, so "
        "the world staying put proves nothing about who depends on whom"
    )

    after_world = {
        (y, s): world_bad_debt_incidence(y, s)
        for y in (2020, 2022, 2030)
        for s in ("resi", "SME", "I&C")
    }
    assert after_world == before_world, (
        "the world's bad-debt incidence moved when the SUPPLIER changed its "
        "provisioning assumption — the crossing is back"
    )
