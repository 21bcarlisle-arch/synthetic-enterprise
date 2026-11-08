**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` §8.8a

# The ninth cold read finds closed accounts still holding credit and debt years after their last bill (2026-11-08)

**Found by.** The ninth cold read's O20 and O7, on the af31e73fa7 book.
- SYN-2016-250 is "Owed on 4 Jul 2025 £-236.74", a credit, with supply ended in 2021.
- SYN-2016-428 owes £111.93 from 2019.
- SYN-2016-035 holds a credit on electricity and a debt on gas, never offset.
- On the mover SYN-2016-527, "£36.31 owed" is followed by "We have refunded the credit on your closed account".

**This is a known class, recurring.**
`done/SEAT_FINDING_THE_CREDIT_REFUND_LOG_AND_THE_LEDGER_DISAGREE_ON_WHICH_MOVERS_ARE_OWED_2026-10-25.md` found that
the refund log and the ledger keep two books of who is in credit. On a 60-account run, 7 of 34 move-outs closed in
credit with no refund, and one debtor was refunded. That finding is in `done/`. Its symptom is on this book.

**Measured over every page.** The pages are `/var/tmp/ninth-read/tree/site/data/customers/`. The measure is
accounts whose last bill ends 1 year or more before the as-of date (4 Jul 2025), with a balance of at least £5 either way.
- 806 accounts have no bill for a year or more.
- **213** of them still hold a **credit**, £15,694 in all. GSoP reg 6D requires a refund. A credit the ledger holds
  with no refund is a breach the refund measure cannot see.
- **208** of them still hold a **debt**, £21,554 in all, neither collected nor written off on the page.
- No row grades a closed account's balance.

**What I cannot yet say:**
- whether the debts are written off in the company's accounts and only the page ledger fails to show it;
- whether the refund log paid the credits and the ledger dropped them (the 10-25 mechanism).

**Next.** The fix re-reads the 10-25 finding's §8.8a choice 4 against this book. One balance must decide both the
refund and the write-off. A blind row for "a closed account's balance reaches zero by a refund, a collection or a
write-off within a stated window" is owed. It was not in this read's blind batch, so it is still to write.

**Reverse.** Delete this file.
