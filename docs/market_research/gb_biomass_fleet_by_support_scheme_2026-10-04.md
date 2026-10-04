# GB transmission biomass by support scheme, and which units carry the calm-day excess

**Knowledge:** none -- no knowledge page covers grid carbon intensity yet; this anchors EP13's reconstruction (`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §37), which is where it is read

*2026-10-04. EP13 §36 found that biomass follows the residual only partly, and named the split by
support scheme as a knowledge item rather than a number to pick. This file is that item. Scratch,
the per-unit pull, the timestamped prediction and the outputs: `/var/tmp/se-ep13-s37/scratch/`.*

## The fleet the meters see

Elexon's BM unit reference (`/reference/bmunits/all`, read 2026-10-04) lists these units with fuel
type BIOMASS and a non-trivial generation capacity:

| BM unit | station | capacity (MW, Elexon) | scheme | source |
|---|---|---|---|---|
| T_DRAXX-1 | Drax unit 1 | 665 | **CfD** (FIDeR investment contract) since 2016-12-21 | Drax / EC state-aid decision ([renewablesnow](https://renewablesnow.com/news/ec-to-assess-cfd-for-645-mw-drax-biomass-plant-in-uk-508208/)); "Unit 1 operates under the CfD scheme" |
| T_DRAXX-2, -3 | Drax units 2, 3 | 669, 661 | **RO** (grandfathered) | same; converted 2013-2016 ([Drax, 2018-08-20](https://www.drax.com/press_release/drax-closer-coal-free-future-fourth-biomass-unit-conversion/)) |
| T_DRAXX-4 | Drax unit 4 | 645 | **RO**, converted August 2018, under a station cap of 125,000 ROCs a year | [Drax, 2018-08-20](https://www.drax.com/press_release/drax-closer-coal-free-future-fourth-biomass-unit-conversion/) |
| E_LYNE1-3 | Lynemouth | 3 x 140 | **CfD** (FIDeR), strike £105/MWh (2012 prices), converted 2018 | EC state-aid approval, Dec 2015 ([E&T](https://eandt.theiet.org/2015/12/01/state-aid-lynemouth-biomass-conversion-approved)) |
| T_TSREP-1 | MGT Teesside (Tees REP) | 285 | **CfD**, commenced 2023 per secondary reporting; full commercial operation delayed | [Wikipedia, Tees REP](https://en.wikipedia.org/wiki/Tees_Renewable_Energy_Plant) -- secondary, not confirmed against LCCC |
| T_WILCT-1 | Wilton 10 | 182 | RO (2007 build; not confirmed against the Ofgem register) | not established |
| E_MARK-1 | Rothes CHP | 86 | RO (not confirmed) | not established |

Drax BM unit number is read as Drax's own unit number. That is an assumption the data can check
(see below), not a published mapping.

## What the schemes say about dispatch -- less than §36 assumed

§10 and §36 carried "a CfD plant runs on availability". The contract does not say that:

- The biomass CfDs settle against the **baseload market reference price** (a season-ahead
  baseload price), not the day's price. So on any given day a CfD unit earns the day's price plus
  a fixed adder (strike minus BMRP). An RO unit earns the day's price plus the ROC value. **Both
  flex against the day's price with an additive constant.** Neither scheme makes a unit baseload by
  construction. Which one flexes more depends on the adder against fuel cost, not on the scheme name.
- When the market runs above the strike, the CfD adder is NEGATIVE, and running costs the unit
  money it must pay back. Bloomberg reported that Drax "lowered production at Unit 1 for weeks at a
  time" in winter 2022-23. Drax said it kept the CfD unit "in reserve" and ran it "when system
  margins were tight and prompt prices made it economical"
  ([City AM](https://www.cityam.com/drax-hits-back-at-claim-it-cut-production-at-biomass-unit-to-avoid-639m-customer-payout/)).
  So the CfD unit's behaviour is regime-dependent, and in 2022 it is the flexing unit.

## Measured: which units carry the metered calm-day gap

Elexon B1610 (settled metered output per BM unit, `/datasets/B1610/stream`) was pulled for the
ten units above, 2019-2024, and graded on §31's day-by-day wind share. "D1-D10" is the mean output
on the calmest tenth of days minus the windiest tenth, in MW. The prediction was filed before the
pull (`scratch/prediction.txt`, 2026-10-04).

**Coverage.** The listed units sum to 0.90-0.98 of FUELHH BIOMASS's annual mean, and to its
D1-D10 within 10 MW in 2020-2024. **2019 is the exception:** the units carry -50 MW of a +361 MW
metered gap. Some 2019 biomass output with a calm-day lean is not in these units. Which BM unit it
is has not been established.

| D1-D10 (MW), year deciles | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| FUELHH BIOMASS (metered) | +361 | +1,122 | +314 | +727 | +366 | +1,021 |
| Drax 1 (CfD) | +10 | +85 | **+220** | +210 | -69 | +130 |
| Drax 2-4 (RO) | +6 | **+962** | +68 | **+480** | **+487** | **+899** |
| Lynemouth (CfD) | -56 | -12 | +13 | +73 | -38 | -19 |
| Teesside, Wilton, Rothes | -11 | +13 | +21 | -34 | -4 | +8 |
| mean output, Drax 1 / Drax 2-4 / Lynemouth | 501/951/257 | 569/1,067/297 | 440/1,280/323 | 260/1,212/118 | 129/1,205/70 | 525/1,177/220 |

| prediction | measured | |
|---|---|---|
| P1 Drax RO carries >=60% of the gap in >=5 of 6 | 0.02 / 0.86 / 0.22 / 0.66 / 1.33 / 0.88: 4 of 6 | **refuted** (2019, 2021) |
| P2 Drax 1 D1-D10 < 100 MW in 2019-21 and 2024 | 10 / 85 / 220 / 130 | **refuted** in 2021 and 2024 |
| P3 2022 Drax 1 above its 2019-21 value | 210 vs 10 / 85 / 220 | **refuted** against 2021; its MEAN fell to 260 and 129 MW in 2022-23 |
| P4 Lynemouth below 60 MW every year | under 60 except 2022 (+73) | **refuted narrowly** in 2022 |
| P5 the units within 10% of FUELHH's mean | 0.90 / 0.97 / 0.97 / 0.97 / 0.96 / 0.98 | held, at the edge in 2019 |

**Post-hoc, NOT pre-registered.** Calm days cluster in summer, which is outage season, so year
deciles mix weather with maintenance. Taking deciles WITHIN each calendar quarter and averaging
the four gaps: Drax 2-4 (RO) carry 177 / 923 / 297 / 643 / 448 / 945 MW of a metered 458 / 1,033 /
518 / 756 / 520 / 989, a share of **0.39 / 0.89 / 0.57 / 0.85 / 0.86 / 0.96**. Drax 1 carries
31-108 MW, except 220 MW in 2021. Lynemouth carries -42 to +19 MW.

## What it establishes

- **Within season, Drax's RO units are the largest carrier of the calm-day excess in every year,**
  at 0.85-0.96 of it in 2020 and 2022-24 and less in 2019 (0.39) and 2021 (0.57). Lynemouth
  (CfD) does not move with the wind in any year. That is the split §36 asked for, measured rather
  than assumed.
- **The scheme is not the mechanism.** The CfD Drax unit flexed in 2021 and was held back in
  2022-23 (mean 440 -> 260 -> 129 MW), as the BMRP reasoning above and the 2022-23 reporting predict.
- **The size of the flex is not a capacity.** The RO units' capacity is about 1,975 MW in every
  year from 2019, and their within-season gap runs from 177 to 945 MW. A rule that flexes "the RO
  share" at published capacity, with nothing else, gives the same gradient every year. The real one
  varies fivefold. What sets it (spark-to-biomass spread, the ROC cap, pellet supply) is not
  established here.

## What it does NOT establish

- Which unit carries 2019's missing +290-410 MW of gap.
- The Drax BM-unit-to-unit mapping, beyond being consistent with Unit 4 flexing like 2 and 3.
- The schemes of Wilton and Rothes against the Ofgem RO register. Their gradient is under 25 MW,
  so the answer cannot matter at this grade.
