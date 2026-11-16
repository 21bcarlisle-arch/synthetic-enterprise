**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The revenue row never read a back-billing bar, and its one remaining breach is an unread tail at the record's end (2026-11-16)

*Worker tick, drawn on the publish-gate wedge (domain_invariant_refused on the f7e17b1316 book).*
*BLOCKING: `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` is one of the rows refusing the 16 Nov publish. D5 holds two more rows (the level-DD finding).*

## What was traced

Both breaches are on the f7e17b1316 book, graded with `tools.domain_invariant_runner --ledger docs/state/billing_ledger.json --printed site/data/customers`. This reproduces the publisher's 2.

1. **OCC-cc0c78690877g (B 1606.19, lower bound 1613.21): fixed in this commit, in the row's reader.**
   - Bill 7852 (May 2025) carries a catch-up of 15 periods that SLC 21BA capped: `catchup_written_off_gbp` 28.26 (gross; the assembly bars it from the gross raw delta, `monthly_bill_assembly._resolve_catchup`).
   - The row's W is "energy the supplier may not bill under SLC 21BA". The evaluator read W from `ledger.total_written_off_gross_gbp`, which holds debt write-offs and never a bar (0 on this page). So W was 0 on every book.
   - It now reads each bill's bar at that catch-up's net share: 26.91 before VAT. The account sits at 1633.10 against a lower bound of 1586.30.
   - **Re-graded on the same book:** 2 → 1. Every other row is unchanged (all BREACHED rows diffed), and nothing went to flagged. The prediction (2 → 1, OCC clears, PROS stays, nothing else moves) was written before the re-grade.
2. **PROS-2025-0095g (B 141.25, lower bound 142.04, short by 0.79): not fixed. This is the row's U bound, not a billing defect.**
   - The account opened 8 Apr 2025. The record ends 7 Jun 2025, and all 435 accounts with a June bill end on that day.
   - Its last actual read is May. The 1–7 June bill is estimated at 85.8 kWh (12.3/day). The company's own P&L month settles 238.24 kWh for the same seven days. That is 34/day, against 27.5/day on May's actual read.
   - The tail is therefore under-billed by ~152 kWh, about £8.6 before VAT. The row's U (the tail bill's own 7.84) assumes an estimate misses by no more than its own size. This one missed by 178%. Because the account is two months old, the 1% tolerance is only £1.51.
   - The P&L is not over-accruing. Across 435 accounts, June P&L kWh over June billed kWh has a **median of 1.00**. The tails run both ways: 0.31 at the low end and 3.1 at the high end, all estimated final-week bills.
   - The world's June is in the top tenth of gas legs, not off the scale. June/May daily is 1.23, where the median is 0.83 and the 99th percentile is 1.42.

## Recommendation (gate owner's call, not taken here)

`unbilled_energy_and_revenue_assurance.md` §1 K2 says billed ≠ consumed "until the next actual read", with either sign and **no magnitude bound**.
- On an account still supplied at the record's end, the row should grade the gap below the lower bound as a **flag** when it lies inside the unread estimated tail's period, not as a breach.
- The estimated run has not been read, so the record cannot establish an error in either direction.
- A closed account keeps its breach, because its estimated final bill closed the run.

This is a change to a gate's bound, and it is filed rather than made. The alternative is a dated exception naming this account, expiring on that change.

## Not established

- Whether the June estimate (12.3/day against May's actual 27.5/day) is a poor estimate. `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` grades that shape; I did not read its flag list for this account.
- The YAML's T term. It reads `ledger.as_of_date` (4 Jul) as the end, but R stops at 7 Jun. The code's "T is zero" is the right reading on this book, and the YAML text overstates it. It is not changed here.
