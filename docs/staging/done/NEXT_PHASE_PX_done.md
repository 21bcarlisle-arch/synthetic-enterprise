# NEXT PHASE PROPOSAL: Phase PX -- Correlated Synthetic Market Generator

## Gap addressed
Phase PV (Market Feed Swappable Adapter) built the MarketDataPort architecture and explicitly
named correlated synthetic generator (endgame) in its key architecture note. The current
live decisions module (PU) is frozen to a single 2025-06-07 market snapshot via Frozen2025Adapter.
CLAUDE.md flags regime-change blindness as a known failure mode: the company converged to
near-naked hedging during calm 2016-2020 data, directly before the crisis. A real UK energy
supplier stress-tests hedging and renewal decisions against multiple plausible market scenarios.

## What real fidelity is gained
1. Company generates correlated electricity+gas price paths using a calibrated statistical model
   rather than being locked to a frozen historical snapshot.
2. Forward curve computed analytically from the model (contango/backwardation), not a fixed
   offset over a single historical point.
3. Regime switching explicitly modelled: can sample in low-vol (normal) or high-vol (crisis)
   regime, matching the observed 2021-22 volatility spike.
4. CorrelatedGeneratorAdapter drops in as MARKET_ADAPTER_SOURCE=synthetic with zero company-layer
   changes (PV guarantee maintained). Frozen2025Adapter remains default.
5. Enables future scenario stress testing: board can request base/bull/bear market decisions
   without touching company layer code.

## Architecture

New file: tools/market_adapters/synthetic_generator.py
  CorrelatedGeneratorAdapter(seed=None, regime="normal")

  Calibrated constants (from 2016-2025 NBP+SSP data):
    GAS_LONG_RUN_MEAN_GBP_PER_MWH = 54.0   (post-2023 ~25p/th normalisation)
    ELEC_LONG_RUN_MEAN_GBP_PER_MWH = 85.0  (post-2023 normalisation)
    GAS_MEAN_REVERSION_SPEED = 0.5          (half-life ~18 months)
    ELEC_MEAN_REVERSION_SPEED = 0.6         (faster reversion; weather-driven)
    GAS_VOL_NORMAL = 0.35                   (35% annualised; normal regime)
    GAS_VOL_CRISIS = 1.20                   (120% annualised; calibrated to 2021-22)
    ELEC_VOL_NORMAL = 0.45
    ELEC_VOL_CRISIS = 1.50
    ELEC_GAS_CORR = 0.70                    (cross-commodity correlation)
    CRISIS_REGIME_PROB = 0.08               (8% of months; 2 of 25 years in crisis)
    FORWARD_CONTANGO_ANNUAL = 0.02          (2%/year storage/carry)

  Bivariate OU step:
    x(t+dt) = x(t) + kappa*(mu - x(t))*dt + sigma*sqrt(dt)*Z
    [Z_gas, Z_elec] drawn from bivariate normal with corr=ELEC_GAS_CORR

  Methods satisfying MarketDataPort:
    get_spot_elec_gbp_per_mwh(as_of=None) -> float
    get_spot_gas_gbp_per_mwh(as_of=None) -> float
    get_forward_price(as_of=None, delivery_date=None, commodity="electricity") -> float
    get_market_summary(as_of=None) -> dict  (same shape as Frozen2025Adapter)

Modified: tools/market_adapters/__init__.py
  Register source="synthetic" -> CorrelatedGeneratorAdapter

No company-layer changes (PV guarantee maintained).

## Epistemic check
CorrelatedGeneratorAdapter is the companys own price model -- built from publicly
observable market statistics (NBP/SSP historical data). No SIM internals. PASS.

## Test targets (~18 tests)
1. OU gas spot stays within plausible range (2-300 GBP/MWh) over 1000 steps
2. OU elec spot stays within plausible range (5-1000 GBP/MWh) over 1000 steps
3. Gas mean-reversion: long simulation mean within 20% of GAS_LONG_RUN_MEAN
4. Elec mean-reversion: long simulation mean within 20% of ELEC_LONG_RUN_MEAN
5. Elec-gas correlation positive (Pearson r > 0.5) over 1000 samples
6. Same seed -> same spot prices (reproducibility)
7. Different seeds -> different spot prices
8. get_forward_price contango: delivery_date=3mo ahead > spot (normal regime)
9. get_forward_price returns float, not NaN/None
10. get_market_summary() returns same top-level keys as Frozen2025Adapter
11. get_market_summary()[spot_electricity_gbp_per_mwh] matches get_spot_elec()
12. Factory resolves synthetic -> CorrelatedGeneratorAdapter instance
13. Factory raises ValueError on unknown source (regression)
14. Factory resolves frozen_2025 -> Frozen2025Adapter instance (regression)
15. Crisis regime produces higher volatility than normal regime
16. MarketDataPort protocol: isinstance(CorrelatedGeneratorAdapter(), MarketDataPort) == True
17. Spot prices are positive (no negative prices in 10000 steps, normal regime)
18. as_of param accepted without error (interface compliance)

## Expected outcome
MARKET_ADAPTER_SOURCE=synthetic enables the company to run decisions against a statistically
sound forward-looking price model. Frozen2025Adapter remains the default for live production
decisions; synthetic enables scenario analysis and stress testing. Regime-change blindness
failure mode (CLAUDE.md known failure) is directly addressed: company can request a crisis-regime
market summary and see what hedging/renewal decisions look like under 2021-22 volatility.
