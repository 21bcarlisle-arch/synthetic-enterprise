**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# Pre-registration: the headline block's own repeat count, and what keying the sign to it costs

Written **before** running `_draw_repetition` against the published floor and before regenerating
the feed. Drawn as `the-published-floor-still-states-a-sign-across-five-repeated-draws`.

## The question

`error_bar` is the headline block: `error_bar.selection_leg` is where the page states how many
standard errors the value of the choosing sits from zero, and `error_bar.reading` is the sentence a
reader meets. The replication census two keys down (`error_bar.does_the_sign_replicate`) now carries
a per-family repeat count and the cross-family comparison that says the narrow bounds ARE the
repeating families. **The headline block itself carries neither.**

The floor the headline is stated on is `NOISE_FLOOR_PATH` — the folded eighteen — and it is not one
of the five families in that census, so **its repeat count is published nowhere on the page.**

## What I predict, written down before I look

1. `_draw_repetition(NOISE_FLOOR_PATH_artefact, "selection_gbp")` returns `countable: True`,
   `draws: 18`, `distinct_values: 13`, `draws_that_repeat_another: 5`. (From the 09-22 finding: one
   value twice, one value three times, so 18 draws − 15 distinct… **the finding's own table says 15
   distinct**, which gives 3 repeats, not 5. The finding's prose says "5 of its 18 draws are
   repeats". These cannot both be right under one definition of "repeat", and which is right depends
   on whether a value appearing k times contributes k−1 or k to the count. I predict
   `distinct_values: 15` and `draws_that_repeat_another: 3` from `_draw_repetition`'s own
   arithmetic (`len(values) - distinct`), and that the "5" in the finding and in the drawn item
   counts every draw that shares its value with another — 2 + 3 = 5. **Both numbers are correct
   about different things and the page must state which one it means.**)

2. The live feed's `error_bar.selection_leg` today carries `clears_its_own_bar: true`,
   `sign_is_stateable: false`, `sign: null` — the sign is ALREADY withheld, for the BOOK reason
   (the floor priced 164 settled accounts, the figure 154–155). So **withdrawing the sign changes no
   rendered value today**, and a guard that only withdraws the sign would be unreachable: the book
   guard fires first. I predict this is what makes the naive reading of the drawn item wrong.

3. Therefore what is live and unqualified is not `sign` but the STATISTICAL claim beside it:
   `distinguishable_from_zero: true`, `clears_its_own_bar: true`, and the rendered sentence "sits
   2.5 standard errors from zero against this family's own bar of 2.11". A reader meets that as
   "we could call this if only the books matched". **The repeat count is what that sentence owes
   and does not carry.**

## The decision rule, fixed before the numbers

- If `draws_that_repeat_another > 0` on the published floor: the headline carries the count, and
  `sign_is_stateable` is withheld by a SECOND, independent rule keyed to that count — so that the
  day the owed book re-run lands and the staleness reason goes quiet, the sign does not silently
  return with the repeats still underneath.
- If it is `0`: the sign is not withheld for this reason and the page says the count is zero, which
  is a fact worth publishing either way.
- **`countable: False` withholds.** Absent is not zero and zero is the flattering answer.
- The sign is NOT withdrawn to a hardcoded "we cannot tell". A literal would still say it on the
  day a clean floor lands.
- `NOISE_FLOOR_PATH` is NOT repointed at a wider family. Choosing an instrument by its answer is
  what that block refused once already, and the width evidence does not make it legitimate.

## What would refute the design

Both branches of the new rule must be reachable from artefacts on disk: the published floor (which
repeats) and the 09-17 next12 family (12 draws, 12 distinct, which does not). If only the refusing
branch can be reached, the guard refuses everything and passes every test of a refusal — the shape
this project has entered three times in one afternoon.

## What this does not settle

Whether the wide bound is the right one. Not repeating is not being correct. Nothing here claims
£5,398.31 or £1,558.36 is the true dispersion of the choosing.
