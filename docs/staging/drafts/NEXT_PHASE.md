# Phase 57 Proposal: Year-varying bad debt (payment default surge in 2021-2022)

**The gap:** `saas/cost_to_serve.py` has flat static bad debt rates (resi 2%, SME 1%, I&C 0.5%)
with no year dimension. In reality, UK domestic payment defaults surged 5-10x during the 2021-2022
energy crisis -- Ofgem data showed 2.4M households in arrears by Q4 2022. Bad debt is also a
reporting overlay only; it does NOT affect the company's cash flow or treasury.

**What to build:**

1. `saas/cost_to_serve.py`: add `get_bad_debt_rate(year: int, segment: str) -> float` with a
   year-segment lookup table:
   - 2016-2020: resi 0.020, SME 0.010, I&C 0.005 (baseline)
   - 2021: resi 0.040, SME 0.015, I&C 0.005 (surge begins as bills rise)
   - 2022: resi 0.080, SME 0.030, I&C 0.010 (peak -- 2.4M UK households in arrears)
   - 2023: resi 0.050, SME 0.020, I&C 0.005 (partial recovery)
   - 2024: resi 0.030, SME 0.012, I&C 0.005 (normalising)
   Fallback to segment default for unrecognised years.

2. `simulation/run_phase2b.py`: deduct bad debt from treasury as a real cost.
   - At each settlement period: bad_debt_gbp = revenue_gbp * get_bad_debt_rate(year, segment)
   - Deduct from net_gbp and treasury (same mechanism as capital_cost_gbp)
   - Emit bad_debt_gbp field in settlement records for per-year reporting

3. `saas/reporting/annual_report.py`: add bad debt row to per-year P&L table.

4. Tests (~8 new): year-varying rates; crisis years higher; bad_debt_gbp in records;
   treasury reduced; I&C stable; out-of-range year fallback.

**Expected impact:** 2021-2022 net margin more negative, treasury takes real hit in crisis years.
