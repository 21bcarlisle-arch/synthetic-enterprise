# What EP13 established about GB grid carbon intensity

**Knowledge:** none -- no knowledge page covers grid carbon intensity yet; carbon-price is the allowance price, a different quantity

*Written 2026-10-05, when `EP13_adapter_carbon_intensity` was parked. Director, 2026-10-05: "Don't
lose EP13's findings — the interconnector and biomass work is real knowledge. Write it up, park
the atom, and we'll return to it if first-principles carbon is ever needed." The product now takes
carbon from NESO's published series instead (atom G14).*

EP13 rebuilt GB half-hourly grid carbon intensity from first principles: demand, a dispatch stack,
coal, biomass, pumped storage, interconnectors and embedded generation. It graded the result against
NESO's published national series. Between 2026-08-14 and 2026-10-05 it ran 43 numbered steps. The
record ends at s43 (`3e7236f43`, 2026-10-05 00:26).

This page gathers what those steps found, by finding. The full narrative is
`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` (§0–§43). The compact state is the
`level_hold_note` in `docs/design/simplifications/EP13_adapter_carbon_intensity.yaml`. Three
sourced research files sit beside this one:

- `neso_carbon_intensity_interconnector_treatment_2026-10-04.md`
- `gb_biomass_fleet_by_support_scheme_2026-10-04.md`
- `drax_biomass_cost_and_the_ro_switch_2026-10-04.md`

Each claim below is marked:

- **[measured]**: a run on real published data, recorded in the commit or frame section cited.
- **[sourced]**: read from a published document, cited.
- **[inferred]**: reasoning from measurements, not tested on its own.
- **[open]**: not established.

---

## How to read the numbers

- **The shape.** The reconstruction (`sim/grid_carbon_intensity.py`) gives each half hour's
  emissions rate relative to the year's demand-weighted mean. It is dimensionless and never in
  grams. It is compared with NESO's series, which is renormalised the same way over the half hours
  both series cover (`sim/neso_carbon_intensity.compare_shapes`).
- **Correlation.** Half-hourly correlation of the two shapes, by year.
- **Within-day and between-day "overstated by".** The model's standard deviation divided by
  NESO's, on two axes. Within-day removes each day's mean. Between-day is the spread of the day
  means. Above 1.0, the model swings too wide. Within-day is the only axis a household can act on.
- **p95/p5 and max/min "overstated by".** The model's spread ratio over NESO's. These are two
  different statistics, and they have often moved in opposite directions. Both are always quoted.
- **Wind deciles (from s31).** Days are ranked within each year by wind share: (transmission wind
  + embedded wind) / (INDO + embedded). D1 is the calmest tenth and D10 the windiest.
- **The crossing conditions.** A half-hourly metered fuel may be handed to the dispatch only if
  two things hold. (1) NESO's own factor for that fuel is exactly zero. (2) Its outturn is never
  negative, which separates an availability from a dispatch decision. A fuel that fails either
  crosses only as annual scalars. Otherwise the reconstruction becomes NESO's arithmetic with a
  different cache (module docstrings of `sim/grid_carbon_intensity.py` and
  `sim/elexon_fuel_outturn.py`).

**Most figures before s19 (2026-09-30) were measured on a model with three input definition
errors** (finding 3). They are true of that model and not of the grid. Correlation in 2024 was 0.726
then and 0.972 at the end.

---

## 1. What NESO's published series is, and what its methodology does

- **[sourced]** The source is NESO's *Carbon Intensity Forecast Methodology*, last revised
  2021-09-24. Imports use a daily factor: each connected country's previous-day ENTSO-E generation
  mix with Table 1's fuel factors applied. Table 1's import rows (French ~53, Dutch ~474, Belgium
  ~179, Irish ~458 gCO2/kWh) are only defaults for when ENTSO-E is down. The live
  `/intensity/factors` endpoint (fetched 2026-10-04) has French, Dutch and Irish rows. It has no
  Norway or Denmark row, and no longer has Belgium. (`f4f80688d`, s33)
- **[sourced]** Table 1's generation factors, as carried in
  `elexon_fuel_outturn.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH`, in gCO2/kWh: coal 937, oil 935,
  OCGT 651, CCGT 394, other 300, biomass 120. Nuclear, hydro, pumped storage, wind and solar are 0.
- **[measured]** NESO's generation mix is FUELHH. NESO's `/generation` gas/nuclear ratio matches
  Elexon FUELHH (CCGT+OCGT)/NUCLEAR to the third decimal place in every month of 2022 and 2024.
  (s33) So NESO's "actual" is itself a model built on the metered mix through a factor table. It is
  not independent of FUELHH inputs.
