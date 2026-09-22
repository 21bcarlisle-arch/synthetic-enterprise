import pytest
from saas.customers import get_customer
from simulation.weather_inputs import (
    load_weather_means,
    lookback_mean_temps,
    weather_means_for_customer,
)


def test_load_weather_means_reads_existing_csv():
    means = load_weather_means("C1")
    assert means["2016-01-01"] == 4.6
    assert means["2016-01-02"] == 9.2


def test_load_weather_means_missing_file_returns_empty():
    assert load_weather_means("DOES_NOT_EXIST") == {}


def test_weather_means_for_customer_gives_two_premises_in_one_place_one_sky():
    """C5 (SME, London) sits in C1's cell, so it reads C1's sky.

    REWRITTEN 2026-09-21 with the seam migration, and the old form is the point of the rewrite: it
    asserted `c5_means["2016-01-01"] == 4.6`, which was ERA5's reading at C1's own coordinate out of
    `sim/weather_data/C1.csv`. The premise now reads the WORLD's weather for the cell it sits in
    (HadUK 1 km + the cell's climatology), so that literal is a different number — and pinning any
    literal here was always keying the control to today's answer rather than to the property, which
    is that two premises in one place cannot get two skies.
    """
    c5_means = weather_means_for_customer(get_customer("C5"))
    c1_means = weather_means_for_customer(get_customer("C1"))
    assert c5_means == c1_means
    assert c5_means, "London resolves no weather at all — the store has lost the book's own cells"


def test_weather_means_for_customer_gives_the_gas_leg_its_electricity_twin_s_sky():
    c2g_means = weather_means_for_customer(get_customer("C2g"))
    c2_means = weather_means_for_customer(get_customer("C2"))
    assert c2g_means == c2_means


def test_lookback_mean_temps_returns_window_before_term_start():
    weather_means = {"2016-01-01": 1.0, "2016-01-02": 2.0, "2016-01-03": 3.0}
    temps = lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2)
    assert sorted(temps) == [1.0, 2.0]


def test_lookback_mean_temps_returns_none_when_window_has_no_data():
    weather_means = {"2020-01-01": 5.0}
    assert lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2) is None


from simulation.weather_inputs import (_has_archive, _weather_source_customer_id,
                                       weather_source_customers, WEATHER_DATA_DIR)


def test_weather_data_dir_constant():
    assert WEATHER_DATA_DIR == "sim/weather_data"


def test_weather_source_c1_resolves_to_c1():
    from saas.customers import CUSTOMERS
    c1 = next(c for c in CUSTOMERS if c["customer_id"] == "C1")
    assert _weather_source_customer_id(c1) == "C1"


def test_weather_source_c5_resolves_to_london_customer():
    from saas.customers import CUSTOMERS
    c5 = next(c for c in CUSTOMERS if c["customer_id"] == "C5")
    result = _weather_source_customer_id(c5)
    assert result in ("C1", "C2", "C3", "C4")


def test_weather_source_unknown_location_returns_self():
    customer = {"customer_id": "X99", "location": {"lat": 0.0, "lon": 0.0, "region": "Unknown"}}
    result = _weather_source_customer_id(customer)
    assert result == "X99"


def test_load_weather_means_returns_dict():
    means = load_weather_means("C1")
    assert isinstance(means, dict)


def test_lookback_mean_temps_length_matches_window():
    weather_means = {"2016-01-01": 1.0, "2016-01-02": 2.0, "2016-01-03": 3.0}
    temps = lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2)
    assert len(temps) == 2


def test_weather_data_dir_is_string():
    assert isinstance(WEATHER_DATA_DIR, str)


