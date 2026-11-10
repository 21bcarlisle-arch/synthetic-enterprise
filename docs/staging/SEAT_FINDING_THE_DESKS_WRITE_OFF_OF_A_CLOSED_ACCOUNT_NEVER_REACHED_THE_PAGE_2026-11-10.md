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

## P5, graded on book 78f82e4242 (`/var/tmp/grade-78f/ledger.json`, the split applied to it)

The book carries the C7 schedule fix and the level cap. Before the posting: 152 desk write-offs, 121
short on the page by GBP 17,678.65, and 123 accounts printing owed (GBP 21,963.08).

| | predicted | measured |
|---|---|---|
| P5 desk-written-off accounts still printing owed | 30 or fewer | **49** (GBP 3,673.84). **Missed** |
| accounts with an unposted excess | (not predicted) | **26** (GBP 2,743.39), against 70 on 4dee9854a4 |
| accounts put into credit / walk against page | 0 / 0 | **0 / 0 of 1,302** |

I had the direction right and the side wrong. The C7 fix mostly removed the desk's write-offs that were
**above** the page (70 to 26). The desk's write-offs **below** the page fell only from 63 to 49.
PROS-2016-0117 is an example: on this book the page shows 38.24 owed on the day, against the desk's
8.24, so 30.00 stays owed. What is left is the desk writing off less than the page shows. That is the
next piece: the desk's closing figure for a level-DD leaver has to count the final bill as the page
does.

## The 49, traced (item `desk-closing-figure-counts-the-final-bill`, 2026-11-10)

**The frame above was wrong for PROS-2016-0117.** The desk did not miss the final bill. INV10139
(61.85) was collected in full on this book. The 30.00 the page still shows is the level collection
returned on 2017-10-23. The household settled it on 2017-11-06 (`world_payment_truth.repayments`, kind
`settlement`). The company's book saw that cash, and so did the world's closing walk:
`closing_balances` is 8.24, the desk's figure. **The page is the one that missed it.**

The mechanism is in `tools/generate_billing_ledger`. A household's repayment reaches the page only as
an `ARREARS_REPAID` stage of an arrears case. A returned level collection with nothing short on the
desk's figure opens no case (`outcome_case = None`), so the repayment the engine matched to that bill
is dropped. This is the same class as `part_paid_gbp` (OCC-cede70b10116): money received on a failed
collection that opened no case.

Census over the 49 on book 78f82e4242: the gap is all GBP 3,673.84. Repayments dated by the write-off
day that the page does not post explain **14 exactly** (GBP 911.92) and **19 in part**. **16 have
none**, so something else causes those. All 49 are level-DD accounts. No account off level is short.

### Pre-registration (written before the change is measured)

Change: when a level return opens no case, its repayments go on the payment record and the page and
the statement walk post them as money in. On book 78f82e4242, with the change and the split applied:

- **P6.** Desk-written-off accounts still printing owed: 49 → **30 to 38**. The 14 exact cases close.
  Some of the 19 partial cases close.
- **P7.** Accounts with an unposted excess: 26 → **26 to 34**. Where the page already matched the desk,
  a newly posted repayment can push the page below it.
- **P8.** Statement walk against the page: **0 of 1,302** disagree.
- **P9.** PROS-2016-0117 closes at **0.00**.

### Result on book 78f82e4242 (ledger regenerated from the run output, before and after, one variable)

The baseline regenerated at HEAD (5cc1afea9c) reproduces the P5 figures exactly: 49 still owing,
GBP 3,673.84, and 26 unposted.

| | predicted | first build | with the cap (landed) |
|---|---|---|---|
| P6 desk-written-off accounts still printing owed | 30 to 38 | 35 (GBP 2,116.50) | **37** (GBP 2,281.34) |
| P7 accounts with an unposted excess | 26 to 34 | 38. **Missed** | **31** (GBP 3,252.82) |
| P8 statement walk against the page | 0 of 1,302 | 0 | **0 of 1,302** |
| P9 PROS-2016-0117 | 0.00 | 0.00 | **0.00** |
| accounts the posting puts into credit | 0 | 0 | 0 |

