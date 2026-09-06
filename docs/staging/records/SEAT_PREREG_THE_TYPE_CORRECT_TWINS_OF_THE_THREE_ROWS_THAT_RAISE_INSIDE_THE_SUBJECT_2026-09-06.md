**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PREREG: the type-correct twins of M3, M9 and M10 — the three rows that raise inside the subject

**Written 2026-09-06 before the run, shared tree at `ff2dd516d`. Claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M12 M13 M14 --suites explore_carbon`
at the spec fingerprint these three rows themselves move it to.**

## What is open, and why the obvious fix does not work

`6965b1ee4` closed M5, M6 and M8. `ff2dd516d` closed M4 and M7 and taught the engine to stamp
`died_by_setup_error_only`. What that stamp then said out loud is the remaining exposure:
**M3, M9 and M10 came back DIED and no control body executed a line.** All three raise *inside*
`fuel_mix()`, so the `real_mix` fixture errors, a module-scoped fixture that errors errors every
test in the module, and the `died` is the type system reddening — not a contract being proved.

No control that calls `fuel_mix()` can assert past a `fuel_mix()` that raises. So the remedy is
not another control against those rows. It is the one this spec already set for M2 and paid for
with M11, written into the M11 comment as a rule: **when a mutation substitutes a value,
substitute one of the SAME TYPE, or the kill grades the type system.**

M3, M9 and M10 each swap a call for one returning the WRONG type — a `list` where a mapping is
read, or a cache with no rows of the fuel being reduced. A real fail-open refactor does not write
that; it writes something that still returns, and that is exactly the patch nothing here can
currently see.

## The three twins

| new row | twin of | the substitution — type-correct, and what a real fail-open patch writes |
|---|---|---|
| **M12** | M3 | the outturn IS normalised, then re-keyed to one period per day: `{(day, 1): row}`. Still `dict[(str, int), Mapping[str, float]]`; every downstream reducer runs. |
| **M13** | M9 | the thermal floor is taken over the BIOMASS cache instead of the thermal one. `biomass_by_period` returns `dict[(str, int), float]` — the exact shape `thermal_floor_by_year` reads, with positive values, so it returns a full envelope. |
| **M14** | M10 | the biomass rows ARE period-ised, then re-keyed to one period per day before the envelope. Still `dict[(str, int), float]`. |

## Printed at real inputs BEFORE any control was written

Every twin returns; none raises. What each one does to the number:

- **M12** — member 0 goes from **175,212** entries to **3,653**, one per date. Coal capacity
  2016 `14,724 → 13,424` MW, 2025 `110 → 0` MW.
- **M13** — the floor is sourced from biomass: 2024 `303 → 73` MW, and **2016 disappears
  entirely** (the biomass cache starts in 2017), so the year set itself changes.
- **M14** — `half_hours` per full year goes from **~17,500 to 365**; 2018 floor `264 → 555` MW.

Real-input grain, measured on the caches now: 3,653 dates, min/median/max **43 / 48 / 50**
periods per date, 99.53% of dates carrying ≥46. A day-collapsed mapping has exactly 1 everywhere,
so the absolute grain leg has three orders of magnitude of margin and is not pinned to today's
count.

## The predictions

1. **M12, M13 and M14 all DIE**, each naming the control written for it, and the three named
   nodes are **three different nodes**. That discriminator is the whole lesson of the previous
   run and it is what will be read first.
2. **`died_by_setup_error_only` is FALSE on all three.** This is the load-bearing prediction: it
   is the difference between this increment and the one that looked like it closed five rows and
   closed none.
3. **M13 additionally reddens the `real_publish` tests** — `build_shape` is handed a thermal
   floor with no 2016 row. M12 and M14 leave `generate()` able to complete. If M13's cell comes
   back with `errored` non-empty this is why, and the stamp must still be false because the
   `real_mix` control asserts before the publish fixture is built.
4. **`survived_all` stays `null` on all three rows.** One suite is graded by choice, so no
   caller is graded. Nothing here touches the standing finding that `fuel_mix` has exactly one
   caller suite able to go red for it and that suite proves none of its contracts.
5. **The fingerprint moves**, because mutations are in the hashed payload — as it did for M11.
   The rows are therefore NOT comparable cell-for-cell with the landed grid at `d7eb36a0b901`,
   and this file says so before the run rather than after.
6. **M3, M9 and M10 themselves keep dying by setup error.** The twins do not repair them and are
   not meant to; they are kept as live rows because they are what would redden if the wrong-type
   crash ever stopped being a crash.

## The decision rule

A twin that dies on a *setup error* is not closed, exactly as its original was not. A twin that
dies naming a node that is not the control written for it is not closed either. Both readings are
written here, before the run, so neither can be settled by whichever is more flattering.
