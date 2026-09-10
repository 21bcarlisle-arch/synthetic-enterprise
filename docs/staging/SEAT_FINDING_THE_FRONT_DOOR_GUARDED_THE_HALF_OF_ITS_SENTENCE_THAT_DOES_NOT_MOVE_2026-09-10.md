**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the selection leg has a mean and not enough draws to state its sign)

# The front door guarded the half of its sentence that does not move

**2026-09-10, Lane 0 delivery.** `site/index.html`'s selection-leg paragraph makes two claims about
the evidence, and until today exactly one of them was checked — the wrong one.

```html
<p class="hypo" data-selection-verdict="withheld">… Re-drawn nine times over nothing but each
household's hidden price sensitivity, the choosing leg lands on both sides of zero …
<a href="./capabilities/#value-arms">The three runs, the split and the nine-draw band</a>
```

| the claim | what checks it |
|---|---|
| the **verdict** is withheld | `generate_dashboard_data._check_front_door_selection_verdict`, recomputed from `value_arms.json → current_world.selection_leg.resolved` on every publish, blocking, in both directions |
| the evidence is **nine** re-draws, twice | **nothing** |

## Why that split is exactly backwards

The paragraph's own comment explains the design, and it is a good one:

> *AND IT IS KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER … If more seeds ever resolve the leg,
> this paragraph goes red for claiming a refusal the evidence no longer supports; it does not
> quietly become a stale disclaimer that flatters us by understating what we know.*

That reasoning is right and it was applied to the **stable** half. The verdict is the thing more
seeds are meant to leave alone until they change it. The **sample size** is the thing that moves
every single time a floor leg lands — and it was hand-typed, in two places, in English words, with
no gate, on the front door, under the strongest claim the company makes.

The same paragraph's comment says, three lines up:

> *(2) A hand-typed figure beside a generated one is the defect this project files against itself
> most often, and /capabilities/#value-arms RETIRED its own prose copy of this band on 2026-09-08
> for exactly that reason — one fact with two homes gets edited on two days for two reasons.*

The band was retired. The **count** of draws in that band was left behind, twice, in the same
paragraph that explains why it should not have been.

## It was hours from biting, and that is how it was found

Two floor legs were running on this guest while this was written:

| pid | started (UTC) | seeds | what it does to the family |
|---|---|---|---|
| 1072649 | 14:50:22 | `11111 … 99999` — the existing nine | reproduces them at a newer tree |
| 1146711 | 15:06:44 | `111111 … 999999` — nine new | takes the family to **eighteen** |

On the publish after those fold, the front door would have told a reader that the money side of the
personalisation claim rests on **nine** re-draws while `/capabilities/#value-arms`, one click away,
showed eighteen — and `_check_front_door_selection_verdict` would have passed the whole way,
because the verdict `withheld` may well still be correct at eighteen. A publish-blocking gate
sitting beside the defect, green, is worse than no gate: it is a reason not to look.

## The remedy, landed with this finding

`_check_front_door_selection_draw_count` — declared in `PUBLISH_VERDICT_CHECKS`, in `generate()`'s
blocking conjunction, controlled in
`tests/tools/test_the_front_doors_selection_verdict_cannot_rot.py`.

It asks **both** forms, because a reader meets only one of them:

1. `data-selection-draws="N"` must equal `current_world.selection_leg.verdict_stability.n`.
2. the **spelled** word for `N` must appear on the page — so a corrected attribute cannot sit above
   rotten prose, which is the failure mode that looks most like a pass.

Keyed to the property, not to today's answer: nothing in it knows that today's number is nine. The
day a fold lands it goes red on its own; the day the sentence is corrected it goes quiet on its own.

Both legs are mutation-proven on the real front door and the real feed — the poison round
(`test_the_draw_count_gate_is_reachable_at_all`) runs before any direction is asserted, and moving
only the feed's family size to eighteen turns the gate red.

## What is NOT claimed here

The count on the door is **correct today**: nine and nine. This is not a published falsehood and
the page is not lying to anyone. It is an unguarded claim on the moving quantity, filed LATENT,
and the finding is the *absence of the control* rather than a wrong number.

## The class

**A control keyed to the stable half of a two-part claim.** Worth sweeping for: wherever a page
states a verdict *and* the evidence base it rests on, the verdict tends to get the gate because it
is the part that reads like the claim — and the sample size, the date, the book size and the window
are what actually move underneath it. `_check_population_consistency` and `data-mix-claim` are the
two neighbours to look at first.
