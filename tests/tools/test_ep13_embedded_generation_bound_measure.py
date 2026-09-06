"""The control over `measure()` — the rung of the embedded-generation bound that nothing ran.

DEFECT THIS FILE EXISTS FOR, measured 2026-09-06 and written up in
`docs/staging/SEAT_RESULT_THE_TENTH_SUITE_CANNOT_SEE_THE_SUBJECT_AND_THE_CALLER_IT_TESTS_HAS_NO_TEST_OF_THE_PATH_THAT_CALLS_IT_2026-09-06.md`:

    `tools/ep13_embedded_generation_bound.measure()` is executed by nothing but `main()`, and no
    test runs `main()`.

`measure` is the one path on which this module loads the real Elexon demand and AGWS caches,
calls `tools.generate_grid_intensity_feed.fuel_mix()`, unpacks its seven-tuple, reads both NESO
series, takes the year intersection and produces `docs/observability/
ep13_embedded_generation_bound.json` — a PUBLISHED ARTEFACT. None of that was executed by any
test in the tree. The `fuel_mix` contract battery proved it from the other side: at spec
fingerprint `d7eb36a0b901` the 623-second suite beside this one came back `reaches_subject:
false` while both control suites stayed green. It cannot execute the subject on any path it
takes.

**THE NAME COLLISION IS HOW IT HID, and it is the reason this is a separate file rather than
six more tests in the old one.** `tests/tools/test_ep13_embedded_generation_bound.py:88` defines
its own helper `_measure`, called from six places, and that helper calls `measure_year` on
SYNTHETIC worlds. A reader — or a grep — looking for coverage of `measure` finds `_measure`
everywhere and stops. Putting the real-cache control in the same file would rebuild the exact
ambiguity that hid the gap for months; here, the filename says which `measure` is meant.

WHAT THIS FILE PROVES AND WHAT THE OLD ONE PROVES, kept apart on purpose:

  the old file   the INSTRUMENT is sound — a within-day third coordinate is detected, a noise
                 column is not, the placebos are cell-matched. Synthetic worlds, because on the
                 real series the right answer is not known and neither claim could be made.
  this file      the PRODUCER runs — the caches load, `fuel_mix` is on the path, the intersection
                 is taken, `main` writes the artefact, and the artefact's schema is what this
                 code emits. Real caches, because a synthetic world cannot prove any of it.

REUSE: `tests/tools/test_ep13_ccgt_level_ceiling.py::
test_the_published_artefact_carries_its_controls_and_its_reimplementation_verdict` is the nearest
existing row and is deliberately NOT extended to cover this. It reads the COMMITTED artefact and
asserts the keys it carries — which is a control over a file on disk, and stays green forever
after the producer that wrote it stops working, because nothing re-runs the producer. That is the
half this file adds: the artefact is compared against a run of the real thing, not read on its
own.

WHY THE RUN IS BOUNDED. An unbounded `measure()` is six years by five rungs by five null seeds
plus a thirty-cell resolution sweep, and it is not a thing a test suite can pay for on every
commit (the cost is measured in
`docs/staging/PREREG_ep13_embedded_generation_measure_cost.md` and its result). So `measure`
gained `only_years`, `grids` and `null_seeds` — and `only_years` FILTERS the intersection rather
than replacing it, which is what keeps the bounded run a control over the real thing rather than
a control over its own argument. **That property is argued in `measure`'s docstring and is NOT
provable from outside it**, for a reason `TestTheBoundCannotGrantAYearTheCachesDoNotCarry` states
in full rather than leaving to the reader; what carries the weight instead is `grids`, whose
effect on the returned dict is visible and asserted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sim import neso_carbon_intensity as neso
from sim import neso_embedded_generation as embedded
from tools import ep13_embedded_generation_bound as bound
from tools.generate_grid_intensity_feed import AGWS_CACHE, DEMAND_CACHE

ARTEFACT = bound.OUT_PATH

#: The four real series `measure()` is made of, each named so a refusal says WHICH one is absent
#: rather than "the caches". Two are `sim/cache` payloads reached through the feed module's own
#: constants — taken from there rather than restated, so a moved cache moves this with it.
#: `neso.CACHE_PATH` is RELATIVE, so it only resolves from the repository root; that is a
#: property of that module and not something this file may quietly paper over, so it is resolved
#: against `bound.PROJECT_DIR` here and the mismatch is left visible.
REAL_CACHES = {
    "elexon demand": Path(DEMAND_CACHE),
    "elexon AGWS": Path(AGWS_CACHE),
    "NESO carbon intensity": bound.PROJECT_DIR / neso.CACHE_PATH,
    "NESO embedded generation": Path(embedded.CACHE_PATH),
}

#: A year that cannot be in the intersection: the GB half-hourly record this company runs against
#: starts in 2016, and no cache here reaches back to it. Asked for alongside a year that MUST be
#: there, it is what turns the bounded run into a control over the filter.
IMPOSSIBLE_YEAR = "1999"


def _absent_caches() -> list[str]:
    return sorted(name for name, path in REAL_CACHES.items() if not path.is_file())


@pytest.fixture(scope="module")
def published() -> dict:
    if not ARTEFACT.is_file():
        pytest.skip(f"{ARTEFACT} has not been generated in this tree")
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def bound_year(published) -> str:
    """The year to re-measure: the LAST one the published artefact itself claims.

    NOT a literal, and not "the most recent year" computed from the clock. Either would key the
    control to today's answer. Keyed to the artefact instead, it states a property that is worth
    having on its own: *the producer can still measure the last year it published*. A cache that
    goes stale, an intersection that breaks, a settlement-period key format that drifts — each
    empties `data["years"]` and reds `TestMeasureExecutesTheRealCachePath` by name.
    """
    years = sorted(published["years"])
    assert years, "an artefact with no years scored is not a measurement"
    return years[-1]


@pytest.fixture(scope="module")
def real(bound_year) -> dict:
    """ONE bounded run of the real `measure()`, shared by every test below.

    Module scope because it is the expensive thing in this file and every consumer treats it as
    read-only. The bound is: the artefact's own last year (plus a year that cannot exist), the
    PUBLISHED grid, and one null seed. `bins` is left at the default, so `ceiling_3d` here is
    computed on exactly the grid the artefact was — which is what lets
    `TestThePublishedFigureIsReproducibleFromTheCaches` compare them at all.
    """
    absent = _absent_caches()
    if absent:
        pytest.skip(
            "the real series this measurement is made of are absent here: "
            + ", ".join(f"{name} ({REAL_CACHES[name]})" for name in absent)
        )
    return bound.measure(
        only_years=(bound_year, IMPOSSIBLE_YEAR),
        grids=(bound.SWEEP_GRIDS[1],),
        null_seeds=(bound.NULL_SEEDS[0],),
    )


class TestMeasureExecutesTheRealCachePath:
    """The gap itself: before this class, no test in the tree ran `measure` at all."""

    def test_the_producer_still_measures_the_last_year_its_own_artefact_claims(
        self, real, bound_year
    ):
        assert bound_year in real["years"], (
            f"{ARTEFACT.name} publishes {bound_year} and a fresh run of measure() does not "
            f"produce it — it produced {sorted(real['years'])}"
        )

    def test_the_shared_population_is_a_year_of_half_hours_and_splits_into_both_halves(
        self, real, bound_year
    ):
        """DEFECT: the intersection collapses and the rungs are fitted on a handful of readings.

        Every rung is scored on ONE population — the half hours where the shipped model, the
        published target, a positive demand reading, both base coordinates and an embedded
        reading all exist. If a cache is swapped, a key format drifts or a series arrives empty,
        that intersection thins toward nothing while every SHAPE assertion in this file stays
        green: the row is still a row, the rungs are still rungs, the controls still compute.
        This is the assertion that notices.

        Keyed to the calendar, not to today's count: a year holds 17,520 half hours (17,568 in a
        leap year), the split is by whole days, and both halves must be populations.
        """
        row = real["years"][bound_year]
        fit = row["control_fit_half_hours"]
        scored = row["control_scored_half_hours"]
        assert fit > 4_000, fit
        assert scored > 4_000, scored
        assert 8_000 < fit + scored <= 17_616, (fit, scored)

    def test_every_rung_the_artefact_names_is_produced_and_carries_its_own_controls(
        self, real, bound_year, published
    ):
        """The rungs are named in the artefact's `rungs` block for a reader. This asserts the
        block is a description of what was computed rather than prose beside it."""
        row = real["years"][bound_year]
        for rung in published["rungs"]:
            assert rung in row, f"the artefact describes rung {rung!r} and measure() emits no such key"
            assert "held_out" in row[rung] and "in_sample" in row[rung], rung
        assert set(row["controls"]) == set(published["years"][bound_year]["controls"])

    def test_the_oracle_unreachability_verdict_is_computed_against_the_real_feed_source(
        self, real
    ):
        """The sibling suite proves `oracle_is_unreachable_from` WALKS AN AST correctly. Nothing
        proved that `measure` calls it on the real file — a verdict published from a function
        nobody runs on a path nobody takes is exactly this file's subject."""
        assert real["oracle_reaches_the_published_feed"] is False


