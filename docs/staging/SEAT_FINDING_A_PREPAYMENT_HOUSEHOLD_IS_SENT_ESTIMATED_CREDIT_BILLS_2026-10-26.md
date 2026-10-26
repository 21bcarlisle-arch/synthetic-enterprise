**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A prepayment household is sent estimated credit bills

Part of defect 1 of the director's Explore steer. Measured on the published 4ae8da9b0f book.

## What is wrong

- **100** households pay by prepayment (a `payment_received` with method `prepayment`).
- **88 of 100** are also sent bills on an estimated read (`read_type` E).
- **3 of 100** carry an outstanding balance on a bill.

A prepayment customer pays at the meter before use. They get no monthly credit bill to pay, so they
cannot get an estimated one. Any debt they carry is recovered at the meter, not shown as "£42.73 to
pay". SYN-2016-476 paid by prepayment from its first payment in Nov 2016 and was billed like a
credit customer for nine years.

## Root cause

The payment method is a ledger attribute. Billing runs the same monthly credit cycle for every
account, so prepayment is a label on the payment and nothing about the bill changes. Class: **units
pass and the joins fail**.

## What catches it now

`_common_failures` in `tools/generate_explore_cast.py` keeps any household that "pays by prepayment
yet is sent estimated credit bills" out of every Explore slot.

## What closes it

Billing must treat a prepayment account as prepayment: vend and statement, not credit bills and
estimates. Write the knowledge page first (K8): what SLC 28 and published practice say a
prepayment statement holds.
