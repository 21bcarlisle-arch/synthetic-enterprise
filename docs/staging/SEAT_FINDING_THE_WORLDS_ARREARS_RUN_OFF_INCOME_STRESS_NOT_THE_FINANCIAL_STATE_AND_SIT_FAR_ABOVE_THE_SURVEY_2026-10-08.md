**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series`

# The world's arrears run off income_stress, not the financial-vulnerability state, and the share behind sits far above the survey

**Fate (2026-10-15):** ATOM -- folds into `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-12, clear-the-decks):** ATOM -- rank and act on the three explanations (definition, driver, level) for the 31% vs 7.6% gap; a fidelity decision for the director, blind to company results (P2)

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

## Where the three explanations stand on 2026-11-25, and the one run that is left

Re-read against the tree at origin 3311aa1b20, before any new number:

1. **The definition: done.** `tools/grade_world_debt_against_ofgem.py` counts Ofgem's own stock
   (a bill unpaid more than 91 days at a quarter end, electricity, every billed account in the
   denominator) against arrears plus debt (5.1%, Q4 2019). The three-seed pool read MET at 1.19x
   (cbfccfc029). The 31% "any failed payment in a year" here was not that quantity.
2. **The level: done for the DD tier.** `_DD_FAILURE_PROB`'s LOW level is the register's sourced
   first-presentation return rate; the MODERATE/HIGH ratios stay a named simplification.
3. **The driver: changed, not by this finding's route.** Since 2026-10-20 `BUDGET_DECIDES_PAYMENT`
   is on: a residential credit bill the household's margin and savings cannot cover is not paid
   and stays unpaid until later money clears it (`background/live_payment_triad.py`,
   `simulation/household_budget.BudgetPaymentBook`). `income_stress` now drives only the transient
   per-bill draw. But V2 (`simulation/vulnerability_state.financially_vulnerable`) is still drawn
   on its own substream, independent of that budget, and still drives nothing. The world holds two
   financial states: the one that decides payment, and the one named for it.

**What V2 is, before it is counted:** "cannot save or absorb an unexpected expense" (§10.1 of
`debt_and_collections.md`; CIM W5, 30% prevalence, RR 3.6 [2.8, 4.6] for being behind).

**The run (pre-registered 2026-11-25 ~12:45 UTC, before the capture started).** One capture to
2019-12-31 at origin 3311aa1b20, default dice. Reading: electricity accounts behind >91 days at
the four 2019 quarter ends, pooled, account-clustered, split by (a) V2 and (b) a budget state
defined by prevalence alone, because nothing published sets a pound threshold: the 30% of drawn
households with the least of savings buffer plus 12 x the 2019 margin. Predictions:

- **Q1.** RR(V2) has a 95% interval containing 1.0 (independent draw, drives nothing).
- **Q2.** RR(budget state) is at or above 2.8, the published lower bound, and I expect above 4.6
  (the budget is what decides sustained non-payment, so the world's gradient should be steeper
  than the survey's).
- **Q3.** The pooled share is inside 1.0-2.0x Ofgem's 5.1% (the budget path has moved it since
  the 1.19x pool; direction not predicted).

If Q1 and Q2 hold, the remedy is a definition, not a fidelity change to arrears: derive V2 from
the budget (one state, two readings), which moves no payment draw. If Q2 fails, the budget does
not carry the survey's gradient, and re-keying arrears is the director's fidelity call.

## The run, graded (2026-11-26, against the predictions above)

The capture ran on 25 Nov (to 2019-12-31, default dice, 1,412 s); the split script was written at
12:30 UTC, before it, and read the capture unchanged on 26 Nov. Between 3311aa1b20 and a3b2a7a0c8
the modules it reads (`household`, `household_budget`, `vulnerability_state`, the grader) did not
change; `live_population` moved only `CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE`, which the
split does not read. 338 electricity accounts, 1,133 account-quarters, 42 accounts behind.

| | point | 95% (account bootstrap) | prediction | |
|---|---|---|---|---|
| Q1 RR(V2) | 0.57 | 0.18-1.16 | interval contains 1.0 | **held** |
| Q2 RR(budget bottom 30%, savings + 12 x margin < £15,535) | 1.42 | 0.70-2.66 | >= 2.8, expected > 4.6 | **failed** |
| Q3 pooled >91-day share | 9.97% (1.96x Ofgem's 5.1%) | 6.9-13.2% | inside 1.0-2.0x | **held, at the edge**; the grader reads NOT MET, HIGH |

V2 and the thin budget overlap on 8.6% of accounts; independence predicts 0.29 x 0.30 = 8.7%. V2 is
the independent draw this finding said it was.

**Exploratory, not pre-registered** (same capture, written after the Q2 answer): bottom 30% by
savings alone (< £3,234) RR 0.94 (0.42-1.78); by 2019 margin alone (< £658) RR 1.43 (0.69-2.71);
margin below zero (8% of accounts) RR 1.10 (0.23-2.72). No reading of the budget carries the
survey's gradient. Every upper bound sits just under 2.8, so the sample cannot exclude a modest
gradient. It does exclude 3.6 on each split.

**What this says.** The pre-registered branch is the second one: the budget decides whether a bill
is paid, but the world's >91-day stock is not concentrated in the households that cannot absorb a
shock. The stock is still near 2x Ofgem's level. Explanations, ranked by the evidence here:
(1) the stock is carried by the transient `income_stress` draw (failed bills that settle late or
never) more than by the budget path, so who is behind is close to random with respect to resilience;
(2) the survey's RR 3.6 is for self-reported "behind", not a 91-day stock, and need not transfer
(erring against our thesis, assume it does); (3) power, with 42 accounts behind: weak, because
every split's point estimate is <= 1.43. Not yet measured: the share of the 2019 stock's bills whose
non-payment came from the budget book rather than the per-bill draw. That reading comes first in
any build.

**Disposition.** Re-keying what drives sustained arrears is a fidelity change to the world. The
pre-registration reserved it for the director, so it is raised in `for_the_director` with a
recommendation, and the work item is parked on his answer. Nothing in the world was changed.
