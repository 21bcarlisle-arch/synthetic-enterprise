# The stale-copy refusal was specified as a subset test, and a subset test catches none of its three blocking findings

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Lane 0 delivery, 2026-09-08.** Claim:
`one-untracked-control-refuses-every-site-lane-commit-and-the-publisher-has-been-dark-twenty-hours`.

Part (a) of that direction landed. This is part (b), and it stops at the measurement on purpose:
the direction said *"if (b) will not fit the window, land (a), publish, and file what you learned
rather than holding both."* What I learned is that the criterion (b) prescribes cannot do the job
it was prescribed for, and that is worth more than a guard built to the wrong shape.

## What (b) asked for, verbatim

> *"For each path a commit stages, if the worktree copy's symbol set is a strict subset of
> `git show HEAD:<path>`'s, refuse and name the path."*

Named as the class behind three banked BLOCKING findings —
`A_REWRITE_DELETED_THE_BINDING_REPAIR`,
`TWO_LANES_EACH_BUILT_R1S_UNBIASED_MAGNITUDE_ESTIMATOR_AND_A_PATHSPEC_LAND_DELETES_NINE_OF_HEADS_SYMBOLS`,
`TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE` — and stated to have sixteen live members, oldest
`site/test_harness_delivery_record.py` at 32.3h.

## The census, run before writing the guard

Subject: the 524 paths `git diff --name-only HEAD` reports in the shared tree, of which 64 are
Python and readable at both ends. Symbol set = module-level `def`/`class`/assignment names.

| criterion | files it refuses today |
|---|---|
| strict subset, **import aliases counted as symbols** | **0** |
| strict subset, import aliases *not* counted (the naive read) | **1** |
| **any HEAD symbol lost** (gains allowed) | **8** |

**The prescribed criterion refuses nothing.** Not one of the 64 changed Python files has a
working-tree symbol set that is a strict subset of HEAD's. A guard shipped to that spec would have
been mutation-proven against a synthetic fixture, gone green forever, and been read as covering the
class.

**Its one naive firing is a false positive on the exact repair the project most wants.** Drop
import aliases from the symbol set — the obvious way to write it — and the census returns one file,
`tools/hot_water_base.py`, which "lost" `HOT_WATER_FIXED_LITRES_PER_DAY`,
`HOT_WATER_LITRES_PER_PERSON_PER_DAY` and `REFERENCE_OCCUPANCY`. It lost nothing. Those three names
are still bound, by `from simulation.premise_trace import _DHW_... as ...`, and the commit that did
it is the consolidation of one quantity that had two implementations — the fix for
`SEAT_FINDING_THE_SETTLEMENT_PATHS_HOT_WATER_IS_HALF_AGAIN_THE_MEASURED_VALUE_AND_I_BUILT_THE_SECOND_COPY`.
A subset guard written the obvious way refuses the de-duplication and passes the duplication.

**And it is blind to its own named example.** `site/test_harness_delivery_record.py` — the file the
direction names as the oldest member — loses 16 HEAD symbols and gains 2. It is not a subset, so
the prescribed guard never sees it. Nor are the other seven:

```
lost= 24 gained=  4  tests/tools/test_commit_refusal_attribution.py
lost= 23 gained= 11  tests/tools/test_r1_inference_ceiling.py
lost= 16 gained=  2  site/test_harness_delivery_record.py
lost= 12 gained=  4  background/self_clearing_alarm_census.py
lost= 11 gained=  4  tools/commit_refusal_attribution.py
lost=  7 gained=  2  tests/tools/test_dd_opening_arms.py
lost=  5 gained=  2  tests/architecture/test_year_keyed_rate_table_census.py
lost=  1 gained=  1  tests/tools/test_a_published_rate_says_which_rate_it_is.py
```

## Why the specification was wrong, which is the part worth keeping

**A lane that reverts another lane does not merely delete — it substitutes.** It wrote its own
version of the file. That version has its own helpers, its own constants, its own names. Symbols
lost *and* symbols gained is the signature of the defect; a pure subset is the signature of
something else entirely (a deletion commit, a file being emptied), which is not what happened in
any of the three banked findings. The third finding says so in its own title: *deletes nine of
HEAD's symbols* — it does not say the file became a subset, and it did not.

**The sixteen came from a different instrument.** The direction's own census recipe is
`git diff --name-only HEAD` filtered to code and pages, comparing **mtime against
`git log -1 --format=%ct -- <path>`**. That is a staleness proxy over file timestamps. The refusal
it then prescribes is a symbol-set test. Two different instruments, one count carried from the
first to justify the second — and the number does not survive the change of instrument. This is
`a-refusal-resting-on-arithmetic` wearing a census's clothes.

## What can actually ship, and why I did not ship it in this turn

`any HEAD symbol lost` is the criterion that matches the defect. It refuses 8 files right now, and
at least some of those 8 are ordinary honest rewrites — renaming a helper, restructuring a test
module — which lose HEAD symbols for good reasons. Shipped as a commit refusal today it wedges
every lane on the shared tree, which is the failure mode of
`freezing_a_ratchet_baseline_from_the_dirty_shared_tree` arrived at from the other direction.

So the open question is the discriminator, not the criterion: **what separates a lane substituting
its own copy from an author rewriting their own file?** The candidate that does not require a
census is authorship — the losing side's symbols were added by a *different* commit than the one the
working-tree copy descends from. That is answerable from `git log -L` / `git blame` on HEAD's
version of the lost symbols, and it is a bounded next piece of work. It is not a guard I can write
honestly in the tail of this turn.

## What is next

1. Settle the discriminator above on the 8 real members: for each lost symbol, is HEAD's author of
   that symbol the same lane as the working-tree copy's? Publish the split before writing any guard.
2. Only then write the refusal, keyed to `any HEAD symbol lost` **plus** the discriminator, and
   prove it fires on `site/test_harness_delivery_record.py` (a real member) before proving it stays
   quiet on `tools/hot_water_base.py` (a real non-member). Both legs on real files, not fixtures —
   a re-tuned synthetic fixture here would be fitted to the conclusion.
3. Whatever ships must count import aliases as symbols, or it inverts on consolidation commits.

## Correction to the record

The direction's "sixteen files are in that state right now" is not wrong about mtime and is wrong
about the state the refusal was specified over. The symbol-set population is 8, and 0 of them are
subsets. Left beside the claim rather than replacing it: the prediction was made before the
measurement, and the measurement refuted it.
