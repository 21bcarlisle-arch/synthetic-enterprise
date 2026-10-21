**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `index-the-two-whole-book-scans-per-renewal`)

# Pre-registration: the two per-renewal whole-book scans, indexed

Written 21 Oct 2026, 15:10 BST, BEFORE the A/B below ran. Parent:
`SEAT_PREREG_WHERE_THE_CENSUS_GREW_AFTER_10_18_2026-10-21.md`, whose profile named the two scans:
`estimate_prior_term_net_margin` (157 s of 2,169 s profiled, 369 calls) and `households_own_records`
(56 s).

## The census measurement the item asked to read first

It is not there yet. The item says to read the 10-22 03:37 run, and this was written on 10-21 at
14:31. The last census in the journal is 10-21. It ran 4h50m wall and 6h31m CPU, was killed at
17,400 s (UNPROVEN), and peaked at **10.3 GB**. That is above the 8.9 GB the item names. It ran
before `a854b39ff` landed, so it is the "before" figure, not the test. The 10-22 night is still
the measurement, and this change will be in it too. So the night cannot attribute its result to
either change alone. The A/B below is the only attribution this change gets.

## What changed

`RecordTable.rows_grouped(column, key_fn)` builds an index once. It catches up over appended rows
only, and drops itself on any write to the column it groups. Both readers ask the book for it when
the book has one (duck-typed, so `company/` imports nothing from `simulation/`). A plain list is
scanned as before. Each reader still applies its own whole filter, and gets the same rows in book
order.

## Probe

The same arm as the parent: `test_a_save_is_not_paid_for_by_the_stayers`'s `on` arm (`run.main` to
2018-09-30, under the save patches). Two worktrees, run serially in separate processes:
HEAD `a854b39ff`, then this one. Each wraps the two functions with a wall-clock accumulator.

## Predictions

1. **Equality:** stdout and the JSON of the whole `run.main` result are byte-identical between
   the arms. **Refuted, and nothing lands,** if either differs.
2. **Own time:** the two functions' combined own wall in the after arm is **under 10%** of the
   before arm's. Refuted if over 25%.
3. **Whole arm:** after/before wall is **about 90%** (the profile share was ~10%). Refuted if it is
   over 97%. A difference under 10% on this shared box cannot be attributed from the wall alone,
   which is why prediction 2 is the attributable one.

## Result (15:04 BST; the arms ran serially, HEAD `a854b39ff` worktree then this one, load 2.3-2.9)

| arm | wall | the two functions' own wall | peak RSS | stdout sha256 | result JSON sha256 |
|---|---|---|---|---|---|
| before (HEAD) | **546.5 s** | 34.4 + 11.4 = **45.8 s** | 3,402 MB | `55ddda44e700a6df` | `00bc9b63fa3bc6c6` |
| after (indexed) | **493.7 s** | 0.6 + 0.2 = **0.8 s** | 3,449 MB | `55ddda44e700a6df` | `00bc9b63fa3bc6c6` |

- **Prediction 1 HOLDS.** The digests are byte-identical, and the same as both arms of the parent's
  A/B. So the HEAD arm reproduces `a854b39ff`'s "after" exactly.
- **Prediction 2 HOLDS.** The two functions' own time is **1.7%** of what it was.
- **Prediction 3 HOLDS.** after/before = **90.3%**, against a predicted ~90% and a refutation line
  of 97%. The 52.8 s fall is the 45.0 s these functions lost, plus about 8 s of box noise.
- **Cost:** about +47 MB peak, which is the two indices' position lists. A census peak of 10.3 GB
  makes that about 0.5% of the margin the item named.
- **Mutations (all fire, `tests/simulation/test_a_grouped_read_of_the_book_answers_as_the_scan.py`):**
  no invalidation on a set; no invalidation on a delete; no catch-up after `extend`; every write
  dropping every index (the only-the-grouped-column leg); each reader ignoring the index (two
  separate mutants, caught by the spy leg); the company key not being the billing account.
- **What it buys the census** is inference. About 8% of each simulation run, on top of `a854b39ff`'s
  39%. The 10-22 night carries both, so it cannot tell them apart. This table is the attribution.

**Is a further turn on run cost worth it?** Not before the 10-22 journal. The super-linear costs
the profile named are now all indexed. What remains (`fold_to_days`, `run_hedged_term`,
`notice_as_of`, `settle_period`'s per-call work) grows linearly with the book. If 10-22 still
times out, the next lever is the census's own shape (its timeout or its sharding), not another
scan.
