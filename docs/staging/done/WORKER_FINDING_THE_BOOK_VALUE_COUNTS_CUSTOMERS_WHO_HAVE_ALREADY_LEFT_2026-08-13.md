**Severity:** RECORDED · **Lane:** B_commercial

> **TRIAGE 2026-11-20 (delivery seat), was BLOCKING -- OBSOLETE. The page it named (site/company/index.html) is gone, no page renders company.json's household block, and its clv_gbp is null. If a drill-down returns, item 3 here is its spec. Record: `docs/staging/SEAT_RECORD_TRIAGE_OF_THE_BLOCKING_FINDINGS_2026-11-20.md`.**

> **20 Nov, delivery seat (rejoining the shared checkout).** The 18 Nov build recorded below was staged in the shared
> tree and never landed, so the triage above read `DRILLDOWN_ID = "C1"` on origin and treated item 3 as a spec. The
> build lands with this edit (`tests/tools/test_generate_company_data.py`, 21 passed). The page's fate stays OBSOLETE;
> the feed now names its account's supply status.

> **DISCHARGED 2026-11-18 (worker tick, RUNG 1c blocking draw). Item 3 is built; nothing is left open.**
> The hardcoded `DRILLDOWN_ID = "C1"` is gone. `tools/generate_company_data.py::_featured_account`
> now picks the residential account the supplier has billed longest among those it still bills.
> Supply status comes from the supplier's OWN invoices, through the one existing rule
> (`saas.enterprise_value.ceased_billing_accounts`, fed bill period ends; both legs of a dual-fuel
> account must go quiet). The household block now carries `still_supplied`, `last_bill_period_end`
> and `selected_as`. The passport says "NO LONGER supplies" whenever a ceased account has to be
> featured.
> Measured on the 6af7fd0bf ledger: 263 of 766 billing accounts are still billed at the ledger
> edge, 2025-06-07. C1's last bill period ended on 2016-04-20, four months after it joined. That
> date matches the run's own `by_billing_account.C1.last_settlement_date`, which this rule does not
> read. The featured account is now SYN-2016-001: joined 2016-01-01, still billed at the edge, 114
> invoices and 38 arrears cases. `site/data/company.json` was regenerated, and only `household`
> (and `generated_at`) changed.
> Controls are in `tests/tools/test_generate_company_data.py`. One partition test covers all three
> outcomes: supplied, ceased-and-says-so, and none. Two mutations were each run and each turned its
> named test red: ranking on acquisition alone, and keying status per leg.
> **Item 1 (the R11 live fetch) is moot, not skipped.** No page renders this block any more.
> site/company/index.html no longer exists, and `/model/company/` sends readers to `/explore/`.
> The block survives only as a data feed, and that feed now states the account's status.

> **H48 PARKED-DOCUMENT AUDIT, 2026-11-18 -- UNBLOCKED.** Still open as written: `DRILLDOWN_ID = "C1"` is hardcoded at `tools/generate_company_data.py:43`, and `still_supplied` is not read by either generator. Nothing upstream blocks it.

## Status history, kept as written (the published run output is now `docs/reports/run_output_latest.json.gz`)

> **DISPOSITION 2026-08-13 (worker tick, RUNG 1c blocking draw) — PARTLY DISCHARGED, PARKED IN PROGRESS.**
>
> **STILL OPEN, and what unblocks it:** discharge item 3 — *"the featured-household
> selection must prefer a currently-supplied account, and any panel showing a forward
> value must state the account's status."* The DATA half landed (`by_billing_account`
> now carries `still_supplied` / `last_settlement_date` / `book_as_of`), but the
> selection and the render are SITE-lane and sit behind a chain this tick did not
> touch: `run_output` -> `tools/generate_customer_sample.py` -> `site/data/company.json`
> (`DRILLDOWN_ID = "C1"`, hardcoded at `tools/generate_company_data.py:43`) ->
> `site/company/index.html:811,819`. **Unblocked by:** propagating `still_supplied`
> through the two generators, replacing the hardcoded `DRILLDOWN_ID` with a
> prefer-a-supplied-account rule, and rendering the status beside the CLV tile.
>
> **ITEM 4 DISCHARGED 2026-08-13 (later tick, sibling BLOCKING draw).** This finding asked
> for "the total must fall by exactly that account's CLV". That control could not be written
> at the time: the sibling finding
> (`docs/staging/done/WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES_2026-08-13.md`)
> meant removing one account also moved every other account's projection, so the coupling was
> pinned by a tripwire test instead. The estimator is now per-account and deterministic, the
> tripwire fired and has been deleted as it instructed, and
> `test_mutation_a_valued_account_marked_ceased_removes_its_value_from_the_total` now asserts
> the exact equality. Items 1 and 3 below remain open and this doc stays parked.
>
> **ALSO STILL OPEN — item 1, the R11 live fetch.** Not attempted: autonomous runs have
> no network. Nothing here is claimed against the live origin.
>
> **AND NOTE:** none of the published artefacts change until a full simulation run
> regenerates them. The fix is in the code and proven by controls; `run_output_latest.json`
> and `site/data/company.json` still carry the defective figures at the time of writing.
>
> **WHAT LANDED (items 2 and 4):** cessation is now derived from the supplier's OWN
> settled records (`saas.enterprise_value.ceased_billing_accounts`, no read of the world's
> `churned_billing_accounts`); `build_enterprise_value` takes a REQUIRED `ceased_accounts`
> with no default; `_build_clv_snapshots` re-derives the supplied roster at each
> Point-in-Time cutoff. R15 both ways, four mutations each killing a named test.
>
> **ONE THING THE FINDING ASKED FOR THAT COULD NOT BE WRITTEN AS STATED:** item 4's
> *"the total must fall by exactly that account's CLV"*. Measured, it does not — excluding
> C1 moved C2's expected lifetime from 50.000 to 35.900 periods. That is independent
> confirmation of the sibling finding
> (`WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES_2026-08-13.md`,
> still BLOCKING and untouched). Rather than tune the control until it passed against a
> defect it is not about, the exact-additivity assertion is deferred and the coupling is
> pinned by `test_removing_one_account_still_moves_another_accounts_projection`, which goes
> RED the day the estimator is fixed and names the tightening it then owes.

# WORKER FINDING — the published book value counts customers who have already left, and the site's featured household is one of them

**Fate (2026-10-12, clear-the-decks):** ATOM -- the hardcoded featured-account id is still unchanged; prefer-a-supplied-account rule and status-beside-CLV render not built (P2)

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