**The first build missed P7, and that miss found a second defect.** It posted the repayment the
engine's walk matched to the bill, and that is the bill's **face**. The household paid the **level
amount** it was asked, which is what the world's payment truth records: PROS-2016-0054g settled 31.21,
and the walk says 46.10. SYN-2016-612 settled 166.16, and the walk says 236.02. Twelve accounts flipped
from "desk below the page" to "desk above". The landed build caps what it posts at what the return
left owed. The cap was added **after** P7 was graded, so P7 counts as missed on the build it was
written for. It is inside the range only on the corrected build.

The 5 accounts still newly unposted (PROS-2016-0370, PROS-2017-0393, PROS-2019-0216, SYN-2016-183,
SYN-2016-406) post exactly the world's repayment, or less. The page is right about the cash on them
now, so the desk's figure above it is a disagreement on the desk's side. It is counted, not resolved.

**Book-wide, the same class is wider than the write-off.** This compares every leg's repayments in the
world's payment truth (dated by the book) with the household repayments the page posts:

- before: **249 legs**, the page short by **GBP 17,828.49** (truth GBP 95,163.40, page GBP 77,334.90);
- after: **194 legs**, short by **GBP 6,399.16**.

The rest is on legs where a case **did** open. There the stage posts the walk's share, which can be
the face, or can leave part of a settlement unposted (PROS-2019-0216g: truth 27.22, page 15.84).
Some legs go the other way (OCC-1bb3be076448: truth 27.00, page 49.38).

**Next piece:** post the household's repayments on the page from one source and check them against
the world's payment truth on every leg. Then re-measure the 37 and the 31. Probably not the desk: on
PROS-2016-0117, which this item was drawn on, the desk was right.

## The page's repayments against the world's cash (item `page-repayments-agree-with-the-worlds-payment-truth`, 2026-11-10)

**What is being compared.** Per leg, dated on or before the book date (2025-07-04):
**T**, the cash of each household repayment the world's payment truth records, as the engine receives
it (`world_payment_truth.repayment_rows`); **E**, what the engine's walk credits as kind `repayment`
(`credits_applied`); **P**, what the page posts as household money in (`ARREARS_REPAID` stage amounts
plus `payments[*].repayments`). Reader: `/var/tmp/repay-truth/measure.py`. The figures above (194 legs,
GBP 6,399.16) came from another reader that I could not find, so this section re-baselines on its own.

**Baseline, book 78f82e4242, ledger regenerated at c5d99ba357:** T GBP 94,133.49, E 92,548.54, P 88,764.23.
The page differs from the cash on **186 legs**: short on 157 (GBP 5,939.92), over on 29 (GBP 570.66).
The desk figures reproduce: **37** accounts still printing owed (GBP 2,281.34), **31** with an unposted
excess (GBP 3,252.82), the statement walk **0 of 1,302**. The engine writes off 272 bills, GBP 10,838.68.

**Where the gap is. Every mismatched row is on a level-DD leg.** 912 rows agree. The rest:

- *The engine credits the face, not the cash.* It prices a settlement at `min(asked, open)`, and both
  are in face terms. A level household settles the **level amount** it was asked. 130 rows are credited
  above the cash (GBP +2,647.70; OCC-1bb3be076448, cash 27.00 and credited 49.38). 144 are credited below it
  (GBP -3,906.90; OCC-3c914ee8cef5g, cash 39.55 and credited 23.00, the summer face). 5 are credited
  nothing (GBP -325.75) because the walk counts the leg as paid at face. `level_collection_difference`
  skips failed months, so a settled failed month adds up only if the walk credits the **cash**. On a
  leaver, crediting the face misstates the closing balance by the difference, which moves the P&L's
  write-off too.
