**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system

# The supply fact is drawn, but the gas register still follows the boiler, and a sixth of gas boilers have no gas supply

## What was measured

Measured on the production path (`net_new_acquisition.STOCK_FROM_FITTED_JOINT = True`, so
`draw_premise_from_joint`), with 6,000 premises, seed 42, as_of 2023-06-01:

| `has_mains_gas_supply` | individual gas boiler | share of homes |
|---|---|---:|
| True | yes | 75.4% |
| True | no | 7.6% |
| **False** | **yes** | **15.3%** |
| False | no | 1.7% |

The supply flag's own marginal is right: 17.0% have no supply, against DESNZ's published 16%
(2023, GB, which DESNZ says is an underestimate) and NEED's raw 19.1% (a ceiling). That is now
held by `tests/simulation/test_the_mains_gas_marginal_recovers_the_published_off_grid_share.py`.
The supply flag reaches nothing, though. `DrawnPremise.commodity`
(`simulation/premise_population.py`) picks the gas register from `heating_system`. So the
direction this atom set out to reverse, supply inferred from the system, is still the direction
the world bills on.

## Why it cannot be fixed by conditioning heating on supply alone

`published_heating_weights()` drops oil, LPG and district heat (5.2%) and renormalises what is
left. That puts gas boilers at **90.7%** of homes, above the **83%** supply share. If a gas boiler
required a supply, both marginals could not hold. The ruling for this atom says a shift in the
heating marginals is a fidelity decision taken blind to P&L, not a side effect. So this is filed
and not absorbed.

Some of the 15.3% is real:

- NEED's "no supply" includes meters it could not match to an address;
- it includes connected homes using under 1,000 kWh a year;
- EHS's 86% "gas-fired" includes communal gas.

None of those is an individual combi or system boiler with no gas meter. The real share of that
combination is not established anywhere this repo holds.

## Proposal

1. **Knowledge first.** Find the published conditional: EHS main heating fuel by gas-grid
   connection (the EHS physical survey records both), or the census 2021 central-heating type
   cross-tabulated against DESNZ's meter-based off-grid share at LSOA level. Until one is found,
   P(individual gas boiler | no individual gas meter) is a named `None`, not a guess.
   *Done 2026-10-07, same day. Correction to "not established anywhere" above: EHS 2017-18
   Annex Table 3.5 publishes main fuel by gas-meter presence from the physical survey. 0.72% of
   gas-fired homes have no meter, and its note 3 says those are LPG or bottled gas. So a mains-gas
   boiler with no gas supply is **0 by measurement**, against the world's 15.3%. With oil and
   communal heat restored, the published stock is consistent: gas-fired 83.6% at DESNZ's 16%
   off-gas, electrical 9.3%, oil 4.4%, communal 2.1%, solid fuel 0.6%. The conditionals table and
   the pre-registered joint are in
   `docs/market_research/mains_gas_is_a_meter_fact_not_a_grid_fact_need_2026.md`. Step 2 is
   now a build against a published joint, not a fidelity judgement waiting for a number.*
2. **Then build** heating conditional on supply. Restore oil/LPG and district heat as drawable,
   non-billable heating so the renormalisation stops inflating the gas share. Pre-register what
   it moves first: the share of the book on a gas register falls by up to about 15 points, which
   moves every gas P&L figure. Decided blind to those figures.
3. `commodity` then reads the supply flag. The test
   `test_the_meter_fact_is_not_folded_into_the_heating_system` stays as it is: it refuses a
   FOLD, and conditioning is not a fold.

## Level

W2_20 is recorded at **L1**: the attribute is built and on the production path, and its
marginal is held against the published share. L2 waits on step 2. Until the supply reaches the
register, "drawn, not inferred" is true of the attribute and false of the bill.

## Step 2 is bigger than a heating-weight swap (worker, 2026-10-07)

Read on origin's base before building. Conditioning the draw is the smallest part. The world has
nowhere to put the restored stock:

- **No oil, LPG or solid-fuel system exists.** `HeatingSystem` (`simulation/household.py`) has
  `DISTRICT_HEAT` and `NONE`, and nothing for a home heated by a fuel no supplier meters.
- **`DISTRICT_HEAT` is billed on electricity at 1:1.** `fabric_physics` returns `heat_kwh` as
  fuel, and `premise_trace` sets `heating_commodity = "electricity"` for anything not gas-heated.
  So drawing communal heat today would put a flat's heat on its electricity meter, which is the
  same error as the 15.3% with the fuel changed.
- The interim of drawing off-gas homes as electric only (no new system) puts ~16% of homes on
  electric heat against the published 9.3%. It swaps one wrong bill for another, so it is not
  taken.

So the build is: (a) a heating system whose heat reaches **no** register (oil, LPG, solid fuel,
communal), with fabric tables and the trace's heat and DHW legs reading it as unmetered;
(b) heating drawn from EHS AT3.5's P(fuel | meter) given `has_mains_gas_supply`; (c) `commodity`
reads the supply flag. Then (d) the value arms get re-taken, because the world digest moves.

**Pre-registered, before any measurement (n=6,000, seed 42, as_of 2023-06-01, production path):**

| quantity | today | predicted after (a)-(c) |
|---|---:|---:|
| homes with a gas boiler and no supply | 15.3% | 0.0% exactly |
| homes on a gas register | 90.7% | 81.5-84.5% (0.987 x 83%, plus nothing for LPG) |
| homes on electric heat | ~8.4% | 8.5-10.5% |
| homes whose heat reaches no register | 0% | 6.0-8.0% |
| `has_mains_gas_supply` marginal | 17.0% | 17.0%, unchanged (a different substream) |

If the gas-register share lands outside 81.5-84.5, the prediction failed and the cause gets
named before anything is tuned.
