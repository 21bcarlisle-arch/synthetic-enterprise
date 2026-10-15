**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `W1_29_the_worlds_homes_are_drawn_too_alike_in_half_hourly_behaviour`

**Knowledge:** none -- this is a SIM fidelity DISCOVER pass, not a knowledge-layer anchor. No knowledge
page covers how a household's electricity moves half-hour to half-hour; the nearest, metering-and-reads,
covers how reads arrive and not what they read.

# The half-hourly texture of real homes' electricity, read from Low Carbon London

**Measured 2026-10-06**, worker on the delivery seat's lane-0 draw
`the-l1-1-texture-floor-is-read-at-source`, answering the L1.1 red recorded in `8fe730297`
(P0000 at 0.1495 against the 0.15 floor). Nothing reads a company figure. **Nothing is built and
the floor is not moved here.**

## What was asked

The L1.1 cell (`background/fabric_gap_ledger.py`, `half_hourly_texture`) judges every home by
`median |x[t] - x[t-1]| / mean(x)` over its half-hourly electricity, net of space and water
heating machines, against a floor of **0.15**. The floor's anchor says it is domain knowledge
("real homes move in the tens of percent, a 20-40% expectation") and that "the SERL/LCL published
band is NOT yet in the artefact library". This pass reads that band.

No publication reports this statistic, because it is this project's own. So it was computed directly
from the published raw data, with the cell's own function.

## Source and method

- **Data:** UK Power Networks, *SmartMeter Energy Consumption Data in London Households* (Low Carbon
  London trial, 5,567 homes, Nov 2011 – Feb 2014), London Datastore, dataset `vqm0d`, file
  `Partitioned LCL Data.zip` (795,722,689 bytes, 168 partitions of ~1M rows, sorted by meter id).
  Licence: UK Open Government Licence.
- **Sample:** 13 partitions spread evenly across the 168 (indices 0, 14, 28 … 154, 167), read by
  HTTP range without downloading the whole archive. That is 411 homes with enough data in the window.
- **Window:** 2013-01-01 to 2013-04-30, the same four calendar months as the world's drawn 60
  (2022-01-01 to 2022-04-30). Only complete 48-reading days count, and a home needs at least 100 of
  them. Calendar 2013 (300+ days) was also read as a check, and it moves the quantiles by under 0.01.
- **Statistic:** `background.fabric_gap_ledger.half_hourly_texture(days)` imported and called
  unchanged. Its source is byte-identical between the shared tree and `origin/main`. LCL homes are
  read on the whole meter, because the data carries no machine split.
- **Tariff:** "Std" (flat tariff) homes are the comparison set. The trial's 2013 dynamic-ToU arm is
  shown separately.

## The result

Std homes, Jan–Apr 2013:

| | n | p5 | p10 | p25 | median | p75 | p90 | p95 | share < 0.15 |
|---|---|---|---|---|---|---|---|---|---|
| LCL, all Std | 313 | 0.050 | 0.072 | 0.117 | **0.158** | 0.208 | 0.311 | 0.384 | **45%** |
| LCL, Std, <1% zero reads | 285 | 0.053 | 0.074 | 0.117 | 0.156 | 0.200 | 0.271 | 0.328 | 46% |
| LCL, Std, <1% zeros, 4–15 kWh/day | 183 | 0.078 | 0.099 | 0.134 | 0.164 | 0.200 | 0.257 | 0.310 | 37% |
| LCL, dynamic-ToU arm | 98 | 0.060 | 0.091 | 0.130 | 0.165 | 0.209 | — | — | 38% |
| **World, drawn 60** (`base_seed=17`, origin/main at `3d9c4fb84`) | 60 | — | 0.166 | 0.186 | **0.209** | 0.231 | — | — | **2%** (P0000) |

The world's minimum is 0.1495 and its maximum 0.289.

By consumption (LCL Std, <1% zeros), real texture falls as the home uses more. The world shows the
same direction, but higher:

| kWh/day | LCL n | LCL median | LCL < 0.15 | World n | World median |
|---|---|---|---|---|---|
| < 5 | 48 | 0.259 | 29% | 6 | 0.273 |
| 5–8 | 66 | 0.174 | 29% | 28 | 0.219 |
| 8–12 | 58 | 0.157 | 41% | 23 | 0.185 |
| 12–20 | 68 | 0.133 | 60% | 2 | 0.205 |
| ≥ 20 | 45 | 0.109 | 71% | 1 | 0.230 |

P0000 uses 11.9 kWh/day and reads 0.1495. Among real homes of its size (8–12 kWh/day), 41% read
lower and the median is 0.157. **P0000 is an ordinary home.**

## What it establishes

1. **The 0.15 floor is refuted at source.** The anchor's "20–40%" expectation is wrong for this
   statistic: the real median is about 16%, and nearly half of real flat-tariff London homes sit
   under 0.15. The kettle argument describes the *mean* step during active hours. This statistic
   takes the *median* over all 48 steps, and half of those fall in the night or in quiet hours,
   where adjacent half-hours differ by a fridge cycle.
2. **P0000's calm behaviour is not a world defect.** It sits at the 44th percentile of the real
   distribution, close to the median of its own consumption band.
3. **The real defect points the other way: the world is too rough and too alike.** The world's
   median is 0.209 against a real 0.158. Its middle half spans 0.186–0.231 (width 0.045), against a
   real 0.117–0.208 (width 0.091). No world home is in the real bottom 44%. Above 12 kWh/day the
   world gets rougher (0.205, 0.230) where real homes get calmer (0.133, 0.109), although only three
   world homes sit there. The world's homes behave like one home with mild variation. This bears on
   per-customer demand inference far more than one home at the floor does, because any company
   method that learns a home's shape from its meter is being tested against too narrow a population.

## Limits, stated so they are not read as established

- **Heating fuel is not recorded in LCL.** London housing is mostly gas-heated, but some homes in the
  sample have electric heat or Economy 7 on a "Std" label. Those homes are read on the whole meter,
  which makes them calmer (a large denominator). The 4–15 kWh/day subset is the cleanest proxy for
  gas-heated, and even there 37% sit under 0.15. The refutation does not rest on the electric tail.
- **2013 London is not 2022 GB.** Appliance stock (LED lighting, more standby electronics) and the
  London housing mix both differ. Neither has a published direction for this statistic. No
  correction is applied.
- **The sample is 13/168 partitions.** That is ~7% of the trial and a systematic spread by meter id,
  not a random draw of homes. The full archive is 796 MB if the tails need tightening.
- **SERL was not read.** Its half-hourly data is safeguarded (UK Data Service, SN 8666) and not
  openly downloadable, so no SERL figure exists for this statistic. Any SERL comparison needs a
  data-access application, and that is the director's call.
- **The world side is one draw** (seed 17, seed-7 traces) of 60 homes. The world's spread
  could vary with the seed. That has not been checked.

## What it does not decide

A changed floor is not this pass's deliverable. If the cell's purpose is "fire only on a generator
that is smooth by construction", the sourced lower tail (p1 ≈ 0.024, p5 ≈ 0.05) is too low to
discriminate home by home. The structural L1.1n null-ratio cell already asks that question with no
external number. The sourced comparison this data supports is distributional: the world's quantiles
against LCL's. Which shape the cell takes is a build decision, recorded in the finding.

## What was done with it (2026-10-06, later the same day)

The L1.1 cell (`background/fabric_gap_ledger.py`) is now judged against the "LCL, all Std" row
above: for each of p10, p25, median and p75, the count of world homes under the real quantile is
tested exact-binomial against n·q, Bonferroni at 5%. The 0.15 per-home floor is gone. On the drawn
60 the cell is red on all four legs (adjusted p 2.5e-13), so the red is now the spread defect in
point 3, filed as the atom named above. The real quantiles are treated as exact, so the test is a
little stricter than a two-sample test would be.

## Why the world's homes are alike: a decomposition, and one hypothesis tested (2026-10-06, evening)

Worker on the self-refill draw of `W1_29`. The same 313 LCL Std homes and the same window, read from
the same 13 partitions. The world side is the drawn 60 (`base_seed=17`, traces `seed=7`, C1 weather,
HEAD `a8bf44ef6`), read net of both heating machines exactly as the L1.1 cell reads it
(`machine_draw` and then `meter_net_of_machines`). **Nothing is built here.** These are per-home
statistics, shown as p10 / p25 / median / p75 / p90 across homes.

