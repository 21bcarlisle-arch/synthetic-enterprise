**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `headcount-given-dwelling-size-then-the-per-occupant-slope`

# Headcount given dwelling size: bedrooms from VOA, then people from Census RM136

Autonomous worker, 2026-10-09. Decided blind to company results: nothing below reads a company
figure. Built off origin `91a798172`. The cooking-class continuation
(`take-the-rest-of-the-cooking-class-off-headcount-per-hes-table-23`) was in flight in another
worktree and is not duplicated. Nothing here touches `premise_trace.APPLIANCE_CATALOGUE`.

## Two defects, both measured before building

1. **Bedrooms came from an unsourced inversion of floor area.**
   `draw_premise_from_joint` set `round(2 + (area_midpoint - base) / 14)`, clamped to 1..6. On
   4,000 drawn homes (seed 17) the result was 23.4% one-bed, 16.8% two, 20.1% three, 5.7% four,
   9.8% five and **24.2% six-plus**. VOA's stock at 31 March 2025 is 12.7 / 28.2 / 42.9 / 12.7 /
   2.5 / 0.9% (CTSOP3.0, England and Wales, known bedrooms only).
2. **Headcount ignores the dwelling.** `people_count_for_area` draws the output area's TS017
   distribution whatever the home. Census 2021 RM136 says 74% of one-bed households are one
   person, against 11% of 4+-bed households.

## The sources, all published and dated (`tools/dwelling_size_joint.py`)

- **VOA CTSOP3.0** at 2025-03-31 (published 2026-05-22): dwellings by council tax band x type x
  bedrooms, England and Wales.