- *The page does not show repayment cash the walk puts on a paid bill.* That is the excess pooled and
  drawn by a later paid bill: 106 bills, GBP 2,016.82, never shown as money in. The page posts **less**
  than the walk on 96 level-return bills with no case (GBP 1,767.49), and there it posts the cash, because
  the room cap already stops at the level amount.

### Pre-registration (written before either change is measured)

The change:
1. In the engine's walk, a settlement on a level-DD leg credits the cash that crossed. What finds
   nothing open waits as credit on the account, as other excess already does. Other legs are unchanged:
   cash already equals the credit on all 388 of their rows.
2. On the page, any part of a truth repayment's cash that no stage or `repayments` entry posts goes on
   the payment record, dated on the day it was received. The page and the statement walk both read
   that record.

On book 78f82e4242, regenerated with both changes:

- **Q1.** Legs where the page differs from the cash by a penny or more: 186 → **0 to 5**. Any left are
  dated so that the stage date, `max(paid, case opened)`, passes the book date.
- **Q2.** Legs where the engine credits more than the cash: 77 → **0**.
- **Q3.** Desk-written-off accounts still printing owed: 37 → **25 to 35**. Accounts with an unposted
  excess: 31 → **31 to 40**. More cash on the page pushes some accounts below the desk's figure.
- **Q4.** Statement walk against the page: **0 of 1,302**.
- **Q5.** Engine write-offs (GBP 10,838.68): **I cannot predict the sign**. The face over-credit raises
  them and the dropped cash lowers them. Predicted |change| < GBP 2,500. This figure feeds the P&L, so
  the run's bad debt moves on the next book and has to be marked when it does.

### Result on book 78f82e4242 (the ledger regenerated from the run output with the change, one build)

| | predicted | measured |
|---|---|---|
| Q1 legs where the page differs from the cash | 0 to 5 | **0 of 367** (page GBP 94,133.49 = cash GBP 94,133.49). The first build left **17** (GBP 640.21). Two settlements on one day shared one key and the second was lost (SYN-2016-244, 15 Feb 2017). Fixed before landing, so Q1 is **missed** on the build it was written for. |
| Q2 legs the engine credits above the cash | 0 | **0** |
| Q3 desk-written-off accounts still printing owed | 25 to 35 | **29** (GBP 1,987.24), from 37 (GBP 2,281.34) |
| Q3 accounts with an unposted excess | 31 to 40 | **28** (GBP 3,320.24), from 31. **Missed**: I had the direction wrong. I cannot yet say why it fell. |
| Q4 statement walk against the page | 0 of 1,302 | **0 of 1,302** |
| Q5 engine write-offs | \|change\| < GBP 2,500 | 272 bills GBP 10,838.68 → **283, GBP 10,957.34** (+GBP 118.66) |

**A second engine defect, found by the measurement and not predicted.** The first engine build
credited the cash, but a later **paid** level collection drew the excess back out of the account, as
if the household had paid less. The household paid that collection in full, and `difference` already
reconciles it to the face. So the walk lost cash that crossed, and the refund at close never paid it
back. The test was: of the closed legs in credit on the page, how many equal the corrected walk's
closing credit less the run's refund? On the first build, **0 of 43**. With a level leg's paid
collection no longer drawing repayment credit, **39 of 41** (GBP 1,217.48). The 2 left are
PROS-2016-0263g (GBP 1.65) and PROS-2017-0351 (66.31 on the page, against 44.45). They are recorded, not traced.

**What this moves, and has to be marked.** Legs in credit on the page rise from 215 to 260. 41 of
them are closed level legs whose credit the run's refund log (paid from the old walk) never repaid. The
next book's reg 6D refunds come from the corrected walk, so they should rise by about GBP 1,200, and its
bad debt by about GBP 120. Both are book figures. Grade them on the first book run with this code.
`open_on_contract_gbp`, which sizes the world's cash, does not pass the level schedule, so the cash
each household sends is unchanged.

