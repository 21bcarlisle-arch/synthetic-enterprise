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

## The last four, 26 Oct (seat executor, second pass). Pre-registered before any fix was measured

**Correction to the paragraph above, beside it.** "Nothing re-issues them" is wrong for the held
bills. SYN-2016-582's held winter bills (supply from 2016-12-10, nothing issued before 2017-03)
are billed by the catch-up on its first actual read: 2017-07, £815.86 over 2016-12-10 to
2017-06-30. That is the route `unbilled_energy_and_revenue_assurance.md` §"A held bill on an
account that closes" already describes ("its catch-up already carries the held energy"). PROS-2024-0010's
held Jan–Feb 2024 is billed the same way (2024-05, £1,596.25 from 2024-01-14) and its 2024 is not
inverted. The inversion is in the gate, not the book. `billed_total_by_customer_year` credits a
catch-up back to its span pro rata by day. That is right when every day of the span was billed on
an estimate and only the estimate's error is corrected. It is wrong on a day no invoice covered:
nothing was billed for that day, so the catch-up carries the whole of its energy. SYN-2016-582 gets
22 of 203 days' share in 2016 (£88.42), when it owes 22 days of the span's whole true cost.

**The three leavers are the K6 leg (b) build that was deferred on 20 Oct**, under the prediction
"no account year changes sign against the defect-4 gate". On this book three do, so that
prediction is refuted. The losing supplier is billed AND settled at the change-of-supplier read
(BSCP504 §4.4.1). Gross is formed on true demand through the exit, so it counts margin on energy
this supplier was neither billed for nor charged for.

**Fixes, chosen before measuring:**
1. Gate attribution. A catch-up's span is priced flat per day, at (billed in span + adjustment) /
   days. A day no invoice covers takes that whole daily amount. The rest of the adjustment is
   spread evenly over the days that were billed. Where every day was billed, this is identical
   to the old rule.
2. Settlement view (K6 choice "the build shape this implies"). For each supply point whose last
   bill is an estimate, the trailing estimate run gets scale = billed kWh / true kWh. Each of the
   run's months gets `cos_read_settlement_gbp = (scale − 1) × (gross − standing charge)`. That is
   carried beside `gross_gbp` in `annual_pnl`, and the sweep compares against gross + that entry.
   It is computed after the run from the run output's own bills and monthly rows, not in phase 4c,
   so it reads this run as it stands.

**Predictions:**
- P1. SYN-2016-582 2016 billed rises from £88.42 to about £190 (22 days × about £8.80), above
  its £149.20 gross. Book-wide billed total is unchanged to the penny. No new inversion appears.
- P2. PROS-2017-0117 2018: scale about 0.48. Settled gross falls from £1,008 to about £500, below
  its £724.69 billed. PROS-2024-0010 2025 and SYN-2016-190 2016 also clear.
- P3. Book-wide, the settlement entry nets to under £2,000 in absolute value over the decade. It
  is zero on every leg whose last bill is actual.
- P4. The sweep reports 0 inversions on this book, with no row excused.

**Result (added after; the predictions above are not edited).** Run on the ledger regenerated
from `run_output_4ae8da9b0f_20261026T022647Z.json` at this commit, with `customer_sample.json`
regenerated from the same run.
- P1 HELD. SYN-2016-582 2016 is now billed at £193.65 against £149.20 gross. Attribution only
  moves within a span, so no new inversion appears.
- P2 HELD FOR TWO OF THREE, then changed. Under one scale over the whole run, PROS-2017-0117 2018
  (−£516) and SYN-2016-190 2016 (−£95 over both fuels) clear. PROS-2024-0010 2025 does not: £215.05
  billed against £255.46 settled. Its true use climbs steeply into January, and one scale keeps the
  true shape. Settlement spreads a deemed advance by the profile, not by the household's shape
  (K2). Spread by `profile_weight`, it settles at −£275.29 and clears. I made the change after
  seeing the refutation, and say so here and on the K8 page. The mechanism is the reason for it.
- P3 REFUTED, narrowly. The book-wide net is −£2,120.75 against the predicted bound of under
  £2,000 (it was −£1,922.72 under one scale). It is 0 on every leg whose last bill is actual.
- P4 HELD. The sweep finds 0 inversions on this book, with no row excused. The test file passes
  13 of 13 on both the committed book and this one.

**Still owed, and not blocking the publish:** `saas/reporting/annual_report.py` and net margin do
not read `cos_read_settlement_gbp` yet. The policy and network costs inside net scale on the same
rule and are not moved. Treasury cash still books margin on true demand for these legs. Next: re-offer the run with
`sim_runner --promote`.

## Published, 26 Oct 12:28Z (worker tick)

- **The re-offer at 10:45Z cleared both billing gates.** The book regenerated from the run at HEAD
  passes 43 of 43. Its commit was then refused by the next-step gate, and not for anything of its
  own: the publish pathspec names `docs/design/maturity_map.yaml` on every cycle, and the shared
  tree's copy held the B13 lane's uncommitted 1 -> 2 move. Fixed as a class in 1853553866: the map
  now rides only on a cycle the publisher's own fold wrote it. The mutation was run, and it fires.
- **The second re-offer landed** as 60e4d4dc52 over 199 paths, and the standing-red ledger is
  discharged. R11: poesys.net serves `customer_sample.json` generated at 12:01:01Z for 4ae8da9b0f,
  carrying `cos_read_settlement_gbp` on 730 rows.
- **Three post-publish readers are red on the published bytes** (`.post_publish_reader_reds.json`,
  12:28Z). They are owed, and they are drawable from here:
  - `tests/background/test_the_published_series_and_the_ledger_it_came_from_are_committed_together.py::test_every_run_the_committed_dashboard_publishes_is_in_the_committed_ledger`
  - `tests/tools/test_the_curtained_validator_rebuilds_the_bills_without_us.py::test_every_period_in_the_book_rebuilds_to_our_own_energy_and_standing_charge`.
    This is likely the same two-register ToU shape as red 2. That is a prediction, not yet run.
  - `tests/company/compliance/test_crisis_bad_debt_validator.py::test_live_run_output_shows_crisis_step_up_ifrs9_charge`.
    It is already filed in `SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_SINCE_THE_RUN_WENT_GZIP_...2026-10-14.md`.
