**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`
**Knowledge:** home-moves -- `docs/market_research/home_moves.md` s.8.8d (the refund waits for its money)

# Old credit netted at close starts the refund clock late (2026-11-12)

*Found while grading `n29-setoff-ceiling-graded-on-fresh-book`. It is the one of the five
`INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` breaches that a fresh run will not clear.*

## What was seen

On SYN-2016-139, origin 90279e5318's pages over the 6fe7827ab2 run read:

- 13 Apr 2022: the final bill INV29537 is raised for 11.52. The balance is −32.04.
- 27 Apr 2022: "Direct debit returned", 0.00. On the same day, `credit_applied` 0.00 reads: "Account credit of
  GBP11.52 (the household's payment of 2021-05-07) netted against this bill".
- 12 May 2022: refund 32.04.

The runner starts reg 6D's clock at the last bill or cash on the page, which is 13 Apr. Ten working days later is
29 Apr, and the account is still 32.04 in credit then. The run's refund log reads `request_date` 2022-04-27 and
`breached_reg_6d_deadline` False.

## Why

`balance_settlement_from_outcomes`'s `money_in_out` (`simulation/arrears_engine.py`, the `arrived` loop) counts a
`kind == "repayment"` credit on the day the walk sets it against a bill. cab13bbd18 wrote that on purpose, naming
this account: "SYN-2016-139's 11.52, dated May 2021, settles an Apr 2022 return". 9392920e60 (fix 2) then ruled
the opposite for the page: "Cash that arrived before an arrears case opened is credit already on the account, not
that case's repayment". So the page shows it as credit that was already held, while the walk still dates it as
money arriving.

Fix 2 and s.8.8d point the same way. Reg 6D runs from the final bill. A credit, under SLC 27.16, exists once the
money does, and here the money arrived in May 2021. Applying credit the account already held is not money in.
So the refund was due by 29 Apr, and the world paid it 9 working days late without recording a reg 6D breach.

## The size of the class

1 of 176 closing refunds on this replay is a breach. This finding has not counted the legs where the same rule
moves the request day but the refund still lands inside the page's clock. Those carry the same defect, with no
row able to see it.

## Recommendation (a reversible world fix, not built here)

1. Amend s.8.8d first (K8): credit the account held before the final bill is not money in.
2. Then let `money_in_out` skip a repayment credit whose own cash day falls before the bill it settles. That is
   the date fix 2 already reads.
3. Pre-register the count of request days that move, and the reg 6D breaches that appear, on a replay before a
   run.

Until the fix lands, `DOMAIN_INVARIANT_EXCEPTIONS.yaml` holds the row at a ceiling of 1, scoped by name to this
account, so the 16 Nov publish is not refused for a traced defect. A second breach still refuses.

**Reverse.** Delete this file and the SYN-2016-139 exception.
