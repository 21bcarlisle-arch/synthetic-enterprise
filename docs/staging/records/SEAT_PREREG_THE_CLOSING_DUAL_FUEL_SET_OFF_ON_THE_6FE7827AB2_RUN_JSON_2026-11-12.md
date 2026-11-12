**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Pre-registration: the closing dual-fuel set-off, replayed over the 6fe7827ab2 run JSON (2026-11-12)

Written before the replay. N29 (`SEAT_FINDING_A_CLOSING_DUAL_FUEL_HOUSEHOLD_IS_REFUNDED_ON_ONE_FUEL_WHILE_IT_OWES_ON_THE_OTHER_2026-11-11.md`).

**The question.** The set-off (home_moves.md §8.8e, choices 21-24) is built in the company's refund door and posted on
both page legs. Replayed through the page code over the 6fe7827ab2 run JSON, does the blind row
`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT` read 0?

**What is known before the replay.**
- The blind row reads **60 households** (GBP 3,965.95 refunded) on the unfixed 6fe7827ab2 pages.
- The fix nets against the world's `closing_balances`. There, 42 billing accounts close with opposite signs:
  GBP 1,339.69 settable, 31 of them before 22 Jan 2021.
- The row reads the other leg's debt from the page at the end of the refund day. The page and `closing_balances`
  are two walks (§8.8a says they agree at close; the cold reads have found them disagreeing before).

**Predictions, written down now.**
1. The row does **not** reach 0. It falls from 60 to between 10 and 25 households. The residue is households whose
   page shows a debt on the other leg that `closing_balances` does not: the other leg closes at 0 or in credit
   there, or it is still on supply. *Confidence: moderate.*
2. The set-off total in the replayed refund log is GBP 1,339.69 to the penny. Refunds of legs without a set-off do
   not move: same amount, same day.
3. The close write-off in the P&L falls by at most GBP 1,339.69.

If (1) is wrong and the row reads 0, the two walks agree on these households, and the residue reasoning was wrong.

**Reverse.** Delete this file.
