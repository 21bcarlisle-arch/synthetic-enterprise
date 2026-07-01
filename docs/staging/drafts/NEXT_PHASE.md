Phase MS -- Real NBP Forward Curve

Replace the synthetic forward curve generator with a term structure model
fitted to real published NBP/EPEX seasonal forward strips (2016-2025).

Motivation: sim/forward_curve.py currently generates synthetic prices.
Every hedging, pricing, and risk decision the company makes is calibrated
against fabricated forward prices. This is the highest-fidelity gap in the sim.

Scope:
1. Identify available published NBP forward data (ICIS heren, EDF, Ofgem seasonal
   projections, or Elexon-adjacent sources). Document what is actually accessible.
2. If published strip data is available: ingest and store in sim/cache/.
   If not: calibrate synthetic curve parameters to match known seasonal benchmarks
   (OIES, Ofgem, NAO publications for 2016-2025 annual average NBP).
3. Fit a term structure (seasonal + carry): F(t,T) = spot * exp(seasonal(T) + carry*(T-t)).
4. Replace forward_curve.py generator with the fitted model.
5. Run full simulation 2016-2025. Confirm hedge fractions and margin move plausibly.
6. 15+ tests: curve shape, crisis-period premium, seasonal peaks, carry sign.
