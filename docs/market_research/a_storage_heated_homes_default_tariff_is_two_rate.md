**Knowledge:** price-cap

# A storage-heated home's default tariff is two-rate, because its meter is

K8 page for E2 (a) of
`docs/staging/SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`,
and for ruling step 3's storage-heating cause
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).
Written 30 Oct 2026, before any build. The question: **what tariff, price and bill does a supplier
give a storage-heated home on its default tariff?** What the rules require, what is published, what
is not (GAP), and the choice a build should make.

## What the book does today (measured, 209c3350ab, 30 Oct 2026)

Probe `/var/tmp/e7-probe/count.py`, run from the book's own worktree, population rebuilt at the run's
seed and read through `live_drawn_households`.

- **36 of 560** electricity accounts are drawn `electric_storage` (11 `electric_direct`, 3 air heat pump).
- Every one of their 537 term rows is single-rate: 479 `svt`, 58 `fixed`. No bill prints a second register.
- The world settles each of them on **Profile Class 2**, "Domestic Economy 7"
  (`simulation/run_phase2b.registered_profile_class`), and charges their space heat and most of their
  cylinder's hot water across 00:30-07:30
  (`fabric_physics.storage_charge_kwh`, `premise_trace.storage_dhw_meter_kwh`).

So the same home is a two-rate meter in settlement and a single-rate customer on its bill. The three
E2 (a) summer over-estimates (PROS-2017-0336, PROS-2024-0010, SYN-2016-565) are this home.

## What the rules and the published record establish

**R1. The meter, and so the profile class, is something the supplier holds.** Elexon's profiling page
(read 2026-10-22, `docs/data-sources/profile-class-2.md`): PC2 is "Domestic Economy 7 Customers", the
class follows the meter's switched load, and "Suppliers are responsible for allocating their customers
in the appropriate Profile Class" (BSCP516). The class is the first two digits of the MPAN's top line.
So reading a home's two-rate meter is on the supplier's side of the epistemic wall. Its heating
system is not: the supplier sees the meter, never the storage heater.

**R2. A default tariff follows the household's meter type (SLC 1, 2017).** Already quoted in
`a_tou_tariff_needs_the_households_choice_not_its_meter.md` rule 2: a rollover tariff must be "similar
in nature to the customer's current tariff, taking into account ... meter type", and the Relevant Fixed
Term Default Tariff must match "their current Relevant Meter Type". That page's choice ("a
default-tariff term is single-rate whatever the meter") was made for a **smart single-rate** meter that
could record time bands. It did not consider a meter whose registration is already two-rate. For an
E7 meter, rule 2 points the other way: the similar default is the E7 one.

**R3. The cap grades an E7 tariff against the multi-register benchmark at a fixed split.** SLC 28AD.4
and 28AD.36(a), quoted in `docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`:
a Multi-Register Tariff is assessed on the multi-register benchmark, and for "each Economy 7 Tariff,
off-peak and peak consumption levels of 42% and 58%" are the Assumed Consumption Split. 28AD.2 caps the
**aggregate** charge. So the cap binds `0.58 x day + 0.42 x night`, not either rate on its own. The
multi-register unit rate per cap period, ex-VAT, is in
`docs/domain_artefact_library/regulatory/ofgem_cap_multi_register_unit_rates.json` (Jan-Mar 2019:
14.63p against 15.723p single-rate). That artefact says its multi-register column is not checked
against a published Economy 7 series.

**R4. Under the EPG, suppliers set the individual E7 rates.** GOV.UK, *Energy Price Guarantee: regional
rates, January to March 2023* (fetched 30 Oct 2026): "For customers on multi-register tariffs such as
Economy 7, suppliers have flexibility to apply slightly different discounts to the individual rates
within the tariff ... Each supplier will approach this differently." The page publishes single-rate
figures only.

**R5. Each rate is shown on the bill.** SLC 22A.3 (quoted in the ToU page, item 6): the Unit Rate(s)
are separately identified wherever charges are displayed. An E7 bill prints a day and a night register,
each with its rate. `a_multi_register_meters_bands_add_up_to_its_total.md` already makes the bill's
bands sum to the total.

## What is not established (GAP)

