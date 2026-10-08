**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `fit-the-worlds-headcount-then-its-per-occupant-slope-against-census-and-serl`

# The 3.02 headcount was the instrument's, not the settled book's

Delivery seat, 2026-10-09. Decided blind to company results: nothing below reads a company figure.

**Duplicate-work note.** The draw reported this id "already held" in `.seat_work_in_hand.json`. No
other seat or `surgical_land` process was running when this invocation started (`ps`), so the
claim was the draw's own write. This is the same item.

## The premise, re-measured before building

The item asks for a sourced headcount, because
`SEAT_FINDING_THE_LEVEL_EXCESS_IS_SPLIT_BY_OCCUPANCY_AGAINST_SERL_2022_2026-10-08.md` measured a
mean of 3.02 occupants per gas home against Census 2021 TS017's 2.36.

**That 3.02 is not the headcount the world settles.** The book already has a sourced headcount.
`fabric_demand_path.build_fabric_series` (the `run_phase2b` path) passes
`household_physical_layer.people_count_for` (TS017, delegated to
`dwelling_records.people_count_for_area`) into `behaviour_profile_for`, and has done since
2026-09-16. `household_physical_layer._profile_for` does the same.

The probe (`/tmp/gaslevel/occ.py`) did something else. It called
`behaviour_profile_for(pid, hh, seed=seed)` with no headcount, and measured
`couple_fabric._trace_for`, which calls `generate_premise_trace` with no `behaviour`. Both fall back
to `premise_trace._PEOPLE_BY_BEDROOMS`, which is unsourced and fed by the floor-area-to-bedrooms
inversion. Every instrument that calls `generate_premise_trace` without a profile does the same:
`tools/couple_fabric.py` (the S4 level the +200 was read from), `simulation/world_home_identity.py`
(the home-demand digest), `tools/book_shape_spread.py` and `tools/explain_premise_year.py`.

So there are still two answers to "how many people live here". `people_count_for`'s own docstring
names this defect: one home, two draws of one quantity. Here the second draw is the one the
measuring instruments use.

## Pre-registration (written before the run)

**Measurement.** `/tmp/gaslevel/occ_book.py` copies `occ.py` with one change. The headcount is
`people_count_for(pid, hh.output_area)`, and the trace is generated with the profile built from that
headcount, as `fabric_demand_path` does. Same 1,200 premises × seeds 17, 29 and 41, C1 2022,
gas-heated no-PV homes.

**Predictions:**
1. Mean occupants **2.30–2.45**, single-occupant share **27–33%**, 5+ share **5–9%**. This is
   close to certain, because the draw is TS017.
2. The overall per-home median falls from 2,923 to **2,550–2,700 kWh/yr**. SERL-reweighting the
   fallback gave 2,606. The Census mix has more single homes than SERL's.
3. The per-occupant elasticity (ln(m4/m1)/ln 4) is **flatter than the fallback's 0.38: 0.20–0.35**.
   The book's headcount is independent of dwelling size, so the floor-area part of the slope drops
   out.

**Decision rule.** If (2) holds, the item's step (1) is spent for the settled book. The remaining
work is (a) to make the instruments draw the book's headcount, which deletes `_PEOPLE_BY_BEDROOMS`,
and (b) the per-occupant slope (item step 2), graded on the book's headcount and not the
fallback's. The +200 then has to be re-read on the corrected instrument before anything else moves.
If (2) fails high (above 2,750), the book's level excess is per-home, and step 2 is the whole remedy.

## Result (`/tmp/gaslevel/occ_book.py`, 2,921 homes, seeds 17/29/41, C1 2022)

Same 2,921 homes as the predecessor finding. The headcount is the only change.

| Occupants | Book n | Book share | SERL share | Book kWh/yr | SERL crisis-free | Book ÷ SERL |
|---|---|---|---|---|---|---|
| 1 | 926 | 31.7% | 25.6% | 1,975 | 1,675–1,702 | 1.17 |
| 2 | 999 | 34.2% | 42.9% | 2,461 | 2,777–2,821 | 0.88 |
| 3 | 434 | 14.9% | 13.6% | 2,902 | 3,208–3,260 | 0.90 |
| 4 | 395 | 13.5% | 12.7% | 3,300 | 4,070–4,136 | 0.80 |
| 5 | 110 | 3.8% | 3.8% | 3,424 | 4,686–4,762 | 0.73 |
| ≥6 | 57 | 2.0% | 1.4% | 4,273 | 4,771–4,848 | 0.89 |

The overall per-home median is **2,613 kWh/yr**, against 2,923 on the fallback headcount. Re-weighted
to SERL's mix it is 2,601.

**Predictions graded.**
1. **Wrong, narrowly.** The mean is **2.29**, just under the predicted 2.30–2.45 (TS017 gives 2.36
   for all households; this is the gas no-PV subset). The other two parts held: the single share is
   31.7% and the 5+ share is 5.8%.
2. **Held.** The median is 2,613, inside 2,550–2,700.
3. **Wrong.** The elasticity is **0.37**, not 0.20–0.35. It is essentially the fallback's 0.38.
   The world's per-occupant slope comes from behaviour, not from dwelling size. With the headcount
   independent of size, the floor-area gradient disappears entirely. The book reads 6.97, 7.08,
   7.28, 7.54 and 6.92 kWh/day across area bands 1–5, against SERL's 3.88 to 12.84.

## What this says

1. **The item's step (1) is spent for the settled book.** The book's headcount marginal is TS017's
   and has been since 2026-09-16. The "+200 kWh level excess" was read off an instrument that drew
   a different population. **On the book's own headcount, the gas no-PV level is 2,613, about 60–100
   *below* the crisis-free SERL 2,674–2,717, not 200 above it.** The predecessor finding's
   re-weighting (2,606) had already shown this. It just did not know the book was already there.
