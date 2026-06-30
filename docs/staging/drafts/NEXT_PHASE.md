# Phase HL: Net Open Position Register — Test Coverage

**Proposed:** 2026-06-30
**Target file:** company/trading/net_open_position_register.py (existing module, zero tests)
**Estimated tests:** 28-35
**Connects to:** bsc_credit_register (FI), wholesale_trading_mandate_register (HH), bsc_performance_assurance_register (HK)

## What it models

NOP (Net Open Position) = forward purchases (MWh) - retail commitment (MWh).
A negative NOP = more retail than hedges = long-retail, short-market = bears wholesale risk.
A positive NOP = overhedged = wasteful capital deployment.

This is the core risk metric Ofgem's Financial Resilience Assessment (FRA) uses.
During 2022, suppliers with large long-retail positions (NOP < 0) faced catastrophic
losses when wholesale prices spiked -- many failed. This module tracks the company's
own NOP across delivery periods and commodities.

## Domain facts

- NOP: retail_commitment_mwh - forward_position_mwh per delivery quarter/commodity
- Direction: LONG_RETAIL (NOP < -5%), FLAT (within ±5%), OVERHEDGED (NOP > 5%)
- Severity: GREEN (<20% abs pct), AMBER (20-40%), RED (>40%)
- Epistemic: company reads own trade blotter + estimated retail commitment
- Distinct from: imbalance_ledger (settlement imbalance), forward_book (forward contract management)
