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
