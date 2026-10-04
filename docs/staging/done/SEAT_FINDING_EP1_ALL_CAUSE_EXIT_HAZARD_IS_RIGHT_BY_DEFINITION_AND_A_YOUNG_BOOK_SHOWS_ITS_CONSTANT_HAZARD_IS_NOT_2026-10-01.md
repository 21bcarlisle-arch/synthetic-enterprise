**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1's all-cause exit hazard is right by definition, and a young book shows its constant hazard is not

**Opened by** the result section of
`docs/staging/records/SEAT_PREREGISTRATION_EP1_TENURE_HORIZON_ON_THE_BOOKS_ALL_CAUSE_EXIT_FREQUENCY_2026-10-01.md`.
It closes the build that
`SEAT_FINDING_THE_WORLD_DECIDES_A_RENEWAL_AT_ONE_ANNIVERSARY_IN_FIVE_SO_A_PER_RENEWAL_HAZARD_HAS_NO_AGREED_DENOMINATOR_2026-10-01.md`
pointed to.

## What landed

H2 `tenure_expected` now values on `BookExitRecord`. That is the book's exits at ANY time (from
`ceased_billing_accounts`) over the account-years it has settled, converted to an annual
probability with `1 − exp(−rate)`. `customer_value_view.observed_book_exits` counts it from the
company's own records, truncated at each snapshot. The per-anniversary `BookRenewalRecord` is still
published beside it as a diagnostic, and H2 never reads it. `clv_gap_selection.lifetime_level` reads
`book_exits` first. Without that order it would publish the renewal hazard as the hazard EP1 used.

The director's answer on what a renewal is does not block this. That answer changes the renewal
reading. A tenure ends at a switch, a mid-term switch or a home move alike.

## What the measurement showed

On the real book at 2025 the hazard is 0.137 (89 exits over 606 account-years), where the
per-anniversary reading gave 0.092. Against HEAD's per-anniversary H2, the one-variable gap arm
moves from **1.437 to 1.558**. Every belief year from 2018 to 2022 improves. 2017 (51 of the 69
graded rows) and 2016 (3 rows) get worse.

- **2017: the constant hazard is the defect.** A one-year-old book's exposure is mostly in-term
  first-year time. Its all-cause rate (0.109) is below its per-anniversary rate (0.145), because
  departures cluster at the first renewal. Valuing a customer's whole tenure at a rate averaged over
  that quiet first year overvalues them.
- **2016: one event.** 1 exit over 61 account-years gives a hazard of 0.016 and a ~61-year tenure.
  The n is on the page (`book_exits` on every snapshot), but no bound is. A minimum-event threshold
  would be a picked number, so none was added.

## Next (handed on)

Value H2 on an all-cause hazard **by tenure year**: exits in the account's k-th year over exposure
in its k-th year, pooled across the book. Survival is then the product of those hazards, not a
geometric series. It is company-observable, it needs no new observable, and it addresses both
readings above: the first-year rate is low, and the first-renewal year carries its spike. Until it
lands, the pooled constant hazard is the honest best and it is labelled as constant.

The ledger row still waits. `run_output_latest.json` is the `b1b4c284e` run, produced before
81977a312. Its snapshots carry the 0.05 belief, so `couple_clv --write-ledger` now would grade the
old H2 under this commit's name. The row needs a fresh run promoted through the ordinary publish
path.

## Closed (2026-10-01): H2 values on the book's life table by tenure year

Landed under `ep1-tenure-hazard-by-tenure-year`. `BookExitRecord.tenure_years` is a monthly
product-limit table of COMPLETE tenure years, counted from `acquisition_date`; the anniversary month
closes its year. Each account reads it from the year it enters next (`next_tenure_year`, published
per account on every snapshot). The tail pools complete years from the last one anyone left in. The
one-variable arm takes the gap from 1.558 (constant) to **1.275**, and 2017 from 532 to 449 MAE.
Spearman is unmoved, because 2017's table has one year. The prediction and result are in
`docs/staging/records/SEAT_PREREGISTRATION_EP1_TENURE_HORIZON_ON_A_LIFE_TABLE_BY_TENURE_YEAR_2026-10-01.md`.
The ledger row still waits on a fresh run, as above.

**Correction (2026-10-01, later the same day).** The gaps above (1.437, 1.558, 1.275) were
measured on a belief re-derived from H1 with the wrong divisor, and its margin is off by up to
7.1×. Their direction between hazard arms holds, because the hazard side is exact. Their level does
not: the true life-table belief is **1.173 on 66 rows**. See
`SEAT_FINDING_EP1_REMAINING_OVERVALUATION_IS_THE_MARGIN_DIVIDED_BY_RENEWAL_POINTS_AND_H2_COUNTS_SURVIVAL_TWICE_2026-10-01.md`.

**The ledger row is measured, but it cannot land yet (2026-10-01, autonomous worker).** The first run produced after the
fixes, `af4709ff1` (09:33Z), grades **1.081 on 69 rows**, down from 2.364 at `b1b4c284e`, with
Spearman +0.172. The realised side is bit-identical, so only the belief moved. Predictions and
results:
`records/SEAT_PREREGISTRATION_EP1_LEDGER_ROW_ON_THE_FIRST_RUN_PRODUCED_AFTER_THE_FIXES_2026-10-01.md`.
Any commit that changes `coupled_gap_ledger.json` selects `tests/harness/test_premise_two_level.py`
and `tests/tools/test_couple_fabric.py`. Ten of their tests are red at origin `5e02bbdda` without
this change: the eight in
`WORKER_FINDING_THE_EIGHT_PREMISE_TWO_LEVEL_REDS_…_2026-09-30.md`, plus two in `test_couple_fabric`.
The gate refused the landing on exactly those ten. To re-write the row once they are green, run
`python3 -m tools.couple_clv --run-output <the af4709ff1 output> --write-ledger`, or re-measure it
on any later run.

**Landed (2026-10-01, autonomous worker, read at 18:09).** The paragraph above is superseded. The
row landed at `7a8e651cd` (12:15, on origin): gap 1.081 on 69 rows, run `af4709ff1`. Both selected
harness files are green at `6ed871310` (320 passed). EP1's next ranking step, replicating "legs,
then rate" on a different book, waits on the director's EP17 book-seed ruling, which has not
arrived. See `SEAT_FINDING_EP1_LEGS_THEN_RATE_HOLDS_ON_REDRAWN_DICE_…_2026-10-01.md`.
