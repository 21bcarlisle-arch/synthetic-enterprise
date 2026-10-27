# Pre-registration: the six ungradeable cold-read rows, read from the company's own events (2026-10-27)

**Item:** `the-six-cold-read-rows-read-the-companys-own-events`. It covers points 1 and 2 of
`SEAT_FINDING_THE_EIGHT_COLD_READ_ROWS_LEAVE_SIX_UNGRADEABLE_ON_THE_RAW_EXPORT_AND_THE_OCCUPIER_EBSS_CREDIT_IS_SIZED_BY_THE_DEBT_2026-10-27.md`.
**Book:** the 2eeb3f0b3 run (`/var/tmp/fresh-run-out-2eeb3f0b3`, the newest full book on disk). Its ledger and raw export
were rebuilt with this item's code at `/var/tmp/six-rows-regrade/` using the same scripts as
the eight-row grade. No new run.

Written before any new evaluator ran on this book. What I had already seen:
- **Input counts only:** 1,291 accounts; 752 billing accounts; 7,151 collections journeys; 41
  write-off events; 553 renewal decisions; 52,782 bills with a due date, 50,699 with a settled date.
- **One household traced by hand (SYN-2016-356).** Its first journey opens on 29 Oct 2016 ("a bill
  is unpaid past its due date"), but both fuels' bills due by then were collected on their due
  dates in the billing ledger.
- **One line of code read:** the run logs a renewal decision at `event_date=term_start_str`, the
  day the new term starts (`simulation/run_phase2b.py`, `_record_renewal_decision`).

## What the export now carries

Every new field is a dated act or an identifier, and none is an amount. On each bill: its
`invoice_number`, `due_date`, and `settled_date` (the day a collection for it succeeded). On each
account: the company's `collections_journeys` (each step and its date, plus a write-off's rule) and
its `renewal_decisions` (date, fuel).

## The six rows

| row | disposition |
|---|---|
| INV_RENEWAL_NOTICE_42_TO_49_DAYS | checkable: the decision date against each fixed term's end |
| INV_COLLECTIONS_EVENTS_ORDERED | checkable: each journey's steps against its opening |
| INV_OVERDUE_WITHIN_BALANCE | partial. Leg 2 (an open debt stage has a bill unpaid past due) is checkable. Leg 1 (overdue <= balance) compares two sums the company worked out, so it is ungradeable on the raw export by design |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | partial. The necessary condition (some bill in the write-off is barred) is checkable. The per-bill form needs the write-off to name its bills, and the company's record posts only a sum |
| INV_ESTIMATE_RUN_WITHIN_TENURE | ungradeable on the export by construction (one fuel per account). Its check moves to the generated page's own counter |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | stays checkable:false. The world has no region (point 6), and its author has not restated the row |

## Predictions

- **Renewal notice** (unit: fixed term ending in supply). Every decision is dated on the term's
  end, an offset of 0 days, not -49 to -42. **Predicted: at least 90% of graded terms breach.**
  Some terms will have no decision within 90 days of their end and grade as missing. I do not know
  how many.
- **Collections order** (unit: journey). Every journey opens with `missed_payment`, so "no opening"
  and "before opening" should both be 0. "Plan before reminder" is possible where a journey goes
  straight to an offer. **Predicted: 0 to 50 of 7,151.**
- **Overdue leg 2** (unit: journey opening). The company's collections desk reads its own account
  ledger, not the billing ledger, and SYN-2016-356 shows the two disagree.
  **Predicted: 5% to 50% of openings find no bill unpaid past its due date.** The range is wide
  because one traced household is all I have.
- **Statute bar** (unit: write-off). The company computes the bar on its own ledger.
  **Predicted: 0 to 10 of 41.**
- **EBSS, after the blind author's restatement** (held at 00:00 on the 1st): the four first-part-month
  breaches go. **Predicted: 12 falls to 8.**
- **MPAN, after the IDNO restatement:** 0 stays 0.

Every breach is traced to a cause, and the grade is written below without editing the predictions.

## Grade (written after the run; the predictions above are unedited)

`python3 -m tools.domain_invariant_runner --ledger /var/tmp/six-rows-regrade/ledger.json`:

