# WORKER FINDING — the per-customer lifetime estimate does not move when the belief about that customer moves

**Severity:** BLOCKING · **Lane:** B_commercial
**Found:** 2026-08-13, during the EP1_clv_three_horizon DISCOVER/FRAME draw (LANE 3 idle, no BUILD).
**Rank:** ahead of any EP1 BUILD; the atom's own deliverable inherits this estimator.
**Measured at:** HEAD de32e8c6b, live published `docs/reports/run_output_latest.json`
(4,152,276 bytes, mtime 2026-08-13 21:08) and `site/data/company.json`.

## The finding, in one sentence

`saas/clv_model.py::build_clv` publishes a per-account `expected_lifetime_periods` and a
`clv_gbp` derived from it, and **swapping the churn beliefs between two accounts does not
change either account's estimate** — the per-account number is a function of the account's
position in the posterior-predictive draw, not of what the company believes about that
account.

## Evidence — observed, R15 mutation, not inferred

The mutation is the one the estimator must fail: give two accounts identical observed
tenure and opposite churn beliefs, then swap the beliefs between them.

```
BELIEF  SAFE=0.05 RISKY=0.45 ->  SAFE life=50.000  RISKY life=23.926
SWAPPED SAFE=0.45 RISKY=0.05 ->  SAFE life=50.000  RISKY life=23.926
```

Identical to three decimal places. The estimate stayed with the *name*, not with the
belief. (`build_clv` over two accounts, 3 renewal points each, £300 margin each,
`random_seed=42` — the shipped default used by every live call site.)

**Mechanism, read from the code and not guessed.** `build_shifted_beta_geo_data` shapes the
model's input as `{customer_id, t_churn, T}` only — the per-renewal `churn_probability` is
not among the per-account inputs. `fit_theta_prior_from_churn_probabilities` pools *every*
renewal's churn probability across the whole book into ONE scalar Beta(alpha, beta), and
`build_clv_model` installs that single pair as the posterior for all accounts. So the
company's belief about a specific customer enters only through the portfolio mean; the
per-account spread that survives is `distribution_customer_churn_time`'s sampling noise.

**It shows in the live artefact.** Across the 13 billing accounts in
`run_output_latest.json::by_billing_account`:

| | |
|---|---|
| expected_lifetime_periods | mean 13.871, sd 1.057, range 11.834 – 15.612 |
| latest_churn_probability | range 0.140 – 0.410 |
| corr(lifetime, churn probability) | **+0.093** |

Near zero, and the sign is backwards: higher believed churn, marginally longer projected
life. The joint-highest-churn account in the book (C_IC3, p=0.410) carries the **longest**
projected lifetime on the book (15.612 years); C4 and C3 (p=0.170, the safest pair) carry
13.096 and 13.478.

**It is published to a user-visible surface.** `site/customers/index.html:1078` renders
`Expected Lifetime — <n> yrs` per customer, and `site/company/index.html:819` renders
`kpiTile("CLV", gbp(h.clv_gbp), "modelled lifetime value")`. NOT fetched from the live
origin this tick (no network in an autonomous run) — measured in the published artefacts at
HEAD and in the render expressions; the live fetch is the first step of the discharge, not
a claim made here (R9, R11).

## Why this is BLOCKING and not LATENT

A published per-customer figure is wrong in the specific sense the severity vocabulary
names: it is presented as this customer's expected lifetime and it is this draw's noise.
Every downstream use inherits it — `clv_gbp = avg_annual_net_margin × annuity(lifetime)`,
and `saas/enterprise_value.py` sums those into the published `enterprise_value_gbp`
(£7,557,256.88). It also makes the account's estimate depend on its *identifier*: rename
an account or reorder the roster and its lifetime changes, which is a C-S2 RNG-substream
defect as well as a valuation one.

## What would discharge it — recommendation, not a question

1. Fetch the live surfaces and record what the two figures render today (R11).
2. Either (a) make the estimate per-account by conditioning on the account's own churn
   history — the individual model's whole purpose — or (b) stop publishing a per-account
   lifetime and publish the portfolio figure that is actually being computed, with the
   pooling stated. Recommendation: **(a)**, because EP1 is about a per-customer valuation
   and (b) deletes the thing the atom exists to build.
3. The control is the mutation above, wired as a test: swap two accounts' churn beliefs;
   if neither estimate moves, the suite goes red. It cannot be written as an equality
   assertion on a fixed seed — that greens on exactly the defect it must catch.

**Not fixed in this tick, deliberately** (SELF_INTERRUPT_DISCIPLINE): this is estimator
surgery inside a live publish chain, on a BUILD-gated atom's file scope. Queued.
