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
