Phase 268 -- /sim/ Section Stub: Wholesale Prices with Real Elexon SSP Data

Status: PROPOSED (2026-06-26)

The nav bar at poesys.net has a /sim/ link marked as "dim" (disabled).
Phase 268 enables it with a first page: a wholesale electricity price
explorer using the real Elexon SSP data already in the simulation.

Goal: give the /sim/ section a landing page that showcases the underlying
market data driving the simulation.

Design:
- site/sim/index.html (new): Wholesale Price Explorer page.
- Nav /sim/ link un-dimmed.
- Loads wholesale price data from site/data/market_data/ (already exists:
  price_feed.json and consumption_feed.json from background processes).
- Displays: spot price chart (monthly mean, P95) 2016-2025, crisis period
  overlay (2021-2022), peak half-hour records, year summary table.
- tools/generate_sim_data.py (new): extracts wholesale summary from
  docs/market_data/price_feed.json or run output into site/data/sim_data.json.
- process_run_complete.py: call generate_sim_data on every run.

Estimated: ~7 tests (sim/index.html exists, nav un-dimmed, generate_sim_data
produces valid JSON, data has crisis years, peak price >£500/MWh in 2022).
