# WORKER FINDING — a null CLV enters the published median, percentile and sum as the number zero

**Severity:** LATENT · **Lane:** D_billing_metering · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-17 worker tick, during the repo-wide sweep closure item 3 of
`WORKER_FINDING_THE_PUBLISH_PATH_SWALLOWED_199_GENERATOR_CRASHES_2026-08-17.md` asked for
(the sweep's job was to find remaining crash sites; there are none — this is what it found
instead).
**Subject:** `saas/reporting/annual_report.py`, lines 8217-8242 and 2367.
**Class:** a structural blank folded into an aggregate as a real value.
**Measured at:** the tree of this tick. Everything below is `observed-with-evidence` (R9).

## The measurement

`build_clv` records `clv_gbp: null` for an account that is no longer supplied — correct
behaviour, and the deliberate output of `W2_17`: an account that has left has no lifetime
value, and publishing 0 for it would state a belief the company does not hold. The
`_round_or_none` helper exists precisely to carry that null to the published per-customer
record without turning it into a number.

Seven sites in the annual report then turn it straight back into 0 before aggregating:

```python
clvs = sorted((v.get("clv_gbp") or 0.0) for v in elec_accounts.values())        # :8217
churns = sorted((v.get("latest_churn_probability") or 0.0) for v in ...)        # :8221
for cid, v in sorted(elec_accounts.items(), key=lambda x: -(x[1].get("clv_gbp") or 0)):  # :8229
    clv = v.get("clv_gbp") or 0.0                                               # :8230
    churn = v.get("latest_churn_probability") or 0.0                            # :8231
    periods = v.get("expected_lifetime_periods") or 0.0                         # :8232
total_clv = sum((v.get("clv_gbp") or 0) for v in elec_accounts.values())        # :8242
```

`v.get("clv_gbp") or 0.0` is a *different* defect from the `round(d.get(k, 0), n)` one just
closed, and it is the reason a sweep for the crash shape does not find it: it never raises.
It silently substitutes.

**Population, measured, not guessed.** In `docs/reports/run_output_latest.json` this tick:
**5 of 13** billing accounts carry `clv_gbp: null` (and the same 5 carry
`expected_lifetime_periods: null`). So on today's book roughly **38% of the accounts entering
these aggregates enter as a manufactured zero.**

## Why it matters, at its real size and no larger

* `sorted(...)` at :8217 and :8221 feeds **percentiles and a median**. Five zeros placed at
  the bottom of a 13-element sorted list do not merely lower the mean — they move the
  *median's index*. A median is supposed to be robust to outliers; it is not robust to
  fabricated members.
* `sum(...)` at :8242 is the one case where the substitution is arguably harmless — an absent
  CLV contributes nothing to a total either way. It is listed for completeness, not as damage.
* The `sorted(..., key=-clv)` at :8229 ranks every no-longer-supplied account **last**, which
  happens to look right, and is right for the wrong reason: it is ranking them as *worth zero*
  rather than as *not applicable*. The moment a genuinely worth-nothing account exists, the
  two become indistinguishable in the published table.

**What this is NOT.** It is not the four-day publish freeze, and it does not retract that
finding's discharge — the crash sites were the two named generators and both are fixed. It is
not a crash, and it is not currently known to have moved a headline the director has read:
this finding measures the mechanism and the exposed population, and deliberately stops short
of claiming a specific published figure is wrong, because that check has not been run.

## Why it is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE`: the supply of findings is infinite and fixing on sight is the
treadmill. It also belongs to a different lane and a different subject than the finding whose
sweep surfaced it — the annual report's aggregation semantics, not the publish path — and
deciding what an aggregate *should* do with a structural blank (exclude from the population,
or report alongside a coverage count) is a design question, not a patch.

## What would close it

1. Decide, once, what these aggregates do with a null: the strong candidate is **exclude from
   the population and publish the excluded count beside the figure**, so a median over 8 of 13
   accounts says so. Silently dropping them is the mirror defect of silently zeroing them.
2. R10 — close the CLASS, not these seven lines. The invariant is "a structural blank must
   never enter an aggregate as a value"; `or 0` on a field the codebase deliberately publishes
   as null is the detectable shape.
3. R15 — the control must be able to fail: swap one account's `clv_gbp` between null and 0.0
   and the published median must MOVE. If it does not, the control is measuring nothing
   (cf. the swap-the-belief-between-two-units technique).
