# [WORKER-FINDING] The tenure horizon cannot tell a deteriorating customer from a recovering one (2026-08-19)

**Severity:** LATENT · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-19 worker tick, LANE 3 DISCOVER/FRAME draw on `EP1_clv_three_horizon`
(level 0, `loop_stage: idle`, BUILD-gated — no BUILD code written this tick). Pass 8.
**Subject:** `saas/clv_model.py::fit_theta_posterior_per_account` and
`expected_lifetime_periods` — the tenure-expected horizon, the only one of this atom's three
that is live, and the one that sets the published `clv_gbp`, `avg_clv_gbp` and
`enterprise_value_gbp`.
**Measured at:** HEAD `74ccddb57`, working tree of this tick,
`docs/reports/run_output_latest.json`, `docs/reports/ANNUAL_REPORT.md` and the published
`site/data/company.json`. Every module named was EXECUTED as it sits on disk; nothing
monkeypatched, nothing regenerated. Everything below is `observed-with-evidence` unless
labelled `inferred` (R9).

## Why LATENT and not BLOCKING

Nothing here is a red test and no shipped figure is arithmetically wrong. What is wrong is that
a load-bearing MODELLING ASSUMPTION is unstated, contradicted by the world in the same repo, and
un-exercised by the control that was written for this exact estimator. BLOCKING would hold
`B_commercial` for a risk rather than a red. The magnitude section says why it is not smaller
than LATENT either.

## 1. The estimator is exchangeable in the signal it is built on

`fit_theta_posterior_per_account` (`saas/clv_model.py:162-208`) is a conjugate Beta update with
SOFT counts over the account's own renewal points:

```
alpha = alpha_prior + sum(p_i)
beta  = beta_prior  + sum(1 - p_i)
```

The sufficient statistic is a SUM, so the posterior — and every figure hanging off it — is
invariant to the ORDER of the renewals. Executed on the shipped functions with two accounts
whose nine renewals are the same multiset in reversed order:

```
DETERIORATING  bill shocks 0,0,0,1,2,3,5,7,9   -> latest churn_probability 0.32
RECOVERING     bill shocks 9,7,5,3,2,1,0,0,0   -> latest churn_probability 0.05

fit_theta_posterior_per_account  both -> (3.035454545454545, 18.64636363636364)
expected_lifetime_periods        both -> 9.415901156198618
build_clv(...)["clv_gbp"]        both -> 142.0649211867      bit-identical
```

A customer whose bill shocks are all in the most recent year and one whose shocks are all
ancient are the same customer to this horizon.

**This is not an arithmetic slip.** It is the correct behaviour of a conjugate update on i.i.d.
Bernoulli trials. It is therefore an ASSUMPTION — that theta is a fixed per-account propensity —
and two things are true of it: this atom's record has never stated it, and the world shipped
beside it contradicts it. `churn_probability(bill_shock_count)` (`saas/churn_model.py:40`) is
evaluated per renewal year on that year's shock count
(`build_churn_risk`, `saas/churn_model.py:105-117`), so the generating process is time-varying
by construction. The estimator that reads it is not.

## 2. The live artefact shows it with no model at all

The 8 valued accounts in `run_output_latest.json::by_billing_account`, published
`latest_churn_probability` against published `expected_lifetime_periods`:

```
acct    churn   lifetime              clv_gbp
C2      0.41    11.127618809847226      791.45
C7      0.38    10.955525994142690     -291.47
C8      0.35    11.127618809847226     1162.39
C9      0.14    11.127618809847226     1462.87
C_IC1   0.29    10.129852262166567   658422.76
C_IC2   0.29    10.139813815266979   387665.13
C_IC3   0.41    10.659296580510661   195606.04
C_IC4   0.20    10.967110667288315    38255.61

pearson(churn, lifetime) = -0.0169      churn spans 0.14..0.41 (2.9x)
lifetime spans 10.130..11.128 (9.9%)
```

Three accounts spanning the whole churn range carry a lifetime identical to 17 significant
figures; two accounts with identical churn carry different lifetimes. **The published pair is
not a function in either direction**, and a reader meets both fields side by side on the live
site — `site/data/company.json::household` publishes `latest_churn_probability`,
`expected_lifetime_periods` and `clv_gbp` for a named account.

