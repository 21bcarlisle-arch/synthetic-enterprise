# Phase 2b Summary — Gas Dual Fuel

## What Was Built
- `simulation/run_phase2b.py` — full dual-fuel orchestration: C1-C4 (resi, electricity PC1 + gas) and C5-C6 (SME, electricity PC3 only), terms processed chronologically across all ten customer/commodity legs against a single shared treasury. Progress logged every 100 settlement periods.
- `sim/gas_prices_history.py`, `sim/gas_data/nbp_sap.csv` — NBP System Average Price daily series (2016-01-01 to 2025-06-07, 3,446 records), sourced from FRED `PNGASEUUSDM` after the NGT MIPI portal required OAuth login. Converted USD/MMBtu → £/MWh at fixed GBPUSD=1.28.
- `simulation/gas_settlement.py` — daily gas settlement (AQ/365 flat consumption, CV/CF conversion per `docs/data-sources/gas-nbp.md`).
- `saas/customers.py` — C1g-C4g gas records (12,000 / 15,000 / 14,000 / 22,000 kWh AQ) for the four resi customers, same acquisition dates as their electricity records.
- `background/prefetch_elexon_ssp.py` + `sim/cache/elexon_ssp_full.json` (gitignored) — pre-fetched the full 2015-11-07..2025-06-07 SSP history (168,026 records) so the simulation hits cache instead of the live API.

## Key Findings
- **Full window survived (with active Context Handshake)**: net margin **£13,970.60** (electricity £10,850.17 + gas £3,120.43) over 2016-2025. Treasury grew £21,829.17 → £35,799.77. Capital cost ratio 50.9% of gross.
- **2021 remains the only net-loss year** (-£1,621.33) — but a smaller loss than the earlier (handshake-silent) run (-£2,002.62); 2022 and 2023 (crisis years) were both net-positive, with 2023 the best year of the run (£6,316.37 net).
- **Context Handshake fired 160 times** over the full window — all in 2016 through early 2023 (last wake-up 2023-03-08). After that the regime switches to `post-2023 (σ_stressed = 1.50)`, which raises the stressed-VaR floor enough that `VaR_current / VaR_stressed` stays below the 2.5× trigger for the rest of the window — no wake-ups 2023-03 through 2025-06. Full log: `docs/observability/risk-committee-log.md`.
- **The hedging tradeoff is now visible end-to-end**: vs. the earlier run where every wake-up failed silently (effectively hedge_fractions frozen at their initial values), the active committee progressively raised hedge_fractions (e.g. by 2023-03-08: C1=0.40, C2=0.20, C3=0.30, C4=0.40, C5=0.60, C6=0.50). This raised capital costs and **reduced total net margin by ~£2,829** (£16,799.11 → £13,970.60, all of the drop falling on the electricity book: £13,678.68 → £10,850.17; gas unchanged at £3,120.43, since gas VaR never breached the threshold) — but **reduced the 2021 crisis-year loss by ~£381** (-£2,002.62 → -£1,621.33). This is the Context Handshake doing exactly its job: trading average-case margin for tail-risk protection.
- **Gas never triggered a wake-up** — gas capital-cost ratio (29.4% of gross) and NBP volatility are low enough that gas-only VaR never approached the 2.5× stressed threshold; all 160 wake-ups were driven by the electricity book (C1, C5 in 2016; later C1/C3/C4/C5/C6 as the portfolio grew).
- **Context Handshake confirmed firing via local Ollama** (`qwen3:14b`, see the routing note in `sim/risk_committee_agent.py`, decision reversed 2026-06-12 — guardrail override from Rich: no justification for autonomous frontier API calls in a synthetic simulation). The earlier "0 wake-ups" figure was misleading: the VaR-breach threshold was firing every ~30 days (the committee cooldown) from the first settlement period, but every wake-up attempt failed silently on the `ANTHROPIC_API_KEY` auth error before reaching `_log_decision`, so nothing was logged. All 160 wake-ups in this run produced valid JSON reasoning and hedge_fraction adjustments, validated against the existing min +0.10 / max +0.30 / no-decrease clamps.

## Key Decisions Made
- **Performance fix (risk_committee.py)**: replaced an O(n) `max()` over up to 17,520 treasury-history entries, called every period once the 1,440-period committee cooldown elapses without a trigger, with a monotonic-deque O(1) amortized rolling-peak. Without this the full run never completed (stalled indefinitely after ~98,600 periods, ~2017-05).
- **Performance fix (sim/system_prices_history.py)**: switched to a `requests.Session()` for connection reuse — per-request TLS handshakes were costing ~12s/day (would have taken ~12hrs for the full prefetch); with reuse the full 3,501-day prefetch completed in ~13 minutes.
- **Bootstrap pricing for C1g's first term**: NBP gas data begins exactly 2016-01-01 — the same date as C1g's acquisition — so the standard 90-day prior lookback (`generate_forward_price`) and 365-day `calculate_sigma_recent` window are both empty for that one term. Added a one-time forward-looking-window bootstrap (mirrors the standard formula, draws from the first `lookback_days` of *available* data instead of prior data) for this single edge case only; every subsequent renewal uses the standard backward-looking windows unchanged.
- **`sim/cache/` gitignored**: the SSP prefetch cache is 123MB — over GitHub's soft limit. Regeneratable via `python3 -m background.prefetch_elexon_ssp`.

## Open Questions
- Gas volume risk (AQ vs actual consumption) is still flat/synthetic — real gas demand is far more weather-sensitive than electricity; worth flagging for the weather-correlation backlog item.
- The committee never re-tightens hedge_fractions downward (by design — "never decrease"). Worth a future discussion on whether a separate, symmetric "de-risking" lever belongs in scope once the post-2023 regime keeps VaR comfortably below threshold for 2+ years.

## Token Efficiency
- Frontier: orchestration (`run_phase2b.py`), the two performance fixes, and the C1g bootstrap fix — all hand-written per the "orchestration touching schemas" delegation lesson from Phase 1e.
- Local: none this session (background worker handled the SSP prefetch).
- Output: ~510-line orchestration script, 2 reusable risk-engine fixes, full 9.5-year dual-fuel simulation result.
