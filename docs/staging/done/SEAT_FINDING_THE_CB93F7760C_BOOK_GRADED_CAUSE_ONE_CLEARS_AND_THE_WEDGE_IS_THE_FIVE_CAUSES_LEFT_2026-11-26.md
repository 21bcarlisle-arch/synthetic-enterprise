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

## Worked, 26 Nov (draw `the-epg-exception-is-keyed-to-a-share-not-a-count`)

Re-graded on HEAD a1eee4d921 over the cb93f7760c ledger before starting:

- **Cause 1 (EPG count ceiling): already spent.** 10bf51c370 keyed the exception to the read-tenths
  class. 362 breaches, all in class, excepted.
- **Cause 3 (estimate follows reads, 44): already spent.** 204b68cca5 grades the quote figure per read
  segment: 0.
- **Cause 2 (EBSS, 8 + 8 over a ceiling of 7): fixed in this landing.** The exception's own
  `retired_by` was the remedy. The ledger now records which deemed accounts a bill was billed to
  (`deemed_accounts`: owner for void days, occupier for an unnamed occupant). Before, it recorded only
  the larger of the two, so OCC-33c7f31198b0's Feb 2023 read "occupier" with a void 1st. The raw export
  carries that list and `deemed_part` (whole or part). Both EBSS rows owe the payer nothing for a month
  whose 1st a deemed account held. A void 1st is owed nothing (Annex C). A 1st the occupier's account
  held on a bill shared with the payer is owed to that account, not the payer (guidance 5.4). A month
  wholly the occupier's stays owed, because its bill is the deemed account's own and carries the
  credit. The first version also exempted that last case, and 8 new "above" breaches refuted it on
  the same book. The void → occupier → named order is checked per account, not assumed. On this book
  no deemed bill follows a named one (0 of 1,129 deemed bills).
  The cb93f7760c ledger, rebuilt with the field, grades **0 and 0**, from 8 and 8. No other row
  moves. Both exceptions are retired.
  GAP, stated on both rows: on a shared month the occupier's account's own receipt is not posted to
  the export, so it is ungraded.

**Still refusing on that book (4 rows):** INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 7 (cause
under investigation in 4df2b4f892), INV_OVERDUE_WITHIN_PAGE_BALANCE 8 (SYN-2016-099),
INV_OVERDUE_WITHIN_BALANCE 1 (SYN-2016-107), and INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT
(1 outside its class).

## Graded on the 76f894811d book (delivery seat, 26 Nov 2026 21:5xZ)

Book: `run_output_76f894811d_20261126T155009Z.json`, 1,382 accounts, 54,463 bills. It descends from
7f90f9563a, d688a224a, 91c32797b3, 9ed3dc9787 and e4dda28119. Its ledger was written in a clean
checkout of 76f894811d (fcd2facdcd's route; sim-runner-log 21:02Z). The publisher's own gate,
`docs/reports/DOMAIN_INVARIANTS.md` at 21:11Z, reads **0 unexcepted breaches across 0 invariants, 6
excepted: the publish stands.** I re-ran the same runner (`load_book` with the printed customer files,
then `run`, then `gate`) on a snapshot of that ledger and the completed customer files. It
reproduced the table row for row. Probe outputs: `/var/tmp/grade76/` (not committed).

| claim (filed here) | measured | grade |
|---|---|---|
| The publish is wedged by five causes, and closing them clears the refusal | Every row this finding named is clean or inside its exception: EPG 355, all in the read-tenths class; EBSS 0 and 0; estimate-follows-reads 0 breached; gas repeat 1; INV_OVERDUE_WITHIN_BALANCE 0; INV_OVERDUE_WITHIN_PAGE_BALANCE 0; closing refunds 6, all in class. Gate verdict: refuse=false | **held** |

The book has not yet reached origin. Its publish commit was refused at 20:51Z by the stale-copy
guard, a non-test gate, not by this suite. The 21:11Z attempt left no outcome line, and the
publisher is re-running the marker (started 21:33Z, another lane). That is a landing cause, not a
billing one, and it is not this finding's.
