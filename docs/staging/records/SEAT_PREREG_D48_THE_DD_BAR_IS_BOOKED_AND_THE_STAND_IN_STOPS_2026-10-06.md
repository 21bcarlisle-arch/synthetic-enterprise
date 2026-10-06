# Pre-registration: the DD back-billing bar is booked, the catch-up stand-in stops, and the book's true charge becomes the company's own

**Filed 2026-10-06, before any measurement below was run.** Atom `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`. Measured over the 8,632 bills in `docs/reports/run_output_latest.json` (129 DD accounts), by re-building `simulation/dd_balance_book` with the review as built (`seek_balance_at_review=False`).

What changes:
1. A DD catch-up writes nothing off. It is a statement, not a demand; the bar is taken on the DD balance book at the final bill (or the review, under the toggle).
2. The book's true charge for an estimated period stops reading the world's `true_total_amount_gbp`. It becomes the company's own: the billed estimate plus a share of the later catch-up's raw delta, pro rata to the estimates it billed.
3. The book's bar at each action posts to the ledger as a back-billing write-off that reduces revenue.

Predictions:
- **P1.** The bar at final bills moves from £17,667 (world true charge) by less than 15% when only the true-charge source changes. Reason: the catch-up delta lands inside the same run, so most of it stays in the same age band.
- **P2.** Adding the stand-in's write-offs back to DD bill totals (change 1) raises the final-bill bar by less than the £901 added back. Some of that debt is younger than 12 months.
- **P3.** The booked back-billing write-off on this book rises from about £1.0k to between £15k and £21k.
- **P4.** No pay-on-bill catch-up figure changes.

**Scored after measuring (same day).** On this file the base is £15,110, not £17,667: it is a newer run output than the one the £17,667 came from.
- **P1 right:** +2.2%.
- **P2 right on size, wrong in spirit:** the bar fell by £3 rather than rising.
- **P3 right:** about £15.5k.
- **P4 right.**

Full table: in the finding.
