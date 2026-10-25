# Director evidence: supplier accounts and capital

**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 05:15 GMT: "Is there no way to use the spare tokens productively? On knowledge creation for example ? Or improving the website? Things that don't impact it's need to run tasks in series"

The advisor spent spare allowance outside your serial gate on research for the knowledge pages the map found missing. This file is one of seven cited evidence packs landed in one commit.

## What to do with it

- Turn it into a published Knowledge page under the map steer (DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN). Register its concepts in the concept register.
- The headline-bands table at the end gives candidate world claims for the knowledge-checks-the-world gate. Grade the simulated world against them and say where it falls outside.
- Items marked [derived] are arithmetic you can re-run. Items marked [unverified] are not claims until you source them.
- Each named gap is a research task. Close it, or record that nothing is published.
- This is drafting work. Do it without displacing the serial queue. The research cost has already been spent.
- Correction it carries: Ofgem's Capital Target is £115 ANA per dual-fuel customer (decided July 2023), not the consulted £130. If any page or constant in the repo says £130, it is wrong. Check and fix.

---

# A GB energy supplier's accounts and capital: revenue, unbilled, bad debt and minimum capital

*Evidence pack for the Poesys knowledge layer. Compiled 25 October 2026. Figures marked **[derived]** are my own arithmetic on the cited numbers. Figures marked **[unverified]** come from recollection and no source was retrieved for them.*

---

## 1. Revenue recognition (IFRS 15): billed vs unbilled

**Policy as practised.** GB suppliers recognise revenue as energy is delivered, not when it is billed. The gap between the two is an estimated "unread" or "unbilled" balance.

- Centrica, 2019 accounts, note 3(b): "Revenue for energy supply activities includes an assessment of energy supplied to customers" between the last meter reading and the year end. "Estimated revenue is restricted to the amount the Group expects to be entitled to in exchange for energy supplied." The estimate runs through the billing systems and uses historical consumption, weather, load forecasts and differences between meter readings. Adjustments to industry reconciliation estimates "can be material with adjustments of up to £30 million." https://www.centrica.com/media/4090/financial-statements.pdf
- Octopus Energy Ltd, FY2024 accounts, note 2.4: "Revenue recognised includes an estimate of the sales value of units supplied to customers." https://octoenergy-production-media.s3.amazonaws.com/documents/Octopus_Energy_Limited_signed.pdf
- Centrica's audited Consolidated Segmental Statements (CSS) say the same: revenue "includes an assessment of energy supplied to customers between the date of the last meter reading and the year end." https://www.centrica.com/media/4011/centrica-2019-ofgem-statement.pdf

**Unbilled balances as a share of revenue**

| Supplier / year | Accrued (unbilled) income | Revenue | Share |
|---|---|---|---|
| Centrica group, 2019 | £1,342m (2018: £1,542m) | £22,674m | ~5.9% **[derived]**. Group-wide, so this is not a pure supply figure. |
| Octopus Energy Ltd, FY24 (to Apr 2024) | £521.2m | £7,972.7m | ~6.5% **[derived]** |
| Octopus Energy Ltd, FY23 | £753.4m (incl. £286.1m unbilled EPG) | £9,437.1m | ~8.0% **[derived]** |

Sources: Centrica (above); Octopus (above).

**Standard text.** I did not retrieve the IFRS 15 standard itself. From recollection **[unverified]**: energy supply is a performance obligation satisfied over time, because the customer simultaneously receives and consumes the benefit (IFRS 15 para 35(a)), and unbilled amounts are typically shown as accrued income or contract assets.

---

## 2. Bad debt: IFRS 9 ECL, charge levels, crisis uplift

**IFRS 9 method.** "IFRS 9 allows entities to apply a 'simplified approach' for trade receivables, contract assets and lease receivables… recognise lifetime expected losses". A provision matrix applies "the relevant loss rates to the trade receivable balances outstanding", with historical rates adjusted for "reasonable and supportable forward-looking information". This is secondary commentary; the standard text was not retrieved. https://www.mondaq.com/Article/819718

**How suppliers do it.** Octopus "assesses billed debt and accrued income to estimate recoverability". Its provision uses "historic non-payment trends" by customer age, payment method and supply status. Ofgem: "Suppliers make estimates (known as provisions) for the amount which will never be paid" and then "finalise them through write-offs." https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf

The cap measures bad debt as the "Profit and loss charge incurred. Costs include write-offs and recoveries, movements in provisions." https://www.ofgem.gov.uk/sites/default/files/2025-05/Appendix-2-Decision-Debt-related-costs.pdf

**Bad debt charge as a share of revenue**

