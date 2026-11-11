**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** home-moves -- `docs/market_research/home_moves.md` §8.8a ("the refund and the closing balance are the same figure")

# 205 of 238 refunds on the 068b5e3cc8 pages pay past the credit the page prints (2026-11-11)

**Found by.** `INV_REFUND_WITHIN_THE_PAGE_CREDIT`, written blind to the refund code (ruling 26 Oct, step 4) in
the commit that files this. The row was filed for a blind writer by e6c1c11b4, which saw 6 legs pushed into
page debit by a final refund. It was graded on the publisher-built pages of the 068b5e3cc8 book
(`/var/tmp/tenth-read/tree/site/data/customers`, built at 6fff2c2575). Output: `/var/tmp/refund-blind-grade-068b.txt`.

**The prediction, and what it met.** The draw expected 6 legs. That number was e6c1c11b4's *change* against the
(b) book, not a level. On these pages the row breaches **205 of 238 refund lines, 149 households, GBP 5,061.85
paid past the credit**. 62 of them refund a leg that held no credit at all. Five of e6c1c11b4's six accounts
breach (OCC-caee88f5fe53g, PROS-2019-0318, PROS-2020-0012, PROS-2020-0191g, SYN-2016-369). The sixth,
PROS-2017-0351, is clean here: on the publisher's pages it is refunded GBP 21.86 *short* instead. That is the
closed-account row's excepted pair, not this row. The scratch pages e6c1c11b4 read were built by a different
chain.

**The shape, read from the page only.**
- **187 of 205:** the refund equals the credit the page printed *before* the last bill or bills. Those bills
  were then collected separately, almost always by direct debit the next working day. Example: SYN-2016-369
  holds GBP 294.70 after its 8.95 final bill on 7 Aug 2024. On 20 Aug it is refunded 303.65, and the 8.95 is
  collected on 21 Aug. A final bill is a statement of account with one balance (SLC 27.16, 27.17), so the
  refund should have been 294.70 with nothing to collect.
- **18:** the refund matches no credit the page printed earlier.
- **6** are followed within two lines by a returned direct debit. In those cases the refund made a debt the
  supplier then failed to collect. PROS-2019-0318 is one: credit 17.88, refunded 42.53, then a 24.65 "part
  payment" and a returned DD on the same day.
- The class runs across every year from 2016 to 2025, so this is not only class L's 2024 change.

**Consequence.** The publisher's gate now refuses every book that carries this shape. That is the ruling's
intent: before this row, the gate certified a book that refunds debtors. No exception has been filed, because
the class is a defect, not a practice. Nothing published moves until a book grades 0 or the director rules
otherwise.

**What done means.** On the first book after the fix, the row reads 0 breached over a non-zero refund
count. The control in `tests/tools/test_a_refund_never_exceeds_the_credit_the_page_shows.py` already proves
the row can pass: a refund to exactly nil passes. The fix belongs to the refund's sizing, not to the row. The
refund must be sized from the balance after the final bill. This writer has not read the refund code and
offers no mechanism.

## Reverse

Delete this file. Removing the row from `docs/design/DOMAIN_INVARIANTS.yaml` reopens the gate. It is the
wrong reverse unless the row itself is shown to be wrong.

## Fix landed, graded on a rebuild (2026-11-11, worker)

**Cause, two mechanisms** (home_moves.md §8.8c, written before the build):
- **A, the 187.** A level leaver's final bill is off the level schedule. The walk took it as paid at its
  face beside the level credit, so `closing_balances` refunded the whole credit and the final DD then
  collected the bill. Now the leaver's level credit meets its bills after its last level collection,
  oldest first, as `credits_applied` kind "credit". The ledger already prints a paid bill's payment less
  that (choice 11).
- **B, most of the 18.** On a level leg, a credit bill was drawn against the next level-paid month at the
  bill's face while the bank paid the level amount. The walk lost the credit, and the page netted it off a
  collection the world took in cash (SYN-2016-493: -42.56 credit, 31.00 collection printed 0.00). Now a
  level-paid month draws no credit.

**Prediction filed before the code** (`/var/tmp/close-refund-probe/PREDICTION.md`), graded on the
068b5e3cc8 run output with the refund log recomputed through the fixed walk, then the publisher's page
chain, then `_domain_invariant_gate_permits_publish` (`/var/tmp/close-refund-probe/{base,fix}/gate.txt`):

| | Predicted | Base (origin 3cb902dc8f) | Fix | |
|---|---|---|---|---|
| P1 refund lines past the page credit | <= 18 | 205 of 238 | **12 of 176** (GBP 256.38) | held |
| P2 SYN-2016-369 refund | 294.70, final DD 0.00, closes 0.00 | 303.65 | **325.82**, final DD 0.00, closes 0.00 | **missed**: B also gave back credit its level months had eaten. My model of B's reach was wrong |
| P3 SYN-2016-493 | refund 29.33, final DD 0.00, closes 0.00 | 12.90, closes 11.56 | 29.33, 0.00, 0.00 | held |
| P4 refunded legs closing non-zero | 2 (the excepted pair) | 3 | **0** | **missed**, toward clean: B cures the excepted pair too |
| P5 refund count | < 238 | 238 | 176 (GBP 21,381.05, was 24,693.37) | held |

Gate: base refuses on INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO (3) and this row (205). The fix refuses on
this row alone (12). No other row got worse. INV_DD_STEP_CHANGE flags 557 -> 496. 115 final payments
are now 0.00, settled by credit, so the payment-row counts fall by 115.

