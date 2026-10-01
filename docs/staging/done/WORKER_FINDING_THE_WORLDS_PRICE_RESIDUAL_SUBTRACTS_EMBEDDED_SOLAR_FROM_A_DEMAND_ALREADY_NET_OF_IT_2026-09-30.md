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

**Addendum, 2026-09-30 (EP13 s20).** INDO also EXCLUDES interconnector exports, and the carbon
shape now serves them (`exports_by_period`, per-cable). That moved the carbon model's 2022 gas
level from −1.7 GW to +0.5 GW against metered CCGT. The same price residuals above take INDO
without exports, so 2022, GB's heaviest export year, is the year their x-axis is shortest. A
refit should test `INDO + exports − wind` alongside `INDO − wind`, not only the solar change.

## Closed (2026-10-01, autonomous worker): the fit had not absorbed an error, and the double count earns its place

Measured against a pre-registration filed before the run:
`records/WORKER_PREREGISTRATION_THE_PRICE_RESIDUALS_AXIS_REFIT_ON_INDO_LESS_WIND_2026-10-01.md`.
The fit holds out one year at a time over 2016–2025.

- **INDO − wind:** pooled held-out MAE is **1.4% worse** than the shipped axis, and 3.7% worse at
  summer middays.
- **INDO + exports − wind:** 4.9% worse, and 8.3% worse in 2022.

A free solar weight has its held-out optimum at β of 1 to 1.5, on top of INDO. That is where the
shipped form already sits. **No price changes.** For a price fit, `RD` is a regressor, not a physical
quantity. `sim/price_engine.py` now says so at the line, so the obvious "fix" is not made. The carbon
shape's physical definition (EP13 s19–s20) is unaffected.
