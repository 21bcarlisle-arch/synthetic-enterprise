# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-25T21:29:45Z

**Phase 64 COMPLETE (2026-06-25):** FI1 Management Accounts from double-entry journal -- 13 new tests (1,493 total).
- company/finance/management_accounts.py (new): build_monthly_accounts(), annual_management_pack(), cross_check()
- P&L now emerges from account codes (4001=revenue, 5001+5100=COGS, 5200=capital, 6xxx=opex) not formulas; FI1 closed
- Annual report: 10-year management accounts table + final-year balance sheet + cross-check vs simulation net

**Phase 63 COMPLETE (2026-06-25):** F1 Double-entry ledger — 24 new tests (1,480 total).
- `company/finance/double_entry.py` (new): 13 account codes (1xxx–6xxx), `to_journal_entry()` for all 9 ledger event types
- `trial_balance()`, `income_statement()`, `balance_sheet()` — Assets = Liabilities + Equity verified
- Foundation for FI1 management accounts and C1 customer invoices (Destinationvision.md F1)

**Phase 62 COMPLETE (2026-06-25):** Standing charges (electricity + gas, resi/SME) -- 12 new tests (1,456 total).
- `simulation/policy_costs.py`: Ofgem tariff tracker year-indexed SC tables; resi elec 24p/day (2016) -> 61p/day (2024), gas 22p->31p; SME 1.5x; I&C=0
- `hedged_settlement.py`: SC prorated per half-hour, added to revenue+margin; `standing_charge_gbp` field per record
- `gas_settlement.py`: daily SC in `gas_standing_charge_gbp` field

**Phase 61 COMPLETE (2026-06-25):** Flex tariff policy pass-through fix — 8 new tests (1,444 total).
- `run_flex_term()` in `hedged_settlement.py`: revenue now includes policy+network recovery (pass-through to customer)
- C_IC4 total net swings from -£1.06M to +£33k; prior model had supplier absorbing all policy costs

**Phase 60 COMPLETE (2026-06-25):** I&C gas flat seasonal profile — 8 new tests (1,436 total).
- `GAS_IC_CONSUMPTION_MONTHLY_PROFILE`: Jan=1.075, Jul=0.913, 1.18× ratio vs resi 5.3×
- `run_gas_term()` selects profile by segment; Phase 59 was applying resi heating swing to 5M kWh I&C

**Phase 59 COMPLETE (2026-06-25):** Monthly gas consumption seasonality — 10 new tests (1,428 total).
- `GAS_CONSUMPTION_MONTHLY_PROFILE` in `gas_settlement.py`: Jan=1.884, Jul=0.353, 5.3× winter/summer ratio (DUKES Table 4.3)
- Per-day `daily_kwh = AQ/365 × seasonal × weather_factor`; prior model was flat AQ/365 every day
- Combined with Phase 58 HDD factor: resi gas has both within-year shape AND year-to-year deviation

**Phase 58 COMPLETE (2026-06-25):** Weather-adjusted gas consumption (HDD model) — 15 new tests (1,418 total).
- `sim/weather_hdd.py` (new): HDD = max(0, 15.5°C - mean_temp); UK 1991-2020 climate normals; `get_weather_factor()` [0.3, 2.0]
- `simulation/gas_settlement.py`: `weather_factor` param scales daily_kwh; resi/SME only — I&C process gas unchanged
- 2019-2020 warm winter reduces resi gas demand; Jan 2021 cold snap increases it

**Phase 57 COMPLETE (2026-06-25):** Year-varying bad debt (crisis surge) — 9 new tests (1,403 total).
- `saas/cost_to_serve.py`: `get_bad_debt_rate(year, segment)` — 2021 resi 4%, 2022 resi 8% (Ofgem 2.4M in arrears), 2023 5%
- `simulation/run_phase2b.py`: bad_debt_gbp deducted from net_margin_gbp + treasury each settlement record
- Solvency dedup fix: MCR ratio now uses billing-account count (C1+C1g = 1, not 2)

**Phase 56 COMPLETE (2026-06-25):** Gas pass-through hedge zero-lock — 5 new tests (1,394 total).
- `simulation/run_phase2b.py`: gas pass-through customers now `hf=0.0` (was 0.85 from RESET default)
- Wrong-way risk eliminated: C_IC3g showed +42% gas margin in 2021 (hedge windfall) and -86% in 2023 (loss on reversion)
- Margin now = service_fee + network + policy only; no forward price exposure for spot-indexed contracts

**Phase 55 COMPLETE (2026-06-25):** Ofgem MCR solvency signal — 12 new tests (1,389 total).
- `saas/capital/solvency.py` (new): `compute_solvency_signal()` → Watch < 2×, STRESS < 1× (below £130/account floor)
- `_section_solvency_signal()` upgraded with formal MCR ratio and status columns in annual report
- ASSUMPTIONS.md: price cap rows (38/41) updated — gas+electricity cap IS applied since Phase 47a

**Phase 54 COMPLETE (2026-06-25):** Supplier mutualization levy — 8 new tests (1,377 total).
- `simulation/policy_costs.py`: `_MUTUALIZATION_LEVY_BY_YEAR` + `get_mutualization_levy_per_mwh()`
- 2021: £4.14/MWh (17 SoLR events); 2022: £10.00/MWh (Bulb SAR + BSC shortfall recovery)
- Applied in all 3 electricity settlement paths; annual report policy table extended

**Phase 53 COMPLETE (2026-06-25):** BSC credit cover — 14 new tests (1,369 total).
- `saas/capital/bsc_credit.py` (new): peak daily electricity wholesale cost × 1.2 buffer
- Annual report: per-year BSC credit cover vs treasury table; 2022 crisis = £10k cover (363× 2016)
- Coverage ratio < 5× flagged Watch; < 2× flagged STRESS; realistic capital stress signal

**Phase 52 COMPLETE (2026-06-25):** ToU demand response — 24 new tests (1,355 total).
- `saas/demand_response.py` (new): peak→off-peak load shift (base 15% + EV +12% + heat_pump +8%)
- `make_shifted_shape_fn()` wraps consumption shape for ToU-eligible customers
- Watchdog: exponential API backoff (1m/2m/5m/10m), NTFY on failure + hourly while down

**Phase 51 COMPLETE (2026-06-24):** ToU eligibility gate — 9 new tests (1,330 total).
- `is_tou_eligible(customer)` in `saas/smart_meter_rollout.py`: True if HH-metered OR smart_meter=True
- Acquired customers with smart meters (from Phase 50 rollout model) now get peak/off-peak pricing

**Test suite: 1,493 total (all saas/company/tools passing)**

**Latest simulation results (2016–2025)** — auto-processed (464s / 8 min):
- Net margin: £6,322,835.71 | Gross: £6,559,770.69 | Capital: £236,935
- Treasury: £2,466,636 → £3,796,762 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,124,100.98 | Net after CTS: £6,454,351
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts