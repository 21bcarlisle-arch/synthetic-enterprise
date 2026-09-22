**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: publishing the selection leg's sign as a replication question across four same-world families

**Claim:** `the-selection-legs-sign-is-a-property-of-which-floor-was-drawn-and-four-same-world-families-disagree`
**Subject:** `tools/generate_value_arms_data.py` · `site/capabilities/index.html` · **Date:** 2026-09-22

Written BEFORE the block, the controls or the mutations exist. What is already known is recorded as
known, so that nothing below can be read as a prediction that was really a result.

## What is ALREADY established and is therefore not predicted here

The four readings are computed in
`docs/staging/SEAT_FINDING_SEVEN_CONTROLS_PAIRED_EVERY_FLOOR_WITH_THE_LIVE_RUN_INSTEAD_OF_THE_RUN_IT_WAS_MEASURED_ON_2026-09-22.md`
and I have re-run them through the production grader `_legs_on_one_bar` before writing this file.
They are inputs, not findings:

| pair | selection leg | level leg | value leg |
|---|---|---|---|
| `noise_floor.json` × `three_arm_20260910` | 2.852σ, **negative** | 49.451σ, positive | 22.707σ, positive |
| `noise_floor_20260910b` × `three_arm_20260910` | 0.548σ, no sign | 39.100σ, positive | 34.388σ, positive |
| `next12_20260917` × live `three_arm` | 0.686σ, no sign | 5.244σ, positive | 7.420σ, positive |
| `next12_at_18327d977` × live `three_arm` | 0.166σ, no sign | 4.727σ, positive | 7.420σ, positive |

## The defect being repaired, stated as what the page does TODAY

`error_bar.legs_on_one_bar` is **refused** on the live publish (`folded18_single_arm_20260917` ×
live `three_arm`: floor older than the figure, and a different book — 164 against 154). The page
therefore renders one amber sentence and says nothing at all about any leg.

That refusal is correct and is not what is being changed. What is wrong is what surrounds it: four
same-world families on this disk *can* grade this contrast, they **agree** on the level and value
legs, and they **disagree** on the selection leg — and none of that reaches the reader. A page that
answers "we cannot tell" by pointing at one refused pair, while holding four graded families that
replicate two legs out of three, is publishing less than it knows in the direction that happens to
be safe.

## Predictions

**P1 — the verdict is derived, so a mutation that makes the families agree flips it.** Substituting
a pair set in which every admitted family states the same sign for the selection leg makes the block
publish `replicates: true` for that leg with no string edited. If any sentence has to be rewritten
to say so, the block is a constant wearing a computation's clothes and the design is wrong.

**P2 — the level leg is the control arm and it must pass the same test.** The block grades all three
legs, not the selection leg alone. If it graded only the contested one, "contested" would be
unfalsifiable — there would be no leg on the page demonstrating what replication looks like when it
happens.

**P3 — mutation count.** I predict **at least 3** distinct mutations of the new producer code each
red at least one control, and that **at least one control reds by name on the replication verdict
itself** rather than on an arithmetic leg. If a mutation of the verdict is silent, that is a missing
test and it will be recorded as one, not as an equivalence.

**P4 — the site lane.** I predict the existing door
`site/test_the_baseline_comparison_reaches_the_reader.py` goes **green unchanged**, because the new
field is additive and the refusing branch it asserts over is untouched. If it reds, the new render
has changed the refusal's own rendering, which is not what this work is for.

**P5 — what I cannot predict.** Whether `build()` gains material runtime from four extra
`_legs_on_one_bar` calls over committed artefacts. Measured after, not guessed at here.

## What done means

Not "the page mentions four floors". Done is:

1. The page states, on the **refusing** branch as well as the admitted one, that the selection
   leg's sign is a property of which floor was drawn — with the four families' own readings beside
   it, each named with the run it was measured on.
2. The replication verdict is **computed from the per-family signs**, so a future family that makes
   them agree changes the sentence with nobody editing it.
3. The level leg's replication is published in the same block, because the contrast between a leg
   that replicates and a leg that does not is the claim — one without the other is half of it.
4. Every control is keyed to the property (does the grader discriminate replication from
   contest?), never to today's four numbers.
