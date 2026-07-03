## Phase PU COMPLETE -- Shadow Live Operation (P4 MVP)
Last updated: 2026-07-03T22:50:13Z

**Status:** COMPLETE. 15,314 tests passing.

**Phase PU -- Shadow Live Operation (P4 MVP):**
- tools/project_portfolio_to_2026.py: extracts active customers as of 2025-12-31; EAC, hedge fractions, last renewal from customer_events
- tools/live_market.py: Elexon SSP cache (2025-06-07 as-of) + price_feed.json fallback; gas forward = gas_spot x 1.05
- tools/run_live_decisions.py: renewal window 60 days; hedge INCREASE/HOLD/REDUCE vs 50-90% band; acquisition price ladder by segment
- KEY FINDING: C9 in renewal window (22 days), proposed 153.49 GBP/MWh vs current 210.0 (market fallen 2022->2025); hedge rec INCREASE (most pass-through I&C at 0% hf). SIM is no longer retrodiction-only.
- Wired into process_run_complete.py; outputs site/state/live_portfolio.json + site/state/live_decisions_latest.json

**Latest simulation results (2016-2025)** -- auto-processed (478s / 8 min):
- Net margin: GBP 1,445,258 | Gross: GBP 6,467,309 | Capital: GBP 51,433
- Treasury: GBP 2,466,636 -> GBP 3,911,894 | 38 committee interventions | 1,605 bills issued
- Enterprise value: GBP 8,826,939 | Net after CTS: GBP 6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts
- Hedging cost: GBP 4,232,037 vs going naked | Net margin 7.7% of revenue (benchmark: 2-5%)
- I&C: 99.5% of net margin (concentration risk: RED)