- **[sourced; corrected 2026-10-05 by measurement]** NESO's methodology says the series is
  loss-corrected to a consumed basis. Its data matches that only until 2020-04-27 period 34; from
  then it is generation basis (G14 knowledge page, "The 2020-04-27 step"). It is published half-hourly from
  2018-05-11, with a forecast and an actual on each half hour. The 14 regional series are modelled
  from a reduced network model, not measured. (`sim/neso_carbon_intensity.py` docstring)
- **[measured]** Feed defects:
  - NESO publishes `actual: 0` for five half hours, four of them consecutive on 2023-06-07. The
    lowest genuine reading is 14 g. These are outages, not a clean grid.
  - The forecast field carries six 2019 half hours above any physical grid (13,579 gCO2/kWh among
    them). The adapter refuses values above Table 1's coal factor of 937, on both forecast and
    actual. (`ece37bfbd`)
- **[measured] NESO's forecast against its own actual** (`28eaca4c9`, §13;
  `tools/ep13_peer_bound.py`):
  - The forecast correlates 0.965–0.979 with the actual over 2019–24.
  - A persistence copy of the outturn (2019, 2021 and 2024 tabulated) scores 0.992–0.994 at a
    30-minute lag, 0.973–0.979 at one hour and 0.53–0.63 at one day. So the forecast is worth about a one-hour persistence model
    (1.99–2.29 half hours).
  - Because forecast and actual share NESO's factors and inputs, this bound overstates what an
    outside reconstruction could reach. **[inferred]**
- **[measured] What following the forecast is worth** (`ece37bfbd`). Over 2019–24, rank each day's
  half hours by NESO's forecast, take the cleanest six, and score them on outturn. That captures a
  mean 0.858 of the day's achievable within-day saving: median 0.909, p5 0.554. On 7 of 2,165 days
  it was dirtier than not shifting. This is a ceiling on any shifting advice. No better
  reconstruction can recover it.
- **[measured] Across 2019–24, NESO's own clean end falls and its spread widens.** The minimum
  relative half hour goes 0.217 → 0.105, and max/min goes 9.3x → 21.6x. (`ee6dd4fd2`)
- **NESO's denominator, as EP13 read it [inferred from definitions, consistent with
  measurement].** INDO is transmission demand. It is net of embedded wind and solar, and it
  excludes exports. NESO's intensity is per kWh consumed, so the denominator carries embedded
  solar and embedded wind. On the target's own mix, cables outside NESO's mix are in neither the
  numerator nor the denominator (finding 2).

---

## 2. Interconnectors

### How NESO's series treats each cable [measured, s33 `f4f80688d`]

Method: NESO's imports share over its nuclear share must equal metered imports over metered
nuclear, whatever denominator NESO uses. Each cable's metered flow was regressed onto NESO's implied
import MW, month by month, over 2022 and 2024.

| cable | in NESO's mix? | evidence |
|---|---|---|
| North Sea Link (Norway, `INTNSL`) | **yes** | coefficient 0.55–1.12, mostly 0.95–1.11, in all 24 months |
| Viking Link (Denmark, `INTVKL`) | **no** | coefficient 0.00–0.22 |
| ElecLink (France, `INTELEC`) | **no** | coefficient 0.00–0.45 |

"All cables but Viking and ElecLink" fits the imports/nuclear ratio at MAE 0.040–0.119 in 2024.
"All nine cables" fits at 0.211–0.436. The prediction had been that NSL and Viking were both in. It
was half refuted, and ElecLink's absence was not predicted.

### What factor NESO gives North Sea Link

- **[measured]** It is low, not like gas. In a pooled fixed-factor fit of NESO's actual, MAE is
  lowest at 0 g and rises steadily: 2024 gives 6.17 g at 0, 7.26 g at 120 and 10.93 g at 394 (GB
  CCGT). A joint fit puts NSL at 23–36 g, but the cable coefficients are collinear (IFA2 comes out at
  −62), so that is not a number. (s33)
- **[sourced]** Statistics Norway table 08307 gives Norway's annual mix. Thermal is 1.03–1.73% of
  production over 2020–25. Table 1 applied to it gives NSL **1.2–6.8 gCO2/kWh**. The range is a
  bracket between treating Norwegian thermal as biomass (120) and as CCGT (394). The shipped end is
  the high one, 4.0–6.8 g by year. (`a65a705ca`, s35; table in
  `neso_carbon_intensity_interconnector_treatment_2026-10-04.md`)
- **[measured]** The bracket barely matters: correlation moves by <0.0001 and swing by up to
  0.0015. Pricing the cable at all moves correlation by about 0.01 in 2024. (s35)
- **[open]** NESO's actual daily figure needs Norway's ENTSO-E daily mix, which needs a token the
  box does not hold. The annual figure flattens Norway's seasonal thermal and ignores that NSL lands
  in bidding zone NO2. Whether NESO changed either rule in 2025 is also open.

### The calm-day gas excess was the unpriced Norway and Denmark imports [measured, s32 `70dee3c7c`]