class TestTheBoundCannotGrantAYearTheCachesDoNotCarry:
    """R15: the bounded run must be a control over `measure`, not over its own argument.

    WHAT IS ESTABLISHED HERE, AND WHAT IS NOT — written this way because the first draft of this
    class claimed the second and proved only the first, and the mutation that would have shown
    the difference does not fire.

    `only_years` is what makes this file affordable. The way it could be worthless is if it
    SELECTED the years rather than filtering the intersection: a run asking for one year would
    then report that year whatever the caches held, and every assertion in this file would be
    about the argument rather than about the series. So the fixture asks for a year that must be
    there AND one that cannot be, in the same call.

    **That does not distinguish the two, and cannot.** Replace `measure`'s filter with
    `years = list(only_years)` and the returned dict is IDENTICAL: `measure_year("1999", ...)`
    finds no fit half hours, raises `NesoIntensityUnavailable`, and the year loop's
    `except ...: continue` swallows it. The selector mutation is an EQUIVALENCE from outside this
    function, not a survivor — and the honest reason is that the swallow makes it one. Nothing
    short of `measure` reporting the intersection it took could tell them apart, and adding that
    would change a published artefact's schema to prove a property of a test's argument.

    What the leg below DOES kill is the swallow itself: narrow that `except` and the same call
    raises instead of returning. That is the property worth having — a year the caches cannot
    support costs a row, not the run — and it is stated under its own name rather than borrowed
    for a claim it does not support.
    """

    def test_a_year_the_caches_cannot_support_costs_a_row_and_not_the_whole_run(self, real):
        """DEFECT: one unmeasurable year takes the other five down with it.

        `measure` asks `measure_year` for every year the series share, and a year can fail to
        split into fit and score halves for reasons that are nobody's fault — a cache refreshed
        mid-year, a series that starts in November. The loop swallows exactly three exceptions
        and continues. Narrow that tuple and this call raises rather than returning.
        """
        assert IMPOSSIBLE_YEAR not in real["years"]
        assert real["years"], "the run returned no rows at all"

    def test_the_bound_narrows_the_run_to_exactly_what_the_caches_and_the_caller_agree_on(
        self, real, bound_year
    ):
        assert set(real["years"]) == {bound_year}

    def test_the_sweep_is_bounded_by_the_same_call_and_reports_the_grid_it_ran(self, real):
        """`grids` has to reach `sweep`, or the bounded run silently pays for all five
        resolutions and this file's cost is not what its docstring says it is."""
        label = "x".join(str(axis) for axis in bound.SWEEP_GRIDS[1])
        assert set(real["resolution_sweep"]) == {label}


