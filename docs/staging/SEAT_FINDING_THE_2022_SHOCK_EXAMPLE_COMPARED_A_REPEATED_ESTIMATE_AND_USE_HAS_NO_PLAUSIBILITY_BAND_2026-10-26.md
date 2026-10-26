**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The 2022 shock example compared a repeated estimate, and use has no plausibility band

Defect 3 of the director's Explore steer. Measured on the published 4ae8da9b0f book.

## What is wrong

- **194 of the 231** households the shock rule matches compare a pair that includes an estimated bill.
  The one published, PROS-2017-0336, compared 3,128.7 kWh in Jan 2022 with 3,128.6 kWh in Jan 2023.
  **Both** bills are estimates; the steer said only the 2022 one was, and the record shows two.
  Neither was observed, so "the same use" is an estimate repeated.
- **27 of 752** households have a typical use outside the book's 1st-99th percentile for their fuel and
  segment. PROS-2017-0336 uses about 37,500 kWh a year, which is roughly ten times a typical home's
  electricity.
- The gap panel set "Bill of £1,080.02" against billed use. That is a figure set against a figure,
  not a belief set against a truth. It is removed.

## Root cause

- The rule ranked by the size of the rise, with no read-type condition.
- Nothing in the code holds use to a range. Class: **aggregates hide tails**.

## What catches it now

- The shock slot needs actual reads on both bills.
- Every slot needs use within the book's percentile band.
- This run shows PROS-2019-0246: an electricity-only home, £311.08 in Dec 2021 rising to £596.06 in
  Dec 2022, both on actual reads.

## Still open

Why does the estimator copy the year-ago kWh into a crisis-winter bill? Check the estimator in
`company/billing/` against the knowledge page on estimates.