Before s34–35, NSL and Viking flow was served as GB gas, because the factor table had no row for
them. An identity split the model's gas minus metered CCGT+OCGT into coal, biomass, pumped
storage, unpriced imports, OIL+OTHER and the INDO residual. It closes to 0 MW at D1 in every year.

| year-mean, MW | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| gas gap (model − CCGT+OCGT) | +146 | +99 | +363 | +697 | +1,018 | **+1,549** |
| unpriced imports served as GB gas | 0 | 0 | 172 | 531 | 1,034 | **1,702** |
| priced share of imported MWh | 1.00 | 1.00 | 0.95 | 0.72 | 0.73 | **0.66** |

- **The level is the unpriced cables.** From 2021 the gap grows step for step with NSL plus Viking
  flow, and in 2023–24 that flow exceeds the whole gap.
- The feed quoted import coverage as 0.84 over the whole series. That figure reads small exactly in
  the years where the hole is large.
- The cables also import harder on calm days, so they join the calm-to-windy gradient from 2023:
  −501 and −523 MW of D10−D1 in 2023–24.

### What changed when the cables were treated as NESO treats them

- **s34 (`7f193c3bb`).** Viking and ElecLink became `unmixed_import_mw`: served before the stack,
  carrying no tonnes, and out of the denominator. No factor was needed.
  - 2024 correlation 0.959 → 0.962.
  - 2024 within-day and between-day both went 0.93 → 0.97.
  - Headline p95/p5 worsened, 1.13 → 1.15x.
  - **[measured]** ElecLink's metered flow starts 2021-09-18, not in 2022. The
    `elexon_fuel_outturn` docstring still says "ElecLink (France, May 2022)".
- **s35 (`a65a705ca`).** NSL priced at Norway's mix.
  - Correlation 2021–24 is 0.970–0.982, at or above the 0.97 peer bound. 2024 went 0.962 → 0.972.
  - Import coverage is 1.0 in every year.
  - The shape now swings **too wide in every year**: between-day 1.01–1.11. Headline p95/p5 went
    1.15 → 1.22x.
- **[measured] Two blockers hid each other.** Serving 1.7 GW of imports as gas damped the 2023–24
  swing, so those years read as under-swung while 2019–20 read as over-swung. With the hole closed,
  the error has one direction in every year. (s32, s35)
- A 2026-08-25 test had dismissed the hole as immaterial (2024 correlation 0.726 → 0.737). That was
  true of the model then. On the corrected model the hole is worth +0.014 at its clean bracket end.
  (s32)

### Import factors as shipped

- French, Dutch, Irish and Belgian cables use Table 1's defaults. **[inferred]** This is not NESO's
  daily ENTSO-E rule, which the record did not reproduce.
- NSL uses Table 1 × SSB's annual mix.
- Viking and ElecLink carry no factor and sit outside the mix.

---

## 3. The input definitions: what the 2024 "decay" actually was

From August to September, correlation in 2024 sat at 0.726–0.746, and four bound instruments said
no dispatch model on those inputs could do better (finding 9). The fault was in how three inputs
were defined. **[measured]**

| step | correction, decided on INDO's published definition before the run | effect |
|---|---|---|
| s18 `7aa39b17a` | diagnosis: with all FUELHH fuels fetched, the residual error splits into solar subtracted twice (2019–21, ~1.3 GW of gas a year), exports invisible (2022, 0.45 of the variation) and a short wind input (2023–24, 0.70 then 1.02) | — |
| s19 `295e9ad64` | embedded solar out of the residual and into the denominator (INDO is already net of it) | gas +1.1–1.3 GW every year; 2016–18 within ±80 MW of metered CCGT; within-day mean 1.45 → 1.26x |
| s20 `0993677cd` | exports added to both the residual and the denominator (INDO excludes them) | 2022 correlation 0.908 → 0.940 |
| s21 `9aef02ba4` | residual subtracts transmission-metered FUELHH `WIND` in place of AGWS | correlation 0.93–0.97 in every year 2019–24; 2024 0.720 → 0.955; 2023 0.807 → 0.969 |

- **[measured] Elexon's AGWS (B1630) wind series is short.** AGWS offshore is 0.52–0.70 of DESNZ
  ET 6.1 offshore generation in every year 2016–24. AGWS total wind in 2023 was 51.7 TWh, below
  transmission-metered wind alone (63.4 TWh). DESNZ puts all GB wind at 82.8 TWh. A live re-fetch
  of one 2023 week agreed with the cache within 2%, so the gap is between two published series and
  not in our walk. FUELHH `WIND` agrees with DESNZ. (s18, s21)
- **[open]** Why B1630 under-reports: missing BM units, or a psrType mapping. It was put to the
  director as a practitioner question on 2026-09-30.
