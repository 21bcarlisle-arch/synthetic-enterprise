**Severity:** RECORDED · **Lane:** E_finance_treasury · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Unbilled energy: estimates, held bills, catch-up and back-billing, unbilled revenue, and the pain points customers meet (2026-10-30)

**Type:** EVIDENCE, through the advisor channel, for `DIRECTOR_STEER_PAIN_POINTS_DRIVE_THE_LOOP_KNOWLEDGE_THEN_SIM_REACTION_THEN_SUPPLIER_TESTS_2026-10-30.md`. The director's words, from chat on Fri 30 Oct, 07:30 GMT: "Create knowledge in this area and in unbilled. What do different people do. What are the pros and cons. What do customers experience. What pain points should we measure. Is the SIM making customers react and behave to pain points?"

Written by an advisor research pass (web-sourced). Items tagged [unverified] are calibration assumptions, not evidence. Verify them with your own network access as you draft the Knowledge pages, as the 25 Oct verification steer asks.

**Correction to note:** the unbilled pack finds that SLC 21B is an *annual* reasonable-steps read duty. The two-yearly duty was a meter *inspection* duty (SLC 12.14–12.16), repealed in 2016. Check this against what the invariant library holds as "the read duty".

---

# Evidence pack: unbilled energy, estimated billing, catch-up bills and back-billing in GB domestic supply

*Compiled 30 October 2026. Every factual claim has its source URL beside it. **[unverified]** marks anything I could not confirm from a primary or reputable source in this session. **[analysis]** marks my own reasoning, which no source states.*

---

## 0. Headline numbers for calibrating the simulation

| Metric | Value | Source |
|---|---|---|
| Bills based on an actual read at first issue (7 largest suppliers, 2024) | 81%, rising to 89% after reconciliation | https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf |
| Bills issued at least 1 month late (2024) | about 11m bills (3%), of which 3.5m were 3–12 months late | same |
| Back-billing write-offs under SLC 21BA (2024) | over £172m across almost 1m customers, just under £200 each | same |
| Time to resolve back-billing cases | about 2 to 10 months on average, depending on supplier | same |
| Share of supplier complaints that are about billing and meter reading | about 30% | same |
| Share of Energy Ombudsman cases that are about billing and meter reading | about 55% | same |
| Energy Ombudsman cases accepted | 92,938 in 2024; 80,256 in 2025 | https://www.energyombudsman.org/news/energy-ombudsman-reports-24-drop-in-complaints ; https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025 |
| Back-billing disputes at the Ombudsman | 3,218 in 2024; 3,216 in 2025 | same two URLs |
| Average back bill seen by Citizens Advice | £2,525 (2023–24), up from £1,694 (2021–22) | https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-helps-with-an-energy-billing-issue-every-two-minutes |
| Median domestic back bill at the time of the 2018 ban | £1,160, with a median length of 24 months | https://ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months |
| Smart meters not working in smart mode | about 8.3% (September 2025) | https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf |
| Domestic debt and arrears | £4.48bn, 3.6m customers (Q3 2025) | same |

---

## Part A: Mechanics and standard practice

### A1. Why energy goes unbilled

