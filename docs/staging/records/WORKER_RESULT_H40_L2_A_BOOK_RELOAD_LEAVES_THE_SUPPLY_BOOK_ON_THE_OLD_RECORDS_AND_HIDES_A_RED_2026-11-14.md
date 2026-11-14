**Severity:** INFO · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `H40_full_suite_pollution_bisect`
**Evidence:** L1 record `WORKER_RESULT_H40_THE_FULL_SUITE_POLLUTER_IS_THE_REGISTRY_EAC_REWRITE_WRITING_INTO_THE_SHARED_ROSTER_2026-10-07.md`; 45d2920a9b; this file

# H40's L2 evidence (level held at 1): the L1 gap is closed, and a book reload leaves the supply book on the old records, which hides a red (2026-11-14)

**Autonomous worker, 14 Nov 03:00-04:40Z.** Every reading below was taken in a detached worktree of
`origin/main` at `0b96265f69`, with `-p no:randomly -p no:cacheprovider`. Nothing was read from the shared tree.

## 0. The level is HELD at 1, and why

This record carries the L2 evidence. The move itself was refused by OPS11 at `record_level_up_self_certified`.
Lane H_harness holds a live BLOCKING finding,
`WORKER_FINDING_THE_EXPERT_HOUR_ON_THE_LIVE_DOORS_FAILS_ON_A_NET_MARGIN_OF_UP_TO_55_PCT_AND_AN_ARREARS_COUNT_THAT_READS_EBSS_AS_DEBT_2026-11-11.md`
(atom SITE1_expert_doors). Nothing in H40's evidence rests on a door figure. But the only release,
`record_limitation_accepted`, is keyed on (lane, finding), not on the atom, so accepting it would also let SITE1
itself move past its own failed Expert Hour. A bounded tick should not take that side effect, so the level
waits. **To move it** once that finding is discharged, set `level_current: 2` on the row and call
`record_level_up_self_certified('H40_full_suite_pollution_bisect', 2, ...)`. Its provenance must carry this
record's End-to-end clause (section 8).

## 1. What held H40 at L1, and what closed it

The L1 record ended "Not L2: the two `test_the_registry_eac_rewrite_reaches_the_dd_opening` nodes are
unexplained." 45d2920a9b explained them the next day with the ordered pair that reproduces.
`serves_industrial_accounts` reloaded `run_phase2b` alone, so `run_phase4c_on_phase2b` kept the old book.
That commit reproduced the defect red and showed it green after the fix (`reload_with_binders`). That
closes the L1 gap. This record goes after the next live instance of the class.

## 2. The 2 Nov instance does not reproduce at HEAD

`SEAT_FINDING_TWO_DUAL_FUEL_MOVER_TESTS_RED_AFTER_TWELVE_EARLIER_SIMULATION_FILES_AND_PASS_ALONE_2026-11-02.md`
recorded `test_a_dual_fuel_movers_gas_follows_it.py` going red after 12 earlier files at 85b044be54. That file
now has 19 predecessors in collection order.

| run | result | wall | peak RSS |
|---|---|---|---|
| movers file alone | 3 passed | 9 m 47 s | 2.0 GB |
| all 19 predecessors, then the movers file | movers **3 of 3 passed**; 1 other red (section 3) | 27 m 47 s | not read |
| reload test, then movers | 4 passed | 9 m 43 s | 2.0 GB |

**I cannot yet say why it stopped.** Three explanations remain open, and the evidence does not rank them.
The movers path may have changed since 85b044be54. The set of predecessors has changed (12 then, 19 now).
Or the 2 Nov failure came from the mechanism in section 4, through a gas record, and something later
masked it. The 2 Nov finding stays where it is. Its "not bisected" claim is now "does not reproduce at
0b96265f69", which this record supplies.

## 3. The instance that does reproduce: a polluter that HIDES a red

In the 19-file run, `test_a_collections_journey_opens_on_the_bill_the_ledger_made_due.py::test_every_journey_opens_the_day_after_a_bill_the_ledger_made_due`
was red. It is **red alone too**. It is a real red, already recorded on 10 Nov and 12 Nov (the desk
write-off and old-credit findings), so it is not this atom's subject. **The count is this atom's subject.**
Alone it finds **4** stray journeys: PROS-2016-0020, SYN-2016-005, SYN-2016-024 and SYN-2016-325. After its
predecessors it finds **3**, because SYN-2016-024 drops out.

The bisect paired each of the collections file's 7 predecessors with it, all run in parallel:

| predecessor | strays |
|---|---|
| `test_a_book_reload_rebinds_the_modules_that_hold_the_book.py` | **3** |
| each of the other six | 4 |

**The ordered pair that reproduces:** `test_a_book_reload_rebinds_the_modules_that_hold_the_book.py`, then the
collections file. Two more runs of that pair, under `PYTHONHASHSEED` 7 and 14, also gave 3. Across all of
this, 4 of 4 runs with the reload test first gave 3, and 8 of 8 without it gave 4.

