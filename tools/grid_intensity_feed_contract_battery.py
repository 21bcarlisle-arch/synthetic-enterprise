#!/usr/bin/env python3
"""R15 mutation battery for `tools/generate_grid_intensity_feed.py`, scored PER SUITE.

The fifth graded subject of the convergence-evidence sweep, and the screen's
second row by caller count: 8 first-party callers, 2 test files that IMPORT it, 108 whose
import closure reaches it.

This file is the SPEC -- the suites, the eight contracts, the reachability anchor
and the null marker. The procedure lives in `tools/contract_battery.py`; what it
guarantees and why is documented there and deliberately not restated here.

Pre-registration, written and landed BEFORE this ran, at `da7336230`:
`docs/staging/SEAT_FINDING_THE_NEXT_SUBJECTS_CONVERGED_SURFACE_IS_MOSTLY_RE_EXPORTS_AND_A_BATTERY_WOULD_HAVE_SCORED_THEM_2026-09-06.md`

WHY ONLY `fuel_mix`, WHEN THE CONVERGED SURFACE HAS FIVE NAMES. Seven of the eight
callers import the identical five: `AGWS_CACHE`, `DEMAND_CACHE`, `aggregate_demand`,
`aggregate_renewable_generation`, `fuel_mix`. Two of those are `Path` constants;
`aggregate_demand` is defined in `sim/grid_carbon_intensity.py` and
`aggregate_renewable_generation` in `sim/generation_demand_history.py`, and this
module imports both at lines 56 and 60 and re-exports them.

**Only `fuel_mix` is this module's own behaviour.** Mutating a re-export applies
cleanly, kills or survives, and says nothing about this subject -- and `target
present exactly once` does not catch it, because the target IS present exactly
once, on an import line. Screening is not scoping: the screen's caller count is
correct and four fifths of the surface it counted cannot be graded here at all.

WHAT `fuel_mix` IS FOR, and why it is worth eight contracts even though every line
of it delegates. `sim.grid_carbon_intensity.build_shape` takes coal capacity,
interconnector flow, the thermal floor, must-run and the biomass envelope as
OPTIONAL keywords whose defaults reproduce the pre-correction shape exactly. That
signature is fail-open by construction, and `fuel_mix` is the one place the
corrections cannot be forgotten: an absent or unusable input RAISES out of
`generate()` and the feed is not written. So its contracts are the routing itself
-- which loader feeds which position of the returned tuple, at what grain, and
which failures are allowed to be swallowed. None of that is in `sim/`.

Usage:
    python3 -m tools.grid_intensity_feed_contract_battery
    python3 -m tools.grid_intensity_feed_contract_battery --only M1 --suites ep13
"""
from __future__ import annotations

from tools.contract_battery import BatterySpec, run

#: The two suites that IMPORT the subject -- the only ones that can NAME a
#: contract of it.
DIRECT_SUITES = (
    "tests/sim/test_elexon_fuel_outturn.py",
    "tests/tools/test_grid_intensity_feed_and_explore_carbon.py",
)

#: One suite per first-party caller. Seven `ep13_*` bound/ceiling tools plus
#: `background/process_run_complete.py`, which is the only caller that runs
#: `generate()` on the publishing path.
#:
#: EVERY ONE OF THESE IMPORTS THE SUBJECT INSIDE A FUNCTION BODY, so the
#: reachability floor here grades something STRICTER than the previous three
#: subjects': not "does this suite import the module" but "does this suite execute
#: the calling path". Six of the seven `ep13_*` suites are expected to report
#: NEVER REACHES for that reason, and a reader who calls them importers would be
#: right about the tool and wrong about the suite. Said before the run, because
#: afterwards a stricter floor and a broken one look identical.
CALLER_SUITES = (
    "tests/tools/test_ep13_biomass_oracle_bound.py",
    "tests/tools/test_ep13_ccgt_level_ceiling.py",
    "tests/tools/test_ep13_ccgt_swap_ceiling.py",
    "tests/tools/test_ep13_embedded_generation_bound.py",
    "tests/tools/test_ep13_input_ceiling.py",
    "tests/tools/test_ep13_peer_bound.py",
    "tests/tools/test_ep13_per_fuel_oracle_bound.py",
    "tests/background/test_process_run_complete.py",
)

SUITES = DIRECT_SUITES + CALLER_SUITES

#: Two suites with no import path to the subject. The poison round must leave
#: these GREEN, or a floor that reddens everything for a reason unrelated to the
#: subject reads exactly like total reachability.
CONTROL_SUITES = (
    "tests/background/test_delivery_lane.py",
    "tests/design/test_atom_notes_store.py",
)

