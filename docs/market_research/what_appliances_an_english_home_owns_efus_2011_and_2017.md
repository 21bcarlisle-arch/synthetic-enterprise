# What appliances an English home owns: EFUS 2011 and 2017

**Knowledge:** none -- this is the ownership read that W1_29's texture evidence doc names as the step before any per-home stock draw. It anchors rates for that build, and no knowledge page covers household appliance stock yet.

*Read 2026-10-06 for W1_29 (`the_half_hourly_texture_of_real_homes_electricity_read_from_low_carbon_london.md`).
That doc found that the world's homes all own the same stock, and that ownership rates were not in the
knowledge layer. This is that read. It also closes the lead that `occupancy_consumption_volume_shape_w2_13.md`
§6 left unfetched on 2026-07-23 (the EFUS light-appliances report).*

## Sources

- **EFUS 2011.** BRE for DECC, *Energy Follow-Up Survey 2011, Report 9: Domestic appliances, cooking &
  cooling equipment* (December 2013, BRE 288143). 2,616 interviewed households in England, weighted to
  21.9 m. assets.publishing.service.gov.uk/…/file/274778/9_Domestic_appliances__cooking_and_cooling_equipment.pdf
- **EFUS 2017.** BEIS, *Energy Follow-Up Survey: Lights, appliances and smart technologies* (2021).
  2,515 households at Interview 1. Table 4.1 sets 1998, 2011 and 2017 side by side.
  assets.publishing.service.gov.uk/…/file/1018724/efus-light-appliances-smart-tech.pdf

Both cover England only, and ownership is self-reported at interview.

## Ownership: share of households owning at least one

| Appliance | 2011 | 2017 | Notes |
|---|---|---|---|
| Washing machine (incl. washer-dryer) | 96.5% | 97% | 2011 T1; 2017 §4.1.1 |
| Tumble dryer (incl. washer-dryer) | 61.6% | 58% | 2011 T1; 2017 §4.1.1 |
| — separate tumble dryer | 49.3% | 45.8% | 2011 T1 vs 2017 T4.1 count different bases (46.7% in T4.1 for 2011) |
| — combined washer-dryer | 13.6% | 13.2% | |
| Any fridge | 98.7% | 99% | |
| Any freezer (not counting ice boxes) | 93.4% | 93% | 98% in 2017 if ice-box fridges count |
| Fridge-freezer | 64.9% | 65.8% (+7.4% American-style) | |
| **Separate freezer** | **46.1%** | **38.2%** | a significant fall from 2011 to 2017 |
| Dishwasher | 38.5–40.6% | **44.3%** | 21.4% in 1998 |
| Oven | 95.4% | 95.8% | |
| Hob | 93.3% | 91.5% | |
| Microwave | 82.6% | 89.7% | |
| TV | 98% (mean 2.3, median 2) | 96.1% | 2011 Fig 7 / T20 |
| Any energy-intensive appliance (aquarium, hot tub, greenhouse heater, workshop…) | — | 10.3% | 2017 T4.2; 25% of 5+ person homes, 5% of 1-person |

## By household size (EFUS 2011, Tables 2, 8, 11, 20)

| Persons | Tumble dryer | Any freezer | Dishwasher | Mean TVs |
|---|---|---|---|---|
| 1 | 49% | 88% | 19% | 1.6 |
| 2 | 65% | 94% | 45% | 2.3 |
| 3 | 66% | 96% | 47% | 2.6 |
| 4 | 70% | 98% | 60% | 2.8 |
| 5+ | 65% | 96% | 48% | 3.3 |

EFUS 2017 gives the same gradient in prose (§4.1.1–4.1.3). Tumble dryers: 43% of one-person homes and
61–71% of larger ones. Freezers: 88% against 93–98%. Dishwashers: 27% against 45–57%.

**Income and tenure drive ownership as hard as size does, and dishwashers hardest.** In 2017, 24% of
first-quintile households owned a dishwasher against 74% of fifth-quintile ones. By tenure it was 58%
of owner-occupiers, 29% of private renters and 12–13% of social renters. Tumble dryers run 52% → 73%
across income quintiles in 2011. Neither survey publishes a size × income cross-tab.

## Cooking fuel (the split ASSUMPTIONS records as NOT FOUND)

