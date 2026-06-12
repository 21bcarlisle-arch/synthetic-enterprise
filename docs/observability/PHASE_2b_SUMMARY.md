# Phase 2b Summary — Gas Dual Fuel

## What Was Built
- `simulation/run_phase2b.py` — full dual-fuel orchestration: C1-C4 (resi, electricity PC1 + gas) and C5-C6 (SME, electricity PC3 only), terms processed chronologically across all ten customer/commodity legs against a single shared treasury. Progress logged every 100 settlement periods.
- `sim/gas_prices_history.py`, `sim/gas_data/nbp_sap.csv` — NBP System Average Price daily series (2016-01-01 to 2025-06-07, 3,446 records), sourced from FRED `PNGASEUUSDM` after the NGT MIPI portal required OAuth login. Converted USD/MMBtu → £/MWh at fixed GBPUSD=1.28.
- `simulation/gas_settlement.py` — daily gas settlement (AQ/365 flat consumption, CV/CF conversion per `docs/data-sources/gas-nbp.md`).
- `saas/customers.py` — C1g-C4g gas records (12,000 / 15,000 / 14,000 / 22,000 kWh AQ) for the four resi customers, same acquisition dates as their electricity records.
- `background/prefetch_elexon_ssp.py` + `sim/cache/elexon_ssp_full.json` (gitignored) — pre-fetched the full 2015-11-07..2025-06-07 SSP history (168,026 records) so the simulation hits cache instead of the live API.

## Key Findings
- **Full window survived**: net margin **£16,799.11** (electricity £13,678.68 + gas £3,120.43) over 2016-2025. Treasury grew £21,829.17 → £38,628.27.
- **2021 was the only net-loss year** (-£2,002.62) — consistent with Phase 1e/2a findings; 2022 and 2023 (crisis years) were both net-positive, with 2023 the best year of the run (£8,358.68 net).
- **Gas is a smaller, steadier contributor**: gas capital-cost ratio is 29.4% of gross vs electricity's 55.4% — gas volumes are smaller and NBP volatility (feeding sigma_recent) is lower than SSP's, so collateral requirements are proportionally lighter.
- **Context Handshake: confirmed firing (2026-06-12)** — the "0 wake-ups" figure above was misleading: the VaR-breach threshold (`VAR_BREACH_MULTIPLIER=2.50`) was firing every ~30 days (the committee cooldown period) from the very first settlement period (VaR ratio 3.25 in the pre-2023 regime), but every wake-up attempt failed silently on the `ANTHROPIC_API_KEY` auth error before reaching `_log_decision`, so nothing was logged.
- **Risk committee now routed through local Ollama** (`qwen3:14b`, see the routing note in `sim/risk_committee_agent.py`, decision reversed 2026-06-12 — guardrail override from Rich: no justification for autonomous frontier API calls in a synthetic simulation). A 10-minute smoke test of the re-routed agent produced 16 real wake-ups across Jan-Apr 2016 alone, each with valid JSON reasoning and hedge_fraction adjustments (e.g. C1 0.50 → 0.80, C1+C5 0.50 → 0.70/0.80), validated against the existing min +0.10 / max +0.30 / no-decrease clamps. Full log: `docs/observability/risk-committee-log.md`.
- **Full 9.5-year re-run launched** (background, started 2026-06-12 ~18:05 UTC, `python3 -m simulation.run_phase2b`) — with the committee now actually executing on its ~30-day cooldown across the whole window, this run will take materially longer than the original (each wake-up costs ~30-50s of local-model latency). Results (updated net margin, full Context Handshake wake-up count, treasury trajectory) to follow once complete.

## Key Decisions Made
- **Performance fix (risk_committee.py)**: replaced an O(n) `max()` over up to 17,520 treasury-history entries, called every period once the 1,440-period committee cooldown elapses without a trigger, with a monotonic-deque O(1) amortized rolling-peak. Without this the full run never completed (stalled indefinitely after ~98,600 periods, ~2017-05).
- **Performance fix (sim/system_prices_history.py)**: switched to a `requests.Session()` for connection reuse — per-request TLS handshakes were costing ~12s/day (would have taken ~12hrs for the full prefetch); with reuse the full 3,501-day prefetch completed in ~13 minutes.
- **Bootstrap pricing for C1g's first term**: NBP gas data begins exactly 2016-01-01 — the same date as C1g's acquisition — so the standard 90-day prior lookback (`generate_forward_price`) and 365-day `calculate_sigma_recent` window are both empty for that one term. Added a one-time forward-looking-window bootstrap (mirrors the standard formula, draws from the first `lookback_days` of *available* data instead of prior data) for this single edge case only; every subsequent renewal uses the standard backward-looking windows unchanged.
- **`sim/cache/` gitignored**: the SSP prefetch cache is 123MB — over GitHub's soft limit. Regeneratable via `python3 -m background.prefetch_elexon_ssp`.

## Open Questions
- Gas volume risk (AQ vs actual consumption) is still flat/synthetic — real gas demand is far more weather-sensitive than electricity; worth flagging for the weather-correlation backlog item.
- Pending: headline net margin / treasury figures for the full re-run with the Context Handshake actually firing throughout (in progress as of 2026-06-12).

## Token Efficiency
- Frontier: orchestration (`run_phase2b.py`), the two performance fixes, and the C1g bootstrap fix — all hand-written per the "orchestration touching schemas" delegation lesson from Phase 1e.
- Local: none this session (background worker handled the SSP prefetch).
- Output: ~510-line orchestration script, 2 reusable risk-engine fixes, full 9.5-year dual-fuel simulation result.
