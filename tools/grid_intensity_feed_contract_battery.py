#!/usr/bin/env python3
"""R15 mutation battery for `tools/generate_grid_intensity_feed.fuel_mix`, scored PER SUITE.

The fourth subject of the convergence-evidence sweep, and the screen's second row
by caller count: 8 first-party callers, 2 direct test importers, 108 reaching
suites.

This file is the SPEC -- the suites, the ten contracts, the reachability anchor
and the null-round marker. The procedure lives in `tools/contract_battery.py`;
what it guarantees and why is documented there and deliberately not restated.

M9 and M10 come from a SECOND draft of this spec, written in the same half hour
by a second delivery seat that the dispatcher launched on the same claim id (see
the finding beside this file). Two lanes writing one new module at one path is
the unlandable-merge shape, so the drafts were merged here rather than raced.

M11 comes from that second seat's own RUN, reconciled in afterwards. It is M2
with `series = {}` in place of `series = []`. M2's kill is an AttributeError on a
list, not the control catching the lost refusal, so `M2 proved` in the result
beside this file is one row too generous. The repair that makes the contract
genuinely proved is landed in the control itself:
`test_the_feed_REFUSES_to_publish_without_the_fuel_mix_rather_than_reverting_to_the_old_shape`
now asserts the refusal NAMES the missing cache.

M11 SURVIVED before that repair and DIES after it, and this paragraph said
"it SURVIVES where M2 dies" in the present tense until 2026-09-06 -- asserting a
survival in the same breath as the landed repair that ends it. Measured at spec
fingerprint `95c9da4db380`: M11 is killed by that same control, `died` with
`died_but_grades_text` false and the null round green throughout, so the kill is
behaviour and not the suite reading this module's bytes. The survival is the
reason M11 exists and the kill is the evidence the repair worked; both belong in
the record, which is why the first is kept above rather than overwritten.

Pre-registration, written and landed BEFORE this ran, at `da7336230`:
`docs/staging/SEAT_FINDING_THE_NEXT_SUBJECTS_CONVERGED_SURFACE_IS_MOSTLY_RE_EXPORTS_AND_A_BATTERY_WOULD_HAVE_SCORED_THEM_2026-09-06.md`

WHY THE SUBJECT IS ONE FUNCTION AND NOT THE MODULE
--------------------------------------------------
Seven of the eight callers import the identical five names --
`AGWS_CACHE`, `DEMAND_CACHE`, `aggregate_demand`, `aggregate_renewable_generation`,
`fuel_mix` -- and that convergence is what put this module on the screen. Four of
those five are **not this module's code**: two are `Path` constants, and
`aggregate_demand` / `aggregate_renewable_generation` are defined in
`sim/grid_carbon_intensity.py` and `sim/generation_demand_history.py` and merely
re-exported from here.

Mutating a re-export applies cleanly, kills or survives, and says nothing about
this subject -- and `target present exactly once` does not catch it, because the
target IS present exactly once, on an import line. So the battery is scoped to
`fuel_mix`, the one name of the converged surface this module defines.

WHY `fuel_mix` IS WORTH GRADING
-------------------------------
It exists to be the one place the three later corrections -- coal capacity,
interconnector flow, the thermal floor, the zero-carbon must-run block and the
biomass envelope -- cannot be forgotten. `sim.grid_carbon_intensity.build_shape`
takes every one of them as an optional keyword whose default reproduces the
pre-correction shape exactly: fail-open by construction, and nothing in the
arithmetic can notice, because both shapes are dimensionless and both normalise
to 1.0. `fuel_mix` is where that is closed. If its contracts stand on one
borrowed suite, a silent revert to the 2024 shape is one refactor away.

Usage:
    python3 -m tools.grid_intensity_feed_contract_battery
    python3 -m tools.grid_intensity_feed_contract_battery --only M1 --suites explore_carbon
"""
from __future__ import annotations

from tools.contract_battery import BatterySpec, run

#: The two suites that IMPORT the module -- the only ones that can NAME a
#: contract of it.
#:
#: `grep -rl generate_grid_intensity_feed tests/` returns a THIRD,
#: `tests/sim/test_grid_carbon_intensity.py`. It is not one: it carries the
#: module's name in a docstring saying where the control is NOT, and never
#: imports it. It is excluded rather than scored, because a suite that cannot
#: reach the subject contributes a green cell to every row and none of those
#: cells was ever at risk. (A partial results file left in `/var/tmp` by an
#: earlier attempt had it in the suite list; that is the grep-is-an-upper-bound
#: hazard the pre-registration names, live in this very list.)
DIRECT_SUITES = (
    "tests/sim/test_elexon_fuel_outturn.py",
    "tests/tools/test_grid_intensity_feed_and_explore_carbon.py",
)

