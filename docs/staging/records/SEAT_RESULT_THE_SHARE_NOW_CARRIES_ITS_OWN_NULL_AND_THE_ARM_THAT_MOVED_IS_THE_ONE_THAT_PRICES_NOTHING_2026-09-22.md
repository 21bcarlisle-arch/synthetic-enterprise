**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The share now carries its own null, and the arm that moved is the one that prices nothing

**Claim:** `the-share-the-page-leads-with-has-seed-noise-ten-times-the-gap-it-explains`
**Filed:** 2026-09-22. Drawn as Lane 0 delivery. Prior result this builds on:
`docs/staging/records/SEAT_RESULT_THE_EIGHTEEN_TIMES_IS_THE_CONTROL_ARM_AND_THE_SHARES_OWN_SEED_NOISE_IS_TEN_TIMES_THE_GAP_2026-09-22.md`
(repointed 2026-09-23 when the RESULT family was routed to `records/`; the document is the same one).

---

## What landed

`current_world.composition` carried `level_share_of_advantage: 0.9848` with `readable: false`, and
explained its 17.9× disagreement with the superseded panel by counting three confounders — the
date, the commit and the book. All three genuinely differ. The explanation was an order of
magnitude too small for what it explained, and the ruler that says so had been measured five days
earlier and wired to nothing.

Two blocks are now computed in `tools/generate_value_arms_data.py` and published on
`/capabilities/#arms-composition`:

**`the_shares_own_null`** — `level_share_spread` read from `AUC_FAMILY_FLOOR_PATH`, the 12-seed
family that re-runs world `39a192ce04c1eda8` with nothing moved but the per-household elasticity
draw. The statistic spans 0.0666 to 12.0735 there. Its statement prepends `why_not_readable`, which
the page already renders, so the refusal now **leads** with the reason that does not depend on
which two runs are being compared.

**`which_arm_moved`** — the numerator's movement split between the two arm nets that compose it.
The level arm's net moved +£450.11 (+0.29%); the control arm's moved +£17,666.33 (+12.61%);
97.52% of the two arms' absolute movement is the control arm. Rendered as its own paragraph beside
the attribution refusal, which stands.

Control: `tests/tools/test_a_share_whose_own_null_outruns_the_gap_is_not_readable_at_one_run.py`,
12 legs, keyed to *the statistic's own null range exceeds the gap being attributed* and to no
number a re-draw moves.

## The comparator is 12.9×, not 181×, and the change is not cosmetic

The finding was written around the endpoint fold — 12.0735 / 0.0666 = 181× against a 17.9×
disagreement. That fold divides one draw of the share by another draw of it. It is undefined the
moment a draw lands at or below zero, and this family's numerator is nowhere near determined enough
in sign to rule that out: the page's own `_composition_in_this_world` docstring records the level
leg running −£882.45 to +£9,085.08 across three re-draws.

What is published instead compares two **spans of one statistic**: the family's range
(12.0069 share units) against the gap between the two draws the page prints (0.9297). Both are
differences of `level_share_of_advantage` in the same unit, so their ratio — **12.9** — counts how
many of the observed gap fit inside the null. `min`, `max`, `mean` and `stdev` are all carried, so
the fold is available to a reader who wants it and is not what a control is keyed to.

The argument survives the smaller number intact, and the reason is that it is **conservative**: the
null moves one thing, the observed gap moves the seed *and* the date *and* the commit *and* the
book. Fewer sources of variation already spanning more than the gap is what makes the gap
uninformative, and that direction holds a fortiori.

## The null is on a neighbouring book, and the page says so

`next12` is drawn on 154 settled accounts. The published run's arms were scored over **164–165** —
control 164, level 164, value 165. So the seed sensitivity of this statistic is established one
book over and is *not* established on its own.

It is published anyway, with the mismatch named in the rendered sentence, because a measured null
on a neighbouring book is evidence and the alternative is the state the page was in: a difference
explained by a confounder story with no ruler underneath it at all.

The comparison asks **containment, not equality**, and that is load-bearing. A function asking "is
the run's book equal to the family's" returns `None` on every real input, because the arms of every
three-arm run on disk span two books. A caveat that is structurally unable to answer agrees with
every answer to it — so the run's books are published as the span they are.

## Correction to the prior result's §1, beside its claim

That result concludes: *"of the three movers the drawn item names — book, commit, arm code — the
one that did the work is the **book**, and it is attributable after all."*

**The first half is right and the conclusion does not follow.** `git diff 04361d6c7 b329e702b --
company/ simulation/` is 4,377 insertions across 28 files, including `premise_population.py`,
`settlement_choice.py`, `svt_rates.py` and `run_phase2b.py`. The control arm runs through all of
that. So the commit can reach the control net directly, and the book count (164 → 154) is itself an
**output** of the code those commits differ in — book and commit are not separable here at all.

What the 97.52% establishes is narrower and still worth publishing: the movement is in the arm that
takes no per-customer pricing decision, so **nothing either pricing arm does can reach it**. That
rules out the reading a reader is most likely to take — that the company got better or worse at
choosing — and locates the move in the baseline the split is measured against. `which_arm_moved`'s
statement says exactly that and stops there.

## What is still owed

1. **A floor on the published run's own book.** `next12` is the nearest available and it is one
   book over. Nothing on disk is a null for the 164/165 run.
2. **The §7 sentence from the prior result** — that the seed price for the selection leg's sign is
   unbounded above, because the estimate it divides by has an undetermined sign — and the control
   it names: *a seed requirement may not be published when the estimate it divides by does not
   clear its own bar*. Not taken here; this turn was the composition block.
3. Not the re-run as the original item specified it. The prior result's §5 stands unaltered.

## Mutations run and reverted

| mutation | outcome |
|---|---|
| `null_is_wider_than_the_disagreement` → always `True` | 2 legs red, including the partition control |
| → always `False` | 3 legs red |
| drop the `n < 2` guard | `test_a_family_of_one_draw_is_not_a_null` reds |
| `_read(path) or {}` (unreadable falls through to the size guard) | reds **on the reason string**, not on `available` — the leg it was written for |
| `share_of_the_movement` denominator → `abs(control − level)` | `test_the_arm_share_counts_what_it_says_it_counts` reds |
| arm deltas swapped in sign | `test_the_numerator_delta_is_the_two_arms_own_difference` reds |
| `>` → `>=` | **silent — an equivalence at these inputs**, recorded as one and deliberately not pinned: a tie between two measured spans is not a state this page can distinguish |

## Note on the draw

The duplicate-work check named `the-companys-churn-belief-is-flat-across-the-book-where-the-world-
responds-nine-fold` as holding `site/data/value_arms.json`. It does not — its five bound paths are
the churn-belief ones, and it landed at `cff89ebaf`. Genuinely different work, so this carried on.

The path check graded the shared tree's `site/data/value_arms.json` as `predates landing`, and
`refresh_to_head` **refused** it: the copy supplies 123 leaves HEAD lacks, so it is not a copy HEAD
supersedes either. The shared copy of `tools/generate_value_arms_data.py` carries 26 hunks against
HEAD from other lanes. Both were left untouched. All work was done in a linked worktree at HEAD,
where the generator reproduces HEAD's feed byte-for-byte apart from its own publishing-tree stamp,
and landed with `surgical_land --content`.
