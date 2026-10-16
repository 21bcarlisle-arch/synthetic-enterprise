**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `D46_the_validator_holds_against_the_varied_population` · **Claim:** none (found by the billing-ledger move, 2026-10-14)

**Discharged:** `tests/company/billing/test_a_held_estimate_is_reconciled_as_billed_nothing.py::test_a_held_estimate_is_reconciled_as_billed_nothing_and_a_sent_one_as_what_was_sent`,
`tests/company/billing/test_a_void_stubs_estimate_is_priced_at_its_own_tariff.py::test_a_void_stubs_estimate_is_charged_at_the_rows_tariff_and_a_row_without_one_keeps_the_true_bill` -- both billing causes are repaired at origin (650fdcdd7, e6785dce5) under these controls, and the defect4 sweep reds a tenth inversion. What remains is deleting the nine KNOWN_OPEN_INVERSIONS rows once a ledger billed by that code is committed (the 2026-10-19 publish); that is a dated follow-up, not an untrustworthy control, so it no longer draws ahead of the lane (worker, 2026-10-16).

# Nine customer-years bill less than their own gross margin at origin, and no census holds the test

**Fate (2026-10-15):** ATOM -- folds into `D46_the_validator_holds_against_the_varied_population` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-14):** ATOM -- D lane: a red at origin that no census holds. First this week, if a gap allows; otherwise the first billing item next week.

`tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`
is **red at untouched origin/main `440ebe1f6`**. A control run in a fresh origin worktree, with
none of the ledger-move change in it, failed in 0.7 s. The ledger move does not cause it: the
`site/` and `docs/` copies were byte-identical (`cmp`). It reads the committed ledger of run
2248e3baf, the founder-ruling book.

It reports 9 customer-years whose billed total is below the gross trading margin, which the test
says cannot happen by definition. The first five are `OCC-25ff8966357a` 2022 (0.57 vs 3.22),
`OCC-b7693802f91c` 2016 (0.59 vs 2.41), `PROS-2017-0117` 2018 (299.37 vs 881.07),
`PROS-2017-0336` 2017 (618.78 vs 690.85), and `PROS-2017-0336` 2018 (−106.00 vs 2,073.73).

Neither `head_red_observed.json` nor `HEAD_RED_REGISTER.md` names it. This is the same gap as the
stayers-control finding (2026-10-14): a test whose data is the committed run artefact goes red when
a publish lands, and the census never sees it.

**I cannot yet say** which of these explains it: (a) a real billing defect on the bigger book,
for example a credit or catch-up netting the year's billed total negative (PROS-2017-0336 2018
bills −£106); (b) a calendar-year attribution mismatch between the ledger and `cdata` for
part-year occupiers (the OCC- ids); or (c) a definition the test assumes that the founder-ruling
book no longer meets. The next step is to print the bills and the margin for PROS-2017-0336 2018
at real inputs before choosing.

## First reading at real inputs (same turn)

All nine are 4 OCC/PROS-2017-0117/PROS-2025-0106 years plus six years of PROS-2017-0336. The
inverted accounts are where the ledger's invoices have **holes**. Of 38,054 consecutive invoice
pairs across the book, 11 have a gap of more than a day. Three examples: PROS-2017-0117 has no
invoice from 2017-11-30 to 2018-04-01, and PROS-2017-0336 has none from 2017-11-30 to 2018-02-01
or from 2018-02-28 to 2018-05-01. Yet PROS-2017-0336's catch-ups credit exactly those holes:
−£271.29 for 2018-03-01..04-30 and −£1,274.42 for 2018-06-01..10-31. The account is credited for
over-estimates that the ledger never shows being billed. `meta.held_bill_count` is 41.

