**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# A closing dual-fuel household is refunded its credit on one fuel while it owes on the other, and the debt is later written off (2026-11-11)

**Found by** the eleventh cold read, objection O14, from an Energy Ombudsman case investigator's lens
(`records/SEAT_READING_THE_ELEVENTH_COLD_READ_ON_THE_6FE7827AB2_BOOK_2026-11-11.md`). **Measured** over every page
file of the 6fe7827ab2 book (`/var/tmp/crbook/arm/tree/site/data/customers`, script
`/var/tmp/eleventh-read/run/scripts/crossleg.py`). Each leg's balance is the running sum of its ledger, and all 1,090
legs reconcile to their own `current_balance_gbp`.

## What it is

At closure, the supplier refunds one fuel leg's credit on its own while the same household owes at least GBP 5 on its
other fuel leg on the refund date.

## How big it is

| quantity | value |
|---|---|
| dual-fuel households on the book | 545 |
| refunds of at least GBP 5 on a dual-fuel leg | 135 |
| refunds paid while the other leg owed at least GBP 5 | **48**, on 48 households, every one at closure (0 mid-life) |
| GBP refunded | 3,786.62 |
| GBP the other leg owed on the refund date | 5,662.78 |
| of that debt, later written off | GBP 2,254.02, on 18 households |

The reader's case is PROS-2019-0318:
- Electricity was refunded GBP 111.33 on 26 Jun 2023.
- On that date gas owed GBP 1,047.61.
- GBP 871.11 of that was written off on 30 May 2024, and GBP 176.50 is still owed on 4 Jul 2025.

The largest case is SYN-2016-552:
- Electricity was refunded GBP 57.21 while gas owed GBP 1,127.01.
- GBP 946.34 of that was later written off.

## Why it is a class, and why it counts as serious

- **The rule.** SLC 27.8D (from 22 Jan 2021) lets a supplier set a credit on one fuel off against a debt on the other.
  `INV_HOUSEHOLD_PAGE_PAID_STAGE_COVERS_EVERY_FUEL_ACCOUNT` already quotes it. It is a permission, not a duty.
- **What we know.** Whether real GB suppliers net a closing dual-fuel customer's two legs before refunding is not
  established in our knowledge layer. It is practice, and a practitioner question (K4).
- **Why it counts.** It moves money: a refund is paid out, and a write-off follows on the same customer. Under
  `serious_class_rule` (priority_order.yaml, 11 Nov), unproven either way counts as serious. So it holds exit leg
  three.

## How it relates to what is known

This is the money consequence of split 1 in
`SEAT_FINDING_A_DUAL_FUEL_HOUSEHOLD_IS_TWO_ACCOUNTS_IN_COLLECTIONS_2026-10-25.md`, which found collections keyed per
fuel leg. That finding judged "All 7 leg credits at close are refunded on their own fuel" sound (SLC 27.16). It did
not look at the other leg, so the defect was never named.

Neither of today's gate rows can see it:
- `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` reads each leg alone.
- `INV_REFUND_WITHIN_THE_PAGE_CREDIT` reads the refunding leg's credit only. It is CLEAN on this book.

## Proposal

1. **Knowledge first (K8).** Add a home_moves.md section on closing a dual-fuel household: SLC 27.8D, what Ombudsman
   decisions say about set-off, and what is GAP.
2. **Then a blind row**, written from that page alone: a closing household's refund is at most the credit across all
   its fuel legs on the refund date.
3. **Then the build** in the close-refund engine (`simulation/credit_refund_events.py`), keyed by household.

The row's ceiling is the 48 measured here.

## Reverse

Delete this file.
