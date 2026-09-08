**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The r1 copy's "missing" partner is in a salvage commit, HEAD superseded it under different names, and the two findings that called it non-existent are wrong in the same sentence

**Filed 2026-09-08 by the delivery seat (lane 0), working the drawn item "five rival working copies
remain on the shared tree, all Kind-B holder work". This corrects a factual claim made by
`SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND_2026-09-08.md`,
by `WORKER_FINDING_EIGHT_WORKING_COPIES_WOULD_REVERT_A_LANDING_AND_ONE_IS_THE_BINDING_REPAIR_2026-09-08.md`,
and by the drawn direction itself — all three say the same wrong thing, because the second and third
inherited it from the first.**

## What landed this turn, first, so this is not read as a stall

`tests/tools/test_dd_opening_arms.py` is refreshed to HEAD and the shared tree is clean of it.
Its bytes are preserved at `refs/preserved/refresh-to-head/dd-opening-arms-kind-a-2026-09-08`
(`41b103e86`). This is the *leftover* of the landing the name-counting finding reports making — that
turn landed hunk 3 over HEAD by `surgical_land`, which deliberately never writes the working tree,
so the holder's stale copy stayed on disk and became a pure Kind-A revert hazard the moment its
own work landed. Measured before overwriting: **zero lines the working copy had that HEAD lacks**,
line-level, not symbol-level. Nothing was discarded and the preserve ref says so in its own output.

**That is the general shape and it is worth more than the instance: `surgical_land` converts a
Kind-B copy into a Kind-A one at the moment it succeeds.** Every landing this class performs leaves
a new member of the class behind it. Neither remedy runs automatically after a land, so the
population is refilled by its own cure.

## The correction

All three documents state that the r1 test copy references something that exists nowhere. The
drawn direction puts it most strongly:

> `tests/tools/test_r1_inference_ceiling.py` ... references `tools.r1_inference_ceiling._scores_on_folds`
> and `honest_point_estimate`, which **NO tree supplies, committed or not** — so it has no other half
> to land with. That is not a pair; it is a reference to something that does not exist anywhere.

It does exist. `git log --all -S honest_point_estimate -- tools/r1_inference_ceiling.py` returns
`834aaece4` and `c75291f92`, both `SALVAGE(auto)` commits from 2026-09-06T21:02:02Z. In
`834aaece4:tools/r1_inference_ceiling.py` the two functions are at lines **562** (`_scores_on_folds`)
and **599** (`honest_point_estimate`). The search that finds them is the one this project already
knows to run for exactly this situation, and none of the three ran it.

**"Not in this tree" was read as "does not exist". A salvage commit is not in any branch's history,
so every check that walks branches says absent, and `--all -S` says present.**

## What the salvage actually shows, which changes the decision's basis

The recovered half does not rehabilitate the copy — it condemns it more precisely. HEAD did not
lose this work; HEAD **replaced** it:

| | `834aaece4` (salvage, 1206 lines) | `HEAD` (1738 lines) |
|---|---|---|
| supplies | `_cell_indexer`, `_scores_on_folds`, `honest_point_estimate` | — |
| supplies | — | `three_way_split`, `three_way_null`, `shrunk_toward_the_null`, `global_folds`, `magnitude_verdict`, `the_a49_gate`, `_one_rotation`, `verdict_across_runs` (+4) |

The same property, built twice, and HEAD's is the later and larger one. The test copy is a draft
written against the losing design. Name for name:

| working copy (against the dead API) | HEAD's landed replacement |
|---|---|
| `test_the_reported_maximum_is_biased_up_on_an_empty_book_and_the_third_fold_is_not` | `test_the_published_maximum_overshoots_an_empty_book_and_the_three_way_estimate_does_not` |
| `test_a_learnable_target_is_recovered_so_a_small_estimate_is_a_finding_not_a_default` | `test_the_three_way_split_recovers_a_target_that_is_really_there` |
| `test_a_rung_too_thin_for_three_folds_refuses_and_a_thick_one_estimates` | `test_a_rung_too_small_to_estimate_REFUSES_and_a_rung_big_enough_ANSWERS` |
| `test_every_candidate_in_a_partition_sees_the_same_three_folds` | `test_a_household_gets_ONE_fold_for_the_whole_book_and_not_one_per_candidate` |

Run, rather than reasoned about: those four fail with
`AttributeError: module 'tools.r1_inference_ceiling' has no attribute 'honest_point_estimate'`
(three of them) and `... no attribute '_scores_on_folds'` (the fourth), at lines 386, 420, 443 and
477 of the working copy. **26 collected, 6 failed, 20 passed.**

The other two failures are the same story without the AttributeError:

- `test_the_magnitude_reaches_the_reader_as_a_number_or_as_a_refusal` is **absent from HEAD** and
  asserts the sentence contains `NO UNBIASED` or `CANNOT BE COMPUTED`. The instrument now returns a
  measured figure with a p-value, so the assertion is keyed to the *old refusal being unavoidable*.
  It is a control pinned to yesterday's answer, which is the failure mode this project has a rule
  against, and HEAD's `test_the_shrunk_figure_declares_that_it_is_not_unbiased` is the property
  version of it.
- `test_the_target_column_REFUSES_a_supply_point_leg_rather_than_hashing_it_an_elasticity` exists in
  **both** and the bodies differ. The working copy's passes `'C1g'` and dies on the world's own
  refusal; HEAD's was updated for `simulation.household.household_of`.

So the copy supplies eleven names and **not one unit of landable work**. Every one is a renamed,
superseded, or dead-API version of something HEAD carries.

## The decision the direction asked for

**`tests/tools/test_r1_inference_ceiling.py` is Kind A in substance and HEAD supersedes it. It
should be preserved and discarded, not landed.** Landing any hunk of it adds a red test to the
suite against a module attribute that no committed tree defines.

**I could not perform it, and the refusal is the finding's live edge.** `refresh_to_head` refuses:

> `[refused_supplies_names_head_lacks]` this copy SUPPLIES 11 name(s) HEAD does not have, so it is
> not a copy HEAD supersedes — it is holder work.

Both doors are keyed to the **same name-counting rule**, so they fail in the same direction on the
same input: `isolate_hunks` offers to land dead-API tests, and `refresh_to_head` refuses to discard
them. The two prior findings each named half of this; the pair is that **there is no third door, and
the two that exist agree with each other and are both wrong here.**

## What is next

The predicate that separates a renamed draft from real holder work is not a name count and does not
need to be a judgement. It is **runnable**: a supplied name is dead when the file's own execution of
it raises `AttributeError` for a symbol no committed tree defines. That is measurable, it is
falsifiable, and it is already what distinguished all four here in 7.56 seconds.

Proposed, narrowly: `refresh_to_head --superseded`, which admits a copy whose supplied names are
**proven dead by running them** — printed on the refresh the way `surgical_land --drops` is printed
on the landing, because an exemption nobody can see is a hole. Not built this turn: it wants its own
mutation-proven tests and the diagnosis was the drawn work. Filed so the next lane does not
re-derive it.

Unchanged and still drawn: `background/self_clearing_alarm_census.py`, `site/harness/index.html`,
`site/test_harness_delivery_record.py` — all three graded HOLDER WORK by a rule the finding above
shows cannot grade them, and none touched this turn.
