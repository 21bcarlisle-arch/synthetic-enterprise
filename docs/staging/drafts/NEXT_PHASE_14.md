# Phase 14 Roadmap — Post-13e Candidates

Generated 2026-06-21 after Phase 13e commit (61e5b3f). Phase 13 complete:
13a ToU tariffs · 13b ToU report section · 13c bill burden churn · 13d electricity seasonal · 13e gas seasonal

The c7aa449 run (Phase 13d active, first with ToU + bill burden + electricity seasonal) completes ~14:10 UTC.
Analyse it first — divergence tables and ToU utilization will show where to focus next.

---

## Phase 14a: ROI-Optimal Retention Offer Size

**Current**: offer 5% discount flat to any customer with company churn estimate > 30%.

**Problem**: a customer with 75% churn risk and £5,000 expected margin warrants a £300 discount
(6%), not the same £50 discount offered to a 32% risk / £1,000-margin customer. Fixed size over-
retains low-value at-risk customers and under-retains high-value ones.

**Proposed**:
```python
# Optimal offer = fraction of expected margin that makes retention economical
# Retention saves (churn_est × expected_margin). Offer costs (discount × term_revenue).
# Net positive when: churn_est × expected_margin > discount × term_revenue
# Max discount = churn_est × gross_margin_fraction
optimal_discount = min(
    MAX_DISCOUNT_FRACTION,          # cap at 20%
    churn_est * GROSS_MARGIN_RATE   # risk-weighted ceiling
)
```

Expected impact:
- Crisis years: high churn_est but low gross_margin_rate → economical offers at small discount, not blocked entirely
- Normal years: borderline customers get smaller targeted offers; high-risk get appropriately larger ones
- Retention ROI: expect improvement because offers are better sized to the actual risk/reward

Files: `simulation/run_phase2b.py` (offer calculation), `saas/ledger.py` (retention cost event), tests.

---

## Phase 14b: Gas-Specific Churn Sensitivity

**Current**: all customers (electricity + gas) use the same `RATE_SENSITIVITY = 0.8` and `BASE_CHURN_RATE = 0.10`.

**Reality**: gas-only customers (e.g. C4 — SME with boilers) respond differently to gas rate changes:
- Gas is a larger fraction of their total energy spend
- Gas price volatility is higher (NBP spot more volatile than electricity in non-crisis years)
- Gas customers have fewer alternative suppliers (market is less liquid for gas-only contracts)

**Proposed**: add `fuel: str = "electricity"` param to `estimate_churn_probability()`:
```python
GAS_RATE_SENSITIVITY = 0.6   # gas customers less price-sensitive (fewer alternatives)
GAS_BASE_CHURN_RATE = 0.08   # lower base rate (stickier contracts)
```

Files: `company/crm/churn_model.py`, `simulation/run_phase2b.py` (pass fuel type), tests.

---

## Phase 14c: Lookback Window Adaptive to Market Volatility

**Current**: company always uses 120-day lookback for forward price estimate.

**Problem**: in high-volatility regimes (2021-22 crisis), 120 days of data includes pre-crisis calm
prices and dilutes the signal. A pricing team would shorten the lookback when vol is elevated.

**Proposed**: adaptive lookback based on 30-day rolling price std:
```python
# High vol: shorten lookback (react faster to current conditions)
# Low vol: extend lookback (smooth out noise)
vol_ratio = price_std_30d / historical_price_std
lookback_days = max(30, min(180, int(120 / vol_ratio)))
```

Files: `company/pricing/tariff_engine.py`, tests.

---

## Recommended ordering

1. **Run c7aa449 completes → process_run_complete.py auto-handles it** (no action needed)
2. **Analyse the new annual report** — focus on: ToU utilization section (first real data), churn divergence
   for C6 2024 (should show company_p > 30% due to bill burden), tariff divergence 2021-22 (seasonal effect)
3. **Proceed with Phase 14a** (ROI-optimal offer size) — most direct impact on the retention P&L story
4. **Phase 14b** (gas churn) — simple change, 8-10 new tests, improves C4 model accuracy
5. **Phase 14c** (adaptive lookback) — more complex, saves for after 14a+14b run results

## Opt-out clause

Proceed with 14a after analysing the c7aa449 run results unless Rich stages a different direction.