So the 10 Nov finding's "3 journeys" probably came from an ordered run, and 4 is the defect's real size. I
did not see that run's order, so this stays "probably".

## 4. The mechanism: a kept container holding replaced elements

The class is **module-level state**, the same class as L1, entered through a test helper this time.

- `reload_with_binders(run_phase2b)` re-executes `run_phase2b`, which redraws the roster as **new** dicts.
  They are equal in content: 1,049 of 1,049 records match, and the hashes of `CUSTOMERS`, `ELEC_CUSTOMERS`,
  `GAS_CUSTOMERS`, `EFFECTIVE_EAC_KWH` and `ACQUIRED_CUSTOMERS` are identical.
- On the re-import, `live_population` calls `register_drawn_points` again. That call is "idempotent by
  `customer_id`", so it refuses every new dict as a repeat. `company.interfaces.supply_book.DRAWN_CUSTOMERS`
  stays the same list object, still holding the **old** dicts.
- `run_phase2b.get_customer` is `supply_book.registered_point`. After the reload, it returns the roster's
  own object for **9 of 576** electricity legs and **4 of 473** gas legs. On a fresh import the figures are
  576 of 576 and 473 of 473.
- `reload_with_binders` rebinds modules that hold a container the reload REPLACED. `DRAWN_CUSTOMERS` was
  not replaced. Its *elements* were, so the identity scan cannot see it.
- So `main()` writes its registry-EAC rewrite into the new roster dicts, and every `get_customer` read gets
  the old drawn-band record. That is the L1 identity defect, re-created by the test that guards against it.
  `tests/conftest.py::_phase2b_book_is_put_back` restores the roster's contents. It does not restore the
  identity.

**The causal chain was measured one variable at a time** (`/var/tmp/h40-scripts/arm.py`, outside pytest,
phase 4c to 2016-12-31, the test's own stray predicate):

| arm | `get_customer` is the roster dict | journeys | strays |
|---|---|---|---|
| fresh import | 576 / 576 | 69 | **4** (incl. SYN-2016-024) |
| reload, supply book left as the reload leaves it | 9 / 576 | 69 | **3** |
| reload, then `DRAWN_CUSTOMERS` re-pointed at the reloaded dicts | 576 / 576 | 69 | **4** |

Only the identity differs between the second and third arms, and it moves the count by exactly the
journey that goes missing.

## 5. What was tried and did NOT explain it

- **A different book after the reload.** It is not different: 0 of 1,049 records differ.
- **Import-time side effects in any other module.** I diffed every loaded module's non-callable state
  before and after the reload, hashing each full `repr`. The only changes were matplotlib's
  `rcParamsDefault`, PIL lazy imports, `attr`'s repr context and `sys.modules`. No domain state changed.
  (A first pass truncated each repr at 20,000 characters and covered sim/company/saas only. It was
  re-run without either limit.)
- **The process-global RNG.** It is not used: `run_phase2b` and `run_phase4c` draw only from local
  `random.Random(seed)`.
- **Stale classes or functions held by other modules.** Of the 65 classes and functions the two modules
  own, none is held anywhere else, so an isinstance or enum split is not possible.
- **Weather-memo id reuse.** The memo is a `WeakKeyDictionary`, so a dead test world's id cannot alias.

## 6. The class fix, drawn on its own priority

Filed as `docs/staging/WORKER_FINDING_A_BOOK_RELOAD_LEAVES_THE_SUPPLY_BOOK_HOLDING_THE_OLD_RECORDS_SO_A_LATER_TEST_READS_A_SPLIT_BOOK_2026-11-14.md`
(LATENT, H_harness). It is not folded in here. H50 (`a_run_entry_point_leaves_no_state_behind`) is closed
at its target, and this is a different entry point: a test helper, not a run.

## 7. Memory discipline, and what it cost

Nothing was stopped. Two long jobs and `sim-runner` were running throughout. Headroom was 11.3 GB available
of 24.0 GB at the start and 16.2 GB before the 7-way bisect. **No full-suite run was made.** The largest run
was the 20-file ordered run, which took 27 m 47 s. The heaviest single process seen was 2.0 GB. Seven
3-to-6-minute pairs ran together and used about 10 GB in total. Two speculative half-bisects of the movers
file were killed unread once the full run showed the movers green. Wall clock for the whole bisect was
about 1 h 40 m.

## 8. End-to-end

I read this against canon's measuring-over-arguing and fail-closed rules, the L1 record, H50 and the 10 and
12 Nov collections findings together.

**Surprise 1: the pollution HIDES a red instead of causing one.** The explanations, ranked by evidence:

1. A split book in the supply book's identity. This is measured, and the re-pointed arm shows it is causal.
2. Nondeterminism. Refuted by 12 runs across two hash seeds.
3. The world or the desk logic is wrong. Not supported, because the fresh arm reproduces the alone count.

**Surprise 2: the 2 Nov movers reds have vanished.** I cannot yet say why (section 2).

**Concern.** H50's guard puts the book's contents back after each test, but not its identity, so a green
suite does not show that the book is whole. The class-fix finding carries the control that would show it.