| per-home statistic | LCL Std (313) | World (60) |
|---|---|---|
| L1.1 texture | 0.072 / 0.117 / 0.158 / 0.208 / 0.311 | 0.165 / 0.185 / 0.205 / 0.227 / 0.246 |
| kWh/day | 3.5 / 5.3 / 9.1 / 15.0 / 23.6 | 5.7 / 6.5 / 7.5 / 9.3 / 10.8 |
| base load, kW (p5 of the home's half-hours × 2) | 0.016 / 0.040 / 0.080 / 0.136 / 0.224 | 0.045 / 0.047 / 0.049 / 0.054 / 0.057 |
| base load ÷ mean | 0.05 / 0.12 / 0.21 / 0.30 / 0.41 | 0.11 / 0.14 / 0.16 / 0.18 / 0.20 |
| night level (periods 2–9) ÷ mean | 0.28 / 0.38 / 0.50 / 0.68 / 0.90 | 0.19 / 0.22 / 0.28 / 0.32 / 0.38 |
| lag-1 autocorrelation | 0.41 / 0.53 / 0.65 / 0.75 / 0.83 | 0.45 / 0.47 / 0.50 / 0.53 / 0.57 |
| coefficient of variation | 0.65 / 0.76 / 0.97 / 1.22 / 1.46 | 1.27 / 1.32 / 1.40 / 1.49 / 1.55 |
| texture, night steps only (t < 12) | 0.031 / 0.059 / 0.103 / 0.160 / 0.264 | 0.092 / 0.106 / 0.129 / 0.150 / 0.173 |
| texture, day steps only | 0.081 / 0.144 / 0.200 / 0.258 / 0.345 | 0.223 / 0.241 / 0.254 / 0.273 / 0.285 |

Correlation of texture with
kWh/day: world **−0.95**, LCL −0.32.

**What this says.** The world's texture is almost entirely a function of how much a home uses. In real
homes, size explains about a tenth of the variance in texture. Every world statistic sits in a band a
quarter to a half as wide as the real one. The world's homes are also too peaky (CV 1.40 against
0.97), too empty at night (28% of their mean against 50%), and too quick to change (lag-1
autocorrelation 0.50 against 0.65).

**The cause is in the code, not the parameters.** `generate_premise_trace` gives every home the same
stock. Each home gets 2.0 lighting units and 2.0 electronics units per person at the same kW, the same
fridge-freezer **and** the same freezer, the same 25 W standby, and the same nine-appliance catalogue
with the same nameplates. A home differs only in people count (and through it `appliance_intensity`),
routine offset, away days and cold-appliance phase. One home's shape, scaled by occupants, is exactly
what the table shows.

**Hypothesis tested: a per-home always-on load.** *Prediction, written before the computation:* raising
each world home's base load to a draw from the LCL base-load distribution (a constant added to the
netted series, so texture × mean ÷ (mean + c)) moves the median towards ~0.17 and widens the spread,
but does not reach the real p10. *Result, over three draws:* median 0.164 / 0.173 / 0.176; homes
under the real p10 / p25 / median / p75 = [0, 11, 28, 53], [3, 8, 17, 49] and [1, 5, 16, 43] against
an expected [6, 15, 30, 45]. **The prediction held.** Base load is part of the mechanism and not
enough on its own. In LCL it is also a weak predictor of texture: within each consumption band,
corr(texture, base ÷ mean) is only −0.13 to −0.34, and log kWh plus the base-load ratio explain
R² = 0.25. The estimate also adds energy the world does not have: +0.8 kWh/day at the median, which
would fail the TDCV level judgement unless something else gives way.

**What the build needs, and what is not established.** The missing mechanism is per-home **stock**
heterogeneity: which appliances a home owns (separate freezer, tumble dryer, dishwasher, electric
oven or hob), how many always-on and long-dwell devices it runs, and the base load those set. That is
how a home gets calm (a large, persistent share of its use) or rough (a small home where every kettle
counts) independently of its size. **Ownership rates are not in the knowledge layer.** No
`docs/market_research/` page carries household appliance ownership. ECUK's domestic end-use
ownership tables and the EFUS 2017 lighting-and-appliances report (already named as the unfetched
lead in `occupancy_consumption_volume_shape_w2_13.md`) are the first places to look. **Build no
ownership draw until those rates are read.** The base-load distribution in the table above is
measured, and it is whole-meter LCL, so it carries the electric-heated "Std" homes in its upper tail.

*Correction, 2026-10-06, later the same day: the ownership rates are now read. EFUS 2011 and 2017 give
them by household size in `what_appliances_an_english_home_owns_efus_2011_and_2017.md`. A separate
freezer is in 38% of homes, a dishwasher in 44% and a tumble dryer in 58%, and the world gives all three
to every home.*

Limits: this is one world draw (seed 17), the 13 partitions described above, the p5 half-hour as the
base-load estimator (a home with logging gaps that read 0 sits at 0), and a constant-shift estimate,
not a regenerated trace.

## What the stock draw did (2026-10-06, night)

Built on the EFUS read: `pt.owned_stock` draws, once per premise and each from its own substream,
whether the home owns a dishwasher and a tumble dryer (EFUS 2011 by household size) and a separate
freezer (EFUS 2017, 38.2%, national). The fridge-freezer and the rest stay in every home. An unowned
appliance still consumes its random draws, so the appliances a home owns replay exactly as before.
That keeps it one variable. Measured on the same drawn 60, both arms in one process:

| | full stock (control) | drawn stock |
|---|---|---|
| homes under real p10 / p25 / median / p75 (expected 6 / 15 / 30 / 45) | 0 / 0 / 3 / 31 | **0 / 7 / 29 / 46** |
| world median texture (real 0.158) | 0.205 | **0.161** |
| world p10 / p25 / p75 | 0.165 / 0.185 / 0.227 | 0.116 / 0.130 / 0.204 |
| legs red after Bonferroni | all four | **p10 only** |
| L2.4 scale spread p90/p10 (real 5.38) | 1.93 | 1.99 |

*Pre-registered before the run:* median within 0.015 of 0.209, a wider spread, and at most 2 homes
under the real p10. **The median prediction was refuted**: it moved 0.044, nearly all the way to the
real value. The other two held.

**Why it moved so far, and the part that is not yet right.** Every one of the seven homes now under
the real p25 owns no separate freezer, and five of the seven have 4–5 people. The freezer's 61-minute
cycle against 30-minute periods was a night-time texture source in every home. Without it a large
home's night goes quiet. Real calm homes are not mostly large ones, though: in LCL, texture correlates
only −0.32 with kWh. So the world's calm tail is now the right size but probably made of the wrong
homes. The p10 leg is the red that is left: no world home is as calm as the calmest real tenth
(0.072). The next readings are the cold appliances' cycle against measured fridge and freezer traces,
and the base-load distribution above, which this build did not touch.

The authored test fixtures (the 8-home panel, the matched pair and the five regimes) hold the stock at
`pt.FULL_STOCK`, because a matched pair that owned different appliances would not be matched. One thing
was measured on that panel: with the household clocks collapsed, the drawn stock alone held L2.3n open
(1.85 → 1.11, against 0.87 with both collapsed). Timing diversity now has two sources.

## What the always-on draw did (2026-10-06, late night)

Built on EFUS 2011 §4.1's base load: `pt.always_on_kw` draws, once per premise, a constant always-on
load from a lognormal fitted to EFUS's median 90 W and mean 136 W (σ 0.909, ceiling 2,438 W, EFUS's
largest mean hourly demand). Before this, every home drew 25 W. The lognormal shape is a stated
simplification, because EFUS publishes no quantiles. Measured on the same drawn 60, both arms in one
process:

| | uniform 25 W (control) | drawn always-on |
|---|---|---|
| base load, kW, p10/p25/median/p75/p90 (LCL: 0.016 / 0.040 / 0.080 / 0.136 / 0.224) | 0.031 / 0.032 / 0.035 / 0.048 / 0.054 | **0.040 / 0.058 / 0.088 / 0.143 / 0.243** |
| base load ÷ mean (LCL: 0.05 / 0.12 / 0.21 / 0.30 / 0.41) | 0.09 / 0.11 / 0.13 / 0.18 / 0.20 | 0.12 / 0.18 / 0.27 / 0.37 / 0.49 |
| night level ÷ mean (LCL: 0.28 / 0.38 / 0.50 / 0.68 / 0.90) | 0.15 / 0.19 / 0.23 / 0.32 / 0.36 | 0.19 / 0.25 / 0.36 / 0.45 / 0.58 |
| homes under real p10 / p25 / median / p75 (expected 6 / 15 / 30 / 45) | 0 / 7 / 29 / 46 | **6 / 22 / 40 / 56** |
| world median texture (real 0.158) | 0.161 | 0.134 |
| legs red after Bonferroni | p10 | **p75** |
| L2.4 scale spread p90/p10 (real 5.38) | 1.99 | 2.44 |
| gas homes' annual kWh, median / mean | 2,535 / 2,650 | 2,970 / 3,382 |

*Pre-registered before the run:* median 0.12–0.14, 3–10 homes under the real p10, the p25 leg at risk
of going red the other way, and the spread toward about 2.3. The median and the p10 count held. p25 rose
to 22 and stayed green. **The p75 red was not predicted**, and the spread moved further than predicted.

