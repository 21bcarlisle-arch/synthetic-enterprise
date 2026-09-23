**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the unorderable-runs sentence has a render site, and the leg I wrote to prove it was unreachable

*Lane 0 delivery, 2026-09-23. Drawn item: `give-the-repeated-figure-refusal-the-door-the-ordering-now-answers-it-with`.
Second increment of the turn; the first is `6c47bca78` and is recorded in
`SEAT_RESULT_THE_RUN_ORDERING_HAD_THREE_SHAPES_IN_ONE_FLATTERING_STATE_AND_EQUAL_FIGURES_WERE_CLAIMING_ONE_RUN_2026-09-23.md`.*

## What this increment is

`how_the_two_runs_order` reached the payload in `6c47bca78` and no render site read it. It now
renders, through `_the_two_runs_order_clause`, into the current-world clause in the headline —
**immediately after the figure it qualifies and inside that figure's own region**, so the caveat
cannot be read under the selection leg's lead.

The gap it closes is narrower and worse than "a field had no door". `run_ordering` already reached a
reader through `_against_the_panels_figure` — but **only on the branch where the two advantages are
arithmetically EQUAL**. On every other branch the page printed one figure as a `SMALLER` or `LARGER`
advantage than the other while its own payload said the two runs could not be ordered at all. The
figure was right and the direction was right; the missing half was the one that says a direction is
all the stamps license. A reader met a revision where the page held two readings.

## What renders, at real inputs, on each of the four states

Printed through the real producer before the control was written, per the house rule:

| `run_ordering` | render site |
|---|---|
| `later` | **silent** — the headline already opens "IN THE WORLD AS IT IS NOW" and calls the panel below the older one |
| `earlier` | **silent** — `_current_world_clause` composes nothing at all; the currency claim is withdrawn upstream |
| `same_stamp` | "THE TWO RUNS THIS PAGE CARRIES BOTH STATE THE SAME STAMP, `<stamp>`, so neither is the later of the two…" |
| `unstated` | "WHICH OF THESE TWO RUNS IS THE LATER ONE IS NOT ESTABLISHED. This block was measured at `<stamp>` and the run it is published against states no stamp this page could read…" |

Only the two unorderable states speak. Rendering on all four would put a recital on the page for two
states that already answer the question and one that is silent.

**It is inert on the live publish, by design.** The live feed is `run_ordering: earlier`, so
`_current_world_clause` returns `""` and this changes no published byte today. It starts speaking the
moment `CURRENT_WORLD_THREE_ARM_PATH` moves onto a run that ties — which is the publish it was built
for. No feed regeneration was needed and none was done, so no contested artefact was written.

## The leg I wrote to prove it, and why it could not fail

The first draft asserted that the two unorderable states render **different** sentences. It passed.
Mutating the render site to print one sentence for both states also made it fail — **but on the
presence leg, not on the distinctness leg.** That is this project's named flattering reading, and it
was a defect in my control rather than a lucky catch:

> The presence leg already pins each state's page to **that state's own producer sentence**. Two
> distinct sentences rendered per state therefore *follows* from presence. Distinctness at the render
> site was an equivalence, not a missing test — it could not be reached by any mutation.

Established rather than assumed, which is what the rule asks. The distinctness that CAN fail is a
property of `_how_the_two_runs_order`, and it is controlled where it can fail — the
`dict_values(['later','earlier','same_stamp','same_stamp'])` leg in
`test_the_two_runs_ordering_has_a_state_for_every_shape_two_stamps_can_take`.

So the leg was **re-keyed to what presence cannot catch**: a render site that prints **both** reasons
on every unorderable state. Presence passes on each one, and the reader is handed two contradictory
explanations of the same pair with no way to tell which is true. The assertion is now that the other
state's sentence is ABSENT.

## Mutations — each leg fires on its own defect

| mutation | leg that fired |
|---|---|
| render site returns `""` always | *"the feed states `same_stamp` … and a reader met no sentence saying so"* |
| both reasons rendered at once, built from the block's own stamp | *"the page is in the `same_stamp` state and also carries the sentence for `unstated`"* |
| rendered unconditionally on all four states | *"the ordering sentence rendered on `later`, where the two runs ARE ordered"* |

**One mutation was mis-built before it was believed.** The first "both reasons" attempt injected the
other sentence formatted with `None` stamps, so it was not byte-identical to what the control
computes and the leg passed. That is a **badly built mutation, not an unreachable leg** — the
distinction the rule turns on, and the reason it was rebuilt from the block's own `generated_at`
rather than recorded as an equivalence. Had I stopped at the first green, I would have filed the
flattering reading twice in one turn.

## A fail-closed branch nothing on disk can reach yet

An ordering that says the stamps do not order, carrying no sentence, is a producer defect. The render
site says so on the surface rather than falling silent, because a reader cannot tell silence from a
page with nothing to say. **That branch is unreachable from any state `_how_the_two_runs_order`
produces** — the two are composed together — so it is a guard against a future edit that separates
them, and it is recorded here as such rather than claimed as controlled.

## What is still owed

The publish itself. Moving `CURRENT_WORLD_THREE_ARM_PATH` onto the corrected 09-18 run, and the three
doors `b36b9cc3d` measured for that route, are untouched by this increment. What has changed is that
the refusal named as the blocker —
`test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved` — now has both
halves it needed: a producer that can say which unorderable state the pair is in, and a page that
tells the reader.

One item of shared-tree hygiene is deliberately left, with its evidence, for whoever draws it:
`tests/tools/test_generate_value_arms_data.py`'s working copy predates its own last landing by
seventeen hours and is 1,771 lines short of it, and the index holds a third revision. It reads as a
rival lane and is not one. See the postscript of the sibling record for the measurement.