**The residual 12, named (§8.8c choice 16).** All 12 close at 0.00. In each one the refund pays out money
that reaches the account after it: a returned final DD that the household part-pays later (PROS-2019-0318,
SYN-2016-139, -202, -361, OCC-cede70b10116), or a final payment dated after the refund (SYN-2016-206g,
-244, -360, -360g, OCC-2974d725d75a). A nets only bills the world collected. Netting a returned final bill
would change the world's payment outcome, so it is a separate payment-truth step. This finding stays open
until a fresh book grades the row 0, or the residual is fixed.

**A published figure that moves on the next book.** Bad debt written off at close on this run output
falls from GBP 10,794.46 (121 leg-years) to GBP 10,293.54 (119), down GBP 500.92, under B. Refunds fall
from GBP 24,693.37 to 21,381.05.

## The residual 12 fixed: a refund waits for the money it pays out (2026-11-11, delivery seat)

**Cause.** Each of the 12 closed at the right balance, but on the wrong day. The closing credit counts every payment
the leg will make. The refund clock ran from the final bill's issue, so the refund paid out a final payment, a
part payment of a returned DD, or a repayment before that money arrived. The rule is now on the K8 page as
`home_moves.md` §8.8d, written before the code. A credit is payments in excess of the charges (SLC 27.16), so it
exists once the money does. The refund now runs from the later of the final bill, the last level collection, and
the last money the credit counts (choice 18). The amount does not move. GAP G8.16 covers two questions no source
answers: when reg 6D's clock starts for a credit that arises after the final bill, and how long a supplier waits
for funds to clear.

**Pre-registered** (`/var/tmp/crfix2/PREDICTION.md`, before the code). Graded on 068b5e3cc8's run output, with
the refund log recomputed through this walk, then the publisher's page chain and
`_domain_invariant_gate_permits_publish` (`/var/tmp/crfix2/gate2.txt`). Base: origin e58699ec9c plus the
§8.8c fix.

| | Predicted | Graded | |
|---|---|---|---|
| P1 refund row | 12 -> 0, count stays 176 | **CLEAN, 0 of 176** | held |
| P2 the 10 named legs | same amount, later, close 0.00 | all 10 later, same amount, 0 late under reg 6D, 0 refunded legs closing non-zero | held |
| P3 totals | refund GBP 21,381.05 and bad debt unchanged | refunds 21,381.05. The write-off code is untouched, so bad debt is unchanged by construction; not re-measured | held |
| P4 dates moved | >= 12 and < 40 | **14** | held at the end. First cut: **81**, then 24 |
| P5 no row worse | | No row is worse. `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` FLAGGED, 0 breached. At the 24-move cut it read **9 breached** | held at the end |

**Two wrong cuts, kept here.**
- **81 moved.** Level-paid bills were counted at their own due date. Their cash is the level collection,
  which the clock already counts: SYN-2016-369's July bill falls due on 15 Aug, but the bank paid on 12 Jul.
- **24 moved, and the closed-account row at 9 breached.** Credit rows were counted at their due date. A credit
  posts when its bill is issued, on or before the final bill, which is where the page prints it.
  PROS-2017-0351's -827.68 credit dated 22 Nov 2024 falls due on 7 Dec. That pushed its refund past the 10
  working days the closed-account row measures from the page's last payment.

**The control.** `tests/simulation/test_a_close_refund_waits_for_the_money_it_pays_out.py` is one control over 7
legs: 5 refunds move and 2 do not. All 8 mutations fail it: no money day reported, level-paid bills counted, a
credit-settled bill counted as cash, credit rows counted at due date, the refund log taking the first date
instead of the later, a repayment applied later ignored, repayment rows ignored, and a part payment ignored.
Mutations 5 to 8 passed until the fixture gained the leg each one needed.

**What the gate still refuses on this book.** Only `INV_OVERDUE_WITHIN_PAGE_BALANCE`: 22 breaches, all
SYN-2016-549. That is D1's class. The 068b5e3cc8 book predates D1 (b47832f7e). D1's own book graded the row 0 of
6,385, and origin retired its exception in dc3e7dfeb4. Owner: the next head book, which carries D1, §8.8c and
§8.8d together. This finding closes when that book grades the refund row 0.

**Named limits, not fixed here** (§8.8d choice 20):
- A returned final DD is still not netted against the credit.
- A level leg long off its schedule still pays its final bill whole beside a credit made of a repayment, then
  gets the credit back. SYN-2016-244 pays 77.82 where the bill should have asked 35.68.
- Both now show as late refunds of money the household paid, not as refunds of money not yet received.

## Retired (2026-11-11, worker tick)

The close condition above was that the next head book, carrying D1, §8.8c and §8.8d together, grades the refund row 0.
That book is 6fe7827ab2, run on cab13bbd18 and published at e816040ce8. Its committed `docs/reports/domain_invariants.json`
(git 6fe7827ab2) reads **INV_REFUND_WITHIN_THE_PAGE_CREDIT CLEAN, 0 breached of 176**. The count of 176 matches the
§8.8c prediction. The same file reads INV_OVERDUE_WITHIN_PAGE_BALANCE CLEAN at 0 of 6,385, so D1's class is gone as
predicted, and the verdict is refuse False with nothing unexcepted. The sister closed-account finding was retired on
the same book in 0827311117.

The two sections above, from the worker and the delivery seat, were written in the shared tree and never committed.
They land here unchanged as the record of the fix.

The named limits of §8.8d choice 20 stay open as limits, not as this finding. A returned final DD is not netted
against the credit, and a level leg long off its schedule is refunded late. Neither breaches this row on the
published book.

Reverse: move this file back to the staging root.
