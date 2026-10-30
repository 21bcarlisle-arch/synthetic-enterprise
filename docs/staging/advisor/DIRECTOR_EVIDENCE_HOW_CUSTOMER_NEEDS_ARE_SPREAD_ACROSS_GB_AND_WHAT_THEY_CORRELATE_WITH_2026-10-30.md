**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] How customer needs are spread across GB, and what they correlate with (2026-10-30)

**Type:** EVIDENCE, through the advisor channel, for `DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`. The director's words, from chat on Fri 30 Oct, 16:22 GMT: "To what degree are the individual dimensions covered by these topics and are there bodies of research available on them individually as topics in energy or other sectors such as financial services or telecoms?"

This pack is from an advisor research pass and is sourced from the web. Items tagged [unverified] are calibration assumptions, not evidence. Verify them with your own network access while drafting.

---

# Distribution of household energy needs in Great Britain: correlates and data sources for the six-need model

*Research report. Every claim has a URL beside it. Anything I could not confirm from a fetched page is tagged [unverified]. Searches and fetches were done on 2026-10-30.*

---

## 0. Executive summary

- **Most of the hidden needs are not independent.** One latent factor drives cash flow, control, certainty and comfort/health. Call it "financial precarity." Its strongest observable proxies are **tenure (renting, especially social renting)**, **low income (<£15–16k)**, **IMD decile 1–2**, **single parenthood**, **unemployment or disability**, and **prepayment status**. The size of the effect is large and consistent: these groups are roughly 2–3× the national rate on low resilience, prepayment, worry and fuel poverty.
- **Carbon and time form a second axis, which is close to orthogonal to precarity and partly opposed to it.** Carbon concern rises steeply with **education (degree)** and varies by region (London and the South West are high; the West Midlands and Scotland are low). Low-carbon technology ownership (EV, PV, heat pump) follows **wealth, owner-occupation, detached housing, off-street parking and rurality or off-gas status**. Concern alone does not predict ownership.
- **Time need (hassle aversion) is the least well measured.** The proxies are disengagement data, which correlate with **C2DE, social renting, prepayment and standard credit** (54–69% disengaged), plus value-of-time theory, which scales with income at elasticity ≈1. So "hassle" shows up in two distinct populations. One is the low-income disengaged, for whom the barrier is capability and trust. The other is the time-poor high earners, for whom the barrier is opportunity cost.
- **Certainty is bimodal.** Worry about bills tracks precarity: 27–33% of renters are very worried, against 13–15% of owners. Uptake of fixed tariffs, by contrast, has historically skewed to engaged, direct-debit, higher-income customers. So the people with the highest certainty *need* are the least likely to hold a certainty *product*.

---

## 1. CASH FLOW: liquidity, buffers, income timing and regularity

