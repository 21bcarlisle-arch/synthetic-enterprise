**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The world's arrears run off income_stress, not the financial-vulnerability state, and the share behind sits far above the survey

*Found 2026-10-08 by the hidden-vulnerability build (director's ruling: vulnerability drawn as a
hidden household state). Recorded, NOT retuned. Changing what drives arrears is a fidelity
decision, to be taken blind to company results.*

## Measured (80 founders to 2019, 160 domestic households, 419 household-years)

"Behind" here means at least one failed payment in the year.

| state | share behind, in state | share behind, rest | relative risk (95% CI) | knowledge |
|---|---|---|---|---|
| PSR-type (prevalence 0.544) | 0.288 | 0.337 | 0.86 (0.64-1.14) | 1.45 (1.09-1.94) |
| Financially vulnerable (0.231 here; 0.30 at n = 20,000) | 0.333 | 0.304 | 1.10 (0.78-1.53) | 3.6 (2.8-4.6) |
| income_stress not LOW | 0.656 | 0.251 | 2.61 (2.02-3.37) | none |

## What it shows

1. **Neither latent state predicts arrears in the world.** Arrears follow `income_stress`
   (simulation/arrears_engine.py `_DD_FAILURE_PROB` by stress). It starts LOW for every household
   and moves only on life events, so it is not the 30% financial state the survey describes.
2. **The world's share behind, 31%, is far above the survey's 7.6%** (Ofgem CIM W5,
   docs/market_research/debt_and_collections.md section 10). The definitions differ: one failed
   payment in a year is not "behind on energy bills". Part of the gap is definitional, and how much
   is not yet known.

## Explanations to rank before changing anything

1. **The definition.** Measure the world's share by the survey's own question: arrears outstanding
   at a point in time, not any failed payment. Cheap, and it should come first.
2. **The driver.** If the measure is like for like and the world is still high, or still flat
   across the financial state, link arrears to the financial state at the published relative risk
   (3.6) in place of, or beside, income_stress. That is a fidelity change.
3. **The level.** The `_DD_FAILURE_PROB` levels are unanchored (gb_domestic_bill_payment_failure_and_
   arrears_prevalence.md:113-115). If 1 and 2 leave a level gap, it is the place to look.

This sits beside SEAT_FINDING_THE_WORLD_LOSES_FORTY_PERCENT_AT_EACH_ANNIVERSARY_... in the same
lane. Both are world rates far above published ones, and both bias every retention and debt result
the company is graded on.
