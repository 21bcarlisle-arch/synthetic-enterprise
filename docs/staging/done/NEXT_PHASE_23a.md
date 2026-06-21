# Phase 23a — Company-Owned Demand Estimation

Generated 2026-06-22 after Phase 22a complete (14fefcc). Staging processed.

---

## Background — The Epistemic Violation

The company currently reads `EFFECTIVE_EAC_KWH`, which is the SIM's exact annual
consumption for each customer. This dict is built at startup from customer
configuration — a SIM internal that a real supplier could not access.

A real UK energy supplier at renewal time knows:
- The billed kWh from the customer's most recent complete term (from its own billing records)
- Profile class benchmarks as a cross-check
- Any information the customer provided (stated EAC on contract)

It does NOT know the customer's true forward consumption — that must be estimated.

This matters because `EFFECTIVE_EAC_KWH` feeds:
1. `estimate_churn_probability()` — bill burden signal (line 622)
2. Retention offer economics — expected margin, offer cost (lines 629-632)
3. Missed-opportunity analysis — expected margin for no-offer churns (line 677)

All three use the SIM's oracle EAC. The company's decisions should use its own
observable estimate, not SIM internals.

---

## Proposed Change

### 1. Build `company_eac_kwh` dict (simulation/run_phase2b.py)

At each renewal, the company estimates annual consumption from prior billing records:

```python
def _estimate_company_eac(cid: str, term_start_str: str, all_records: list[dict]) -> float:
    """Estimate EAC from prior-year billing records observable to the company."""
    from datetime import date
    term_start = date.fromisoformat(term_start_str)
    # Sum billed kWh in the 12 months ending at term start
    cutoff_start = term_start.replace(year=term_start.year - 1)
    billed_kwh = sum(
        r["kwh"] for r in all_records
        if r.get("customer_id") == cid
        and r.get("record_type") == "settlement"
        and cutoff_start <= date.fromisoformat(r["period_end"][:10]) < term_start
    )
    return billed_kwh if billed_kwh > 0 else EFFECTIVE_EAC_KWH.get(cid, 0.0)  # fallback to true EAC for first term
```

This is epistemically honest: the company reads from its own billing ledger (which
it has accumulated from meter reads), not from SIM internals.

### 2. Use company estimate in company-layer decisions

Replace `EFFECTIVE_EAC_KWH.get(cid, 0.0)` with `_estimate_company_eac(cid, ...)` in:
- Line 622: `estimate_churn_probability()` call (bill burden signal)
- Line 629: `eac_for_ret` (retention offer economics)
- Line 677: `eac_missed` (no-offer missed opportunity analysis)

The SIM continues to use `EFFECTIVE_EAC_KWH` for all SIM-internal calculations
(hedging volume, risk committee, counterfactual, portfolio sizing).

### 3. Track divergence in run output

In `_compute_company_divergence()` in run_phase2b.py, add:
```python
"demand_error_by_year": {
    year: {
        "mean_abs_pct_error": ...,
        "max_abs_pct_error": ...,
    }
    for year in years_with_renewals
}
```

### 4. Annual report section

Add `_section_demand_estimation()` in `saas/reporting/annual_report.py`:
- Table: customer | true EAC | company estimate | % error | source (prior billing / fallback)
- Year-by-year mean demand estimation error
- Impact: how many retention offers changed economics (delta expected margin > 10%)?
- Section silent if `demand_error_by_year` not in run output (backward compat)

---

## Expected impact

- First renewal for each customer: company uses `EFFECTIVE_EAC_KWH` (fallback, since
  no prior billing). No change to first-term decisions.
- Subsequent renewals: company uses prior-year billed kWh. For profile class customers
  billed on their stated EAC, error should be small (5-15%). For HH customers whose
  actual consumption differs from estimated EAC, error may be larger (10-25%).
- Crisis years (2021-22): customers reduced consumption under bill stress →
  company EAC estimate from prior-year billing will be lower than forward consumption
  when market stabilises → slightly conservative retention economics (underestimates future margin)
- New divergence dimension: demand error + price error + churn error now all tracked

---

## Files to change

1. `simulation/run_phase2b.py`: add `_estimate_company_eac()`, replace 3 EFFECTIVE_EAC_KWH calls, add demand_error to _compute_company_divergence()
2. `saas/reporting/annual_report.py`: add `_section_demand_estimation()`
3. `tests/simulation/test_customer_events.py` (or new test file): 8-12 new tests
   - company estimate uses billing records, not SIM oracle
   - fallback to true EAC on first term
   - demand error tracked correctly
   - report section appears/is silent correctly

Estimated tests added: 10-14 new
Estimated session time: 1.5h

---

## Opt-out clause

Proceed with Phase 23a after 4h unless Rich stages a different direction.
