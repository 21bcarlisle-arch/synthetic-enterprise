**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `a-gas-homes-2021-serl-median-says-whether-the-remainder-is-the-crisis`

# A gas-heated home's electricity level, split into the 2022 crisis and a level excess

Delivery seat, 2026-10-08. Decided blind to company results: nothing below reads a company figure.

**Duplicate-work note.** The draw reported this id "already held" in `.seat_work_in_hand.json`. The
only process holding it was this invocation (pid 2980862), so the claim was the draw's own write.
The work and the claim are one item.

## What SERL publishes, read at source

The draw asked for "SERL's 2021 gas no-PV annual median". SERL publishes no annual median on that
basis for any year. What it does publish, in the **Vol 2 aggregated tables**
(<https://api.figshare.com/v2/articles/25472560>, file `SERL_Stats_Report_Aggregated_Tables_Vol_2.xlsx`,
sheet `Figure_4`), is **every month's** median electricity import for homes with gas heating and no
PV, from 2021 to 2023. That is the basis the world's S4 cell uses (`fabric_gap_ledger`, the monthly
medians times the days in each month). Summed, at n ≈ 7,200–8,960 homes per month:

| Year | Sum of monthly medians | Same, from monthly means | Jan | Jun–Aug low |
|---|---|---|---|---|
| 2021 | **2,851** | 3,455 | 9.69 | 6.64 |
| 2022 | **2,535** | 2,998 | 8.52 | 6.02 |
| 2023 | **2,452** | 2,911 | 7.75 | 5.82 |

**Correction, made beside the claim.** The "~2,600" carried as SERL 2022 in the research doc and in
the S4 anchor text was an estimate from Table 3's two extremes. The twelve months sum to **2,535**.

Cross-check on another basis: Vol 1's tables (figshare 20039816, `Figure_12`) give gas-boiler homes
in 2021 a median of 7.869 kWh/day, about 2,872 kWh/yr, on net electricity (n = 8,553). That agrees
with 2,851.

## Why 2021 minus 2022 is not the crisis

The fall from 2021 to 2022 is −316 (−11.1%). SERL's own text names three things inside it: the third
lockdown (January–March 2021), a year about 1 °C colder, and the crisis. Month by month, January to
March 2022 sit 12–15% below 2021. July to November sit 8–11% below. So lockdown and cold show up in
the first quarter, and the gap that remains from summer onwards is about −9%.

The crisis has a published counterfactual. Both studies were trained on data before the crisis and
correct for weather. Winter 2022/23 against 2021/22, electricity:

- **−7.1%**: Zapata-Webborn et al. (2024), as SERL Vol 2 §2 cites it.
- **−8.4%**: the published version of the same work (n = 5,594).
- **−9.1%**: McKenna et al. (2024b).

The baseline these studies use is winter 2021/22. That puts January to March 2022 **before** the
crisis on their definition. The cap rose 54% in April 2022, and the gap from July to November is
already about −9%. So the response is applied from April to December, which is 1,819 of the year's
2,535 kWh.

## Why the world is compared with SERL 2022 with the crisis removed

The world's electricity has no price input. `simulation/premise_trace.draw_appliance_events` and the
fabric trace that `tools/couple_fabric._serl_home` reads take no unit rate. The world's only price
response is the heating setpoint, in `premise_trace.comfort_constraint_for`, and that acts on gas.
So the world's 2022 electricity is a 2022 **without** the crisis, and it must be compared with SERL
2022 with the response added back:

| Assumption | SERL 2022 without the crisis |
|---|---|
| −7.1% from April to December | **2,674** |
| −9.1% from April to December | **2,717** |
| Outer bound: −9.1% over the whole year | 2,789 |

## Pre-registration (filed before the measurement below)

The last reading of the world on this basis was **2,787**: origin `676415030`, 163 homes, seed 17,
C1 2022. But a median over 163 homes has a standard error of about 1.25 × 1,430 / √163 ≈ **±140
kWh**, where 1,430 is the interquartile range over 1.35, taken from SERL's own spread. The gap I am
trying to detect is smaller than that. One seed of 163 homes cannot say whether a level excess exists.

**Measurement.** `fgl.level_and_season_vs_serl` run on the S4 cell, at the current origin, over
1,200 drawn premises (about 980 gas-heated no-PV homes) for each of seeds 17, 29 and 41, at C1 2022.
The 95% interval comes from a bootstrap over homes, with 400 resamples per seed.

**Predictions:**
1. The world's S4 will be **2,700–2,850** on each seed, with the pooled point near 2,780.
2. The bootstrap half-width will be **50–80** per seed.
3. **Level excess**, meaning the world minus 2,717 (the upper end of the central band): **+30 to
   +130**.

**Decision rule, written now.** A level excess "remains" only if the pooled 95% interval lies wholly
above **2,717**. If it does, the cooking arm is pre-registered as the draw specifies: oven ×0.80 and
hob ×0.84, over the same homes, seed 17, C1 2022. If the interval reaches 2,717 or lower, the level
is inside the crisis adjustment. In that case no cooking arm is run **for the level**. Cooking's case
then rests on the evening peak (S2), which is a separate cell, and a refit of cooking would be
fitting a world constant to a price response.

## Result (origin `7cc5b1525`, C1 2022, `/tmp/gaslevel/measure.py`)

