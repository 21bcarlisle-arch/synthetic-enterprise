**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A third of households go more than a year on estimates without the read duty firing

Defect 4 of the director's Explore steer. Measured on the published 4ae8da9b0f book.

## What is wrong

- **250 of 752** households have at least one bill dated more than 365 days after that fuel's last
  actual read.
- The home page says the supplier "instructs a meter visit when a year passes on estimates, as the
  read duty requires (SLC 21B.4)".
- The published example SYN-2016-587 had 33 estimated bills in a row, with no read from 30 Apr 2021 to
  29 Feb 2024.

## Open question

The run instructs visits (`company/billing/read_duty_register`, `company/policy/decision_policy.py:238`).
So the question is whether the visit is instructed and then fails to produce a read, or is never
instructed for these accounts. That decides whether the capability claim or the record is wrong.
Re-measure it on a run that carries the register.

## Second question, from the same example

SYN-2016-587's catch-up after 33 months of estimates was £7.03. That is too exact. Check whether the
estimate is fed the true consumption. If it is, it breaks the epistemic wall.

## What catches it now

The estimate-trap slot ranks only runs within the read-duty year. This run shows PROS-2017-0264: 12
gas estimates since joining, then a read and a £45.43 credit.