**The base is now right and the ratio is not.** The drawn base load matches LCL's at every quantile,
and LCL played no part in the fit: the draw used EFUS's two moments only. What overshoots is base
÷ mean, by about 0.06 at the median. That is because the world's homes use less than LCL's whole
meters (9.1 kWh/day median, 2013, including electric-heated "Std" homes). Night ÷ mean is still below
LCL's, so the world's night is short of something above its base, not of the base itself. The red has
moved from "no home as calm as the calmest real tenth" to "the upper half too calm". Within the world,
texture now correlates −0.58 with log always-on. That may give the base too much of the job, and LCL
cannot say how much, because it does not separate base from size within a band (−0.13 to −0.34 above).

Gas homes' median use is 2,970 kWh a year, against TDCV medium of 2,900 (2021–24) and 2,500 (2026).
That is inside the medium band. The EFUS base includes a gas boiler's ~3 W standby, which the world
also carries, so a gas home counts ≤3 W twice.

**What this did to other controls.** L1.1n's worst home (P0049, 195 W always-on) now reads 1.018 times
its own flat day, which is a squeak: a home whose behaviour rides on a large constant cannot stand far
from its flat counterfactual. No real home's L1.1n ratio has been read. Peak-to-mean's correlation with
the L1.1n null rose to +0.457 through a common cause (base share), and it is +0.226 held at the share.
L1.4's day-type-shuffled null now puts 7 of 240 homes under its floor, where it put none, which is still
nowhere near firing the cell.

## Where the upper half's calm comes from: the night above the base (2026-10-06, close to midnight)

Worker on the self-refill draw of `W1_29`. The same 313 LCL Std homes and window. The world side is the
drawn 60 at `origin/main` `ba5728611`, measured in a clean worktree and read net of both heating machines,
as the cell reads it. **Nothing is built here.** Three new per-home statistics:
*above-base use* = (mean − p5 half-hour) × 48 kWh/day; *active texture* = median step ÷ (mean − p5),
which is texture with the constant taken out of the denominator; and the daily profile above the base
as a share of the active mean.

*Pre-registered before the run:* (P1) the world's above-base use is at least 25% below LCL's at the
median; (P2) the active-texture median is within ±15% of LCL's; (P3) within matched above-base bands,
world texture is below LCL's only in the upper bands, so the p75 red is a level defect and not a shape
defect.

| p10 / p25 / median / p75 / p90 | LCL Std | world |
|---|---|---|
| above-base use, kWh/day | 2.7 / 3.8 / 6.6 / 11.3 / 18.7 | 3.1 / 4.9 / 5.7 / 7.3 / 8.8 |
| active texture | 0.093 / 0.154 / 0.213 / 0.285 / 0.377 | 0.126 / 0.145 / 0.185 / 0.252 / 0.285 |
| night (periods 2–9) above base ÷ active mean | 0.14 / 0.20 / 0.34 / 0.54 / 0.85 | 0.07 / 0.09 / 0.11 / 0.17 / 0.20 |
| night step ÷ active mean (LCL 4–15 kWh/day, n 189) | 0.055 / 0.095 / 0.149 / 0.201 / 0.270 | 0.080 / 0.093 / 0.116 / 0.181 / 0.206 |
| day step ÷ active mean (LCL 4–15 kWh/day) | 0.163 / 0.229 / 0.275 / 0.339 / 0.400 | 0.178 / 0.198 / 0.238 / 0.297 / 0.335 |

Texture at matched above-base use (medians): 5–7 kWh/day, LCL 0.173 (n 58) against world 0.133
(n 23); 7–10 kWh/day, LCL 0.150 (n 54) against world 0.112 (n 18). Below 5 and from 10 to 15 the two
agree within about 0.01–0.04, on few world homes.

Median profile above base ÷ active mean, every other half-hour from 00:00 (LCL 4–15 kWh/day, then world):

    LCL    0.62 0.38 0.29 0.25 0.24 0.25 0.34 0.60 0.88 1.05 1.04 0.98 1.01 1.08 1.02 1.02 1.11 1.29 1.57 1.77 1.69 1.60 1.41 1.08
    world  0.11 0.11 0.11 0.12 0.12 0.14 0.22 0.72 0.92 0.81 0.90 0.83 0.82 0.79 0.79 0.84 1.16 1.91 2.21 2.33 2.47 2.46 1.70 0.93

**P1 was refuted**: the world's above-base median is 15% short, not 25%. What the world lacks is the
upper tail (p90 8.8 against 18.7), not the middle. **P2 held, narrowly** (−13%). **P3 was refuted**:
the calm sits in the 5–10 kWh/day bands, where most world homes are, and there a world home is
25–30% calmer than a real home that uses the same energy above its base. The p75 red is a **shape**
defect, so adding energy is not the remedy.

**The shape defect is the night.** From midnight to 04:00 a world home runs at about 0.11 of its active
mean above its base. A real gas-proxy home runs at 0.62 at 00:00, falling to 0.24 by 04:00. The world
moves that energy into a 17:00–22:00 peak about 40% too tall instead. Night steps are 22% too small
and day steps 13% too small.

**What the code does, and what is not established.** `generate_premise_trace` draws each home's
bedtime as `rise.randint(43, 47)`, so the household retires between 21:30 and 23:30. No world home is
up after midnight, and asleep counts as "present, nothing switched on" (`occupancy_at`, 0.25 with no
load). That range carries no source. No `docs/market_research/` page or knowledge-map row holds a GB
bedtime distribution. A quick search this pass found none published as figures: UKTUS 2014–15 is
microdata (UK Data Service), and Pérez et al. 2019 (*J Sleep Res*, PMC6378586) shows 2015 sleep onset
only as a figure, with no quantiles in the text. **Build no bedtime draw until a distribution is read.**

The night gap has more than one candidate cause, and this pass cannot yet attribute it:
(a) bedtimes capped at 23:30;
(b) nothing above base while asleep, where real homes run dehumidifiers, chargers, timed washing and
dishwasher runs, and a second fridge;
(c) electric-heated or Economy 7 homes carrying a "Std" label in LCL, already narrowed by the 4–15
kWh/day proxy without removing the gap;
(d) London 2013 being a later-living population than GB 2022.

The one-variable test is to move the bedtime range alone to a sourced distribution and re-read the
00:00–04:00 profile. Its prediction will be written when the distribution exists. LCL must not be the
source of the bedtime, because LCL is the comparison.

Limits: one world draw (seed 17, traces seed 7), 13/168 LCL partitions, p5 as the base estimator.
Scripts: `/tmp/w129b/` (not committed).

## Load while asleep, candidate (b): timed appliance runs are not the night gap (2026-10-07)

After `387ffe6ab` the midnight slot reads 0.43, but 01:00-04:00 is still at 0.14/0.11/0.11/0.11 against
LCL's 0.38/0.29/0.25/0.24. This pass first asked what KIND of load fills a real home's night, then ran
the one arm the world can test for (b). Same draw as before: world seed 17, traces seed 7, 60 homes, C1
2022-01..04, net of both machines, on origin/main at `387ffe6ab`. LCL Std is 4-15 kWh/day, n 189,
Jan-Apr 2013.

**The decomposition.** For each home, over periods 2-9 (01:00-04:30), divided by the active mean
(mean − p5): N is the night mean above p5. F is that night's own minimum above p5, averaged over days:
a floor that moves from day to day. E = N − F is variation within the night. BIG is the part of E from
half-hours more than 0.25 kWh over the night's minimum, which is an appliance run of 500 W or more.
SMALL = E − BIG. Medians, LCL against world:

| | N | F | E | SMALL | BIG |
|---|---|---|---|---|---|
| LCL | 0.309 | 0.044 | 0.221 | 0.199 | 0.007 (p75 0.045) |
| world | 0.119 | −0.012 | 0.128 | 0.126 | 0.000 |

The world's within-night variation is the fridge cycle and nothing else: 0.128 × 239 W ≈ 31 W, which
is a 90 W fridge-freezer at 0.32 duty. **A real home's night is not appliance runs.** Runs of 500 W or
more are 0.007 of the active mean at the median. The gap is small sustained load, about 0.07 (roughly
18 W), plus a floor that sits higher on some nights than others, about 0.06 (roughly 13 W).

**The arm.** A share s of washing-machine and dishwasher starts was re-drawn into periods 2-7. These
are the catalogue's two delay-start appliances. s is an envelope, not a sourced share, and nothing
ships. Pre-registered at 2026-10-07T04:19:55Z, before any run (`/tmp/w129s/PREDICTION.md`). s = 0
reproduced the baseline to the third decimal, which is the placebo.