# ---------------------------------------------------------------------------
# W1_14: the weather-source predicate asks the PROPERTY (a CSV on disk), not the
# PROXY (commodity + segment) it read until 2026-09-20.
#
# The first two controls BIND THEIR OWN ROSTER, and that is the whole design. On
# the LIVE supply book the archived ids (C1/C2/C3) precede the un-archived ones
# (C7/C8/C9) at the same three coordinates, so the RESOLUTION the proxy produces
# is right for the wrong reason and all four pre-existing live-roster controls
# stay green when the repair is reverted (measured 2026-09-20, by mutation). The
# discriminating pair is bound so no acquisition, world-repair or reordering can
# take the subject away.
#
# The third IS on the live roster, deliberately, and it fires too — because
# MEMBERSHIP of the source list is observable there even when resolution is not.
# That is the split worth keeping: a live-roster control can see that C9 is named
# a weather source with no file behind it; only a bound pair can see which id a
# premise actually resolves to when both sit at one coordinate.
# ---------------------------------------------------------------------------

LONDON = {"lat": 51.5074, "lon": -0.1278, "region": "London"}


def test_a_premise_with_no_csv_cannot_be_a_weather_source_however_early_it_sits():
    """DEFECT: resolving a premise to a customer_id that holds no archive. That is not an error —
    `load_weather_means` returns an EMPTY DICT for a missing file, so the premise silently gets no
    weather at all, with nothing on any surface saying so."""
    roster = [
        # No CSV, and FIRST — the position C7/C8/C9 do not occupy on the live book.
        {"customer_id": "Z9", "commodity": "electricity", "segment": "resi", "location": LONDON},
        {"customer_id": "C1", "commodity": "electricity", "segment": "resi", "location": LONDON},
    ]
    premise = {"customer_id": "P1", "location": dict(LONDON)}

    # The branch CAN be taken: the proxy this repair replaced would have picked Z9 here...
    proxy_sources = [c for c in roster
                     if c["commodity"] == "electricity" and c["segment"] == "resi"]
    assert proxy_sources[0]["customer_id"] == "Z9", "the bound pair no longer discriminates"
    # ...and Z9 really does yield nothing, silently, which is the harm.
    assert not _has_archive("Z9")
    assert load_weather_means("Z9") == {}

    assert _weather_source_customer_id(premise, roster=roster) == "C1"


def test_an_archived_premise_is_a_source_whatever_its_commodity_and_segment():
    """DEFECT: the mirror — an archive that exists and cannot be reached. Birmingham and Teesside
    each hold two premises at one identical coordinate and neither is resi electricity, so under
    the proxy an archive pulled for the first could never answer the second."""
    roster = [
        {"customer_id": "C1", "commodity": "gas", "segment": "I&C", "location": LONDON},
    ]
    premise = {"customer_id": "P2", "location": dict(LONDON)}

    assert not [c for c in roster
                if c["commodity"] == "electricity" and c["segment"] == "resi"], (
        "the bound roster no longer excludes its source under the proxy"
    )
    assert _has_archive("C1"), "C1's archive is the witness this control needs"
    assert [c["customer_id"] for c in weather_source_customers(roster)] == ["C1"]
    assert _weather_source_customer_id(premise, roster=roster) == "C1"


def test_the_live_book_names_every_source_it_holds_and_no_id_without_a_file():
    """DEFECT: the source list drifting from what is on disk — the two halves above, on the real
    roster. This cannot catch the ORDER defect (that is what the bound pairs are for); what it
    pins is that the list is a statement about files, so a pull landing or a CSV going missing
    moves it."""
    sources = {c["customer_id"] for c in weather_source_customers()}
    assert sources, "the book resolves no weather at all"
    for cid in sources:
        assert _has_archive(cid), f"{cid} is a weather source with no archive on disk"
    for cid in ("C7", "C8", "C9", "C_IC1", "C_IC2"):
        assert not _has_archive(cid) or cid in sources
    assert "C7" not in sources, (
        "C7 is resi electricity and holds no CSV — it is back in the source list, so the proxy "
        "has returned"
    )


# ---------------------------------------------------------------------------
# W1_14 step 1 (2026-09-21): the demand-shape and forward-price legs read the
# PER-CELL STORE, not the four per-property archives.
#
# THE DEFECT THESE EXIST FOR. From 2026-09-17 the fabric physics leg read the
# per-cell store and these two legs did not, so ONE premise's demand was
# generated against its cell's sky and its shape adjusted — and its forward
# temperature priced — against a per-property ERA5 archive resolved by exact
# `location` match. Two weather sources for one household, disagreeing by
# +1.19 C on the mean at London, and nothing anywhere able to notice: both legs
# returned numbers, and an unadjusted shape looks exactly like a shape whose
# weather said no adjustment was needed.
# ---------------------------------------------------------------------------

