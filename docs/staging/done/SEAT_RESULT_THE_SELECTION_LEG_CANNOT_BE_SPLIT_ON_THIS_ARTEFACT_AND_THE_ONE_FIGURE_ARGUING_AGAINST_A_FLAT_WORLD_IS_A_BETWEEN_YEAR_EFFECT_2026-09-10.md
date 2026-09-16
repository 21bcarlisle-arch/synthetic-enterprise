**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — separate a flat world from an unfree arm before anything is widened or tuned) · **Class:** measurements_that_mirror

# RESULT — the selection leg cannot be split on this artefact, and the one published figure arguing against a flat world is a between-year effect

Graded against
`docs/staging/records/PREREG_IS_THE_NEGATIVE_SELECTION_LEG_A_FLAT_WORLD_OR_AN_UNFREE_ARM_2026-09-10.md`,
written and landed in this same commit **before the third leg was computed**. The split — 76 freely
chosen against 139 bound-decided — was named there first and is not redefined here.

---

## The answer, in one paragraph

**This artefact cannot separate the two causes, and the question as posed cannot be asked of it at
all.** The −£335.40 has no sign: the nine-seed floor already on disk puts it at **0.19 standard
deviations** of the instrument's own spread, and the floor's own artefact says
`selection_distinguishable_from_zero: false`. The money split the item asked for is not computable
because the artefact publishes no per-account book for the level arm, and would not be computable
even if it did, because the bound partition exists on one arm only. But the third leg found
something that was not being looked for: **the single published number that argued against a flat
world — `discrimination_auc`, live on `site/capabilities/` at 0.627 with a reading that calls it
"real information about who stays" — does not survive stratification by the term's own year.**
Within a year it is 0.444 and sits inside its own null. The arm's belief tracks the era, not the
household. That does not prove cause A, but it removes the only evidence against it, and for the
estimand this artefact exists to measure, the between-year part IS the level and the within-year
part IS the selection — so the two findings are one fact.

---

## Leg 1 — the money split. NOT COMPUTABLE, for three reasons, only the first of which is fixable

The pre-registration recorded before any arithmetic that this leg was already dead on a reading of
the schema. Confirming, with the reasons ranked by how hard they are to remove:

**1. The level arm publishes no per-account book.** `selection_gbp` is
`value_arm_net_gbp − level_arm_net_gbp`: a difference of two whole-run totals. The artefact carries,
for the level arm, the twelve scalars in `level_arm` and the fifteen integers in
`level_arm_decision_shape`, and nothing else. `margin_movers` (165 accounts) and
`bound_attribution.realised_margin_movement` (62 bound-decided accounts, £15,723.24 net on them
against £1,070.45 elsewhere) both compare the value arm against the **control** arm. Neither touches
the level arm. This one is a producer change and it is cheap — see *what run could*, below.

**2. The partition exists on one arm only, and it is not an accident of reporting.**
`ceiling_bound` is a per-decision flag on `value_arm_log`, and `decision_shape` versus
`level_arm_decision_shape` says:

| | value arm | level arm |
|---|---|---|
| priced | 215 | 281 |
| `ceiling_bound` | **138** | **0** |
| `extrapolation_bound` | 5 | 0 |
| median margin £/MWh | 20.00 | 19.52 |

The flat arm sits below the lawful cap everywhere and is bound on nothing. So there is no
bound/free partition on the level side to difference the value side against — the halves have no
counterparts.

**And this is the sharpest structural point in the whole exercise.** It means `selection_gbp` is not
a clean contrast between *a per-customer view* and *a flat view*. It is a contrast between **an arm
the statutory cap binds on 64% of its decisions and an arm it never binds at all.** Whatever
`selection_gbp` measures, "the value of selecting per customer" is not all of it, and the confound
is in the estimand rather than in the sample.

**3. The rosters are different books.** The value arm priced 215 renewals on 100 accounts; the level
arm 281 on 103. `decision_population.what_a_reader_must_not_do` forbids exactly the move Leg 1
requires — *"Do not take a per-decision figure from one arm and compare it with a per-decision figure
from another: the denominators above are different books, not the same book measured twice."* The
accounts that differ are precisely the ones the price difference moved, so equalising them would
delete the effect being measured.

## Leg 2 — the floor. The quantity has no sign

`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json`, same world digest
`39a192ce04c1eda8`, re-ran this three-arm A/B over nine seeds with only the per-household elasticity
assignment re-drawn:

| | |
|---|---|
| `selection_gbp` per seed | +1260.9, −3036.3, +494.4, −2644.3, +286.1, +1090.0, −2482.6, −2719.1, −1952.6 |
| stdev | **£1,810.50** |
| SEM (n=9) | £603.50 |
| range | £4,297.18 |
| `selection_distinguishable_from_zero` | **false** |

