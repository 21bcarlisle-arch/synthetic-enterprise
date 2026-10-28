**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The second cold read finds seven new classes, and the suite grades a record the page does not print (2026-10-28)

**Source:** the second cold read, on the fresh 1691ec0ecd book's pages. The reading, with each
objection's quote checked, is
`docs/staging/SEAT_READING_THE_SECOND_COLD_READ_ON_THE_1691EC0ECD_BOOK_2026-10-28.md`. BLOCKING
because the director's correctness stretch cannot exit while a cold read finds a new class (ruling
of 26 Oct, exit test). Under step 6, each confirmed objection becomes a new invariant, written blind
from the knowledge pages.

## The classes, worst first

1. **N1. The suite grades the ledger, and the page prints the invoice.** PROS-2019-0246 (the 2022-shock
   slot) has all six EBSS `scheme_credit` adjustments (£400) on its ledger. Its invoices carry
   `credit_applied_gbp: None`, and the page prints "The electricity bill for December 2022 was
   £598.04" with no credit line. `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` reads the ledger, so it
   passes.
   - The same shape explains O4 and O14 (overdue larger than owed on the page, 4 openings in the
     suite).
   - **First:** say which record each row grades. A row about what the customer is shown must grade
     the invoice and the page's own figures.
2. **N2. Settlement revenue before VAT exceeds the VAT-inclusive amount billed**, before any crisis
   support. OCC-423594fbfa6b (2016 to 2019) shows £2,277.10 against £1,998.82. Before differencing,
   say what "revenue" counts here. It is likely settlement-side revenue, a different record from
   the bills.
3. **N3. The payment-record counters do not reconcile with the bills.** Example: "34 payments, 4
   returned, 42 missed" on a 50-bill account. A returned DD is not counted as missed ("6 payments,
   4 returned, 0 missed"), and the DD is kept after 4 of 6 returns. Define payment, returned and
   missed per bill first.
4. **N4. No demand response to 2022–23 prices.** For example, 2,467 / 2,511 / 2,494 kWh. This is a
   world question: read the knowledge layer's response arc against the book-wide 2021→2023 change
   before any build.
5. **N5. Two figures for one quantity disagree on one page.** The carbon panel says 7,303 kWh of gas
   for 2017 and the usage panel says 6,180. A part-year carbon figure is also published against its
   own "has no figure" rule.
6. **N6. The smart data-access copy says monthly reads need consent.** Check the commons copy of
   Ofgem's data access and privacy framework before rewording. GAP until it is read.
7. **N7. Estimates do not follow the latest actuals.** On the EV home, after a read-confirmed rise
   to 398 kWh/mo, the next estimate is 136 kWh.

## Not new (for the drawer)

Every other objection (O1–O40) maps to the first read's classes, an open finding, or a suite row.
The mapping is in the reading.

## N1 actioned (2026-10-28)

**The cause.** The ledger invoice carried the credit (`scheme_credit_month_gbp`, the month's credit,
and `scheme_credit_gbp`, the part the bill used). `tools/generate_invoice_data._real_invoice`, which
writes the page's bills, mapped neither. 3ab3ea925 (the occupier-window share) touches the ledger
and bill assembly, not this mapping, so nothing here redoes it.

**The fix.** The page invoice carries `scheme_credit_gbp` (the month's credit, which the bill shows)
and `scheme_credit_applied_gbp` (the part this bill used). The Explore bill prints the credit below
the total, then "= To pay", and says when part of the credit stays on the account. The 2022-shock
sentence names it: "...was £598.04 before its £67.00 Energy Bills Support Scheme credit, against
£311.08 a year earlier." Tests, red on origin's code (3 of 3) and green after:
`tests/tools/test_the_bill_prints_the_scheme_credit_the_ledger_holds.py`.

**Before and after, on the 1691ec0ecd book.** I rebuilt the book's ledger with origin's tools from
3ab3ea925's re-shared outputs (`/var/tmp/share-fix-1691/run`), the way
`/var/tmp/gasleg-remeasure-scripts/probe.py` does. I built the page invoices in memory with each
version of `_real_invoice`. No run was launched. Script: `/var/tmp/credit-probe/scripts/probe.py`.

| | credited accounts whose page invoices omit a credit | credited bills omitting it |
|---|---|---|
| ledger holds a credit | 232 | 1,314 |
| **before** (origin's `_real_invoice`) | **232 of 232** | 1,314 of 1,314 |
| **after** | **0** | 0 |

Before the fix, no page bill anywhere in the book showed the credit.

**Every row names its record.** `DOMAIN_INVARIANTS.yaml` now gives each row a `grades:` field, and
`meta.conventions.grades` defines the three values. 42 rows grade `ledger` (the raw export).
`INV_ESTIMATE_RUN_WITHIN_TENURE` grades `page`, because the Explore test checks it there. The two
new twins grade `invoice` and `page`.

**The twins.** I wrote both from `energy_bills_support_scheme_delivery.md` and the ledger row's
logic, not from the code. They read the published customer files, passed with `--printed` and by
the publish gate (`site/data/customers`). A book read without those files reads NOT_IN_EXPORT, never
clean.

| row | grades | before the fix | after |
|---|---|---|---|
| `INV_EBSS_CREDIT_ON_THE_BILL` (twin of the EBSS row) | invoice | 1,193 of 2,277 | **6**, the ledger row's five accounts and causes; excepted, ceiling 6 |
| `INV_OVERDUE_WITHIN_PAGE_BALANCE` (twin of `INV_OVERDUE_WITHIN_BALANCE`, its first leg) | page | 10,180 of 32,741 | 10,180: not this fix's subject, see below |

- **Why the overdue twin grades the page, not the invoice.** The quantity is the overdue sum a
  collections step prints, against the page ledger's balance. Neither figure is on a bill.
- **It found a new defect at book scale.** The page prints more overdue than it says is owed on
  493 of 752 households. Filed as
  `SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.
- **It is excepted at its measured count**, with that finding as `retired_by`, so the count is on
  the surface every run and a rise refuses.

**Not done here.** N2 to N7 are untouched.
