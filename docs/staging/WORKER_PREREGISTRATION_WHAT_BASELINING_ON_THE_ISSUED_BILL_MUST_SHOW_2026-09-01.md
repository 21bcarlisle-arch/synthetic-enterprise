# [WORKER PREREGISTRATION] What baselining bill shock on the ISSUED bill must show

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01, **before the change and before the run.** Nothing below was written after a result.

## The change, in one line

`company/billing/monthly_bill_assembly.py:533`

    -   previous_bill_total_gbp = true_bill["total_amount_gbp"]
    +   previous_bill_total_gbp = bill["total_amount_gbp"]      # the bill actually issued

**Why:** the world currently measures a household's bill shock against a bill the household never
received. 63% of bills in this book are estimated; what the household experienced is the estimate,
what the instrument differences is the truth. Established in
`WORKER_FINDING_BILL_SHOCK_IS_THREE_CAUSES_AND_A_SIGN_COLLAPSED_INTO_ONE_ABS_2026-09-01`, second
correction: 9,813 of 10,655 pairs (92.1%) reproduce against the previous TRUE total, 3,198 (30.0%)
against the issued one.

## My first prediction was wrong, and it is recorded here rather than quietly dropped

Before computing anything I predicted **uniformly larger shocks** — reasoning that differencing
against an estimate adds the estimation error, and |a+e| averaged over e is at least |a|.

The counterfactual, computed on the published book's own totals, says something different and more
interesting. **The mean rises 7% while the median falls by two thirds.**

## The predictions, with numbers

Computed by re-differencing the 10,654 published consecutive pairs against the previous **issued**
total instead of the previous **true** total. These are first-order: a real run recomputes clarity,
contact propensity, satisfaction and churn, which feed back. So the shock-distribution figures are
the sharp predictions and the downstream ones are directional.

| | current (true baseline) | predicted (issued baseline) |
|---|---:|---:|
| mean `bill_shock_pct` | 0.4190 | **0.4487** (+7.1%) |
| **median** | 0.1616 | **0.0497** (−69%) |
| p90 | 0.8458 | **0.7695** |
| share ≥ 30% | 30.5% | **21.3%** |
| pairs reproducing from the published bill | 30.0% | **~100%** |

**P1.** Median `bill_shock_pct` falls to **0.04–0.06**. If it does not fall, the change did not take.
**P2.** Share of pairs ≥30% falls to **20–23%**, from 30.5%.
**P3.** Mean rises by **5–10%**, i.e. to roughly 0.44–0.46. *This is the one that would have refuted
my original reasoning if it had fallen, and it is kept as a leg for that reason.*
**P4.** Reproducibility against the published baseline reaches **≥99%** (from 30.0%).
**P5.** Mean `clarity_score` **rises**, because clarity is penalised by shock and the typical month's
shock collapses. Contact propensity therefore **falls** and contact volume **falls**.

## Why the predicted shape is the right one, stated before the result

On a run of estimates the household receives **the same estimate each month**, so month-to-month
movement is near zero — and then the catch-up month is a single large jump. Flat, flat, flat, bang.
That is the shape the director described and the shape the published record describes: *"a catch-up
after months of estimates."*

The current model produces the opposite — a constant churn of moderate shocks — because it
differences against a true series that moves every month while the household's actual bills did not.
**So the change should make the distribution more bimodal, not merely larger**, and P1 (median down)
together with P3 (mean up) is exactly that signature. If both hold, the world has stopped smoothing
away the one event this variable exists to represent.

## What would refute the whole change rather than one leg

If the median falls **and** the mean falls **and** the ≥30% share falls, the change has not made the
distribution bimodal — it has simply made shocks smaller everywhere, which would mean estimated
bills track the truth closely enough that the household never experiences a catch-up. That would say
the defect was cosmetic and the change should be reverted rather than kept.

## The R13 direction, stated honestly rather than claimed

The standing rule is that where evidence is ambiguous we choose the option that makes the company's
advantage harder to demonstrate. **That rule does not cleanly apply here, and I am not going to
pretend it does.** This is a correctness fix with a published mechanism behind it, not an ambiguous
choice — and its net effect on the company is genuinely unclear in advance: quieter typical months
flatter us (higher clarity, fewer contacts), while louder catch-up months punish us. I predict the
net effect on churn is **small and I cannot sign its direction**, and I would rather record that than
guess and be right by accident.

## What is NOT in this change

Not the `abs()` — a bill falling still reads as a shock afterwards. Not the cause split. Both remain
owed and both sit **behind** this one, because a sign or a cause attached to a movement measured from
the wrong baseline is a label on the wrong event.

## How the result will be recorded

Appended below this line after the one-variable run, with the predictions above left exactly as
written whether or not they hold.

---
*(result section, empty until the run)*
