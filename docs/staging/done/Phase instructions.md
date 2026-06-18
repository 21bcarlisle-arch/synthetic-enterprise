# Phase 8a: Growth Mandate & Acquisition Model

## Objective

Introduce a strategic growth mandate that drives acquisition spend as a
function of forecast churn. The business is no longer passively losing
customers — it has a target book size and spends to defend it. This creates
the commercial incentives a real supplier faces: fixed costs, acquisition
cost, retention value, and the feedback loop between service quality and
margin.

## The Model

### Growth Mandate

A configurable parameter: `GROWTH_MANDATE = "flat"` (options: shrink,
flat, grow).

- **flat**: target net zero customer movement. Forecast expected churn,
  set acquisition budget to replace expected losses.
- **shrink**: target book reduction. Minimal acquisition spend. Accepts
  customer losses to reduce cost base.
- **grow**: target book expansion. Acquisition spend exceeds churn
  replacement. Accepts margin pressure for volume.

For now set to **flat**. The other modes should be implemented but not
the focus of this phase.

### Churn Forecast

The business uses its existing churn model (`saas/churn_model.py`) to
forecast expected losses over the next 12 months. This forecast drives
the acquisition budget. The business can only see what it's allowed to
see — it forecasts from current churn risk scores, not future actuals.

### Acquisition Budget

`acquisition_budget = forecast_churns * cost_per_acquisition`

`cost_per_acquisition` is a new constant — start at £150 for residential,
£400 for SME. These are realistic UK acquisition costs (price comparison
site fees, onboarding, first bill subsidy).

Acquisition budget is a real cost line in the P&L, deducted monthly
whether or not acquisitions actually occur. This reflects the reality that
marketing and sales spend is continuous, not event-driven.

### Acquisition Events

When a churn event fires, the business attempts to acquire a replacement
customer. Success probability is determined by:
- Base win rate (existing home-move model: 55% resi, 35% SME)
- Modified by: how much the business is spending vs market average
  (spend more = higher win rate, spend less = lower win rate)
- Modified by: service quality score (better service = better referrals
  and reviews = higher win rate)

This creates the incentive loop: good service → lower churn → lower
acquisition spend → better margin AND good service → higher win rate →
more replacements when churn does occur.

### Fixed Cost Floor

Introduce a monthly fixed cost that doesn't scale with customer count:

`fixed_cost_monthly = £500`

This covers: minimum regulatory compliance cost, systems licences,
bank charges, minimum staffing equivalent. It's deducted from margin
regardless of book size.

Effect: a shrinking book spreads this fixed cost over fewer customers,
raising cost-per-customer and compressing margin. This is the death
spiral dynamic — losing customers makes the remaining ones less
profitable, which can accelerate further losses.

### New Acquired Customers

When an acquisition succeeds, create a new customer record:
- Segment: match the churned customer's segment (like-for-like replacement)
- Tariff: current market tariff at acquisition date
- Start date: one month after churn date (switching window)
- Naming convention: extend existing pattern (C2_2 → C2_3, or new
  IDs for organic acquisitions)

### CLV Impact

The value of retaining a customer is now:
`retention_value = customer_CLV + avoided_acquisition_cost`

Surface this in the annual report's customer book section — show
retention value alongside CLV for each customer.

## What to build

1. `saas/growth_mandate.py` — mandate configuration, churn forecast,
   acquisition budget calculation, acquisition event generation

2. Extend `saas/ledger.py` — add `acquisition_spend` and `fixed_cost`
   as monthly ledger event types

3. Extend `saas/cost_to_serve.py` — add fixed cost floor

4. Wire into the simulation run — acquisition budget deducted monthly,
   acquisition events fired on churn, replacement customers activated

5. Extend annual report — new section: "Growth & Acquisition"
   - Forecast churn vs actual churn by year
   - Acquisition spend by year
   - Win rate: attempts vs successes
   - Fixed cost as % of gross margin
   - Retention value (CLV + avoided acquisition cost) per customer

6. Fast-mode validation first (`--fast --end-year 2020`), then full run

## Fidelity delta

After this phase the simulation models a business that actively manages
its book size, not just passively loses customers. Fixed costs create
real pressure on shrinking books. Acquisition spend is a genuine cost
line. The incentive to retain customers is properly wired into the
economics.

## Constraints

- Delegate all implementation to local Qwen
- Growth mandate must be a single configurable constant — don't
  hard-code flat
- Acquisition spend must appear in the ledger and P&L, not just as
  a model output
- The business forecasts churn from what it can see — no look-ahead
  into future actuals

## What Rich needs to decide (flag via NTFY if unclear)

- Cost per acquisition: £150 resi / £400 SME — does this feel right
  from industry experience, or adjust?
- Fixed cost floor: £500/month — calibrate against the book size
- Whether win rate modification by spend level should be linear or
  have diminishing returns

## Gate

**[REVIEW_GATE]** — Rich reviews the annual report Growth & Acquisition
section. Key questions:
- Does acquisition spend as % of revenue look realistic?
- Does the fixed cost floor create meaningful pressure on the 2024
  book (post-churn)?
- Does retention value change how you'd think about which customers
  to prioritise?

## NTFY

On completion:
1. "Phase 8a complete. Growth mandate active — flat mode."
2. "Acquisition spend across run: £[x]. Fixed cost: £[y]/yr."
3. "Retention value — highest: [customer] £[x]. Lowest: [customer] £[y]."
4. Report URL.
