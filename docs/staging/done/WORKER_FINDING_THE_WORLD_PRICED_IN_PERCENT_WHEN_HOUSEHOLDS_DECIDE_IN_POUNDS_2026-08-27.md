# The world priced in percent when households decide in pounds — and the elasticity spread was three times too wide

**Date:** 2026-08-27. **Author:** the delivery seat.
**Occasion:** director — *"does the switching decision key on £ saved or % saved? It changes the
economics completely… Find what our world uses, find what the evidence says, and if they differ, fix
the world and say what moved."* They differed. This says what moved.

**Standing instruction applied throughout:** *"derive them from published evidence, not from what
makes the arm look good… If the honest read of the evidence is ambiguous, choose the option that
makes per-customer pricing harder to win, record why, and move on — erring against our own thesis is
the safe direction."*

---

## 1. THE EVIDENCE BASE

Ofgem / BMG Research, **Understanding Consumers' Energy Tariff Choices** — conjoint choice
experiment, **n = 3,235** GB energy bill payers, representative on 2021 census targets; fieldwork
29 Mar – 9 Apr 2024; published July 2025. Feature importance: **annual savings 41%, customer service
rating 32%, exit fees 22%, tariff type 5%.**

## 2. £ OR %? — POUNDS, and the world had it wrong

**The evidence.** *"We found that consumers value savings in absolute terms rather than in
proportion to their bill. This means that it may benefit suppliers to frame savings in cash rather
than percentage terms, i.e. £150 and not a 3% saving — particularly for customers with higher energy
outgoings."* And: *"Reported household spending on energy has a very limited impact on how consumers
evaluate prospective deals."* Its Table 3 is the same finding inverted — the Spearman correlation
between energy SPEND and switching propensity runs **−0.07 to +0.05**, so a big bill barely changes
how eagerly a household chases a given *number of pounds*.

**What the world did.** `_savings_to_rate`, the DESNZ-calibrated curve, has ALWAYS been a function
of an absolute annual saving in £. But the conversion into it multiplied the household's percentage
differential by `CALIBRATION_ANNUAL_BILL_GBP = 1700.0` — **one market-average bill, for every
household**. A 3,000 kWh flat and a 25,000 kWh house priced 10% above the market were modelled as
facing the same £170 shortfall. The world was effectively percentage-keyed.

**The fix, and it needed no recalibration.** The curve was already in the right units; only the scale
was wrong. `churn_position_multiplier` and `offer_position_multiplier` now take `annual_bill_gbp`,
and the renewal decision derives it from **what we have actually billed this household over the
trailing year, summed across ALL its supply points**.

```
              +10% dearer      churn multiplier      old world
    bill £600                      x1.24              x1.96
    bill £1,700                    x1.96              x1.96      <- exact regression anchor
    bill £8,000                    x9.20              x1.96
```

At the calibration bill it reproduces the old world to the bit, so this is a **re-scaling, not a
re-levelling**, and any moved figure is attributable to households having different bills.

**What it means economically, which is the director's point and not a refactor.** Customer value now
scales with consumption: a large home is cheaper to win and dearer to lose per point of margin,
because the same percentage buys a more visible saving. A percentage world cannot express that.
**And consumption is OBSERVABLE** — so unlike the hidden sensitivity axis, this is structure the
company can legitimately act on. It is the first genuinely inferable structure in this part of the
world.

Three R15 details worth keeping: the bill **sums both fuel legs** (scoring a dual-fuel home on
electricity alone understates the money at stake — this repository has already paid once for
reasoning about one leg of a two-leg household); it returns **`None`, not a guess**, when there is no
settled history, because inventing a bill would put a fabricated number inside a churn decision; and
the window **cannot see past the term start**, so it stays Point-in-Time safe.

## 3. THE SPREAD WAS THREE TIMES TOO WIDE — and derived from intuition, not evidence

The first version of `PRICE_SENSITIVITY_WEIGHT` was **1.5 / 1.0 / 0.4**, a **3.75x** high-to-low
ratio, reasoned from intuition about disengaged households and labelled "asserted".

The published subgroup range for savings-importance is **35%–44%**, mean 41%, across *every* group
Ofgem reports:

| subgroup | savings importance |
|---|---|
| rates own supplier 0–2 stars | 44% |
| aged 65+ · highly financially vulnerable | 42% |
| overall · "doing well financially" | 41% |
| aged 18–34 (weights service 37% instead) | 35% |

Each weight is now that subgroup's importance over the **share-weighted population importance**
(40.4%), making the population mean exactly 1.000 by construction rather than by a fudge factor:
**1.089 / 1.015 / 0.866 — a 1.26x ratio.** The invented spread was **three times too wide, in the
direction that makes per-customer pricing look more winnable than it is.**

**The negative finding, recorded because it is the answer and not a gap.** GB households weight price
remarkably homogeneously. Ofgem states it directly: *"feature importance scores are generally quite
stable across different groups"*, and *"highly vulnerable consumers have scores that are close to
identical (42%) for price savings to those doing well financially (41%)"*. **There is very little in
this axis for any supplier to infer, and that is a fact about GB households rather than a modelling
gap.**

