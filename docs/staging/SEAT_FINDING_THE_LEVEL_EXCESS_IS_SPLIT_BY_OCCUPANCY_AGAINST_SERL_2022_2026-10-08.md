**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `land-the-dated-cooking-cut-and-find-the-unsourced-200`

# The gas-home level excess, split by occupancy against SERL 2022

Delivery seat, 2026-10-08. Decided blind to company results: nothing below reads a company figure.

**Duplicate-work note.** The draw reported this id "already held" in `.seat_work_in_hand.json`. The
claim was stamped about two minutes before this invocation read it, with `paths: []`, and no other
process held the item. It was the draw's own write. The claim and this work are the same item.

Follows `SEAT_FINDING_A_GAS_HOMES_ELECTRICITY_LEVEL_SPLIT_INTO_THE_CRISIS_AND_A_LEVEL_EXCESS_2026-10-08.md`,
which left about +200 kWh/yr of level with no sourced end use. That figure is the world's 2,924
after the cooking cut, against a crisis-free SERL 2022 of 2,674–2,717.

## Step 1: the cooking cut is landed

Oven ×0.80 and hob ×0.84 (DESNZ ECUK 2023 Electrical Products, per appliance, 2011 → 2022) now sit
on `duration_hours` in the two `APPLIANCE_CATALOGUE` rows. They are named constants with their
source beside them. The control is `tests/simulation/test_a_homes_oven_and_hob_sit_at_their_2022_energy.py`.
The paired run (−61 on the annual median, 2,921 homes) is in the predecessor finding.

**The value-arms re-take is budgeted, not run.** This is the fourth `premise_trace.py` level change
since the value arms were last taken, after 92d39bf60, a41cf3fc0 and 6987325ae. No change here moves
`world_level_identity()`, because the departure block is untouched. So no control reds, and the arms
describe the previous electricity world. One re-take covers all four, and it should run after the
level work below settles, not once per term.

## Step 2: lighting cannot be the +200 on any published level

Lighting has no metered 2016–2025 level. ECUK's modelled series breaks in 2021/22, with about 305
kWh/yr per household in 2021 on the old method and about 137 in 2022 on the new
(`docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md`). The world's
constant gives about 210, which sits inside that bracket. Even ECUK's new-method low end takes only
about **−70** from the world, and the old method would *add* about +95. Lighting can contribute at
most about a third of the +200, and only if the lower regime is the true one. That is not
established, so the lighting constant is not changed. It stays a named gap.

## Step 3: is the world drawing SERL's homes? (pre-registered before the probe ran)

**What SERL publishes.** SERL Statistical Report Vol 2, aggregated tables (figshare 25472560,
`SERL_Stats_Report_Aggregated_Tables_Vol_2.xlsx`), sheet `Figure_48`. It gives 2022 electricity
imports for gas-heated no-PV homes by number of occupants: the median of each home's daily mean,
with n.

| Occupants | n | Share | Median kWh/day | ≈ kWh/yr | Crisis-free ×1.055–1.072 |
|---|---|---|---|---|---|
| 1 | 1,770 | 25.6% | 4.35 | 1,588 | 1,675–1,702 |
| 2 | 2,970 | 42.9% | 7.21 | 2,632 | 2,777–2,821 |
| 3 | 940 | 13.6% | 8.33 | 3,040 | 3,208–3,260 |
| 4 | 880 | 12.7% | 10.57 | 3,858 | 4,070–4,136 |
| 5 | 260 | 3.8% | 12.17 | 4,442 | 4,686–4,762 |
| ≥6 | 100 | 1.4% | 12.39 | 4,522 | 4,771–4,848 |

The crisis factor is the predecessor's 2,674–2,717 over 2,535. It is carried across bands unchanged,
which is a simplification. `Figure_44` gives the same by floor area (≤50: 3.88 kWh/day; 51–100:
6.09; 101–150: 8.54; 151–200: 11.02; >200: 12.84; n 310/2,410/950/260/130).

**What the world does.** `premise_trace._PEOPLE_BY_BEDROOMS` draws the headcount from bedrooms. It
is marked `domain-knowledge` and cites no source. A 3-bed home is never drawn with one occupant, and
a 2-bed home is single one time in four. In the 2021 Census, about 30% of English households are a
single person, and many of them live in 3-bed houses.

**Measurement.** `/tmp/gaslevel/occ.py`, at the current origin with the cooking cut, C1 2022. Same
1,200 premises × seeds 17, 29 and 41. Each gas-heated no-PV home is tagged with its
`behaviour_profile_for(...).people_count` and its `floor_area_band`. Per home, the reading is the
annual import over 365, which is SERL's per-band basis.

**Predictions:**
1. The world's single-occupant share is **8–15%**, against SERL's 25.6%.
2. Re-weighting the world's per-band medians to SERL's occupancy mix takes **−100 to −200** off the
   world's overall per-home median.
3. Band by band, the world sits within **±10%** of SERL's crisis-free medians for 1–4 occupants. The
   excess is mostly composition, not per-home level.

