**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PREREG: what M3, M4, M7, M9 and M10 do against the direct suite that now publishes

**Written 2026-09-06 before the run, shared tree at `6965b1ee4`. Claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M3 M4 M7 M9 M10 --suites explore_carbon`
at spec fingerprint `d892342119e8`.**

## Why this run comes before any new control

`6965b1ee4` closed M5, M6 and M8 by adding three controls to
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py`. All three share a module-scoped
fixture, `real_publish`, that calls `gif.fuel_mix()` and then `gif.generate()` **on the real
caches**. Before that commit, nothing in that suite executed `fuel_mix()` on real data.

That fixture is a new execution path through the subject, and it did not exist when the landed
grid was measured. **Some of the five remaining rows may now redden without anyone writing a
control for them** — a fixture that errors reddens every test in its module. Writing five controls
first and then measuring would make it impossible to say which kill each control earned.

So the order is: measure the five against the suite as it stands, then write controls only for what
survives, and — for anything that reddens — say whether the kill grades the contract or grades the
type system. This spec already carries that distinction as a recorded false-kill mode: M11 exists
because M2's kill was a wrong-class `AttributeError`, and the rule the spec states is *"when a
mutation substitutes a value, substitute one of the SAME TYPE, or the kill grades the type
system."*

## The predictions, from reading the source, before the run

| row | the substitution | predicted | predicted MECHANISM |
|---|---|---|---|
| M3 | `series = fuel.load_cached()` (raw `list[dict]`, not period-ised) | **DIES** | FALSE KILL. `imports_by_period` does `series.items()`; a list has none → `AttributeError` inside the fixture. Grades the type system, not "normalised before anything is derived". |
| M4 | tuple members 0 and 1 swapped | **DIES** | Probably a type crash too — `build_shape` gets `coal_capacity_by_year={(date, period): (mw, t/MWh)}` and `imports_by_period={year: float}`. Honest only if something asserts the members' SHAPES. |
| M7 | `zero_carbon_must_run_coverage(rows)` → `import_coverage(series)` | **SURVIVES** | No crash: member 5 is a `dict[str, float]` either way. Only its vocabulary differs (`usable_fraction`/`negative_half_hours` vs `covered_fraction`), and nothing in the suite reads it. This is the one clean silent-substitution row. |
| M9 | `load_cached_thermal()` → `load_cached()` | **DIES** | HONEST KILL if it fires as predicted: the carbon-relevant cache carries coal and cables, so `thermal_by_period` should find no half hour with both CCGT and OCGT and raise `FuelOutturnUnavailable`. That refusal IS the contract. If instead it returns a non-empty floor, the row is live and needs a control. |
| M10 | `biomass_envelope_by_year(fuel.load_cached_biomass())` (drops `biomass_by_period`) | **DIES** | FALSE KILL. `biomass_envelope_by_year` does `biomass_mw_by_period.items()` on a list → `AttributeError`. Same mode as M3. |

**Summary prediction: four die, one (M7) survives; and of the four, at least two (M3, M10) die for
a reason that grades nothing about the contract.**

## The decision rule, on the record before the answer

- **A row that SURVIVES** gets a control in the direct suite, written the way M5/M6/M8 were: a
  coverage leg and a materiality leg, both printed at real inputs before the test is written.
- **A row that DIES on a wrong-class exception** does not count as closed. The remedy the spec's own
  M11 precedent sets is a **type-correct twin mutation** — the substitution a real fail-open patch
  would actually write — plus a control that kills the twin. Adding a mutation moves the
  fingerprint; that is expected and is what M11 did.
- **A row that DIES on a fail-closed refusal that names its own reason** counts as closed by the
  subject's own suite, and the result says which control node named it.
- **If the baseline is not ~30s**, the caches are absent and every row below is vacuous. The run is
  discarded, not reported. (`sim/cache/` is gitignored; this file is under a second without it.)

## What this run cannot establish either way

`--suites explore_carbon` grades ONE suite by choice, so `survived_all` will be `null` on all five
rows and no caller is graded. Nothing here can change the standing finding that `fuel_mix` has
exactly one caller suite that can go red for it and that suite proves none of its contracts.
