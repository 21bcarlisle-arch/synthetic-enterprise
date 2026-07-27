"""Tests for the population coverage report (§1.3): realised cells vs curriculum,
thin cells reported not smoothed, and the publish gate.

The gate control is proven both ways: a well-covered draw passes; a draw with a
thin/absent cell fails (blocks publication), never silently smooths.
"""

import types

from simulation.population_coverage import (
    DEFAULT_JOINT_THIN_FLOOR,
    DEFAULT_REDUNDANCY_FLOOR,
    coverage_gate_ok,
    population_coverage_report,
)
from simulation.population_draw import draw_population


def _drawn(seed, **kw):
    # cohorts assigned so the report can read the 9 hidden axes
    return draw_population(seed, assign_cohorts=True, **kw)


def test_report_counts_realised_cells():
    pop = _drawn(20260724)
    rep = population_coverage_report(pop)
    assert rep.n_customers == len(pop)
    # every drawn customer has segment + the cohort axes populated
    assert sum(rep.axes["segment"].counts.values()) == len(pop)
    assert sum(rep.axes["tenure"].counts.values()) == len(pop)
    # a worst cell is always identified (the nested-design objective)
    assert rep.worst_cell is not None
    assert rep.worst_cell["count"] >= 1


def test_thin_cells_reported_not_smoothed():
    # a tiny draw WILL leave thin/absent curriculum cells; they must surface,
    # and the realised counts must still sum to the true drawn size (no
    # redistribution/imputation happened)
    pop = _drawn(20260724, acquisitions_per_year_lambda=0.4)
    rep = population_coverage_report(pop, redundancy_floor=3)
    assert (rep.thin_cells or rep.absent_cells)  # thinness surfaced
    total = sum(rep.axes["segment"].counts.values())
    assert total == len(pop)  # nothing smoothed away
    assert not coverage_gate_ok(rep)  # a thin draw does not get to publish


def test_gate_passes_a_well_covered_curriculum_draw():
    # a large draw covers every curriculum marginal category at redundancy 1+
    pop = _drawn(20260724, acquisitions_per_year_lambda=40.0)
    rep = population_coverage_report(pop, redundancy_floor=1)
    # every curriculum-enumerated axis has no ABSENT expected category
    assert rep.absent_cells == []
    assert coverage_gate_ok(rep) is True


def test_absent_cells_never_fabricated_when_curriculum_unreadable():
    pop = _drawn(20260724)
    rep = population_coverage_report(pop, curriculum={})  # no curriculum
    # with no curriculum we cannot claim any category is 'absent'
    assert rep.absent_cells == []


def test_static_customer_without_cohort_not_imputed():
    # a customer with no cohort contributes to observable axes only, never
    # imputed onto a hidden axis
    class _Static:
        segment = "resi"
        consumption_band = "MEDIUM"
        cohort = None

    rep = population_coverage_report([_Static()])
    assert rep.axes["segment"].counts == {"resi": 1}
    assert rep.axes["tenure"].counts == {}  # honestly absent, not imputed


def test_default_floor_is_a_dial_not_a_target():
    assert DEFAULT_REDUNDANCY_FLOOR >= 1


# ─────────────────────────────────────────────────────────────────────────────
# CA2 — the ~12-cell VALUE KNEE (price_sensitivity × tenure) joint (ruling §3).
# Thin/absent joint cells are NAMED as findings, never smoothed (R15 both ways).
# ─────────────────────────────────────────────────────────────────────────────
_PS = ("high", "medium", "low")
_TEN = ("own_outright", "own_mortgage", "private_rent", "social_rent")
_KNEE = "price_sensitivity_x_tenure"


def _cust(ps, tenure):
    """A minimal customer carrying only the two knee axes on its cohort."""
    cohort = types.SimpleNamespace(price_sensitivity=ps, tenure=tenure)
    return types.SimpleNamespace(cohort=cohort, segment="resi", consumption_band="MEDIUM")


def _population_from_grid(counts):
    """counts: {(ps, tenure): n} -> a flat customer list realising exactly that."""
    pop = []
    for (ps, tenure), n in counts.items():
        pop.extend(_cust(ps, tenure) for _ in range(n))
    return pop


