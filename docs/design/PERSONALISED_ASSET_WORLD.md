# The personalised asset world: draw the person, then the asset, then the half hour

*Design note, 25 Oct 2026. Asked for by the director's steers of that morning:
`DIRECTOR_STEER_ASSET_DEMAND_IS_DERIVED_PER_HOME_NOT_A_STATIC_PERCENTAGE_2026-10-25.md` (06:03, "It
should be derived from miles driven and car type etc. ... I was the SIM to be personalised for home
assets and behaviours"), `DIRECTOR_STEER_THE_ASSET_DESIGN_NOTE_HAS_ITS_DISTRIBUTIONS_2026-10-25.md`
(06:42, "driveways matter too"), `DIRECTOR_STEER_COMFORT_HEALTH_AND_CARBON_ARE_OUTPUTS_..._2026-10-25.md`
(06:30) and `DIRECTOR_STEER_FLEX_AND_NETWORK_KNOWLEDGE_IS_THOROUGH_AND_THE_SIM_IS_LAYERED_2026-10-25.md`
(06:44). All four are in `docs/staging/advisor/` until actioned, then `done/`.*

**Status: design, not build.** Nothing here is built by this note. Its place in the order is step 8
of `docs/direction/priority_order.yaml`: after the basics (steps 2-5) and the forward years (step 6).
Each figure below is the advisor's pack figure; its verification outcome (confirmed, corrected or
open) is recorded on the Knowledge page drafted from that pack, and no open figure is used as a
check until it is confirmed.

---

## 1. The four rules

1. **Inputs are attributes of entities.** Person, vehicle, roof plane, device, home. Each is drawn
   from a published distribution, conditioned on who lives there and what the home is. Where no
   distribution is published, the attribute is a **named design choice** (section 7), never a
   number that looks sourced.
2. **Energy, cost and carbon are computed**, half hour by half hour, from those attributes under the
   home's own weather, the tariff in force and the price chain (replayed 2016-25, generated after).
   Nothing downstream reads a percentage uplift, a fixed p/kWh or a payback figure.
3. **Published figures are population checks, never per-home targets.** "Across the book, simulated
   EV home-charging kWh falls within the published range." A failed check changes an input or a
   mechanism; it never feeds an output back into the generator.
4. **Every saving is that home's own counterfactual.** Rerun the same home without the change, same
   weather, prices and behaviour (plus rebound where modelled). Money and kgCO2 come off the same
   pair of runs. The savings grader (step 10) compares the supplier's estimate with exactly this.

The order of the draw, for every asset: **person → asset → half hour.** High-mileage people choose
BEVs and diesels; the fuel does not cause the miles (cars under 3 years, 2024: BEV 10,054, petrol
7,585, diesel 10,728 miles a year).

---

## 2. EV

| Attribute | Entity | Drawn from | Conditioned on | Source |
|---|---|---|---|---|
| Drivers in the household | person | NTS licence holding | age, sex, household type | DfT NTS |
| Annual mileage | person | lognormal fitted to MOT quartiles; × vehicle-age index (1.00 → 0.51); × ~2.4 company car | age, sex, work, income, area type, company car, cars in household | DfT NTS0901/0904; RAC/MOT mileage |
| Year-on-year persistence | person | person factor × yearly shock, plus a regime-change probability | — | **design choice** (unpublished) |
| Trip pattern | person | commute/leisure day-of-week and month shape | work status | DfT TRA0305/0306 |
| Parking | home | off-street share by dwelling type, tenure, area (7% Westminster to 84% Flintshire) | dwelling type, tenure, LA | EHS parking tables; NTS0908 |
| Vehicle | vehicle | segment / model given mileage, income, parking | mileage, income, parking, year | DfT VEH0141/VEH1103 |
| Base efficiency | vehicle | per-model Wh/mi (mainstream 220-310) | model | vehicle-mix pack |
| Temperature multiplier | vehicle | ~1.15-1.2 at 10°C, 1.28 at 0°C, 1.43 at −7°C; heat pump cuts 8-10 points at 0°C | that day's local temperature, heat pump fitted | vehicle-mix pack |
| BEV or PHEV; PHEV electric share | vehicle | private ~45-49%, company ~11-15% | keeper type, charging access | vehicle-mix pack (ICCT) |
| Charger | home | none / granny lead / untimed / timed / smart; AC limit; phase | parking, tenure, install year | EV pack |
| Charging loss | home | granny lead 13-24%, wallbox 5-7% | charger | EV pack |
| Plug-in habit | person | frequency, arrival time, plug-in state of charge, target | engagement | **design choice** where unpublished |
| Previous car (counterfactual) | vehicle | official mpg × real-world gap (NEDC 1.08-1.39, WLTP 1.17-1.21) | age of previous car | vehicle-mix pack |

**Derivation to the half hour.** Daily miles (person × trip shape) × kWh/mile at that day's
temperature + charging loss = energy needed. The plug-in decision and the tariff or smart signal put
it into half hours at home, at work or on public chargers. **A public-only EV has zero home kWh**
(about 11% of BEV drivers, mostly urban; DfT tracker year 2): it pays public prices (54-79p/kWh PAYG) and 20% VAT. The ICE
counterfactual is the same miles × the previous car's real-world mpg × the dated weekly pump price.

