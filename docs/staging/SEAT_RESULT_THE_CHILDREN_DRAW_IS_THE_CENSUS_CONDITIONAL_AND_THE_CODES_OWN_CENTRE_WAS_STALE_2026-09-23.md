**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# The children draw is the Census conditional now — and the code's own centre was stale

LATENT rather than RECORDED because one thing here is filed and not fixed: the two centre-resolvers
key on different tests and diverge for a book that declares `children_counts` whose every entry is
0. Unreachable on the live book, reachable in fixtures. The rest is a baseline fidelity change
(R13) decided blind to P&L, plus one correction to a number the code stated about itself.

**Claim id** `children-count-needs-one-sourced-draw-not-a-uniform-randint`.
**Pre-registration** `docs/staging/records/SEAT_PREREG_ONE_SOURCED_CHILDREN_DRAW_2026-09-23.md`,
filed before the live book was built with the new draw.

## The premise, re-measured

Not spent. `30f5578fd` and `6af1f907b` are both at HEAD, so R10 GAP (a)'s population half exists,
and the embargo in `SEAT_FINDING_THE_VOLUME_CENTRE_IS_THE_SECOND_CUT_SET_INSTANCE...` reads *"until
`CHILDREN_WITHIN_SIZE_REFERENCE` has a source"* — lifted by its own terms. The draw itself was
untouched. The duplicate-work note named this same id; `.seat_work_in_hand.json` does not exist on
the shared tree, so there was no rival holder.

## What landed

One function — `dwelling_records.children_count_for(customer_id, people_count)` — drawing from the
Census conditional `P(children | size)` by inverse CDF on its own named substream, read by both
paths. The third and last field of the segmentation set to carry the "one home, two answers" shape,
after `people_count_for_area` and `composition_cuts_for`.

1. `premise_trace.behaviour_profile_for` delegates; the `randint` is deleted.
2. `dwelling_records.build_properties` writes the drawn value; `DEFAULT_CHILDREN_COUNT` is now that
   function's *fallback when the source is withdrawn*, not the field's answer — so retiring the
   constant restores the previous world rather than inventing a third one.
3. `demand_model.build_demand_shape` resolves `children_reference` at the production volume call
   site. **Legs 2 and 3 are one change.** Without 3, wiring 2 would have divided a book that
   declares children by the ALL-ADULT centre — the 1.5% silent cut measured at 0.9846, sitting
   comfortably inside `VOLUME_FACTOR_BIAS_TOL`, where no band could have caught it.

## THE ITEM'S OWN MOTIVE WAS WRONG IN DIRECTION, and the mechanism was right

The item, the knowledge-map row, `dwelling_records`' comment and the finding that unblocked this
all say the uniform draw *"puts a child in half of all 2-person homes against the Census's 8.7%"*.
It puts a child in **none** of them — the draw was guarded `if people_count >= 3`. Measured over
20,000 ids before anything was built:

| size | old draw mean | Census mean | direction |
|---|---|---|---|
| 2 | **0.000** | 0.087 | short — no child was *possible* |
| 3 | 1.000 | 0.702 | long |
| 4 | 1.495 | 1.532 | short |
| 5 | 1.996 | 2.144 | short |
| 6 | 2.497 | 2.224 | long |
| 7 | 2.982 | 2.319 | long |
| 8 | 3.494 | 2.405 | long |

So it disagreed in **both** directions, and it was also the wrong SHAPE: the Census conditional is
strongly bimodal at size 4 (61.4% on exactly two children) where a uniform is flat by construction.
A remedy argued from "half of 2-person homes" would have been argued from a number that is not
there. The remedy is identical either way, which is why this is a correction beside the claim
rather than a reason to stop — but four artefacts carried one wrong instance of a right mechanism,
and none of them had run it.

## Predictions, against results

| | prediction | result | |
|---|---|---|---|
| **P1** | new draw reproduces the Census conditional within 0.01 absolute at every cell | worst cell **0.0048** (size 7, 2 children) | **HELD** |
| **P2** | a 2-person home can carry a child | 1,764/20,000 synthetic (8.82% vs 8.70%); **5 on the live book** | **HELD** |
| **P3** | 30–70 of 144 records declare ≥1 child | **46 of 144 (31.9%)**; mean 0.549/household | **HELD** |
| **P4** | book mean volume factor in [1.011, 1.021] and within 0.02 of 1.0 | **1.01321** electricity, **1.00819** gas | **HELD** |
| **P5** | decided blind to P&L (R13) | book revenue/margin not looked at before landing | **HELD** |
| **P6** | only old-draw-pinned controls red | no existing control red; 121 suites green | **HELD** |

