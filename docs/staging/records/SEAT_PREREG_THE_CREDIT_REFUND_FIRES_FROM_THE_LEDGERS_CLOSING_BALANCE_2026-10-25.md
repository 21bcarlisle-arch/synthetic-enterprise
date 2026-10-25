# Pre-registration: the move-out credit refund fires from the ledger's closing balance

**Written 2026-10-25, before either arm ran and before the credit rows were named.** Claim
`the-credit-refund-fires-from-the-ledgers-closing-balance` (Lane 0, seat). Knowledge:
`docs/market_research/home_moves.md` §8.8a. Finding:
`docs/staging/SEAT_FINDING_THE_CREDIT_REFUND_LOG_AND_THE_LEDGER_DISAGREE_ON_WHICH_MOVERS_ARE_OWED_2026-10-25.md`.

**The one variable.** Which balance `generate_credit_refund_log` reads to decide that a closed account
is in credit and how much it is owed.
- Arm A (today): its own level-DD smoothing balance (trailing-mean DD less each bill), DD payers only.
- Arm B (the build): the run's `closing_balances`, the ledger's balance at the final bill
  (`arrears_engine.balance_settlement_from_outcomes`), credit negative; domestic accounts whatever
  their payment method, since reg 6D binds a domestic credit however it was paid.

Everything else is held: 60 founder supply points, report end 2020-12-31, settlement budget 0, seed 42.

**Why B and not DD3 first.** The world now has one payment truth (`world_payment_truth.py`): a paid
bill is paid exactly. No household in the run ever paid a level DD amount, so the smoothing balance
is money nobody collected, and a refund of it hands back cash that was never taken. DD3 (posting a
level DD's over- or under-collection to the ledger) needs the world to collect level amounts first.
That is a payment-truth change, not this one.

**Predictions.**
1. Arm B refunds exactly the move-outs `move_out_final_bills` grades `debt == credit` (7), and no
   move-out it grades carried or settled. A refund to a ledger debtor is 0 by construction; the
   control is a test, not this run.
2. Arm B's refunded total over all leavers equals the sum of the domestic leavers' negative closing
   balances to the penny (at most £253.74, the all-leaver figure printed at 33dd50527).
3. Arm A reproduces the printing at 33dd50527: 3 move-out refunds (C1, C1g, SYN-2016-052), none of
   the 7.
4. Bad debt and every P&L line are identical between arms to the penny: the refund log feeds no cash
   line today (it is graded, never booked). If anything moves, that is a finding.
5. The 7 ledger credits are mostly gas legs closing on an estimated read: a negative final true-up or
   a credit bill. I expect at least 5 of 7 to net from a single `credit` row on the last two bills.

## Result

Run 2026-10-25, both arms on one tree; arm A is HEAD's module, called with its own arguments
(`/var/tmp/credit_refund_probe/arm.py`; outputs `/var/tmp/credit_refund_probe/arms/arm_{A,B}.json`).
The row naming is `/var/tmp/credit_refund_probe/r60/named.json`.

| | Arm A (smoothing balance) | Arm B (ledger closing balance) |
|---|---|---|
| Move-outs refunded | 3: C1, C1g, SYN-2016-052 | 7: exactly the 7 in ledger credit |
| Owed on the ledger, unrefunded | 7 | 0 |
| Refunded, not owed on the ledger | 3 | 0 |
| All leavers refunded | 10, £327.64 | 13, £253.74 |
| All-leaver refunds to an account the ledger holds in debt or settled | 8 | 0 |
| Everything else in the run output | digest 315411e27746567f | identical |

1. Exactly the 7: **held**. One of the 7 is paid late (the 90% on-time draw), so reg 6D now has a
   late refund to grade, where arm A had none.
2. £253.74 to the penny over 13 legs, all domestic: **held**.
3. Arm A reproduces 33dd50527's 3 refunds: **held**.
4. Nothing else moves: **held**. Every other key of the run output is byte-identical, which confirms
   that the refund is graded and never booked (§8.8a choice 10).
5. At least 5 of 7 net from a credit on the last two bills: **refuted**, 2 of 7. The other 5 are
   mid-life credit bills the walk sets only against arrears. They sat for 5 weeks to about 2½ years,
   filed as `SEAT_FINDING_A_MID_LIFE_CREDIT_BILL_IS_NEVER_SET_AGAINST_THE_NEXT_CHARGE_2026-10-25.md`.

Arm A handed £327.64 back to 10 leavers, 8 of whom the ledger did not hold in credit. That money had
never been collected, because no household in the run pays a level DD.
