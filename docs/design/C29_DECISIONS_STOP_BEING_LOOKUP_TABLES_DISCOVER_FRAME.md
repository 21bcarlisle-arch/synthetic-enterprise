# C29 — DISCOVER / FRAME: which company decisions are still lookup tables, and what would let each vary per account

*Delivery seat, 2026-10-05. Atom: `C29_decisions_stop_being_lookup_tables`. Coupled twin of
`PB4_engagement_separated_from_elasticity` (the triad gate holds PB4's L3 until C29 reaches L2) and
of `PB6_the_engagement_observable_crosses_the_seam`.*

## What "a lookup table" means here

A decision is a **lookup** when the supplier's action for an account is fully determined by a
category label or band the account falls in (segment, tier, payment method, days-overdue band, a
fixed probability cut), so two accounts in the same cell get the same action whatever their own
history says. A decision is **per-account** when an estimate formed from *that account's own
observed record* moves the action continuously, or at least moves which cell the account is in by
something other than the cell's own definition.

This is not "every constant is wrong". A band can be the right instrument when the law sets it
(the cap, SLC 27 timelines) or when the supplier genuinely has nothing finer to go on. The question
for each row is: **does a real supplier hold an observable that would separate accounts inside the
cell, and does the cell's action matter enough to the money/time/carbon outcome that separating them
could change it?**

## Why this atom matters now

The attribution showed the renewal rule's edge does not move when the company's code changes on a
fixed world. Two readings fit that: (a) the world gives the company nothing to learn from, or (b)
the company's decisions cannot use what it learns, because they read a cell, not the account. PB4
and PB6 have made (a) less true — engagement is now an antecedent in the world and its channel
observable crosses the seam. (b) is this atom. Per-account inference is the thesis's own mechanism
("finding individual customers we can create value for"); a book run on lookups cannot show it.

## B10 is no longer a dependency in fact

`block_reason` named B10 (a world that can react). B10 reached its target and was refiled to the
closed half on 2026-08-30 (`15a9703ae`). The outstanding dependencies are PB5 (pounds or percent,
L0, building) and PB4 (L2 → L3). Neither blocks DISCOVER/FRAME or the first BUILD increment below,
which is a per-account *estimate* the company can form and grade before any decision reads it.

The old `block_reason` carried one measured fact worth keeping: the decision surface as it stood
was nine accounts wide and the choosing was worth -£175 against an error bar about 25 times that.
That is why the first increment is an estimate graded on its own, not a widened decision — a
decision surface widened before the estimate is shown to rank produces a better-instrumented null.

## The census

Method: an import-reachability pass (`import simulation.run_phase4c_on_phase2b`, then list the
`company.{billing,crm,pricing}` modules loaded) plus a read of each decision site. **Import is not
call** — modules imported lazily inside a function are missing from the list, and a module that is
imported may still not reach the line named. The "reached" column is therefore a first reading to
re-ask at BUILD time with a call trace, not a verdict.

| # | Decision | Where | Keyed on | Reached by the run? | Observable a real supplier holds that would separate accounts in the cell |
|---|---|---|---|---|---|
| 1 | **Retention discount on a renewal at risk** | `company/policy/decision_policy.py` `CURRENT_POLICY.retention_tiers` (8% at P≥0.75, 5% at ≥0.50, 3% at ≥0.30) | the company's own P(leave), in three fixed bands | Yes — `CURRENT_POLICY` is the default run's policy | **Engagement, separately from elasticity (PB4).** P(leave) is engagement × response; a discount buys nothing from a household that was never going to look and little from an engaged, price-inelastic one. Observables: payment channel (crosses via `get_payment_method`, PB6), the account's own renewal history (did it actively choose a fix last time or roll to the default — the supplier's own tariff record), contact and complaint events, digital activity. |
| 2 | Retention offer type and value (CRM desk) | `company/crm/customer_retention.py:96` `_choose_offer` — 8% price-match on rate shock, 5% loyalty otherwise | `ChurnRiskDriver` enum from three fixed thresholds (`portfolio_churn_risk._classify_driver`: 20% rate rise, £3,000 bill, 2-year tenure) | Not imported at module load by the run | Same as #1. Also: the account's own response to a previous offer, which the supplier logs. |
| 3 | Churn risk tier label | `company/crm/portfolio_churn_risk.py:34` `_classify_band` (0.50/0.30/0.15) | fixed probability cuts | Not imported at module load | A tier is a presentation of #1's estimate; it varies per account only as much as the estimate does. Fixing #1 fixes this. |
| 4 | SVT drift belief by payment behaviour | `company/crm/churn_desk.py:374` `_SVT_DRIFT_BAND_POSITION_BY_BEHAVIOUR` | `BehaviourScore` (5 levels) | Yes — `churn_desk` is imported | Already one per-account field; the docstring argues the spacing is not load-bearing for a ranking. Engagement (#1's observables) would be a second axis inside each behaviour band. |
| 5 | Dunning step | `company/billing/arrears_engine.py:329` `current_dunning_step(segment, days_overdue)`; `collections_journey.ladder_actions(segment)` | `Segment` + days-overdue band; takes **no account id** | Yes — both imported | The account's own payment pattern: a first-time late payer and a habitual one at 30 days are different risks and want different contact. The supplier holds payment dates, DD returns, prior plan history (`payment_behaviour_analytics`, `dd_collections_desk`). Bounded by SLC 27 and Ofgem's ability-to-pay rules — the ladder's *legal floor* is not discretionary, its *pace and channel above the floor* are. |
| 6 | DD stop after returns | `company/billing/dd_collections_desk.py:127` `DD_STOP_THRESHOLD_CONSECUTIVE_RETURNS = 2` | flat count | Yes | Return reason codes (insufficient funds vs mandate cancelled) and the account's own collection history. Whether that is worth separating is a question for the knowledge layer — **no source on file establishes how suppliers vary this**; filed as a gap, not a number. |
| 7 | Payment plan default after missed instalments | `company/billing/payment_plan.py:21` `_DEFAULT_THRESHOLD = 2` | flat count | Yes | The plan's own instalment record. Ability-to-pay guidance limits how hard a supplier may push; it does not fix this count. |
| 8 | Receivable provision rate | `company/pricing/value_based_renewal.py:453–460` | payment method × age band | Yes (inside the value arm) | Reasonable as a band — a provision is a book-level accounting estimate. **Not a C29 target**; listed so nobody re-finds it. |
| 9 | Acquisition cost budget | `company/pricing/cost_to_serve.py:110` `acquisition_cost_gbp(segment)`; `company/crm/marketing_budget.py` | segment / year; takes **no customer id** | Imported by `saas/growth_mandate`, `acquisition_cohort` | Channel of acquisition and the prospect's own quote request (fuel, consumption band, region). Per-*prospect* inference is the acquisition half of the mission, but the company sees little about a prospect before the win. Second-wave, after #1. |
| 10 | Deposit on credit tier | `company/crm/credit_scoring.py:30` `_DEPOSIT_MULTIPLIERS` | tier (the score itself is per-account) | Not imported at module load | Score is already per-account; only the step from score to deposit is banded. Low value; regulated. Not a first target. |
| 11 | DD review action | `company/billing/dd_review.py` ±5% band | flat band, per-account inputs | Reached via `company/interfaces/dd_review` | Per-account already in its inputs; the band is the materiality line a customer is told about. Owned by `DD_seasonal_cashflow_physics`, not C29. |

Already per-account and excluded: `credit_scoring.assess_credit` (the score),
`retention_risk.retention_risk` (the score), `enriched_churn_estimate` (reads the book's own
per-channel engagement belief from `competitive_pressure`), `tou_desk.decide_tou_offer`, and the
value-based renewal arm `company/pricing/value_based_renewal.py` — which prices one renewal on that
account's own estimated value, but is **opt-in** (`VALUE_ARM_POLICY`), not the default run's
behaviour.

## The first one, and the trait it must infer

**Decision #1, the retention discount tiers, inferring ENGAGEMENT as distinct from elasticity.**

Why this one first:

- It is reached on every default run, and it moves money in both directions: a discount given to a
  household that would have stayed is pure transfer, and the mission names transfer as not value.
- PB4 says a renewal-time departure is two traits: whether the household looks
  (`household_segments.active_renewal_probability_for_customer`) and how far price moves it once it
  does (`population_draw.price_elasticity_for_customer`), drawn independently.
  `tools/engagement_separation.py` publishes the consequence on the real book — disengaged
  households with above-mean elasticity exist and are counted. A single P(leave) band cannot tell
  "won't look" from "looks but won't move", and those two want opposite retention actions.
- The observable already crosses: payment channel via `get_payment_method` (PB6), and the
  company's own record of whether the account actively chose its last term. Nothing new needs to
  cross the seam for the first increment.

**What BUILD's first increment is:** a per-account engagement estimate formed only from company
observables, graded against the world's engagement trait
(`household_segments.active_renewal_probability_for_customer`) resolved at the book's own run seed
— `tools/r1_inference_ceiling.true_traits` does this for ELASTICITY only, so the engagement side
follows the way `tools/engagement_separation.py` already reads it — with a planted-signal arm and a null
arm — PB6's open Expert-Hour finding (EH-2: "no planted/null recovery run") is the warning. Only
once that estimate is shown to rank accounts better than the channel alone does a decision read it.
The control it writes, named on the map row before it exists:
`tests/company/test_the_per_account_engagement_estimate_ranks_better_than_the_channel_alone.py`.

**What it is not allowed to do:** pick a discount per engagement band. The discount a household
should get is a question about value created, and the size of a bill-shock engagement lift is a
declared `None` in the world (`BILL_SHOCK_ENGAGEMENT_MULTIPLIER`). Neither gets a placeholder.

## What would refute this frame

If the engagement estimate, graded on held-out accounts, ranks no better than payment channel
alone, then the company has no per-account engagement signal beyond what PB6 already gives it,
decision #1 cannot be made per-account on engagement, and the next candidate is the dunning ladder
(#5) on the account's own payment pattern. Write that down as the result if it happens.

## Gaps filed, not filled

- No source on file for how real suppliers vary the DD-stop return count (#6) or the plan-default
  missed-instalment count (#7) by account. Both stay as they are and are named here.
- Whether the retention tiers' 8/5/3% are sourced: `CURRENT_POLICY` gives no origin. Ask the
  knowledge layer before BUILD touches them.
