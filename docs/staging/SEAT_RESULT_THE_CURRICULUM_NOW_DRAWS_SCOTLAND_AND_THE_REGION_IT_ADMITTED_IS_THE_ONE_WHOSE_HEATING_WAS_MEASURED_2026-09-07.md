**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W2_18_the_housing_joint_the_sample_and_the_ceiling

# RESULT: the curriculum draws eleven regions, 17 of 210 drawn households are now Scottish, and the region it admitted is the only one whose heating mix was measured rather than shaped

**Measured 2026-09-07 in the shared tree.** Claim
`W2_18-the-curriculum-region-marginal-is-england-and-wales`. R13 fidelity change to the curriculum
— named, versioned, decided blind to any company result.

## What was wrong

`docs/design/segmentation_curriculum_v1.json::region_marginal_synthetic_acquisitions` was an
England-and-Wales distribution normalised to 1.0 over ten regions. Its own basis line named the
scope, and it inherited that scope from the census join that dropped Scotland at the region LABEL —
measured and fixed in `d331c255c`, since when the siting frame has covered all eleven regions and
sited nobody in the eleventh. The frame's own manifest said so in a field nothing read:
`regions_the_curriculum_does_not_draw: ["Scotland"]`.

The omission is **biased, not merely absent**. Scotland is 9.19 % of GB households, so every other
region was overstated by a factor of 1.1012, and it is the cold, windy end of GB — the drivers
W1_14's weather cells exist to carry.

## The number was a question to research, and the answer was already in the repo

Nothing was picked. `tools.weather_cell_weights.read_households()` already merges Census 2021 TS041
with Scotland's Census 2022, and `tools.household_siting_frame.region_namer()` already labels all
eleven regions since `d331c255c`. Composing the two answers the question exactly:

| | output areas | households |
|---|---|---|
| England & Wales (TS041) | 188,880 | 24,783,304 |
| Scotland (Census 2022) | 46,363 | 2,508,542 |
| **GB** | **235,243** | **27,291,846** |

**Every output area places; zero unplaced households.** Shares sum to 1.0 at 6 dp with no residual.

| region | share | | region | share |
|---|---|---|---|---|
| South East | 0.139525 | | South West | 0.089733 |
| London | 0.125454 | | West Midlands | 0.089019 |
| North West | 0.115543 | | Yorkshire and The Humber | 0.085398 |
| East | 0.096323 | | East Midlands | 0.074652 |
| **Scotland** | **0.091915** | | Wales | 0.049360 |
| | | | North East | 0.043078 |

The value it replaced was a **transcription with no caller** — nothing could re-run it, so nothing
could notice its stated scope had stopped matching the frame underneath it. It is now
re-derivable: `tools.household_siting_frame.census_region_household_shares()` recomputes exactly
these eleven figures and **fails closed** on any output area the labeller cannot place, rather than
normalising over whatever placed. Silent renormalisation is the shape that hid Scotland for seven
weeks.

## The interconnection: admitting a region is not the same as modelling it

`population_draw.heating_fuel_weights_for_region` fails OPEN —
`_HEATING_FUEL_TILT_BY_REGION.get(region, {})` hands back the national shape for any region with no
row, silently. Admitting Scotland and stopping there would have moved the bias rather than removed
it, and the existing sum-to-one control passes either way (**proved, below** — it survives the
poison that kills the new one).

So the tilt was measured, not shaped. Scotland's Census 2022 **UV407** (central heating by output
area) is already inside the pack `weather_cell_weights.pull_scotland` caches. Banded to the seven
levels over the 2,456,487 households with central heating (its "All occupied households" total is
2,508,542 — the same figure as the household join, so it is the same census):

| level | Scotland | national shape | tilt |
|---|---|---|---|
| mains_gas | 0.7499 | 0.74 | 1.013 |
| mixed | 0.0626 | 0.09 | 0.696 |
| electric | 0.0922 | 0.08 | 1.152 |
| **oil** | **0.0519** | 0.02 | **2.597** |
| **lpg_bottled** | **0.0135** | 0.005 | **2.709** |
| heat_network | 0.0055 | 0.03 | 0.185 |
| other_offgas | 0.0243 | 0.035 | 0.695 |

