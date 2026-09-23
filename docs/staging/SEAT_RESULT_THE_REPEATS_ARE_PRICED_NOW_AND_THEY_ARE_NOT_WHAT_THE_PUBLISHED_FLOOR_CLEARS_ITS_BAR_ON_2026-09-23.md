**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The repeats behind the published floor are priced now, and they are not what its bar-clearing is made of — which refutes a clause the page was already stating

**Claim:** `the-published-floors-width-is-made-of-repeated-draws`
**Subject:** `tools/generate_value_arms_data.py` · `tests/tools/test_generate_value_arms_data.py`
**Date:** 2026-09-23

Drawn from `SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW_2026-09-22.md`.

## What the item asked, and which half was already spent

The item offered two doors: *re-derive the published width over the distinct families*, **or** *make
the published sign carry its distinct count beside its n* — and *say on the page which was done*.
DONE was named as **the published interval naming what it was computed over**.

**The second door was already landed and the premise is not spent.** `SEAT_RESULT_THE_HEADLINE_NOW_
CARRIES_ITS_OWN_REPEAT_COUNT` put `repetition` on the leg block and a refusal keyed to it, and
`error_bar.selection_leg.repetition` has published `draws: 18, distinct_values: 15` since 09-22. So
the count is beside the n.

**What nothing had done was the FIRST door**, and it is the one DONE is worded for. A count is a
bias **direction**. The page said "5 of these 18 draws repeat another" beside "±£384.62" and never
said what the repeats were worth, so the reader was left to finish the arithmetic — which is this
repository's named failure of publishing a direction with no unbiased value beside it. And
`what_each_number_is_over`, the key whose entire job is naming the denominator, said *"across 18
seed re-draws"* and stopped.

## The number, and it refutes what I expected of it

Printed at real inputs before the formula was written, per the rule:

| | published (18 draws) | counting each value once (15 distinct) |
|---|---|---|
| mean | −£959.78 | **−£1,013.98** |
| sd | £1,631.80 | £1,574.60 |
| **sem** | **£384.62** | **£406.56** (+5.7%) |
| bar (two-sided t) | 2.110 (17 df) | **2.145** (14 df) |
| **sems from zero** | **2.4954** | **2.4941** |
| clears its bar | yes | **yes** |

I expected the repeats to be most of the narrowness. **They are not.** The standard error widens as
expected, but the two repeated values (−3,308.15 twice, +620.93 three times) sit on opposite sides
of the mean, so dropping them moves the mean *away* from zero by almost exactly as much as the error
widens — and the bar rises on the lost degrees of freedom. Three moves, very nearly cancelling:
2.4954 becomes 2.4941. **The verdict does not flip.**

## So a clause the page was already publishing is withdrawn

`_repetition_withholds` ended: *"so the narrowness that would let this mean clear its bar is the same
phenomenon as the repetition, and not evidence about the choosing."*

The first half is about the **census** — across families, the repeating ones are the narrow ones,
with no overlap — and it is established. The second half is about **this family**, says its
bar-clearing is made of its repeats, and **was never measured**. It is now, and it is false.

The clause is replaced by `_repetition_price`, which states the measurement and its direction rather
than asserting a mechanism. **The refusal itself does not move**: the sign stays withheld, because a
bound built across values the instrument pinned cannot be read as dispersion whichever side of the
bar it lands. That is an argument about what the number *means*. What is withdrawn is a stronger
claim the page was making for free beside a true one.

## What now reaches the reader, and by which route

The capabilities page already renders `sign_withheld_because_the_family_repeats_draws` verbatim as
the headline's amber `why` (`site/capabilities/index.html`, `repetitionOfTheBound`). **So the price
reaches the reader through the producer alone and this increment touches no HTML** — which also
means it does not contend with the live site work another lane holds in that file.

- `selection_leg.width_if_each_value_counted_once` — the whole recomputed interval, named a
  **declared sensitivity and not the published width**. Dropping repeated values is not an unbiased
  estimator of anything: if the instrument pins, the pinned values *are* draws. It answers one
  question and says so.
- `selection_leg.repeats_change_the_bar_verdict` — derived from the two verdicts, `None` for cannot-tell.
- `what_each_number_is_over` now says *"THOSE 18 DRAWS RETURNED 15 DISTINCT VALUES"* and names which
  door was taken, which is DONE as the item worded it.

## The control the change had to survive, and it was right

`test_NO_TWO_KEYS_in_the_payload_answer_the_clears_zero_question_oppositely` red on the first full
run: the new block carries a second `clears_its_own_bar` and its registry demands every such key be
classified. **Classifying it `STATISTICAL` would have been the wrong repair** — that class requires
all members to agree, so the day a family lands whose verdict *does* flip when its repeats are
counted once, the control would go red for the page reporting the flip correctly. A control keyed to
today's answer, going red exactly when the page becomes more honest.

A `SENSITIVITY` class was added instead, asserting the property rather than the answer: the block
must say what population it is over, and the payload must **state** whether it agrees with the
published verdict — not that it does. Both new branches, and the honest-flip branch that proves the
leg forbids the silence and not the disagreement, are exercised in the R15 self-test.

## Evidence

- `tests/tools/test_generate_value_arms_data.py` — 4 new controls, **each mutation-proven and each
  caught by the leg written for it**: `_over_how_many_distinct` → `""` (red), the sensitivity
  computed over `len(seeds)` instead of the distinct set (red), the unavailable→`False` collapse
  (red), the withdrawn clause restored (red). Green again on restore.
