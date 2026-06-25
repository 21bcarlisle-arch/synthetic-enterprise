# Phase 65 Proposal: FI2 -- Budget vs Actual

**The gap:** Destinationvision.md FI2: Annual budget set at start of year. Monthly variance
reported. Drives management decisions. Currently: no budget model.

FI1 (management accounts) is now complete (Phase 64). The double-entry income statement
per year/month is available via company.finance.management_accounts. Budget vs actual
is the next layer: a planned budget against which actuals are compared.

**What to build:**

1. company/finance/budget.py (new):
   - BUDGET_BY_YEAR: {year: {revenue, wholesale, gross, opex, net}} -- static budget
     constants derived from: prior year actuals + expected growth/cost assumptions.
   - get_annual_budget(year): returns budget dict for that year.
   - variance_report(management_accounts_pack, year): compares budget to actual.
     Returns {revenue: {budget, actual, variance_gbp, variance_pct},
              gross: {...}, net: {...}} for each line.
   - monthly_variance(management_accounts_pack, year, budget=None): same at monthly level.
   - traffic_light(variance_pct): "GREEN" if <5%, "AMBER" if <15%, "RED" if >=15%.

2. saas/reporting/annual_report.py:
   - _section_budget_vs_actual(data): renders annual variance table (10 years).
     Columns: Year | Budget Revenue | Actual Revenue | Var | Budget Net | Actual Net | Var | RAG.
   - Only rendered if management_accounts is available in data.

3. Tests (~12 new):
   - test_budget_constants_present_2016_2025 -- all 10 years have budget entries
   - test_variance_report_structure -- all required keys present
   - test_variance_zero_when_actual_equals_budget -- perfect budget gives 0% var
   - test_traffic_light_green_under_5pct -- green within tolerance
   - test_traffic_light_amber_5_to_15pct -- amber range
   - test_traffic_light_red_over_15pct -- red when badly off
   - test_variance_positive_when_actual_beats_budget -- outperformance tracked
   - test_variance_negative_when_actual_misses -- shortfall tracked
   - test_monthly_variance_returns_12_months -- monthly breakdown
   - test_budget_vs_actual_section_in_report -- section heading present
   - test_2022_crisis_year_shows_red_net -- energy crisis year has unfavourable net variance
   - test_budget_tolerates_missing_year -- graceful degradation

**Budget methodology:** Derive 2016 budget from first year actual (baseline). Each subsequent
year: revenue = prior budget * 1.10 (10% growth target); opex = prior budget * 1.05;
net = revenue - estimated cogs (85% pass-through) - opex. This gives a static but
meaningful comparison that shows real deviations (2022 crisis year will show big red variance).

**Expected impact:** Company now has a budget model and monthly variance tracking. Management
reporting moves from observation to control: actuals compared to plan, deviations flagged.
FI2 closed.

**Files changed:** company/finance/budget.py (new), saas/reporting/annual_report.py,
tests/company/finance/test_budget_vs_actual.py (new). ~12 new tests.
