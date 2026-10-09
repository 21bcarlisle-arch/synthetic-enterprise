**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `a-gas-homes-summer-electricity-level-against-serl-table-3`

# A gas home's season miss is now the winter, and lighting is the one end use off its source

## The premise was re-measured first, and it is spent

The drawn item said the world's S3 is 1.227 and its summer about +0.9 kWh/day too high. Both
figures come from the 2026-10-08 reading (`SEAT_FINDING_THE_FABRIC_PATH_…_NO_SEASON_2026-10-06.md`,
last section). Eleven world commits have landed since: electronics at its 2022 level, cooking fuel
and hours, microwave ownership, headcount given bedrooms, dishwasher hours, and daylight lighting.

**Ten months "still unread" were already on file.** SERL's aggregated tables (figshare 25472560,
sheet `Figure_4`) give every month's median and mean. The research doc used them on 2026-10-08 for
the annual sum, but not month by month. Here they are for 2022, gas-heated, no PV:

| kWh/day | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SERL median | 8.52 | 8.00 | 7.36 | 6.80 | 6.38 | 6.14 | 6.18 | 6.02 | 6.19 | 6.61 | 7.22 | 7.98 |
| SERL mean | 10.28 | 9.60 | 8.77 | 8.04 | 7.45 | 7.18 | 7.14 | 6.99 | 7.24 | 7.73 | 8.53 | 9.69 |
| World median, origin `bbdb6c1a7` | 7.88 | 7.70 | 7.14 | 6.90 | 6.63 | 6.24 | 6.37 | 6.22 | 6.57 | 6.66 | 7.06 | 7.90 |
| World mean | 8.36 | 8.10 | 7.64 | 7.41 | 7.17 | 6.92 | 7.02 | 6.98 | 7.26 | 7.36 | 7.60 | 8.38 |

