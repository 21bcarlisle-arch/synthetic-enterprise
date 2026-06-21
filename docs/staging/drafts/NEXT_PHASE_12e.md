# Phase 12e: SIM/Company Full Operational Independence — Divergence Measurement

## What this phase does

**Close hollow gap #3 (SIM/company barrier) by making the company run end-to-end on its own models
and measuring the divergence from SIM ground truth.**

The company already has:
- `CompanyTariffEngine` (Phase 11a): tariff from observable forward prices, not SIM internals
- `CompanyChurnEstimator` (Phase 11b): churn estimate from rate change + tenure only
- `CompanyEventLog` (Phase 12a): dated churn/acquisition/retention artefacts
- Retention decisions (Phase 12b-12d): pre-roll offer based on company estimate

What's still shared/leaky:
- Company receives outputs through `LiveSimInterface` but this is still a Python in-process call —
  no network boundary; shared module state could propagate SIM internals implicitly
- No formal audit of what the company "sees" vs what a real supplier could actually observe
- No measurement of company-model divergence from SIM ground truth over time

## Mechanism

1. **Audit the LiveSimInterface boundary** (`company/interfaces/sim_interface.py`):
   - List every value the company receives. Classify each as: (a) observable by a real supplier,
     (b) derived from SIM internals only. Flag any (b) as a violation.
   - Fix violations: substitute observable proxies or remove access entirely.

2. **Add divergence tracking to `run_phase2b.py`**:
   - For every consequential company decision (tariff, churn estimate, retention):
     Record: company_value, sim_ground_truth_value, error_pct, cumulative_error
   - New output key `company_divergence` in run JSON.

3. **Annual report section "Company Model Divergence"**:
   - Table: year × decision_type → mean_error_pct, max_error_pct
   - Trend: is divergence growing or shrinking over time? (Companies calibrate their models)
   - Cost of divergence: error_pct mapped to P&L impact (uses existing basis risk machinery)

4. **Optional (if time allows): Company calibration event**:
   - Once per year (e.g., January), the company "looks at its own year-end bill data" and
     recalibrates its forward price model (e.g., updates the rolling mean window).
   - This simulates a real supplier refining its view without seeing SIM internals.

## What this unlocks

- Hollow gap #3 formally closed: company makes all consequential decisions using only observable
  information; divergence from SIM ground truth is measured, not assumed.
- Foundation for "company learning": once divergence is measured, we can add calibration events
  that narrow it over time (mimics how a real supplier would improve its models).
- Unlocks I&C and VPP/DER: both require a company that can independently value contracts
  (without reading SIM forward curve internals).

## Deliverables

1. `company/interfaces/sim_interface.py`: audit + fix any SIM-internal leaks; add docstring
   listing every value exposed and its observability classification.
2. `simulation/run_phase2b.py`: `company_divergence` dict in output (per-year, per-decision).
3. `saas/reporting/annual_report.py`: `_section_company_divergence()` — divergence table + trend.
4. Tests: divergence tracking (values populated, structure correct); interface audit (no forbidden keys).

## Acceptance criteria

- `company_divergence` key in run output with non-empty data for all 3 decision types
- Annual report includes "Company Model Divergence" section with year-by-year error table
- `LiveSimInterface` docstring lists every exposed value with observability classification
- 637+ tests passing (net-new tests for divergence tracking)

## Commit message

"Phase 12e: SIM/company divergence tracking — close hollow gap 3"
