# LATEST -- Synthetic Enterprise Simulation
Last updated: 2026-07-03T18:51:35Z

## Current Status
Phase OL COMPLETE (2026-07-03) -- Carbon Emissions: FuelMixRecord 2016-2025; scope 2+1; 290->175g/kWh trend. 17 tests, 15,148 total.

Website fixes deployed (2026-07-03):
- Supplier dashboard: kpi() function + CSS added -- Regulatory and Capabilities tabs now render correctly.
- Customer portal: JS string bug fixed (line 208 kpi-value class attribute was broken) -- portal now renders account details.
- Annual report: management_accounts None guard fixed (was crashing on empty ledger).

## Last Run
Net position: £1,445,258 (git 3a370587, 2026-07-03)
Revenue: GBP 14,060,576 | Treasury: GBP 3,911,894 | EV: GBP 8,826,939

## Test Suite
- **15,148 tests passing**
- Epistemic verifier: PASS
- PRIORITIES.md: OM (Fuel Mix Disclosure) next

**Latest simulation results (2016–2025)** — auto-processed (989s / 16 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 37 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts