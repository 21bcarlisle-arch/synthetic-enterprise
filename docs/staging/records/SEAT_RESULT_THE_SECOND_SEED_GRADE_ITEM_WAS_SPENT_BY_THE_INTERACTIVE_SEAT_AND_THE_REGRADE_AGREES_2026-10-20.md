# The second-seed grade item was spent before it was drawn; an independent re-grade agrees

**Severity:** informational — no defect; a drawn item whose premise was already spent.
**Item:** `the-budget-second-seed-grade-after-the-unit-driver` (drawn 2026-10-20 ~17:31Z)

## What was asked
Grade the seed-2 arms in `SEAT_PREREG_THE_SHARED_SHORTFALL_ON_A_SECOND_DICE_SEED_2026-10-20.md`, write the
SEAT_RESULT, add the "Graded, second seed" section, flip `BUDGET_DECIDES_PAYMENT` and
`ENERGY_SHARES_THE_SHORTFALL` if P1–P5 and B1 hold, then remove `/var/tmp/budget-seed2`.

## What I found at draw time
- The driver had finished: `ALL_DONE 2026-10-20T17:34:42+01:00`, and all three arms were written.
- The grade had landed 14 minutes earlier as b8045dd4e, with
  `SEAT_RESULT_THE_SHARED_SHORTFALL_HOLDS_ON_A_SECOND_DICE_SEED_2026-10-20.md` and the knowledge-page section.
- The switch flip is **in the interactive session's hands**. Both constants are `True` in the shared tree's
  `simulation/household_budget.py` (mtime 18:15 BST), and that session was running its wider tests on the flip when I
  drew the item. I did not touch it, so it does not land twice.

## Independent re-grade (same script, same arms)
`python3 /var/tmp/budgetpay/grade6.py seed2_off.json seed2_basket.json seed2_shared.json` gives the same result,
figure for figure, as the landed record. Shared minus off, Q4 2016–21: −0.5 to +0.9, with 0 years above +1. U1 is
2/31 = 6%. GBP behind per account, Q4 2023: £302 shared and £1,011 basket. The diff-in-diff is +2.1. U4 is 0.926. 55
households are under water in both ON arms. The landed verdict "every band holds" is reproducible from the artefacts.

## Done here
- `/var/tmp/budget-seed2` is unlocked and removed. Its only changes were run by-products (context handshake,
  observability ledgers). The arms' evidence lives in `/var/tmp/budgetpay/seed2_*.json`.
- The claim is released. Nothing else is owed on this item. The flip and the crisis bad-debt validator belong to the
  lane that landed b8045dd4e.
