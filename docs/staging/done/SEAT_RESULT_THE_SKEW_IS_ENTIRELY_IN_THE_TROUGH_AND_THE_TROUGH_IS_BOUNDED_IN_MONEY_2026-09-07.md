**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — A49, the skew not the spread)

# RESULT — the skew is entirely in the trough, and the trough is bounded in money

**Verdict: MERELY RARER.** An extreme-day-only time-of-use tariff is not a better product than one
that pays every day. It is a strict subset of it, worth 39% of an everyday tariff that is itself
worth 74p per household-year under perfect foresight, against a sourced £27.50 acquisition cost.

Instrument: `tools/tou_extreme_day_concentration.py` → `docs/observability/tou_extreme_day_concentration.json`.
Pre-registered at `SEAT_PREDICTION_WHAT_AN_EXTREME_DAY_ONLY_TOU_TARIFF_CAN_AND_CANNOT_BE_WORTH_2026-09-07.md`,
landed at `bc656c72f` **before this module existed**. Eight predictions: **five held, three were
refuted**, and the most important one was refuted.

---

## 1. The headline, which refutes the premise I was given

The direction I was working to said 2024-2025 has "by far the FATTEST tail (p90 6.67 against the
landed panel's 3.38)" and asked whether the concentration makes the product better or merely rarer.
The p90 figure is correct. **The inference from it is not**, and this is the project's own named
recurring failure: *before dividing two numbers, say out loud what each one counts.*

Write the two quantities out. Both are already in the code:

```
ratio_d  = peak_rel_d / off_rel_d
saving_d = mean_d × (1 − off_rel_d)      ← achievable_saving_per_kwh is mean minus cheapest.
                                            The dearest window is not in it at all.
```

As the overnight trough collapses toward zero, the **ratio diverges without bound** and the
**saving converges on the day's mean price and stops**. The ratio is unbounded in exactly the thing
the money is bounded by. So a day of near-zero overnight prices posts a spectacular ratio and a gain
that has already saturated, and no further collapse adds a penny.

Measured, not argued — a variance decomposition in logs, where `ln ratio = ln peak_rel − ln off_rel`
is additive:

| | 2016-2020 | 2021-2023 | 2024-2025 |
|---|---|---|---|
| **Var(ln peak_rel)** — the peak side | 0.02221 | 0.02220 | **0.02212** |
| **Var(ln off_rel)** — the trough side | 0.19418 | 0.22987 | **0.42507** |
| trough share of the two | 89.7% | 91.2% | **95.1%** |
| p90 of peak_rel | 1.618 | 1.581 | 1.600 |
| p10 of off_rel | 0.463 | 0.425 | **0.241** |

**The peak side has not moved in ten years — 0.0222, 0.0222, 0.0221, flat to three decimal places.**
Every bit of the widening is the trough. The p90 ratio doubled because the denominator halved.

And the money saturates where the ratio does not: p90 of `saving/mean` runs 0.537 → 0.575 → 0.759
against a hard ceiling of 1.0, while the p90 ratio ran 3.39 → 3.71 → 6.67 against no ceiling at all.

**So the value distribution did not get more concentrated. It got less.** Top decile of days by
value, PC1-weighted: **26.5% (2016-2020) → 28.2% (2021-2023) → 24.5% (2024-2025)**. The episode with
the fattest ratio tail in the record has the *flattest* value distribution of the three.

This is the commercially load-bearing part. As renewables push overnight prices to zero and below,
the price ratio a time-of-use tariff can advertise explodes while the money it can deliver
saturates. **The headline ratio is becoming steadily less informative about the product**, and a
supplier marketing "6:1 overnight savings" would be quoting a number whose growth is bounded to
nothing.

## 2. The structural answer, which was arithmetic and was written down first

Company value sums non-negative per-day terms, so an extreme-day tariff sums a **subset** of the
everyday tariff's days and cannot beat it at a common pass-through and response model. Pre-registered
as arithmetic rather than claimed as a discovery, and enforced in the module by
`assert_the_subset_cannot_beat_the_whole`, which runs on the live figures every run.

