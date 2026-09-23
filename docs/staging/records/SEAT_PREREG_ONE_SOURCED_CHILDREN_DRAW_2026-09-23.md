# PRE-REGISTRATION — one sourced children draw, for every reader

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

A baseline fidelity change (R13) to the world's household composition, decided blind to P&L, plus
a correction to the drawn item's own stated instance.

**Filed** 2026-09-23, BEFORE the live book was built with the new draw and before any volume
centre over it was computed. Claim id `children-count-needs-one-sourced-draw-not-a-uniform-randint`.

## The premise, re-measured at draw time

The item cites `30f5578fd`. HEAD is `6af1f907b`, which contains it. The population half of R10 GAP
(a) is landed: `demand_model.CHILDREN_WITHIN_SIZE_REFERENCE` carries the sourced ONS Census 2021
joint `(size, dependent children, share)`. The embargo in
`SEAT_FINDING_THE_VOLUME_CENTRE_IS_THE_SECOND_CUT_SET_INSTANCE...` reads *"no lane may wire
`DEFAULT_CHILDREN_COUNT` to `premise_trace`'s children draw **until
`CHILDREN_WITHIN_SIZE_REFERENCE` has a source**"* — that condition is now met, so the embargo is
lifted by its own terms rather than set aside. **The premise is NOT spent: the draw is untouched.**

The duplicate-work note names this same id; `.seat_work_in_hand.json` does not exist on the shared
tree, so there is no rival holder. Not a duplicate.

## CORRECTION TO THE ITEM'S OWN MOTIVE — measured before building anything

The item (and the knowledge-map row, and `dwelling_records`' own comment) says `premise_trace`
*"puts a child in HALF of all 2-person homes where the census puts one in 8.7%"*. **That is wrong
in direction.** The draw is guarded:

```python
children_count = (
    _substream(base, "children").randint(0, max(0, people_count - 1))
    if people_count >= 3 else 0
)
```

so a 2-person home gets **0 children, always**. Measured over 20,000 synthetic ids:

| size | current draw, mean children | census conditional, mean | current P(0 children) | census P(0) |
|---|---|---|---|---|
| 2 | **0.0000** | 0.0870 | 1.0000 | 0.9130 |
| 3 | 0.9997 | 0.7020 | 0.3356 | 0.4310 |
| 4 | 1.4952 | 1.5319 | 0.2515 | 0.1939 |
| 5 | 1.9962 | 2.1439 | 0.2027 | 0.1363 |
| 6 | 2.4965 | 2.2235 | 0.1675 | 0.1215 |
| 7 | 2.9822 | 2.3193 | 0.1444 | 0.1059 |
| 8 | 3.4937 | 2.4050 | 0.1234 | 0.1100 |

**The mechanism the item names is right and its instance is not**, and the disagreement is not
one-directional: the uniform draw is short of the census at sizes 2, 4 and 5 and long at 3, 6, 7
and 8. It is also the wrong SHAPE — the census conditional is strongly bimodal at size 4 (61.4% on
exactly two children) where the uniform is flat by construction. A remedy argued from "half of
2-person homes" would have been argued from a number that is not there; the remedy is the same
either way, which is why this is a correction filed beside the claim rather than a reason to stop.

## What is being built

One function, `dwelling_records.children_count_for(customer_id, people_count)`, drawing from
`CHILDREN_WITHIN_SIZE_REFERENCE`'s conditional `P(children | size)`, keyed on the customer id —
the same shape `composition_cuts_for` already has for pensioner/employment. Then:

1. `premise_trace.behaviour_profile_for` delegates to it; the `randint` is deleted.
2. `dwelling_records.build_properties` sets `children_count` from it; `DEFAULT_CHILDREN_COUNT`
   becomes that function's stated fallback rather than the field's answer.
3. **`demand_model.build_demand_shape` passes `children_reference` at the production volume call
   site.** Without this leg, wiring (2) is a silent re-levelling: `occupancy_volume_factor` with a
   declared `children_count` and no reference divides by the ALL-ADULT centre, which is exactly
   the 1.3-point wrong-centre cut the same-day correction identified. Legs 2 and 3 are one change
   and cannot land apart.

## Predictions, each falsifiable, none of them looked at

**P1 (the draw reproduces its source).** Over 20,000 synthetic ids at each fixed size, the new
draw's conditional `P(children | size)` matches `CHILDREN_WITHIN_SIZE_REFERENCE`'s conditional to
within 0.01 absolute at every `(size, children)` cell. If it does not, the inverse-CDF is wrong,
not the source.

**P2 (the partition is reachable).** On the live book a 2-person household CAN now carry a child
— i.e. at least one record with `people_count == 2` and `children_count == 1` exists, or, if 144
draws are too few for an 8.7% cell at the book's 2-person count, the control asserts it over
synthetic ids instead. **I assert reachability before I assert what the branch does**, because a
draw that returns 0 everywhere passes every per-size mean test I could write.

**P3 (the book declares children).** The live book's `children_count` is currently `{0: 144}`.
After the change I predict **between 30 and 70 of 144** records declare at least one child. (The
census marginal is 28.5% of households with children, and the book skews to small homes, but it
also draws its sizes from the census, so I expect the book near the marginal rather than far
below it.)

**P4 (the volume centre stays neutral, and MOVES LITTLE).** With the new children and the sourced
centre, the live book's `population_mean_volume_factor` (electricity) lands **within
`VOLUME_FACTOR_BIAS_TOL` (0.02) of 1.0** — and, more sharply, **in [1.011, 1.021]**, i.e. within
0.005 of the 1.01601 the same book reads with `premise_trace`'s uniform children against the same
sourced centre. Rationale: the two draws disagree in both directions across the size mix (table
above), so I expect substantial cancellation rather than a one-way move. A reading outside
[1.011, 1.021] refutes the cancellation argument, not the change.

**P5 (direction is not the reason).** This is a baseline fidelity change decided blind to P&L
(R13). I have not looked at the book's revenue or margin under it and will not before landing.
The argument is fidelity alone: the world's record was drawing a household composition from an
uncited uniform where the Census publishes the conditional.

**P6 (what reds).** I predict the only existing controls that go red are ones pinned to the OLD
draw's specific output (a literal children count for a named premise, or a "children are absent
from every record" census). Controls keyed to the PROPERTY — one home one answer, mean-1
normalisation, the refusal on an unanchored reference — stay green, because the property is what
they were keyed to. If a property-keyed control reds, the change is wrong and not the control.

## What is NOT in scope, and why

- **The RESPONSE half of R10 GAP (a).** `CHILD_ADULT_EQUIVALENT_RANGE` (0.35–0.85) stays a
  sampled interval. NEED publishes no adults-×-children consumption cross-tab. This turn answers
  how many children a household has, not what one costs.
- **Scotland**, and the "8 or more" band's non-reconciliation. Both are carried by the reference
  and stated there; this draw inherits them rather than adding to them.
- **The "three or more" ceiling.** The census publishes its top band as three, so this draw can
  never return 4+ children where the uniform could. That is a property of the source, and it is
  the reason the existing `min(children, people_count - 1)` clamp stays as a guard rather than
  being deleted as unreachable.