**Leading explanation (not yet one-variable tested):** an estimated bill held by
`validate_bills` drops out of the ledger, but the next actual read's catch-up is still computed
against it. That would be a credit with no matching charge, which is a real customer-facing
defect (b-side of (a) above). One existing register entry ("the leaver's final actual bill is
held by validate_bills") is the same family. The test is the place to start:
print, for one gap, whether the bill generator produced and held an estimate for that period.

**What was done so the control keeps its teeth:** the nine are named in
`KNOWN_OPEN_INVERSIONS` under one reason pointing here. That lets the move of the ledger out of
`site/` land, because the test sits in its file scope. A tenth inversion still reds. Clearing this
finding means removing those nine rows.

## The leading explanation, confirmed by the print (delivery seat, 2026-10-14 evening)

The ledger's `exception_queue` (41 held bills) fills the invoice holes exactly:
- PROS-2017-0117: held 2017-12-31, 2018-01-31, 2018-02-28 and 2018-03-31. The hole runs from
  2017-11-30 to 2018-04-01.
- PROS-2017-0336: held across both holes, and through 2018-2020 (27 months).

Every hold carries the same two reasons: `vat_by_segment`, because a declared resi account meters
2,300-4,400 kWh a month, which looks like an SME-as-household mislabel; and
`slc_6_7_billing_accuracy`, which calls that implausible for resi.

So two layers, now separated:
1. **World:** two prospects drawn as residential with SME-scale use (about 30-50 MWh a year). A
   real book has such mislabels. Holding the bill is what a real supplier does, so it is not by
   itself a defect.
2. **Company, the defect:** `validate_bills` holds bills AFTER assembly (company/interfaces/
   bill_assembly.py, accounting_close.py, run_phase4c). But `_resolve_catchup`
   (company/billing/monthly_bill_assembly.py) reconciles the estimated run DURING assembly, as if
   every estimate were billed. The next actual read credits `true - billed` for months whose
   estimate never reached the customer. The fix makes holding known at assembly (a held period
   carries billed 0), or reconciles after holding. It moves billed totals across the book, so it
   is a pre-registered change, not a patch: next week's first billing item.

## Graded 2026-10-15: the fix holds where it can be measured; 5 of 7 rows are ungraded

On the one-variable run (2248e3baf + 650fdcdd7's assembly hunk), PROS-2017-0117 2018 and PROS-2025-0106
2025 clear to the penny of the prediction. The two OCC rows stay red as predicted, with no held bill.
The five PROS-2017-0336 rows cannot be graded: that run's book does not draw the account. Two runs at
one commit drew different households from 2016-02-13
(`WORKER_FINDING_TWO_RUNS_AT_ONE_COMMIT_DRAW_DIFFERENT_BOOKS_FROM_FEBRUARY_2016_2026-10-15.md`).
Grades are written beside each prediction in
`records/SEAT_PREREG_A_HELD_ESTIMATE_IS_KNOWN_AT_ASSEMBLY_2026-10-15.md`. This finding stays open, and
so do its `KNOWN_OPEN_INVERSIONS` rows, until PROS-2017-0336 is graded.

## Graded 2026-10-15 22:40: all seven held-estimate rows clear on A's own book

On X1 against X0 (`81c129fe8` with and without the assembly hunk, X0 equal to A bill for bill),
all five PROS-2017-0336 rows clear by their predicted deltas. The book rises £20,335.72 on exactly
the 11 catch-ups, and no bill is newly held. The defect4 sweep reads 9 inversions on X0 and 2 on X1,
which are the two OCC December stubs, the D46 remainder. Grades are in the prereg record. The
seven `_HELD_ESTIMATE_NETTED` rows are deleted by the first landing whose committed ledger carries
650fdcdd7 (the 2026-10-19 publish). Until then the ledger is run A's, and deleting them reds the
gate. The finding's billing cause is closed. Its atom fate (D46) stands for the two stubs.

## The two OCC rows are void stubs billed an estimate at 0p (worker, 2026-10-16)

P3 put these two down to the test's day-weighting, "not billing". The day-weighting is real.
But printing the invoices shows a billing defect under it, and the defect is bigger than two rows.

- **What the stub is.** `OCC-25ff8966357a` 2022-12-24..31 bills 55 kWh at **0p/kWh**: commodity
  £0, non-commodity £0, standing charge £3.22, total £3.38. Its next month bills £6.31 a day.
  The account-year's gross margin is £3.22, the standing charge exactly. These are B7 void rows:
  `as_void_row` (sim/customer_state_layer.py) zeroes the energy and leaves the owner's standing
  charge. `OCC-b7693802f91c` 2016-12-26..31 is the same shape (34 kWh at 0p, £1.21).
- **Why 0p.** The company cannot see the void. With no read it estimates the period from the
  registry EAC (`opening_estimate_kwh`), as it should. But `build_monthly_bills` prices the
  estimate by scaling the true records, and only when `true_kwh > 0`. Otherwise it falls back to
  the true bill. The code calls that branch "rare". So a void stub prints the estimate and charges
  the truth, and whether the estimate is priced depends on a fact only the world holds.
- **How many.** 60 invoices on the 2248e3baf ledger price a positive kWh at 0p, all OCC: 57 are
  opening stubs and 3 are second invoices where the void runs on. Together they hold 11,447 kWh,
  and 35 sit inside a later catch-up window. 57 OCC opening stubs bill under 30% of their next
  month's daily rate; no PROS or C account does.
- **Why it inverts.** Raw stub totals sit just above margin (£3.38 vs £3.22). The over-estimate
  credit at the next actual read (−£98.62 over 2022-12-24..2023-09-30) is spread by day, so the
  stub takes a share although it over-billed nothing. Netted, it falls to £0.57.

**The repair is D46's next slice, and it is a choice, not a patch.** The estimate needs a rate the
company can name. From 2019 the cap is the default tariff's price (`get_cap_unit_rate_for_date`).
Before 2019 there is no cap; the company's own default tariff is the rate, and today it reaches
only renewals (`own_default_tariff_inc_vat_gbp_per_mwh` through company/interfaces/renewal_rate_chain.py),
never `build_monthly_bills`. Prediction for when the repair lands, written before it exists: the
60 invoices rise by estimate × default rate × (1+VAT). The next actual read credits that back,
because the void's true kWh is 0, so run totals move by pennies outside held runs. Both OCC
inversions clear with no change to the test's netting. Until then the two rows stay in
`KNOWN_OPEN_INVERSIONS`, under a reason that now names the void.

## The void stub's estimate is priced at its own tariff (worker, 2026-10-16)

Knowledge first: `docs/market_research/back_billing_and_liability.md` §14. `build_monthly_bills`
now prices an estimate over a 0 kWh period at the settled rows' `unit_rate_gbp_per_mwh`. The
estimate is spread evenly over the rows, and the standing charge is unchanged. Control:
`tests/company/billing/test_a_void_stubs_estimate_is_priced_at_its_own_tariff.py`. It is
mutation-proven: switching the branch off reds both tests. Both branches are asserted reachable,
because a row with no rate keeps the true bill.

**Correction beside the earlier claim.** The section above proposed the cap from 2019, and the
company's own default tariff before that. The rows already carry a better rate: the tariff the
account is actually on. For an OCC account that is its deemed rate, which is the capped rate from
2019. So the rows' rate is used. **GAP, carried in the code:** on a pass-through term the row rate
leaves out the policy and network costs that term adds, so that estimate is priced low. The
catch-up corrects the total.

**Prediction, written before any run grades it.** On the next committed ledger billed by this code:
1. The OCC opening-stub invoices that price a positive kWh at 0p go from 60 to 0. Any left will be
   pass-through or rate-less rows, and each will be named.
2. Each of those invoices rises by estimate × rate × (1 + VAT). On a run of estimates the next
   actual read credits the same amount back, because the void's true kWh is 0.
3. Book billed totals outside held runs move by under £5 in total. The only movement is the timing
   of that credit across a year boundary.
4. Both OCC rows stop inverting. The test's netting is not changed.

The two `KNOWN_OPEN_INVERSIONS` rows stay until that ledger is committed, as the held-estimate rows
do. With them gone, this finding's billing causes are closed.
