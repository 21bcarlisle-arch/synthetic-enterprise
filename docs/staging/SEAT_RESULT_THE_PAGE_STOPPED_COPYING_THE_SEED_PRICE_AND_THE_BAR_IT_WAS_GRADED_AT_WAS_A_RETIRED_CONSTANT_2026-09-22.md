**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The page stopped copying the seed price — and the bar it was graded at was a constant this repo had deleted

**Claim:** `the-republished-seed-price-carries-an-unbounded-count-in-every-artefacts-own-bytes`
**Pre-registration:** `docs/staging/records/PREREG_WHAT_THE_REPUBLISHED_SEED_PRICE_LOOKS_LIKE_WHEN_IT_IS_DERIVED_INSTEAD_2026-09-22.md`
(filed before the arithmetic; **all six predictions held**, and P5 refutes a field my own
predecessor commit landed — see below).

## The premise, re-measured before starting

`06e316ae4` is an ancestor of `origin/main`, so the item's cited commit has landed. The premise is
**not** spent: that commit fixed the BUILDER and said so in its own message under *"STILL LIVE, NOT
FIXED, handed on"*. The republish path was live on `site/data/value_arms.json` at draw time —
measured, not assumed:

    current_world.selection_leg.population_repair_bias.sign_on_the_shared_population
      sems_from_zero: 0.16591746236761307
      sems_needed_to_state_a_sign: 2.0
      seeds_needed_to_state_a_sign: 1744

The duplicate-work check named two live claims. `the-republished-seed-price-...` is **this draw's
own claim** re-reported as a rival — the known shape. `the-belief-ceiling-names-no-world-and-the-
grader-never-stamps-one` holds `tools/run_value_cycle_ab.py`, which this item names, and that
collision is real; §"What is deliberately not done" records how it was handled.

## What was wrong, in one sentence

The page published a number of seeds as the price of settling a question, where the count divides by
an estimate the page simultaneously reported as **0.166 standard errors from zero** — so the
denominator's own interval contains zero and the quotient has no upper bound. `1,744` is the more
misleading of the two instances precisely because it is large: it reads as a considered price rather
than as an artefact of a near-zero denominator.

The landed control could not reach it **by construction**, and that was stated in advance rather
than discovered afterwards: the control is written over the builder, and this block *copied* the
field out of the artefact's own `distance_to_a_sign` instead of deriving it. **Copying was the
carrier, so copying is what stopped.**

## The second defect, which the bytes made plain and nobody had asked

The admissible artefact was produced by `18327d977` — a tree that **predates the 2026-09-18 deletion
of `SEMS_TO_STATE_A_SIGN = 2.0`**. Its `distance_to_a_sign` grades the family at a flat `2.0`: the
exact constant this repo deleted, with the deletion note recording it as *"short at every family this
instrument has ever drawn and short by MORE as the family shrinks"*. So the live page was publishing
a **retired rule under the live rule's key name**.

And a consumer could not have noticed. `sems_needed_is_derived_from_the_family_size` — the field
added specifically so a reader could tell a pinned bar from a derived one — **is absent from that
artefact entirely**, because the producing tree predates it. A `.get()` returns the same `None` as a
derived-bar denial. That is the *"a field structurally unable to answer agrees with every answer"*
shape, and it is why the bar is now re-derived rather than trusted.

## What the numbers actually are

| quantity | published before | published now |
|---|---|---|
| bar | 2.0 (retired constant) | 2.200985 (`sems_to_state_a_sign(12)`) |
| seed price | `1744` | withheld; point evaluation 1677, endpoints 37 and 69, **not a range** |
| verdict | producer's, at 2.0 | producer's **AND** this repo's rule; both published |

**P2 held and inverted the naive reading.** A stricter bar looks like it must cost more seeds —
`1744 · (2.201/2.0)² ≈ 2112`. It costs *fewer*: 1677. `seeds_to_state_a_sign` scans against the bar
the **projected** family would face, and `t(m-1) → 1.96` past a thousand draws, so the pinned 2.0 was
charging a ~1,700-seed family a twelve-seed family's tail. The published 1744 was not merely
unbounded, it was also wrong in the direction that made it look larger.

## P5 — a correction to a field `06e316ae4` landed three commits ago

`share_of_the_interval_the_search_cannot_price` published **6.79%** on the book-154 family. The
shared-population family returns `0.0679033636330581`. Identical to thirteen digits — and **not**
because the families resemble each other.

When the denominator's one-error interval contains the whole unpriceable band, both the `min` and the
`max` bind on the band and the share collapses to

    t(ceiling-1) · sqrt(n / ceiling)

The mean cancels. The spread cancels. Both families are n = 12. **A reader who took 6.79% as a
property of the family it sat beside was reading the seed count restated back to them.**

