**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — give the renewal objective the departure term it has never had) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — what adding a departure cost to `expected_value_gbp` will and will not move

**Written and landed BEFORE the changed code was run once.** The baseline in §1 is HEAD's own
output, re-read this turn; every figure in §3 onward is a prediction with nothing yet measured
against it. Filed because a prediction written after the answer is not a prediction.

Subject: `company/pricing/value_based_renewal.expected_value_gbp`, which at HEAD is

```python
p_retain × (margin × eac_mwh + fixed_revenue − cost_to_serve) × annuity(periods)
```

so a departure costs **exactly zero** and no price this arm chooses is ever penalised for causing
one. Named as step 2 of "what is next" in
`docs/staging/SEAT_FINDING_THE_RENEWAL_ARM_CANNOT_HEAR_A_HOUSEHOLD_IN_DISTRESS_AND_PRICES_THE_CRISIS_YEAR_HARDEST_2026-09-09.md`.

## 0. The change, stated precisely, so the prediction is about one variable

```python
EV(m) = p(m) × C(m) × A  −  (1 − p(m)) × K
```

`K` is **not a new number.** It is `saas.growth_mandate.cost_per_acquisition_gbp(segment)`, which
reads `saas.opex_ledger.CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER["pcs_aggregator"]` = **27.50 GBP**
against `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md` — the single-fuel band, which is already
the unit this company's live campaign spends per billing account, and which has sat sourced,
cited and unwired for seven weeks.

`max()` in `enriched_churn_estimate` is **untouched**, deliberately, so any move below is
attributable to this term and to nothing else.

**Two known holes, named here rather than discovered later.** (a) `K` is taken **undiscounted**:
the departure and the replacement spend both sit at the renewal boundary, one period ahead of
nothing. Discounting it would make it smaller, so undiscounted is the direction that does NOT
flatter the maximiser. (b) `cost_per_acquisition_gbp` returns **0.0 for SME and I&C**, because
those segments are acquired on a broker trail rather than a one-off. That zero is correct about
the one-off and wrong about the cost, so it must be **carried as a named hole on the decision**,
not summed silently — a silent zero there says an SME departure is free.

## 1. The baseline, re-read at HEAD this turn (not quoted from the record)

`python3 -m tools.renewal_rule_price_response`, anchor household, `expected_periods` unset so
`periods = 1.0` and `annuity = 0.9091`:

| year | mkt_move | flat_to | chosen | believed p_retain |
|---:|---:|---:|---:|---:|
| 2017 | 0.00 | 12.0 | 113.25 | 0.5289 |
| 2018 | 0.00 | 12.0 | 91.75 | 0.5065 |
| 2019 | 0.00 | 12.0 | **88.25** | 0.5034 |
| 2020 | −0.05 | 5.0 | 80.50 | 0.4702 |
| 2021 | 0.17 | 45.0 | 110.00 | 0.5930 |
| 2022 | 0.67 | 130.0 | **160.00** | 0.9574 |
| 2023 | −0.13 | 0.5 | 114.50 | 0.5086 |
| 2024 | −0.21 | 0.5 | 92.25 | 0.4429 |
| 2025 | −0.10 | 0.5 | 95.75 | 0.4759 |

LIVE: `eac_kwh`, `tenure_years`, `cost_to_serve_gbp_per_year`, `credit_risk`, `fuel`.
SILENCED: `bill_shock_count`, `satisfaction_score` — both 0.00 GBP/MWh spread.

Book-side figures this must be re-measured against, from
`docs/observability/value_cycle_ab_s1_three_arm_20260909.json` (world digest `39a192ce04c1eda8`,
producing commit `62334dc76`): cross-stratum concordance **0.2686** — the arm gave the departure
the higher margin in **73%** of departure-against-survivor pairs — and margin-against-departure
**AUC 0.6667** pooled, **0.6513** within belief quartiles.

## 2. The arithmetic the predictions rest on

At the old optimum, `[p'C + pC']A = 0`. The new objective's derivative there is therefore exactly
`p'(m) × K`, and `p' ≤ 0` everywhere on this grid. So the gradient at the old answer is
**non-positive**, and the new argmax cannot be above it for a well-behaved objective.

Size: at the 2019 anchor the retained side is `0.5034 × ≈292 × 0.909 ≈ 134 GBP` and the new term is
`(1 − 0.5034) × 27.50 ≈ 13.7 GBP`. **The departure term is about a tenth of the number being
maximised, not a rounding error** — which is why this is worth doing before the noisy-OR.

