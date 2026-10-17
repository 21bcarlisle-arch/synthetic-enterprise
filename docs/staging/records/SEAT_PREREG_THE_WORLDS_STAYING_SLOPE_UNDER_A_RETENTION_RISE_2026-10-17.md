**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# Pre-registration: does the world's P(stay) fall at the rate the page's slope assumes when a renewal price RISES by £1–4 a month?

Written 2026-10-17T01:46Z, before the probe output below was analysed by this invocation. Claim
`retention-price-rescue-turns-on-the-staying-slope`; page
`docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md` §4; director's
open row `c34-now-ranks-next-best-action-on`. This file is not edited after the measurement.

## The instrument

`/var/tmp/retention_rise/probe_default.json`: `python3 -m tools.decision_probe` on the default book,
run 2026-10-16 22:32 → 2026-10-17 01:53 by an earlier invocation that left it unanalysed. No commit to
`simulation/customer_events.py`, `simulation/run_phase2b.py`, `company/pricing/` or
`saas/tariff_pricing.py` since it started. 260 probed renewals, 192 accounts (215 electricity, 45 gas).

Each row carries the world's true P(stay) (`roll_lifecycle_event` re-asked with only the rate changed)
at the flat offer and at 30 grid margins (£5–150/MWh over the decision's own base). For each page band
M ∈ {£5, 15, 30}/month, the base point is margin 12M/V £/MWh (V = the household's annual MWh) and the
rise is +£d/month (d = 1–4), interpolated on the grid. **Slope** = (P(stay) at base − P(stay) at
base+d) / (12d), in P(stay) per £/yr: the page's K. **Hazard band** = (1 − P(stay at base))/12,
split at 1.5%/month. **Collected** = the share of the rise a STAYER is billed, after the world's
decline-a-fix-above-the-default rule. Scripts: `/var/tmp/retention_rise/bands.py`, `rescue.py`.

## What the page's count does at each slope (the page's own arithmetic, printed before the world was read)

| K (per £/yr) | rescued | rescued and clearing the household's floor |
|---|---|---|
| ≤ 0.0006 | 18/18 | 18/18 |
| 0.00065–0.0008 | 18/18 | 17/18 |
| 0.00085 | 18/18 | 16/18 |
| 0.0009–0.0012 | 15/18 | 14–13/18 |
| 0.0015 (Deller) | 12/18 | 10/18 |

So the question splits at about **0.00085**: below it every case is rescued.

## Predictions

| | Prediction |
|---|---|
| P1 | The median rise-side slope at d = £2, over all graded band-decisions, is in [0.0003, 0.0009] per £/yr — the world's cut-side figure (0.00060–0.00065, `retention_slope_per_pound_of_renewal_cut.md` §0) ± half, not Deller's 0.0015. |
| P2 | Fewer than 20% of graded decisions at d = £2 have a slope ≥ 0.0015. |
| P3 | The slope does not rise with d: median at d = 4 ≤ median at d = 1 (the world's curve is concave on the cut side; a rise widens the gap, so the response per £ should not steepen). |
| P4 | Within each margin band the two hazard bands' median slopes differ by less than a factor of 2. |
| P5 | The decline-a-fix-above-the-default rule takes a visible bite: in at least one margin band, ≥ 20% of graded decisions collect less than half of a £2 rise. If so, the page's §4 omits a second leg — a rise the stayer is never billed — and that leg is the world's, not a slope. |

A refuted P1 on the steep side (median ≥ 0.00085) means the 18/18 count does not hold in the world
and the page's 10–12/18 bound is the nearer one. A refuted P5 means only the slope matters.
