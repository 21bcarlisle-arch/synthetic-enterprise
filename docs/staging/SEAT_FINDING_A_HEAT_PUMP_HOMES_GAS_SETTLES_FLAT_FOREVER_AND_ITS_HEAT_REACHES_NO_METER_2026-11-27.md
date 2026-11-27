**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape`
**Knowledge:** none yet -- what a gas meter left after a heat pump draws (hob only, or capped) is NOT ESTABLISHED here; a knowledge page comes before the build (K8)

# A heat-pump home's gas settles flat forever, and the heat it stopped burning reaches no meter (2026-11-27)

**What the book shows.** On the 2100f84f85 book, INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR refused the publish
with 4 breaches against a ceiling of 1. Two of the four legs are new: PROS-2019-0208g and PROS-2021-0396g. Each
moves with the weather until one April term (2021 for 0208g, 2023 for 0396g). From that term on, every measured
month is exactly 4.50 kWh a day: 135.1 kWh in a 30-day month, 139.5 in a 31-day month, 126.0 in a February. January
reads the same as July. Those two legs hold 38 of the book's 53 repeats. The rest of the book repeats at about
0.4%, against a bound of 1%.

**Route (read in code, not run).** After a heat pump, `HouseholdDemandRegister.gas_eac_multiplier_for_date` returns
`GAS_HEAT_PUMP_RESIDUAL_FRACTION` (0.12). EPC multipliers are 0.75 or more, so 0.12 is the only route to a cut that
deep. The term's `aq_kwh` drops to about 1,640. `SeasonalGasSplit.heating_fraction_for` keeps the trace's flat base
whole in kWh, so it returns `max(0, 1 - flat/aq)` = 0 once that base exceeds the shrunken AQ.
`resi_daily_gas_kwh` then settles `aq/365` every day, on an AQ that does not move.

**Two defects, not one.**
1. *The residual has no shape.* Gas left on a hob still has cooking's season (the trace already models one, see
   `premise_trace` "cooking and laundry have a SEASON") and still moves with occupancy. The draw is constant to the
   tenth of a kWh, so the invariant fires. This is the same missing year-to-year term as SYN-2016-206g's summer, the gas
   half of N17. Here it covers the whole year.
2. *Energy is not conserved across the fuels.* Neither PROS leg's electricity rises after the cut. PROS-2019-0208 is
   about 2,750 kWh/yr in both 2020 and 2021, and `eac_multiplier_for_date`'s `ashp_annual_kwh` (5,500) does not reach
   it. Those legs settle on another path (the fabric trace or the own-reads registry), which never reads the
   multiplier. So the space heat the gas stopped carrying reaches no meter. That flatters any carbon or cost figure
   made from these homes (M3), and the company could read it as a household that simply stopped heating.

**Not established.** Whether `heat_pump_installed` is the life event on these two households: the run output's
`life_event_history` was not read for them, and the inference rests on the 0.12 fingerprint. Also not known: how many
other heat-pump homes reach electricity through a path that skips the ASHP uplift. A census over the world's
heat-pump households is the first step.

**Smallest next step.** (a) A census: for every household with `heat_pump_installed`, its gas and electricity
annual kWh either side of the event. Defect 2 is established only if electricity stays flat across most of them.
(b) A knowledge page: what a post-heat-pump gas supply actually draws (a hob-only meter or a capped supply) and with
what season. (c) Only then, the world change.

**Held meanwhile by** the re-filed exception in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`
(INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR, `max_breached: 4`, recheck_by 2026-12-11). That exception unblocks the
2100f84f85 book's publish and does not repair anything.