**Adoption.** The year-indexed table may keep setting the market-level rate; *who* adopts and *what*
they buy follows from income, parking, tenure, mileage, company car and replacement cycle.

**Population checks.** About 87% of BEV drivers park off-street and about 11% charge only in public (DfT EV driver tracker, year 2; the pack's 90% and 9% were the year 1 figures, corrected 25 Oct). Home
charging kWh per EV household within the EV pack's band. Mileage by fuel within the 2024 figures
above. PHEV electric share by keeper type.

---

## 3. Solar PV and battery

| Attribute | Entity | Drawn from | Source |
|---|---|---|---|
| Roof planes: kWp, azimuth, tilt | roof | azimuth × tilt × kWp × install-cohort joint distribution | OCF `uk_pv` metadata (terms accepted 25 Oct; token requested), reweighted to FiT/MCS cohorts. **Until the token arrives the orientation shares are a named assumption.** |
| Shade factor | roof | — | **design choice** |
| Install year | roof | DESNZ deployment by year and size band | DESNZ ET 6.3; FiT/SEG cohort |
| Degradation | panel | −0.8%/yr | roofs pack |
| Inverter limit and clipping | device | kWp ratio by cohort | roofs pack; **design choice** for the ratio spread |
| Irradiance | home | SARAH-3 30-minute at the home's 0.05° pixel (homes in one pixel share a sky) | EUMETSAT, free with attribution |
| Battery: kWh, kW, round-trip, fade | device | by install year and size band | solar and battery pack |
| Battery mode, reserve, windows, controller | device | none / app / supplier | **design choice** where unpublished |
| Export registration and tariff | home | FiT vintage or SEG | install year |

**Derivation.** Irradiance × plane geometry × kWp × degradation, clipped at the inverter, gives
half-hourly generation. **Self-consumption emerges** from generation against that home's own
half-hourly demand; it is never a share. A battery dispatches by its mode against that demand and
the tariff.

**Population checks.** Fleet yield 806-920 kWh/kWp by year (CV about 4%); South West about 20% above
Scotland; east or west roofs at 0.76-0.84 of south depending on tilt (PVGIS grid run 25 Oct, 168
cases, calibration only; corrects the pack's 0.80-0.82); self-consumption within the pack's 28-57% range.
**Attribution:** Open Climate Fix and Sheffield Solar wherever `uk_pv`-derived data is published.

---

## 4. Gas boiler, heating and hot water

| Attribute | Drawn from | Source |
|---|---|---|
| Boiler type and install year (condensing or not); combi or system | stock by dwelling and age (combi ~62%) | boilers pack; EHS |
| Flow temperature setting | mode 72-75°C, ~6% at 60°C or below | heating-behaviour pack |
| Emitter oversizing | by dwelling and install | **design choice** where unpublished |
| Controls present and used | only ~46% use a timer | EFUS |
| Setpoint, setback | mean ~20°C, falling to ~19°C after 2022 | EFUS; SERL |
| Schedule type and daily hours | median 7-8 h; 6% heat all year; ~4% report 24-hour heating | EFUS |
| Unheated rooms | EFUS | EFUS |
| Hot water litres and draws; electric shower | EST/EFUS | heating-behaviour pack |
| Comfort response to a change (take-back) | pack evidence; rest is a **design choice** | heating-behaviour pack |

**Derivation.** The existing thermal model takes these attributes; return temperature (flow ×
emitter size) gives in-use efficiency on the SAP 10 curve, so boiler choices show in the gas
profile. **Indoor temperature per half hour is an output**, at least for the main living space.
"Always on" is not a label: reported 24-hour heating is ~4%, but ~31% of homes show a flat measured
profile, and flatness should emerge from low setback, long hours and building type.

**Comfort outputs.** Degree-hours below setpoint while occupied; warm-up time. The physics should
show what the director described: a lower flow temperature responds more slowly, most in cold
weather and with small radiators (test house: 80→60°C cut gas ~9%, warm-up +17 minutes, rooms 0.5°C
cooler; about half a "flow-temperature saving" is cooler rooms).

**Population checks.** The 2022-23 price response: setpoint −1°C, ~−3.8% gas per °C, the cut
concentrated in fuel-poor homes. Flow-temperature distribution. Timer use.

---

## 5. Heat pump and fabric

- **Heat pump:** sizing against that home's heat loss, flow temperature and weather compensation,
  emitters, cylinder, cycling and defrost. **SPF emerges** under that home's weather; it is never
  drawn. Population check: measured SPF median about 2.8.
- **Fabric:** each element's state (loft depth, cavity filled, solid wall, glazing, draughts) feeds
  the heat-loss coefficient. Measured savings emerge; NEED medians are the population check, and
  ECO in-use factors are the evidence for the deemed-to-measured gap the savings grader tests.
- **Capex** for every measure is a dated cost curve with a spread between homes (BUS ad hoc
  releases for heat pumps; DESNZ PV cost data by size band; battery £/kWh by size band).

---

## 6. Health floors on advice (hard rules, not outputs)

Never advise a living room below 18°C; higher for over-65s, chronic illness and Priority Services
Register homes; flag any occupied room-hour below 16°C; never advise a cut to a household already
below 18°C or self-rationing, route it to support; stored hot water at 60°C or above. Basis: WHO
2018, PHE 2014, NICE NG6 (UKHSA's current guidance to be checked and cited on the heating page).
Ofgem sets no temperature rule.

## 7. Prices, costs and carbon are dated series

Energy prices come from the tariff in force in that half hour. Pump prices are the weekly series
from 2003. Capex is dated by size band. Grants, VAT and tax carry effective dates (0% VAT on
domestic electricity 1 Oct 2026-31 Mar 2027 to be verified against Ofgem and HMRC before any
constant uses it). Grid carbon: index DESNZ factors by **data year**, not reporting year; prefer
NESO half-hourly regional intensity from Sep 2017. TDCVs are for quoting and checking only; homes
keep their own derived use.

## 8. Named design choices (no published distribution)

Year-on-year mileage persistence; plug-in habit where unpublished; roof shade factor; inverter ratio
spread; emitter oversizing; battery mode and reserve where unpublished; comfort take-back beyond the
pack evidence. Each is named in code where it is drawn, with a range, never a single value.

## 9. Minimum viable world and layers

L0, built in step 8, is everything above plus, for the network: cut-out amps (30/60/80/100 A),
phase, a looped-service flag and the ENA notify-or-apply rule with delay and cost drawn from
published distributions. The supplier can then offer smart time-of-use shifting valued on its own
wholesale book, with install lead times and conversion loss when it sells an asset.

| Layer | World holds | Supplier can offer | Trigger to build |
|---|---|---|---|
| L1 | DFS and Capacity Market events; opt-in, response, fatigue | event payments | an L0 smart-shift book exists to bid |
| L2 | region-specific DNO policies; G98/G99/G100 export | region-aware installs; export-limited designs | the company sells installs |
| L3 | DNO flex zones; feeder/secondary layer on ADMD | local flex revenue | L2 regions are drawn |
| L4 | rival aggregators (P415): newest registration takes the meter | retention and pricing against rivals | L1 pays households |
| L5 | Balancing Mechanism; load-control licensing | BM revenue; licensed load controller | SSES licensing, Mar 2028 |

The same MVP-plus-layers framing for the other domains is the seat's recommendation, carried in
`for_the_director` with this note: heating L0 is the attributes in section 4 with comfort as an
output; EV L0 is section 2 with home charging only and public charging as a price; PV/battery L0 is
section 3 with self-consumption mode only; the savings grader L0 is tariff-choice advice, which needs
no asset world; budget-first advice is a layer above the grader and settings advice.

## 10. What is already built that reads a static figure

Read from code, not run:
- `simulation/life_events.py:540` — `ev_acquired` draws only a charger kW from [3.7, 7, 7, 22]: no
  driver, mileage, vehicle or plug-in habit. Explore's "+8%" EV home is its symptom.
- `simulation/life_events.py:512` — PV kWp ~ uniform(2.5, 4.5), no planes, tilt or vintage.
- `simulation/life_events.py:526` — battery kWh ~ uniform(4.0, 13.5), no mode, reserve or controller.
- `simulation/life_events.py:107,122,137,163` — adoption is a coin per year from year-indexed tables.
- `simulation/household_demand.py:141-144` — EV energy enters as an annual kWh over the base
  consumption.
- `simulation/household.py:283` and `simulation/run_phase2b.py:762` — the demand path adds a fixed
  2,143 kWh a year per EV; the company assumes a different fixed 2,500 (`company/crm/property_model.py:128`).
- `simulation/household.py:431` — "driveway" means detached or semi-detached, so no terrace or flat
  gets an EV and no owner charges in public. `life_events.py:540` draws 22 kW home chargers, which
  need a three-phase supply most homes lack.
- `simulation/demand_model.py:1017-1025` — half-hourly PV output uses a fixed 3.5 kWp for every home,
  ignoring the drawn size; every non-flat roof is labelled `east_west` (`household.py:433-447`).
- `simulation/run_phase2b.py:617-652` — the battery charges only from surplus solar.
- `simulation/household.py:84` — every heat-pump home gets a fixed 5,500 kWh in settlement while the
  physics derives its own; `fabric_physics.py:1127` gives once-a-day heating a 6-8.5 h block where
  the survey median is 15 h; the boiler has no flow temperature; there are no electric showers; the
  setpoint never moves after 2022 (the response scales whole-fuel use instead).
- Dated series that exist but are not read: no petrol or diesel price anywhere; four fixed retrofit
  capex figures in every year; VAT undated and fuel-blind (`vat_rate_for_segment`, 5% for all domestic
  supply, wrong for electricity from 1 Oct 2026); 2026 TDCV bands applied to 2016-25 in three places.
The Knowledge pages drafted on 25 Oct carry each topic's fuller code read, with file and line.