The departure run's −£335.40 is **0.19 SD** and **0.56 SEM** from zero. It is inside the floor by a
wide margin, and so is every other three-arm run on disk (+£270.21, +£319.10, +£323.52, +£1,815.79,
+£2,176.66, +£2,574.37 — six positives and one negative, all inside £1,810.50 of zero).

**So the item's question contains a false premise, and it is worth naming plainly rather than
answering around.** "Which of two causes is the −£335.40" presumes the leg has a sign to explain.
It does not. Attributing a cause to it would be attributing a cause to noise, and the departure
run's sign flip relative to its six siblings is the instrument, not the departure term.

**The floor was measured without the departure term** — producing commit `c066c114b` at 09:05 on
2026-09-09, against the departure run's `e1895d6c8` at 20:58. It bounds the instrument, not that
exact configuration, and no reason has been established for the departure term to *shrink* the
variance. `SEAT_RESULT_THE_DEPARTURE_TERM_MOVES_EVERY_YEAR_BUT_THE_CRISIS_ONE_AND_IT_DOUBLES_THE_ARMS_SIZE_GRADIENT_2026-09-09.md`
argues the other way.

## Leg 3 — the belief→price channel. One prediction held, one was refuted, and the refutation was mine

Over the 124 records in `belief_vs_outcome.scored_decisions` (85 retained, 39 left):

| pre-registered | predicted | measured | verdict |
|---|---|---|---|
| **P3a** ρ(`believed_p_retain`, `chosen_margin`) | \|ρ\| < 0.35 | **−0.2035** | **HELD** |
| **P3b** \|AUC(price → retained) − 0.5\| | < 0.1163 | **0.1713** (AUC 0.3287) | **REFUTED** |

**P3b was refuted and the prediction was badly framed — mine, in the prereg, and the error is the
one CLAUDE.md names.** *"Before dividing two numbers, say out loud what each one counts."* I compared
the belief's distance from chance with the price's distance from chance as though they were the same
quantity. They are not. The belief **predicts** churn; the price **causes** it. AUC(price) = 0.3287
is below 0.5 — a higher price associates with leaving — and it is large because the arm's own price
rise manufactured part of the outcome, which the live page's own `auc_reading` already says of four
named accounts. A causal channel being strong is not evidence the inferential channel is. P3b should
never have been written as a comparison and its refutation says nothing about either cause.

P3a stands and is worth one line: ρ = −0.2035 means the arm charges **more** to households it
believes are **more likely to leave**, weakly. That is the same shape as
`SEAT_RESULT_THE_ESTIMANDS_INVERSION_IS_NOT_THE_TIE_MASS_IT_IS_THE_ARM_PRICING_UP_THE_CUSTOMERS_IT_LOST_2026-09-09.md`,
arriving through a different door.

---

## The thing that was not being looked for

*Post-hoc. Not pre-registered, and labelled so. It is reported because it is a defect in a live
published figure, not because it helps the argument.*

`belief_vs_outcome.discrimination_auc` is **0.6163** on the departure run and **0.6270** on
`value_cycle_ab_s1_three_arm_20260909c.json` — the artefact that feeds `site/data/value_arms.json`
and renders on **`site/capabilities/index.html:1792`**. The page tells a reader:

> *"A signal carrying no information at all scores between 0.39 and 0.61 on a population this size
> (exact null, two-sided 95%). The observed value is OUTSIDE it and above the null (two-sided p
> 0.023), **so on this population the belief carried real information about who stays.**"*

Stratify the concordance by the term's own calendar year — count concordant pairs only between
decisions taken in the **same year** — and it collapses, on both artefacts:

| artefact | unstratified AUC | pairs | **within-year AUC** | same-year pairs | within-year null 95% | p | inside null |
|---|---|---|---|---|---|---|---|
| `..._20260909c` (**live page**) | 0.6270 | 3,320 | **0.4440** | 402 | 0.376 – 0.619 | 0.375 | **yes** |
| `..._departure_20260909` | 0.6163 | 3,315 | **0.4257** | 404 | 0.380 – 0.620 | 0.237 | **yes** |