| row | predicted | found | verdict |
|---|---|---|---|
| Renewal notice | at least 90% of terms | **1,338 of 1,338**: 1,173 missing, 163 at 0 days, 2 at -9 | held |
| Collections order | 0 to 50 of 7,151 | **0** | held |
| Overdue, leg 2 | 5% to 50% of openings | **1,987 of 7,151 (27.8%)** | held |
| Statute bar | 0 to 10 of 41 | **25 of 41** | **wrong**: more than double the top of the range |
| EBSS after restatement | 12 falls to 8 | **12**: the 4 part-months went, 5 others appeared | **wrong** |
| MPAN after IDNO restatement | 0 | 0 | held |

**A correction to the method, made before this grade and recorded here.** The first build exported
`renewal_decisions_log` as "the company's renewal decision". That log is the household's own choice
on its journey (`_record_renewal_decision` -> `journey.record_decision`), so it was a world fact under
a company label. The export now carries the company's retention offers (`retention_log`), and the
grade above is on those. The first build also put `invoice_number` and `due_date` on the
validator's raw export. `test_no_bill_document_is_exported`, the director's own correction, refused
that. The company's dated acts are now a second export (`account_events`) that the bill validator
never reads.

### Causes, every breach

- **Renewal, 1,338.** The company records no end-of-fixed-term notice.
  `company/crm/renewal_notice_register.py` implements the window and nothing in the run calls it.
  Its only dated act is the retention offer, made on the day the term ends: O6's class, on 163
  terms. 1,173 terms have no act at all: 800 roll to the SVT, 59 roll to a new fix, and 240 end
  when the household leaves. A world/company defect.
- **Overdue leg 2, 1,987. Partly diagnosed.** The collections desk opens a journey on "a bill is
  unpaid past its due date" from its own account ledger, and the billing ledger disagrees:
  - 1,769: the last bill due before the opening was collected on or before its due date;
  - 136: no bill had fallen due;
  - 82: the last bill was settled late, so the opening may be right and this leg's reading too
    strict.

  1,627 open 8 to 31 days after the last due date. 1,639 are DD households. Traced by hand:
  SYN-2016-356 opens on 29 Oct 2016, and on the 29th of later months, while its bills fall due
  between the 14th and the 19th. Two payment records; **which one is wrong I cannot yet say.**
  Prediction, filed before the check: the desk reads the DD collection book's schedule, not the
  bill's due date.
- **Statute bar, 25.**
  - 24 "payment after the bar": in 23 the household had left supply, and the final bill was paid
    two to four weeks after the bar date. The write-off falls about six years after supply ended,
    and the row and the company's own rule both say a payment restarts the six years. Likely
    cause, not established: the desk's ledger lacks final-bill payments received after the account
    closed.
  - 1 "no bill old enough": not traced.

  My prediction was wrong because I assumed the company's rule, applied to its own ledger, would
  agree with the billing ledger. The overdue leg shows the same disagreement.
- **EBSS, 12.**
  - 7 on four occupier accounts: the occupier path, as before.
  - 5 on PROS joiners (PROS-2022-0356, -0400, PROS-2023-0010, -0013, -0039), each traced. Each
    joined mid-month and was credited for that part month, which guidance 5.4 says is owed nothing.
    The surplus credit lands in a later month's window. The occupier path credits a joiner nothing
    and the named-household path credits a whole month: two homes for one rule.

  My prediction of 8 assumed only the part-month breaches would move. It did not ask what the
  stricter predicate does to a joiner the world did credit.

Each of these is filed as a named exception, capped at its count, in
`docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`, and the defects are in
`docs/staging/SEAT_FINDING_THE_COMPANYS_OWN_EVENTS_SHOW_NO_RENEWAL_NOTICE_TWO_PAYMENT_RECORDS_AND_A_CREDITED_PART_MONTH_2026-10-27.md`.

### Where the six rows stand

- **Checkable on the company's events:** renewal notice and collections order.
- **Partial:**
  - Overdue: leg 2 is graded; leg 1 compares computed sums and belongs on the page.
  - Statute bar: the necessary condition is graded; the per-bill form needs the write-off to name
    its bills.
- **Not checkable:**
  - The estimate run holds by construction on the export. Its page check is the next increment.
  - The SVT-per-region row stays checkable:false: the world has no region.
