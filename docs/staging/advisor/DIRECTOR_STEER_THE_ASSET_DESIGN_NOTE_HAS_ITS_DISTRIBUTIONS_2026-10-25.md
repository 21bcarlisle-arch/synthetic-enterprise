**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The asset design note has its distributions: draw the person, then the asset, then the half hour (2026-10-25)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sun 25 Oct:

- 06:03 GMT: "It should be derived from miles driven and car type etc. it fine to explain how things work now, but I was the SIM to be personalised for home assets and behaviours"
- 06:30 GMT: "There is a comfort measure here. There is also a healtg and safety aspect to house temp recomnedations."
- 06:42 GMT: "NB driveways matter too, as it only really makes sense to have an ev if you can charge from home"

Six evidence packs land beside this file:
- drivers, mileage and parking;
- vehicle mix and real-world efficiency;
- roofs, PV orientation, yield and irradiance;
- heating behaviour, comfort and health floors;
- dated cost and price series;
- gap closure.

They are the inputs to the asset design note you were asked for in `DIRECTOR_STEER_ASSET_DEMAND_IS_DERIVED_PER_HOME_NOT_A_STATIC_PERCENTAGE_2026-10-25.md`. This steer gives the design rules that come out of them. The order of work stands: basics, then forward years, then the advice roadmap.

## Design rules from the evidence

1. **Draw the person first, then the asset.** BEV and diesel drivers do more miles because high-mileage people choose them. The fuel does not cause the miles. 2024 figures for cars under 3 years old: BEV 10,054, petrol 7,585, diesel 10,728.
   - Draw each driver's mileage from person and household attributes: age, sex, work, income, area, company car, cars in household. Then draw the vehicle given mileage, income and parking.
   - Mileage is heavily skewed. Fit a lognormal on the MOT quartiles. Scale it down with vehicle age (index 1.00 → 0.51) and up for company cars (about 2.4×).
   - Year-on-year persistence is unpublished. Name a person factor × yearly shock, plus a regime-change probability, as a design choice.
2. **Parking is a home attribute, and it conditions EV adoption strongly but not absolutely.**
   - About 90% of BEV drivers can charge at home. About 9% are public-only, mostly in cities. That figure comes from the DfT tracker and is unverified in the pack, so fetch it.
   - Off-street parking runs from about 7% (Westminster) to 84% (Flintshire). Draw it by dwelling type, tenure and area once the EHS parking tables are fetched.
   - A public-only EV has **zero home kWh**. It pays public prices (54–79p/kWh PAYG) and 20% VAT. It can cost more per mile than petrol.
   - A granny lead loses 13–24% of energy in charging, against 5–7% on a wallbox.
3. **Vehicle energy is derived, never looked up.**
   - Use per-model base efficiency (220–310 Wh/mi for mainstream models) × a temperature multiplier on that day's local temperature: about 1.15–1.2 at 10°C, 1.28 at 0°C, 1.43 at −7°C, with a heat pump cutting about 8–10 points at 0°C. Add charging losses.
   - PHEV electric share comes from charging behaviour and keeper type: private about 45–49%, company 11–15%.
   - The ICE counterfactual is that household's previous car's official mpg × the real-world gap for its age (1.08–1.39 for NEDC-era cars, 1.17–1.21 for WLTP) × the dated weekly pump price.
4. **PV generation comes from the home's own sky.**
   - Use SARAH-3 30-minute irradiance at the home's 0.05° pixel, which is free with attribution to EUMETSAT. Homes in the same pixel share their sky, and that gives street-level correlation.
   - Each roof plane needs kWp, azimuth, tilt, shade factor, install cohort, degradation (−0.8%/yr) and an inverter limit with clipping.
   - Self-consumption emerges from that home's own half-hourly demand.
   - The GB azimuth × tilt × kWp × install-date joint distribution is in the OCF `uk_pv` metadata, under CC-BY-4.0 and gated behind accepting terms on Hugging Face. **Accepting those terms is a real-world agreement, so it is the director's call.** The advisor recommends accepting: it is the only GB source, and attribution is the only obligation. Until then, the pack's placeholder orientation shares are a named assumption.
   - Population checks: fleet yield 806–920 kWh/kWp by year, with a coefficient of variation of about 4%; South West about 20% above Scotland; east or west roofs at 0.80–0.82 of south.