#: The eight callers of `fuel_mix()` itself, one suite each. Every one of them
#: imports it INSIDE a function body -- `tools/ep13_input_ceiling.py:550`,
#: `background/process_run_complete.py:7575`, and the rest -- so the poison
#: round below grades something stricter here than on the previous subjects.
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
#: these GREEN; a floor that reddens everything for a reason unrelated to the
#: subject reads exactly like total reachability.
CONTROL_SUITES = (
    "tests/background/test_delivery_lane.py",
    "tests/design/test_atom_notes_store.py",
)

#: (id, the contract as the module states it, old, new). Each `old` appears
#: exactly once in the subject and the engine refuses the row if it does not.
#:
#: Every one is inside `fuel_mix`'s own body. None touches a re-export.
MUTATIONS = (
    (
        "M1",
        "an unusable BIOMASS cache RAISES -- the envelope is never silently dropped",
        "    biomass = fuel.biomass_envelope_by_year("
        "fuel.biomass_by_period(fuel.load_cached_biomass()))",
        "    try:\n"
        "        biomass = fuel.biomass_envelope_by_year("
        "fuel.biomass_by_period(fuel.load_cached_biomass()))\n"
        "    except Exception:\n"
        "        biomass = {}",
    ),
    (
        "M2",
        "an unusable FUEL OUTTURN cache RAISES -- no mix, no feed, never the old shape",
        "    series = fuel.to_settlement_periods(fuel.load_cached())",
        "    try:\n"
        "        series = fuel.to_settlement_periods(fuel.load_cached())\n"
        "    except Exception:\n"
        "        series = []",
    ),
    (
        "M3",
        "the outturn is normalised to SETTLEMENT PERIODS before anything is derived from it",
        "fuel.to_settlement_periods(fuel.load_cached())",
        "fuel.load_cached()",
    ),
    (
        "M4",
        "the returned tuple's ORDER is the contract -- every caller unpacks it positionally",
        "        fuel.imports_by_period(series),\n        fuel.coal_capacity_by_year(series),",
        "        fuel.coal_capacity_by_year(series),\n        fuel.imports_by_period(series),",
    ),
    (
        "M5",
        "the THERMAL FLOOR reaches the published feed -- an empty one is a lost correction",
        "    floors = fuel.thermal_floor_by_year("
        "fuel.thermal_by_period(fuel.load_cached_thermal()))",
        "    floors = {}",
    ),
    (
        "M6",
        "the ZERO-CARBON MUST-RUN block reaches the published feed",
        "        fuel.zero_carbon_must_run_by_period(must_run_rows),",
        "        {},",
    ),
    (
        "M7",
        "must-run coverage is ITS OWN measurement and not the import coverage beside it",
        "        fuel.zero_carbon_must_run_coverage(must_run_rows),",
        "        fuel.import_coverage(series),",
    ),
    (
        "M8",
        "the BIOMASS ENVELOPE is returned -- the diagnostic that sizes the 2,400 MW gap",
        "        biomass,\n    )",
        "        {},\n    )",
    ),
    (
        "M9",
        "the thermal floor comes from the THERMAL cache and not the fuel-outturn one beside it",
        "fuel.load_cached_thermal()",
        "fuel.load_cached()",
    ),
    (
        "M10",
        "the biomass rows are period-ised BEFORE the yearly envelope is taken over them",
        "fuel.biomass_envelope_by_year(fuel.biomass_by_period(fuel.load_cached_biomass()))",
        "fuel.biomass_envelope_by_year(fuel.load_cached_biomass())",
    ),
    (
        # M11 IS M2 WITH A TYPE-CORRECT FALLBACK, and it is here because M2's kill is not
        # what it looks like. MEASURED 2026-09-06 by the second seat on this claim: M2
        # substitutes `series = []`, and `imports_by_period` then dies on
        # `AttributeError: 'list' object has no attribute 'items'`. The control asserts
        # `pytest.raises(FuelOutturnUnavailable)`, so it reddens on the WRONG CLASS -- it
        # never saw the contract at all. Substitute `series = {}` instead, which is what a
        # real fail-open patch would write, and `FuelOutturnUnavailable` still arrives --
        # from `coal_capacity_by_year` refusing an empty series -- so the control passed and
        # the fallback shipped. THAT WAS THE PRE-REPAIR READING. Since the control began
        # asserting the refusal NAMES the missing cache, the wrong namer is caught: measured
        # at fingerprint `95c9da4db380`, M11 DIES. Kept as a live row rather than retired,
        # because it is the only thing that would redden if that naming assertion were ever
        # weakened back.
        #
        # A NEW FALSE-KILL MODE FOR THE FAMILY, and the mirror of the recorded false
        # survivors: a mutation whose replacement is the wrong TYPE reddens a suite on a
        # TypeError instead of on the property, and `died` cannot tell the difference. The
        # rule: when a mutation substitutes a value, substitute one of the SAME TYPE, or the
        # kill grades the type system.
        "M11",
        "an unusable FUEL OUTTURN cache raises FROM THE LOADER -- not from an adapter "
        "downstream that happens to share the class (M2 with a dict, not a list)",
        "    series = fuel.to_settlement_periods(fuel.load_cached())",
        "    try:\n"
        "        series = fuel.to_settlement_periods(fuel.load_cached())\n"
        "    except Exception:\n"
        "        series = {}",
    ),
)

