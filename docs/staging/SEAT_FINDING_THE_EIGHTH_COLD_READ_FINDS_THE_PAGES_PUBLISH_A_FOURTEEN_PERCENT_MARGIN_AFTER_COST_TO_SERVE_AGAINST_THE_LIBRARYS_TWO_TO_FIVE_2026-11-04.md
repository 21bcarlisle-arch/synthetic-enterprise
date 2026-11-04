**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `unminted`

# N21. The household pages publish a margin after cost to serve of 14.5% of revenue, three to seven times the 2–5% the invariant library itself states (2026-11-04)

**Source.** Reader objection O35 in the eighth cold read, raised by an Ofgem price-cap analyst
(`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`). The seat confirmed it over all
1,289 domestic page files of the b3ce2a4e73 book.

**What the pages show.** Each household's "For them" stage prints revenue, gross, net and "net after cost to serve".
- **Book-wide**, `lifetime_net_after_cts_gbp` over `lifetime_revenue_gbp` is **14.5%**. The median account is 12.9%,
  p10 −0.9% and p90 22.6%.
- SYN-2016-531, for example: revenue £4,856.02, gross £3,255.76 (67%), net £1,521.28 (31%), net after cost to serve
  £1,050.96 (21.6%).
- The page also labels the figure before cost to serve as "Net margin" (O35's second half).
- `annual_pnl` carries `revenue_gbp: 0` in every year, beside a non-zero gross and net, on the pages checked.

**Why it is wrong, or needs a definition before it can be read.**
- `company/compliance/domain_invariants.py` holds `NET_MARGIN_PCT_OF_REVENUE` at 0.02–0.05 ("Ofgem Retail Market
  Report; Cornwall Insight").
- The cap's EBIT allowance is about 1.9–2.4% (`docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md`).
- A supplier billing at the cap, as this book's default tariffs are (named check (a): median 1.000 of the cap),
  cannot keep 14.5% after cost to serve unless a cost line is missing or booked too low.
- The reader also saw booked wholesale of about 6p/kWh on a summer 2023 account (O32), against an energy component
  of 24.36p on the same page.

**I cannot yet say** which of two causes it is:
- "net" omits a cost line: network, policy, the EPG pass-through, or bad debt. That is this project's known
  "net margin" definition failure, now on the page.
- The booked costs themselves are too low.

The first measurement is one account's revenue taken apart line by line against the cap's allowances for the
same periods.

**Say what it is before differencing (CLAUDE.md).** "Net after cost to serve" has to be defined line by line on the
knowledge layer before any bound is set. The library's 2–5% may be a different quantity.

**The row this owes (ruling step 6).** Once the definition is written down, it must be written blind from it and
from the Ofgem Retail Market Report: the book's margin on that definition sits in a sourced two-sided band per
year.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.

## Advanced 2026-11-04 (worker, focus `a-fresh-book-carrying-n18-and-the-margin-decomposed`)

**Defined before dividing.**
- **Numerator:** Σ settlement-record net over 1,291 per-fuel legs, less the flat `saas/cost_to_serve.py` £55 per leg
  per year. A record's net is revenue less wholesale, the modelled levies, network and capital cost.
- **Denominator:** the same records' ex-VAT revenue, unit rate plus standing charge.
- It is a contribution after a placeholder service cost, **not** EBIT.

**The two causes this finding could not separate: it is both.** The line-by-line table is in
`docs/market_research/supplier_financial_reporting.md` §1a. On b3ce2a4e73 (and 4669d77ddd, identical):
- wholesale 42.5%, network + policy 35.3%, capital 0.9%, cost to serve 6.8% → **14.5%**;
- about **5.7 points** are a page definition. The ledger bears bad debt (£68k), acquisition (£74k), back-billing
  write-offs (£47–50k), fixed cost and read visits, and the page omits all of them. Deducting them gives about 8.8%.
- most of the remaining 4–7 points is **operating cost the company is not charged**. The book charges £55 per leg,
  about £110 per dual-fuel home. The cap's operating, debt and industry allowance is £297.92 per dual-fuel DD
  customer per year (one period).

**Gaps, each filed against its owner.**

| # | Gap | Kind | Owner | Fix |
|---|---|---|---|---|
| 1 | Page omits ledger costs; it labels the pre-CTS figure "Net margin"; `annual_pnl` carries `revenue_gbp: 0` | definition on the page | `saas/reporting/annual_report.py` (`per_customer_lifetime`) → `tools/generate_customer_data.py`; B_commercial | Publish per account the ledger-basis net (after bad debt, acquisition, write-offs, fixed), or name the printed figure for what it is. Fix the zero revenue and the label. |
| 2 | Operating cost is a £55 placeholder | cost not borne | `saas/cost_to_serve.py`; B_commercial. MARGIN_REALISM Step 3, parked since July (ASSUMPTIONS.md) | K8 first: a knowledge page with the cap's operating, debt and industry allowance per cap period, netting out what is charged elsewhere. Then charge it. |
| 3 | No depreciation or fixed-asset cost | cost not borne | knowledge layer → `saas/`; B_commercial | **GAP**: no published depreciation rate is in the tree. The cap's £90 per customer of fixed assets (`price_cap_ebit_allowance.md` §C) is the start. |
| 4 | ECO and WHD absent from `simulation/policy_costs.py` | cost not borne, **or** a real small-supplier exemption | world (`simulation/policy_costs.py`) after a knowledge page | **GAP**: obligation thresholds by scheme year decide which it is. |
| 5 | The ledger's revenue and non-commodity cost (£3.21M, £0.84M) disagree with the settlement records' (£3.46M, £1.22M) | **I cannot yet say** | `saas/ledger.py` vs `simulation/*settlement*`; D_billing_metering | Measure first: per year, per fuel, which lines move the £256k and the £384k. |
| 6 | Calm-year wholesale reads 23.6–32.4% against 35–40% | **I cannot yet say** | world; B5_shaped_cost_benchmark_value_add | Book £/MWh against the cap's wholesale allowance per period. |
| 7 | The library's bands disagree: `NET_MARGIN_PCT_OF_REVENUE` 2–5% against 1–3% in §2 and 1.9–2.4% for EBIT | definition | `company/compliance/domain_invariants.py` | Ruling step 6's row: write the definition, then the band blind from it. |

**N18's effect, pre-registered before the book exists.**
`records/SEAT_PREREGISTRATION_THE_A6B7A0FD47_BOOK_CARRIES_N18_AND_WHAT_N21S_MARGIN_AFTER_COST_TO_SERVE_WILL_READ_2026-11-04.md`
predicts **15.4%** (band 15.0–16.0%) on the a6b7a0fd47 book. That is +£37k of 2017–18 SVT revenue on unchanged
costs, so yes, N18 raises it. The book is running (`longjob-fresh-run-a6b7a0fd47`), and a follow-on unit promotes
it to the publisher when it ends.

**Stays open** until the result sits beside that prediction, and until gaps 1 and 2 are either fixed or each owned
by a drawn item.
