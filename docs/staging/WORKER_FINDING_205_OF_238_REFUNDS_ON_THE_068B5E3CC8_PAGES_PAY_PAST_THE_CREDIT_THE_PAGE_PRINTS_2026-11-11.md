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