| Supplier / year | Charge | Share of revenue |
|---|---|---|
| British Gas Energy, 2024 | £352m (2023: £541m) | Residential 2.3% (2023: 3.1%); SME 6.1% (2023: 8.0%) |
| Octopus Energy Ltd, FY24 | £231.0m | ~2.9% **[derived]** |
| Octopus, provision vs gross trade debtors FY24 | £696.6m of £1,596.9m | ~44% coverage **[derived]** (FY23: £270.8m of £825.8m, ~33%) |
| Centrica group, 2019 ("credit losses on financial assets") | £197m (2018: £143m) | ~0.9% of group revenue **[derived]** |

Sources: https://www.centrica.com/media/f1jbfsfs/centrica-plc-2024-preliminary-results-announcement.pdf ; Octopus and Centrica 2019 (above).

**Cap allowances and the crisis uplift (Ofgem)**

- In cap period 10a (Apr–Jun 2023), debt-related costs were "approximately 6% of typical dual fuel standard credit bills", "1% of typical dual fuel direct debit bills" and "0.4% of typical dual fuel prepayment meter (PPM) bills". The COVID-19 true-up was about £30 per dual-fuel customer. (Call for Input, above)
- The temporary "Float" was £28 per typical dual-fuel customer for Apr 2024–Mar 2025, then extended "at the current level of £31". https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy-price-cap-additional-debt-related-costs-extension-decision.pdf
- From the 2025 decision: baseline benchmark "£71 per dual fuel customer per year" (Q1 2023–Q4 2024 data), allocated DD £57, standard credit £160, PPM £19 (Table 5.1). (Appendix 2, above)
- Historical review, Apr 2022–Jun 2025, weighted average of eight suppliers per dual-fuel customer: bad debt charge £176, debt admin £25, working capital −£27, total £174. Suppliers "recovered £1.22 per customer more" than they incurred. https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf
- Market debt and arrears went from about £1.8bn to about £4.5bn between Oct 2021 and Sep 2025 (same source), reaching £5.02bn in Q2 2026 (+13% year on year). Arrears not on a repayment plan are "around three times greater than debt." https://www.ofgem.gov.uk/data/debt-and-arrears-indicators

**Write-off practice and debt sale prices.** The sources define write-offs only. None of them gave debt sale prices (see Gaps).

---

## 3. Customer credit balances (CCBs)

- Fixed-DD credit balances averaged £3.09bn over the 12 months to Sep 2025, down from £3.53bn a year earlier. https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-october-2024-september-2025
- The 12-month average to Mar 2026 was £3.2bn. The end-March 2026 balance was £1.9bn, up £181m on a year earlier. Accounts "will have more credit in them during the summer but then more is spent in the winter". https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-april-2025-march-2026
- In March 2026 suppliers held £2.7bn of cash against £1.9bn of domestic CCBs. https://www.ofgem.gov.uk/sites/default/files/2026-06/Supplier-financial-resilience-report-2026-v.1.1.pdf

**Ringfencing direction.** The 2023 decision gave Ofgem power to direct ringfencing when a supplier is below its Capital Target, or when "a supplier's cash position goes below 20% of the value of its gross CCBs from fixed direct debit customers" (the Cash Coverage Trigger). https://www.ofgem.gov.uk/sites/default/files/2023-07/FRC%20Decision%20doc%20-%20July%202023.pdf

Reporting started on 20 September 2023. Guidance and templates were updated on 17 July 2024. https://ofgem.gov.uk/decision/decision-introducing-minimum-capital-requirement-and-ringfencing-customer-credit-balances-direction

The 2026 report says Ofgem can direct ringfencing "where it is in the Consumer Interest to do so". Suppliers are "collectively holding amounts of cash which are significantly higher than the 20% reporting threshold". The trigger measure (20% of live fixed-DD CCB) peaked at £922m in Sep 2025, against average monthly cash of £3,360m. (2026 report, above)

**Note:** In the sources read, ringfencing is a power Ofgem can use by direction, not a blanket rule. That is the position for 2024–25.

---

## 4. Ofgem Minimum Capital Requirement

**Correction to the brief: the decided Capital Target is £115, not £130.** Ofgem consulted on £130 and set £115 in the July 2023 decision.

