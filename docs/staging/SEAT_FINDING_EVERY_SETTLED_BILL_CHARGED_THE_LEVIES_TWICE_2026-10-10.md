**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `DD_seasonal_cashflow_physics`

# Every settled bill charged the non-commodity levies twice

*Worker tick, 2026-10-10, drawn on `DD_seasonal_cashflow_physics` (L2 -> 3). Found by printing the
DD book at real inputs before recording anything about it.*

## What was seen

`docs/reports/run_output_latest.json`, annual DD reviews by year and window:

| reviews | median variance | share > 15% |
|---|---:|---:|
| first review (window 0), 2017-2021 | **+24% to +34%** | ~85-90% |
| later reviews, 2019-2021 | +0.5% to +7% | 15-30% |

A level DD set at sign-up was ~25% short of what the household then paid, every calm year, and only
in year one. The portfolio ended **-£81,185 in net debit** across 691 DD customers, with peak held
credit **£9,987** (~£14 a customer, against Ofgem's ~£200 average fixed-DD credit balance).

## Cause, to the penny

Consumption is not the gap: first-year kWh / registry EAC = 0.95-1.01. The rate is. The opening DD
for C1, C2 and C3 reproduces exactly as `(strike x EAC + standing x 365) x 1.05 / 12`; the bill
charges `strike + non_commodity_rate` per MWh. `saas/bill_generator.py` added the blended levy line
ON TOP of `revenue_gbp`, while every settlement writer already holds policy and network inside it --
explicitly for pass-through and flex (`hedged_settlement.py` 189, 508; `gas_settlement.py` 182),
inside the all-in unit rate for fixed and default tariffs (184-192, and the cap they are held under
is all-in) -- and every writer's `net_margin_gbp` deducts them from that same revenue.

June 2024, resi electricity: strike 221.7 £/MWh ex-VAT (cap 245 inc-VAT = 233 ex), plus 74 levy =
295.7, i.e. **billed ~27% above the cap**. Gas: 54.6 + 14 against a cap of 57.5 ex-VAT. The supplier
collected money it never booked. Same shape as the standing-charge double count fixed 2026-07-11,
one line further down the same function.

## Fix

The levy line is carved out of revenue on settlement records; the total is revenue plus VAT and the
printed unit rate is unchanged. Control: `tests/saas/test_a_settled_bill_charges_the_levies_once.py`
(removing the carve-out reds all three legs).

## Predictions, written before any re-run

1. First-review median variance in 2017-2021 falls from ~+30% to within ±10%; share > 15% below 40%.
2. Portfolio final DD balance moves from -£81k to within ±£20k; peak held credit rises above £20k.
3. Resi bill totals fall ~20-25% (electricity) and ~15-20% (gas); settlement revenue does not move (bad debt and
   cash, which read bills, may).
4. Anything reading bill totals moves with them: arrears, bad debt, the debt-to-income figures. The
   arrears finding that the world's arrears sit far above the survey
   (`SEAT_FINDING_THE_WORLDS_ARREARS_RUN_OFF_INCOME_STRESS_...`) should be re-read after this lands;
   part of that excess may be this.

## Not done here

The published run is not re-run in this tick. Until it is, every bill-derived published figure
still carries the double count.

## The drawn atom's state, held here until the map can take it

`DD_seasonal_cashflow_physics` stays at L2. Two of its three residuals were already built: DD4b (a material DD rise at review reaching the world's churn) under PB4 (`simulation/experienced_bill_shock.py`, population A, since 2026-10-01), and opening-DD sizing from an estimate (`D_opening_dd_seasonal_sizing`, 2026-09-02). Its `depends_on: [W2_12_change_of_tenancy_debt_physics]` names a pruned row. What blocks L3 is this finding: re-read the DD book after the published run regenerates, then the expert hour. The note was kept out of the map store in this commit because staging the map selects `test_a_promoted_feed_still_reproduces_at_the_commit_it_records`, which is red at origin itself (`capabilities_door.json` records cf8706023 with the map read off a working tree).

## The re-run (in flight, 2026-10-10)

**sim-runner cannot produce this run.** It runs in the shared tree, whose HEAD (6171b788e) is 71
commits behind origin and whose `saas/bill_generator.py` is the pre-fix copy. Its next cycle would
bill the levies twice again and stamp a commit without the fix -- on top of deferring every cycle
since 11:07 for resident long jobs. So the run is queued from an origin worktree at abb925ec7
(descends from 1d3c28930) through `background.launch_long_job` as unit
`longjob-published-run-single-levy`, writing `/var/tmp/single_levy/run_output_abb925ec7.json`; it
waits for room behind the save suite and the fam1 members.

The grader is `/var/tmp/single_levy/grade.py`. Run over the published cf8706023 run it reproduces
this finding's own figures, so the before and after readings come from one instrument:

| prediction | cf8706023 (levies twice) |
|---|---|
| 1. first-review DD variance, 2017-2021 pooled | median **+32.8%**, share > 15% **90%** (n=621) |
| 2. portfolio DD balance / peak held credit | **-£81,185** / **£9,987** (2024-11) |
| 3. resi bill totals, electricity / gas | **£2,073,168** / **£811,185**; settlement revenue £2,211,737 |
| 4. bad debt (written off / provisioned / ledger) | £8,285 / £94,084 / £58,344; receivables peak £73,931 (2022) |

Debt-to-income is not in `run_output_latest.json`; that leg of prediction 4 will read "cannot yet
tell" from this artefact unless the arrears harness is re-run against it.
