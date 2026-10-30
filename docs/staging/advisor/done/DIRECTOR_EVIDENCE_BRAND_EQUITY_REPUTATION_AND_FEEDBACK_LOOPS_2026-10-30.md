**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Brand equity, reputation and feedback loops for a GB energy supplier (2026-10-30)

**Type:** EVIDENCE, through the advisor channel, for `DIRECTOR_STEER_REPUTATION_IS_A_STOCK_AND_THE_SUPPLIER_LISTENS_THROUGH_BIASED_FEEDBACK_2026-10-30.md`. It is an advisor research pass, web-sourced. Every key figure is graded P (primary), S (secondary) or A (assumption). [lit] marks an academic reference that was not re-read in this session. Apply the data standard of 30 Oct, 16:51 GMT: verify against the primary source, and re-derive from the underlying data wherever it is published.

---

# Evidence pack: brand equity, reputation, and feedback loops for a simulated GB domestic energy supplier

**Prepared for:** the Poesys simulation director
**Scope:** Parts A–E as briefed
**Search budget used:** 25 web searches, plus about 30 direct page fetches

## How to read this pack

**Grades (applied to key figures):**
- **P**: a primary publication by the data holder, for example an Ofgem survey report, a Citizens Advice methodology page, a Centrica annual report, a Trustpilot profile page or an Ofgem enforcement notice.
- **S**: a secondary summary, such as press coverage, commentary or a vendor blog.
- **A**: an assumption or derivation of mine. Every A-grade value says how it was derived.

**Tags:**
- **[unverified]**: I could not confirm the claim from a primary or reputable source in this session.
- **[lit]**: a standard academic reference cited from the established literature. A DOI or publisher link is given, but the page was not fetched this session, so the specific numbers attributed to it should be checked before they are relied on. Treat [lit] as a milder form of [unverified]: the source exists and is reputable, but I did not re-read it this session.

**Headline findings, short version:**
1. The evidence supports the *shape* of the director's hypothesis but not its *sign everywhere*. Overcharging is followed by large account losses with roughly one-year lags (British Gas lost about 1.38m accounts in 2017 and 742k in 2018). Operational failures leave long tails in satisfaction rankings (ScottishPower is still bottom of the Ofgem and Which? measures about ten years after its 2013–15 billing failures). Against this, the 2023 forced-prepayment scandal did *not* visibly dent British Gas's whole-base satisfaction: it was the *only* large supplier with a significant satisfaction *rise* by January 2025. Reputational damage concentrated on a vulnerable minority may not propagate to the base.
2. **Inertia, not trust, is what keeps overcharged customers.** In 2021 only 38% trusted their own supplier to charge a fair price, yet the leading reason for not switching was "current supplier is satisfactory". The resentment-ledger model fits this: low trust accumulates without crossing the churn threshold until a trigger arrives, such as a price rise, a bill shock or a price-comparison prompt.
3. **Public review platforms are a heavily mediated signal.** Octopus's Trustpilot distribution (90% 5-star, 3% 1-star) closely mirrors its Ofgem survey satisfaction (89% satisfied, 3% dissatisfied). British Gas's (66% 5-star, 20% 1-star) shows about 4× more negativity than its survey dissatisfaction (6%). The supplier's invitation policy decides how far reviews track hidden satisfaction.
4. There is **no published GB energy-supplier data** on survey response rates, and no published churn-hazard elasticity with respect to satisfaction. These parameters must be A-grade, anchored on academic analogues.

---

## Part A. Theory, briefly

### A1. Goodwill as a stock: Nerlove–Arrow and advertising carryover

- **Nerlove & Arrow (1962)** model advertising as investment in a stock of goodwill G that depreciates at a constant rate δ: dG/dt = a(t) − δG. Demand depends on G as well as on price. This is the canonical formal statement of the director's "brand equity as a stock" idea. It implies that the effect of today's behaviour (positive or negative) persists with an exponential half-life of ln2/δ. Source: Nerlove & Arrow, "Optimal Advertising Policy under Dynamic Conditions", *Economica* 29(114), 1962, https://doi.org/10.2307/2551549 [lit]. Grade: P (model, not a parameter).
- **Leone (1995)** reconciled inconsistent carryover estimates by correcting for temporal-aggregation bias. He supports the generalisation that "the average advertising duration interval is of brief duration—typically between six and nine months." https://ideas.repec.org/a/inm/ormksc/v14y1995i3_supplementpg141-g150.html. Grade: **P** (academic generalisation, abstract fetched).
- **Clarke (1976)** is the earlier meta-analysis. It is commonly reported as finding that 90% of the cumulative advertising effect dissipates within about 3–15 months, and that published estimates depend on the data interval. *Journal of Marketing Research* 13(4), https://doi.org/10.2307/3151027 [lit] [unverified for the exact range].
- **Derived decay rate (A).** If the "duration interval" is read as the time for 90% of the effect to dissipate under geometric decay, then λⁿ = 0.1:
  - n = 6 months gives monthly retention λ ≈ 0.68 (half-life about 1.8 months).
  - n = 9 months gives λ ≈ 0.77 (half-life about 2.7 months).
  - Grade A, derived from Leone's range above.
  - **Caution:** this is the decay of *advertising-induced* goodwill for mostly fast-moving consumer goods. Reputation built from service experience and public scandal is plausibly much slower (see C and E).

### A2. Reputation economics: Shapiro (1983)

- Shapiro shows that when buyers cannot observe quality before purchase, a firm's reputation for quality earns a **price premium above cost**. That premium is the return on the firm's earlier investment in building the reputation, and it is what makes "milking" the reputation (cutting quality while charging the premium) a real temptation. The equilibrium needs the premium to exceed the one-off gain from cheating. "Premiums for High Quality Products as Returns to Reputations", *Quarterly Journal of Economics* 98(4), 1983, https://doi.org/10.2307/1881782 [lit]. Grade: P (theory).
- **Simulation reading.** Overcharging is the energy-retail form of milking. The model predicts a short-run profit gain followed by a loss of the premium once customers update their view. The *speed* of that update depends on how observable the overcharge is. Energy is a hard case: bills are complex and tariffs are hard to compare, so updating is slow. That is consistent with the director's delayed-depletion idea.

### A3. Customer-based brand equity (Keller)

- Keller (1993) defines customer-based brand equity as "the differential effect of brand knowledge on consumer response to the marketing of the brand". Brand knowledge comprises awareness and an image of favourable, strong and unique associations. Positive CBBE shows up as lower price elasticity, greater tolerance of price rises, higher response to communications and easier brand extension. "Conceptualizing, Measuring, and Managing Customer-Based Brand Equity", *Journal of Marketing* 57(1), https://doi.org/10.1177/002224299305700101 [lit]. Grade: P (framework).
- This maps directly onto the director's four outcome channels: churn, acquisition, price tolerance and advice/product uptake.

### A4. The service–profit chain: satisfaction, retention, profit

