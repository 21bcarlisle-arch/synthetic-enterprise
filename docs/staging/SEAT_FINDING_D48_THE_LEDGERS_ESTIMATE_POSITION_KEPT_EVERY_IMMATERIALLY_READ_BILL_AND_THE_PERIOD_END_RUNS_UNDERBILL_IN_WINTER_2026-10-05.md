**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `d48-slice-2-grade-the-accrual-against-the-true-ups`

# D48 slice 2: the ledger's estimate position kept every immaterially read bill, and period-end runs under-bill in winter

## Where the work came from

The duplicate-work note at draw time named this same id as already held. The holder was this
invocation's own draw: the only live process on the item was this seat, started seconds before,
and no rival `surgical_land` was running. The premise was not spent. Slice 1 (`2b8644248`) never
graded the accrual, and K3 had been read only over 2016-2020. Another lane had already renamed
`saas.ledger.unbilled_revenue_accrual` to `estimated_billing_outstanding` the same day, and that
is the function graded here.

Predictions were filed first in
`records/SEAT_PREREG_D48_SLICE_2_FULL_DECADE_K3_AND_THE_ACCRUAL_GRADE_2026-10-05.md` (22:50; Q8 at 23:12).

## What the K1 figure is

`estimated_billing_outstanding` is the whole value of estimated bills whose run no read has yet
ended. It is the "billed on estimate" half of Centrica's "unread revenue", not unbilled revenue,
and the annual report says so. The grade asks two questions:

- Is everything in the figure still awaiting a read?
- For a run open at a month end, what did the next actual read show?

## The defect, fixed in this slice

The ledger cleared an estimate only when a bill with `catchup_applied` covered it. That flag is
set only for a MATERIAL correction (over £5). A run that an actual read closed with a smaller
correction therefore stayed "outstanding" for ever, and the figure only grew. On the decade run:

- **£77,337 of the £93,059** the annual report printed (83%, 1,248 of 1,461 bills) sat on
  estimates a read had already ended.
- Corrected, the figure is **£15,722 on 213 bills**.

`saas/ledger.py` now also clears an estimate that has a later actual-read bill. A read ends the
run whether or not its correction is billed. Pre-registered Q5 put this share at 5-40%. **It was
wrong**: the defect was far larger than predicted, because the figure accumulates over the whole
run.

## The grade

`company/billing/billing_accuracy.estimated_billing_outstanding_grade(bills, as_of)` returns, at a
month end:

- the position the ledger carries (`open_*`);
- the immaterially closed estimates beside it (`closed_immaterial_*`);
- for each open run, the next read's true-up against the run's billed kWh. This is per run,
  because the supplier never learns the month-by-month split.

`billing_accuracy_summary` carries it at every December, per fuel, and
`run_phase4c_on_phase2b.main()` hands it back. It reads only bills, never world truth.

**Decade run, runs open at a year end (pooled 2016-2024):**

| | Electricity | Gas |
|---|---|---|
| Runs graded | 270 | 111 |
| Net true-up / run billed kWh | **+10.3%** | **+23.9%** |
| Gross \|true-up\| / run billed kWh | 17.3% | 53.3% |

- Q6 (\|net\| < 5%) was **wrong**.
- Q7 (gross 8-25%) was right for electricity and **wrong** for gas.

**The cause, tested one variable at a time (Q8, filed before the run).** The estimate is the mean
of the last three actual reads. A run open in December was therefore estimated from autumn use and
under-bills. The same grade at June month ends gives electricity **−1.7%** and gas **−26.3%**.
Q8 predicted negative gas and electricity below +10%: **right**.

The bias is seasonal and comes from the company's estimator. Every period-end position carries it:
a December book is understated and a June book overstated. Centrica estimates "taking into account
weather patterns". Our estimator has no seasonal profile at all. A profile-shaped estimate
(EAC/AQ with a profile class) would remove most of this bias. That is the next piece of work for
this lane, and it changes what the customer is billed. It is not done here.

## K3 over the full decade (2016 to June 2025, 175 accounts)

| | Predicted | Measured | |
|---|---|---|---|
| Q1 K3 barred share, electricity | 0.5-3% | **1.05%** (17 barred true-ups) | right |
| Q2 K3, gas, and below electricity | 0.1-1.5%, below electricity | **1.25%** (6) | in range; **wrong** on the order |
| Q3 both below W2_36's 5.5% | yes | yes | right |
| Q4 K2 share billed on estimate | 0.55-0.65 | electricity 0.581, gas **0.531** | electricity right; gas **wrong** (just below) |

- The share roughly trebled for electricity and rose about 25-fold for gas once the cap had 7 years
  to bind instead of 2.7.
- It is still a fifth of 5.5%. That figure is a different quantity, so the gap is not a
  discrepancy.
- Gas exceeds electricity on very few events (6 barred true-ups). With counts this small, the order
  of the two fuels is not established.
- Snapshot of accounts with no bill on a read in 12 months, at June 2025: electricity 2/48, gas
  1/27, so 3/75 = 4%. Ofgem's 2017 median was 5.2-5.6%. With n = 75 the interval is roughly 1-11%.

## Controls and the mutations that red them

- `tests/company/billing/test_billing_accuracy.py`:
  - every branch of the grade (open, graded, never read, immaterially closed) is shown reachable in
    one statement before what each holds is asserted;
  - the grade's position equals the ledger's on a book that holds an immaterial closure;
  - the year-end grades are carried in the summary.
- `tests/saas/test_ledger.py`: a read with an immaterial correction clears the estimate, and the
  estimate after it stays outstanding.
- `tests/simulation/test_run_phase4c_on_phase2b.py`: on `main()`'s own bills, the grade equals the
  ledger and a year end exists in the window.
- Mutations:
  - revert the ledger leg: 2 fail;
  - an immaterial closure left in the open run: 2 fail;
  - grade from the next bill whatever its basis: 1 fails;
  - `as_of` ignored: 1 fails;
  - drop `catchup_applied` from the grade's coverage test: **0 fail**. This is an equivalence,
    not a missing test: `catchup_period_start`/`_end` are stamped only inside the material block
    (`monthly_bill_assembly.py:530`), so the flag adds nothing to the range test.

## Corrected in the record

The knowledge note's K1 row now carries the fix and the seasonal grade, and its K3 row carries the
decade figures, each beside the claim.
