**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8c (choice 14, GAP G8.15)

# A switching level leaver is refunded short: the world nets the final bill for movers only (2026-11-23)

*Closes the trace that `SEAT_FINDING_A_LEVEL_LEAVERS_FINAL_BILL_IS_NETTED_ON_THE_PAGE_AND_COLLECTED_AT_FACE_BY_THE_WORLD_2026-11-12.md`
asked for (claim `a-level-leavers-refund-is-paid-on-the-credit-it-held`). Pre-registration for the world fix:
`records/SEAT_PREREG_A_SWITCHING_LEVEL_LEAVERS_FINAL_BILL_NETTED_BY_THE_WORLD_2026-11-23.md`.*

## Who pays the refund, and from which figure

1. The world walk, `simulation/arrears_engine.balance_settlement_from_outcomes`
   (`arrears_engine.py:1540`), nets a level leaver's closing credit against its final bill (s.8.8c choice 14). It
   writes the netted closing to `closing_balances`.
2. `simulation/credit_refund_events.generate_credit_refund_log` states `credit = -closing` to the company.
3. The company answers through `company/interfaces/credit_refund_requests.refunds_on_account_closures` and
   `company/billing/credit_refund`. On all 149 legs below, `credit_amount_gbp + set_off_gbp` equals `-closing` to
   the penny. **The company refunds exactly the credit its ledger states. No `company/billing` change is warranted,
   so none is made.**
4. The world collects the final bill in `background/live_payment_triad.record_period`. The s.8.8c net (choice 25,
   37d934286) fires only when `final_month` is true. `final_month` needs `moved_out_on`
   (`live_payment_triad.py:1557`), and only a home move sets it (`simulation/run_phase2b.py:3652`). **A leg that
   switches away is never in its final month**, so its final DD asks the face, less only the credit-bill credit
   waiting.

The household therefore pays the final bill in cash at face (less credit-bill credit), and is then refunded the
closing balance, which assumes the bill was netted. It is refunded short by exactly the netted amount.

## Measured on 6a588a832f (the newest published book, 20 Nov)

Method: `/var/tmp/ll-scripts/replay.py`, run in a detached worktree at 6a588a832f, re-runs the walk on the book's
own `bills`, `per_customer_behavioral` and `level_dd_collections`. **Its closing balances match the book's
`closing_balances` on all 854 leaver legs, with 0 mismatches.** A netted leg is one whose final bill carries a
`credits_applied` row of kind "credit" listed under the leg's last level collection. The world's ask comes from
`world_walk_truth_6a588a832f_20261120T134224Z.json` → `final_month_nets`.

| Netted legs (page) | Count | GBP netted | What the world did |
|---|---|---|---|
| All | 216 | 4,780.79 | |
| World row, ask equals face less page net | 59 | -- | netted the same: refund right |
| World row, ask below face less page net | 8 | 201.03 asked less | netted more than the page (reverse, below) |
| **No world final-month row** | **149** | **3,673.83** | **collected at face: refunded short** |

The 149 legs are 146 switch-aways and 3 households that switched away before they moved: PROS-2019-0135,
PROS-2020-0132 and SYN-2016-326. Their final bills fall before `moved_out_on - 1 day`. 68 of the legs are gas.

**The 149 legs, by final bill year:**

| Year | Legs | Under-refunded GBP | Final bill face GBP | Refunded (incl. set-off) GBP | Credit held before netting GBP |
|---|---|---|---|---|---|
| 2016 | 4 | 85.13 | 138.32 | 21.35 | 106.48 |
| 2017 | 47 | 806.14 | 1,335.72 | 379.70 | 1,185.84 |
| 2018 | 11 | 231.81 | 369.76 | 120.79 | 352.60 |
| 2019 | 18 | 507.43 | 780.08 | 295.82 | 803.25 |
| 2020 | 32 | 754.33 | 949.86 | 2,406.95 | 3,161.28 |
| 2021 | 14 | 397.08 | 421.23 | 1,188.42 | 1,585.50 |
| 2022 | 4 | 28.77 | 75.90 | 148.29 | 177.06 |
| 2023 | 4 | 309.02 | 309.02 | 424.49 | 733.51 |
| 2024 | 9 | 354.73 | 432.33 | 2,700.30 | 3,055.03 |
| 2025 | 6 | 199.39 | 265.49 | 2,670.37 | 2,869.76 |
| **Total** | **149** | **3,673.83** | **5,077.71** | | |

In every year, credit held minus refunded equals the under-refund. On 85 legs the credit covered the whole final
bill: the world should have presented nothing, and it collected the face. On 52 legs the netting took all the
credit, so no refund event exists at all.

Largest: PROS-2020-0132 held 157.90, its 118.20 final bill (Sep 2020) was collected at face, and it was refunded 39.70.
OCC-7a3c89d8e37b held 288.46, was collected 98.07, and was refunded 190.39.

**The writer line** is `background/live_payment_triad.py:1557` (`final_month = bool(moved_out_on) and ...`). The
s.8.8c net at `:1587` sits behind it. The world is not changed in this item. Fixing it is the handed-on world half.

## The reverse: 8 movers netted more by the world than by the page (GBP 201.03)

OCC-4cf53939dfbf, OCC-6387bf64272a, OCC-cede70b10116, OCC-cede70b10116g, PROS-2016-0207, SYN-2016-010g,
SYN-2016-037g and SYN-2016-040g. On each, the triad's `_leg_balance_on` ledger credit was larger than the walk's
closing credit. OCC-4cf53939dfbf's ledger read -216.52 while the walk closed at 0.00, so the world took the
whole 61.20 face and the page netted 25.85. The household paid less cash than the page prints, so the page's
closing overstates what it holds. Two balances disagree here: the triad's ledger balance and the walk's. That is
a separate item, and it goes beside the world half.

## What this does to the 16 Nov pre-registration

`records/SEAT_PREREG_LEVEL_DD_W1_W4_AND_H1_H2_ON_THE_FIRST_FINAL_MONTH_NETS_BOOK_2026-11-16.md`, W1: on this
book `netted_ledger_credit_legs` is **84, GBP 1,768.48**, below its band of 168–213 legs and GBP 4,030–4,990. The
band was calibrated on every final bill the page netted, switch-aways included. The branch can reach movers only.
This is a reading, not that record's formal grade.
