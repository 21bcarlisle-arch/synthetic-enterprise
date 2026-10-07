**Severity:** LATENT · **Lane:** C_customer_ops · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Direction item:** `retention-guard-nets-the-companys-own-bad-debt-belief` · **Claim:** released on landing

# Pre-registration: the retention guard nets the company's own bad-debt belief

Written at 2026-10-07T06:55Z, **before either arm was run.** No run of
this pair, or of any run reading `scores_read`, had been made when these were written.

## What is measured

`python3 -m tools._c29_retention_engagement_arm {off|net} <out.json>`, one process per arm, the
full 2016–2025 window on the shipped settlement sampler (the chosen book). The two arms are the same
world and book and differ in `DecisionPolicy.retention_nets_bad_debt` alone. Every guard row
carries the payment behaviour score the churn belief read. In `net`, `offered_unweighted` against
`offered` is exactly the set of offers the netting withdrew.

**The defined quantity.** An offer "to a POOR/CRITICAL account" is a guard row with `offered` true
whose account-level score (`account_payment_behaviour_score`, both legs) read POOR or CRITICAL at
that renewal. It is not the account's score at any other date.

## Predictions

- **P1 (the count asked for).** In `off`, retention offers to POOR/CRITICAL accounts number
  **between 3 and 20**. Their share of offers **exceeds** their share of renewals read
  (`scores_read`), because the score's uplift is what carries them over 0.30.
- **P2.** `net` withdraws **between 1 and 10** offers. **More than half** of those withdrawn are
  POOR/CRITICAL. The charge is keyed on arrears state, not score, so the overlap is the
  prediction, not a construction.
- **P3.** A clean account's charge is about the 2% prior on roughly £600 of energy billing, far
  below margin plus acquisition saved. So **no GOOD/EXCELLENT offer is withdrawn**.
- **P4.** Renewal departures differ between the arms by **at most 2**, and retention spend falls
  in `net`.

Graded in the result record beside this file, with any wrong prediction kept next to its answer.
