**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `bad-debt-provisioning` -- `docs/market_research/bad_debt_provisioning.md` "How the company's write-off reaches the account page"

# The desk's write-off of a closed account never reached the page (2026-11-10)

*Delivery item `desk-write-off-reaches-the-page`. Correctness stretch (director ruling, 26 Oct). Parent:
`SEAT_FINDING_THE_LEDGER_BALANCE_WAS_PAID_LESS_BILLED_..._2026-11-09.md`, "Open: the desk's write-off never
reaches the page".*

## Premise, re-measured at draw time

On the 4dee9854a4 book (`/var/tmp/grade-ondd/ledger.json`), with the code at 36a31da845:

- the desk (`collections_desk_journeys`, stage `write_off`) wrote off **152** accounts, all under
  `closed_account_unpaid_a_year_after_its_final_bill`. 115 have two fuel legs and 37 have one;
- the page posts no write-off, or less than the desk's, on **121** of them, short by **GBP 17,782.71**;
- **120** still print a balance owed, **GBP 20,566.56**.

The premise is not spent. The committed ledger (run 0a6391d186) shows none of this: there, all 88 desk
write-offs are matched by the engine's per-invoice `WRITTEN_OFF`. The gap opened on a later book.

## What the gap is: two defects, not one

1. **Posting.** The page writes off only the engine's per-invoice cases (`arrears_history`,
   `WRITTEN_OFF`). An engine write-off dated on the desk's day is the **same** closing event (119 of the
   208 engine write-offs on these accounts are dated on it; the other 89 are earlier, different
   events). Where the engine raised no case for a bill, the desk's write-off has no line on the page.
2. **Amount.** The desk's figure and the page's balance on the write-off day differ on **93 of the 94**
   accounts where the page posts nothing (50 page higher, 43 page lower). PROS-2016-0117 is a level-DD
   leaver: the desk wrote off GBP 8.24, which is the level schedule's shortfall, and never counted the
   final bill (INV10139, GBP 61.85, no collection), so the page still shows GBP 70.09 owed. This is the
   C7 class (`58869f0f33`, `dea1c34fdf`), and a book carrying those fixes has not been graded yet
   (`longjob-book-78f82e4242` is running).

This item fixes (1). It does not fix (2), and it does not hide it.

## The rule (written before the after figures are read)

The split across legs needs both legs at once, so it is decided once, in the ledger generator
(`desk_write_off_postings`), and each leg carries its own share as `desk_write_offs`. The page and the
statement walk post that stored share. Neither re-derives it.

- The page posts the desk's figure **less** what the page already wrote off on that day. A posting is
  never in addition to the engine's posting for the same event.
- The remainder goes to the legs that owe on that day, largest debit first, each up to what it owes.
- If the desk wrote off **more** than the page shows owed, the excess is **not posted**: posting it
  would print a credit the household never had. It goes in the ledger's `desk_write_off_unposted`, by
  account and date, so it can be counted.
- If the desk wrote off **less**, the rest stays on the page as owed. The company wrote off what it
  wrote off, and the shortfall is defect (2), out in the open.

## Pre-registration (before any after figure is computed)

On the 4dee9854a4 book re-generated with this change:

- **P1.** Desk-written-off accounts still printing a balance owed: 120 → **45 to 60**. These are the
  accounts where the page owes more than the desk's figure.
- **P2.** Accounts with an unposted excess: **40 to 55**.
- **P3.** Accounts the posting itself puts into credit: **0**, by construction.
- **P4.** The statement walk against the page: **0 of 1,302** disagree.

On book 78f82e4242, once it completes (its output not yet read):

- **P5.** Desk-written-off accounts still printing owed after the posting: **30 or fewer**. The C7
  schedule fix should narrow defect (2). Low confidence: I have not traced which of the 50 it reaches.

## Result on the 4dee9854a4 book (the split applied to `/var/tmp/grade-ondd/ledger.json`)

| | predicted | measured |
|---|---|---|
| P1 desk-written-off accounts still printing owed | 45 to 60 | **63** (GBP 3,999.38), from 120 (GBP 20,566.56). **Missed** high by 3 |
| P2 accounts with an unposted excess | 40 to 55 | **70** (GBP 4,448.36). **Missed** high by 15 |
| P3 accounts the posting puts into credit | 0 | **0** |
| P4 statement walk against the page | 0 of 1,302 | **0 of 1,302** |

GBP 16,567.18 of the desk's write-offs now reach the page. **Why the misses:** I predicted from the
day-balance buckets of the 94 accounts with no engine write-off and left out the 58 that had one. 13 of
those 58 add to P1 and 27 to P2; the 94 give exactly the 50 and 43 I read. That was an error in the
prediction, not in the rule.

Named accounts: C3 and C7 close at 0.00. C2 still owes 53.05: the desk wrote off 219.57 against the
page's 272.62. C9 still owes 1.87 (146.98 against 148.85). PROS-2016-0117 still owes 61.85, the final
bill the desk never counted.

**What is left is defect (2), the amount.** The desk wrote off less than the page shows on 63 accounts
and more on 70. Each is now counted (the balance owed, and `desk_write_off_unposted`), and the next
piece is to make the desk's closing figure and the page's agree. P5 is graded when book 78f82e4242 lands.
