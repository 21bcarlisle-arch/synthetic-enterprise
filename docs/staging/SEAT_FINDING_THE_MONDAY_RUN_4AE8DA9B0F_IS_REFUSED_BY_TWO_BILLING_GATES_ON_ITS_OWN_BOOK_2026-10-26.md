# SEAT FINDING: the Monday run 4ae8da9b0f is refused by two billing gates reading its own book

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

Why LATENT and not BLOCKING: the gate refused these figures, so nothing published carries them.
The published book is still 8b6fea024's, and both tests pass on it at HEAD. The cost is that no
figures reach origin this Monday. They have now gone 165 hours without a publish.

## What was found (26 Oct 08:28Z, publish of `run_complete_20261026T080604Z.md`)

The fifth publish attempt of `run_output_4ae8da9b0f_20261026T022647Z.json` cleared the publisher
races. The stale-copy fix and the index.lock fix both held. It was then refused `commit_refused`
by the test gate: 2 failed and 1702 passed, on the tree the publish would create. The publisher
re-ran both reds at HEAD and they passed, which tells us they are the regenerated book's reds. They
are not HEAD's.

I re-ran both on the shared tree, which still holds the regenerated `docs/state/billing_ledger.json`
and `site/data/customer_sample.json`. Prediction, filed before the run: both are real defects in
the book, not faults in the tests. Both reproduced:

1. `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`.
   10 customer-years are billed less than their own gross margin. Among those named (billed,
   gross): `OCC-14d60fd5bb78` 2023 (1913.94, 1998.94), `PROS-2016-0263` 2023 (407.95, 485.75),
   `PROS-2017-0117` 2018 (724.69, 1008.19), `PROS-2017-0336` 2023 (6092.68, 7450.98) and
   `PROS-2021-0279` 2023 (431.8, 483.34). Most are in 2023. 2023 sits inside the government-credit
   window, so one candidate is a credit netted from "billed" that gross margin does not carry. That
   is unmeasured. 2018 does not fit that candidate.
2. `tests/company/billing/test_the_raw_export_carries_nothing_derived.py::test_every_real_period_exports_readings_that_reproduce_our_own_volume`.
   1416 of 52782 periods export as `consumption_only`, with no readings that reproduce our volume.
   C1/1-4 and C2/9-10 are among them.

What changed between 8b6fea024 and 4ae8da9b0f is the suspect set. It includes the four billing
fixes, b2bc3d8da5's ancestors and the PB8 DD-stop spells. More than one thing changed, so I
cannot yet say which one causes either red.

## What is owed

Bisect each red on the run's own book, using its `meta.git_commit` and the two inputs above. Fix
each red as a class, then re-offer the run with `sim_runner --promote`. Never excuse a row to make
the gate pass.

## Bisected, 26 Oct (seat executor). The prediction held for red 2 and held only in part for red 1

The method: I regenerated the ledger from `run_output_4ae8da9b0f_20261026T022647Z.json` with the fix
in place and ran both whole-book tests against it, using the shared tree's `customer_sample.json`.
Apart from the two new fields, the regenerated ledger is identical, invoice for invoice, to the shared
tree's copy: 52,782 of 52,782 invoices.

**Red 2 is one class and it is closed: 1416 → 0.** All 1,416 periods are two-register ToU invoices.
Commit 50001b0b7b made a ToU bill print Peak and Off-peak registers, but the ledger kept a single
opening/closing pair per invoice. The export (correctly) refuses to guess how one index splits across
two registers. The fix is that the ledger now carries each register's own cumulative index, and
`raw_account_export._reads_per_register` exports two readings per register. The control now sums
the advance over all registers. Limit, stated in the code: a register's index does not advance over
periods that bill single-rate.

**Red 1 was two classes, and only one is closed: 10 → 4.**

- *EPG, 6 of 10 (OCC-14d60fd5bb78, PROS-2016-0263, PROS-2017-0336, PROS-2021-0279, SYN-2016-221,
  SYN-2016-298, all 2023).* Since 4ef70aba92 the household pays the EPG price and the Treasury pays
  the supplier the rest. Gross margin counts that receipt; the invoice did not carry it. This is a
  transfer being read as a break (M2). The fix: the invoice now carries `hmt_epg_receipt_gbp` (outside
  its total) and the gate compares bill + receipt. The whole book carries £198,651 of receipt. All
  six now clear their gross by margins of £124 to £1,962.
- *Not EPG, 4 of 10. Still red, and not excused.* Each one is gross earned on volume that was never
  billed:
  - `SYN-2016-582` 2016 and `PROS-2024-0010` (Jan–Feb 2024): their first bills are HELD in the
    exception queue. The load is SME-sized on an account labelled resi (vat_by_segment plus slc_6_7).
    Nothing re-issues them, so the margin is earned and the bill never goes out. These are 2 of the
    book's 4 held accounts.
  - `PROS-2017-0117` 2018, `PROS-2024-0010` 2025 and `SYN-2016-190` 2016: each leaver closed on a run
    of estimates at 0.39–0.55 of true use, with no final read. On the 8b6fea024 book, PROS-2017-0117
    ended in Nov 2017 and the account did not reach 2018. A change to the departure date moved it
    onto those estimates, not a change to billing. SYN-2016-190 was never read in its three months on
    supply (both fuels).

  I cannot yet say which commit brought each of these four in. The populations differ between runs,
  so a per-row bisect needs reruns, not a re-read. They are the same shape as C7 (an estimate that
  never meets a read), and the open question is the same one too: does a held bill have a re-issue
  route, and does a leaver get a final read (SLC 21B)?

**What is owed now:** a re-issue or rebill route for held bills (or a ruling that a held bill's
period is excluded from gross), and a final-read or true-up for a leaver who closes on a low
estimate. Until one of those lands, this run's publish stays refused, which is correct.
