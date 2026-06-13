# Phase 4c Summary — Physical Simulation Layer

Six sub-phases, all completed 2026-06-13 under the Phase 4c REVIEW_GATE
relaxation in `CLAUDE.md` (informational-only gates, proceed automatically
unless a genuine blocker or one-way door arises — none did). Each sub-phase
is a standalone pure module (`saas/` or `sim/`/`simulation/`), following the
same shape: plain dicts/lists in, plain dicts out, seed-estimate constants
flagged pending the `customer-archetype-data-enrichment` background task.

---

## 4c-1 — Property and Asset Model

### What Was Built
- `saas/property_model.py` — `build_properties()`. For each resi customer
  (C1-C4), derives a physical property record from `saas/customers.py`:
  property type (flat/semi/detached, from `home_type`), EPC rating, bedroom
  count, heating system (`gas_boiler` for the current dual-fuel customers,
  `electric_storage` otherwise), occupancy pattern (single/family/elderly),
  and an asset mix (EV/solar/smart meter).
- 10 tests (166 total at the time).

### Key Decisions
- Occupancy pattern and asset mix are seed-estimate constants — no real
  per-customer survey data exists yet.
- Heating system inferred from existing dual-fuel contract data rather than
  added as a new independent attribute, keeping the model anchored to data
  that's already Historical-Ground-Truth-derived.

---

## 4c-2 — Weather-Driven Demand

### What Was Built
- `simulation/demand_model.py` — `build_demand_shape()` and
  `solar_generation_shape()`. Adjusts a base PC1/PC3 consumption shape using:
  - heating/cooling degree days (UK bases: 15.5C heating, 22C cooling),
    rate depending on heating system from 4c-1 (gas boiler vs electric
    storage vs heat pump);
  - an occupancy-pattern time-of-day multiplier (single/family/elderly);
  - asset adjustments — EV overnight charging block, solar generation netted
    off daytime demand (floored at 0).
- 20 tests (186 total).

### Key Decisions
- Pure module: takes a daily mean temperature and optional half-hourly
  irradiance as plain inputs rather than importing `sim.weather_engine`
  directly — existing weather-engine output slots straight in without a
  dependency edge from `simulation/` back into `sim/`.
- **Not yet wired into `simulation/settlement.py`** — replacing the
  population-average PC1/PC3 shape with `build_demand_shape()` per customer
  is the natural integration step, flagged as a follow-up (see Open
  Questions below).

---

## 4c-3 — Weather → Wholesale Price Sensitivity

### What Was Built
- `sim/weather_price_sensitivity.py` — `weather_sensitivity_multiplier()`.
  Applies `COLD_SPELL_PRICE_MULTIPLIER` (1.10x, seed estimate) to the
  synthetic forward price when the *lookback window's* average
  heating-degree-days exceeds `COLD_SPELL_HDD_THRESHOLD`.
  `sim/forward_curve.py`'s `generate_forward_price()` gains an optional
  `lookback_daily_mean_temps_c` parameter, defaulting to `None` (no change,
  fully backward compatible).
- 6 tests (192 total).

### Key Decisions
- **Point-in-Time-safe by construction**: reads only the same lookback
  window `forward_curve.py` already uses for its base/volatility
  calculation — no future information leaks into the forward price.
- Real Elexon SSP data already covers 2016-2025 (Historical Ground Truth) —
  there was no synthetic *historical* curve to replace. This sub-phase's
  scope is the forward-price sensitivity layer only, used for future-dated
  pricing decisions within the simulation.

---

## 4c-4 — Bill Generation

### What Was Built
- `saas/bill_generator.py` — `generate_bill()` and
  `consumption_coefficient_of_variation()`. Aggregates a customer's monthly
  settlement records into total consumption, total amount due, average unit
  rate, and a `clarity_score` in [0,1].
  - Clarity reduced by consumption volatility within the month
    (coefficient of variation of daily kWh — a cold-spell-driven spike from
    4c-2/4c-3 makes a flat-rate bill harder to reconcile against actual
    usage).
  - Clarity further reduced by "bill shock" — % change vs the previous
    month's total, capped at 100% for the penalty, reported as
    `bill_shock_pct` (uncapped).
  - `fixed_1yr` contracts start at clarity 1.0; unknown/future tariff types
    (e.g. time-of-use/`tou_smart`) default to 0.7 base clarity.
- 9 tests (201 total).

