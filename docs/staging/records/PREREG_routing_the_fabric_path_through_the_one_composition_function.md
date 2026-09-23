**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# PRE-REGISTRATION — routing the fabric path through the one composition function

Written 2026-09-23, after `daa7951f0` / `72cf04b51` landed the property-record half, and **before
the fabric-path change was made**. This is increment 2 of the finding
`SEAT_FINDING_THE_DAYTIME_REFERENCE_WAS_ONE_NUMBER_FOR_THREE_INCOMPATIBLE_SCALES_2026-09-23.md`,
and it is the leg that keeps that finding BLOCKING.

## What changes

`premise_trace.behaviour_profile_for` draws `pensioner_present` at an uncited 0.22 and
`someone_employed` as `not pensioner_present or random() < 0.25`. It becomes a delegation to
`dwelling_records.composition_cuts_for`, so the same house gets the same answer whichever path in
the world asks — the arrangement `people_count_for_area` already has for the headcount.

## Already measured, before the change (2,000 premises, the draw's own substreams)

| | fabric path today | delegated (EFUS-implied) |
|---|---|---|
| pensioner-present share | **0.2075** | **0.3235** |
| someone-employed share | **0.8445** | **0.6805** |

**This is the fidelity case and it is not a close call.** Feed each of today's shares back through
EFUS's own published cut rates and neither reproduces EFUS's published all-household headline:

* pensioner: `0.63·0.2075 + 0.34·0.7925 = 0.4002` against a published **0.43**
* employment: `0.35·0.8445 + 0.60·0.1555 = 0.3889` against a published **0.43**

Both land BELOW it, so the fabric book's composition is systematically *less at home in the day*
than GB is. The delegated shares reproduce 0.43 exactly on both cuts by construction, because that
is where they came from. **R13: decided on fidelity, blind to P&L; the direction was not looked at
before deciding.**

## Predictions

**Q1.** The book's mean `daytime_occupancy` **rises**. More households reach the
`pensioner_present and not someone_employed` branch (0.70–0.95 uniform), which today needs the
0.22 draw to hit AND the 0.25 employment draw to miss — measured at 5.2% of premises. Predicted
new frequency ≈ 0.3235 × (1 − 0.6805) ≈ **10.3%**, roughly double.

**Q2.** Mean `away_days_per_year` **falls**, because `pensioner_present` multiplies it by 0.7 and
that branch is taken ~11.6pp more often. Predicted fall: order 3–4%.

**Q3.** Some existing `premise_trace` / `household_physical_layer` tests **red**, because a
premise's drawn profile moves. I predict the reds are *fixture-value* reds, not *property* reds —
i.e. every one of them is a test pinned to a specific drawn household rather than to a relation.
If any red turns out to be a relation, that is the interesting result and this prediction is
refuted.

**Q4.** `demand_model`'s daytime bias controls are **untouched**. The fabric path is the thermal
physics path; it does not call `occupancy_multiplier`. I predict the
`test_w2_13_occupancy_volume_shape.py` suite stays green with no edits.

**Q5.** The independence change is the part with no anchor either way. Today employment is drawn
CONDITIONAL on pensioner presence (`not pensioner or 0.25`); delegated, it is independent. Neither
is published — EFUS §4.1–4.2 is one-way. I predict the conditional version's joint
`P(pensioner ∧ employed)` is far below the independent version's, and that **neither can be
defended from the source**, so the defensible choice is the one that at least reproduces both
published marginals. Recorded as a gap, not settled.

## Results

Same 2,000 premises, same substreams, HEAD extract against the changed tree.

| | HEAD | after | |
|---|---|---|---|
| pensioner share | 0.2075 | **0.3235** | as designed |
| someone-employed share | 0.8445 | **0.6805** | as designed |
| P(pensioner ∧ employed) | 0.0520 | **0.2200** | Q5 |
| P(pensioner ∧ ¬employed) | 0.1555 | **0.1035** | Q1 |
| mean `daytime_occupancy` | 0.3881 | **0.3909** | Q1 |
| mean `away_days_per_year` | 14.968 | **14.359** | Q2 |

**Q1 — REFUTED, and the way it was wrong is worth more than the prediction.** I predicted the
`pensioner ∧ ¬employed` branch would roughly DOUBLE, from 5.2% to ~10.3%. The *delegated* figure is
10.35%, near enough exactly as predicted — but HEAD's figure is **15.55%, not 5.2%, so the branch
FELL by a third rather than doubling.** The 5.2% I anchored on was `P(pensioner ∧ employed)` — the
other cell of a two-by-two I had already measured and printed one turn earlier. I read the wrong
cell of my own table.

The mechanism, which the arithmetic makes obvious in hindsight: HEAD draws employment CONDITIONAL on
pensioner presence (`not pensioner or random() < 0.25`), so a pensioner household is unemployed 75%
of the time — `0.2075 × 0.75 = 0.1556`. Under independence it is unemployed only 32% of the time —
`0.3235 × 0.3195 = 0.1034`. **Raising the pensioner share LOWERS the fully-retired-at-home
population, because the conditional structure it replaces was far stronger than the marginal it
preserves.** Two of the model's parameters moved in opposite directions and I predicted the sum from
one of them.

Mean `daytime_occupancy` consequently barely moved: **+0.7%**, not the material rise predicted. The
branches offset — fewer households in the 0.70–0.95 retired branch, and also fewer in the 0.05–0.35
employed-no-children branch (employed share fell 16.4pp), with both surpluses landing in the
0.25–0.65 middle.

**Q2 — HELD**, at the edge of the stated range: 14.968 → 14.359, a fall of **4.07%** against a
predicted 3–4%.

**Q3 — REFUTED, in the good direction.** I predicted some `premise_trace` /
`household_physical_layer` tests would red as fixture-value reds. **None did: 125 passed, 0 failed**
across `test_premise_trace.py`, `test_household_physical_layer.py`,
`test_w2_13_occupancy_volume_shape.py`, `test_one_home_has_one_headcount.py` and
`test_the_dwelling_record_is_the_worlds.py`. Every existing test in the blast radius was keyed to a
relation rather than to a drawn value — which is the repo's own "key a control to the property, not
to today's answer" rule, honoured by whoever wrote them, and it is the reason a fidelity change of
this size costs no test churn.

**Q4 — HELD.** The shape suite needed no edits.

**Q5 — HELD, and it is the residual gap.** P(pensioner ∧ employed) moves 0.052 → 0.220. Neither is
defensible from the source: EFUS §4.1–4.2 is one-way and publishes no cross-tabulation. The
independent version is chosen because it at least reproduces both published marginals, which the
conditional version does not — but that is a choice between an unanchored joint and an unanchored
joint, and it is recorded as a gap in `demand_model` at the shares, not settled here.

## A control I shipped wrong for ten minutes, caught by mutating it

`test_the_shares_the_two_paths_share_are_the_published_ones` first sampled `composition_cuts_for`
only. Its own docstring claimed *"the pre-delegation fabric draw FAILS this ... that is the mutation
this leg is proof against"* — and it was not: reverting the fabric draw left the leg **green**,
because the function it sampled was not the one being reverted. A control pinned to the reader is
blind to the writer, and the docstring asserting otherwise would have been read as evidence. It now
samples the FABRIC path, and the mutation reds **4 of the 12 legs** instead of 3.

**This is why the mutation is run even when the leg looks obviously right.** I would have shipped
the false claim; running it cost one minute.