Defaulting Scotland to the national shape would have understated its oil at 2.0 % against a measured
5.2 %, and its bottled gas at 0.5 % against 1.35 %. Note the tilt runs **both ways**: communal heat
is 0.55 % in Scotland against a London-inflated 3.0 % national shape, so a table written to make
Scotland uniformly off-gas would also have been wrong.

## The book at real inputs

`draw_population(base_seed=7, acquisitions_per_year_lambda=40.0, draw_region=True)` — 210 households:

- **17 Scottish (8.10 %)**, against 0 before and a 9.19 % marginal (sampling, n=210).
- **210 / 210 sited**, 0 unsited Scots. The frame already held the coordinates.

## Controls, and the poison round that says they can fail

Two new controls in `tests/simulation/test_population_draw.py`, both over COMMITTED artefacts (no
census cache on either side, so neither can pass vacuously in a clean extract):

| poison | control | outcome |
|---|---|---|
| drop the Scotland fuel row (region falls to the national shape) | `test_scotland_is_not_drawn_on_the_national_heating_shape` | **KILLED** |
| the same poison | incumbent `test_heating_fuel_weights_sum_to_one_for_every_region` | **SURVIVED — blind, as its docstring now says** |
| revert the marginal to the ten E&W regions | `test_the_region_marginal_draws_exactly_the_regions_the_committed_frame_can_site` | **KILLED** (`sited-not-drawn {'Scotland'}`) |
| the frame drops Wales instead (the OTHER side moving alone) | same control | **KILLED** (`drawn-not-sited {'Wales'}`) |
| baseline, unpoisoned | both new controls | **SURVIVED** |

The region control is keyed to the property (the two region sets are one set), so it fires on either
side moving alone and stays green when both are rebuilt together. The fuel control is keyed to the
measured DIRECTION, not to today's multipliers: re-measuring the tilts keeps it green, dropping the
row makes every share exactly the national one and no strict inequality survives.

## Two things this leaves open, named rather than absorbed

1. **Scotland is now the only region whose fuel mix is measured; the other ten are documented
   shapes.** That is the better direction to be inconsistent in, but it is an inconsistency and the
   code says so where it lives. The reason is not a judgement: **TS046 is not in the cache pack** —
   `weather_cell_weights` pulls TS041 (households) and Scotland's topic zip, and the England-and-
   Wales heating table would need a new nomis pull. That pull would let all ten be measured the same
   way, and is the follow-on.
2. **A concurrent lane holds `simulation/weather_cell_siting.py` dirty with a `FRAME_SCOPE` constant
   asserting the curriculum draws no Scottish region**, and an uncommitted control
   `test_the_frame_covers_exactly_the_regions_the_curriculum_can_draw` that asserts
   `FRAME_SCOPE[1] not in curriculum`. Neither exists at HEAD. **This change makes both false**, and
   in the good direction: their equality leg (`frame_regions() == curriculum`) is red at HEAD today
   because the frame holds eleven and the marginal held ten, and it goes GREEN with this. Their
   `not in` leg and the FRAME_SCOPE prose are keyed to today's answer — Scotland absent — and are
   the thing to rewrite, not this. Left untouched on purpose: editing a file another lane holds
   dirty would carry their work inside mine.

## Landed

`docs/design/segmentation_curriculum_v1.json` · `tools/household_siting_frame.py`
(`census_region_household_shares`) · `simulation/population_draw.py` (the Scotland tilt row) ·
`sim/household_siting/region_household_frame.json` (the derived `regions_the_curriculum_does_not_draw`
field, now empty — recomputed by hand from an eleven-region `want` against an eleven-region `rows`,
which is the whole of what `build()` computes for it) · `tests/simulation/test_population_draw.py`.
