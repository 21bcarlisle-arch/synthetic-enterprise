**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** none — claim `the-company-is-charged-its-real-cost-to-serve`

# Pre-registration: under the cap's sourced cost to serve, N21's margin on the a6b7a0fd47 book falls from 15.50% to about 9.7% (2026-11-04)

Written before `saas/cost_to_serve.py` changed. The charge is defined in
`docs/market_research/the_caps_operating_debt_and_industry_allowance_per_cap_period.md` §3.

**Quantity.** The same as N21's: Σ `net_margin_after_cost_to_serve_gbp` over Σ settlement revenue, on the a6b7a0fd47 book
(`docs/reports/run_output_a6b7a0fd47_20261104T173649Z.json`). It is a contribution, not EBIT.

**How the prediction was made.**
- Every leg-month present in `years[y].per_customer_monthly` was priced at the period's charge over 12 for its fuel.
  SME and I&C stay flat.
- The flat £55 priced the same way gives £245,943, against the book's actual £240,607. Leg-months over-count partial
  months by about 2%.
- So the actual cost to serve was scaled by the ratio, new over flat: ×1.859.

**Prediction.**
1. Portfolio cost to serve: £240,607 → **about £447k** (band £420k–£475k).
2. Margin: 15.50% → **9.67%** (band 9.2%–10.2%).
3. By year, the multiple rises from about 1.5× (2016) to about 2.2× (2024–25). The 2017 SMNCC and the CPIH
   indexing drive it.

**Falsifiers.**
- A recomputed margin outside 9.2–10.2% means the leg-month proxy is wrong about how the module counts days.
- An unchanged figure means the date never reached the charge.

**How it is graded.**
- The run JSON carries no settlement records, so the changed module cannot be run over this book.
- The grade is the next fresh book.
- Until then the offline repricing above is the only number, and it is labelled that way wherever it is printed.
