**Severity:** RECORDED · **Lane:** D_billing_metering · **Claim:** `d48-slice-2-grade-the-accrual-against-the-true-ups`

# Pre-registration: D48 slice 2, the full-decade K3 share and the grade of the estimated-billing accrual

Filed before `run_phase4c_on_phase2b.main()` was run to the end of the record, and before the grade below
existed. Slice 1 measured 2016-2020 only (129 accounts).

## Full window (`main()` with no `report_end`)

| | Prediction | Reasoning |
|---|---|---|
| Q1 K3 barred share of undercharge kWh, electricity | **0.5%-3%**, point 1.2% | The cap binds from 1 May 2018: 2.7 years of 2016-2020, about 7.7 of the decade. Slice 1 had 0.36% with 5 barred true-ups. |
| Q2 K3, gas | **0.1%-1.5%**, point 0.4%; below electricity | Slice 1 had 0.05%, one barred true-up. |
| Q3 K3 against W2_36's 5.5% | **both fuels stay below 5.5%** | Different quantity (months >12 back at catch-up, over synthetic months; not a share of undercharge kWh). If either fuel reaches it, that is a surprise to explain, not a convergence. |
| Q4 K2 estimated share of billed kWh | **0.55-0.65 both fuels** | Slice 1: 0.608 / 0.590. Nothing in the read process changes after 2020. |

## The grade of the accrual (`saas.ledger.estimated_billing_outstanding`)

It holds an estimated bill as outstanding until a bill with `catchup_applied` covers it. `catchup_applied`
is set only when the money correction is MATERIAL. An immaterial correction still means an actual read
arrived and closed the run.

| | Prediction |
|---|---|
| Q5 Share of the period-end outstanding £ that sits on runs a later actual read has ALREADY closed (immaterially) at that period end | **5%-40%**, point 15%. Non-zero is the defect. |
| Q6 Runs open at a year end and later closed by a read: net true-up as a share of the run's billed kWh | **\|net\| < 5%** |
| Q7 same, gross (sum of \|true-up\|) | **8%-25%** of run billed kWh |

## Added 23:12, after Q1-Q7 were read and before this was run

Q6 failed: runs open at a YEAR END under-billed (net +10% electricity, +24% gas). Explanation offered:
the estimate is a trailing mean of recent actuals, so a run open in December was estimated from autumn
use. **Q8: the same grade at each JUNE month end gives a NEGATIVE pooled net for gas, and an electricity
net below the December figure (+10%).** If gas in June is also positive, the seasonal explanation is
wrong and the bias is somewhere else.
