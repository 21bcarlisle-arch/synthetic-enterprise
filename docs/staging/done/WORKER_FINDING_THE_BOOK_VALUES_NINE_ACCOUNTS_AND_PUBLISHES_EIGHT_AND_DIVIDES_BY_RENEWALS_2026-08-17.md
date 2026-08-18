# WORKER FINDING — the book values nine accounts and publishes eight, and divides a total by a count of a different thing

**Severity:** RECORDED · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** carried forward from
`WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17`
(BLOCKING, repaired same day). That finding recorded both items in its own read and repaired
neither: each moves published numbers again and owes its own evidence, and the basis error was
the blocking one. Filed separately rather than swept into the repair
(SELF_INTERRUPT_DISCIPLINE — queue by default).

**Subject:** `saas/clv_model.build_clv` (the divisor), and the join between
`enterprise_value_account_count` and `by_billing_account` in
`saas/reporting/annual_report.py`.

**Measured at:** a full `tools.run_annual_report` re-run on the repaired tree, 2026-08-17.
Everything below is `observed-with-evidence`.

## 1. The divisor is renewal points, not years of margin

`build_clv` computes `avg_annual_net_margin_gbp = lifetime_margin / len(churn_risk[account])`.
The numerator is a cumulative total over the years the account settled; the denominator counts
its renewal POINTS. An account settling for N years has N-1 renewal points between them, so
the "average annual" margin is systematically overstated, and by MORE for shorter-tenure
accounts:

    acct     renewal points   years settled   overstatement
    C2                    9              10            +11%
    C7                    9              10            +11%
    C8                    9              10            +11%
    C9                    9              10            +11%
    C_IC1                 8               9            +12%
    C_IC2                 7               8            +14%
    C_IC3                 6               7            +17%
    C_IC4                 5               6            +20%

It is a unit error — a cumulative total divided by a count of a different thing — and it is
not uniform, so it tilts the book toward the newest accounts. Small beside the basis error
that was repaired, and real: every figure in that repair's restatement table inherits it.

**Why it is not obviously a one-line fix.** The renewal-point count is also what the sBG
lifetime projection is fitted on, and `expected_lifetime_periods` is denominated in renewal
PERIODS — so `clv = avg_annual × annuity(lifetime_periods)` is at least internally consistent
in its units today. Changing the divisor to years without deciding what a "period" is
throughout would trade a stated error for an unstated one. The right repair names the unit
once and applies it to both halves.

## 2. Nine accounts are valued; eight are published

    enterprise_value_gbp            1,296,786.28
    enterprise_value_account_count             9
    by_billing_account rows carrying a clv_gbp 8
    sum of those eight                  1,296,113.37
    residual                                672.91

The residual is `SYN-2021-001`, the drawn successor: present in `churn_risk`, valued inside
`build_clv`, absent from `by_billing_account`. It was `inferred` in the parent finding and is
now confirmed — the account appears in the run's `churn_risk` keys and in no
`by_billing_account` row.

£672.91 of a £1.3m book is immaterial as a number. It is material as a SHAPE: a published
total that no published decomposition reconciles to is unauditable by a reader, and this is the
second time this table has been found to publish a different population from the one it counts
(the first was the ceased-account exclusion, 2026-08-13). A reader checking the tile against
the rows finds a discrepancy and has no way to tell which side is wrong.

## What would close it — recommendation, not an ask

1. **Recommended for item 2 (cheap, and it is the auditability one):** include every account
   `build_clv` valued in `by_billing_account`, or publish the residual as its own labelled
   row. Either makes the total reconcile to its own decomposition; silently publishing eight of
   nine does not.
2. **For item 1:** name the projection's unit once — renewal periods or years — and apply it to
   the divisor and to `expected_lifetime_periods` together. Do not change one alone.
3. **R10 — the class:** *a published total reconciles to the decomposition published beside
   it.* Detectable arithmetically over every total/decomposition pair in the payload, of which
   `enterprise_value_gbp`/`by_billing_account` is one. This is a sibling of the
   basis-parentage gate landed for the parent finding — that one checks a derived figure
   against its declared PARENT, this checks a total against its declared PARTS.
4. **R15 — the control must be able to fail:** drop one valued account from the published
   decomposition and the reconciliation must go red; today it is silent. Second direction, so
   it cannot fail open: a legitimately unvalued account (no renewal points, or ceased) must NOT
   trip it — those are correctly absent from both sides.