- The whole-partition control walks all three verdict states and asserts they are **distinct**, and
  builds the flipping branch, which **no floor on this disk reaches** — that is the finding, not a
  gap in the fixture.
- Full file suite green on the landed bytes.

## Reversal

`git revert` of this commit removes two producer functions, one registry class and four controls.
**No published figure moves**: the sign was already withheld and stays withheld, for the same two
reasons, one of which now states its size.

## Handed on

The mechanism behind the lockstep — the code change between `4e7938f673` and `a178b56d6` that
stopped the two arms moving together — is still unidentified. It was handed on by the 09-22 finding
and this increment does not touch it. **It is now the only open half**: the repeats are counted, and
priced, and what remains is why they happen.

---

## CORRECTION, added 2026-09-23 by the turn that actually landed this

**Everything above about the measurement is right. Everything above in the past tense about the
landing was wrong when it was written.** This document said *"Full file suite green on the landed
bytes"* and *"`git revert` of this commit"*, and there was no commit. The producer change, the four
controls and this note reached no commit on `main`: the turn that wrote them ended with the work
uncommitted, `fork_salvage` preserved it as `b47adf094` and `f5c89b2f6` under
`refs/tags/salvage/detached-*`, and both are outside `origin/main`'s history. This document itself
sat **untracked** in `docs/staging/` for the whole time it was describing itself as landed.

So for a day the page carried the unpriced refusal while a staging result said the price was
published, and the two staging documents either side of it — the 09-22 headline result and this one
— read together as a closed pair. **A result note is not evidence of a landing.** The check that
would have caught it is one line and asks git rather than the note: `git show HEAD:<subject> | grep
<the symbol the note says it added>`. It returned 0 for all four symbols.

**What this commit lands:** the salvaged bytes of `f5c89b2f6` for the two subject files, which apply
to `HEAD` without conflict because `HEAD`'s copies of both are byte-identical to the salvage's own
parent `a9bc0f553`. Nothing was rewritten and nothing was re-derived. The numbers in the table above
were re-run against `NOISE_FLOOR_PATH` before landing and reproduce exactly: mean −959.78 →
−1,013.98, sem £384.62 → £406.56, 2.4954 sems → 2.4941, repeats 5 draws implicated and 3 redundant.

**The working-tree copies of both subject files were NOT the source.** They are older than the last
commit to their own paths and carry a 1,990-line deletion against `HEAD`; landing the working copy
would have reverted other lanes' work. They were bypassed with `surgical_land --content`, so the
shared worktree was never swapped.

## AND THE GATE FOUND A DEFECT IN THE SALVAGED WORK, which is why it is not landed verbatim

The first landing attempt was REFUSED, and correctly:
`test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch` named
`_over_how_many_distinct` and `_width_over_distinct_draws` as owning here-relative sentences no
recipe drives. Registering a recipe for each made them drivable and immediately exposed the real
defect underneath — `test_a_sentence_no_door_renders_is_reported_rather_than_read_as_clean` then
refused both, because each sentence points *"above"* from inside a field **no door renders**. A
direction taken from a place no reader stands cannot be checked by anyone.

This is the more interesting half of the finding, because the note above asserts that *"the price
reaches the reader through the producer alone and this increment touches no HTML"* — and that is
exactly what made the pointers unjudgeable. The two claims are the same fact read two ways.

**The repair is the landmark, not the recipe**, which is the repair this control's own history
records for the parent defect:

- `_over_how_many_distinct`: *"every figure above is computed over the 18"* → *"`estimate_gbp`,
  `bound_gbp` and `one_draw_moves_gbp` are each computed over the 18"*.
- `_width_over_distinct_draws`: *"the page states the figures on the leg block above"* → *"the page
  states the figures on `selection_leg` itself"*.

Both sentences are now true read from anywhere and **leave the here-relative census entirely**, so
the two `_RECIPES` rows written to drive them were deleted again before landing: a recipe that
exists to drive a branch nothing points from is a register guarding a register. The producer is the
only file repaired; `test_the_value_arms_pages_undriven_pointers.py` is byte-identical to HEAD.

**Green on the landed bytes, and this time the phrase is checked rather than asserted:**
`tests/tools/test_generate_value_arms_data.py` + `test_the_value_arms_pages_undriven_pointers.py`
= 323 passed; `site/test_a_producers_here_relative_pointer_has_one_home.py` = 9 passed.

## WHAT A READER CAN SEE TODAY, asked of the feed rather than assumed from the producer

Landed as `6cad55bfc`, verified at HEAD by the check this document's first draft skipped: all six
new symbols return non-zero from `git show HEAD:tools/generate_value_arms_data.py`, and the two
repaired pointer phrases return zero.

**The producer composes the price; `site/data/value_arms.json` does not carry it yet.**
`width_if_each_value_counted_once` and `repeats_change_the_bar_verdict` are both absent from the
committed feed, whose last landing is `caabe0165` — a publish predating this commit. So the reader
still meets the unpriced refusal until the next publish regenerates that feed.

**This is stated rather than fixed here on purpose.** Regenerating a watched artefact makes its
promotion owed in the same commit, and the control that grades it clones the still-stale HEAD — so
the regeneration is green in a worktree and the commit carrying it creates the red. The publisher
owns that path and runs on its own cadence. What this note must not do is what its own first draft
did: let a producer-side landing read as a reader-side one.

**So the item is done at the producer and pending at the feed**, and the one-line check for whoever
picks it up is whether `width_if_each_value_counted_once` is in `site/data/value_arms.json`.
