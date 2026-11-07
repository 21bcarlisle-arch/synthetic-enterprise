**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] What GB households do after a billing or supply pain point: contact, complaint, Ombudsman, switch, DD change, arrears, rationing, inaction (2026-11-07)

**Type:** EVIDENCE, through the advisor channel. The director's words, from chat on Sat 7 Nov, 16:00 GMT: "ok, so we have a lot of tokens to use? How can we do that? A big knowledge push? What else?" He then chose two passes: write-offs and debt, and customer reactions.

**Use: the pain-point audit.** The 30 Oct pain-point steer's audit found that the world reacts to one pain point in seven. This pack gives evidence-based reaction rates for eight pain points, with group multipliers, and a model with two layers. The first layer is internal state (grievance and strain) that moves on almost every pain point. The second is external action that fires mostly inside salient trigger windows, such as the end of a fix, a price-rise notice, a DD change or a deadlocked complaint. The anchors are revealed rates where they exist: 19% acted at the end of a fix (Ofgem trial); a 22.4%-versus-2.6% collective switch; about a 4× monthly net-loss spike at Centrica after its 2018 rise; 42% with a reason to complain did not. This is world-side knowledge for the world-reaction build, which is ranked first in your next-additions order. Build it after the correctness exit test.

This pack is from an advisor research pass, sourced from the web. Figures are graded P, S or A, with [unverified] marking anything not confirmed against a primary source. Apply the 30 Oct data standard: verify against primary sources and re-derive figures from the underlying data where it is published. No world parameter may rest on S or A alone.

---

# Evidence pack: what GB households do after a billing or supply pain point