**Decision rule, written now.** If (2) is −100 or more and (3) holds, the +200 is mainly a
population-mix defect. The remedy is a sourced headcount-given-bedrooms table, from Census 2021
occupancy by bedrooms and tenure, not an end-use constant. That remedy is handed on and is not
built in this item. It changes every premise's draw, so it gets its own pre-registered arm. If the
per-band medians run above SERL in every band, the excess is per-home, and the next place to look is
the end uses.

## Result (`/tmp/gaslevel/occ.py`, 2,921 homes, seeds 17/29/41, cooking cut in, C1 2022)

The per-home median is **2,923 kWh/yr**. That agrees with the S4 sum of monthly medians (2,924), so
the two bases can be used interchangeably here.

| Occupants | World n | World share | SERL share | World kWh/yr | SERL crisis-free | World ÷ SERL |
|---|---|---|---|---|---|---|
| 1 | 512 | 17.5% | 25.6% | 1,961 | 1,675–1,702 | **1.16** |
| 2 | 731 | 25.0% | 42.9% | 2,456 | 2,777–2,821 | 0.88 |
| 3 | 648 | 22.2% | 13.6% | 2,888 | 3,208–3,260 | 0.89 |
| 4 | 488 | 16.7% | 12.7% | 3,331 | 4,070–4,136 | **0.81** |
| 5 | 310 | 10.6% | 3.8% | 3,711 | 4,686–4,762 | 0.79 |
| ≥6 | 232 | 7.9% | 1.4% | 3,905 | 4,771–4,848 | 0.81 |

Mean occupants: world **3.02**, SERL 2.30, Census 2021 (TS017, England and Wales) 2.36. Re-weighted
to SERL's occupancy mix, the world's per-home median is **2,606**: −317, and now *below* the
crisis-free 2,674–2,717.

**Predictions graded.** (1) Single-occupant share 8–15%: **wrong**. It is 17.5%. The world's error
is at the top of the distribution, not the bottom: 18.5% of homes have 5+ occupants, against SERL's
5.2%. (2) Re-weighting takes −100 to −200: **wrong**, it takes −317. (3) Within ±10% per band:
**wrong**. The world is too *flat* in occupancy. It is +16% at one occupant and −19 to −21% at four
or more. SERL's whole-home elasticity, ln(10.57/4.35)/ln 4, is **0.64**. The world's is **0.38**.

**Where the extra occupants come from: the bedroom count, not floor area.** The world's floor-area
mix is close to SERL's (bands 1–5: 9.7/53.9/28.2/5.4/2.8% against 7.7/59.4/23.4/6.4/3.2%).
`premise_population.py` (and `tools/demand_case_coverage.py`, the same expression) turns the band
midpoint into bedrooms as `round(2 + (area − base)/14 m²)`, clamped at 6. A 101–150 m² semi or
terrace (midpoint 125) is therefore **six bedrooms**, and so is every band-4 and band-5 home. Over
the drawn gas homes, **36% have 5+ bedrooms**. The English Housing Survey's figure is a few percent.
`_PEOPLE_BY_BEDROOMS` then draws 3–6 people for a 5- or 6-bed home. The 14 m²/bedroom is the
fabric model's *forward* rule, and inverting it from a band midpoint over-counts bedrooms. Neither
`_FLOOR_AREA_PER_BEDROOM_M2` nor `_PEOPLE_BY_BEDROOMS` cites a source.

The same flatness shows by floor area (world against SERL crisis-free, kWh/day). ≤50 m²: 5.97
against 4.13 (+45%). 51–100: 7.26 against 6.48 (+12%). 101–150: 9.50 against 9.08. 151–200: 10.05
against 11.72 (−14%). >200: 9.59 against 13.65 (−30%).

## What this says

1. **The +200 is not an unsourced end use. It is two offsetting defects in who lives in the world's
   homes.** Too many large households (bedrooms over-drawn from area, then people from bedrooms)
   pushes the level up. Too little extra use per occupant pulls it down. Net: about +200.
2. **Fixing either one alone moves the level the wrong way.** A sourced headcount alone puts the
   world near 2,606, about 90 below the crisis-free band. Steepening the per-person slope alone
   raises it further. They must be fitted as a pair, in order: headcount first (sourced: Census 2021
   occupancy by bedrooms and household size), then the per-person slope graded against SERL
   `Figure_48`'s per-band medians.
3. **This reaches beyond electricity.** Headcount drives DHW litres, gas cooking, metabolic gain and
   `appliance_intensity`. Bedrooms drive the fabric model's floor area. Every gas figure the world
   produces carries the same mix. It is a world-fidelity defect of the W2 population class, decided
   blind to company results.
4. **No end-use constant should move for the level until the mix is fixed.** The lighting gap stays
   a gap. The per-band reading in this note is the instrument for the next arm.

**Not established.** SERL is unweighted and over-represents two-person households (42.9%, against
about 34% in Census 2021). So SERL's mix is not GB's either, and the headcount fix should target the
Census, with SERL's per-band medians as the per-home check. The crisis factor is applied uniformly
across bands.