| s | N | F | SMALL | BIG | profile 01:00 / 02:00 / 03:00 / 04:00 |
|---|---|---|---|---|---|
| 0 | 0.119 | −0.012 | 0.126 | 0.000 | 0.14 / 0.11 / 0.11 / 0.11 |
| 0.025 | 0.140 | −0.011 | 0.124 | 0.018 | |
| 0.10 | 0.195 | −0.011 | 0.119 | 0.075 | 0.17 / 0.22 / 0.22 / 0.18 |

| pre-registered | result | grade |
|---|---|---|
| P1 s=0.10, N rises 0.06-0.12 | +0.076 | held |
| P2 s=0.10, BIG ≥ 0.035 (5× LCL median) | 0.075 | held |
| P3 s=0.10, F moves < 0.01 | +0.001 | held |
| P4 s=0.10, SMALL moves < 0.02 | −0.007 | held |
| P5 s=0.025, N ≤ +0.04 and BIG ≤ 0.02 | +0.021, 0.018 | held |
| P6 s=0.10, 3 of 4 slots stay under LCL | 4 of 4 | held |

**What this settles.** Timed runs while asleep can raise the night. But a share big enough to matter puts
10× LCL's own large-excursion texture into the world (BIG 0.075 against 0.007), and it never touches the
two terms that make up the gap. Kept inside LCL's BIG band (s ≈ 0.01), the arm is worth about +0.01 of
the 0.19. **So (b) as delay-start appliances is refuted as the cause.** Do not wire a night-start share.

What (b) still means is **small, sustained load while asleep, plus a floor that moves between nights**.
The world has neither: `always_on_kw` is one constant per home, and the fridge is its only night cycle.
Candidates for the SMALL term: a second cold appliance's power, chargers, a dehumidifier, an aquarium,
someone up in the night. Candidates for F: a home that leaves a light, a TV or a computer on some nights.
Nothing in the knowledge layer sources either one. The next one-variable arm is the moving floor,
because F is a single term the world sets to zero by construction. It needs a published day-to-day
spread of household baseload first, and LCL cannot be that source because LCL is the comparison. (c)
and (d) stay open.

Limits: one world draw, 60 homes; the 0.25 kWh/hh cut for BIG is a choice (a dishwasher half-hour is
0.35). Scripts: `/tmp/w129s/` (not committed).

## L1.1n on real homes: a calm home can read below its own flat day (2026-10-09)

**Asked because** the drawn 60 put one home, P0049, at L1.1n 0.984 once it drew the book's census
headcount. L1.1n is `half_hourly_texture` over the same statistic on the home's own flat day (its mean
profile scaled to each day's total). Its rate band said this was impossible for a real household. It
tolerated no home under 1.0, on the premise that "a home whose meter is no rougher than its own mean
profile ... no real household is". Nobody had read the ratio on a real home.

**Pre-registered before the run:** (P1) 0–3% of real homes under 1.0; (P2) real p05 1.1–1.5, median
1.5–2.5; (P3) the world's 0.984 sits under the real p05.

**Result.** The same 313 homes and window as above, read with `half_hourly_texture_vs_own_null` on the
whole meter:

| Homes | Under 1.0 | Under 0.984 | p01 | p05 | p10 | p25 | p50 |
|---|---|---|---|---|---|---|---|
| 313 | 22 (7.0%) | 19 | 0.354 | 0.894 | 1.358 | 1.862 | 2.425 |