#: (id, the contract as the module states it, old, new). Each `old` appears
#: exactly once in the subject and the engine refuses the row if it does not.
#:
#: Every one of these is a contract of `fuel_mix` ITSELF -- the routing, the grain
#: and the refusals. A mutation that broke `sim.elexon_fuel_outturn`'s arithmetic
#: would be graded against the wrong module, and that is the hazard this subject
#: was chosen to make concrete.
MUTATIONS = (
    (
        "M1",
        "an absent FUEL cache raises out of fuel_mix -- no mix, no feed (the one place "
        "build_shape's fail-open keywords are closed)",
        "    series = fuel.to_settlement_periods(fuel.load_cached())",
        "    try:\n"
        "        series = fuel.to_settlement_periods(fuel.load_cached())\n"
        "    except Exception:\n"
        "        series = {}",
    ),
    (
        "M2",
        "an absent BIOMASS cache raises too -- the envelope is REQUIRED though not dispatched, "
        "which is what makes the not-dispatched decision honest",
        "    biomass = fuel.biomass_envelope_by_year(fuel.biomass_by_period("
        "fuel.load_cached_biomass()))",
        "    try:\n"
        "        biomass = fuel.biomass_envelope_by_year(fuel.biomass_by_period("
        "fuel.load_cached_biomass()))\n"
        "    except Exception:\n"
        "        biomass = {}",
    ),
    (
        "M3",
        "the thermal floor is unpacked to per-YEAR here -- the per-half-hour series is a "
        "measurement input and must not reach the dispatch",
        "    floors = fuel.thermal_floor_by_year(fuel.thermal_by_period("
        "fuel.load_cached_thermal()))",
        "    floors = fuel.thermal_by_period(fuel.load_cached_thermal())",
    ),
    (
        "M4",
        "the thermal floor comes from the THERMAL cache, not from the fuel outturn series",
        "fuel.thermal_floor_by_year(fuel.thermal_by_period(fuel.load_cached_thermal()))",
        "fuel.thermal_floor_by_year(fuel.thermal_by_period(fuel.load_cached()))",
    ),
    (
        "M5",
        "the returned tuple's ORDER is (imports, coal capacity, coverage, ...) -- all seven "
        "callers unpack it positionally and nothing names a field",
        "        fuel.imports_by_period(series),\n"
        "        fuel.coal_capacity_by_year(series),\n"
        "        fuel.import_coverage(series),",
        "        fuel.import_coverage(series),\n"
        "        fuel.coal_capacity_by_year(series),\n"
        "        fuel.imports_by_period(series),",
    ),
    (
        "M6",
        "coal capacity is MEASURED from the outturn series -- an empty map is the pre-coal shape "
        "and build_shape would accept it silently",
        "        fuel.coal_capacity_by_year(series),",
        "        {},",
    ),
    (
        "M7",
        "the published import coverage is the MEASURED one and not a sentence",
        "        fuel.import_coverage(series),",
        '        {"covered_fraction": 1.0, "covered_mwh": 0.0, "total_mwh": 0.0},',
    ),
    (
        "M8",
        "must-run coverage is measured from the SAME rows the must-run series came from, and is "
        "not asserted complete",
        "        fuel.zero_carbon_must_run_coverage(must_run_rows),",
        '        {"covered_fraction": 1.0, "half_hours": 0},',
    ),
)

#: The reachability floor: an import-time raise. Every caller imports LAZILY, so a
#: suite reddens here only if it EXECUTES the function that does the import. See
#: `CALLER_SUITES` for why that is the stricter floor and why it was stated first.
POISON_OLD = "\ndef fuel_mix() -> tuple[dict, dict, dict, dict]:"
POISON_NEW = ('\nraise RuntimeError("POISON: generate_grid_intensity_feed reachability floor")'
              "\n\n\ndef fuel_mix() -> tuple[dict, dict, dict, dict]:")

#: THE NULL ROUND, and this subject is the one it was built for. Six of the seven
#: `ep13_*` tools do
#: `(PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text()` and
#: walk the result as an AST, and two tests in the direct suites walk
#: `inspect.getsource(gif.generate)`. For a subject like that, `died` and "the
#: suite executed the mutated line" are different claims.
#:
#: The marker is a module-level no-op assignment: it changes the bytes, adds an
#: AST node, and cannot change what any function does. It deliberately contains no
#: import and no string literal, because the property those AST walks grade is
#: "nothing here imports an ep13 module" -- so an honest null marker SHOULD leave
#: them green. What this round can therefore establish is bounded, and the bound
#: is stated here rather than discovered from the output: a green cell means the
#: suite does not grade the bytes THIS EDIT PERTURBS, never that it runs the code.
NULL_OLD = "def dates_with_reads(paths=READ_BEARING_ARTEFACTS) -> set[str]:"
NULL_NEW = ("_NULL_ROUND_MARKER = None  # behaviour-preserving; tools/contract_battery.py\n"
            "\n\ndef dates_with_reads(paths=READ_BEARING_ARTEFACTS) -> set[str]:")

SPEC = BatterySpec(
    name="grid_intensity_feed",
    subject="tools/generate_grid_intensity_feed.py",
    suites=SUITES,
    mutations=MUTATIONS,
    poison_old=POISON_OLD,
    poison_new=POISON_NEW,
    control_suites=CONTROL_SUITES,
    null_old=NULL_OLD,
    null_new=NULL_NEW,
)


def main(argv: list[str] | None = None) -> int:
    return run(SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