## 3. Predictions — the function (cheap probe, settled this turn)

* **P1 — DIRECTION, the hard one.** No year's chosen margin **rises**. All nine are ≤ their
  baseline above, to `SAME_ANSWER_GBP_PER_MWH` = 0.25. *If any year rises, that is a real finding
  about non-concavity in the arm's own objective and it gets reported as one, not smoothed over.*
* **P2 — REACHABILITY.** At least one year falls by more than 0.25, i.e. the term reaches the
  decision and is not merely a level change in a reported number. A term that changes no choice
  anywhere would make this an equivalence, and I would have to say so.
* **P3 — MAGNITUDE at 2019.** The chosen margin falls from 88.25 into **78–88** (a fall of 0.5 to
  10 GBP/MWh). Deliberately wide: the curvature of `EV` near its peak is not something I have
  printed, and a narrow band here would be false precision.
* **P4 — 2022 MOVES LEAST, IN GBP/MWh.** Its believed `p_retain` is 0.9574, so `p'` is small in
  magnitude near its optimum and `p' × K` is the smallest gradient of the nine. I predict 2022's
  fall is **strictly smaller than 2019's**. This is the one that could embarrass the "it prices the
  crisis year hardest" reading: **the departure term does not fix that, and I am saying so first.**
* **P5 — THE SILENCED ROWS STAY SILENCED.** `bill_shock_count` and `satisfaction_score` still read
  0.00 GBP/MWh spread. They enter only through `payment_est`, which loses the `max()` at every
  price this arm chooses; 2019's belief is flat only up to 12.0 GBP/MWh and no fall of the size
  P3 predicts gets anywhere near it. **The one way this could be refuted is the interesting one**:
  a large enough fall walks the chosen margin down into the band where the payment floor binds, and
  a row going LIVE would mean the objective change had un-silenced the distress channel by moving
  the arm rather than by combining the channels. I predict it does not happen; if it does it is the
  headline.
* **P6 — THE PINNED TEST STAYS GREEN.**
  `tests/tools/test_renewal_rule_price_response.py::test_the_household_distress_channel_cannot_reach_the_price`
  passes. It is keyed to the `max()` mechanism, which this does not touch. A red there would mean
  I had changed more than one thing.

## 4. Predictions — the book (needs the three-arm run; graded next)

* **P7 — THE INVERSION SOFTENS AND DOES NOT CLOSE.** Cross-stratum concordance rises from 0.2686
  into **0.28–0.40** (the 73% falls into 60–72%), and margin-against-departure AUC falls from
  0.6667 into **0.58–0.66**. It does **not** reach 0.50. Reason: `K` is a tenth of the objective,
  and the finding's own claim is that the mechanism is structural — a tenth-sized nudge should
  move the number without removing the cause.
* **P8 — WITHIN-BELIEF AUC STAYS ABOVE POOLED-MINUS-0.02.** The 0.6667 → 0.6513 gap was "no
  mediation at all". I predict the new pair keeps that property: the belief still fails to mediate
  the arm's own price, because the departure term is a function of the same belief. **This is the
  prediction I most expect to be wrong**, since the new term makes the objective more sensitive to
  `p_retain` and could make belief a better statistic for price.
* **P9 — REALISED NET: I CANNOT PREDICT THE SIGN.** Lower margins mean less revenue per retained
  account and more retained accounts and less replacement spend. I have not printed that trade and
  will not guess it. Recorded as "no prediction" so that whatever the run says cannot be read back
  as having been expected.
* **P10 — WHAT WOULD MAKE THIS ITEM WRONG.** If P1 and P2 both hold but P7 fails in the direction
  of *no book-side movement at all*, then the term reaches the function and not the book, and the
  honest verdict is "this changed nothing that matters" — which is a real answer about whether the
  arm's blindness is what costs us the selection leg, and it gets filed as one.

## 5. What this run cannot settle, whatever it says

One world, one seed. Decisions cluster on accounts and the AUCs carry no account-level standard
error. **Direction, not magnitude, on every book-side figure.** And this prices *one* of the three
repairs the finding names: it does not combine the churn channels, so a household in distress is
still inaudible to its own renewal price at every value — that remains open and is not claimed
fixed here.
