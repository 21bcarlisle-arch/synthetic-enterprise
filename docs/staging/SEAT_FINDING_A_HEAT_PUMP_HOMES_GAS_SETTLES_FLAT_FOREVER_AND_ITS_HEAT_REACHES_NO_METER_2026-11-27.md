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

## Cause established: one home draws two lives (2026-11-27, on the 601887d76a book)

**Correction to "Not established" and to defect 2's route above.** Both PROS homes do pass through
`heat_pump_installed`, but only on their GAS leg. The electricity household never installs one. The
register was rebuilt at HEAD (no world-code diff from 601887d76a in `simulation/household_demand.py`,
`household.py`, `life_events.py`, `live_population.py`) with `HouseholdDemandRegister(CUSTOMERS,
drawn_households=live_drawn_households())`, the run's own call:

| supply point | its life events (register at seed 42) | gas multiplier 2022-06-01 |
|---|---|---|
| PROS-2019-0208 | illness 2023-09, income_recovery 2024-05, new_baby 2025-06 | 0.75 (EPC) |
| PROS-2019-0208g | job_loss 2018-08, reemployed 2018-12, **heat_pump_installed 2021-01-29**, income_scar_ended 2023-12 | **0.12** |
| PROS-2021-0396 | none | 1.0 |
| PROS-2021-0396g | new_baby 2017-07, **heat_pump_installed 2023-01-02** | 0.12 from the 2023 term |

**The source.** `simulation/household_demand.py:90-94`. `build_household_register` has aliased a gas
leg to its electricity point's `Household` since the August one-property-one-household fix, so
`register["X"] is register["Xg"]`. But `HouseholdDemandRegister.__init__` still calls
`generate_life_events` once per supply-point id, seeded `seed ^ _cid_hash(cid)`. The gas leg therefore
draws its own independent life against the shared dwelling. That is the defect the August docstring
says it repaired ("two sets of babies, divorces and home moves against one dwelling"), repaired for the
dwelling and not for the event stream.

**Defect 2 is this, not a second settlement path.** The heat pump exists only on the gas half, so
`gas_eac_multiplier_for_date` gives 0.12 while `eac_multiplier_for_date` on the electricity id never
adds `ashp_annual_kwh`. It also runs the other way: a heat pump drawn only on the electricity half adds
the ASHP uplift while the gas leg keeps burning its full heating load.

**Census (register at HEAD, 503 gas legs).** 19 gas legs have a heat pump on one side of the home.
None has it on both. 13 are gas-only and 6 electricity-only. Billed after the install in the 601887d76a
book: gas-only PROS-2019-0208g (53 months), PROS-2021-0396g (29), PROS-2023-0089g (11),
SYN-2025-001g (3), PROS-2025-0103g (3); electricity-only PROS-2017-0396g (20), PROS-2024-0345g (8).
The non-heat-pump events (job loss, new baby, illness) also diverge across the two fuels of every
dual-fuel home. Nothing here measures what reads those on a gas leg (for example `income_stress_at_date`).

**Severity stays LATENT.** The exception (`max_breached: 4`, recheck_by 2026-12-11) holds the publish.
But the world is wrong for every dual-fuel home's events, and for carbon on the seven heat-pump legs
billed after the install (M3).

### Pre-registration (written before the fix is built or any run made with it)

Fix under test: draw life events once per HOME, keyed by `household_of(cid)`, and alias the gas leg's
event list to its primary's, exactly as the `Household` is aliased. An orphaned leg keeps its own draw.
Graded on the first published book built with that fix and with no other world change to gas:

- **P1.** PROS-2019-0208g and PROS-2021-0396g leave INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR's
  breach list. Their gas keeps a weather shape after April 2021 and April 2023 (winter months over
  30 kWh/day). Refuted if either still shows 3 or more repeats.
- **P2.** The book's repeat count falls by at least 30 of today's 53. Its share falls under 1%, so the
  book-level breach clears. The invariant breaches at most 2 legs: SYN-2016-206g (a different class,
  summer N17) and possibly PROS-2017-0396g.
- **P3.** PROS-2017-0396g and PROS-2024-0345g gain the 0.12 cut from their first term after the
  electricity-side install. Their gas then settles flat at aq/365, because defect 1 (a residual with no
  season) is untouched by this fix. PROS-2017-0396g may become a NEW repeat breach (20 months after
  install, inside 2018-2019). If it does, that confirms defect 1 is separate and does not refute the fix.
- **P4.** No heat-pump home in the book has its gas fall without its electricity rising, or the
  reverse. On every leg in the census, the sign of the gas change at install is opposite to the sign of
  the electricity change.

Do not narrow the exception before P1-P2 are graded. Do not raise `max_breached` above 4 to absorb P3:
a P3 breach is defect 1, and it is filed here.

## Fix built (2026-11-27): the gas leg's events alias its primary's

`HouseholdDemandRegister.__init__` now draws once per home: a leg whose Household is its primary's
object takes the primary's event list (the same object), and a primary keeps its own seed, so no
electricity point's life changes. An orphaned leg keeps its own draw. Control:
`tests/simulation/test_one_home_draws_one_life_across_its_two_fuels.py` (the pre-fix per-id loop reds it,
starting C2g, C3g, C4g, SYN-2016-001g).

Census at the fix (register at seed 42, `CUSTOMERS` + `live_drawn_households()`): 470 gas legs read
from this roster (the census above counted 503; the difference was not chased). 0 have a heat pump on
one fuel only, against 19 before. 6 have it on both: PROS-2017-0396g, PROS-2018-0169g, PROS-2024-0345g,
SYN-2016-012g, SYN-2016-153g, SYN-2016-457g. Gas multiplier at 2022-06-01: PROS-2019-0208g 0.75 and
PROS-2021-0396g 1.0 (the 0.12 is gone); PROS-2017-0396g 0.12 (P3's direction). P1-P4 are not graded:
that needs the first published book built with this fix.
