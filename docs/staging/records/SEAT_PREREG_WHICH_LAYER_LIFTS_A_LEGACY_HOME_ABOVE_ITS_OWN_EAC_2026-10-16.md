**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: which layer of the legacy demand path lifts a home above its own EAC

Written 2026-10-16T14:47Z, before any layer was integrated. Claim
`legacy-pc1-homes-use-a-fifth-more-than-their-own-eac`, from
`WORKER_FINDING_D48_ELECTRICITYS_PRE_2020_UNDER_BILL_IS_ONE_UNREAD_EV_HOME_BILLED_ON_THE_TDCV_FALLBACK_2026-10-16.md` §1.
This file is not edited after the measurement.

## What was read before predicting (code only, no number from a run)

`run_phase2b._weather_adjusted_shape_fn` builds a legacy home's electricity in this order:

1. `eac_scaled_shape_fn(GAD, customer["eac_kwh"])`: integral = EAC by construction.
2. `build_demand_shape`: + HDD heating (electric_storage 3.0, heat_pump 1.2 kWh/DD), + CDD cooling
   (0.5 kWh/DD, every home), x occupancy shape, x occupancy VOLUME factor, solar offset.
3. x `epc_consumption_multiplier` (A/B 0.75, C 1.00, D 1.25, E 1.55, F 1.85, G 2.20), applied to the
   whole electricity shape of every home, gas-heated or not, and centred on band C, not on the stock.
4. + ASHP 5,500 kWh/yr if a heat pump; + EV 2,143 kWh/yr if an EV.

## Predictions

| | Prediction |
|---|---|
| P1 | Layer 1 integrates to the EAC within +-0.5% in every calendar year (the scaler works). |
| P2 | The largest single lift is the EPC multiplier (layer 3). Its book mean is >= 1.12, because the band is centred on C while the English stock mean of these multipliers is about 1.17. |
| P3 | The occupancy volume factor's book mean is within +-3% of 1 (it is centred per cut-set by design). |
| P4 | CDD cooling adds under 1%; HDD electric heating adds under 3% book-wide (few storage-heated homes). |
| P5 | EV + ASHP together add under 5% book-wide. |
| P6 | Removing the EPC layer alone brings the book's integral/EAC within +-5% of 1.0. |

A refuted P2 means the fix named in the finding is wrong, and the finding will say so.
