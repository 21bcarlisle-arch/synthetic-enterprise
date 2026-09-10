# PRE-REGISTRATION — what choosing the settled sample for difference moves

**Written 2026-09-11, before any arm was run.** Lane 0 delivery, claim
`the-settlement-sample-is-a-count-based-cull-and-the-chooser-earns-1.64x-at-its-size`.

---

## The question

`simulation/net_new_acquisition.plan_growth_campaign` wins ~500 accounts and can settle ~91 of
them. Which 91 is decided today by a **systematic count cull**:

```python
wanted = int((i + 1) * sample_rate) > int(i * sample_rate)
```

Every settled account then stands for the same `1 / sample_rate` (~5.46) accounts, published as one
number (`settlement_sample_rate`, 18.3%) on every row.

**Does choosing those 91 for DIFFERENCE over the demand axes, and carrying a per-account weight,
make the settled book a better stand-in for the campaign's wins than the count cull does?**

## Why it is being asked here and not on the world's stock

Measured 2026-09-10 (`simulation/premise_population.py`, the fitted-stock-joint block): chosen+
weighted beats a random draw on worst KS by **1.68x at N=40, 1.31x at N=400, 1.04x at N=4,400**.
The world's stock is 4,400 — nothing to compress, so the chooser is deliberately NOT wired there.
The settlement sample is 91 of 500. That is the size at which the design earns something.

## What is NOT being changed, stated so a later reader cannot infer otherwise

This is an **engineering artefact**, not a baseline change and not a curriculum act. The campaign
above the sampling pass is untouched: the quotes, the spend, the funnel's verdict on each prospect,
the company's own plan. `SETTLEMENT_CUSTOMER_YEAR_BUDGET` does not move. Nothing the company
decided can see this pass — the two-pass shape is what guarantees it, and it stays.

## Predictions, in order, before the first arm runs

**P1 — the count cull is NOT a random draw, so the 1.64x will not be reproduced.** The cull is
systematic on a year-ordered list, which is implicit stratification by year. It is therefore
already better than random on every axis correlated with acquisition year, and no better than
random on the within-year axes. I predict the chosen+weighted arm improves worst-axis KS against
all campaign wins by a factor in **[1.2x, 2.0x]**, and I predict the *gain is concentrated on the
fabric axes* (floor area, heat-loss coefficient, remaining insulation ceiling) rather than on cost.

**P2 — a pure difference-chooser will DEGRADE the per-year proportionality, and this is the thing
most likely to make the change not worth having.** The cull's one real virtue is that each year's
booked wins are proportional to that year's funnel wins, so `booked / rate` estimates any year
without bias. Cluster medoids over a fabric space have no reason to respect year at all. I predict
unweighted per-year shares move by more than 5 percentage points on at least one year. **The
per-account weights must reconstruct the per-year proportionality; if they cannot, the change is
refused.** That is the acceptance test, and it is written here before the number is known.

**P3 — the settled account count changes, so every published financial figure moves.** Today: 582
commercial, 173 settled, 91 of 500 wins settled, 409 refused. The chooser returns medoids plus axis
extremes plus per-fuel extremes, so its k is not exactly the cull's count and the customer-year
guard binds on a different set. **I do not predict the sign of the company's P&L move**, and
nothing in the implementation may be adjusted in response to it.

**P4 — the null case stays byte-identical.** When `campaign_cy <= headroom_cy` the whole pass is a
no-op today: nothing refused, no sample, no note. The chooser must not run at all in that case. A
run at 13 founders must be byte-identical to HEAD. This is the leg that shows the change is aimed
at the artefact and not at the answer.

**P5 — the hard budget guard still binds and is still the invariant.** Selection is by design;
the budget is in customer-years. The settled set may never exceed `customer_year_budget`, however
the members were chosen. If the chooser's set is dearer than the cull's, fewer accounts settle, and
that is the correct outcome rather than a bug.

## What would refute the change

- P2 fails and the weights cannot reconstruct per-year proportionality → **refused**, and the
  finding is that the count cull's stratification was the load-bearing property all along.
- The chosen+weighted arm's worst-axis KS is **not better** than the cull's → refused; the cull
  was already doing the job and the 1.64x did not transfer to this population.
- The demand vector computable for a *candidate* turns out to carry no more information than
  property type already carries → the premise of the whole item is wrong and that is the finding.

## How it is measured — one variable, one HEAD

The campaign is run **once**. Its candidate list `(year, prospect, in_market, customer_years)` is
captured and both selection rules are applied to that same fixed list. The campaign above the pass
is deterministic and identical in both arms by construction, so the only variable is the selection
rule. Running the campaign twice would put the seed stream in the comparison.

## Stated in advance: which of the two the change keeps

The instruction allows either "keep the per-year proportionality or replace it with per-account
weights that reconstruct it, and say which". **The intent is to replace it with per-account
weights that reconstruct it**, because a single global inflation factor is exactly the defect —
18.3% inflates the settled book to the commercial one with one number for every account. With
per-account weights the inflation is per account and arguable. If P2 refutes that, the fallback is
to keep the year stratification and choose for difference WITHIN each year, and that fallback is
named here so choosing it later is not a result fitted to the answer.