Two homes read 0.0 (a degenerate flat day, scored as a violation by the cell's own rule). Without them
it is 20 of 311 (6.4%).

**Graded.** P1 **wrong**: 7.0%, not 0–3%. P2 **wrong at the bottom**: p05 is 0.894, and the median
2.425 held. P3 **wrong**: 0.984 is above the real p05, so P0049 is an ordinary calm home.

**Mechanism.** The statistic is a median of half-hour steps. A calm home's days each step very little,
while its mean profile averages events that land at different times on different days, so it steps
moderately in every half-hour. Its median step can therefore exceed the real days' median step.

**Acted on.** The L1.1n rate band (`background/fabric_gap_ledger.py`, `RATE_BANDS`) moved from 0.0 to
0.26. That uses L1.4n's existing rule: the geometric midpoint of the gap between the populations that
have behaviour (real 0.070, drawn world 0.017) and the ones that have none (rescaled-day and flattened,
1.0).

**Limit.** LCL has no machine split, so this is the whole meter, compared against the world's netted
meter. The panel is London only and 2013.

Script: `/tmp/l11n/` (not committed).

## The pass is one 60-home draw, and at 240 homes the world is too calm and set by its size (2026-10-13)

Worker on the self-refill draw of `W1_29`, at `origin/main` `e4595810a`, in an isolated worktree. Nothing
reads a company figure. The limit stated at the top of this doc ("the world side is one draw ... could
vary with the seed. That has not been checked") is checked here. The world side is read exactly as the
L1.1 cell reads it (net of both machines), C1 weather Jan-Apr 2022, traces seed 7, homes drawn by
`premise_population.draw_premise_population(n, base_seed=s, as_of=2022-05-01)`.

**The L1.1 cell's own verdict** (`fgl.evaluate_two_level`), homes under the real p10 / p25 / median / p75:

| draw | under | expected | verdict |
|---|---|---|---|
| seed 17, n 60 (the pinned draw) | 3 / 14 / 27 / 44 | 6 / 15 / 30 / 45 | PASS |
| seed 17, n 240 | 17 / 73 / 134 / 197 | 24 / 60 / 120 / 180 | **FAIL** (p75 p 0.011) |
| seed 18, n 240 | 17 / 81 / 142 / 196 | | **FAIL** (p25 p 0.003) |
| seed 19, n 240 | 16 / 74 / 133 / 196 | | PASS (p75 p 0.018, inside the four-leg correction) |
| seed 23, n 240 | 16 / 79 / 141 / 194 | | **FAIL** (p25 p 0.007) |

World texture at n 240, p10 / p25 / median / p75 / p90: 0.081-0.083 / 0.106-0.108 / 0.144-0.145 /
0.188-0.193 / 0.232-0.240, against real 0.072 / 0.117 / 0.158 / 0.208 / 0.311. 52-55% of world homes
sit under 0.15, against real 45%. The red is on the **calm** side: the middle is too calm, and the
rough tail is missing (p90 0.24 against 0.31). The n=60 pass was a matter of statistical power. The
world was not already right.

**Why: a world home's texture is set by its size, and its size by its always-on draw.** These are
per-home Pearson correlations over the n 240 draws (the range across the four seeds):

| | world |
|---|---|
| texture ~ log kWh/day | −0.72 to −0.73 (real, on kWh/day: −0.32) |
| texture ~ log always-on kW | −0.69 to −0.70 |
| log kWh/day ~ log always-on kW | **+0.80 to +0.82** |
| log kWh/day ~ people | +0.42 to +0.46 |
| texture residual on log kWh ~ owned-stock count | +0.39 to +0.45 |

By kWh band (n 240, four seeds), world medians are 0.197-0.207 under 5 kWh/day, with **0%** of homes
under 0.15 (real 29%), and 0.076-0.092 at 12-20 kWh/day, with **100%** under 0.15 (real 60%).

So the world does have homes from calm to busy, and no two are alike (no exact duplicate texture in
any draw). But which home is calm is decided almost entirely by how big its always-on load happens to
be. A big always-on draw makes a home big and calm at once. Real homes differ by size mostly through
**active** use: above-base use p90 is 18.7 kWh/day in LCL against the world's 8.8 (the section of
2026-10-06 near midnight). That is the same missing spread L2.4 measures (scale spread 1.9-2.4 against
5.38). At a given size, a real home's texture still varies widely.

**The flats in the twin line are not established.** LCL records no dwelling type, so "a rough tail of
small busy flats" is prose rather than a measured fact. In the world, flats' median texture is
0.151-0.164 against 0.129-0.149 for houses, with a similar p90. Nothing here is keyed on dwelling type.

**GAP: the between-home spread of active use at a given household size.** The world draws a home's
active electricity from its headcount, owned stock and routine. No source in the knowledge layer gives
how much homes of one size differ in it. EFUS 2011 gives only a range of mean hourly demand (121 W
to 2,438 W, n 79). The candidates to read first are DESNZ NEED's consumption by household
characteristics (the stratified source L2.4's anchor names) and HES 2012's per-household appliance
totals, if HES publishes their spread. LCL cannot be the source, because LCL is the comparison. A
per-home intensity multiplier tuned until these quantiles match would be circular, so none is built.

**What was built.** A comparator in `tests/harness/test_premise_two_level.py`: a Fisher-z two-sample
test of the world's texture~kWh/day correlation against LCL's −0.32 (n 313). On the drawn 60 it reads
r −0.665, z −3.27, and it is pinned as a strict xfail. A companion control shows that both of its
branches are reachable on the drawn 60's own textures: dealt at random they pass, and dealt in size
order they fire. Two mutations were run: a constant True and a constant False result. Each reds the
companion, and the constant False result also turns the strict xfail into an XPASS. **No world draw
changed**, so the world digest and the value arms do not move.

**The always-on draw, one variable** (added the same day, after landing). This checks the causal
sentence above. The drawn 60 was regenerated with only `standby_kw` held at the old uniform 25 W, both
arms in one process. No prediction was filed before the run.

| drawn 60 | r(texture, kWh/day) | median texture | kWh/day p10/50/90 | under real p10/25/50/75 |
|---|---|---|---|---|
| drawn always-on (live) | −0.665 | 0.161 | 4.4 / 6.7 / 12.7 | 3 / 14 / 27 / 44 |
| uniform 25 W | −0.469 | 0.213 | 3.7 / 5.1 / 8.0 | 0 / 3 / 10 / 28 |

So the always-on draw does tighten the coupling (−0.47 → −0.67), and it is also what brought the
median onto the real one. Narrowing it is **not** the remedy, because that undoes the median and the
real base-load match. Even at 25 W the world is more size-bound than LCL, though not significantly
at n 60 (z ≈ −1.2). The −0.95 recorded on 2026-10-06 was an earlier world with the full stock in every
home, so it does not compare to either row. What is missing is a spread of active use that does not
travel with the always-on draw.

Limits: four seeds and one weather site. Whole-meter LCL carries electric-heated homes, which are big
and calm, so net of heating the real coupling is probably weaker than −0.32. That makes the comparison
lenient to the world. The section of 2026-10-06 does not name the estimator behind LCL's −0.32. It is
taken here to be linear Pearson on kWh/day, and the comparator depends on that. The log-kWh
correlations above are world-only. A NEED search found consumption-change and stock medians, but no
spread of electricity at a given household size, so the GAP stands.

*Correction, 2026-10-14: the GAP is closed. NEED's Table A14 (by number of adults) publishes p5–p95, not only
the medians quoted in 2026-07. See the 2026-10-14 section below.* Scripts: `/var/tmp/se-w129/.scratch_w129/` (not committed).

## NEED publishes the spread at a given household size, and a per-home use intensity is not the texture remedy (2026-10-14)

Worker on the self-refill draw of `W1_29`. **The GAP above ("no source gives how much homes of one size
differ") is closed by a table the 2026-07-23 read already had and quoted only for its medians.** DESNZ
NEED 2026 (published June 2026), `Consumption_additional_EW_2024.xlsx`, Table A14 ("Electricity
consumption by number of adults", Experian-modelled adults, England and Wales). It publishes p5, p10, p25,
median, p75, p90 and p95 for each adult count and year. 2022 electricity year, whole meter, kWh:

| adults | share | p10 | p25 | median | p75 | p90 | p90/p10 | p75/p25 |
|---|---|---|---|---|---|---|---|---|
| all | 100% | 1,043 | 1,630 | 2,539 | 3,946 | 6,195 | 5.94 | 2.42 |
| 1 | 36% | 850 | 1,278 | 1,946 | 3,121 | 5,198 | 6.12 | 2.44 |
| 2 | 38% | 1,366 | 1,944 | 2,774 | 4,060 | 6,179 | 4.52 | 2.09 |
| 3 | 13% | 1,541 | 2,225 | 3,200 | 4,653 | 6,940 | 4.50 | 2.09 |
| 4 | 5% | 1,700 | 2,502 | 3,624 | 5,262 | 7,775 | 4.57 | 2.10 |

2016, 2019 and 2024 have the same shape: p75/p25 is 2.0–2.5 at every adult count. Knowing the adult count
narrows the real spread very little. A14 is whole-meter and includes electric-heated homes. The cleaner
comparison is `Consumption_multiple_attributes_EW_2024.xlsx`, which gives quartiles for each region ×
property type × age × bedrooms × gas present × meter type cell. Weighted by sample size, the geometric
mean p75/p25 **inside one cell, gas present, standard meter** is **2.08 in 2022** (2.04–2.16 across
2020–2024). Even a home's region, dwelling and fuel leave a real p75/p25 of about 2.1.

**The world, same quantity.** Four draws of 1,000 homes (`draw_premise_population`, base seeds 17, 18,
19, 23, as of 2022-05-01; traces seed 7, C1 weather Jan–Apr 2022; `annual_kwh("electricity")`; origin
`3b9848300` code). Gas-heated homes, p75/p25 at a given adult count: **1.45–1.66** (1 adult 1.57–1.66, 2
adults 1.48–1.57, 3 adults 1.45–1.57). Gas homes' log-variance of annual electricity is 0.148–0.151, and
87–89% of it sits within an adult count. A lognormal reading of the real cell quartiles puts that
within-size variance at about 0.29 (σ ≈ ln 2.08 / 1.349). **So the world has about half the real
between-home variance at a given size, and corr(log kWh, log always-on) is 0.78–0.79.** What spread it
has comes mostly from the always-on draw.

**Two one-variable arms, each pre-registered** (`/var/tmp/w129need/PREDICTION.md`, filed before the run).
240 homes, seeds 17 and 18, read as the L1.1 cell reads them (net of both machines). A per-home
multiplier m = exp(σz) was keyed on the premise id. σ = 0 reproduced the control to the last digit, and
the seed-17 control reproduces the 2026-10-13 row (17 / 73 / 134 / 197). Nothing ships.

| seed 17 / seed 18 | control | arm 1: m on `appliance_intensity` (σ 0.5) | arm 2: m on every event rate + lighting + electronics kW (σ 0.5) |
|---|---|---|---|
| gas p75/p25, 1 adult and 2 adults | 1.57, 1.57 / 1.63, 1.51 | 1.60, 1.60 / 1.64, 1.47 | **1.83, 1.70 / 1.79, 1.76** |
| corr(texture, kWh/day) | −0.671 / −0.662 | −0.671 / −0.665 | −0.621 / −0.604 |
| texture p10 / p25 / median / p75 / p90 (real 0.072 / 0.117 / 0.158 / 0.208 / 0.311) | 0.079 / 0.107 / 0.147 / 0.189 / 0.235 | 0.081 / 0.107 / 0.146 / 0.188 / 0.236 | 0.081 / 0.106 / 0.145 / 0.192 / 0.238 |
| under real p10 / p25 / median / p75 | 17 / 73 / 134 / 197 | 19 / 75 / 138 / 195 | 18 / 76 / 137 / 196 |
| L1.1 verdict | FAIL / FAIL | PASS / FAIL | PASS / FAIL |
| L2.4 p90/p10 (real 5.38) | 2.97 / 3.56 | 3.15 / 3.55 | 3.74 / 3.84 |
| median annual kWh | 2,801 / 2,820 | 2,797 / 2,861 | 2,857 / 2,902 |

The L1.1 verdict flips on seed 17 within the cell's own sampling noise, because the leg counts barely move.
Read it as noise, not as an effect.

**Graded.** Arm 1 refuted P1–P3: `appliance_intensity` reaches only washing, dishwashing, drying and
vacuuming, about a tenth of use. P4 held. Arm 2: Q1 held in 3 of 4 cells (1.70–1.83 against 1.75–2.05).
**Q2 was refuted**: |corr| fell 0.05–0.06, not ≥ 0.10. Q3 held on seed 17 (+0.77) and was refuted on
seed 18 (+0.28). **Q4 was refuted**: p90 texture moved +0.003 and −0.013, and the rough tail did not appear.
Its other half held: the p25 leg did not improve. Q5 was refuted: the median rose 2–3%, not 5–15%.

**What this settles.**
1. **A per-home intensity on active use is a lever on L2.4, the size spread, and not on L1.1.** It
   widens the within-size spread toward NEED's, but it neither creates the rough tail nor loosens texture's
   coupling to size. In this world a home's texture is set by its always-on share. Scaling the active part
   moves the home's size and its steps together, so the ratio barely moves.
2. **The sourced target for that lever now exists.** A within-size p75/p25 of about 2.1 comes from NEED,
   not LCL, so sizing a per-home intensity on it would not be circular against L1.1's LCL comparison. It
   belongs to L2.4's open "a stratified source should replace it" (`RATE_BANDS`, the L2.4 anchor), and it
   should be built under that cell, not as W1_29's remedy.
3. **W1_29's L1.1 red is in what makes a home rough or calm at a given size**: the rough tail (p90 0.24
   against 0.31) and too many calm homes in the middle. Neither more always-on nor more active volume
   produces that. The remaining candidates are the ones the 2026-10-07 section named and nobody has
   tested. One is how much of a home's active use comes in short high-power bursts against long low ones
   (kettle-and-oven homes against TV-and-lights homes). The other is a night floor that moves from night
   to night. Neither has a published per-home distribution in the knowledge layer.

Limits: A14's adult count is Experian-modelled, and the world's is `adult_count` (people minus children),
so the two definitions differ. The world reads Jan–Apr annualised, while NEED reads a Feb–Jan year. The arm
multiplier is lognormal by choice, and σ 0.5 is an envelope, not a fit. Scripts: `/var/tmp/w129need/` (not
committed).

## The size spread has to ride with the always-on load, and it still does not loosen texture from size (2026-10-15)

Worker on the self-refill draw of `W1_29`, at `origin/main` `fc015460d`. The section above (2026-10-14)
was committed as `997f78bf7` on a fork of the shared tree that never reached origin. It is carried
here unchanged. Every prediction below was filed before its run (`/var/tmp/se-w129b/PREREG.md`). Nothing
ships: no world draw changed.

**NEED, read per dwelling.** The 2026 anonymised 50k sample (`anon2026_50k.csv`, the file
`tools/need_stock_joint.py` reads) was filtered to gas-heated homes (`MAIN_HEAT_FUEL` 1) with no PV and a
valid 2022 reading, giving n 36,150. Within each `PROP_TYPE` × `FLOOR_AREA_BAND` cell of n ≥ 200 (16 cells), the median
p90/p10 of annual electricity is **4.09** (3.66–4.96). The median log-sd is **0.567**, the pooled
within-cell log-sd is **0.562**, and the log-sd over all homes is 0.601. So dwelling type and floor area
explain about 13% of the log-variance. The figure agrees with the 2026-10-14 reading of the published cell
quartiles (σ ≈ ln 2.08 / 1.349 = 0.54), and it is a second route to it rather than the same table. On the world's
side, 4 seeds × 240 homes, gas no-PV, read in the same cells (`fp.floor_area_m2`): the pooled within-cell
log-sd is **0.394–0.409** and the median cell p90/p10 is 2.43–2.75. Pre-registered as 1.8–2.6: the direction held and
the range was refuted on 2 of 4 seeds.

**Where the world's spread sits** (seed 17, n 240, gas no-PV, Jan–Apr kWh/day): the meter's mean is 8.08.
The always-on load is 3.27 of it (40.5%) with an sd of 3.42, against the meter's sd of 3.88, and its
correlation with log meter is +0.80. The event appliances are 2.16 (26.8%) with an sd of 0.66. Cold appliances
are 0.92 and the boiler's auxiliaries 0.36. The world's between-home size is its always-on draw.

**A coupled arm, one variable.** Active use (the event rate, lighting kW, electronics kW) was multiplied per
home by (always-on ÷ 90 W)^β. That is the opposite of the 2026-10-14 arm, which drew its multiplier
independently of the base. Seed 17, n 240:

| β | within-cell log-sd (NEED 0.562) | L2.4 p90/p10 (real 5.38, floor 4.88) | L1.1 under p10/25/50/75 (expected 24/60/120/180) | texture p90 (real 0.311) | r(texture, kWh/day) (LCL −0.32) |
|---|---|---|---|---|---|
| 0 (control) | 0.401 | 2.97 | 17 / 73 / 134 / 197, FAIL | 0.234 | −0.671 |
| 0.5 | 0.499 | 4.01 | 24 / 73 / 130 / 186, PASS | 0.260 | −0.697 |
| 1.0 | 0.618 | 5.83 | 26 / 78 / 129 / 176, FAIL (p25) | 0.276 | −0.646 |

**Graded.** P8 held: the within-cell spread rises, 0.50 and 0.62. P6 was refuted: r did not rise above −0.55
at any β, and the comparator fires throughout (z −5.1 to −6.1). P7 was refuted: the median of always-on ÷ mean
moved 0.32 → 0.30, not to 0.20–0.25.

**What this adds to the 2026-10-14 section.**
1. **The L2.4 lever has a shape as well as a size.** An independent σ 0.5 multiplier reached an L2.4 of only 3.74.
   A multiplier tied to the always-on load reaches NEED's within-cell spread and LCL's 5.38 at the
   **same β, about 0.7** (interpolated, not run). Those are two independent anchors, from two publishers, agreeing on one
   number. The physical reading is that a home with more devices left on also uses more. It is a belief, with β
   bounded by the two anchors, and no published source states that coupling. **GAP: the correlation of a
   home's always-on load with its active use.** EFUS 2011 §4.1's per-home base-load table is the first
   place to read. That is L2.4's build, not W1_29's.
2. **It confirms by a second route that no volume lever loosens texture from size.** Coupled or independent, r stays at
   −0.65 to −0.70. What sets a world home's texture is its always-on share, and scaling the active part with
   the base moves both of them together.
3. **An electric shower is not the texture remedy, and this was argued, not run.** The world's gas homes
   have none (`_dhw_fuel_kwh` sends all their hot water to gas), but HES (Powering the Nation 2, 2014) puts
   showers at 112 kWh/yr, 2.7% of an average home. L1.1 is the MEDIAN half-hour step over the mean, and a
   shower moves 2–4 of a day's 48 steps, so it cannot shift a median. It may matter to a peak or L1.1n
   reading. A first event-rate arm (σ 0.3–0.7 on `appliance_intensity` alone) moved nothing, which repeats
   the 2026-10-14 arm 1.

The texture red therefore stays where the 2026-10-14 section left it: in how a home's active use is split
between short, high-power bursts and long, low draws, and in a night floor that moves. Limits: one seed for
the coupled arm, and Jan–Apr against NEED's Feb–Jan year. The world's always-on ÷ mean here is the
drawn base over the whole meter, not LCL's p5 estimator, so its level does not compare with the LCL row
above, only its movement does. Scripts: `/var/tmp/se-w129b/` (not committed).

## A home's active use rides with its always-on load: measured in LCL, built at β 0.7 (2026-10-15, L2.4)

Delivery seat, lane-0 draw `l2-4-the-active-use-rides-with-the-always-on-load`, at `origin/main` `7ac5bf514`.
Every prediction was filed before its run (`/var/tmp/se-l24/PREREG.md`). **This section is the knowledge page
for the build (K8), and the build is in the same commit.**

**What is published.** EFUS 2011 (`9_Domestic_appliances__cooking_and_cooling_equipment.pdf`) §4.1–4.2 was read in
full. It gives base load (power exceeded 90% of the time, 10-second data, n 79) and mean hourly demand (121–2,438 W,
median 447 W) only as two separately sorted per-home charts (Figs 10 and 11). It says in prose that the high
tail correlates with "high TV and appliance ownership … and high base load power", but it publishes no joint, no
correlation and no slope. The HES 2012 early findings put standby at 5.1% of use, with no per-home joint either.
**GAP: no publication states the coupling.** It is therefore built as a stated belief, with its β measured.

**Measured from Low Carbon London raw** (the same 13 partitions as the 2026-10-06 read, Std tariff). One estimator is
applied identically on both sides. Per home: base = the 5th percentile of its half-hourly kW, and active = mean − base.
The statistic is the OLS slope b of ln(active) on ln(base). Homes with a zero p5 are dropped and counted: 23 of 313 in
Jan–Apr and 20 of 305 in Jun–Aug.

| | n used | b | r |
|---|---|---|---|
| LCL Jan–Apr 2013 | 290 | **0.459** | 0.518 |
| LCL Jun–Aug 2013 (little electric heating) | 285 | 0.384 | 0.543 |

P1 (r 0.30–0.60), P2 (b 0.40–0.90) and P3 (summer within 0.20) held.

**The estimator is calibrated on the world, not taken at face value.** The p5 base is noisy, and active = mean − base
shares that noise. So β was chosen where the world's *estimated* b matches LCL's b, and β was never set equal to b.
The placebo arm (true β 0) reads b = 0.11 (P4 held, [0, 0.35]). Seed 17 / seed 18, n 240, C1 Jan–Apr 2022, whole
meter, all homes:

| true β | est. b | within-cell log-sd (NEED 0.562) | L2.4 p90/p10 (LCL 5.38, floor 4.88) | r(texture, size) | L1.1 |
|---|---|---|---|---|---|
| 0 | 0.11 / – | 0.401 / – | 2.97 / 3.56 | −0.671 | FAIL / FAIL |
| 0.5 | 0.37 / 0.34 | 0.499 / 0.502 | 4.01 / 4.42 | −0.70 / −0.68 | PASS / FAIL |
| 0.6 | 0.42 / 0.39 | 0.521 / 0.524 | 4.28 / 4.75 | −0.70 / −0.68 | PASS / FAIL |
| **0.7** | **0.47 / 0.44** | **0.543 / 0.546** | **4.57 / 5.05** | −0.69 / −0.67 | PASS / FAIL |
| 1.0 | 0.63 / 0.60 | 0.618 / 0.621 | 5.83 / 6.16 | −0.65 / −0.62 | FAIL / FAIL |

**β = 0.7.** The two seeds' estimated b average 0.459, which is LCL's b to three places, so P5 held. The two
out-of-fit anchors both sit just under the real value at β 0.7. NEED's within-cell spread is 0.54 against 0.56, and
L2.4 is 4.6–5.1 against 5.38. That is the safe side (F11): β was not raised to clear the floor. **So L2.4 may still
read red on some populations, seed 17's 4.57 among them.** The summer b (0.384) would put β nearer 0.6. Range
0.6–0.8.

**What did not move:** texture's tie to size (r −0.67 to −0.69, against LCL's −0.32). This repeats the 2026-10-14 and
2026-10-15 arms, so W1_29's L1.1 red is untouched by this build.

**Built:** `simulation/premise_trace.py` `active_use_multiplier` = (always-on ÷ 90 W)^0.7. It multiplies the
people-scaled event rate (`appliance_intensity`), lighting kW and electronics kW. A caller holding the old world
fixed passes `active_use=1.0`. The built path reproduces the β 0.7 probe row above to the last digit on both seeds.
**The world redraws, so the world digest moves and the value-arms artefacts need re-taking.**

Limits: LCL is London, 2013, and whole-meter, and some of its Jan–Apr homes heat electrically (hence the summer
check). The p5 estimator is not EFUS's p10-of-10-second base. Two seeds of 240. Scripts: `/var/tmp/se-l24/` (not
committed).

## Real homes differ most in their bursts, and giving the world that spread still does not loosen texture from size (2026-10-15)

Worker on lane-0 draw `w1-29-bursts-against-long-draws`, at `origin/main` `025ca62ae` (β 0.7 coupling and storage
off-peak charging both live). Every prediction was filed before its run (`/var/tmp/se-w129c/PREREG.md`). Nothing ships:
no world draw changed.

**What is published, per home and per category.** No source in reach publishes a per-home split of active use into
short bursts and long draws. HES 2012's final report (Intertek R66141 §7.5, Figs 289–324) gives the split as averages
by household type only. Its early findings and its consumer-archetypes report (Element Energy, seven clusters) add no
per-home composition either. The HES microdata (UK Data Service) were not read. **But Powering the Nation 2 (DECC/DEFRA
2014, pp. 79–87, "Assess electricity demand for products with high agency") publishes Student t-tests per appliance
category**, giving group sizes, means and t. The within-group SD can be backed out as s = |m1 − m2| ÷ (|t| √(1/n1 + 1/n2)),
assuming the pooled-variance test. Over the household-size rows (|t| ≥ 1):

| category (HES population) | s, kWh/yr (per row) | mean | CV |
|---|---|---|---|
| kettle (owners, n ≈ 234) | 90 / 92 / 94 / 95 | 168 | **0.55** |
| electric cooking, all homes (n 249, gas cooks included) | 268 / 283 / 293 / 294 | 450 | **0.64** |
| lighting (n 246) | 491 / 505 / 510 | 491 | 1.03 |
| audiovisual (1-person row only) | 473 | 541 | 0.87 |
| washing machine | 116 / 119 / 123 / 126 | 158 | 0.77 |

The rows agree to a few percent, and the kettle mean matches HES Table 14's 167. That supports the pooled-t reading.
PtN2 says the same thing in prose: "a factor of 16 difference between energy use for lighting in the highest and
lowest households, but only 2.3 for cold appliances".

**The world, same quantity** (seed 17, n 240, C1 Jan–Apr 2022, the meter's own event and switching draws, annualised):

| | mean kWh/yr | CV (HES) | corr(log x, log meter) |
|---|---|---|---|
| kettle (owners) | 164 | **0.06** (0.55) | +0.09 |
| cooking class (kettle, toaster, microwave, oven, hob) | 438 | **0.34** (0.64) | +0.27 |
| lighting | 209 | 0.98 (1.03) | +0.79 |
| electronics | 356 | 1.01 (AV 0.87) | +0.79 |
| washing machine | 231 | 0.83 (0.77) | +0.84 |

**So the world's long draws already carry the real between-home spread, and all of it rides the meter.** The β 0.7
coupling did that. The bursts carry almost none: every cooking spec is `scales_with_people=False`, so neither headcount
nor `active_use_multiplier` reaches it. Every home's expected kettle use is identical, and what spread the class has
comes from gas cooking and ownership. The burst-against-long-draw composition is therefore wrong in exactly the
direction the 2026-10-14 section suspected. Big homes get more smooth load and the same bursts.

**The arm, one variable.** A per-home, mean-one lognormal factor exp(sz − s²/2) on the five cooking specs'
`events_per_day`, with z keyed on the premise id alone (independent of base and size). s = 0.48 is the sourced value,
filling the gap between ln(1 + 0.64²) and the world's ln(1 + 0.34²). s = 1.0 is an envelope. A manipulation check
confirms the factor reached the events: at s 0.48 the cooking CV reads 0.62, against HES's 0.64.

| seed | r control | r at s 0.48 | r at s 1.0 | texture p90, control → s 0.48 | L2.4, control → s 0.48 |
|---|---|---|---|---|---|
| 17 | −0.691 | −0.694 | −0.660 | 0.267 → 0.267 | 4.57 → 4.78 |
| 18 | −0.671 | −0.675 | −0.641 | 0.273 → 0.274 | 5.05 → 5.13 |
| 19 | −0.685 | −0.692 | −0.659 | 0.265 → 0.265 | 5.03 → 5.27 |
| 23 | −0.672 | −0.677 | −0.637 | 0.262 → 0.267 | 5.12 → 5.36 |

The comparator fires in every cell (z −4.9 to −6.1). The L1.1 leg counts move by at most 5, which is noise. The p90
texture under the β 0.7 world is now 0.262–0.273 (it was 0.232–0.240 on 2026-10-13), against the real 0.311.

**Graded.** P1 held (−0.671 to −0.691). **P2 was refuted low:** at the sourced spread r did not rise at all (it moved
−0.003 to −0.007), where 0.04–0.12 was predicted. **P3 was refuted low:** the envelope moved r by +0.026 to +0.035,
against 0.08–0.20. P4 held at its floor: p90 moved 0.000–0.005 and the median less than 3%. P5 held. Census C1:
cooking held, kettle held in direction (0.06 against a predicted 0.10–0.30), and lighting was refuted (0.98 against a
predicted 0.4–0.7). The prediction assumed the long draws were narrow, and they are not.

**What this settles.**
1. **Composition of active use, as bursts, is not W1_29's lever.** Even with the real spread, and even doubled, the
   cooking bursts move r by under 0.04. They are ~13–15% of a meter and fill a few of a day's 48 steps, so they cannot
   carry the median step. This closes the last candidate the 2026-10-14 section named on the active-use side.
2. **What is left is the night floor that moves from night to night,** which is the other candidate named there, and
   an LCL-side split nobody has run. Apply r(texture, size) to LCL's own p5 base share and to its active texture
   (median step ÷ (mean − p5)), and the same to the world. That says whether the gap lives in the base share or in the
   steps per unit of active use. The LCL raw partitions are no longer cached, so it was not run here.
3. **A fidelity defect independent of texture:** the cooking class does not scale with headcount and has no
   between-home spread, which contradicts PtN2's owner-only kettle rows (one-person homes 116 kWh/yr against 189,
   t −5.6). It is appended to `SEAT_FINDING_THE_KETTLE_DOES_NOT_SCALE_WITH_HEADCOUNT_IN_HES_2026-10-09.md`
   (atom W2_30), which fitted the kettle flat. It is not built here, because it moves the world digest and the
   value arms, and the arm above shows it buys W1_29 nothing.

Limits: the pooled-t back-out assumes equal group variances; if PtN2 ran Welch's test, s shifts by a few percent. HES
is 2010–11, 250 owner-occupiers. Four seeds, one weather site, Jan–Apr. Scripts: `/var/tmp/se-w129c/` (not committed).

## The world's gap is in both halves, and a night floor alone cannot clear it (2026-10-15)

Lane-0 draw `w1-29-texture-gap-base-share-or-steps`, at `origin/main` `836ec06fa` (β 0.7 world). Every prediction was
filed before either side was read (`/var/tmp/se-w129d/PREREG.md`). Nothing ships: no world draw changed.

**One estimator on both sides.** Texture T is `fgl.half_hourly_texture`. Base share S is the p5 half-hour ÷ mean.
Active texture A is the median step ÷ (mean − p5). These obey T = A × (1 − S), so the split is exact. Size is
kWh/day, and r is Pearson on linear kWh/day, which is the comparator's form. LCL: the same 13 partitions,
re-fetched by HTTP range from the London Datastore, Std, Jan–Apr 2013, ≥ 100 complete days, whole meter.
World: n 240, seeds 17/18/19/23, C1 Jan–Apr 2022, traces seed 7, netted as `_netted_texture_and_size` nets
(the script asserts T matches it to 1e-12). **Instrument checks held.** LCL gives n 313, r(T, size) −0.316 and
a median A of 0.214 (0.213 on 2026-10-06). The world's comparator r is −0.691 / −0.671 / −0.685 / −0.672, which
matches the 2026-10-15 burst-arm controls.

| | r(T, kWh/day) | r(S, kWh/day) | r(A, kWh/day) | S p10 / 50 / 90 | A p10 / 50 / 90 | share of cov(log T, kWh) via log(1−S) / log A |
|---|---|---|---|---|---|---|
| LCL Std (n 313) | −0.316 | **−0.033** | **−0.346** | 0.048 / 0.213 / 0.412 | 0.093 / 0.214 / 0.377 | −0.05 / 1.05 |
| world, 4 seeds (n 240 each) | −0.671 to −0.691 | **+0.463 to +0.517** | **−0.581 to −0.608** | 0.22 / 0.37 / 0.54 | 0.13 / 0.24 / 0.40 | 0.26–0.28 / 0.72–0.74 |
| gap, Fisher z (world − LCL) | −5.6 to −6.1 | **+6.2 to +7.0** | **−3.5 to −4.0** | | | |

**Graded.** P1 held: LCL's r(S, size) is −0.03, so a real home's base share does not depend on its size. P2 held:
the world's is +0.46 to +0.52. P3 held (−0.346). **P4 was refuted:** the world's r(A, size) is −0.58 to −0.61,
past the predicted floor of −0.55. **P5 held by its stated rule:** S carries the larger gap (z +6.2 to +7.0
against A's −3.5 to −4.0).

**But both halves carry a significant gap, and the decision rule was too coarse to say what to do next.** In real
homes, all of texture's size coupling comes through the active steps (105%), and none comes through the base share.
In the world, about three quarters of it still comes through the active steps. A counterfactual on the measured
rows settles the next step. Deal the world's S at random across its homes (200 deals per seed). That keeps S's
distribution and removes its tie to size. T' = A × (1 − S) then reads **r −0.51 to −0.54** (deal range −0.45 to
−0.58). With S held at its median, r is −0.58 to −0.61. The comparator fires below r ≈ −0.46 at n 240. **So a
night-floor arm that only loosens the base share from size cannot clear W1_29's comparator, even if it works
perfectly.** It also has a level to fix: the world's median base share is 0.37 against 0.21. The world's
active steps are also tied to size more tightly than real ones (−0.59 against −0.35). In the world, a home with
more active use has smoother active use, and in real homes much less so.

**What this means for the next test.**
1. The night floor stays worth testing, but for the **level and the size tie of S** (median 0.37 against 0.21, r +0.49
   against −0.03), not as the remedy for r(T, size). Its prediction should be written against S, and should expect r(T)
   to move by at most about +0.15.
2. **The second lever is A's tie to size**: why a world home's steps per unit of active use fall with its volume. The
   β 0.7 coupling scales lighting and electronics kW, which are long, smooth draws, with the always-on load. So a big
   world home's active use is mostly smooth draw. That fits the 2026-10-15 burst table (lighting and electronics
   corr(log x, log meter) +0.79). The candidate to read first is whether real big homes add *more events* or *bigger
   smooth draws*. No source in the knowledge layer separates the two per home. **GAP.**

