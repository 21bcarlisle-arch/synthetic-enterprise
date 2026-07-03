# NEXT PHASE PROPOSAL: Phase PS -- Complaints & Arrears Population Anchoring (closes P3)

## Gap addressed
P3 Population Anchoring -- two of the three required benchmarks remain unanchored:
- Complaints/ombudsman volumes: avg_complaint_probability exists in run output (4-6% per
  billing period) but is never compared against published Ofgem/Citizens Advice benchmarks.
  The Ofgem Supply Return section still hardcodes complaints_per_100=0.0.
- Arrears rates: Phase PP billing ledger has full per-customer arrears history with dates,
  but there is no population-level aggregation or DESNZ benchmark comparison.

Switching rates (NS/PQ/PR) and bad debt (plausibility section) are already anchored.
Phase PS finishes P3.

## What real fidelity is gained
A real UK energy supplier CFO compares complaint and arrears rates against Ofgem QoS
survey benchmarks each year. The board cannot currently answer: Are our complaint and
arrears rates plausible for a UK I&C supplier? After this phase they can -- with
per-year RAG flags anchored to published data.

## What this phase builds

### Part A: tools/population_anchor.py

_complaints_check(years_data) -> list[dict]:
  Metric: complaint_rate_pct = avg_complaint_probability x 100
  Benchmarks (Ofgem QoS, I&C adjustment):
    GREEN 2.0-6.0% normal; 2.0-8.0% crisis (2021-2023)
    AMBER 6.0-10.0% or 1.0-2.0%
    RED >10.0% or <1.0%

_arrears_check_by_year(billing_ledger, years_data) -> list[dict]:
  new_arrears_rate_pct = unique customers with new arrears in year / active customers x 100
  Denominator from years_data[yr][active_customer_ids]
  Benchmarks (DESNZ, I&C portfolio):
    GREEN <8% normal; <12% crisis (2021-2023)
    AMBER 8-15%; 12-18% crisis
    RED >15%; >18% crisis

generate() extended: reads site/state/billing_ledger.json; adds complaints_vs_benchmark
and arrears_vs_benchmark keys to population_anchoring.json.

### Part B: saas/reporting/annual_report.py -- _section_population_anchoring(data)

New dedicated section. Per-year table:
  Year | Complaint rate% | Benchmark | RAG | Arrears rate% | Benchmark | RAG

Summary: X of 10 years GREEN for complaints; Y of 10 years GREEN for arrears.

### Part C: Fix Ofgem Supply Return hardcoded zero

Replace complaints_per_100=0.0 with:
  round(yd.get('avg_complaint_probability', 0.0) * 100, 1)

### Part D: Wire billing_ledger into process_run_complete.py -> generate()

## Epistemic check: all data company-observable or publicly published. PASS.

## Test targets (~20 tests)
1.  _complaints_check converts avg_complaint_probability to complaint_rate_pct correctly
2.  _complaints_check GREEN for normal year 5.0% (within 2-6%)
3.  _complaints_check AMBER for 6.5% in normal year (above 6.0%)
4.  _complaints_check GREEN for 2022 at 5.8% (crisis ceiling 8.0%)
5.  _complaints_check RED for rate <1.0%
6.  _arrears_check_by_year counts unique customers with new arrears per year
7.  _arrears_check_by_year GREEN for arrears_rate <8%
8.  _arrears_check_by_year AMBER for arrears_rate 9%
9.  _arrears_check_by_year GREEN for crisis year at 10% (ceiling 12%)
10. _arrears_check_by_year RED for rate >15%
11. _arrears_check_by_year handles empty arrears_history gracefully
12. generate() output includes complaints_vs_benchmark key
13. generate() output includes arrears_vs_benchmark key
14. generate() handles missing billing_ledger.json without crash
15. _section_population_anchoring renders complaints and arrears table
16. _section_population_anchoring GREEN for in-range year
17. _section_population_anchoring summary line counts GREEN years correctly
18. _section_population_anchoring returns empty string if no year data
19. Ofgem supply return: complaints_per_100 now >0.0 for any year with bills
20. _arrears_check_by_year denominator uses active_customer_ids count per year

## Expected key finding
SIM complaint rate (4-6% per billing period) within GREEN for most years; 2022 elevated.
Arrears elevated in 2016 (early resi, DD failures) and 2022 (crisis), GREEN in I&C-
dominated 2017-2021. Board confirmed: complaint and arrears profile consistent with
UK I&C supplier -- Ofgem benchmarks met.
