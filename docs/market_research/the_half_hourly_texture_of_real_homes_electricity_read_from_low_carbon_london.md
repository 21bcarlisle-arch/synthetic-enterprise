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