- **[measured] Shared inputs carry most of the correlation.** A null with no merit order keeps
  every shared input and burns the whole residual at one gas factor. It reaches 0.92–0.97. So
  correlation no longer grades the merit order. The swing ratios do. (s22 `999b87b14`)

---

## 4. Embedded generation

- **[measured]** NESO's published embedded wind and solar (`sim/neso_embedded_generation.py`, NESO
  CKAN) are estimates from capacity registers and a weather model, not meter reads.
- **As a within-day timing input, embedded generation was retired** (`d636b19ed`, 2026-08-28). An
  oracle holding the true embedded series scored below the day-mean placebo out of sample in all six
  years (−0.0040 to −0.0912), at every resolution from 48 to 600 cells. **[measured on the pre-s19
  model.]** The artefact was regenerated after s34 and s35, and its oracle headroom stays negative
  in every year (2024: −0.083 after s35).
- **As a denominator term, it is owed by NESO's definition.** s26 (`3b4a12a9a`) added NESO's
  embedded wind beside embedded solar. Within-day became 0.94–1.11x (mean 1.02) and between-day
  0.95–1.12x, so the between-day swing became too wide in 5 of 6 years.
- **[measured] It is the timing of embedded wind, not its size, that carries the between-day
  overshoot** (s29 `d647798e0`). Holding NESO's embedded wind flat at its year mean moves
  between-day by ≤0.012. Putting the energy on the right days moves it +0.05 to +0.09. Metered
  transmission wind scaled to the same energy reproduces NESO's between-day to 0.008. So NESO's
  weather model has the timing right.
- **[measured] NESO's embedded wind is not too large** (s30 `26c63f7c7`). It is 0.80–0.94 of
  DESNZ-implied embedded wind (ET 6.1 total wind minus FUELHH transmission wind) over 2019–24.
  **[open]** ET 6.1 is UK-wide and includes Northern Ireland. NI wind is not in the knowledge layer,
  so the 114–434 MW gap cannot be split between NI and a GB shortfall.

---

## 5. Pumped storage

- **[measured]** Pumped storage fails condition 2, because it goes negative when it pumps. So only
  annual scalars may cross into the dispatch. (s24, s25)
- **[measured] It was the missing fleet behind the within-day over-swing** (s24 `e1fcee749`).
  - Pumped-storage generation taken off the residual lowered within-day by 0.043–0.048.
  - Pumping added as overnight load (about 1 GW) lowered it a further 0.10–0.11, about five times
    the 0.01–0.03 predicted.
- **[measured] It is built as a daily water-fill from four annual scalars**: mean and largest
  generation, and mean and largest pumping (s25 `b16412024`).
  - The fill recovers 115–129% of the measured-PS oracle's within-day cut. Perfect foresight of
    the day's residual flattens the day more than GB's fleet did.
  - The fill was chosen on timing: its half-hourly correlation with measured PS is 0.67–0.81,
    against 0.54–0.69 for a rectangle.
- **[measured] Pumped storage is not the between-day cause** (s28 `50701e00d`). With measured PS,
  2020 between-day stays at 1.10. The rule's even daily energy split costs 0.007–0.017 of
  between-day.

---

## 6. Biomass

### The fleet by support scheme [sourced and measured, s37 `8e22fed43`]

| unit | capacity (Elexon) | scheme |
|---|---|---|
| Drax 1 | 665 MW | CfD from 2016-12-21 |
| Drax 2, 3, 4 | ~1,975 MW together | RO. Unit 4 converted Aug 2018, under a 125,000 ROC/yr station cap |
| Lynemouth | 3 × 140 MW | CfD, strike £105/MWh (2012 prices) |
| Tees REP | 285 MW | CfD, from 2023 (secondary source only) |
| Wilton 10, Rothes | 182 MW, 86 MW | RO, not confirmed against the Ofgem register |

Together these units are 0.90–0.98 of FUELHH BIOMASS. Sources are in
`gb_biomass_fleet_by_support_scheme_2026-10-04.md`.

### The calm-day biomass excess, and who carries it

- **[measured]** Metered biomass runs higher on calm days than windy ones in 6 of 6 years. FUELHH
  D1−D10 is +361 / +1,122 / +314 / +727 / +366 / +1,021 MW (2019–24). A flat block at the year mean
  therefore under-serves calm days and over-serves windy ones. In the s32 decomposition this is the
  largest gradient term in 2020, 2022 and 2024, around −1.0 GW in 2020 and 2024.
- **[measured] Drax's RO units carry it.** Calm days cluster in summer, the outage season, so
  deciles were taken within each calendar quarter (post-hoc, not pre-registered). On that basis
  Drax 2–4 carry 0.39 / 0.89 / 0.57 / 0.85 / 0.86 / 0.96 of the calm-day gap over 2019–24.
  Lynemouth carries about none in every year. Drax 1 carries 31–108 MW, except 220 MW in 2021.
