**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Customer needs in segmentation, conjoint and behavioural research: energy, financial services and telecoms (2026-10-30)

**Type:** EVIDENCE, through the advisor channel, for `DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`. The director's words, from chat on Fri 30 Oct, 16:22 GMT: "To what degree are the individual dimensions covered by these topics and are there bodies of research available on them individually as topics in energy or other sectors such as financial services or telecoms?"

This pack is from an advisor research pass and is sourced from the web. Items tagged [unverified] are calibration assumptions, not evidence. Verify them with your own network access while drafting.

---

# Six-Need Household Energy Framework: Evidence Review

*Scope: GB energy evidence first, then UK financial services and telecoms. Every claim carries a URL. Claims I could not check against a primary or reputable source in this pass are tagged [unverified]. I ran about 25 searches and spent the rest of the budget on WebFetch of primary documents.*

---

## 1. Executive summary

- **The framework is broadly supported.** It most needs refining in three places: CONTROL, TRUST and CAPABILITY.
  - Four of the six needs show up again and again across all four bodies of research: COST, CASH FLOW, TIME/hassle and a CERTAINTY/CONTROL cluster.
  - CARBON is well covered in stated-preference work but weakly in revealed behaviour.
  - The literature mostly treats COMFORT/HEALTH as a vulnerability constraint rather than a preference. That fits the framework's choice to model it as a "floor".
- **Price dominates trade-offs, as expected.**
  - In a 2025 UK discrete-choice experiment (DCE), price took 59.5% of attribute importance for UK consumers ([Lim, Fell & Shipworth 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)).
  - In the 2026 DESNZ heat pump DCE (n=6,086), upfront cost weighed 7 to 16 times more than running cost. The implied discount rate was about 10–15% ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)).
  - That gap between upfront and running cost is the clearest quantitative evidence that **CASH FLOW is distinct from COST**.
- **CONTROL has two meanings in the literature, and the framework blends them.**
  - *Spend control* means budgeting, visibility and avoiding debt. This is the prepayment, pay-as-you-go mobile and buy-now-pay-later evidence.
  - *Agency over devices and automation* is the demand-side response (DSR) evidence. It interacts with trust, privacy and locus of control. People who feel *least* in control were *more* willing to accept direct load control ([Fell et al. 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)).
- **The strongest dimensions the framework is missing:**
  1. **Trust.** It is a segmentation input, it moderates DSR acceptance, and it is a reason for inertia.
  2. **Self-efficacy or capability.** For example, Ofgem's "Anxious Avoiders" segment, and the FCA's finding that 22% of adults lack confidence managing money.
  3. **Relationship and loyalty.** The CMA lists it as an inertia driver.
  4. **Privacy.**
  5. **Fairness and pro-social preferences.**
  6. **Simplicity as cognitive load.** This is separate from clock time.
- **Segmentations built on attitudes describe engagement differences well but predict behaviour poorly.**
  - The intention–action gap is large. Median stated willingness to take a time-of-use (ToU) tariff was 36%, against a median commercial sign-up of 7% ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
  - Targeting on *behavioural state* works much better. In Ofgem's collective-switch randomised controlled trials (RCTs), customers who had been on a default tariff for 3+ years switched at 24–30% when treated, against 3–4.5% for controls ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)).

---

## 2. How energy segmentations are actually built

### 2.1 The GB catalogue

The most useful single source is the ClimateXChange review by CAG Consultants and the Centre for Sustainable Energy. It covers eleven segmentation approaches used in GB energy, drawing on a desk review, 15 stakeholder interviews and a workshop ([Maiden, Jones & Bridgeman 2020](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)). It sorts them by what each is built on:

| Basis | Example | Segments | Source |
|---|---|---|---|
| Socio-demographic and physical | Ofgem household archetypes (CSE, 2014; DIMPSA) | 12 archetypes, split on/off gas; discontinued | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |
| Engagement (behavioural) | Ofgem Index of Consumer Engagement (TNS BMRB, 2014) | Unplugged / On standby / Tuned in / Switched on | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |
| Attitudinal | Ofgem Consumer Engagement Survey segmentation (GfK, 2017) | 6 segments (below) | [Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf) |
| Attitudinal plus geodemographic fusion | Smart Energy GB (2018): attitudes linked to ACORN, census and TGI | Follow the crowd; Enough on my plate; Good intentions; On top of it; Best for me; Money worries; Set in my ways | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |
| Attitudinal plus behavioural | Scottish Government Climate Change Behaviours (Experian, 2012) | 9 segments scored on 10 behaviours | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |
| Financial situation and behaviour | FCA Consumer Spotlight (2011/12) | 10 segments; discontinued | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |
| Geodemographic | ACORN (6/18/62); MOSAIC (14/57); ONS Output Area Classification (8/15/24); Cameo | Area-level | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |
| Supplier proprietary | Survey plus commercial plus customer data | Not public; one supplier could assign 70–80% of customers | [ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf) |

The Smart Energy GB segment names read almost directly as framework dimensions:
- "Money worries" maps to CASH FLOW.
- "Enough on my plate" maps to TIME or cognitive bandwidth.
- "Good intentions" maps to CARBON with an intention–action gap.
- "On top of it" maps to CONTROL.
- "Set in my ways" maps to inertia.

