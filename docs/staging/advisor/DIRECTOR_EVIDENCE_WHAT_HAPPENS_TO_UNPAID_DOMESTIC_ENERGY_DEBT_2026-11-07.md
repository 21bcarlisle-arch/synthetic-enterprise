**Severity:** RECORDED · **Lane:** E_finance_treasury · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] What happens to unpaid GB domestic energy debt: provisioning, final-account recovery, debt sale, write-off (2026-11-07)

**Type:** EVIDENCE, through the advisor channel. The director's words, from chat on Sat 7 Nov, 16:00 GMT: "ok, so we have a lot of tokens to use? How can we do that? A big knowledge push? What else?" He then chose two passes: write-offs and debt, and customer reactions.

**Use: it settles the write-off rule.** The value-test redesign (`docs/design/THE_VALUE_TEST_REDESIGN.md`) needs the write-off rule settled against GB evidence first. Today the world writes off every failed bill in full for any customer who ever leaves. The evidence does not support that. Suppliers model departed (final) debt as worse than live debt but not as a total loss: overall book coverage is about 30–36%, and Ofgem's own Debt Relief Scheme working paper uses about 75% provisioning on 2–3-year-old crisis debt. Switch rules (the 28-day debt objection, and prepayment debt assignment of £10–£500) mean most ordinary switchers cannot leave with old debt. Section 6 proposes a replacement rule. Verify it, adjust it, and decide; that decision is yours. Then run the value test's write-off measurement against it.

This pack is from an advisor research pass, sourced from the web. Figures are graded P, S or A, with [unverified] marking anything not confirmed against a primary source. Apply the 30 Oct data standard: verify against primary sources and re-derive figures from the underlying data where it is published. No world parameter may rest on S or A alone.

---

# GB domestic energy debt evidence pack: provisioning, final-account recovery, write-off and recovery after write-off

