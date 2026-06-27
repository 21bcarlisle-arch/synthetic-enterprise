# Simulation Status — LATEST

Last updated: 2026-06-27T03:51:00Z

## Current state

- **Phase:** 328 complete
- **Tests passing:** 4,470 (all green)
- **Python modules:** 291+
- **Company modules:** 230
- **Net position (latest sim run):** £1,330,126

## Phase 300 milestone summary

Starting from Phase 277 in this session, built 24 phases across:

- **7 non-commodity electricity cost ledgers:** CM, CfD, RO, FIT, DUoS, TNUoS, BSUoS
- **Cost-to-Serve Calculator:** unified per-unit economics (Ph294)
- **Ofgem Price Cap Book:** 26 quarters real data Q1-2019 to Q1-2025 (Ph295)
- **Trading infrastructure:** Margin Calls (Ph289), Counterparty Credit Limits (Ph290), Imbalance Ledger (Ph297)
- **Regulatory compliance:** REMIT Reporting (Ph296), Regulatory Dashboard (Ph300)
- **Customer operations:** CoS Process (Ph298), Supply Point Register (Ph299)
- **ESG/Sustainability:** ECO Obligation (Ph288), Decarbonisation Score (Ph279)
- **Regulatory protections:** WHD (Ph281), EBSS (Ph280), Consumer Duty (Ph283)
- **Reporting:** VaR Monitor (Ph282), Smart Meter Rollout (Ph284), FIT/RO/FMD books

## All company modules (219 total)

Finance (19): treasury, credit facility, P&L, double-entry, cash flow, payroll, budget,
working capital, margin calls, credit limits, management accounts, board KPIs, bad debt,
revenue accruals, period reconciliation, trade finance, company P&L, board dashboard

Market (22): forwards, day-ahead, intraday, gas OTC, gas storage, CfD levy, PPA,
capacity market, metering contracts, DUoS, TNUoS, BSUoS, imbalance, smart meter rollout

CRM (57): acquisition, retention, CLV/CAC, churn, CSS, NPS, campaign tracker,
behaviour segments, contact journey, CoS process, supply point register, vulnerability,
property improvements, energy profiles, home registry...

Regulatory (18): SFR, compliance scorecard, consumer duty, RO, FIT, FMD, EBSS, WHD,
ECO obligation, price cap, REMIT, regulatory dashboard

Risk (3): hedge policy, risk appetite, VaR monitor

Sustainability (1): decarbonisation score

Pricing (2): tariff smoothing, cost-to-serve

Compliance (1): consumer duty

Portal (2): app, templates

Interfaces (1): sim_interface

**Latest simulation results (2016–2025)** — auto-processed (485s / 8 min):
- Net margin: £6,322,835.71 | Gross: £6,559,770.69 | Capital: £236,935
- Treasury: £2,466,636 → £3,796,762 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,124,100.98 | Net after CTS: £6,454,351
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts