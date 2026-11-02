**Severity:** RECORDED · **Lane:** B_billing · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `control_cannot_fail` (primary)

# Pre-registration: SYN-2016-582's Aug and Sep 2017 estimates sit on the reads rung, because its change of supply is December 2016 and the row dates it from the first PRINTED bill

**Claim:** `trace-syn-2016-582-pc2-estimate`
**Written BEFORE the regraded row was run on the book.** The trace above it was done first, from the book.

## What the trace found (08f267b666 book, `run_output_08f267b666_20261102T173915Z.json` and its ledger)

- The run supplied SYN-2016-582 (electricity, PC2, registry EAC 22,909.7 kWh) from **2016-12-10**: 13 bills.
  The ledger prints 9, from 2017-04-01. The four from Dec 2016 to Mar 2017 sit in the ledger's
  `exception_queue` (pre-issue checks: 1,869 to 2,633 kWh a month "implausible for a resi electricity
  account", and the SME-as-household VAT check). Every bill prints the term `tariff_effective_from 2016-12-10`.
- The row dates the change-of-supply day as "the first bill's period_start less one day": 2017-03-31.
  The 31 Jul actual read is then 122 days in, under `switch_days` 182, so Aug and Sep are graded on the
  QUOTE rung, against Apr to Jun (which ARE the quote: Day/Night 955.8/814.9 is PC2's April split exactly).
- The company's register log opens on 2016-12-09 (`monthly_bill_assembly`, the change-of-supply read at 0).
  At the 31 Jul read its reads span 234 days, so it is on the READS rung and estimates each register from
  its own Dec 10 to Jul 31 advance: Day 7,147.9 x 3.627 / 35.397 = **732.4** and Night 7,261.6 x 1.438 /
  31.084 = **335.9**, both exactly the printed Aug registers. Sep likewise (836.6, 554.4).
- So the company followed its declared policy. The defect is the row's date for the change of supply on an
  account whose opening bills were held. The cause the exception guessed (308a3f168e over-correcting a
  Day-heavy register) is refuted: neither printed bill uses `annualised_register_advance_kwh`.

## The change

The runner dates the change of supply as the earlier of (the first bill's period_start) and (the first
contracted term's `tariff_effective_from`, which every bill prints), less one day. The opening read at 0
moves with it: the ledger's register index counts from 0 at the change of supply (Jul's closing 14,409.5
is the sum of the true use from 10 Dec), so the reads-rung's switch window is also corrected.

## Predictions, on the 08f267b666 ledger

1. INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS: **2 -> 0 breached.**
2. SYN-2016-582's Aug and Sep move to the reads rung, where with one actual read they are NOT graded (the
   row needs two), so the row's graded count falls by 2 from that account. Its Nov and Dec stay graded.
3. Any other account whose first term starts before its first printed bill (the held-bill accounts in the
   exception queue, five other entries) may move by a few bills; I predict no new breach anywhere.
4. Every other invariant row is unchanged (only this evaluator reads the change-of-supply day).

## Result

(written after the run, below this line)

Graded 2 Nov on the same 08f267b666 ledger and printed pages (`python3 -m tools.domain_invariant_runner
--ledger <shared>/docs/state/billing_ledger.json --printed <shared>/site/data/customers`), before and after:

| Prediction | Result |
|---|---|
| 1. the row: 2 -> 0 breached | **Held.** BREACHED 2 -> FLAGGED 0 (flags 136 -> 136) |
| 2. SYN-2016-582's Aug and Sep leave the graded count | **Held.** 30,710 -> 30,708 graded |
| 3. the other held-bill accounts: no new breach | **Held.** Acquisition date precedes the first printed bill on 3 of 1,293 pages: SYN-2016-582, PROS-2024-0010 and PROS-2025-0106. They are exactly the accounts in the ledger's `exception_queue`. None breaches. |
| 4. every other row unchanged | **Held.** The diff of the two grade tables is that one line |

The exception is retired in `DOMAIN_INVARIANT_EXCEPTIONS.yaml`. Its `retired_by` asked for "graded 0 on a fresh run".
That clause assumed a company-side cause. The cause is in the grader, and the company's bills do not move, so the same
book is the test. The next fresh run grades it again anyway.

What the held bills did to the customer is the filed queue-never-worked defect: SEAT_FINDING_THREE_SMALL_EXCEPTIONS_
TRACED_ON_THE_209C_BOOK_MOVERS_DDS_HELD_BILLS_AND_THE_REVENUE_ROWS_CLASSES_2026-10-29.md §3. A correction was added
beside its "unbilled for good" claim: here the July read's catch-up bills the held months as one £1,220.95 lump.