**Grading key:** P = primary publication by the data holder (Ofgem, the supplier's own accounts, legislation, DWP). S = secondary summary (news, charity summary, consultancy, a commentator reading the accounts). A = assumption I have built from the evidence for simulation use. **[unverified]** = not confirmed against a primary source in this session.

**Coverage note.** I could not get Centrica's ageing and ECL table. The centrica.com annual report URLs and financial-filings mirrors were blocked or returned truncated text. One SEC XBRL ageing table looked like Centrica's but turned out to be a different (US) company, and I discarded it. Instead I used ScottishPower Energy Retail Ltd (SPERL) 2024, Octopus Energy Ltd FY2022 and OVO (via a commentator) as published GB supplier evidence. Centrica is listed in the gaps.

---

## 0. Bottom line for the simulation rule

The current rule writes off 100% of every failed bill for any customer who ever leaves. GB evidence does not support it, for five reasons.

1. **Suppliers' own provision models treat "lost (final)" debt as worse than live debt, but not as a total loss.** ScottishPower Energy Retail's 2024 accounts describe a provision matrix that reflects "the differences in collection rates between debt attributable to current or lost (final) customers" and "the greater challenge in collecting older debt balances." The model is "supported by a projection based on a 36-month cash collection performance" ([SPERL 2024 accounts](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P**. If final debt were treated as 100% lost, there would be no collection rate to model.
2. **Total book coverage is about 30–36%, not 100%.** SPERL's allowance on billed domestic and SME receivables was £332.7m on £931.8m gross (about 35.7%) at end-2024, against 32.0% at end-2023 ([SPERL 2024](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P**. Octopus Energy Ltd provided £164.5m on £537.0m gross (30.6%) at 30 April 2022 ([Octopus Energy Ltd accounts 2022](https://octopusenergy.group/static/documents/Octopus-Energy-Limited-accounts-2022.pdf)) **P**.
3. **Even old, crisis-era debt of benefit recipients is provisioned at about 75%, not 100%.** Ofgem's Debt Relief Scheme working paper uses "an average weighted provisioning rate of approximately 75%," with a floor of 56.7% ([Ofgem DRS working paper, Aug 2025](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf)) **P**.
4. **Debt that is sold still has a market value.** E.ON sells debt to Lowell Portfolio I Ltd ([Lowell, E.ON page](https://www.lowell.co.uk/eon)) **P**. Buyers offer large settlement discounts, for example a "pre-approved 75% discount" on an E.ON-origin debt held by PRAC Financial ([inkl/press report](https://www.inkl.com/news/law-firm-for-debt-company-pursues-customers-for-e-on-bills-on-homes-they-weren-t-living-in)) **S**.
5. **Switching rules mean most departing credit customers cannot leave with old debt.** A supplier may object to a transfer for debt owed 28 days or more (SLC 14.4) ([CPAG](https://askcpag.org.uk/?id=-242650)) **S**. Prepayment debt from £10 to £500 per fuel travels to the new supplier under the Debt Assignment Protocol (SLC 14.6) ([CPAG](https://askcpag.org.uk/?id=-242650); [Citizens Advice](https://citizensadvice.org.uk/consumer/energy/energy-supply/get-a-better-energy-deal/switching-energy-supplier-if-youre-in-debt)) **S**. Large unpaid final balances therefore come mostly from home moves, "occupier" accounts and supplier failures, not from ordinary switches.

**A defensible replacement (A):** apply a final-account loss given default (LGD) of about 65–80% to the unpaid balance at departure, and phase recovery over 24–36 months. Keep a residual 3–10p in the pound from debt sale, or a slow tail from debt collection agencies (DCAs). Do not write off customers who leave owing nothing or less than one bill cycle that they then pay. Section 6 has the parameters.

---

## 1. (a) IFRS 9 expected credit loss provisioning as GB suppliers do it

### 1.1 Method

- Suppliers use the IFRS 9 simplified (lifetime ECL) approach with a provision matrix. SPERL's matrix is segmented by (i) current versus lost (final) customers and (ii) age of balance. It is based on historical credit loss experience adjusted for forward-looking factors ([SPERL 2024](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P**.
- Octopus (FY2022): "management calculates a bad debt provision based on historic non-payment trends based on age of customer balances" and "uses these percentages to calculate the bad debt provision" ([Octopus Energy Ltd 2022](https://octopusenergy.group/static/documents/Octopus-Energy-Limited-accounts-2022.pdf)) **P**.
- Ofgem describes the cycle like this: "Suppliers make estimates (known as provisions) for the amount which will never be paid. They then adjust these estimates over time, and eventually finalise them through write-offs" ([Ofgem Call for Input on debt-related costs, Apr 2023, para 2.6](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf)) **P**. Ofgem notes suppliers differ on "the point at which suppliers 'provision' for bad debt" and "when debt is written off" (paras 4.4) **P**.
- Ofgem measures bad debt for the cap as a P&L charge "including write-offs and recoveries, movements in provisions and credit balance recognition." It considered and rejected a bottom-up model by age, payment method and live/final status ([Ofgem Appendix 2, Debt-related costs, Dec 2024](https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf)) **P**. So even Ofgem has no published industry provision rates by age and live/final status.
- Ofgem's 2026 review cites differing provisioning methodologies between suppliers as a reason not to use a lower-quartile benchmark ([Ofgem, review of historical debt-related costs, Mar 2026, para 3.50](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) **P**.

### 1.2 Published coverage figures (GB suppliers)

| Supplier / date | Gross billed receivables | Loss allowance | Coverage | Impairment charge (year) | Revenue | Charge / revenue | Grade |
|---|---|---|---|---|---|---|---|
| SPERL, 31 Dec 2024 | £931.8m | £332.7m | 35.7% | £108.0m | £4,690.4m | 2.3% | P ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) |
| SPERL, 31 Dec 2023 | £897.4m | £286.9m | 32.0% | £207.0m (£201.2m on IFRS 15 receivables) | £7,610.6m | 2.7% | P (same) |
| Octopus Energy Ltd, 30 Apr 2022 | £537.0m | £164.5m | 30.6% | £106.4m | £3,911.1m | 2.7% (stated) | P ([Octopus 2022](https://octopusenergy.group/static/documents/Octopus-Energy-Limited-accounts-2022.pdf)) |
| Octopus Energy Ltd, 30 Apr 2021 | £192.9m | £66.1m | 34.3% | £53.0m | £1,897.4m | 2.8% (stated) | P (same) |
| OVO Energy Ltd, 2021–2024 | n/a | n/a | n/a | £80m / £113m / £214m / £212m | £0.96bn / £5.04bn / £8.17bn / £5.46bn | 8.3% / 2.2% / 2.6% / 3.9% | S ([Watt-Logic](https://watt-logic.com/2026/02/04/ovo-energy-looking-shaky/)) |

Ratios marked "computed" in the text below are my arithmetic on the P figures. SPERL's sensitivity disclosure: ±5% on the overall expected loss rate moves the allowance by ±£46.6m ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P**.

### 1.3 Ageing buckets and provision rates by age

**No GB domestic supplier ageing table with loss rates by bucket was retrieved in this session.** Octopus FY2022 explicitly gives none ([Octopus 2022](https://octopusenergy.group/static/documents/Octopus-Energy-Limited-accounts-2022.pdf)) **P**. The SPERL excerpt read did not contain one ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)). Centrica is believed to publish a days-past-due table for residential receivables [unverified, not retrieved].

The best anchors for an age curve are:
- overall book coverage of 30–36% (above) **P**;
- about 75% weighted provisioning on debt accrued April 2022 to March 2024 and at least 91 days old, which was roughly 2–3.5 years old in 2025–26. The floor is 56.7%, and individual suppliers range from 53% to 87% in Ofgem's illustration ([DRS working paper, paras 5.20, 5.27, Table 0-5](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf)) **P**;
- SPERL's 36-month collection-curve basis **P**, which implies that by about 36 months the remaining balance is close to fully provisioned.

The assumed curve in Section 6 is built from these anchors (**A**).

### 1.4 Live versus final accounts

- The live/final distinction is a named segment in SPERL's provision matrix ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P**. No GB supplier publishes separate loss rates for each segment [gap].
- Ofgem's October 2025 debt package says suppliers estimate "£1.1 and £1.7bn" of historic debt sits on accounts in "occupier" status. That is up to a third of the total, and Ofgem says it is "written off in the worst case" ([Ofgem press release, 30 Oct 2025](https://www.ofgem.gov.uk/press-release/ofgem-set-out-plan-reset-and-reform-growing-energy-debt)) **P**. Occupier accounts are the closest published proxy for "untraceable final" debt.
- When a supplier fails to issue final bills properly, final-account debt can become uncollectable. E.ON Next "voluntarily wrote off the debt of those customers who left supply" during its SLC 27.17 non-compliance from February 2021 to September 2023. More than 248,000 former prepayment accounts were affected ([Ofgem decision, E.ON Next £14.5m](https://ofgem.gov.uk/decision/eon-next-pay-total-ps145m-former-prepayment-meter-customers-due-failure-issue-final-bills)) **P**.

### 1.5 How provisions moved through the 2022–23 crisis

- Ofgem: debt-related costs "peaked in summer 2023 at well over twice the prior year's level" ([Ofgem Appendix 2](https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf)) **P**.
- SPERL: the impairment charge fell from £207.0m (2023) to £108.0m (2024), while coverage rose from 32.0% to 35.7%. That pattern is consistent with ageing crisis debt moving into higher provision buckets as new defaults slowed ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P** (interpretation **A**). SPERL attributes the allowance to "recovery of historic debt from the PPM moratorium and the energy crisis, plus new bad debt from affordability concerns" (same) **P**.
- Octopus: gross receivables rose 2.8× from April 2021 to April 2022, while coverage fell from 34.3% to 30.6% because the new debt was young ([Octopus 2022](https://octopusenergy.group/static/documents/Octopus-Energy-Limited-accounts-2022.pdf)) **P**.
- OVO: the impairment charge rose from £113m (2022) to £214m (2023) and stayed at £212m (2024) ([Watt-Logic](https://watt-logic.com/2026/02/04/ovo-energy-looking-shaky/)) **S**.
- Market stock: total debt and arrears over 91 days were about £1.8bn in October 2021 and about £4.5bn in September 2025 ([Ofgem Mar 2026 review](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) **P**. They reached £4.79bn in Q1 2026 ([Irish News/PA, 25 Jun 2026](https://www.irishnews.com/news/uk/energy-debt-reaches-record-479-billion-ahead-of-13-price-cap-jump-3PJPXVQHG5MHBBWPDNRGXW7IKA/)) **S** and £5.02bn in Q2 2026 ([Ofgem debt and arrears indicators](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators)) **P**.

---

## 2. (b) When a customer leaves owing money

### 2.1 Final bill and collection practice

- **Final bill:** suppliers must "take all reasonable steps to send a final Bill or statement of account" within six weeks of supplier transfer or contract termination (SLC 27.17) ([Ofgem E.ON Next decision](https://ofgem.gov.uk/decision/eon-next-pay-total-ps145m-former-prepayment-meter-customers-due-failure-issue-final-bills)) **P**.
- **Reminders, then DCA or debt sale.** No Ofgem source retrieved sets standard timings. Industry practice is usually final bill, then two or three reminders over 4–8 weeks, then trace and DCA placement around 60–120 days, then a second DCA or sale after 6–18 months **A [unverified]**.
- Debt sale happens. Lowell states that for E.ON debts "we've bought it from e.on," with Lowell Portfolio I Ltd as purchaser and Lowell Financial or Overdales Legal collecting ([Lowell](https://www.lowell.co.uk/eon); [Lowell, EDF](https://www.lowell.co.uk/edf)) **P**. PRAC Financial (via BW Legal) bought E.ON-origin occupier-account debt, in one case at least 5.5 years after the period of supply ([inkl report](https://www.inkl.com/news/law-firm-for-debt-company-pursues-customers-for-e-on-bills-on-homes-they-weren-t-living-in)) **S**. EDF had a 2018 incident with debt collectors wrongly contacting households ([MSE](https://blog.moneysavingexpert.com/news/2018/05/edf-apologises-after-hundreds-of-households-are-wrongly-contacted-by-debt-collectors)) **S**.
- **Collection cost:** Ofgem's DRS impact assessment uses 3p per £1 of debt and arrears as the debt collection cost ([Ofgem DRS Impact Assessment, Nov 2025](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf)) **P**.

### 2.2 Recovery rates on final-account debt

- **No published GB recovery rate for final-account energy debt was found** [gap].
- Indirect anchors:
  - The 75% weighted provisioning on crisis debt implies an expected recovery of about 25p in the £ on 2–3-year-old debt, for a cohort that includes live accounts ([DRS working paper](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf)) **P** (implication **A**).
  - "Average time to recover Eligible Debt: more than 22 months" ([DRS Impact Assessment](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf)) **P**.
  - Ofgem: "a larger debt will likely be outstanding for longer, and therefore may be less likely to be repaid" ([Ofgem CfI 2023, para 4.8](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf)) **P**.
  - A debt buyer offering a "pre-approved 75% discount" implies that buyers see settlement at 25p as profitable on a purchase price well below that ([inkl](https://www.inkl.com/news/law-firm-for-debt-company-pursues-customers-for-e-on-bills-on-homes-they-weren-t-living-in)) **S**.

### 2.3 Share eventually written off, and timing

- Write-off timing differs by supplier and is not published (Ofgem CfI para 4.4, [link](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf)) **P**.
- SPERL's 36-month collection-curve horizon ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) **P** and the Limitation Act's six years (below) bracket the practical write-off window. Typical accounting write-off is after 12–36 months for final accounts, often when the debt is sold or a DCA returns it **A [unverified]**.

### 2.4 Debt sale prices (pence in the pound)

- **No GB source retrieved publishes utility debt-sale prices** [gap].
- Market structure evidence: UK debt-buyer cash multiples fell from about 3.0× (Arrow, 2010) and 3.67× (Cabot, 2009) to about 1.5–1.7× by 2014. The collection tail lengthened from about 60 months to about 120 months ([L.E.K., UK Debt Purchase Market, c.2016](https://www.lek.com/sites/default/files/insights/pdf-attachments/1801_UK_Debt_Purchase_Market_Debt_Buying_Industry_Consulting_LEK_Executive_Inisghts.pdf)) **S**.
- An Arvato case study confirms energy utility residual debt is sold for "a comprehensible and fair purchase price" paid upfront. Average leaver debt was about €600 (probably Germany, no price given) ([Arvato case study](https://finance.arvato.com/4a828a/globalassets/02-documents/01-corp/02-insights/03-case-study/case-study-en-debt-purchase-utility.pdf)) **S**.
- **Working assumption:** aged final-account energy debt (12+ months, already through one or two DCAs) sells for 3–8p in the £. Fresher final debt (3–9 months, untouched) sells for 8–15p **A [unverified]**. These figures are consistent with a buyer's ~2× gross multiple and the ~25p discounted-settlement offers above.
- ScottishPower's 2026 proposal would ring-fence about £1.6bn (one third of £4.8bn) of "unable to pay" debt and sell it to banks, repaid "over around 10 years at under £10 per household each year." No price was disclosed ([Scottish Financial Review citing FT, 30 Jun 2026](https://scottishfinancialreview.com/2026/06/30/scottish-power-household-debts-should-be-securitised/)) **S**.

### 2.5 Can debt block a switch?

- **Credit meters:** a supplier may object to a transfer for debt owed 28 days or more (SLC 14.4). It must tell the customer the grounds, how to resolve them, and that they have 30 working days to pay (SLC 14.9). It must keep evidence for 12 months (SLC 14.10) ([CPAG](https://askcpag.org.uk/?id=-242650)) **S**. Citizens Advice puts it as: you can switch if the bill was sent "less than 28 days ago," otherwise you "can't switch until you pay the bill" ([Citizens Advice](https://citizensadvice.org.uk/consumer/energy/energy-supply/get-a-better-energy-deal/switching-energy-supplier-if-youre-in-debt)) **S**.
- **Prepayment, Debt Assignment Protocol (SLC 14.6):** debts from £10 to £500 can be assigned to the new supplier with its consent, and the old supplier cannot block within that range. Assignment is normally within 90 days of the new supplier taking over, and the right can be lost if time limits are missed ([CPAG](https://askcpag.org.uk/?id=-242650)) **S**. Citizens Advice gives separate thresholds of "more than £500 for gas" and "more than £500 for electricity" ([Citizens Advice](https://citizensadvice.org.uk/consumer/energy/energy-supply/get-a-better-energy-deal/switching-energy-supplier-if-youre-in-debt)) **S**. Per-fuel application is likely but [unverified] against the licence text.
- **Disputed PPM debt of £500 or less:** the supplier cannot object if the debt is wholly disputed or arose from supplier error (SLC 14.7) ([CPAG](https://askcpag.org.uk/?id=-242650)) **S**.
- **Simulation implication (A):** switchers on credit meters should leave with at most the final bill plus any balance less than 28 days old. Debt older than that blocks the switch, and a sensible model has a share of blocked customers pay to switch. PPM switchers with debt of £500 or less per fuel move their debt, so it leaves the book at face value with no loss to the losing supplier. Final-account debt that is old and large comes from change of tenancy, occupier accounts, death and insolvency.

### 2.6 Limitation

- England and Wales: Limitation Act 1980 s.5 bars an action on a simple contract six years after the cause of action accrued ([legislation.gov.uk, s.5](https://www.legislation.gov.uk/ukpga/1980/58/section/5)) **P**. The page was blocked from fetch in this session, but the provision is long-established.
- Scotland: 5-year prescription under the Prescription and Limitation (Scotland) Act 1973 **[unverified]**.
- Debt buyers pursue E.ON-origin debts more than five years old ([inkl](https://www.inkl.com/news/law-firm-for-debt-company-pursues-customers-for-e-on-bills-on-homes-they-weren-t-living-in)) **S**, so collection can continue right up to the limitation bar.
- **Simulation rule (A):** no recovery after month 72 from the date of the final bill. In Scotland, use month 60.

---

## 3. (c) Write-off on live versus departed accounts; the Debt Relief Scheme; cap allowances

### 3.1 Live accounts

- Live debt is collected through payment plans, Fuel Direct, or prepayment conversion. Ofgem's arrears indicators for Q2 2026 ([Ofgem](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators)) **P** show:

| | Electricity | Gas |
|---|---|---|
| Accounts repaying debt under an arrangement | 888,824 | 726,838 |
| Average debt on an arrangement | £842 | £697 |
| Accounts in arrears with no arrangement | 1,187,788 (4.0% of customers) | 954,966 (3.9%) |
| Average arrears with no arrangement | £1,872 | £1,613 |

  "The value of arrears not on a repayment plan was around three times greater than debt" (same) **P**.
- Total debt and arrears were £5.02bn in Q2 2026, up 13% year on year (same) **P**. The page's publication date reads 27 June 2025, which conflicts with the Q2 2026 data it shows.

### 3.2 Ofgem Debt Relief Scheme (2025–26)

- **Size:** "up to £500m" for "around 195,000 customers" in Phase 1 ([Ofgem press release, 30 Oct 2025](https://www.ofgem.gov.uk/press-release/ofgem-set-out-plan-reset-and-reform-growing-energy-debt)) **P**. The impact assessment models Phase 1 on £0.905bn of eligible debt across 706,000 accounts. It expects £312.4m–£472.9m written off for 280,000–400,000 accounts. Phase 2 covers about £1.6bn across about 1.7m accounts ([DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf)) **P**. The explanatory memorandum puts the total at up to £1bn across phases ([Selectra](https://selectra.co.uk/energy/news/energy-debt-write-off-legal-blocker-lifted-195000-households)) **S**.
- **Eligibility:**
  - Means-tested benefits (the Warm Home Discount test).
  - More than £100 of debt (the documents also say "£100 or more").
  - Accrued 1 April 2022 to 31 March 2024, and outstanding at least 91 days.
  - The customer must contribute towards the debt or ongoing use, or engage with debt advice.
  - Sources: [DRS working paper](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf); [Ofgem press release](https://www.ofgem.gov.uk/press-release/ofgem-set-out-plan-reset-and-reform-growing-energy-debt) **P**.
- **Live accounts only.** The IA defines a Live Account as one with active supply at implementation. Final-account debt is not addressed ([DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf)) **P**. This matters for the simulation: the scheme is not a recovery route for departed debt.
- **Funding:**
  - Reimbursement = eligible debt written off × (1 − average provisioning rate) + admin + interest. The total requirement is £91.8m–£145.6m, or £3.23–£5.13 per dual-fuel household over one year, recovered through network charges on a "pay when paid" basis, with payments from May 2027 ([DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf); [working paper §6](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf)) **P**.
  - Net reimbursement is about 20% of face value under the notional model and at most about 38% under the hybrid model (working paper) **P**.
  - The press release instead says costs are spread through "the existing debt allowance, which currently adds £52" ([Ofgem](https://www.ofgem.gov.uk/press-release/ofgem-set-out-plan-reset-and-reform-growing-energy-debt)) **P**. The two documents describe the funding route differently, and this is worth reporting.
- **Status:** licence changes were confirmed January 2026. The DWP data-sharing regulations (Digital Government (Disclosure of Information) Regulations 2026) came into force 18 September 2026. No customer-contact start date had been set as at November 2026 ([Selectra, updated 7 Nov 2026](https://selectra.co.uk/energy/news/energy-debt-write-off-legal-blocker-lifted-195000-households)) **S [unverified against Ofgem]**.

### 3.3 Bad-debt allowances in the price cap

- **Debt-related costs (DRC) allowance by payment method,** Cap 13a, £ per dual-fuel customer per year at benchmark consumption ([Ofgem Appendix 2](https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf)) **P**:

| Payment method | Excluding adjustment allowances | Including adjustment allowances | Share of the cap (excl. / incl.) |
|---|---|---|---|
| Direct Debit | £25 | £56 | 1.4% / 3.2% |
| Standard Credit | £121 | £152 | 6.5% / 8.1% |
| PPM | £10 | £19 | 0.6% / 1.1% |

  The proposed reset for April 2025 was DD £60, SC £156, PPM £24 (net of a £21 working-capital proxy in EBIT). The weighted benchmark was £73 (same) **P**.
- **Headline:** about £52 per typical bill ([Ofgem, Oct 2025](https://www.ofgem.gov.uk/press-release/ofgem-set-out-plan-reset-and-reform-growing-energy-debt)) **P**. About £55 per year in mid-2026 ([SFR/FT](https://scottishfinancialreview.com/2026/06/30/scottish-power-household-debts-should-be-securitised/)) **S**.
- **Additional debt costs "float" (2022–24 debt):**
  - £28 per typical dual-fuel customer (£30.57 at benchmark), applied 1 April 2024 to 30 June 2025 to DD and SC only. Its bad-debt component was £55.35, offset by −£11.36 debt admin and −£13.43 working capital ([Ofgem Mar 2026 review, Table 2.3](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) **P**.
  - Decision documents: [Feb 2024 decision](https://www.ofgem.gov.uk/sites/default/files/2024-02/Energy-price-cap-additional-debt-costs-review-decision.pdf); [Feb 2025 extension](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy-price-cap-additional-debt-related-costs-extension-decision.pdf) **P**.
- **True-up review (minded-to, March 2026):**
  - Over 1 April 2022 to 30 June 2025, suppliers' debt-related revenue (weighted average) was £175 per customer, of which bad debt was £159. Costs were £174, of which bad debt was £176. Net over-recovery was £1.22, or £0.38 a year, 0.03% of the cap.
  - Ofgem is minded to make no further adjustment. The final decision was expected August 2026 [unverified whether issued].
  - Most suppliers over-recovered on DD and under-recovered on SC, with PPM under-recovered to a lesser extent. The sample was 8 suppliers, about 94% of domestic accounts ([Ofgem Mar 2026](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) **P**.
  - **Derived (A):** the weighted-average bad-debt cost of £176 over 39 months is about £54 per dual-fuel customer per year in 2022–25.
- **COVID true-up:** total COVID-19 debt-related allowance of about £30 per typical customer, over cap periods 4–7 ([Ofgem CfI 2023, para 3.1](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf); [decision](https://www.ofgem.gov.uk/sites/default/files/2023-02/Price%20cap%20-%20Decision%20on%20the%20true-up%20process%20for%20COVID-19%20costs.pdf)) **P**.
- **Additional Support Credit (ASC) allowance:** £8.77 added to the dual-fuel PPM cap at nil consumption, 1 October 2023 to 30 June 2025 ([Ofgem Mar 2026, para 2.17](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) **P**. Appendix 2 rounds it to £9 ([Appendix 2](https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf)) **P**. ASC is emergency credit given to PPM customers that suppliers may never recover. Further documents: [ASC allowance consultation 2023](https://www.ofgem.gov.uk/sites/default/files/2023-08/Allowance%20for%20additional%20support%20credit%20bad%20debt%20costs1692828077507.pdf); [ASC extension decision letter](https://www.ofgem.gov.uk/sites/default/files/2024-08/ASC_Extension_Decision_Letter_0.pdf) **P**.

### 3.4 Bad-debt charge as a share of revenue

- Octopus 2.7% (FY22) and 2.8% (FY21) **P**; SPERL 2.3% (2024) and 2.7% (2023, computed) **P**; OVO 2.2–3.9% for 2022–24 **S**. Sources are as in §1.2.
- Ofgem (cap period 10a): debt-related costs are about 6% of a typical dual-fuel Standard Credit bill, about 1% for DD and 0.4% for PPM ([CfI 2023, para 1.2](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf)) **P**.
- **Parameter (A):** a blended charge of 2.3–3.0% of revenue for 2022–25, and 1.0–1.5% in a normal year (pre-2020, [unverified]).

---

## 4. (d) Recoveries over time and repayment plans

- **After write-off (sold debt):** buyers collect over a tail of about 84–120 months at gross multiples of about 1.5–2× the purchase price ([L.E.K.](https://www.lek.com/sites/default/files/insights/pdf-attachments/1801_UK_Debt_Purchase_Market_Debt_Buying_Industry_Consulting_LEK_Executive_Inisghts.pdf)) **S**. For the selling supplier, recovery after sale is the sale price received at once, and nothing further **A**.
- **After write-off (retained with a DCA):** no GB energy data was found [gap]. Assumption: 5–12p in the £ gross over 36 months, less 15–30% DCA commission, so 4–10p net **A [unverified]**.
- **Repayment plans:** no published GB failure rate was found [gap].
  - StepChange: 45% of new clients with energy arrears had a negative budget, against 24% of those without arrears. Average energy arrears were £1,826 in 2023 and rose from £1,608 to £2,050 during that year. The case evidence includes suppliers demanding £232 a month against a £30 offer ([StepChange response, May 2024](https://stepchange.org/Portals/0/23/Reports/StepChange-Response-To-Ofgem-Affordability-And-Debt-Call-For-Input-May-2024.pdf)) **P** (StepChange client data).
  - Citizens Advice: average client energy debt is over £1,840, up 21% ([Citizens Advice, Debt protection gap, Apr 2024](https://www.citizensadvice.org.uk/policy/publications/the-debt-protection-gap/)) **P**.
  - Ofgem's DRS IA assumes engaged customers on plans contribute £15–£50 over six months, and puts the average recovery time for eligible debt at more than 22 months ([DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf)) **P**.
  - **Parameter (A):** about 35–50% of new repayment plans break within 12 months, with a higher rate for customers with a negative budget [unverified].
- **Average debt on a plan versus off a plan:** £842 versus £1,872 for electricity ([Ofgem](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators)) **P**. This is consistent with plans being concentrated on smaller, more recoverable debts.

---

## 5. (e) Prepayment debt

- **Recovery through the meter:** no published GB recovery rate per £ of PPM debt was found [gap].
- PPM debt-related costs are the lowest of any payment method: £10 per customer excluding adjustments, £19 including ([Appendix 2](https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf)) **P**. In the true-up, PPM bad-debt allowances moved from £9.20 (Cap 8) to £19.66 (Cap 14a), and PPM was under-recovered on average, but less than SC ([Ofgem Mar 2026](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) **P**.
- The ASC allowance (£8.77) shows that some PPM credit is unrecoverable by design (§3.3) **P**.
- **Fuel Direct (DWP third-party deductions):**
  - A "fixed amount towards the arrears," paid to the supplier every four weeks in arrears, with the first payment taking six weeks or more.
  - At most three arrears deductions at once, and claimant consent is needed if total deductions exceed 25% of the main benefit.
  - PPM customers can have only arrears deductions, not ongoing consumption.
  - Source: [gov.uk Fuel Direct guide for suppliers, updated 1 Apr 2026](https://www.gov.uk/government/publications/how-to-request-deductions-from-benefit-a-guide-for-creditors/third-party-deductions-from-benefits-a-guide-for-fuel-suppliers) **P**.
  - The rate is believed to be about 5% of the Universal Credit standard allowance [unverified].
- **Debt assignment on switching:** £10–£500 per fuel transfers to the new supplier (SLC 14.6) (§2.5) **S**.
- **Final PPM accounts:** final bills for former PPM customers have often not been issued properly. E.ON Next (more than 248,000 accounts), Octopus (£1.5m) and Good Energy (£150k) all paid redress, and E.ON Next wrote off leavers' debt ([E.ON Next](https://ofgem.gov.uk/decision/eon-next-pay-total-ps145m-former-prepayment-meter-customers-due-failure-issue-final-bills); [Octopus](https://www.ofgem.gov.uk/decision/octopus-energy-pay-total-ps15m-former-prepayment-meter-customers-due-failure-issue-final-bills); [Good Energy](https://www.ofgem.gov.uk/decision/good-energy-pay-total-ps150k-former-prepayment-meter-customers-due-failure-issue-final-bills)) **P**. Among E.ON's affected former PPM accounts, about 100,000 were in credit, averaging £51 (E.ON decision) **P**. This shows that departed PPM accounts often net to credit, not debt.
- **Parameter (A):** recovery through the meter on live PPM debt runs at £2–£5 a week (debt-recovery rate on the meter, [unverified]). Live PPM debt LGD is about 25–40%, and debt assigned on a switch is a 0% loss to the losing supplier.

---

## 6. Parameter table for the simulation

| # | Parameter | Value | Basis | Grade |
|---|---|---|---|---|
| 1 | Provision rate, live credit account, not yet due | 1% | Book coverage of 30–36% overall ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf), [Octopus](https://octopusenergy.group/static/documents/Octopus-Energy-Limited-accounts-2022.pdf)) | A |
| 2 | Provision rate, live, 1–30 days past due | 4% | as above | A |
| 3 | Provision rate, live, 31–90 days | 12% | as above | A |
| 4 | Provision rate, live, 91–180 days | 25% | as above | A |
| 5 | Provision rate, live, 181–365 days | 45% | as above | A |
| 6 | Provision rate, live, 1–2 years | 65% | DRS ~75% on 2–3-year-old debt ([working paper](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf)) | A anchored on P |
| 7 | Provision rate, live, 2–3 years | 75% (range 57–87%) | DRS mean and floor; supplier spread 53–87% | P-anchored |
| 8 | Provision rate, live, more than 3 years | 90% | 36-month collection curve ([SPERL](https://www.scottishpower.com/userfiles/file/SPERL_2024_Accounts.pdf)) | A |
| 9 | Provision rate, final account, 0–90 days after final bill | 35% | Final debt is collected worse than live (SPERL matrix) | A |
| 10 | Provision rate, final, 91–180 days | 55% | as above | A |
| 11 | Provision rate, final, 181–365 days | 75% | as above | A |
| 12 | Provision rate, final, 1–2 years | 88% | as above | A |
| 13 | Provision rate, final, more than 2 years, or "occupier" untraced | 95–100% | Ofgem: occupier debt written off "in worst case" ([Ofgem](https://www.ofgem.gov.uk/press-release/ofgem-set-out-plan-reset-and-reform-growing-energy-debt)) | A / P-anchored |
| 14 | Final-account debt outcome, traced and balance under £250 | Full 45% / partial 15% / none 40%, within 12 months | Small final bills are often paid after reminders | A [unverified] |
| 15 | Final-account debt outcome, traced and balance £250–£1,500 | Full 20% / partial 25% (average 40% of balance) / none 55%, within 24 months | Implied ~25p recovery on aged debt (DRS 75%) | A |
| 16 | Final-account debt outcome, more than £1,500 or untraced "occupier" | Full 5% / partial 15% (average 30%) / none 80%, within 36 months | Ofgem 4.8 "larger debt … less likely to be repaid" ([CfI](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf)) | A |
| 17 | Blended final-account LGD (pre-sale) | 65–80% | Rows 14–16 weighted | A |
| 18 | Timing of recovered cash on final accounts | 50% in months 1–3, 30% in months 4–12, 20% in months 13–36 | 22+ month average recovery ([DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf)) | A |
| 19 | Accounting write-off point, final accounts | 12–24 months after final bill, or on sale | Supplier practice varies ([CfI](https://www.ofgem.gov.uk/sites/default/files/2023-04/Price%20cap%20-%20Call%20for%20Input%20on%20the%20allowance%20for%20debt-related%20costs1681735393691.pdf)) | A |
| 20 | Debt sale price, fresh final debt (3–9 months) | 8–15p in the £ | Buyer multiple ~1.5–2× ([L.E.K.](https://www.lek.com/sites/default/files/insights/pdf-attachments/1801_UK_Debt_Purchase_Market_Debt_Buying_Industry_Consulting_LEK_Executive_Inisghts.pdf)); 75% settlement discounts ([inkl](https://www.inkl.com/news/law-firm-for-debt-company-pursues-customers-for-e-on-bills-on-homes-they-weren-t-living-in)) | A [unverified] |
| 21 | Debt sale price, aged final debt (12+ months, worked by DCAs) | 3–8p in the £ | as above | A [unverified] |
| 22 | Recovery curve after write-off, DCA route | 5–12p gross over 36 months (≈50% in year 1, 30% in year 2, 20% in year 3), less 15–30% commission | No GB data | A [unverified] |
| 23 | Hard stop on recovery | 72 months (E&W), 60 months (Scotland) | Limitation Act s.5 ([legislation.gov.uk](https://www.legislation.gov.uk/ukpga/1980/58/section/5)) | P (E&W); Scotland [unverified] |
| 24 | Collection cost | 3p per £1 of debt per year | [DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf) | P |
| 25 | Switch-blocking, credit meter | Block if any debt is 28 days old or more; customer has 30 working days to pay | SLC 14.4/14.9 ([CPAG](https://askcpag.org.uk/?id=-242650)) | S |
| 26 | Debt assignment, PPM switch | Debt of £10–£500 per fuel moves to the new supplier (loss to the old supplier = 0); above £500, block | SLC 14.6 ([CPAG](https://askcpag.org.uk/?id=-242650); [CA](https://citizensadvice.org.uk/consumer/energy/energy-supply/get-a-better-energy-deal/switching-energy-supplier-if-youre-in-debt)) | S |
| 27 | Payment-method bad debt allowance | DD £25 / SC £121 / PPM £10 a year excluding adjustments; DD £56 / SC £152 / PPM £19 including | [Appendix 2](https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf) | P |
| 28 | Relative LGD multiplier by payment method (live) | DD 0.6×, SC 1.5×, PPM 0.5× of the blended rate | Allowance ratios; SC under-recovered, DD over-recovered ([Ofgem Mar 2026](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) | A anchored on P |
| 29 | Bad debt charge, % of revenue | 2.3–3.0% (2022–25); 1.0–1.5% normal years | Octopus, SPERL (P); OVO (S); normal-year figure [unverified] | P / S / A |
| 30 | Bad debt cost per dual-fuel customer | ~£54 a year (2022–25 weighted average) | £176 over 39 months ([Ofgem Mar 2026](https://www.ofgem.gov.uk/sites/default/files/2026-03/Energy-price-cap-review-of-historical-debt-related-costs.pdf)) | P (derived) |
| 31 | Vulnerability: means-tested benefit customers with crisis debt | Live LGD ~75%; eligible for DRS write-off with reimbursement ~20–38% of face from 2027; final accounts excluded | [DRS working paper](https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf); [IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf) | P |
| 32 | Vulnerability: negative-budget customers | Plan failure ×1.5–2 the base rate; LGD +15 percentage points | 45% vs 24% negative budgets ([StepChange](https://stepchange.org/Portals/0/23/Reports/StepChange-Response-To-Ofgem-Affordability-And-Debt-Call-For-Input-May-2024.pdf)) | A anchored on P |
| 33 | Repayment-plan break rate | 35–50% within 12 months | No published figure | A [unverified] |
| 34 | Arrears off a plan versus on a plan | Off-plan stock ≈3× on-plan; average £1,872 vs £842 (electricity) | [Ofgem indicators](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) | P |
| 35 | Working-capital cost of carrying debt | 12.2% a year (1.02% a month) | [DRS IA](https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf) | P |

**Suggested change to the rule (A):** at departure, crystallise the unpaid balance. Apply row 17's LGD with the row 18 timing. Optionally sell at month 12 for row 21's price. Cap recoveries at row 23. Route PPM switchers with £500 or less per fuel through row 26, so the losing supplier has zero loss. Credit-meter switchers cannot carry debt older than 28 days out (row 25).

---

## 7. Gaps

1. **Centrica (British Gas) ECL ageing table and coverage:** not retrieved. The centrica.com and filings-mirror URLs were blocked or truncated. This is the single most valuable missing primary source for rows 1–13.
2. **Loss rates split by live and final accounts:** confirmed as a provision-matrix dimension (SPERL), but no supplier publishes the numbers. Ofgem holds the data from its DRC RFI and has not published it.
3. **SPERL ageing table and allowance movement (write-offs utilised):** not in the portion read, and the text was truncated at 127k characters.
4. **Utility debt-sale prices:** no GB primary or trade source found. Rows 20–21 are assumptions. Credit Services Association material, debt-buyer bond prospectuses (Lowell, Cabot) or a supplier tender would close this.
5. **Recovery curve after write-off and DCA commission rates for energy debt:** none found.
6. **Repayment-plan break rates:** none published by Ofgem, Citizens Advice or StepChange in the documents read.
7. **PPM recovery rates through the meter** and the current Fuel Direct £ rate: not confirmed.
8. **Final bill to write-off timing:** supplier-specific and unpublished.
9. **DRS live status and funding route:** the impact assessment says network charges (£3.23–£5.13 per household), while the press release refers to the existing £52 debt allowance. Go-live is still unconfirmed in November 2026 (the status comes from a secondary source).
10. **Final outcome of Ofgem's 2022–25 DRC true-up** (minded-to "no adjustment," decision due August 2026): not checked.
11. **OVO receivables and ECL coverage:** only the impairment charge is available, via a secondary source. Companies House filings were not read.
12. **Scottish prescription period (5 years)** and the per-fuel application of the DAP £500 threshold: not verified against primary legal text.
13. **Pre-2020 "normal year" bad-debt % of revenue:** not sourced. A CMA 2016 energy market investigation appendix would likely have it.