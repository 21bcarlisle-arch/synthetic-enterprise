# PROPOSAL — heating above flex, and gas in the carbon a customer is shown (2026-10-05)

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `heating-above-flex-and-gas-in-the-carbon-shown` (Lane 0 delivery)

**For the director.** Your carbon investigation, step 1 of DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05. The knowledge is at `site/knowledge/household-carbon-and-the-measures-that-save-it/`; its research, sources and gaps are in `docs/market_research/household_carbon_and_the_measures_that_save_it.md`. Your direction is that carbon's job is to show customers what they have saved and could save. Read against that, the evidence argues for three changes.

## What the evidence says

**Heating is most of a home's carbon, more so every year.** For Ofgem's typical medium gas-heated home, gas carbon divided by electricity carbon:
- 2.4x in 2016;
- 4.1x in 2020;
- 5.9x in 2024;
- 5.8x in 2025.

The gas factor moved 0.6% over the decade; the household's electricity intensity fell 57%. "About five times" is right now and was not in 2016.

**Our knowledge and code lean the other way:**
- 21 research documents that discuss carbon are about electricity timing, against 4 on insulation.
- None held a household gas carbon figure until today.
- The only household carbon figure the company publishes (`company/carbon/half_hourly_footprint.py`, `site/data/explore_carbon.json`) counts electricity only: about 15% of a typical home's carbon. It would show a heat pump as a carbon INCREASE.

**Your three claims hold, with numbers:**
- **EV:** saves about 1.8 t CO2e a year in total, but roughly doubles the home's electricity carbon. The supplier can only estimate the avoided petrol.
- **Solar:** carbon displaced per kWp fell from 253 kg (2016) to 82-94 kg (2024-25), while its money per self-used kWh roughly doubled. It is now a money decision.
- **Heat pump:** carbon-led on flat tariffs in every price-cap period, saving 46% to 77% of heating carbon, but £60-260 a year dearer. It is win-win on a heat-pump tariff or against an old boiler.

**Flex is small in carbon.** Moving one kWh from evening to night saves about 36 g at the real 2025 half-hourly spread; not burning one kWh of gas saves 183 g.

## Proposals

1. **Within step 5's value-add lever, heating measures rank above flex.** Next best action order:
   1. zero-cost heating behaviour (thermostat, flow temperature);
   2. cheap insulation and controls;
   3. heat pump with our own heat-pump tariff, which makes it win-win;
   4. EV with smart charging;
   5. solar and battery, sold as the money products they now are;
   6. time-of-use shifting.

   The seven steps themselves are unchanged.
2. **Gas goes into the household carbon figure before any customer sees it.** I am treating this as a plain error and fixing it now. A figure that omits 85% of the carbon, and inverts the sign of the biggest measure, contradicts your stated purpose for carbon. The gas factor is already in code, and gas meter reads already reach the company.
3. **Step 1 gains "home heating as a product",** alongside EV, solar and batteries.

## What a supplier can honestly show

- **From its own meters:**
  - reduced gas;
  - the gas account closing with a heat pump's electricity arriving;
  - smart-charging shifts.
- **Only estimated:** avoided petrol.

A "you saved X kg" statement should say which kind each figure is.
