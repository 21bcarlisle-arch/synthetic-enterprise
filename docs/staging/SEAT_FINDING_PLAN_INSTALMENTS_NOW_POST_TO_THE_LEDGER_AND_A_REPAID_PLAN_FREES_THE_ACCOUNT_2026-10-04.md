# Plan instalments now post to the ledger, and a repaid plan frees the account instead of refusing

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey` · **Claim:** `plan-instalments-post-to-the-ledger` (Lane 0 delivery)

## Premise, re-measured at draw

The draw flagged a duplicate claim under this item's own id. The only holder in `ps` was this
invocation (seconds old), and no rival `surgical_land` touched the subject. So the claim is this
draw's own write and the work was not spent. At HEAD, `_read_instalments` raised
`PlanPaydownNotOnLedgerError` on any COMPLETED plan, because instalments moved only the plan book.

## Knowledge first: where plan cash goes

`docs/market_research/account_hierarchy_payment_allocation.md` s1: a domestic account is
**balance-based** (a rolling balance, with no matching of bills to payments) and ages FIFO from the
oldest unpaid bill. Open-item (business) accounts allocate by remittance, else oldest first.
Clayton's Case is cited there as the doctrine the oldest-first default simplifies. So plan cash
needs no plan-specific allocation: posted as an ordinary received payment, it discharges the oldest
arrears, and that is the debt the plan was agreed against. Nothing here needed a new number.

## What was built

- `CollectionsJourneyDesk` takes `post_cash`. Each instalment the seam reports PAID posts through it,
  on the instalment's due date, for the amount the plan book actually took (the final payment is
  the remainder, not the full instalment). The reference is `plan:<account>:<plan>:<n>`, which makes
  the post idempotent. A missed instalment posts nothing.
- `PaymentObservationConsumer._post_plan_instalment` routes those posts into the same `_post_cash`
  that remittances and successful ARUDD collections use, so they take the same ledger rule.
- A desk that can agree plans refuses to be built without the cash seam.
- `PlanPaydownNotOnLedgerError` and its refusal are removed.

## Printed at real inputs before the test

Two unpaid GBP 100 bills (01-01, 05-01), plan at GBP 60 agreed 02-12. Paid: credits of GBP 60 on
03-13 and GBP 40 on 04-12. The plan completes, the ledger falls from 200 to 100, and the May miss
opens a journey on **GBP 100**, so the repaid debt is not dunned again. Missed: no credits, the plan
defaults, and the May journey opens on GBP 200.

Control: `test_a_paid_instalment_posts_to_the_ledger_as_cash_and_a_repaid_plan_frees_the_account`
covers both legs. All four mutations went red: no post, post the instalment instead of the takings,
post on a missed instalment, and drop the seam guard.

## What it leaves open, named

1. **The world does not know about the plan's cash.** `simulation/plan_offer_response.py` draws
   paid/missed with no amount, and nothing on the world side treats the household's debt as being
   repaid through the plan. If the world's ordinary payment stream also pays down those arrears,
   the company receives the cash twice. This is inert live because every answer is None, but it
   must be settled before a sourced take-up rate is switched on.
   **SETTLED 2026-10-04**, and the route turned out to be the world's later lump settlement of the
   same bill, not ordinary payments:
   `SEAT_FINDING_THE_WORLD_NOW_KNOWS_AN_AGREED_PLAN_SO_ITS_ARREARS_ARE_NOT_PAID_TWICE_2026-10-04.md`.
2. **A plan's debt is fixed at the offer.** Ordinary payments that land meanwhile can leave the
   ledger in credit when the plan ends. A real desk would re-state the plan (docstring
   simplification 4).
3. **Instalments are read only at evaluation dates.** An account with an active plan and no further
   bills gets no evaluation date, so its instalments are never read. In a live run monthly bills
   supply the dates; a supply that has ended does not.

None of the three blocks the ten-year run from completing. Open item 1 blocks it from being
*right* once a rate exists.