class TestMeasureReallyCallsWhatTheArtefactSaysItIsMadeOf:
    """REACHABILITY, the poison round done as two ordinary tests.

    A green run of `measure()` proves the function returns a dict. It does NOT prove `fuel_mix`
    is on the path — stub `fuel_mix` out and every shape assertion above still passes, because
    the shipped shape's numbers are not what those assertions read. That is the same
    "survived_all" trap the battery that found this defect exists to name: green means the
    subject was reached OR the subject was never reached, and only a poison round tells them
    apart.

    So each leg breaks ONE of the things `measured_from` claims and asserts `measure` dies of it.
    They are worth more than they look: a `fuel_mix` whose failure this function swallowed would
    publish a bound built on a shipped shape that silently lost its imports, its coal capacity
    and its thermal floors.
    """

    def _skip_without_caches(self):
        absent = _absent_caches()
        if absent:
            pytest.skip("the real series are absent here: " + ", ".join(absent))

    def test_a_demand_cache_that_cannot_be_aggregated_is_not_swallowed(self, monkeypatch):
        """The FIRST thing `measure` does, and the cheapest leg — it fires after one cache
        parse. Proves the demand series is read here and not only by the caller."""
        self._skip_without_caches()
        import sim.grid_carbon_intensity as gci

        def refuse(*_a, **_k):
            raise AssertionError("the demand cache was aggregated by measure()")

        monkeypatch.setattr(gci, "aggregate_demand", refuse)
        with pytest.raises(AssertionError, match="aggregated by measure"):
            bound.measure(
                only_years=(IMPOSSIBLE_YEAR,), grids=(), null_seeds=(bound.NULL_SEEDS[0],)
            )

    def test_a_fuel_mix_that_raises_is_not_swallowed(self, monkeypatch):
        """THE LEG THE BATTERY WAS LOOKING FOR. `fuel_mix` is imported inside `measure`, so the
        name is resolved from the feed module at call time and patching it there is what a
        caller-side poison would do.

        `only_years=(IMPOSSIBLE_YEAR,)` costs nothing beyond the loads: the filter empties the
        year list, so if this leg ever goes green it means `fuel_mix` was reached and its failure
        was absorbed — not that the work was skipped.
        """
        self._skip_without_caches()
        import tools.generate_grid_intensity_feed as feed

        def refuse(*_a, **_k):
            raise AssertionError("fuel_mix() was called by measure()")

        monkeypatch.setattr(feed, "fuel_mix", refuse)
        with pytest.raises(AssertionError, match="called by measure"):
            bound.measure(
                only_years=(IMPOSSIBLE_YEAR,), grids=(), null_seeds=(bound.NULL_SEEDS[0],)
            )