**Estimates that drift from real use.** Ofgem names this as a main cause: suppliers estimate "until an actual meter reading shows higher consumption than expected, then [send] a 'catch-up' bill" (https://ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months). Its 2017 statutory consultation also lists estimated bills as a cause of back bills (para 2.48) (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf). OVO's 2020 settlement with Ofgem (£8.9m) included underestimating consumption over one winter and failures in its "estimation processes" (https://finance.yahoo.com/news/ovo-energy-fined-9m-overcharging-115600956.html).

**Missing reads.** In H1 2017, just over 7% of domestic consumers went more than a year without an accurate bill (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf). Case studies in that consultation include readings that suppliers received but did not use, and opening readings that were never loaded (same URL). In 2024, 19% of customers who contacted their supplier did so to give a meter reading (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf).

**Smart meters in "dumb" mode.**
- About 8% of smart meters (8.3% in the summary) were not working in smart mode in September 2025. Over 900,000 have been restored since July 2024, and Ofgem has taken compliance action against nine suppliers (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf).
- Citizens Advice found that 20% of smart meter households, about 2.86m homes, still have to submit readings by hand (https://uk.news.yahoo.com/smartmeter-british-gas-edf-ovo-070112421.html).
- Of people who came to Citizens Advice with an estimated or inaccurate bill, 49% had a smart meter (https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-helps-with-an-energy-billing-issue-every-two-minutes).
- In one Which? case, a faulty E.ON smart meter stopped recording gas. The customer was first shown a bill for over £7,000, later reduced to £700 (https://www.which.co.uk/news/article/energy-bills-why-you-should-know-about-the-back-billing-rules-aVPOM5J7FmXu).
- Installing a smart meter can itself reveal consumption that was never billed (para 2.6) (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf).

**Meter exchange gaps.** The Energy UK code of practice told suppliers to apply back-billing principles automatically "during routine meter replacements, smart meter rollouts, billing system changes, and when customers move between billing systems". That wording implies these events are known sources of risk (https://britishgas.co.uk/aem6/content/dam/britishgas/downloads/code-of-practice/back-billing-for-domestic-customers.pdf). I found no GB figure for how many back bills come from lost removal or install reads at exchange **[unverified]**.

**Held bills, exception bills and system migrations.**
- Ofgem says late billing is "concentrated among a smaller group of suppliers and is mainly caused by system migrations or operational issues" (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
- **npower:** at peak, 859k accounts were billed late after its SAP migration (2011–13) (https://www.ofgem.gov.uk/sites/default/files/docs/2016/01/160125_npower_sap_final_penalty_notice.pdf).
- **British Gas (Which? case):** a software issue left a customer unbilled for nearly two years, followed by a bill of £8,249.17 (https://www.which.co.uk/news/article/energy-bills-why-you-should-know-about-the-back-billing-rules-aVPOM5J7FmXu).

**Crossed meters and wrong MPANs.** Ofgem's 2020 open letter lists "errors caused by incorrect metering or smart meter arrangements" as a case where suppliers wrongly refused the back-billing protection (https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/open_letter_on_expectations_for_energy_suppliers_undertaking_charge_recovery_action_0.pdf). I found no GB figure for how often crossed meters occur **[unverified]**.

**Wrong tariff, wrong Direct Debit, and prepayment debt not applied.** All three are named causes:
- wrong tariff loaded and prepayment debt not applied (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf);
- Direct Debit set too low, and a prepayment meter's tariff or balance not updated (https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/open_letter_on_expectations_for_energy_suppliers_undertaking_charge_recovery_action_0.pdf).

**Unregistered and deemed occupiers.** SLC 21BA covers deemed contracts as well as domestic supply contracts ("Relevant Contract means any Domestic Supply Contract and Deemed Contract") (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_modification_notice_electricityfinal5march2018_-_website.pdf). In gas, consumption at unregistered supply points is a named source of Unidentified Gas (https://www.xoserve.com/media/s4lmsm5u/uig-executive-summary.pdf). The old voluntary code excluded customers who "used energy without contacting the supplier to arrange payment" (https://britishgas.co.uk/aem6/content/dam/britishgas/downloads/code-of-practice/back-billing-for-domestic-customers.pdf). Whether a silent occupier counts as "manifestly unreasonable" under the licence is not settled in anything I could find **[unverified]**.

**Late final bills on loss or change of tenancy.** These are held bills by another name. Recent cases:
- **Octopus:** failed to send prepayment final bills within six weeks to more than 34,000 customers between 2014 and October 2023, and paid about £1.5m (https://www.gbnews.com/money/energy-customers-compensation-octopus).
- **E.ON Next:** about 250,000 prepayment customers did not get final bills between February 2021 and September 2023 (https://news.eonenergy.com/news/e-on-next-takes-responsibility-for-21-to-23-billing-error-impacting-a-limited-number-of-customers-direct-action-taken-to-refund-and-compensate-those-involved). The redress was £14.5m, averaging £144 per customer, with about 150,000 debts written off (https://shropshirestar.com/uk-news/2024/11/20/eon-next-pays-out-145m-for-unacceptable-pre-payment-meter-billing-failures).
- **ScottishPower:** over 300,000 customers received late final bills during 2013–15 (https://www.ofgem.gov.uk/press-release/scottishpower-pay-ps18m-customer-service-failings).

### A2. How suppliers estimate

**Customer-level billing estimates.** Centrica describes its method: unread revenue is estimated "through the billing systems, using historical consumption patterns, on a customer-by-customer basis". It also takes account of weather, load forecasts, and the gap between actual reads and system estimates (https://centrica.com/media/vakdtnhh/annual-report-24_financial-statements.pdf).

**Electricity settlement (EAC/AA).** I could not fetch Elexon's EAC glossary page in this session. The following description is therefore **[unverified]**:
- each non-half-hourly MPAN carries an Estimated Annual Consumption (EAC);
- the EAC is spread across settlement periods using standard profile coefficients;
- each new actual read produces an Annualised Advance that replaces the estimate for the read period and updates the EAC.

Elexon's performance target is for suppliers to have 97% of energy settled on actual data by the RF run (https://www.elexon.co.uk/bsc/glossary/final-reconciliation-volume-allocation-run/).

**Gas (AQ and NDM).** Non-daily-metered sites are allocated gas using Annual Quantities (AQs) and NDM demand models. Inaccurate AQs and NDM estimation errors are named drivers of Unidentified Gas (https://www.xoserve.com/media/s4lmsm5u/uig-executive-summary.pdf). From 1 October 2025, a Seasonal Normal reset produced "a step change in NDM AQ (c.4 to 5% reduction)" (https://umbraco.xoserve.com/media/c2cne4vj/uig-gas-year-25_26-update.pdf). After a warm March, over-allocation from NDM modelling error caused a spike of negative UIG in April 2025 (same URL).

**[analysis]** A simulation should model three layers of "truth" that disagree for months:
1. the supplier's billing estimate, built from the customer's read history and a profile;
2. the industry settlement estimate (EAC or AQ);
3. actual consumption.

The catch-up bill is the moment when layer 1 is forced to meet layer 3.

### A3. Read duties: a correction to the brief

The brief mentions an "SLC 21B read every 2 years". The primary sources show something different:

- **SLC 21B: annual read.** "Suppliers must take all reasonable steps to obtain meter readings at least annually." They must also make a bill or statement of account available at least twice a year, or quarterly on request (https://www.ofgem.gov.uk/sites/default/files/docs/2019/02/licence_guide_metering_billing_and_payments_1.pdf). SLC 21B.5 contains the twice-yearly bill duty. SLC 21B.5A requires suppliers to offer monthly consumption-based billing information where a meter can be read remotely (https://www.ofgem.gov.uk/system/files/docs/2020/12/annex_3_-_keeling_schedule_electricity_supply_0.pdf).
- **The two-year rule was an inspection duty, and it has been repealed.** SLC 12.14–12.16 said "the licensee must take all reasonable steps to ensure that it inspects, at least once every two years, any Non-Half-Hourly Meter". It was repealed from 1 April 2016 (https://www.ofgem.gov.uk/sites/default/files/docs/2016/02/notice_of_licence_modifications_to_the_standard_conditions_of_the_electricity_supply_licences.pdf ; https://www.ofgem.gov.uk/publications/decision-reforming-suppliers-meter-inspection-obligations).
- **Read-visit practice.** Suppliers differ in when they send meter readers after a long gap without a reading. Some are trialling booked appointments instead of unannounced visits (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
- **Priority Services Register read service.** About 9m customers (about 25%) are on the PSR, and about 1m use its free meter-read service. Some suppliers enrol customers automatically, while others ask them. Some register customers with working smart meters as a backup in case the meter fails. Ofgem is working with several suppliers on visit success rates (same URL).

### A4. The back-billing cap

**History**

| Date | Event | Source |
|---|---|---|
| 2005 | Energywatch submits a super-complaint on back-billing | https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf (para 1.6) |
| 2007 | Ofgem sets out a back-billing principle. Industry adopts a voluntary 12-month limit for domestic customers, applying only where the supplier is at fault | same |
| 2012 | Voluntary microbusiness limits: 3 years for electricity, 4 years for gas | same (para 1.7) |
| April 2017 | Ofgem open letter | https://ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months |
| November 2017 | Statutory consultation | same |
| 5 March 2018 | Decision published | same |
| 1 May 2018 | SLC 21BA in force for domestic customers | https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_modification_notice_electricityfinal5march2018_-_website.pdf |
| 1 November 2018 | SLC 21BA in force for microbusinesses | same |
| 2019 | Energy UK closes the voluntary Billing Code | https://www.energy-uk.org.uk/publications/energy-uk-explains-back-billing/ |

**Why the voluntary code was replaced.** Only the six largest suppliers had signed it, out of more than 100 suppliers. Citizens Advice and the Ombudsman reported that all six still issued back bills older than 12 months (paras 1.9, 2.5) (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf). Back-billing made up about 15% of Citizens Advice domestic cases and 12% of Ombudsman cases in 2016 (para 2.1) (same URL).

**What SLC 21BA says.**
- A supplier may only bill or recover charges, including through a prepayment meter, for "units of electricity which could reasonably be considered to have been consumed within the 12 months preceding the date" of the charge recovery action, plus standing charges for the same 12 months (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_modification_notice_electricityfinal5march2018_-_website.pdf).
- Exceptions:
  - (a) charge recovery action taken before the condition started;
  - (b) continued collection of a compliant earlier charge;
  - (c) where the supplier could not bill correctly "due to obstructive or manifestly unreasonable behaviour of the Domestic Customer";
  - (d) other circumstances the Authority specifies after consultation.
- Contract terms that conflict with the condition cannot be enforced (21BA.5).

**When the customer exception applies, and when it does not.**
- **It applies to:** energy theft, failing to keep one's own meter in working order, and preventing physical access to the meter (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf).
- **It does not apply to:**
  - not supplying a meter reading (same URL);
  - failing to notice estimated billing, or not responding to requests for meter readings (https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/open_letter_on_expectations_for_energy_suppliers_undertaking_charge_recovery_action_0.pdf).
- **The licence is stricter than the old code.** The voluntary code let suppliers exclude customers who "didn't cooperate with meter readings or queries, such as refusing access or not responding to requests" (https://britishgas.co.uk/aem6/content/dam/britishgas/downloads/code-of-practice/back-billing-for-domestic-customers.pdf). Under the licence, not responding is no longer enough.
- **Record keeping.** Suppliers must keep evidence when they rely on the exception (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf). Ofgem found "weaknesses in how many suppliers record their use of exceptions" (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
- **Ofgem's consumer page uses broader wording.** It lists "ignored payment requests" as an example of acting unreasonably (https://www.ofgem.gov.uk/information-consumers/energy-advice-households/what-do-if-you-get-back-bill). That is looser than the licence text, which is worth noting in the simulation's rules.

**Scope.** The cap covers all payment methods, meter modes and meter arrangements, including prepayment. Suppliers had wrongly assumed prepayment customers were excluded, and had relied on customers to spot from monthly statements that a Direct Debit was too low (https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/open_letter_on_expectations_for_energy_suppliers_undertaking_charge_recovery_action_0.pdf).

**The three-condition test as consumers are told it.** Customers do not pay for energy used more than 12 months ago where they:
- had no accurate bill for it;
- were not told the amount through a statement of account; and
- had a Direct Debit set too low to cover it.

(https://www.ofgem.gov.uk/information-consumers/energy-advice-households/what-do-if-you-get-back-bill ; https://www.energy-uk.org.uk/publications/energy-uk-explains-back-billing/)

**Possible tightening.**
- Citizens Advice has called for a 6-month limit for smart meter customers since 2017, and suggested it could apply to all meters (https://www.citizensadvice.org.uk/wales/policy/publications/response-to-ofgems-open-letter-to-launch-a-project-to-protect-consumers-from-back-billing/). It repeated the call in 2026 (https://www.citizensadvice.org.uk/policy/publications/the-state-of-smart-consumer-experiences-of-smart-meters/).
- The Energy Security and Net Zero Committee is considering a 6-month window and automatic compensation (https://www.which.co.uk/news/article/energy-bills-why-you-should-know-about-the-back-billing-rules-aVPOM5J7FmXu).
- Ofgem plans to review SLC 21BA. It says a shorter period could push suppliers towards accurate billing (https://www.ofgem.gov.uk/sites/default/files/2024-12/Improving_debt_standards_in_the_domestic_retail_market(2)%20(1).pdf). The 2026 billing assessment says its findings will feed a "billing outcomes framework" and may lead to more guidance on back-billing (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).

**[analysis]** The simulation should treat the back-billing window as a parameter (12 or 6 months, and smart or all meters) so that a policy shock can be tested.

### A5. Catch-up bills and Ofgem's accurate-billing work

**Duties around catch-up bills.**
- Suppliers must take all reasonable steps to reflect accurate readings in bills, and must explain how a bill was worked out if asked (https://www.ofgem.gov.uk/sites/default/files/docs/2019/02/licence_guide_metering_billing_and_payments_1.pdf).
- Suppliers must explain how a fixed Direct Debit was set (same URL), and set Direct Debits on the best current information (SLC 27) (https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/open_letter_on_expectations_for_energy_suppliers_undertaking_charge_recovery_action_0.pdf).
- Even when the rules are applied correctly, a catch-up bill can still cover up to 12 months (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).

**Direct Debit review (July 2022).**
- Standard variable tariff Direct Debits rose by 62% on average in the two months before the April 2022 cap rise, and 8% of customers saw rises above 100%.
- Ofgem found no evidence of widespread inflation, but 12 suppliers had weak processes and were told to submit action plans.
- Source: https://www.ofgem.gov.uk/decision/ofgem-seeks-improvements-12-suppliers-relation-customer-direct-debit-setting

**Domestic billing performance assessment (July 2026).** This covered seven suppliers (British Gas, EDF, E.ON Next, Octopus, OVO, Scottish Power and Utility Warehouse) using 2024 data. Findings:
- 81% of bills were on actual reads at first issue and 89% after reconciliation;
- 97% of customers got a bill within 30 days of the due date;
- 99% got the required number of bills;
- more than 300m bills were issued in the year;
- the good practices named were proactive monitoring, system alerts flagging unbilled accounts, "health flags", proactive engagement, controlled use of AI and strong governance.

Source: https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf. Ofgem's January 2026 State of the Market gives slightly different figures from the same exercise: about 82% accurate, about 1.2% of bills at least 3 months late, and about 95% issued within 10 days (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf).

### A6. How suppliers handle exception queues and held bills: named examples, pros and cons

**1. Big-bang migration, then manual working of the backlog (npower, 2011–13).**
- What happened: 859k accounts billed late at peak; over 510k bills sent late between September 2013 and December 2014, about 51k of them more than 6 months old; complaints up from 36k a month (May 2011) to 133k a month; back bills issued in breach of the code, with £5.4m repaid.
- What Ofgem said would have helped: a fallback billing method, effective manual bill review, and putting hard-to-resolve accounts first.
- Outcome: £26m redress, with a target to cut invoices more than 6 months old from about 46k to 15k.
- Sources: https://www.ofgem.gov.uk/sites/default/files/docs/2016/01/160125_npower_sap_final_penalty_notice.pdf ; https://ofgem.gov.uk/publications/npower-pay-ps26m-failing-treat-customers-fairly
- **Pros:** one platform at the end. **Cons:** the queue grows faster than staff can clear it, complaints are logged as resolved when they are not, and bill shock plus wrongful back bills follow.

**2. IT rollout without contingency plans (ScottishPower, 2013–15).**
- What happened: over 1m complaints and over 300,000 late final bills; a 12-day halt to proactive selling in March 2015; £18m paid.
- After intervention: late bills fell 75%.
- Source: https://www.ofgem.gov.uk/press-release/scottishpower-pay-ps18m-customer-service-failings
- **Pros:** recovery was possible once the backlog was the focus. **Cons:** a regulator-imposed sales stop is a direct revenue lever on the supplier.

**3. Surge staffing to clear queues (British Gas Business, 2014 migration).**
- What happened: tens of thousands of late or inaccurate bills; up to 350 specialist agents hired; £9.5m redress.
- Source: https://www.ofgem.gov.uk/publications/british-gas-business-pay-ps95-million-customer-service-failings
- **Pros:** fast relief. **Cons:** expensive, and it treats the symptom rather than the cause.

**4. Abandoning the platform change (SSE, FY2016/17).**
- What happened: SSE took an impairment on a customer billing system upgrade it did not proceed with, and reported retail operating profit fell 29% to £309.6m.
- Source: https://theenergyst.com/aborted-billing-system-upgrade-hits-sse-retail-profits/
- **Pros:** avoids migration harm. **Cons:** sunk cost, and the old system's limits on exceptions remain.

**5. Silent held-bill classes that nobody monitors (Octopus prepayment final bills 2014–2023; E.ON Next prepayment final bills 2021–2023).**
- What happened: a whole class of account was never billed for years.
- Sources: https://www.gbnews.com/money/energy-customers-compensation-octopus ; https://shropshirestar.com/uk-news/2024/11/20/eon-next-pays-out-145m-for-unacceptable-pre-payment-meter-billing-failures
- **Cons:** each record is cheap to hold, but the harm piles up into a mass redress event.

**6. Proactive monitoring, unbilled-account alerts and health flags.** Ofgem calls this good practice but does not name which suppliers do it (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
- **Pros:** catches exceptions before they age past 12 months. **Cons:** needs investment in data and governance up front.

**7. Automatic 12-month write-off on known risk events** (meter exchange, smart install, system migration), as the old Energy UK code required (https://britishgas.co.uk/aem6/content/dam/britishgas/downloads/code-of-practice/back-billing-for-domestic-customers.pdf).
- **Pros:** consistent outcomes, so fewer complaints and Ombudsman cases. **Cons:** a guaranteed loss of revenue on older consumption.

**Platforms.** I found no reliable public source on which billing platform each supplier uses for exception handling, such as Octopus and E.ON Next on Kraken **[unverified]**.

---

## Part B: Unbilled revenue from the supplier's side

### B1. Accounting

- **IFRS 15** recognises revenue as energy is delivered. Consumption that has been delivered but not yet billed is booked as accrued (unbilled) income. Variable-consideration estimates are constrained to amounts that are highly probable not to reverse. This is general standard knowledge: https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/ **[unverified: page not fetchable this session]**.
- **Centrica (FY2024).**
  - Unread revenue for UK downstream customers (British Gas Energy and Centrica Business Solutions) was £2,732m at 31 December 2024 (2023: £2,992m).
  - It is estimated customer by customer from historical consumption, weather and load forecasts, and is checked against actual reads until the accounts are finalised.
  - Bill cancellation and re-bill rates are taken into account, and the estimate is limited to what Centrica expects to be entitled to.
  - A 2% change in assumptions moves revenue and profit by £55m.
  - Source: https://centrica.com/media/vakdtnhh/annual-report-24_financial-statements.pdf
- **Centrica credit provisions.** Total credit provision on receivables was £1,532m (2023: £1,309m). British Gas Energy recognised £1,309m of credit losses on billed receivables, of which £891m relates to UK residential customers. The auditor tested the "methodology to generate unbilled revenue" (same URL).
- **Octopus, OVO, E.ON UK and SSE retail (historical).** I could not get accrued-income figures in this session:
  - OVO's FY24 annual report URL redirected to its press page (https://company.ovo.com/wp-content/uploads/2025/09/OVO-ANNUAL-REPORT-FY24-FINAL-SEPT-2025.pdf);
  - Octopus reported a £255m loss for the year to April 2025, which it linked partly to lower gas demand in a record-warm spring (https://www.bloomberg.com/news/articles/2025-12-30/octopus-energy-reports-annual-loss-after-mild-spring-cuts-demand). That illustrates how sensitive estimated volumes and revenue are to weather.
  - All accrued-income amounts for these four companies are **[unverified]**.
- **[analysis]** Simulation calibration: Centrica's unread revenue is the same order of size as its annual UK residential credit losses. The supplier's balance sheet therefore carries a large estimated asset that reads and settlement either confirm or erode.

### B2. Settlement truth arriving months later

**Electricity (BSC).**

| Run | Timing after the settlement date |
|---|---|
| Interim Information (II) | about 1 week (information only) |
| Initial Settlement (SF) | about 1 month |
| R1 | 2 months |
| R2 | 5 months, as Elexon states |
| R3 | 7 months |
| RF | 14 months |
| Dispute Final (DF) | 28 months |

Source: https://www.elexon.co.uk/bsc/glossary/2nd-reconciliation/

Under the MHHS migration, RF moves to 7 months from 1 April 2027 (decision point October 2026), then to 4 months from 2 July 2027 (M16). SF moves from 15 to 7 working days, subject to a decision point in April 2027 (https://www.elexon.co.uk/bsc/article/new-settlement-timetable-reducing-from-14-months-to-seven-months-from-april-2027/). Elexon's target is 97% of energy on actual data by RF (https://www.elexon.co.uk/bsc/glossary/final-reconciliation-volume-allocation-run/).

**Gas.**
- UIG is worked out daily for each Local Distribution Zone as the balancing figure.
- It is shared between shippers using weighting factors set by the AUGE.
- When reads update meter point reconciliations, UIG moves in the opposite direction through Unidentified Gas Reconciliation on the Amendment Invoice.
- UIG can change with every read reconciliation.
- Source: https://www.xoserve.com/media/s4lmsm5u/uig-executive-summary.pdf
- Modification 0398 proposed narrowing the retrospective reconciliation window from 4–5 years to a 3–4 year "line in the sand" (https://www.gasgovernance.co.uk/sites/default/files/ggf/Final%20Modification%20Report%200398%20v2.1_0.pdf). Whether and when it was implemented is **[unverified]**.

**[analysis] Why this matters.** A supplier pays wholesale and network costs on settled volumes, which are corrected through reconciliation as reads arrive. It can only bill the customer for 12 months under SLC 21BA. When consumption goes unbilled for longer than 12 months, the supplier still pays the industry for the energy but cannot recover it from the customer. MHHS shortens the industry correction cycle to 4 months, but does not change the customer-side 12-month cap. A supplier whose own billing lags will therefore see the cost certainty earlier than the revenue.

### B3. The cost of getting it wrong

- **Write-offs.** Over £172m in 2024 across almost 1m customers (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf). When the rule was made, Ofgem expected annual write-offs of only £0.8m–£2.3m (para 2.48) (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf). One supplier estimated sector costs of about £60m, mainly extra read staff and write-offs (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf).
- **Estimation risk.** A 2% change in assumptions is worth £55m at Centrica (https://centrica.com/media/vakdtnhh/annual-report-24_financial-statements.pdf).
- **Enforcement and redress.**

| Supplier | Year | Amount | Issue | Source |
|---|---|---|---|---|
| npower | 2015 | £26m redress (plus a £1-per-company nominal penalty) | Late and inaccurate bills, wrongful back bills | https://ofgem.gov.uk/publications/npower-pay-ps26m-failing-treat-customers-fairly |
| ScottishPower | 2016 | £18m | IT rollout, late final bills | https://www.ofgem.gov.uk/press-release/scottishpower-pay-ps18m-customer-service-failings |
| British Gas Business | 2017 | £9.5m | Billing migration | https://www.ofgem.gov.uk/publications/british-gas-business-pay-ps95-million-customer-service-failings |
| OVO | 2020 | £8.9m | Estimation and inaccurate annual statements to over 500,000 customers | https://finance.yahoo.com/news/ovo-energy-fined-9m-overcharging-115600956.html |
| E.ON Next | 2024 | £14.5m | Prepayment final bills | https://shropshirestar.com/uk-news/2024/11/20/eon-next-pays-out-145m-for-unacceptable-pre-payment-meter-billing-failures |
| Octopus | 2025 | about £1.5m | Prepayment final bills | https://www.gbnews.com/money/energy-customers-compensation-octopus |
| United Gas & Power | 2023 | £1.7m–£2m, as reported | Deliberate overcharging of business customers | https://www.ofgem.gov.uk/publications/ofgem-penalises-united-gas-power-ugp-following-deliberate-and-significant-overcharging-customers |

I found no named Ofgem penalty under SLC 21BA alone. Ofgem's 2020 letter warned that it would investigate and seek redress (https://www.ofgem.gov.uk/sites/default/files/docs/2020/12/open_letter_on_expectations_for_energy_suppliers_undertaking_charge_recovery_action_0.pdf).

- **Sales bans.** ScottishPower stopped proactive selling for 12 days (https://www.ofgem.gov.uk/press-release/scottishpower-pay-ps18m-customer-service-failings). npower faced a sales stop if it missed its targets by June 2016 (https://ofgem.gov.uk/publications/npower-pay-ps26m-failing-treat-customers-fairly).

---

## Part C: What customers experience

### C1. Catch-up shock, repeated estimates and bills people cannot understand

- **Unexpected high bills.** 27% had one in the last three months (July 2024), down from 33% in August–September 2023 (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf).
- **Bill accuracy.** 77% satisfied and 9% dissatisfied. Of those dissatisfied, 30% blamed wrong estimates (same URL).
- **Understanding bills.** 78% satisfied and 8% dissatisfied (same URL).
- **Size of catch-up problems at Citizens Advice.** 24% of billing cases involve a shock or catch-up bill. Over 52,000 people sought billing help in January–October 2024, 83% more than in 2020. 67% of them had a disability or long-term condition (https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-helps-with-an-energy-billing-issue-every-two-minutes).
- **How people feel.** "When they sent the bill for £2,500 my first reaction was just shock" (same URL). Ofgem: "Large catch-up bills can leave consumers struggling financially or even in debt to their supplier" (https://ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months).

### C2. Complaints data

- **Energy Ombudsman.**
  - 2024: billing was 58% of cases (53,607). Other categories were customer service 10,377, smart meters 10,164, standard meters 2,473, and payments and debt 2,420 (https://www.energyombudsman.org/news/energy-ombudsman-reports-24-drop-in-complaints).
  - 2025: billing was 56% of cases. Suppliers told consumers about the Ombudsman in only 48% of eligible cases (range 25–68%). Up to 75% of eligible consumers never use the service (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025).
  - Back-billing is about 3–5% of Ombudsman cases (https://www.which.co.uk/news/article/energy-bills-why-you-should-know-about-the-back-billing-rules-aVPOM5J7FmXu ; https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
  - Upheld rates for back-billing complaints: 79% in 2018 (1,903 resolved) and 83% in 2019 (2,539 resolved) (https://www.creditstrategy.co.uk/news/news/backbilling-complaints-to-energy-ombudsman-rise-a-third-despite-ban-6711).
  - The average Ombudsman award for upheld billing complaints was £106 (autumn 2019) (https://www.which.co.uk/news/article/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard-armgk3m2JJgN).
  - Consumers can escalate after 8 weeks, or earlier with a deadlock letter (https://www.which.co.uk/news/article/energy-bills-why-you-should-know-about-the-back-billing-rules-aVPOM5J7FmXu).
- **Ofgem complaint statistics.** The industry average was 0.9 complaints per 100 accounts in Q3 2025. "Billing and meter reading" is the largest category, at about 109 per 100k accounts (my best reading of a chart). Billing plus customer service make up about 60% of complaints (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf).
- **Citizens Advice star rating.**
  - Billing accuracy is 15% of the score. It is measured as the share of customers with a bill based on a reading in the last 6 months (smart) or 12 months (non-smart).
  - Smart meter operation is 10%.
  - Complaints to third parties are 35%, scored per 10,000 customers: 5 or fewer scores 5, more than 80 scores 0.5.
  - Call wait time is 18%.
  - Source: https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/
  - Suppliers must publish their star rating (https://www.ofgem.gov.uk/sites/default/files/2023-10/Consumer%20Standards%20-%20Decision1697539480940_0.pdf).
- **Complaints that are never made.** 42% of customers with a reason to complain did not. Nearly a third of those thought it would make no difference, and 17% did not know how (https://www.which.co.uk/news/article/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard-armgk3m2JJgN). In 2018, 27% of complainants had given up on their complaint (https://www.energyombudsman.org/news/how-good-are-energy-suppliers-at-handling-complaints).

### C3. Vulnerability, affordability and debt after catch-up bills

- **Debt link.** 34% of people who sought billing advice from Citizens Advice also needed help with energy debt (https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-helps-with-an-energy-billing-issue-every-two-minutes).
- **Resilience.** 32% of UK adults could not pay an unexpected £300 bill without cutting back on essentials (para 1.4) (https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf).
- **Ofgem's view.** Shock bills raise debt risk, and a working smart market "can remove the need for back-bills" (https://www.ofgem.gov.uk/sites/default/files/2024-12/Improving_debt_standards_in_the_domestic_retail_market(2)%20(1).pdf).
- **Repayment plans.**
  - In Q3 2024, 57% of accounts in debt or arrears had no repayment plan.
  - About 66,000 electricity repayment arrangements failed in that quarter, the most since records began in 2016.
  - Only 18% of customers falling behind said their supplier had contacted them first.
  - Source: same URL.
  - Average debt was £714 with a plan and £1,686 without one (July 2023) (https://www.ofgem.gov.uk/sites/default/files/2023-10/Consumer%20Standards%20-%20Decision1697539480940_0.pdf).
- **SLC 27 ability-to-pay rules.**
  - Suppliers must take all reasonable steps to find out a customer's ability to pay and consider third-party information (27.8). They must give due consideration to ability to pay (27.8A(c)), set plans on it (27.8A(d)), offer repayment holidays where appropriate (27.8A(d)(iv)), and point customers to debt advice (27.8A(b)(iv)) (https://www.ofgem.gov.uk/system/files/docs/2020/12/annex_3_-_keeling_schedule_electricity_supply_0.pdf ; https://www.ofgem.gov.uk/sites/default/files/2024-12/Improving_debt_standards_in_the_domestic_retail_market(2)%20(1).pdf).
  - Since 14 December 2023, suppliers must contact customers after two missed monthly payments or one missed quarterly payment, consider pausing repayments, and review a plan before restarting it (https://www.ofgem.gov.uk/sites/default/files/2023-10/Consumer%20Standards%20-%20Decision1697539480940_0.pdf).
  - Ofgem has proposed standardised assessments using the Standard Financial Statement or similar, and accepting offers from FCA-authorised debt advisers (https://www.ofgem.gov.uk/sites/default/files/2024-12/Improving_debt_standards_in_the_domestic_retail_market(2)%20(1).pdf).
- **Satisfaction by financial position.** 82% overall, 73% for financially vulnerable customers, 71% for highly financially vulnerable customers, and 67% for customers behind on bills (July–August 2025) (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf).

---

## Part D: Pain points and quantified customer reactions

- **Calls.** 32% contacted their supplier in a three-month period, and a further 4% tried but could not get through. Reasons: giving a meter reading 19%, querying a bill 19%, a smart meter question 16% (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf).
  - The share finding contact easy fell from 73% (Q4 2018) to 58% (Q4 2022) (https://www.ofgem.gov.uk/sites/default/files/2023-10/Consumer%20Standards%20-%20Decision1697539480940_0.pdf).
  - npower's billing failure produced over 2m complaints. Monthly complaints rose about 3.7 times, from 36k to 133k (https://www.ofgem.gov.uk/sites/default/files/docs/2016/01/160125_npower_sap_final_penalty_notice.pdf).
- **Complaints.** About 8% of contacts are complaints. Satisfaction with complaint handling is 47% satisfied against 44% dissatisfied (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf).
- **Escalation.** Back-billing cases are upheld about 80% of the time (https://www.creditstrategy.co.uk/news/news/backbilling-complaints-to-energy-ombudsman-rise-a-third-despite-ban-6711). Suppliers signpost the Ombudsman in only 48% of cases (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025).
- **Churn.** In 2016, 52% of complainants had switched or planned to switch supplier, up from 44% in 2014 (https://www.ofgem.gov.uk/press-release/ofgem-publishes-biennial-survey-how-suppliers-handle-complaints). Among switchers, 50% cited getting a cheaper tariff as the main reason (January–February 2025) (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf). I found no source giving a churn uplift caused specifically by back bills **[unverified]**.
- **Non-payment.** 10% fell behind or ran out of credit in three months, and 20% of standard credit customers fell behind (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf).
- **Direct Debit cancellation.** The old code advised customers not to cancel a Direct Debit during a dispute (https://britishgas.co.uk/aem6/content/dam/britishgas/downloads/code-of-practice/back-billing-for-domestic-customers.pdf). That suggests cancellation is a common reaction, but I found no GB figure for cancellations after catch-up bills **[unverified]**. MSE's self-selected survey of over 40,000 people found 30% of British Gas, Octopus and Shell customers said their Direct Debit had doubled in 2022 (https://debtcamel.co.uk/?p=25912).
- **Trust.** Ofgem does not publish a trust measure. Satisfaction is the closest proxy (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf). 15% of consumers said they were resigned to poor service in energy (https://tag-craft.files.svdcdn.com/production/assets/assets/CAM-Report-2018.pdf).

---

## Summary table: pain points

| Pain point | How the customer meets it | Measurable signal | Evidence of customer reaction (URL) | Suggested simulation behaviour |
|---|---|---|---|---|
| Repeated estimated bills | Bills marked "E" for months; read requests | Months since last actual read; share of bills estimated | 30% of those unhappy with bill accuracy blame estimates; 19% of contacts are to give a read (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf) | Each estimate raises P(call) and lowers trust; P(customer submits a read) falls with fatigue |
| Catch-up or shock bill | One large bill after an actual read | Catch-up size relative to monthly Direct Debit | 24% of Citizens Advice billing cases; average £2,525; 34% also get debt help (https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-helps-with-an-energy-billing-issue-every-two-minutes) | P(complaint) and P(arrears) rise steeply with the ratio; size is capped at 12 months under SLC 21BA |
| Back bill over 12 months, wrongly applied | Bill covering more than a year; supplier claims an exception | Days of usage beyond 12 months; exception flag | Back-billing cases upheld about 80% at the Ombudsman (https://www.creditstrategy.co.uk/news/news/backbilling-complaints-to-energy-ombudsman-rise-a-third-despite-ban-6711) | High P(escalation); supplier pays write-off plus redress; regulator risk counter |
| Non-communicating smart meter | "Smart" meter still needs manual reads | SMETS comms status; days in dumb mode | 49% of people with estimated-bill problems had a smart meter (https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-helps-with-an-energy-billing-issue-every-two-minutes); 8.3% of meters in dumb mode (https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf) | Extra trust penalty ("I was promised no estimates"); higher P(complaint) |
| Late or held bill (migration, exception queue) | No bill for months, then one arrives | Days since last bill; exception-queue age | npower complaints rose about 3.7 times (https://www.ofgem.gov.uk/sites/default/files/docs/2016/01/160125_npower_sap_final_penalty_notice.pdf); 3% of bills a month or more late (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf) | Silence at first, then a burst of complaints; churn if the bill exceeds 2× Direct Debit **[analysis]** |
| Direct Debit sharply increased | Payment amount jumps after a review or catch-up | % change in Direct Debit | 62% average rise; 8% saw rises over 100% (https://www.ofgem.gov.uk/decision/ofgem-seeks-improvements-12-suppliers-relation-customer-direct-debit-setting) | P(Direct Debit cancellation) and P(call) rise with the % change; cancelled Direct Debits move to standard credit with more arrears |
| Missing or late final bill | Leaves the supplier and never gets a closing bill or refund | Days from loss to final bill | E.ON Next: 250k customers, £144 average redress (https://shropshirestar.com/uk-news/2024/11/20/eon-next-pays-out-145m-for-unacceptable-pre-payment-meter-billing-failures) | Former customer's complaint escalates; reputational hit lowers acquisition |
| Bill hard to understand | Cannot work out what is being charged | Bill-query contact rate | 8% dissatisfied with understanding; 19% of contacts are bill queries (https://www.ofgem.gov.uk/sites/default/files/2024-11/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20%E2%80%93%20July%202024.pdf) | Each unclear bill raises P(call); a clear catch-up explanation lowers P(complaint) |
| Complaint not resolved or not signposted | Long complaint, no deadlock letter | Complaint age; 8-week breach | 44% dissatisfied with handling; 27% give up (https://www.energyombudsman.org/news/how-good-are-energy-suppliers-at-handling-complaints); 48% signposting (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) | Branch: escalate to Ombudsman, give up (trust falls), or switch |
| Catch-up debt and an unaffordable plan | Debt from the catch-up; plan does not fit income | Arrears; failed plans; plan instalment as a share of income | 57% with no plan; 66k failed plans in Q3 2024 (https://www.ofgem.gov.uk/sites/default/files/2024-12/Improving_debt_standards_in_the_domestic_retail_market(2)%20(1).pdf) | Vulnerable agents ration or default; an ability-to-pay check lowers P(plan failure) |
| Missed meter-read visit | Unannounced reader, nobody home | Read-visit success rate | Some suppliers are trialling booked appointments (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf) | P(read obtained) depends on the visit model and the household's daytime presence |

---

## Supplier levers to experiment with

1. **Read chasing**, by escalating SMS, then app, then email, then letter, triggered by months since the last actual read.
   *Metrics:* % of bills on actual reads; age of last read; estimate-related calls; catch-up size; write-offs.
2. **Booked read appointments instead of unannounced visits** (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
   *Metrics:* visit success rate; cost per read; share of accounts over 12 months without a read.
3. **PSR meter-read service, automatic or opt-in.** Includes registering smart customers as a backup.
   *Metrics:* reads for vulnerable customers; catch-ups among vulnerable customers; star-rating complaints.
4. **Fixing smart meters in dumb mode**, by remote reconfiguration, a visit, or replacement.
   *Metrics:* % in smart mode; star-rating smart score; estimate rate among smart customers; Ombudsman smart-meter cases.
5. **Unbilled-account alerts and health flags**, aged-exception dashboards and AI triage with human oversight (https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf).
   *Metrics:* % of bills 1 month or more late; exception-queue age distribution; accounts approaching 12 months unbilled; £ written off under SLC 21BA.
6. **Exception-queue working policy**: oldest first, highest value first, or nearest to 12 months first (because of the cap); with or without a fallback estimated bill (lesson from npower).
   *Metrics:* write-off £; complaint volume; days to clear; settlement-versus-billing mismatch.
7. **Automatic 12-month write-off on risk events** (meter exchange, smart install, migration) instead of case-by-case review.
   *Metrics:* write-off £; Ombudsman back-billing cases; upheld rate; time to resolve (benchmark 2 to 10 months).
8. **Proactive catch-up notices.** Warn before the bill, explain why it happened, and offer a plan.
   *Metrics:* P(complaint after catch-up); calls per catch-up; Direct Debit cancellations; satisfaction.
9. **Smoothing.** Spread the catch-up over 12 months or longer interest-free, set on ability to pay (SLC 27.8A).
   *Metrics:* arrears; plan failure rate; bad-debt charge; cash timing.
10. **Early-review Direct Debit messaging**: smaller, more frequent rises triggered by read drift, with an explanation.
    *Metrics:* % Direct Debit change distribution; Direct Debit cancellations; credit/debit balance spread; calls.
11. **Complaint signposting and early deadlock letters.**
    *Metrics:* complaints over 8 weeks; Ombudsman cases and costs; trust; churn among complainants (benchmark 52% switched or intending to switch).
12. **Control over the estimation model**: own read history plus weather-adjusted profile, compared with industry EAC/AQ.
    *Metrics:* forecast error at the read; accrued-income true-up (sensitivity benchmark: 2% = £55m at Centrica, https://centrica.com/media/vakdtnhh/annual-report-24_financial-statements.pdf); UIG and reconciliation exposure.
13. **Migration strategy**: big-bang or phased, with parallel run and fallback billing.
    *Metrics:* peak late-billed accounts (npower peaked at 859k); complaint multiple; regulator sales-stop risk; redress £.

---

### Notes for the simulation team

- **[analysis]** The brief's "SLC 21B read every 2 years" should be modelled as an annual reasonable-steps read duty (SLC 21B). The 2-year inspection duty was repealed in 2016.
- **[analysis]** Not found or **[unverified]**: accrued-income figures for Octopus, OVO, E.ON UK and SSE retail; how often crossed meters and lost exchange reads occur; rates of Direct Debit cancellation after a catch-up bill; churn caused specifically by back bills; any penalty under SLC 21BA alone; the implementation status of UNC Modification 0398.
## Done

2026-10-30, the worker. The knowledge this pack was for is written and published:
`docs/market_research/unbilled_energy_what_suppliers_do_and_what_customers_meet_2026-10-30.md` (topic
`unbilled-energy-and-revenue-assurance`, whose site entry now carries its headline figures). It adds
what the existing unbilled and back-billing pages lacked: named suppliers' handling of held bills and
exception queues with pros and cons, what customers meet, and eight pain points, each defined for one
population before it is measured (the pack's rows mixed a DD change and a bill as "bill shock").

- **Verified first-hand:** Ofgem's *Domestic billing performance assessment* (July 2026), text extracted
  from the PDF: 81% / 89% read-based, 11m (3%) late bills, over £172m written off for almost 1m
  customers, 2 to almost 10 months to resolve. One figure moved: back-billing is "around 5%" of
  Ombudsman referrals in the primary, against the pack's 3-5%.
- **The read-duty correction** was checked: `INV_READ_DUTY_ANNUAL` already holds an annual duty.
  Nothing to correct.
- **The SIM reaction** is not built here. It is `unbilled-energy-pain-points-react` in
  `docs/direction/priority_order.yaml`, drawn after the correctness exit test. The page names one lever
  the supplier can be graded on without any world reaction: the order it works its exception queue,
  graded on SLC 21BA write-offs.