### 1.1 National distribution
- 24% of UK adults (13.1m) had **low financial resilience** in May 2024, unchanged from 2022 ([FCA FLS 2024 key findings](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).
- 10% had **no cash savings**. 21% had **less than £1,000** ([FCA FLS 2024](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).
- 9% could not cover living costs for **one week** if they lost their main income. 42% could not cover **three months** ([FCA FLS 2024](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).
- 8% (4.3m) were **constantly or usually overdrawn by payday** ([FCA FLS 2024](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).
- 8% were in **financial difficulty**, defined as missing bills in 3 or more of the last 6 months. 13% found bills a **heavy burden** ([FCA FLS 2024](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).

### 1.2 Correlates (FCA FLS May 2022, the most detailed published split)
Source: [FCA FLS 2022 early insights](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience/printable/print)

| Attribute | Low financial resilience | In financial difficulty |
|---|---|---|
| All UK adults | 24% | 8% |
| Renters | **47%** | 19% |
| Mortgage holders | 17% | – |
| Household income < £15k | **50%** | 20% |
| Unemployed | 48% | 25% |
| Gig-economy workers | 37% | 16% |
| Black / Black British | 44% | 16% |
| Mixed ethnicity | 39% | 13% |
| IMD decile 1 (most deprived) | **42%** | 20% (vs 3% least deprived) |
| Age 18–54 | 29% | 12% (age 25–44) |
| Women | 28% | 9% |
| North East | 31% | 12% |
| North West | 28% | 10% |
| South West | 21% | 6% |
| South East | 19% | 6% |

The FCA reported that differences between the four nations were small and not significant ([FCA 2022](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience)). The 2024 key-findings PDF has the same segment chart (Fig 3.9), but its values were not in the extractable text. A simulation should take the 2024 values from the FCA data tables [unverified that the 2024 split matches 2022].

### 1.3 Wealth buffers (ONS Wealth and Assets Survey, Apr 2020–Mar 2022)
Source: [ONS Household total wealth 2020–22](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022)
- Median **financial** wealth is £10,400 overall. It is **£900 for renters** and £55,300 for outright owners, a gap of about 60×.
- By age of household head, median financial wealth is £1,300 at 25–34 and £32,300 at 65–74.
- It is £300 for households that are economically inactive but not retired.
- Median total wealth is £489,800 in the South East and £179,900 in the North East.
- Caveats: ONS suspended accreditation for this round, and the London estimates are especially uncertain ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022)).

### 1.4 Income volatility and timing
- About 75% of workers see their pay fluctuate month to month, and about 40% have persistent volatility. This comes from 7m Lloyds accounts covering 2016–17 ([Resolution Foundation, Oct 2018](https://www.resolutionfoundation.org/?p=17788); [report PDF](https://www.resolutionfoundation.org/app/uploads/2018/10/Irregular-payments-RF-REPORT.pdf)).
- More than 80% of low earners (around £10k) see volatility, against about two in three earners on around £35k. The average monthly fall is 20% ([RF 2018](https://www.resolutionfoundation.org/?p=17788)).
- Two in five low-to-middle-income families cannot save more than £10 a month ([RF 2018](https://www.resolutionfoundation.org/?p=17788)).
- About 40% of new Universal Credit claimants are paid more often than monthly. When two four-weekly pay packets fall in one assessment period, UC can drop sharply. This is a structural source of cash-flow lumpiness for low-income workers ([RF 2018](https://www.resolutionfoundation.org/?p=17788)).
- **Universal Credit:** 8.4m people in 7.2m households were on UC in May 2026, a record. 37.7% of claimants were in work and 44% of paying households had children ([DWP UC statistics to May 2026](https://www.gov.uk/government/statistics/universal-credit-quarterly-statistics-29-april-2013-to-14-may-2026/universal-credit-quarterly-statistics-29-april-2013-to-14-may-2026)). Regional splits are in DWP Stat-Xplore.
- I did not find a fetched source for the share of the workforce paid weekly or four-weekly. A commonly cited figure is that about 1 in 5 employees are paid weekly or four-weekly [unverified].

**What this means for the simulation:** cash-flow need ≈ f(tenure, income, age, IMD, employment type, UC receipt). Renters at under £15k sit at about 2× the national rate of low resilience.

---

## 2. CONTROL: budgeting, visibility, debt avoidance

### 2.1 Payment method distribution (DESNZ Public Attitudes Tracker, Summer 2025)
Source: [DESNZ PAT Energy bills and tariffs, Summer 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk)

| Group | Direct debit | Pay on receipt (standard credit) | Prepayment |
|---|---|---|---|
| All | 80% | 10% | 9% |
| Owner-occupiers | 89% | – | **2%** |
| Renters | 60% | – | **23%** |
| Social renters | – | – | **27%** |
| Private renters | – | – | 15% |
| Income < £15k | 69% | 13% | **15%** |
| Income ≥ £45k | 93% | 5% | 2% |
| Age 16–24 | 60% | – | – |
| Age 65+ | – | – | 4% (vs 8–14% under 55) |
| Finding it difficult financially | – | – | 17% (vs 5% "fine") |

Prepayment correlates with **social renting at about 13× the owner rate**, and with low income at about 7× the rate for incomes of £45k or more. Standard credit (paying on receipt) is concentrated in low-income and older households: 13% of those under £15k against 5% of those at £45k or more. The older skew is my inference from the age pattern, and the age split for standard credit was not given [unverified].

**Regional prepayment.** DESNZ publishes regional payment-method shares in QEP tables 2.4.2 (standard electricity), 2.4.3 (Economy 7) and 2.5.2 (gas), most recently updated on 29 September 2026 ([DESNZ quarterly domestic energy price statistics](https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-price-stastics)). I could not fetch the spreadsheets from this environment. Northern Ireland is widely reported to have the highest prepayment share (keypad meters, over 40%), followed by the North East, Scotland, the North West and Wales [unverified; read off table 2.4.2].

### 2.2 Why people choose prepayment
- 65% of smart prepayment users said budgeting got easier after moving from an analogue meter, and 72% said they understood their usage better. This is a Censuswide poll of 2,000 adults for Smart Energy GB, published in March 2023, so the source has an interest in the result ([Solar Power Portal report of the poll](https://www.solarpowerportal.co.uk/residential-solar/new-poll-by-smart-energy-reaffirms-the-benefits-of-smart-prepayment-meters)).
- Choice is not the only route into prepayment. Citizens Advice estimated **600,000 people were moved onto prepayment for debt in 2022**, up from 380,000 in 2021 ([Citizens Advice, Jan 2023](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/)). A simulation should therefore split prepayment into **elective (control need)** and **imposed (debt)** cases. The Ofgem 2023 prepayment review and the Involuntary PPM Code of Practice have more detail [unverified; not fetched].
- Half of prepayment customers said keeping topped up was a "major daily concern" ([Citizens Advice, 2018](https://www.citizensadvice.org.uk/about-us/our-work/policy/policy-research-topics/energy-policy-research-and-consultation-responses/energy-policy-research/improving-support-for-prepay-customers-self-disconnecting/)). This shows that "control" and "certainty" are tangled: prepayment users get budget control at the price of supply uncertainty.

### 2.3 Self-disconnection: prevalence and who it hits
- In 2022, **3.2m people** ran out of credit because they could not afford to top up, and **more than 2m were cut off at least monthly** ([Citizens Advice, Jan 2023](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/)).
- 19% of those cut off went without supply for 24 hours or more. In more than a third of prepayment households containing a disabled person or someone with a long-term condition, the household was cut off in the month after October 2022, which is over 470,000 households ([Citizens Advice 2023](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/)).
- Earlier, more stable-period data:
  - 16% of prepayment customers ran out of credit each year.
  - Of the roughly 140,000 households unable to afford to top up, 88% had a child or someone with a long-term health condition, 87% were on benefits, and only 9% contacted their supplier ([Citizens Advice 2018](https://www.citizensadvice.org.uk/about-us/our-work/policy/policy-research-topics/energy-policy-research-and-consultation-responses/energy-policy-research/improving-support-for-prepay-customers-self-disconnecting/)).
  - Children lived in half of all prepayment households ([Citizens Advice 2014](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/1-62-million-prepayment-energy-consumers-cuts-off-each-year/)).
- Payment method interacts with energy stress. 72% of prepayment users had difficulty affording energy, against 42% of direct debit or one-off payers (OPN, Sep–Oct 2022) ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/articles/impactofincreasedcostoflivingonadultsacrossgreatbritain/junetoseptember2022)).

### 2.4 Smart metering (the visibility layer)
- 73% of meters run by large suppliers are smart (39m), and 92% of those are in smart mode. 75% of homes have a smart electricity meter and 57% a smart gas meter (end of June 2026) ([DESNZ smart meter statistics, June 2026](https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2026/smart-meters-in-great-britain-quarterly-update-june-2026-statistical-bulletin)). The bulletin has no demographic or regional split. The Smart Energy Research Lab (SERL) panel is the route to one ([unverified access details](https://www.serl.ac.uk)).

**What this means for the simulation:** control need is highest where cash flow is weakest (renters, low income, IMD 1–2, single parents). Payment method is an observable trait in its own right and a strong signal of the hidden need. A *voluntary* prepayment customer reveals a high control need. An *involuntary* one reveals debt.

---

## 3. CERTAINTY: risk aversion and worry

### 3.1 Worry about bills (DESNZ PAT)

| Group | Very worried, Spring 2025 | Very worried, Summer 2025 |
|---|---|---|
| All | 19% (52% very or fairly) | 17% (47% very or fairly) |
| Age 16–24 | 9% | 7% |
| Age 25+ | 17–25% (peaks at 25% at 35–54) | 13–22% |
| Renters | 29% (social renters 33%) | 27% |
| Owner-occupiers | 15% | 13% |
| Finding it difficult | 57% | 49% |
| Comfortable or doing alright | 7% | 6% |

Sources: [PAT Spring 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-spring-2025-uk); [PAT Summer 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk).
- Worry peaks in **mid-life (35–54)**, where housing costs and children coincide, not among the oldest.
- Sole household decision-makers were more likely to name energy as their top bill worry: 50% against 33% of others ([PAT Spring 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-spring-2025-uk)). This is a single-adult-household signal.

**ONS OPN (Jun–Sep 2022, energy crisis peak)**, difficulty affording energy bills ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/articles/impactofincreasedcostoflivingonadultsacrossgreatbritain/junetoseptember2022)):
- Overall: 45%.
- Disability: 55% disabled, against 40% non-disabled.
- Tenure: 60% renters, 43% mortgagors, 35% outright owners.
- Ethnicity: 69% Black, 59% Asian, 44% White. The samples were small. 21% of Black adults were behind on energy bills, against 4% of White adults.
- Personal income: about 50% under £20k, against 23% at £50k or more.
- Region: 40–51%. Arrears were highest in the North East and London (9% each).

### 3.2 Fixed vs variable as revealed certainty demand
- The fixed-tariff share **collapsed from a peak of 44% (electricity) and 46% (gas) in June 2020 to 13% in Q1 2024**, during the crisis when the cap undercut fixes ([DESNZ QEP June 2024](https://assets.publishing.service.gov.uk/media/667c38215b0d63b556a4b3d2/quarterly-energy-prices-june-2024.pdf)).
- It **rebounded to 38% (electricity) and 40% (gas) by end-December 2025** ([DESNZ QEP March 2026](https://assets.publishing.service.gov.uk/media/69ca357a4a06660f085443c1/quarterly-energy-prices-march-2026.pdf)).
- Consumers misreport their tariffs. In early 2024, 50% *said* they were on a fixed tariff when the official figure was 11% ([Ofgem CIM wave 5](https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-5-january-february-2024)). A simulation should not calibrate certainty need from self-reported tariff type.
- Who holds fixes: in the 2021 Ofgem survey, those on fixed tariffs were more aware of the price cap (79% against 64% on SVT), and direct-debit payers were far more engaged than prepayment or standard-credit payers ([Ofgem Consumer Survey 2021 Engagement](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
- Fixes have historically required direct debit and online account management. So uptake of fixed tariffs skews towards the *lower*-precarity population [inference; demographic split of current fixes not published in sources fetched; check Ofgem CIM wave data tables](https://www.ofgem.gov.uk/sites/default/files/2024-09/CIM_Wave_5_Data_Tables.xlsx).

### 3.3 Dispositional risk aversion
- A YouGov survey of 4,000 UK adults (Cass and Bristol, "Quantifying Loss Aversion: Evidence from a UK Population Survey") found that **women are more risk-averse than men**, and that **the young and the old are more risk- and loss-averse than the middle-aged**. Full-time workers had the lowest aversion; retirees and the unemployed were high. Aversion fell as financial understanding rose ([Bayes Business School, Oct 2019](https://www.bayes.citystgeorges.ac.uk/news-and-events/news/2019/october/women-dislike-financial-risk-taking,-research-finds); [Bristol research portal](https://research-information.bris.ac.uk/en/publications/quantifying-loss-aversion-evidence-from-a-uk-population-survey/)). No effect sizes were in the summary.
- Understanding Society carries a 0–10 "willingness to take risks" item in some waves [unverified which waves]. The effect sizes are well established in the German SOEP: risk willingness falls with age, is lower for women, and rises with income and height ([Dohmen et al., DIW](https://www.diw.de/de/diw_01.c.767250.de/s_3706.html)). This is a non-UK analogue.

**What this means for the simulation:** certainty need = dispositional risk aversion (age U-shape, gender, financial literacy) + situational worry (renting, low income, disability, 35–54, single decision-maker). The situational part dominates in the observable data: the very-worried rate is about 8× higher among those "finding it difficult" than among the comfortable.

---

## 4. TIME: hassle and effort

### 4.1 Disengagement as a revealed time and hassle cost
Source: Ofgem Consumer Survey 2021, n = 4,037, "no engagement in past 12 months" ([Ofgem 2021 Engagement report](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf))

| Group | Disengaged |
|---|---|
| All | 37% |
| **Prepayment** | **69%** |
| **Standard credit** | **62%** |
| Direct debit | 30% |
| **Social tenant** | **54%** |
| Private tenant | 43% |
| Owner-occupier | 31% |
| C2DE | 44% (ABC1 32%) |
| Income < £16k | 44% (≥ £16k 34%) |
| Age 35–64 | 40% (16–34: 35%; 65+: 33%) |

- "Switching is a hassle" (agree): **44% of 16–34s**, 45% of those in arrears, 34% of households with children and 33% of private renters, against 28% overall ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
- Low-carbon technology adopters switched more: 35%, against 27% overall ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
- In early 2024, 18% said finding deals took a lot of effort, and only 21% were likely to switch in the next 3 months ([Ofgem CIM wave 5](https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-5-january-february-2024)).
- The CMA 2016 Energy Market Investigation found that disengagement was associated with lower income, lower education, social renting, age 65+ and no internet access [unverified; see the CMA descriptive-statistics appendix](https://assets.publishing.service.gov.uk/media/559fb603e5274a155c00004a/Appendix_7.5_Descriptive_Stats__Retail_.pdf).

### 4.2 Value of time
- DfT TAG says willingness to pay for time savings **varies with income**. Non-work values grow with income at an **elasticity of 1**. For equity reasons, though, national-average values are used in appraisal ([TAG Unit A1.3](https://assets.publishing.service.gov.uk/media/689af5abad0cbc0e27643264/tag-unit-a1-3-user-and-provider-impacts.pdf)).
- The per-hour values are in TAG Data Book table A1.3.1, and the cross-sectional income elasticity from the 2015 national value-of-time study is around 0.4–0.6 [unverified]. For the simulation, scale the hassle cost by income^ε, with ε ∈ [0.5, 1.0].

### 4.3 Time poverty
- Time use is "highly differentiated, not just by sex, but by income group." Leisure has fallen as people prioritise childcare and sleep, and calls for shorter paid hours reflect higher-income households' preferences more than lower-income ones' ([Resolution Foundation, *The time of your life*, July 2020](https://www.resolutionfoundation.org/publications/the-time-of-your-life/)).
- The ONS time-use study (autumn 2023) holds the unpaid-work-by-gender data ([ONS Time use in the UK](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/timeuseintheuk/latest)). Quantified splits were not extracted. Working mothers in dual-earner households with young children are the most time-poor group [unverified].

**What this means for the simulation:** time need is **two-humped**:
- **Hump A (capability or trust hassle):** prepayment, social renters, C2DE, the digitally excluded. The cost is cognitive and procedural.
- **Hump B (opportunity-cost hassle):** high-income, dual-earner households with children. The cost is foregone time.

Both disengage, but they respond to different interventions: simplification and defaults for A, automation and delegation for B.

---

## 5. CARBON: environmental concern and its link to low-carbon technology adoption

### 5.1 Concern (DESNZ PAT Winter 2025)
Source: [PAT Net Zero and climate change, Winter 2025](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk)
- 77% concerned and 33% very concerned, down from 85% and 44% in Autumn 2021.
- **Education is the strongest gradient: very concerned 45% with a degree, 27% with no qualifications.** Support for government climate action: 80% with a degree, against 52% with none.
- Gender: 81% of women concerned, against 73% of men.
- Region (very concerned): **London 40%**, South West 37%, East of England and Northern Ireland 36%, **West Midlands and Scotland 24%**. "Not concerned" is highest in the North East and West Midlands (27%).
- Age: no clear age differences in concern. Net Zero *knowledge* is higher at 55+ (55%) than at 16–24 (39%).
- Income and tenure splits were not published on this page.

### 5.2 Low-carbon technology ownership: who actually has it
**EVs**
- BEVs are 4% and PHEVs 2% of cars owned in England (NTS 2024). 64% of respondents park overnight on private property (excluding garages). Car-less households: about 40% in the bottom income quintile, against 14% in the top ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips)).
- BEV penetration by deprivation is **3.31% in IMD decile 10 against 1.0% in decile 1 (LSOA level, to Q2 2025)**. Recent growth is more even (+0.86pp against +0.6pp), so the gap is narrowing (New Automotive and char.gy) ([EV Infrastructure News, Mar 2026](https://www.evinfrastructurenews.com/emobility/uk-ev-adoption-wealth-gap-beginning-to-close-say-new-automotive-char-gy)).
- A household-level NTS model (Yiu et al., 2025) found income, on-street overnight parking (negative), having a mortgage, and population density to be significant. It concludes that charging in the north is a constraint ([EDRC](https://www.edrc.ac.uk/publications/systematic-study-of-battery-electric-vehicle-ownership-in-england/)).
- Plug-in registrations by local authority are in DfT vehicle licensing table VEH0142 [unverified table code](https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables).

**Heat pumps and PV**
- Retrofit heat pumps: 48,857 installed in 2024 and about 9% more in 2025. Installs in H1 2026 split **South East 18%, South West 14%, East 13%**, with London at 1,065 and Northern Ireland at 36 ([DESNZ heat pump deployment, June 2026](https://www.gov.uk/government/statistics/heat-pump-deployment-statistics-june-2026/heat-pump-deployment-statistics-june-2026-summary)).
- MCS certified 267,032 solar PV installations in 2025, a record, with a cumulative total near 2m. It also certified more than 60,000 heat pumps and more than 40,000 batteries ([MCS, *The 2026 low carbon landscape*](https://mcscertified.com/the-2026-low-carbon-landscape/)).
  - More than 1 in 10 Welsh households have an MCS installation, the highest of any nation.
  - The top local authorities by volume are Cornwall, Somerset and North Yorkshire. In Wales the leaders by share are Anglesey, Ceredigion and Gwynedd; in Scotland, Highland and Aberdeenshire lead by volume.
  - Detached homes are just over a third of installs, and new-builds 28%.
  - The MCS page contains an internal inconsistency in its totals ([MCS](https://mcscertified.com/the-2026-low-carbon-landscape/)).
- Census 2021, England and Wales: **74% gas-only central heating**, about 9% electric-only, and under 1% renewables-only (98,730 households). 18 local authorities have 50% or less mains gas, concentrated in central London (heat networks and flats) and the rural west and east: Cornwall at 47%, plus Ceredigion, Powys and rural Norfolk and Suffolk. Renewable heating is highly clustered at LSOA level ([Nesta analysis](https://www.nesta.org.uk/blog/what-does-the-latest-census-data-reveal-about-how-homes-are-heated-across-england-and-wales/); [ONS TS046](https://www.ons.gov.uk/datasets/TS046)).

### 5.3 Concern vs adoption: a mismatch
- Attitudinal concern peaks in **London**, but heat pump and PV adoption peaks in the **rural South West, East and Wales**. London has the lowest uptake because of flats and renting ([PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk) vs [DESNZ HP stats](https://www.gov.uk/government/statistics/heat-pump-deployment-statistics-june-2026/heat-pump-deployment-statistics-june-2026-summary)).
- Low-carbon technology is gated by **capital, tenure, dwelling form and off-gas status**, not by concern. Off-gas rural owners have an economic reason (oil or LPG displacement) on top of any carbon motive.
- Low-carbon technology adopters are more engaged switchers ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)). Adoption is therefore positively correlated with engagement, which is the inverse of time or hassle need.
- Green tariffs: in 2021, 27% of respondents said they were on one, and understanding of what "green tariff" means was poor ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)). Self-reported green tariff status is not a reliable marker of carbon need.

**What this means for the simulation:** draw carbon *concern* from education, gender and region, with income as a weaker positive effect [unverified magnitude]. Draw low-carbon technology *ownership* separately from wealth, tenure, dwelling, parking, off-gas status and rurality. Treat ownership as only weakly informative about concern, with conditional lift [unverified magnitude].

---

## 6. COMFORT/HEALTH floor

### 6.1 Fuel poverty (England, LILEE)
- Headline: **9.9% (2.47m households) in 2024, final**, with an average gap of £381. The projection for 2025 is **9.4% (2.36m)** ([DESNZ 2026 main report](https://assets.publishing.service.gov.uk/media/69c3af123ed0546101e0dc3e/Main_Report__2026_Fuel_Poverty_Statistics_Publication_.pdf); [2026 factsheet](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf)).
- The 2025 report gave 2023 as final at 11.4% and 2024 projected at 11.0%. The 2026 report revised 2024 to 9.9% final ([2025 report](https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf)).

**2025 projections by group** ([2026 factsheet](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf)):
- Tenure: private rented 17.2%, social 12.0%, owner-occupied 6.5%.
- Household type: single parents 18.1%, the highest.
- Region: highest West Midlands 10.9%, lowest South East 7.8%. The South West has the largest average gap (£558) and London the smallest (£231).
- Unemployed household reference person: about 3× the national rate.
- Low-income households pay a median 14.9% of after-housing-cost income for required energy, against 6.8% for all households.

**Detailed breakdowns from the 2025 report.** The page labels these "2024" breakdowns ([2025 report](https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf)) [unverified: check whether these are 2023 final or 2024 projected]:

| Attribute | Fuel poverty rate |
|---|---|
| Electricity prepayment | **22.3%** |
| Standard credit | 18.5% |
| Direct debit | 8.8% |
| Electric main heating | **20.7%** (gas 10.0%) |
| Off gas grid | **17.0%** (on grid 10.1%) |
| Private rented | 21.5% |
| Owner with mortgage | 6.6% |
| Owned outright | 8.3% |
| Converted flat | 18.8% (detached 7.3%) |
| Single parents | **24.7%** (couples under 60, no children: 5.2%) |
| Oldest member aged 16–24 | 18.9% |
| Unemployed household reference person | **30.1%** (full-time work 6.8%; retired 11.0%) |
| Black household reference person | 14.9% (White 10.7%) |
| Rural | 12.3% (urban 11.0%) |
| West Midlands | 16.4% (East 9.0%) |
| Benefit recipients | more than 3.5× non-recipients |

- Low-income households in FPEER band C or better: 58.0% in 2023 ([2025 report](https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf)). Band F–G homes have a fuel poverty gap more than 5× that of D–E homes ([2026 factsheet](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf)).
- Sub-regional (LSOA) fuel poverty estimates for 2024 are published openly ([DESNZ sub-regional 2026](https://www.gov.uk/government/statistics/sub-regional-fuel-poverty-report-2026-2024-data/sub-regional-fuel-poverty-in-england-2026-report-2024-data-accessible-webpage)). This is the most direct geographic prior for comfort risk.
- Scotland, Wales and Northern Ireland use different definitions. Scotland's rate is materially higher (around a third of households under the Scottish definition) [unverified].

### 6.2 Cold-home health risk
- 9.6m UK households (about a third) live in poorly insulated homes on incomes below the minimum for an acceptable standard of living ([Institute of Health Equity, Feb 2024](https://www.instituteofhealthequity.org/in-the-news/press-releases-and-briefings-/left-out-in-the-cold-the-hidden-impact-of-cold-homes)).
- Prolonged cold exposure doubles the risk of new mental-health conditions in adults. 28% of children in cold homes are at risk of multiple mental-health symptoms. At least 1 in 5 people out of work through ill health live in cold homes ([IHE](https://www.instituteofhealthequity.org/in-the-news/press-releases-and-briefings-/left-out-in-the-cold-the-hidden-impact-of-cold-homes)).
- At-risk groups: pre-existing conditions, older people, young children, low income and people of colour ([IHE](https://www.instituteofhealthequity.org/in-the-news/press-releases-and-briefings-/left-out-in-the-cold-the-hidden-impact-of-cold-homes)).
- Fixing the coldest homes would save the NHS about £540m a year (BRE) ([Construction Digital](https://constructiondigital.com/articles/tackling-cold-homes-would-save-the-nhs-540m-per-year)).

### 6.3 Priority Services Register
I could not confirm a current PSR headcount from a fetched page. The commonly cited figure is about 8–9m+ households across electricity networks [unverified]. Ofgem's vulnerability reporting is the authoritative source ([Ofgem PSR press release](https://www.ofgem.gov.uk/press-release/more-customers-vulnerable-situations-receive-help-under-priority-services-register)). Eligibility includes pensionable age, disability, chronic illness, children under 5, and medical dependency on electricity ([Wikipedia summary of Ofgem/Ofwat criteria](https://en.wikipedia.org/wiki/Priority_Services_Register)).

**What this means for the simulation:** the comfort floor binds where *low income × poor efficiency × high-need occupant* coincide:
- low income: single parents, the unemployed, benefit recipients;
- poor efficiency: private renters, converted flats, electric or off-gas heating, EPC E–G;
- high-need occupant: disability, under-5s, 75+.

Self-disconnection data show the floor is actively breached for about 2m people a month at crisis peak ([Citizens Advice 2023](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/)).

---

## 7. Geodemographics

- **2021/22 Output Area Classification (OAC):** UK-wide, built by GeoDS with ONS, and openly downloadable ([GeoDS OAC 2021](https://data.geods.ac.uk/dataset/output-area-classification-2021); [ONS methodology](https://www.ons.gov.uk/methodology/geography/geographicalproducts/areaclassifications/2021and2022residentialbasedareaclassifications)). LSOA and MSOA versions also exist ([LSOAC](https://data.geods.ac.uk/dataset/lsoac)). The ONS page lists the **local-authority** supergroups: Services and industrial legacy; Densely populated urban centres; Education and heritage centres; English metropolitan living; Coastal and countryside living; Commuter living ([ONS](https://www.ons.gov.uk/methodology/geography/geographicalproducts/areaclassifications/2021and2022residentialbasedareaclassifications)). The 8 OA-level supergroup names were not on the fetched page [unverified].
- **Acorn (CACI) and Mosaic (Experian)** are licensed, household or postcode-level segmentations with energy and financial attitudes appended [unverified product detail]. They are widely used by suppliers, but cost money.
- A recommended open alternative: join OAC at OA level to IMD (deprivation), the sub-regional fuel poverty LSOA file, Census TS046 heating, EPC open data and DfT plug-in vehicle counts by local authority. Together these reproduce most of what Acorn offers for energy.

---

## 8. Where the needs pull together and where they pull apart

**Pull together (the precarity cluster).** Low cash buffer → high control need → high certainty need → binding comfort floor.
- The evidence chain: renters show 47% low resilience ([FCA 2022](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience)), 23% prepayment ([PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk)), 27–29% very worried ([PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-spring-2025-uk)) and 17–21% private-rented fuel poverty ([DESNZ](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf)).
- Cost sensitivity is also high here, *but* the ability to act on it through switching is low, at 54–69% disengaged ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)). Cost need and time or hassle need are both high in this cluster.

**Pull apart.**
1. **Certainty need against certainty access.** The most worried are the least likely to be on fixed tariffs, which require direct debit and engagement (inference from [PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk) and [Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
2. **Control against cash flow within prepayment.** Prepayment gives control but makes the comfort floor fragile through self-disconnection ([Citizens Advice 2023](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/)).
3. **Carbon against time (affluent).** Degree holders and high earners have high carbon concern ([PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk)) and a high value of time ([TAG](https://assets.publishing.service.gov.uk/media/689af5abad0cbc0e27643264/tag-unit-a1-3-user-and-provider-impacts.pdf)). They will pay for carbon outcomes but not spend effort on them, so they prefer automated propositions. 45% would let a supplier control appliances ([PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk)) [link to affluent segment unverified].
4. **Carbon concern against carbon ability.** Concern is high in London and among young graduate renters, but ownership is low there because of tenure and flats ([MCS](https://mcscertified.com/the-2026-low-carbon-landscape/), [Nesta](https://www.nesta.org.uk/blog/what-does-the-latest-census-data-reveal-about-how-homes-are-heated-across-england-and-wales/)).
5. **Comfort against cost among older owners.** Outright owners are cash-rich in wealth terms (median financial wealth £55k, [ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022)), yet retirees still have an 11% fuel poverty rate. Some under-heat to save money, so a health floor needs to be enforced even where cash flow is fine [inference].
6. **Off-gas rural households.** Fuel poverty is higher (17%) and the fuel cost burden higher, but heat pump and PV adoption is highest here ([DESNZ](https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf), [MCS](https://mcscertified.com/the-2026-low-carbon-landscape/)). In this group, carbon and cost align.

---

## 9. Deliverable 1: needs × correlates matrix

Direction: ↑ means the need rises with the attribute. Magnitudes are approximate ratios or percentage-point gaps from the cited source.

| Need | Correlate 1 | Correlate 2 | Correlate 3 | Correlate 4 | Correlate 5 |
|---|---|---|---|---|---|
| **CASH FLOW** | Renting ↑: 47% vs 17% (mortgagors) low resilience, ~2.8× [FCA22](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience) | Income <£15k ↑: 50% vs 24% all, ~2× [FCA22](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience) | IMD decile 1 ↑: 42% LFR; FD 20% vs 3%, ~7× [FCA22](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience) | Unemployed or gig ↑: 48% / 37% [FCA22](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience); low pay → >80% volatile [RF](https://www.resolutionfoundation.org/?p=17788) | Region NE ↑ (31%) vs SE (19%), ~1.6× [FCA22](https://fca.org.uk/data/financial-lives-2022-early-survey-insights-vulnerability-financial-resilience); age 25–34 financial wealth £1.3k vs £32k at 65–74 [ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022) |
| **CONTROL** (prepayment as proxy) | Social renting ↑: 27% PPM vs 2% owners, ~13× [PAT S25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk) | Income <£15k ↑: 15% vs 2% (≥£45k), ~7× [PAT S25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk) | Financial difficulty ↑: 17% vs 5% [PAT S25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk) | Age 65+ ↓: 4% vs 8–14% under 55 [PAT S25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-summer-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-summer-2025-uk) | Region: NI, NE, Scotland ↑ [unverified; QEP 2.4.2](https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-price-stastics) |
| **CERTAINTY** (worry) | Renting ↑: very worried 27–29% vs 13–15%, ~2× [PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-spring-2025-uk) | Financial difficulty ↑: 49–57% vs 6–7%, ~8× [PAT](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-spring-2025-uk) | Age: inverted U, peak 35–54 (25%), low 16–24 (9%) [PAT Sp25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-spring-2025/desnz-public-attitudes-tracker-energy-bills-and-tariffs-spring-2025-uk) | Disability ↑: 55% vs 40% energy difficulty [ONS OPN](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/articles/impactofincreasedcostoflivingonadultsacrossgreatbritain/junetoseptember2022) | Gender (female ↑ risk aversion), no magnitude [Bayes](https://www.bayes.citystgeorges.ac.uk/news-and-events/news/2019/october/women-dislike-financial-risk-taking,-research-finds) |
| **TIME / HASSLE** | Prepayment / standard credit ↑: 69% / 62% disengaged vs 30% DD [Ofgem21](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf) | Social tenant ↑: 54% vs 31% owners [Ofgem21](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf) | Age 16–34 ↑ "hassle": 44% vs 28% [Ofgem21](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf) | Children in household ↑: 34% hassle [Ofgem21](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf) | Income ↑ value of time, elasticity ≈1 [TAG A1.3](https://assets.publishing.service.gov.uk/media/689af5abad0cbc0e27643264/tag-unit-a1-3-user-and-provider-impacts.pdf) |
| **CARBON** | Degree ↑: very concerned 45% vs 27%, ~1.7× [PAT W25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk) | Region: London 40% vs W Mids / Scotland 24% [PAT W25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk) | Female ↑: 81% vs 73% [PAT W25](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk) | Ownership: IMD 10 vs 1 BEV 3.3% vs 1.0%, ~3× [EVIN](https://www.evinfrastructurenews.com/emobility/uk-ev-adoption-wealth-gap-beginning-to-close-say-new-automotive-char-gy) | HP and PV: SE/SW/E and rural Wales ↑, London ↓ [DESNZ HP](https://www.gov.uk/government/statistics/heat-pump-deployment-statistics-june-2026/heat-pump-deployment-statistics-june-2026-summary), [MCS](https://mcscertified.com/the-2026-low-carbon-landscape/) |
| **COMFORT / HEALTH floor** | Unemployed household reference person ↑: 30% FP vs 6.8% full-time [DESNZ25](https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf) | Single parent ↑: 18–25% vs 5% [DESNZ](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf) | Private rented ↑: 17–21% vs 6.5% owners [DESNZ](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf) | Prepayment ↑ 22% vs DD 9%; electric heat 21% vs gas 10%; off-gas 17% [DESNZ25](https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf) | Disability or long-term condition ↑: more than a third cut off at least once in the month after October 2022 [Citizens Advice](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/) |

*Cost (total paid)* is not one of the six in the matrix but runs through it. Cost sensitivity, measured as energy share of AHC income, is 14.9% for low-income households against 6.8% for all ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/69c3b0ec380a2a73a7cf9e35/Factsheet__2026_Fuel_Poverty_Statistics_Publication_.pdf)), roughly 2.2×.

---

## 10. Deliverable 2: need mix by household type

Scale: H = high, M = medium, L = low. "S" means anchored in a source cited above. "A" means assumption or inference.

| # | Household type | Cost | Cash flow | Control | Certainty | Time / hassle | Carbon | Comfort floor | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Single parent, social rent, North / Midlands, UC, prepayment, flat** | H (S) | **H** (S: renters 47% LFR, UC) | **H** (S: 27% PPM in social rent) | **H** (S: 33% very worried) | H, capability type (S: 54–69% disengaged) | L–M (A) | **H, binding** (S: 18–25% FP; children; self-disconnection) | Every precarity need fires at once; the comfort floor is actively breached |
| 2 | **Young private renters, 25–34, sharers or couple, urban (London or cities), graduate** | M | M–H (S: 25–34 financial wealth £1.3k) | M (S: PR 15% PPM) | M (A) | H (S: 16–34 "hassle" 44%) | **H** concern (S: degree, London) but **L** ability (S: tenure, flats) | M (S: PR 17–21% FP; converted flats 19%) | Concern without the means to act; landlord-gated |
| 3 | **Dual-income family with children, mortgaged semi or detached, South East commuter belt** | M | L–M (S: mortgagors 17% LFR) | L–M (A) | M (S: worry peaks 35–54) | **H, opportunity-cost type** (S: children 34% hassle; TAG income elasticity) | M–H (A; S: SE heat pump share 18%) | L (S: couples with children low FP) | Prime market for automated, bundled EV and smart tariffs |
| 4 | **Affluent early adopter: owner, detached, EV + PV (+ heat pump), degree, SW / SE / East** | L | L | L–M (wants data visibility, A) | L–M | M (engaged; S: low-carbon adopters switch 35%) | **H** (S: degree; IMD 10 BEV 3.3%) | L | Values optimisation and automation; low price sensitivity (A) |
| 5 | **Older outright owners, 70+, off-gas rural (oil / LPG), Wales / SW / East Anglia** | M | L (S: outright-owner financial wealth £55k) | M (familiar billing, standard credit; A) | **H** dispositional (S: older risk averse) | M (S: 65+ engaged but switch tariff, not supplier) | L–M (S: no age gradient in concern; A) | **M–H** (S: off-gas 17% FP, rural 12%; age health risk) | Income-poor but asset-rich; heat pump retrofit candidates; comfort risk is health-driven |
| 6 | **Pensioner living alone, social or private rent, city, PSR, possibly disabled** | H | M–H (A) | M–H (A) | H (S: sole decision-maker 50% top worry) | H capability (A; digital exclusion) | L (A) | **H** (S: disability, cold-home health risk; PSR) | Comfort floor and PSR handling dominate |
| 7 | **Low-paid volatile earners, couple, private rent, terraced, Midlands / North, weekly or four-weekly pay** | H | **H** (S: >80% volatile pay among low earners) | H (A: smoothing preference) | H (S: renters very worried) | M–H (A) | L (A; S: W Mids concern 24%) | M–H (S: W Mids highest FP 10.9–16.4%) | Income-timing mismatch is the key cash-flow driver |
| 8 | **Mid-life professional couple, no children, owner, flat or terrace in a city** | L–M | L | L | L–M | **H** opportunity cost (A) | M–H (S: degree) | L (S: couples under 60, no children, 5% FP) | Will pay for low-effort green; low comfort risk |

---

## 11. Deliverable 3: datasets for drawing hidden traits per household

Each entry gives the conditioning attributes the simulation already holds, the traits it lets you draw, and the access route.

| Dataset | Lets you draw | Conditioning variables available | Access |
|---|---|---|---|
| **FCA Financial Lives Survey 2022/2024**, published data tables ([FCA FLS 2024](https://www.fca.org.uk/financial-lives/financial-lives-2024-survey)) | Low resilience, savings buffer, missed bills, overdraft, risk / vulnerability | Age, gender, ethnicity, region, tenure, income, employment, IMD (aggregate tables) | **Open** (aggregate tables); microdata via UKDS [unverified licence] |
| **ONS Wealth and Assets Survey** ([ONS bulletin](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022)) | Financial wealth / liquidity buffer distribution | Region, age, tenure, economic activity, household type | **Open** (tables); microdata **UKDS safeguarded / special licence** [unverified SN] |
| **Understanding Society (UKHLS)** ([UKDS](https://ukdataservice.ac.uk/), [Understanding Society](https://www.understandingsociety.ac.uk/)) | Risk willingness (0–10) [unverified waves], financial strain, environmental attitudes and behaviours, income volatility (panel), fuel arrears | Very rich: region, tenure, age, income, household composition, health, employment, dwelling | **UKDS safeguarded (EUL)**; geographies at LSOA level under special licence / secure |
| **DESNZ Public Attitudes Tracker** ([PAT series](https://www.gov.uk/government/statistics/desnz-public-attitudes-tracker-winter-2025/desnz-public-attitudes-tracker-net-zero-and-climate-change-winter-2025-uk)) | Bill worry, payment method, climate concern, flexibility openness, smart appliance attitudes | Age, tenure, income, education, region, financial situation | **Open** (tables); microdata via UKDS [unverified] |
| **ONS Opinions and Lifestyle Survey** ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/articles/impactofincreasedcostoflivingonadultsacrossgreatbritain/junetoseptember2022)) | Difficulty paying energy, arrears, cutting back | Age, disability, tenure, income, region, ethnicity, IMD | **Open** (tables); microdata **UKDS secure** [unverified] |
| **Ofgem Consumer Survey / Consumer Impacts of Market Conditions** ([CIM wave 5 data tables](https://www.ofgem.gov.uk/sites/default/files/2024-09/CIM_Wave_5_Data_Tables.xlsx); [2021 Engagement](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)) | Engagement / hassle, switching intent, tariff knowledge, arrears, rationing | Age, SEG, tenure, income, payment method, low-carbon tech, PSR, region | **Open** (cross-tabs XLSX) |
| **English Housing Survey** + **fuel poverty detailed tables** ([DESNZ fuel poverty series](https://www.gov.uk/government/organisations/department-of-energy-climate-change/series/fuel-poverty-statistics)) | Fuel poverty / comfort-floor probability, FPEER, under-occupancy, heating type | Tenure, household type, age, employment, region, dwelling, EPC, fuel, payment method, rurality, ethnicity | **Open** (tables); EHS microdata **UKDS safeguarded / special licence** |
| **Sub-regional fuel poverty (LSOA)** ([DESNZ 2026](https://www.gov.uk/government/statistics/sub-regional-fuel-poverty-report-2026-2024-data/sub-regional-fuel-poverty-in-england-2026-report-2024-data-accessible-webpage)) | Area-level comfort-risk prior | LSOA → region, IMD, OAC | **Open** |
| **DESNZ QEP payment method by region** ([tables 2.4.2 / 2.5.2](https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-price-stastics)) | Regional prepayment / DD / credit priors; fixed vs SVT share over time | Region (PES area), fuel, quarter | **Open** |
| **Census 2021 TS046 (heating), tenure, accommodation, car availability** ([ONS TS046](https://www.ons.gov.uk/datasets/TS046)) | Off-gas / heating type, tenure-dwelling joint distributions | OA / LSOA → everything geographic | **Open** |
| **EPC register** ([EPC open data](https://epc.opendatacommunities.org/)) [not fetched] | Dwelling efficiency, heating, PV, heat pump flags by address | UPRN / postcode, tenure (self-declared), property type | **Open** (registration); Scotland separately |
| **MCS installations** ([MCS](https://mcscertified.com/the-2026-low-carbon-landscape/)); **DESNZ heat pump deployment** ([DESNZ](https://www.gov.uk/government/statistics/heat-pump-deployment-statistics-june-2026/heat-pump-deployment-statistics-june-2026-summary)) | PV, heat pump, battery adoption priors by LA / region, property type | LA, region, property type | **Open** (dashboard / tables); postcode-level MCS data **licensed** [unverified] |
| **DfT vehicle licensing statistics (plug-in by LA / LSOA)** ([DfT VLS](https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables)) [table codes unverified] | EV ownership prior by area | LA / LSOA → IMD, OAC | **Open** |
| **National Travel Survey** ([NTS 2024](https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-household-car-availability-and-trends-in-car-trips); [EDRC model](https://www.edrc.ac.uk/publications/systematic-study-of-battery-electric-vehicle-ownership-in-england/)) | EV ownership | Income, parking, tenure / mortgage, density, region | **Open** (tables); special licence via UKDS |
| **DWP Stat-Xplore (UC, by LA, household type)** ([DWP UC](https://www.gov.uk/government/statistics/universal-credit-quarterly-statistics-29-april-2013-to-14-may-2026/universal-credit-quarterly-statistics-29-april-2013-to-14-may-2026)) | UC receipt prior → income timing, cash flow | LA, household type, employment, children | **Open** (Stat-Xplore registration) |
| **Family Resources Survey / HBAI; Living Costs and Food Survey** ([UKDS](https://ukdataservice.ac.uk/)) | Income distributions, benefit receipt, pay frequency [unverified], energy spend, savings bands | Region, tenure, household type, age, disability | **UKDS safeguarded (EUL)** |
| **ONS Time Use Survey** ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/timeuseintheuk/latest)) | Time poverty / unpaid work load | Age, sex, employment, children | **Open** (tables); microdata UKDS |
| **DfT TAG Data Book A1.3.1** ([TAG A1.3](https://assets.publishing.service.gov.uk/media/689af5abad0cbc0e27643264/tag-unit-a1-3-user-and-provider-impacts.pdf)) | £/hour value of non-work time; income elasticity | Income (by elasticity) | **Open** |
| **Smart Energy Research Lab (SERL)** ([SERL](https://www.serl.ac.uk)) [unverified] | Half-hourly consumption with linked survey (attitudes, demographics) | EPC, tenure, income band, region | **UKDS secure / controlled** [unverified] |
| **2021 Output Area Classification** ([GeoDS](https://data.geods.ac.uk/dataset/output-area-classification-2021)) | Area-type stratifier for all of the above | OA / LSOA | **Open** |
| **IMD 2019 / 2025** (England; devolved equivalents) [not fetched] | Deprivation decile | LSOA | **Open** |
| **CACI Acorn / Experian Mosaic** | Household-level segment with energy and financial attitudes | Postcode / household | **Licensed (commercial)** |

**Suggested drawing approach** (assumption; how it fits the simulation is for the simulation owner to decide):
1. Sample observables (region, tenure, income, age, household type, dwelling, EPC, low-carbon tech) from Census, EHS and EPC.
2. Draw a latent **precarity** score from an FCA- or UKHLS-style ordered model on tenure × income × age × IMD × employment.
3. Derive cash flow, control, certainty-worry and comfort-floor from the precarity score plus their own specific shifts (disability, children, payment method).
4. Draw **carbon** independently on education × gender × region, then condition low-carbon tech ownership on wealth × dwelling × off-gas status, with only a modest lift from carbon concern [unverified magnitude].
5. Draw **time** as a mixture: a capability component (from precarity, age 16–34, digital exclusion) and an opportunity-cost component scaled by income at elasticity 0.5–1.0.

---

## 12. Gaps and caveats

- **Regional prepayment shares** (QEP 2.4.2) could not be retrieved here because the spreadsheet host was blocked. Fetch them directly.
- **FCA 2024 segment values** were not extractable. The 2022 values are used instead.
- **The year label on the fuel poverty breakdowns** in the 2025 report needs checking: 2023 final or 2024 projected. The 2026 report also revised 2024 from 11.0% to 9.9%.
- **Risk aversion** has no fetched UK effect sizes. UKHLS microdata is the route.
- **Fixed-tariff holders by demographic** are not published in the sources fetched. Self-reports are unreliable: 50% said fixed against 11% actual ([Ofgem CIM5](https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-5-january-february-2024)).
- **PSR headcount**, the **pay-frequency share**, the **CMA 2016 engagement demographics** and the **TAG cross-sectional elasticity** are all [unverified].
- **Self-disconnection figures** come mainly from crisis-era (2022) Citizens Advice surveys and are probably above steady state.