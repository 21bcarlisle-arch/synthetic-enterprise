**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PREREG — what does the republished seed price become when the page derives it instead?

**Filed:** 2026-09-22, BEFORE the arithmetic below was run. Drawn as Lane 0 delivery,
`the-republished-seed-price-carries-an-unbounded-count-in-every-artefacts-own-bytes`. The
predecessor `06e316ae4` fixed this defect in the BUILDER; this item is the surviving instance on
the REPUBLISH path, and the numbers here are a different family from that one's, so none of them
are handed to me.

## The subject

`_sign_on_the_shared_population` (`tools/generate_value_arms_data.py:11085`) copies three fields
straight out of `value_cycle_ab_s1_noise_floor_next12_at_18327d977.json`'s own
`distance_to_a_sign` block and publishes them under
`current_world.selection_leg.population_repair_bias.sign_on_the_shared_population`. Measured on the
live feed and in the artefact's own bytes, before any prediction:

    artefact selection_gbp_spread:  n = 12   mean = -259.29018858333194   stdev = 5413.5806336694695
    artefact selection_sem_gbp:     1562.7661180644066
    artefact selection_distinguishable_from_zero:  False
    artefact distance_to_a_sign:    sems_from_zero 0.16591746236761307
                                    sems_needed_to_state_a_sign 2.0
                                    seeds_needed_to_state_a_sign 1744
    artefact selection_sems_needed_to_state_a_sign:  null

Two things are already established by those bytes and are NOT predictions. The bar in the artefact
is **2.0** — the fixed constant this repo deleted on 2026-09-18 as "short at every family this
instrument has ever drawn, and short by MORE as the family shrinks". And
`sems_needed_is_derived_from_the_family_size` is **absent** from the block entirely: the producing
tree `18327d977` predates that field, so a consumer holding this artefact has no field that can
tell it the bar was pinned. A `.get()` on an absent key returns the same `None` as a derived-bar
denial, which is the "structurally unable to answer agrees with every answer" shape.

## Predictions, written before running

- **P1 — the verdict does not flip.** At the honest derived bar `t(11) = 2.201` instead of the
  pinned 2.0, `selection_distinguishable_from_zero` stays **False**. `sems_from_zero` is 0.166;
  both bars are more than an order of magnitude away. Confidence: near-certain. Stated anyway,
  because a bar move that silently re-graded a live claim is the expensive version of this.
- **P2 — the self-consistent point price is LOWER than the published 1744, not higher.** The naive
  reading is that a stricter bar costs more seeds, i.e. `1744 · (2.201/2.0)² ≈ 2112`. But
  `seeds_to_state_a_sign` scans against the bar the PROJECTED family faces, and `t(m-1) → 1.96` as
  `m` grows past a thousand. I predict the scan returns a value in **1650..1700**, and specifically
  that it is BELOW 1744 — the pinned 2.0 was charging a ~1700-seed family a tail it would not face.
- **P3 — both ends of the denominator's one-error interval price finitely.**
  `mean ± sem` is `-1822.06` and `+1303.48`, neither near zero. I predict the low-end price lands
  in **30..50** and the high-end price in **55..85**.
- **P4 — the interval straddles zero, so the price has no upper bound.** `low < 0 < high` is
  arithmetic on the two numbers above and is not a prediction; what IS predicted is that
  `_seed_price_interval` returns non-`None` here, i.e. `clears_bar is False` reaches it unchanged
  through the republish path.
- **P5 — `share_of_the_interval_the_search_cannot_price` comes back at 6.79%, the SAME figure the
  book-154 family published**, and not because the two families resemble each other. When the
  denominator's interval comfortably contains the unpriceable band, that share reduces to
  `t(ceiling-1) · sqrt(n) / sqrt(ceiling)`, which depends on `n` and the search ceiling ALONE — not
  on the mean, not on the spread. Both families are n = 12. If this holds, the field carries no
  information about the family it sits beside, and that is a finding against a field `06e316ae4`
  landed, filed against my own predecessor work rather than around it.

## The second, independent item

The remedy sentence at `generate_value_arms_data.py:1471` — *"re-running the noise floor on the
point estimate's own run is owed work"* — can now be priced rather than asserted, because
`AUC_FAMILY_FLOOR_PATH`'s widened prohibition permits reading `next12` on its own book 154.

- **P6.** `next12` read on book 154 states **neither a sign nor a price for one** — so the owed
  re-run, if it were performed and came back looking like next12, would buy the page nothing. I
  predict the sentence is not FALSE (the arms span books 154–155, so the point estimate's own run
  is strictly narrower than next12's book) but that the evidence now bears against its optimism,
  and the honest repair is to name what the nearest available floor on that book actually returned
  rather than to delete or keep the sentence as-is.

## What would refute the design, not just the numbers

If P2 comes back ABOVE 1744, the "the pinned bar overcharged" reading is wrong and the republished
figure was conservative rather than inflated — the defect would still be the unboundedness, but the
finding's emphasis would have to move. If P4's `_seed_price_interval` returns `None` on this
family, the builder's mechanism does not reach this path and the repair is a new one rather than a
reuse.