- **DESNZ NEED anon 50k** (2026): each row's type, HMRC floor-area band and council tax band.
  P(bedrooms | world type, area band) is the sum, over NEED rows in that cell, of VOA's
  P(bedrooms | the row's own type, its band).
- **ONS Census 2021 RM136**, all tenures, England and Wales: P(bedrooms | household size), both
  capped at 4+.
- Headcount: P(size | output area, bedrooms) ∝ TS017(size | area) × RM136(bedrooms | size).

**Out-of-sample check, passed before building.** EHS 2012 (*Floor Space in English Homes*,
technical report Fig 2.5) publishes the mean usable floor area by number of bedrooms. None of the
three sources contains that relation. Derived against EHS:
1 bed 53.2 vs 47.0 m², 2 beds 75.1 vs 70.9, 3 beds 97.3 vs 94.7, 4+ beds 139.0 vs 158.4. The
order holds, and the gaps are about the size of the band-midpoint coarseness (band 5 is ">200",
taken as 230).

**One variable at a time.** `fabric_physics.floor_area_m2` reads area back out of `bedrooms`. A
home drawn from the joint now keeps the area its old round trip gave, computed from its
floor-area band. **The fabric, and so the gas, is byte-identical.** The round trip's own loss is
a separate defect, recorded here and not acted on: a band-5 detached home (midpoint 230 m²) is
heated as 144 m², because the six-bed clamp caps it.

## Pre-registration (written before any run)

Measurement: `/tmp/hcbed/occ_beds.py` copies `/tmp/gaslevel/occ_book.py` (2,921 gas-heated no-PV
homes, seeds 17/29/41, C1 2022) and runs both arms in one process: the unconditioned headcount
and the bedrooms-conditioned one, on the new bedrooms.

1. **Bedrooms marginal** on drawn homes: six-plus falls from 24% to **≤3%**; three-bed is the
   mode at **35–45%**.
2. **Mean occupants**, gas no-PV: from 2.29 to **2.30–2.45**. Gas homes skew to houses, and
   houses have more bedrooms. **5+ share** from 5.8% to **6–8%**. **Single share** from 31.7% to
   **27–31%**.
3. **Overall per-home electricity median** from 2,613 to **2,630–2,720 kWh/yr**. Headcount is the
   only input that moves.
4. **Per-occupant elasticity** ln(m4/m1)/ln 4: **unchanged within ±0.03 of 0.37**. Per-occupant
   behaviour is untouched, and the elasticity is read within headcount.
5. **Floor-area gradient** (kWh/day, band 5 ÷ band 1): from 0.99 (6.92/6.97) to **1.15–1.40**.
   SERL's is 3.3x. Most of that gradient is NOT headcount.

**Decision rule.** If (5) lands at or below 1.4, conditioning on size closes little of SERL's
gradient. The rest is per-dwelling end use (lighting, appliances by size), or the per-occupant
slope, or both. Neither is moved without a dated source.

## Result (`/tmp/hcbed/occ_beds.py`, both arms in one process, origin `91a798172`)

**The population is not the predecessor's, and that is not this change.** The predecessor had
2,921 gas-heated no-PV homes; at origin `91a798172` the same draws give **2,431**. The likely
cause is W2_20 (heating drawn given gas supply, landed 2026-10-07), which removes about a sixth
of gas boilers, and that probe ran on a tree without it. So the baseline is arm U below, **not
2,613**. Arm U and arm C are the same 2,431 homes, and only the headcount differs.

**Integrity.** Fabric floor area is identical to the old round trip on **2,431 of 2,431** homes.
Every row's bedrooms and both headcounts were recomputed in a clean process afterwards, and **0 of
2,431 differ**. The worktree was edited for a mutation test about 30 s after launch, and this
shows no worker read the mutated file.

| | Arm U (unconditioned) | Arm C (given bedrooms) | Prediction | Graded |
|---|---|---|---|---|
| Six-plus bedrooms | 25.3% (old inversion) | **0.8%** | ≤3% | held |
| Three-bed share | 21.5% (old inversion) | **49.2%** | 35–45% | **wrong**: gas homes are houses, and VOA's semi is 73% three-bed |
| Mean occupants | 2.292 | **2.318** | 2.30–2.45 | held, at the bottom |
| 5+ share | 6.1% | **6.4%** | 6–8% | held |
| Single share | 32.3% | **31.3%** | 27–31% | **wrong, narrowly** |
| Per-home median kWh/yr | 2,617 | **2,642** | 2,630–2,720 | held |
| Elasticity ln(m4/m1)/ln 4 | 0.335 | **0.344** | 0.37 ± 0.03 | **wrong as written**: the delta (+0.009) held, the base did not. 0.37 was the predecessor's population |
| Area band 5 ÷ band 1 | 0.967 | **1.095** | 1.15–1.40 | **wrong, low** |

RM136 in the conditioned arm: one-bed homes hold one person 79% of the time (RM136 74%), and 4+-bed
homes 12% (RM136 11%).

**What this says.** Conditioning on size is a fidelity correction: one home's bedrooms and its
headcount now agree with the published stock. It is not a lever on the level. It moves the mean by
+0.03 people and the median by +25 kWh/yr, and it gives the world a floor-area gradient of 1.10
against SERL's 3.3. **By the decision rule, almost none of SERL's floor-area gradient is
headcount.** It belongs to per-dwelling end use, or to ownership by dwelling, and no source here
yet sets either.

## The per-occupant slope: filed as a named gap, no constant moved

On the book's own conditioned headcount the slope is **0.344**, and **0.272** on the landing base below. Whole-home anchors: SERL 2022
gas no-PV **0.64** per occupant, and NEED 2023 Table A14 (electricity by number of ADULTS,
Experian-modelled, all heating types) ln(3,772/1,993)/ln 4 = **0.46**.

The per-end-use evidence points the other way. HES 2012 (Intertek R66141) by household type:

| HES table | Single pensioner | Single non-pensioner | Multiple pensioner | With children | Multiple, no children |
|---|---|---|---|---|---|
| Table 25 lighting, kWh/yr | 548 | 581 | 413 | 477 | 548 |
| Table 26 audiovisual, kWh/yr | 465 | 453 | 441 | 603 | 630 |
| Table 23 cooking (kettle, oven) | flat (see the kettle finding) | | | | |

Lighting has **no** headcount gradient in HES, and audiovisual about +35% from one-person to
multi-person households. The world's lighting and electronics are **linear** per person
(`_LIGHTING_KW_PER_PERSON`, `_ELECTRONICS_KW_PER_PERSON`), so they are already steeper than
HES. HES's whole-home total is also flat by type (Table 1: 3,427 single pensioner, 3,853
single non-pensioner, 3,812 multiple pensioner, 3,672 with children).

**So no per-person constant in the world can be steepened from a dated source, and two are
steeper than their source.** SERL's 0.64 and NEED's 0.46 are whole-home gradients, and the
per-use evidence says the gradient is not in use per person. The candidates left are ownership
by household size (EFUS ownership is already headcount-keyed in `owned_stock`), dwelling
correlates, and SERL's own composition (crisis response by size). None is sourced. **The gap
is: a per-end-use source of the whole-home slope.** Fitting the exponent in
`appliance_intensity = (n/2.4)^0.6` to SERL is refused: that exponent's comment says "as
EFUS/NEED volume scaling is", and it cites no table.

