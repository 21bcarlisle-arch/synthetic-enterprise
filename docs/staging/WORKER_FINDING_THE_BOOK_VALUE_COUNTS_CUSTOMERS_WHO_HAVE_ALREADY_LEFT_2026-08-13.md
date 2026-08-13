# WORKER FINDING — the published book value counts customers who have already left, and the site's featured household is one of them

**Severity:** BLOCKING · **Lane:** B_commercial
**Found:** 2026-08-13, during the EP1_clv_three_horizon DISCOVER/FRAME draw (LANE 3 idle, no BUILD).
**Rank:** with the sibling finding on the same estimator
(`WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES_2026-08-13.md`);
this one is the population defect, that one is the estimator defect.
**Measured at:** HEAD de32e8c6b, live published `docs/reports/run_output_latest.json` and
`site/data/company.json`.

## The finding, in one sentence

Five of the thirteen billing accounts in the published book **churned during the run**, none
of them won back, and every one still carries a forward-looking CLV in the final artefact
and in every year-end snapshot after it left — including the household the public
`/company/` page features by name.

## Evidence — observed, not inferred

`run_output_latest.json::customer_events`, the five non-renewal events (53 renewals, 5 churns):

| account | churned | home_move_won |
|---|---|---|
| C3 | 2020-06-30 | false |
| C5 | 2020-12-30 | false |
| C1 | 2021-12-30 | false |
| C6 | 2024-03-30 | false |
| C4 | 2024-09-29 | false |

`run_output_latest.json::clv_snapshots` carries a CLV for each of them in **every year after
the churn date** — C3 £2,852 (2021) … £2,309 (2025); C5 £8,873 (2021) … £6,424 (2025); C1
£2,216 (2022) … £1,833 (2025); C6 £12,171 (2025); C4 £891 (2025). The final
`by_billing_account` block does the same, and `saas/enterprise_value.py::build_enterprise_value`
sums it:

```
churned accounts' CLV total          £35,597.13
residential book CLV total           £68,685.83   -> churned share 51.8%
published enterprise_value_gbp    £7,557,256.88   -> churned share 0.471%
```

The book-level share is small only because 98.9% of this book's value is four I&C accounts.
**On the residential book the majority of the published forward value belongs to customers
who have gone.**

`build_enterprise_value` cannot see the exit: its inputs are `churn_risk`, `cost_to_serve`
and the CUSTOMERS roster, and the accounts-to-value list is `[a for a, renewals in
churn_risk.items() if renewals and a in net_margin_by_account]` — "has renewal history",
never "is still supplied". `churned_billing_accounts` is computed in the same run and sits
in the same output file; nothing joins them.

**The user-visible half.** `site/data/company.json::household` is account **C1** — which
churned 2021-12-30 — published with `clv_gbp: 2840.5`, `expected_lifetime_periods: 14.94`,
`latest_churn_probability: 0.23`, and an `annual_pnl` series that stops at 2021.
`site/company/index.html:819` renders it as `CLV — modelled lifetime value`, and line 811
renders `Latest churn 23%`. No attribute on that panel says the customer left; the panel's
own passport calls it "A real named account". So the public page presents 14.9 more years of
expected life for a customer whose last renewal was three and a half years before the run
ended. NOT fetched from the live origin this tick (no network in an autonomous run) —
measured in the published artefacts at HEAD and in the render expressions (R9, R11).

## Why this is BLOCKING and not LATENT

Two published figures may be wrong: the residential portion of `enterprise_value_gbp`, and
the featured household's CLV on `/company/`. It is also the exact defect a real supplier's
auditor would find first — book value that has not been reduced for customers lost — so it
is a fidelity failure as well as an arithmetic one.

## What would discharge it — recommendation, not a question

1. Fetch the live `/company/` page and record what the CLV tile renders today (R11).
2. Exclude churned-and-not-won-back accounts from the valued population at the point of
   valuation, not by post-hoc subtraction — the roster the valuation walks should be the
   supplied book. `churned_billing_accounts` and `home_move_won` are already in the same
   run output; the join is available today.
3. The featured-household selection must prefer a currently-supplied account, and any panel
   showing a forward value must state the account's status. A CLV tile that cannot say
   "this customer left in 2021" is the fail-open shape.
4. R15 control: mutate the roster so one valued account is marked churned with
   `home_move_won: false`; the enterprise-value total must fall by exactly that account's
   CLV and a named test must go red if it does not.

**Not fixed in this tick, deliberately** (SELF_INTERRUPT_DISCIPLINE): it changes a published
headline figure inside a BUILD-gated atom's file scope. Queued.