I could not obtain segment shares or the underlying factor structure [unverified beyond the names listed in ClimateXChange].

### 2.2 The Ofgem 2017 attitudinal segmentation in detail

**How it was built** ([Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)):
- 4,001 face-to-face interviews in homes, using a quota sample rather than a probability sample.
- Attitude items came from earlier Ofgem surveys and the BIS Consumer Empowerment Segmentation.
- Factor analysis reduced the items, then k-means clustering produced the segments.
- **Behaviours were deliberately excluded as inputs.** Engagement was then used to validate the segments.

| Segment | Share | Engaged in last 12 months | Defining attitudes | Framework mapping |
|---|---|---|---|---|
| Happy Shoppers | 20% | 63% | Enjoy shopping around, trusting, focused on saving | COST, low TIME cost |
| Savvy Searchers | 13% | 63% | Confident across markets, sceptical of comparison sites | COST plus *distrust of intermediaries* |
| Market Sceptics | 14% | 40% | Very low trust in suppliers; 20% on prepayment; 63% keep up with bills | **TRUST** (missing), CONTROL |
| Hassle Haters | 20% | 33% | Confident, trusting, but put off by time, hassle and risk | TIME, CERTAINTY |
| Anxious Avoiders | 13% | 28% | Low self-efficacy; 32% DE; 27% social housing | **CAPABILITY** (missing) |
| Contented Conformers | 20% | 22% | Status quo, trusting, nervous of change; 21% disabled | Inertia, **relationship** (missing) |

**Ofgem 2021.** Ofgem kept the six segments in its 2021 survey (n=4,037, online, Ipsos). Happy Shoppers and Savvy Searchers were over-represented among engaged consumers. Market Sceptics, Anxious Avoiders and Contented Conformers were over-represented among disengaged consumers ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).

**Implication.** Two of the six empirically derived axes have no home in the framework:
- trust, which separates Market Sceptics from Happy Shoppers;
- self-efficacy, which defines Anxious Avoiders.

TIME/hassle, by contrast, defines a fifth of the population.

### 2.3 How well does segment membership predict behaviour?

- **Descriptive separation is real but modest.** Engagement runs from 63% in the top segments down to 22%. The review authors note that this describes segments rather than validating their predictive power ([ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)).
- **Socio-economic status is a weak proxy for engagement.** One interviewee said many low-income prepayment households are highly engaged ([ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)).
- **Stated intentions overstate uptake.** Across 27 studies, median survey willingness to take ToU was 36%, median trial recruitment 12% and median commercial sign-up 7% ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)). Fell et al. cite meta-analytic evidence that intention explains about 28% of the variance in behaviour ([Fell et al. 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)).
- **Household characteristics explain little of the variation in load.**
  - In the Irish CER smart-meter trial (about 3,488 homes), household characteristics explained a marginal R² of 0–20% across load-profile indicators.
  - Going the other way, load profiles classified employment status correctly about 59–70% of the time ([Anderson et al. 2016](https://eprints.soton.ac.uk/396943/1/Anderson_et_al_Predicting_Household_Characterstics_CEUS_Accepted.pdf)).
  - The same review found that usage can vary up to twenty-fold between identical homes depending on how they are used ([UKERC/ESC](https://ukerc.rl.ac.uk/publications/policy_briefing_paper/FINAL-Domestic-Heat-Energy-Services.pdf)).
- **Behavioural-state targeting beats attitudinal targeting.**
  - Ofgem's collective-switch RCTs targeted customers on a default tariff for 3+ years (n = 55k, 105k, 105k, 5k and about 2.5k). Switching was 27% vs 3%, 24% vs 4% and 29.5% vs 4.5%.
  - A reengagement trial after six months still got 14% vs 2% ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)).
  - The messenger mattered: letters from Ofgem rather than the supplier produced 15% rather than 27% in Trial 1, which points to *trust and relationship* effects ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)).
- **Design implication.** The review recommends layered "lenses", such as a vulnerability lens, over a single segmentation, and says the data should set the number of segments ([ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)). This fits a needs-weight vector per household better than discrete segments do.

---

## 3. Dimension-by-dimension evidence

### 3.1 COST (total paid)

