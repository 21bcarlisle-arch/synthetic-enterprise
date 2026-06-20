# Phase 11b: Company Churn Model — Deepen SIM/Company Separation

## What this phase closes

Continues closing **hollow gap 3** (SIM/company barrier functional, not structural) by applying
the same pattern as Phase 11a to a second consequential decision: **when to intervene on
churn risk**.

Currently the company reads churn probabilities that are derived from the SIM's internal churn
model parameters (`saas/customer_reaction.py` — bill shock model, etc.). A real energy supplier
never sees its churn model's internal parameters. It sees bill amounts, customer tenure, complaint
rates, payment history — and builds its own estimate from those observables.

After this phase: the company has its own churn probability estimator built from observable
signals only. It decides whether to offer a retention discount (not yet implemented) or mark the
account as at-risk — without reading the SIM's churn model parameters.

## Epistemic contract

The company IS allowed to observe:
- The customer's bill history (bill amounts, frequency of large increases)
- The customer's tenure (how long they've been on supply)
- Market prices at the time of renewal (observable from public sources)
- Its own unit rate change (old rate → new rate at renewal)

The company is NOT allowed to see:
- `saas/customer_reaction.py` bill-shock parameters (alpha, beta, thresholds)
- The SIM's computed `churn_probability` directly
- Random roll outcomes from the SIM's churn roll

## Deliverables

### 1. `company/crm/churn_model.py`

Observable-signal churn risk estimator:
- Input: observable bill history and renewal context
- Algorithm:
  - `rate_increase_pct` = (new_unit_rate - old_unit_rate) / old_unit_rate
  - `tenure_years` = years since first acquisition_date
  - `company_churn_estimate` = base_rate + rate_sensitivity × rate_increase_pct - tenure_discount × min(tenure_years, 5)
  - Base rate: 0.10 (10% annual churn base)
  - Rate sensitivity: 0.8 (each 10% rate increase adds 8% to churn probability)
  - Tenure discount: 0.01 per year (loyal customers less likely to leave)
  - Clamp to [0.0, 0.95]

This will systematically differ from the SIM's bill-shock model:
- The SIM uses the ACTUAL bill amount relative to a threshold
- The company uses the rate change % (observable) rather than the bill amount relative to threshold
- For moderate rate changes: similar estimates
- For large rate increases on high-consumption customers: company may under-estimate churn vs SIM

### 2. `company/interfaces/sim_interface.py` additions

Add to `LiveSimInterface`:
- `get_churn_estimate(account_id, old_rate, new_rate, tenure_years)` → calls `company/crm/churn_model.py`
- Returns company's observable-data estimate (0.0–1.0)

### 3. `simulation/customer_events.py` modification

At each renewal point (when `roll_lifecycle_event` is called), record:
- `sim_churn_probability` (current — SIM's ground truth)
- `company_churn_estimate` (new — company's observable estimate)
- `churn_estimate_error_pct` = (company_est - sim_est) / sim_est

Store in the customer event log. The ACTUAL churn outcome still uses the SIM's roll
(ground truth determines reality — the company's estimate is what it THINKS will happen,
not what determines the outcome).

### 4. Churn basis risk reporting

New JSON output field: `churn_basis_risk` — per-renewal:
- `customer_id`, `term_start`, `sim_churn_probability`, `company_churn_estimate`, `error_pct`

New annual report section: "Churn Prediction Basis Risk" — average absolute error by year.
Key insight: if the company systematically under-estimates churn in crisis years (when bills
spike), it will be surprised by losses — the same epistemic failure that makes real suppliers
lose customers when prices spike.

## Test scope

- `tests/company/crm/test_churn_model.py` — unit tests for observable churn estimator
- `tests/company/interfaces/test_churn_via_live_interface.py` — integration
- `tests/simulation/test_customer_events_basis_risk.py` — check both estimates appear in output

## What this unlocks

- The company now has TWO consequential observable-data models: pricing (Phase 11a) and churn (Phase 11b)
- Foundation for retention intervention: the company could offer discounts to high-risk customers
  (observable: if company_churn_estimate > threshold, flag for intervention)
- The SIM/company barrier is now functional for the two most financially significant decisions

## Commit message

"Phase 11b: company churn model — deepen SIM/company separation beyond tariff pricing"
