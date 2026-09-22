**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `the-value-arms-pointer-rung-is-red-at-head-and-invisible-to-the-gate-that-should-catch-it`

# The value_arms pointer rung measures again, and the two sentences it could finally drive were both wrong

Closes the finding filed earlier today,
`SEAT_FINDING_THE_VALUE_ARMS_POINTER_RUNG_HAS_BEEN_ERRORING_AT_SETUP_AND_ITS_OWN_REFUSAL_NAMED_THE_FIX_2026-09-19.md`.
Its premise was re-measured before any work and held exactly: four tests ERRORING at setup on a
clean `HEAD`, `build` reading nine artefacts against a fixture supplying six.

---

## What landed

One commit to `tests/tools/test_the_value_arms_pages_undriven_pointers.py` and
`tools/generate_value_arms_data.py`. **Four errors → four passed.**

1. **The fixture arity fix**, verbatim as the parent finding measured it — the three paths
   `generate()` resolves after `DEPARTURE_TERM_RERUN_PATH` added to `_real_inputs()`. On its own
   this reproduced the parent's prediction exactly: *4 errors → 3 passed, 1 failed*, naming the
   same three symbols.
2. **Three bespoke recipes**, one per symbol. None takes `_returns_string`: all three return dicts.
3. **A repair to `_ALSO_ADMIT`**, which was a second red hiding behind the setup error.
4. **Two producer sentences corrected**, both found by driving branches nothing had ever driven.

## The parent finding's one wrong call, corrected here

It said to leave `_population_repair_bias` to its own live Lane 0 item and *"say so in its row
rather than exempting it"*, accepting that the file might then stay red. **That is not a state this
file can be left in, and the parent finding's own reasoning is why.** `tests_for` maps a changed
test file to ITSELF; the gate has no pre-existing-red allowance (`head_red_baseline.json` is a human
acceptance list read by the head-red register, not by `pre_commit_test_gate`). So a red anywhere in
this file makes the arity fix unlandable too, and the choice was never "two recipes or three" — it
was "three recipes or nothing lands".

It has a recipe, and the row says at length what keeps it out of that item's way: it is keyed to
`decision_population.same_priced_population`, the field `_population_repair_bias`'s own docstring
names as its retirement path, and to nothing that item can move — not the £810, not the source, not
the paired twelve.

## The two sentences, and both were wrong

Driving a branch for the first time is what found these. Neither is reachable from any published
byte today, so no feed regeneration is owed and `site/data/value_arms.json` is unchanged — checked
by grep for all four strings, old and new, before and after.

**`_skill_sample_size_explanation` said "the figure above" about a figure in its own region.**
Driven, the `refuted_by_this_run` sentence lands in `.method_skill.the_sample_size_explanation.sentence`
and renders in `#arms-method`; the concordance figure it names renders in `#arms-method` too. A
reader sent upwards leaves the block the figure is in. Corrected to **"beside this"** in the
producer — the same repair, and the same vocabulary, as `_departures`' "named above" in 2026-09-08.

**`_population_repair_bias`'s cleared branch pointed "above" from a field no door renders.** The
door reaches for `.clause` and only when `available`, and says so deliberately: *"Goes quiet on its
own when the page publishes a run that carries the repair."* So the sentence's direction was claimed
from a place no reader stands. Corrected to **name `selection_gbp`** — true from anywhere, which is
the repair `_decomposition_is_the_same_contrast` already made for this shape. Rendering the field
instead was considered and rejected: it would contradict the door's own stated design.

## The red that was hiding behind the red

With the setup error gone, `_against_the_panels_figure` surfaced as **driven but reaching no field
at all** — the recipe had silently stopped taking its branch, and the file's own fail-open leg
(`unwitnessed`) is what named it.

Cause: `is_the_later_run` is read in two places one call apart. `_current_world_clause` gates on the
FIELD, which `_ALSO_ADMIT` patched on the way out of `_current_world_contrast` — but
`_withdraw_a_verdict_stated_from_a_superseded_run` had already consumed the same fact INSIDE it, so
`verdict_withheld_because` stayed set, `_leg_clause` took its withheld branch, and `resolved_tail`
— the only thing that composes the sentence — was discarded.

`_ALSO_ADMIT` now takes a LIST, and `None` means "pass the leg through", which is verbatim what the
withdrawal does on its own first line when the run IS the later one. **Clearing
`verdict_withheld_because` by hand would have been the exemption**: the withdrawal APPENDS to any
reason already there, so a hand-cleared field would erase an unrelated cause and force a state the
producer cannot compose. Today's value happens to begin with the withdrawal text, which is the
evidence it was the sole cause — but keying on that would be keying on today's answer.

## Mutations, each fired on its own leg

Run and restored, every one:

| Mutation | Caught by | Verdict |
|---|---|---|
| Fixture back to six paths | the file's own arity check | names itself at setup |
| Any of the three `_RECIPES` rows removed | `..._has_a_recipe_that_drives_its_branch` | names the exact symbol |
| Family recipe stops stripping `FAMILY_AUC_KEY` | the recipe's own assert | *"reached 'asked_and_unanswerable'"* |
| Skill recipe stops forcing the leg's counts | the recipe's own assert | *"reached 'not_settled_the_other_cut_had_more_power'"* |
| `_ALSO_ADMIT`'s second row removed | `unwitnessed` leg | names `_against_the_panels_figure` |
| Bias sentence back to "the figure above" | *renders-nowhere* leg | names the two legal repairs |
| Skill sentence back to "above" | *unregistered phrase* leg | **see below** |

**The last one is the honest entry.** Reverting the word alone fires the UNREGISTERED-PHRASE leg,
not the misdirection leg — which is this repository's catalogued flattering reading, a mutation
caught by a different leg than the one written for it. So it was run again with
`("_skill_sample_size_explanation", "figure above")` registered claiming `"above"`, and the
misdirection leg itself fired:

```
'figure above' tells a reader at #arms-method that what it names is above,
and #arms-method is same: the pointer misdirects
```

That is the leg that proves "above" was wrong rather than merely unregistered, and it is why
"beside this" is a repair and not an alias.

## What is NOT closed, and is owed

**`.method_skill.the_sample_size_explanation.what_this_is` carries the same misdirection and is
PUBLISHED.** It reads *"the explanation for the figure above being unreadable"*, one field from the
sentence repaired here, in the same region as the figure it names. It is out of this rung's reach
because the rung judges UNTIED literals and this one is tied — and the published-feed sweep that
does see it checks only that a sentence has ONE home, never its direction. **So the direction of a
published here-relative pointer is judged by nothing in this tree.** That is the sharper statement
of the gap and it is a separate landing: repairing it moves a published byte and owes a feed
regeneration, which this commit deliberately does not.

**The invisibility finding stands unrepaired.** `tests_for` still maps
`generate_value_arms_data.py` to `test_generate_value_arms_data.py` only, so this rung is still
selected by no lane that changes only the producer. It is green now, so the next time it rots
nothing will say so until someone edits the test file. The parent finding named this; it is not
fixed here, and it is the reason the file rotted for as long as it did.
