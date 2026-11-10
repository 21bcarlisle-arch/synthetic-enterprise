**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `payments-and-direct-debit` -- `docs/market_research/payments_and_direct_debit_2026-10-25.md` "Leaving level direct debit with a debit: the closing statement"

# A credit bill waits for the next bill in the world and meets the scheme debit on the page (2026-11-10)

*Delivery item `syn-2016-549-page-balance-breach-is-named-and-fixed`. Correctness stretch (director ruling, 26 Oct).
Parent: `SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE_2026-11-10.md` (class L).*

## What the breach is (written before reading a step)

`INV_OVERDUE_WITHIN_PAGE_BALANCE` on a leg that has left level DD: the desk printed a step on day d with "GBP X
overdue", and X is more than the household's pages (the sum of each fuel page's balance at the end of d) say is owed.
Off level, the desk's figure is the unpaid asks capped at the company's own balance (`arrears_engine.age_left_level`),
so a breach means the company's balance is above the page's: the page shows money in that the company never had.

## Premise, re-measured at origin head

The control (book 78f82e4242, ledger regenerated at d867f5a98e, which carries 6fb708f3a): **22 breaches, all on
SYN-2016-549**, as on `/var/tmp/grade-dca2/control-78f/`. Predicted before running: 22, not fewer, because class L only
adds money in to the page, which can only lower what the page shows owed. **549 is not class L.**

## The cause, traced to the penny

On 18 of the 22 steps (9 days) the desk's figure is the page's owed **plus GBP 53.98** exactly. The other 4 (15 Jul 2021, 20 Mar 2023) are 3.54 and 4.29 over, days when the desk's unpaid asks sit below the company's balance. Before Dec 2019 the two agree
to the penny on every capped step. The 53.98 opens in Sep 2020:

- The gas leg left level DD in Feb 2019. Its Dec 2018 and Jan 2019 level collections (58.82 each) were returned and
  settled at the level amount, against bills of 86.01 and 85.61. **27.19 + 26.79 = 53.98** is the face-minus-level
  remainder of those two months: part of the leg's scheme debit, owed since the closing statement.
- On 1 Sep 2020 the leg got a **GBP -62.12 read catch-up credit bill** (INV50959).
- **The world (the triad)** let the whole credit wait for the next bill (`background/live_payment_triad.py`, the
  `_leg_credit` block). Its test is "no failed bill on the leg stands unsettled". Its leg rows carry a level month at
  the level amount, so every failed bill reads as settled and the scheme debit reads as nothing. The household was
  asked **0, 0 and 41.60** for the Sep, Oct and Nov 2020 bills (21.83, 32.37 and 49.52), and paid that.
- **The page's walk** (`simulation/arrears_engine.balance_settlement_from_outcomes`) holds the 53.98 open on INV50951,
  the newest bill the Feb 2020 settlements did not clear, oldest first. It nets **53.98 of the credit there** (SLC 27.16,
  credit meets arrears first) and only 8.14 off the next bill. So it posts **13.69 + 32.38 + 49.52 = 95.59** of cash
  for bills the household paid **41.60** on. The page shows **GBP 53.98 that never crossed**.
- **The company's desk** ages the credit note against the earliest due (`unpaid_asks`): the closing statement. So it
  holds the next bills owed at face, and its balance is the cash truth. **The desk is right about the money.**

**Whose error.** It is the **world's** first: the triad's credit test misses the scheme debit, so the household is asked
nothing on bills its supplier's own desk then chases at face. The **page** compounds it by re-deriving cash with a
different rule from the one that set the ask. Neither the desk nor the reader is wrong.

## How wide: every credit bill on the book (`/var/tmp/g549/census.py`)

| | credit bills (not in a level month) |
|---|---|
| on the book | 125 |
| the triad let it wait whole | 102 |
| ... and the page netted part against old debt (page shows cash never sent) | **1**: SYN-2016-549g, GBP 53.98, every one of the 22 breaches |
| the triad did not let it wait, and the page took part off later paid bills (page drops cash the household sent) | **5**: PROS-2020-0126g, PROS-2021-0152g, SYN-2016-016, SYN-2016-380, SYN-2016-382 |

