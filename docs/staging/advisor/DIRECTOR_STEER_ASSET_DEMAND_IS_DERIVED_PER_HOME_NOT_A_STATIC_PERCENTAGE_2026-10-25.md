**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Asset demand is derived per home, from that home's assets and behaviour, never from a static percentage or price (2026-10-25)

**Type:** STEER, sent through the advisor channel. **It corrects the advisor's cover steer of the same morning**, `DIRECTOR_STEER_THE_ADVICE_ROADMAP_NEEDS_ITS_KNOWLEDGE_FIRST_2026-10-25.md`, and the six evidence packs that came with it. Read it alongside them, and where they conflict this steer wins.

The director's words from chat on Sun 25 Oct:

- 06:03 GMT: "I'm worried you are using static costs and %. The EV percentage is irrelevant. It should be derived from miles driven and car type etc. it fine to explain how things work now, but I was the SIM to be personalised for home assets and behaviours"

## What was wrong

The cover steer's "now" item 2 told you to make "+65–120% EV uplift" (and a 1,750–3,500 kWh band) into a world claim and "fix the generator" to it. That is backwards. A household's EV consumption is not a percentage of its other use. It follows from **who drives, how far, in what car, in what weather, and where they plug in**. Fitting a generator to a band would only replace one invented number with another.

The packs' worked tables (cost per mile, paybacks, savings per °C, SPF running-cost tables) are **explanations of how things work now**. They are not model constants.

The current code shows the gap. In `simulation/life_events.py`:

- `ev_acquired` carries only `ev_charger_kw` (drawn from [3.7, 7, 7, 22]). It has no vehicle, no driver, no mileage and no charging behaviour.
- `solar_install` draws `kWp ~ uniform(2.5, 4.5)`, with no tilt and no install vintage.
- `battery_installed` draws `kWh ~ uniform(4, 13.5)`, with no mode, reserve or control.
- `heat_pump_installed` changes the heating system only.
- Adoption is a coin per year from a year-indexed probability table.

The Explore EV home showing "+8%" is a symptom of this, not a percentage to correct.

## The rule

1. **Inputs are attributes of entities.** Each attribute is drawn per person, vehicle, roof, device or home from a published *distribution*, conditioned on who lives there and what the home is. Every input has a source. Where none exists, it is a named design choice.
2. **Energy, cost and carbon are computed.** They come from those attributes, half hour by half hour, under that home's own weather, the tariff actually in force and the price chain (replayed in 2016–25, generated in the forward years). Nothing downstream reads a percentage uplift, a fixed p/kWh or a payback figure.
3. **Published figures are checks on the population, never targets for one home.** They include the bands in the packs: home charging kWh, self-consumption, SPF, setpoint, the shares. The claim is "across the book, the distribution of simulated EV home-charging kWh falls within the published range". If it doesn't, fix the inputs or the mechanism, never the output. A claim of this kind is a calibration check and reads no output back into the generator.
4. **Every saving is that home's own counterfactual.** Rerun the same home without the change, with the same weather, prices and behaviour (and with rebound where the world models it). Payback is that difference against that home's cost. A published payback or saving range is a population check, under rule 3. The savings grader (cover steer, item 3) compares the supplier's estimate with exactly this per-home counterfactual.

## What "personalised" needs per asset

Use the packs' "world needs to model" lists as the attribute inventory. At minimum:

- **EV.** These attributes belong to the *person*, the *vehicle* and the *home*, not to the household's bill.
  - **Person:** drivers in the household, each with annual mileage drawn from the published distribution for their age, sex, work status and rural or urban setting (NTS; RAC MOT mileage for new cars). Commute and leisure trip pattern. Plug-in habit (frequency, arrival time, state of charge at which they plug in, target charge). Price and tech engagement.
  - **Vehicle:** make or segment, usable battery kWh, efficiency curve against temperature (with or without a heat pump), AC charge limit, and BEV or PHEV (with an electric share of miles).
  - **Home and access:** parking (off-street, on-street, communal), charger (none, granny lead, untimed, timed, smart), single or three-phase supply. Share of energy from work, public and rapid charging follows from access and the trip pattern.
  - **Derivation:** daily miles × kWh per mile at that day's temperature gives energy needed. Plug-in decisions and the tariff or smart signal place it in half hours at home or elsewhere. Home kWh, timing, cost and carbon all emerge from this.
  - **Adoption:** conditioned on income, parking, tenure, mileage, company car or salary sacrifice, and the vehicle's age and replacement cycle. The year coin may set the market-level rate, but who adopts and what they buy must follow from the household.
- **Solar PV and battery.**
  - **Roof planes:** kWp, azimuth, tilt and shading for each.
  - **Install year:** gives the FiT vintage or SEG status, degradation to date and inverter age.
  - **Generation:** half-hourly irradiance for the home's own weather cell, using the same weather store as demand.
  - **Self-consumption:** emerges from that generation against that home's own half-hourly demand. It is never a share.
  - **Battery:** usable kWh, charge and discharge kW, round-trip efficiency, fade, mode, reserve and windows, and controller (none, app, or supplier).
  - **Export:** registration and tariff.
- **Gas boiler and heating.**
  - Boiler type and install year (condensing or not).
  - Flow temperature setting and emitter oversizing, which together give return temperature and therefore in-use efficiency (SAP 10 curve).
  - Controls present *and used*, setpoint, setback and schedule type.
  - Hot water draws (showers, baths, short draws) and cylinder or combi.
  - The household's comfort response to a change.
  - Gas use emerges from the existing thermal model with these attributes, so the boiler choices show up in the gas profile.
- **Heat pump.** Sizing against that home's heat loss, flow temperature and weather compensation, emitters, cylinder, and cycling or defrost behaviour. SPF emerges from these under that home's weather. It is not drawn.
- **Fabric.** The state of each element (loft depth, cavity filled or not, solid wall, glazing, draughts), feeding the building's heat-loss coefficient. Measured savings emerge, and the NEED medians are the population check.

## Costs and prices

- **Energy prices** come from the tariff the household is on, in that half hour. They are cap levels or the supplier's own tariff, built from the replayed or generated wholesale chain. Never use a fixed 26.32p or 7p.
- **Fuel prices for the EV counterfactual** come from a dated petrol and diesel series, replayed and then projected in the forward years.
- **Capex** (charger, panels, battery, heat pump, insulation) is a dated cost curve with a spread between homes. It is never one figure.
- **Grants, VAT and tax rules** carry their effective dates and apply when in force.

## What changes in the cover steer

- **"Now" item 2** is replaced. Before any further EV work, specify the EV person, vehicle and home attributes above and the derivation. The home-charging kWh band becomes a population check on what comes out. The "+65–120%" is removed.
- **"Now" item 3 (Economy 7)** stands, with the same rule: a two-rate meter is an attribute of a home with storage or other off-peak load. The 14–17% restricted-meter share is the population check.
- **Item 1 (the household asset world)** is to be built in this generative form. The attribute lists in the packs are the inventory. The packs' tables are explanation.
- **Item 3 (the savings grader)** rests on rule 4: every home has its own counterfactual.

## Ask

- Before you build, write a short design note in `docs/design/`: for each asset, list its attributes, the distribution each is drawn from and its source, the derivation to half-hourly energy, and the population checks. Name every attribute that has no published distribution as a design choice, rather than filling it in.
- Say whether anything already built reads a static percentage or price where it should derive one, and list it. The EV `+8%` path in Explore is the first case.
