**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION (round 2) — what forcing the year marginal costs the demand axes, and what removing three duplicate axes does

**Filed 2026-09-11, delivery seat, AFTER round 1 was graded and BEFORE either repair is measured.**
Round 1 is
`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`;
its grading is §1 below and is a RESULT, not a prediction. §3 is the prediction.

---

## 1. Round 1, graded. 3 of 5 hold, and the two failures are different kinds

Seed 42, `origin/main` @ `b30661c1d`, both arms from one campaign run, one variable.

```
ARM A  systematic cull   rate 0.1796  settled 90  cy 1195.4  distinct fabric 47
ARM B  chosen+weighted   k 78         settled 89  cy 1198.5  distinct fabric 56  zero-weight 2
```

| | ARM A cull | ARM B chosen | ratio |
|---|---|---|---|
| `fabric_w_per_k` | 0.04967 | 0.02698 | 1.84× |
| `raw_infiltration_ach` | 0.07751 | 0.03298 | 2.35× |
| `volume_m3` | 0.06671 | 0.01531 | 4.36× |
| `solar_aperture_m2` | 0.06671 | 0.01531 | 4.36× |
| `internal_gain_kw` | 0.06671 | 0.01531 | 4.36× |
| `customer_years` | 0.01080 | 0.04959 | **0.22×** |
| **JOINT** | 0.11421 | 0.07466 | 1.53× |

**P1 HOLDS — 1.530×**, against a band of ≥1.25× and a kill line at 1.10×. The chooser earns its
keep at this size on this base's coarser homes. *It does not reproduce the item's 1.64×, and I said
in advance it would not be expected to.*

**P4 HOLDS.** 89 settled (band 80–100), 1198.5 of 1200.0 customer-years, ceiling never crossed.

**P5 HOLDS, by two orders of magnitude.** Non-zero weights run 0.061 to 12.650 — a spread of
**206×** against a band of ≥3.0. The uniform arm gives every account 5.57. The inflation is now a
vector and it is arguable per account, which was the point.

**P2 FAILS, and the prediction was uninformed rather than wrong-headed.** Distinct fabric vectors
among the settled book went 47 → 56, against a predicted ≥70. I had not measured the ceiling:
**the 502 candidates contain only 109 distinct fabric vectors between them.** So arm B holds 51% of
every distinct home in the population in 89 accounts, against arm A's 43%, and ≥70 of 89 was never
available. The right way to have asked it was as a share of the ceiling, and I asked it as a count.

**P3 FAILS, and this one is a real defect in the design.** Predicted every year within ±25%;
measured **+84.9% on 2017** (10 accounts carrying 64.7 wins of weight against 35 funnel wins), with
2016 at −43.7% and 2021 at −30.4%. The campaign **total** is exact — 502.0 against 502 — so the
headline is right and the composition inside it is wrong. That is the shape that publishes a
correct total over a false growth curve, on a page whose whole subject is growth over time.

## 2. And round 1 carried a defect of its own that no test would have caught

`volume_m3`, `solar_aperture_m2` and `internal_gain_kw` returned **identical KS to five decimal
places in both arms**. They are not three agreeing measurements. Read off
`fabric_physics.fabric_parameters`:

```
volume_m3        = area * _STOREY_HEIGHT_M
solar_aperture_m2= area * _WINDOW_AREA_RATIO * _SOLAR_TRANSMITTANCE * _FRAME_FACTOR
internal_gain_kw = area * _INTERNAL_GAIN_W_PER_M2 / 1000
```

**One quantity in three units, by construction, on every base and for every household** — measured
pairwise correlation exactly 1.000 over the 502 candidates. Carrying all three weighted floor area
**three times against infiltration's once**, in both the standardised distance the medoids are
chosen by and the least squares the mass is solved from. The sample was being chosen for difference
in *size* while reporting that it was chosen for difference in *behaviour*.

Caught by printing the table at real inputs before shipping the formula. Nothing else would have
caught it: every test I would have written would have passed, and the arm still beat its
counterfactual by 1.53× while carrying the defect.

## 3. The two repairs, and the ONE prediction that matters

**REPAIR A — the axes are four, not six.** `CHOICE_AXES` becomes
`(floor_area_m2, fabric_w_per_k, raw_infiltration_ach, customer_years)`. Area is carried once,
under its own name.

**REPAIR B — the year marginal becomes a CONSTRAINT, not an axis.** `fit_weights` gains an additive
`groups=` parameter (`None` keeps it byte-identical, the same promise `rake(axes=...)` makes):
one heavily-weighted row per distinct label requiring the chosen members carrying it to sum to that
label's population share, at the *same* weight as the sum-to-one row it partitions.
`customer_years` **stays** on `CHOICE_AXES`, because the choosing has no constraint rows and it is
the only thing stopping the medoids collapsing onto one year of the campaign.

**P8 — the year composition is reconstructed.** Every year within **±5%**. This is close to
arithmetic rather than a discovery — the rows state the very quantity being graded — and it is
recorded so that a failure is visible, not because passing it is evidence of anything.

**P9 — THE PREDICTION THIS DOCUMENT EXISTS FOR: what does the constraint COST?** Mass forced onto
ten year rows is mass the fit cannot spend on the demand axes, so P1's ratio must fall. I predict
it lands in **1.20×–1.45×** — down from 1.530× but still clear of the 1.10× kill line.

**If it lands below 1.10×, the design does not survive the constraint the published page requires,
and I will land that refusal rather than the wiring.** Round 1's 1.53× would then be a number
bought by a sample that reconstructs no year correctly, which is not a sample this repository may
publish a growth curve from. There is no third option where I keep the 1.53× and drop the year
rows: the per-year counts are rendered on
`site/data/book_growth.json` and read by a human as facts about years.

**P10 — removing the two duplicate axes moves P1 by less than 0.15× on its own.** They were
perfectly correlated with a retained axis, so the *information* in the matrix is unchanged and only
the relative weighting moves. A large swing would mean the medoids were being driven by the
triple-counting rather than by the population, and would make round 1's 1.53× an artefact.

## 4. What is graded where

P6 (the P&L moves by more than 1.0%) and P7 (the null case stays byte-identical) are round 1
predictions not yet measured. They are graded in the results document with these, against the
**repaired** arm, because measuring a margin on a sample I already know reconstructs no year
correctly would be measuring the defect.