- **[open]** In 2019 the listed units miss most of the metered gap (−50 of +361 MW on year
  deciles). The unit carrying 2019's calm-day biomass is not identified. The BM-unit-to-Drax-unit
  mapping is an assumption, consistent with the data.

### The support scheme is not the mechanism [sourced, s37]

- **The earlier premise was wrong.** Through s36, EP13 carried "a CfD plant runs on availability".
  The contract does not say that. Biomass CfDs settle against a season-ahead baseload market
  reference price, so a CfD unit earns the day's price plus a constant, as an RO unit does.
- When the market runs above the strike, the CfD constant is negative. Drax held unit 1 back in
  2022–23: mean output 440 → 260 → 129 MW.
- **[measured]** The RO flex runs 177–945 MW by year on flat capacity. Its size is economic, so a
  capacity rule cannot carry it.

### The price switch, and how it moves by year [measured, s38 `f78925e65`]

Drax 2–4 daily output, demeaned by calendar month, binned by Elexon's daily MID:

| year | where output falls off |
|---|---|
| 2019 | no day cheap enough to show a switch (lowest bin £20–30) |
| 2020 | ~£20 |
| 2021 | ~£55 |
| 2022 | ~£125 |
| 2023 | ~£75, graded rather than a step |
| 2024 | ~£55 |

- A switch exists and moves by year, roughly as a fuel cost would.
- How far windy days sit below it does **not** explain the size of the flex: pre-registered rank
  correlation 0.09, post-hoc 0.54, with 2020 the outlier. So "flex size = how far days straddle a
  step" is refuted.
- The response is graded, so a rule would need a supply curve.
- Unit 4's ROC cap does not raise its switch.

### What Drax's published cost grades [sourced, s39 `d2d8a4d82`]

- **[sourced]** Drax publishes a biomass cost in £/MWh only for 2019 (c.£75–80, Capital Markets
  Day) and 2023 ("over £100/MWh", a December 2022 forecast). Other years give pellet production
  cost in $/t FOB, which is not a cost per MWh generated. The ROC buy-out is in the commons (£48.78
  in OY2019 to £64.73 in OY2024). **[open]** The ROC recycle value is unsourced, so buy-out is only
  a lower bound.
- **2019 is the only year that can be graded.** Fuel minus buy-out is at most £26–31. That is
  consistent with no visible switch, but it is not a test. 2020–24 are ungraded.
- **[sourced] In 2022 Drax names a different mechanism.** Its FY2022 results describe buying back
  first-half positions, reprofiling to the second half, and selling biomass on a high spot market.
  So the switch was an opportunity cost (resale or later-half value), not contract cost.
  - **[measured]** Drax 2–4 output, second half minus first, was largest in 2022 (+306 MW). That is
    only 66 MW above 2021, so it is consistent with Drax's account and does not isolate it.
- So a rule that locates the switch at "fuel cost minus ROC" would carry an honest `None` in 5 of
  6 years. In 2022 it would be the wrong quantity even with the data.

### Biomass dispatch rules that were tried and refuted

- **Perfect biomass knowledge** (`e9faadece`, §10, pre-s19 model) was worth −0.005 of
  correlation. 70–86% of the fleet's variance is between days, not within them. This retired the
  outage model.
- **[measured] An envelope rule runs bang-bang** (s36 `47d2d8d88`). The rule was a year-long
  water-fill on the residual, between the fleet's observed minimum and maximum, with the mean
  conserved.
  - It sits at capacity about half the year and at the outage-set floor about a third.
  - Its calm-windy gradient is 2.2–8x the meters'.
  - Every year swings too narrow (0.83–0.97), and correlation falls 0.009–0.019.
  - The floor is set by outages: 50–383 MW against means of 1.5–2.2 GW.
- **[measured] The fleet follows the residual more closely than the price** (s40 `59b6f79f6`).
  Metered biomass correlates daily 0.37–0.58 with the residual and 0.01–0.48 with MID. A year's
  absolute MID ranks months by gas cost before it ranks days by scarcity. The same rule ranked by
  MID tracks the meters worse in 6 of 6 years. Its near-1.0 swing came from a near-random order and
  is not progress.
- **What ships:** a flat block at each year's measured FUELHH mean, 1.5–2.2 GW over 2019–24. The
  earlier constant was 2,400 MW. (s27 `d793553e1`)
- **[open]** What sets the flex amplitude by year. EP13 parked the biomass gradient on it.

---

## 7. Coal

- **[measured] The shipped merit order serves almost no coal** (s41 `1ae9bfa69`).
  - Coal is served only above `CCGT_CAPACITY_MW` = 30,000 MW of thermal
    (`sim/merit_order_reconstruction.py`). The model's thermal sat a median 14.4–21.7 GW below that
    whenever metered coal ran.
  - So the model serves 0–3% of metered coal in every year: 19 MW against 652 MW in 2019, and about
    0 after. `coal_capacity_by_year` crosses, is tested, and moves nothing. It is a dead dial.
  - The code comment calling the mis-ordered half hours "few and small" was corrected beside the
    claim.
