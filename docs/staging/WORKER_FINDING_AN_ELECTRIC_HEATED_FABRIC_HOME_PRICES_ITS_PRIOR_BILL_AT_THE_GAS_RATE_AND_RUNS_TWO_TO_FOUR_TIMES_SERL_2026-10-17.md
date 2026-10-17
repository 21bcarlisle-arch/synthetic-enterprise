**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape`
**Knowledge:** what-a-house-does-to-its-energy

# An electric-heated fabric home uses two to four times SERL's level, and its prior-year bill is priced at the gas rate (2026-10-17)

**Fate (2026-10-17):** ATOM -- a world build for `W2_30`. **Not before the 2026-10-19 publish.**
Found on draw `the-fabric-homes-summer-swing-against-published-heating-shapes`. The reading is in
`WORKER_FINDING_W2_36_THEFT_NOW_ARISES_AT_A_PREMISE_AND_AT_THE_IAS_OWN_VOLUME_IT_LOOKS_LIKE_A_VOID_2026-10-16.md`,
in the section "GAP 1 read".

## The defect

On the published run (`78f77c34e`), fabric-path storage homes with a whole calendar year use
19.6 kWh/day (2022) and 42.3 (2023) at the median. SERL's storage-radiator homes (figshare 25472560
v2, Figure_46 / Figure_13) use 12.5 and 11.9, with p75 of 17.5 and 16.7. The direct-electric homes
use 29 against SERL's 10.6. Under published heating seasons, a higher level gives a steeper
winter-to-summer swing. So these homes swing 4–15 (DJ/JJA) where SERL supports up to about 3.8, and
they carry 63% of the theft screen's occupied-home false positives.

## The candidate cause, read in the code (not yet tested)

`simulation/fabric_demand_path.build_fabric_series` prices last year's heating for the prebound
constraint as `prior_kwh × REFERENCE_UNIT_PRICE_P_PER_KWH / 100`. The constant is 4.0 p/kWh and
its docstring says "pre-crisis domestic gas unit rate". For an electric-heated home, `prior_kwh` is
its whole electricity (`electricity_total_kwh`), but it is still priced at the gas rate. A 26 MWh
storage home is therefore billed £1,040 against the £1,200 affordability reference. Its bill
pressure is zero, so it heats to full comfort. That is the SAP-theoretical demand, which is where
the prebound gap is largest.

Other explanations the evidence allows, not yet ranked by measurement:
- the fabric heat demand of electric-heated dwellings is itself too high (EPC E–F detached homes
  dominate the ten);
- storage is modelled as direct-acting (the 2026-10-15 storage-heater finding). This moves the time
  of day more than the monthly kWh;
- SERL's electric-heated sample (n 120 / 160) under-represents large all-electric homes.

## Pre-registration (written before any arm is run)

**The one-variable arm:** price an electric-heated home's prior-year bill at an electricity unit
rate, and leave everything else alone. The rate must be read from the knowledge layer at build
time. No electricity reference rate is held today, so that is a GAP the build's K8 page fills
first. Nothing else changes, including the 0.35 response and the £1,200 reference.

- **P1.** The fabric storage and direct-electric homes' 2022 median falls from 19.6 and 29 kWh/day
  to between 12 and 22. The upper bound is set by the response's 0.45 cap on comfort hours lost and
  its 3.5 °C setpoint floor.
- **P2.** Of the ten flaggers, the median DJ/JJA falls from 4.9 to between 3.0 and 4.5.
  PROS-2017-0336 stays above 8, because its excess is shape as well as level.
- **P3.** Gas-heated fabric homes do not move: their annual level and their DJ/JJA of 1.16 stay
  within ±1%.
- **P4.** The theft screen's occupied own-reads flags under 0.65
  (`tools/theft_void_screen_probe --occupied-run`) fall from 1,796 to between 900 and 1,500 per
  10,000 premise-years. The empty-period row stays at 0.

*Refutation.* If P1 fails low (under 12), the response is now too strong for electric homes. That
is a 0.35 coefficient tuned on gas, and it is filed rather than adjusted. If P1 fails high (over
22), the gas-rate price is not the main cause, and dwelling heat demand is next. If P3 fails, the
arm has touched more than one variable.