163 homes, seed 17, C1 2022 (`python3 tools/couple_fabric.py --serl 200` reads S1 0.127 pass,
S2 0.484 pass, **S3 1.269 fail** (Dec/Aug), S4 2,532 against SERL's 2,535).

**The summer is right: +0.10 to +0.20 kWh/day on the median, −0.01 to −0.26 on the mean. The
miss is the winter: January −0.64 on the median, −1.92 on the mean.** *(Wrong at scale, corrected
below: 163 homes is a low draw. Over 2,412 the summer is +0.56 to +0.84 and January −0.35.)* The annual level matches,
so the season is now a pure SHAPE miss. Median swing (Jan − Aug) is 1.66 against SERL's 2.50.

## Attribution by end use (world, same 163 homes, mean kWh/day)

Lighting and electronics were read by zeroing their kW constant. The switching RNG is shared and
untouched, so only their energy leaves. Appliances were read by event name, and the rest from the
trace's own fields. Standby is the residual and comes out flat, which checks the decomposition.
Instrument: `/var/tmp/summer/measure.py`.

| End use | Dec–Jan | Jun–Aug | Swing | World DJ ÷ JJA | Published season | Source |
|---|---|---|---|---|---|---|
| Supplementary heater | 0.47 | 0.00 | +0.46 | — | ~2.3× mean in DJF, ~0 in JJA | HES Fig 537, CAR 656 kWh/yr |
| Boiler pump, fan, controls | 0.54 | 0.09 | +0.44 | 5.9 | zero in summer | SAP 10.2 Table 4f/5a |
| Lighting | 0.53 | 0.33 | +0.20 | **~1.6** | **~2.5–2.6** | CAR Lighting p.6, HES Fig 465 |
| Washer + dryer | 0.83 | 0.57 | +0.26 | 1.47 | 1.48 | HES Fig 359 |
| Oven, hob, kettle, microwave, toaster | 1.36 | 1.08 | +0.28 | 1.24–1.25 | 1.25 | HES Fig 413 |
| Cold appliances | 0.97 | 1.23 | −0.26 | 0.79 | 0.74 | HES Fig 334 |
| Electronics | 0.77 | 0.77 | 0.00 | 1.00 | flat | HES §13.1 |
| Dishwasher, vacuum/iron, standby | 2.91 | 2.90 | 0.00 | 1.00 | not published | — |

**Every end use with a published season matches it, except lighting.** CAR's *Further analysis
of HES: Lighting* (p.6) regresses each year-monitored home's daily lighting on day length. Over
25 homes the slope is a **median of 11.4% of the annual mean per hour** (mean 11.5%, SD 7.2%).
At 51.5° N that gives DJ 1.48 and JJA 0.59 of the annual mean, a ratio of **2.51**. HES Fig 465
reads ~2.6. The world read 2.54 until `da944e500` (2026-10-09) let a light switch on in daylight
at a flat 0.19 × occupancy all year. That share was sized to CAR's other figure from the same
report (p.25: 24 W from April to September, 09:00–18:00). It flattened the season to ~1.6. The two
CAR facts are not yet reconciled by one mechanism.

**Size.** At the world's lighting level (~157 kWh/yr), restoring CAR's season moves the lighting
swing from 0.20 to about 0.38 kWh/day. That is about a fifth of the median's 0.84 shortfall. The
rest of the shortfall has no end use contradicting its source. The candidates are:

1. **The lighting level.** The 2016–2025 level is not established. ECUK brackets it at 137–430
   kWh/yr, and the world sits near the bottom. At CAR's season, every 100 kWh/yr adds about
   0.25 kWh/day to the swing, and also adds 100 to S4, which is already at SERL.
2. **The tail.** SERL's mean swing is 3.3 against the world's 1.4. Supplementary heating at
   10% × 656 is a sourced tail, and SERL's gap on the mean is twice its gap on the median.
3. **The crisis year.** SERL 2022's January is pre-response and its December is post-response.
   The world has no price response, and that cuts in the opposite direction.

## Pre-registration (written 2026-10-09T18:55Z, before either arm was run)

Two one-variable sizing arms, both arms in ONE process over the same 163 homes. Neither is a landing.

- **Arm A, `_DAYLIGHT_LIGHTING_SHARE = 0`.** The kW constant re-derives to 0.035, so the annual
  level is held by the code's own formula. Prediction: lighting DJ ÷ JJA returns to **2.3–2.7**.
  Annual lighting stays within ±5%. S3 median moves **1.269 → 1.29–1.33**. S4 moves by less
  than ±40.
- **Arm B, lighting level × 430/157 at today's share.** This is the top of ECUK's bracket, as a
  bound and not a candidate. Prediction: S3 **1.28–1.31**, and **S4 2,750–2,850**, so it is
  refused by the level cell.

If Arm A lands inside its band, lighting's season is worth about +0.04 on S3. The miss is then
mostly not a missing season in any one end use. It is a named gap: the lighting level, and the
sourced heater tail that the median barely sees.

## Result (same evening, both arms in ONE process, `/var/tmp/summer/arms.py`)

| 163 homes, seed 17, C1 2022 | S3 | S4 | Lighting kWh/yr | Lighting DJ ÷ JJA | Predicted |
|---|---|---|---|---|---|
| Origin | 1.269 (Dec/Aug) | 2,532 | 154 | 1.59 | — |
| A: daylight share 0 | **1.277** (Jan/Jun) | 2,534 | 154 | **2.00** | S3 1.29–1.33 ✗, DJ÷JJA 2.3–2.7 ✗, level ±5% ✓, S4 ±40 ✓ |
| B: lighting at 430 | **1.305** (Dec/Jun) | **2,799** | 422 | 1.59 | S3 1.28–1.31 ✓, S4 2,750–2,850 ✓ |

- **Arm A is refuted on both its season legs.** Without daylight lighting, the world's dark-hours
  mechanism gives DJ ÷ JJA of 2.00, not CAR's 2.51. The "2.54" quoted above came from the
  2026-10-06 one-premise reading, at an older occupancy and headcount, and was not re-read before
  I predicted from it. So daylight lighting flattened the season, but did not flatten it from
  CAR's level. Lighting's season is worth **+0.008** on S3 from the share, and about +0.02 at most
  if the whole season reached CAR. **It is not the lever, and nothing is moved on it.**
- **Arm B holds, and is refused by S4, as predicted.** The lighting level cannot close S3 without
  putting the annual sum ~265 over SERL.

## Correction to the premise section above: at scale, the summer IS high (re-read 2026-10-09)

"The summer is right … the miss is the winter" was read from **163 homes, which is a low draw**.
The 2026-10-08 finding had already said so ("The 163-home reading was a low draw"), and I did not
heed it. The triage row's 1.220 came from 2,431 homes. Re-read at origin `a2a93c183`
(`python3 tools/couple_fabric.py --serl 3000`):

| 2,412 homes | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World median | 8.17 | 7.97 | 7.47 | 7.29 | 7.01 | 6.70 | 6.78 | 6.73 | 7.03 | 7.19 | 7.49 | 8.16 |
| − SERL 2022 | −0.35 | −0.03 | +0.11 | +0.50 | +0.63 | +0.56 | +0.60 | +0.71 | +0.84 | +0.58 | +0.27 | +0.18 |
| − SERL **2021** | −1.52 | −1.35 | −1.18 | −0.61 | −0.51 | **+0.06** | **+0.08** | **+0.08** | **+0.26** | −0.21 | −0.48 | −0.45 |

S1 **0.137 fail** (band 0.125–0.135), S2 0.495 fail, **S3 1.220 fail** (Jan/Jun), S4 2,676 against
2,535. The end-use breakdown re-run over 1,213 homes gives the same season for every end use as
the table above. The one term that differs is the always-on draw: **3.23 kWh/day (135 W mean)**
against 2.61 in the 163.

## The summer level is a named gap: it is the 2022 price response, measured by SERL itself

**SERL's own months split it.** From 2021 to 2022, SERL's gas no-PV summer median fell **8–9%**
(June −0.51, July −0.52, August −0.62, September −0.58 kWh/day). Jan–May 2021 was lockdown, so
those months fell more (−12% to −15%) and are not a clean comparison. The world's 2022 summer sits
**+0.06 to +0.26 above SERL's 2021 summer**, and +0.56 to +0.84 above its 2022 summer. Two
independent figures give the same size: SERL's own 2021→2022 summer fall, and the published
crisis counterfactuals already in the research doc (−7.1% to −9.1%). **The world's summer excess
is the price response from April 2022, which the world's electricity behaviour does not model.
It is not an end use.** Every end use with a dated 2022 source sits at or below that source:
electronics 288 against ~376, cooking ~425 against ~460, and cold ~390 against ~393.

So S3 against SERL 2022 compares a world without a price response to a year with one, and the
ratio's shortfall is mostly that difference. **This is why the summer is a named gap and not a
build:** fitting any end use down to SERL 2022's summer would put the crisis into a constant, and
it would then sit in 2016–2021 and 2024–25 too.

**What is left after the crisis, ranked:**
1. **The winter is short, by about 0.35 kWh/day in January.** January 2022 predates the April cap
   rise. A world with no price response should sit at or above SERL here, not below. The ranked
   candidates: lighting's season (CAR, +~0.09 in January at most, from Arm A); the lighting level
   (not established, 137–430); and the heater tail (sourced, mostly in the mean).
2. **The trough is +0.007 kWh/h at scale** (0.137 against 0.13). That is about +0.17 kWh/day flat,
   and the 2026-10-08 finding that "the EFUS base survives a 2022 check" rested on the same
   low 163-home draw. EFUS 2011's always-on (median 90 W, mean 136 W) is a 2010–11 figure, and no
   2020s whole-home always-on source has been read. SERL Table 6's trough is a 2022 crisis-year
   statistic, so fitting the base to it would also be the crisis.
3. **The band.** SERL's three S3 years each have a special winter or summer: the 2021 lockdown
   January, and the 2022 and 2023 crisis summers. Corrected by its own 8–9% summer fall, 2022's
   ratio is about 8.52 ÷ 6.54 ≈ **1.30**. That is below the band's lower edge of 1.36. Whether the
   band itself carries the crisis is a question for the cell's owner, raised here and not acted on.

**Triage row `a-gas-heated-homes-electricity-has-no-season`:** restated with the 2,412-home reading
and this split. It is still `fix` and open. The winter shortfall and the trough are real and
unsourced. The summer is the price response, and that belongs to whoever models a 2022
electricity price response in household behaviour. Nothing in the world was moved.