Limits: LCL is whole-meter, London 2013, and includes some electric-heated homes. The world is netted of both
machines. A is undefined for 2 LCL homes with a zero median step, which are excluded from the log decomposition
only. The counterfactual shuffles measured S, so it does not run a world. The p5 estimator is the same noisy base
as the L2.4 section, on both sides. Scripts: `/var/tmp/se-w129d/` (not committed).

## Big world homes grow by smooth draw; growing them by events loosens texture from size (2026-10-15)

Lane-0 draw `w1-29-active-steps-smooth-with-volume`, at `origin/main` `8f92f93ca`. Predictions P1–P5 were filed
before any arm ran, and P6–P7 were filed after P1–P5 were read but before their own arms ran
(`/var/tmp/se-w129e/PREREG.md`). Nothing ships: no world draw changed.

**Method.** The estimator is the same as in the section above (A = median step ÷ (mean − p5), netted meter, Pearson on
kWh/day, n 240, seeds 17/18/19/23). Each home's behavioural stream is split per half hour, read from the generator
itself. Lighting L and electronics D are `switched_units_on` × per-unit kW. Events E is behavioural − standby − cold −
L − D, and it is never negative. β 0.7 multiplies E's people-scaled rate **and** L and D's kW. The arms regenerate the
world with β moved: `ev_only` (β on the event rate, L and D at β 0), `le_only` (β on L and D kW only), `b0`, and
`ev_hi_b` (L and D at β 0, event rate × (always-on ÷ 90 W)^b). "L2.4 slope" is ln(mean − p5) on ln(p5) over the
**netted** meter. This is not the shipped L2.4 estimator. It reads 0.43 on the live world against the shipped
0.444–0.475, and LCL's whole-meter figure is 0.459. **Instrument check held.** Live r(A) reads −0.608 / −0.581 /
−0.586 / −0.588, matching `01d99f7c3`.

