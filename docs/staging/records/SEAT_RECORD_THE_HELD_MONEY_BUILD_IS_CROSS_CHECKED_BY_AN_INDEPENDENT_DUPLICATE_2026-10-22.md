**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `W2_demand_negative_margin_part_payment`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-22: held money is a part payment"

# The held-money build is cross-checked by an independent duplicate, which is withdrawn

**2026-10-22, 02:45 BST.** The seat executor drew `W2_demand_negative_margin_part_payment` at 02:33.
The interactive session had already built it on the shared tree, unclaimed:
`HELD_MONEY_IS_A_PART_PAYMENT`, prereg `SEAT_PREREG_HELD_MONEY_IS_A_PART_PAYMENT_2026-10-22.md`, arms
`longjob-held-{off,on}-arm` launched at 02:28 from `/var/tmp/held-mut`. The executor's turn built the
same rule independently (`HELD_MONEY_STAYS_WITH_THE_BILL`, which keeps the held money in its own
field). It found the rival arms before its landing finished, stopped the landing, and withdrew its own
build and prereg. Nothing from that turn is on any branch.

**What the duplicate is still worth: a cross-check of the build being graded.** Both modules were
replayed over the seed-2 demand arm's own credit bills (`/var/tmp/leaver_trace/arm_demand_s2.json`,
1,048 accounts, driver `/var/tmp/partpay/crosscheck.py`), with every bill's outcome compared: whether
it was paid, and which earlier bills cleared. **The two builds agree on every account, switch off
(0 of 1,048 differ) and switch on (0 of 1,048).** The switch moves 62 accounts. So the arms now
running grade the rule the knowledge page states, not an artefact of one way of writing it.

**Two counts the grade can reuse.**
- Zero-payment spells of 12+ months on credit accounts (`/var/tmp/partpay/zero_spells.py`), seed-2
  arms: **demand 22** (461 account-months, median 15.5, longest 46, every one starting with `m < 0`);
  **stock 0**.
- Offline replay of the rule alone over the same bills (`/var/tmp/partpay/replay.py`; no transient
  draw, no churn feedback): zero spells **14 to 0**. At 31 December 2023 the budget-driven tail moves
  from **20 accounts at £1,572 to 18 at £916**, which agrees with the prereg's H3/H4 direction.

**The process cause, for the record.** The interactive session built a direction item without
`seat_work_in_hand --claim`, so the executor drew it as well. This is the known trap
(memory: "INTERACTIVE SESSION: claim BEFORE building"), and this time it cost one executor turn.