- **G1. The day/night ratio a supplier set, per period, 2016-2025.** The cap fixes the weighted
  aggregate (R3), not the split. One secondary point only: a supplier guide (British Gas, citing Ofgem,
  April 2026) gives a direct-debit average of about 29.73p day and 13.89p night, a ratio of 0.47.
  That is one quarter, after the window, and not a primary source. A build must carry the ratio as a
  stated belief with a range, never a picked point.
- **G2. The E7 SVT before the cap (2016-2018).** No published E7 default-tariff price series has been
  read. DESNZ *Quarterly Energy Prices* Table 2.2.4 is reported to carry Economy 7 unit and fixed
  costs by region, with bills at 4,800 kWh (earlier 5,100 kWh); that is from a search summary of the
  methodology note, not read first-hand. Reading Table 2.2.4 is the next knowledge step.
- **G3. The night window by region and meter.** E7 gives seven off-peak hours set by the meter's time
  switch, and they vary by region and meter. The world charges 00:30-07:30. No regional table has been
  read, so a build would bill the world's own window and say so.
- **G4. How far a storage home's real night share sits from 42%.** Nottingham's trial (in
  `when_an_electrically_heated_homes_water_heater_runs.md`) gives a 53-66% off-peak meter share for
  storage homes, so they sit above the cap's split. Published commentary (Sustainability First,
  2023) argues that this mismatch leaves E7 households overcharged under the cap. Its papers returned
  404 on 30 Oct 2026 and were not read, so no figure is taken from them.
- **G5. E7 meters in homes that are not storage-heated.** As in `profile-class-2.md` G2/G3: absent
  from the world, not measured as zero.

## The choice a build should make

*Built 2026-10-30 except the estimate half of 3:
`docs/staging/SEAT_FINDING_AN_ECONOMY_7_METER_IS_BILLED_ON_ITS_TWO_REGISTERS_2026-10-30.md`.*

1. **The supplier reads the meter, not the heating.** Each electricity account carries its registered
   profile class across the seam (`company/interfaces/sim_interface.py`), as the MPAN's top line would.
   The company never reads `heating_system`.
2. **A PC2 meter's default tariff is an E7 SVT**: a Night register (the world's 00:30-07:30, G3) and a
   Day register for the rest. From 2019 the pair is struck so that `0.58 x day + 0.42 x night` equals the
   period's multi-register cap rate, at a night/day ratio carried as a belief with its range (G1). Before
   2019 it waits on G2, and the code says so rather than inventing an E7 list price. *Corrected 2026-10-30, at the build: before 2019 the pair is struck off the company's
   own single-rate list price at the same 58/42 rule. That invents no E7 list price, and the alternative
   was billing a two-rate meter on one rate for three years. G2, the real pre-cap E7 level, stays open.*
3. **The bill prints both registers**, with their sums adding to the total (R5), and an estimate is
   shaped per register on the published PC2 profile (Elexon's, the same file the world settles on), which a supplier holds.
4. **A fixed term on a PC2 meter** follows the same pair. Whether a household could choose single-rate
   on an E7 meter is a separate GAP and stays out of scope.

**Which way this errs.** The multi-register cap rate sits below the single-rate one (0.93 of it in Jan
2019), and a storage home's night share (G4) sits above 42%. Both lower these households' bills. The
change therefore takes revenue off the book, which is the safe direction (F11). No figure is predicted
here, because the ratio in G1 is a range.

**Prediction for the grade after a build** (written now, before any build): E2 (a)'s three summer
over-estimates leave `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`, because a per-register estimate on
PC2's shape does not carry winter night load into a summer day. The row's other three E2 residuals
(SYN-2016-396g, PROS-2016-0263g, and any direct-electric home) do not move.

## Sources

- Elexon, *Profiling* (elexon.co.uk/bsc/settlement/profiling/), read 2026-10-22, via `docs/data-sources/profile-class-2.md`.
- Ofgem, SLC 28AD and SLC 1 default-tariff modification (2017), via the regulation commons files named above.
- GOV.UK, *Energy Price Guarantee: regional rates, January to March 2023*, fetched 2026-10-30.
- British Gas, *Economy 7 meters explained* (secondary, April 2026 averages), seen in search, not fetched.
- DESNZ, *Domestic energy prices: methodology* (assets.publishing.service.gov.uk), seen in search, not read first-hand.
