**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration: where the unattributed 12% of the ex-VAT standing-charge run comes from

_Written 2026-10-01 at 16:59, before either arm returned. Arms: `/var/tmp/se-sc-attr/measure.py`, ARM=old then ARM=new, in series, on base `2d3b87a6b`._

Claim `attribute-the-renewal-feedback-on-the-ex-vat-standing-charge`.

Reading done BEFORE the run (not a measurement):
- The default world runs `CURRENT_POLICY.renewal_margin_arm == "flat_rules"`, and
  `value_based_renewal.renewal_margin_uplift` returns `MarginArmUplift(0.0)` for FLAT_RULES before
  calling `observed_account_state`. So `_observed_standing_charge_gbp` is never reached in the default
  world, and the directed freeze is a no-op by construction.
- Both writers that stamp a standing charge (`hedged_settlement`, `gas_settlement`) add it into
  `revenue_gbp` 1:1. No later writer reassigns record `revenue_gbp`.

Predictions:
- Q0. `observed_account_state` call count = 0 in both arms (the freeze is equivalent, not untested).
- Q1. Unit revenue (revenue_gbp − standing_charge_gbp − gas_standing_charge_gbp) differs between
  arms by +£1,356 ± £5 in total, and consumption_kwh is identical per account to 1e-6.
- Q2. I do not know where the unit-revenue delta sits. Stated in advance: if it concentrates in
  terms that START after the first divergence of any upstream state, it is a feedback; if it is
  spread across every term from 2016 on, it is an accounting effect in the per-record arithmetic,
  not behaviour.
