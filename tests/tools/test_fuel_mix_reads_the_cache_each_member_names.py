"""R15 contract for WHICH CACHE each member of `tools.generate_grid_intensity_feed.fuel_mix`
is read from, graded against caches this file builds itself.

WHY THIS IS A SEPARATE FILE FROM `test_grid_intensity_feed_and_explore_carbon.py`, which is the
subject's other direct suite and where these two controls were first written. That file's controls
reach the subject through `real_mix` / `real_publish` -- module-scoped fixtures that call
`fuel_mix()` on the real 235 MB caches at SETUP. That is right for what they grade, and it makes
this file necessary, for a reason that was MEASURED rather than anticipated:

    `tools/contract_battery._run_suite` runs each mutation round with `-x`. A mutation that makes
    `fuel_mix()` raise errors the module-scoped fixture, which errors EVERY test in the module,
    and `-x` stops at the first one. Battery row M9 was run against that file on 2026-09-06 with
    the control below sitting in it, and the cell came back
    `DIED (SETUP ERROR -- no control body ran)` naming `test_the_TUPLES_ORDER_...`. The control
    had not run. A cell cannot report a control that `-x` never reached, and no amount of care in
    writing the control changes that -- it is a property of where it lives.

So the controls that must survive a mutation which BREAKS the real-cache path live here, in a file
with no real-cache fixture in it. They build their own FUELHH rows, call `fuel_mix()` in their own
bodies, and run in ~0.2s with no `sim/cache/` present at all -- which also means, unlike that file,
that a `git archive HEAD` extract grades them honestly rather than skipping them.

WHAT THEY GRADE, and it is not arithmetic: `sim/tests/test_elexon_fuel_outturn.py` owns what each
adapter computes. What is guarded here is WHICH CACHE AND WHICH ROWS each adapter is handed --
the one thing that cannot be seen from a correct-looking number, because a floor measured off the
wrong fleet is a perfectly well-formed floor.
"""
from __future__ import annotations

from tools import generate_grid_intensity_feed as gif

_STUB_DAYS = tuple(f"2020-01-{day:02d}" for day in range(1, 11))
_STUB_PERIODS = tuple(range(1, 49))


def _fuelhh(fuel_type, mw_at_period):
    """FUELHH rows over `_STUB_DAYS` x `_STUB_PERIODS` for one fuel, `mw_at_period(period)` MW.

    The real thing has three more keys (`dataset`, `publishTime`, `startTime`) and no adapter
    here reads any of them; adding them would be a fixture that looks more like the feed and
    grades nothing more.
    """
    return [{"settlementDate": day, "settlementPeriod": period, "fuelType": fuel_type,
             "generation": mw_at_period(period)}
            for day in _STUB_DAYS for period in _STUB_PERIODS]


def test_the_THERMAL_FLOOR_is_read_from_the_THERMAL_CACHE_and_not_the_OUTTURN_one_beside_it(
        monkeypatch):
    """M9. `fuel_mix()` loads two Elexon caches that hold the same KIND of thing -- half-hourly
    FUELHH rows -- and the thermal floor must come from the one that carries CCGT and OCGT.

    WHY ITS `DIED` ON THE REAL CACHES IS NOT A PROOF, and this is the whole reason this control
    exists. Substituting `load_cached()` for `load_cached_thermal()` today raises
    `FuelOutturnUnavailable: no half hour carried a reading for every thermal fuel type` -- which
    reads like the contract fail-closing, and is not. MEASURED 2026-09-06: `sim/cache/
    elexon_fuelhh.json` is 1,298,444 rows of COAL and nine interconnectors and **no CCGT or OCGT
    at all**, so the refusal is a fact about what that file happens to contain, not about which
    cache the floor is read from. Widen the outturn fetch to all fuel types -- a one-line change
    with its own good reasons -- and the same mutation would silently publish a floor measured
    off the whole gas fleet, six times too high, with nothing anywhere going red.

    So the outturn cache stubbed here DOES carry gas, which is the state that makes the contract
    load-bearing rather than incidental. Printed at these inputs before the assertions were
    written: the thermal cache gives a 2020 floor of 3,102 MW, the outturn cache 20,502 MW.

    MUTATION (must fire): `fuel.load_cached_thermal()` -> `fuel.load_cached()` -- battery row M9,
    whose kill at `d892342119e8` was `real_publish` erroring at setup with no control body run.

    M13, landed by a concurrent lane at `c477232ea`, is M9's type-correct twin and is killed from
    the real-cache suite. It does not make this redundant and the reverse is also true: M13
    substitutes the BIOMASS cache, which reduces to the same shape, so it grades that the floor is
    reduced over gas-shaped rows. This grades which of two GAS-CARRYING caches is read, which is
    the state a widened outturn fetch would create, and it is the only one of the two that can be
    graded at all once the mutation breaks the real-cache path.
    """
    from sim import elexon_fuel_outturn as fuel

    outturn = (_fuelhh("COAL", lambda p: 1000.0 + p)
               + _fuelhh("INTFR", lambda p: 800.0 + p)
               # An EXPORT. Dropped rather than netted by `to_settlement_periods`, so it is also
               # what stops this stub agreeing with a netted series by accident.
               + _fuelhh("INTNED", lambda p: -600.0 - p)
               + _fuelhh("CCGT", lambda p: 20000.0 + p)
               + _fuelhh("OCGT", lambda p: 500.0 + p))
    thermal = _fuelhh("CCGT", lambda p: 3000.0 + p) + _fuelhh("OCGT", lambda p: 100.0 + p)

    monkeypatch.setattr(fuel, "load_cached", lambda: outturn)
    monkeypatch.setattr(fuel, "load_cached_thermal", lambda: thermal)
    monkeypatch.setattr(fuel, "load_cached_zero_carbon_must_run",
                        lambda: _fuelhh("NUCLEAR", lambda p: 5000.0 + p)
                        + _fuelhh("NPSHYD", lambda p: 300.0 + p))
    monkeypatch.setattr(fuel, "load_cached_biomass", lambda: _fuelhh("BIOMASS",
                                                                    lambda p: 1000.0 + p))

    # THE WRONG SOURCE MUST BE ABLE TO ANSWER AT ALL, asserted BEFORE the contract. A stub whose
    # outturn cache carried no gas would make this control pass because the mutation crashes --
    # which is exactly the false kill it was written to replace, rebuilt inside its own fixture.
    from_wrong_cache = fuel.thermal_floor_by_year(fuel.thermal_by_period(outturn))
    from_right_cache = fuel.thermal_floor_by_year(fuel.thermal_by_period(thermal))
    assert from_wrong_cache and from_right_cache, "one of the two stubs cannot produce a floor"
    assert from_wrong_cache != from_right_cache, (
        "the two stubbed caches give the SAME floor, so reading the wrong one is invisible here "
        f"and this control proves nothing: {from_wrong_cache}"
    )

    floors = gif.fuel_mix()[3]

    assert floors == from_right_cache, (
        f"the thermal floor is {floors}, and the THERMAL cache measures {from_right_cache}. The "
        f"outturn cache beside it measures {from_wrong_cache} -- if that is what came back, the "
        "floor is the whole gas fleet's minimum and not the fleet's own"
    )


def test_the_BIOMASS_ROWS_are_FILTERED_TO_BIOMASS_before_the_ENVELOPE_is_taken_over_them(
        monkeypatch):
    """M15, a type-correct twin of M10, and it is here for the reason M11 is here for M2.

    M10 substitutes `biomass_envelope_by_year(load_cached_biomass())` -- a LIST where a mapping
    is expected -- and the `AttributeError: 'list' object has no attribute 'items'` that follows
    grades the type system, not the contract. The substitution a real fail-open patch would
    actually write keeps the type: build the mapping inline and skip `biomass_by_period`. That is
    M15, and this control is what kills it.

    IT IS THE SECOND TWIN OF M10, NOT THE ONLY ONE. A concurrent lane on this same claim landed
    M14 at `c477232ea`, which substitutes a mapping period-ised and then collapsed to one period
    a day -- the GRAIN leg of the same call. This is the FILTER leg. Both are type-correct, both
    still return, and neither control kills the other's row; the two were reconciled rather than
    one dropped, because a call that loses either leg loses a different thing.

    WHY THE CACHE HERE IS MIXED, which is the only reason this can be graded at all. Of the four
    things `biomass_by_period` does, three are equivalences on the real record -- MEASURED
    2026-09-06 on 143,057 rows: every `settlementDate` is already 10 characters, every period is
    inside 1-50, and 19 duplicate `(date, period)` keys out of 143,038 resolve the same way a
    dict comprehension resolves them. The fourth is the fuel-type filter, and the real cache is
    100% `BIOMASS`, so on the real record M15 is an EQUIVALENCE and no control over it could
    fire. It stops being one the moment the biomass fetch is widened or the caches are merged --
    which is what the stub here is: a cache that carries a second fuel.

    Printed at these inputs before the assertions were written: filtered, 2020's envelope is
    1,001-1,048 MW; unfiltered it is 20,001-20,048 MW, the CCGT rows entire.

    MUTATION (must fire): `fuel.biomass_envelope_by_year(fuel.biomass_by_period(
    fuel.load_cached_biomass()))` -> the same call over
    `{(r["settlementDate"], r["settlementPeriod"]): float(r["generation"]) for r in
    fuel.load_cached_biomass()}` -- battery row M15.
    """
    from sim import elexon_fuel_outturn as fuel

    biomass_only = _fuelhh("BIOMASS", lambda p: 1000.0 + p)
    mixed = biomass_only + _fuelhh("CCGT", lambda p: 20000.0 + p)

    monkeypatch.setattr(fuel, "load_cached", lambda: _fuelhh("COAL", lambda p: 1000.0 + p)
                        + _fuelhh("INTFR", lambda p: 800.0 + p))
    monkeypatch.setattr(fuel, "load_cached_thermal",
                        lambda: _fuelhh("CCGT", lambda p: 3000.0 + p)
                        + _fuelhh("OCGT", lambda p: 100.0 + p))
    monkeypatch.setattr(fuel, "load_cached_zero_carbon_must_run",
                        lambda: _fuelhh("NUCLEAR", lambda p: 5000.0 + p)
                        + _fuelhh("NPSHYD", lambda p: 300.0 + p))
    monkeypatch.setattr(fuel, "load_cached_biomass", lambda: mixed)

    # THE UNFILTERED READING MUST BE A DIFFERENT, VALID ENVELOPE -- not a crash and not the same
    # answer -- or the assertion below is satisfied by something other than the filter.
    unfiltered = fuel.biomass_envelope_by_year(
        {(row["settlementDate"], row["settlementPeriod"]): float(row["generation"])
         for row in mixed})
    filtered = fuel.biomass_envelope_by_year(fuel.biomass_by_period(mixed))
    assert unfiltered and filtered and unfiltered != filtered, (
        f"the mixed cache grades nothing: filtered {filtered}, unfiltered {unfiltered}"
    )
    assert filtered == fuel.biomass_envelope_by_year(fuel.biomass_by_period(biomass_only)), (
        "the filtered envelope over the MIXED cache is not the envelope over biomass alone, so "
        "the stub's second fuel is leaking into the reading this control calls correct"
    )

    envelope = gif.fuel_mix()[6]

    assert envelope == filtered, (
        f"the biomass envelope is {envelope}, and the BIOMASS rows alone measure {filtered}. "
        f"Taking the whole cache measures {unfiltered} -- an envelope built from another "
        "fleet's output, published as the wood-burning fleet's demonstrated range"
    )