from sim.weather_world import WeatherWorld, WeatherWorldRefusal  # noqa: E402
from simulation import weather_inputs as wi  # noqa: E402
from simulation.fabric_demand_path import WeatherWorldSource  # noqa: E402


def test_the_shape_leg_reads_the_world_and_not_the_per_property_archive():
    """DEFECT: resolving a premise to `sim/weather_data/{id}.csv` — the design the director refused,
    under which two households in one cell get two skies.

    Keyed to AGREEMENT WITH THE WORLD, not to a temperature: the store may be rebuilt, corrected or
    extended and this stays green. What it cannot survive is the series coming from anywhere but the
    cell the premise sits in.
    """
    c1 = get_customer("C1")
    verdict = wi.cell_weather_for_customer(c1)
    world = wi.shared_world()
    assert verdict.cell == world.cell_id_for(c1["location"]["lat"], c1["location"]["lon"])
    from_the_world = {row["date"]: row[wi.TEMPERATURE_FIELD]
                      for row in world.for_cell(verdict.cell)}
    assert weather_means_for_customer(c1) == from_the_world

    # ...and the archive really is a DIFFERENT reading, so the leg above is not vacuous. If a
    # future store rebuild ever made the two identical, this control has gone blind and says so
    # rather than passing.
    archive = load_weather_means("C1")
    assert archive, "C1's archive is the witness this non-vacuity check needs"
    assert any(archive[d] != from_the_world[d] for d in archive if d in from_the_world), (
        "the cell store and the per-property archive now read identically at C1, so the control "
        "above can no longer tell which source the shape leg read"
    )


def test_the_physics_leg_and_the_shape_leg_send_a_premise_to_the_same_cell():
    """DEFECT: two resolution rules for one question — which sky this household had.

    This is the control that would have caught the state this migration ended, and it is keyed to
    the two legs AGREEING rather than to either answer. It walks the live book because the defect
    was a whole-book property: the physics leg said `E529N0180` and the shape leg said `C1`.
    """
    source = WeatherWorldSource.load()
    resolved, refused = [], []
    for customer in wi.CUSTOMERS:
        mine = wi.cell_weather_for_customer(customer, world=source.world)
        theirs = source.site_for(customer)
        if mine.cell is None:
            refused.append(customer["customer_id"])
            assert not theirs.startswith("E"), (
                f"{customer['customer_id']}: the shape leg refuses and the physics leg resolved "
                f"{theirs} — one premise, two answers about which sky it had"
            )
        else:
            resolved.append(customer["customer_id"])
            assert mine.cell == theirs, (
                f"{customer['customer_id']}: shape leg reads {mine.cell}, physics leg reads "
                f"{theirs}"
            )
    # BOTH BRANCHES REACHABLE, asserted over the partition rather than one leg each: a resolver
    # that refused every premise, or resolved every premise, would satisfy every assertion above.
    assert resolved and refused, (
        f"the book no longer exercises both branches ({len(resolved)} resolved, {len(refused)} "
        "refused), so this control passes without testing the disagreement it exists for"
    )


def test_a_premise_the_store_cannot_reach_gets_a_named_refusal_not_a_silent_empty_series():
    """DEFECT: an empty series that says nothing. `_weather_adjusted_shape_fn` falls back to the
    UNADJUSTED base shape for any date it has no weather for, so a premise 7.4 km outside the store
    and a premise with a complete sky are indistinguishable downstream — a declared `None` and a
    silent `None` collapsing into the flattering branch.

    C_IC1/C_IC2 (Birmingham) are the live instance. The refusal must be clearable by whoever reads
    it, which means naming the cell and the per-cell remedy — never a per-property pull.
    """
    world = wi.shared_world()
    birmingham = next(c for c in wi.CUSTOMERS if c["customer_id"] == "C_IC1")
    verdict = wi.cell_weather_for_customer(birmingham, world=world)
    assert verdict.series == {} and verdict.cell is None
    assert verdict.refusal, "the premise got no weather and no reason: this is the silent failure"
    assert "km from the nearest cell" in verdict.refusal
    assert "needs its cell adding" in verdict.refusal
    assert "pull that coordinate" not in verdict.refusal, (
        "the refusal is recruiting the reader into the per-property design the director refused"
    )

    register = wi.weather_refusals_for_book(wi.CUSTOMERS, world=world)
    # THE REGISTER CANNOT DISAGREE WITH THE SERIES. Two surfaces answering one question is the
    # shape this whole migration existed to remove; a register built by a second rule would be it.
    empty = {c["customer_id"] for c in wi.CUSTOMERS
             if not wi.cell_weather_for_customer(c, world=world).series}
    assert set(register) == empty
    assert "C_IC1" in register and register["C_IC1"] == verdict.refusal


