**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Year one is no longer blind; its quote and the review it is met by are on different bases

Claim `price-the-opening-dd-at-the-rate-the-supplier-sold-at`. Code `7a119f52c`, pre-registration
and result `records/SEAT_PREREGISTRATION_PB4_THE_OPENING_DD_AT_THE_RATE_SOLD_2026-10-01.md`.

## What moved

The opening DD is now annualised at the unit rate on the leg's first bill, not at the default-tariff
cap. On one world, first renewals went from **4 defined to 31 of 31 in scope**, with 9 shocked
(0.290) against 0.323 at later renewals. Later renewals are byte-identical, so the run is
one-variable. All four rows that had a cap quote before now read a higher rise: the cap had over-set
the opening DD on each one. The hazard swap's stated blocker is gone.

## What is still owed before year one is trusted as a LEVEL

Year one compares two amounts built differently. Later renewals compare a review against a review,
so they are not affected.

- **VAT.** The quote is inc-VAT: the cap path always was, and the rate sold is grossed up to match.
  The amount it is met by is `reviewed_monthly_amount(revenue_gbp × 12)`, and `revenue_gbp` is
  ex-VAT (`simulation/hedged_settlement.py` settles ex-VAT). That alone under-reads a year-one rise by
  about 5 points.
- **Standing charge.** The quote uses `STANDING_CHARGE_RESI_P_PER_DAY` (53p, a 2024 figure) per leg
  across 2016–2025. The bills carry the world's dated standing charge.

The median first-renewal rise is −0.084 against +0.04 later. That is the direction both gaps
predict, but it is not attributed: the size of each gap has not been run. The fix is to put the met
amount on the quote's basis: an inc-VAT `revenue` read, or a door that returns the review of a
VAT-inclusive year. It is the same five-implementations VAT class, so look for the existing VAT
rule before writing one.

## Not changed here, on purpose

`run_phase4c_on_phase2b`'s DD-book caller still opens accounts at the cap: pre-2019 accounts stay
unestimated and post-2019 accounts open high. Passing the rate sold there moves the company's DD
books and the DD mis-setting figures. That is a separate one-variable change and is handed on.