- Capital Floor: "We have decided to proceed with the consulted Capital Floor of £0 Adjusted Net Assets" (§1.6).
- Capital Target: "a target level of £115 Adjusted Net Assets per domestic dual fuel equivalent customer" (§1.13), which is "£57.50 per domestic electricity customer and £57.50 per domestic gas customer."
- Timetable: "these new rules will take effect from the 31st of March 2025." A supplier between the Floor and the Target is in an "Intermediate Position" and needs a credible Capitalisation Plan.
- Measure: Adjusted Net Assets = "(tangible fixed assets + current assets)" minus liabilities, plus approved Alternative Sources of Capital (§2.8). Those sources are unsecured loans, parent facilities and guarantees, rated by two of Moody's, S&P and Fitch, with at least 12 months of tenor left (§2.26–2.30).

Source for all of the above: https://www.ofgem.gov.uk/sites/default/files/2023-07/FRC%20Decision%20doc%20-%20July%202023.pdf

**Outcomes**

- March 2025: 20 of 23 suppliers above Target, about £7.5bn of Adjusted Net Assets (up from −£1.7bn net assets during the crisis), and £2.4bn of approved Alternative Sources of Capital. https://www.ofgem.gov.uk/sites/default/files/2025-04/FRC_transparency_report.pdf
- March 2026: £6.8bn held against an aggregate Target of £3.1bn, with 21 of 24 above Target (low of 18 at Q3 2025). Since 31 Mar 2025, suppliers below Target face default Transition Controls.

| Date | Net assets | Adjusted net assets |
|---|---|---|
| Dec 2023 | £3,536m | £1,664m |
| Dec 2024 | £4,857m | £3,600m |
| Mar 2025 | £6,138m | £7,480m |
| Dec 2025 | £5,119m | £5,448m |
| Mar 2026 | £5,879m | £6,849m |

Source: 2026 resilience report (above).

---

## 5. Consolidated Segmental Statement and margins

**Requirement.** Under ES/GS SLC 19A, "Relevant Licensees" publish audited statements that separate supply from other activities. Costs are split into direct fuel, transportation, environmental and social obligations, other direct and indirect costs, down to EBITDA and EBIT, with a numerical reconciliation to the statutory accounts. Ofgem's 2025 modification adds a standard reconciliation table, definitions quantified in £m, and a rule that the CSS format overrides the statutory format, with differences disclosed to the nearest £1m. It was intended to take effect on 31 Oct 2025. https://www.ofgem.gov.uk/sites/default/files/2025-09/modification-of-consolidated-segmental-statements-review.pdf

Centrica's 2019 CSS was audited by Deloitte with £20m materiality. Bad debt was allocated between fuels using actual billing-system cost. (Centrica 2019 CSS, above)

**Centrica (British Gas) domestic supply EBIT margins from the CSS**

| Year | Electricity | Gas | Combined **[derived]** |
|---|---|---|---|
| 2015 | 0.3% | 12.5% | ~7.6% |
| 2016 | (3.9)% | 15.1% | ~7.2% |
| 2018 | 1.6% | 10.8% | ~6.7% |
| 2019 | (1.1)% | 4.7% | ~2.0% |
| 2023 | 7.8% | 1.4% | ~4.6% |

Sources: https://www.centrica.com/media/x5fbv45i/2016_ofgem_consolidated_segmental_statement.pdf ; Centrica 2019 CSS (above) ; https://www.centrica.com/media/4zgl5yea/ofgem-consolidated-segmental-statement-2023.pdf

On a statutory basis, BGE's adjusted operating margin was 2.5% in 2024 and 4.2% in 2023 (Centrica 2024 prelims).

**Market-wide.** Average EBIT was £26 per domestic customer in 2024 and £5.31 in 2025. Domestic market EBIT was £2.57bn (2023), £0.88bn (2024), £0.19bn (2025 forecast) and £0.88bn (2026 forecast). (2026 resilience report)

**Ofgem's view of a normal margin**

- In 2018 the cap took "the CMA's 1.9% EBIT estimate".
- From 1 Oct 2023 the allowance became capital employed × cost of capital. Capital employed was £358 per customer at typical consumption, the cost of capital 12.3%, and working capital about £102 per customer. This gave an indicative £44 per year against £34 under the old method. https://www.ofgem.gov.uk/sites/default/files/2023-08/Price%20Cap%20-%20Decision%20on%20amending%20the%20methodology%20for%20setting%20the%20Earnings%20Before%20Interest%20and%20Tax%20(EBIT)%20allowance.pdf
- Resulting share of the DD cap: 2.50% (£44 of £1,758) in Jan–Mar 2026, and 2.6% of £1,862 in Jul–Sep 2026. https://www.ofgem.gov.uk/sites/default/files/2025-11/Summary-of-changes-to-energy-price-cap-1-January-to-31-March-2026.pdf ; https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026.pdf
- The "~2.4%" in the brief was not found in any source **[unverified]**. The verified range is 1.9% (2018–Sep 2023) to about 2.5–2.6% (2026).

