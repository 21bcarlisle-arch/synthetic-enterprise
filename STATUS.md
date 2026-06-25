# Project Status

Last updated: 2026-06-25T15:45:00Z
Current phase: **Phase 59 COMPLETE** (2026-06-25). 1,428 tests passing.

## Current state

**Phase 59 (2026-06-25): Monthly gas consumption seasonality**
- `GAS_CONSUMPTION_MONTHLY_PROFILE` in `gas_settlement.py`: Jan=1.884, Jul=0.353, 5.3× ratio (UK DUKES)
- Per-day `daily_kwh = AQ/365 × seasonal × weather_factor` (composed with Phase 58 HDD factor)
- 10 new tests (1,428 total)

**Phase 58 (2026-06-25): Weather-adjusted gas consumption (HDD model)**
- `sim/weather_hdd.py` (new): `get_weather_factor(year, month, cid)` — HDD-based ratio vs UK 1991-2020 climate normals, clipped [0.3, 2.0]
- `simulation/gas_settlement.py`: `weather_factor` param scales daily_kwh; field in every record
- `simulation/run_phase2b.py`: resi/SME gas gets term-averaged factor; I&C process gas unchanged
- 15 new tests (1,418 total)

**Latest simulation results (2016-2025)** — auto-processed (commit cb88fe1, 489s):
- Revenue: £17,190,654 | Gross margin: £5,506,328 | Net margin: £5,269,031
- Final treasury: £2,749,581 | Enterprise value: £6,024,926 | Admin event: None (SURVIVED)
- Bad debt: £85,939 total (2022 resi 8% crisis peak); 1,549 bills; 43 committee interventions

**Five hollow gaps status:**
1. Customer events - DEEPENED (Phases 12b-16b, 17b, 23a, 50-52): smart meters, ToU, demand response
2. Ledger - CLOSED (Phase 7a/7b): 2.2M+ ledger events; P&L from transaction sum
3. SIM/company barrier - DIVERGENCE MEASURED + DEMAND FIXED (Phases 12e, 23a): epistemic verifier passes
4. HH data path - CLOSED (Phase 6a): C7-C9 on real HH consumption; ToU tariffs live (Phase 13a)
5. Reporting - CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline, GitHub Pages

1,428 tests passing.

Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
Status: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md
