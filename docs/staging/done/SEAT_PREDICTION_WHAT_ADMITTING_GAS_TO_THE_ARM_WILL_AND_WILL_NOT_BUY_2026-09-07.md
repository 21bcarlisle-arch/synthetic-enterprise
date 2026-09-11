**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas)

# PREDICTION — what admitting gas to the renewal arm will and will not buy

**Written 2026-09-07 01:05 BST, BEFORE the A/B answers it.** The run
(`python3 -m tools.run_value_cycle_ab --level-arm --out docs/observability/value_cycle_ab_gas_admitted_2026-09-07.json`)
was launched at 00:57 and was still executing when this file was written. Filed separately from
the result so the result cannot be read as a prediction made after its own answer.

## The state established before the run

`site/data/value_arms.json` → `decisions.why_the_rest_were_not_priced` records **346 of 1,953**
offered renewals (17.72%) excluded at stage `not_the_arms_commodity`, `by_design: true`, against
**120** the value arm priced (6.14% of renewals offered). The gate was one constant —
`UPLIFTABLE_COMMODITY = "electricity"` — read at five sites.

**Gas was fittable, and every input it needs was already on disk.** This is the part that is
established rather than predicted, and it was checked against the code and not assumed:

| input | gas answer that already existed |
|---|---|
| churn curve | `company/crm/churn_model.estimate_churn_probability(fuel="gas")` — its own base rate and rate sensitivity, for a stickier dual-fuel product |
| cost-to-serve | `saas/cost_to_serve.cost_to_serve_for_period(..., "gas")` — daily cadence, not half-hourly |
| standing charge | `saas/non_commodity.STANDING_CHARGE_GBP_PER_DAY["gas"]` — resi/SME, carried all along |
| lawful ceiling | `company/pricing/ofgem_price_cap.get_cap_unit_rate_for_date("gas", …)` — a first-class fuel |

So the arm's stated reason for refusing gas — "priced off a book this policy has never been
calibrated against" — was true when written and had stopped being true. It was not a wall and not a
world gap: it was a constant nobody had revisited.

## The prediction

**1. `decisions_scored` rises, but by much less than 346.** The book is 87 dual-fuel of 164
accounts. A dual-fuel household's gas renewal is a SECOND decision on a customer the arm already
prices on the electricity leg — it adds a decision, but not an independent one: the two legs share
tenure, credit risk, and the household behind them. I predict the renewal count moves by most of
the 346 and the count of newly-reached ACCOUNTS moves by far less — the gas-only accounts, which
are the minority. **The gain worth publishing is accounts, not renewals**, and I expect the
headline temptation to be the other way round.

**2. `detectable_excess` falls, and that is the actual prize.** The A/B's own curve puts the
effect it saw at ~1,181 decisions to resolve, against 86 scored. If the scored count roughly
doubles, the curve says `detectable_excess` falls from 0.0715 toward ~0.051. **That still does not
reach the observed 0.0171.** I predict the verdict stays "cannot tell" and that the honest
statement afterwards is *"cannot tell, and here is how much closer"* rather than a flip.

**3. The arm will DECLINE a material share of the gas renewals it now admits, lawfully.** Gas unit
rates are roughly a third of electricity's and so is the gas cap — £33.40/MWh at 2021-06 against
~£190 for electricity. Where a gas renewal's struck rate is near its cap there is no candidate
margin surviving both the ceiling and the churn model's support bound. That is `STAGE_DECLINED`,
which is a decision and not an omission — but it means the funnel will move renewals from
`not_the_arms_commodity` into `declined` as well as into `priced`, and **`declined` growing is not
the change failing.** (Measured while writing the controls: a gas renewal struck at £60/MWh in
2021-06 declines with "ceiling 33.4, support bound 105.3, base rate 58.0".)

**4. The realised money contrast may move in either direction and I am not predicting its sign.**
More decisions is more chances to be right and more chances to be wrong, and the arm's churn belief
has never been scored on gas at all. Naming a direction here would be picking one.

## What would refute each

1. is refuted if newly-reached accounts ≈ newly-scored renewals (the book is not as dual-fuel as
   the 87/164 says, or gas-only accounts dominate the 346).
2. is refuted if `detectable_excess` drops below `observed_excess` — the verdict flips to a real
   detection and the thesis gets its first non-null answer.
3. is refuted if `declined` is unchanged — meaning gas renewals are struck far enough under the gas
   cap that the ceiling never binds, which would say the strike chain already knows about gas
   levels better than I have credited it.

## The one thing that is NOT a prediction

Widening the gate is the easy half. Four inputs behind it are commodity-specific and each had an
electricity literal sitting where the gas answer belongs, so a gate that admits gas while any of
them keeps its literal prices a gas renewal off an electricity book and **returns a number rather
than an error**. On a book that is 87 dual-fuel of 164, that account really has an electricity leg
to read, so the wrong answer is populated and plausible. All four are threaded and each has a
control that was proved by reverting it. One of those controls did not exist until the poison round
found the first version unkillable — see the result document for which, and why.
