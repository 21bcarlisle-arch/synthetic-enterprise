**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration (2): which learned writer recovers the standing charge through the unit rate

Written before the instrumented pair ran. The first pair (`/var/tmp/se-sc-attr/`) established
that Δunit revenue = +£1,356.19, that kWh is identical, and that first terms move by exactly
£0.00 while every later term moves. That is the signature of the chain's learned writers, which
apply only at `term_index >= 1`.

- R1. `struck_unit_rate_gbp_per_mwh` (the rate entering the chain) is identical across arms on
  every renewal, to 1e-6. If not, the strike itself reads the standing charge, and the learned
  writers are not the whole story.
- R2. The `components` that differ between arms are only `portfolio_premium`,
  `margin_surcharge` and `profitability_uplift`.
- R3. Portfolio premium carries more than half of the £1,356. The movers are many and small
  (929 keys), which fits a book-wide reading better than a per-loss-maker one. Low confidence.

_Written 2026-10-01 at about 18:00, before the instrumented pair (`/var/tmp/se-sc-attr2/measure.py`) ran. Landed with its result; the result is in `SEAT_FINDING_THE_12_PERCENT_IS_THE_COMPANY_PRICING_ITS_LOWER_MARGIN_BACK_INTO_RENEWAL_UNIT_RATES_2026-10-01.md`._
