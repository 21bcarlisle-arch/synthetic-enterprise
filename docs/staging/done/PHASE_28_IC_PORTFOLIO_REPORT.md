# Phase 28: I&C Portfolio Section + Full Sim Run

## What's ready

All I&C product capabilities are now live (Phase 27a-e):
- C_IC1 (2 GWh warehouse, Birmingham) + C_IC2 (1 GWh office, Birmingham)
- CCL: I&C pays main rate (£5.44-7.35/MWh), resi exempt
- Volume tolerance: ±10% term-level tracking with excess/deficit P&L
- Triad risk: SSP-proxy identification, TNUoS tariff exposure per winter
- I&C churn: broker-driven model (20% base vs 10% resi)

## Phase 28a: I&C Portfolio Section in Annual Report

Add a dedicated I&C portfolio summary section to the annual report:

1. **I&C vs SME vs Resi margin comparison** — net margin per MWh by segment
   - I&C should show higher absolute margin but higher volatility
   - CCL is a significant pass-through cost at I&C volumes

2. **I&C portfolio summary table** — per customer per year:
   - Contracted kWh vs settled kWh, % variance
   - CCL cost (auto from settlement records)
   - Estimated TNUoS exposure (from triad_log)
   - Company churn estimate at each renewal

3. **Crisis-year I&C losses** — 2021-22 should show large losses for both I&C
   customers (2-3 GWh at £150-200/MWh contract vs £400+ spot). Report
   should make this visible and quantify it.

## Phase 28b: Full simulation run

After 28a, trigger a full sim run to get:
- Volume tolerance breach data (actual breaches vs calibrated profiles)
- Triad exposure figures for all winters 2016-2024
- CCL totals by year
- I&C churn rate in action (20% base → what actually happened?)
- I&C vs SME vs Resi net margin comparison in practice

This will be the first run with the complete I&C product stack active.

## Why now

The annual report sections for Phase 27b-e are backwards compatible (silent
when data absent). The next full run will populate them all simultaneously.
We need the I&C portfolio section (28a) first so it's ready for when the run
completes.

## Estimated scope

- Phase 28a: 1 new report section, 4-5 tests, ~2 hours
- Phase 28b: trigger run, review outputs, update LATEST.md, push
