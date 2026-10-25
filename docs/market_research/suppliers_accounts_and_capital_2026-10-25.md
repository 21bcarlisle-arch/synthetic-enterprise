# A GB supplier's accounts and capital: revenue, unbilled, bad debt, credit balances and minimum capital

**Knowledge:** suppliers-accounts-and-capital

Written 2026-10-25 for the director's map steer of 24 Oct (item 4, third owed page), from the
advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_SUPPLIER_ACCOUNTS_AND_CAPITAL_2026-10-25.md`.
Figures marked **[derived]** are the pack author's arithmetic on the cited numbers; **[unverified]**
items are recollection and not claims until sourced. Unbilled revenue and bad-debt provisioning each
already have their own page (`unbilled-energy-and-revenue-assurance`, `bad-debt-provisioning`); this
note holds the figures for them and adds what those pages do not: minimum capital, credit-balance
protection, the segmental statement and margins, working capital and collateral.

## 0. What this project's company does today (read from code, not run)

- **The Capital Target is £115 and has one live home.** `saas/growth_mandate.py`
  (`CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT = 115.0`, dated from 31 March 2025) sizes growth against
  it. Six documents still said £130 as if decided; corrected beside the claim in this commit.
- **Nothing computes the Cash Coverage Trigger.** No module compares cash with 20% of fixed-DD
  customer credit balances. `company/billing/credit_balance_control.py` checks that a credit balance
  is discharged, not that it is covered, and nothing calls it.
- **`company/risk/capital_adequacy.py` states thresholds no source here supports** ("wind-down reserve
  min 1.5% of annual revenue", "regulatory equity ratio min 10% of risk-weighted assets", cited to an
  "Ofgem FRA 2023 consultation"). Ofgem's decided rule is a £0 Floor and £115 Target of Adjusted Net
  Assets per dual-fuel customer plus the 20% cash coverage trigger. Nothing calls the module, so no
  run reads those numbers; it is dead code carrying wrong law.
- `company/finance/revenue_accruals.py` and `company/finance/working_capital.py` are uncalled too.

## 1. Revenue recognition (IFRS 15): billed against unbilled

- Centrica 2019, note 3(b): revenue "includes an assessment of energy supplied to customers" between
  the last read and the year end; "Estimated revenue is restricted to the amount the Group expects to
  be entitled to"; industry reconciliation adjustments "can be material with adjustments of up to £30
  million." https://www.centrica.com/media/4090/financial-statements.pdf
- Octopus FY2024, note 2.4: "Revenue recognised includes an estimate of the sales value of units
  supplied to customers." https://octoenergy-production-media.s3.amazonaws.com/documents/Octopus_Energy_Limited_signed.pdf

| Supplier / year | Accrued (unbilled) income | Revenue | Share |
|---|---|---|---|
| Centrica group, 2019 | £1,342m | £22,674m | ~5.9% **[derived]**, group-wide |
| Octopus Energy Ltd, FY24 | £521.2m | £7,972.7m | ~6.5% **[derived]** |
| Octopus Energy Ltd, FY23 | £753.4m (incl. £286.1m unbilled EPG) | £9,437.1m | ~8.0% **[derived]** |

IFRS 15 text not retrieved; over-time recognition (para 35(a)) is **[unverified]**.

## 2. Bad debt (IFRS 9 expected credit loss)

- The simplified approach recognises lifetime expected losses on trade receivables through a
  provision matrix (secondary commentary, https://www.mondaq.com/Article/819718). Octopus provisions
  by customer age, payment method and supply status. The cap counts bad debt as the "Profit and loss
  charge incurred. Costs include write-offs and recoveries, movements in provisions."
  https://www.ofgem.gov.uk/sites/default/files/2025-05/Appendix-2-Decision-Debt-related-costs.pdf

| Supplier / year | Charge | Share |
|---|---|---|
| British Gas Energy, 2024 | £352m (2023: £541m) | residential 2.3% (2023: 3.1%); SME 6.1% (8.0%) |
| Octopus Energy Ltd, FY24 | £231.0m | ~2.9% **[derived]** |
| Octopus provision / gross trade debtors FY24 | £696.6m of £1,596.9m | ~44% **[derived]** (FY23 ~33%) |
| Centrica group, 2019 | £197m | ~0.9% of group revenue **[derived]** |

Source: https://www.centrica.com/media/f1jbfsfs/centrica-plc-2024-preliminary-results-announcement.pdf

- Cap: debt-related costs about 6% of standard-credit, 1% of DD and 0.4% of PPM dual-fuel bills
  (Apr-Jun 2023); baseline £71 per dual-fuel customer, allocated DD £57, standard credit £160, PPM £19
  (2025). Historical review Apr 2022-Jun 2025: bad debt charge £176, admin £25, working capital -£27,
  total £174 per customer. https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf
- Market debt and arrears rose from about £1.8bn (Oct 2021) to £5.02bn (Q2 2026).
  https://www.ofgem.gov.uk/data/debt-and-arrears-indicators

## 3. Customer credit balances and ringfencing

- Fixed-DD credit balances averaged £3.09bn over the year to Sep 2025 (£3.53bn a year earlier); the
  end-March 2026 balance was £1.9bn. Balances build in summer and are spent in winter.
  https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-april-2025-march-2026
- March 2026: suppliers held £2.7bn of cash against £1.9bn of domestic credit balances.
  https://www.ofgem.gov.uk/sites/default/files/2026-06/Supplier-financial-resilience-report-2026-v.1.1.pdf
- Ofgem may direct ringfencing below the Capital Target, or when "a supplier's cash position goes
  below 20% of the value of its gross CCBs from fixed direct debit customers" (the Cash Coverage
  Trigger). It is a power used by direction, not a blanket rule. Reporting began 20 Sep 2023.
  https://www.ofgem.gov.uk/sites/default/files/2023-07/FRC%20Decision%20doc%20-%20July%202023.pdf

## 4. Minimum Capital Requirement

- Capital Floor £0 Adjusted Net Assets (§1.6). Capital Target "£115 Adjusted Net Assets per domestic
  dual fuel equivalent customer" (§1.13), £57.50 per electricity and per gas customer. Ofgem consulted
  on £130 and decided £115. In force from 31 March 2025; between Floor and Target a supplier needs a
  credible Capitalisation Plan. ANA = tangible fixed assets plus current assets less liabilities, plus
  approved Alternative Sources of Capital (rated guarantees and facilities with 12 months' tenor).
  Source: the July 2023 decision above.
- March 2025: 20 of 23 suppliers above Target, about £7.5bn ANA. March 2026: £6.8bn against an
  aggregate Target of £3.1bn, 21 of 24 above. https://www.ofgem.gov.uk/sites/default/files/2025-04/FRC_transparency_report.pdf

## 5. Consolidated Segmental Statement and margins

- SLC 19A: audited statements separating supply from other activities, down to EBITDA and EBIT, with
  a reconciliation to statutory accounts; a 2025 modification standardises the reconciliation.
  https://www.ofgem.gov.uk/sites/default/files/2025-09/modification-of-consolidated-segmental-statements-review.pdf
  Centrica's and EDF's statements for 2016-2024 are read in `CSS_BENCHMARKS.md`.

| Centrica domestic EBIT | Electricity | Gas | Combined **[derived]** |
|---|---|---|---|
| 2015 | 0.3% | 12.5% | ~7.6% |
| 2016 | (3.9)% | 15.1% | ~7.2% |
| 2018 | 1.6% | 10.8% | ~6.7% |
| 2019 | (1.1)% | 4.7% | ~2.0% |
| 2023 | 7.8% | 1.4% | ~4.6% |

- Market EBIT £26 per domestic customer in 2024, £5.31 in 2025; domestic market EBIT £2.57bn (2023),
  £0.88bn (2024). The cap's allowance was the CMA's 1.9% EBIT to Sep 2023, then capital employed (£358
  per customer) at 12.3%: about 2.5-2.6% of the DD cap in 2026. No source supports "2.4%".
  https://www.ofgem.gov.uk/sites/default/files/2023-08/Price%20Cap%20-%20Decision%20on%20amending%20the%20methodology%20for%20setting%20the%20Earnings%20Before%20Interest%20and%20Tax%20(EBIT)%20allowance.pdf

## 6. Working capital and collateral

- Ofgem's collateral capital "£165 per customer" at 12.2%; working capital £127 per customer, about
  £167-168 under a price shock (CRA for Energy UK).
  https://www.energy-uk.org.uk/wp-content/uploads/2023/07/CRA-Non-Confidential-Report_230628_Final.pdf
- Centrica posted £105m of margin cash at end-2024 (2023: £240m). Octopus says its hedge is
  "procured through a third party without collateral requirements".

## Headline bands for checking the company

| Metric | Band | Basis |
|---|---|---|
| Unbilled income / annual revenue at year end | 5-8% | Centrica 2019, Octopus FY23-24 |
| Bad debt charge / residential revenue, normal | ~1-2% (thin) | Centrica 2019; cap DD ~1% |
| Bad debt charge / residential revenue, crisis | 2.3-3.1% | BGE 2023-24, Octopus ~2.9% |
| ECL provision / gross trade debtors | 33-44% | Octopus FY23-24 |
| Debt-related allowance per dual-fuel customer | ~£71 (DD £57 / SC £160 / PPM £19) | Ofgem 2025 |
| Domestic EBIT margin | allowance 1.9% then ~2.5-2.6%; actuals -1% to +8% per fuel | Ofgem, Centrica |
| Capital Floor / Target | £0 / £115 ANA per dual-fuel customer from 31 Mar 2025 | Ofgem 2023 |
| Cash / fixed-DD credit balances | trigger below 20%; market ~140% in Mar 2026 | Ofgem 2026 |
| Working capital / collateral per customer | ~£102-127 / ~£165 | Ofgem, CRA |

## Named gaps

1. Debt sale prices (pence in the pound): no primary source.
2. E.ON UK, EDF UK and OVO accounts not retrieved.
3. A BGE bad-debt series for 2016-2022, so the normal-times band is thin.
4. Market-wide segmental margins 2016-2024 (on Ofgem's data portal, not retrieved).
5. IFRS 15 and IFRS 9 text not fetched.
6. Centrica 2022-2025 accrued income (PDFs would not parse).
7. A monthly credit-balance series.
8. Corrected: the Capital Target is £115, not £130; no source supports a 2.4% EBIT allowance.
