# Proposed Phase 10a — Segment Customer Model

## What Rich asked for

Two NTFY messages (2026-06-20 07:21 and 07:32):
1. "Maybe we treat customers as segments not individuals. Each one represents ~100 customers.
   Churn and sales are changes in the number of customers in each segment. Economies of
   scale get more sensible."
2. "Lets keep smart customers as separate. But maybe what we have is the same customer
   segments but smart and not smart version? Then we can also model the flow from non to smart."

## Why this is the right call

The current model has 9 named accounts. The overhead problem I flagged earlier (£50/month /
9 accounts = £5.56/customer/month overhead, making net margins look falsely healthy) is
structural. Switching to segments of ~100 customers fixes it naturally: the same £50/month
overhead divided over 100+ residential customers is £0.50/customer — credible.

More importantly, it's how real energy suppliers actually model their portfolio. Individual
named customers are a first-pass simplification; cohort-based segment economics are the
operating reality.

## Proposed segment structure

| Segment | Meter type | Starting headcount | Notes |
|---------|-----------|-------------------|-------|
| Residential Standard | Profile class | 150 | Core domestic book |
| Residential Smart | HH | 20 | Smart meter customers; flows from Standard |
| SME Standard | Profile class | 40 | Small business electricity |
| SME Smart | HH | 5 | Smart business customers |
| Gas Residential | Profile class | 80 | Dual-fuel gas legs |

Total: ~295 "customers" (comparable to a micro-supplier launch book).

## Smart meter flow

Each year, a fraction of Residential Standard customers get a smart meter installed and
transition to Residential Smart. The UK rollout target was ~85% smart by 2025. We model:
- `smart_upgrade_rate`: proportion of Standard segment upgrading per year (e.g. 3-8%/yr,
  accelerating 2019-2025 to match the actual rollout curve)
- Upgrades move headcount from Standard → Smart; their consumption profile switches from
  profile-class shapes to HH consumption data
- This is the "non to smart" flow

## How the segment model works mechanically

**Volume**: `segment_kwh = avg_annual_consumption_per_customer × headcount × weather_factor`
  - Each segment has a mean annual consumption (e.g. residential: 3,100 kWh/yr/customer)
  - Weather scaling applied at segment level via the existing weather engine

**Revenue**: same bill-generation logic, applied to segment volume

**Churn/acquisition**:
  - Churn: `churned = round(headcount × churn_rate)` — rate from existing churn model
    calibrated to segment characteristics (bill-shock driven, same physics)
  - Acquisition: `won = round(attempts × win_rate)` — attempts as a strategy parameter,
    win rate from existing home_move_win_rate model
  - Both fire annually at renewal; headcount updates mid-year

**Overhead scaling**:
  - Fixed overhead now expressed per-customer (e.g. £0.50/customer/month cost-to-serve
    for Standard, £1.20/customer/month for Smart — metering data services cost more)
  - Total overhead = sum over segments of (headcount × rate × months)
  - This immediately makes the unit economics credible at any scale

## What stays the same

- All hedging physics (mandate, VaR, risk committee) — unchanged, just runs on segment
  aggregate volume
- Weather engine — unchanged, segment volume scales with weather factor
- Forward curve, capital cost, settlement — unchanged
- Annual report structure — segment-level rather than customer-level sections

## What the named customers become

C1-C6 (profile class) collapse into their respective segments with headcount = 1 initially
(or we seed segments at realistic headcounts immediately). C7-C9 (HH smart) become the
initial Residential Smart and SME Smart headcount.

The named individual customer identity is gone from the simulator. If needed for audit
trail, the historical run output (pre-Phase-10a) is preserved.

## What this is NOT

- Not a full rewrite — the simulation loop structure stays; we replace the customer list
  with a segment list
- Not removing the company layer (Phase 9a) — the CRM will track segments, not individual
  accounts. `customer_registry.py` gets a `segments` table alongside its `accounts` table
- Not changing the hedging model or the risk committee

## Open questions for Rich

1. **Starting headcounts**: should we start at 1 per segment (to preserve continuity with
   the Phase 9a figures) or jump straight to realistic scale (150 resi, 40 SME, etc.)?
   The latter gives more interesting unit economics immediately but breaks comparability
   with existing published figures.

2. **Named customer reports**: the per-customer CLV, churn events, pricing flags in the
   current ANNUAL_REPORT.md — should these become per-segment tables, or do we preserve
   one "representative customer" per segment for illustration?

3. **Phase 9b (SIM/company separation)**: this supersedes that proposal. Should I archive
   it, or implement segment model first and then wire up company layer to segments?

## Gate

Per CLAUDE.md opt-out pattern: proceeding in 4 hours unless Rich redirects via staging or NTFY.

Proposed by Claude Code — 2026-06-20