**(a) What exists and how strong it is**
- This is the most heavily researched dimension. Stated preference comes from DCEs, contingent valuation (CV) and surveys. Revealed preference comes from switching data and CMA market analysis.
- Sample sizes are large: the CMA surveyed about 7,000 households ([GOV.UK 2016](https://gov.uk/government/news/cma-sets-out-energy-market-changes)), Ofgem about 4,000 a year, and DESNZ 6,086.

**(b) Key quantified findings**
- **Weight in choices.** Price took 59.5% of attribute importance for UK consumers and 56% for UK prosumers ([Lim et al. 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)).
- **Disengagement costs money.**
  - The CMA's provisional findings put customer detriment at about £1.7bn a year. About 70% of Big Six customers were on the standard variable tariff (SVT), and switching could save the average customer over £300 a year ([GOV.UK 2016](https://gov.uk/government/news/cma-sets-out-energy-market-changes)).
  - The final report's figure of about £1.4bn a year is widely quoted [unverified; not fetched].
- **Inertia persists even when savings are available.** In 2021, 42% of disengaged consumers said their current deal was satisfactory and 26% said switching wouldn't save enough ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
- **Money framing doesn't reliably move people.** Savings-framed ToU messaging showed no significant uplift across the review's studies ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
- **Heat pump price elasticity.** Each £1,000 off the upfront cost raised heat pump demand by about 10 percentage points ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)). The average consumer needed a heat pump to be about £1,500 cheaper than a boiler ([Nesta/BIT, n=1,801](https://www.nesta.org.uk/project-updates/how-much-will-people-pay-make-home-heating-greener/)).
- **Cross-sector loyalty penalty.** The penalty was put at £4.1bn a year across mobile, broadband, home insurance, mortgages and savings, averaging £877 per affected household. Eight in ten people paid it in at least one market ([Citizens Advice 2018](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-has-welcomed-the-cmas-response-to-their-super-complaint-on-the-loyalty-penalty/)). The CMA put it at about £4bn ([CMA 2018](https://assets.publishing.service.gov.uk/media/5c194665e5274a4685bfbafa/response_to_super_complaint_pdf.pdf)).

**(c) Distinct or folded in?** Always distinct, and usually the numeraire against which every other attribute is valued.

**(d) Refinement.** Literature on energy and the loyalty penalty separates *cost level* from *perceived fairness of price*:
- Only 38% trust their supplier to charge a fair price, against 45% who trust it to treat them fairly ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
- The CMA found that customers who feel ripped off become *less* engaged ([CMA 2018](https://assets.publishing.service.gov.uk/media/5c194665e5274a4685bfbafa/response_to_super_complaint_pdf.pdf)).

So cost has a fairness component that changes behaviour.

### 3.2 CASH FLOW (timing, liquidity, buffers, income regularity)

**(a) What exists and how strong it is**
- *Energy:*
  - implicit discount rate (IDR) studies, mostly revealed-preference or elicited, and mostly from the US;
  - the DESNZ heat pump DCE;
  - prepayment qualitative work.
- *Financial services:* the FCA Financial Lives Survey (n=17,950, a nationally representative tracker) is the strongest UK source on buffers ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).

**(b) Key quantified findings**
- **Implicit discount rates.**
  - The mean elicited rate was 19% (median 11%) across 1,217 US homeowners. It was higher for people with less education, lower income and lower credit scores. Willingness to pay for operating savings fell about 1.6% per extra percentage point on the discount rate ([Newell & Siikamäki 2015, NBER](https://www.nber.org/papers/w20969.pdf)).
  - IDRs range from 2–36% for space heating and 10–32% for insulation, up to 39–300% for refrigerators.
  - **Liquidity-constrained consumers show discount rates about 40% higher** than unconstrained ones (Epper et al. 2011, cited in [Stadelmann 2017](https://srv-clst-301-data66.zhaw.ch/bitstream/11475/20977/1/2017_Stadelmann_Mind-the-Gap_Postprint.pdf)). This is direct evidence that liquidity acts as its own channel, separate from preference over total cost.
  - Hausman's 1979 air-conditioner estimate appears as about 30% in that review. Other sources often cite 20–25% [unverified].
- **Upfront versus running cost in heat.** Upfront cost was 7–16 times more important than running cost, an implied discount rate of 10–15% ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)). Respondents valued financing mechanisms highly:
  - 54% of mortgage holders said a reduced mortgage rate would help "a lot";
  - 31% said a 0% loan over 7 years would, but only 16% over 2 years. This is a cash-flow-shape preference.
  - Holding over £10,000 in savings added about 2 points to heat pump choice.
- **Buffers.**
  - 24% (13.1m) of UK adults have low financial resilience.
  - 10% have no cash savings and a further 21% have less than £1,000.
  - 42% could not cover living costs for 3+ months, and 9% could not last a week without their main income.
  - 8% are in financial difficulty, meaning they missed bills in 3+ of the last 6 months ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).
- **Smoothing products, used because of cash flow.**
  - 20% used buy-now-pay-later (BNPL) in 12 months, up from 17%.
  - 21% were overdrawn at some point, and 8% are usually overdrawn by payday ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).
  - A qualitative study by Which? (n=30) produced a BNPL typology: *Spending Smoothers* (the largest group), *Experimenters*, *No Choicers* and *Plate Spinners* (low, unpredictable income). Reasons included protecting savings and using BNPL as a budgeting tool ([Which? 2021](https://www.which.co.uk/policy/money/8573/buynowpaylater2)).
- **Willingness to pay for smoothing.** 49% of holders of five common insurance products pay by instalment. 56% of contents-policy instalment payers believe it costs more and do it anyway ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)). This is revealed willingness to pay for cash-flow smoothing.
- **Payment-method cost differentials in energy.**
  - In 2014 average dual-fuel bills were £1,266 for prepayment, £1,267 for standard credit and £1,188 for direct debit ([Ofgem 2015](https://www.ofgem.gov.uk/ofgem-publications/95497/prepaymentreportjune2015finalforpublication-pdf)).
  - Ofgem levelised prepayment and direct-debit standing charges from April 2024 and paused Phase 2 (debt costs across standard credit and direct debit) in August 2024 ([Ofgem 2024](https://ofgem.gov.uk/decision/decision-adjusting-standing-charges-prepayment-customers)).
  - Households who pay a premium for standard credit or prepayment are revealing a preference over *payment timing and control*.

**(c) Distinct or folded in?**
- Economics usually folds it into the discount rate or "liquidity constraints".
- Energy-poverty and FCA work treat resilience as distinct.
- The IDR evidence supports keeping CASH FLOW separate from COST. Income regularity, though, is rarely measured. I could not find FCA income-volatility figures in the key findings [unverified].

### 3.3 TIME (hassle, effort, attention)

**(a) What exists and how strong it is**
- Mostly survey and qualitative evidence, plus the behavioural RCT literature on friction.
- I found **no GB energy study that monetises value of time** for switching or tariff management. This is a gap.

**(b) Key quantified findings**
- **Switching hassle.** 28% agree switching is a hassle they don't have time for. That rises to 37% of disengaged consumers and **41% of prepayment customers**, against 20% of engaged consumers ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
- **Hassle Haters are 20%** of the population ([Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)).
- **Heat pumps.**
  - Wanting to minimise time and inconvenience cut heat pump choice by 10 points, and wanting to minimise space by 6 points ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)).
  - 80% said disruption discouraged them ([Nesta/BIT](https://www.nesta.org.uk/project-updates/how-much-will-people-pay-make-home-heating-greener/)).
- **Removing friction works.**
  - Opt-out ToU enrolment averaged 83% against 26% for opt-in, about 70 percentage points more ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
  - Collective switching with assisted, mostly phone-based switching raised switching about eightfold ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)).
- **Cross-sector.**
  - The CMA lists hassle, complexity and missed renewal deadlines as inertia drivers ([CMA 2018](https://assets.publishing.service.gov.uk/media/5c194665e5274a4685bfbafa/response_to_super_complaint_pdf.pdf)).
  - 25% of in-contract mobile users didn't know they could move to SIM-only at contract end ([Ofcom 2018](https://www.ofcom.org.uk/__data/assets/pdf_file/0030/113898/pricing-report-2018.pdf)).
  - About 1.5m kept paying for handsets they had already paid off, overpaying about £330m a year ([Ofcom 2018](https://www.ofcom.org.uk/__data/assets/pdf_file/0030/113898/pricing-report-2018.pdf)).

**(c) Distinct or folded in?**
- Usually treated as "switching costs" (economics) or "friction/hassle" (behavioural science).
- **Refinement: split clock time from cognitive bandwidth.**
  - The scarcity literature finds that financial worry consumes cognitive capacity ([Mani, Mullainathan, Shafir & Zhao 2013, Science](https://www.clime.rutgers.edu/publications-filtered/poverty-impedes-cognitive-function)). The commonly cited effect size, roughly equal to 13 IQ points, is [unverified].
  - Complexity also lowers uptake on its own: real-time pricing had about 13% lower uptake than static ToU, which the authors link to unpredictability and complexity ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
  - Smart Energy GB's "Enough on my plate" segment describes the bandwidth version ([ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)).

### 3.4 CARBON (environmental values)

**(a) What exists and how strong it is**
- Large stated-preference work: CV with n=4,006 and DCEs.
- Revealed-preference evidence is thin and points to weak effects.

**(b) Key quantified findings**
- **Stated importance.** Renewable share took 18.7% of attribute importance for UK consumers ([Lim et al. 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)).
- **The strongest attitude predictor of heat pump choice.** Wanting to minimise environmental impact added 17 points and climate concern added 5. Saving on bills added only 6 ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)).
- **Green willingness to pay is concentrated.**
  - About 67–69% had zero willingness to pay a green-electricity premium in 2008–09 (n=4,006).
  - People who would be *less* interested if others also paid had much lower WTP. That points to warm-glow and social-comparison motives rather than pure carbon value ([Akcura 2013, EPRG](https://jbs.cam.ac.uk/wp-content/uploads/2023/12/eprg-wp1316.pdf)).
- **Revealed behaviour.**
  - 27% are on a green tariff ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
  - Environmental framing had no significant effect on ToU uptake, though only two measures tested it ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
  - About half of those choosing a gas boiler were not convinced heat pumps had environmental benefits ([Nesta/BIT](https://www.nesta.org.uk/project-updates/how-much-will-people-pay-make-home-heating-greener/)).

**(c) Distinct or folded in?** Distinct in DCEs and segmentations. Defra's 2008 pro-environmental behaviours framework had 7 segments [unverified; not fetched]. The literature often frames it as **identity, values or social norms** rather than willingness to pay per tonne.

**(d) Refinement: separate carbon value from pro-social and community preferences.**
- UK consumers preferred non-profit providers (coefficient 0.676) and non-profit generators (0.463).
- Prosumers preferred selling to fuel-poor households (coefficient 0.478) ([Lim et al. 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)).
- Those are fairness and identity preferences, not carbon.

### 3.5 PEACE OF MIND: CERTAINTY

**(a) What exists and how strong it is**
- Revealed-preference evidence on tariff choice is reasonable.
- **Direct UK estimates of willingness to pay for price certainty are scarce.** I found no published UK DCE that monetises the fixed-tariff premium.
- A German RWI choice experiment measuring the compensation households need to give up price stability (n=3,000) is pre-registered and ongoing, with no results yet ([Hümmecke, Andor & Tomberg, AEA RCT Registry](https://www.socialscienceregistry.org/trials/17459)).
- I did not locate an Ofgem/Frontier fixed-versus-variable study [unverified].

**(b) Key quantified findings**
- **Revealed take-up of fixes.** 68% were on fixed tariffs in 2021, rising to 81% of engaged consumers against 46% of disengaged ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
  - Caveat: fixes were often the cheapest offers before 2021, so this mixes COST and CERTAINTY.
- **A fixed price is preferred to alternatives.** UK consumers rated a fixed price above provider control of appliance timing (coefficient −0.677) and app-based generator choice (−0.573) ([Lim et al. 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)).
- **Loss aversion reduces ToU willingness.**
  - Bill protection raised willingness by about 10% in one survey experiment, though the pooled effect was not significant ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
  - The top perceived switching risk was "might not save as much as they thought", cited by 54% ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)).
  - Loss aversion over uncertain savings is a recognised source of the energy efficiency gap (Greene et al. 2009, cited in [Stadelmann 2017](https://srv-clst-301-data66.zhaw.ch/bitstream/11475/20977/1/2017_Stadelmann_Mind-the-Gap_Postprint.pdf)).
- **Bill anxiety drives behaviour in heating trials.** Some households turned heating down out of bill anxiety, and users worried about overrunning allowances and being "locked in" ([UKERC/ESC](https://ukerc.rl.ac.uk/publications/policy_briefing_paper/FINAL-Domestic-Heat-Energy-Services.pdf)).
- **Bill shock in telecoms.** Ofcom suggests lower-income consumers may prefer pay-as-you-go (PAYG) to avoid bill shock, but gives no survey figure ([Ofcom 2018](https://www.ofcom.org.uk/__data/assets/pdf_file/0030/113898/pricing-report-2018.pdf)).
- **Fear of risk drives cross-sector inertia** ([CMA 2018](https://assets.publishing.service.gov.uk/media/5c194665e5274a4685bfbafa/response_to_super_complaint_pdf.pdf)).

**(c) Distinct or folded in?**
- Economics treats it as risk aversion or loss aversion. Policy work folds it into "confidence".
- Certainty evidence is often confounded with CONTROL and CASH FLOW. The prepayment literature bundles "avoid large unexpected bills" with budgeting ([Ofgem 2015](https://www.ofgem.gov.uk/ofgem-publications/95497/prepaymentreportjune2015finalforpublication-pdf)).
- **Missing evidence:** a GB-specific WTP for certainty. This is the largest quantitative gap for the framework.

### 3.6 PEACE OF MIND: CONTROL

**(a) What exists and how strong it is.** The literature has two separate strands.

*Strand 1: spend control.* This is the prepayment, PAYG and BNPL evidence: qualitative work plus administrative data.

**(b) Key quantified findings, spend control**
- **Chosen vs imposed prepayment: the literature does not settle this.**
  - In 2014 about **60% of newly installed prepayment meters were fitted because of debt**, and about 16% of those under warrant ([Ofgem 2015](https://www.ofgem.gov.uk/ofgem-publications/95497/prepaymentreportjune2015finalforpublication-pdf)).
  - Only about 7% (electricity) and 10% (gas) of prepayment customers were in debt to their supplier.
  - Only 3% moved to a credit meter in 2013 ([Ofgem 2015](https://www.ofgem.gov.uk/ofgem-publications/95497/prepaymentreportjune2015finalforpublication-pdf)). That suggests many who arrive via debt then stay, by preference or by inertia.
  - **No nationally representative estimate of the "chosen" share was found** [gap].
- **A qualitative typology of how people come to be on prepayment** (n=50, involuntary users oversampled):
  - *active choice* (18): chose it for control over usage and spend;
  - *moved in* (6): inherited it with the property, often unaware they could change;
  - *involuntary* (26): moved onto it for debt, with 16 not notified ([Ofgem/Savanta 2023](https://www.ofgem.gov.uk/sites/default/files/2023-09/Prepayment%20Meter%20Customer%20Journey%20-%20Qualitative%20Research.pdf)).
- **What people value about prepayment** ([Ofgem/Savanta 2023](https://www.ofgem.gov.uk/sites/default/files/2023-09/Prepayment%20Meter%20Customer%20Journey%20-%20Qualitative%20Research.pdf)):
  - visibility of usage and spend;
  - topping up when and how much they choose;
  - avoiding large bills and new debt;
  - **some preferred prepayment to direct debit, where they felt debt was hidden.** This directly supports the framework's "distrust of DD/supplier access".
- **The long-standing evidence agrees.** A Warwick/UEA survey of 3,400+ low-income consumers found they preferred prepayment for budgeting, controlling consumption and avoiding debt. A quarter had self-disconnected in the previous year ([Warwick 2001](https://warwick.ac.uk/news/pressreleases/ne1000000081535/)).
- **Prepayment users value budgeting** (focus groups n=42, survey n=2,095). Prepayment users were more tolerant of involuntary installation (28% support, against 19% of others), yet half still opposed it ([Ofgem/Thinks/Ipsos 2023](https://www.ofgem.gov.uk/sites/default/files/2023-04/Consumer%20Attitudes%20to%20Involuntary%20Prepayment%20Meter%20Installation%20Rule%20Changes.pdf)).
- **Telecoms analogue.**
  - 24% of mobile users are on PAYG.
  - That rises to 45% of 65–74s, **65% of over-75s and 41% of the DE group**.
  - Ofcom attributes this partly to cost control and partly to failing credit checks, so it too mixes choice and constraint ([Ofcom 2018](https://www.ofcom.org.uk/__data/assets/pdf_file/0030/113898/pricing-report-2018.pdf)).
- **Finance analogue.** BNPL's clear repayment schedule, where users know when payments are due and when the debt ends, is valued as a control feature ([Which? 2021](https://www.which.co.uk/policy/money/8573/buynowpaylater2)).

*Strand 2: device and automation control.* This is DSR survey experiments and trials.

**(b) Key quantified findings, device control**
- **Survey experiment** (n=2,002, five DSR offers; [Fell et al. 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)):
  - Direct load control (DLC) had the highest acceptance. The offer had an unlimited override and less than 1°C of temperature effect.
  - Trust predicted acceptance of every tariff (β 0.13–0.29).
  - Privacy concern lowered acceptance of every tariff, most for dynamic ToU with automation (β −0.245).
  - Locus of control mattered only for DLC (β 0.18). **A more external locus of control predicted higher DLC acceptance**, and the authors warn this creates exploitation risk.
- **Automation has no clear pooled effect on ToU uptake** (p=0.958), with a +4.5% effect in one study ([Nicolson et al. 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)).
- **People want supervisory control.** Heating trial users want to feel they haven't lost control to automation, and split into "planners" and "reactors" ([UKERC/ESC](https://ukerc.rl.ac.uk/publications/policy_briefing_paper/FINAL-Domestic-Heat-Energy-Services.pdf)).
- **Provider control of appliance timing is disliked** relative to a fixed price (−0.677; [Lim et al. 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)).

**(c) Distinct or folded in?**
- The literature treats CONTROL as distinct, but as *two constructs*:
  - spend control sits close to CASH FLOW and mental accounting;
  - device control sits close to TRUST and privacy.
- The framework puts both under "peace of mind" with certainty. The evidence suggests:
  - spend control and certainty move together for low-resilience households;
  - device control can trade *against* time. Automation saves effort but costs agency, and the people who value agency least accept automation most.
- The mental-accounting mechanism (Thaler) behind prepayment is widely asserted [unverified as an energy-specific empirical test; the 2001 Warwick release does not mention it].

### 3.7 COMFORT/HEALTH floor

**(a) What exists and how strong it is**
- Treated mainly in fuel-poverty and vulnerability policy, prepayment harm research and heating-service trials.
- It is **rarely a DCE attribute**. DSR studies usually *hold it fixed*: for example, Fell's DLC offer capped the temperature effect below 1°C ([Fell et al. 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)).

**(b) Key quantified findings**
- **Prepayment self-rationing.** Many prepayment users ration, some go days without supply, and this is most common among older people and those living alone ([Ofgem/Savanta 2023](https://www.ofgem.gov.uk/sites/default/files/2023-09/Prepayment%20Meter%20Customer%20Journey%20-%20Qualitative%20Research.pdf)). About 25% of low-income prepayment users had self-disconnected in a year ([Warwick 2001](https://warwick.ac.uk/news/pressreleases/ne1000000081535/)).
- **Public norms treat health as a hard floor.** 73% oppose involuntary prepayment where continuous supply is needed for health, and 72% where someone is aged 85+ ([Ofgem 2023](https://www.ofgem.gov.uk/sites/default/files/2023-04/Consumer%20Attitudes%20to%20Involuntary%20Prepayment%20Meter%20Installation%20Rule%20Changes.pdf)).
- **Comfort is multi-factor and under-recognised.** It covers radiant heat, drying clothes and cool bedrooms, and "many people don't realise their comfort could be better". Fuel poverty affects about 2.5m English households, about 11% ([UKERC/ESC](https://ukerc.rl.ac.uk/publications/policy_briefing_paper/FINAL-Domestic-Heat-Energy-Services.pdf)).
- **Vulnerability is widespread.** 49% of UK adults show characteristics of vulnerability ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)).

**(c) Distinct or folded in?**
- Policy treats it as a constraint, which supports the framework's "floor".
- **Refinement:** comfort *above* the floor is a real preference that people trade against cost and anxiety. ESC heating users paid for on-demand heat once costs were visible ([UKERC/ESC](https://ukerc.rl.ac.uk/publications/policy_briefing_paper/FINAL-Domestic-Heat-Energy-Services.pdf)).
- So the evidence supports a floor plus a utility term, not a floor alone. Also, people perceive comfort poorly, so it interacts with information.
- Ofgem's Consumer Vulnerability Strategy, updated 2025, frames this as a supplier duty. Its content was not fetched [unverified].

---

## 4. Dimensions the literature finds that the framework is missing

| Candidate dimension | Evidence | Strength | Recommendation |
|---|---|---|---|
| **Trust (in supplier, sector, intermediary)** | Market Sceptics (14%) defined by low trust ([Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)); 34% trust the sector, 45% their own supplier ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)); trust predicts DSR acceptance ([Fell 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)); messenger effect 27% vs 15%, and avoidance of unfamiliar suppliers ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)); FCA: 36% think firms are honest ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)) | Strong, multi-method | Add as a **cross-cutting moderator**. It scales the perceived value of any supplier-mediated promise (certainty, automation, savings). The framework's "distrust of DD/supplier access" is one instance |
| **Self-efficacy / capability / confidence** | Anxious Avoiders (13%) ([Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)); 63% confident comparing deals ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)); 22% lack confidence managing money ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)); overclaimed knowledge −7 points on heat pump choice ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)) | Strong | Model as a **capability state** that raises effective TIME cost and lowers the ability to act on COST, not as a preference |
| **Relationship / loyalty** | CMA: some customers feel a bond with their provider ([CMA 2018](https://assets.publishing.service.gov.uk/media/5c194665e5274a4685bfbafa/response_to_super_complaint_pdf.pdf)); Contented Conformers trusting and status-quo ([Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)); 42% of disengaged "satisfied" ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)); switchers chose the exclusive offer from the known channel even when not cheapest ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)) | Moderate | Add as a **status-quo or relationship utility**, distinct from TIME |
| **Privacy / data intrusion** | Negative for every DSR tariff (β up to −0.245) ([Fell 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)) | Moderate (one large survey experiment) | Fold into a **device-control/agency** sub-dimension |
| **Fairness / pro-social / ethics** | 41% would accept a bill increase to protect vulnerable groups ([Ofgem 2023](https://www.ofgem.gov.uk/sites/default/files/2023-04/Consumer%20Attitudes%20to%20Involuntary%20Prepayment%20Meter%20Installation%20Rule%20Changes.pdf)); preference for non-profit providers and selling to fuel-poor households ([Lim 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf)); "fair price" trust gap ([Ofgem 2021](https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf)) | Moderate | Consider a **fairness/identity** term, separate from CARBON |
| **Social norms** | Green WTP depends on whether others pay ([Akcura 2013](https://jbs.cam.ac.uk/wp-content/uploads/2023/12/eprg-wp1316.pdf)); "Follow the crowd" segment ([ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)); Opower home energy reports cut consumption about 2% (Allcott 2011, [doi](https://doi.org/10.1016/j.jpubeco.2011.03.003)) [unverified; not fetched] | Moderate | Model as a **response lever**, not a need |
| **Simplicity / cognitive load** | Dynamic/real-time tariffs about 13% lower uptake than static ([Nicolson 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)); scarcity and bandwidth ([Mani et al. 2013](https://www.clime.rutgers.edu/publications-filtered/poverty-impedes-cognitive-function)) | Moderate | Split TIME into clock time and cognitive load |
| **Stigma / dignity** | Shame topping up in public; distress at warrant installs ([Ofgem/Savanta 2023](https://www.ofgem.gov.uk/sites/default/files/2023-09/Prepayment%20Meter%20Customer%20Journey%20-%20Qualitative%20Research.pdf)) | Qualitative | Treat as part of the PEACE OF MIND harm channel |
| **Space / aesthetics / home disruption** | Minimising occupied space −6 points ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)) | Single strong DCE | Asset-specific; could sit under TIME/disruption |
| **Tech enthusiasm / digital access** | 2% digitally excluded; 7% don't bank online ([FCA 2025](https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf)); most collective switchers preferred the phone ([Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)); internet use 62% vs 93% across engagement segments ([ClimateXChange](https://www.climatexchange.org.uk/media/4433/consumers-energy-domestic-energy-consumer-types-review-of-existing-segmentation-approaches-december-2020.pdf)) | Moderate | Model as a **channel constraint**; tech enthusiasm as a preference is weakly evidenced here |

---

## 5. Coverage matrix: dimension by research body

Ratings are my judgement from the sources above: ●●● strong, ●● moderate, ● thin, ○ absent.

| Need | Segmentation | DCE / stated preference | Behavioural economics | Socio-economic / demographic |
|---|---|---|---|---|
| COST | ●●● (Happy Shoppers) | ●●● (numeraire) | ●● (inertia, loyalty penalty) | ●●● (CMA, Ofgem) |
| CASH FLOW | ●● ("Money worries") | ●● (upfront vs running, finance) | ●●● (IDRs, present bias, liquidity) | ●●● (FCA resilience) |
| TIME | ●●● (Hassle Haters) | ●● (disruption) | ●●● (defaults, opt-out, friction) | ● |
| CARBON | ●● ("Good intentions") | ●●● | ● (framing null) | ● (WTP by income/gender) |
| CERTAINTY | ● | ● (no GB WTP found) | ●● (loss aversion) | ● |
| CONTROL (spend) | ●● (Market Sceptics: 20% prepayment) | ○ | ●● (mental accounting [unverified]) | ●●● (prepayment, PAYG demographics) |
| CONTROL (device) | ○ | ●● | ●● (locus of control) | ● |
| COMFORT floor | ○ | ● (held constant) | ● | ●● (fuel poverty, vulnerability) |
| *Trust* (missing) | ●●● | ●● | ●● | ●● |
| *Capability* (missing) | ●●● | ● | ●● (scarcity) | ●●● |

---

## 6. Synthesis: support, refine, contradict

**Supported**
- COST, CASH FLOW, TIME and CARBON appear as independent drivers in large-sample DCEs and surveys.
  - The DESNZ DCE alone separates cost, liquidity, hassle and environmental motivation with distinct effect sizes ([DESNZ 2026](https://assets.publishing.service.gov.uk/media/6ab24ef3fceb6fb3a6500f72/impact-of-heat-pump-costs-on-uptake-report.pdf)).
- A COMFORT/HEALTH floor matches how regulators and the public treat vulnerability ([Ofgem 2023](https://www.ofgem.gov.uk/sites/default/files/2023-04/Consumer%20Attitudes%20to%20Involuntary%20Prepayment%20Meter%20Installation%20Rule%20Changes.pdf)).
- The framework's DD-distrust item has direct qualitative support ([Ofgem/Savanta 2023](https://www.ofgem.gov.uk/sites/default/files/2023-09/Prepayment%20Meter%20Customer%20Journey%20-%20Qualitative%20Research.pdf)).

**Refined**
1. **Split CONTROL** into spend control (next to CASH FLOW) and device agency (next to TRUST and privacy). The two can point in opposite directions: an external locus of control means higher DLC acceptance ([Fell 2015](https://discovery.ucl.ac.uk/1476671/1/9-207-15_Fell.pdf)).
2. **Split TIME** into clock time and cognitive bandwidth. Bandwidth is depleted by financial scarcity, so it should be *coupled* to CASH FLOW state rather than set independently ([Mani et al. 2013](https://www.clime.rutgers.edu/publications-filtered/poverty-impedes-cognitive-function)).
3. **Model trust and capability as moderators** rather than needs. They are the main axes on which empirical segmentations separate ([Ofgem 2017](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)).
4. **Separate CARBON from pro-social/fairness and identity preferences** ([Lim 2025](https://discovery.ucl.ac.uk/10207824/1/1-s2.0-S2214629625001537-main.pdf); [Akcura 2013](https://jbs.cam.ac.uk/wp-content/uploads/2023/12/eprg-wp1316.pdf)).
5. **Treat prepayment as an unclear signal of chosen versus imposed.**
   - About 60% of new installations were debt-driven in 2014 ([Ofgem 2015](https://www.ofgem.gov.uk/ofgem-publications/95497/prepaymentreportjune2015finalforpublication-pdf)), yet active choosers value control.
   - A simulation should assign prepayment through *both* channels and not infer preference from meter type.

**Contradicted or cautioned**
- **Stated CARBON and CONTROL preferences overstate behaviour by about 3–5×** ([Nicolson 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf)). Weights calibrated from surveys need an intention–action discount.
- **Defaults and friction dominate attitudes.** Opt-out raises ToU uptake by about 70 percentage points, and assisted switching works across all attitudinal segments ([Nicolson 2018](https://discovery-pp.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf); [Ofgem 2019](https://www.ofgem.gov.uk/sites/default/files/docs/collective_switch_trials_final_report_final.pdf)). A purely needs-weighted choice model will under-predict inertia unless it adds a status-quo term.
- **Socio-demographics predict engagement and load poorly**: marginal R² of 0–20% for load ([Anderson 2016](https://eprints.soton.ac.uk/396943/1/Anderson_et_al_Predicting_Household_Characterstics_CEUS_Accepted.pdf)). Deriving need weights only from Acorn-style geodemographics would be weakly grounded.

**Biggest evidence gaps** (where the simulation's parameters will be assumptions)
1. GB willingness to pay for tariff price certainty.
2. A monetised value of time for energy tasks.
3. A representative chosen-vs-imposed prepayment split.
4. Income-volatility effects on energy payment choice.
5. Predictive validation of any attitudinal energy segmentation against revealed behaviour.

---

*Notes on method and limits:*
- The 2016 CMA final-report figure (£1.4bn) and the Defra 2008 segments were not fetched.
- The Allcott 2011 norms result is from recall, not fetched.
- The Mani et al. effect size and the mental-accounting attribution are not confirmed from fetched sources.
- Ofgem's 2025 Consumer Vulnerability Strategy and any Ofgem/Frontier fixed-tariff study were not located in this pass.
- Lim et al. (2025) uses a Prolific sample (n=536 UK); treat its importance shares as indicative.