2. **The instruments should draw the book's headcount. Built, measured, and NOT landed.** The
   change is small. In `behaviour_profile_for`, the `people_count is None` branch returns
   `dwelling_records.people_count_for_area(premise_id, household.output_area)`, the draw the book
   settles on, and `_PEOPLE_BY_BEDROOMS` is deleted. Its control is a third leg in
   `tests/simulation/test_the_settled_book_draws_its_headcount_from_the_census_and_not_from_bedrooms.py`:
   every one of the 2,000 drawn homes gets `people_count_for` when no headcount is supplied. It is
   mutation-proven: a constant fallback of 3 reds 1,687 of 2,000. **It cannot land on its own,
   because it reds 15 controls across the 28 test files that build a profile-less trace or
   profile.** Several of those reds are verdicts, not pins:

   | Control | Was | On the book's headcount | Kind |
   |---|---|---|---|
   | `test_a_kettle_boils_at_hes_energy::test_a_kettle_owners_year_is_hes_167_kwh` | ≈167 | **145** (±8.35 band) | **verdict**: per-occupant kettle use was fitted on a 3.02-occupant population |
   | two-level `test_L1_1n_CAN_PASS` / `TOLERANCE_is_LOAD_BEARING` | 0 violating | **P0049 at 0.984** | **verdict**, but one draw: P0049 reads 1.59/1.33/1.67/1.38/0.98/1.92 at 1–6 people, not monotonic |
   | two-level `test_the_L2_4_BAND_CAN_PASS` | reachable | stretched 3.590 < floor 4.881 | **verdict** on reachability |
   | two-level `REPAIR_ITSELF_fires_its_own_named_defect` | — | `InsufficientEvidence`: 25 consecutive-day pairs | structural |
   | two-level `netting_CHANGES_NOTHING_for_a_home_heated_off_the_judged_meter` | 3 homes moved | 2 | composition |
   | two-level `SMOOTH_mutation_is_VALID_AGAIN` | holds | 0.088 vs 0.112 | mutation relation |
   | two-level `L1_1n_FIRES_on_the_RESCALED_REAL_DAY` | 0.1633-ish | faked homes 0.194–0.217 | finding premise |
   | two-level MEASURED legs / P0000 / water-heater r / raw r / heat-pump critical | [3,15,31,47] / 0.1633 / 0.563 / 0.569 / 0.349 | [3,15,27,44] / 0.216 / 0.602 / 0.493 / 0.503 | pins |
   | `test_couple_fabric::TEXTURE_CELL_BREACH_CLOSED` S9 | 0.0604 | 0.0621 | pin |
   | `test_household_physical_layer::…bedrooms_draw_does_not` | its poison is the fallback | 0.008 > 0.025 fails | rewrite: the poison is deleted |

   **The class behind the verdicts.** Every end use and texture control calibrated or pinned on a
   profile-less trace was fitted to the bedroom population (mean 3.02, 18.5% at 5+), not the
   settled one (2.29, 5.8%). The kettle is the clearest case, and it is the per-occupant slope (3a
   below) showing up in a single end use.
3. **Two real defects remain, and they are not the ones the item named.**
   - **(a) The per-occupant slope is too flat**: 0.37 against SERL's 0.64, +17% at one occupant
     and −20% at four. This is the item's step (2), and it is now graded on the right headcount.
     Fixing it alone pushes the level UP, from below the band towards or above it. A rough
     mean-shift at the book's mix is +200 to +250 on the mean, and less on the median.
   - **(b) Headcount is independent of dwelling size.** In the bedrooms × people table above, a
     6-bed home is single 30% of the time, the same as a 1-bed. SERL's floor-area gradient (3.3×
     from ≤50 to >200 m²) shows dwelling size and occupancy are joint in the real stock. The source
     to fetch is Census 2021 household size by number of bedrooms (England and Wales). It would
     condition `people_count_for_area` on bedrooms, holding the TS017 marginal. Its input is the
     floor-area-to-bedrooms inversion, which over-counts bedrooms (36% of gas homes are 5+ bed).
     So (b) needs a sourced bedrooms-given-area mapping first (EHS), which is the item's original
     step (1) re-aimed.
4. **Order.** First the instrument switch (2 above), re-taking its 15 controls on the book's
   headcount. A verdict there is diagnosed, never loosened. Then (b), then (a): conditioning
   headcount on size gives the world some floor-area gradient, which changes how much of SERL's
   slope is still owed to per-occupant behaviour. The kettle verdict is (a) seen in one end use, so
   it may be the first per-occupant fit rather than a separate repair. The value-arms re-take waits
   for all three.

**Not established.** SERL's per-band medians are unweighted, and its mix is not the Census's. The
crisis factor is applied uniformly across bands. The bedroom distribution produced by the inversion
is unsourced.

**A composed fixture lost its drawn headcount (part of the unlanded switch).** `test_premise_trace.py`'s `P-base` (a 3-bed semi)
was 3 people under the fallback and is 1 under the census draw. A one-person home's winter/summer
gas ratio is 10.1, outside the G.2 diagnostic band of 2.5–9.0, which is anchored on the population's
~4.6×. The fixture now states three people. The band was not touched. Whether a per-home band
should hold for a one-person home is a separate question, recorded here and not acted on.

**A dead dial, noted and not acted on.** `tools/couple_fabric.PANEL` rows carry a composed `people`
column. `_household` accepts it and drops it, because `Household` has no headcount. So the panel
homes got the bedroom fallback before this change and get the census draw after it. They never got
their composed value. Threading it through `behaviour_profile_for(people_count=...)` would move every
panel figure. That is its own change.
