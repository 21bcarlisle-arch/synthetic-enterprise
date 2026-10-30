**Knowledge:** household-carbon-and-the-measures-that-save-it

# Every change a household can make: one list for the world and the supplier, prioritised by cost, ease and remaining market

Written 30 Oct 2026 for the director's steer
(`docs/staging/advisor/DIRECTOR_STEER_TIME_IS_VALUE_A_SUPPLIER_CAN_CREATE_AND_THE_WORLD_MUST_FEEL_HASSLE_2026-10-30.md`;
12:22 GMT "Do we have a list of the all changes and investments customers can make to save money and
carbon?", 12:26 GMT "This needs to be prioritised based on costs, ease and remaining market size (IE
existing pentration, and restrictions)").

**What this page is.** It is the index. It replaces nothing. Each row points to the topic page that holds
the evidence. Both sides read it, for different things:
- **The world** reads it for who *can* adopt (applicability, the restrictions) and what drives the
  decision (value, cost, hassle).
- **The supplier** reads it for what to offer, to whom, and in what role. It can only see the households
  the "observe" column says it can see.

**Where the numbers come from.**
- £ and carbon come from §5 of `household_carbon_and_the_measures_that_save_it.md` wherever it has a
  figure, because those figures are sourced per row and on one basis.
- Everything else comes from the advisor's evidence pack
  (`docs/staging/advisor/done/DIRECTOR_EVIDENCE_EVERY_CHANGE_A_HOUSEHOLD_CAN_MAKE_PRIORITISED_2026-10-30.md`),
  which cites a URL beside each claim.
- **[unverified]** is the pack's own tag. It is kept wherever the pack used it, and it means a calibration
  assumption, not evidence. This page adds no number of its own.
- GB-wide counts are built on a 27.8m household base and on English Housing Survey tenure shares applied
  to GB. Both are [unverified] (pack §13, gaps 1-2). Every "remaining addressable" figure inherits that.

---

## 1. What "remaining addressable" and "ease" mean, said before they are used

- **Remaining addressable households** = homes where the measure is *physically and legally possible*
  × (1 − the share that already has it). It applies the restrictions the director named:
  - tenure and landlord or freeholder consent;
  - house type and roof;
  - off-street parking;
  - gas connection;
  - listed or conservation status;
  - what is already installed.

  It is not demand. A household that can, and has not, is not a household that will.
- **Ease, 1 to 5** (5 is easiest), scored by the pack. It combines hassle hours, disruption, the number of
  parties and installer availability. It is ordinal and the pack's judgement. It is not a measurement.
- **Hassle** is household minutes, by C31's classes: T1 shopping, T2 servicing, T3 recovery, T4 routine
  admin and T5 adoption (`docs/design/C31_TIME_AS_A_CURRENCY_DISCOVER_FRAME_2026-10-04.md` §9). It is never
  converted to £ in any score on this page.
- **Observe** says how the supplier can know the household is eligible or has acted:
  - *Account*: it is on the supply record;
  - *HH*: it is visible in half-hourly data;
  - *Ask*: only the household can say;
  - *Register*: an external register (EPC, MCS).

## 2. The ranking (the director's 12:26 ask)

**Scoring formula. It is the pack's §12, published so it can be re-weighted:**

`Score = N_rem × max(NAV, 0) × (Ease / 5)^α`, where:
- `NAV = £/yr + λ·tCO2/yr − Upfront / Life`;
- `N_rem` is remaining addressable households, in millions;
- `λ` = £250/t [unverified], `α` = 1, and asset lives are [unverified].

Ways to re-weight it:
- λ = 0 gives a pure-money view;
- a higher α penalises hassle more;
- an annuity at a household discount rate in place of `Upfront/Life` gives the household-realistic view,
  which punishes capital hard.

Three warnings travel with the table:
- **Behaviour rows need a persistence haircut.** The one GB RCT in the pack (flow temperature) measured
  0.4% against a modelled 8-9%. The pack suggests a haircut of 50% or more [unverified].
- **Enablers are understated.** A smart meter's and a smart charger's value is the tariffs they unlock.
- **Bundles turn negative rows positive.** A battery is positive with ToU, and an induction hob with gas
  disconnection.

| Rank | Measure | N_rem (m) | NAV £/hh/yr | Ease | Score | Topic page |
|---|---|---|---|---|---|---|
| 1 | Switch to an EV (off-street parking, at ownership change) | 10.0 | 475 | 2 | 1,900 | `ev_charging_and_the_saving_against_petrol_and_diesel_2026-10-25.md` |
| 2 | Thermostat −1°C | 13.9 | 152 | 4 | 1,696 | `household_carbon_and_the_measures_that_save_it.md` §5 |
| 3 | Move off the default tariff to a beating fix, or switch | 18.0 | 80 | 5 | 1,440 | `cheapest_fix_against_the_default_tariff_gb_2016_2025.md`, `switching_mechanics_2026-10-25.md` |
| 4 | Shorter showers / hot-water timing | 13.9 | 75 | 4 | 834 | §5 (shower row) |
| 5 | Standby and appliance habits | 13.9 | 52 | 5 | 730 | — (pack only) |
| 6 | Air-source heat pump after BUS (gas, owner-occupied) | 13.0 | 267 | 1 | 693 | `heat_pumps_and_fabric_measures_2026-10-25.md` |
| 7 | DIY draught-proofing | 13.9 | 50 | 4 | 556 | §5 |
| 8 | Loft top-up to 270 mm | 10.6 | 85 | 3 | 541 | §5, `heat_pumps_and_fabric_measures_2026-10-25.md` |
| 9 | Cavity wall insulation | 2.5 | 348 | 3 | 521 | as above |
| 10 | Solar PV | 6.4 | 195 | 2 | 499 | `solar_pv_and_home_batteries_2026-10-25.md`, `pv_roofs_orientation_and_yield_2026-10-25.md` |
| 11 | Boiler flow temperature | 8.2 | 65 | 4 | 426 | §5 |
| 12 | Standard credit → Direct Debit | 3.1 | 136 | 5 | 422 | `payments_and_direct_debit_2026-10-25.md`, `gb_payment_method_migration_rates.md` |
| 13 | EV tariff for existing EV owners | 0.8 | 400 | 4 | 256 | `a_tou_tariff_needs_the_households_choice_not_its_meter.md` |
| 14 | Smart meter install (enabler) | 8.0 | 38 | 4 | 240 | `smart_meters_and_half_hourly_settlement_2026-10-25.md` |
| 15 | Full heating controls / TRVs | 3.0 | 128 | 3 | 230 | §5 |
| 16 | Solid wall insulation | 6.5 | 157 | 1 | 204 | `heat_pumps_and_fabric_measures_2026-10-25.md` |
| 17 | Heat-pump tumble dryer (at replacement) | 3.0 | 42 | 4 | 102 | — |
| 18 | Demand Flexibility Service-type events | 17.8 | 6 | 4 | 78 | `neso_dfs_called_day_response_2026-09-07.md`, `household_flexibility_and_the_advice_roadmap_2026-10-25.md` |
| 19 | Remove the gas connection after a heat pump | 0.3 | 93 | 2 | 11 | — |
| 20 | Induction hob (gas homes, alone) | 5.0 | negative | 3 | 0 | — |
| 21 | Battery added to existing PV (alone, flat tariff) | 1.5 | negative | 3 | 0 | `solar_pv_and_home_batteries_2026-10-25.md` |
| 22 | Glazing for the single-glazed remainder | 3.1 | negative | 2 | 0 | — |

**Where this page and §5 disagree on £**, both figures are shown, and the ranking uses the pack's:
- *Thermostat −1°C*: the pack gives £90 (EST at 2024 prices); §5 gives £120 (EST current, 22→21°C).
- *Loft*: the pack gives £230 (EST current, 0→270 mm); §5 gives ~£198 (EST 2016 semi, re-priced at the
  2025 rate).

  These differences are price basis, not disagreement about physics.
- *Heat pump*: the pack's +£267 NAV includes £250/t carbon. On flat cap rates, §5 measures **−£112 to −£169**
  a year in money against a working gas boiler. The pack's money-only NAV for a heat pump is therefore not
  positive on a flat tariff, and **with λ = 0 the heat pump drops out of the money ranking**. That is
  §5's "carbon-led on flat tariffs" finding seen from the ranking side.

**A second ranking: value per hour of household effort** (pack §10; every hour figure is [unverified]).
- Top of that list: Direct Debit (~£540/h), an EV tariff for an EV owner (~£400/h), claiming WHD where it
  is not automatic (~£300/h), and SEG choice for PV owners (~£260/h).
- Bottom: ASHP (~£15-30/h) and grant-funded insulation (~£15-40/h).

The two rankings disagree on purpose. Market size favours broad behaviour and EVs. Value per hour favours
the money levers a supplier itself controls.

## 3. The catalogue, by group

Each group gives one line per measure: £ and carbon, cost, who can (applicability and restrictions),
penetration → remaining, ease and hassle, what the supplier can observe, the supplier's role, and evidence
strength. Rows the ranking does not score are still listed: they are part of "every change".

### A. Money levers (no capital; the supplier controls most of them)

| Measure | £/yr (carbon) | Who can | Penetration → remaining | Ease / hassle | Observe | Supplier role | Evidence |
|---|---|---|---|---|---|---|---|
| Standard credit → DD | £136 (Jan-Mar 2026 cap gap); no carbon | Bank account, credit meter | SC ~11% [unverified] → 3.1m | 5 / T4 10-20 min [unverified] | Account | Default offer, prompt | Regulated price gap |
| Default tariff → fix, or switch | £0-150 now [unverified]; £160 CMA 2015 detriment | All but some PPM and legacy meters | ~65% on default [unverified] → ~18m | 5 / T1 20-40 min [unverified]; 21 days elapsed (2018) | Account | Auto-roll to the best tariff; retention | **Trial-measured**: collective-switch RCT, £150-298 per switcher |
| Economy 7 / ToU | Gains only above ~40% off-peak [unverified] | Storage heating, EV, heat pump, or high shiftable load; smart meter or E7 meter | Not found → ~4m [unverified] | 4 / T1 30 min, then ongoing scheduling unless automated | HH: off-peak share, EV and heat-pump signatures | Tariff; device integration | Modelled or claimed. See `a_storage_heated_homes_default_tariff_is_two_rate.md` |
| EV tariff | £300-600 [unverified] | EV with home charging (93% of EV drivers) | 52% have smart chargers → ~0.8m | 4 | HH: 7 kW blocks | Tariff; managed-charging API | Survey (DfT, non-probability) |
| Heat-pump tariff | £100-250 [unverified] | Heat-pump homes | → ~0.25m [unverified] | 4 | HH: cold-weather load, defrost | Tariff | Claimed |
| Export / SEG choice | 2p→15p on 1,500 kWh ≈ £195 [derived] | PV with an export-capable meter | → ~0.85m [unverified] | 5 / 20-60 min plus the MCS certificate | HH: export register | Export tariff, often tied to supply | Market data (MSE) |
| Prepayment vs DD | PPM £47 cheaper at the Jan 2026 cap | Smart meter for a remote switch | Not a general recommendation; it is a vulnerability question | 4 | Account | — | Regulated |
| Dual fuel / paperless | £0-30 [unverified] | Gas homes | Small | 5 | Account | Tariff | Claimed |
| Warm Home Discount | £150 | Core Groups 1 and 2 (means-tested) | 5.52m core rebates, **96% automatic** → <0.3m [unverified] | 4-5 / usually 0 | Account (core list) | Mandated gateway | Administrative |
| Hardship funds; Ofgem debt relief | Case by case; write-off over £100 for ~195k | Struggling households; benefits plus arrears | £4.4bn arrears pool | 3 / T3 1-3 h with an income and expenditure form [unverified] | Account: arrears, PPM self-disconnection | Advise, fund, refer | Administrative |
| Priority Services Register | Non-financial | Vulnerable, including temporary vulnerability | ~13% (2015, the latest found) → under-registered [unverified] | 5 / 5-10 min | Ask; HH: self-disconnection | Register; share with the network | Administrative. See `vulnerability_psr_and_ability_to_pay_2026-10-25.md` |

### B. Behaviour (zero capital; persistence is the open question)

| Measure | £/yr | Who can | Remaining | Ease / hassle | Observe | Role | Evidence |
|---|---|---|---|---|---|---|---|
| Thermostat −1°C | £90-120 (~350 kg [derived]) | Controllable heating; **comfort and health risk for vulnerable people** | ~13.9m [unverified] | 4 / 1 min, then ongoing comfort | HH: degree-day regression | Advise, nudge | Modelled (EST) |
| Heating schedule | 5-10% of heating [unverified] | Programmer or smart controls | ~13.9m [unverified] | 4 | HH | Advise | Modelled |
| Flow temperature 80→60°C | ~£65 modelled; **0.4% measured per household advised** | Condensing gas boilers (~22.8m) | 64% say they have lowered it (self-selected) → ~8.2m [derived] | 4 / 15-30 min [unverified] | HH: perhaps, from cycling [unverified] | Advise; remote optimisation for connected boilers | **Trial-measured** (Nesta RCT, ~61k homes) |
| Hot water timing and setpoint | £20-40 [unverified] | Cylinder homes (~40% [unverified]) | ~11m | 4 | Ask | Advise | Modelled |
| Shower to 4 min | £45-70 [unverified] | All | ~13.9m | 4 / ongoing | HH: electric showers only | Advise, feedback | Modelled |
| Laundry: 30°C, line-drying | £15-100 [unverified] | Drying space; damp risk in flats | ~7m dryer homes [unverified] | 4-5 | HH: dryer signature | Appliance insights | Modelled |
| Standby off | £40-55 [unverified] | All | ~13.9m | 5 / 30 min audit with smart plugs | HH: overnight baseload | Baseload alert | Modelled |
| DFS / event shifting | ~£0.48 per registrant (2024/25) [derived] | Smart meter in smart mode (71%) | 1.98m registered → ~17.8m | 4 / 5-15 min per event manually, ~0 if automated | HH, settlement-grade | Tariff; aggregator; automation | **Trial-measured** (NESO delivery data) |

### C. Low cost (under ~£500)

| Measure | £/yr | Upfront | Who can | Ease | Observe | Role |
|---|---|---|---|---|---|---|
| Draught-proofing | £40-55 (~160 kg [derived]) | £50-250 DIY | All; renters can use reversible strips | 4 / 0.5-3 h DIY | HH (weather-normalised gas only) | Ship kits |
| LEDs | £45 a home (EST); 35 kg | low | All; ~8m with material non-LED stock [unverified] | 5 | HH: baseload | Advise |
| Cylinder jacket | £40-45 | £15-30 | Uninsulated cylinders (~0.6m [unverified]) | 5 | Ask | Ship kits |
| TRVs (with programmer and thermostat) | £35 | ~£510 installed | Wet systems | 3 | Ask | Partner |
| Smart thermostat | ~£33-36 (BIT-measured 4.5-5%) | £150-250 plus install | Boiler or heat-pump homes; renters need consent for wired units | 3-4 | HH | Tariff bundle |
| Efficient shower head | £20-70 incl. water [unverified] | £15-40, often free from water companies | Mixer showers only | 5 | Ask | Ship |
| Radiator panels, curtains, smart plugs | £5-30 each [unverified] | £10-150 | All | 4-5 | — | Advise |
| Working smart meter plus IHD | 2-3% feedback [unverified]; mainly an **enabler** | £0 (supplier-funded) | All supply points; comms dead spots | 4 / T5 ~2 h with a half-day window [unverified] | Account | **Core obligation**; fixing the 3.1m in traditional mode |

### D. Fabric (the landlord decides in private rented homes; EPC C by 1 Oct 2030, £10k cap)

| Measure | £/yr (carbon) | Upfront | Who can / restrictions | Penetration → remaining | Ease / T5 hassle | Evidence |
|---|---|---|---|---|---|---|
| Loft 0→270 mm | £198-230 (580 kg) | £750-950 | Houses and top-floor flats with an accessible loft | 42% over 200 mm → ~10.6m | 3 / loft clearance; 0.5-1 day | NEED exists, not fetched |
| Cavity wall | £222-240 (650 kg) | £1,700-2,200 | Unfilled cavities, not exposed or flood-risk | ~2.5m unfilled-easy [unverified] | 3 / 1 day outside | as above |
| Solid wall (IWI or EWI) | £300-376 (1,100 kg) | £7k-15k | EWI is restricted in conservation areas and on listed buildings; IWI loses room space. **The NAO found 98% of ECO/GBIS EWI had major issues** | <10% done → ~6.5m [unverified] | 1 / EWI 3-10 days of scaffold; IWI 1-3 weeks per room | Modelled |
| Floor (suspended timber) | £50-100 [unverified] | £1k-3k | Suspended floors | not estimated | 2 | Modelled |
| Glazing (single-glazed remainder) | £100-150 [unverified] | £5k-10k | Listed buildings need consent; secondary glazing or film for renters | 89% double → ~3.1m | 2 | Modelled |
| External doors | £20-50 [unverified] | £500-1,500 | Houses | not estimated | 3 | — |

The supplier's role across the group: grant gateway, vetted installer partner, government-backed loans,
and a landlord compliance service for 2030. Observe: the after-state is HH-visible (gas drop); the
before-state is Ask or EPC Register.

### E. Heating systems

| Measure | £/yr (carbon) | Net upfront | Who can / restrictions | Penetration → remaining | Ease / T5 hassle | Evidence |
|---|---|---|---|---|---|---|
| Air-source heat pump | −£112 to −£169 on flat cap rates, positive on an HP tariff or against an old boiler (§5); ~1,600 kg | £3k-6k after the £7,500 BUS | Owner-occupied for BUS; outdoor space (8% lack it); 15% need efficiency upgrades first | 80,098 BUS-funded → ~13.0m [derived; feasibility unverified] | 1 / 10-20 h research, 1-2 surveys, 2-5 days install, 1-2 months lead time. **48% of boiler buys are distress purchases (13% for heat pumps)** | EoH trial (742); Nesta survey |
| Ground-source heat pump | above ASHP [unverified] | £20k-35k gross | Land for loops | <2m | 1 | Claimed |
| Hybrid heat pump | partial [unverified] | £6k-10k | Gas homes where a full heat pump is hard | — | 2 | Claimed |
| Heat battery | enables ToU hot water | £2k-4k | Combis without cylinder space; **being added to BUS** | — | 3 | Claimed |
| High-heat-retention storage heaters | £150-400 vs old storage on ToU [unverified] | £1k-2k a room | Electric-heated flats, off-gas, PRS | ~1.5m [unverified] | 3 | Claimed |
| Air-to-air heat pump | heating plus cooling | £1.5k-4k a head | Flats, electric-heated homes; BUS eligibility being added | — | 3 | Claimed |
| Full heating controls | £100-110 (~290 kg) | ~£860 | Wet systems without them | ~3m [unverified] | 3 | Modelled (EST) |
| Non-condensing boiler replacement | £200-300 [unverified] | £2.5k-4k | Pre-2005 boilers | ~1.5m [unverified] | 3 | Modelled |
| District heat connection | Regulated by Ofgem from 2026 [unverified] | developer-led | Heat-network zones | 2-3% [unverified] | 1 (rarely the household's choice) | — |
| Remove gas (cap the meter) | £108.33 standing charge [derived] plus servicing | £0-500 | Only after full electrification | ~0.3m [unverified] | 2 | — |

### F. Generation and storage

| Measure | £/yr | Upfront | Who can / restrictions | Penetration → remaining | Ease | Note |
|---|---|---|---|---|---|---|
| Solar PV ~4 kWp | £180-1,060 (§5; the self-use share is the gap); ~260 kg net | £5k-8k | Owner-occupied; suitable roof; conservation and listed limits; rarely flats | ~1.7m stock [unverified] → ~6.4m | 2 / 5-10 h, 1-2 days of scaffold | Money-led now (§5) |
| Battery | £150-400 with ToU [unverified]; carbon ≈ neutral | £3k-6k | PV or ToU homes, with space | ~1.5m PV homes without one [unverified] | 3 | Positive only as a bundle |
| Solar diverter | £50-150 [unverified] | £300-500 | PV plus a cylinder | <0.5m | 4 | — |
| Solar thermal | £50-100 [unverified] | £3k-6k | Cylinder; competes with PV plus a diverter | niche | 2 | — |
| V2G | £300-800 [unverified] | £3k-6k bidirectional charger | Compatible EV plus parking | niche | 2 | — |

### G. Transport and H. Appliances

| Measure | £/yr (carbon) | Who can / restrictions | Remaining | Ease | Observe |
|---|---|---|---|---|---|
| Switch to an EV | £600-1,000 fuel [unverified]; ~1,800 kg (§5) | Car-owning homes; **68% of English homes** have or could have off-street parking | 1.737m ZEV cars → ~10m at ownership change [unverified] | 2 | HH: 7 kW blocks |
| Home charger / smart charging | enables the EV tariff | Off-street parking; freeholder consent for flats | ~0.8m EV drivers without smart chargers | 3 / 5 | HH |
| Public charging only | higher £/kWh | the 32% without off-street parking | — | 3 (ongoing hassle) | — |
| A-rated fridge-freezer (end of life) | £40-80 [unverified] | Old units | ~3m [unverified] | 4 | HH (disaggregation) [unverified] |
| Induction hob | ≈ neutral alone at Oct 2026 rates; positive with gas disconnection | Gas-hob homes | ~5m [unverified] | 3 | — |
| Heat-pump tumble dryer | £40-80 [unverified] | Dryer replacers | ~3m a year pool | 4 | HH |

## 4. Where a supplier creates value mainly in time (the pack's §11, for C31)

1. An auto-optimised tariff (the collective-switch effect).
2. Automated DFS participation (below £1 of cash value, so zero effort is the only version that scales).
3. A grant gateway concierge.
4. Pre-surveyed, heat-pump-ready homes, so that a boiler failure can become a heat pump.
5. A one-stop install with a single point of accountability.
6. Remote flow-temperature and controls optimisation.
7. SEG bundled with supply.
8. Auto-enrolment for the PSR, WHD and debt relief.
9. A landlord EPC C compliance service.
10. Fixing the 3.1m smart meters in traditional mode.

The evidence that this works is the trial-measured contrast:
- removing hassle moved switching 7-10x (collective switch) and reaches 96% (WHD automatic matching);
- advice alone moved 0.4% (flow temperature).

## 5. How the world and the supplier read this page

- **The world.** Applicability and penetration are *per home*, drawn and hidden: who can adopt is a
  property of the house and household, not a share. Each "remaining" figure above is a calibration target
  for the drawn population's aggregate. It is never a probability applied to a household. The hassle
  column is the T5 friction that the world-hassle sketch prices (`docs/design/THE_IMPROVEMENT_LOOP.md` §8).
- **The supplier.** Its ranking is an *estimate*, built only from the "observe" column (Account, HH, or
  what it asks). It is graded against the world's truth. A row whose eligibility is Ask-only cannot be
  targeted from data, and a supplier claiming otherwise has crossed the wall.

## 6. GAPs (from pack §13, kept here so they are not read as answered)

1. The GB household count and the GB tenure split.
2. The current fixed/default and standard-credit shares (Ofgem retail market indicators not fetched;
   `gb_domestic_default_tariff_share_2016_2025.md` holds the historical series).
3. The HEE/NEED cavity, solid-wall and measured savings by measure.
4. Stock totals for PV, batteries and heat pumps.
5. Neutral sources for EV, heat-pump and ToU tariff savings.
6. **Household hours per measure, disruption days, and any GB willingness to pay to avoid hassle.** This
   is C31 T5, and none was found.
7. Current PSR registrations.
8. Warm Homes Plan low-income detail.
9. Storage-heater stock and district-heat customer numbers.
10. GB off-street parking (68% is England only).
11. Persistence of behavioural savings beyond 90 days.
12. Conservation-area and listed shares of the stock.