5. **Heating is behaviour plus physics, and comfort is an output.**
   - Draw these from the EFUS and SERL distributions: setpoint, schedule type, daily hours, season, flow temperature (mode 72–75°C, about 6% at 60°C or below), controls present and used, unheated rooms, hot-water litres and draws, and electric shower.
   - Indoor temperature per half hour comes out of the thermal model.
   - "Always on" is not a label. Reported 24-hour heating is about 4%, but about 31% of homes show a flat measured temperature profile. Let flatness emerge from low setback, long hours and building type.
   - The 2022–23 price response is evidence for the behaviour model: setpoint −1°C, about −3.8% gas per °C, and the cut concentrated in fuel-poor homes.
6. **Health floors are hard rules on advice.** They are listed in the heating pack, section (c):
   - never advise a living room below 18°C;
   - higher for over-65s, chronic illness and Priority Services Register homes;
   - flag any room-hour below 16°C;
   - never advise a cut to a household already below 18°C or self-rationing; route them to support instead;
   - stored hot water at 60°C or above.

   Cite WHO 2018, PHE 2014 and NICE NG6 as the basis. Ofgem sets no temperature rule.
7. **Every price and cost is a dated series with a spread between homes.**
   - Use the series register in the cost pack: weekly pump prices from 2003, the cap by region × payment method from 2019, QEP, PV £/kW by size band, Boiler Upgrade Scheme heat pump costs, and battery £/kWh by size band.
   - **Grid carbon:** index the DESNZ factor by *data year*, not reporting year. The lag was two years until 2025 and data year 2024 is skipped. Prefer NESO's half-hourly regional intensity from Sep 2017, which ran from 47 g (North Scotland) to 252 g (South Wales) in 2025.
   - 2026 pump prices spiked (petrol about 175p, diesel about 200p in Oct 2026). A dated series carries this automatically, which is the point.
8. **Dated facts confirmed in the gap pack.** Each one is a dated rule, not a constant.
   - The TDCV history 2015 → 2017 → 2020 → 2023 → 1 Jul 2026, with all three bands and the multi-rate values. Medium gas went 12,500 → 12,000 → 11,500 → 9,500 kWh; medium electricity went 3,100 → 2,900 → 2,700 → 2,500 kWh. TDCVs are only for quoting and checking; homes keep their own derived use.
   - Zero VAT on GB domestic electricity from 1 Oct 2026 to 31 Mar 2027, under SI 2026/987 and HMRC Revenue and Customs Brief 10 (2026). Gas stays at 5%, Northern Ireland stays at 5%, and public chargepoints stay at 20%.
   - The radio teleswitch switch-off was completed at the end of June 2026. Economy 7 timing now runs through the smart meter.
   - ECO1 in-use factors by measure. These are evidence for the deemed-to-measured gap the savings grader will test.
   - The CalTRACK specification for the savings grader:
     - a 365-day baseline;
     - a data-sufficiency rule of 37 or fewer missing days;
     - a balance-point search;
     - an hourly time-of-week-and-temperature model;
     - fractional savings uncertainty, with portfolio results combined by root-sum-square;
     - ASHRAE G14: savings uncertainty under 50% at 68% confidence.

## Fetches the advisor's sandbox could not make (yours)

- DfT NTS0901/NTS0904 (mileage bands 2025), NTS0908 (overnight parking by area), TRA0305/0306 (monthly and day-of-week traffic), VEH0141/VEH1103 (parc by make, model and fuel).
- English Housing Survey parking tables by dwelling type and tenure.
- DESNZ Solar PV cost data xlsx (DNC series from 2013/14, with quartiles) and the ET 6.3 deployment workbook.
- The two ad hoc Boiler Upgrade Scheme cost releases (regional medians, mode and capacity).
- DESNZ "Valuation of energy use" tables (retail price projections), and the FES 2025 Pathway Assumptions Log.
- PVGIS grid: about 6 sites × 8 azimuths × 3 tilts, used as calibration only.
- OCF `uk_pv` metadata, once the director rules on the terms.

## Ask

- Write the asset design note, `docs/design/PERSONALISED_ASSET_WORLD.md`. It covers EV, PV and battery, heating and hot water, heat pump and fabric. For each attribute give its distribution, the conditioning variables and the source. Give each derivation down to the half hour. List each population check. Name each design choice.
- Bring back a recommendation on the OCF terms, along with your other reserved items.
- Flag anything already built that reads a constant where a dated series is now available.
