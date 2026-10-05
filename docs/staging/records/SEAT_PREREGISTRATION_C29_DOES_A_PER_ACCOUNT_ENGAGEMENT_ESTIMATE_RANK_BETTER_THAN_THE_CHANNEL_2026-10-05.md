# Pre-registration — C29: does a per-account engagement estimate rank better than payment channel alone?

*Delivery seat, 2026-10-05, claim `c29-build-a-per-account-engagement-estimate-graded-against-the-world`.
Written BEFORE any measurement against the world's trait. Results go in a separate finding beside this one.*

## What is measured

- **Truth:** `simulation.household_segments.active_renewal_probability_for_customer(household)`, read the
  way `tools/engagement_separation.py` reads it. It is the archetype's probability (0.65 / 0.15 / 0.02)
  times a channel multiplier anchored to Ofgem CIM w6. I know these constants from reading the code. I
  have not looked at any ranking.
- **Baseline:** payment channel alone. Each account gets its channel's book-pooled active-choice rate.
- **Estimate:** an empirical-Bayes beta-binomial. The prior mean is the channel's pooled rate. The prior
  strength is a method-of-moments fit of the between-account spread over the company's own book. Each
  account's data is its own count of anniversaries where it ACTIVELY CHOSE (it started a fixed term, or
  left at the renewal) out of all anniversaries it reached, where the alternative was ROLLING onto the
  default. Every input comes from the company's own tariff record. The truth never enters the fit, so
  the fit cannot overfit to it and needs no held-out split.
- **Score:** Spearman rank correlation with the truth over households on the latest run's book.

## Predictions (real book, latest run output)

- P1. Channel alone has rho with the truth in [-0.05, +0.25]. DD and standard-credit multipliers are
  close (5.6 vs 5.7) and prepayment is lower (3.1). The archetype carries almost all of the spread.
- P2. The estimate has rho of about 0.55, and at least 0.25 above channel alone.
- P3. At least 30% of households will have reached no anniversary at all, so the estimate can only give
  them the channel prior. This caps the lift that can be measured.
- P4. Null arm: shuffle each account's outcomes across accounts within the same channel. The lift then
  collapses to within ±0.10 of zero.
- P5. Planted arm: draw synthetic outcomes from the truth with 5 anniversaries each. The lift is at
  least 0.30.

What would refute the frame: P2 fails with the lift under 0.10. The decision then cannot be made
per-account on engagement from this record, and C29's next candidate is the dunning ladder (#5).
