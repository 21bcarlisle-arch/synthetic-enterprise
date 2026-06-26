# Synthetic Enterprise — Status

Last updated: 2026-06-26T09:18:36Z

## Latest Simulation Run
- **Git:** d1cd591 (run 2026-06-26T08:49)
- **Net Margin:** £1,330,126
- **Gross Margin:** £6,546,003
- **Revenue:** £14,215,256
- **Treasury:** £3,796,762
- **Enterprise Value:** £6,124,101
- **Administration Event:** No — SURVIVED

## Build State
- **Current Phase:** 216
- **Tests:** 3,001 passing
- **Session theme:** Financial layer + regulatory + market ops + CRM maturation (3k milestone)

## This Session (Phases 198-216)
- Ph 216: Network charge ledger (TNUoS/DUoS/BSUoS/CMSUoS; charge_gbp; charges_by_type) ★3k
- Ph 215: Supply contract lifecycle (FIXED_TERM 42d notice; IN_NOTICE state; expiring_within)
- Ph 214: Ancillary product bundle tracker (7 products; avg_products_per_customer; annual_revenue)
- Ph 213: Meter read validation (REVERSAL/EXCESSIVE/TRANSPOSITION; QUERIED/REJECTED)
- Ph 212: Wholesale price monitor (spot/M1/Q1; NORMAL→EXTREME; active_alerts)
- Ph 211: Payment behaviour analytics (ON_TIME/LATE/DD_FAILED/PARTIAL/MISSED; EXCELLENT→CRITICAL)
- Ph 210: Regulatory reporting calendar (PENDING/SUBMITTED/OVERDUE; due_within_days; by_regulator)
- Ph 209: Carbon emissions per customer (Scope 2 fuel mix; g/kWh by fuel type; total_co2_tonnes)
- Ph 208: Staff headcount and payroll (8 depts; employer NI + pension; cost_per_customer_gbp)
- Ph 207: Commodity hedging schedule (forward delivery by month; hedge_ratio_pct; over_hedged_months)
- Ph 206: Supply licence health monitor (6 SLC checks; is_going_concern; PASS/WATCH/BREACH)
- Ph 205: Capacity-to-Pay assessment (CANNOT_PAY/FUEL_POVERTY; recommended_action)
- Ph 204: Switch cooling-off and ET management (14-day right; 15-day objection; ET resolution)
- Ph 203: Outbound contact campaign tracker (7 types; CONVERTED/reached; by type)
- Ph 202: Revenue accruals ledger (BILLED/ACCRUED; accrual_ratio; monthly_summary)
- Ph 201: Bad debt provisioning model (IFRS 9 ECL; 5 aging buckets; 0.5-90% rates)
- Ph 200: Customer lifecycle state machine (10 stages; PENDING→ACTIVE→CHURNED)
- Ph 199: Annual regulatory obligations report (WHD/ECO4/GSOP/Ofgem/REGO; penalty estimates)
- Ph 198: Revolving credit facility (drawdown/repay; limit breach guard; interest accrual)

## Company layer: 154 files | CLAUDE.md: 140/200 lines

**Latest simulation results (2016–2025)** — auto-processed (477s / 8 min):
- Net margin: £6,322,835.71 | Gross: £6,559,770.69 | Capital: £236,935
- Treasury: £2,466,636 → £3,796,762 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,124,100.98 | Net after CTS: £6,454,351
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts