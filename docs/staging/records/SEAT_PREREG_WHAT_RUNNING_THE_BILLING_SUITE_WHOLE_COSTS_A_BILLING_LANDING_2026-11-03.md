**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: what running tests/company/billing whole costs a billing landing

**Written 2026-11-03, before any selection was printed or timed.** The item is the fix row
`a-billing-or-gate-change-lands-on-its-own-test-selection` in `docs/direction/wrong_triage.yaml`.

## What is measured

For each of `845a5222b`, `ea2f3394d`, `54f76662d`, `1bdd86b84`: the commit gate's selection today
(`select_targets` plus the capped import-derived extras) and the selection with
`tests/company/billing` run whole on a billing or validator landing, as file counts, and the wall
time of the whole billing directory on this box.

## Predictions

1. `tests/company/billing` (135 files) runs whole in **2 to 6 minutes** wall on one process.
2. The three billing-touching commits (`845a5222b`, `54f76662d`, `1bdd86b84`) each gain **over 90**
   files; `ea2f3394d` (simulation only) gains none from the billing rule.
3. On the current tree, `test_the_raw_export_carries_nothing_derived.py` is **not** in today's
   selection for a change to `company/billing/monthly_bill_assembly.py` alone, because it imports
   `raw_account_export`, not the module that changed.
4. `ea2f3394d`'s simulation importers are already reached by the import-derived leg; the change it
   needs, if any, is that those importers are run uncapped rather than graded "NOT GRADED".

## Result (same day, after the predictions above)

Selection on today's tree, test files (main selection | capped import-derived extras):

| commit | today | with the billing suite whole |
|---|---|---|
| `845a5222b` | 62 \| 6 | 186 \| 5 |
| `ea2f3394d` | 53 \| 98 | 53 \| 98 (unchanged) |
| `54f76662d` | 72 \| 29 | 194 \| 14 |
| `1bdd86b84` | 75 \| 48 | 193 \| 34 |
| `08f267b666` | 87 \| 31 | 218 \| 11 |

1. **Held.** `tests/company/billing` whole: 2,556 passed in 178.6s, 183s wall.
2. **Held.** The three billing commits gain 118 to 124 files; `ea2f3394d` gains none. The suite is
   133 `test_*.py` files, not 135: two entries in the directory are not test files.
3. **Held.** For `monthly_bill_assembly.py` alone, today's selection was 45 files plus 27 extras,
   and the refusing file was in neither; with the rule it is selected.
4. **Held, and it decides against the simulation half.** `ea2f3394d`'s 79 simulation importers are
   already in the import-derived leg (30s per file, 180s in all). Timed one file each, uncapped, the
   first 13 took **1,447s**, eight times today's whole budget, before I stopped the run: four files ran
   154s, 253s, 462s and 474s, and every file passed. Over the 100 non-merge simulation landings since
   2026-10-20, the median pulls 35 importers and nearly half pull 72 or more. The one recorded
   simulation red (`SEAT_FINDING_TWO_DUAL_FUEL_MOVER_TESTS_RED_AFTER_TWELVE_EARLIER_SIMULATION_FILES_AND_
   PASS_ALONE_2026-11-02.md`) is order-dependent and passes alone, so a per-file run would not have
   caught it at any cost. The simulation half is therefore not built. The whole-suite pretest before
   each fresh run stays the leg that catches it, as the triage row already said.

The box was shared with a full-suite census and two other landings throughout, so every wall time
above runs high by an unmeasured amount.