- Heskett et al. (1994) link internal service quality, employee satisfaction, customer satisfaction, loyalty, growth and profit. "Putting the Service-Profit Chain to Work", *Harvard Business Review*, https://hbr.org/2008/07/putting-the-service-profit-chain-to-work [lit].
- Reichheld & Sasser (1990) report that a 5-percentage-point cut in defections raised profits by 25–85% across the service industries they studied. "Zero Defections", *HBR*, https://hbr.org/1990/09/zero-defections-quality-comes-to-services [lit] [unverified for the exact range]. Grade S: practitioner study, not peer-reviewed.
- **Asymmetry and non-linearity** are the most useful findings for the simulation:
  - Bolton (1998), studying a continuous-service provider (cellular), found that duration of the relationship depends on cumulative prior satisfaction. Customers with longer tenure weight prior satisfaction more heavily, and negative experiences weigh more than positive ones. https://doi.org/10.1287/mksc.17.1.45 [lit].
  - Mittal, Ross & Baldasare (1998) find that negative attribute-level performance has a disproportionately larger effect on overall satisfaction and repurchase than positive performance. https://doi.org/10.1177/002224299806200104 [lit].
  - Mittal & Kamakura (2001) show that the satisfaction-to-repurchase link is non-linear and differs by customer characteristics, with thresholds. https://doi.org/10.1509/jmkr.38.1.131.18832 [lit].
- At firm level, Anderson, Fornell & Mazvancheryl (2004) find that customer satisfaction (ACSI) is positively associated with shareholder value (Tobin's q). https://doi.org/10.1509/jmkg.68.4.172.42723 [lit].

### A5. Trust as an asset

- Morgan & Hunt's commitment-trust theory (1994) treats trust and commitment as the key mediating variables of relationship marketing. They reduce propensity to leave and increase cooperation. https://doi.org/10.1177/002224299405800302 [lit].
- In GB energy, Ofgem's own survey separates **trust to treat you fairly** from **trust to charge a fair price**. They differ by 7 points (45% vs 38% for one's own supplier in 2021; see B4) https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf (P). That supports modelling **two trust dimensions** (fairness or competence vs price) rather than one.

### A6. The loyalty-penalty paradox

- Citizens Advice's 2018 super-complaint estimated that loyal customers in five markets (mobile, broadband, home insurance, mortgages, savings) lose **£4.1bn a year**, about **£877 per affected household**. It found **8 in 10** people pay a significantly higher price in at least one market for staying, and **89%** think this is wrong. Energy was excluded because of the forthcoming price cap, which the same release says would cut loyal customers' bills by £75 a year on average. https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-issues-super-complaint-as-loyal-customers-continue-to-be-penalised-by-over-4-billion-a-year/ (P).
- The CMA's response is at https://www.gov.uk/government/news/cma-tackles-loyalty-penalty-charges (P, not fetched in detail).
- **The paradox for the model.** Overcharged customers stay because of hassle, inertia, low expected gain and fear of things going wrong, not because they trust the supplier. In GB banking, the CMA found that "over half" see switching as a hassle and "over 40%" fear something may go wrong. Over half are "very satisfied" with their bank, and a substantial share pay above-average prices for below-average service. https://assets.publishing.service.gov.uk/media/57a8c0fb40f0b608a7000002/summary-of-final-report-retail-banking-investigation.pdf (P).
- In energy, the 2021 Ofgem survey shows the most common reason for not switching was "existing supplier/tariff satisfactory" (42%), even though only 38% trusted their supplier to charge a fair price (P, link above).
- **Implication.** Low trust and high retention can coexist for years. The ledger's churn threshold needs a *trigger* (salience) term, not only an accumulated level.

---

## Part B. Energy supplier brand equity in GB

### B1. Attributes customers value, and their measured importance

GB has no single published "attribute importance" study that covers all of price fairness, trust, competence, service, ease, green credentials, simplicity and local identity. The best available proxies are the following.

**(a) Revealed reasons for choice (Which?, Sep–Oct 2025, n = 11,985).** Of those who actively chose their supplier:
- **45%** did so for a lower price than they were paying;
- **33%** chose it for its **good reputation**.

Source: https://www.which.co.uk/policy-and-insight/article/power-struggle-which-reveals-the-best-and-worst-suppliers-as-switching-returns-to-the-energy-market-aUK0I6Z8w7Yn (P). This is the most direct GB evidence that reputation is an acquisition lever of roughly the same order as price.

**(b) Reasons for dissatisfaction (Ofgem/Citizens Advice, BMG, January 2025).** Among the 6% dissatisfied:
- **46%** cited prices;
- **12%** cited poor customer service, the next highest reason.

Source: https://www.ofgem.gov.uk/sites/default/files/2025-05/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20-%20January%202025_0.pdf (P). Price fairness dominates the negative pole.

**(c) Regulator and watchdog weightings.** These are normative weights, not measured importance.

*Citizens Advice star rating:*

| Component | Weight |
|---|---|
| Complaints to third parties | 35% |
| Ease of contact (total) | 30% |
| – of which average call wait | 18% |
| – of which email response | 6% |
| – of which other channels | 6% |
| Billing and metering (total) | 25% |
| – of which billing accuracy | 15% |
| – of which smart-meter operation | 10% |
| Customer commitments | 10% |

- Complaints are banded per 10,000 customers, from ≤5 (score 5) to >80 (score 0.5).
- Call wait is banded from <30s (score 5) to >300s (score 1).
- Billing accuracy is banded from >98% (score 5) to <90% (score 1).
- **No trust or customer-survey component is included.**

Source: https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/ (P).

*Which? 2025 overall score:* 50% customer survey and 50% Which? assessment. The assessment weights are:

| Assessment component | Weight |
|---|---|
| Complaints performance | 30% |
| Supporting customers who need it | 25% |
| Contacting your supplier | 25% |
| Switching | 10% |
| Smart meters | 10% |

Which? Recommended Provider status needs an overall score of at least 70% and at least 3 stars in every customer-survey category (P, Which? link above).

**(d) Non-price preferences.** In a field study of more than 7,000 real switching offers ("The Big Switch"):
- just over a quarter of consumers offered a positive saving accepted it;
- even with savings above **£300/year**, only about half switched;
- non-price preferences, including a supplier's ethical or environmental stance, kept some consumers with more expensive suppliers.

Deller, Giulietti, Loomes, Waddams Price et al., *Energy Journal* 42(3), 2021. Executive summary: https://iaee.org/ej/ejexec/ej42-3-Waddams-exsum.pdf (P); repository copy: https://centaur.reading.ac.uk/91919. This is the cleanest GB evidence of **price tolerance driven by non-price attributes**, including green credentials.

**(e) Green credentials, simplicity, local identity.** No measured GB importance weights were found this session [unverified]. Treat these as A-grade segment preferences.

### B2. Measured levels by supplier

**Ofgem Energy Consumer Satisfaction Survey, January 2025 (BMG; n = 3,854 plus 481 boost; ±1.6%)**
Source: https://www.ofgem.gov.uk/sites/default/files/2025-05/Customers%27%20satisfaction%20with%20their%20supplier%20-%20supplier%20level%20findings%20-%20January%202025.pdf (P)

| Supplier | Overall satisfied | Overall dissatisfied | Customer service satisfied | Customer service dissatisfied |
|---|---|---|---|---|
| GB average | 81% | 6% | 74% | 7% |
| Octopus | **89%** (sig. higher) | 3% | **81%** | 3% |
| Utilita | 84% | 5% | 74% | 9% |
| British Gas | 80% | 6% | 75% | 7% |
| E.ON / E.ON Next | 76% (sig. lower) | 7% | 71% | 7% |
| OVO | 75% (sig. lower) | 6% | 67% (sig. lower) | 9% |
| EDF | 74% (sig. lower) | 7% | 66% (sig. lower) | 6% |
| ScottishPower | **72%** (sig. lower) | **11%** (sig. higher) | **63%** | **13%** |

British Gas was the only supplier group with a significant *increase* in overall and customer-service satisfaction since July 2024 (P, same source). Ofgem's report notes some text/table inconsistencies in the dissatisfaction figures.