class TestMainWritesThePublishedArtefact:
    """`main` is `measure`'s only caller and was itself run by nothing.

    Its body is a write and a print loop, and the print loop reaches into fourteen distinct keys
    of every row (`row['baseline']['correlation']`, `row['ceiling_3d']`, `c['fit_bites_in_sample']`
    …). A key renamed anywhere in `measure_year` or `verdicts` turns the published producer into
    a `KeyError` at the moment someone regenerates the artefact, and until this class existed
    nothing in the tree would have said so first.

    `measure` is stubbed here to hand back the REAL row the module fixture already computed —
    the data is not synthetic, the second run is what is avoided. What is under test is `main`.
    """

    @pytest.fixture
    def written(self, monkeypatch, tmp_path, real):
        out = tmp_path / "ep13_embedded_generation_bound.json"
        monkeypatch.setattr(bound, "OUT_PATH", out)
        monkeypatch.setattr(bound, "measure", lambda: real)
        assert bound.main([]) == 0
        return out

    def test_main_writes_the_artefact_it_publishes_and_it_round_trips(self, written, real):
        assert written.is_file(), "main() returned 0 and wrote nothing"
        assert json.loads(written.read_text(encoding="utf-8")) == json.loads(
            json.dumps(real, default=str)
        )

    def test_main_creates_the_directory_it_publishes_into(self, monkeypatch, tmp_path, real):
        """`OUT_PATH.parent.mkdir(parents=True, ...)` — the leg that makes regenerating the
        artefact work in a checkout where `docs/observability/` does not yet exist."""
        out = tmp_path / "nested" / "deeper" / "artefact.json"
        monkeypatch.setattr(bound, "OUT_PATH", out)
        monkeypatch.setattr(bound, "measure", lambda: real)
        assert bound.main([]) == 0
        assert out.is_file()

    def test_main_prints_a_line_for_every_year_and_every_sweep_grid(
        self, monkeypatch, tmp_path, real, capsys, bound_year
    ):
        monkeypatch.setattr(bound, "OUT_PATH", tmp_path / "artefact.json")
        monkeypatch.setattr(bound, "measure", lambda: real)
        assert bound.main([]) == 0
        printed = capsys.readouterr().out
        assert bound_year in printed
        for label in real["resolution_sweep"]:
            assert label in printed, f"the sweep ran {label} and main() did not report it"
        assert "wrote" in printed