**Out of scope, recorded.** On a level leg the page nets a **credit bill's** credit from the level
collection as if the collection were smaller (`credit_applied_gbp`), but a level collection is
fixed. Not measured. `test_every_journey_opens_the_day_after_a_bill_the_ledger_made_due` fails at
c5d99ba357 **without** this change (3 journeys: PROS-2016-0020, SYN-2016-325, SYN-2016-005).
`test_reconciliation_identity_holds_across_full_live_book` also fails at c5d99ba357 without this
change, in a fresh worktree whose `site/data/customers` is stale (OCC-00909e50a521, GBP 102.30).

## The 29 and the 28, traced (item `desk-and-page-agree-on-the-29-and-the-28`, 2026-11-10)

**Premise, re-measured.** Book 78f82e4242, ledger regenerated at 8100fc86e (`/var/tmp/desk29/ledger.json`):
**29** desk-written-off accounts still printing owed (GBP 1,987.24), **28** with an unposted desk
excess (GBP 3,320.24), statement walk **0 of 1,302**. Same as the last section. Not spent.

**Every gap is on the write-off day.** No account in either set has a page movement after the desk's
day except a DCA recovery note (zero amount). So each one is "the company's ledger on the day" against
"the page on the day". Define **X** = the page's balance on the desk's day, with every engine write-off
dated after the account's last bill added back, and every closing refund taken out. Readers:
`/var/tmp/desk29/s/{trace,classify,resid}.py`.

