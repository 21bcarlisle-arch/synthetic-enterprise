Phase 267 -- Dashboard Phase B Completion: Year/Customer Filters on Financial, Customers, Trading Tabs

Status: PROPOSED (2026-06-26)

Phase 261 added the Year Spotlight on the Overview tab. Phase B is not yet
complete -- the Financial, Trading, and Customers tabs still show all-years
data with no filtering.

Goal: add year-filter controls to each of these three tabs so Rich can
isolate a single year across the full dashboard.

Design:
- Reuse the existing YEAR_FILTER state variable and selectYear() function.
- Add year-btn selector to top of Financial, Trading, Customers tabs.
- When a year is selected, re-render the relevant tab filtered to that year only.
- Affected charts: P&L bar chart (highlight selected year), hedge chart, spot
  price chart (zoom to year), customer heatmap (highlight year column).
- Affected tables: annual P&L table (bold selected year row), customer events
  (filter to year), retention log (filter to year).
- "All" resets to full 10-year view.

Estimated: ~8 tests (year filter state, per-tab rendering with filter applied,
clear-filter restores all data).
