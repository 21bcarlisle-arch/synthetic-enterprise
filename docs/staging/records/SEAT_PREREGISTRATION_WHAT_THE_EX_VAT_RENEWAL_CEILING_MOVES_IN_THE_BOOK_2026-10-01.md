**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration: what the ex-VAT renewal ceiling moves in the book

Claim `ceiling-the-renewal-strike-at-the-ex-vat-cap`. Filed before the measurement runs.

**The change.** `company/pricing/renewal_rate_chain.py` read `cap_ceiling` once, from
`get_cap_unit_rate_for_date`. That figure is inc-VAT. The chain's strike is ex-VAT. One site feeds
both writer 4's clamp and the value arm's `max_offered_rate_gbp_per_mwh`, so one change fixes both.
The ceiling becomes `cap / (1 + VAT_RATE_DOMESTIC)`, with the rate taken from
`company/pricing/tariff_comparison`. `simulation/svt_product.py` is not touched in this run.

**The measurement.** The same default world and the same script as
`SEAT_FINDING_THE_28_ACCOUNTS_ABOVE_THE_CAP_ARE_EX_VAT_STRIKES_CEILINGED_AT_THE_INC_VAT_CAP_2026-10-01.md`
(`/var/tmp/se-dd-books-rate-sold/measure28.py`). It runs once, on origin/main `68e4fb4bf` with this
change applied. The comparison is the rows recorded before the change (`rows28.json`).

**H1 (predicted).** No account's first-month sold rate is above the company's ex-VAT cap by more than
0.1%: **0 of N**, where the baseline was 28 of 120.
- The 24 strikes that were clamped to the inc-VAT cap now sit at the ex-VAT cap. Their sold-rate ÷
  inc-VAT cap ratio is 1/1.05 = 0.9524 ± 0.0005.
- The 4 strikes that sat between the two caps are clamped to the ex-VAT cap as well.

**Refuted if:** any priced account still sits above the ex-VAT cap. That would mean another writer
puts an inc-VAT rate into the strike: the world's SVT segment, or a path that does not go through
writer 4.

**Secondary predictions. These are weaker, because the change moves renewal prices and with them
churn.**
- The 88 below the ex-VAT cap keep their first-month rate, within 0.01 £/MWh. A first term is struck
  before any renewal, so the change cannot reach it. *Correction risk: the value arm also prices
  first terms if any sit inside `renewal_rate_chain`. If more than 5 of the 88 move, this is
  refuted, and the chain also reaches first terms.*
- The account count N stays 120 ± 3. Acquisition does not read the renewal ceiling.

**What done means.** The clamp and the arm both use the ex-VAT ceiling. A control fails if either one
reverts to the inc-VAT ceiling. This measurement is recorded against H1.
