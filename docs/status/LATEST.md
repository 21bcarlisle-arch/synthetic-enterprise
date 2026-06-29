# Simulation Status — LATEST

Last updated: 2026-06-29T22:33:35Z

## Current state

- **Phase:** Y complete (ToU Rate Card Optimiser) -- T+U+V+W+X+Y shipped this session
- **Tests passing:** 5,057 (all green)
- **Python modules:** 328+
- **Company modules:** 230+
- **Net position (latest sim run):** £1,243,337

## Latest run figures (git 173b93c, 2026-06-29)

| Metric | Value |
|--------|-------|
| Total Revenue | £14,137,721 |
| Gross Margin | £6,462,146 |
| Net Margin | £1,243,337 |
| Enterprise Value | £6,142,209 |
| Administration Event | None |

## Recent build phases (P→I)

- **Phase P:** EV overnight smart-charging shape (12 tests). 90% overnight (periods 1-14, 47-48); triad periods now correctly low. Precondition for ToU tariff economics.
- **Phase S:** Unified Dual-Fuel Billing Engine + Payment Ledger (44 tests). DualFuelBill/DualFuelBillBook/PaymentLedger. Portal billing page.
- **Phase R:** SEG Export Estimator (21 tests). Wires SEGBook to solar customers via capacity-based estimation.
- **Phase Q:** Battery home energy storage settlement wiring (14 tests). Battery charges from excess solar, discharges in evening peak.
- **Phase O:** Solar dynamic settlement wiring (12 tests). Life-event solar now gets irradiance reduction in HH shape.
- **Phase N:** EV settlement wiring + physical suitability (26 tests). has_driveway/roof_aspect/hp_eligible gates.
- **Phase M:** Renewal Conversion Rate Book (21 tests). CRM lifecycle complete.
- **Phase L:** Tariff Segment Profitability Book (19 tests).
- **Phase K:** Break-Even Tariff Assessor (21 tests).
- **Phase I:** ASHP Seasonal Electricity Shape HDD-weighted (10 tests).

## Architecture

- SIM layer: half-hourly settlement, weather, household physics, life events
- SaaS layer: billing, risk, regulatory, CRM, finance
- Seam: company/interfaces/sim_interface.py (epistemic boundary)

→ Full history: docs/PROJECT_OVERVIEW.md | Report: docs/reports/ANNUAL_REPORT.md

**Latest simulation results (2016–2025)** — auto-processed (442s / 7 min):
- Net margin: £6,239,245.03 | Gross: £6,475,913.39 | Capital: £236,668
- Treasury: £2,466,636 → £3,709,973 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,037,509.08 | Net after CTS: £6,370,846
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts