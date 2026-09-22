**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The published selection figure now states its bias direction and one size, and the size cannot travel without the sentence that nothing was created

**Filed** 2026-09-19 · delivery seat · scheduled tick
**Item** `the-published-selection-figure-states-its-bias-direction`

> A reader of the arms page now meets, on the surface and not in a footnote: the DIRECTION the
> published `selection_gbp` is wrong in, ONE measured magnitude for it, and WHICH BOOK that
> magnitude came from. The magnitude and the sentence that defuses it are **one string in the
> feed**, so no future renderer can publish the flattering half.

---

## 1. What a reader sees

Driven through the real door (`site/_live_harness.mjs` against `site/capabilities/index.html`),
`#arms-redraw` renders, under "… of which, the choosing", a second amber block after the existing
`bind_asymmetry` clause:

> THE FIGURE ABOVE IS BIASED DOWNWARD, and here is one measured size for that bias. This run never
> asked whether the two arms priced the same renewals … The flat arm priced 281 renewals against
> the per-customer arm's 214. … Twelve seeds paired across exactly that one repair price it:
> `selection_gbp` rose by £810.18 (95% CI £778.26 to £842.11, t = 55.86 on 12 paired seeds). **THAT
> SIZE IS NOT A GAIN AND NOT A CORRECTION TO THE FIGURE ABOVE. On every one of those 12 seeds the
> WHOLE advantage moved by £0.00 — not a penny, not a rounding — because the £810.18 came OFF the
> price-level leg and went ONTO the choosing leg by exactly equal and opposite amounts. Nothing was
> created; one side of the decomposition was handed to the other. A reader who takes this as "the
> choosing leg is now positive and significant" has read it backwards.** AND IT IS A DIFFERENT BOOK
> FROM THIS ONE: it was measured on `18327d977` against `a178b56d6`, 20 paths of pricing code away
> from the run above, so it is the size of the CLASS and not this figure's own error. Subtracting
> it here would be arithmetic across two instruments. The figure above stands as published.

The source measurement is
`docs/staging/SEAT_RESULT_THE_PAIRED_TWELVE_PRICE_THE_POPULATION_REPAIR_AT_810_POUNDS_AND_THE_STANDALONE_SIGN_GOT_SEVENTEEN_TIMES_HARDER_2026-09-19.md`.
Nothing here re-derives it; the reading is carried, cited and labelled.

## 2. THE DESIGN DECISION, which is the only part worth arguing about

The item named its own falsifier before any of this was written: *"the £810.18 appearing anywhere
on the page without the sentence that `value_advantage_gbp` did not move by a penny on any of the
twelve seeds."*

A `magnitude_gbp` key with the counter-sentence as a SIBLING key satisfies that today and fails
open on the first renderer that reaches for the number alone — and every renderer reaches for the
number alone eventually, because the number is the part that fits in a table cell. So
`_population_repair_bias` composes `clause` with both halves welded together, the door renders
`clause` and nothing else, and `magnitude_gbp` is published only inside a block whose `clause`
already states the counter. **The welding is the control; the test defends the welding.**

## 3. Keyed to the property, not to today's run

The trigger is the artefact's own `decision_population.same_priced_population` — the same field
`_one_book` reads, from the same place, so the two can never disagree about which run this is.
Three-valued, and `None` (never asked) and `False` (asked, and they differed) BOTH take the bias
branch: absence is not neutrality here, because the field is absent exactly when the run predates
the repair. `True` clears it.

The day the page publishes a run taken after the level arm was given the per-customer arm's
refusal frontier, the block goes unavailable and the clause **comes off the page with nobody
editing it**. It does not key on the commit date, on `CURRENT_WORLD_THREE_ARM_PATH`, or on the
2026-09-18 boundary as a literal — each of which would need a human to retire it.

The published run (`04361d6c7a`, 2026-09-08) carries `same_priced_population: null` and
`priced_by_arm` 281/214, so the bias branch is live today.

## 4. R15 — the mutations were RUN, not asserted

Each applied to the isolated worktree and reverted. Five, each firing on the leg written for it:

| mutation | red |
|---|---|
| feed `clause` keeps the size, drops the counter | `…_without_the_sentence_that_nothing_was_created` — **and nothing else**, which is what makes it the discriminating poison |
| `_population_repair_bias` → `available: False` on every branch | `test_both_sides_of_the_partition_are_reachable` |
| `_population_repair_bias` → `available: True` on every branch | the same control, other leg |
| door drops `caveats[1]` (reverts to the single caveat slot) | 5 of 6 |
| clause rendered muted rather than amber | `…_qualifies_the_figure_rather_than_footnoting_it` |

The partition is **one control over both states**, not a leg per branch: a guard that refuses its
whole partition passes every "does it refuse correctly" rung, which is the trap CLAUDE.md records
being entered three times in one afternoon.

## 5. What was NOT landed, and why

**`site/data/value_arms.json` was regenerated from ISOLATED bytes, not from the shared tree.** At
the time of this landing `tools/generate_value_arms_data.py` carried a rival lane's uncommitted
work — moving `NOISE_FLOOR_PATH` to the twelve at `18327d977`, with a pre-registered decision rule
behind it — and `site/data/value_arms.json` carried that lane's 12:02Z regeneration.

Landing the shared working copy would have swept their generator change's OUTPUT into a commit
without their generator CODE, producing a published feed that no landed generator reproduces —
which the regeneration control landed this morning exists to catch. Landing a feed regenerated
from the shared tree's generator would have swept their code. So:

- `tools/isolate_hunks.py` kept hunks 4 and 5 (mine) and dropped 1–3 (theirs);
- the feed was rebuilt by running the ISOLATED generator in a detached HEAD worktree;
- all four paths landed with `surgical_land --content`, which never opens the shared index.

Their working copy is untouched and their change is still theirs to land. **The one thing this
costs:** when they land, the feed regenerates and carries both changes; until then the published
feed is HEAD's floor (`folded18`) plus this block, which is a consistent pair.

## 6. What is still owed

1. **The one-variable width run is still owed and still unrun** — these twelve seeds at
   `4e7938f673`. This landing does not touch it and does not claim to. The size published here
   holds the seed set fixed and varies the instrument; that run would do the opposite.
2. **`bind_asymmetry` and this block are two different complaints about the same number** and both
   are now on the page. Nobody has asked whether the two biases compose, and this does not assume
   they do — it publishes one size for one named class and says so.
