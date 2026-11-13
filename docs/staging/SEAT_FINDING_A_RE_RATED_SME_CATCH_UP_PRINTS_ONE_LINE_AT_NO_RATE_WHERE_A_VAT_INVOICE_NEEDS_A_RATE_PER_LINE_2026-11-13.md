**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A re-rated SME catch-up prints as one line with no rate, but a VAT invoice needs a rate on every line (2026-11-13)

K8 page: `docs/market_research/back_billing_and_liability.md` §15, "What a business VAT invoice must
show" (2026-11-13). It was written before any build and closes that section's GAP from c158fe03c.

## The rule (read in the primary, VAT Notice 700, updated 25 June 2026)

- §16.3.1: a VAT invoice shows, "for each description, the quantity of the goods or the extent of
  the services," "the rate of VAT, and the amount payable excluding VAT". It also shows one total,
  "the total amount of VAT chargeable". **No total per rate is required.** The per-rate totals
  (§16.6.1, §16.6.2) are for simplified and retailers' invoices.
- §18.2.3 and §18.2.4: a credit or debit note shows "the rate and amount of VAT credited" (or
  debited) and the number and date of the original invoice or invoices.
- §18.2.5: "The rate of VAT to be used for a credit or debit note is the one which was in force"
  "at the time of the tax point of the original supply."

## What our bill does

A catch-up prints as one description, `catchup_adjustment_gbp`, and its VAT as one figure,
`catchup_vat_gbp`. Since c158fe03c the page splits the VAT line into this month's part and the
catch-up's part. That split is by period. The rule asks for a split by rate.

For a domestic run, and for an SME run whose months were all billed and are all true at one rate,
the catch-up has one rate. Printing that rate beside the line meets §16.3.1, and the page does not
print it yet. For an SME run whose estimate crossed the de minimis, such as C5-INV113, the catch-up
is a credit at 20% for the estimated August (VAT -£31.50) and a debit at 5% for the August that was
read (VAT +£5.62). One line showing -£25.88 VAT on -£45.02 is at no rate. It is not a valid VAT
invoice or credit note line for a VAT-registered business customer.

## Pre-registration (written before the count below was run)

Question: on the shared tree's current ledger, how many SME bills carry a catch-up whose VAT fits
neither 5% nor 20% of its line (to within 1p per corrected month)?
Prediction: between 1 and 10. Two are known (C5/110 and C5/113). Re-rating needs an estimate
on one side of 33 kWh/day (electricity) or 145 kWh/day (gas) and the read on the other, and most
SME accounts sit well away from the line.

## Result

Committed ledger `docs/state/billing_ledger.json` (twin last written in e816040ce8; 53,921 invoices,
1,302 customers). Bills carrying `catchup_vat_gbp`: 6,589 domestic and **4 SME**. Bills whose catch-up
VAT fits neither 5% nor 20% of its line: **1**. It is C5, electricity, period ending 2016-09-30,
-£25.88 on -£45.02, which is C5-INV113. No domestic bill fails. **The prediction held**, at its low
end: 1 is inside 1-10. C5/110 now fits a single rate on this ledger. The surface is one bill in this
book. It grows with the SME share of the book and with how many SME estimates cross the de minimis
line.

## The build this asks for (not done this turn)

The catch-up carries one entry per rate, each with its own net, VAT and rate:
`catchup_lines_by_rate: [{rate, net_gbp, vat_gbp}]`. Each entry sums the month-by-month
differences at that rate: the billed side at the billed rate, the true side at the true rate. The
existing `catchup_adjustment_gbp` and `catchup_vat_gbp` stay as the sums of those entries, so
every current reader is unchanged. The page prints one catch-up row per rate, with its rate. The
bill also needs the original invoice number or numbers the correction relates to (§18.2.3). The
ledger already holds `catchup_period_start` and `catchup_period_end`, so this is a print change.
The control is C5-INV113: two rows, -£157.50-ish at 20% and +£112.4-ish at 5%. Exact figures come
from the build's own printed table.

**Reverse:** delete this file once `catchup_lines_by_rate` is printed and C5-INV113's door test
reads a rate on every catch-up row.
