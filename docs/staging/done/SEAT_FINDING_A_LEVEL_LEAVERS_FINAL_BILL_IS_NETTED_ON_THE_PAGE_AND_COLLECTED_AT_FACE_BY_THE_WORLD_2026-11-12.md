**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8c (choice 14, GAP G8.15)

# A level leaver's final bill is netted on the page and collected at face by the world (2026-11-12)

*Found while closing `level-dd-142g-walk-draws-level-surplus-against-a-paid-bill` (LEVEL_DD map s.9.6).*

## What the code does

- **Page and engine.** `simulation/arrears_engine.balance_settlement_from_outcomes` nets a level leaver's
  closing credit against its final bill (s.8.8c choice 14, final bill only since s.9.6). The page prints the
  smaller payment, and the closing balance, which the refund pays, is reduced by the same amount.
- **World.** `background/live_payment_triad.record_period` takes a mover's final month off the level schedule
  (`final_month`: "settled on the final bill's face"). Its waiting credit `_leg_credit` holds credit-bill notes
  only, never a level surplus, so it asks and collects the bill's full face.

On the 6fe7827ab2 book this covers 195 legs and GBP 4,715.67 of final bills. The page says the credit covered
these bills. The world took the cash, and the desk counted it.

## Why it matters

The rules s.8.8c reads (SLC 27.17, 31H.12, 27.16, GSoP reg 6D) say the final bill nets the credit the account
holds. The page follows them; the world does not. If the refund is paid from the engine's netted closing, a
household on these legs is refunded less than it is in credit, by the netted amount. That is not established
yet: who pays the refund, and from which figure, is not traced here.

## Recommendation

Make the world net it too. At `final_month` on a leg that was on level DD, the triad's waiting credit should
include the schedule's surplus (`level_collection_difference`'s sign, as the walk reads it), so the final bill
asks its face less that surplus. That is a payment-truth change, the shape choice 16 already names as "not in
this step". Pre-register the 195 legs' money-in and refunds before running it. Until then the cure read is
unaffected: no hold rests on it.

## Not this

The s.9.6 fix is the other half: bills paid on receipt BEFORE the final bill keep their cash on the page,
because the world collected them at face (choice 17).

## Closed 23 Nov (claim `a-level-leavers-refund-is-paid-on-the-credit-it-held`)

Traced on 6a588a832f. The company refunds exactly the closing credit the walk states, on every netted leg, so
there is no company under-refund and no `company/billing` change. 37d934286 has since made the world net a
**mover's** final bill (59 legs agree, and 8 net more than the page). A **switch-away** level leaver is never in its
`final_month`, so its final bill is still collected at face. That is 149 legs, GBP 3,673.83, refunded short. The
writer is `background/live_payment_triad.py:1557`. The count by year, the writer lines and the 8 reverse legs are in
`SEAT_FINDING_A_SWITCHING_LEVEL_LEAVER_IS_REFUNDED_SHORT_BECAUSE_THE_WORLD_NETS_THE_FINAL_BILL_FOR_MOVERS_ONLY_2026-11-23.md`.
The world half is pre-registered in `records/SEAT_PREREG_A_SWITCHING_LEVEL_LEAVERS_FINAL_BILL_NETTED_BY_THE_WORLD_2026-11-23.md`.
