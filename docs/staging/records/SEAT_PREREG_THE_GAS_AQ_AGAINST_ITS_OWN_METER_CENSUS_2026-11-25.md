**Severity:** LATENT · **Lane:** W3_industry_systems · **Item:** `a-gas-premise-carries-the-aq-its-own-meter-makes`

# Pre-registration: how many gas premises carry a registry AQ that is not their own meter's (25 Nov 2026)

Filed before the census is run.

**What is measured.** Each gas premise in the book is drawn an AQ (`customer["aq_kwh"]`). The world's
demand for that premise is `aq_kwh x gas_eac_multiplier_for_date(cid, term_start)`
(`simulation/run_phase2b.py`, the gas term). The multiplier is 0.12 for a heat-pump home
(`GAS_HEAT_PUMP_RESIDUAL_FRACTION`), the EPC multiplier for a gas-heated home, and 1.0 otherwise. Its
level is the AQ, and only the seasonal shape moves (`heating_fraction_for`). So the meter's own
weather-normal annual use, which is what Xoserve's AQ estimates, is `aq_kwh x` the mean multiplier over
the year before acquisition. The registry AQ the company is handed is the unmultiplied `aq_kwh`.

**Denominator.** Every drawn gas premise with a household on the register, graded per premise. This
uses no billed days, so the voids and missing-truth rows in the finding's crude 49/422 census cannot
enter it.

**Predictions.**
1. PROS-2021-0100 is a heat-pump home with ratio drawn/own = 1/0.12 = 8.33. The billed 9.48 is higher
   because the five estimated months are winter-shaped on the class profile.
2. Every premise over 3x is a heat-pump home. The EPC multiplier band stays within 0.6 to 1.6, so no
   EPC-only premise crosses 3x.
3. I cannot predict the count of heat-pump gas homes. I expect it in the tens out of about 420, not the
   hundreds.

## Result (run after the predictions above, same day)

Script: `/tmp/aqprobe/census.py` (the run's own `HouseholdDemandRegister(CUSTOMERS,
drawn_households=live_drawn_households())`, then the mean multiplier over the 365 days before
`max(acquisition, run start + 365)`). 503 gas premises, all domestic, all with a household.

| Own use / registry AQ | Premises | Heat pump |
|---|---|---|
| < 0.34 | 3 | 3 |
| 0.34 to 0.8 | 14 | 0 |
| 0.8 to 1.25 | 247 | 0 |
| 1.25 to 2.2 | 239 | 0 |

- **Prediction 1 held.** PROS-2021-0100 is a heat-pump home with multiplier 0.12, so the registry is
  8.33x its meter.
- **Prediction 2 held.** All 3 premises over 3x are heat-pump homes. The non-heat-pump range is 0.34 to
  2.2. That is wider than the 0.6 to 1.6 I predicted, but none crosses 3x.
- **Prediction 3 was wrong.** The count over 3x is 3, not tens.
- **Not predicted, and the larger class:** 239 premises (48%) carry a registry AQ *below* their own
  use, and 36 of them by 1.5x or more. The estimator's hold under-bills these households until its
  own reads take over. The over-3x invariant does not see that direction.

The census is per premise and uses no billed days, so it is free of the void contamination in the
finding's 49/422. Built from it: `simulation/run_phase2b.register_gas_premises_on_their_own_reads`
(knowledge: `docs/market_research/a_gas_meter_points_aq_is_made_from_its_own_reads.md`). Exit, not yet
measured: PROS-2021-0100 leaves INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER on the next fresh book,
and the exception is re-based downward to the count its reason covers.
