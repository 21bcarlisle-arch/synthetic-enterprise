**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `DD_seasonal_cashflow_physics`
**Discharged:** `docs/reports/domain_invariants.json`, `tests/background/test_a_final_bill_reads_the_last_bill_issued_before_it_whether_or_not_it_is_due.py`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8f choice 29

# Row 7's three leavers are the world's due-only read at the final bill, not the desk (2026-11-17)

*Claim `row7-three-leavers-desk-ask-traced`. BLOCKING: row 7 (`INV_OVERDUE_WITHIN_PAGE_BALANCE`) is one of the two
rows refusing the 18f201c5bf book. The predictions below are filed before any book carries the fix.*

## What was traced

**The hypothesis on file is refuted.** That hypothesis (VAT finding s.9; D5 pre-registration, "What is not done") was that the desk's `left_level_asks`
dates a leaver's ask from a bill the final bill already netted. In fact the desk reads the cash that crossed, and it
is right. The page prints a final-bill payment that did not cross in full.

`background/live_payment_triad._leg_balance_on` reads a leg's balance at the final bill (D5 choice 26). It counted
bills only once they were **due**, but it counted **all** cash. A leaver's last regular bill is issued days before
the final bill and is not yet due when the final bill is issued. Its level cash, collected the month before, was
still counted. So the leg read in credit. The final bill netted that phantom credit and asked less than its face, or
nothing. The page (`balance_settlement_from_outcomes`) counts every issued bill, so it netted nothing and printed the
face as paid.

Read from the 18f201c5bf billing ledger and pages. Each row is the leg the phantom credit sat on.

| leg | last regular bill, not due at the final issue | due-only read | true balance | final face | netted | desk − page |
|---|---|---|---|---|---|---|
| SYN-2016-471 | 45893, 38.13, issued 1 Mar 2021, due 15 Mar | −9.35 | 28.78 | 14.10 | 9.35 | 38.13 − 28.78 = **9.35** |
| SYN-2016-523 | 48632, 107.27, issued 5 Jul 2023, due 19 Jul | −51.86 | 55.41 | 25.28 | 25.28 | 139.33 − 114.05 = **25.28** |
| SYN-2016-546 | 23.16, issued 2 Nov 2018, due 16 Nov | −8.10 | 15.06 | 6.73 | 6.73 | 49.98 − 43.25 = **6.73** |

That is 18 of row 7's 20 steps. The other two are SYN-2016-001's, a different class (D5 pre-registration file).

The same filter also under-asked the gas legs 523g and 546g. They were in debit, so the final bill asked a debit
without the not-yet-due bill (37.44 and 28.19). Page and desk agree on what was left, so no row saw it.

## The fix (this landing)

`_leg_balance_on` counts every bill issued on or before the day, except the bill being issued (`excluding`). The
other caller, the credit-bill "waits" rule, reads the same balance and so also counts an issued-but-not-due bill as
owed (SLC 27.16).

Control: `tests/background/test_a_final_bill_reads_the_last_bill_issued_before_it_whether_or_not_it_is_due.py`. With
the due-only filter restored, both tests go red: the leg reads −50 where it owes 10, and a true credit of 20 nets 25.

## Predictions for the first book carrying this commit (not one-variable)

1. **Row 7 loses SYN-2016-471, -523 and -546 entirely.** Each final collection now asks face plus the true debit. The
   outcome draw is keyed by period and is unchanged, so on this book's draws each succeeds and nothing stays owed.
   Row 7 reads **2** (SYN-2016-001), unless that book's draws move its 15 Aug 2023 lump.
2. **No new row-7 household of this shape.** If a leaver appears with desk − page equal to an amount netted off its
   final bill, this fix is incomplete.
3. **Move-out collections rise and level-leaver write-offs fall.** Upper bound: 125 ended level legs on the 18f201c5bf
   ledger had a last regular bill not yet due at the final issue, GBP 6,101.66 of such bills. The ask moves only by
   the part that was mis-netted or left out, which is less. How much less: **I cannot yet say.**
4. **Row 4 stays at most 1.** A failed final collection now leaves a larger ask owed from the final bill's due date.
   The runner already reads that bill as the demand (choice 27).

## Not done

- The closing-refund row (24 against 23) is EP4's, untouched here.
- `final_month_nets` still never reaches the run output (VAT finding s.9). So the netted amounts above are
  reconstructed from the ledger, not read from the world's own row. Prediction 1 is graded on the page and desk alone.

## Predictions graded on 6af7fd0bfd, the first book carrying 594ed82390; retired (worker tick, 18 Nov 2026 ~13:30 GMT)

The 6af7fd0bfd book (built 18 Nov 07:02Z, published by 43fa9534d9, live on poesys.net) carries D5 switched on (341df49657), the row-7 leaver fix (594ed82390) and the walk writer (d645233e8b). Its committed `docs/reports/domain_invariants.json` reads `refuse: false`, `unexcepted: []`. The book is not a one-variable test of this fix. It also carries the walk writer and every other landing
between 18f201c5bf and 6af7fd0bfd.

1. **Held, and went further than predicted.** SYN-2016-471, -523 and -546 have left row 7. The row reads **0**, not 2.
   SYN-2016-001's lump is not on this book's draws (its 2023 arrears cases each carry GBP 0.00), the case this
   prediction allowed for.
2. **Held.** Row 7 has no new leaver of this shape.
3. **Not graded.** I have not compared move-out collections and level-leaver write-offs between 18f201c5bf and
   6af7fd0bfd. **I cannot yet say** whether they moved, or by how much.
4. **Held.** Row 4 reads 0 of 975.

On the "Not done" items:
- The closing-refund row is re-keyed to the N29 class (153a675ad4). It reads 24, excepted.
- `final_month_nets` now reaches `world_walk_truth_<head>_<ts>.json` beside the run, which carries 5 entries on this book.

Moved to `done/`.
