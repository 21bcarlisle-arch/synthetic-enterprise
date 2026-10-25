# Director evidence: proving and showing household savings

**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 05:37 GMT: "Also should we do more research on key future topics? How do gas boilers work and how do choices in the sim appear and gas usage and choices for customer and advice that the supplier can offer? E..g condensing or not? Thermostat. Timer and schedule. Flow rate. Radiator modernity and maintenance. . The same for EV purchase. Home charge versus venue. Cost and carbon savings versus petrol and diesel for different mileages. Then the actual charging and usage patterns that occur, based on logic that the SIM knows about the premise and person but the supplier has to figure out or ask about. Then the same for pv and battery. How old, what orientation, what settings. How much would the unit cost and save the customer. Then proving if it did or didn't. Sharing the savings clearly for the customer to enjoy. All these subjects are quite complicated and need knowledge. There may be others too we need for our roadmap??"

This is one of six cited evidence packs researched in the advisor's chat, outside your serial gate. They land in one commit with a cover steer: DIRECTOR_STEER_THE_ADVICE_ROADMAP_NEEDS_ITS_KNOWLEDGE_FIRST_2026-10-25.md. Read the cover steer first. It sets the order of work.

## What to do with it

- Turn this pack into a published Knowledge page, register its concepts, and take its headline bands as candidate world claims.
- Its "world needs to model" list is the hidden-attribute spec for the world, and the observe / infer / ask table is the wall spec for the supplier. The cover steer says when each is built.
- [derived] figures can be re-run. [unverified] figures are not claims until sourced. Named gaps are research tasks, and the research budget ran out on several of them. Close a gap, or record that nothing is published.
- This is drafting work, so it must not displace the serial queue.

---

# Evidence pack: proving household savings (money and carbon) and showing them so customers believe them

*Knowledge layer, Poesys. Compiled 25 Oct 2026. Every figure has its source URL beside it. **[derived]** marks my own arithmetic. **[unverified]** marks things I recall but could not confirm from a fetched source. The shared web-search budget ran out before I finished, so some of the named sources were not fetched; they are listed under Named gaps.*

---

## 1. Measurement and verification (M&V) methods

### 1.1 Deemed vs modelled vs metered savings

