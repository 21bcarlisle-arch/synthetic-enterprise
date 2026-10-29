**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The printed-register fix exposes estimates set from one read and prints 6,436 opening reads nobody took (2026-10-28)

**Source.** A fresh full run at 37abacdf42 (`fresh-run-37abacdf42`), graded against its pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_THE_PRINTED_REGISTER_FIX_GRADED_ON_A_FRESH_RUN_AT_37ABACDF42_2026-10-28.md`
(results section). The fix does what it claimed: `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` falls 292 → 153 and
`INV_PERIOD_MATCHES_READS` stays 0. BLOCKING because the correctness stretch's exit test needs zero unexplained
breaches, and three of the four items below are an energy reader's objection on a printed bill.

## E1. Estimates set from one read (8 of 13 breached runs)

After an occupier's first, often short, month, every later estimate scales from that one advance. On
OCC-f6813bf9f05eg gas, 138 kWh in Oct 2016 is followed by eight estimates totalling about 1,890 kWh, against about
8,065 kWh on the meter. Before the fix, the printed register hid this. It is the same kind of cause as the zero-advance
fix (`estimate_unread_kwh`: a zero-kWh window establishes nothing), but for a window of one month.
**Next:** K8 first. Establish what a supplier estimates from when it holds one read (BSC default EAC, or gas AQ, from
the registry). Then let `company/billing/unread_month_estimate.estimate_unread_kwh` fall back to the registry figure in
that case. Whatever minimum it sets must be sourced, not picked.

## E2. Summer over-estimates on heating households (5 of 13)

Estimated runs over summer, on households using 9.6 to 34.5 MWh a year, come out 3.0 to 5.5 times the meter.
PROS-2017-0336 electricity uses about 300 kWh a month in summer and was estimated at about 1,600. The estimate's
seasonal shape is flatter than the household's. Not traced. It may be the profile the estimator applies, or the
reference window carrying winter months into a summer estimate. A real supplier on a Profile Class 1 shape would also
misestimate an electrically heated home, so whether the band or the estimator is wrong is part of the trace.

## E3. 6,436 actual bills open on a read the supplier never saw

An actual bill after an estimated run prints `register_opening_kwh` = the register less the month. That is not the
previous bill's closing (6,435 of 6,444 E→A transitions), and no meter or customer ever gave it. Example: C3g gas,
Dec 2016, previous estimated closing 3,839.2, printed opening 5,942.3, closing 8,419.1. The K8 page's own §13 practice
(`docs/market_research/back_billing_and_liability.md`) is that the opening is the previous estimated reading and the
advance covers the catch-up. The page records this as the design's Limit. No invariant grades it, so it passes the
suite and would fail a cold reader.
**Next:** print the previous closing as the opening on an actual bill. Show the advance as the month plus the catch-up
the bill already carries, so that closing − opening equals the billed kWh plus the catch-up kWh. Add a blind row: on an
actual bill, the opening equals the previous bill's closing for the same meter.

## E4. ToU band indices do not sum to the total (417 of 1,189 invoices, 39 of 79 accounts; 223 before)

The fix re-anchors the total index to the register, not the bands. The 223 predate it (a band does not advance while
the household is on a single rate). The fix adds 194. No row grades it.

## E5. The 153 residual, partly diagnosed

The estimate-window fix (c4738b64c9) removed 37 and set 39 new breaches on 6 accounts. 114 carry over from R3's scratch
ledger. The open cause is the gap between the estimator's reference window and the row's. It is excepted at 153.

## Disposition: E1 and E3 built (2026-10-28, lane 0 `the-one-read-estimate-and-the-printed-opening`)

**E1.** K8 first: `how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §7. The published
minimum is the one the annualised advance already used: reads at least 6 months apart (DESNZ on the
BSC's AA) and, for gas under the switch, 9 months (Xoserve's AQ). Until the company's reads span it,
`build_monthly_bills` bills the registry figure spread by the shape (`opening_estimate_kwh`). No new
number. Not yet measured on a book: the estimate is set in the run, so it needs a fresh run.
**Prediction, filed before any such run:** `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` falls from 13
to between 3 and 7 (point 5, the summer heating runs, E2). The 8 one-read runs leave, unless an
occupier's registry figure is itself far from its use. `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`
moves an unknown amount in an unknown direction: I cannot yet say, because that row reads the latest
actuals, and the registry figure does not.

**E3.** K8: `back_billing_and_liability.md` §13, corrected beside the old Limit. An actual bill after
estimates opens on the previous closing and prints `catchup_kwh`, so closing − opening = usage +
catch-up. The new blind-suite row `INV_OPENING_IS_THE_PREVIOUS_CLOSING` grades it. On the 37abacdf42
book, with the ledger rebuilt at this change: openings off the previous closing go from 6,436 to 0
(`chain.py`). The new row goes from 6,405 on the old ledger to 13 on the new one. Every other
invariant's checked, breached and flagged counts are identical to origin/main's rebuild of the same
book, and no bill is held. The 13 are accounts coming back from ToU (E4's class) and are excepted at
13. **The row was written by the seat that changed the ledger, not by a reader blind to the code.**
The row says so in its `gap`.

**Still open here:** E2 (summer over-estimates), E4 (ToU band indices; `chain.py`'s band-sum count
moves 417 → 433, because its base is taken from the first ToU bill's total opening, which this change
moves on 16 accounts), E5, and the fresh run that grades E1.

**E5 traced (2026-10-29, on the 209c3350ab book).** The "gap between the estimator's reference window
and the row's" was the row's. It stopped its long window at 365 days and at actual reads. Its own cited
page gives 6 to 36 months, and the estimator annualises the advance nearest a year in 182 to 731 days from
any read it holds, the change-of-supply read included. Of the 269 on that book, 90 sat outside E1's
branch, and all 90 were this. The row now takes its window's ends from the page, and all 90 pass. 179
remain, all of them E1's class, and the E1 finding carries them. E5 is closed.