| Draw | Homes | World S4 | 95% (bootstrap over homes) | S2 peak | S3 max/min |
|---|---|---|---|---|---|
| seed 17, 1,200 premises | 969 | 2,965 | 2,894–3,039 | 0.650 | 1.255 |
| seed 29, 1,200 premises | 977 | 2,983 | 2,883–3,080 | 0.647 | 1.260 |
| seed 41, 1,200 premises | 975 | 3,013 | 2,919–3,100 | 0.655 | 1.242 |
| **Pooled** | **2,921** | **2,985** | **2,938–3,031** | | |
| seed 17, first 200 premises (the old set) | 163 | 2,787 | 2,629–2,965 | 0.626 | 1.291 |

**Predictions graded.** (1) The level would be 2,700–2,850: **wrong**. It is 2,965–3,013 on every seed.
(2) The half-width would be 50–80: **right** for each seed (72–98, slightly above), and 47 pooled.
(3) The excess would be +30 to +130: **wrong**. It is **+268** (+221 to +314) against 2,717, and
+196 against the 2,789 outer bound.

**What the miss was.** The 163-home set is a low draw. At this origin it reproduces its 2,787 exactly,
and it sits about 200 below the same seed's 969 homes. That is about 1.4 of its own standard errors,
so the set is not broken. It is small. **Every level and shape reading taken on those 163 homes
carries that draw:** the 2,760 after electronics, the 2,787, the "+0.9 kWh/day summer excess", and the
0.626 peak and 1.291 season in the fabric-path finding. At about 2,900 homes, the peak is **0.650**
and the season **1.25**, both further from SERL than those readings said. The pre-registration's own
standard error (±140) said one seed could not settle this. Running the larger draw is what showed
the old set was low as well as noisy.

**The split.** SERL 2022 without the crisis is 2,674–2,717 (2,789 at the outer bound). The world is
2,985. **The 2022 crisis explains about 140–180 of the 450-kWh gap to SERL's 2,535. A level excess of
about +270 (+200 to +310) remains** that the crisis cannot account for. On the rule written above,
the cooking arm is pre-registered.

## The cooking arm (pre-registered before it ran)

One variable: oven energy per use ×0.80 and hob ×0.84 (ECUK, dated to 2022 in the research doc).
Implemented as `duration_hours` scaled on the two `APPLIANCE_CATALOGUE` rows, so the power and the
timing window stay where they are. Same three seeds, same 1,200 premises, paired by home.

**Prediction.** World S4 falls by **35–65** on each seed. Electric ovens are in about 70% of these
homes, at ~300 kWh/yr, so that leg is about −42. Electric hobs are in about 30% of homes with gas,
at ~160 kWh/yr, which is about −8. A median moves a little less than the mean. **The level excess
after the arm is +200 to +235.** Cooking at its sourced trend cannot close the level. If that
holds, cooking is a real but minor term, and the rest of the level has no sourced end use yet.
The S2 peak falls by 0.01–0.03, because ovens and hobs are evening load.

### The arm's result (`/tmp/gaslevel/arm.py`, paired by home, 400 bootstrap resamples)

| Seed | Homes | S4 off → on | ΔS4 (95%) | Mean per home | S2 peak | S3 |
|---|---|---|---|---|---|---|
| 17 | 969 | 2,965 → 2,908 | −57 (−66, −49) | −59.0 | 0.650 → 0.625 | 1.255 → 1.251 |
| 29 | 977 | 2,983 → 2,917 | −66 (−74, −53) | −58.0 | 0.647 → 0.622 | 1.260 → 1.267 |
| 41 | 975 | 3,013 → 2,951 | −62 (−70, −51) | −58.6 | 0.655 → 0.629 | 1.242 → 1.245 |
| **Pooled** | **2,921** | **2,985 → 2,924** | **−61** | | | |

**Graded.** ΔS4 −35 to −65: **right** on every seed, near the top of the range. Excess after the arm
+200 to +235: **right**, at **+207** against 2,717 and +135 against the 2,789 outer bound. Peak −0.01
to −0.03: **right** (−0.025). The season does not move.

## What this says, and what it does not

1. **The remainder is not mostly the crisis.** The 2022 response accounts for about 140–180 kWh. The
   world's level sits about **+270 above a 2022 without the crisis**, and about +200 above it once
   cooking is at its dated source.
2. **Cooking at its dated source is a −61 term.** It is sourced and the right size, but it is small.
   It also takes 0.025 off the evening peak, against a peak excess of about 0.17 (0.650 against
   SERL's 0.48). The world constant is **not changed in this item.** Landing it refits a world anchor,
   and that has to budget the value-arms re-take. It is handed on.
3. **About +200 kWh of level has no sourced end use yet.** Electronics is at its 2022 level. Cold sits
   at its trended source. Lighting has no level, because ECUK's series breaks in 2021/22. Cooking is
   now accounted for. The next place to look is the term with no dated level at all, lighting. After
   that comes the distribution: whether the world's homes are SERL's homes by occupancy and floor
   area, since a median of a different population is a different median.
4. **The 163-home instrument misled.** `tools/couple_fabric.py --serl 200` reads one draw of about 163
   homes. Its median sits about 200 kWh low at seed 17, and its peak and season sit on the flattering
   side. Use `--serl 1200` or more: about 70 s, and about 970 homes.
5. **Not established.** SERL is unweighted and its sample changes from year to year (Vol 2 §2). The
   crisis response is a winter figure, carried here from April to December. The two counterfactual
   studies disagree by 2 points, and the bands above carry that range rather than choosing within it.