---

## 6. Working capital and collateral

- **Collateral:** CRA's report for Energy UK cites Ofgem's collateral capital as "£165 per customer", costed at 12.2%. CRA's illustrative initial margin per customer runs from £294.88 to £688.05, depending on the ICE scanning rate. https://www.energy-uk.org.uk/wp-content/uploads/2023/07/CRA-Non-Confidential-Report_230628_Final.pdf
- **Working capital (Ofgem base case in the same report):** £127 per customer, peaking at about £167–168 under a price shock.
- **Margin cash in practice:** Centrica posted £105m at end-2024 (2023: £240m). BGE had a £456m working-capital outflow in 2024, attributed to "falling commodity prices" (Centrica 2024 prelims). Octopus says its hedge is "procured through a third party without collateral requirements" (Octopus FY24).
- **Seasonal DD levelisation:** Credit balances build in the warmer months, when earned revenue is below the flat payments. They turn into debit balances in winter (CRA para 44). Ofgem confirms the summer-high, winter-low pattern (CCB data pages, above). The cap's debt-related working-capital element came out at −£27 per customer for Apr 2022–Jun 2025 (historical debt review), meaning it was a net benefit to suppliers.

---

## Headline bands to check a simulated supplier against

| Metric | Band | Basis |
|---|---|---|
| Unbilled/accrued income ÷ annual revenue (year end) | 5–8% | Centrica 2019, Octopus FY23–24 |
| Bad debt charge ÷ residential revenue, normal times | ~1–2% | Centrica group 0.9% (2019); cap DD ~1% of bill. Thin evidence. |
| Bad debt charge ÷ residential revenue, crisis | 2.3–3.1% | BGE 2023–24, Octopus ~2.9% |
| Bad debt ÷ SME revenue | 6–8% | BGE |
| ECL provision ÷ gross trade debtors | 33–44% | Octopus FY23–24 |
| Debt-related cost allowance per dual-fuel customer | ~£71 baseline (DD £57 / SC £160 / PPM £19) | Ofgem 2025 |
| Domestic EBIT margin | allowance 1.9% → ~2.5–2.6%; actuals −1% to +8% per fuel | Ofgem, Centrica CSS |
| Market EBIT per customer | £5–26 (2024–25) | Ofgem 2026 |
| Capital Floor / Target | £0 / £115 ANA per dual-fuel customer, enforceable from 31 Mar 2025 | Ofgem 2023 |
| Cash ÷ fixed-DD CCB | must stay ≥ 20%; market about 140% in Mar 2026 (£2.7bn / £1.9bn) | Ofgem 2026 |
| CCB seasonal swing (market) | 12-month average ~£3.1–3.5bn; Mar trough ~£1.9bn | Ofgem CCB data |
| Working capital / collateral per customer | ~£102–127 / ~£165 | Ofgem via EBIT decision and CRA |

## Named gaps

1. **Debt sale prices (pence in the pound):** not found in any primary source.
2. **E.ON UK, EDF UK, OVO accounts:** not retrieved. The OVO report redirected and the press pages failed. Their unbilled, ECL and margin figures are missing.
3. **BGE bad debt 2016–2022 time series:** not retrieved, so the "normal-times" bad-debt band rests on thin evidence.
4. **Market-wide CSS margins 2016–2024 (all six large suppliers):** these sit on Ofgem's data portal and were not retrieved. Only Centrica's statements were read.
5. **IFRS 15 and IFRS 9 standard text:** not fetched. Paragraph references are recollection **[unverified]**.
6. **Centrica 2022–2025 accrued energy income:** those PDFs would not parse.
7. **Monthly CCB series:** sits on the Ofgem data portal and was not retrieved.
8. **Brief vs source:** the Capital Target is £115, not the consulted £130, and no source supports an EBIT allowance of "2.4%".
## Done

2026-10-25, autonomous worker, claim `map-steer-knowledge-pages-and-forward-plan`.

- Published as `site/knowledge/suppliers-accounts-and-capital/`, with the pack kept as the note
  `docs/market_research/suppliers_accounts_and_capital_2026-10-25.md` plus a read-from-code section.
- The £130 correction it carries: code already used £115 (`saas/growth_mandate.py`); six documents
  still called £130 the decided target and are corrected beside each claim.
- Three concepts registered: `capital.mcr`, `capital.ccb_coverage`, `accounts.segmental_statement`.
  Found: nothing computes the Cash Coverage Trigger, and the uncalled `company/risk/capital_adequacy.py`
  states thresholds no source supports.
- The company's own book is NOT graded against the bands here.
