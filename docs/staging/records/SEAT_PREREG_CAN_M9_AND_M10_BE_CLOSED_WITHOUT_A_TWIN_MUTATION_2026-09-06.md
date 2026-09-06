**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PREREG: can M9 and M10 be closed by a STUBBED-LOADER control, without a twin mutation?

**Written 2026-09-06 BST before anything was run, on claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`, shared tree at `8a2f11bb3`.**

## The premise the drawn item carries is spent, and this says so

The item asks for controls that kill **M5, M6 and M8** and a re-run **at fingerprint
`d7eb36a0b901`**. Both halves are already answered on this claim and neither is available:

- The three controls landed at `6965b1ee4` and were graded at `d892342119e8`
  (`SEAT_RESULT_THREE_OF_FUEL_MIXS_EIGHT_UNPROVED_CONTRACTS_NOW_DIE_AND_THE_FINGERPRINT_THEY_WERE_ASKED_FOR_NO_LONGER_EXISTS_2026-09-06.md`).
- `d7eb36a0b901` no longer exists: `contract_battery.fingerprint` hashes the engine's field list,
  and three fields were added after `03387ff1e`.

Re-measured here rather than taken from those documents: the landed results file
`/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json` has M1, M2 and M11 killed by
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py` and M3–M10 killed by nothing, which
is the item's premise exactly — and the two commits above post-date that file by two hours.

**So this lane takes the increment the last result named as next, on the same claim: M3, M9 and
M10, whose `DIED` at `d892342119e8` was `died_by_setup_error_only` — one module fixture erroring,
no control body run.**

## The question

The named remedy was a **type-correct twin mutation** for each. This asks whether M9 and M10 need
one, or whether the real defect is that both existing controls reach the subject through
`real_mix`, a module-scoped fixture that calls `fuel_mix()` on the real caches at SETUP. A control
that builds its own inputs and calls `fuel_mix()` **in its own body** cannot error at setup, and
can choose inputs under which the mutation produces a WRONG VALUE rather than a crash.

## What is predicted, before running

1. **M9 does NOT need a twin.** Its crash today (`FuelOutturnUnavailable: no half hour carried a
   reading for every thermal fuel type`) is an accident of what the outturn cache happens to hold:
   measured here, `sim/cache/elexon_fuelhh.json` is 1,298,444 rows of COAL and nine
   interconnectors and **no CCGT or OCGT at all**. Hand `fuel_mix()` an outturn cache that DOES
   carry gas — the exact state a future widening of the fetch would create — and M9 stops raising
   and starts returning a floor measured off the wrong fuel. Predicted: a control that stubs both
   loaders at distinguishable levels kills M9 on an ASSERTION, not a crash.
2. **M10 DOES need a twin, and the reason is an equivalence.** `biomass_by_period` filters to
   `BIOMASS`, truncates the date to 10 characters, range-checks the period and takes last-row-wins.
   Measured here on the real cache: 143,057 rows, **100% `BIOMASS`**, every `settlementDate`
   already 10 characters, every period inside 1–50, and 19 duplicate `(date, period)` keys out of
   143,038. So a twin that drops the filter is an equivalence on the real cache in three of its
   four legs. Predicted: the control must stub a MIXED biomass cache, and the twin must be
   type-correct (a dict, not the list M10 substitutes).
3. **M3 is predicted to stay open**, and this is filed as a prediction rather than discovered
   afterwards. Its only type-correct twins re-implement `to_settlement_periods` inline, which
   grades the twin rather than the subject. If that is wrong it will be said so here.

## The decision rule

- A row is closed only if its kill names the control written for it AND
  `died_by_setup_error_only` is false on that cell.
- A row whose kill is a wrong-class exception is NOT closed, whatever `died` says.
- If the stubbed control passes unmutated but the mutation still crashes before the assertion, the
  row is recorded as open and the twin is written; the flattering reading is not available.