### Key Decisions
- This is the sub-phase that operationalises the Key Domain Insight from
  `CLAUDE.md` ("arithmetically correct bills frequently produce complaints
  and churn") into a quantitative `clarity_score` — the input that 4c-6's
  contact model consumes directly.

---

## 4c-5 — Payment Behaviour

### What Was Built
- `saas/payment_behaviour.py` — `build_payment_behaviour()`,
  `bad_debt_provision_gbp()`, `expected_payment_date()`. Replaces
  `saas/cost_to_serve.py`'s flat 2%/1% `BAD_DEBT_RATE` with a per-customer
  credit-risk segment (low/medium/high/vulnerable), each carrying its own
  default-probability-derived bad-debt provision rate (0.5%-8% of revenue)
  and payment-timing delay (5-45 days after bill period-end).
  `CREDIT_RISK_BY_CUSTOMER` seeds C1-C4 as low/medium/vulnerable/low.
- 9 tests (210 total).

### Key Decisions
- **Not yet wired into `cost_to_serve.py`/`portfolio_pnl.py`** — same
  "standalone, ready for integration" pattern as 4c-2's `demand_model.py`
  (see Open Questions below).
- Segment-keyed by customer (not a derived score) — matches the seed-estimate
  pattern of 4c-1's occupancy/asset mix, and is the simplest thing that lets
  4c-6 flag a customer as `is_vulnerable` for contact-handling purposes.

---

## 4c-6 — Contact and Complaints

### What Was Built
- `saas/contact_model.py` — `contact_probability()`,
  `complaint_probability()`, `service_quality_score()`, and
  `build_contact_model()`.
  - `contact_probability(clarity_score, bill_shock_pct)`: starts from
    `BASE_CONTACT_PROBABILITY` (0.05), adds `(1 - clarity_score) *
    LOW_CLARITY_CONTACT_PENALTY` (0.3) and `min(bill_shock_pct, 1.0) *
    BILL_SHOCK_CONTACT_PENALTY` (0.5), clamped to [0,1]. Consumes
    `clarity_score`/`bill_shock_pct` directly from 4c-4's
    `generate_bill()` output.
  - `complaint_probability(contact_probability)`: `COMPLAINT_ESCALATION_DAYS
    = 14` per the sub-phase spec — an unresolved contact escalates to a
    complaint after 14 days. Modelled as a fixed
    `UNRESOLVED_AFTER_14_DAYS_RATE` (0.25, seed estimate) applied to contact
    probability, since no per-contact resolution-date data exists to track
    an actual 14-day clock.
  - `service_quality_score(complaint_rate)`: `1.0 - complaint_rate *
    SERVICE_QUALITY_PENALTY_FACTOR` (2.0), clamped to [0,1].
  - `build_contact_model(bills)`: per-bill records (`by_customer`) plus a
    `portfolio` summary (`avg_complaint_probability`,
    `service_quality_score`).
- 12 tests (222 total).

### Key Decisions
- The 14-day escalation window is captured as a constant
  (`COMPLAINT_ESCALATION_DAYS`) for documentation/traceability even though
  the current implementation can't simulate an actual per-contact clock —
  if per-contact open/resolved timestamps are added in a future enrichment,
  `UNRESOLVED_AFTER_14_DAYS_RATE` is the natural replacement point.
- `service_quality_score` is portfolio-level (averaged across all bills),
  not per-customer — mirrors 4b-5's enterprise-value-function pattern of a
  single headline portfolio metric, while `by_customer` retains the
  per-bill detail for drill-down.

---

## Phase 4c — Cross-Cutting Open Questions

1. **Integration backlog**: 4c-2 (`demand_model.py`), 4c-5
   (`payment_behaviour.py`), and 4c-6 (`contact_model.py`) are all built as
   standalone modules, not yet wired into `simulation/settlement.py`,
   `saas/cost_to_serve.py`, or `simulation/portfolio_pnl.py`. A natural next
   step (Phase 4d or a Phase 4c wrap-up increment) is a single
   `simulation/run_phase4c_on_phase2b.py`-style re-run, analogous to
   4b's `run_phase4b_on_phase2b.py`, that chains: settlement (with 4c-2's
   per-customer demand shape) → 4c-4 bills (with 4c-3's weather-sensitive
   forward prices already baked into settlement cost) → 4c-5 payment
   behaviour → 4c-6 contact/complaints, producing a portfolio-level
   `service_quality_score` alongside the existing financial headline figures.
2. **Seed estimates throughout**: every constant introduced across 4c-1
   (occupancy/asset mix), 4c-3 (`COLD_SPELL_PRICE_MULTIPLIER`,
   `COLD_SPELL_HDD_THRESHOLD`), 4c-5 (credit-risk segments, default
   probabilities, payment timing), and 4c-6 (contact/complaint
   probabilities, `UNRESOLVED_AFTER_14_DAYS_RATE`,
   `SERVICE_QUALITY_PENALTY_FACTOR`) is a seed estimate pending the
   `customer-archetype-data-enrichment` background task. None of these have
   been calibrated against real data.
