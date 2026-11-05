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

**Result (19:12Z): 15.50%** on the a6b7a0fd47 book, inside the band. N18 raised the figure as predicted. The
revenue prediction missed: +£76k against £25–55k, with 10 more legs, not fewer. The grade is in the record. The
book is the one `run_output_latest.json` now holds for the 9 Nov publish.

**Stays open** until gaps 1 and 2 are either fixed or each owned by a drawn item. Under the 26 Oct ruling, both are
correctness work, not features.

## Advanced 2026-11-04 (worker, claim `the-company-is-charged-its-real-cost-to-serve`): gaps 5 and 1

N21's margin on the a6b7a0fd47 book starts at **15.50%** (£548,926 over £3,540,583).

**Gap 5 measured.** The per-year, per-fuel table is in `docs/market_research/supplier_financial_reporting.md` §1a,
"Gap 5 measured".
- **Revenue.** The settlement records are right. They equal bills ex-VAT plus the EPG to within £861.
  - The management accounts dropped the whole £252,708 EPG receipt: the journal had no branch for
    `epg_receipt_event`.
  - Fixed, with a control red on HEAD.
- **Non-commodity.** The settlement records are right in kind.
  - `saas/ledger.py` books the billed unit-rate non-commodity *price* as its cost. That is £338k short on
    electricity, about what the standing charge recovers. Gas agrees.
  - **Open, owner `saas/ledger.py`:** book the settlement records' levies and network as the cost event.
- **Still dropped by the journal, open:** `revenue_restatement_event`, `back_billing_write_off_event` and
  `dd_back_billing_write_off_event`. Each needs its account pair decided.
- Margin after this step: **15.50%**, unchanged. The page reads the settlement records.

**Gap 1.** On the household page:
- "Net margin" now reads "Margin after network, policy and capital".
- The bottom line now reads "Contribution after cost to serve", with a sentence saying it is not profit and naming
  what it leaves out.
- `annual_pnl.revenue_gbp` is the customer's own monthly revenue summed: `tools/generate_customer_data._per_year_data`
  had read a key the run never writes. It is None, never 0, when there is none.
- Margin after this step: **15.50%**, unchanged. Labels only.

**Gap 2.** Knowledge first:
`docs/market_research/the_caps_operating_debt_and_industry_allowance_per_cap_period.md`, read cell by cell from
Ofgem's cap level model v1.28 and Appendix 6.

- **The charge.** `saas/cost_to_serve.py` now charges each resi fuel account, per cap period, the cap's benchmark
  OC + PAAC + SMNCC, less the DD bad debt inside OC. From July 2025 it is CO + IC + SMNCC.
  - That is £79–127 per fuel account per year, against the flat £55.
  - A dual-fuel home is charged £171 in 2016 and £238 in 2024.
- **Not charged:** PAP, DRC and the debt floats. The book bears bad debt and capital on its own lines.
- **GAP:** sales and marketing sits inside OC, unseparated, so the book's acquisition line double-counts some of it.
  That errs against our thesis, bounded by about £17 per leg-year.
- **Control:** `tests/saas/test_the_cost_to_serve_sits_inside_the_caps_published_allowance.py`, with bands written
  from the published cells. All six are red on HEAD.
- **Downstream:** the renewal desk and the value-based arm read the same dated charge.
- **Margin after this step:** **about 9.7%**, from offline repricing of the a6b7a0fd47 book's leg-months, as
  pre-registered (`records/SEAT_PREREGISTRATION_N21_MARGIN_UNDER_THE_CAPS_SOURCED_COST_TO_SERVE_2026-11-04.md`). The
  next fresh book grades it.

**Gap 3 narrowed.** Depreciation is inside Ofgem's OC (Table A6.1). Charging OC therefore charges it for the domestic
book. SME and I&C remain unanchored.

**Still open after this claim:** gaps 3 (SME/I&C only), 4, 6 and 7; the ledger's non-commodity cost line; and the
three journal event types.
