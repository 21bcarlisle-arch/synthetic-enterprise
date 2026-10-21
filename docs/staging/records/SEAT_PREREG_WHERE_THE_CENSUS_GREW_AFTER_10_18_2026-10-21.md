**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `the-census-times-out-before-it-says-anything`)

# Pre-registration: where the census grew after 10-18, and where one run spends its time

Written 21 Oct 2026, 12:45 BST, BEFORE either probe below ran. Parents:
`SEAT_PREREG_THE_TWO_CENSUS_SPIKES_MEASURED_ALONE_2026-10-21.md` (the peak is fixed) and
`SEAT_PREREG_THE_CENSUS_TIME_IS_THE_FORWARD_PRICE_RESCAN_2026-10-21.md` (the forward price
buys ~17% of a whole run; "the run profile is next").

## What is known before measuring

- The 10-18 census finished in 13,190 s. Its 80 slowest rows sum to 7,891 s. About 5,000 s of
  that is simulation runs: fixture setups, or calls that drive `run_phase2b`.
- 10-19 and 10-21 were killed at 17,400 s. 10-21 used 6h31m of CPU, against 4h46m-5h12m on
  the complete nights. So the suite did MORE WORK. That is not starvation alone.
- A killed census prints no `--durations` table, so the nights that matter left no per-test
  record (the census discards partial output, and correctly).
- 26 test files were added to `origin/main` after 10-18 03:00. Thirteen of them name
  `run_phase2b`, `run.main(` or a module-scoped fixture. Those thirteen are the candidates for
  the growth.

## Probes

- **A (profile).** cProfile of one arm of the census's slowest fixture
  (`test_a_save_is_not_paid_for_by_the_stayers`: `run.main(report_end="2018-09-30")`, under
  the save patches), at `83eb9c697`, with the forward-price index in place.
- **B (growth).** The thirteen new modules, run alone with `--durations=0` at `83eb9c697`.

## Predictions

1. **A:** no single production function holds more than 30% of the run's cumulative time, now
   that the forward price is indexed. The 17% that `83eb9c697` bought was the largest single
   leaf. **Refuted** if one non-framework function (not `run.main` or its month loop) holds
   more than 30%.
2. **B:** the thirteen modules sum to **>= 2,500 s**, which is enough to explain most of the
   10-18 -> 10-21 growth (>= 4,200 s wall, plus box load). **Refuted** if they sum to under
   1,000 s. In that case the growth lies in pre-existing tests that became slower, and the next
   step is a full durations run at HEAD.

**Done means:** the largest contributors found by A or B are shrunk at their source, with the
answer unchanged and shown equal, never by deselecting a test. The before and after times are
written below. If neither probe finds a source that can be shrunk inside one turn, the number
is written here and the item is handed on with it.

## Result of B, and what it moved (13:00 BST, before A was read)

**Prediction 2 is REFUTED.** The thirteen new modules sum to **37 s** (81 passed), not
>= 2,500 s. The growth is not in new tests. Reading `git log` for the window found a likelier
cause: `8927e9345` (10-20 23:14) made the founders 400 HOUSEHOLDS, which is 689 supply points,
up from 400 supply points. The 10-21 census was the first night to run every simulation
fixture against a ~72% larger book. That is the director's ruling and is not a lever. The lever
is any cost that grows faster than the book.

## Result of A (profile, 2,169 s under cProfile, 7.3bn calls)

**Prediction 1 HOLDS.** No production leaf holds more than 13%. The largest:
`fold_to_days` 287 s, `ForwardBook.settle_period` 212 s (14.9m calls, each a linear scan of
the contract list), `run_hedged_term` 181 s, `notice_as_of` 165 s, and
`estimate_prior_term_net_margin` 157 s (369 calls, each a scan of the whole book).

**One cost is QUADRATIC in the book, and it is a printout.** `_main` made 595m row visits and
594m column reads. They came from the "Per-customer lifetime P&L" report, which filtered the
whole book once per customer, about 1,050 customers x ~567k rows. A larger book pays it twice
over: more rows, and more customers.

Also: `meter_reads.assumption_toggle` re-parsed `assumption_toggles.yaml` on each of its 262
calls, 45 s.

### Added before the A/B ran (13:15 BST)

Three shrinks, each with an unchanged answer by construction: group the printout's rows once in
book order; key `settle_period`'s first match in a dict; parse the toggle register once per
distinct text. The A/B runs the same arm in a HEAD worktree and then in this one, serially, in
separate processes.

3. **Equality:** stdout and the JSON of the whole `run.main` result are byte-identical between
   the two arms. **Refuted, and nothing lands,** if either differs for any reason other than a
   path or a clock.
4. **Time:** the after arm's wall is **<= 80%** of the before arm's. The profile shares
   (~10% + ~2% + the printout's ~15-20%) predict about 70%. The arms run serially on a shared
   box, so a difference under 10% is not attributable.

## Result of the A/B (13:40 BST; the same arm, serially, HEAD `83eb9c697` worktree then this one)

| arm | wall | peak RSS | stdout sha256 | result JSON sha256 |
|---|---|---|---|---|
| before (HEAD) | **923.8 s** | 3,380 MB | `55ddda44e700a6df` | `00bc9b63fa3bc6c6` |
| after (three shrinks) | **565.6 s** | 3,387 MB | `55ddda44e700a6df` | `00bc9b63fa3bc6c6` |

- **Prediction 3 HOLDS.** stdout and the JSON of the whole result are byte-identical.
- **Prediction 4 HOLDS.** after/before = **61%**, inside the predicted <= 80% and near the
  ~70% the profile shares implied. The two arms ran serially (load 3.5-3.8 over the first,
  2.3-3.5 over the second), so the speed-up is a little flattered. A 39% fall is far outside a
  10% load band, though.
- **What it should buy the census.** This is inference. About 5,000 s of 10-18's 13,190 s was
  simulation runs. Those runs now carry the 400-household book, which is why 10-21 used ~30%
  more CPU. If each run costs ~61% of what it did, the census falls by roughly 2,000-3,000 s
  from where 10-21 would have finished. Together with `83eb9c697`'s ~1,150 s (svt-origin) and
  ~17% per run, the next night should land inside 17,400 s. It is not measured. The 10-22
  journal measures it, along with every other lane's landings that night.

**Mutations (all fire):** a later contract overwriting the first under one key; a key that drops
the term; a missing key falling through to some contract; the toggle cache removed; the toggle
cache keyed on the path instead of the text. **One shrink has no control:** the printout
regroup is stdout only, so no test reads it. A test would cost a whole run, the cost being
removed, so its evidence is the identical stdout digest above. That is a missing test, not an
equivalence.

**Left for the next piece, from the same profile.** Two costs still scan the whole book per
renewal: `estimate_prior_term_net_margin` (157 s under profile) and `households_own_records`
(56 s). Each needs an index the run maintains as `all_records` grows, and the first is a
company-side reader. That is a wider change than this one. The flat leaves (`fold_to_days`,
`run_hedged_term`, `notice_as_of`) are per-record work that grows only linearly with the book.