The lighting and audiovisual shapes above are a *sourced* reason to make lighting flatter per
person. That would make the slope flatter still, moving it away from SERL. It is the same class
as the cooking continuation (an end use off headcount) and is left to that line of work: one
variable each.

## Peak and season re-read (`couple_fabric.serl_level_and_season` cells, 2,431 homes, seeds 17/29/41)

| Cell | Arm U | Arm C | SERL band | Verdict |
|---|---|---|---|---|
| S1 trough @04:30 | 0.1388 | 0.1388 | 0.125–0.135 | **FAIL, high** (identical in both arms) |
| S2 peak | 0.534 @20:00 | 0.537 @20:00 | 0.445–0.485 @18:30 | **FAIL**, high and 1.5 h late |
| S3 month max/min | 1.248 | 1.241 | 1.36–1.47 | **FAIL**, flat |
| S4 annual, sum of monthly medians | 2,602 | 2,626 | unjudged; crisis-free 2022 ≈ 2,674–2,717 | below the derived band |

**The headcount holds none of them.** Peak and season fail whatever the headcount. What holds the
peak is the evening non-cooking stack the season finding named (electronics on-mode, lighting,
dishwasher; with all cooking removed the peak sits at 20:30). The season shortfall is the summer
level. Both are written into triage row `a-gas-heated-homes-electricity-has-no-season`, which
stays open.

**A trough that moved, and I cannot yet say why.** The season finding's last section read the
trough as passing at 0.127 on 163 homes. It now fails at 0.139 on 2,431 homes, identically with
and without the conditioning. Since then the population (W2_20), the headcount instrument
(`b9808cf60`) and the kettle (`302477495`) have all landed. Prediction filed here, before any
run: the trough rose with the census headcount switch (`b9808cf60`), because the always-on load
(cold appliances, standby) is drawn from ownership keyed on headcount. That is a one-variable
check for the next draw.

## Re-read on the landing base (`fbf3e3ba2`: cooking class off headcount, then the microwave level)

Two cooking changes landed while this was measured: `ecd94c38c` (oven, hob, toaster and microwave
off headcount) and `fbf3e3ba2` (the microwave at HES's 56 kWh). The work was moved onto each in
turn, and every read was taken again on the base it lands on: same probes, same 2,431 homes,
both arms in one process. **These are the numbers of record.** The tables above were measured
on `91a798172` and are kept as the earlier measurement.

| | Arm U | Arm C | SERL |
|---|---|---|---|
| Mean occupants / single / 5+ | 2.292 / 32.3% / 6.1% | 2.318 / 31.3% / 6.4% | -- |
| Per-home median kWh/yr | 2,666 | **2,679** | crisis-free 2022 ≈ 2,674–2,717 |
| Elasticity ln(m4/m1)/ln 4 | 0.267 | **0.272** | 0.64 |
| Area band 5 ÷ band 1 | 0.971 | **1.052** | 3.3 |
| S1 trough | 0.1388 | 0.1388 | 0.125–0.135, **FAIL** |
| S2 peak | 0.553 @20:00 | **0.562 @20:00** | 0.445–0.485 @18:30, **FAIL** |
| S3 month max/min | 1.246 | **1.239** | 1.36–1.47, **FAIL** |
| S4 annual | 2,644 | 2,663 | unjudged |

The cooking changes flattened the slope from 0.335 to 0.267, as HES Table 23 predicts. They
raised the peak from 0.534 to 0.553: one-person homes now cook a whole household's meal, and the
microwave adds evening uses. On `7d5259c7b` (cooking off headcount, before the microwave) the two
arms read 2,631/2,653, slope 0.274/0.280, and peak 0.547/0.552. The conclusions above stand on
every base.

## Also recorded, not acted on

- **The floor-area round trip loses information.** `fabric_physics.floor_area_m2` heats a band-5
  (>200 m²) detached home as 144 m², because the old six-bed clamp caps the area it recovers.
  Using the band midpoint directly is a separate gas-side change.
- **Assumptions named in `tools/dwelling_size_joint.py`.** Bedrooms are independent of floor area
  given type and council-tax band. Bedrooms are independent of output area given household size.
  The NEED 50k sample is stratified, not population-weighted.