The field is kept — it *is* the right quantity in the other regime, where the interval is narrower
than the band — and it now travels with `that_share_is_a_function_of_the_seed_count_alone`, keyed to
the containment and never to `n == 12`. Filed here beside the claim rather than quietly revised,
because a wrong prediction kept next to its result is the only evidence the experiment was designed
before the answer was known. This one was predicted, in writing, before it was run.

## The second, smaller item: the remedy is priced rather than asserted

`_staleness_caveat` ended *"re-running the noise floor on the point estimate's own run is owed
work"* and stopped. Honest about what is missing; silent about what it is worth — and a reader meets
"owed work" as *"and then the page could say something"*.

It was not priceable when written. It is now, because `AUC_FAMILY_FLOOR_PATH`'s widened prohibition
licenses reading `next12` on its own book, and **next12 IS a floor on book 154** — the book the point
estimate prices. Measured: 0.686 of the 2.201 errors from zero, 12 seeds, and no publishable price.

**P6 held, including its careful half.** The sentence is *not* false and is not deleted: the arms
span books 154–155 and that floor covers one, so the owed re-run is still strictly better evidence.
What the page now adds is that **the closest thing to an answer already on disk says more draws of
this instrument do not buy a direction.** The book number is read off the family's own seeds, never
pinned — a family whose seeds disagree names no book and the sentence says "same".

## Controls, and the mutation each one survives

Six mutations applied and reverted; each reds its named test, and the tree was verified byte-identical
afterwards.

| mutation | test that reds |
|---|---|
| restore the copied seed count | `..._is_DERIVED_and_never_copied_off_the_artefact` (+ the FIRES leg) |
| republish the artefact's retired bar | `..._bar_is_this_repos_rule_and_not_the_artefacts_retired_one` |
| AND → OR on the two verdicts | same |
| pin the n-alone flag True | `..._says_when_it_is_a_function_of_the_seed_count_alone` |
| unprice the owed re-run | `..._priced_by_the_nearest_floor_on_the_figures_own_book` (+ the live-page leg) |
| put a seed count back in the plan grammar | `..._prices_the_gap_without_naming_a_number_of_seeds` |

**Every rare branch is asserted reachable before anything is asserted about it**, by moving the
synthetic family's own mean — never by stubbing the function whose claim is under test, which would
prove the stub. The `999999` carried in the fixture's bytes is the load-bearing trick: it appears in
no arithmetic any of these families can produce, so its absence from every published leaf is evidence
the value was *derived*, which `assert x is None` could never establish — `None` is also what a broken
derivation returns.

**The property is graded by the SAME function as the builder**, via a four-key adapter, and not by a
second copy of the rule. That mattered immediately: the helper's re-derivation leg *refused* on first
run because the adapter had not mapped `estimate_gbp`/`one_draw_moves_gbp`. A control that had quietly
dropped those keys would have left that leg permanently unfirable on this path — green for the reason
this repository has been caught by three times in one afternoon.

## The `or 0` that made this one change rather than two

The page sentence read the count with `or 0`. Removing the key without repairing the sentence would
have published **"0 seeds away at today's spread"** — which says the sign is *free*. That is the one
reading worse than 1,744, and it is why the feed change and the sentence change could not be split.

## What is deliberately not done, and why

**The producer, `tools/run_value_cycle_ab.distance_to_a_sign`, is unchanged.** Two reasons, and the
first is the ordering argument rather than the collision:

1. **Fixing the consumer first is the correct order.** The item warns the page could "end up reading
   a field its own producer no longer writes". It now reads no such field: the page derives from the
   artefact's `mean`, `stdev`, `n` and `sem`, which every floor artefact on disk carries. So the
   producer can change freely without breaking the page — which is the story the artefacts needed,
   and it had to land first either way.
2. `tools/run_value_cycle_ab.py` is held right now by the live claim
   `the-belief-ceiling-names-no-world-and-the-grader-never-stamps-one`. Landing a change to it from
   here would put two claims on one file.

**The producer change is non-trivial and is handed on, not merely deferred.** Removing the count
would break `test_the_seed_count_and_the_verdict_are_the_same_inequality`, which cross-checks two
spellings of one inequality and is a genuinely good control. The design that keeps it: rename the
producer's field so its grammar stops being a plan (`seeds_at_the_point_estimate`), leave the
arithmetic where the control can still reach it, and add the `_seed_price_interval` evidence beside
it. **Every artefact already on disk still carries `seeds_needed_to_state_a_sign` in its bytes**, so
any *other* consumer of that field has the same defect the page just lost — and a census of those
consumers is the first step, not the rename.

## One interconnection noted and left alone

`contrast_bounds.what_this_costs` still reads *"no contrast on this page can have its direction
stated until the noise floor is re-run on the book the figure was measured on"*. That sits directly
beside the newly-priced remedy and is in mild tension with it. It is **not false** — the re-run is
necessary, and the new clause only says it is unlikely to be sufficient — so it is recorded here
rather than edited, because "necessary but not sufficient" is the accurate reading of both sentences
together and rewriting one to pre-empt a misreading of the pair is a change I cannot evidence.
