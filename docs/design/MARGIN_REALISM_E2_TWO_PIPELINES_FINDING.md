# E2 (revenue reconciliation) finding: two independent P&L pipelines disagree, deeper than Step 1 fixed

**Status:** REAL FINDING, NOT YET RESOLVED. Filed while working the maturity-map atom
`E2_revenue_reconciliation` (self-refill draw, 2026-07-10). One safe, well-understood fix
shipped alongside this doc (`tools/generate_insights.py`); the deeper issue below is
flagged, not silently picked a side on, per R4/R12.

## What was being checked

`E2`'s own simplification note said "Financial tab fixed 2026-07-10 (Step 1); other
surfaces (fra_ratio_series etc.) not yet reconciled." Auditing every surface that reads
or displays `revenue_gbp`/a margin %:

- `saas/reporting/fra_capital_ratio.py` (`fra_ratio_series`) -- already uses
  `management_accounts[yr].income_statement.revenue_gbp` (the TOTAL, Step-1-consistent
  basis). Not a bug -- my own note in the maturity-map atom was an unverified assumption,
  corrected here rather than left standing.
- `tools/generate_insights.py::_financial_insight()` -- a REAL, live, uncaught instance of
  the exact Step 1 class of bug: computed `net_pct` against the commodity-only revenue
  (`_ledger_headline.revenue_gbp` / `total_revenue_gbp`), then compared it to
  `_INDUSTRY_MARGIN_LOW/HIGH` (2-5%), a real external Ofgem/CMA benchmark for TOTAL
  margin -- apples to oranges, inflating every run's headline/narrative and (via
  `process_run_complete.py` -> `run_insights.json` -> NTFY) every run-completion message
  that quotes it. `generate_dashboard_data.py`'s consistency gate never caught this because
  it only cross-checks absolute £ fields, never a percentage. **Fixed** in this commit:
  sums `management_accounts[yr].income_statement.revenue_gbp` across all years as the
  denominator, falling back to the old commodity-only figure only if `management_accounts`
  is absent. 1 new test.

## The deeper finding (not fixed here)

Investigating `_financial_insight()`'s fix exposed something bigger: `years[yr].*`
(the SIM-side aggregate that feeds the Financial tab's Annual P&L table, built in
`saas/reporting/annual_report.py` by summing raw settlement records) and
`management_accounts[yr].income_statement.*` (the real double-entry ledger P&L, built in
`company/finance/double_entry.py` from actual booked ledger events) are **two entirely
independent computations of gross and net margin that disagree with each other**, not
merely a revenue-denominator question Step 1 already closed.

Real 2016-2025 data (`docs/reports/run_output_latest.json`):

| Year | years[].gross | ma.gross | diff | years[].net | ma.net |
|---|---:|---:|---:|---:|---:|
| 2016 | 6,822.2 | 7,874.3 | 1,052.1 | 1,278.0 | 6,477.3 |
| 2017 | 123,238.7 | 124,793.6 | 1,554.9 | 31,631.1 | 114,713.1 |
| 2018 | 262,602.4 | 264,244.9 | 1,642.5 | 101,530.6 | 246,945.7 |
| 2019 | 702,100.6 | 703,948.1 | 1,847.5 | 234,108.0 | 663,831.7 |
| 2020 | 791,769.7 | 793,568.7 | 1,799.0 | 128,512.2 | 744,280.2 |
| 2021 | 763,155.3 | 764,465.6 | 1,310.3 | 75,231.6 | 702,066.5 |
| 2022 | 1,049,224.8 | 1,050,634.3 | 1,409.5 | 338,347.9 | 938,216.9 |
| 2023 | 955,881.8 | 957,108.7 | 1,226.9 | 144,376.8 | 856,787.9 |
| 2024 | 1,257,805.7 | 1,258,286.7 | 481.0 | 347,815.4 | 1,172,190.4 |
| 2025 | 518,611.4 | 519,077.5 | 466.1 | 120,993.0 | 470,392.9 |

**Gross margin** diverges only slightly (a small, mostly-stable difference across years,
consistent with a real but minor scope/rounding difference in how non-commodity costs are
netted at the gross line). **Net margin diverges enormously** -- e.g. 2016: 1,278 (years[])
vs 6,477 (ma), a >5x difference, despite the ledger pipeline's net ALSO deducting bad debt,
cost-to-serve, fixed overheads, and acquisition spend that `years[].net_gbp` does not
itemise the same way.

Reconstructing both formulas from source:
- `years[].net_gbp` (`saas/reporting/annual_report.py`) = gross − capital − bad_debt −
  policy_cost − network_cost (electricity + gas). For 2016: 6,822.2 − 86.34 − 75.35 − 1,701
  − ~3,681 ≈ 1,278 -- reconciles.
- `income_statement.net_margin_gbp` (`company/finance/double_entry.py::income_statement()`)
  = gross − capital − (bad_debt + cost_to_serve + fixed + acquisition_spend), where gross
  already nets out `non_commodity_cost_gbp` (account 5100, fed by `non_commodity_cost_event`)
  at the REVENUE level, not as a further net-margin deduction. For 2016: 7,874.3 − 86.34 −
  (234.59+476.07+600+0) ≈ 6,477.3 -- reconciles.

**The real, unresolved question:** the ledger pipeline's `non_commodity_cost_gbp` (£3,892
for 2016) is meant to represent the same real-world cost as `years[]`'s combined
`policy_cost_gbp + network_cost_gbp` (£1,701 + ~£3,681 ≈ £5,382 for 2016) -- but they
disagree by ~£1,490, AND, more importantly, the ledger pipeline treats this as fully netted
at the gross-margin line while `years[]` treats it as a SEPARATE deduction after gross,
meaning **the two pipelines are not just using different numbers for the same concept --
their net-margin formulas structurally differ in what gets subtracted at all**. Bad debt
alone cannot explain a 5x gap given both pipelines include it.

## Why this is not fixed in this commit

Picking either pipeline as "the" answer without root-causing which one is actually correct
(or whether they are legitimately measuring different things -- e.g. does the ledger's
`non_commodity_cost_event` fire for the true recovered network/policy cost, or only a
partial/mistimed subset?) would repeat exactly the mistake Step 1's own diagnosis warned
against: computing a headline percentage without understanding what it excludes. This
needs its own dedicated trace through `saas/ledger.py`'s event-emission call sites (does
every non-commodity charge on a bill actually emit a `non_commodity_cost_event`, and does
every `years[].policy_cost_gbp`/`network_cost_gbp` source correspond 1:1 to one) before any
further "fix" is attempted. Registered in PRIORITIES.md as the real next step under E2,
not silently absorbed into a rushed re-fix of Step 1's already-shipped dashboard figure.

**Implication for Step 1's own "~12.5% -> ~8.9%" claim:** that figure used `years[yr].net_gbp`
over the total-revenue denominator -- a real, mechanically-explained correction on its own
terms, but now known to be paired with the SMALLER of the two available net-margin
numerators. Whichever pipeline turns out to be the structurally correct one, the Financial
tab's number may need a second pass once this is resolved. Not restated here as broken --
just no longer assumed closed.
