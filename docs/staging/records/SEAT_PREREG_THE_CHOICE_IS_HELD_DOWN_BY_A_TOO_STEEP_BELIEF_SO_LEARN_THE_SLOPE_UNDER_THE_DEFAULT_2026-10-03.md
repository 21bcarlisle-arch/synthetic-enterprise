# The choice is held down by a too-steep belief, so learn the slope under the default

**Pre-registered 2026-10-03 by the delivery seat, before any run of the change below.**

## What the belief curves show

Source: `/var/tmp/se-probe-out/probe_bel_{default,61001}.json`. These are the first probe runs to
record the company's believed P(stay) beside the world's at every level-grid offer (ac465ac38).

Belief / truth, mean over decisions, by renewal year (default path; 61001 agrees to within a few
points):

| year | n | margin 10 | margin 30 | margin 55 |
|---|---|---|---|---|
| 2017 | 24 | 0.72 / 0.76 | 0.49 / 0.70 | 0.35 / 0.62 |
| 2018 | 16 | 0.50 / 0.71 | 0.30 / 0.66 | 0.19 / 0.57 |
| 2019 | 12 | 0.95 / 0.66 | 0.87 / 0.61 | 0.71 / 0.49 |
| 2020 | 12 | 0.94 / 0.37 | 0.94 / 0.31 | 0.90 / 0.18 |
| 2021 | 9 | 0.78 / 0.33 | 0.64 / 0.28 | 0.51 / 0.22 |

Pooled drop in P(stay) from margin 10 to margin 55: **believed 0.259, true 0.155** (default path;
0.262 / 0.160 on 61001).

**Two different errors.**

1. **LEVEL, by regime.**
   - **Before the cap** the belief is too pessimistic. It prices the move from the old rate, and a
     first renewal moves +45-75% off the acquisition rate.
   - **From 2019** it reads the offer's gap to the default. An offer under the default reads as
     almost no reason to leave, so the belief sits at 0.9+ while the world keeps 0.2-0.7.
2. **SLOPE.** Pooled, the belief is about 1.7x too steep: the company thinks its customers are far
   more price-sensitive than they are.

**Why the slope, not the level, holds the price down.** A level error that scales P(stay) the
same at every candidate leaves the argmax where it is. A too-steep slope moves the argmax down.
That matches the stayer-pays grading (`..._STAYER_PAYS_THE_DEFAULT_...`):
- the capped rule chooses a median margin of GBP 18-26;
- the best flat level in hindsight is GBP 55-60.

B8 (`discovered_price_sensitivity`) learns exactly this flatter slope from the company's own
closed renewals. It was refuted earlier today (-37) because the value rule was then pricing above
the default, so learning "less sensitive" pushed already-dominated offers higher. Under the
default, that reason is gone.

## The change

No new mechanism. `VALUE_ARM_CAPPED_LEARNED_POLICY` sets both existing switches:
- `renewal_stayer_pays_at_most_default`;
- `learn_price_response`.

The probe scores it as rule `value_capped_learned`.

## Predictions, written before the run

On the four 2025 paths (default, 61001, 61002, 61003):

- **L1.** value_capped_learned's median chosen margin is higher than value_capped's on every path,
  by at least GBP 5/MWh.
- **L2.** value_capped_learned - value_capped > 0 on at least 3 of 4 paths.
- **L3.** value_capped_learned - (the best flat level in hindsight) is less negative than
  value_capped - (the same level) on at least 3 of 4 paths.
- **L4 (the bar that matters).** value_capped_learned beats a flat level chosen IN ADVANCE on at
  least 3 of 4 paths. The level is the company's flat target margin
  (`TARGET_MARGIN_GBP_PER_MWH`), i.e. the 'flat' rule, scored on what the world bills. I expect
  this to hold, because capped already beats flat by 4.7-6.4k.

  L4 is weak. The stronger in-advance bar is a level fixed before 2016 from published margins, and
  none is established in the knowledge layer. So the honest strong bar remains "beats the best
  level in hindsight", which **I predict is NOT reached (L3 only narrows the gap).**

## Grading

Filled in below after the runs.