#: The subject's `def` block, VERBATIM. Three of the four anchor strings below
#: embed it, so it is held once: a one-character divergence between two copies of
#: a nine-line signature is not findable by reading, and its only symptom is
#: TARGET NOT UNIQUE -- reachability UNKNOWN, printed once and easy to skim past.
#:
#: NOT read from the subject at run time, which would make the anchor derive from
#: the thing it anchors and grade nothing. It is a literal, and `poison_old`'s
#: occurs-exactly-once refusal is what proves the literal still matches.
#:
#: It said `-> tuple[dict, dict, dict, dict]` here and in the subject until
#: 2026-09-06, while the function returned seven members and all eight callers
#: unpacked seven. Correcting the subject moves this spec's fingerprint, which is
#: why the two edits are one commit and why this spec's results file starts empty.
SUBJECT_DEF = """def fuel_mix() -> tuple[
    dict[tuple[str, int], tuple[float, float]],  # imports: {(date, period): (MW, t/MWh)}
    dict[int, float],                            # coal capacity: {year: demonstrated max MW}
    dict[str, float],                            # import coverage: the priced fraction, measured
    dict[int, dict[str, float]],                 # thermal floor: {year: {floor_mw, p1_mw, ...}}
    dict[tuple[str, int], float],                # must-run: {(date, period): NUCLEAR+NPSHYD MW}
    dict[str, float],                            # must-run coverage: measured vs flat fallback
    dict[int, dict[str, float]],                 # biomass envelope: {year: {floor_mw, p99_mw...}}
]:"""

#: The reachability floor: an import-time raise. Unlike the previous subjects,
#: EVERY caller here imports lazily inside a function body, so this reddens a
#: suite only if the suite executes the calling path -- a stricter floor that
#: grades "does this suite run the caller" rather than "does it import the
#: module". Stated before the run, because afterwards a stricter floor and a
#: broken one look identical, and the flattering reading of an unexpected
#: NEVER REACHES is that the floor is working.
POISON_OLD = "\n" + SUBJECT_DEF
POISON_NEW = ('\nraise RuntimeError("POISON: generate_grid_intensity_feed reachability floor")'
              "\n\n\n" + SUBJECT_DEF)

#: THE NULL ROUND, and this subject is the reason the engine has one. Six of the
#: eight callers do `(PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py")
#: .read_text()` and walk the result as an AST, asserting the feed does not
#: import them -- a no-oracle control. For a subject read as text, `died` and
#: "the suite executed the mutated line" are different claims.
#:
#: The marker carries BOTH halves deliberately: a module-level no-op assignment
#: (new bytes, a new AST node, no behaviour) and a comment naming two ep13
#: modules (new bytes, no AST node at all). The walkers' own docstrings say a
#: substring search "would be satisfied by this module's name in a comment and
#: defeated by an import written any way but the one it looked for" -- so the
#: comment is the exact input that separates the walk they claim to do from the
#: search they claim not to. A red here does not say WHICH half caused it; that
#: is a second run with the halves split, and it is only worth paying for if a
#: suite reddens.
NULL_OLD = SUBJECT_DEF
NULL_NEW = (
    "# NULL ROUND (tools/contract_battery.py): behaviour-preserving by construction.\n"
    "# It names ep13_input_ceiling and ep13_biomass_oracle_bound on purpose -- their own\n"
    "# walkers say a substring search would be satisfied by exactly this and an AST walk\n"
    "# is not. Neither name is imported here, so both walks must still return unreachable.\n"
    "_NULL_ROUND_MARKER = None\n"
    "\n"
    "\n"
    + SUBJECT_DEF
)

SPEC = BatterySpec(
    name="grid_intensity_fuel_mix",
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