**Which? 2025 overall scores** (https://www.which.co.uk/policy-and-insight/article/power-struggle-which-reveals-the-best-and-worst-suppliers-as-switching-returns-to-the-energy-market-aUK0I6Z8w7Yn, P):

| Supplier | Overall score | Notes |
|---|---|---|
| E (Gas & Electricity) | 79% | 86% would recommend |
| Octopus | 74% | |
| 100Green | 72% | 94% would recommend |
| Sainsbury's Energy | 71% | |
| Co-op Energy | 71% | |
| Outfox | 71% | |
| British Gas | 59% | 2 stars across the survey |
| EDF | 58% | 2 stars across the survey |
| ScottishPower | 56% | 2 stars across the survey; fewest complaint-handling points |

**UKCSI (Institute of Customer Service), July 2025.** Utilities score **71.7**, up 1.9 points year on year, the **lowest of 13 sectors** and about 5.6 points below the all-sector average. Octopus, UK Power Networks and Utility Warehouse were the top-rated utilities for satisfaction; Octopus was highest on NPS. The survey covered 59,500 customer experiences. https://www.instituteofcustomerservice.com/?p=207191 (P).
- In 2015, utilities were also bottom, with OVO top in the sector (13th overall) and the lowest loyalty index of any sector. https://www.cxnetwork.com/cx-service-support/articles/news-utilities-companies-imrprove-customer-satisfaction-but-still-rank-lowest-of-all-industries (S).
- Utilities have been the bottom-ranked UKCSI sector for at least a decade. That is a **sector-level brand-equity deficit**.

**Spread narrowing over time.** Littlechild, using Citizens Advice scores:
- the average was 65% across 18 suppliers in 2023, the same as across 26 suppliers in October 2019;
- the standard deviation fell from **13 to 8**;
- no supplier scored above 80% (five had in 2019);
- 16 of 18 sat in the 60–79% range.

Source: https://www.eprg.group.cam.ac.uk/wp-content/uploads/2023/09/Professor-Stephen-Littlechild-11-September-2023_Energy-Spectrum-1.pdf (S). Post-2021 consolidation removed many of the tails.

### B3. Change over time (sector satisfaction)

- Ofgem overall satisfaction was **78% (July 2024)** and **81% (January 2025)**, the highest since tracking began in 2018 (P, Ofgem January 2025 findings report above).
- Customer-service satisfaction was **62% (Aug/Sep 2023)**, 71% (July 2024) and 74% (January 2025) (P, same source).
- The share experiencing at least one contact difficulty fell from **63% (Aug/Sep 2023)** to **47% (January 2025)** (P).
- Read together, this is a recovery from the crisis-era trough (2022–23) over about 18 months. It is a useful **sector recovery timescale** (see E).

### B4. Trust in the sector and in one's own supplier

| Measure | Value | Source and grade |
|---|---|---|
| Own supplier treats you fairly (2021, pre-crisis) | 45% (engaged 48%, disengaged 42%) | Ofgem Consumer Survey 2021, Ipsos, n = 4,037. https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf (P) |
| Own supplier charges a fair price (2021) | 38% | same (P) |
| Energy sector treats customers fairly (2021) | 34%, "broadly unchanged from 2020" | same (P) |
| Own supplier treats fairly (later Ofgem research, date not given) | 60% | Utility Week summary of Ofgem research, https://staging4.utilityweek.co.uk/customer-trust-in-own-energy-suppliers-increases/?amp=true (S); original not located [unverified] |
| Sector trust (same) | 36% | same (S) |
| "No longer trust energy companies" | 34% (2022) rising to 48–49% (2023) | Eco Experts National Home Energy Survey, n = 2,134. https://www.theecoexperts.co.uk/news/trust-in-energy-companies (S; commercial survey, non-comparable wording) |

**Stylised fact:** trust in one's *own* supplier runs about 10–25 points above trust in the *sector*. That supports separating a **portfolio reputation index** from a **sector or category trust** that applies to all suppliers, small entrants included. Ofgem also observes that high trust may increase *inertia* among disengaged consumers (P, 2021 report). In other words, trust can *reduce* engagement, which matters for advice uptake.

---

## Part C. Quantified effects of reputation, satisfaction and complaints

### C1. Churn, with lags

**British Gas / Centrica, 2017–2018: overcharging, then delayed losses**
- 2018: UK energy account holdings fell by **742,000**. The Chairman attributed this to "two price increases during 2018". Market switching was at record levels, mostly to smaller suppliers. https://www.centrica.com/media/1112/annual_report_2018.pdf (P). Also reported at https://www.rte.ie/news/business/2019/0221/1031865-centrica-annual-results (S).
- The same report says losses were **634,000 lower than in 2017**, despite two SVT rises in 2018 against one in 2017. That implies 2017 net losses of about **1.38m accounts** (grade A, derived). This matches the press figure of about **1.4m accounts / ~750k households** lost in 2017 https://www.pressreader.com/uk/daily-mail/20180223/281973198137661 (S).
- **Brand NPS was flat** in 2018 against 2017. Energy-supply complaints fell 1%. Cost to serve per Home customer *rose* 10%, partly because of lower account holdings (P, Centrica AR 2018). A shrinking base raises unit cost, which is a second-order cost of brand depletion.
- **Lag structure (A).** Losses followed SVT rises within the same reporting year, so lags of months are visible at annual resolution. They also persisted into the following year despite stable NPS. This looks like a *stock* effect: customers who had silently become "at risk" over several price rounds exited when switching became salient (price-cap debate, record switching, cheap challengers).
- Account-base denominator: about 12–13m energy accounts in 2018 [unverified], so 742k is about 6% of the base per year (A).

**npower: billing-system failure, then losses, sale and brand exit**
- A new IT system was introduced in 2011. Between September 2013 and December 2014 there were **over 500,000** late bills and **over 2 million complaints**. Ofgem required a **£26m** redress package and threatened to halt domestic sales and advertising if targets were missed by June 2016. https://ofgem.gov.uk/press-release/npower-pay-ps26m-failing-treat-customers-fairly (P).
- About **200,000** customers left in 2015, alongside a £48m loss in the first nine months. https://www.yorkshirepost.co.uk/news/200000-customers-desert-npower-watchdog-hits-it-ps26m-fine-1807254 (S).
- The planned 2018 merger of npower with SSE retail was abandoned; E.ON acquired npower through the RWE/innogy asset swap (2019–20); npower customers were migrated to E.ON Next and the npower retail brand retired [unverified; Wikipedia surfaced but was not fetched: https://wikipedia.com/wiki/Npower_UK].
- **Timescale (A):** a failure that went live in 2011, peaked in 2013–14 and ended with the brand gone by about 2020–21 is roughly 7–9 years from operational shock to brand exit.

**ScottishPower: 2013–15 billing and contact failures, with a long tail**
- There were over **1 million complaints** between June 2013 and December 2015, and over **300,000** late final bills. Thousands of Ombudsman rulings were not implemented within 28 days. Ofgem **stopped proactive selling for 12 days in March 2015**. The penalty was **£18m**, with up to £15m to vulnerable customers. https://ofgem.gov.uk/publications-and-updates/scottishpower-pay-18m-customer-service-failings (P).
- **About ten years later**, ScottishPower is the lowest-satisfaction large supplier in the Ofgem survey (72% satisfied, 11% dissatisfied, January 2025; P, link in B2). It has 2 stars across the Which? customer survey and the fewest complaint-handling points (P, Which? 2025).
- **Caution:** this persistence may reflect continuing operational weakness rather than *memory* of 2015. It is evidence that **low rank is sticky**, not that reputational damage has a ten-year half-life.

**Satisfaction and switching in the Ofgem tracker.** In January 2025:
- 8% switched supplier and 17% switched tariff with the same supplier in the past year;
- satisfaction was 83% among supplier switchers, 87% among internal tariff switchers and 79% among non-switchers.

Source: https://www.ofgem.gov.uk/sites/default/files/2025-05/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20-%20January%202025_0.pdf (P). Switching rates were **27% in 2021 and 31% in 2020** (pre-crisis), against 24% in 2019 and 14% in 2014 (P, Ofgem 2021 engagement report). Ofgem's figures are cross-sectional and say nothing about churn hazard *by* satisfaction level. **This is a key gap.**

**Academic anchor for churn hazard by satisfaction.** Bolton (1998) estimates the effect of cumulative satisfaction on relationship duration for a continuous-service provider. Losses are weighted more than gains, and long-tenure customers rely more on prior satisfaction [lit] https://doi.org/10.1287/mksc.17.1.45. De Haan, Verhoef & Wiesel (2015) compare CSAT, NPS and Customer Effort Score as predictors of retention across 18 Dutch industries, reportedly including energy. They find the metrics broadly similar in predictive power, with top-box and "top-2-box" transformations performing well [lit] [unverified for the detail] https://doi.org/10.1016/j.ijresmar.2015.02.004.

**Banking analogue (low hazard despite gains).** Only **3%** of GB personal current account customers switched in the last year, and 8% over three years. Over half had been with their bank more than 10 years. About 90% could gain about **£92/yr** by moving to one of the five cheapest products. https://assets.publishing.service.gov.uk/media/57a8c0fb40f0b608a7000002/summary-of-final-report-retail-banking-investigation.pdf (P). PPI mis-selling (redress of roughly £38bn across the sector [unverified]) is the canonical example of large, lasting trust damage that coexisted with very low current-account switching.

**Telecoms analogue.** Ofcom publishes annual "Comparing customer service" reports on satisfaction, complaints and loyalty-penalty end-of-contract notifications. Citizens Advice responses are at https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-response-to-ofcoms-announcement-on-end-of-contract-notifications/ (P, not read in detail). Specific Ofcom churn-by-satisfaction figures were not obtained [unverified].

### C2. Acquisition, conversion and cost of acquisition

- **Reputation as a choice driver:** 33% of active choosers chose for good reputation, against 45% for lower price (Which? 2025, P).
- **Octopus as the high-satisfaction case:**
  - Nearly **1 million** customers switched to Octopus from other suppliers in 2024 ("one every 30 seconds").
  - It now serves **7.3m households** and is the largest UK supplier at about **24% share** (Cornwall Insight via Octopus).
  - Group net margin was **0.7%** on £12.4bn revenue.
  - It holds Which? Recommended Provider status for the 8th year and a Trustpilot score of 4.8.
  - Source: https://octopus.energy/press/octopus-energy-group-results-for-fy24-delivered-07-profit-margin-tripled-non-uk-customer-base-and-increased-net-assets-to-17bn/ (P).
  - Much of the scale came from acquisitions: Avro 2021, Bulb 2022 (1.6m customers per NAO) and Shell Energy Retail in December 2023 (1.3m migrated in under three months) (P, same release; analysis at https://davidturver.substack.com/p/peak-pink-octopus, S). **Organic and acquired growth are not separated in any source found** [gap].
- **Referral economics.** Octopus says it has paid "**nearly £100 million**" in referral rewards over about eight years. Current rewards are £100 to the referrer and £100 discount or credit to the referee for heat pumps and solar. https://octopus.energy/press/Octopus-hands-out-100m-to-customers-in-energy-referral-payments/ (P). Historical energy-supply rewards were around £50 per side [unverified]. At £50–£100 per side, £100m implies roughly **0.5–1.0m successful referrals** over eight years (A), or about 60–125k per year. Bulb also grew on a referral scheme [unverified]. No source gives the share of new customers from referrals [gap].
- **Octopus is not "low advertising".** Google's case study reports that Octopus doubled its Google Ads spend, saw clicks rise about 9× and sales about 5×, and cut **cost per acquisition by 36%** after moving from target CPA to target ROAS bidding. Google Ads is its largest digital sales channel. https://ads.google.cn/intl/en_uk/home/resources/success-stories/octopus-energy (S; vendor case study, no absolute CPA). **Do not assume high-NPS suppliers have negligible paid acquisition.** Assume instead that reputation *lowers CPA and raises conversion* on paid channels.
- **Absolute CPA for GB energy** (often quoted in industry at about £30–£100 per dual-fuel customer via price-comparison sites) [unverified]: no primary source found.

### C3. Price premium and tolerance of price rises

- **Theory:** Shapiro's reputation premium (A2) and Keller's lower price elasticity (A3) [lit].
- **GB evidence:** Deller et al. 2021 found that at savings above £300/yr only about half switched, and that ethical or green preferences keep some on more expensive suppliers (P, link in B1). Both inertia and brand preference create *tolerance*, but the study does not separate them.
- **Counter-evidence: tolerance can be inertia, not equity.** British Gas kept a large SVT book at a premium for years (the "loyalty penalty") and then lost accounts fast once switching became salient (C1). In banking, a "substantial proportion" pay above-average prices for below-average service (P, CMA banking summary). **Tolerance without equity is fragile tolerance**: modelling it as low-trust inertia plus a salience trigger is better supported than treating it as brand equity.
- **Price cap context (2019 onward):** the cap compresses SVT premia, so price tolerance now shows up mostly in fixed-tariff spreads and in retention offers (A).

### C4. Response to supplier communications and advice

- Satisfaction with information from the supplier was **84%** in January 2025, up from 75% in January/February 2024 (P, Ofgem January 2025 report).
- Customers who fell behind or ran out of credit reported **72%** satisfaction with support, against 10% dissatisfied (P).
- Ofgem notes that high trust may *increase* inertia among disengaged consumers (P, 2021 report). That is a caution that trust raises *acceptance* of supplier advice but not necessarily *action* on it.
- **No GB study was found that links supplier reputation to uptake of advice or products** (smart meters, heat pumps, flexibility, time-of-use tariffs) [gap]. The Octopus referral programme extending into heat pumps and solar suggests reputation and network effects are being used to sell products (P, Octopus press above), but there is no effect size.

### C5. GB events: delayed or durable effects, with timescales

| Event | Shock | Observed outcome | Lag / duration | Grade |
|---|---|---|---|---|
| British Gas SVT rises, 2017–18 | 1 rise in 2017, 2 in 2018 | about −1.38m (2017) and −742k (2018) accounts; brand NPS flat | Within year, persisting into a 2nd year | P (Centrica AR 2018) |
| npower billing IT, 2011–15 | 500k late bills, 2m complaints | about −200k customers in 2015; loss-making; sold and brand retired | about 7–9 years shock to exit | P / S / [unverified] |
| ScottishPower IT, 2013–15 | 1m complaints; 12-day sales ban | Still lowest satisfaction in 2025 | about 10 years of low rank (causation unclear) | P |
| Supplier failures, 2021–22 | 28 failures plus Bulb; 2.4m via SoLR; £2.7bn (about £94/customer) | Market consolidated; Citizens Advice score spread narrowed (SD 13 to 8) | 2–3 years | P (NAO https://www.nao.org.uk/press-release/the-energy-supplier-market/); S (Littlechild) |
| British Gas / Arvato forced PPM, Feb 2023 | Media exposé; warrant installs suspended | Centrica shares −3% on the day https://morningstar.co.uk/uk/news/231508/centrica-feels-heat-after-outrageous-british-gas-meter-saga.aspx (S). Ofgem settlement May 2026: £20m to the Voluntary Redress Fund plus up to £70m debt write-off; failings flagged in 2018 and 2021 reviews. https://www.ofgem.gov.uk/press-release/british-gas-agrees-settlement-relation-ofgems-investigation-unfair-treatment-prepayment-meter-customers (P). Sector-wide PPM compensation £73.6m across eight suppliers (P, same). **BG base satisfaction rose significantly to 80% by Jan 2025** (P) | Regulatory tail about 3 years; **no visible base-satisfaction tail** | P |
| Crisis 2022–23 | Price spike, contact failures | Customer-service satisfaction 62% (2023) to 74% (2025); distrust 34% to 49% (2022 to 2023) | Recovery about 18 months | P / S |

**Effect of the 2021 failures on trust in small suppliers.** No primary survey isolating trust in small or new suppliers was found [gap]. Proxy: 28 failures plus Bulb put 2.4m customers through Supplier of Last Resort at a mutualised cost of about £94 per customer (P, NAO). Ofgem tightened financial resilience rules in 2021 (P, NAO). In simulation terms, this is a **category-level trust shock to "entrant" suppliers**, separate from any one supplier's index (A).

---

## Part D. Feedback mechanisms and response bias

### D1. What GB suppliers measure

- **Brand NPS:** Centrica reports "Brand NPS" in its annual report, flat in 2018 against 2017 (P, Centrica AR 2018).
- **NPS league tables:** UKCSI publishes NPS by organisation, with Octopus highest in utilities (P, ICS 2025). Which? reports "would recommend" (E: 86%, 100Green: 94%) (P).
- **Transactional NPS, CSAT and CES** are widely used in GB energy contact centres [unverified]. **No supplier-published response rates were found** [gap].
- **Regulatory feedback:** Ofgem/Citizens Advice's BMG survey is a quota online panel with a face-to-face element (n ≈ 3,854; P). Which? surveys about 12k people via Deltapoll (P). These are *not* supplier-invited and are the least self-selected benchmark.

### D2. Trustpilot for energy suppliers

| Item | Octopus Energy | British Gas |
|---|---|---|
| TrustScore | 4.8 | 4.4 |
| Total reviews | 909,090 | 360,288 |
| Reviews, last 12 months | 209,134 | 54,959 |
| 5★ / 4★ / 3★ / 2★ / 1★ | 90% / 5% / 1% / <1% / 3% | 66% / 8% / 3% / 3% / 20% |
| Invites reviews | Yes ("whether positive or negative") | Yes |
| Paid subscription / claimed | Yes, since Feb 2016 | Yes, since May 2014 |
| Reply to negative reviews | 97%, within about 1 week | 99%, within about 24 hours |
| Source | https://uk.trustpilot.com/review/octopus.energy (P) | https://uk.trustpilot.com/review/www.britishgas.co.uk (P) |

**Observations:**
- **Shape:** both are **J-shaped** (mass at 5★, a secondary mode at 1★, a hollow middle). British Gas is markedly *bimodal*.
- **Solicited vs organic:** reviews are labelled "Invited" or "Unprompted", but **Trustpilot does not publish the proportion** (P, profile pages). Littlechild noted that ScottishPower's 2023 TrustScore rise of 10% came with reviews that were "organic rather than invited" (S, EPRG link above). That suggests invitation policy varies across suppliers and over time.
- **Calibration against the hidden-satisfaction proxy (Ofgem survey, January 2025):**
  - Octopus: survey 89% satisfied / 3% dissatisfied, against Trustpilot 95% 4–5★ / about 3–4% 1–2★. Close agreement.
  - British Gas: survey 80% / 6%, against Trustpilot 74% 4–5★ / 23% 1–2★.
  - British Gas's review-negativity is **about 3.8×** its survey dissatisfaction; Octopus's is **about 1.2×** (A, derived).
  - **Interpretation (A):** heavy, unselective invitations after routine interactions pull the review distribution toward the true distribution (Octopus). A larger organic or complaint-driven inflow inflates the negative mode (British Gas, with services and boiler-repair reviews possibly mixed in).
- **Review incidence (A):** Octopus 209k reviews/yr over 7.3m households is about **2.9%** of households per year. British Gas 55k/yr over an assumed base of about 7m households [unverified] is about **0.8%**.

### D3. Extremity and self-selection bias: the evidence

- **Hu, Pavlou & Zhang (2009)**, "Overcoming the J-shaped distribution of product reviews", *CACM*:
  - on Amazon, 78% of book, 73% of DVD and 72% of video ratings are 4★ or higher;
  - when subjects were *randomly assigned* to rate the same CD, the distribution was **unimodal** (only 3% gave 5★ and 7% gave 1★), and its mean was significantly below Amazon's;
  - they attribute the J-shape to **purchasing bias** (those who value the product less don't buy) plus **under-reporting bias** (moderates don't review; people review "to brag or complain").
  - Source: https://cacmb4.acm.org/magazines/2009/10/42353-overcoming-the-j-shaped-distribution-of-product-reviews (P).
- **Schoenmueller, Netzer & Stahl (2020)**, *Journal of Marketing Research*:
  - over **280 million reviews across 25 platforms** show an extreme, predominantly positive distribution;
  - its prevalence depends on how selective customers are about reviewing;
  - the main driver is **polarity self-selection** (people with extreme experiences review);
  - it reduces review informativeness; less selective, frequent reviewers are more representative.
  - Sources: https://papers.ssrn.com/abstract=3100217 (P, abstract); https://business.columbia.edu/press-release/cbs-press-releases/why-online-reviews-are-mainly-positive-and-often-do-not-reflect (S).
- **Purchasing-bias analogue in energy:** the customer chose the supplier, and dissatisfied customers can leave. Survivors skew positive, which is the same selection Hu et al. describe (A).

### D4. Response rates to post-interaction surveys

- **No reputable published benchmark was found for GB energy** [gap]. A practitioner source reports one client's 22% response rate and argues there is no "healthy" threshold. It notes that frequent survey requests leave mainly those "motivated by a particularly good or bad experience" responding, and that post-support surveys over-sample people who had problems. https://greatbrook.com/?p=913 (S).
- Commonly quoted practitioner ranges for email tNPS/CSAT are about 5–15%, and about 20–40% for in-app or IVR immediately after the interaction [unverified].
- **Shape (A, anchored on D3):** response probability is U-shaped in satisfaction. The negative arm is driven by grievance and the positive arm by engagement, and the arms are steeper for *unsolicited* channels than for *solicited* ones.

### D5. Do NPS and review scores predict churn? For and against

- **For:** Reichheld (2003) claimed NPS ("likelihood to recommend") was the single best predictor of growth across most industries. https://hbr.org/2003/12/the-one-number-you-need-to-grow [lit]. Satisfaction predicts relationship duration in continuous services (Bolton 1998 [lit]). Firm-level satisfaction predicts shareholder value (Anderson et al. 2004 [lit]).
- **Against or qualified:**
  - Keiningham et al. (2007), with 17 Norwegian firms in 5 industries, found NPS the best or second-best predictor of revenue growth in only 2 of 5 industries. In retail gasoline r = −0.45 for NPS against 0.84 for top-2-box satisfaction. A reanalysis of Reichheld's data found NPS and ACSI statistically indistinguishable. "Satisfaction and NPS offer comparable predictive ability." https://measuringu.com/article-summaries/a-longitudinal-examination-of-net-promoter-and-firm-revenue-growth/ (S summary of P). Original: *Journal of Marketing* 71(3), https://doi.org/10.1509/jmkg.71.3.39 [lit].
  - De Haan et al. (2015): no single metric dominates for retention [lit].
  - **GB energy:** Centrica's brand NPS was *flat* in 2018 while it lost 742k accounts (P). That is direct evidence that **brand NPS did not lead churn** in this case. Churn was driven by price salience acting on a stock that NPS did not capture.
- **Simulation reading:** the feedback metrics should be *noisy, biased, lagging and partial* readings of the hidden state, correlated with churn but not sufficient for it.

### D6. How suppliers use feedback

- **Closed loop and reply practice:** Octopus replies to 97% of negative Trustpilot reviews within about a week, possibly with AI-drafted replies; British Gas replies to 99% within about 24h (P, Trustpilot pages). Root-cause analysis of complaints is a standard practice [unverified for named suppliers].
- **Regulatory complaint obligations:** complaint handling standards, Ombudsman referral after 8 weeks, and implementation of Ombudsman rulings within 28 days. Enforcement history: npower and ScottishPower (P, Ofgem links above).
- **Consumer side of the loop:** in 2015 UKCSI, 41% of utilities customers did not report problems because they felt it "would make no difference" (S, cxnetwork). This is a large *silent dissatisfaction* share and the strongest argument for modelling unobserved resentment.

### D7. The regulator's version of feedback

- **Energy Ombudsman:** **80,256** cases accepted in 2025, against **92,938** in 2024 (−14%). Billing is **56%** of disputes. Average supplier "signposting" to the Ombudsman is **48%** (range 25–68%). https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025 (P).
- **Citizens Advice star rating:** complaints to third parties per 10,000 customers, weighted 35% (P, B1).
- **Ofgem survey:** only about **2%** of respondents complained in the period (n = 89). Of those, **44%** were satisfied with handling and **50%** dissatisfied; **55%** were dissatisfied with time to resolution (P, Ofgem January 2025).
- **Pipeline (A):** friction leads to (silent | contact | complaint), then complaint leads to (resolved | unresolved > 8 weeks), then unresolved leads to Ombudsman. Each stage loses mass, and signposting varies by supplier from 25% to 68%.

---

## Part E. Simulation design implications

### E1. Parameter table

Every row is a calibration *starting point* with its evidential basis. "A" rows should be exposed as configurable and swept in sensitivity tests.

| # | Parameter | Suggested value / form | Evidence | Grade |
|---|---|---|---|---|
| 1 | **Advertising goodwill decay** (paid-acquisition stock) | Monthly retention λ ≈ 0.68–0.77 (half-life 1.8–2.7 months) | Leone 1995, 6–9 month duration interval; derivation in A1 | S/A |
| 2 | **Portfolio reputation index decay** (toward a baseline) | Half-life about 12–24 months; asymmetric: negative shocks decay slower than positive gains | No GB study. Bounds: sector service satisfaction recovered from its trough in about 18 months (B3); ScottishPower low rank persisted about 10 years (C1, confounded); BG/PPM showed no base tail (C5) | A |
| 3 | **Category or sector trust** (separate stock) | Own-supplier trust about 45–60%; sector about 34–36%; crisis shock about −15 points over 1 year (distrust 34% to 49%) | Ofgem 2021; Utility Week/Ofgem; Eco Experts | P/S/A |
| 4 | **Per-customer resentment decay** | Half-life about 3–9 months for ordinary friction; much slower (≥24 months) for "betrayal" events (wrongful PPM, debt pursued while disputed) | Bolton 1998 (prior satisfaction persists, more with tenure) [lit]; no GB data | A |
| 5 | **Friction event weights** (relative) | Unresolved complaint 1.0; billing error or late bill 0.7; failed contact or long wait 0.5; overcharge salience event (price rise above market) 0.8; negative events about 2× the weight of equal positive ones | Relative weights from the Citizens Advice scheme (complaints 35%, contact 30%, billing 25%); reasons for dissatisfaction (price 46%, service 12%); asymmetry from Mittal et al. 1998 [lit] | A (anchored on P) |
| 6 | **Overcharge to churn** | Calibration target: an incumbent with one or two above-market SVT rises per year loses about 6–10% of accounts per year in a high-switching market (BG 2017: about 1.38m; 2018: 742k on about 12–13m accounts) | Centrica AR 2018 | P (losses) / A (denominator, mapping) |
| 7 | **Churn hazard by resentment** | Logistic hazard h = h₀ · exp(β·R) · S(t), where S(t) is a salience multiplier (price-rise letter, fix expiry, comparison prompt, press coverage) of about 2–5×; irreversible exit above a threshold. Calibrate h₀ so annual supplier switching is about 8% (2025) to 27–31% (2020–21) | Ofgem switching 8% (2025), 27% (2021), 31% (2020); banking 3%/yr shows a low h₀ is possible with high inertia | P (targets) / A (form) |
| 8 | **Inertia floor** | About 25–50% of customers do not switch even at savings above £300/yr | Deller et al. 2021: about a quarter accept positive offers; about half at >£300 | P |
| 9 | **Recovery from good service** | Good resolution removes most of the resentment from the triggering event (about 60–80%) but creates *no surplus loyalty*. Recovery raises satisfaction, not repurchase | Service-recovery-paradox meta-analysis: effect on satisfaction but not on repurchase or WOM (de Matos, Henrique & Rossi 2007, https://doi.org/10.1177/1094670507303012) [lit] [unverified detail] | A/lit |
| 10 | **Reputation to acquisition conversion** | Reputation explains about a third of active choice (33% vs 45% price). Model conversion = f(price rank) × g(reputation) with g's elasticity about 0.4–0.7 of price's | Which? 2025 | P (shares) / A (elasticity) |
| 11 | **Reputation to CPA** | High-reputation supplier CPA about 30–40% below baseline on paid channels | Octopus CPA −36% after bidding change (confounded) | S/A |
| 12 | **Referral rate** | About 1–2% of the base produces a successful referral per year at £50–100/side for a top-NPS supplier (≈60–125k/yr on about 5–7m base); near zero for low-NPS suppliers | Octopus about £100m over 8 years (P) plus derivation | P/A |
| 13 | **Price tolerance** | Two components: (a) brand equity, where a high-reputation supplier holds about £30–80/yr premium with no extra churn; (b) inertia, which tolerates the premium until salience, then collapses | Deller (non-price preferences); CMA banking; loyalty penalty £877 average across five markets | P (qualitative) / A (magnitude) |
| 14 | **Trust to advice uptake** | Uptake ∝ trust × engagement; high trust among *disengaged* customers may reduce action (inertia) | Ofgem 2021 qualitative observation | P (qualitative) / A |
| 15 | **Complaint propensity** | P(complaint \| friction) about 0.1–0.3; about 41% of dissatisfied customers never report | UKCSI 2015; Ofgem 2% complained | S/P/A |
| 16 | **Ombudsman escalation** | Unresolved after 8 weeks, then P(Ombudsman) ≈ signposting rate (25–68%, mean 48%) × uptake about 0.2–0.4; billing about 56% of cases | Energy Ombudsman 2025 | P/A |
| 17 | **Survey response by satisfaction** (solicited) | Base about 8–15% email, about 25% immediate in-channel; U-shape with multiplier about 1.5–2× at the extremes against the midpoint | Greatbrook (S); Hu et al. 2009 (P) | A |
| 18 | **Unsolicited review propensity** | About 0.1–0.5%/yr of households at neutral; ×5–10 for strongly negative, ×2–3 for strongly positive (organic skew negative) | Hu et al.; Schoenmueller et al.; BG vs Octopus calibration | A |
| 19 | **Invited review propensity** | Invite after positive or routine interactions; response to invites about 3–10%; invited reviews carry the satisfaction distribution of the invited pool | Octopus about 2.9% of households/yr with near-survey-matching distribution | A |
| 20 | **NPS to churn predictive value** | Correlation with subsequent churn moderate; no better than CSAT; can be flat while churn spikes | Keiningham 2007; de Haan 2015; Centrica 2018 | S/P/lit |

### E2. Generating realistic feedback from the hidden state

**Hidden state per household i at time t:**
- `Sat_i(t)`: running satisfaction, on a 0–10 scale, a decayed function of recent experiences;
- `R_i(t)`: the resentment ledger (existing);
- `Tf_i(t)` and `Tp_i(t)`: trust in fairness or competence, and trust in a fair price (two dimensions, per Ofgem's split);
- `E_i`: engagement trait;
- `V_i`: vulnerability flag;
- `G(t)`: portfolio reputation index (existing);
- `C(t)`: category or sector trust.

**1. True attitude.** Let `A_i = Sat_i − κ·R_i + γ·(Tf_i + Tp_i)/2 + ε`, mapped to 0–10. Calibrate so that the population share with A ≥ 7 roughly matches Ofgem "satisfied" (about 75–89% by supplier type) and A ≤ 3 matches "dissatisfied" (3–11%).

**2. Solicited surveys (NPS, tNPS, CSAT, CES).**
- *Triggers:* tNPS or CSAT after a contact, a bill or a switch; relationship NPS on a periodic sample.
- *Invitation:* the supplier chooses the policy, either "all contacts" or "resolved contacts only". The second is a selection bias the supplier controls and should be tempted to use.
- *Response:* P(respond) = r₀ · (1 + a·|A_i − 5|^k) · (0.5 + E_i), with r₀ about 0.08–0.15, a about 0.1, k about 1.5 (A). Add *fatigue*: r₀ falls with the number of invites in the last 90 days (Greatbrook S).
- *Answer:* NPS score = round(A_i + transaction-specific shock + noise). The transaction-specific shock (for example the agent effect) makes tNPS more volatile than relationship NPS.
- *What the supplier sees:* NPS = %9–10 − %0–6 among *respondents*. That is biased upward if resolved-only invitations are used and polarised at low response.

**3. Unsolicited public reviews (Trustpilot-like).**
- *Organic hazard:* h_org = b₀ · (1 + c₋·max(0, 4 − A_i)² + c₊·max(0, A_i − 8)²) with c₋ > c₊ (complaints are the main organic driver). Spike it on events: a bill shock, a failed complaint, an Ombudsman referral or media coverage. That gives bursts like ScottishPower's July–August 2023 (S, Littlechild).
- *Invited hazard:* if the supplier invites, h_inv = invite rate × P(accept | A_i), with acceptance rising in A_i.
- *Star mapping:* stars = clip(round((A_i − 1)/2) + noise, 1, 5) with fat extremes, giving a J-shape.
- *Public score:* a recency-weighted mean with a Bayesian prior. Trustpilot's exact TrustScore method has not been verified here [unverified].
- *Reply loop:* the supplier's reply to a negative review reduces that reviewer's R_i by a small amount if a resolution follows (rule 9). It has no effect on onlookers beyond a small rise in G.

**4. Public score to the world.** The public review score and the Which? or Citizens Advice style composite feed *prospects'* conversion (row 10) and G(t). Hidden satisfaction feeds churn. **The supplier only ever observes the biased measures.** That is the imperfect loop the director wants.

**5. Regulator channel.** An independent panel draws a stratified random sample of n ≈ 4,000 per wave, half-yearly. It gives an *unbiased but noisy* (±1.6 points) reading of satisfaction by supplier and is published with a lag. A Citizens Advice style star rating is computed from complaints per 10,000, call waits, billing accuracy and so on, published quarterly. This is the closest thing the simulation has to ground truth that is visible to all.

**6. Sanity checks against GB data.**
- A high-service supplier's invited-review distribution should look like about 90/5/1/1/3 with survey dissatisfaction about 3%.
- A legacy incumbent with organic complaint inflow should look like about 66/8/3/3/20 with survey dissatisfaction about 6%.
- Brand NPS can stay flat while annual churn runs at 6–10%.

### E3. Structural recommendations

1. **Split the stock.** Keep a fast-decaying advertising-goodwill stock (row 1) separate from a slow reputation index (row 2). Also add a **category trust** stock (row 3) that is hit by sector events (2021 failures, the 2022 crisis) for all suppliers, and especially entrants.
2. **Add salience triggers to churn.** The British Gas evidence and the loyalty-penalty literature show resentment accumulating silently and *crystallising* at triggers. Without triggers the model will over-predict smooth churn.
3. **Segment-local reputation damage.** The PPM case suggests scandals affecting vulnerable minorities need not reach whole-base satisfaction (BG rose to 80%). Model scandal effects as a hit to G that hurts **prospects and regulators** more than **existing customers**, with direct ledger hits only for affected households.
4. **Two trust dimensions.** Treat price fairness and treatment fairness separately: price drives dissatisfaction (46% of reasons), service drives the star ratings.
5. **Make invitation policy a supplier decision variable** with a regulatory or platform penalty for selective invitations. That creates the "gaming the feedback" dynamic.

### E4. Gaps (what no primary source in this session provided)

1. **Churn hazard as a function of satisfaction or trust for GB energy households.** No published elasticity was found. Ofgem data are cross-sectional. Candidate: Ofgem or Citizens Advice microdata, or supplier panel data.
2. **Decay or half-life of reputational damage in energy.** No event study was found. A candidate method is to estimate it from Ofgem satisfaction waves (2018–2025) around enforcement events, or from Centrica and SSE account series.
3. **Survey response rates** (tNPS, CSAT, CES) for any GB supplier, and response by satisfaction level.
4. **Share of invited and organic Trustpilot reviews** by supplier. Trustpilot labels individual reviews but publishes no aggregates. It could be estimated by scraping a sample of review labels.
5. **Cost of acquisition** in absolute £ by channel (price-comparison sites, paid search, referral) for GB energy.
6. **Referral share of gross adds** for Octopus or Bulb.
7. **Effect of the 2021 supplier failures on trust in small suppliers:** no direct survey found.
8. **Link between reputation and uptake of advice or products** (smart, time-of-use, heat pumps, flexibility).
9. **British Gas customer-number trajectory 2022–2025** and any churn attributable to the 2023 PPM scandal. Centrica 2023/24 reports were not fetched [unverified].
10. **npower's end-state facts** (brand retirement date, migration numbers) [unverified].
11. **Ofcom telecoms satisfaction-to-churn figures** and **PPI trust-recovery timescales** in banking [unverified].
12. **The Ofgem trust series after 2021**: the 60% / 36% figures come via Utility Week, and the original Ofgem publication and date were not located.
13. **Importance weights for green credentials, simplicity and local identity.**

---

## Source index (fetched this session; grade in brackets)

**Ofgem and Citizens Advice**
- Ofgem Energy Consumer Satisfaction Survey, January 2025, findings report: https://www.ofgem.gov.uk/sites/default/files/2025-05/Energy%20Consumer%20Satisfaction%20Survey%20%E2%80%93%20Findings%20Report%20-%20January%202025_0.pdf [P]
- Ofgem supplier-level findings, January 2025: https://www.ofgem.gov.uk/sites/default/files/2025-05/Customers%27%20satisfaction%20with%20their%20supplier%20-%20supplier%20level%20findings%20-%20January%202025.pdf [P]
- Ofgem Consumer Survey 2021, Engagement report: https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf [P]
- Ofgem npower £26m: https://ofgem.gov.uk/press-release/npower-pay-ps26m-failing-treat-customers-fairly [P]
- Ofgem ScottishPower £18m: https://ofgem.gov.uk/publications-and-updates/scottishpower-pay-18m-customer-service-failings [P]
- Ofgem British Gas PPM settlement (May 2026): https://www.ofgem.gov.uk/press-release/british-gas-agrees-settlement-relation-ofgems-investigation-unfair-treatment-prepayment-meter-customers [P]
- Citizens Advice star-rating methodology: https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/ [P]
- Citizens Advice loyalty-penalty super-complaint: https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-issues-super-complaint-as-loyal-customers-continue-to-be-penalised-by-over-4-billion-a-year/ [P]

**Other public bodies and independent ratings**
- Which? 2025 best and worst suppliers: https://www.which.co.uk/policy-and-insight/article/power-struggle-which-reveals-the-best-and-worst-suppliers-as-switching-returns-to-the-energy-market-aUK0I6Z8w7Yn [P]
- Institute of Customer Service UKCSI, July 2025 (utilities): https://www.instituteofcustomerservice.com/?p=207191 [P]
- Energy Ombudsman annual data 2025: https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025 [P]
- NAO, The energy supplier market: https://www.nao.org.uk/press-release/the-energy-supplier-market/ [P]
- CMA retail banking final report summary: https://assets.publishing.service.gov.uk/media/57a8c0fb40f0b608a7000002/summary-of-final-report-retail-banking-investigation.pdf [P]

**Companies and platforms**
- Centrica Annual Report 2018: https://www.centrica.com/media/1112/annual_report_2018.pdf [P]
- Octopus FY24 results: https://octopus.energy/press/octopus-energy-group-results-for-fy24-delivered-07-profit-margin-tripled-non-uk-customer-base-and-increased-net-assets-to-17bn/ [P]
- Octopus referral payments: https://octopus.energy/press/Octopus-hands-out-100m-to-customers-in-energy-referral-payments/ [P]
- Trustpilot, Octopus Energy: https://uk.trustpilot.com/review/octopus.energy [P]
- Trustpilot, British Gas: https://uk.trustpilot.com/review/www.britishgas.co.uk [P]

**Academic**
- Deller et al. 2021, *Energy Journal* (executive summary): https://iaee.org/ej/ejexec/ej42-3-Waddams-exsum.pdf [P]
- Leone 1995: https://ideas.repec.org/a/inm/ormksc/v14y1995i3_supplementpg141-g150.html [P]
- Hu, Pavlou & Zhang 2009: https://cacmb4.acm.org/magazines/2009/10/42353-overcoming-the-j-shaped-distribution-of-product-reviews [P]
- Schoenmueller, Netzer & Stahl (SSRN abstract): https://papers.ssrn.com/abstract=3100217 [P]
- Keiningham et al. 2007 (MeasuringU summary): https://measuringu.com/article-summaries/a-longitudinal-examination-of-net-promoter-and-firm-revenue-growth/ [S]

**Secondary commentary and press**
- Littlechild, Energy Spectrum (September 2023): https://www.eprg.group.cam.ac.uk/wp-content/uploads/2023/09/Professor-Stephen-Littlechild-11-September-2023_Energy-Spectrum-1.pdf [S]
- Google Ads Octopus case study: https://ads.google.cn/intl/en_uk/home/resources/success-stories/octopus-energy [S]
- Utility Week, trust in own supplier: https://staging4.utilityweek.co.uk/customer-trust-in-own-energy-suppliers-increases/?amp=true [S]
- Eco Experts trust survey: https://www.theecoexperts.co.uk/news/trust-in-energy-companies [S]
- Yorkshire Post, npower losses: https://www.yorkshirepost.co.uk/news/200000-customers-desert-npower-watchdog-hits-it-ps26m-fine-1807254 [S]
- Morningstar, Centrica PPM reaction: https://morningstar.co.uk/uk/news/231508/centrica-feels-heat-after-outrageous-british-gas-meter-saga.aspx [S]
- Greatbrook, survey nonresponse bias: https://greatbrook.com/?p=913 [S]
- CX Network, UKCSI 2015: https://www.cxnetwork.com/cx-service-support/articles/news-utilities-companies-imrprove-customer-satisfaction-but-still-rank-lowest-of-all-industries [S]
- Daily Mail via PressReader, British Gas 2017 losses: https://www.pressreader.com/uk/daily-mail/20180223/281973198137661 [S]
- RTÉ, Centrica 2018 results: https://www.rte.ie/news/business/2019/0221/1031865-centrica-annual-results [S]
- David Turver, "Peak Pink Octopus": https://davidturver.substack.com/p/peak-pink-octopus [S]

**[lit] references, not fetched this session**
- Nerlove & Arrow 1962: https://doi.org/10.2307/2551549
- Clarke 1976: https://doi.org/10.2307/3151027
- Shapiro 1983: https://doi.org/10.2307/1881782
- Keller 1993: https://doi.org/10.1177/002224299305700101
- Morgan & Hunt 1994: https://doi.org/10.1177/002224299405800302
- Heskett et al. 1994: https://hbr.org/2008/07/putting-the-service-profit-chain-to-work
- Reichheld & Sasser 1990: https://hbr.org/1990/09/zero-defections-quality-comes-to-services
- Reichheld 2003: https://hbr.org/2003/12/the-one-number-you-need-to-grow
- Bolton 1998: https://doi.org/10.1287/mksc.17.1.45
- Mittal, Ross & Baldasare 1998: https://doi.org/10.1177/002224299806200104
- Mittal & Kamakura 2001: https://doi.org/10.1509/jmkr.38.1.131.18832
- Anderson, Fornell & Mazvancheryl 2004: https://doi.org/10.1509/jmkg.68.4.172.42723
- Keiningham et al. 2007: https://doi.org/10.1509/jmkg.71.3.39
- de Haan, Verhoef & Wiesel 2015: https://doi.org/10.1016/j.ijresmar.2015.02.004
- de Matos, Henrique & Rossi 2007: https://doi.org/10.1177/1094670507303012

---

**Notes for the main session:**
- Nothing in this pack came from the user's memory.
- Ofgem's British Gas PPM settlement is dated 15 May 2026, which is recent relative to most other sources.
- Ofgem's January 2025 report has small inconsistencies between its text and tables on billing and dissatisfaction figures. They are noted where used.
## Done

Moved here unread on 2026-10-30 at 17:50Z by the seat executor. The advisor channel refused it at
draw time: it has no attribution. It does not say it acts "on the director's standing delegation of
15 Oct", and it does not quote his chat words with the time, so it carries no authority. The steer
beside it, `DIRECTOR_STEER_REPUTATION_IS_A_STOCK_AND_THE_SUPPLIER_LISTENS_THROUGH_BIASED_FEEDBACK_2026-10-30.md`,
quotes him (16:53 and 16:59 GMT) and names this pack as its evidence. When that steer is worked, this
pack is read there as evidence to verify, not as an instruction.
