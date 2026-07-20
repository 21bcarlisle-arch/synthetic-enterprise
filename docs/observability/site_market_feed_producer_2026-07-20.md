# New site-data producer registered: intra-day market feed (`market.json`)

**Date:** 2026-07-20
**Trigger:** director correction (2026-07-20) — "the annual-mean SSP is too coarse for an
operational window — I need to see what the market is *doing*, not its average. Wire the real
intra-day feed into the site pipeline properly rather than inventing one; register it if non-trivial."

This records the new producer so it is not invisible (per the "register it if non-trivial"
instruction — a new generator + pipeline wiring is non-trivial).

## Producer
- **Generator:** `tools/generate_market_data.py`
- **Reads (real source, not invented):** `docs/market_data/price_feed.json`
  (`{published_at, prices:[{fuel, period, price_gbp_per_mwh}]}` — 48 half-hourly electricity
  points + 10 daily gas points, ending at the settlement frontier ~2025-06-07).
- **Emits:** `site/data/market.json` — derived intra-day movement: latest price, session
  open/close/high/low/mean/range, last half-hour change (£ and %), a recent HH trajectory,
  and the `settlement_frontier` (== electricity as-of period). `available:false` on a
  missing/malformed feed (fail-closed, R15).
- **Consumer:** `site/world/index.html` "World state" panel — leads with the intra-day movement,
  keeps the settled annual mean/p95 as tail context.

## Wiring (the orphan-at-commit guard, both required)
1. **Regen:** `background/process_run_complete.py::generate_dashboard_json` — calls
   `gen_market()` in the Door-5 block (before `gen_world()`).
2. **Commit-list:** same file's `git_commit_push` — explicit `site_market_json` append
   (matching world/company/proof) **and** covered by the durable `site/data/*.json` glob.

## Clocks (R14) and the settlement lag (Directive 1)
Every figure carries its clock. The wholesale price is on the observed/wholesale clock, and its
**as-of is the latest feed period (~2025-06)**, NOT `published_at` (2026-07-17). The World panel
computes and shows the distance between the realised-weather clock (~2025-12) and this
settlement-frontier clock (~2025-06) — a **6-month settlement lag**, made legible rather than pinned away.

## DoD (met)
- Generator runs standalone, emits valid `market.json` — values hand-verified against the feed.
- Wired into regen call AND commit-list (verified by reading both).
- R11 render-harness tests + R15 mutation tests (mutate a price/date → rendered movement/lag
  follows) in `site/world/test_world_door.py`; generator-level derivation + fail-closed tests in
  `tools/test_generate_market_data.py`.
- `python3 -m pytest site/` green; `python3 -m tools.epistemic_verifier` PASS.
- SITE1_expert_doors left at `level_current: 2` (no self-promotion).
