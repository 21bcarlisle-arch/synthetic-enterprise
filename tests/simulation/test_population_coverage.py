"""Tests for the population coverage report (§1.3): realised cells vs curriculum,
thin cells reported not smoothed, and the publish gate.

The gate control is proven both ways: a well-covered draw passes; a draw with a
thin/absent cell fails (blocks publication), never silently smooths.
"""

from simulation.population_coverage import (
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