- **2011 (T15, T16):** ovens 68.7% electric and 29.3% gas; hobs 37.9% electric and 61.2% gas. Among
  homes with an electric oven, 54.8% are all-electric and 43.5% have a gas hob. Among homes with a gas
  oven, 95.2% are all-gas.
- **2017 (Fig 4.5):** 37% electric oven and electric hob, 33% electric oven and gas hob, 20% gas oven and
  gas hob, 9% another combination. Electricity's share of cooking has grown across 1998, 2011 and 2017.

This is the national split, not one conditioned on gas heating. Among gas-heated homes the electric
hob share must be below 37–38%, because almost every home without gas cooks electrically, but the
survey does not publish that conditional. **`premise_trace.py` currently puts ALL cooking of a
gas-DHW home on gas** (the comment at the cooking block names the split NOT FOUND). Even when
conditioned on gas heating, an electric oven is the majority case. That is a separate defect from
W1_29's texture red, and it is noted here and not filed, because it moves energy between fuels and not
the texture.

*Corrected 2026-10-08 (worker, by reading the code): the sentence above is wrong. A gas-DHW home in
the world cooks on BOTH fuels. It burns cooking gas (`cooking_daily_kwh`, 7.5% of domestic gas), and
`owned_stock` gives every home the electric `oven` and `hob` from `APPLIANCE_CATALOGUE`, because no
cooking fuel is drawn. So the defect does more than move energy between fuels. It adds about 500 kWh/yr
of electricity at the gas-heated median and most of the evening peak excess against SERL 2022.
Measured in the finding named in the seasonal-swing doc's 2026-10-08 section.*

## Base load (EFUS 2011 §4.1)

The median base load was **90 W** and the mean 136 W. Base load here means the power exceeded 90% of the
time, measured at 10-second resolution. The sample was 79 monitored homes without electric space or
water heating, unweighted. Mean hourly demand ran from 121 W to 2,438 W across homes. The report puts
the high tail down to high TV and appliance ownership, unusual equipment (a heated pool) and high base
load. This gives a sense of scale for W1_29's LCL base-load distribution. It is not a substitute for
it: n=79, and the sample excludes electric heating.

## What this means for the world's stock, against `simulation/premise_trace.py`

| Code today (every home) | Real share |
|---|---|
| fridge-freezer **and** separate freezer (`COLD_APPLIANCES`) | separate freezer 38% (2017), lowest in one-person homes |
| dishwasher in `APPLIANCE_CATALOGUE` | 44% (19–27% of one-person homes) |
| tumble dryer in `APPLIANCE_CATALOGUE` | 58% (43–49% of one-person homes) |
| oven and hob as electric appliances (and cooking gas too, in a gas-DHW home) | 73% electric ovens and 37–38% electric hobs nationally |
| 25 W constant standby (`UNIFORM_STANDBY_KW`) | not established per home here. EFUS gives whole-home base load only. *Since 2026-10-06 drawn per home from that base load (`always_on_kw`, lognormal on median 90 W / mean 136 W)* |
| `_ELECTRONICS_UNITS_PER_PERSON = 2.0` | TVs alone run 1.6 to 3.3 per home by size, which is not proportional to persons (1 person → 1.6, 4 → 2.8) |

**Every row is a structural sameness the texture red predicts.** The two cold appliances alone set the
night level and the autocorrelation. The 62% of homes that own no separate freezer in reality each carry
one in the world, about 0.1 kW × 0.30 duty (≈0.7 kWh/day) of cycling load they should not have. The 56%
with no dishwasher and the 42% with no tumble dryer carry those large, long-dwell events too.

**What is anchored for a build:** the per-appliance ownership probabilities by household size in the
2011 table above, with 2017 as the later check. **What is still not established:** the joint
distribution (ownership is correlated through income and tenure, and the world has no income on a
premise at this seam unless it is drawn), per-home standby, and the number of lighting and electronic
units. Nothing here supports a per-person lighting count either way.

*Built 2026-10-06, the same evening: `simulation/premise_trace.py` `owned_stock` draws the dishwasher and
tumble dryer from the 2011 by-size rows above and the separate freezer from the 2017 national 38.2%. The
cooking-fuel split, standby and electronics counts are untouched. What it did to W1_29's texture cell is
in the texture doc's last section.*
