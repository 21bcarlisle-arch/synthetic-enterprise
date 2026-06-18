# URGENT: Bill Structure Fundamental Gap

## Problem

The simulation is missing the majority of a real UK energy bill. Current
bills include only wholesale cost and supplier margin. The following
components are completely absent:

**Residential (regulated, Ofgem Price Cap):**
- Network costs: ~20-25% of bill (TNUoS, DUoS for electricity; NTS, LDZ
  for gas)
- Environmental & social obligations: ~10-15% (ECO, Warm Home Discount
  levy, Renewables Obligation, FiT, CfD, Capacity Market)
- Meter costs, Elexon/Xoserve settlement charges: ~5%
- VAT: 5% (flat, reduced rate for domestic)

**SME (unregulated, bespoke tariffs):**
- Network costs: ~25-30% (DUoS, TNUoS, BSUoS, potentially MIC charges)
- Environmental & government obligations: ~30% (RO, FiT, CfD, Capacity
  Market — significantly heavier than residential)
- Climate Change Levy (CCL): applicable to all non-domestic supplies
- VAT: 20% standard rate (unless under de minimis threshold)

**Impact of this gap:**
- Revenue is understated by ~55-60%
- Gross margin as % of revenue is wrong (appears 4.7%, should be ~10-15%)
- CLV is wrong — cost to serve looks enormous relative to understated revenue
- Every profitability metric in the simulation is distorted

## What to build

### 1 — Non-commodity cost model
`simulation/non_commodity_costs.py`

For each customer, each settlement period, calculate:
- Network charges (pass-through, based on consumption and published rates)
- Environmental levies (pass-through, based on consumption and obligation
  rates — these change annually, use real Ofgem/Elexon published rates
  where available, reasonable estimates otherwise)
- CCL for SME customers
- Meter and settlement charges (fixed per customer per month)

Use the market research library (see companion instruction) to validate
the rates used.

### 2 — VAT layer
Apply correct VAT rate to each bill:
- Residential: 5%
- SME: 20% (check de minimis threshold — C2/C3 SME accounts)

### 3 — Revised tariff structure
The supplier's tariff now has two components:
- Non-commodity pass-through: cost recovery only, no margin
- Commodity + margin: wholesale cost plus supplier margin

This is how real tariffs are structured. The supplier earns margin only
on the commodity component. Pass-through costs are recovered at cost.

### 4 — Re-run and validate
After implementing, do a fast run (`--fast --end-year 2020`) and check:
- Gross margin as % of revenue moves toward 10-15%
- Revenue per customer looks realistic for their consumption profile
- CLV improves as revenue is correctly stated

Then full run. Regenerate and publish annual report.

## Constraints
- Use real published rates where possible — Ofgem, Elexon, NESO
- Document every rate assumption in the market research library
- Rates must vary by year — obligation rates change annually
- Delegate implementation to Qwen

## NTFY on completion
1. "Bill structure fix complete. New gross margin as % of revenue: [x]%"
2. "Revenue per customer range: £[low] - £[high]. Realistic? Yes/No."
3. Report URL.

---

# Standing Discovery Function

## Purpose

Discovery is not a phase — it is a standing business function that runs
in parallel with everything else. The simulation's assumptions must be
continuously validated against real market data. A bad assumption that
persists unchallenged distorts every number the simulation produces.

The bill structure gap (above) persisted through multiple phases because
there was no systematic process for checking assumptions. That must not
happen again.

## What to build

### Discovery Agent
`background/discovery_agent.py`

A Qwen-powered background process that:
- Maintains `docs/market_research/ASSUMPTIONS.md` — a living log of
  validated industry assumptions with sources, dates, and confidence levels
- Runs a discovery cycle at the start of each session or when triggered
- Prioritises assumptions by impact on simulation outputs
- Flags discrepancies between simulation assumptions and validated reality
- Notifies Rich via NTFY when a significant discrepancy is found

### Assumption Library
`docs/market_research/ASSUMPTIONS.md`

Structured as a table:

| Assumption | Current SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Wholesale as % of bill (resi) | ~95% | 40-45% | Ofgem/Gemini | 2026-06-18 | ❌ FIXED |
| Network charges (resi) | £0 | 20-25% of bill | Ofgem | 2026-06-18 | ❌ GAP |
| Environmental levies (resi) | £0 | 10-15% of bill | Ofgem | 2026-06-18 | ❌ GAP |
| VAT (resi) | £0 | 5% | HMRC | 2026-06-18 | ❌ GAP |
| Net margin as % of revenue | 3.2% | 2-5% | Ofgem/industry | 2026-06-18 | ✓ OK |
| Bad debt rate (resi) | 2% | 1-3% | Industry | 2026-06-18 | ✓ OK |
| Cost per acquisition (resi) | £150 | £100-200 | Industry | 2026-06-18 | ✓ OK |

Seed this with all current simulation assumptions. Mark known gaps.

### Priority Queue

The discovery agent checks assumptions in priority order:
1. Bill structure components (highest impact — affects all revenue metrics)
2. Forward curve term structure (affects all hedging metrics)
3. Churn rates by segment (affects CLV and book dynamics)
4. Network charge rates by year (Ofgem publishes these — use real data)
5. Obligation rates by year (RO, FiT, CfD — published annually)
6. Bad debt rates by segment
7. Cost per acquisition by channel

### Discovery Cycle

Each session, the discovery agent:
1. Reviews the assumption library for anything not checked in >30 days
2. Uses Qwen to reason about whether current SIM values are realistic
3. Where Qwen flags uncertainty, notes it and asks Rich via NTFY
4. Updates the library with findings and timestamps
5. Produces a weekly "Discovery Digest" — what was checked, what changed,
   what needs Rich's input

### Integration with Main Agent

When the main agent starts a new phase:
- It checks the assumption library for any ❌ GAP items relevant to that phase
- It does not build on top of known gaps without flagging them first
- Discovery findings automatically feed into phase design

## NTFY on setup
1. "Discovery function live. Assumption library seeded with [n] items."
2. "Critical gaps found: [list]. Bill structure fix already staged."
3. "First discovery digest will run at next session start."