- **[measured] How real coal ran, 2019–24:**
  - More than 50 MW in 36–60% of half hours.
  - 2.0–8.5x higher on calm days than windy ones. Even on the windiest decile the fleet kept
    93–313 MW running.
  - 4–5x higher by day than overnight in 2019.
  - 0.65–0.91 of its energy fell in October–March. 2021 and 2022 ran through the summer, which is
    the gas price and not the season.
  - When coal ran, metered gas was a median 8.1–14.9 GW.
- **[measured] Coal was not a peaker, and forcing it to be one makes every year worse** (s42
  `12f142775`). Coal was placed at the top of the model's own thermal stack, with the right annual
  energy (solved level 15.0–18.6 GW of model thermal).
  - Correlation fell in every year, by 0.007–0.021.
  - Between-day went from 1.01–1.11 to 1.13–1.27, and headline p95/p5 from 1.22 to 1.45.
  - The model ran coal in 11–25% of half hours, against the meters' 36–60%, and never on a windy
    day.
- **[measured] A flat block at the year's mean is too flat** (s41 arm F). Between-day goes to
  0.95–1.04 and p95/p5 to 1.06, but correlation falls 0.005 in 2019–20.
- **[measured] Only coal's monthly timing helped** (s41 arm M). It lifts 2020 correlation .931 →
  .953 and cuts MAE .104 → .077. But it reads monthly metered energy, which condition 1 refuses, so
  it is an oracle and not a build.
- **[superseded by s43]** s41–s42 inferred that coal's within-year timing is a price question
  (gas–coal switching). s43 tested that and refuted it.
- **[measured] Coal's month follows demand, not the coal–gas price** (s43 `3e7236f43`).
  - Input: the World Bank Pink Sheet's monthly Richards Bay coal and TTF gas, run through the tree's
    own `coal_srmc_gbp_per_mwh` and `ccgt_srmc_gbp_per_mwh`. It passes condition 1, because a traded
    index has no NESO term.
  - In 2017–22 the price gap ranks coal's months at 0.01–0.78. Demand ranks them at 0.60–0.94.
  - Where price and demand part (2018, 2021, 2022), the price explains nothing (0.01–0.03). The
    years where the price looks right (2017, 2019, 2023) are years where the price itself tracks
    demand (0.69–0.82).
  - Pooled over 108 months (2016–24), Pearson(gap, coal load factor) is −0.04.
  - Newcastle coal in place of Richards Bay changes no verdict.
- **[measured] At monthly grain, the switch has no variation to time coal with** (s43).
  - Coal was out of merit against fleet-average CCGT in every month of 2019–20. It still ran
    2.0–2.4 GW in January and almost nothing in summer.
  - It was in merit in every month of 2022, and still ran from 9 MW to 990 MW by season.
  - So s41's monthly oracle helps because it carries the season, not the price.
- **[measured] 2024 shows a closure, not a price** (s43). Coal ran at 0 MW from October 2024, after
  Ratcliffe closed. The annual `coal_capacity_by_year` cannot see that, so every arm that sizes coal
  by year serves coal in Q4 2024.
- **[measured] An instrument gap: the tree's UK ETS series is a named gap for 2022–24** (s43). There
  `carbon_price_total_gbp_per_tonne` returns Carbon Price Support alone (£18/t), so a price arm's
  sign cannot be graded in those years.
- **[measured] A monthly coal block narrows the swing a household acts on, and does not ship** (s43
  arm R). The block was flat within each month, shaped by the model's own monthly thermal, with the
  annual mean conserved.
  - Correlation moved −0.002 to +0.001.
  - Between-day, headline p95/p5 (1.22 → 1.07) and MAE improved.
  - Within-day fell below truth in 4 of 6 years (2021: 1.00 → 0.90; 2022: 1.00 → 0.93).
  - The block runs coal in every half hour, against the meters' 36–60%.
- **[open] Coal's within-day shape.** The flat block (F), the monthly block (R) and the top-fill
  (L) all fail. F and R run coal always on, and L runs it as a peaker. The meters show neither: coal
  ran in 36–60% of half hours and kept 93–313 MW on the windiest days. No annual or monthly scalar
  held has located it.
- **[measured, s17 `365c03341`]** On the pre-s19 model, coal carried 0.93 of the daily gas-level
  error in 2017 and 0.77 in 2018, and about 0 by 2023. s41 shows this was the dead dial.

---

## 8. The residual shape errors the dispatch model could not close

### Where the shipped shape ended (s35 state; s36–s43 changed nothing shipped)

