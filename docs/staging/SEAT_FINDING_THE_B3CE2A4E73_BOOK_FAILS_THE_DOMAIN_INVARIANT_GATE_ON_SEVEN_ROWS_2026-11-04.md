**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The b3ce2a4e73 book would be refused by the domain-invariant gate: 203 unexcepted breaches on seven rows (2026-11-04)

**Source.** `/var/tmp/fresh-grade-b3ce2a4e73/grade.txt`, the whole suite over 1,291 accounts, `enforce: true`. Full table
and the departures from the 85b044be54 chain in
`docs/staging/records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_AGAINST_ITS_FIXES_PREDICTIONS_2026-11-04.md`.
It is BLOCKING because the publisher would refuse this book when the window opens and the ruling's exit test is this gate.

| Row | Breached | Exception ceiling | First examples |
|---|---:|---:|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 128 | none | OCC-75d17c23c1da, 2022-07-16 to 2022-09-16: page prints 336.84 overdue against a balance of 273.62, on `arrangement_offered` and `repayment_plan_reoffer` steps |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 53 | 3 | OCC-00909e50a521 electricity 2020-02..06 (5 bills) ratio 0.235 against a band of 0.333-3.0; OCC-14d60fd5bb78, OCC-288aa561d534, OCC-2cf83688b2d2 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 6 | PROS-2017-0233 electricity 2019 and 2020 (10 and 5 months billed on the carbon panel), PROS-2020-0167 2024 |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 5 | 1 | OCC-bad56e8f97f9 (revenue 2595.34 against 857.08 billed), PROS-2020-0025, OCC-8c6b8bb21743, SYN-2016-264, SYN-2016-604g |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 1 | none | SYN-2016-110 electricity 2018-11 |
| INV_PERIODS_CONTIGUOUS | 1 | none | SYN-2016-604g gas, 2017-06-30 -> 2017-08-01, 32 days |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | 1 | none | SYN-2016-604g gas register 1, 2017-08-01, opening 253.6 kWh above the previous close |

**What it is not.** The four rows the 85b044be54 grade refused on (E7 two registers, read monotonic, ToU bands sum, estimate
after actual) are 0, 0, 0 and 1. The three supplier fixes' predictions hold except the cap edge (separate finding).

**Attribution: I cannot yet say.** More than one thing changed between the two books. Two cautions for whoever draws this:
- The revenue row compares page revenue (here from `per_customer_lifetime`, a substitution for summing `p2b__all_records`
  that the pickle chain used) against page bills. Re-grade it from the pickles, or from the pages built in
  `/var/tmp/fresh-grade-b3ce2a4e73/tree`, before treating the five as the book's.