| arm (4-seed mean) | r(A, kWh/day) | r(T, kWh/day) | r(S, kWh/day) | L2.4 slope | sd ln kWh/day | r(T) with S dealt at random |
|---|---|---|---|---|---|---|
| LCL Std (n 313) | −0.346 | −0.316 | −0.03 | 0.459 (whole meter) | | |
| live (β 0.7 on all three) | −0.591 | −0.680 | +0.49 | 0.43 | 0.548 | −0.52 |
| `le_only` | −0.496 | −0.678 | +0.56 | 0.27 | 0.480 | −0.41 |
| `ev_only` (b 0.7) | −0.468 | −0.676 | +0.59 | 0.25 | 0.470 | −0.38 |
| `b0` | −0.236 | −0.665 | +0.62 | 0.05 | 0.406 | −0.17 |
| `ev_hi_1.4` | −0.516 | −0.563 | +0.26 | 0.50 | 0.576 | −0.46 |
| `ev_hi_2.1` | −0.341 | −0.287 | −0.29 | 0.82 | 0.764 | −0.32 |

**Graded.** P1 held: in the live world, the share of active energy in lighting and electronics rises with size
(r +0.55 to +0.58). P2 held: per unit of volume, the L+D stream steps 0.23 against events' 1.29. With events
removed, r(A) is −0.62 to −0.65, so the smooth draws on their own are tied to size. P3 held: `ev_only` gives −0.468.
**P4 refuted:** `le_only` gives −0.496, so β on either channel ties A to size, and the two effects add. P5 held:
`b0` gives −0.236. **P6 refuted, in the direction against the prediction.** Raising β on events alone until L2.4's
slope is restored (b 1.4, slope 0.50) gives r(A) −0.52, not ≤ −0.55. It also loosens T (−0.56 against live −0.68),
halves S's size tie (+0.26 against +0.49) and keeps the size spread (0.576 against NEED's within-cell 0.562). **P7
refuted:** dealing S at random clears the comparator's −0.46 in four arms, not only in `b0`.

