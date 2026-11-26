**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# The cb93f7760c book, graded: cause one clears all its classes, and five causes still wedge the publish

Graded on 26 Nov 2026 by the delivery seat (draw `grade-the-first-book-after-the-measured-yield`).

## The yield admitted

Since 934ba954c, sim-runner sizes a cycle beside a long job. At 21:06Z on 25 Nov it deferred. Two
books were built after that:

- `run_output_3d3a8ee691_20261125T215702Z.json` (completed 23:42Z). Decomposed in
  `SEAT_FINDING_THE_3D3A8EE691_BOOKS_475_INVARIANT_BREACHES_DECOMPOSED_AND_THE_FIRST_CAUSE_FIXED_2026-11-26.md`.
- `run_output_cb93f7760c_20261126T013243Z.json` (completed 03:17Z). It is the first book that
  carries f0c0e7889a (a won switch is looked up at its predecessor's dwelling). It is graded here.

The publisher refused cb93f7760c twice, at 03:31Z and 04:16Z: `domain_invariant_refused`, rc=82, 446
unexcepted breaches across 8 invariants. The site still serves the 18 Nov book (6af7fd0bfd) under
the "verification paused" banner (4e62276512).

## The three grades

1. **`tools/grade_svt_invoices_over_ceiling.py` (`billing_grade_refusal`) is clean, with no
   defects.** 0 of 23,777 graded default-tariff invoices are above the household ceiling (12,373 are
   ungradeable). The EPG receipt shows £214,613.32 paid against £214,613.32 booked, with none carved
   outside the windows. There are no overlapping-term legs and no negative estimated bills. The
   unit-charge fall moves by quarter, as it should: 2022-Q4 electricity 0.345, 2023-Q1 0.496, 2023-Q2
   0.328. **The billing and EPG fixes hold together on this book.**
2. **`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`: 6 of 4,258 runs breached, all excepted.** They
   fall on 5 accounts: SYN-2016-215 (2), PROS-2016-0203, PROS-2017-0364, SYN-2016-221 and
   SYN-2016-565. This is the same count as on 3d3a8ee691. The handoff
   `the-gas-aq-fix-is-graded-on-the-first-book-built-after-it` owns what this means for the gas-AQ
   fix.
3. **`company/compliance/domain_invariants.py`, through the runner, refuses: 446 unexcepted.** The
   breakdown is below.

## The prediction, scored

f0c0e7889a filed this before any book carried the fix: "8 actual-read holds release; 3 estimate
holds stay ... OCC's two estimate gaps will still breach contiguity and the carbon panel."

| predicted | measured on cb93f7760c |
|---|---|
| SYN-2016-175_3's 8 actual-read holds release | **held**: all released |
| 3 estimate holds stay held | **wrong, in the safe direction**: ledger `held_bill_count` 0 and `exception_queue` empty |
| the 2021-03 reads hold "expected to clear, cannot yet say" | cleared: `held_reads_reconciliation_count` 0 |
| OCC-d5419b4a0f6e still breaches contiguity and the carbon panel | **wrong**: INV_PERIODS_CONTIGUOUS 0 of 107,174; INV_CARBON_PANEL 0 of 8,902 |

I have not yet worked out why the three estimate holds released. My most likely explanation is that
`release_confirmed_domestic` treats an estimate at a listed dwelling the same as an actual read once
the dwelling resolves, so the separate question that finding raised may not exist. Check that before
building anything on it.

The arithmetic agrees: 475 − 446 = 29. Thirty breaches cleared (9 contiguity, 14 carbon panel, 1 each
for opening, reconcile and closing, and 2 + 2 EBSS), and EPG rose by 1 (361 → 362) as the book grew.
Nothing else moved.

## What still refuses, by account (full lists from the probe; nothing is truncated)

| invariant | breaches | accounts | read |
|---|---|---|---|
| INV_UNIT_RATE_EPG_HOUSEHOLD | 362 of 3,339 (10.8%), ceiling 350 | 191 | the breach rate is flat; the ceiling counts breaches and refuses a larger book |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 44, no exception | 17, mostly OCC (OCC-5c90c6dd919a 8) | open |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 8 / 8, ceiling 7 | 7, **all OCC** | an occupier admitted mid-scheme |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 8, no exception | 1 (SYN-2016-099) | one account |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 7, ceiling 1 | 7 gas legs, 5 of them PROS | b3f3a23f6f suspected |
| INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT | 8, 1 outside its class | 8 | one account |
| INV_OVERDUE_WITHIN_BALANCE | 1, no exception | 1 (SYN-2016-107) | one account |

Excepted and within their ceilings: INV_PPM_NOT_CREDIT_BILLED 12, INV_ESTIMATED_RUN 6, and
INV_ELEC_MONTHLY_USE 2.

## What this means

The site has shown 18 Nov figures for eight days. No single fix ends that, because **five
independent causes each refuse the publish on their own.** The order in the 3d3a8ee691 finding
still stands, and this book adds nothing new. The first of them is the EPG exception. It is a
control keyed to today's answer: its ceiling is a count from one book's size, and the breach rate
has fallen while the count has grown. Re-key it to a share, or retire it by pricing the energy line
on the printed kWh. Do not raise the number.

## Probe

`/tmp/seat_g2/probe.py`, not committed. It is a copy of `/tmp/seat_inv/probe.py`: it wraps
`domain_invariant_runner.EVALUATORS` so the breach lists stay whole, then runs `load_book` over
`docs/state/billing_ledger.json` (source_json cb93f7760c) and `site/data/customers`.
