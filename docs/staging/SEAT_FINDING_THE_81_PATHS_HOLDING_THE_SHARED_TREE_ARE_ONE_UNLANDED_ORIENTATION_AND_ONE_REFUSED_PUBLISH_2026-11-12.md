**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The 81 paths holding the shared tree are one unlanded orientation and one refused publish (2026-11-12)

*Lane-0 item `the-81-live-copies-holding-the-shared-tree-are-landed-or-reverted-by-their-lanes`.*

## The premise, re-measured at 22:50Z

The premise still holds. The shared tree is 61 behind origin. `paths_blocking_fast_forward` names 1,477
paths. A no-write dry run of `advance_shared_tree` holds 81 of them and proves the other 1,396 lossless.
For the dry run, every writer, the lock and the ff were injected to raise. The held set falls into three
groups by who wrote it.

**A. The 22:22 orientation's record never reached origin (3 paths).** These are `DIRECTION.yaml`,
`decisions.jsonl` and `SEAT_STRETCH_LOG.md`, written for the 21:21 orientation. The `delivery-seat.service`
journal for 22:22:49 reads `landing refused (DirectionNotLanded): origin/main moved under the gate on all 1
attempt(s) inside 2793s`. Origin's record is still the 19:01 one. Two producer logs sit in the same group,
because each holds rows origin lacks:
`docs/observability/naive_organ_log.jsonl` has 2 rows and `site/state/live_decisions_log.jsonl` has 4
(the 8 to 11 Nov decision runs). Neither copy deletes a row that HEAD has.

**B. A publish of run 6fe7827ab2 that did not land (77 paths).** It covers 72 `site/data/customers/*.json`
pages, `docs/state/{customer_sample,sim_data}.json`, `site/code/galaxy.png` and `site/data/director_delta.json`.
All of them were written between 16:26 and 16:34 on 11 Nov. `docs/staging/done/run_complete_20261111T160541Z.md`
records `Publish outcome: did not land`. Origin then published the same run from a worktree at 20:31
(e816040ce). So each copy here is an earlier render of a run whose published render is already on origin.
The run JSON it came from is still in `docs/reports/`. No class clears these copies, for two reasons. The
generated-path oracles cannot see them: the customer pages have composed names, the `.png` has no artefact
suffix, and `docs/state/` is not a declared tree. And `refresh_to_head` refuses them as rival drafts: for
example, SYN-2016-536 carries a `ledger.entries[51].level_dd` key that origin's render lacks.

**C. The retired 205-of-238 refund finding (1 path).** Origin deleted it from the root and added it under
`done/` in 63ede2e3b. Every line of the shared copy is in origin's `done/` copy. Origin's copy adds only
the retirement section, which says the two unlanded sections "land here unchanged". The copy has nothing
to lose, but no class covers a root edit whose content origin moved to another path.

## What landed with this finding

Group A, landed on origin as the orientation lander would have landed it. `DIRECTION.yaml` goes in as the
shared bytes. Origin's copy differs from it only in the orientation's own fields (`oriented_at`, `thesis_read`,
`stretch_reviewed`, `focus`, `not_now`, `wrong`), and `for_the_director` is identical. The stretch log and
`decisions.jsonl` go through `delivery_seat.rebase_append_only`, which puts the shared block onto origin's
copy. The two logs land as origin's rows plus the missing rows, each placed after the row it follows on
disk. The 21:21 record is out of date (its item 1 asks for the F net, which 37d934286 has since landed),
but it is newer than the 19:01 record origin still carries. The next orientation replaces it.

To reverse it, revert the commit. Nothing on the shared tree is written.

## Pre-registration (written before the post-landing dry run)

Prediction: once this lands and the shared tree fetches, the same dry run holds **78**: the 77 of B and the
1 of C. `DIRECTION.yaml` becomes a tracked twin. The other four A paths fall to the ninth class
(`superseded_live_verdicts`), because none of them holds a line origin lacks. If any A path is still held,
either the shared copy was rewritten between the build and the run (a fresh orientation, or an organ
tick), or the ninth class does not read an inserted row as superseded. The result goes below and does not
replace this paragraph.

## What stays, and the recommendation

Even with A cleared, B and C still hold the advance. Each needs a class that `advance_shared_tree` can
prove. The isolated seat cannot write the shared tree, so this item cannot finish them.

- **B: recommended build.** Add a class for a render of a run whose published render is on origin. It would
  key on the `run_complete_*` marker that says `did not land`, and on an origin publish commit for the
  same `Git:` id that is newer than the copy's mtime. It would preserve the copy to a ref and then restore
  it, as the abandoned class does. The cheaper alternative is to declare `site/data/customers/` and the
  three stragglers to the generated-path oracle. Restoring a producer's output is free, but that would also
  restore the next unlanded render, which the publish marker can tell apart. So I recommend the marker key.
- **C: recommended build.** Add a class for a tracked root edit that origin deletes and re-adds elsewhere
  with every line of the copy. Preserve, then restore.

## Result

*(pending: the post-landing dry run)*
