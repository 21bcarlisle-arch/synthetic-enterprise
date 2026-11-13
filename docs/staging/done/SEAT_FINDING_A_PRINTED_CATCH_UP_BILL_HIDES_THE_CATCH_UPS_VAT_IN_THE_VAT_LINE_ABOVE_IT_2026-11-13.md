**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# A printed catch-up bill hides the catch-up's VAT in the VAT line above it (N31, presentation, 2026-11-13)

**Found by** the twelfth cold read, objection O15 (billing-systems test analyst,
`records/SEAT_READING_THE_TWELFTH_COLD_READ_ON_THE_6FE7827AB2_BOOK_2026-11-13.md`).

## What it is

On "THE BILL, AS THE CUSTOMER RECEIVED IT", a bill carrying a catch-up prints its lines in this order:

1. usage;
2. standing charge;
3. network and environmental;
4. **VAT**;
5. **catch-up adjustment**;
6. total.

The VAT line includes the catch-up's VAT. The catch-up line below it is ex-VAT.

**Example:** OCC-A097D0031A9F-INV5940, April 2023.
- The lines above VAT come to £74.73 + £8.32 + £14.53 = £97.58, so 5% VAT on them is £4.88.
- The VAT line prints £5.96, which is 5% of £97.58 + £21.57.
- The catch-up prints below the VAT line, ex-VAT, at £21.57.
- The total is right (£125.11).

## Severity: presentation, not serious

No money moves. Over all 47,528 domestic bills on this book, `scripts/arith.py` finds:
- VAT at 5% of the net, catch-up included, on every bill;
- totals that close on every bill.

A customer or a tester checking VAT against the lines above it reads a wrong VAT figure. SLC 31A asks for a bill a
customer can follow.

## What done means

The catch-up line prints above VAT, or the catch-up prints VAT-inclusive with its VAT named. The page's VAT line then
equals 5% of the lines above it, and a door test reads that from the rendered bill.

**Reverse.** Delete this file.

## Done (2026-11-13)

`site/explore/index.html` `BILL_COMPONENTS` now prints the catch-up adjustment above VAT; VAT is the
last line before the total. No figure changed: only the order of the lines.

Door test `site/explore/test_a_catch_up_bills_vat_is_the_vat_of_the_lines_above_it.py` drives the
page's own `billEquationHtml()` over the committed per-customer ledger extract (`site/data/customers/`):
- OCC-a097d0031a9f-INV5940 (the id is lower-case hex on the book; the cold read printed it upper-case)
  reads VAT £5.96 = 5% of £97.58 + £21.57, with nothing between VAT and the total;
- every domestic catch-up bill with VAT (6,581) prints VAT within 3p of 5% of the lines above it.

Red before the change: both tests, 6,585 of 6,585 catch-up bills failing. Green after.

The population test covers domestic accounts only. Four SME catch-up bills fail a single-rate
identity. Two of them (C5-INV110 and C5-INV113) do not fit 20% on the whole net:
- C5-INV110 fits mixed-rate VAT (5% de minimis this month, 20% on the corrected period);
- C5-INV113 (VAT −£20.02) fits no rate.
Filed separately as `SEAT_FINDING_AN_SME_CATCH_UP_BILLS_VAT_FITS_NO_RATE_2026-11-13.md`.

Not changed: `company/billing/invoice.py`'s text invoice prints no catch-up line at all. It has no
caller on a published surface, so it is out of this item's scope.