The whole commercial question is therefore displaced onto **cost avoided** and a **called-day
attention premium**, neither of which is established anywhere in the knowledge layer. Neither is
invented here. Both are carried as break-evens.

2024-2025, slope-only response, PC1-weighted, per household-year:

| product | days paid on/yr | company | household | reachable value |
|---|---|---|---|---|
| everyday | 324.8 | **£0.7392** | £0.7541 | 82.5% |
| extreme, top 25% | 80.9 | £0.4947 | £0.5149 | 39.2% |
| **extreme, top 10%** | **32.5** | **£0.2916** | £0.3035 | 20.6% |
| extreme, top 5% | 16.0 | £0.1892 | £0.1930 | 12.3% |
| extreme, top 1% | 3.0 | £0.0733 | £0.0704 | 3.9% |

**The two break-evens, at the top decile:**

- **Running cost: 0.1345 pence per household per day.** The everyday tariff would have to cost more
  than an eighth of a penny per household per day to run, before dropping to extreme days is worth
  doing. Nothing in `docs/market_research/` or `docs/domain_artefact_library/` establishes a
  per-household-day running cost for a domestic TOU tariff.
- **Attention premium: 2.53×.** Called-day response would have to be more than two and a half times
  the standing-tariff response. Arcturus 2.0 does not model a called-day effect. **NESO's Demand
  Flexibility Service is the real GB product that pays only on called days** and is where this could
  be settled — that is the single highest-value open question this leaves.

The premium break-even is **2.47× / 2.48× / 2.53×** across the three episodes. It barely moves with
the price level, because it is a property of the shape distribution and not of the level — which is
the same lesson the landed panel closed the spread question with.

## 3. What dominates all of it

| | everyday | extreme top 10% |
|---|---|---|
| company £/household/year | 0.7392 | 0.2916 |
| **payback on a sourced £27.50 CAC** | **37.2 years** | **94.3 years** |

Both products are worth pence per household-year against an acquisition cost the book actually
spends, **under perfect foresight of which days are extreme**. Choosing between them is a rounding
error inside a product that does not clear recruitment on this book at this price shape. The
household side is no better: the everyday tariff hands a household **75p a year**, which is not a
proposition anybody switches supplier for.

## 4. Three things the instrument found that nobody asked for