**Purpose:** set evidence-based reaction probabilities for simulated households in the Poesys model.
**Grades:** **P** = primary (the regulator's or originator's own data or trial). **S** = secondary (press or third-party reporting of someone else's data). **A** = assumption (my derivation or calibration, with the anchor named).
**Note:** the core sources are the Ofgem CIM and ECSS waves, the Ofgem trials, the CMA appendix, the Ombudsman data, the FCA evaluation and the Ofcom evaluation. Some statements could not be pinned to a primary page; these carry the tag [unverified].

---

## 0. The core finding

The evidence shows the simulation's current behaviour (one pain point in seven gets any reaction) is broadly right for **visible, external actions**. It is too low for **invisible, internal actions** such as rationing, worrying and stated intent.

Across every source, the pattern is the same:

- **A large minority do nothing at all.**
  - 42% of customers with a reason to complain did not complain ([Which? 2020](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/)).
  - 46% of MSE respondents whose direct debit (DD) doubled did not challenge it ([MSE 2022](https://www.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey)).
  - 81% of customers reaching the end of a fix asked for no switch within six weeks ([Ofgem EFTC trial 2019](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)).
  - Up to 75% of consumers eligible for the Energy Ombudsman do not use it ([Energy Ombudsman 2025](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)).
- **External action is concentrated at salient moments.** These are the end of a fix, a price-rise announcement, a doubled DD, or a bad complaint outcome. Centrica's account losses accelerated sharply after its SVT rises in 2017 and 2018 ([Enerdata](https://www.enerdata.net/publications/daily-energy-news/centrica-has-lost-more-one-million-customers-2017-uk.html); [London Loves Business](https://londonlovesbusiness.com/centrica-profits-drop-loses-340000-uk-customer/)).
- **Internal action is common and often silent.**
  - 44% of households reduced energy use because they couldn't afford it in July 2022 ([Ofgem CIM Wave 2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)).
  - Only 9% contacted their energy supplier for help paying ([same source](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)).

**Modelling implication:** split each household's reaction into two layers.

1. An internal state that moves on almost every pain point: resentment, financial stress and rationing.
2. External actions that fire rarely and mostly at trigger events: contact, complaint, Ombudsman, switch, DD change and arrears.

---

## 1. Cross-cutting baselines

### 1.1 Inertia and switching baselines

| Metric | Value | Source | Grade |
|---|---|---|---|
| Never switched supplier (2014) | 56% | [CMA EMI Appendix 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| Never switched and never considered it, or thinks it isn't possible | 34% | [CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| Never switched tariff with own supplier | 72% | [CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| Unlikely to consider switching in the next 3 years | 42% | [CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| Switched supplier in past 12 months (Q4 2019, normal market) | 20% | [Ofgem Consumer Perceptions Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Ever switched (Q4 2019) | 58% | [same](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Switched to a new supplier (CIM W2, July 2022, crisis market); the recall period is not clear [unverified] | 11% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Switched tariff with the same supplier (CIM W2) | 18% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Compared tariffs but did not switch (CIM W2) | 29% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Likely to switch in the next 3 months (Jan–Feb 2024): stated intent, not action | 21% (down from 30% in July 2023) | [CIM Wave 5 summary](https://ofgem-publications-fumadocs.vercel.app/publications/consumer-impacts-market-conditions-survey-wave-5-january-february-2024); [report PDF](https://www.ofgem.gov.uk/sites/default/files/2024-09/CIM_Wave_5_Final_Report.pdf) | P |
| Think cheaper deals are unlikely to be available (2024) | 31% | [CIM W5](https://ofgem-publications-fumadocs.vercel.app/publications/consumer-impacts-market-conditions-survey-wave-5-january-february-2024) | P |
| Default (SVT/cap) share of non-PPM accounts, April 2019 | 53% electricity / 51% gas | [Ofgem EFTC report](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf) | P |

**Stated versus revealed.** CIM "likely to switch" (21–30%) runs far above any revealed rate. In the CIM W2 survey, 69% said they were likely to switch to a cheaper tariff with their current supplier ([CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)). **Do not use stated intent as a switching probability.** As an assumption, apply a stated-to-revealed conversion of roughly 0.15–0.3 (A). The anchors are:

- **Deller et al.:** only "just over a quarter" of consumers offered positive savings in an opt-in collective switch accepted. For savings above £300 a year, only about half accepted ([Deller, Giulietti, Loomes, Waddams Price, Moniche, Jeon, Energy Journal 42(3), exec summary](https://iaee.org/ej/ejexec/ej42-3-Waddams-exsum.pdf)). These were people who had already opted in.
- **Credit Karma / Opinium:** 6% of adults said they would cancel energy DDs in October 2022 ([Credit Karma/Opinium via notltd](https://notltd.co.uk/news/we-wont-pay-insist-1-7m-planning-to-stop-energy-direct-debits)). No revealed figure was ever published. See Gaps.

### 1.2 Complaint funnel baselines

| Stage | Value | Source | Grade |
|---|---|---|---|
| Had reason to complain, past 12 months | ~20% | [Which? 2020 (survey Sept 2019, n=8,353)](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) | P |
| Of those, did not complain | 42% | [same](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) | P |
| Reason for not complaining: "wouldn't make a difference" | ~1/3 of non-complainers (58% among 55–64s) | [same](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) | P |
| Reason for not complaining: didn't know how | 17% of non-complainers | [same](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) | P |
| Complaints to suppliers per year (2019) | ~4m, plus ~2.9m unmade | [same](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) | S |
| Complaints as a share of recent supplier contacts | 12%, about 4% of all consumers | [Ofgem CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Complaint rate if dissatisfied vs satisfied | 37% vs 7% | [same](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Complaint rate, standard credit vs DD | 18% vs 10% | [same](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Made a complaint (ECSS, Jan 2025) | 6% (8% in July 2024) | [Ofgem ECSS Jan 2025 interim](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf) | P |
| Satisfied with complaint handling (ECSS) | 44% (Jan 2025); 47% (Jul 2024) | [same](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf) | P |
| Complaint status: gave up | 23% (30% concluded, 36% ongoing) | [Ofgem CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P (small base) |
| Complainants planning, switching or switched because of the complaint | 52% overall; npower 71% | [Ofgem complaints handling research 2016](https://www.ofgem.gov.uk/publications/complaints-energy-companies-research-report-2016) ([PDF](https://www.ofgem.gov.uk/sites/default/files/docs/2016/09/quadrangle_ofgemchs_report_final_22092016.pdf)) | P (stated plus actual mix) |
| Ombudsman cases accepted | 80,256 (2025); 92,938 (2024) | [Energy Ombudsman 2025](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) | P |
| Ombudsman cases that are billing | 56% (2025) | [same](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) | P |
| Ombudsman cases that are billing or meter reading | ~55% (2024) | [Ofgem Domestic Billing Performance Assessment, Jul 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf) | P |
| Suppliers signposting to the Ombudsman at 8 weeks or deadlock | 48% average (range 25–68%) | [Energy Ombudsman 2025](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) | P |
| Eligible consumers who don't use the Ombudsman | "as many as 75%" | [same](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) | P (estimate) |
| Resigned to poor service in energy | 15% | [Ombudsman Services CAM 2018](https://tag-craft.files.svdcdn.com/production/assets/assets/CAM-Report-2018.pdf) | P |

**Derived escalation ratio (A).** About 4m supplier complaints a year ([Which?](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/)) set against roughly 80–93k accepted Ombudsman cases ([EO](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)) gives **about 2–2.5% of complaints reaching the Ombudsman**.

The years don't match (2019 complaints against 2024–25 cases), so treat this as an order of magnitude. I would model it conditionally:

- **Base:** about 2% of all complaints.
- **Unresolved at 8 weeks:** about 10–20% escalate (A). The Ombudsman's own statement that up to 75% of eligible consumers don't use it implies about 25% of eligible (deadlocked) complainants do ([EO](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)).
- **Signposting:** multiply escalation by about 1.5 when the supplier signposts (A). Signposting coverage of 48% is the relevant variable.

### 1.3 Financial-stress baselines (the "silent" reactions)

| Metric | Value | Source | Grade |
|---|---|---|---|
| Reduced energy use because they can't afford it | 44% (Jul 2022); 43% (Mar 2022) | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Reduced spending on necessities | 34% (Jul 2022) | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Reduced spending on necessities | 26% (Jan–Feb 2024; 33% Jul 2023) | [CIM W5](https://ofgem-publications-fumadocs.vercel.app/publications/consumer-impacts-market-conditions-survey-wave-5-january-february-2024) | P |
| Behind on household bills: all | 10% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Behind on household bills: income under £16k | 17% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Behind on household bills: income £80k+ | 4% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Behind on energy bills | 9% (early 2024; 12% previous wave) | [CIM W5](https://ofgem-publications-fumadocs.vercel.app/publications/consumer-impacts-market-conditions-survey-wave-5-january-february-2024) | P |
| Contacted anyone for help paying (3 months) | 34%; 61% of those already behind | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Contacted their energy supplier for help | 9% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Contacted Ofgem for help | 3% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| PPM customers using emergency credit for affordability | 29% | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Electricity accounts in arrears with no arrangement (Q2 2026) | 1,187,788 (4.0%); average arrears £1,872 | [Ofgem debt and arrears indicators](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) | P |
| Electricity accounts repaying under an arrangement (Q2 2026) | 888,824 (3.0%); average debt £842 | [same](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) | P |
| Gas accounts in arrears with no arrangement (Q2 2026) | 954,966 (3.9%); average arrears £1,613 | [same](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) | P |
| Total domestic debt and arrears (Q2 2026) | £5.02bn | [same](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) | P |

**Derived (A).** Of electricity accounts with a debt problem, about **57% are in arrears without an arrangement** and about 43% are repaying under one: 1.19m ÷ (1.19m + 0.89m), using [Ofgem indicators](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators). This is the best available steady-state proxy for "no engagement after a debt letter".

---

## 2. Revealed switching after price rises

### 2.1 Centrica / British Gas, 2017–18

**2017.**
- Centrica lost **823,000 UK residential accounts from June to October 2017**, about 6% of accounts. Losses since the start of 2017 were about 8%, roughly 1.2m ([Enerdata](https://www.enerdata.net/publications/daily-energy-news/centrica-has-lost-more-one-million-customers-2017-uk.html); [Energy Digital](https://energydigital.com/oil-and-gas/centrica-loses-823000-customers-second-half-2017)) — S.
- Of these, about **150,000 left after the September 2017 tariff rise** ([Enerdata](https://www.enerdata.net/publications/daily-energy-news/centrica-has-lost-more-one-million-customers-2017-uk.html)) — S. The size of the rise is commonly reported as 12.5% on electricity [unverified]; the size was not confirmed on a fetched page.
- Context: about 600,000 households switched supplier in October 2017 alone ([Enerdata](https://www.enerdata.net/publications/daily-energy-news/centrica-has-lost-more-one-million-customers-2017-uk.html)) — S.

**2018.**
- British Gas raised SVT dual-fuel bills by **5.5% (£60 a year) for 4.1m customers** ([Energy Voice](https://energyvoice.com/all-news/171368/centrica-boosted-by-beast-but-still-losing-customers)) — S. The effective date is commonly cited as 29 May 2018 [unverified].
- Centrica lost **110,000 accounts in January–April 2018**, before the rise ([Energy Voice](https://energyvoice.com/all-news/171368/centrica-boosted-by-beast-but-still-losing-customers); [Sharecast](https://sharecast.com/amp/news/news-and-announcements/centrica-loses-110000-uk-customers-first-4-months-of-2018--3291784.html)) — S.
- It lost **340,000 in H1 2018** ([London Loves Business](https://londonlovesbusiness.com/centrica-profits-drop-loses-340000-uk-customer/); [Inkl](https://www.inkl.com/news/british-gas-owner-loses-340-000-uk-customer-accounts-after-bill-hikes)) — S.

**Derived revealed elasticity (A).**
- Before the rise, net loss was about 27.5k accounts a month (110k over 4 months).
- In May–June it was about 115k a month (230k over about 2 months).
- That is roughly a **4× spike in the monthly net-loss rate** in the 1–2 months around a 5.5% SVT rise, against a base of about 13m accounts.
- In hazard terms, monthly net churn moved from about 0.2% to about 0.9% of the base.

**Caveats.** These are net losses (gains are netted out) and the period boundaries are approximate. The spike also coincided with heavy price competition from challenger suppliers. **Lag:** the spike starts within the notice period (notice of about 30 days was required) and runs about 1–2 months after the effective date.

### 2.2 Collective switch trials (Ofgem, 2018)

**Active Choice Collective Switch trial.**
- Sample: about 50,000 customers who had been on an SVT for 3 years or more, at one Big Six supplier, February–April 2018.
- Result: **22.4% switched under a simplified exclusive offer, against 2.6% in a control group** ([Ofgem press release](https://www.ofgem.gov.uk/press-release/eight-times-many-people-get-better-deal-ofgems-collective-switch-trial)) — P.
- The average saving for switchers was about £300 ([same](https://www.ofgem.gov.uk/press-release/eight-times-many-people-get-better-deal-ofgems-collective-switch-trial)).
- Final results: [Ofgem](https://www.ofgem.gov.uk/research/active-choice-collective-switch-trial-final-results).

**Implications (A).**
- The **untreated hazard for deeply disengaged SVT customers is about 2.6% over about 3 months**, roughly 0.9% a month.
- Removing friction raises this about 8×.
- Even then, **about 78% did nothing** while being offered a saving of about £300.

### 2.3 End of fixed term (Ofgem EFTC RCT, 2019)

- Sample: n=19,553 analysed. Tariffs ended 28 February 2019. Switching was measured over 6 weeks ([Ofgem EFTC report](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)) — P.
- **Control:**
  - 19% requested a switch: about 14% internal re-fix and about 6% external.
  - About 81% rolled onto the default tariff.
  - The internal/external split was read from a chart; treat it as approximate.
- **Enhanced letter:** 28% switched, a gain of 9pp, all of it internal.
- **Planning assumption:** Ofgem assumed a baseline of 16% switching within 30 days of tariff end, from 2018 supplier data ([same](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)) — P.
- **Offline-only account holders** switched less: 12% (control) against 23% for online-only ([same](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)) — P.
- **Complaints during the trial:**
  - 146 in control (about 1.5% of the arm).
  - 199 under intervention (about 2.0%).
  - This gives a **price or renewal letter complaint rate of about 1.5–2% within 6 weeks** ([same](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)) — P, with the arm sizes derived.

### 2.4 Switching collapse and recovery around the 2021–24 crisis

- In 2022, switching collapsed because no deals beat the cap. Energy UK described a "slow start to switching in 2022" ([Energy UK](https://www.energy-uk.org.uk/news/slow-start-to-switching-in-2022/)) — S. I did not retrieve monthly volumes [unverified].
- Commentary describes 2024 as a "year of switching resurgence" after fixed deals returned below the cap ([Solar Power Portal / ElectraLink](https://www.solarpowerportal.co.uk/solar-projects/electralink-reviews-the-end-of-the-year-of-switching-resurgence-); [Energy Live News](https://energylivenews.com/2025/02/13/switching-is-back)) — S. Volumes are [unverified].
- **Modelling rule (A):** switching in response to any trigger must be gated on the **availability of a cheaper alternative**. In 2024, 31% believed none existed ([CIM W5](https://ofgem-publications-fumadocs.vercel.app/publications/consumer-impacts-market-conditions-survey-wave-5-january-february-2024)). When no alternative exists, the trigger's energy flows into rationing, arrears and complaints instead.

---

## 3. "Trigger" research: what precedes a switch

The evidence that names the event behind a switch is weak:

- **Ofgem Consumer Perceptions Q4 2019** did not quantify triggers. It reports only that 49% of SVT customers recalled receiving price-increase information ([Ofgem CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf)) — P.
- **CMA 2014 survey:**
  - 83% of switchers in the last 3 years cited cost or tariff reasons; 73% specifically cited a cheaper tariff.
  - Among those who had shopped around, 20% cited "existing tariff expensive" and 22% "nothing specific / just curious" ([CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf)) — P.
  - 76% of those who switched for customer-service reasons reported better service ([same](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf)) — P.
  - The appendix's itemised trigger table did not extract cleanly [unverified]. The remaining part of the PDF, past offset 100k, holds it and should be read manually.

**Proposed trigger shares (A, for calibration only).** These are anchored on revealed hazards:

- **End of fix:** EFTC at about 19% in 6 weeks.
- **Price-rise notice:** Centrica's about 4× spike.
- **Background:** collective-switch control at about 0.9% a month.

| Share of switches | Trigger |
|---|---|
| ~35–45% | End-of-fix window |
| ~15–25% | Price-rise or annual-review notice window |
| ~5–10% | Complaint or service failure (CMA's 76% "got better service" shows this route exists) |
| ~5–10% | Bill shock or DD change |
| ~25–35% | Untriggered or curious (CMA's 22% "nothing specific") |
| Excluded | Change-of-tenancy moves |

---

## 4. Analogue elasticities (telecoms and insurance)

**Ofcom: end-of-contract notifications (ECNs, February 2020).**
- **Broadband:** re-contracting rose about **+10pp at BT, EE and Virgin, and +13pp at Plusnet** after the alert. Savings were above £110 a year for some ([Ofcom 2022](https://ofcom.org.uk/news-centre/2022/end-of-contract-notifications-driving-better-deals-for-customers)) — P.
- Out-of-contract broadband fell from 40% (2019) to 35% (2020), though this is not attributed causally ([same](https://ofcom.org.uk/news-centre/2022/end-of-contract-notifications-driving-better-deals-for-customers)) — P.
- **Mobile:** the 2024 ex-post evaluation found **mixed, small effects**:
  - Re-contracting moved roughly between −8.6pp and +11.9pp by provider.
  - Switching (leaving the provider) moved by about ±2pp and was "slightly negative" overall.
  - There was no consistent age gradient. Notices go out 10–40 days before contract end ([Ofcom ECN ex-post evaluation 2024](https://www.ofcom.org.uk/siteassets/resources/documents/consultations/category-2-6-weeks/130197-helping-consumers-get-better-deals-on-their-broadband/ex-post-evaluation/ex-post-evaulation-ecn-2024.pdf)) — P. Provider labels were inferred.
- **Lesson:** a salient notice mostly produces **internal re-contracting**, not external switching. This matches the EFTC result.

**FCA general insurance pricing practices (GIPP) remedy.** Source: [FCA EP25/2](https://www.fca.org.uk/publication/corporate/ep25-2.pdf) — P.
- **Annual attrition** (non-renewal), pre- and post-remedy:
  - Home: 26% (2020) to 25% (2022).
  - Motor: 39% to 40%.
- **Auto-renewal effect on attrition:**
  - Home: about 20–21.5% with auto-renewal against 32–38.5% without.
  - Motor: 33–35% with against 49–54% without.
- **A default roughly halves to two-thirds the annual leaving rate (A).**
- Home auto-renewal by default rose from 54% to 70%. Of auto-renewing policies, 15–17% (home) and 11–15% (motor) actively cancelled auto-renewal.
- **Analogue (A):** a "DD cancellation" or opt-out of a default is a **10–17% a year** behaviour among people actively exposed to a renewal. This is an upper bound for energy, where the renewal salience is lower.

---

## 5. Evidence by pain point

### 5.1 Direct debit increase, by size

**Exposure.**
- Before the April 2022 cap rise of 54%, SVT DDs rose **62% on average**, and **8% of SVT customers saw a rise above 100%** ([Ofgem DD review decision, Jul 2022](https://www.ofgem.gov.uk/decision/ofgem-seeks-improvements-12-suppliers-relation-customer-direct-debit-setting)) — P.
- 71% of DD customers saw a DD increase within 4 months, and **57% of those believed they were being charged more than needed** ([CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)) — P.

**MSE survey** (41,000 self-selected respondents, 26 April – 3 May 2022), from [MSE](https://www.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey) — P, biased toward the angry:
- 25% of in-credit capped customers saw their DD at least double. The median rise was 66%.
- The share who saw it double rose to 38–46% for customers coming off a fix.
- **46% of those whose DD doubled did not challenge it, "because they didn't know they could"**. The challenge rate is therefore at most about 54% even in this angry, self-selected sample, and probably well below that in the population (A).

**DD cancellation.**
- Only stated intent exists: 6% of adults planned to cancel energy DDs in October 2022 ([Credit Karma/Opinium](https://notltd.co.uk/news/we-wont-pay-insist-1-7m-planning-to-stop-energy-direct-debits)) — S.
- In 2024, 26% felt their DDs were set too high, and 33% found the DD calculation hard to understand ([Warm This Winter/Opinium via NPC](https://npcuk.org/post/two-thirds-of-public-demand-automatic-return-of-credit)) — S.

**Dose–response proposal (A).** Contact probability within 30 days of a DD change notice:

| DD change | Contact probability |
|---|---|
| Up to +10% | 2–4% |
| +10–30% | 5–10% |
| +30–60% | 10–20% |
| +60–100% | 20–35% |
| Over +100% | 35–50% |

The anchor at the top is MSE's 54% ceiling, discounted for self-selection. Other reactions:
- **Complaint:** about 25–35% of contacts. The anchor is Ofgem's figure that complaints are 12% of all contacts, raised because these are dispute contacts (A).
- **DD cancellation or payment-method change:** 0.5–2% for rises above 60%. This is stated intent of 6% × a 0.15–0.3 conversion (A).
- **Switching:** only if a cheaper alternative exists. Hazard multiplier of about 1.5–2× for 60 days (A, half the Centrica price-rise multiplier, because a DD change is not a price change).

### 5.2 Catch-up or shock bill

**Exposure.**
- In 2024, suppliers **wrote off backbilled charges for almost 1m customers, totalling over £172m**, about £200 each ([Ofgem Billing Performance Assessment 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)) — P.
- Customers can still receive catch-up bills covering up to 12 months.
- Resolution took 2–10 months, depending on the supplier ([same](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)) — P.
- 3.5m bills were issued 3–12 months late ([same](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)) — P.
- On Citizens Advice billing cases, the **average catch-up bill could have risen by more than £800 over three years** ([Citizens Advice, Footing the bill, Nov 2024](https://www.citizensadvice.org.uk/policy/publications/footing-the-bill-how-the-energy-bill-protection-gap-is-putting-strain-on/)) — P.
- Citizens Advice billing help requests: more than 52,000 by October 2024, 83% above 2020 ([same](https://www.citizensadvice.org.uk/policy/publications/footing-the-bill-how-the-energy-bill-protection-gap-is-putting-strain-on/)) — P.
- 49% had at some point unexpectedly owed or been owed money after a meter reading. Average amounts were £125 owed and £137 owed to them; 5% owed £500 or more ([Uswitch/Opinium 2016](https://www.uswitch.com/media-centre/2016/09/1-in-4-households-face-energy-bill-shock-from-estimated-meter-readings/)) — P (old).

**Ombudsman.**
- Backbilling cases: 3,216 (2025) and 3,238 (2024) ([EO 2025](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)) — P.
- This is about 5% of referrals ([Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)) — P.
- **Derived (A):** about 3,200 cases against about 1m customers with write-offs is **an Ombudsman rate of about 0.3% per backbilled customer**. Write-off customers were partly protected, so the rate among unprotected catch-up recipients is probably higher; about 0.5–1% (A).

**Reactions (A).**
- **Contact:** 30–50% for a catch-up bill above £300. Billing and metering make up about 30% of supplier complaints ([Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)).
- **Arrears:** 15–30% of low-income recipients, using CIM W2's 17% behind-on-bills rate for under £16k as a floor.
- **Giving up:** 23%, the CP Q4 2019 rate.

### 5.3 A run of estimated bills

- **19% of first-issue bills in 2024 were not based on actual reads**, falling to about 11% after reconciliation ([Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)) — P, inferred from 81% and 89%.
- 77% are satisfied with bill accuracy and 8% dissatisfied (July 2024) ([same](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)). This rose to 80% satisfied in January 2025 ([ECSS Jan 2025](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf)) — P.
- 26% submit readings less than quarterly ([Uswitch 2016](https://www.uswitch.com/media-centre/2016/09/1-in-4-households-face-energy-bill-shock-from-estimated-meter-readings/)) — P.

**There is no source that quantifies reactions to a run of estimates.**

**Modelling (A).**
- Treat estimates as **resentment accumulators with near-zero direct action**: about 1–3% contact per estimated bill.
- The action crystallises at the **true-up** (5.2) or at a DD change (5.1).
- Contact probability should rise with the number of consecutive estimates (k): roughly 2% at k=1 and 8–12% at k≥4 (A).

### 5.4 Large credit balance or refused refund

- Domestic credit balances were **£7.1bn gross (about £4.1bn net of unbilled use) in Q1 2023**, about £140 net per customer ([Ofgem letter to ESNZ Committee, Nov 2023](https://www.ofgem.gov.uk/sites/default/files/2023-12/ESNZ%20Committee%20letter%20on%20CCBs.pdf)) — P.
- From Opinium polling in 2024 ([via NPC](https://npcuk.org/post/two-thirds-of-public-demand-automatic-return-of-credit)) — S, with the survey attribution mixed:
  - 32% of households were in credit all year.
  - **28% never tried to reclaim credit.**
  - **12% were refused** despite being in credit.
  - Nearly a third found it difficult to get credit back.
  - 68% want credit returned automatically.
- Ofgem said suppliers held more than £400m on closed accounts ([Ofgem](https://www.ofgem.gov.uk/press-releases/ofgem-calls-suppliers-take-action-over-400-million-they-hold-customers-closed-accounts)) — P. This is another form of giving up.

**Modelling (A).**
- **Refund request:** 15–25% a year when credit exceeds about £200, rising with the balance. Inferred from 28% never trying against 32% in credit; the denominators are unclear.
- **Refusal:** about 12% of requests.
- **Complaint if refused:** 30–40%, using the "dissatisfied" complaint rate of 37% ([CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf)).
- **DD reduction or cancellation:** a high-credit DD customer who is refused is the most likely group to cut or cancel the DD. About 5–10% (A, no direct evidence).

### 5.5 Billing error

- Billing is **56% of Ombudsman cases** ([EO 2025](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)). In 2018, 60% of Ombudsman Services cases were billing ([Which? 2020](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/)) — P/S.
- Billing and metering are **about 30% of supplier complaints but about 55% of Ombudsman cases** ([Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)) — P.

**Implication (A).** Billing complaints escalate at roughly **1.8× the average complaint** (55 ÷ 30).

**Modelling (A).**
- **Contact on a detected error:** 50–70%. An error is salient and attributable; Which? found 58% complain among those with a reason.
- **Complaint:** 40–60% of contacts.
- **Ombudsman:** about 3–4% of complaints, which is 2% × 1.8.

### 5.6 Price rise or renewal letter

**Revealed evidence.**
- **End-of-fix letter:** 19% act within 6 weeks (mostly an internal re-fix) and 81% go to the default ([EFTC](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)) — P.
- **SVT rise of 5.5%:** about 4× monthly net-loss spike for 1–2 months ([Energy Voice](https://energyvoice.com/all-news/171368/centrica-boosted-by-beast-but-still-losing-customers); [LLB](https://londonlovesbusiness.com/centrica-profits-drop-loses-340000-uk-customer/)) — S/A.
- **Complaint:** about 1.5–2% within 6 weeks ([EFTC](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf)) — P.
- **Rationing under large cap rises:** 44% reduced use ([CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)) — P.

**Recall.** Only 49% of SVT customers recall price-rise information at all ([CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf)) — P. Apply a **salience filter of about 0.5** (A) before any reaction.

### 5.7 Debt or collection letter

- **57% of electricity accounts with debt are in arrears without an arrangement** ([Ofgem indicators, Q2 2026](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators)) — P/A. This is a steady-state non-engagement proxy.
- **National Debtline / Money Advice Trust** ([via Credit Connect, Jan 2024](https://www.credit-connect.co.uk/?p=90435)) — S, sample not stated:
  - 13% of people in debt are scared to open post.
  - 12% are afraid to speak to creditors.
  - **4 in 10 National Debtline clients wait a year or more before seeking help.**
- 61% of those already behind had contacted someone for help, but only 9% of all respondents contacted their supplier ([CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)) — P.
- 65% of those behind on bills worry about disconnection ([same](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf)) — P.

**Modelling (A).**
- **Engagement:** P(arrangement agreed within 60 days of a first debt letter) is about 25–40%. This is calibrated so that the steady state reproduces the 43:57 split between arrangements and arrears without one.
- **Avoidance:** about 12–15% persistent avoiders, who never respond to letters.
- **Lag for the rest:** heavy-tailed, with a median of months and about 40% at 12 months or more.
- **Rationing:** high, around 50–65%. Anchor: 44% of all households rationed in 2022, and arrears households will be higher.
- **Switching: about 0.** Indebted customers are effectively locked in by the debt-objection rules; this is from domain knowledge, and no URL was retrieved [unverified].

### 5.8 Poor complaint-handling experience

- 44–47% are satisfied with complaint handling ([ECSS Jan 2025](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf)) — P.
- In 2019, 59% were satisfied with the outcome ([CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf)) — P.
- **52% of complainants planned, were in the process of, or had switched**. Where very dissatisfied rates were highest (npower 67% very dissatisfied), 71% had switched or planned to ([Ofgem 2016 complaints research](https://www.ofgem.gov.uk/publications/complaints-energy-companies-research-report-2016)) — P, stated plus revealed.
- 23% of complainants gave up ([CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf)) — P.
- About 25% of eligible consumers use the Ombudsman ([EO](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)) — P. Signposting reaches 48% ([same](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025)) — P.
- Ombudsman Services CAM, all sectors: 30% switched providers or spent less after disappointing experiences ([CAM 2018](https://tag-craft.files.svdcdn.com/production/assets/assets/CAM-Report-2018.pdf)) — P, but not energy-specific.

**Modelling (A).** Revealed switching is about 15–25% within 6 months after a poorly handled complaint. This applies the 0.3–0.5 stated-to-revealed discount to 52%, recognising that the complaint has already selected engaged customers.

---

## 6. How reactions vary by group

| Group | Effect | Source | Grade |
|---|---|---|---|
| Income under £18k | Switched in last 3 yrs 20% vs 35% (over £36k) | [CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| No qualifications | Switched 18% vs 32% (degree) | [same](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| No internet | Switched 11% vs 29% | [same](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| No internet | Ever switched 32%; PCW use 5%; more satisfied (86% vs 71%) | [CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Offline-only accounts at end of fix | 12% act vs 23% online-only | [EFTC](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf) | P |
| Prepayment | Switched 22% vs 30% DD; shopped around 25% vs 37% | [CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) | P |
| C2DE | Ever switched 49% (below ABC1) | [CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Age 16–34 | Most likely to complain (23% of contacts); least likely to have ever switched (44%) | [same](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| Age 55–64 | 58% of non-complainers think complaining "won't make a difference" | [Which? 2020](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) | P |
| Age 65+ | Rationing among DD customers rose to 46% (from 37%) | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Income under £16k | Behind on bills 17% vs 4% (£80k+); disconnection worry 50% | [same](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Benefits recipients | Behind on bills 17% vs 6% non-claimants | [same](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |
| Financially vulnerable | Supplier satisfaction 66% (highly vulnerable) vs 89% (doing well) | [ECSS Jan 2025](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf) | P |
| Standard credit payers | Complain more (18% vs 10% DD) | [CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) | P |
| PSR | About 9m customers (about 25%) | [Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf) | P |
| PSR | More often contacted by suppliers (31% vs 28% about price rises) | [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) | P |

**Suggested multipliers on external action (A), relative to an engaged online DD payer = 1.0:**

| Segment | Switch | Complain | Ombudsman | Ration | Arrears |
|---|---|---|---|---|---|
| Disengaged (3+ years on SVT) | 0.3 | 0.7 | 0.5 | 1.0 | 1.0 |
| Low income / benefits | 0.6 | 0.9 | 0.7 | 1.4 | 2.5 |
| Older (65+) | 0.6 | 0.7 | 0.6 | 1.2 | 0.7 |
| Digitally excluded | 0.4 | 0.8 | 0.5 | 1.2 | 1.3 |
| Prepayment | 0.7 | 0.8 | 0.6 | 1.5 (self-disconnection) | n/a; debt sits on the meter |

The anchors are the CMA and Ofgem ratios above. For example, the switch multiplier for no internet is 11/29 ≈ 0.4, and for low income 20/35 ≈ 0.6.

---

## 7. Summary table

Probabilities are **per household experiencing the event**, within the stated lag. Where a cell is graded P or S, the figure is taken directly from the source. Where it is graded A, it is calibrated from the named anchor.

| # | Pain point | Contact / complaint | Ombudsman | Switch / churn (lag) | DD cancel / method change | Arrears | Rationing | Gives up / no action | Key sources |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DD increase | Contact by size: ≤10%: 3%; 10–30%: 7%; 30–60%: 15%; 60–100%: 28%; >100%: 40–50% (30 days). Complaint ≈30% of contacts [A] | ≈2% of complaints [A] | Hazard ×1.5–2 for 60 days, only if a cheaper deal exists [A] | 0.5–2% for rises >60% [A] (stated intent 6% [S]) | +1–3pp for low income on large rises [A] | +5–10pp [A] | ≥46% of those with a doubled DD did not challenge [P, self-selected] | [MSE](https://www.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey); [Ofgem DD review](https://www.ofgem.gov.uk/decision/ofgem-seeks-improvements-12-suppliers-relation-customer-direct-debit-setting); [Opinium](https://notltd.co.uk/news/we-wont-pay-insist-1-7m-planning-to-stop-energy-direct-debits) |
| 2 | Catch-up / shock bill | Contact 30–50% if >£300 (14 days); complaint 40% of contacts [A] | 0.3% of backbilled customers (P-derived); 0.5–1% if unprotected [A] | Hazard ×1.5 for 90 days [A]; blocked if debt objection applies | Payment-method change 3–5% [A] | 15–30% low income; 5–10% others (60–90 days) [A] | 20–40% [A] | 23% of complainants give up [P] | [Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf); [CA 2024](https://www.citizensadvice.org.uk/policy/publications/footing-the-bill-how-the-energy-bill-protection-gap-is-putting-strain-on/); [EO](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) |
| 3 | Run of estimated bills (k bills in a row) | 2% at k=1, rising to 8–12% at k≥4 [A] | ~0 directly [A] | ~0 directly; stored as resentment [A] | ~0 [A] | ~0 until true-up [A] | ~0 [A] | ≈90%+ no action [A] (19% of first bills estimated [P]) | [Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf); [Uswitch](https://www.uswitch.com/media-centre/2016/09/1-in-4-households-face-energy-bill-shock-from-estimated-meter-readings/) |
| 4 | Large credit / refund refused | Refund request 15–25% a year if credit >£200 [A]; 12% refused [S]; complaint after refusal 30–40% [A] | ≈2% of complaints [A] | Hazard ×1.5 for 90 days after refusal [A] | DD cut or cancel 5–10% after refusal [A] | n/a | n/a | 28% never try [S]; about 1/3 find it difficult [S] | [Ofgem CCB letter](https://www.ofgem.gov.uk/sites/default/files/2023-12/ESNZ%20Committee%20letter%20on%20CCBs.pdf); [NPC/Opinium](https://npcuk.org/post/two-thirds-of-public-demand-automatic-return-of-credit) |
| 5 | Billing error (detected) | Contact 50–70%; complaint 40–60% of contacts (7 days) [A] | ≈3.5% of complaints (1.8× average) [A from P] | Hazard ×2 for 90 days [A] | 2–4% [A] | Low income +2–5pp if the error is an undercharge [A] | low | 42% of those with cause don't complain [P] | [Which?](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/); [Ofgem 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf) |
| 6a | End-of-fix / renewal notice | Complaint 1.5–2% within 6 weeks [P] | ~0 | 19% act in 6 weeks: 14% re-fix, 6% external switch; 28% with a good prompt [P] | ~0 | ~0 | ~0 | 81% roll to default [P] | [EFTC](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf) |
| 6b | SVT/cap price rise (about 5%) | Complaint ~1–2% [A from EFTC] | ~0 | Monthly net-loss rate ×4 for 1–2 months (about 0.2% to 0.9% a month) [S/A]; untreated disengaged base about 0.9% a month [P] | ~0 | Shift with rise size [A] | 44% under 2022-scale rises [P]; about 5–10% for small rises [A] | About 50% don't recall the notice [P]; 78% inaction even with a £300 offer [P] | [Energy Voice](https://energyvoice.com/all-news/171368/centrica-boosted-by-beast-but-still-losing-customers); [LLB](https://londonlovesbusiness.com/centrica-profits-drop-loses-340000-uk-customer/); [Collective switch](https://www.ofgem.gov.uk/press-release/eight-times-many-people-get-better-deal-ofgems-collective-switch-trial); [CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) |
| 7 | Debt / collection letter | Arrangement agreed 25–40% within 60 days [A, steady state 43:57 P] | <0.5% [A] | ~0 (debt-blocked) [unverified] | Moves to PPM or payment plan within the arrangement path [A] | 57% of debtors stay in arrears without an arrangement [P-derived] | 50–65% [A] | 12–15% persistent avoiders [S]; 40% wait 12+ months [S] | [Ofgem debt indicators](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators); [National Debtline](https://www.credit-connect.co.uk/?p=90435) |
| 8 | Poor complaint handling | Repeat contact 40–60% [A] | 10–25% if deadlocked at 8 weeks; about 25% of eligible use the Ombudsman [P]; ×1.5 if signposted [A] | Stated 52% (P); revealed 15–25% within 6 months [A] | 3–5% [A] | n/a | n/a | 23% give up [P]; 15% resigned [P] | [Ofgem 2016](https://www.ofgem.gov.uk/publications/complaints-energy-companies-research-report-2016); [ECSS](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf); [EO](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025); [CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) |

---

## 8. How to model inertia and triggers: accumulate, then crystallise

1. **Two state variables per household.**
   - Grievance G accumulates on every pain point, weighted by severity, and decays slowly (half-life about 6–12 months, A).
   - Financial strain F is driven by bill size against income.
   - Most pain points move **only G or F**, with no visible action. This is consistent with the 42% non-complaint rate, the 46% non-challenge rate, 81% defaulting at the end of a fix, and 78% inaction even with a £300 offer.

2. **Salience gate.** External action can fire only in a **trigger window**:
   - an end-of-fix notice (6 weeks);
   - a price-rise notice (about 30 days before plus about 60 days after);
   - a DD change notice (30 days);
   - a catch-up or error bill (14–30 days);
   - a complaint deadlock (8 weeks).

   Outside these windows, use the background hazard of about 0.9% a month for disengaged customers ([collective-switch control](https://www.ofgem.gov.uk/press-release/eight-times-many-people-get-better-deal-ofgems-collective-switch-trial)). Apply a recall filter of about 0.5 for letter-based triggers ([CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf)).

3. **Crystallisation.** Inside a window:

   P(action) = 1 − exp(−(β₀ + β_G·G + β_event)) × friction

   - **Friction:** about 0.3–0.4 for offline or disengaged segments; derived from offline 12% against online 23% in the EFTC, and the CMA's 11% against 29%.
   - **Calibration targets:** 19% action at the end of a fix with G≈0; about 4× churn on a price rise; a 22.4% ceiling when friction is removed.

4. **Action routing.** The action taken depends on the household's options:
   - **Cheaper alternative available:** route mainly to internal re-fix or external switch. The EFTC split was about 70:30 internal to external.
   - **No alternative (as in 2022):** route to complaint, rationing or arrears.
   - **In debt:** route to rationing or avoidance.
   - **Billing-type grievance:** route to complaint, with escalation weighted 1.8×.

5. **Lags.** Use heavy-tailed lags for debt help-seeking (lognormal, median about 6 months, 40% beyond 12 months). Use short lags for notices (days to 6 weeks).

---

## 9. Gaps

1. **No revealed GB data on DD cancellation or payment-method change after a DD rise.** Only stated intent exists (6%, Opinium 2022). Supplier DD-mandate cancellation logs or Bacs data would close this.
2. **No dose–response by size of DD rise for contact or complaint.** The MSE data gives medians and a single "didn't challenge" figure, and only for doublings.
3. **Trigger attribution for switches is unquantified.** The CMA trigger table (App 8.1, past offset 100k) and the Ofgem Consumer Engagement Survey 2017–19 trigger questions need manual extraction [unverified].
4. **Monthly switching volumes around cap changes from 2019 to 2026 (Energy UK, ElectraLink) were not retrieved.** Event-study multipliers for cap announcements are therefore assumed.
5. **The size and date of the Centrica 2017 rise** (12.5% electricity, September 2017) are [unverified]. The 2018 figures are net and approximate.
6. **There is no study of reactions to consecutive estimated bills.**
7. **The refund-refusal → complaint → switch chain has no direct evidence.** The Opinium figures come via campaign reporting with mixed survey attribution.
8. **Revealed switching after a bad complaint is not separated from stated intent.** The Ofgem 2016 52% mixes the two. The full Quadrangle PDF may split them.
9. **The Ombudsman escalation rate mixes years**: 2019 supplier complaints against 2024–25 Ombudsman cases. Current total supplier complaint volumes were not retrieved.
10. **The CIM Wave 6+ (2024–26) tables were not read.** Rationing, self-disconnection and contact-supplier rates in the post-crisis "normal" market would recalibrate the 2022 crisis figures.
11. **Analogues are thin.** Ofcom mobile ECN effects are mixed, and the FCA gives attrition, not causal switching responses. Neither covers bill-shock analogues; Ofcom's mid-contract price-rise rules (2024–25) and FCA Consumer Duty data were not searched.
12. **Group splits for reactions** (as opposed to engagement levels) are scarce. Most multipliers are derived from engagement ratios, not from reaction-specific data.

---

**Sources used** (all cited inline): [MSE 2022](https://www.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey) · [Ofgem DD review 2022](https://www.ofgem.gov.uk/decision/ofgem-seeks-improvements-12-suppliers-relation-customer-direct-debit-setting) · [Ofgem CIM W2](https://ofgem.gov.uk/sites/default/files/2022-09/2261_Ofgem___CIM_W2_V10%20FINAL.pdf) · [CIM W5](https://ofgem-publications-fumadocs.vercel.app/publications/consumer-impacts-market-conditions-survey-wave-5-january-february-2024) · [Ofgem collective switch](https://www.ofgem.gov.uk/press-release/eight-times-many-people-get-better-deal-ofgems-collective-switch-trial) · [Ofgem EFTC](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf) · [Ofgem CP Q4 2019](https://www.ofgem.gov.uk/system/files/docs/2020/03/consumer_perceptions_of_the_energy_market_q4_2019.pdf) · [Ofgem ECSS Jan 2025](https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy%20Consumer%20Satisfaction%20Survey%20-%20Interim%20Report%20of%20Findings%20January%202025%20.pdf) · [Ofgem Billing Performance 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf) · [Ofgem debt indicators](https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) · [Ofgem CCB letter](https://www.ofgem.gov.uk/sites/default/files/2023-12/ESNZ%20Committee%20letter%20on%20CCBs.pdf) · [Ofgem complaints 2016](https://www.ofgem.gov.uk/publications/complaints-energy-companies-research-report-2016) · [CMA App 8.1](https://assets.publishing.service.gov.uk/media/559fb619ed915d1592000044/Appendix_8.1_Customer_survey.pdf) · [Energy Ombudsman 2025](https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) · [Which? 2020](https://www.which.co.uk/news/2020/02/energy-complaints-wouldve-hit-almost-6-9-million-in-the-last-year-did-your-gripe-go-unheard/) · [CAM 2018](https://tag-craft.files.svdcdn.com/production/assets/assets/CAM-Report-2018.pdf) · [Citizens Advice 2024](https://www.citizensadvice.org.uk/policy/publications/footing-the-bill-how-the-energy-bill-protection-gap-is-putting-strain-on/) · [Uswitch 2016](https://www.uswitch.com/media-centre/2016/09/1-in-4-households-face-energy-bill-shock-from-estimated-meter-readings/) · [NPC/Opinium 2024](https://npcuk.org/post/two-thirds-of-public-demand-automatic-return-of-credit) · [Credit Karma/Opinium 2022](https://notltd.co.uk/news/we-wont-pay-insist-1-7m-planning-to-stop-energy-direct-debits) · [National Debtline 2024](https://www.credit-connect.co.uk/?p=90435) · [Enerdata 2017](https://www.enerdata.net/publications/daily-energy-news/centrica-has-lost-more-one-million-customers-2017-uk.html) · [Energy Voice 2018](https://energyvoice.com/all-news/171368/centrica-boosted-by-beast-but-still-losing-customers) · [LLB 2018](https://londonlovesbusiness.com/centrica-profits-drop-loses-340000-uk-customer/) · [Deller et al. 2021](https://iaee.org/ej/ejexec/ej42-3-Waddams-exsum.pdf) · [Ofcom ECN 2022](https://ofcom.org.uk/news-centre/2022/end-of-contract-notifications-driving-better-deals-for-customers) · [Ofcom ECN ex-post 2024](https://www.ofcom.org.uk/siteassets/resources/documents/consultations/category-2-6-weeks/130197-helping-consumers-get-better-deals-on-their-broadband/ex-post-evaluation/ex-post-evaulation-ecn-2024.pdf) · [FCA EP25/2](https://www.fca.org.uk/publication/corporate/ep25-2.pdf) · [Energy UK 2022](https://www.energy-uk.org.uk/news/slow-start-to-switching-in-2022/) · [Solar Power Portal / ElectraLink](https://www.solarpowerportal.co.uk/solar-projects/electralink-reviews-the-end-of-the-year-of-switching-resurgence-)

*Process note: I used about 25 searches and fetches. Memory was not used. No files were written.*
## Done

2026-11-07, worker tick. Attached as `evidence:` to the candidate `unbilled-energy-pain-points-react` in
`customer_outcomes_candidates` (`docs/direction/priority_order.yaml`), the world-reaction build the pack
names. The build comes after the correctness exit test, as the pack says. Its S/A rows are verified against
primary sources before any world parameter rests on them.
