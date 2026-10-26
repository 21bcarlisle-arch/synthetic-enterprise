**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A statute-barred write-off lands before six years and repeats monthly

Defect 5 of the director's Explore steer. Measured on the published 4ae8da9b0f book.

## What is wrong

- The published debt example, SYN-2016-356, passes the limitation check. Its last payment was on
  28 Jun 2018 and it was written off as statute-barred on 28 Jun 2024, exactly six years later
  (Limitation Act 1980 s.5, England and Wales).
- Across the book, **24 of the 602** debt-journey households are written off as statute-barred less
  than six years after their last recorded payment.
- SYN-2016-356 is written off three times: on 28 Jun, 28 Jul and 28 Aug 2024. One debt has one
  write-off.

## Caveat

The test reads the ledger's last payment as the last acknowledgement. Section 29 also restarts the
clock on a written acknowledgement, and the record does not carry one. So some of the 24 may be right
on a fact the record lacks. That would make them a GAP, not a pass.

## Where

`company/billing/collections_journey.py:143` (the statute-barred amount) and the desk's write-off
stage.

## What catches it now

The debt slot's check in `tools/generate_explore_cast.py`.
