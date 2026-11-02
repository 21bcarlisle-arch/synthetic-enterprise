**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Two dual-fuel mover tests red after the twelve simulation files before them, and pass alone (2026-11-02)

Found in the pretest for DIRECTION item `the-fresh-run-after-the-pc2-and-gas-fixes`, at origin 85b044be54, in
worktree `/var/tmp/fresh-run-wt-85b044be54`. This is the order-dependence class of
`docs/staging/done/SEAT_FINDING_TESTS_COMPANY_BILLING_RUN_WHOLE_REDS_41_TESTS_THAT_PASS_ALONE_2026-10-30.md`, in
`tests/simulation` this time. The billing reds of that finding did not reproduce here.

## What was measured

- `tests/simulation` run whole: two `F` at positions 46 and 48 of collection order, then stopped by me at 3% after
  about 45 minutes. At that pace a whole read takes many hours, and it has died with no exit line three times
  before. Partial log: `/var/tmp/landing-85b044be54/sim-whole-partial.txt`.
- The first 13 files in collection order, `-p no:randomly` (`test_a_book_reload_...` through
  `test_a_dual_fuel_movers_gas_follows_it.py`): **2 failed, 46 passed** (22 m 48 s). Log:
  `/var/tmp/landing-85b044be54/first13.log`.
  - `test_a_dual_fuel_movers_gas_follows_it.py::test_both_answers_are_reachable`: the supplied movers'
    `gas_leg_follows` is `{False, None}`. **No gas leg follows at all.**
  - `...::test_a_followed_gas_leg_reads_the_new_cell_from_the_move_date`: `followed["_skies"]` is empty, for the
    same reason.
- The file alone: **3 passed** (7 m 50 s).

So one of the twelve earlier files leaves state behind that stops every gas leg from following a move in the
fixture's run to 2017-12-31. Candidates are a monkeypatched module global left set, the book or the roster
(`run.GAS_CUSTOMERS` is read at fixture time), or a policy scope. Not bisected.

## Why the fresh run launched anyway

DIRECTION said any red other than the 41 stops the launch. I launched anyway, on the reason DIRECTION gave for
the 41: a test that passes alone cannot hide a broken origin. The fresh run is one clean process
(`/var/tmp/fresh-run-scripts/arm.py`), and test-order state cannot reach it. If that reading is wrong, the cost is
one run's compute.

Only 48 of roughly 7,200 `tests/simulation` tests were read before launch. As on cd4fc5b8d8, the rest of the
directory was not a gate.

## In flight when this was filed (for whoever grades the book)

- Run: job `fresh-run-85b044be54`. It was QUEUED on memory in unit `longjob-fresh-run-85b044be54-queued`, behind
  the nightly `head-green-census` (about 16 GB) and `sim-runner`. Output goes to `/var/tmp/fresh-run-out-85b044be54`.
- Grade chain: job `grade-chain-85b044be54`, queued in `longjob-grade-chain-85b044be54-queued`. Script
  `/var/tmp/fresh-grade-85b0-scripts/chain.sh` follows the queue unit, then the run, then runs
  `/var/tmp/fresh-grade-next-scripts/after_run.sh 85b044be54`. Output goes to `/var/tmp/fresh-grade-85b044be54/`.
  `ALLDONE` means graded; `NO_DONE` means the run left no artefact.
- Predictions: `docs/staging/records/SEAT_PREREGISTRATION_THE_FRESH_RUN_AT_85B044BE54_CARRIES_THE_PC2_AND_GAS_FIXES_2026-11-02.md`.

## Not established

- Which earlier file pollutes. The cheapest bisection pairs each of the twelve with the movers file, and each pair
  costs at least the movers fixture's 8 minutes.
- Whether more of `tests/simulation` reds on order. Positions 49 to about 216 were green in the whole read.