The heterogeneity that IS large and published lies elsewhere, and both are more inferable:
**satisfaction with the current supplier** (Table 4 — at a 1-star alternative, 57% of 1–1.5-star
raters switch against 39% of 5-star raters, a **1.46x** spread, larger than anything price
sensitivity shows; already in the world as `satisfaction_score` with a universal curve, and a
supplier observes its own service failures), and a **17%** minority who *"disproportionately
prioritise exit fees over other factors"* — a real published segment with a different decision rule,
and exit fees are not modelled in this world at all.

## 4. BETWEEN-GROUP IS THE WRONG QUANTITY — within-segment variance now drawn

Director: *"The Ofgem subgroup range is a between-group statistic — it says nothing about spread
between individuals, and elasticity is typically close to orthogonal to observables. That's why
couponing, time-limited offers and price walks work at all: you can't tell in advance who
responds."*

Correct, and the first version used the three subgroup means as if they were the whole distribution
— modelling a world where a household's segment gave its elasticity *exactly*. That is not a small
spread; it is the wrong quantity.

`price_elasticity_for_customer` now returns **segment mean × a lognormal within-segment draw**, mean
1.0, strictly positive, from its own C-S2 substream so the existing cohort draw is untouched.
Measured over 4,000 households: mean 0.996, SD 0.591, 5th–95th percentile **0.35x – 2.13x**.

`PRICE_ELASTICITY_SEGMENT_R2 = 0.02` — the segment explains 2% of elasticity variance. **Anchored
conservatively and against our own thesis:** Ofgem's own Table 3 puts an observable's correlation
with switching propensity at r ≤ 0.07, i.e. **r² under 0.5%**. 2% is four times *more* generous than
that measurement, and more irreducible variance is the direction that makes per-customer pricing
harder to win, which is the standing rule for an ambiguous read.

## 5. THE DISCOVERABILITY FLAG WAS DECORATIVE, AND TWO OF ITS THREE CLAIMS WERE FALSE

`hidden_truth_only` in `segmentation_curriculum_v1.json` was read by **no code anywhere** — a claim
in a data file with nothing behind it, which is the prose-only failure MAKE_IT_STICK names.

- **`price_sensitivity`** claimed *"discoverable via rate-change churn response"*. Nothing wired it
  to the churn response. **Now true**, as of this wiring — kept `false`, with the channel named.
- **`channel_pref`** claimed *"discoverable via the contact channel actually used"*.
  `contact_propensity.py` keys on the ENGAGEMENT archetype and never reads it. **Marked hidden.**
- **`green_stance`** was already honest: hidden, no observable, and must never acquire a proxy.

Both false claims made their axis undiscoverable *in principle* while the curriculum promised a
route: a supplier that tried would be right to try and would fail forever, and the failure would read
as a weak company model rather than as an absent channel.

**Enforced, not merely corrected.** `tests/simulation/test_discoverability_claims_are_enforced.py`
requires every axis claiming discoverable to carry a PROBE that runs the world's decision and shows
two households differing only in that axis facing different outcomes. Not a grep — *a mention is not
a use*, found five times in one day. Mutation-proven: restoring the `channel_pref` claim fires two
tests; reverting restores green.

## 6. A FAIL-OPEN I SHIPPED FOR AN AFTERNOON, AND A HARNESS THAT MEASURED NOTHING

**The fail-open.** When elasticity went continuous, callers began passing floats to
`price_sensitivity_weight`. It looked them up: `PRICE_SENSITIVITY_WEIGHT.get(1.5, 1.0)` → **1.0**.
Every household silently received the neutral weight and the entire per-household draw was
discarded, with nothing raised and every function still exported. The *"unknown is 1.0"* kindness —
written for an unrecognised **label** — quietly absorbed a completely different kind of unknown.
Caught within the hour by its own wiring test, which asserts a DIFFERENCE and so could not pass on a
world that had gone homogeneous.

**The harness.** `noise_floor.py` patched `price_sensitivity_for_customer`, which the decision had
stopped calling. The patch reached nothing; every seed ran the identical world; **two different
seeds returned byte-identical pounds and pence** while the tool reported a noise floor. Caught only
because the pennies matched. It now counts invocations and **aborts** rather than reporting.

**Four instances of one class in a day**, and the discriminator is sharp: the controls that failed
LOUD were the ones asserting that something must *change*; the ones that failed QUIET asserted a
value. A control keyed to a structure that moved goes silent unless it demands a difference.

---

*Evidence: Ofgem/BMG 2024 as cited. Code: `simulation/market_switching_propensity.py`,
`simulation/population_draw.py`, `simulation/customer_events.py`,
`docs/design/segmentation_curriculum_v1.json`. 231 tests green across the affected simulation
suites; epistemic verifier PASS on 548 files. R13: mechanism is baseline/fidelity; the MARGINALS
remain the director's, and the mean-preservation control reads the curriculum file so a change to
them fails loudly rather than silently converting fidelity into difficulty.*