| class | accounts | desk vs X | what it is |
|---|---|---|---|
| **U. Same write-off, another day** | **all 28** unposted (GBP 3,320.24) | desk = X on all 28 | The engine writes off each fuel leg a year after **that leg's** final bill. The desk writes off the account a year after the **account's** last bill. On a dual-fuel account those are days apart (SYN-2016-285: engine 41.95 on 31 Mar 2019, desk 41.95 on 4 Apr 2019). The posting nets only an engine write-off dated **on** the desk's day, so it found nothing owed and counted the whole figure as excess. A posting-rule defect. No money is in dispute. |
| **R. A refund the desk never sees** | **18** owing (GBP 446.29), exact | desk = X | The run pays closing-credit refunds after the run (`simulation/run_phase4c_on_phase2b.py`, from the world walk's `closing_balances`). They never reach the company's ledger, so the desk writes off the balance **before** the refund and the page owes the refund. 19 of the 20 refunds are on dual-fuel accounts. Two parts: **stale**, the refund above the leg's cash credit (the walk this book ran on credited the face; 47fdeacd5 fixed it for the next book), GBP 336.60 on 18 of the 20 refunds; **per leg**, one leg's credit refunded while the account's other leg owes, GBP 218.00 on 13. (The two parts are summed over all 20 refunds, including the one on PROS-2017-0249 and the ones on the two accounts that are also in another class. I first wrote GBP 340.60 on 17 and GBP 218.47 on 13 here, before summing them. Those were wrong.) The stale part should go on the next book. The per-leg part will not. |
| **L. A presented level collection the page never resolves** | **11** owing (GBP 1,540.95) | desk below X | All level DD. The world presented a level collection (`level_dd_collections`) that has no payment row on the page, neither paid nor failed. The gap equals it exactly on 3 (SYN-2016-218g 19.63 on 13 Mar 2017, SYN-2016-035g, SYN-2016-571g), and in part on the other 8. The desk's figure is below the page's by that cash, so the company's ledger counted a collection the page did not. Not traced to which side is right. |

(R and L overlap on PROS-2018-0359. One account, SYN-2016-552, is R+U.)

**Why the unposted count fell 31 → 28, against the prediction.** Class U is a fixed set of accounts,
whatever the repayments do: it depends only on the two write-off dates. The repayment change moved 3
accounts' day balances, and that changed which side of the desk they sat on. It did not create excess.
I predicted the direction from "more cash on the page lowers the page", and I left out that U's excess
does not depend on the page's cash at all.

### Pre-registration (written before the change is measured)

Change: the posting nets **every engine write-off on the account's legs dated after the account's last
bill and on or before the desk's day**, not only the one dated on the day. Each engine amount is netted
once across the desk's stages.

On book 78f82e4242 at 8100fc86e plus this change:

- **S1.** Accounts with an unposted desk excess: 28 → **0**.
- **S2.** Desk-written-off accounts still printing owed: 29 → **30**, GBP 1,987.24 → **GBP 2,003.70**.
  PROS-2017-0249 is U+R: once the engine's write-off is netted, its 16.46 refund stays owed.
- **S3.** Statement walk against the page: **0 of 1,302**. Accounts the posting puts into credit: **0**.
- **S4.** Desk postings in total fall by the same-event engine amounts no longer double-counted:
  **I cannot predict the size** without running it, so this is not a prediction.

### Result (book 78f82e4242, ledger regenerated at 8100fc86e with the change, one variable)

| | predicted | measured |
|---|---|---|
| S1 accounts with an unposted desk excess | 0 | **0** (from 28, GBP 3,320.24) |
| S2 desk-written-off accounts still printing owed | 30, GBP 2,003.70 | **30, GBP 2,121.64**. Count hit, amount **missed** by GBP 117.94 |
| S3 statement walk / legs put into credit by a posting | 0 / 0 | **0 of 1,302 / 0** |
| S4 desk postings in total | (not predicted) | GBP 17,660.71 → 17,526.31 |

**Why S2's amount missed.** Two of the 29 owing accounts were also class U, and I carried only
PROS-2017-0249 through. SYN-2016-552 rises 30.68 → 118.70, which is its refund. PROS-2019-0318 rises
229.01 → 258.93, which is its class-L gap. Once the engine's earlier write-off is netted, the desk had
been covering part of those gaps with it.

**What is left is exactly two classes, to the penny.** The 30 accounts owe GBP 2,121.64 =
**R** GBP 550.77 (19 accounts: the 17 exact, SYN-2016-552 and PROS-2017-0249) + **L** GBP 1,570.87
(11 accounts). No account is unexplained.

### Next pieces (each its own item)

1. **L, a presented level collection the page never resolves** (11 accounts, GBP 1,570.87). The world
   presented it (`level_dd_collections`) and the page has no payment row for it. Is it paid in the
   world, failed in the world, or never resolved? Then which side is wrong, the page or the company's
   ledger? Start on SYN-2016-218g: 19.63 presented on 13 Mar 2017, which matches the gap exactly.
2. **R per leg** (GBP 218.00 on 13 refunds). The run refunds one fuel leg's credit while the
   account's other leg owes. SLC 27.16 treats the account as one balance, so the credit should meet
   the other leg's debt first. The refund is world-side and post-run
   (`simulation/credit_refund_events.py`) and the desk never sees it. Both need fixing.
3. **R stale** (GBP 336.60 on 18 refunds). This should go by itself on the first book run at or after
   47fdeacd5. Grade it there and do not build for it.

## Class L traced: a credit bill eats that month's level collection (2026-11-10, same item)

**A first hypothesis, refuted.** "The unshown collection sits next to a credit bill" was tested on the
two bills **before** each collection: **0 of 17**. That was the wrong window, because the page keys a
level collection by the month of the bill's period end.

**What it is.** On a level-DD leg, the page takes the month's level collection
(`level_dd_collections`, keyed by leg and month) only while posting a bill whose method is
`direct_debit` (`tools/generate_billing_ledger.py`, the `level = (level_dd.get((cid, period_end[:7]))`
line). A **credit bill**, such as a read catch-up that refunds an overcharge, has no method and takes
the `else` branch. Its month's level collection is never taken, so the cash the household's bank paid
that month has no row on the page. **15 of the 17** unshown collections across the 11 accounts are in a
credit bill's month: 14 where the next bill is the credit, and SYN-2016-037g on 3 Apr 2017, whose
credit falls a month later. The two that are not are PROS-2019-0318 on 28 Dec 2022 and 24 Mar 2023,
and those are not traced. SYN-2016-218g: 19.63 presented on 13 Mar 2017, and the 1 Apr 2017 bill is
a -11.30 catch-up credit.

**Who is right.** A level direct debit collects the set amount whatever the month's bill is
(`payments_and_direct_debit_2026-10-25.md`, "What a level direct debit must be"). The company's ledger
counted the 19.63, which is why the desk's figure is 19.63 below the page. **The world's closing walk
drops it too**: `closing_balances` for SYN-2016-218g is 73.44, the page's figure. So the page and the
world's walk are both wrong in the same way, and the desk is right. The walk's closing balance sizes
the run's refunds and its bad debt, so this is a book figure and not only the page's.

**Next piece (`a-credit-bills-month-keeps-its-level-collection`):** in the world's walk and on the
page, a level collection presented in a credit bill's month is money in, at the level amount, on its
collection date. Pre-register the change in class L (11 accounts, GBP 1,570.87) and in the walk's
closing balances before measuring it. The world side is `sim-engineer` work.

## Class L built: a credit bill's month keeps its level collection (2026-11-10, worker tick)

**The change.** This was one variable, and the page and the world's walk pair it identically. For a credit bill, the engine now carries the triad's result for the month as `collection_result`. That result is the presented level collection's own (`arrears_engine._resolve_bills`).
- **The world's walk.** `level_collection_difference` makes that bill take its month's collection. A paid collection is all difference.
- **The page.** `tools/generate_billing_ledger.py` posts a paid collection as a level DD payment on the credit invoice, at the level amount, on its collection date. A returned collection posts nothing, because nothing crossed and the credit bill owes nothing.
- **The company's books.** `saas.ledger.build_ledger` already paired every bill in the month, credit bills included, so it needed no change. That is why the desk was right.

**Predicted before measuring** (`/var/tmp/lvlcred/PREDICTION.md`), on book 78f82e4242, regenerated with and without the change:

| | predicted | measured |
|---|---|---|
| P1 SYN-2016-218g walk closing balance | 73.44 → 53.81 | **73.44 → 53.81** |
| P2 walk closing balances that rise | 0 | **0**; 59 of 850 leaver legs fall, GBP 6,860.04 in total |
| P3 unshown collections on the 11 class-L accounts | 17 → 2 | **17 → 3, a miss.** All three are on PROS-2019-0318 (25 Jul 2022, 28 Dec 2022, 24 Mar 2023), which this change does not touch. The other ten accounts go 14 → 0. My filter counted three PROS-2019-0318 collections where the trace above counted two. |
| P4 existing level DD rows changed | 0 | **0**; 196 rows added, all on credit invoices (GBP 22,717.63) |

Across the book, schedule rows with no page payment on their date fall from 744 (GBP 55,019.57) to 548 (GBP 32,301.94). The remainder is returned collections and other classes, not graded here.

**What moves when the next book runs.** The walk's closing balance sizes the reg 6D refunds and the bad debt at close. On this book that is 59 leavers whose balances fall by GBP 6,860.04, so refunds rise or write-offs fall by up to that sum on the next run. Every published refund and bad-debt figure will move. This book's published figures were made before the change, and that is stated here rather than recomputed off-run.

**Seen and not built (next item, untraced on the book).** In the walk, a level household's paid DD bill still draws waiting credit of kind `"credit"` (the `_draw(... ("credit",) if on_level ...)` line). The household paid its level amount in cash whatever the credit, and the triad keeps the credit on the balance (`record_period`: "A level collection takes the level amount whatever the bill: credit stays on the balance"). So a credit bill followed by a paid month reads as credit used in the walk, while the page holds it. The unit test here places the credit last to keep this out of scope. It is a hypothesis to measure on the book, not a finding yet.

**PROS-2019-0318** (three collections, GBP 190.13) is still not traced.
