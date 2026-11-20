**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# The held per-debt sale rule learns from a window the agency never pays into, so on the varying world it sells debts worth 12.2p at 5.4p (2026-11-20)

Drawn item: `knife3-the-held-per-debt-sale-rule-lands-on-the-varying-world`. Branch
`knife3-per-debt-sale` (9fcd4a53fa) is now on origin under that name. The world change it waited for
(f696fca4eb: recovery after write-off varies with the bill's age at close) is on origin.

## Pre-registration (written 03:35Z, before any replay ran; verbatim)

```
KNIFE3 per-debt sale on the varying world -- pre-registration, written 2026-11-20 before any replay ran.
Book: docs/reports/run_output_67d454905c_20261119T184502Z.json, world at origin f696fca4eb, company
pieces from knife3-per-debt-sale 9fcd4a53fa.

Derived from constants only, not from outcomes: the world writes a close-leg debt off at final bill
+365 d (CLOSED_ACCOUNT_WRITE_OFF_AFTER_FINAL_BILL_DAYS), places it at +30 (DCA_PLACEMENT_DAYS) and the
agency remits at +180 (DCA_OUTCOME_DAYS): final bill +575 d. cash_forecast_provision.learn() counts
post-close cash in (last bill, last bill +365] (POST_CLOSE_RECOVERY_DAYS).

P1. 0 of the close-leg RECOVERED stages fall within 365 days of the debt's final_bill_on; every gap
    is 575 days.
P2. So, with the remittance posted to the company's book as cash on its own date, the learned
    cells carry NONE of the world's age gradient: an aged debt (>365 d overdue at close) and a young
    one in the same PostCloseCell get the same expected recovery, and the cells' spread, if any, is
    customer cash before write-off. Predicted: every cell's observed share is below 0.02, so every
    per-debt figure falls below the prior 0.122, towards the cell mean.
P3. Hence, at 0.054, 0.07 and 0.093, the rule SELLS nearly every close-leg debt (predicted > 90% of
    them by GBP), which contradicts the world, where working recovers 0.122 (young) or 0.063 (aged)
    per GBP and both beat 0.054. The per-debt rule as built would sell young debts at a loss.
P4 (control, window widened to 600 d in the replay only): the remittance then enters, and only cell
    (3, True) holds aged debts, so it alone falls below the others. Its figure lies in (0.063, 0.122),
    the other cells are about 0.122, and nothing is sold at 0.054 or 0.07.
Landing rule (from the direction): land the per-debt rule only if the cells spread with the world
AND both sell and work are reached at a published price. If P2/P3 hold, it does not land: only the
sensitive exclusion lands, and the window mismatch is filed as the reason.
```

## The replay (book 67d454905c, world f696fca4eb, company pieces from 9fcd4a53fa)

The company's book was rebuilt from `tools/generate_billing_ledger.generate` output:
- bills as BILL_DEBIT, with credit bills as ADJUSTMENT_CREDIT;
- successful payments as PAYMENT_CREDIT;
- the agency's RECOVERED amount as PAYMENT_CREDIT on its own date.

Then `learn(as_of=2025-07-04)` ran. Script: `/var/tmp/k3land/replay_kept.py` (machine-local).

| | window 365 (as built) | window 600 (replay only) |
|---|---|---|
| remittances inside the window | 0 of 215 (every gap is 570-599 d) | 0 of 215 in 365 d; all inside 600 d |
| cell (0, False) / (0, True) | 0.916 / 0.352 | 0.922 / 0.374 |
| cell (1, True) / (2, True) | 0.265 / 0.139 | 0.271 / 0.142 |
| cell (3, True), 149 placed debts (118 young, 31 aged) | 0.033 | 0.084 |
| SELL at 0.054 / 0.070 / 0.093 | 149 / 149 / 149 (GBP 5,991.86) | 0 / 0 / 149 |
| WORK at the same prices | 66 (GBP 2,194.95) each | 215 / 215 / 66 |

In every cell, aged and young debts get the same figure. For example, cell (0, True) holds 26 young
and 15 aged debts, and all 41 get 0.352.

## Grading

- **P1 HELD.** 0 of 215 remittances fall within 365 days of the last bill.
- **P2 WRONG in its number, right in its conclusion.** I predicted every cell would read below 0.02.
  They read 0.03 to 0.92. The cells spread, but on customer cash against the whole closing
  balance, and most of that balance is paid before write-off (582 closes, 215 written off). The
  world's age gradient reaches no cell. I had not thought about the denominator: the rule applies a
  figure learned on the whole closing balance to the written-off remainder, which is exactly the
  part the customer did not pay.
- **P3 HELD in kind, wrong in size.** I predicted over 90% of GBP sold. It was 73% (149 debts, all in
  (3, True)). The other 66 are worked only because their cell figures (0.14-0.92) are inflated by
  customer cash. They are right by accident.
- **P4 HALF HELD.** (3, True) read 0.084, inside (0.063, 0.122). Nothing sold at 0.054 or 0.070. But
  the other cells did not sit near 0.122, which is the denominator fault again.

## Disposition

The landing rule: the cells must spread *with the world*, and both sell and work must be reached.
They spread, but not with the world, so **the per-debt rule does not land.** Only the
sensitive-circumstances exclusion lands, at the rule and at the door, with mutation-checked tests.
No world caller passes `sensitive` yet: the company's PSR is not in reach of the post-run recovery
stage. Today the exclusion is reached by tests only.

**A successor needs three definitional fixes, not tuning:**
1. learn on the written-off remainder and the agency's remittance, not on the whole closing balance
   and customer cash;
2. use a window that covers write-off, placement and outcome (575 days in this world);
3. cut by the oldest unpaid bill's age at close (Energy UK's published cut, read off the company's
   own `fifo_unpaid_bills`), not by consecutive months unpaid, which caps at 3.

A further point: the company's book does not receive the agency's remittance as cash today.
`generate_payment_ledger_data` shows it as an informational `recovery_note`. So in-run, no
estimator could learn it until that remittance crosses as a ledger event.

Knowledge: `docs/market_research/debt_and_collections.md` s.7.7, "The held per-debt rule, replayed
on the varying world".
