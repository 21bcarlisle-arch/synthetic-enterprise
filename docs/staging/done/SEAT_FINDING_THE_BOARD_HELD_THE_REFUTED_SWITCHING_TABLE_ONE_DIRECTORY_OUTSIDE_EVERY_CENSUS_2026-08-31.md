# The board held the refuted switching table, one directory outside every census

*Delivery seat, 2026-08-31. Closes the item
`WORKER_FINDING_CORRECTING_THE_SWITCHING_BELIEF_MADE_THE_TWO_SIDES_INDISTINGUISHABLE_2026-08-31.md`
deferred deliberately — "not fixed in this commit" — pending the denominator question below.*

---

## 1. The denominator is settled, and it was not a units question

`tools/population_anchor.py` line 37 carried `OFGEM_SWITCHING_RATE` under the comment
*"% of **dual-fuel** accounts switching per year"*, cited to "Ofgem Retail Market Indicators".
The commons' `unreconciled_cross_check` records that a both-fuel change-of-supplier count read
over an electricity account base differs by a factor of about **1.8**, so the first question was
whether the table was the record on a different base rather than a wrong reading of it.

**It is not.** A both-fuel numerator over an electricity denominator reads about 1.8x **HIGH**.
This table read **LOW** — 14% for 2020 against a published 22.5–23.0, 9% for 2021 against
17.9–18.4. No denominator reconciles a table that is low against a base that would make it high.
The label was decoration on ten hand-authored numbers.

The record settles the basis outright, so no refusal was needed:
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` → `basis`. Numerator:
external changes of supplier on a GB domestic **electricity** meter point, once per transfer.
Denominator: **all** GB domestic electricity accounts, whether or not the account was at a
decision point. The gate now inherits that basis whole and states it in its own output `meta`
rather than restating it in a comment where it can drift.

The 1.8x per-fuel question stays open where it already was — in the commons, not in the gate.

## 2. Both declarations are now derivations

* `OFGEM_SWITCHING_RATE_PCT_BY_YEAR` — the band **midpoint** per year, `published_bands()` at
  import, fail-closed. Midpoint and not the high end: the high-end tie-break is a *curriculum*
  value governing where the world is aimed, and this is a measuring stick, not a dial.
* `OFGEM_SWITCHING_RATE` — that table over 100, because everything downstream is in fractions.
* `CALIBRATED_MULTIPLIER` — the rate normalised to 2024, derived and unrounded. It was a
  **byte-identical copy** of the ten numbers refuted in `company/crm/market_conditions.py` the
  night before: 2016: 2.17 … 2020: 0.95 … 2022: 0.44, falling monotonically 2016→2022 while the
  record *rose* to its high-water mark in 2020.
* `_crisis_churn_direction` read `OFGEM_SWITCHING_RATE.get(2022, **0.04**)` — a hand-authored
  literal standing by to answer for the published record if the record went missing. Removed; a
  failed read now reports `insufficient_data`, because an unavailable check is a failed check.

The old docstring in `market_conditions` said its multiplier *"matches the calibration already
published for board-facing population anchoring"*. It did. That was the defect and not the
reassurance — one published series, three implementations, one repaired: the VAT class the
director named on 2026-08-30, reproduced inside twenty-four hours of the rule being written.

## 3. What moved on the board's page

`site/state/population_anchoring.json`, regenerated against the same run.

| Figure | Before | After |
|---|---|---|
| `long_run_comparison.ofgem_avg_pct` | 14.7 | **17.1** |
| `long_run_comparison.ratio` (sim/record) | 1.32 | **1.13** |
| `crisis.2022_ofgem_rate_pct` | 4.0 | **3.6** |
| `multiplier_alignment` AMBER transitions | 3 of 8 | **1 of 8** |
| `overall_rag` | RED | RED (unchanged) |

The alignment column is the honest one to read twice. Three transitions were AMBER — *"the record
went down and the sim went up"* — for 2017→18, 2018→19 and 2019→20. **The record went UP in all
three.** The gate was flagging the simulation for tracking a rise that actually happened, because
its own copy of the series had the shape inverted. Those are now GREEN on the record, not on a
loosened threshold.

`overall_rag` stays RED and is driven by the bad-debt leg, untouched here. Nothing in this repair
made a verdict better by moving a benchmark: `sim_avg_pct` is unchanged at 19.4, and the ratio
fell only because the denominator it is measured against is now the published one.

Each year's row also now carries `ofgem_benchmark_band_pct`. A midpoint published without the
range it came from reads as a measured scalar, and the record does not state one — 2024 is
12.5–16.1, and a reader told "14.3" could not see that.

## 4. The census reaches `tools/`

`tests/architecture/test_switching_rate_commons.py` `_SCOPE` was `("company", "saas",
"simulation")` — the three lanes that hold the *model*, missing the one that holds what the
*board reads*. That is precisely the enumerator blindness `test_year_keyed_rate_table_census` was
written for: *a register of unverified constants inherits the blindness of its own enumerator*,
one directory over, in the census written for that lesson.

Now `("company", "saas", "simulation", "tools")`, and all nine candidates it reaches are
registered or classified. Two registers gained entries and one is new:

* `_LANE_READINGS` ← `tools.population_anchor:OFGEM_SWITCHING_RATE_PCT_BY_YEAR` (band-held).
* `_MULTIPLIER_READINGS` ← `tools.population_anchor:CALIBRATED_MULTIPLIER`, declaring the level
  it normalises by, so leg (b3) holds the derivation.
* `_UNIT_DERIVED_READINGS` (new) — a table that is another registered table in different units.
  `_CALLABLE_READINGS` already carried an explicit `to_pct` factor for exactly this; the dict
  registers had no equivalent, so a fraction-shaped rate had nowhere to go but
  `_NOT_A_LEVEL_READING`, and calling a switching rate "not a level reading" because it is
  written `0.228` rather than `22.8` would be false in the register that exists to stop that.

**Mutations proved firing:**

* `test_mutation_i` — put `0.14` back into the **fraction** table for 2020 only. The band leg
  cannot see it (the per-cent table is still right); the derivation leg fires. That is the state
  a repair stopping at the per-cent table would have left the board in.
* `test_mutation_j` — the leg the direction named. A level-shaped reading planted in `tools/`
  fires the census, **and** the same decoy goes silent with `tools` removed from `_SCOPE`. Both
  halves are asserted: a widened scope that quietly narrowed again would otherwise leave every
  other leg in the file green.

## 5. What is still owed

The gate's remaining benchmarks are unexamined by this pass and three of the four are
rate-shaped, hand-authored, and reach the same page: `BAD_DEBT_BENCHMARK_*`
("Ofgem/EUA annual survey", no artefact), the complaint band ("Ofgem QoS survey, I&C adjusted"),
and the arrears band ("DESNZ business energy debt"). None is in a commons and none is held by a
census — the switching census is keyed to the switching series and correctly cannot see them.
`overall_rag` is RED **on the bad-debt leg**, so the one benchmark currently deciding the board's
verdict is the one with no artefact behind it. That is the next thread, and it is a bigger one
than this was.
