**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** none (found by the billing-ledger move, 2026-10-14)

# Nine customer-years bill less than their own gross margin at origin, and no census holds the test

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
