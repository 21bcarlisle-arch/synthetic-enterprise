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