**a. The days the product most wants are the days the model cannot price.** 81 of 731 days in
2024-2025 (11.1% of days, **17.5% of the year's gross value**) have a non-positive cheapest window —
negative wholesale prices. The saving on such a day is well-defined and large; the *ratio* is
meaningless rather than large, and Arcturus is a function of its logarithm. That share has risen
6.6% → 10.0% → **17.5%** across the episodes. The everyday product can only reach 82.5% of the
year's value for this reason alone, and the blind fraction is growing fastest of any number here.
They are carried in the concentration and excluded from the products, with the money stated both
times, rather than dropped.

**b. A tariff triggering on a published spread calls the wrong days.** Top decile by value and top
decile by ratio overlap with a Jaccard of just **0.368** in 2024-2025 (35 days in common out of 65
in each). Value ranks on level × shape; the ratio ranks on shape alone. A product whose trigger is
an advertised price spread selects one set and earns on the other.

**c. The payout is not something a household can be recruited against.** With a fixed £58.45/MWh
trigger held across the whole record — which is what a real tariff would carry, rather than a rank
recomputed inside each year — the qualifying days per year run: 3, 1, 2, 1, 2, **78, 154, 49**, 17,
26. **2022 alone carries 46.6% of the decade's extreme-day value**; 2017 carries £0.63 against
2022's £156.67, a 250-fold range. Four of ten years fall below half the median. This product's
payout is a crisis derivative wearing a tariff's clothes.

## 5. And it is a ceiling, because the day cannot be called

Every product figure above assumes **perfect foresight** of which days are extreme. We hold no
day-ahead auction series, so the real skill is a **named gap, not a number**. Two skill-free floors,
2024-2025:

| caller | days called/yr | recall | precision | share of extreme-day VALUE |
|---|---|---|---|---|
| persistence (call tomorrow iff today was) | 36.5 | 27.4% | 27.4% | 28.3% |
| winter (Nov–Feb, every day) | 120.4 | 52.1% | 15.8% | 56.9% |

The truth lies between these and the ceiling, and **the ceiling is already worth pennies**.

---

## The pre-registration, scored beside the claim

| | prediction | outcome |
|---|---|---|
| P1 | top decile ≥35% of value in 2024-25 (40–55%); 25–32% in 2016-20 | **REFUTED.** 24.5% and 26.5%. Not only below the band — the wrong way round. The fattest ratio tail has the flattest value distribution. This refutation is the finding. |
| P2 | ≥50% of the everyday product's value is the fitted intercept (55–75%) | **REFUTED.** 43.2% (£0.7392 slope-only against £1.3007 fitted). Large and directionally right, below the bound I set. |
| P3 | everyday slope-only under £1.00; extreme delivers 40–70% of it | **SPLIT.** £0.7392 ✓. Extreme delivers 39.4% — just outside the band. |
| P4 | running-cost break-even under 1p/household/day (0.1–0.4p) | **HELD.** 0.1345p. |
| P5 | attention premium ≥2× (1.8–3.0×) | **HELD.** 2.53×. |
| P6 | persistence recall under 30% (15–25%) | **HELD** on the bound, 27.4%; above my point band. |
| P7 | biggest year ≥25% of decade value; ≥1 year under half the median | **HELD, and understated.** 46.6%, and four years under half the median. |
| P8 | payback >19 years for everyday, longer for extreme | **HELD.** 37.2 and 94.3 years. |

I was right about the economics and wrong about the physics. I predicted the value was concentrating
because the ratio tail was fattening, and it was not: **I made the same mistake the direction did,
in the same file, and only the measurement caught it.** The verdict rule fixed in advance returned
MERELY RARER on either reading, which is the only reason the refutation of P1 did not change the
answer.

## Controls

`tests/tools/test_tou_extreme_day_concentration.py` — 20 tests, each named for the defect it exists
to catch. **Poison round run before this was written**, because "survived" is ambiguous: six
mutations, six kills by the intended control, baseline green after restore.

| mutation | killed by |
|---|---|
| decomposition always blames the trough | `test_a_varying_peak_against_a_fixed_trough_is_attributed_to_the_peak` |
| subset guard made a no-op | `test_it_refuses_when_a_subset_product_out_earns_the_whole` |
| slope response keeps the intercept | `test_it_keeps_the_papers_slope_and_only_drops_the_constant` |
| PC1 allocation falls back to flat | `test_pc1_weights_a_winter_day_above_a_summer_day_and_flat_does_not` |
| break-even divides by the year, not days avoided | `test_the_running_cost_break_even_is_per_household_DAY_and_not_per_year` |
| unpriceable days leak into products | `test_a_product_of_only_unpriceable_days_refuses_instead_of_returning_zero` |

Both legs are asserted on every partition — the decomposition's mirror leg especially, because a
decomposition hard-wired to answer "trough" would have produced this document's headline out of
nothing.

## What is next

1. **Settle the attention premium against NESO's DFS.** It is the one number that could change this
   verdict, the real GB product that pays only on called days exists, and 2.53× is a research
   question somebody can answer rather than a hedge. `W1_9_dsr_flex_markets` already holds a DISCOVER
   pass on DFS and records `_DFS_RATE_GBP_PER_MWH = 4.5` and `_DISPATCH_EVENTS_PER_YR = 20` as
   **company-authored constants with no world behind them** — so the atom that would answer this is
   already on the map, at level 0, and its own discovery pass says the constants are handed rather
   than discovered.
2. **The blind 17.5% is the fastest-moving number in this artefact** and it is growing. A response
   function that cannot price a negative-price day is going to be wrong about a larger share of the
   value every year. That is a knowledge-layer gap, not a code defect.
3. **Do not spend more on the spread.** Two instruments have now closed on the same answer from
   opposite directions: the level moved, the shape did not, and the shape's one real change is on
   the side that is bounded in money. A third cut of the same panel will not say anything new.
