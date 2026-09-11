**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Finding — the shock-aftermath exclusion became unreachable when shock became signed, and the test that guards it went red for a different reason

*Delivery seat, 2026-09-02. Found while clearing a pre-existing red at clean HEAD that was wedging
the lane-0 direct-debit commit. Not the item I drew; filed rather than routed around, because
following the thread is the rule and the thread had two ends.*

---

## What was measured, at clean HEAD, not recalled

`tests/simulation/test_run_phase4c_on_phase2b.py::test_bill_shock_likely_seasonal_false_for_shock_aftermath_month`
fails on a `git archive HEAD` extract with:

```
TypeError: '>=' not supported between instances of 'NoneType' and 'float'
```

This is a **red at clean HEAD**, not a red my change caused: it reproduces on an extract of HEAD
with none of the working tree present. It wedges every commit whose pathspec touches
`simulation/run_phase4c_on_phase2b.py`, which is how it reached me.

Printed at the real inputs (the test's own construction: twelve flat £300 months, then a £1,500
July spike, then flat again):

| month | total | `bill_movement_pct` | `bill_shock_pct` | `bill_shock_yoy_pct` | `likely_seasonal` |
|---|---|---|---|---|---|
| 2020-06 | 81.24 | 0.0 | 0.0 | 0.008 | False |
| 2020-07 | 405.06 | **+3.986** | 3.986 | 4.025 | False |
| 2020-08 | 81.24 | **−0.799** | **None** | 0.008 | False |
| 2020-09 | 81.24 | 0.0 | 0.0 | 0.008 | False |

## The first end of the thread: the test was stale, the code is right

`saas/bill_generator.bill_movement` was corrected on 2026-09-01 to make shock **signed** — a shock is
an *increase*, so a bill that fell carries `None` rather than the `abs()` of its fall. That
correction is well argued and well evidenced (45.9% of movements previously called shocks were bills
that went *down*, including refunds).

August reverts **down** from July's spike. `None` is therefore the correct value, and the assertion
`august_y2["bill_shock_pct"] >= 0.20` was pinning the exact behaviour the correction removed. Amended
in the same change onto the honest quantity — `bill_movement_pct <= -0.20`, asserting the **sign** as
well as the magnitude so an `abs()` regression cannot make it green again.

## The second end, and the one that matters: the exclusion is now unreachable

`company/billing/monthly_bill_assembly.py`:

```python
bill["bill_shock_likely_seasonal"] = bool(
    mom_pct is not None and mom_pct >= 0.20 and yoy_pct < 0.20
    and not prior_month_was_shock
)
```

`prior_month_was_shock` — the shock-aftermath exclusion, added for the phase-close-evaluator's live
finding of 2026-07-10 — **can no longer decide this case.** An aftermath month is *by definition* a
month that fell back from a spike; a month that fell now has `mom_pct is None`; and `mom_pct is not
None` short-circuits before the exclusion is ever consulted. The `None` guard does the exclusion's
job and does it one clause earlier.

This is this repository's `a_control_whose_pass_branch_is_unreachable_reports_a_constant_verdict`
shape, arriving sideways: nobody deleted the exclusion, and a correct and well-evidenced change
somewhere else made it dead for its own motivating case.

**The test that guards it would pass with the clause deleted.** That is stated in the test's own
docstring now, beside the assertion, so a reader cannot take its green as coverage. I did not delete
the clause: it is still reachable for a *different* shape — a month that rises when the prior month
also rose (a two-step climb) — which is not what it was written for and not what any test covers.

## What I am NOT claiming

I have not established whether the two-step-climb case occurs in the published book, nor whether the
exclusion earns its place on that case alone. That needs a count over the real run and I have not
run one. **The honest state is: one clause, written for a case it can no longer see, retained for a
case nobody has measured.**

## Next question

Count, on the published book, how many bills have `mom_pct >= 0.20` with the prior month also
`>= 0.20`. If that count is zero the clause is dead outright and should be deleted with its evidence;
if it is non-zero the clause needs a test built on *that* shape, and this test's name should stop
promising the aftermath case.