The census reproduces the triad's test from exported truth. The triad's own test uses each failed bill's *drawn*
settlement date, so its result can differ wherever a settlement was withdrawn or cut to nothing. The book does not
export what each bill asked, so on this book **the page cannot know the cash exactly**. That is why no page-only fix is
built here: it would copy the world's rule into a second place, which is the VAT-rule shape.

## The fix (next item, K8 first): `a-credit-bill-meets-the-scheme-debit-before-the-next-bill`

1. **Knowledge.** Amend the closing-statement section of `payments_and_direct_debit_2026-10-25.md`: a credit bill issued
   after a leg left level DD while its closing-statement debit is still owed. Which debt does the supplier set it
   against (SLC 27.16 credit net of arrears; SLC 31H.12 the next bill asks its charges less the credit)? What does the
   household get told?
2. **One rule, one place.** The supplier decides what the next bill asks, from its own ledger: the credit waits only for
   what exceeds the leg's debit (the scheme debit included). The world pays what was asked. The truth records each
   bill's ask, and the page posts that cash rather than re-deriving it.
3. **Pre-registered for the first book carrying it:** this breach class 0 (549's 22 → 0). The 5 mirror legs' page cash
   equals the cash asked. The walk's closing balances move on every leg with a credit after leaving level, so refunds
   and bad debt move and must be marked.

## The residual, excepted

`docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`: `INV_OVERDUE_WITHIN_PAGE_BALANCE`, at most 22, filed 2026-11-10, retired by
the item above graded 0 on a fresh run. A defect, not an explanation, excepted so the gate's last named blocker on the
control is named rather than unexplained.

## PROS-2019-0318's three unshown collections (GBP 190.13), traced

| collection | GBP | what it is |
|---|---|---|
| 25 Jul 2022 | 65.17 | **Returned** (truth: Jul 2022 failed). Nothing crossed that day, so nothing should post. The household settled 65.17 on 22 Nov 2022 (truth `repayments`). The electricity page's entries show no money in on that day, so whether that cash reaches the page is **not yet established** (it may sit on another row). |
| 28 Dec 2022 | 62.48 | **Class L′: a scheme-credit month drops its level collection.** The Dec 2022 bill (INV16543, 32.39) was met by the EBSS credit (67.00). The engine's outcome is `credit`, the page gives it `method = "scheme_credit"` (`tools/generate_billing_ledger.py`, line 572), and the level collection is taken only `if method == "direct_debit"` (line 1014). The world collected it (truth: success). |
| 24 Mar 2023 | 62.48 | The same, on the Mar 2023 bill (INV16546, 42.83, EBSS 67.00). |

Class L′ is class L's shape on the other branch: 6fb708f3a fixed a credit **bill's** month and left a bill met by a
**scheme** credit. It is EBSS-only (Oct 2022 to Mar 2023 on level legs where the month's credit exceeds the bill). Next
item `a-scheme-credit-month-keeps-its-level-collection`, to be pre-registered on this control. The world's walk
(`level_collection_difference`) has to be checked for the same gap first.

## Step 1, the knowledge: written (worker, 10 Nov 2026 ~00:00 GMT)

`payments_and_direct_debit_2026-10-25.md` "A credit bill after leaving with the debit still owed" answers the step's two
questions from SLC 27.16 and 31H.12 (already read in `home_moves.md` §8.8a). The credit meets the leg's unpaid charges
first, and only the excess waits for the next bill. The household is told one figure owed, by or to it. There are two
GAPs, both on the document, not the amount. The build's choice and its prediction are filed there before any code:
549g 22 -> 0, at most 3 of the 102 waiting credits' asks move, and the 5 mirror legs do not move.

NEXT: a-credit-bill-meets-the-scheme-debit-before-the-next-bill