P4's cancellation argument is worth keeping: the same book with the OLD uniform children against
the same sourced centre reads 1.01601, and read as all adults 1.01799. The new draw moved it to
1.01321 — 0.0028, well inside the 0.005 I predicted, because the two draws disagree in both
directions across the size mix and most of it cancels. The book's children count went UP (mean
0.549 against the Census's 0.493, because the book skews to sizes 2–4 where the conditional is
richest) while its volume factor moved DOWN only slightly.

## CORRECTION — the code's own statement about its centre was stale

`volume_factor_normaliser`'s docstring stated the children centre as **1.4009133872553938**
electricity / **1.2206949489351744** gas (−3.09% / −2.44%). The live values are
**1.4047186532865028** / **1.224679820805055** (−2.83% / −2.13%). The docstring was written against
an earlier draft of the reference constant, and the same day's refinement (`6af1f907b`) moved the
constant and not the sentence.

`docs/market_research/children_within_household_size_census_2021.md` and the knowledge map both
carried the right pair throughout. **The code's own statement about itself was the wrong one**,
which is the direction hardest to notice — the knowledge layer is what gets re-derived and
re-checked, and a docstring is read as settled. Corrected in place, beside the wrong value.
Found only by reading the two against each other while wiring a caller of that function.

## FILED, NOT FIXED — one narrow divergence between the two centre-resolvers

`population_mean_volume_factor` keys its reference on `any(children_counts)`; the production call
site now keys on the record **declaring** `children_count`. These differ for exactly one book: one
that declares the field and whose every entry is 0. That book gets the all-adult centre from the
aggregate function and the Census centre from the production path.

The live book cannot be it (46 of 144 declare a child), so this is reachable in fixtures only. It
is filed rather than fixed because `any(...)` also governs that function's **refusal**, which is a
guard with its own separate argument, and guards do not get changed as a side effect of a different
change. **Recommendation:** key both on declaration — `children_counts is not None` — which the
aggregate function already receives and discards. That is a one-line change to a guard and it wants
its own mutation pass, not this one.

## Controls, and the five mutations run against them

Four legs in `tests/simulation/test_one_home_has_one_headcount.py` (agreement, reachability, the
published conditional, no production callers of the old draw, and the record matching the delegate)
and three in `tests/simulation/test_w2_13_occupancy_volume_shape.py` (the call site's centre).

| mutation | reds |
|---|---|
| M1 restore the uniform `randint` in `premise_trace` | 3 legs — agreement, conditional, caller census |
| M2 draw always returns 0 (the flattering collapse) | 3 legs — **reachability first** |
| M3 draw ignores household size | 1 leg — the conditional |
| M4 drop `children_reference` at the call site (the original defect) | all 3 call-site legs |
| M5 key the reference on the VALUE not the declaration | 2 legs |

**M3 was silent on the reachability leg, and that is an equivalence rather than a gap.** Fixing the
size to 4 still leaves each size's reachable SET correct, because `min(k, people_count - 1)` clamps
it — so the partition genuinely is still reachable and that leg's claim still holds. The conditional
leg is the one that owns "conditioned on the right size", and it fired at 0.72 absolute error.

The call-site legs measure by **withdrawing the source** and taking the ratio of two runs, so every
other term (shape multiplier, heating load, the child-weight draw) cancels and what is left is the
divisor. That keys them to the property rather than to today's kWh: re-deriving the Census
population moves the target with them.

One control was wrong on its first run and is worth recording. The caller census matched the bare
substring `'"children")'`, which reds `tools/sample_gate_rss_premium.py` — a file that reads the
cgroup path `<task>/children` and has nothing to do with who lives in a house. Tightened to the
call shape `_substream(..., "children")`. *(The sibling composition census one block above matches
`'"pensioner")'` and `'"employed")'` the same loose way. It is green today by luck of vocabulary,
and it is not this turn's subject — filed here so the next lane touching that file knows.)*

## What is still open

- **The RESPONSE half of R10 GAP (a).** `CHILD_ADULT_EQUIVALENT_RANGE` (0.35–0.85) stays a sampled
  interval; NEED publishes no adults-×-children consumption cross-tab. This turn answers how many
  children a household has, never what one costs.
- **England and Wales only** (no Scotland), and the "8 or more" band's non-reconciliation. Both are
  properties of the reference, inherited rather than added.
- **The "three or more" ceiling.** This draw cannot return 4+ children where the uniform could.
  That is the instrument's, not a bound chosen here — which is why the existing
  `min(children, people_count - 1)` clamp stays as a guard rather than being deleted as unreachable.
