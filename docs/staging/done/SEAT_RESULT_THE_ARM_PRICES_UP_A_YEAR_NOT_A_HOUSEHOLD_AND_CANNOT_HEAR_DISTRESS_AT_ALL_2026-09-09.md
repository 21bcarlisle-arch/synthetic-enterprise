**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — find where the renewal rule prices up the households it then loses) · **Class:** measurements_that_mirror

# RESULT — the renewal arm does not price up a household feature. It prices up a YEAR, and it cannot hear a household in distress at any price.

Graded against
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_ARM_PRICES_UP_WHAT_IT_BELIEVES_IT_WILL_LOSE_2026-09-09.md`,
written before any statistic over the 123 rows was computed. **Three of seven predictions were
refuted and the headline mechanism was in none of them.** Everything is reported the way it fell.

Subjects: `docs/observability/value_cycle_ab_s1_three_arm_20260909.json` (world digest
`39a192ce04c1eda8`, producing commit `62334dc76`) and
`company/pricing/value_based_renewal.decide_margin` as it stands at HEAD.

---

## The answer, in one paragraph

The Lane 0 item asked which household features the renewal rule prices up. **It prices up almost
none of them, and the frame was wrong.** Of the seven observables swept one at a time, five reach
the price and two — `bill_shock_count` and `satisfaction_score` — **cannot change the answer at any
value**, because `enriched_churn_estimate` reduces its two channels with `max(rate_est,
payment_est)` and the rate channel wins at every price this arm chooses. The same `max()` run the
other way is what actually moves the margin: in a year whose published cap moved a long way, the
rate channel is netted to nothing, the belief goes **flat in the arm's own price up to
130 GBP/MWh**, and the maximiser has no retention left to trade off. The chosen margin at the
anchor household is **88.25 GBP/MWh in 2019 and 160.00 in 2022** — the crisis year, priced hardest,
by the same rule, on an identical household. And on the run's own 123 scored decisions the chosen
margin predicts departure at **AUC 0.667**, which **survives conditioning on the arm's own belief
at 0.651** — so the arm is not merely optimising against a one-sided objective it understands. It
is buying departures its own churn model did not see coming.

## The predictions, graded

| | prediction | outcome |
|---|---|---|
| **P1** | Spearman(believed_p_retain, chosen_margin) negative, \|ρ\| ≥ 0.30 | **SPLIT.** ρ = **−0.2199** — direction confirmed, magnitude **refuted** |
| **P2** | mean believed_p_retain lower for departures | **CONFIRMED.** 0.6243 (n=40) against 0.7236 (n=83); reproduces the published AUC 0.6270 to four places |
| **P3** | chosen margin's own AUC against departure in 0.55–0.70 | **CONFIRMED.** **0.6667** over 3,320 pairs. Mean margin 48.98 for departures against 34.30 for survivors |
| **P4** | within-belief-quartile margin AUC falls to 0.45–0.58 | **REFUTED.** Pooled within-stratum AUC **0.6513** over 783 pairs. 0.6667 → 0.6513 is **no mediation at all** |
| **P5** | chosen margin non-increasing in `eac_kwh` | **REFUTED, and backwards.** It **rises** monotonically, 74.75 → 93.00 GBP/MWh from 1,000 to 12,000 kWh |
| **P6** | chosen margin non-decreasing in `bill_shock_count` | **REFUTED, and not by degree.** It is **exactly flat**: spread 0.00 GBP/MWh across 0, 1, 2, 3 and 5 shocks |
| **P7** | `expected_value_gbp` charges nothing for a departure | **CONFIRMED.** `p_retain × annual_contribution × annuity_factor` — the departure branch contributes exactly zero |

**P4 is the one that mattered and it is the one that fell.** I predicted the belief would mediate
the margin's selection of departures, which would have made this a clean one-sided-objective
finding: the arm knows and harvests anyway. It does not know. Holding the arm's own belief fixed,
the margin still ranks departures at 0.651 — the belief is **not a sufficient statistic for the
arm's own price**, which is exactly what a `max()` that discards the price channel produces.

## What I did not predict, and it is the finding

Not one of the seven predictions is about `max()`. The pre-registration reasoned about the
objective and about the estimate's accuracy, and the mechanism is neither: it is the **reduction**
between the two channels.

```
result = max(rate_est, payment_est) × market_pressure × payment_method_engagement
```

Exactly one channel is ever live. `docs/observability/renewal_rule_price_response.json`, produced
by `tools/renewal_rule_price_response.py`:

| swept input | margin spread | verdict |
|---|---:|---|
| `cost_to_serve_gbp_per_year` | 33.50 | LIVE |
| `fuel` | 30.75 | LIVE |
| `eac_kwh` | 18.25 | LIVE |
| `tenure_years` | 4.25 | LIVE |
| `credit_risk` | 4.25 | LIVE |
| **`bill_shock_count`** | **0.00** | **SILENCED** |
| **`satisfaction_score`** | **0.00** | **SILENCED** |

And by year, at one unchanged household:

| year | market move | belief flat to | chosen margin | believed p_retain |
|---:|---:|---:|---:|---:|
| 2017 | 0.00 | 12.0 | 113.25 | 0.5289 |
| 2019 | 0.00 | 12.0 | 88.25 | 0.5034 |
| 2020 | −0.05 | 5.0 | 80.50 | 0.4702 |
| 2021 | 0.17 | 45.0 | 110.00 | 0.5930 |
| **2022** | **0.67** | **130.0** | **160.00** | **0.9574** |
| 2024 | −0.21 | 0.5 | 92.25 | 0.4429 |

The 2022 row is the whole shape. The netting is defensible on its own terms — a supplier who raised
prices by less than the market did not become less competitive, and `market_conditions` says so in
its own docstring. Composed with a per-customer expected-value maximiser and an objective that
charges nothing for a departure, it becomes **charge the ceiling in the year the household could
least afford it**, and the arm believes it will lose 4% of them.

The book agrees. On the run's own 123 scored decisions, the two highest-margin years are 2017 and
2018 at mean margins 55.93 and 53.24, with realised departure rates **0.524 and 0.476**; the two
lowest are 2025 and 2021 at 17.79 and 18.00, with departure rates **0.071 and 0.200**.

## Why P5 fell, since it is a real correction to how I was reasoning

I predicted a bigger household would be protected — more volume at risk, more to lose. The
arithmetic says otherwise and printing it took seconds. `expected_value_gbp` is
`p_retain × (margin × eac_mwh + fixed_revenue − cost_to_serve) × annuity`. The fixed revenue and
the cost to serve do not scale with volume, so on a **larger** household the margin term dominates
the contribution sooner and the optimum sits further up the grid. The rule protects the household
whose standing charge is a large share of its bill — the **small** one — and harvests the large
one. That is the opposite of the intuition I filed, and no amount of further reasoning would have
caught it.

## What this does and does not establish

* **Direction, not magnitude.** One world, one seed, 123 scored decisions on the belief population
  and 161 on the fixed-horizon estimand. These are different populations under different matching
  rules and **nothing here is netted against a figure from there.**
* Decisions are clustered on accounts. The AUCs carry no account-level standard error and the
  pair counts are not independent observations.
* **The sweep is a statement about the function, not about the book.** A LIVE row proves an input
  *can* reach the price at the anchor inputs; it says nothing about how often it varies. A
  SILENCED row is the stronger claim, and it is structural: the silencing is a comparison being
  lost, not a term being absent — `test_the_max_switch_can_throw_both_ways` holds that apart.
* **This does not price the repair.** Whether combining the channels rather than switching between
  them improves the realised book is a three-arm question and needs its own run. It is not
  answerable from a response surface and is not claimed here.

## The control, and what it cost to make it able to fail

`tests/tools/test_renewal_rule_price_response.py` — seven legs, and an eight-poison battery run
before the green was trusted. **Three poisons survived the first draft** and each was a real hole:

1. Cutting `bill_shock_count` to a single swept value passed everything — an unexercised input
   reads exactly like a structural silencing. Now a refusal in the producer and a leg in the test.
2. Wiring the payment channel to `0.0` passed everything — `max()` broke the resulting 0–0 tie
   toward "payment", so the switch read as throwing both ways while one side was identically
   absent. `channel_that_binds` now reports `"tie"` and publishes `margin_of_the_win`.
3. Removing the market-move netting from the reporter passed everything — nothing called it on a
   year whose netting mattered. Now reconciled against the estimator's own deadband.

And one control was simply wrong: the first draft of the reconciliation asserted over every year
and went red on 2023, because `flat_to` reports the first rung when there is no deadband at all.
The rule was wrong, not the code. It is fixed, and the vacuity guard (`checked >= 1`) is there
because skipping years is exactly how that leg could come to reconcile nothing.

## What is next, ranked

1. **The `max()` is the defect and it is filed separately** —
   `SEAT_FINDING_THE_RENEWAL_ARM_CANNOT_HEAR_A_HOUSEHOLD_IN_DISTRESS_AND_PRICES_THE_CRISIS_YEAR_HARDEST_2026-09-09.md`.
   A household sliding into arrears cannot change its own renewal price. That is a fidelity defect
   and a fairness one, and it is the same shape in both directions.
2. **The objective has no departure term** (P7). `saas/opex_ledger.py` carries sourced
   `CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER` / `..._SINGLE_FUEL_CUSTOMER` figures against
   `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`. The arm values a departure at **£0** while
   the company's own books carry a sourced cost to replace them. That is a one-line composition
   with a sourced constant already in the tree — and it is the first thing to try, because it is
   the only repair here that needs no new knowledge.
3. **P4 says the belief under-responds to the arm's own price.** `calibration_error` is 0.0165 —
   the level is right and the *slope* is not. Separate level from amplitude before attributing
   this to the netting; that is a distinct measurement and it is not made here.