def _full_grid_counts(n_per_cell=4):
    return {(ps, t): n_per_cell for ps in _PS for t in _TEN}


def test_knee_joint_is_reported_at_twelve_cells():
    rep = population_coverage_report(_population_from_grid(_full_grid_counts()))
    assert _KNEE in rep.joints
    j = rep.joints[_KNEE]
    assert j.n_cells_grid == 12          # 3 price_sensitivity × 4 tenure
    assert set(j.axes) == {"price_sensitivity", "tenure"}


def test_knee_full_draw_not_false_flagged():
    # every cell at ≥ the tail floor: NO thin/absent finding (no false positive)
    counts = _full_grid_counts(n_per_cell=DEFAULT_JOINT_THIN_FLOOR + 1)
    j = population_coverage_report(_population_from_grid(counts)).joints[_KNEE]
    assert j.thin_cells == []
    assert j.absent_cells == []
    assert any("KNEE SURVIVES" in f for f in j.findings)


def test_knee_thin_cell_reported_not_smoothed():
    # MUTATION: one cell below the floor while the rest are healthy.
    counts = _full_grid_counts(n_per_cell=DEFAULT_JOINT_THIN_FLOOR + 2)
    counts[("low", "social_rent")] = 1  # plant a thin cell (< floor 3)
    j = population_coverage_report(_population_from_grid(counts)).joints[_KNEE]
    # it SURFACES as a named thin finding (fail-closed), not smoothed
    assert {"cell": "low|social_rent", "count": 1} in j.thin_cells
    assert any("low|social_rent=1" in f and "THIN" in f for f in j.findings)
    # NOT redistributed: the planted count stays 1 and the grid total is exact
    assert j.cells["low|social_rent"] == 1
    assert sum(j.cells.values()) == j.n_customers_scored


def test_knee_absent_cell_surfaces_as_finding():
    # MUTATION: a full HOLE — one cell has zero, others healthy.
    counts = _full_grid_counts(n_per_cell=DEFAULT_JOINT_THIN_FLOOR + 1)
    del counts[("high", "private_rent")]  # 0 realised for this cell
    j = population_coverage_report(_population_from_grid(counts)).joints[_KNEE]
    assert {"cell": "high|private_rent"} in j.absent_cells
    assert any("KNEE HOLE" in f and "high|private_rent" in f for f in j.findings)
    assert j.cells["high|private_rent"] == 0        # reported zero, not omitted
    assert j.n_cells_filled == 11


def test_knee_cells_sum_to_scored_nothing_imputed():
    # a real draw: joint cell counts sum to the scored customers exactly
    pop = _drawn(20260724, acquisitions_per_year_lambda=40.0)
    j = population_coverage_report(pop).joints[_KNEE]
    assert sum(j.cells.values()) == j.n_customers_scored
    # a customer with no cohort is excluded, never imputed onto the grid
    pop2 = list(pop) + [types.SimpleNamespace(cohort=None, segment="resi")]
    j2 = population_coverage_report(pop2).joints[_KNEE]
    assert j2.n_customers_scored == j.n_customers_scored  # the cohort-less one dropped


def test_knee_grid_unenumerable_never_fabricates_absent():
    # with no curriculum, price_sensitivity has no expected level set -> the joint
    # grid is un-enumerable -> we report realised cells but NEVER claim 'absent'
    counts = _full_grid_counts()
    del counts[("high", "private_rent")]
    j = population_coverage_report(
        _population_from_grid(counts), curriculum={}
    ).joints[_KNEE]
    assert j.absent_cells == []  # no fabricated expectation
    assert any("UN-ENUMERABLE" in f for f in j.findings)


def test_joint_thin_floor_is_a_dial_not_a_target():
    assert DEFAULT_JOINT_THIN_FLOOR >= 1
    # the floor changes only what is FLAGGED, never the realised counts
    counts = _full_grid_counts(n_per_cell=4)
    strict = population_coverage_report(
        _population_from_grid(counts), joint_thin_floor=5
    ).joints[_KNEE]
    loose = population_coverage_report(
        _population_from_grid(counts), joint_thin_floor=2
    ).joints[_KNEE]
    assert strict.cells == loose.cells        # same draw, same counts
    assert strict.thin_cells and not loose.thin_cells  # only the flag moved
