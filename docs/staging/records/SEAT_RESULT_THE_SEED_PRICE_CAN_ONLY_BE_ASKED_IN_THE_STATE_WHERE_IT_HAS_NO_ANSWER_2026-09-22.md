**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the seed price can only be asked in the state where it has no answer

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level`. Predictions filed
before the arithmetic, in
`docs/staging/records/PREREG_WHAT_SHAPE_IS_THE_SEED_PRICES_INTERVAL_ON_A_MEAN_OF_UNDETERMINED_SIGN_2026-09-22.md`;
marked in §5 below, **beside each prediction and not over it.** All five hold.

## 0. The draw's four warnings, re-measured before any work

The item arrived with four reasons it might already be spent. Three were, and none in the way the
note expected — recorded here because the next draw will carry the same four.

| The warning | Re-measured at 11:06 |
|---|---|
| PREMISE: both cited commits are ancestors of origin/main | **Correct and irrelevant.** They are the MEASUREMENT half, which the item says is finished. The code half is what was owed and it had not landed. |
| BASE: HEAD is 3 behind origin/main, 1 ahead | **SPENT.** `git rev-list --left-right --count HEAD...origin/main` reads `0  0`. The reconciler landed `c3bf6f761` between the draw and the turn. Every "holder work" reading computed against that stale base is void. |
| DUPLICATE: the id is already held by another writer | **SPENT — it is MY OWN DRAW.** `claimed_at` is 1790071529 = 11:05:29; this invocation started 11:05. The store holds exactly one entry and it is this id. |
| DUPLICATE: `the-belief-ceiling-...` holds the same file | **SPENT as a claim, LIVE as bytes.** That id is no longer in the claim store. Its work is still on the shared tree uncommitted — and it is **disjoint**: its hunks are all in `_svt_drift_belief`, mine are in `_leg_over_its_own_family`, the two floor constants and `MORE_SEEDS_WOULD_NOT`. No contest. |
| CONTINUATION: `a-shared-canonical-constant-...` | **Genuinely separate.** It is a census of `background/` canonical constants (the `_ITEM_PROSE_KEYS` shape). Nothing to do with the arms page. Carried on, as the note licenses. |

## 1. THE ANSWER — a seed price is wanted only when it cannot be given

`error_bar.selection_leg.seeds_needed_to_state_a_sign` published a bare integer. The key's grammar
is a plan: *draw this many and you will know.* It is not a plan, and the reason is structural
rather than a property of today's family.

The count solves `|m| > t(k-1)·s/√k`, so it grows as **`(t·s/|m|)²` — the estimate is in the
denominator.** The page computes it **only when `clears_its_own_bar` is False**, and failing that
bar is *precisely the statement that the family's own confidence interval for `m` contains zero*.
An interval containing zero contains denominators arbitrarily close to zero, and `(t·s/|m|)²`
diverges there.

> **So the two states coincide. A family that clears its bar wants no seeds; a family that fails
> its bar cannot be priced. There is no third state.** No family this page can hold yields a
> publishable count — not because of an arrangement of the code, but because of that argument.

Measured on the book-154 family the published figure is drawn from (mean −£1,069.475, sd
£5,398.314, sem £1,558.359, 0.686 errors from zero against a bar of 2.201):

| | |
|---|---|
| price at the point estimate | **101 seeds** |
| denominator's own ±1 standard error | −£2,627.83 … +£488.88 — **straddles zero** |
| price at the low end (denominator furthest from zero) | **19 seeds** |
| price at the high end | **471 seeds** |
| share of that interval needing more than the 10,000 search ceiling | **6.79%** |
| **the supremum** | **infinite** |

**19 and 471 are not a range.** The price is not monotone between them; it rises without limit at
the crossing. A reader handed "19 to 471" has been handed a bound that does not exist — which is
why `these_two_are_not_a_range` is a *published field* and not a comment.

## 2. What landed

**`tools/generate_value_arms_data.py`**

1. **`AUC_FAMILY_FLOOR_PATH`'s prohibition, widened to name what it actually forbids.** It said
   *"it bounds nothing else on this page"* — a blanket that forbids more than the two things it
   was written for. Now two named prohibitions: **the FOLD** (12+18 → 21 draws, the sibling lane's
   subject, and the union would declare no book at all) and **the SPREAD-AS-INTERVAL** (its stdev
   as any figure's error bar). And the reading the blanket was wrongly refusing is now licensed:
   next12's twelve seeds are **all on book 154** (12 of 12, min == max), which is **the published
   figure's own book**, while `NOISE_FLOOR_PATH`'s folded eighteen are all on **164**. So next12 is
   the only floor on disk that is a floor *for the run the page is drawn from*. Reading it on its
   own book folds nothing and lends its width to nothing. **The prohibition is on mixing, never on
   reading.**
2. **`_seed_price_interval` (new).** The price as an interval with the unboundedness keyed to
   `clears_bar` — which *is* the test of whether the denominator's interval contains zero — so the
   block returns `None` with nobody editing a string the day a family pins its mean.
3. **`_leg_over_its_own_family`** withholds the count and publishes the evidence in its place:
   `seeds_needed_unavailable` (the reason) and `seeds_needed_interval` (the arithmetic). The
   permanently-null key now *says* it is structurally null, so the emptiness cannot read as a
   measurement nobody took.
4. **`MORE_SEEDS_WOULD_NOT`, repaired — and this is the interconnection leg.** That constant
   pointed a reader at `error_bar.selection_leg.seeds_needed_to_state_a_sign` as the block that
   *"prices how many the family on disk would need"*. My change makes that key structurally empty,
   so the sentence would have sent a reader to an empty field to find a price this page had just
   established does not exist. **This is the third time that one sentence has been falsified by a
   correction thousands of lines away** — its own comment block records the first two. The claim is
   not narrowed here, it is **inverted**: seeds are still the right *kind* of remedy and the number
   of them is not a finite quantity.

**`tests/tools/test_generate_value_arms_data.py`** — `seed_price_complaints` and three tests.

## 3. The control, and the trap the direction named in advance

**The rule, keyed to the property:** *a seed count may carry an integer only when the estimate it
divides by clears its own bar.* No figure, no book, no seed count, no direction is named in it.

**The trap.** On the live feed the error bar's family is the folded eighteen, which **clears** its
bar — so `seeds_needed_to_state_a_sign` is `None` there for a reason that has nothing to do with
this rule. A control pointed at `site/data/value_arms.json` passes **vacuously**, and would go on
passing with the defect fully restored.

That is asserted, not described. `test_the_real_feed_would_NOT_have_entered_this_branch` pins
`clears_its_own_bar is True` on the live feed, and its message says that if it ever reds, nothing
is broken — the feed has reached the branch and the rule may be pointed at it too.

**R15 — the mutation, applied and reverted.** Restoring the one line
(`needed = seeds_to_state_a_sign(mean, stdev)` under `if clears_bar is False`) reds
`test_a_seed_price_is_NOT_published_for_a_family_that_cannot_bound_it` by name:

```
a seed count (101) is published for a family that does NOT clear its own bar, so the page
prices a question whose price has no upper bound
```

**And the feed-level test stayed GREEN under that same mutation** — the vacuity, demonstrated
rather than argued.

**The rare branch is asserted reachable.** Both verdicts come out of the same builder in the same
test (`cannot["clears_its_own_bar"] is False and can[...] is True`), so a builder answering `False`
to everything — which would satisfy every assertion about the failing family — is caught by the
clearing one.

## 4. The row the index did not have

`clears_zero_complaints` already forbids a seed price at a family that **clears** ("a priced remedy
for the wrong refusal"). The missing row was its mirror: a seed price at a family that **does
not**. The two together forbid it in every state, and *that* is the finding rather than an
oversight in either.

## 5. Predictions, marked beside themselves

| | Predicted | Measured | |
|---|---|---|---|
| P1 | point price = 101 | **101** | held |
| P2 | low end under 25; expect 19 | **19** | held |
| P3 | high end in 400..550; expect 471 | **471** | held |
| P4 | **not monotone; `None` over a band inside; unbounded above** | divergent for \|m\| < £105.5 | **held** |
| P5 | divergent band > 1% of the interval | **6.79%** | held |

P4 was the one that was not arithmetic I had been handed, and it is the one the control rests on.
Had it failed, "no upper bound" would have been a theoretical claim and the right control would
have been a different one.

**Closed form, not the scan I predicted with.** The prereg sampled 2,001 points. The shipped code
derives the threshold algebraically — `t(ceiling−1)·s/√ceiling` = £105.5 — which agrees with the
scan (band ±105) and costs nothing. The scan was the right instrument for *asking*; it would have
been the wrong one to ship.

## 6. What is NOT fixed, and it is live

`current_world.selection_leg.population_repair_bias.sign_on_the_shared_population` publishes
**`seeds_needed_to_state_a_sign: 1744`** beside `sems_from_zero: 0.166` and
`sign_is_stateable: false`. **That is the same defect, live on today's feed** — a family a sixth of
a standard error from zero, priced at a number.

It is **out of this control's reach by construction**: that block *republishes* the artefact's own
`distance_to_a_sign` (`generate_value_arms_data.py:10997`,
`distance.get("seeds_needed_to_state_a_sign")`) rather than deriving it, so the producer to fix is
`tools/run_value_cycle_ab.distance_to_a_sign` and every artefact already on disk carries the
unbounded count in its own bytes. Naming it rather than reaching for it: fixing the producer
without a story for the artefacts would leave the page reading a field its own producer no longer
writes.

**That is the next piece, and it is handed on.**
