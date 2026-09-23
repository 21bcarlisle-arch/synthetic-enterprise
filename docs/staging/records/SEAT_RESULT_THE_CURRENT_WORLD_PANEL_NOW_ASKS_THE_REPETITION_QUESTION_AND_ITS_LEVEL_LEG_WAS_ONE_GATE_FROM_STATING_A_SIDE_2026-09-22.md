**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The current_world panel now asks the repetition question, and its level leg was one gate away from stating a side without it

Nothing was published wrong. A rule that exists in one of the page's two homes for the sign verdict
reached the other nowhere, and the unreached home was one unrelated gate away from stating a
direction off a bound partly made of draws that pinned.

*Lane 0 delivery, claim
`the-current-world-panel-is-a-second-home-for-the-sign-verdict-and-the-repetition-rule-does-not-reach-it`.
Pre-registration: `docs/staging/records/PREREG_WHAT_THE_REPETITION_RULE_DOES_TO_THE_CURRENT_WORLD_PANELS_THREE_LEGS_2026-09-22.md`,
written before any of the measurements below.*

---

## The premise, re-measured

`39330677b` is an ancestor of `origin/main`, and it is **not spent for this item**: its own commit
message hands this gap on in terms — *"`_leg_in_this_world` is a second home for the same verdict
and does not reach this rule -- handed on."* The duplicate-work check named this claim's own id,
which is this draw, not a rival.

## What was wrong

`site/capabilities/index.html` decides "may this page state a direction" in two places:

| home | leg builder | repetition rule as of 39330677b |
|---|---|---|
| headline block (`#arms-errorbar`) | `_leg_over_its_own_family` | **asked** |
| current_world panel (`#arms-legs-first`) | `_leg_in_this_world` | **not asked** |

One legal requirement, two implementations — the VAT shape this repository's CLAUDE.md prices at
"fixed in one of five copies in July, still live in another in August, and nothing anywhere able to
notice."

## The finding the item did not predict, and it is the reason this was worth doing today

The drawn item's motive said the current_world selection leg is *unavailable* today, so nothing is
published wrong and the fix is cheap. Half right, and the correction matters:

- The panel is **available**. All three legs carry `bound_available: true`.
- The leg at risk is not the selection leg but the **level leg**, and it is not hypothetical.
  `CURRENT_WORLD_NOISE_FLOOR_PATH` has 9 seeds; on `level_advantage_gbp` they return **7 distinct
  values, so 4 of the 9 draws repeat another**. Measured, one variable, against the real artefacts:
  with the new rule removed that leg's verdict is `resolved: True` with
  `verdict_withheld_because: None` — it clears its bound, survives a re-draw, and its family
  determines a sign.
- The only thing keeping it off the page today is the **panel-level superseded-run withdrawal**,
  applied one gate further out for a completely unrelated reason (this block was measured
  2026-09-08, the run beside it published 2026-09-18).

So the state was not "a dormant rule on an unavailable panel". It was a stated direction suppressed
by a neighbouring gate that goes quiet the moment a later current-world run lands.

## Both branches come free from one artefact

The same floor, the same run, one leg apart:

| contrast | draws | distinct | `draws_that_repeat_another` |
|---|---|---|---|
| `value_advantage_gbp` | 9 | 9 | 0 |
| `selection_gbp` | 9 | 9 | 0 |
| `level_advantage_gbp` | 9 | 7 | **4** |

A rule whose passing branch no artefact can reach passes every test of a refusal. This one has both
branches on disk, in one file, under one run.

## What landed

- `_leg_in_this_world` asks the question through the **same producer and the same sentence** as the
  headline — `_draw_repetition` counts, `_repetition_withholds` words the refusal. A repetition rule
  written afresh here would have been the defect it was installed to prevent, and a control asserts
  the panel's text *is* `_repetition_withholds`'s rather than a copy.
- The count is asked **only when a floor was admitted**. `floor_current` reaches the function before
  `_current_world_bound` has ruled on it, and that function refuses floors from the wrong world or
  the wrong leg; counting a refused family would qualify a bound that does not exist with evidence
  from a family that did not produce it.
- The reason is **appended, never substituted** — the three refusals are independent and any subset
  can hold.
- `repetition` is published on **every** leg, zero included, and renders on every branch of
  `legVerdict` through the `repetitionOfTheBound` renderer that already existed. A qualification
  that appears only when it disqualifies teaches a reader that its absence means the question was
  not asked.

## The predictions, against the result

