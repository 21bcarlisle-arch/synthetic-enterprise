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


def population_coverage_report(
    customers: Iterable,
    *,
    redundancy_floor: int = DEFAULT_REDUNDANCY_FLOOR,
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
