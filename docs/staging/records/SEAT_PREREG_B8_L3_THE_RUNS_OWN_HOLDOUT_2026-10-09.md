**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# Pre-registration: B8 L3, the run's company runs its own retention holdout

*Filed 2026-10-09 before the run below was started. The answer is not known.*

## What is being measured

`DecisionPolicy.retention_runs_holdout` (new, off on every standing policy). On the renewals the
retention guard would consider (`company_est_pre > RETENTION_THRESHOLD`), the company flips its own
coin (`discovered_price_sensitivity.holdout_arm`, 50/50, seeded on account and day). Held out: no
offer. Treated: the standing guard's offer while the company's own interval, over rows closed before
today, is undecided; `retention_cut_decision` once it decides.

The run: `CURRENT_POLICY` with the flag on, 80 founders (the default roster), `report_end`
2019-12-31, against the same run with the flag off.

## Predictions

1. **The interval never decides.** At about 28 considered renewals over four years, each arm holds
   about 14 rows; the B8 L2 finding needed about 27,700 per arm for this effect. Every row of
   `retention_holdout_log` carries `decided: False`. So the learned decision is never consulted in
   the founders' run, and the policy reduces to "the standing guard on half the book".
2. **Offers about halve:** the flag-on run makes 9-19 offers against 28 flag-off. Held-out rows 9-19.
3. **No departure is attributable to the holdout at this size.** The flag-off run kept 25 of 28
   offered; at the run's own mean ΔP(stay) of about +0.01 per offer (the 2026-10-09 rate finding),
   withholding ~14 offers costs about 0.14 expected stays. Departures differ by 0-2, and any
   difference is within what the diverging book alone produces.
4. **Headline net moves by less than the retention cost the flag-off run booked** (about GBP 770), in
   either direction: the held-out half is no longer billed its discount.

If (1) fails, the coin or the closed-before rule is wrong, and that is the first thing to read.
