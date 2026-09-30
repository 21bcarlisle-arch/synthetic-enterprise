**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** EP13_adapter_carbon_intensity (sibling defect)
**Evidence:** `docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` s18-s19; `sim/price_engine.py:205`, `sim/merit_order_reconstruction.py:394`, `background/fidelity_emitter.py:169`, `simulation/run_phase3b_calibration.py:59`

# The world's price residual subtracts embedded solar from a demand already net of it

**2026-09-30.** Found by a scheduled-tick worker while fixing the same definition in the carbon
shape (EP13 s19). That fix is landed and covers only `sim/grid_carbon_intensity.py` and the feed.

INDO is transmission demand and is already net of embedded generation. GB solar is embedded.
EP13 s18 found that subtracting AGWS solar from INDO a second time hid about 1.3 GW of gas in every
year. It carried 0.40 of the daily gas-level variation in 2019–21.

The same residual, `RD = INDO − (AGWS wind + solar)`, is the price model's x-axis in:
- `sim/price_engine.system_margin_price` (`residual_demand_mw = demand_mw - renewable_generation_mw`),
  calibrated by `simulation/run_phase3b_calibration.py` on `aggregate_renewable_generation`;
- `sim/merit_order_reconstruction.py:394`;
- `background/fidelity_emitter.py:169` (`x = (demand_mw - renewable_mw) / DISPATCHABLE_CAPACITY_MW`).

**Why this is not fixed in the same pass.** Those models were FITTED on this definition, so their
parameters have absorbed the error. A midday residual understated by solar has been mapped onto
real SSP. Changing the input without refitting would move the world's prices, and refitting is a
world-fidelity change that has to be decided blind to company results. It is its own piece of work.

**What would settle it.** Refit `system_margin_price` on `INDO − wind` and compare the
held-out SSP error against the current fit. If the error falls, the definition was costing
fidelity. If it does not, the fit had absorbed the error and the only gain is honesty of the axis.
Say which before changing any price.

`sim/weather_price_chain.py` already splits solar out as its own regressor, so it is not affected.
