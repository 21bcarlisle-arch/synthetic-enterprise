**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# SEAT RESULT — the children reference is sourced, and the book's "1.5% cut" was the centre, not the children

A published quantity's CAUSE was mis-attributed and is corrected beside itself; no live figure
was wrong and nothing downstream is blocked.
Claim id `children-within-size-reference-is-owed-a-source`. Pre-registration:
`docs/staging/records/SEAT_PREREG_THE_CHILDREN_WITHIN_SIZE_REFERENCE_2026-09-23.md`, filed before
any observation was fetched.

## What landed

`simulation.demand_model.CHILDREN_WITHIN_SIZE_REFERENCE` is no longer `None`. It carries the
joint `(size, dependent children, share)` distribution for England and Wales, derived from ONS
Census 2021 and controlled against two independent Census products. Full derivation, the one
assumption it makes and what that assumption is worth:
`docs/market_research/children_within_household_size_census_2021.md`.

The aggregate functions no longer refuse a book that declares children — they centre it on that
population. The refusal survives, **re-keyed from "the argument was omitted" to "no reference
exists"**, so withdrawing the source makes every children book refuse again rather than quietly
re-level. That re-keying is the point: wiring the constant would otherwise have turned a live
guard into a branch no book could reach, which reads exactly like a working control.

## The predictions, graded

| | prediction | observed | verdict |
|---|---|---|---|
| **P1** | ≥65% of households have no dependent children | **71.54%** | HELD |
| **P2** | children centre strictly lower, by <4% | **−2.83%** elec, −2.13% gas | HELD |
| **P3** | live book stays **below 0.995** against the new centre | **1.01601** | **REFUTED** |
| **P4** | ambiguous cells under 10% of households | **4.674%** | HELD |
| **P5** | min-vs-max resolution worth <1% on the centre | **0.268%** | HELD |

## P3 is the one worth having been wrong about, and the error was mine, not the model's

I predicted the book would stay below 1.0 because `premise_trace` draws `randint(0, n−1)`
children — far more than the Census carries — so the book is child-heavy and should sit below a
correctly-sourced centre. The direction was right about the draw and **wrong about the book**,
because I attributed the whole of the measured 0.98458 to the children draw when the book's SIZE
MIX was also in it.

The one-variable control settles it. The same 144 homes, read as **all adults**, against the
**all-adult** centre:

| | children book / all-adult centre | children book / ONS centre | all-adult book / all-adult centre |
|---|---|---|---|
| electricity | 0.98458 | **1.01601** | **1.01799** |
| gas | 0.98678 | 1.01150 | 1.01272 |

So this book sits **1.8% above its centre for reasons that have nothing to do with children** —
it is a 144-home sample, not the reference population, and it is free to be biased. Of the
original 1.5% "cut", **1.3 points were the wrong centre and 0.2 points were the children.**

That matters beyond my scorecard, because the prior finding's headline — "a silent 1.3–1.5% cut
to the whole book's volume, caused by declaring children" — names a cause that this measurement
refutes. The cut was real and the mechanism named for it was not: declaring children moves this
book by 0.2%. The correction is written beside the claim in `volume_factor_normaliser` and
`population_mean_volume_factor` rather than replacing it, because the prediction and the result
together are the only evidence the experiment was designed before its answer was known.

**This is the project's own recurring shape, committed by me in a pre-registration:** when a
result moves and more than one thing changed, you cannot attribute it. I wrote the attribution
into P3's reasoning and only the one-variable run caught it.

## A mutation found a hole that reading did not

Six controls were mutated. Two mutations were SILENT: moving mass between children counts *within*
a size band — `(3, 2, s) → (3, 1, s)`, the reference silently disagreeing with its own source.

Every existing control was invariant to it, and each for a good reason: the identity holds because
the centre and the population move together, the all-adult read holds because the children column
is zeroed, and the size marginal is untouched by construction. **A silent mutation is a missing
test or an equivalence, and this one was a missing test.** It is closed by
`test_the_conditional_children_split_agrees_with_two_INDEPENDENT_census_products`, keyed to two
household-based Census products rather than to the person-based table the reference came from —
a figure checked against its own source agrees with itself. All three such mutations now die.

## An existing control was keyed to the day's answer

`test_the_population_half_of_R10_GAP_a_is_declared_absent_not_filled` asserted
`CHILDREN_WITHIN_SIZE_REFERENCE is None`. It would have gone **red the moment the gap was
closed** — the one event it should have welcomed. Rewritten as the property that holds on both
sides: the slot holds a valid population or an honest absence, and never a fill wearing a
population's shape.

## Side finding: a registered red is asserting the wrong property, and it costs nothing

`tests/saas/test_w2_13_property_people_count.py::test_ons_shares_agree_across_the_wall` has stood
red since 2026-09-18 (5 census runs). It asserts dict equality between
`dwelling_records.HOUSEHOLD_SIZE_SHARE_ONS_TS017` (1…8+, split on 2026-09-17 so the world can draw
six- and seven-person homes) and `demand_model.HOUSEHOLD_SIZE_POPULATION_SHARE` (1…5+).

**Measured here: the two give bit-for-bit identical volume centres** — 1.4456452584044155
electricity, 1.2512721741165458 gas — because `need_volume_index` is flat at and above five
adults, so how the 5+ band is split cannot move an all-adult centre at all. The red is demanding
identity of REPRESENTATION where the requirement is identity of the CENTRE, and the refined
constant is the more faithful of the two.

It is NOT fixed here, deliberately: changing that anchor re-levels every household's volume factor
and would have made this commit's own centre move unattributable. It is handed on with the
measurement it was missing. The equivalence is now *used* rather than merely noted — it is what
licenses the children reference to carry the finer 6/7/8 tail (worth 0.272% there) while leaving
the all-adult centre untouched.

## What remains owed

`DEFAULT_CHILDREN_COUNT` still cannot be wired, and **the reason has changed**: not the
population, which now exists, but the DRAW. `premise_trace`'s `randint(0, n−1)` puts a child in
half of all 2-person homes where the Census puts one in 8.7% of them. One sourced draw from this
conditional, answering in `dwelling_records` and `premise_trace` both — the shape
`composition_cuts_for` already has for pensioner/employment.
