# WORKER FINDING — a null CLV enters the published median, percentile and sum as the number zero

**Severity:** BLOCKING · **Lane:** D_billing_metering · **Disposition:** QUEUED (not fixed on sight)

**Severity ESCALATED LATENT → BLOCKING 2026-08-18** (worker tick, LANE 3 DISCOVER draw on
`EP1_clv_three_horizon`, pass 6) by running the one check this document said it had not run —
see "The check this finding declined to run" at the foot. A published figure is not merely at
risk; `docs/reports/ANNUAL_REPORT.md:2237` at HEAD `9718066ce` names five accounts to the board
as priority retention targets, and two of them are on that list only because five manufactured
zeros sat beneath them in the sort. That is the BLOCKING trigger verbatim.

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

---

## The check this finding declined to run (2026-08-18, worker tick, EP1 LANE 3 pass 6)

This document stopped, deliberately and correctly, at "it is not currently known to have moved
a headline the director has read: this finding measures the mechanism and the exposed
population, and deliberately stops short of claiming a specific published figure is wrong,
because that check has not been run." The check has now been run. Everything below is
`observed-with-evidence` (R9), measured at HEAD `9718066ce` against
`docs/reports/run_output_latest.json` and the committed `docs/reports/ANNUAL_REPORT.md`.

**The site the finding did not name is the one that publishes a board instruction.**
`saas/reporting/annual_report.py::_section_customer_strategic_value` is where `clvs[n // 2]`
lands: the median is not a reported statistic there, it is the **quadrant boundary** of the
Customer Strategic Value Matrix, and the section ends in

    **Board action: CRITICAL quadrant has 5 account(s). High CLV at risk from elevated churn
    probability. Immediate retention offers recommended.**

— `docs/reports/ANNUAL_REPORT.md:2237`, committed, present at HEAD (`git grep` on HEAD, not on
the working tree). The median itself renders at `:2194` as `Median CLV: £791.98`.

**Population, re-measured this tick:** 13 electricity billing accounts, 5 with `clv_gbp: null`
(C1, C3, C4, C5, C6 — the ceased book; each also `expected_lifetime_periods: null`), 8 valued.
Same 5-of-13 the finding recorded.

**R15, the mutation this document itself proposed, executed on the shipped section builder.**
The proposal was: "swap one account's `clv_gbp` between null and 0.0 and the published median
must MOVE. If it does not, the control is measuring nothing." Calling
`_section_customer_strategic_value` on the real run output, then again with all five nulls
replaced by explicit `0.0`:

    as published    sha256[:12] d997858d414a
    nulls -> 0.0    sha256[:12] d997858d414a   IDENTICAL

Byte-identical. The distinction `build_clv` and `_round_or_none` are built to preserve — a
`null` is *not applicable*, a `0.0` is *worth nothing* — does not survive to the aggregation
site at all. The control measures nothing, as predicted.

**What the substitution actually moves, decomposed so the two effects are not conflated.**

*Effect A — the mechanism this finding names, in isolation.* Hold the population at 13 and the
churn boundary at its published 0.29; change only whether the five nulls enter the CLV order:

    med_clv  £791.98 (as shipped)  ->  £38,255.61   (48x)
    CRITICAL {C2, C8, C_IC1, C_IC2, C_IC3}  ->  {C_IC1, C_IC2, C_IC3}

**C2 (£791.98) and C8 (£1,163.69) are published under the heading "High CLV, High Churn —
priority intervention" and inside a board recommendation for immediate retention offers.**
They are the 7th and 6th largest of the 8 accounts that have a CLV at all. They clear a "High
CLV" boundary of £791.98 that exists only because five accounts with no CLV were counted as
worth zero. C2 clears it by being *equal to* it.

*Effect B — the population question, for completeness.* Removing the five unvalued accounts
outright (the finding's own preferred repair, "exclude from the population and publish the
excluded count beside the figure") also moves the churn boundary 0.29 -> 0.35, because those
five carry real churn probabilities. Executed on the shipped builder:

    Median CLV: £38,255.61 | Median churn: 35%
    **Board action: CRITICAL quadrant has 1 account(s). ...**

**The conclusion is robust to which repair is chosen**, which is why it is stated as a defect
rather than as a preference: the median is £38,255.61 under exclusion and £38,255.61 under
Effect A alone. Only the current silent zero yields £791.98. No honest treatment of a
structural blank reproduces the published figure.

**Sized honestly, and no larger.** The wrong figure is in the committed annual report, not on
the live site: `grep -rl "Strategic Value Matrix\|CRITICAL quadrant" site/` returns nothing, and
the live `https://poesys.net/data/company.json` publishes `enterprise_value_gbp` and a null
`household.clv_gbp`, not the matrix. `total_clv` is unaffected (£1,283,652.65 either way) — the
sum was always the harmless case, exactly as this document said. What is wrong is the boundary,
the quadrant memberships it decides, and the board instruction that counts them.

**One further defect at the same line, recorded not escalated.** `clvs[n // 2]` is not a median
for even *n* — it is the upper of the two middle values. With the nulls excluded the population
is 8, so the published boundary would be the 5th of 8. It happens not to change any conclusion
above, and it is named here so that whoever repairs the null handling does not inherit it
silently.

**What this adds to "what would close it".** Item 1 (decide what the aggregates do with a null)
and item 2 (close the class, R10) stand unchanged. Item 3's mutation is now **executed and
failing** on today's code, so it is available as the falsifier a repair discharges against
rather than as a proposal — and the repair must move `_section_customer_strategic_value`'s
rendered board line, not merely a median, because that line is what a reader acts on.
