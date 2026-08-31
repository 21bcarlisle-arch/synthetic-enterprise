**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Two of the world's four departure risks are one variable seen twice, so bad service makes a household LESS likely to leave

**Found:** 2026-08-31, by removing a discretisation that had been hiding it. Pre-registration and
run: `WORKER_PREREGISTRATION_WHAT_A_CONTINUOUS_SATISFACTION_RESPONSE_MUST_SHOW_2026-08-31.md`.
Ladder rung 3: `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md`.

## The measurement

Realised churn by income-stress tier, on a full two-route capture (144 renewal decisions):

| income stress | n | mean satisfaction | dissatisfaction multiplier | action propensity | **realised churn rate** |
|---|---|---|---|---|---|
| low | 111 | 0.6844 | 1.0238 | 0.9801 | **0.243** |
| moderate | 20 | 0.6089 | 1.1367 | 0.7947 | **0.200** |
| high | 12 | 0.5265 | **1.2261** | **0.6067** | **0.083** |

`corr(dissatisfaction_response, action_propensity) = −0.5188`.

**The households the world models as most dissatisfied leave at a third the rate of the most
satisfied** — 0.083 against 0.243, on 12 and 111 decisions respectively.

As a discriminator, `sim_dissatisfaction_response` alone scores **0.3806** against a null of
**[0.3794, 0.6206]**. **It sits INSIDE that null — by 0.0012, on the bottom edge — so on this leg
we cannot tell**, in those words, per the standing rule in `tools/inference_claim.py`. What can be
said is narrower and is still the finding: **there is no evidence the term predicts in the right
direction, and the point estimate is on the wrong side of chance.** The claim that the mechanism is
backwards rests on the realised-churn table above, which is a direct outcome measurement rather than
a rank statistic — and its high-stress cell is 12 decisions, which is stated here so nobody quotes
the ratio without it.

*(This paragraph replaced a first draft that read "not merely uninformative, but pointing the wrong
way". That asserted a direction the interval does not support. The correction is kept visible rather
than applied silently: a reading inside its null says we cannot tell, and that rule binds hardest
when the point estimate is the one I would like to be true.)*

## The cause is structural, not a parameter

`simulation/sim_satisfaction` computes satisfaction from income stress, bill shocks, tenure and
payment channel. `action_propensity` is `stress_switching_multiplier(income_stress) ×
tenure_switching_multiplier(tenure)`. **They share two of their drivers, and income stress is the
dominant one on both.**

So the world's four departure risks are not four reasons. `dissatisfaction` says *"I am unhappy with
this supplier, so I leave"*; `action_propensity` says *"I am under financial stress, so I do
nothing"*; and because unhappiness in this world is largely *caused by* financial stress, the second
cancels the first roughly three to one. The C2 design chose the damping deliberately and gave a good
argument for it — *"I was too financially stressed to switch"* is not a reason anyone left. **The
argument is right and the wiring makes it self-defeating**, because it damps a risk it also
generates.

Both real phenomena exist: dissatisfied customers switch more, and financially vulnerable customers
switch less. They are **different axes in the real world and the same axis here.**

## Why nothing saw it until today

`satisfaction_churn_multiplier` collapsed 434 distinct satisfaction scores into three values, 88% of
the book sharing one. That produced **92.0% tied pairs**, and a tied pair scores 0.5 in any rank
statistic, so the factor read **0.4672 — inside its null and near enough chance**. The honest
conclusion available to a reader was *"service does not drive departures in this world"*.

*(Corrected in place, 2026-08-31, before this finding was landed. The first draft of this paragraph
and of the pre-registration's result table cited **0.4971** as the baseline arm. That figure is real
but belongs to the **pre-C1b, renewal-only** capture of 465 decisions — a different run and a
different population from the treatment it was being subtracted from. The paired baseline, measured
on `ladder_churn_factors.json` at the same 2,000 permutations as the treatment, is **0.4672**.
Nothing in the conclusion moves: the reading still sits inside its null before and below chance
after. It is corrected because a baseline taken from another run is the specific way this repository
has published a difference between two numbers that do not have one.)*

**That conclusion was wrong in the way that matters.** The mechanism was there, wired backwards, and
the tie fraction was standing in front of it. Making the response continuous moved the reading to
0.3806 and made the cause measurable in one table.

This is the *tie fraction is not the same as no signal* lesson, first instance: two variables can
both read 0.50 and mean completely different things, and only the tie fraction separates
"discretised until it cannot speak" from "genuinely unrelated".

## What is owed

1. **Give satisfaction a driver that income cannot explain.** Service failures, contacts,
   complaints, a bill that went wrong — the things a real supplier both causes and observes. Until
   then "unhappy with us" and "unable to act" are one variable and neither can be inferred from the
   other's absence. **This is choice-and-channel work** and it is where the world's service risk
   starts being a reason rather than a proxy for poverty.
2. **Do not re-derive the dose first.** `_HIGH_SATISFACTION_MULTIPLIER` 0.85 and
   `_LOW_SATISFACTION_MULTIPLIER` 1.30 carry no source and that is separately owed — but this run
   says the dose is not what is stopping the mechanism. Tuning a term that is being cancelled
   anyway would move a number and change nothing.
3. **Nothing here is repaired by weakening the damping.** `action_propensity` reflects a real
   phenomenon and the published evidence for it is the stronger of the two. The defect is the shared
   driver, not the modulator.

## Severity

**LATENT.** No published figure is wrong today: the departure *level* is unchanged (32 departures
either way, +0.0699pp on the mean hazard) and the reason mix that reaches a reader is a separate,
already-filed problem. What is wrong is a **mechanism**, and its consequence is that any company-side
attempt to infer service-driven churn in this world is inferring against a signal that points
backwards. That is a rung-3 defect under the director's canon: the individuals do not carry the
rationale the thesis needs them to carry.