| 2019–24 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| correlation | 0.959 | 0.931 | 0.970 | 0.982 | 0.978 | 0.972 |
| within-day overstated by | 1.06 | 1.10 | 1.00 | 1.00 | 1.02 | 1.07 |
| between-day overstated by | 1.05 | 1.11 | 1.01 | 1.07 | 1.07 | 1.07 |

Headline p95/p5 is 1.22x and max/min 1.21x. 2024 MAE is 0.089. **The shape swings too wide in every
year**, so any time-shifting benefit read from it is an upper bound. That is the sentence
`tools/generate_grid_intensity_feed.ERROR_DIRECTION` carries.

### Named errors

- **[measured] Windy days come out too clean, in every year** (s31 `a5c8c4509`). The model shape
  over NESO's falls from D1 to D10 in all six years. D10−D1 is −0.211 in 2020 and −0.017 to −0.093
  elsewhere.
- **[measured] In gas MW, the error is too much gas on calm days, not too little on windy ones.**
  Before s34–35, the model ran +0.4 to +2.1 GW above metered CCGT+OCGT on D1. On D10 it was within
  0.8 GW either side. In 2019–22 D10 ran below metered gas, by 758 MW in 2020.
- **[measured] The calm-to-windy gradient is mostly biomass and coal**, and the split changes by
  year (s32):

  | D10 − D1 gas-gap terms, MW | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|
  | biomass (flat block vs timed fleet) | −279 | **−1,051** | −305 | −683 | −337 | **−1,032** |
  | coal | −329 | −224 | **−601** | −393 | −211 | −97 |
  | unpriced imports | 0 | 0 | +145 | −153 | **−501** | −523 |
  | pumped storage | −124 | −162 | −120 | −144 | −203 | −277 |

- **[measured] OIL+OTHER is a level, not a mechanism.** It runs 0.07–0.43 GW, nearly flat across
  deciles. The model has no such fleet.
- **[measured] The INDO residual is a constant −0.6 to −0.7 GW.** Metered supply exceeds INDO by
  about that much on every kind of day. **[inferred]** That is station load and pumping, which are
  outside INDO's definition.
- **[open] Why the windiest decile ran short of metered gas in 2019–22.** One industry reading is
  that transmission constraints curtail wind north of the boundaries while gas runs south of them.
  Constraint volumes are not in the knowledge layer. (s31)
- **[open] Coal's within-day shape and biomass's within-year timing.** Every rule built from annual scalars on the
  model's own residual came out bang-bang (s36, s42). The real fleets sit between "always on" and
  "only at the top", and no annual scalar held says where.
- **[open]** Whether the within-day spread is right in 2019–20: it is 1.06–1.10, with no NSL in
  those years.

### Thermal floor and must-run

- **[measured] The thermal floor** (2026-08-25, module docstring). GB's thermal fleet never reaches
  zero. Before the floor, the model ran no thermal plant in 16.1% of 2024's half hours. The floor
  is now the CCGT+OCGT fleet's demonstrated annual minimum: 1,835 MW in 2016 falling to 303 MW in
  2024. The 1st percentile would be 1,720 MW in 2024, and it was not used because it is also the
  flattering statistic.
- **[measured] The must-run fleet** (2026-08-26, module docstring). FUELHH NUCLEAR+NPSHYD runs
  544–9,831 MW over 2016–25, mean 6,013 MW, against the old flat 8,000 MW. It passes both crossing
  conditions: zero factor, and 0 negative half hours in 175,212.

---

## 9. Where the timing information lives in the grid

These two results come from the pre-s19 model, but both are facts about NESO's series and the
metered mix.

- **[measured] The within-day timing in NESO's series is almost entirely in CCGT**
  (`d5303f115`, §14; `tools/ep13_per_fuel_oracle_bound.py`). Each fuel in the true mix was
  flattened to its day mean in turn. Flattening CCGT costs 0.052–0.095 of correlation over 2019–24.
  Coal costs 0.001–0.014 and biomass about 0.0003. Wind's cost collapses from −0.031 (2019) to about
  0 (2023–24).
- **[measured] The model already saw when gas runs** (`9dc0cd1fc`, §15). Its implied gas tracked
  metered gas within days at r = 0.807–0.870. Perfect within-day CCGT timing was worth at most
  +0.0485 (2024). In that model the error was the gas **level**. s17–s21 later traced that level to
  the input definitions (finding 3).

---

## 10. Three tables that disagreed by half (2026-08-14)

**[measured, `30e27aebb`]** Before EP13, the tree held three annual GB grid-intensity series. All
cited DESNZ, and they disagreed by up to 55.6% (2024: 196.1 / 126 / 181 g). They were reduced to one
owner, `company/regulatory/carbon_emissions.py::grid_intensity_g_co2e_per_kwh`, guarded by
`tools/grid_intensity_guard.py` (`5103f6fbf`). The reconstruction therefore publishes a
dimensionless shape and never grams.