All four held. Feed diff: no leg's published `resolved` changed (all three were already withheld at
panel level); `level_leg.verdict_withheld_because` gained the sentence naming 4 of 9; the value and
selection legs gained no sentence; all three gained a `repetition` key.

The one thing the pre-registration understated, recorded here beside it rather than quietly fixed:
prediction 1 was about the *published* feed and is true of it, but at the **leg** level the level
leg's `resolved` did move from `True` to `None`. That is the rule being load-bearing, and it is a
stronger result than predicted, not a weaker one.

## The rule deleted a reason from the page, and the door caught it

**This is the most useful thing in this write-up.** With the rule in and the feed regenerated, two
site controls went red. Neither was a fixture problem.

`_withdraw_a_verdict_stated_from_a_superseded_run` returned early on `resolved is None`, reasoning
— in its own docstring — that *"a leg that already states no verdict has none to withdraw"*. That
held only while the single route to `resolved: None` was a gate that wrote its own reason first. My
rule added a second route: it set `resolved = None` on the level leg one step earlier, the early
return then swallowed the ordering sentence, and **the page lost a reason it had published the day
before**. The docstring's justification was an argument against *substitution*, and the line it
guards has always *appended* — so the early return bought nothing, and its `existing + " "` branch
had been unreachable dead code since it was written.

The two reasons are independent: a clean floor at this book does not make this run the later of the
two, and a later run does not un-repeat these draws. So the early return is deleted and the reason
is always appended. `test_a_leg_that_ALREADY_withholds_still_learns_it_is_on_a_superseded_run`
drives it.

**It improved a leg I was not repairing.** The selection leg has withheld for one-draw instability
for days and never told the reader it also sits on a superseded run. It does now.

The second red, `test_the_resolved_leg_is_not_given_the_withheld_legs_sentence`, is the sibling
fixture the defect was propping up. Its docstring already records being re-keyed once in September
for being pinned to today's answer — and it still was, one level down: it read `level_leg`
specifically and failed unless *that* leg resolved. The repetition rule made the level leg honest
and the control went red for it. Re-keyed to whichever leg the producer's rules permit to resolve,
synthesising one only from a leg the repetition rule clears, so the renderer is driven with a state
the producer could actually compose.

## A mutation survived, and that is how the last control was found

The sweep ran four mutations. Three died. **Substituting `verdict_withheld_because` instead of
appending to it survived**, because no leg of the real floor has both a prior withheld reason and a
repeat count — the level leg repeats 4 and is stable, the selection leg is unstable and repeats
none. Substitute and append coincide on today's inputs.

That is an equivalence of the **inputs**, not of the rule, so it is a missing test and not a free
pass — and the untested state is the one where a reader is told the sign returns once the re-draws
settle while the repeated draws are still underneath it.
`test_the_current_world_leg_publishes_BOTH_refusals_when_both_of_them_fire` builds the witness (the
real floor with one collision introduced and its published spread block recomputed, because
`_current_world_bound` cross-checks the two).

**Final sweep: seven mutations, seven killed, each by the leg written for it** — verified by test
name rather than by failure count, because a mutation caught by a different leg is the flattering
reading. Tree confirmed byte-identical afterwards.

| # | mutation | killed by |
|---|---|---|
| 1 | drop the `resolved = None` latch | `..._withholds_its_direction_for_repeated_draws` |
| 2 | count a refused floor anyway | `..._a_refused_floor_does_not_get_a_repeat_count...` |
| 3 | substitute the reason instead of appending | `..._publishes_BOTH_refusals_when_both_of_them_fire` |
| 4 | publish the count only when it withholds | `..._on_the_CLEAN_legs_too` (+2) |
| 5 | restore the withdrawal early return | `..._ALREADY_withholds_still_learns...` |
| 6 | prepend the ordering reason | `..._ALREADY_withholds_still_learns...` |
| 7 | one sentence for both verdict branches (door) | `test_the_resolved_leg_is_not_given...` |

Door side additionally: dropping `legRepetition` from the withheld branch, and rendering the count
only when non-zero, both go red.

## What is NOT closed

The level leg's 4-of-9 repeat count is now *published*, not *explained*. `_width_against_repetition`
— the census establishing that repeating families are bounded more tightly with no overlap — is
computed over the headline block's family roster and does not include the current-world floor, so
the level leg's refusal borrows a cross-family finding measured elsewhere. That is honest as far as
it goes (the sentence is the shared producer's, and it says what it rests on) but the current-world
floor is not one of the families the comparison was made across. Handed on.