*(Permutation null: `retained` shuffled within each year, 8,000 draws, seed 20260910. Ties count a
half, exactly as the producer's own AUC does.)*

The composition table says why in one look — the belief tracks the era:

| term year | n | realised retention | median `believed_p_retain` |
|---|---:|---:|---:|
| 2016 | 1 | 0.000 | 0.3915 |
| 2017 | 21 | 0.476 | 0.4526 |
| 2018 | 21 | 0.524 | 0.4458 |
| 2019 | 12 | 0.667 | 0.9116 |
| 2020 | 14 | 0.571 | 0.7562 |
| 2021 | 10 | 0.800 | 0.9152 |
| 2023 | 10 | 0.900 | 0.9489 |
| 2024 | 20 | 0.800 | 0.9363 |
| 2025 | 14 | 0.929 | 0.8179 |

Ranking a 2017 decision against a 2024 one is what earns the 0.627. Of the 3,320 pairs behind the
published figure, only **402 (12%)** compare two households *in the same year*; the other 88% compare
two eras.

**Why stratifying is not a stylistic choice here.** A defender could say knowing 2017 churns harder
than 2024 IS information. It is — and it is precisely the **LEVEL**. This artefact's whole estimand
is `level_vs_selection`: the part of the advantage a flat rate could have had, against the part only
a per-customer view could. A signal that moves with the calendar and not within it contributes to the
first and nothing to the second. So for the question the artefact exists to answer, the between-year
component must be stratified out, and the page's word — *"who"* — is a household claim that the
stratified figure does not support.

**What is NOT claimed.** At 402 same-year pairs the null spans 0.376–0.623. The within-year figure is
inside it, so this does **not** establish that the belief is uninformative. It establishes that the
**published figure's evidence is between-year**, and that within a year this sample cannot tell in
either direction. Halving that null needs about four times the same-year pairs.

---

## So which cause does the data support?

**Neither is established, and the honest verdict is asymmetric.**

- **Cause B (an arm that could not speak) is neither supported nor refuted.** The channel evidence
  points its way and clears nothing: ρ(belief, price) is **+0.275** in the pre-cap era where the
  ceiling *structurally cannot fire* (`_CAP_FIRST_DAY` = 1 Jan 2019,
  `company/pricing/ofgem_price_cap.py:216` returns `None` before it), and **+0.060** from 2019 on,
  where it can. Permutation p = 0.078 and 0.598 at n = 43 and n = 81. Directionally exactly what
  cause B predicts; statistically nothing. *(This era split is exogenous — a statutory date and a
  fuel type, not a threshold on the arm's own output. The prereg refused the tempting margin-threshold
  proxy for bound status in advance, and that refusal stands.)*

- **Cause A (a flat world) has had its only counter-evidence withdrawn.** The `discrimination_auc`
  was the one measured number on the artefact that said households differ in a way the arm can see.
  Stratified, it says nothing. Cause A is now **unopposed on this artefact rather than supported by
  it** — which is a different and weaker statement than the `level_vs_selection` prose makes, and
  that prose is still unmeasured.

**What this obliges.** No widening and no tuning on the strength of the −£335.40. The item's own
title had it right: separate them *before* anything is widened or tuned, and they are not separated.
Specifically: the world-fidelity question does **not** go to the director yet, because the evidence
that would justify raising it is a composition artefact.

## What run could settle it

Three things, and each is written as a number rather than as "more":

1. **A per-account book for the level arm.** `_lifetime_by_billing_account(level_result)` — the same
   call `bound_attribution` already makes for control and value — emitted alongside them, so the
   selection leg can be summed over any account subset. Producer change, no world change, no ruling.
2. **A bound flag defined exogenously, so it applies to BOTH arms.** `ceiling_bound` as recorded is
   a property of a value-arm decision and is 0 on the level arm by construction. What is needed is,
   per renewal, whether the lawful cap at that term's own window lies below the arm's *unconstrained*
   optimum — a shadow score `decide_margin` already computes. Applied to both rosters it partitions
   both sides. **Cheapest first step, and it costs one field:** carry `ceiling_bound` onto the
   per-decision records `belief_vs_outcome.scored_decisions` already publishes. That alone makes the
   belief-side question answerable from the artefact with no new instrument.
3. **Seeds enough to clear the floor.** At stdev £1,810.50, resolving a leg of size *X* at two SEMs
   needs *n* > (2 × 1810.50 / *X*)²:

   | leg size to resolve | seeds needed |
   |---|---|
   | £2,574 (largest three-arm selection leg seen) | 2 |
   | £1,810 | 5 |
   | £1,000 | 14 |
   | £500 | 53 |
   | **£335.40 (the figure this item asked about)** | **117** |

   Each run takes hours. **117 seeds is not affordable, and that is the finding:** the whole
   selection leg does not clear its floor, so a *half* of it certainly cannot. A sub-population
   split of `selection_gbp` is not a measurement this instrument can make at any sample it can
   afford, and the route is variance reduction in the design — the roster divergence
   `decision_population.the_mechanism` describes is the variance source — not more seeds.

## What lands next, and what does not

The live-page sentence at `site/capabilities/index.html:1792` and its `auc_reading` in
`tools/generate_value_arms_data.py` now state something the stratified figure does not support. That
is a page correction and a producer change, and it is **deliberately not made in this commit**:
regenerating `site/data/value_arms.json` from a tree carrying 1,100+ modified paths across several
lanes is the shape that reverts other lanes' landings, and the generator reads artefacts off disk.
It is named here so the next turn in this lane has it in hand rather than rediscovering it.

**Correction filed beside the claim, per CLAUDE.md.** P3b in the pre-registration was a wrong
comparison, is left in that file unedited, and is marked refuted here.
