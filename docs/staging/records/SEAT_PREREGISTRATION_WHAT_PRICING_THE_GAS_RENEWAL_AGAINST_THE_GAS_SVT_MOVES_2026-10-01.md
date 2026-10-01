**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what pricing the gas renewal against the gas SVT moves

Claim `price-the-gas-renewal-against-the-gas-svt`. Filed before either run. The parent is
`SEAT_FINDING_THE_SWITCHING_REFERENCE_IS_ON_ONE_VAT_BASIS_AND_GAS_RENEWALS_ARE_PRICED_AGAINST_THE_ELECTRICITY_SVT_2026-10-01.md`.

The duplicate-work note at draw time named this same id as "already held". It was the draw's own
write: no other seat or `surgical_land` process carried it.

## The change

`customer_events._price_differential_vs_market`, `_reference_level_gbp_per_mwh`,
`_market_reference_gbp_per_mwh` and `_svt_position` take a required keyword `commodity`.
`tools/run_price_ladder._svt_position_pct`, `run_phase2b._build_churn_basis_risk` and
`tools/couple_value_based_pricing.belief_versus_truth` pass the leg's own fuel. A gas leg reads
`svt_rates.get_svt_gas_rate_charged_to_household_gbp_per_mwh`. An unknown fuel is refused by name.

**No default.** A default of `"electricity"` is how this defect was built: the function had no fuel
and silently answered for one.

**A gas leg has no rival.** `competitor_reference` is anchored on the electricity cap, and its cost
floor is the electricity policy and network stack. Feeding it a gas leg would chase a gas offer
down an electricity anchor. Nothing in the knowledge layer establishes how a gas rival defends, so
a gas leg's reference is the published gas default tariff, with no chase. That is an explicit gap,
not a model.

## The numbers at the real inputs, printed before the run

The six gas renewals in the parent's run, with each offer's VAT gross-up:

| date | offer ex-VAT | gas SVT | elec SVT | new diff | multiplier then → now |
|---|---|---|---|---|---|
| 2017-01-13 | 26.84 | 28.0 | 140.0 | +0.007 | 0.2273 → 1.044 |
| 2017-02-24 | 29.87 | 28.0 | 140.0 | +0.120 | 0.2273 → 2.234 |
| 2019-02-24 | 33.65 | 37.3 | 165.2 | −0.053 | 0.2273 → 0.736 |
| 2019-02-26 | 33.58 | 37.3 | 165.2 | −0.055 | 0.2273 → 0.729 |
| 2019-06-22 | 22.80 | 41.4 | 185.6 | −0.422 | 0.2273 → 0.2273 |
| 2021-06-21 | 31.81 | 33.4 | 189.5 | 0.000 | 0.2273 → 1.000 |

These multipliers are before the household's own `price_sensitivity` weight, which scales the
differential.

## Predictions, one world, base vs base+change, both from one commit

- **G1.** Every gas renewal's `price_differential_vs_svt` lies in [−0.45, +0.15]. None lies below
  −0.60.
- **G2.** Every gas renewal's `market_reference_gbp_per_mwh` equals the gas charged SVT on its date.
- **G3.** Gas realized churn probability rises on at least 4 of the 6 gas renewals and falls on none
  that was not already saturated. The mean rises by **+5% to +60%**. That is a wide band, on
  purpose: the parent measured that only about 6.5% of a multiplier move reached the probability,
  and that was over moves 20 times smaller than these.
- **G4.** The gas churned count goes from 3 to 3 or 4. With six rolls, no change is evidence of
  nothing.
- **G5.** If no gas roll flips, all 101 electricity renewal events are identical in both runs. This
  is the one-variable control: the rival ledger still observes the same struck rates, and the
  electricity reference has not moved.
- **G6.** `rate_vs_svt_pct` in `churn_basis_risk` equals `100 × price_differential_vs_svt` for every
  row that has both. That holds for gas as well as electricity.

## Found while reading, not changed here

`run_phase2b` feeds **every** decision leg's struck rate into the one
`CompanyPositionLedger`, gas included. So the rival's electricity position is the mean of
electricity rates of about £150/MWh and gas rates of about £30/MWh. That drags it down, and
the rival chases electricity offers further than the company's electricity price would justify.
Fixing it would move electricity churn too, which would make it a second variable in this run. It
is handed on separately.