**What it means.** A world home that is big because it leaves more on is big mostly through **smooth** load. That
load is standby (which raises S) plus lighting and electronics (which smooth A). Spread over a longer-lit, more-
watched day, a bigger home's steps shrink against its volume. When the same coupling is routed through **events**,
a big home is big through bursts. Its steps then grow with its volume, and both halves of texture loosen from size.
At roughly matched L2.4 slope (b ≈ 1.2–1.4), the event channel helps on three readings at once (A, S's size tie and
the size spread). On its own it does not clear the comparator (r(T) −0.56 against −0.46), and b 2.1 overshoots
L2.4's slope by 0.36. The β 0.7 coupling's *size* was measured. **Its *channel* (which loads carry it) was a
modelling choice, and this measurement says it matters.**

**GAP, before any build (K8).** No source in the knowledge layer says whether a real home with a higher base load
uses more appliance *events* (more cycles, more appliances owned: dishwasher, tumble dryer, electric shower) or
bigger *smooth* draws (more rooms lit, more screens on longer). HES ownership and cycle counts by household
type are the first place to read. LCL's own r(A, size) of −0.35 alongside a 0.459 slope is consistent with the
event channel, but it does not establish it. **Next:** read that, then pre-register a combined arm (event channel at
the b that restores the shipped L2.4 estimator, plus the night floor for S's level of 0.37 against 0.21) against
the comparator, L2.4 and NEED's spread together.

Limits: these are the same as above. One weather site, Jan–Apr, the L2.4 slope is read on the netted meter, and the
arms are counterfactual worlds, not candidate builds. Scripts: `/var/tmp/se-w129e/` (not committed).
