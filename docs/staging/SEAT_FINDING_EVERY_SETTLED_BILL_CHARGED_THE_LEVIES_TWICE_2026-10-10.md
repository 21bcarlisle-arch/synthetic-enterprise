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

## The grade (run finished 14:50, 2026-10-10)

The run finished at 14:50. Its payload stamps **`7379375f6`**, the run worktree's HEAD and not the
`abb925ec7` in the file name. It descends from 1d3c28930 and is on origin. Same grader, same keys:
before is in `/var/tmp/single_levy/grade_before_cf8706023.txt`, after in
`grade_after_abb925ec7.txt`, and the run is at `/var/tmp/single_levy/run_output_abb925ec7.json`.

**This is not a one-variable comparison.** cf8706023..7379375f6 is 74 commits, and 9 of them touch
the world or the company: move-out notice, gas-only change of tenancy, a gas meter needed on a gas
arrival, switching at renewal, the B8 retention holdout, and the retention offer at a term. Gas is
the clean leg: 12,976 bills and 11,382,289 kWh in both runs, identical to the kWh. Electricity
moved +0.9% in kWh (25,462 to 25,527 bills), so it is read per MWh.

| prediction | before (cf8706023) | after (7379375f6) | grade |
|---|---|---|---|
| 1. first-review DD variance 2017-2021: median within ±10%, share > 15% below 40% | +32.8%, 90% (n=621) | **-1.8%, 17%** (n=620); every year 2017-2021 is between -4.5% and +3.9% | **MET** |
| 2. final DD balance within ±£20k; peak held credit above £20k | -£81,185 / £9,987 | **-£39,344 / £19,105** (2024-11) | **NOT MET**, on both legs |
| 3. resi bills: elec down 20-25%, gas down 15-20%; settlement revenue unmoved | £2,073,168 / £811,185; rev £2,211,737 | £1,663,007 (-19.8%; **-20.5% per MWh**, 312.9 to 248.7 inc-VAT) / £671,942 (**-17.2%**, same kWh); rev £2,228,274 (+0.75%, with kWh +0.9%) | **MET** (elec on the per-MWh reading; the raw total sits 0.2 pt outside the band because volume moved) |
| 4. figures reading bill totals move with them | see below | see below | **MET on the four bill readers**; the provision is not one; debt-to-income cannot yet tell |

**Prediction 2, why it missed.** The portfolio balance month by month (before to after):
2016-12 -£22.6k to +£1.5k; 2018-06 -£63.5k to **-£20.6k**; 2021-12 -£53.4k to -£19.7k; 2023-06
-£284k to -£238k; 2025-06 -£81k to -£39k. The fix removed about £40-45k of steady pre-crisis
net debit. It did not create a summer credit build. Held credit before the crisis stays at
£2-6k across ~600 DD customers, about £5-10 each against Ofgem's ~£200, and the book is £20k net
debit by mid-2018. That residual is not the levy. The prediction assumed the levy was the whole
pre-crisis gap, and it was not. What drives the rest is the open question for
`DD_seasonal_cashflow_physics` L3, now that the double count no longer hides it. **I cannot yet say
what it is.** The other 73 commits are not ruled out, because this run changed more than one thing.

**Prediction 4, per figure.** Ledger total billed £2,890,673 to £2,334,378 (-19.2%). Bad debt
written off £8,285 to £6,460 (-22%). Ledger bad debt £58,344 to £47,099 (-19%). Back-billing
write-off £43,334 to £22,469 (-48%). Receivables peak (2022) £73,931 to £66,460 (-10%).
**Provisioned bad debt £94,084 to £94,999 (+1%) did not move.** Cash at 2025 fell £1,211,253 to
£684,780 (-£526k), about the £556k fall in total billed: the supplier's cash had been holding the
over-collection. Treasury £739,345 to £746,471 and total net £489,345 to £496,471 barely moved,
because both read settlement. Most of the bill readers moved with the bills; the provision did not.
Debt-to-income is not in the artefact. The prediction is graded "cannot yet tell" for two reasons:
the provision's non-move is unexplained until each bad-debt figure is traced to its source (the
continuation `the-levy-findings-bad-debt-leg-is-sourced-before-it-is-graded`, refused at today's
draw as held by `/var/tmp/se-cap`), and debt-to-income needs the arrears harness re-run on this
artefact (`the-arrears-grade-is-retaken-on-single-levy-bills`).

## Prediction 4, each figure traced to its source (2026-10-10, continuation `the-levy-findings-bad-debt-leg-is-sourced-before-it-is-graded`)

Prediction 4 is about figures that read bill totals, so each figure's source decides whether it
is covered. Each one below was traced in the code at 7252e8d72, then checked against the ratio
it should keep fixed: a settlement reader keeps a constant share of settlement revenue, and a
bill reader keeps a constant share of ledger total billed.