class TestThePublishedArtefactIsWhatThisProducerProduces:
    """The other half of the defect: an artefact on disk and a producer nobody runs cannot be
    known to correspond. Both of these compare a LIVE run against the COMMITTED file."""

    def test_the_artefacts_top_level_schema_is_the_one_measure_emits(self, real, published):
        assert set(real) == set(published), (
            "the committed artefact and a fresh run of its producer disagree on their top-level "
            f"keys: only in the artefact {sorted(set(published) - set(real))}, only in the run "
            f"{sorted(set(real) - set(published))}"
        )

    def test_the_artefacts_rows_carry_exactly_the_keys_measure_year_emits(
        self, real, published, bound_year
    ):
        assert set(real["years"][bound_year]) == set(published["years"][bound_year])

    def test_the_declared_grid_is_the_grid_the_rungs_were_scored_on(self, real, bound_year):
        """DEFECT: `grid` is a hand-written block beside numbers computed from the constants, so
        it can say 12x4x3 while the rungs were partitioned on something else. Multiplied out, it
        is the cell count the 3-D rung must report."""
        grid = real["grid"]
        assert grid["u"] * grid["v"] * grid["w"] == real["years"][bound_year]["ceiling_3d"]["cells"]


class TestThePublishedFigureIsReproducibleFromTheCaches:
    """The strongest thing this file says, and the one most likely to red on someone.

    `measure` is deterministic given its inputs: the split is by day-of-month, the placebo seed
    is fixed, and `ceiling_3d` does not read a null seed at all. So a fresh run on the same
    caches at the same grid must return the published correlation EXACTLY. When this reds, one of
    two things is true and the message says which to check: the code that produces the figure has
    moved, or the caches under it have been refreshed and the artefact is stale. Both are things
    a reader of `docs/observability/ep13_embedded_generation_bound.json` needs told, and neither
    was visible from inside the tree before.

    The remedy for the second is `python3 -m tools.ep13_embedded_generation_bound`, which is the
    producer this file exists to keep runnable.
    """

    def test_the_published_ceiling_for_that_year_is_reproduced_by_a_fresh_run(
        self, real, published, bound_year
    ):
        fresh = real["years"][bound_year]["ceiling_3d"]["held_out"]["correlation"]
        was = published["years"][bound_year]["ceiling_3d"]["held_out"]["correlation"]
        assert fresh == pytest.approx(was, abs=1e-9), (
            f"{bound_year} ceiling_3d: artefact {was!r}, fresh run {fresh!r}. Either the "
            "producer moved or the caches did; regenerate with "
            "`python3 -m tools.ep13_embedded_generation_bound`."
        )

    def test_the_published_within_day_gain_is_reproduced_by_a_fresh_run(
        self, real, published, bound_year
    ):
        """The gain is THE NUMBER this whole module publishes — the one the atom's next decision
        rests on. Asserted separately from the ceiling because it is a DIFFERENCE of two rungs,
        and a change that moved both equally would leave the ceiling test green."""
        fresh = real["years"][bound_year]["embedded_gain_within_day"]
        was = published["years"][bound_year]["embedded_gain_within_day"]
        assert fresh == pytest.approx(was, abs=1e-9), (
            f"{bound_year} embedded_gain_within_day: artefact {was!r}, fresh run {fresh!r}"
        )
