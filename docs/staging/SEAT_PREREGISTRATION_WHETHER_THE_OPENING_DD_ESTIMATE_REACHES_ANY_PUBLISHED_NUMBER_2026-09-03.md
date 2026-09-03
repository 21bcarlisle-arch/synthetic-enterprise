**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Pre-registration — whether the opening DD estimate reaches any published number

*Delivery seat, 2026-09-03, lane-0. Written BEFORE either arm was run and BEFORE any diff was read.
Companion to `SEAT_PREREGISTRATION_WHAT_GIVING_THE_DIRECT_DEBIT_AN_ESTIMATE_MUST_SHOW_2026-09-02.md`,
whose P1–P5 are still ungraded and which this experiment is designed to grade.*

---

## The measurement I am starting from, not re-deriving

Publish `1c4f64733` (run at `4013b1de1`, **before** `company/billing/annual_consumption_estimate.py`
landed at `9760fc7a5`) and publish `b6b3c3fa8` (run at `19f226e46`, **after**) carry **identical**
net margin, gross, capital, treasury start, treasury end, enterprise value, net after cost-to-serve
and bills issued. Whatever the organ did, none of those eight figures felt it.

## The design

Both arms are **pure functions of one seed's issued bills**. `opening_dd` is computed at
`simulation/run_phase4c_on_phase2b.py:319`, *after* `bills` exists, and is passed to exactly three
call sites — `annual_dd_review_view` (320), `build_dd_balance_book` (332), and transitively
`build_dd_level_collection_book` (341, which consumes the balance book). Nothing upstream of `bills`
can see it. So one seed's `bills` is a sufficient and exact substrate for both arms, and running the
100-minute Phase 2b twice would add nondeterminism, not fidelity.

* **Arm F (flat)** — the displaced rule: opening amount = `seq[0][1]`, the first issued bill.
* **Arm E (estimate)** — `_opening_dd_by_customer`, i.e. `opening_monthly_amount` through the seam.

**The control that makes Arm F trustworthy:** `docs/reports/run_output_latest.json` was produced on
2026-09-01, before the organ landed, so its own `dd_balance_book` and `annual_dd_review` **are** Arm
F as the real run computed it. If my reconstruction of Arm F does not reproduce that published book
exactly, the reconstruction is wrong and the whole comparison is void. I will state that check's
result before I state any diff.

---

## Predictions, filed before the run

**Q1 — which run-output keys differ.** I predict the diff is **confined to exactly three keys** —
`annual_dd_review`, `dd_balance_book`, `dd_level_collection_book` — plus, downstream in the report,
`dd3_held_credit_balance_sheet` (which reads `dd_balance_book.summary.peak_held_credit_gbp`). I
predict **no other key of the run output or the report moves at all**, including every one of the
eight headline figures above. If a fourth key moves I have missed a reachability edge and must say so.

**Q2 — the treasury identity is structural, not a coincidence of this book.**
`saas/reporting/annual_report.py:964` states `treasury_cash_balance_gbp` is a running total of
settled net margin. I predict `final_treasury_gbp − starting_treasury_gbp == total_net_gbp` holds by
**construction in the settlement record**, not in the reporting layer, and therefore that **no DD
arrangement whatsoever can move the published cash figure** — the two arms cannot differ on it even
in principle. If instead it is an accident of this book, the published cash figure is a coincidence
and that is the larger finding.

**Q3 — Arm E's unestimated count is large, and concentrated pre-2019.** `opening_monthly_amount`
returns `None` when no cap rate exists for the date, and this repository holds no published rate
before January 2019. I predict Arm E refuses a **double-digit percentage** of the book, that Arm F
refuses **zero**, and that the refused set is **almost entirely accounts acquired before 2019-01-01**.

**Q4 — the two rules agree exactly for essentially nobody.** I predict the count of customers where
Arm E and Arm F chose the same amount to the penny is **0 or near 0**, and that this is a weak
result, not a strong one: two continuous quantities rarely coincide, so a low count evidences
nothing about whether the estimate is *better*.

**Q5 — end-of-year balance drift.** Reported with credit and debit **separately and never summed as
one absolute**. I predict Arm E's drift is **not uniformly smaller** than Arm F's, and specifically
that Arm E will show a *systematic* direction (the estimate is built from a registration EAC and a
cap unit rate, both of which are wrong in a consistent direction for a given year) where Arm F's is
scattered by join month. A systematic bias is a worse defect than a scattered one and I will say so
if I find it.

**Q6 — the basis split is degenerate.** `_opening_dd_by_customer` passes `registry_eac_kwh` and, only
when that is absent, `band="MEDIUM"`. It never passes metered history or a customer declaration. So I
predict the basis split has **exactly two populated values** — `registry_eac` and `tdcv_typical` —
with `metered_history`, `customer_declared` at **zero**, meaning three quarters of `BASIS_ORDER` is
built, tested and unreachable from the only live call site. If so that is a finding of its own class
(`no_caller_and_never_runs`), not a footnote here.

---

## What must NOT happen

1. **No ground-truth annual consumption reaches either arm.** Both arms see only issued bills and
   registration facts. If I find myself reaching for the household's true usage the work stops.
2. **No figure published without its bound.** Any new published per-account figure carries its clock
   and the interval its sample size earns. "We cannot tell the two arms apart" is an acceptable
   published result; a point estimate without a bound is not.
3. **No summing credit and debit drift into one absolute.** They are different customer experiences
   and the mean of the two is a quantity nobody has.
4. **No re-cutting a statistic that disagrees with me.** Q5 is the one designed to refute the organ.
   If it does, that is the result.

## How I will know I was wrong

If Q1 holds *and* Q2 holds, the organ is real but publishes nothing, and the repair is the surface,
not the organ. If Q1 fails — something outside those three keys moves — then the published identity
between the two publishes above is itself the anomaly and needs its own explanation.