| figure | where it is computed | reads | share of its base, before to after | moved with the bills? |
|---|---|---|---|---|
| provisioned bad debt £94,084 to £94,999 | `simulation/run_phase2b.py` 4201-4202, `revenue_gbp x world_bad_debt_incidence x stress`, frozen as `provisioned_total_bad_debt` by `settlement_clocks.refresh_settlement_scalars` | settlement revenue | 4.254% to **4.263%** of settlement revenue | **not a bill reader**, so it is outside the prediction. Its non-move is what its source predicts |
| bad debt written off £8,285 to £6,460 | `arrears_engine.emergent_bad_debt_lines` via phase 4c; payments resolved against `bill["total_amount_gbp"]` (`arrears_engine.py` 831) | issued bills | 0.287% to 0.277% of billed | **yes** (-22% against -19.2% billed) |
| ledger bad debt £58,344 to £47,099 | `saas/ledger.build_ledger`: `payment_behaviour.bad_debt_provision_gbp(credit_risk, b["total_amount_gbp"])` | issued bills | 2.018% to **2.018%** of billed | **yes**, exactly, because it is a rate times the bill |
| back-billing write-off £43,334 to £22,469 | `accounting_close` -> `make_dd_back_billing_write_off_event` over `dd_balance_book.bar_actions`; after the fix £22,097 of it is DD bars at final bills | the DD balance (bills minus level DD) | 1.50% to 0.96% of billed | **yes**, and by more than the bills (-48%), because it reads a difference that the levy had inflated |
| receivables peak (2022) £73,931 to £66,460 | `company/finance/double_entry` account 1100 over the ledger events (billing less payment) | open balance on bills | 2.56% to 2.85% of billed | **yes** in direction (-10%). It is a balance, not a flow, so it is not proportional |
| debt-to-income | not in the artefact | -- | -- | **cannot yet tell** (`the-arrears-grade-is-retaken-on-single-levy-bills`) |

**Grade: MET on the four bill readers; the provision falls outside the prediction; debt-to-income
cannot yet tell.** The provision is called "provisioned", but it is the world's incidence applied
to settlement revenue, which the fix left unchanged (+0.75%). Grading its non-move as a miss would
have read a correct no-move as a refutation.

**There are two arrears books with different bases.** The world's payment triad
(`_payment_month_open`, `run_phase2b.py` 4226-4238) accumulates `revenue_gbp`. That is why the
arrears re-take at 1f35bc21f did not move: the world never asked households to pay the double
levy. `arrears_engine` resolves payments against bill totals, and that is why written-off bad debt
did move. Until 1d3c28930 these two books disagreed by the levy on every bill. On this run, ledger total billed ex-VAT (£2,334,378 / 1.05 = £2,223,217) is
within 0.23% of settlement revenue (£2,228,274), where before it was 24.5% above it. This is
recorded here, not fixed: after the fix they should not diverge, and whether
two books should exist at all is a question for `DD_seasonal_cashflow_physics` L3. It is not a
levy question.

## Not on origin yet, and Monday's publish may not get it there

The run is graded, not published. Two things hold it back.

1. **The weekly window.** Figures go to origin from Monday 04:00 London (director, 2026-09-26,
   `process_run_complete` "THE WEEKLY WINDOW"). sim-runner's cf8706023 run was HELD at 02:46 for
   exactly that reason. Promoting this run and its pages by hand mid-week would bypass his cadence,
   so `docs/reports/run_output_latest.json` on origin is still 998814330 (2026-10-05). Every
   published page (`site/data/customers.json`, `supplier.json`, `dashboard.json`, `company.json`,
   `customer_sample.json`, `margin_bridge.json`, `sim_data.json`, `site/state/billing_ledger.json`,
   and the annual report and LATEST.md) quotes that pre-fix run. No published page carries the
   single-levy figures yet.
2. **GitHub refuses a file over 100 MB, and the run is 123.5 MB.** Every sim-runner run since
   2026-10-09 13:01 is ~120 MB (indent=2), against 26 MB for the 10-05 run that last reached
   origin, and `git_commit_push` commits `run_output_latest.json` beside `customers.json`. Measured
   on this run: compact JSON is 91.5 MB, which fits with 8% to spare; gzip is 11.5 MB. `bills`
   alone is 37.7 MB compact. Unless the committed copy shrinks, the first publish after the window
   opens will be refused at push. Filed separately:
   `SEAT_FINDING_THE_PUBLISHED_RUN_OUTGREW_GITHUBS_FILE_LIMIT_2026-10-10.md`.

On Monday, sim-runner will publish its own run. That run carries the fix only if the shared
checkout has advanced past 1d3c28930 by then (at 14:30 it was 87 commits behind origin).