`inferred`: the 17-figure identity is the signature of equal soft counts (equal renewal count
and equal summed churn probability); the alternative is two accounts landing on the same level
set of the lifetime function through compensating differences in count and sum. The histories
themselves are not published, so this is not settled from the artefact alone.

Note this is NOT the 2026-08-13 defect returning. That finding
(`WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES`, BLOCKING, repaired)
was about the estimate following the account's POSITION IN A DRAW; the repair worked, and the
direction is now right (that finding recorded +0.093, backwards; it is now −0.0169). What
remains is a magnitude at noise, for a different and legitimate reason — the estimator answers
to the whole history, and the artefact publishes only the latest value. Both readings point at
the same gap: **nothing published lets a reader see what the horizon is a function of.**

## 3. Magnitude

Stated in the form pass 7 had to learn (a substituted-input counterfactual predicts the world in
which ONLY that input changes; a repairer who sees this will likely see its neighbours too).
Under the shipped estimator with ONLY the horizon substituted — each account's posterior
conditioned on its own latest renewal instead of its whole history, `_annuity_factor`, the
discount rate and the margins untouched:

```
account   shipped_clv     latest-only_clv    delta
C2             791.45            366.51      -53.7%
C7            -291.47           -140.98      +51.6%   (a loss, so shrinking)
C8            1162.39            576.41      -50.4%
C9            1462.87            925.79      -36.7%
C_IC1       658422.76         368853.65      -44.0%
C_IC2       387665.13         217050.66      -44.0%
C_IC3       195606.04          92857.23      -52.5%
C_IC4        38255.61          22757.29      -40.5%
TOTAL      1283074.77         703246.56      -45.2%
```

The published `enterprise_value_gbp` (GBP 1,283,769.58, live on `site/data/company.json`) is a
first-order function of a choice nothing in the tree has argued. The identity
`clv_gbp == avg_annual_net_margin_gbp * _annuity_factor(expected_lifetime_periods, 0.10)` was
checked and holds for all 8 accounts, so the horizon is the whole of the difference.

## 4. R15 — the control that exists cannot fire on this

`tests/saas/test_clv_model.py:186-207` is a real mutation test, written for the 2026-08-13
finding, and it passes: swap two accounts' churn beliefs, their lifetimes must swap, and it
carries an explicit anti-vacuity clause.

Its fixture is the limit. `_belief` (`:159-167`) builds each account's history as three renewals
that all carry the SAME probability:

```python
return {
    account_id: [
        {"renewal_period": f"201{i}-01", "bill_shock_count": 0, "churn_probability": p}
        for i in range(3)
    ]
    for account_id, p in account_churn_probabilities.items()
}
```

No account in the control's population HAS a trajectory. The only mutation the fixture can
express is BETWEEN accounts, and the estimator passes that one. The mutation that would fire —
permuting one account's renewals WITHIN itself — is bit-identical on the output and no test in
the suite asks it. The anti-vacuity clause is honest and does not reach: it requires two
accounts to be distinguishable, which they are, on a statistic that is order-blind.

Grepped `tests/saas/` for a within-account permutation of `churn_probability`: none.

## What this owes, and what it does not

It does NOT owe a repair. Which time model the tenure horizon should use is an EP1 design
question and EP1 is BUILD-gated (epoch 2, `loop_stage: idle`); choosing one here would be
writing BUILD code on a parked atom.

What it owes is **one falsifier and one sentence**, both cheap and both available today:

1. A control that permutes a single account's renewal history and asserts the projected lifetime
   moves. It needs no new account, no new population and no world change — only a permutation of
   a fixture that already exists. This is the first EP1 falsifier that does not need a
   deliberately constructed account (pass 7's problem: both discriminating cells of the cohort
   horizon's population 2x2 are empty on the live book).
2. Every horizon states its TIME MODEL in the record it writes, alongside the population and
   basis pass 6 and pass 7 already established. "Tenure-expected" is a family, not a horizon;
   today's member assumes constant propensity and does not say so.

Recorded in full in `docs/design/simplifications/EP1_clv_three_horizon.yaml`, pass 8, which also
carries the demand-side census this pass ran alongside it (five decision modules, six CLV
formulas, three tenures for one customer, two discount rates, and a 3x acquisition hurdle that
one live account straddles depending on which estimator answers).