- **Deemed.** A fixed saving is assigned to each measure in advance. GB's ECO4 and GBIS work this way: "Scores are based on the annual bill saving achieved by a measure or package of measures", read from a partial-project scores matrix ([Ofgem ECO4 Scores](https://www.ofgem.gov.uk/guidance/eco4-scores)). GBIS "adopts the ECO4 partial project scores framework", and its matrix is the same as ECO4's minus ineligible measures ([Ofgem GBIS scoring](https://www.ofgem.gov.uk/guidance/great-british-insulation-scheme-scoring-methodology)).
  - ECO corrects for over-prediction with "in-use factors", a flat percentage cut. The carbon formula is "S x P x L x (100% − IUF)" ([Ofgem ECO consultation 2013](https://www.ofgem.gov.uk/sites/default/files/docs/2013/05/eco-consultation-on-p-23-may-2013_0.pdf)). I recall IUF values of about 35% for cavity and loft insulation and 33% for solid wall **[unverified]**.
- **Modelled.** The saving comes from a SAP/RdSAP or engineering model. The ECO4/GBIS mid-scheme assessment says its impacts were "quantified using well-understood modelling techniques", with "no sensitivity analysis" ([DESNZ options assessment, Nov 2024](https://www.gov.uk/government/consultations/energy-company-obligation-4-and-the-great-british-insulation-scheme-mid-scheme-changes/eco4-and-gbis-mid-scheme-changes-options-assessment-published-and-updated-20-november-2024)).
- **Metered / measured.** The saving comes from meter data.
  - The same 2024 document proposes a **voluntary Pay-for-Performance (PFP)** mechanism for ECO4/GBIS. It would reward measured efficiency gains using SMETERs (smart-meter-enabled thermal efficiency ratings), which "take direct measurements from a building" ([DESNZ, Nov 2024](https://www.gov.uk/government/consultations/energy-company-obligation-4-and-the-great-british-insulation-scheme-mid-scheme-changes/eco4-and-gbis-mid-scheme-changes-options-assessment-published-and-updated-20-november-2024)).
  - **SMETER accuracy.** A blind trial in 30 homes tested 8 methods against co-heating tests. Bias (NMBE) ranged from −0.7% to −26.9%; scatter (CV(RMSE)) from 13.4% to 38.9%. Three methods showed low bias, and the best beat an expert RdSAP assessment ([DESNZ SMETER evidence annex](https://assets.publishing.service.gov.uk/media/6a4790e28effd97622f53c04/smeter-case-studies-evidence-base-annex.pdf)).
  - **Calculated vs measured heat loss.** In the MEASURED trial (56 homes), BS EN 12831 calculations matched measured heat loss in only 30% of homes and overestimated it in 59% ([Elmhurst, Aug 2026](https://www.elmhurstenergy.co.uk/blog/2026/08/11/new-smeter-guidance-from-measurement-to-action-the-future-of-measured-building-performance/)).
  - **Outcome-based contract.** Aarschot, Belgium: 166 homes contracted on "results achieved rather than works completed", with a 25% target. The achieved reduction was 37%, verified under IPMVP ([DESNZ SMETER annex](https://assets.publishing.service.gov.uk/media/6a4790e28effd97622f53c04/smeter-case-studies-evidence-base-annex.pdf)).

### 1.2 IPMVP options (EVO)

I could not fetch the EVO text. The standard definitions are **[unverified]**:

| Option | What is measured | Typical use |
|---|---|---|
| A | Retrofit isolation, key parameters measured and others stipulated | A single measure |
| B | Retrofit isolation, all parameters measured | A single measure |
| C | Whole facility, from utility meters | Whole-house meter analysis |
| D | Calibrated simulation | Where there is no baseline data |

- The core equation is Savings = (Baseline − Reporting-period use) ± Adjustments. Adjustments are "routine" (weather, occupancy) or "non-routine" (static changes such as an extension or a new EV) **[unverified]**.
- For a supplier with smart-meter data, **Option C is the natural default**.

### 1.3 Weather normalisation and model-fit criteria

- **ASHRAE Guideline 14 calibration thresholds:**

  | Data interval | CV(RMSE) | NMBE |
  |---|---|---|
  | Monthly | ≤ 20% | ≤ ±5% |
  | Hourly | ≤ 30% | ≤ ±10% |

  Both must pass ([energy-data.io G14 summary](https://energy-data.io/standards/ashrae-guideline-14/)). I recall 15% monthly CV(RMSE) for calibrated simulation **[unverified]**. I also recall a G14 rule that fractional savings uncertainty must be below 50% at 68% confidence **[unverified]**.
- **Monthly regression is generally usable only when savings are at least 10% of whole-building use.** Interval data can detect smaller savings. With fewer than 6 months of data, mean bias error is "unacceptably high"; 9-month models have median MBE close to zero ([Kemper, ACEEE 2015](https://aceee.org/sites/default/files/pdf/conferences/ie/2015/Session3C-Kemper-IE15-12.7.15.pdf)).
- **CalTRACK / OpenEEmeter.** I recall the following, but the docs redirected to a domain I could not fetch, so all of it is **[unverified]**:
  - a 365-day baseline;
  - a data-sufficiency rule of about 90% coverage;
  - daily and billing models using HDD/CDD with a balance-point search;
  - an hourly "time-of-week and temperature" model with occupancy segmentation;
  - a design aimed at portfolio-level aggregation rather than single-site claims.
- **Uncertainty is often understated when residuals are autocorrelated.** Bayesian AR(1) and Newey–West intervals achieved coverage "consistently close to 95%". By comparison, the best method in Touzani et al. (2019) on real data reached only 71% ([arXiv 2607.25382](https://arxiv.org/pdf/2607.25382)).
- **Weather normalisation in practice.** The BIT Nest evaluation used heating-degree days with propensity matching and fixed-effects difference-in-differences. Measured savings were 4.5–5% of household gas ([BIT, 2017](https://www.bi.team/wp-content/uploads/2017/11/311013-Evaluating-Nest-BIT-Exec-Tech-Summaries.pdf)).

### 1.4 Comparison groups and difference-in-differences

- **The gold standard is the RCT.**
  - Ofgem's CMOL trial randomised about 150,000 customers ([Ofgem CMOL](https://www.ofgem.gov.uk/sites/default/files/docs/2017/11/cmol_report_slidepack_1.pdf)).
  - The BIT IHD-vs-app trial randomised 7,903 customers ([BIT/BEIS 2019](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf)).
- **The workhorse is quasi-experimental difference-in-differences with matching.** All 7 supplier smart-meter studies in BIT's 2023 meta-analysis used it ([BIT/DESNZ 2023](https://assets.publishing.service.gov.uk/media/64831d59103ca60013039c7a/energy-supplier-review-of-smart-meter-energy-consumption-impacts.pdf)).
- **Controls matter.** A meta-analysis of 156 trials found an average saving of 7.4%. Studies with control groups and weather/demographic controls found about 2%; studies without them found about 9.6% ([Delmas, Fischlein & Asensio 2013](https://www.ioes.ucla.edu/wp-content/uploads/2017/07/2013-Delmas-Fischlein-Asensio-EnergyPolicy.pdf)).

### 1.5 Minimum detectable saving: one home vs a portfolio

**One home, US evidence.** Hourly models give a median detectable saving of **3.6% at 90% confidence**; daily models give 4.3%. This is from 96 homes ([Kemper, ACEEE 2015](https://aceee.org/sites/default/files/pdf/conferences/ie/2015/Session3C-Kemper-IE15-12.7.15.pdf)).

**Portfolios, empirical UK anchors (95% confidence-interval half-widths):**

| Trial | Arm size | Half-width | Source |
|---|---|---|---|
| BIT IHD vs app, electricity | ~2,760 per arm | ±1.4 percentage points (−0.50 to +2.26) | [BIT 2019](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf) |
| BIT IHD vs app, gas | ~2,760 per arm | ±1.8 percentage points | [BIT 2019](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf) |
| SENS smart thermostat (SEN-ST), gas | ~395 per arm | ±3.9% | [SENS 2023](https://assets.publishing.service.gov.uk/media/6480aa3cb32b9e000ca963a6/sens-overall-impact-evaluation-report.pdf) |
| SENS GenGame | 1,760 vs 1,067 | ±2.0% | [SENS 2023](https://assets.publishing.service.gov.uk/media/6480aa3cb32b9e000ca963a6/sens-overall-impact-evaluation-report.pdf) |

- **Scaling check [derived].** Scaling the SENS ±3.9% by √(395/2760) gives about ±1.5%. That is consistent with the BIT figure, so half-widths do fall roughly with 1/√N.
- **Rule of thumb [derived].** For a randomised comparison, the 95% half-width is about 1.5pp × √(2,760 / n per arm):

  | n per arm | Approximate 95% half-width |
  |---|---|
  | 300 | ±4.5pp |
  | 1,000 | ±2.5pp |
  | 10,000 | ±0.8pp |
  | 100,000 | ±0.25pp |

  Weather and price shocks are common to both arms, so they cancel in an RCT. They do **not** cancel in a single-home pre/post estimate.
- **Underpowered trials.** In SENS, "energy consumption analyses were likely to have reduced statistical power", so its null results cannot tell "no effect" from "too small to detect" ([SENS 2023](https://assets.publishing.service.gov.uk/media/6480aa3cb32b9e000ca963a6/sens-overall-impact-evaluation-report.pdf)).

### 1.6 How long a baseline needs to be

- **At least 6 months, ideally 9–12** to avoid seasonal bias ([Kemper, ACEEE 2015](https://aceee.org/sites/default/files/pdf/conferences/ie/2015/Session3C-Kemper-IE15-12.7.15.pdf)).
- One full year of calibration data was used in [arXiv 2607.25382](https://arxiv.org/pdf/2607.25382).
- CalTRACK's 12 months is **[unverified]**.
- Heating-led gas savings need a baseline that spans a winter.

---

## 2. Baselines for flexibility events

- **DFS winter 2022/23 (P376 basis).** The baseline is average use over the previous 10 working days (or 4 weekend days), matched by day type. A domestic **in-day adjustment** then shifts it, using the window from 4 to 1 hours before the event compared with the same window on the 10 baseline days ([NESO DFS deep-dive](https://neso.energy/document/279586/download)).
- **Gaming arithmetic in NESO's own slides.**
  - Inflating the 3-hour adjustment window at 34p/kWh costs about £1.02 per kWh of baseline uplift, against a £3/kWh reward. That is a net gain of £1.98.
  - A 10-hour window would cost £3.40 against a £1 reward, so gaming would lose money.
  - NESO's preferred option was to remove the adjustment ([NESO](https://neso.energy/document/279586/download)).
  - It was removed for 2023/24 ([Solar Power Portal](https://www.solarpowerportal.co.uk/solar-projects/2023-24-dfs-saves-2-507mwh-so-far)).
- **Evaluation of the 2022/23 season.** ERM and the Centre for Sustainable Energy analysed about 139,000 domestic customers ([NESO / ERM-CSE 2025](https://www.neso.energy/document/371411/download)):
  - The in-day adjustment was applied to 77% of customer-events, usually shifting the baseline down, and "often obscured true response".
  - Average delivery was **0.39 kWh per participating consumer per event**. A Centre for Net Zero study found 0.31 kWh.
  - About 52% of those who opted in actually reduced demand.
  - Over the whole event day, 62% of opted-in consumers *increased* demand. Post-event demand exceeded the baseline in 14 of 18 events, which indicates load shifting.
  - There was no systematic gaming. However, 60% of the top 1% of shifters moved load into the pre-event window.
  - Average reward was £1.19 per consumer per event.
- **Industry standard emerging.** The ENA/Elexon standardised baselining rule uses a "Recent History" baseline (worked example: 10 eligible days). Its accuracy thresholds are 10% Net % Error and 20% Absolute % Error. It warns that unrestricted nomination resubmission "introduces a material risk of gaming". It takes effect on 1 Apr 2026 ([Elexon FMR-SBM](https://www.elexon.co.uk/elexondocuments/about/consultations/2025-consultations/mf/fmr-sbm-standardised-baselining-methodologies/)).
- **Octopus Saving Sessions.**
  - Baseline: compared with average use at the same time over the previous 10 days, excluding other sessions. This comes from a secondary source ([householdmoneysaving.com](https://www.householdmoneysaving.com/?p=21619)).
  - Winter 2022/23: £5.3m paid, 1.86 GWh, 430 t CO2, over 700,000 signed up ([Octopus press, Jan 2024](https://octopus.energy/press/price-cap-protect-saving-sessions/)). That is about 2.7 kWh and £7.57 per sign-up across the winter, an implied 0.23 kg CO2/kWh **[derived]**.
  - Winter 2023/24 to January: 1.2m signed up, 397,000 average opt-ins per session, £4m paid, 1.41 GWh, 355 t CO2 ([Octopus](https://octopus.energy/press/price-cap-protect-saving-sessions/)).
- **DFS 2023/24 scale.** 2.2m signed up, and about 497 MWh per 1.5-hour live event ([Solar Power Portal](https://www.solarpowerportal.co.uk/solar-projects/2023-24-dfs-saves-2-507mwh-so-far)).

---

## 3. Evidence on what really saves

### 3.1 Smart meters, in-home displays and feedback

- **Early Learning Project (2015):** 2.3% electricity and 1.5% gas compared with traditionally metered customers. Durable savings of about 3% are judged "realistic" ([ELP Synthesis](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/407568/8_Synthesis_FINAL_25feb15.pdf)). BIT quotes the ELP electricity figure as 2.2% ([BIT 2019](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf)).
- **Advice changes the result.** A Northern Ireland trial of 200 low-income prepayment customers who also got in-home advice saved 10%. A broader trial with no advice saved 3% ([ELP Synthesis](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/407568/8_Synthesis_FINAL_25feb15.pdf)).
- **BIT meta-analysis (2023), 7 supplier studies:**

  | Estimate | Electricity | Gas |
  |---|---|---|
  | Pooled | −3.43% (95% CI −3.56% to −3.31%) | −2.97% (95% CI −3.08% to −2.86%) |
  | Robustness check | −2.61% | −2.43% |

  The cost-benefit analysis assumes 3.0% electricity and 2.2% gas for credit customers, and 0.5% gas for prepayment ([BIT/DESNZ 2023](https://assets.publishing.service.gov.uk/media/64831d59103ca60013039c7a/energy-supplier-review-of-smart-meter-energy-consumption-impacts.pdf)).
- **Apps vs IHDs.** Apps did not meet a 0.5% equivalence bar against IHDs. Supplier B's app users used 2.61% more gas ([BIT 2019](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf)).
- **Disaggregated feedback.** The participant-weighted saving is 4.5%, but likely biased upward. The population-level range is 0.7–4.5%. Aggregate feedback gives about 3% (Davis et al.) ([Kelly & Knottenbelt 2016](https://arxiv.org/pdf/1605.00962)).
- **Individualised audits and consulting** had the largest weighted average effect, about 13.5%. These are mostly uncontrolled studies ([Delmas et al. 2013](https://www.ioes.ucla.edu/wp-content/uploads/2017/07/2013-Delmas-Fischlein-Asensio-EnergyPolicy.pdf)).

### 3.2 Home energy reports (Opower)

- **Allcott (2011).** About 600,000 households; average saving 2.0%.
  - Top decile of prior use: −6.3%. Bottom decile: −0.3%.
  - Equivalent to an 11–20% short-run price rise ([SUFE summary of Allcott 2011](https://academicnewsletter.sufe.edu.cn/info/280278)).
  - In the Minnesota quarterly arm, effects faded between letters ([CEEPR](https://ceepr.mit.edu/workingpaper/social-norms-and-energy-conservation)).
- **The "1.4–3.3%" range** across programmes is **[unverified]**. A practitioner summary gives 1.5–2.5% in years 1–2 ([Cadmus 2017](https://insights.cadmusgroup.com/hubfs/Content%20on%20Insights%20Blog/Cadmus-%20HERs%20Program%20White%20Paper-2017.pdf)).
- **Allcott & Rogers (2014), persistence.** 3 sites, about 234,000 households ([AER pdf](https://toddrogers.scholars.harvard.edu/resource/allcottrogersaer2014pdf), [NBER](https://www.nber.org/papers/18492)):
  - First report: 1–1.3%. Year 2: about 3%.
  - After reports stop, effects decay **10–20% per year**.
  - About 58–60% of total savings arrive after the intervention ends.
  - Continuing the reports gives effects 50–60% stronger in years 3–5.
- **Cadmus planning figures.** Assume about 20% decay per year. Savings ramp up over 6–24 months. In one Connecticut programme, 83% of savings dissipated within 5 months of a 6-month programme ending ([Cadmus 2017](https://insights.cadmusgroup.com/hubfs/Content%20on%20Insights%20Blog/Cadmus-%20HERs%20Program%20White%20Paper-2017.pdf)).

### 3.3 Fabric and equipment measures (NEED)

- **2023 first-year median gas savings:**
  - Solid wall insulation: 16%.
  - Cavity wall plus loft insulation: 9%.
  - Scotland: condensing boiler 3%; solar PV 11% electricity.
  - Persistence to year 5: loft and boiler savings fall by about a tenth, PV by about a fifth ([NEED 2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf)).
- **Cavity wall insulation by cohort:** median savings of 5.7–11.5%, falling for later installation cohorts ([DESNZ Energy Trends, CWI](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/853563/Gas_consumption_savings_from_bead_and_mineral_wool_cavity_wall_insulation.pdf)).
- **Measured vs modelled.** The BRE solid-wall field trial (16 homes) measured 2,982 kWh against 4,079 kWh modelled, so **about 73% of the predicted saving was achieved** ([BRE 2016](https://assets.publishing.service.gov.uk/media/5c9234ca40f0b633f24d046c/Closing-the-gap_Pre-post-insulation-field-trial.pdf)). NEED itself publishes no modelled-vs-measured ratio.

### 3.4 Biases and offsets

- **Prebound.** Across 3,400 German dwellings, actual use was about 30% below calculated. For the least efficient homes it was about 40% below, so retrofits may deliver "only half the expected savings" ([Cambridge](https://www.cam.ac.uk/research/news/the-prebound-effect)).
- **Rebound.**
  - Direct rebound for space heating: best guess 10–30%, range 1–60% ([Sorrell, via CCCEP](https://www.cccep.ac.uk/wp-content/uploads/2015/10/rebound-effects-energy-efficiency.pdf)).
  - UK heating: 70% direct and 54% combined (Chitnis, Fouquet & Sorrell 2020) ([LSE Grantham](https://www.lse.ac.uk/granthaminstitute/publication/rebound-effects-for-household-energy-services-in-the-uk/)).
  - NEED notes that comfort-taking lowers metered savings ([NEED 2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf)).
- **Hawthorne effect.** Households that were merely told they were being studied cut electricity use by 2.7%, and "the gains vanished after the study finished" ([Schwartz et al., via Jackson Free Press](https://www.jacksonfreepress.com/news/2013/sep/06/energy-savings-simply-power-observation/)). Eight of 12 disaggregation studies did not control for it ([Kelly & Knottenbelt](https://arxiv.org/pdf/1605.00962)).
- **Boomerang.** In a descriptive-norm comparison, low users *increased* consumption. Adding an injunctive cue (a smiley face) largely removed this ([Schultz et al. 2007, via Bit by Bit](https://www.bitbybitbook.com/en/running-experiments/beyond-simple/)).

---

## 4. Attribution and defensible claims

### What confounds a measured saving

- **Weather.** Handled with HDD normalisation.
- **Price changes.** SENS flagged rising prices as a confounder ([SENS](https://assets.publishing.service.gov.uk/media/6480aa3cb32b9e000ca963a6/sens-overall-impact-evaluation-report.pdf)).
- **Life events, such as occupancy or an EV.** These are IPMVP non-routine adjustments **[unverified]**.
- **Load shifting** around flexibility events ([NESO/ERM](https://www.neso.energy/document/371411/download)).
- **Other programmes.** Under 5% of HER savings come from rebated measures, but credit must not be double-counted ([Cadmus](https://insights.cadmusgroup.com/hubfs/Content%20on%20Insights%20Blog/Cadmus-%20HERs%20Program%20White%20Paper-2017.pdf)).

**Only a randomised or matched comparison group separates the supplier's effect from these.**

### Rules and rulings on claims

- **Ofgem Standards of Conduct (SLC 0).** Information must be "complete, accurate and not misleading" and in "plain and intelligible language". Suppliers must understand vulnerable customers' needs ([Ofgem SoC draft 2023](https://www.ofgem.gov.uk/sites/default/files/2023-11/Draft%20Update%20to%20Standards%20of%20Conduct%20Guidance.pdf); [Ofgem SoC 2017](https://www.ofgem.gov.uk/system/files/docs/2017/10/standards_of_conduct.pdf)).
- **CMA Green Claims Code (2021).** Claims must be truthful and accurate; clear; must not omit material information; must make fair comparisons; must consider the full life cycle; and must be substantiated ([Linklaters](https://sustainablefutures.linklaters.com/post/102h6ul/uk-cma-publishes-green-claims-code-to-combat-greenwashing)).
- **ASA ruling on British Gas (4 Mar 2026).** The ad said "Save up to £546 with a heat pump" ([ASA](https://www.asa.org.uk/rulings/british-gas-services-ltd-a25-1295064-british-gas-services-ltd.html)). The ASA upheld the complaint:
  - An "up to" claim needs a significant proportion of customers to achieve it. Only **34% of 194** did.
  - Modelled status and assumptions must be stated in the ad itself.
  - Assumptions (Ofgem typical consumption, a D-rated boiler, coming off the SVT) must be representative of actual customers.
- **ASA ruling on Octopus (23 Apr 2025).** "Most homes would save" was misleading because the basis (SVT vs SVT only) was unstated. "Learn more" is not an adequate signpost to the substantiation ([ASA](https://www.asa.org.uk/rulings/octopus-energy-ltd-a24-1265573-octopus-energy-ltd.html)).

---

## 5. Showing savings to customers

- **Personalised £ savings drive action.** In CMOL, switching was 1% in the control group and 2.9% across letter arms; supplier-branded letters reached 3.4%. Interviewees cited the size of the saving as the main draw. Supplier A had mean potential savings of £293 and 4.5% switching; Supplier B had £203 and 2.3% ([Ofgem CMOL](https://www.ofgem.gov.uk/sites/default/files/docs/2017/11/cmol_report_slidepack_1.pdf)).
- **But money framing can backfire for conservation.**
  - In regressions, pecuniary feedback and incentives "lead to a relative increase in energy usage" ([Delmas et al. 2013](https://www.ioes.ucla.edu/wp-content/uploads/2017/07/2013-Delmas-Fischlein-Asensio-EnergyPolicy.pdf)).
  - Health and environment messages saved 8% vs control (19% in families with children) and outperformed money-saved messages ([Asensio & Delmas 2015, UCLA](https://www.ioes.ucla.edu/publication/nonprice-incentives-and-energy-conservation/)).
- **Social comparison.** It works mainly on high users (6.3% top decile vs 0.3% bottom; [Allcott 2011](https://academicnewsletter.sufe.edu.cn/info/280278)). Pair it with an injunctive cue to avoid the boomerang ([Schultz 2007](https://www.bitbybitbook.com/en/running-experiments/beyond-simple/)).
- **Always-on, calibrated feedback.**
  - IHDs beat apps partly because of always-on feedback that more household members used ([BIT 2019](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf)).
  - Traffic-light thresholds should be calibrated to each household's own range. A "monitoring" approach (trends and exceptions) beat an "information" approach ([ELP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/407568/8_Synthesis_FINAL_25feb15.pdf)).
- **Service units customers understand.** Customers "found [Warm Hours] much easier to understand" than kWh. Most could not work out the cost of heating per hour or week ([ESC SSH2](https://es.catapult.org.uk/report/ssh2-industry-insight-from-kilowatt-hours-to-warm-hours/)).
- **Gamified rewards.** Octopus uses points, streak bonuses and prize draws; the top 5% earned over £60 in winter 2023/24 ([Octopus](https://octopus.energy/press/price-cap-protect-saving-sessions/)). Engagement is very concentrated: about 1% of DFS consumers opted into every event, and 61% earned £0–£1 per event ([NESO/ERM](https://www.neso.energy/document/371411/download)).
- **OVO, British Gas, Ohme and Tesla app presentations:** not fetched. See Named gaps.

---

## 6. Sharing value

- **Heat as a Service (Bristol Energy / ESC Living Lab, about 100 homes).**
  - Plans were either a fixed price for a set number of Warm Hours, or pay-as-you-go per Warm Hour, each priced from the home's own thermal and room-by-room data.
  - 9 in 10 new customers continued, and half chose plans that included low-carbon heating ([ESC](https://es.catapult.org.uk/project/bristol-energy-heat-plan-trial/)).
  - No energy-saving figures were published.
- **Consumer protection risk.** Some participants did not understand the offer until after long use, and did not know who accessed their data ([Citizens Advice / ESC 2019](https://www.citizensadvice.org.uk/policy/publications/smarter-protections-using-field-trials-to-explore-how-people-understand-energy-as-a-service)).
- **Outcome contracts need an M&V protocol.** Aarschot used IPMVP against a 25% target ([DESNZ SMETER annex](https://assets.publishing.service.gov.uk/media/6a4790e28effd97622f53c04/smeter-case-studies-evidence-base-annex.pdf)). The proposed ECO PFP uses SMETERs ([DESNZ 2024](https://www.gov.uk/government/consultations/energy-company-obligation-4-and-the-great-british-insulation-scheme-mid-scheme-changes/eco4-and-gbis-mid-scheme-changes-options-assessment-published-and-updated-20-november-2024)).
- **Event-based sharing.** In DFS, NESO pays the supplier (for example a £3,000/MWh guaranteed acceptance price), and the supplier passes on £1–£6/kWh to households ([NESO/ERM](https://www.neso.energy/document/371411/download)).
- **Implication for Poesys.** Any savings-share must be paid on a baseline the customer can audit and cannot cheaply game. The DFS in-day adjustment is the counter-example.
- **Persistence changes the economics.** With observed persistence, HER cost per kWh is about 1.4¢, against about 3.3¢ assuming zero persistence ([Allcott & Rogers](https://toddrogers.scholars.harvard.edu/resource/allcottrogersaer2014pdf)).

---

## (a) Headline figures and bands

| Quantity | Band / value | Source |
|---|---|---|
| Smart meter + IHD saving, electricity | 2.3% (ELP), 2.6–3.4% (BIT meta), CBA assumption 3.0% | [ELP](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/407568/8_Synthesis_FINAL_25feb15.pdf), [BIT 2023](https://assets.publishing.service.gov.uk/media/64831d59103ca60013039c7a/energy-supplier-review-of-smart-meter-energy-consumption-impacts.pdf) |
| Smart meter + IHD saving, gas | 1.5% (ELP), 2.4–3.0% (BIT meta), CBA 2.2% (prepayment 0.5%) | same |
| Home energy report saving | ~2.0% average; 1–1.3% after first report; ~3% in year 2; 0.3–6.3% by decile | [Allcott 2011](https://academicnewsletter.sufe.edu.cn/info/280278), [Allcott & Rogers](https://toddrogers.scholars.harvard.edu/resource/allcottrogersaer2014pdf) |
| HER decay after stopping | 10–20%/yr (plan on ~20%) | [NBER](https://www.nber.org/papers/18492), [Cadmus](https://insights.cadmusgroup.com/hubfs/Content%20on%20Insights%20Blog/Cadmus-%20HERs%20Program%20White%20Paper-2017.pdf) |
| Controlled vs uncontrolled information studies | ~2% vs ~9.6% | [Delmas 2013](https://www.ioes.ucla.edu/wp-content/uploads/2017/07/2013-Delmas-Fischlein-Asensio-EnergyPolicy.pdf) |
| Measured / modelled, solid wall insulation | ~0.73 | [BRE 2016](https://assets.publishing.service.gov.uk/media/5c9234ca40f0b633f24d046c/Closing-the-gap_Pre-post-insulation-field-trial.pdf) |
| Prebound (actual / calculated) | ~0.70; ~0.60 for the least efficient homes | [Cambridge](https://www.cam.ac.uk/research/news/the-prebound-effect) |
| NEED median gas saving | SWI 16%; CWI 5.7–11.5%; CWI + loft 9% | [NEED 2025](https://assets.publishing.service.gov.uk/media/685bf0d30433072fce0e1000/need-report-june-2025.pdf), [CWI](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/853563/Gas_consumption_savings_from_bead_and_mineral_wool_cavity_wall_insulation.pdf) |
| Heating direct rebound | 10–30% best guess (UK estimate up to 70%) | [Sorrell](https://www.cccep.ac.uk/wp-content/uploads/2015/10/rebound-effects-energy-efficiency.pdf), [Chitnis](https://www.lse.ac.uk/granthaminstitute/publication/rebound-effects-for-household-energy-services-in-the-uk/) |
| Hawthorne effect | ~2.7%, non-persistent | [Schwartz](https://www.jacksonfreepress.com/news/2013/sep/06/energy-savings-simply-power-observation/) |
| Minimum detectable saving, one home (hourly data) | ~3.6% (90% confidence); monthly data needs ≥10% | [Kemper](https://aceee.org/sites/default/files/pdf/conferences/ie/2015/Session3C-Kemper-IE15-12.7.15.pdf) |
| 95% CI half-width, RCT | ±3.9% at ~400 per arm; ±1.4–1.8pp at ~2,760; ~±0.8pp at 10k; ~±0.25pp at 100k | [SENS](https://assets.publishing.service.gov.uk/media/6480aa3cb32b9e000ca963a6/sens-overall-impact-evaluation-report.pdf), [BIT](https://www.bi.team/wp-content/uploads/2020/10/smart-meters-in-home-displays-impacts-1.pdf); larger N **[derived]** |
| DFS delivery per household per event | 0.31–0.39 kWh | [NESO/ERM](https://www.neso.energy/document/371411/download) |
| Flexibility baseline error thresholds | 10% net / 20% absolute | [Elexon](https://www.elexon.co.uk/elexondocuments/about/consultations/2025-consultations/mf/fmr-sbm-standardised-baselining-methodologies/) |
| SMETER heat-loss (HTC) bias / scatter | NMBE −0.7% to −26.9%; CV(RMSE) 13.4–38.9% | [DESNZ annex](https://assets.publishing.service.gov.uk/media/6a4790e28effd97622f53c04/smeter-case-studies-evidence-base-annex.pdf) |
| "Up to" claims | "Significant proportion" must achieve it; 34% failed | [ASA BG](https://www.asa.org.uk/rulings/british-gas-services-ltd-a25-1295064-british-gas-services-ltd.html) |

## (b) What the simulation can do that a real supplier can't

Poesys knows each home's true counterfactual. It can therefore **grade the supplier's own M&V estimator** rather than trusting it. Suggested tests:

1. **Estimator bias and coverage.** For each method (deemed, pre/post HDD regression, CalTRACK-style, matched difference-in-differences, RCT), compute the estimated saving minus the true saving, per home and per portfolio.
   - Report NMBE, CV(RMSE), and 95% interval coverage. Target about 95%, given the 71% coverage seen in [arXiv 2607.25382](https://arxiv.org/pdf/2607.25382).
2. **Empirical minimum-detectable-saving curve.** Inject known savings of 1–10% into N = 1 to 100k homes. Find the N at which each method detects them 80% of the time.
   - Check the result against the 3.6% single-home figure and the 1/√N rule above.
3. **Deemed-score gap.** Compare deemed or modelled savings with the true savings by measure. Check the ratio lands near 0.7 (BRE / prebound).
   - Compare the ratio between initially high- and low-consuming homes. That tests whether the prebound mechanism is in the model.
4. **Confounder stress tests.** Inject a cold winter, a price shock, an EV arrival, a new baby or a home-working shift. Measure how much of each is wrongly credited to advice when there is no control group.
5. **Rebound, Hawthorne and persistence ground truth.**
   - Log comfort-taking explicitly and check whether metered estimates recover it.
   - Run a "told you're observed" arm.
   - Stop the advice and check whether the decay estimate falls within 10–20%/yr.
6. **Flexibility baseline gaming.** Simulate agents that know the baseline rule (10-day average, with or without in-day adjustment). Measure the gap between paid and true delivery, and whether the baseline stays inside the 10% net / 20% absolute error limits.
7. **Claim audit.** For every "you saved £X" message, record the true saving. A claim passes if, for example, the true saving is at least the claimed saving for a "significant proportion" of recipients (ASA test). Count false-credit and false-blame rates.
8. **Value-share fairness.** Pay the share on the estimated saving vs the true saving. Measure systematic over- or under-payment by segment (prepayment, vulnerable, low users).

## (c) Design rules for a savings claim shown to a customer

1. **Label the evidence class**: "estimated" (deemed or modelled), "measured, your home" or "measured, homes like yours". Never present a modelled number as measured ([ASA BG](https://www.asa.org.uk/rulings/british-gas-services-ltd-a25-1295064-british-gas-services-ltd.html)).
2. **Show the baseline and its basis** in the message itself, not behind "learn more" ([ASA Octopus](https://www.asa.org.uk/rulings/octopus-energy-ltd-a24-1265573-octopus-energy-ltd.html)).
3. **Show a range when uncertainty is wider than the claim.** Below about 4% (hourly data) or 10% (monthly data) for a single home, say "too small to measure reliably for one home" or quote the cohort result ([Kemper](https://aceee.org/sites/default/files/pdf/conferences/ie/2015/Session3C-Kemper-IE15-12.7.15.pdf)).
4. **Normalise for weather and say so.** A raw bill comparison is not a saving.
5. **"Up to" only if a significant share of customers really achieve it**, validated against actual installs before publication.
6. **Lead with personal, concrete units**: £ and warm hours for engagement, carbon as a secondary frame. Do not rely on money framing alone for conservation ([Delmas](https://www.ioes.ucla.edu/wp-content/uploads/2017/07/2013-Delmas-Fischlein-Asensio-EnergyPolicy.pdf), [Asensio](https://www.ioes.ucla.edu/publication/nonprice-incentives-and-energy-conservation/), [ESC](https://es.catapult.org.uk/report/ssh2-industry-insight-from-kilowatt-hours-to-warm-hours/)).
7. **Comparisons with similar homes need an injunctive cue for low users**, so they do not drift upward ([Schultz](https://www.bitbybitbook.com/en/running-experiments/beyond-simple/)). Comparisons must be like-for-like (CMA principle 4).
8. **Count only net savings for flexibility events.** Net out load moved to the hour after the event, since post-event demand exceeded the baseline in 14 of 18 events ([NESO/ERM](https://www.neso.energy/document/371411/download)).
9. **Show cumulative savings, decay-adjusted.** Do not keep crediting a one-off action at full value forever.
10. **Make it auditable and plain-language** (SLC 0), and check for vulnerable customers that the claim doesn't push them into under-heating.

## (d) Named gaps

- **Not fetched, because the domain was blocked or the search budget ran out:**
  - CalTRACK technical specification (baseline length, data sufficiency, model forms).
  - EVO IPMVP text.
  - ASHRAE G14 fractional-savings-uncertainty clause.
  - LBNL M&V 2.0 acceptance criteria.
  - ECO in-use factor values.
  - Allcott & Kessler on the welfare effects of nudges.
- **No fetched source for:** the exact Opower 1.4–3.3% cross-programme range; Gillingham's rebound review; Ofgem rules specific to *estimated savings* in sales (beyond SLC 0's general principles).
- **No fetched evidence on how OVO, British Gas, Ohme or Tesla apps present savings**, and no RCT on the believability or trust of "you saved £X" messages. Citizens Advice trust material was not reached.
- **NEED publishes no formal modelled-vs-measured ratio.** The 0.73 figure rests on a 16-home BRE trial.
- **No UK published DFS baseline-accuracy figure** (error vs true counterfactual). Only qualitative evidence that the in-day adjustment "obscured" the response.
- **No GB heat-as-a-service result with measured savings**, and no evaluated GB savings-share tariff.
- **No GB evidence on SMETER data duration requirements** or on pay-for-performance outcomes.
- **Nesta:** the fetched page gave only modelled flexible-tariff savings ("up to £650", Cornwall Insight), not measured results ([Nesta](https://www.nesta.org.uk/project/testing-tools-to-help-households-flex-their-energy-tariffs/)).

A follow-up session with fresh search budget could close the CalTRACK, IPMVP, G14 and supplier-app gaps.