"""POPULATION COVERAGE REPORT — realised cell counts vs the curriculum.

Builds DIRECTOR_RULING_POPULATION_ACTIVATION_AND_RUN_LEDGER_2026-07-25 §1
condition 3: "Coverage report before any derived figure is published. The
first activated run emits realised cell counts against the curriculum before
any number from it reaches a site surface. Thin cells are reported, not
smoothed."

WHAT THIS IS
------------
Given the ACTUAL drawn population for a run (the SIM-truth `SyntheticCustomer`
stream, cohorts assigned), report how many customers landed in each curriculum
cell — per axis, and the worst (thinnest) cell — and FLAG cells below a
redundancy floor. It never redistributes or smooths a thin cell; a gap is
reported as a gap (the whole point of the nested worst-cell coverage design,
`docs/market_research/population_coverage/nested_design.json`, whose objective
is "the worst cell, never the average").

WALL / R13
----------
This reads SIM-truth cohort cells directly — that is CORRECT: a coverage report
is a DIRECTOR / HARNESS artefact about what the world drew, not a
company-facing surface, so it does not cross `company/interfaces/`. The company
still discovers segment structure through the wall; this report is for judging
the DRAW, and it must see the truth to do that. It is READ-ONLY over the draw
and changes no curriculum value (R13): the marginals it counts against are read
live from the same director-set `segmentation_curriculum_v1.json`.

WHY BEFORE PUBLICATION (the gate, not just the report)
------------------------------------------------------
`coverage_gate_ok()` returns False when the realised draw has a cell below the
redundancy floor. The activation pipeline (held, §1) must call this and BLOCK
publication of any derived figure from a draw that fails it — "reported, not
smoothed" means a thin draw stops the number reaching a surface, it does not
get quietly averaged away. This module provides the check; wiring it into the
publish gate is part of the held activation, registered not built here.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

# The curriculum/cohort axes we report realised counts against. The 9 hidden
# cohort axes (population_draw.Cohort) plus the two saas-observable axes the
# static book also carries, so a mixed activated book (static + SYN-*) reports
# coherently on the axes every customer has.
_COHORT_AXES = (
    "tenure", "accommodation", "cars", "nssec", "heating_fuel",
    "region", "green_stance", "price_sensitivity", "channel_pref",
)
_OBSERVABLE_AXES = ("segment", "consumption_band")

# Redundancy floor: a curriculum category realised fewer than this many times is
# a THIN cell (flagged, never smoothed). This mirrors the nested design's
# redundancy idea; it is a reporting DIAL (a flag threshold), never a target
# (R12) — it changes what we WARN about, never what the draw produces.
DEFAULT_REDUNDANCY_FLOOR = 2

# Joint thin floor: the director's ≥3-households-per-named-protected-cell tail
# floor (DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED_2026-07-27 §4). A JOINT
# cell realised below this at N=200 is a FINDING about the value knee surviving a
# real draw (ruling §3), NEVER a defect to smooth and NEVER a target to tune the
# draw toward (R12). Same DIAL semantics as the per-axis floor: it changes what
# we flag, never what the draw produces.
DEFAULT_JOINT_THIN_FLOOR = 3

# WHICH JOINTS ARE WORTH REPORTING (the agent's call, ruling §3). The learning-
# value frontier (docs/market_research/population_coverage/learning_value_
# frontier.json) is a CONCAVE curve: step 1 adds price_sensitivity (3 segments,
# marginal learning-value +0.226), step 2 adds tenure (→ 12 segments, marginal
# +0.221) — the last big marginal jump before the curve bends. Step 3
# (channel_pref → 36 segments) adds only +0.170 and, at N≈200, would expect ~5.5
# customers/cell before skew — below reporting usefulness (a finding in itself:
# we stop at the knee). So the ONE joint reported is the analytically-derived
# ~12-cell VALUE KNEE: price_sensitivity × tenure. Each entry: (name, axes,
# why). Adding a joint here is the only change needed to report another.
_REPORTED_JOINTS = (
    (
        "price_sensitivity_x_tenure",
        ("price_sensitivity", "tenure"),
        "the ~12-cell value knee (learning_value_frontier.json step 2: "
        "3×4 cells, marginal learning-value +0.221 — the last big jump "
        "before the frontier bends); first real test of whether it survives a draw",
    ),
)


def _axis_levels(axis: str, curriculum: Optional[dict]) -> tuple:
    """The FULL expected level set for an axis, so a joint grid is enumerable and
    an absent (0-count) cell is catchable — not just realised categories.

    Curriculum-driven axes (green_stance / price_sensitivity / channel_pref) take
    their levels from the director-set marginals (R13, read live); structural
    axes take theirs from the taxonomy tuples in `population_draw` (a schema fact,
    not a curriculum knob). Fail-closed: an axis whose level set cannot be
    resolved returns `()` — we then flag realised-thin cells but never claim a
    cell is 'absent' from a grid we cannot enumerate (never fabricate an
    expectation), exactly as the per-axis report does for un-enumerated axes.
    """
    expected = _expected_categories(curriculum, axis)
    if expected:
        return tuple(sorted(expected))
    try:  # lazy import: keep the SIM-truth generator off importers that only score
        from simulation import population_draw as _pd
    except Exception:
        return ()
    structural = {
        "tenure": _pd.TENURE_LEVELS,
        "accommodation": _pd.ACCOMMODATION_LEVELS,
        "cars": _pd.CARS_LEVELS,
        "nssec": _pd.NSSEC_LEVELS,
        "heating_fuel": _pd.HEATING_FUEL_LEVELS,
    }
    return tuple(structural.get(axis, ()))


@dataclass
class JointCoverage:
    """Realised cell counts for ONE reported joint (e.g. the ~12-cell value knee).

    `cells` maps a "cat1|cat2|…" key to its realised count for EVERY cell of the
    enumerated grid (including the zeros — an absent cell is a reported cell, not
    an omission). `thin_cells`/`absent_cells` are the findings; `findings` is the
    human-legible derivation (ruling §3: thin cells NAMED as findings).
    """

    name: str
    axes: tuple
    why: str
    thin_floor: int
    cells: dict                 # "cat1|cat2" -> realised count (whole grid, zeros included)
    n_cells_grid: int           # size of the enumerated grid (0 if un-enumerable)
    n_cells_filled: int         # cells with count > 0
    n_customers_scored: int     # customers with ALL joint axes present
    uniform_expected: float     # n_scored / n_cells_grid (a reference, NOT a target — R12)
    thinnest_cell: Optional[dict]   # {cell, count} — the worst realised cell
    thin_cells: list            # [{cell, count}] 0 < count < floor
    absent_cells: list          # [{cell}] count == 0 within the enumerated grid
    findings: list              # legible strings; thin/absent NAMED, knee-survival verdict

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "axes": list(self.axes),
            "why": self.why,
            "thin_floor": self.thin_floor,
            "n_cells_grid": self.n_cells_grid,
            "n_cells_filled": self.n_cells_filled,
            "n_customers_scored": self.n_customers_scored,
            "uniform_expected": round(self.uniform_expected, 2),
            "thinnest_cell": self.thinnest_cell,
            "thin_cells": self.thin_cells,
            "absent_cells": self.absent_cells,
            "findings": self.findings,
            "cells": self.cells,
        }


@dataclass
class AxisCoverage:
    axis: str
    counts: dict            # category -> realised count
    thin_categories: list   # categories present but below the floor
    absent_expected: list   # curriculum categories with ZERO realised count

    @property
    def worst_count(self) -> int:
        return min(self.counts.values()) if self.counts else 0


@dataclass
class CoverageReport:
    n_customers: int
    redundancy_floor: int
    axes: dict = field(default_factory=dict)   # axis -> AxisCoverage
    joints: dict = field(default_factory=dict) # joint name -> JointCoverage (§3 legibility)
    worst_cell: Optional[dict] = None          # {axis, category, count}
    thin_cells: list = field(default_factory=list)   # [{axis, category, count}]
    absent_cells: list = field(default_factory=list) # [{axis, category}] expected-but-zero

    @property
    def passes_floor(self) -> bool:
        """True iff NO expected curriculum category is absent and no realised
        category is below the redundancy floor."""
        return not self.thin_cells and not self.absent_cells

    def as_dict(self) -> dict:
        return {
            "n_customers": self.n_customers,
            "redundancy_floor": self.redundancy_floor,
            "worst_cell": self.worst_cell,
            "thin_cells": self.thin_cells,
            "absent_cells": self.absent_cells,
            "passes_floor": self.passes_floor,
            "axes": {
                a: {
                    "counts": c.counts,
                    "thin_categories": c.thin_categories,
                    "absent_expected": c.absent_expected,
                    "worst_count": c.worst_count,
                }
                for a, c in self.axes.items()
            },
            "joints": {name: j.as_dict() for name, j in self.joints.items()},
        }


def _axis_value(customer, axis: str):
    """Read `axis` from a SyntheticCustomer (cohort axis or top-level field)."""
    if axis in _OBSERVABLE_AXES:
        return getattr(customer, axis, None)
    cohort = getattr(customer, "cohort", None)
    if cohort is None:
        return None
    return getattr(cohort, axis, None)


def _expected_categories(curriculum: Optional[dict], axis: str) -> set:
    """Curriculum categories expected for an axis (so an absent one is caught).

    Only the director-set marginal axes have an authoritative expected set; for
    structural axes we have no curriculum enumeration, so 'absent' is not
    asserted (we can only flag a realised category as thin, not claim one is
    missing). Fail-closed: an unreadable curriculum yields an empty expected
    set, so we NEVER fabricate an expectation.
    """
    if not curriculum:
        return set()
    key_map = {
        "green_stance": "green_stance_marginals",
        "price_sensitivity": "price_sensitivity_marginals",
        "channel_pref": "channel_pref_marginals",
    }
    node = curriculum.get(key_map.get(axis, ""), {})
    value = node.get("value") if isinstance(node, dict) else None
    return set(value.keys()) if isinstance(value, dict) else set()


def _joint_coverage(
    customers: list,
    *,
    name: str,
    axes: tuple,
    why: str,
    thin_floor: int,
    curriculum: Optional[dict],
) -> JointCoverage:
    """Realised cell counts for one joint (the ~12-cell knee). Thin/absent cells
    are NAMED as findings (ruling §3), never smoothed or averaged (R15 fail-
    closed). A cell is scored only for customers carrying ALL joint axes; a
    customer missing any axis (e.g. a static-book customer with no cohort) is
    honestly excluded, never imputed onto the grid.
    """
    scored = []
    for c in customers:
        vals = [_axis_value(c, ax) for ax in axes]
        if all(v is not None for v in vals):
            scored.append(tuple(vals))

    # Enumerate the FULL grid so an absent cell is a reported zero, not an
    # omission. If any axis is un-enumerable (fail-closed), we still report
    # realised cells but cannot assert 'absent' against a grid we can't build.
    level_sets = [_axis_levels(ax, curriculum) for ax in axes]
    grid_enumerable = all(len(ls) > 0 for ls in level_sets)
    realised = Counter("|".join(t) for t in scored)

    cells: dict = {}
    if grid_enumerable:
        from itertools import product
        for combo in product(*level_sets):
            cells["|".join(combo)] = realised.get("|".join(combo), 0)
    else:  # only realised cells are known
        cells = dict(sorted(realised.items()))

    n_grid = len(cells)
    n_filled = sum(1 for v in cells.values() if v > 0)
    n_scored = len(scored)
    uniform = (n_scored / n_grid) if n_grid else 0.0

    thin = sorted(
        ({"cell": k, "count": v} for k, v in cells.items() if 0 < v < thin_floor),
        key=lambda d: (d["count"], d["cell"]),
    )
    absent = sorted(
        ({"cell": k} for k, v in cells.items() if v == 0),
        key=lambda d: d["cell"],
    ) if grid_enumerable else []
    thinnest = None
    for k, v in sorted(cells.items()):
        if thinnest is None or v < thinnest["count"]:
            thinnest = {"cell": k, "count": v}

    # DERIVED findings (ruling §3: thin cells NAMED; §3 knee-survival verdict). No
    # hardcoded cell names — each string is built from the realised draw.
    findings: list = []
    if grid_enumerable:
        if absent:
            findings.append(
                f"KNEE HOLE (fail-closed): {len(absent)}/{n_grid} cells of "
                f"{name} are ABSENT (0) at N_scored={n_scored}: "
                f"{', '.join(a['cell'] for a in absent)}. The analytic knee does "
                f"NOT fully realise here — reported, NOT smoothed."
            )
        if thin:
            findings.append(
                f"THIN: {len(thin)} cell(s) below the ≥{thin_floor} tail floor: "
                f"{', '.join(f'''{t['cell']}={t['count']}''' for t in thin)}. "
                f"Named as findings, not redistributed."
            )
        if not absent and not thin:
            findings.append(
                f"KNEE SURVIVES: all {n_grid} cells of {name} realised at "
                f"≥{thin_floor} (N_scored={n_scored}); thinnest "
                f"{thinnest['cell']}={thinnest['count']} vs uniform-expected "
                f"{uniform:.1f}. The analytic value knee survives a real draw."
            )
    else:
        findings.append(
            f"GRID UN-ENUMERABLE for {name}: reporting {n_filled} realised "
            f"cell(s) only; 'absent' not asserted (no fabricated expectation)."
        )

    return JointCoverage(
        name=name, axes=axes, why=why, thin_floor=thin_floor,
        cells=cells, n_cells_grid=n_grid, n_cells_filled=n_filled,
        n_customers_scored=n_scored, uniform_expected=uniform,
        thinnest_cell=thinnest, thin_cells=thin, absent_cells=absent,
        findings=findings,
    )


def population_coverage_report(
    customers: Iterable,
    *,
    redundancy_floor: int = DEFAULT_REDUNDANCY_FLOOR,
    joint_thin_floor: int = DEFAULT_JOINT_THIN_FLOOR,
    curriculum: Optional[dict] = None,
) -> CoverageReport:
    """Report realised cell counts vs the curriculum. Thin cells reported, not smoothed.

    `customers` is the run's drawn SIM-truth `SyntheticCustomer` stream with
    cohorts assigned (`draw_population(seed, assign_cohorts=True)`). Customers
    whose value for an axis is `None` (e.g. a static book customer with no
    cohort) are simply not counted on that axis — honestly absent, never imputed.
    """
    customers = list(customers)
    if curriculum is None:
        try:
            from simulation.population_draw import _load_cohort_curriculum
            curriculum = _load_cohort_curriculum()
        except Exception:
            curriculum = {}

    report = CoverageReport(n_customers=len(customers), redundancy_floor=redundancy_floor)

    for axis in _COHORT_AXES + _OBSERVABLE_AXES:
        counts = Counter(
            v for c in customers if (v := _axis_value(c, axis)) is not None
        )
        expected = _expected_categories(curriculum, axis)
        thin = sorted(cat for cat, n in counts.items() if n < redundancy_floor)
        absent = sorted(cat for cat in expected if counts.get(cat, 0) == 0)
        ac = AxisCoverage(
            axis=axis, counts=dict(counts), thin_categories=thin, absent_expected=absent
        )
        report.axes[axis] = ac
        for cat in thin:
            report.thin_cells.append({"axis": axis, "category": cat, "count": counts[cat]})
        for cat in absent:
            report.absent_cells.append({"axis": axis, "category": cat, "count": 0})

    # JOINT structure (ruling §3): make the realised cohort JOINT legible where it
    # matters — the ~12-cell value knee. Per-axis coverage can look full while a
    # joint cell is empty; the knee is where the frontier's marginal value lives.
    for jname, jaxes, jwhy in _REPORTED_JOINTS:
        report.joints[jname] = _joint_coverage(
            customers, name=jname, axes=jaxes, why=jwhy,
            thin_floor=joint_thin_floor, curriculum=curriculum,
        )

    # worst realised cell across all axes (the nested-design objective)
    worst = None
    for axis, ac in report.axes.items():
        for cat, n in ac.counts.items():
            if worst is None or n < worst["count"]:
                worst = {"axis": axis, "category": cat, "count": n}
    report.worst_cell = worst
    return report


def coverage_gate_ok(report: CoverageReport) -> bool:
    """The publish gate (§1.3): a draw that fails the floor must NOT publish.

    Returns False if any curriculum category is absent or any realised category
    is below the redundancy floor. The held activation pipeline calls this
    before letting any derived figure from the run reach a site surface.
    """
    return report.passes_floor