def test_a_premise_with_no_coordinate_says_so_in_its_own_sentence():
    """DEFECT: sending someone to extend the store for a premise no store build can help. A
    coordinate-less premise needs a coordinate at the DRAW, and `(0.0, 0.0)` would send them to the
    Gulf of Guinea."""
    verdict = wi.cell_weather_for_customer({"customer_id": "P0", "location": {}})
    assert verdict.cell is None and verdict.series == {}
    assert "no coordinate" in verdict.refusal and "at the draw" in verdict.refusal
    assert "build_weather_world" not in verdict.refusal


def test_a_cell_holding_temperature_and_no_cloud_still_answers_the_temperature_question():
    """DEFECT: asking completeness over five fields when the caller reads one. 8 of the store's 221
    cells hold temperature and no wind, cloud or precipitation; the physics leg must refuse them and
    this leg must not, or a real 1 km temperature reading is thrown away for a wind column nobody
    asked for."""
    class _HoledWorld:
        cells = {}

        def cell_id_for(self, lat, lon):
            return "E001N0001"

        def for_cell(self, cell, start=None, end=None):
            return [{"date": "2022-01-01", "temperature_mean_c": 3.5,
                     "cloud_cover_pct": float("nan")}]

    premise = {"customer_id": "P9", "location": {"lat": 51.5, "lon": -0.1}}
    holed = _HoledWorld()
    assert wi.cell_weather_for_customer(premise, wi.TEMPERATURE_FIELD, holed).series == {
        "2022-01-01": 3.5}
    cloud = wi.cell_weather_for_customer(premise, wi.CLOUD_COVER_FIELD, holed)
    assert cloud.series == {}, "a NaN reached a caller as a number"
    assert "holds no cloud_cover_pct" in cloud.refusal and "build_weather_world" in cloud.refusal


def test_the_world_is_loaded_once_per_process_and_an_injected_world_is_never_reloaded():
    """DEFECT: a load per leg. `WeatherWorld.load()` reads an 8 MB gzip into ~807,000 rows, and two
    copies of the world in one process can drift from each other — which is precisely what the
    per-cell architecture exists to make impossible."""
    loads = []
    real_load = WeatherWorld.load

    def counting_load():
        loads.append(1)
        return real_load()

    original = wi._WORLD
    try:
        wi._WORLD = None
        WeatherWorld.load = staticmethod(counting_load)
        first = wi.shared_world()
        second = wi.shared_world()
        assert first is second and len(loads) == 1
        injected = object()
        assert wi.shared_world(injected) is injected
        assert len(loads) == 1, "an injected world still triggered a load"
    finally:
        WeatherWorld.load = real_load
        wi._WORLD = original


def test_the_store_refusing_entirely_is_a_reason_and_not_a_crash():
    """DEFECT: a missing store taking the whole run down, or worse, being swallowed. Every premise
    must carry the store's own build instruction as its reason."""
    class _NoStore:
        def cell_id_for(self, lat, lon):
            raise WeatherWorldRefusal("cells.json is absent: the world has no weather")

    verdict = wi.cell_weather_for_customer(
        {"customer_id": "P1", "location": {"lat": 51.5, "lon": -0.1}}, world=_NoStore())
    assert verdict.series == {} and verdict.cell is None
    assert "cells.json is absent" in verdict.refusal
