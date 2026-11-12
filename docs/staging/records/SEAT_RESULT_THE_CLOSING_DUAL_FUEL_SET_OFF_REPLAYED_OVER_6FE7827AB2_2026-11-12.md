**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Result: the closing dual-fuel set-off, replayed over the 6fe7827ab2 run JSON (2026-11-12)

This reads against the pre-registration `SEAT_PREREG_THE_CLOSING_DUAL_FUEL_SET_OFF_ON_THE_6FE7827AB2_RUN_JSON_2026-11-12.md`.
It is N29 (`SEAT_FINDING_A_CLOSING_DUAL_FUEL_HOUSEHOLD_IS_REFUNDED_ON_ONE_FUEL_WHILE_IT_OWES_ON_THE_OTHER_2026-11-11.md`).

## What landed, and what did not

- **Landed:** the knowledge, home_moves.md §8.8e (choices 21-24, GAP G8.17).
- **Landed:** the blind row `INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`, with its evaluator and test. A
  fresh agent wrote it from §8.8e, the runner and the page files. It opened no refund code.
- **Landed:** an exception, ceiling 60, so the red row does not stop the weekly publish. It retires with the build.
- **NOT landed:** the set-off build. It is kept as a patch at `/var/tmp/n29/build.patch`, with its test at
  `/var/tmp/n29/test_a_closing_dual_fuel_household_is_set_off_before_it_is_refunded.py`. Every leg is
  mutation-proven: 8 mutations, all of which fire. It is held back for the reason under Prediction 3.

## The readings (the publisher's page chain over the run JSON, in a scratch tree)

| book | blind row | `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` |
|---|---|---|
| 6fe7827ab2 as published (control) | **60** breached of 149 | 0 breached, 87 flagged |
| the same run JSON, with the set-off replayed through `generate_credit_refund_log` | **31** breached of 124 | **4 breached**, 69 flagged |

The control's 60 counts every household. The finding's 48 counts only those where the other leg owes at least
GBP 5. The row has no floor.

## Against the predictions

1. **Prediction 1 was wrong.** I predicted the row would fall to between 10 and 25. It fell to 31. The cause I
   predicted for the residue is right: the page and `closing_balances` disagree on the other leg. But it is
   larger than "60 minus 42" suggested, because the two walks disagree in both directions:
   - **20 households:** the world closes the other leg at 0 or in credit, while the page shows it owing. That is
     GBP 455.58 over the bound. Examples: PROS-2021-0117g, where the world says 0.00 and the page owes 153.24;
     PROS-2023-0013, where the world says 0.00 and the page owes 94.28.
   - **11 households:** the world set off its own closing debt, but the page's debt that day differs. That is
     GBP 233.41 over the bound. Examples: PROS-2016-0024g, where the world says 13.05 and the page owes 180.12;
     PROS-2020-0012, where the world says 228.58 and the page says 40.38 after the set-off.
2. **Prediction 2 held to the penny.** 42 refunds carry a set-off, GBP 1,339.69 in all, GBP 599.68 of it before
   2021. 26 credits were taken whole. No other refund moved, in amount or in day.
3. **Prediction 3** (the P&L close write-off falls by at most GBP 1,339.69) was not read, because no run was
   made. The page found a defect in the build itself. The set-off is posted beside the debt leg's arrears case,
   and the case is not netted by it. So the case still writes off its full amount later.
   - OCC-6387bf64272a has 4.64 set off on 22 Oct 2021, then a 2.93 part payment, then a case write-off of 4.64.
     The page closes at -4.64.
   - The same happens on SYN-2016-323, PROS-2016-0207 and OCC-cede70b10116g.

   Those are 4 new `CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` breaches, and with no exception they would refuse the
   next publish. So the build waits.

## What the build needs (the hand-off)

The set-off must enter the debt leg's own walk as a credit. `balance_settlement_from_outcomes` already nets a
credit oldest-first against a leg's outstanding bills. On the page, `_with_credits_applied` already turns a
credit into a CREDIT_APPLIED stage that reduces a case. Put the set-off through that machinery, and the case,
the page write-off and the P&L close write-off all fall together. Posting it beside them leaves them where
they were.

The 20 households where world and page disagree on the other leg are the same two-walk class that
`INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`'s 87 flags read. Netting in the walk should close part of it. The
rest goes to its own finding, with a cause for each household.

## Other things seen

- `tests/tools/test_billing_and_payments_ledger.py::test_reconciliation_identity_holds_across_full_live_book`
  fails at HEAD on the committed live pages (OCC-00909e50a521), with no change of mine. It was not traced here.

**Reverse.** Delete this file.
