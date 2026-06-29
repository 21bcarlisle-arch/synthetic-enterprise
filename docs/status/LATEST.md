# Simulation Status — LATEST

Last updated: 2026-06-29T14:57:50Z

## Current state

- **Phase:** N complete (EV Settlement Wiring + Physical Suitability Constraints)
- **Tests passing:** 4,861 (all green)
- **Python modules:** 325+
- **Company modules:** 230+
- **Net position (latest sim run):** £1,243,172

## Latest run figures (git 173b93c, 2026-06-29)

| Metric | Value |
|--------|-------|
| Total Revenue | £14,137,721 |
| Gross Margin | £6,462,858 |
| Net Margin | £1,243,172 |
| Enterprise Value | £6,142,209 |
| Administration Event | None |

## Recent build phases (N→G)

- **Phase N:** EV settlement wiring + physical suitability (26 tests). has_driveway/roof_aspect/hp_eligible gates.
- **Phase M:** Renewal Conversion Rate Book (21 tests). CRM lifecycle complete.
- **Phase L:** Tariff Segment Profitability Book (19 tests).
- **Phase K:** Break-Even Tariff Assessor (21 tests).
- **Phase J:** Customer Profitability Register (25 tests).
- **Phase I:** ASHP Seasonal Electricity Shape HDD-weighted (10 tests).
- **Phase H:** Electricity EAC Multiplier at Term Signing (12 tests).
- **Phase G:** ASHP Electricity Settlement Wiring (12 tests).

## Architecture

- SIM layer: half-hourly settlement, weather, household physics, life events
- SaaS layer: billing, risk, regulatory, CRM, finance
- Seam: company/interfaces/sim_interface.py (epistemic boundary)

→ Full history: docs/PROJECT_OVERVIEW.md | Report: docs/reports/ANNUAL_REPORT.md
