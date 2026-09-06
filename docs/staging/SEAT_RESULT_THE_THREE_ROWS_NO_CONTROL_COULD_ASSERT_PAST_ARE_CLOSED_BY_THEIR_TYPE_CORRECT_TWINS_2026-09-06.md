**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the three rows no control could assert past are closed by their type-correct twins

**Measured 2026-09-06 08:32–08:34 BST, shared tree at `ff2dd516d`. Claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M12 M13 M14 --suites explore_carbon`
at spec fingerprint `4c2f0abd38d4`. Results
`/var/tmp/grid_intensity_fuel_mix_M12_M13_M14_TWINS_4c2f0abd38d4.json`, log
`/var/tmp/fuel_mix_twins_4c2f0abd38d4.log`. Exit 0, subject restored (`git status` clean on
`tools/generate_grid_intensity_feed.py`, and byte-identical to the pristine copy the run took).
Prereg, written and landed BEFORE the run at `ff2dd516d`:
`docs/staging/records/SEAT_PREREG_THE_TYPE_CORRECT_TWINS_OF_THE_THREE_ROWS_THAT_RAISE_INSIDE_THE_SUBJECT_2026-09-06.md`.**

## The premise, re-measured

The drawn item asks for controls that kill **M5, M6 and M8** and a re-run **at fingerprint
`d7eb36a0b901`**. Both halves are spent, and were before this tick started:

- M5, M6 and M8 were closed at `6965b1ee4`; M4 and M7 at `ff2dd516d`. The fingerprint
  `d7eb36a0b901` expired at `35109bb09` when the engine gained three payload keys, and has moved
  twice more since — `d892342119e8`, and now `4c2f0abd38d4` because the three twins are
  themselves mutations and mutations are in the hashed payload.
- The claim it belongs to — *M3 to M10 are proved by nothing* — was **not** spent. Three of the
  eight were still closed by nothing, and the reason no further control could close them is what
  `ff2dd516d` built the engine's `died_by_setup_error_only` stamp to say out loud.

So the item's stated work was not redone. Its claim was continued at the point the previous
increment left it.

## What was open

M3, M9 and M10 each substitute a value of the **wrong type**. `fuel_mix()` raises before it
returns, the module-scoped fixture that calls it errors, every test in the file errors with it, and
`died` is the type system reddening rather than a contract being proved. **No control that calls
`fuel_mix()` can assert past a `fuel_mix()` that raises**, so the remedy was never another control
against those rows — it is the rule this spec already paid for with M11: *when a mutation
substitutes a value, substitute one of the SAME TYPE, or the kill grades the type system.*

The three originals are kept as live rows. They are what would redden if the wrong-type crash ever
stopped being a crash.

## The grid, at `4c2f0abd38d4`

| round | result |
|---|---|
| BASELINE | `rc=0 failed=0`, **30.1s**, 51 passed — the data-present timing, so nothing below is a vacuous pass on an empty `sim/cache/` |
| POISON | `explore_carbon` **reaches the subject** (0.8s); both control suites stayed GREEN, so the floor discriminates rather than reddening everything |
| NULL | `behaviour only`, `grades_text: false` — no kill below is a suite reading the subject's bytes |

| row | twin of | verdict | `setup_error_only` | `errored` | named by |
|---|---|---|---|---|---|
| **M12** | M3 | **DIED** (15.6s) | **false** | `[]` | `…::test_the_OUTTURN_stays_at_HALF_HOUR_GRAIN_all_the_way_to_the_derived_mix` |
| **M13** | M9 | **DIED** (15.0s) | **false** | `[]` | `…::test_the_THERMAL_FLOOR_is_reduced_over_the_THERMAL_CACHE_and_not_one_beside_it` |
| **M14** | M10 | **DIED** (17.4s) | **false** | `[]` | `…::test_the_BIOMASS_ROWS_reach_the_YEARLY_ENVELOPE_at_HALF_HOUR_GRAIN` |

`target_occurrences: 1` and `held_through_run: true` on all three; no `error` on any row.
**Three rows, three different named nodes, and each is the control written for that row** — the
discriminator the previous run failed and this one had to pass.

## The predictions, all six of which held

Filed before the run, and none revised after it:

1. *All three die, each naming the control written for it, three different nodes.* **Held.**
2. *`died_by_setup_error_only` is FALSE on all three* — the load-bearing one, the difference
   between this increment and the one that looked like it closed five rows and closed none.
   **Held**, and `errored` is empty on every row, so not one red anywhere in the three runs was a
   setup error.
3. *M13 additionally reddens the `real_publish` tests, because `build_shape` is handed a thermal
   floor with no 2016 row.* **Not observable, and the prereg's escape clause is the reason it is
   not being claimed either way.** `errored` is empty, which the prereg named as the signal — but
   the engine runs with `-x`, so the run stopped at the first red and that red was the `real_mix`
   control asserting before the publish fixture is ever built. What the prereg required is what
   was measured: the stamp is false. Whether the publish tests would *also* have reddened is a
   question this run cannot answer and does not.
4. *`survived_all` stays `null` on all three.* **Held** — one suite was graded by choice, so all
   eight callers sit in `ungraded_callers` and `killed_by` is `[]` on every row.
5. *The fingerprint moves.* **Held**: `d892342119e8 → 4c2f0abd38d4`.
6. *M3, M9 and M10 keep dying by setup error.* Untouched by this run and unchanged.

## Where `fuel_mix` now stands

Eleven original contracts. Eight of them — M3 to M10 — were killed by nothing when this claim was
drawn. **All eight now have a control that fires**, five of them directly (M4, M5, M6, M7, M8) and
three through the type-correct twin that a real fail-open refactor would actually write (M12 for
M3, M13 for M9, M14 for M10).

## What this does NOT establish

- **Every one of these kills is by the subject's own suite.** The engine's verdict is
  `PROVED ONLY BY THE SUBJECT'S OWN SUITES (no caller kills these): ['M12', 'M13', 'M14']`. That
  is a promotion from *killed by nothing*, and it is not a promotion from *unproved by callers*.
  **The standing finding is unchanged: `fuel_mix` has exactly one caller suite that can go red for
  it at all, and that suite proves none of its contracts.**
- **M3, M9 and M10 are still, in themselves, proved by nothing**, and the run says so on the cell.
  The twins close the *contract*; they do not close the row, and the rows are deliberately kept.
- **This is not a re-grade of the landed 99-cell grid** and must not be read against it as one.
  Three cells at a new fingerprint, one suite wide.
- **The tenth column is still ungraded.** `tests/tools/test_ep13_embedded_generation_bound.py` is
  now both reachable and cheap (~6 minutes for a full column, down from 112), and buying it is
  what would replace the `null` in `survived_all` with a real verdict. It was outside this
  increment and is the obvious next one.

## Beside the claim: a refusal in the shared tree that is not this lane's

`background/finding_classes --check` is RED on
`SEAT_PREREG_ARE_DIRECTIONS_FOUR_CALLER_COLUMNS_CALLERS_2026-09-06.md`: the file is staged as
deleted from `docs/staging/` **and** present there untracked, with an identical untracked copy in
`docs/staging/records/`. That is the half-staged room move — the direction-battery lane's
`surgical_land` was refused and restored the tracked path it had just moved. It is not this lane's
file and not this lane's index entry; landing around it rather than resolving it, because
completing someone else's move from here would stage a room change they have not finished.
