# MARGIN_REALISM Step 1 — gauge diagnosis (2026-07-10, in progress)

**Status: PARTIAL.** One real, confirmed root-cause mechanism found and evidenced below. The
exact surface/computation producing the specific percentages the director cited (10.2/13.6/23.3/
19.5/10.5/4.4/9.8/5.6/15.9/12.5) has NOT yet been located -- neither candidate revenue denominator
tried below reproduces those exact figures against the current run's net_margin_gbp. Registering
this honestly rather than claiming the gauge is fixed.

## Confirmed: two genuinely different "revenue" figures coexist, both real, not a bug in either

`docs/reports/run_output_latest.json` contains at least two live revenue figures per year that
disagree by 26-52%, every year, with no shrinking trend over the 10-year history (ruling out a
simple "first-year billing lag" explanation):

| Year | `years[yr].revenue_gbp` (commodity-only, settlement-based) | `management_accounts[yr].income_statement.revenue_gbp` (total billed, net of VAT) | Gap |
|---|---|---|---|
| 2016 | 10,417 | 15,362 | 47.5% |
| 2017 | 234,294 | 348,631 | 48.8% |
| 2018 | 435,480 | 601,110 | 38.0% |
| 2020 | 1,223,313 | 1,857,023 | 51.8% |
| 2025 | 970,672 | 1,228,035 | 26.5% |

Traced both to source:

- `years[yr].revenue_gbp` (`saas/reporting/annual_report.py::extract_report_data()`) sums each
  settlement record's own `revenue_gbp` field -- this is the pure ENERGY/COMMODITY revenue only
  (wholesale cost + margin), excluding standing charges, non-commodity pass-through, and VAT
  entirely.
- `management_accounts[yr].income_statement.revenue_gbp` (`company/finance/management_accounts.py`
  -> `company/finance/double_entry.py`) is built from a real double-entry journal: `billing_event`
  books the FULL bill total to the revenue account (`saas/ledger.py`'s own docstring: "total
  customer bill (cash in, all-in including non-commodity + VAT from 9a)"), and a
  `vat_remittance_event` then reduces that account back out for VAT collected on HMRC's behalf.
  Non-commodity costs are NOT netted out of revenue -- they show as a separate cost line
  (`non_commodity_cost_gbp`), matching how a real supplier's accounts report total revenue
  (network/environmental levy recovery counts as revenue, then shows as a cost). Verified
  arithmetically for 2016: commodity revenue (10,417) + non-commodity cost (3,892) + standing
  charges (~1,053 implied) ≈ total billed net of VAT (15,362).

**Neither figure is wrong.** They answer different real questions: "energy sold" vs "total billed
to customers." The bug, if there is one, is a SURFACE using one where a genuine total-revenue
margin percentage needs the other -- exactly the class of confusion Rich's original complaint
("net margin % looks 5x too high vs real UK domestic retail ~1-3%") would produce if a percentage
were computed against the smaller, commodity-only denominator (which inflates any margin % since
the same £ net margin is divided by a understated revenue base).

## NOT yet resolved

Tried `management_accounts[yr].net_margin_gbp / management_accounts[yr].revenue_gbp` (total, VAT-net)
and `.../ years[yr].revenue_gbp` (commodity-only) as the two candidate percentages for 2016-2025 --
neither reproduces the director's cited 10.2/13.6/23.3/... series (both come out much higher,
22-62%, since `management_accounts.net_margin_gbp` is itself a different, more complete bottom-line
figure than whatever fed the reviewed surface). The exact site surface and computation the director
was looking at when he made this observation has not been located in this pass -- registered as the
concrete remaining task, not guessed at.

## Next concrete step (not done in this pass)

1. Find the exact dashboard.json/supplier.json/site page showing the cited percentages (likely the
   Supplier tab's Performance/Financial view, possibly the segmented-financials `net_margin_pct`
   field added earlier today, or the management-accounts `net_margin_pct` -- both need checking
   against the exact cited numbers, not assumed).
2. Once found, decide (with the director, per the DoD) which revenue definition is canonical for a
   margin percentage claim, or whether both should surface with unambiguous labels reflecting the
   commodity-vs-total distinction confirmed above.
3. Add the reconciliation to the consistency gate per the original instruction.
4. Only then does diagnosis (MARGIN_REALISM.md step 2) and the mechanism builds (steps 3-5) make
   sense to start.
