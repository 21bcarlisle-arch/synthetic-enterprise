**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted`

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
