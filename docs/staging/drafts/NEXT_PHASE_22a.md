# Phase 22a — Post-Crisis Churn Hangover + Trailing-Margin CLV

Generated 2026-06-21 after CLV/EV investigation (from_rich_20260621_200516).

---

## Background

Investigation of the -£7,978 enterprise value revealed two compounding issues:

1. **CLV history anchor**: `avg_annual_net_margin` averages ALL historical years including crisis losses.
   Only 2019 (+£334) and 2024 (+£948) were profitable over 10 years. The 10-year average is -£401/yr
   portfolio-wide — CLV correctly projects that forward.

2. **Churn model: wrong direction post-crisis**: For 2024 renewals, company estimates 0-3% churn
   (rates fell from crisis peaks → rate_increase_pct is negative → formula collapses to near-zero).
   But SIM truth is 35-41%. The company is badly under-estimating post-crisis churn because the
   model only sees rate changes, not the cumulative financial stress customers carry from 2+ years
   of crisis billing. This is the "scarring" effect: customers who survived crisis prices stay
   financially anxious and shop around even when their current bill improves.

---

## Phase 22a Part 1: Churn Hangover Term

**File**: `company/crm/churn_model.py`

Add a `crisis_hangover` signal: elevated base churn for 2 renewal periods after the company
observes its own net margin falling below -20% of revenue (observable from its own ledger).

Constants:
  CRISIS_HANGOVER_BASE_UPLIFT = 0.12   # 12% extra churn during hangover window
  CRISIS_HANGOVER_WINDOW_PERIODS = 2   # applies for 2 renewal periods after qualifying event
  CRISIS_HANGOVER_LOSS_THRESHOLD = 0.20  # triggers when prior net loss > 20% of revenue

Wire-up in `simulation/run_phase2b.py`: track `net_loss_fraction` per customer per rolling
2-period window; pass `hangover_periods_remaining` at each renewal.

Expected impact: 2024 company churn estimates for C7/C8/C9 rise from 0-2% toward 15-25%
(closer to SIM truth of 35-41%). Churn basis risk error shrinks significantly.

---

## Phase 22a Part 2: Trailing-Margin CLV

**File**: `saas/clv_model.py`

Add `margin_lookback_periods` param (default None = all history) to `build_clv()`.
When set to 3, use only the last 3 years of net margin as the forward-looking rate.

Run both variants. Report BOTH in annual report: "EV (full history): -£7,978 | EV (3yr trailing): +£X,XXX".
This makes the CLV methodology choice explicit.

---

## Part 3: Annual Report Section

`saas/reporting/annual_report.py`: add `_section_enterprise_value_analysis()`:
- Full-history EV vs 3yr-trailing EV
- Year-by-year net margin table (shows the history anchor effect)
- Churn basis risk summary for recent years (company vs SIM actual)
- Which customers are in the hangover window at report date

---

## Implementation sequence

1. `company/crm/churn_model.py` — hangover term + tests (8-10 new tests)
2. `simulation/run_phase2b.py` — hangover tracking wiring
3. `saas/clv_model.py` — trailing-margin variant + tests (4-6 new tests)
4. `saas/enterprise_value.py` — pass through
5. `saas/reporting/annual_report.py` — dual-EV section (4 new tests)
6. Full sim run, confirm churn basis risk narrows

Estimated tests added: 18-22 new
Estimated session time: 1.5h

---

## Opt-out clause

Proceed with Phase 22a after 4h unless Rich stages a different instruction.
