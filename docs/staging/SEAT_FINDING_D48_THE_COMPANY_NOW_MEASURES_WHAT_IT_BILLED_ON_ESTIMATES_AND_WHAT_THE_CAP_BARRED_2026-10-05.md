**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `d48-first-build-billed-against-read`

# D48 slice 1: the company now measures what it billed on estimates, the true-up, and what the cap barred

## Where the work came from

The duplicate-work note at draw time named this same id as already held. That holder was this
invocation's own draw: the only live process on it was this seat, started at 21:50, and no rival
`surgical_land` was running. The premise was not spent. `977e17453` (W2_36 slice 2) made a run
outlast the back-billing limit, and nothing on the company side measured it.
`company/billing/billing_accuracy.py` did not exist on origin or in the shared tree.

## What was built

- `company/billing/monthly_bill_assembly._resolve_catchup` now forms the same reconciliation in
  energy as well as money. At the actual read, the register advance over the run is known. The
  run's split by month is not, so only run totals are formed. Each actual-read bill that closes a
  run carries `read_true_up_periods`, `read_true_up_billed_kwh`, `read_true_up_kwh` (register
  advance less what the estimates billed) and `read_true_up_barred_kwh`. These are stamped whether
  or not the money correction is material: an immaterial correction is not billed, but the
  register still moved.
- `company/billing/back_billing.BackBillingAssessment.barred_fraction` exposes the share by days
  that the cap already computed inside `capped_amount_gbp`. The money cap and the energy cap now
  read one rule. The money arithmetic is unchanged.
- `company/billing/billing_accuracy.py` builds one row per account plus totals per fuel, for kinds
  K2 (estimates and true-up) and K3 (barred by SLC 21BA). The kinds are those of
  `docs/market_research/unbilled_energy_and_revenue_assurance.md`. The module reads each bill's
  `billing_basis`, its billed `total_consumption_kwh` and the `read_true_up_*` stamps. It never
  reads `true_consumption_kwh`.
- Production caller: `simulation/run_phase4c_on_phase2b.main()` returns `billing_accuracy`
  through the door `company.interfaces.bill_assembly.billing_accuracy`.

## Pre-registered, then measured

Predictions were written at 21:54:19, before the table was read. The run was
`main(report_end="2020-12-31")`, 129 accounts.

| | Predicted | Measured | |
|---|---|---|---|
| P1 K2 share of billed kWh on estimates | electricity 0.25–0.60 (point 0.40); gas higher | electricity **0.608**, gas **0.590** | **wrong** (both legs) |
| P2 no bill on a read in 12 | 2–8% of accounts | **26/129 (20%)** under the first definition | **wrong**, and the definition was wrong (below) |
| P3 K3 barred share of undercharge kWh | 0.5–5% | electricity **0.36%**, gas **0.05%** | **wrong** (low) |
| P4 net true-up small | \|net\| < 10% of estimated kWh | electricity **+1.7%**, gas **−0.7%** | right |

The gross true-ups are much larger than the net. For electricity they were 76,416 kWh of
undercharge and 64,050 of overcharge, against 729,269 kWh billed on estimates. For gas they were
144,365 and 148,814 against 672,558. The estimate is a trailing three-actual mean, so seasonal
errors cancel over a year and are large within it.

**P2's miss was a definition error, and the measure was corrected before landing.** The first
draft counted accounts that *ever* went 12 bills without a read over five years. The Citizens
Advice measure the note cites is a **snapshot**: of the accounts on supply at a date, the share
with no read-based bill in the last 12 months. Measured that way on the same window:

- electricity **2/43**, gas **1/17**: **3/60 = 5%** at December 2020.
- Ofgem's 2017 median supplier was 5.2–5.6% (note §2 K2).
- With n = 60 the 95% interval is roughly 1–14%. It is **consistent with** the published figure;
  it cannot confirm it.

Leavers are excluded from the snapshot. A leaver's last bill is on a forced final read, so
including them flatters the share. A control holds this, and the mutation "include leavers" reds
it.

**The barred share is low for a reason the window explains.** The cap applies only to bills from
1 May 2018, so 2016–2020 gives it 2.7 years to bind, and only 6 true-ups were barred (5 for
electricity, 1 for gas). The W2_36 sweep's 5.5% is a different quantity: months more than 12
back, at catch-up, over 600 synthetic months. It is not a share of undercharge kWh. **I cannot yet
say** whether the full-decade run's K3 share converges toward it. That needs a full-window run,
and the next slice should read it.

## Controls, and the mutations that red them

- `tests/company/billing/test_billing_accuracy.py`, built through the company's own
  `build_monthly_bills` with a scripted read feed and no `simulation` import:
  - the estimating arm and the every-read-actual arm are asserted in one statement;
  - world truth scrambled on estimated bills leaves the summary unchanged;
  - an immaterial true-up is still measured;
  - the snapshot excludes leavers.
- `tests/simulation/test_run_phase4c_on_phase2b.py`:
  - against the world's own read process, the barred energy is found, and it is zero when every
    read is actual;
  - against `main()`, the `billing_accuracy` key reconciles with the bills beside it.
- Mutations, all red:
  - the measure reads `true_consumption_kwh`: 3 tests fail;
  - the energy stamp is gated on materiality: 1 fails;
  - the barred energy ignores the cap: 2 fail, plus the run-level test;
  - every read actual in the feed: 5 fail;
  - leavers included in the snapshot: 1 fails.

## What this does not do, and the open question

- K1 (the accrual) is not yet graded against these true-ups. That is slice 2, and it is the step
  the D48 mint notes name. K4–K7 still cannot arise (note §5).
- **For the director, as a practitioner question, not a block.** About 60% of kWh is billed on
  estimates in a book that is monthly-billed and mostly traditional-metered 2016–2020. The
  snapshot no-read share matches Ofgem's, so reads are not too rare at the 12-month horizon. Is a
  majority-estimated monthly bill what a GB supplier with this meter mix actually issued? Or would
  customer reads (app or phone submissions) have put most monthly bills on a read? Nothing
  published that this pass found gives the share of *bills*, as opposed to customers, on an
  estimate. If customer reads are the missing source, that is a world change (W2_36) and not a D48
  one.
- Correction made in the record: the knowledge note's K3 row still described the forced read at
  12 months that `977e17453` removed. It is now marked corrected beside the claim, and the K2 row
  carries the D48 figures.