3. **4c-6's escalation model is a stand-in**: `UNRESOLVED_AFTER_14_DAYS_RATE`
   approximates "fraction of contacts unresolved after 14 days" as a fixed
   rate rather than simulating actual contact lifecycles (open date,
   resolution date). If a future phase adds per-contact tracking, this
   constant should be replaced by a real day-14 unresolved check.

---

## Follow-up — Full Portfolio Re-run (2026-06-13)

New `simulation/run_phase4c_on_phase2b.py` ran the full 9.5-year Phase 2b
settlement (2016-01-01 → 2025-06-07, 10 accounts: 6 electricity + 4 gas)
once, grouped its `all_records` output into one monthly bill per customer
via `build_monthly_bills()` (chronological, carrying each customer's own
`previous_bill_total_gbp` for the bill-shock penalty), then fed those bills
through 4c-5 (`build_payment_behaviour`) and 4c-6 (`build_contact_model`).
3 new tests for `build_monthly_bills` (231 total), lint clean.

**Scope note**: 4c-2 (weather-driven demand) and 4c-3 (weather→price
sensitivity) are *not* included in this re-run — both modify
`simulation/settlement.py`'s inputs (consumption shape, forward price) rather
than consuming its output, so wiring them in means re-running
`simulation/run_phase2b.py` itself with different inputs, not a downstream
pass over its existing records. That remains open (see item 1 above, now
narrowed to 4c-2/4c-3 only).

### Phase 2b re-run (re-confirmed, point estimate)
- Gross margin £28,014.63; capital costs £14,368.43; net margin £13,646.21
- Treasury £21,829.17 → £35,475.37 (+£13,646.21); capital cost ratio 51.3%
- OUTCOME: SURVIVED — full window completed
- (Differs slightly from PHASE_2b_SUMMARY.md's £13,970.60 and 4b's
  £13,430.48 — each re-run is its own stochastic trajectory through the same
  Context Handshake/hedging agent, consistent with 4b's "single point
  estimate, not a distribution" caveat.)

### Phase 4c billing-experience layer — portfolio-level results
- Bills generated: 1,101
- Average clarity score: 0.923
- Average bill shock (where shown): 10.9%
- Total bad-debt provision: £2,016.30
- Avg complaint probability: 0.030
- **Service quality score: 0.941**

| Account | Bills | Avg clarity | Credit risk | Bad debt £ |
|---|---|---|---|---|
| C1  | 114 | 0.926 | low        |  35.25 |
| C2  | 111 | 0.930 | medium     | 132.97 |
| C3  | 108 | 0.928 | vulnerable | 376.29 |
| C4  | 105 | 0.929 | low        |  31.67 |
| C5  | 114 | 0.841 | medium     | 487.46 |
| C6  | 111 | 0.842 | medium     | 460.33 |
| C1g | 114 | 0.965 | medium     | 100.39 |
| C2g | 111 | 0.959 | medium     | 111.85 |
| C3g | 108 | 0.959 | medium     |  85.39 |
| C4g | 105 | 0.957 | medium     | 194.72 |

### Open Questions
- **C5/C6's lower clarity (0.84 vs ~0.93 elsewhere)**: these are the two
  customers without 4c-1 property records (`saas/property_model.py` only
  covers C1-C4), so this isn't driven by occupancy/asset mix — it's purely
  consumption volatility and bill-shock from their settlement records.
  Worth checking whether C5/C6's consumption shapes are inherently more
  volatile (e.g. SME load profile from Phase 2a) once 4c-2's per-customer
  demand shapes are wired in.
- **Gas accounts (Cxg) have higher clarity (0.96) and lower bad-debt (despite
  `medium` risk, same as their electricity counterparts) than electricity**:
  gas consumption is naturally smoother (heating-dominated, less peaky than
  electricity), so less CV-driven clarity penalty — consistent with the
  4c-4 model's mechanics, not a bug.
- **`CREDIT_RISK_BY_CUSTOMER` (4c-5) and 4c-1's property records only cover
  C1-C4** — C5/C6 and all four gas accounts (Cxg) fall back to
  `DEFAULT_CREDIT_RISK = "medium"`. Extending these seed tables to the full
  10-account portfolio is part of the same
  `customer-archetype-data-enrichment` background task referenced
  throughout.
- 0.030 avg complaint probability / 0.941 service quality score are a single
  point estimate from one stochastic Phase 2b trajectory — same "not a
  distribution" caveat as 4b's enterprise-value figures.

## Token Efficiency

Phase 4c (all six sub-phases) ran as a single continuous session with no
REVIEW_GATE pauses, per the standing relaxation in `CLAUDE.md`. Each
sub-phase followed the established pattern (pure module + tests, mirroring
4b's modules), which kept design overhead low — most sub-phases needed only
one read of the preceding sub-phase's module plus its test file before
writing the new module and tests directly.