**[measured, 2026-10-05]** The surviving owner was still the hand fuel-mix table x lifecycle
factors (196.1 for 2024). It now reads the annual level the grid-intensity feed publishes from
NESO's series (`annual_level`: demand-weighted, 133.1 for 2024 on the API; since the same day's
G14 rebase, the Historic Generation Mix, generation basis, 131.9), and the hand
table keeps only its `Low Carbon %` role. 2016 and 2025 have no whole-year level because Elexon's
demand record spans 2016-03-01..2025-06-07.

---

## If first-principles carbon is resumed

**Modules and their state**

- **`sim/neso_carbon_intensity.py`: sound.** It is the truth adapter, kept independent by an AST
  test. `compare_shapes` holds the within/between decomposition with unbalanced-panel weighting.
  `forecast_skill` returns annual aggregates only.
- **`sim/elexon_fuel_outturn.py`: sound.** It holds the FUELHH adapter, Table 1, the cable map,
  `OUTSIDE_NESO_MIX`, NSL's Norway factor, `coal_capacity_by_year`, `thermal_floor_by_year`,
  `biomass_envelope_by_year`, and a `--remainder` cache for WIND, PS, OIL and OTHER.
  - Stale: the docstring's "ElecLink (France, May 2022)". Metered flow starts 2021-09-18.
- **`sim/neso_embedded_generation.py`: sound.** It is the NESO CKAN adapter, with 2016–25 cached.
- **`sim/grid_carbon_intensity.py`: the shipped dispatch at the s35 state.**
  - Sound, by measurement: the input definitions (s19–s21, s26), pumped storage (s25), the cable
    treatment (s34–s35) and the year-mean biomass block (s27).
  - **Coal is a dead dial** behind the 30 GW threshold (s41).
  - Stale **[inferred from reading]:** several docstring paragraphs predate the later steps. One
    says "SINCE 2026-10-02 THE DIRECTION IS MIXED", another lists "the must-run floor is a constant
    8 GW", and another says "coal is now dispatched". `ERROR_DIRECTION` in
    `tools/generate_grid_intensity_feed.py` is current, so read that instead.
- **`sim/merit_order_reconstruction.py`.** It supplies emission factors and `CCGT_CAPACITY_MW` =
  30,000. `coal_srmc_gbp_per_mwh` exists, but no coal price series feeds it.
  - **[open]** Whether 30,000 MW is right as de-rated CCGT capacity (DUKES 5.11).

**Bound instruments (`tools/ep13_*.py`, artefacts in `docs/observability/`)**

- **Still sound, because they are facts about the target, not the model:**
  - `ep13_peer_bound`: NESO's forecast reaches 0.97, and the persistence ladder.
  - `ep13_per_fuel_oracle_bound`: CCGT carries the timing.
- **Measured on the pre-s19 model and not re-run since:** `ep13_input_ceiling`,
  `ep13_ccgt_swap_ceiling`, `ep13_ccgt_level_ceiling` and `ep13_biomass_oracle_bound`.
  - **[inferred]** Their verdicts bounded functions of inputs later found to be mis-defined (2024
    correlation 0.74 then, 0.97 now). Read them as history, and re-run them before citing any.
- **`ep13_embedded_generation_bound` was regenerated at s35** and is still negative in every year.

**Scratch.** The s23–s43 arm scripts lived in `/var/tmp/se-ep13-s*/` and are not in git. The frame
sections describe each arm precisely enough to rebuild it, and §17 embeds its script.

**The coal-price question is answered, and it was the wrong question** (s43 `3e7236f43`).

- The Pink Sheet monthly coal price is a fair input under condition 1.
- But it does not time GB coal: demand ranks coal's months better in every year 2017–22.
- So `coal_srmc_gbp_per_mwh` fed with a coal price is not the route to coal's timing.

**The first open question is now coal capacity by month, from published closure dates.**

- Closure dates are public facts about steel, so they need no condition-1 argument.
- Monthly capacity removes the coal every arm serves in Q4 2024, after Ratcliffe closed, and in
  each closure year's tail.
- Measure it on the shipped base shape, not on arm R's.

Behind it, in the order the record leaves them:

- coal's within-day shape (finding 7);
- the UK ETS gap for 2022–24 in the tree's carbon price series;
- the de-rated CCGT capacity;
- the ROC recycle value by year (Ofgem annual RO reports);
- the unit carrying 2019's missing biomass;
- Northern Ireland wind;
- GB constraint volumes;
- NSL's daily factor (needs an ENTSO-E token).

**The open question about the level bar.** L3 needs the reconstruction to "fail like reality", and
it now swings too wide in every year, which is a one-sided error. s13 also recorded that a lag-1
copy of the outturn scores 0.993 on correlation, so correlation discriminates weakly. Whether to
score a reconstruction on a statistic that autocorrelation does not dominate was left as the
director's call and never taken.
