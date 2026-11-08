**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The publisher's gate cannot grade the payment-record row, so the level-DD payment-record defect is invisible to the gate that decides the publish (2026-11-08)

**Found by.** Grading the af31e73fa7 book through the publisher's own function
(`background.process_run_complete._domain_invariant_gate_permits_publish`), from a scratch tree at origin
8b8a737211, for the ninth cold read.

**What.**
- `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` reads **NOT_IN_EXPORT**: "needs `payment_record`, which no period
  of this export carries".
- `load_printed` (`tools/domain_invariant_runner.py`) builds the page's invoices, ledger, steps, totals, usage,
  carbon years and the cast's `payment_tallies`. It never builds `payment_record`.
- The scratch grader (`/var/tmp/b3ce-grade-scripts/grade.py`) builds it in memory with
  `tools.generate_explore_cast.payment_record(page_ledger, invoices, as_of)`. That is how fa915ac0d7's grade found
  the row's **45** level-DD breaches (`SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL..._2026-11-07.md`,
  part 2).

**So:** the publisher would refuse this book on INV_OVERDUE_WITHIN_PAGE_BALANCE (1,729) alone. Once the level-DD fix
clears that row, the publisher cannot see the second half of the same defect. The cold read saw it ("0 of 0 bills
paid" beside "£41.73 owed", O12; "81 of 83 bills paid" beside "£2,041.37 owed", O13).

**The rest of the publisher path, checked on this book.** It does build `cast_tariffs` and `payment_tallies`, from the
cast beside the page files. INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED reads 28 checked. With the household-page
tariff landing, INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM reads 47,504 checked.

**Next.**
- `load_printed` should compute `payment_record` from the page file's own ledger entries and invoices, with the same
  function the cast prints from.
- The control is that the row reads CHECKED > 0 through `_domain_invariant_gate_permits_publish` on a real page tree.
- The work belongs with the level-DD fix (`fix-level-dd-households-dunned-per-bill`), whose done-means already
  names this row.

**Reverse.** Delete this file.

## Pre-registration (2026-11-08, written before the grade)

- **Change.** `generate_payment_ledger_data` writes `payment_record` into each customer file. It uses
  `generate_explore_cast.payment_record` over the file's own bills and ledger, at the ledger's as-of date.
  `load_printed` reads it from the file. The runner keeps its import wall: its only repository import is
  still the raw export.
- **Grade.** The af31e73fa7 book (`/var/tmp/ninth-read/book/billing_ledger.json`). Its page files are the
  ninth read's, built at 8b8a737211. The payment-ledger step is re-run on a copy at this change, which
  includes fc45c2c45. Then `_domain_invariant_gate_permits_publish` is called with that book and those
  pages.
- **Prediction.** INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE reads CHECKED > 0, about the ~1,300
  page files that hold a bill due. Breached **0**, as fc45c2c45 measured 45 -> 0 on fa915ac0d7. No other row
  moves from the ninth read's `gate.txt`, apart from rows that read the page ledger's new `level_dd` flag.

## Result (graded after the pre-registration)

Graded through `_domain_invariant_gate_permits_publish("af31e73fa7", ...)`, as pre-registered. Scripts and
outputs are in `/var/tmp/pubgate-af31/` (`grade.py`, `before.txt`, `after.txt`).

| Pages | INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE |
|---|---|
| The ninth read's, as built (before) | NOT_IN_EXPORT |
| Payment ledger re-patched at this change (after) | **CLEAN: 1,139 checked, 0 breached** |
| After, with the ledger's `level_dd` flag stripped (the pre-fc45c2c45 reading) | BREACHED: 1,139 checked, **45** breached |

- **The prediction held.** The row reads CHECKED > 0 and 0 breached.
- **The 0 is not vacuous.** The same pages without fc45c2c45's flag breach 45 times. That is the same count
  fc45c2c45 measured on fa915ac0d7, e.g. `OCC-01f752dc9316 electricity 70 payments, 0 returned, 5 missed;
  75 due`. The publisher's gate can now see the level-DD half of the defect, and fc45c2c45's 45 -> 0 is shown
  on the publisher's path, not only by a replay.
- **One part of the prediction was wrong.** I predicted about 1,300 checked. 1,139 of the 1,302 page files
  have a bill whose due date has passed and that was not paid by prepayment. The rest have no collection due.
- **No other row moved** between before and after (diffed, 80 rows).
- **The verdict is unchanged.** It refuses on INV_OVERDUE_WITHIN_PAGE_BALANCE 1,729 alone, which is the
  level-DD fix's step 2.
- **A row that moved for another reason.** The ninth read's INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL 4,031
  reads CLEAN, with 8,829 checked, under today's code in both grades. Code landed since 8b8a737211 moved it,
  not this change.

## The sweep: every row on the publisher's path that is not graded

On this book through the publisher's path there are 45 CLEAN, 15 FLAGGED, 8 BREACHED, 12 UNCHECKABLE,
**1 UNREACHED**, **0 NOT_IN_EXPORT** and 0 NO_EVALUATOR.

- **INV_STATUTE_BARRED_WRITE_OFF_AGE: UNREACHED, 0 checked.**
  - *Cause:* the book holds no write-off under `STATUTE_BAR_RULE` (`company/billing/collections_journey.py`).
    `limitation` appears 0 times in the af31e73fa7 ledger. The row is graded on the ledger, not the page, so
    the loader is not what hides it. The book reaches nothing the row applies to.
  - *Whether that absence is right* is the ninth read's closed-account debt finding
    (`SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_CLOSED_ACCOUNTS_STILL_HOLDING_CREDIT_AND_DEBT_YEARS_AFTER_THEIR_LAST_BILL_2026-11-08.md`).
    That finding has debt held for years after the last bill and never barred. Until a book reaches a barred
    write-off, the row reads UNREACHED, and an UNREACHED row is not clean.
- **The 12 UNCHECKABLE rows** are marked uncheckable by the invariants file itself, each with its named GAP.
  None of them is a gap in the loader:
  - INV_EV_ADOPTION_ELECTRICITY_ONLY
  - INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE
  - INV_TWO_RATE_BILL_PRINTS_ONE_READ_PAIR_PER_REGISTER
  - the four Bacs processing-day rows (INV_DD_COLLECTION_IS_DATED_ON_A_BACS_PROCESSING_DAY, ..._NEXT_PROCESSING_DAY,
    ..._PILE_ONTO_MONDAYS_...)
  - INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START
  - INV_OPENING_DAY_CREDIT_IS_ONLY_WHAT_WAS_COLLECTED_ON_OR_AFTER_SUPPLY_START
  - the four household-diagnostics rows (gas against weather twice, winter/summer ratio, electric-heating verdict)
- **Seen in passing, not a path gap:** INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD reports
  1 checked and 2 breached.
  - *Corrected the same day, after reading the row's output:* I first wrote that its breaches were counted in a
    different unit from its checks. They are not. The row grades one book, and two of that book's legs
    breached: the median |r-1| 0.0075 is under 0.05, and 29% of pairs sit within 0.1 kWh, against 17%
    expected by chance. The verdict excepts it. Nothing here needs fixing.

## Done

- **The export carries the record.** `tools/generate_payment_ledger_data.generate` writes `payment_record`
  into each customer file, using the function the cast prints with.
- **The loader reads it.** `tools/domain_invariant_runner.load_printed` reads it from the file. The runner's
  import wall holds: `test_the_runner_imports_nothing_from_the_repository_but_the_raw_export`.
- **The test.** `tests/tools/test_the_publishers_loader_grades_the_payment_record_row.py` writes a page file
  through the export and reads it through the publisher's loader.
  - It is red on the parent: NOT_IN_EXPORT.
  - Both halves are mutation-proven. Taking out the export's write or the loader's read reds 2 of its 3 tests.
  - Both sides of the partition are covered: a paid bill reads CHECKED > 0, and a missed DD with no return
    reads BREACHED.
- **The grade and the sweep** are above.
