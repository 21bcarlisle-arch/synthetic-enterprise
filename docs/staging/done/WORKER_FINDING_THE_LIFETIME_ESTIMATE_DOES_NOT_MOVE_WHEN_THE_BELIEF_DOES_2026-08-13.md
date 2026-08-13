> **DISPOSITION 2026-08-13 (worker tick, RUNG 1c blocking draw) — DISCHARGED, ARCHIVED.**
>
> Recommendation (a) taken: the estimate is now per-account. `fit_theta_posterior_per_account`
> updates the pooled prior with each account's OWN renewal history (conjugate Beta-Bernoulli,
> soft counts — the company holds probabilities, not realised churn flags), and
> `expected_lifetime_periods` evaluates the sBG expected lifetime in CLOSED FORM truncated at
> `MAX_PROJECTION_PERIODS` instead of sampling, which also removes the seed/roster-position
> dependence this finding called a C-S2 defect. `build_clv_model` is retained as the
> portfolio-level view and explicitly off the CLV path.
>
> **The named control is live, and R15 both ways.** The belief-swap mutation is
> `test_mutation_swapping_two_accounts_churn_beliefs_swaps_their_lifetimes`, written as an
> exchange between the two accounts rather than an equality against a recorded number — the
> failure mode this finding named. Four source mutations were each shown to kill named tests:
> reinstating the pooled posterior (4 tests, incl. the headline), inverting the survival term
> (4, incl. an independent Monte-Carlo check of the closed form), re-admitting the seed (1),
> and letting the valued population contaminate a retained account (4).
>
> **Measured effect.** corr(believed churn, projected lifetime) moves from +0.093 to **-0.987**
> against each account's own churn history. Mean projected lifetime ~13.5y -> ~5.2y; recomputed
> enterprise value over the same 8 accounts falls 49.7% (£7.01M -> £3.53M). A fidelity
> correction, not a tuning (R12/R13): 13.5y implies ~7.4% annual churn while this book's own
> believed probabilities run 0.140-0.410, mean 0.240.
>
> **It also discharged item 4 of the sibling finding**
> (`docs/staging/in_progress/WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT_2026-08-13.md`),
> whose exact-additivity control was blocked by this defect: its tripwire fired, was deleted as
> it instructed, and the exact-equality assertion is written.
>
> **STILL OPEN — item 1, the R11 live fetch.** Not attempted: autonomous runs have no network.
> Nothing here is claimed against the live origin. Published artefacts still carry the old
> figures until a full simulation run regenerates them; the render expressions
> (`site/customers/index.html` Expected Lifetime, `site/company/index.html` CLV tile) read the
> field and are unchanged, so they inherit the corrected value at the next run.

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