- `INV_OVERDUE_WITHIN_PAGE_BALANCE` was CLEAN on the 85b044be54 grade (0), so 128 is a new regression, not a first
  count. The five examples the runner keeps are all one account, OCC-75d17c23c1da, on `arrangement_offered` and
  `repayment_plan_reoffer` steps printing 336.84, 316.80, 352.72 overdue against balances of 273.62, 253.58, 289.50.
  N15 (6a3da3e48) changed exactly when a re-offer step exists, and the commit's test names no print-side row. Candidate,
  not attribution: the steps that now survive are the ones where the standing arrear exceeds the page's balance.
  Related and older: `SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.

**Prediction, filed before any trace:** the 53 estimated-run breaches concentrate on the accounts N14's second pass
re-billed (`rebill_catchups_off_direct_debit`, 63 on the 0a6391d186 book), because that pass rewrites the estimated runs
this row bounds; if fewer than half of the 53 are on re-billed accounts, the cause is elsewhere (candidates: the world
change moving true use under the estimates, or the draw). Two accounts, SYN-2016-604g's pair, are one gap in a gas
leg's periods in 2017 and look like a single defect.

**Reverse:** delete this file.

## Prediction before tracing INV_OVERDUE_WITHIN_PAGE_BALANCE (filed 2026-11-04, before the 4669d77ddd re-grade was read)

The steps that 6a3da3e48 (N15) and ba868134c keep are the re-offers on days a bill was truly unpaid. Prediction: the
breaching steps are those where the desk's standing arrear (`undisputed_overdue_gbp`) is larger than the page balance,
and they are re-offer/arrangement steps that the calendar trigger used to fire on days the page balance had already
caught up. Before N15, the breach was there on these accounts too and was diluted, not absent: refuted if fewer than
half of the 4669d77ddd breaches are `arrangement_offered` or `repayment_plan_reoffer` steps.

## Re-graded on the 4669d77ddd book (2026-11-04)

`run_output_4669d77ddd_20261104T132452Z.json`, the same chain (`/var/tmp/b3ce-grade-scripts/`) at origin 61ddb41250,
scratch `/var/tmp/grade-4669/`. ba868134c and 4669d77dd moved none of the seven:

| Row | b3ce2a4e73 | 4669d77ddd |
|---|---:|---:|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 128 | 128 (6,391 checked, 13 households) |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 53 | 53 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 14 |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 5 | 5 |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 1 | 1 |
| INV_PERIODS_CONTIGUOUS | 1 | 1 |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | 1 | 1 |

An eighth row now reds the gate: `INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE` 147, N19's blind row
(0f1fe62b9f), which 61ddb41250 says waits on a household fix not yet on origin. Not this finding's.

## INV_OVERDUE_WITHIN_PAGE_BALANCE traced: the prediction is refuted

The prediction above named N15's re-offer steps. 110 of the 128 are `arrangement_offered`/`repayment_plan_reoffer`,
so the count it set to refute it does not fire. But the cause is not N15. Census
(`/var/tmp/grade-4669/overdue_census.py`), each breach's excess set beside the household's back-billing write-offs
on bills issued by the step:

- **78 of 128: the excess is exactly a back-billing write-off.** OCC-75d17c23c1da's GBP 63.22 is
  `catchup_written_off_gbp` on gas bill INV3866 (June 2022), on every step from July 2022. N14 (c6e1a29e1) caps a
  catch-up on a bill paid on receipt in a second pass after the run (`rebill_catchups_off_direct_debit`). The desk's
  bills come in-loop from `StopNoticeBoard.issued_bills_before`, which never re-billed, so the desk chased the
  uncapped first pass. The page was right; the desk was wrong. This is N14's regression, which landed after
  85b044be54 and before b3ce2a4e73.
  Fix: the board asks the same second pass when a bill carries a DD-basis catch-up. Control:
  `tests/simulation/test_the_desk_is_asked_the_capped_catchup_the_page_prints.py`. On origin's code it is red: the
  desk is asked 1034.31 against 857.36 printed. The uncapped arm still asks its whole bill.
  **Prediction for the next fresh run carrying it:** this row falls to the 50 below, on the same households, give
  or take the draw.
- **32: a credit bill the page nets and the desk does not.** SYN-2016-269 (credit bill INV36008 of -85.95, Aug 2023,
  27 steps; and 12 more from Nov 2024 at 85.95 + a 10.41 write-off) and OCC-81b87bae7bec (gas credit bill -4.84, of
  which 1.64 was netted, leaving 3.20; 5 steps in 2017). Not yet traced into the triad's credit-note path.
- **6: a standing credit on one fuel leg beside a missed bill on the other.** PROS-2016-0020 (electricity page at
  -10.00, gas DD returned 37.12), SYN-2016-291 (-20.42 vs 45.11). The row nets the two pages and the desk does not
  net across legs. That is a definition question (does a credit on one fuel's account reduce what is overdue on the
  other's?), to be answered from the knowledge layer before either side is changed.
  SYN-2016-380's 2 steps (desk 165.75 against one returned bill of 148.95, 16.80 over) are not yet explained.

## SYN-2016-604g's three rows traced: one held bill (2026-11-04)

The run has all 13 of the gas leg's bills, but the billing ledger issues 12. July 2017 sits in the exception queue:
"billed usage 253.5 kWh does not reconcile with the printed meter reads 5001.4 -> 5255.0". June closed the register
at 5001.45, which prints 5001.4. July's register opened at 5001.450000000001, and `generate_billing_ledger` started
the usage line there, which rounds to 5001.5. The 0.1 kWh went to a catch-up line that a bill with no true-up never
prints. The gate was right to hold the bill; the builder was wrong. Across the book this is the only such bill (1 of
8,030 actual bills with a register and no true-up whose opening rounds apart from the previous close).
Fix: a gap below print precision, with no true-up, is float noise, so the usage line opens on the printed close.
Control: `tests/tools/test_an_actual_bill_with_no_catch_up_opens_on_the_last_printed_close.py` (red on origin with
the same hold; the true-up arm still prints its 0.1 kWh catch-up).
**Prediction, filed before the re-grade of the 4669d77ddd book with this builder:** INV_PERIODS_CONTIGUOUS 1 -> 0,
INV_OPENING_IS_THE_PREVIOUS_CLOSING 1 -> 0, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 5 -> 4 (SYN-2016-604g leaves),
and no other row moves.

## INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER against its pre-registered split: refuted (2026-11-04)

On the 4669d77ddd book (census `/var/tmp/grade-4669/estrun_census.py`): **2 of 53** breaches are on N14-rebilled
accounts (66 such accounts in the book), against the "more than half" the prediction needed. N14's second pass is not
the cause. Split: electricity 52, gas 1; 41 below the band (the estimate is well under the meter's advance, ratios
0.10-0.33) and 12 above (3.1-5.3). Runs that start in 2016-17: 31 of 53. Runs of 2 bills: 20. 44 accounts, none with
more than 2. Gas is 1, so N13 (the gas-noise change) does not carry it. **I cannot yet say** which change does. The
electricity-side candidates between 85b044be54 (4) and b3ce2a4e73 (53): 7ec8b1030d (490 premises leave the climate
normal and read the weather store), 308a3f168e (an E7 meter's annualised estimate is per register) and 54f76662d1
(held opening estimates issued). Next: one-variable replays of a breaching account's leg, one candidate at a time.

**Result (the 4669d77ddd book re-graded with the fixed builder, `/var/tmp/grade-4669-fix/grade.txt`):**
INV_PERIODS_CONTIGUOUS 1 -> 0, INV_OPENING_IS_THE_PREVIOUS_CLOSING 1 -> 0, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 5 -> 4:
as predicted. **"No other row moves" was wrong:** INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL also fell, 14 -> 12. I did not
predict it. The likely reading is that the held month was missing from one panel's year for this leg, but I have not
checked it row by row. Every other row reads as before.
