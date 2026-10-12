# Do GB domestic energy debtors offered a repayment plan take it up, and keep to it?

**Knowledge:** none -- no knowledge page covers supplier debt and collections; the nearest, price-cap, carries the bad-debt ALLOWANCE and not how a household answers a plan offer

**2026-10-04, delivery seat (web research by a search sub-agent, read and graded here).** Asked for
the EP4 collections journey (`company/billing/collections_journey.py`), which since `49ce42e6c`
records a plan OFFER on SLC 27.8's step but has no world answer to it. Starts from
`company_debt_management.md` s.2 and `gb_domestic_bill_payment_failure_and_arrears_prevalence.md`
(d), which hold the stock figures below and are not repeated beyond what the verdict needs.

## What is being asked, before any figure

Three different quantities, and none of them is the stock share Ofgem publishes:

1. **Take-up** -- a FLOW over offers: of households offered an arrangement, the share that agree one.
2. **Keeping** -- a FLOW over agreed plans: of instalments due (or of plans, over a horizon), the
   share paid; equivalently a breakage hazard per period.
3. **The stock share** -- at a quarter end, accounts repaying under an arrangement over all accounts
   >91 days owing. This is what IS published. It is the product of take-up, keeping, plan length
   and arrears spell length together, and cannot be divided back into any one of them without an
   unpublished model of the other three.

## Verdict

| Quantity | Status | Evidence |
|---|---|---|
| Take-up of an offered plan | **NOT ESTABLISHED.** No published rate found. | none of the sources below reports offers made; agreements are counted only by one supplier (EDF, 251,000 in 2023) with no denominator, and the stocks do not bound it (below) |
| Share of instalments / plans kept, or a breakage hazard | **NOT ESTABLISHED as a per-instalment rate. ESTABLISHED, 2012-2015 only, as an annual share of customers with at least one failed repayment** (section below). | Suppliers report failed arrangements to Ofgem quarterly (SOR Q3.6-Q3.27), but Ofgem publishes only end-of-quarter stocks; no published flow of plans started, completed or broken |
| Stock share of >91-day debtors on an arrangement | ESTABLISHED (as a stock) | Q2 2026: 888,824 electricity accounts "repaying a debt" (2.9%) against 1,187,788 "in arrears" with no arrangement (4.0%) -- Ofgem, *Debt and arrears indicators*, https://www.ofgem.gov.uk/data/debt-and-arrears-indicators, read 2026-10-04 |
| Share of debt VALUE held with no plan | ESTABLISHED (as a stock of GBP) | "75% sits with customers who are not on repayment plans" -- Ofgem, *Debt strategy -- a 'reset' and 'reform' for customers in debt*, Dec 2024, https://www.ofgem.gov.uk/sites/default/files/2024-12/Debt_Strategy_(5).pdf (read in full with `pdftotext`, 2026-10-04). The NAO's "only 25% of total customer debt ... is held by customers who have repayment plans in place" is the same quantity |
| Share of repaying customers using a PPM | ESTABLISHED (as a stock) | "typically ranged between around 30% and 40% over the last 15 years" -- Ofgem, *Debt and arrears indicators* |

**Why the stock shares are not a take-up rate.** 2.9 / (2.9 + 4.0) = 42% of >91-day debtors are on
an arrangement at a quarter end. That counts households whose plans have lasted years (Ofgem's
average length AGREED for a prepayment meter installed for debt in calendar 2025 is 365 weeks,
electricity, and 342 gas -- *corrected 2026-10-04: this line first called it the average plan
duration, but the published chart covers new PPM-for-debt installs only, not plans in force and not
credit-account plans*) against debtors who may never have been
offered one, and excludes everyone whose plan broke and who fell back into arrears, and everyone
who agreed and cleared inside 91 days. Using 42% as a take-up probability would be choosing a
number because a number was needed.

## Every named source, read to the end (2026-10-04, second pass)

*The first pass left three sources unread. All three are now read in full: the two Ofgem PDFs are
Word exports with a text layer, which `pdftotext` extracts whole (the fetch tool, not the file, was
the obstacle), and the 403 was read from the Internet Archive's copy. Nothing here needed OCR.*

| Source | Read | What it gives | Why it does not answer |
|---|---|---|---|
| Ofgem, *Debt strategy*, Dec 2024, https://www.ofgem.gov.uk/sites/default/files/2024-12/Debt_Strategy_(5).pdf | 16 pp, full text | the 75% unplanned debt value (Fig. 1, from the indicators); "repayment plans as long as 10 years"; 69% satisfied with supplier support (Energy Consumer Satisfaction Survey, Jul 2024) | stocks and satisfaction, no flow of offers, agreements or breaks |
| Ofgem, *Affordability and debt in the domestic retail market -- call for input*, Mar 2024, https://www.ofgem.gov.uk/sites/default/files/2024-03/Affordability%20and%20debt%20in%20the%20domestic%20retail%20market%20-%20call%20for%20input.pdf, and its Dec 2024 response document | full text, both | the policy frame; no repayment-plan rate in either | no take-up, keep or break figure |
| Citizens Advice, written evidence COE0077 (*The cost of energy*, Apr 2025), https://committees.parliament.uk/writtenevidence/140192/pdf/ -- still 403 direct; read via http://web.archive.org/web/20251123030801/https://committees.parliament.uk/writtenevidence/140192/pdf/ | 7 pp, full text | 6.7m people in households in debt to their supplier, GBP3.8bn; 92,000 helped with energy debt in 2024 | no figure on plans at all |
| Citizens Advice response to the 2024 call for input | full text | of consumers who spoke to their supplier after falling behind: 20% issue not resolved, 14% plan offered "didn't suit their needs"; 9% not asked what they could afford (Ofgem/Citizens Advice, *Energy Consumer Satisfaction Survey*, Aug-Sep 2023) | a dissatisfaction share among those who called, not a take-up rate: an unsuitable offer may still be accepted, and the denominator is callers, not offers |
| Money Advice Trust response to the 2024 call for input | full text | 21% of its surveyed clients said their supplier had not accepted an affordable repayment offer; EDF: "251,000 repayment plans" set up for residential customers in 2023, up 25% | the 21% is the SUPPLIER refusing the household's offer, the reverse direction; EDF's count has no denominator of offers or of debtors |
| Ofgem/Citizens Advice (BMG), *Consumers' experiences of debt and affordability support from suppliers*, Sep 2024 | full text | 31 qualitative interviews; one plan "worked well" (participant able to "stick to it") | qualitative, no rate by design |
| Ofgem, *Consumer Vulnerability Strategy: progress report*, Jul 2026 | full text | at end-2025, ~58% of customers behind on their bills were in arrears without a plan, up from ~49% at end-2020 (SOR data, Fig. 6) | the same stock ratio as below, as a time series; no flow |
| StepChange response to Ofgem, Oct 2019, https://www.ofgem.gov.uk/sites/default/files/docs/2019/10/stepchange_response.pdf | full text | the source of the 7% (gas) / 8% (electricity) of StepChange clients "set a repayment rate that I couldn't afford", 2016 and 2018 -- **now cited, superseding the uncited search synthesis the first pass refused**; 5-6% "offered a reduced payment plan" | an experience share among debt-advice clients, not a rate over offers |
| PFRC (Bristol)/StepChange, *Powering up support*, Oct 2025 | full text | of 256 StepChange clients with energy arrears: since contacting StepChange, 37% agreed a payment they felt affordable, 16% agreed a plan they felt unaffordable, 12% had debt written off | a selected population (people who reached debt advice), self-reported, no denominator of supplier offers; it cannot stand for a household at the supplier's SLC 27.8 step |
| Energy UK, *Energy debt: everyone pays*, Feb 2026 | full text | "nearly three fifths" of customers with unpaid bills not on a plan | the same stock |
| Ofgem, *Improving debt standards* consultation (OFG1164, Dec 2024); GSOP phase 1 report (Nov 2020); GSOP review call for input (Nov 2025); British Gas SLC 27.8 decision (Apr 2017) | full text, all four | GSOP's reconnection-within-24h of "agreeing a repayment plan"; the BG decision requires suppliers to monitor "credit customers' broken arrangements" | rules and remedies; no rate |
| Ofgem, *Domestic suppliers' social obligations: 2015 annual report*, its data annex, and the Oct 2016 event slides | full text, plus Figure 13 rendered as an image | the annual failed-repayment shares (section below); "around 30% of customers in debt on a repayment plan [at small and medium suppliers], compared to around 60% at large suppliers" (slides, p. 8) | a share of customer-years with a miss, not a per-instalment rate; the 30%/60% is a stock |
| Ofgem, *Social obligations reporting* guidance (Sep 2019) and its 2018 consultation | full text | **the reporting template.** Every quarter suppliers return, for non-PPM arrangements extending beyond 91 days: customers ENTERING an arrangement (Q3.1), the mean weekly amount (Q3.2), the mean weeks to recover (Q3.3), and, per weekly-amount band, the NUMBER OF FAILED ARRANGEMENTS (Q3.6, 3.9 ... 3.27). A failed arrangement is a payment not received in full within 10 working days of its date, counted once per customer per quarter, excluding active cancellation and early payment in full (guidance 2.31-2.33) | **the keep/break flow exists and the regulator holds it. Since this template replaced the one behind the 2015 figure below, the debt-and-arrears indicators page publishes only stocks, average balances, and PPM-for-debt length and weekly rate.** Neither the entry counts nor the failed-arrangement counts appear on it (read 2026-10-04) |

## The one published break figure: Ofgem 2012-2015, an annual share, not a per-instalment rate

Ofgem, *Domestic suppliers' social obligations: 2015 annual report* (Oct 2016),
https://www.ofgem.gov.uk/sites/default/files/docs/2016/10/social_obligations_report_2015.pdf,
paras 4.13-4.15 and **Figure 13**: "the proportion of electricity customers repaying a debt where
there has been at least one failed debt repayment in the year", by weekly-repayment band, for credit
(non-PPM) arrangements. A failure is a payment not received in full within 10 working days of its
date without prior agreement (SOR guidance 2.31). Figure 13 is a bar chart with no data table, so
the values below are READ OFF THE CHART (page 32, rendered and read 2026-10-04), +/- about 1pp:

| Electricity, share with >=1 failed repayment in the year | GBP0.01-2.99 | 3.00-5.99 | 6.00-8.99 | 9.00-11.99 | 12.00-14.99 | >15 |
|---|---|---|---|---|---|---|
| Large suppliers 2012 | 37% | 49% | 53% | 58% | 56% | 56% |
| Large suppliers 2013 | 30% | 36% | 39% | 42% | 45% | 47% |
| Large suppliers 2014 | 32% | 45% | 49% | 50% | 51% | 48% |
| Large suppliers 2015 | 23% | 38% | 38% | 40% | 41% | 41% |
| Medium suppliers 2015 | 42% | 58% | 71% | 53% | 45% | 26% |

Small suppliers 2015, in the text: "below 17% of customers ... in each category, with the exception
of customers paying over GBP15 per week, where 29%". Ofgem's own caveat (fn 38): "This data should
be interpreted with caution ... some suppliers may be interpreting this indicator incorrectly." The
same report's data annex
(https://www.ofgem.gov.uk/sites/default/files/docs/2016/10/monitoring_social_obligations_-_2015_annual_data_report.pdf)
publishes, by supplier, 2015 ENTRIES into credit arrangements (British Gas 156,616, E.ON 135,462,
EDF 134,408 electricity) and the mean weeks to recover a credit-arrangement debt (46, 96 and 77
weeks respectively), but no failure counts. After the 2019 template change no failure figure has
been published that this pass could find.

**Why this does not fill `instalment_keep_rate`.** The world's slot is a per-instalment probability.
The published figure counts customer-years with at least one miss. Under the world's own
independence simplification, `f = 1 - k^m`, and `m` (the payments a customer was exposed to in the
year) is unpublished twice over: the payment frequency (weekly, fortnightly or monthly) is not
reported, and the denominator does not say whether customers who entered or cleared mid-year count.
At the large-supplier 2015 mid-band f of about 0.40, `k` runs from 0.60 (one payment) through 0.958
(twelve monthly) to 0.990 (fifty-two weekly). Choosing a point in that range is choosing a number.
The figure is also a decade old, from a template since replaced, and carries the regulator's caution.
So the slot stays None. Its reason now names this figure, so whoever builds a plan-year breakage
model, which is the quantity actually published, starts from it.

**What it does establish for the world's design:** breakage is common, not marginal. Roughly two in
five large-supplier credit plans had a miss inside a year. It rises with the weekly amount, which
argues against simplification 1's one flat rate. And it differed by a factor of about two between
supplier tiers, which makes it a property of the supplier's ability-to-pay assessment as much as of
the household.

## Do the published stocks bound take-up? No, from either side

Write the steady state of the two published stocks (electricity, Q2 2026) as flow times stay:
`S_plan = lambda_plan * D_plan` (888,824 repaying) and `S_arrears = lambda_arrears * D_arrears`
(1,187,788 in arrears with no arrangement). Take-up is `p = lambda_plan_from_offers / N_offers`.

- `N_offers` is published nowhere. For any p in (0, 1], `N_offers = lambda_plan / p` reproduces both
  stocks exactly. That alone means no bound.
- Even granting that every arrears entrant is offered a plan (so `N_offers ~ lambda_arrears`),
  `lambda_arrears` needs `D_arrears`, the time spent in arrears without a plan, which is
  unpublished and can range from one quarter to never-ending. The ratio of the stocks (42% / 58%)
  fixes `lambda_plan * D_plan / (lambda_arrears * D_arrears)`, one equation in four unknowns.
- `D_plan` is not published as realised duration either. The 342/365 weeks are the length AGREED
  for new PPM-for-debt installs, and breakage and early clearance shorten realised plans. No length
  is published for credit-account plans, which is what the company offers.
- Plans agreed before 91 days enter `S_plan` without ever entering `S_arrears`, so the two stocks
  are not even one pipeline.

The value share (75% of GBP unplanned) adds an equation in average balances, not in flows, and does
not help. So the gap stands as an **established absence**: no published rate, no bound, and the
flow that would give the keep rate is collected by Ofgem and unpublished.

**The next place to look:** (1) the 2012-2014 and 2016 social-obligations reports, for the same figure
in other years and for gas (only 2015's was read); (2) the
quarterly SOR returns themselves -- reaching them means a request to Ofgem, which is a real-world
action under Poesys's name and is the director's, not this seat's; (3) the third side, a
practitioner: what share of debtors offered a plan at the SLC 27.8 step agree one, and how many
plans break in their first quarter.

## What the world does with this

*(Superseded 2026-10-12 by "The world's answer to an offer" at the end of this page: the world
now answers from labelled ranges when switched on, and still answers None as shipped.)*
`simulation/plan_offer_response.py` answers every plan offer with `accepted: None` and the reason
named, because no published rate establishes take-up or keeping. The answer crosses
`company/interfaces/sim_interface.py` (`answer_plan_offer`, `get_plan_instalments`), so the
company records the WORLD's reason on each offer. The mechanism that turns a rate into an answer
-- acceptance drawn at the take-up rate, then each monthly instalment paid or missed at the keeping
rate -- is built and tested with an injected basis, so the day a rate is sourced it is one constant.
The average weekly repayment in `company_debt_management.md` s.2 (GBP 6.01 electricity, GBP 4.40
gas, calendar 2025) is a mean over prepayment meters INSTALLED FOR DEBT in the year, weighted by
new installs (*corrected 2026-10-04: first written as "a mean over plans in force"*). It is not a
credit-account instalment, and is not wired while take-up is unknown. The credit-account mean
(SOR Q3.2) is collected and not published.

## Cure rates for plans, and the effect of early contact (2026-10-11)

**2026-10-11, discovery pass for the director's request of the same day:** *"what is known about cure
rates for payment plans and early contact"*, for one engine covering payment, credit risk and debt,
with early warnings and automated self-serve responses. This extends the sections above and does not
repeat them. *Tooling: the WebSearch budget was spent, so sources were reached through the OpenAlex
API, the GOV.UK search API, the NBER, FCA, ESC (Victoria), Insolvency Service and Ofgem sites
directly. Ofwat (403), UK Finance (403), the AER (no response) and Ofcom (no response) were not
reachable. Each gap below says which.*

**What "cure" means here, before any figure.** There are three different things, and the sources
measure different ones:
(a) **plan completed**: the agreed balance is cleared under the plan;
(b) **plan kept to date**: still paying at a horizon, so not yet a cure;
(c) **account cured**: back to current with no arrangement, by any route. Ofgem publishes none of
the three for GB energy. Every figure below is labelled with the one it measures.

### A. Plan outcomes, nearest analogue first

| Finding | Measures | Mark | Source |
|---|---|---|---|
| **Victoria energy retailers, hardship programmes, exits by type.** 2015-16: by agreement **34.2%**, excluded for not meeting the programme's terms **47.1%**, switched/transferred **18.7%**. 2016-17: 25.6 / 55.8 / 18.6. 2017-18: 22.4 / 63.9 / 13.7. Jul-Dec 2018: 24.6 / 61.0 / 14.4. Mean debt on entry rose from AUD 915 to AUD 1,385. Mean days in the programme were 278-317. | (a)-ish: an exit "by agreement" is not defined as debt cleared | ESTABLISHED, **analogous: energy retail, not GB** | ESC Victoria, *Victorian Energy Market Report* performance data workbook, Tables 2.7 and 2.10-2.16 (https://www.esc.vic.gov.au/sites/default/files/documents/Appendix%20Excel%20-%20Performance%20data_0.xlsx, read 2026-10-11) |
| **Victoria, tailored assistance under the Payment Difficulty Framework.** In 2019-20, electricity exits were **47.1% by agreement, 45.7% excluded, 7.2% switched**. Gas was 48.6 / 45.0 / 6.4. In 2020-21 the categories were redefined. Electricity exits were then **30.2% with no arrears** (cured), **14.9% with arrears**, **48.7% excluded for non-compliance** and **6.2% changed retailer**; gas was 31.0 / 15.3 / 47.9 / 5.7. The cured share by large retailer ran from **8.5% (Simply) to 41.7% (Origin)**. | (a) for "no arrears" | ESTABLISHED, analogous | ESC, *Appendix 2019-20 Performance data* (Tables S17-S20, Figs 93-94) and *Appendix 2020-21 Performance data* (Tables 23-26), same site, read 2026-10-11. 2020-21 is a Covid year. |
| **GB IVAs (statutory 5-6 year repayment plans).** Termination for failing to keep to the terms is about **1 in 3 over the lifetime** for 2016-18 registrations. It is front-loaded: **6.0% within year 1** (2024 cohort), **13.2% within 2 years** (2023) and **21.0% within 3 years** (2022). Lifetime termination was **42% for 2007 registrations and 24% for 2012**. The Insolvency Service attributes the fall to the 2008 IVA Protocol "introducing more flexibility to account for debtors' individual circumstances". | (a), its complement | ESTABLISHED, analogous (GB, but a formal insolvency) | Insolvency Service, *Individual Voluntary Arrangements outcomes and providers 2025*, commentary, 27 Feb 2026, https://www.gov.uk/government/statistics/individual-voluntary-arrangements-outcomes-and-providers-2025 |
| **US credit counselling repayment programmes (MMI, about 80,000 borrowers, randomised).** Control arm: **31.85% started a programme and 13.66% finished one** over about 5 years, so about 43% of starters completed. Treatment: debt write-downs (interest cut) raised finishing by 1.31pp (+9.6%). **Minimum-payment reductions had no detectable effect**, with the CI excluding more than +0.15pp on completion. The median reduction was 0.14pp of the balance, against a control payment of 2.38% of it. | (a) | ESTABLISHED (RCT), analogous | Dobbie & Song, *Targeted Debt Relief and the Origins of Financial Distress*, AER 110(4), 2020, doi:10.1257/aer.20171541; NBER w23545, Table 3 text pp. 22-24 |
| **US mortgage modifications (HAMP).** An 18pp larger payment cut at an eligibility cutoff lowered default from a control mean of **32% by 6pp**: "a one percent payment reduction reduces default rates by about one percent". Principal forgiveness that left the payment unchanged had **no effect** on default. | (c)'s complement | ESTABLISHED (RD design), analogous | Ganong & Noel, *Liquidity versus Wealth in Household Debt Obligations*, AER 110(10), 2020, doi:10.1257/aer.20181243; NBER w24964 p. 3 |
| **Covid payment deferrals, UK (about 4.5m granted).** Share of expired first deferrals where the customer needed further help (a second deferral or other forbearance), Jan 2021: top-6 mortgage firms **19%**, smaller deposit-takers **9%**, non-bank mortgage lenders **28%**, cards and loans **13%**, motor finance **13%**, high-cost credit **40%**. | (c) at deferral end: about 60-91% resumed without further help | ESTABLISHED, analogous (a payment holiday, not an arrears plan) | FCA, *Coronavirus linked forbearance: key findings*, Figure 1, 2021, https://www.fca.org.uk/publications/multi-firm-reviews/coronavirus-linked-forbearance-key-findings |
| StepChange clients 15 months after advice: 85% of those who acted on a recommended DMP or token payment plan said the problem was "sorted" or they were "still following" it, and 12% of all clients were debt free | (b), self-reported | ESTABLISHED as a survey, L for rates (self-selected respondents) | StepChange, *Paths to Recovery*, Mar 2020, https://www.stepchange.org/Portals/0/assets/pdf/Paths-to-Recovery_March-2020.pdf p. 9 |
| Ofgem 2014 data annex: credit-arrangement entries (BG 179,058; E.ON 154,466; EDF 153,398 electricity) and weeks to recover (46 / 58 / 68). **No failure counts.** This confirms that the 2015 Figure 13 above is the only published GB energy break figure this pass could find. | entries, not outcomes | ESTABLISHED | Ofgem, *Domestic suppliers' social obligations: 2014 annual data report*, https://www.ofgem.gov.uk/sites/default/files/docs/2015/09/externalreportpage_2014_annual_0.pdf |
| Water (Ofwat, CCW, company payment-matching schemes): plan completion or break rates | - | **NOT ESTABLISHED** | Ofwat returned 403. CCW's site search returned only press items (the 2006 "firm and flexible" release, with no rate). |

**Derived reading (DERIVED).** Every arrears-plan population with published exits shows the same
shape. **Roughly half of plans end in breach, and a quarter to a third end cured.** Victoria
hardship: 22-34% exit by agreement and 47-64% are excluded. Tailored assistance: 30% cured and 49%
excluded. IVAs: about two-thirds complete. Credit counselling: about 43% of starters finish. The
Ofgem 2015 figure (about 40% of large-supplier credit plans had at least one miss in a year) sits
in the same range. **Breaks are front-loaded.** IVA terminations run 6% in year 1, 13% by year 2
and 21% by year 3, and the Victorian programmes last under a year on average. So the first months
of a plan carry most of the hazard. **Supplier practice moves the cure share by a factor of about
5**: Victoria's large retailers range from 8.5% to 41.7%, and GB's 2015 tiers differed by a factor
of 2. That makes the cure rate a property of the engine as much as of the household.

### B. Early contact

| Finding | Mark | Source |
|---|---|---|
| **Days, not weeks.** In a random 10% of new delinquencies at a Chinese online lender, half were called by AI on days 1-5 and the other half by humans. The NPV gap grew to **12pp by day 5**, fell to **2pp by day 10** once humans took over, and to **0.8pp at day 30**. The 0.8pp gap persisted for 11 more months. Borrowers first contacted by AI were **1-2pp more likely to be late on each of the next 12 payments**. On a first answered call, AI got **21pp fewer promises to pay** and 18pp fewer same-day repayments, and promises made to AI were kept less often. | ESTABLISHED (RCT + RD), working paper, analogous (unsecured instalment loans, China) | Choi, Huang, Yang & Zhang, *How Good is AI at Twisting Arms? Experiments in Debt Collection*, NBER w33669, Apr 2025, https://www.nber.org/papers/w33669 |
| **Most first shortfalls self-cure.** Industry respondents told the FCA that "approximately 80% of initial payment shortfalls are rectified within 30 days" on mortgages. | DERIVED: an industry claim reported by the regulator, not an FCA statistic | FCA, *PS24/2: Strengthening protections for borrowers in financial difficulty*, Mar 2024, para 4.10, https://www.fca.org.uk/publication/policy/ps24-2.pdf |
| **People delay.** "On average, more than 50% of clients waited more than a year between realising their debt was a problem and getting advice" (2013 clients) | ESTABLISHED (survey), GB, cross-creditor | StepChange, *UK personal debt statistics*, Mar 2014, listed at https://www.stepchange.org/policy-and-research/personal-debt-statistics-in-the-uk.aspx |
| **Prompts raise contact and payment.** For HMCTS court fines, the share paying after a final text, interim results: **no text 5.2%, standard text 23.2%, the best personalised (name-first) text 33.0%**. A mortgage early-arrears contact rate rising from 45.9% to 62.2% (BIT/DfC NI 2018) is already in `debt_and_collections.md` §4. | ESTABLISHED as an interim chart (the bar-to-arm order is read off the chart), analogous | BIT, *Applying behavioural insights to reduce fraud, error and debt*, Feb 2012, Trial 5, p. 29, https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/60539/BIT_FraudErrorDebt_accessible.pdf (now read; the earlier "about 10pp" summary is confirmed) |
| SMS to borrowers who are already late, Colombian bank (7,063 clients): **-4% (relative) probability of being late**, larger with social-norm wording. **No effect when sent to on-time borrowers to prevent delinquency.** | ESTABLISHED (RCT), analogous | Barboni, Cardenas & de Roux, *Behavioral messages and debt repayment*, Review of Finance, 2026, doi:10.1093/rof/rfag015 (abstract) |
| A moral-appeal SMS cut credit-card delinquency by **4.4pp from a 66% baseline** (Indonesia). Email reminders at a US credit union **reduced moderate and severe delinquency**. Intensive offers (a savings account, counselling) did nothing because take-up was low. | ESTABLISHED (RCTs), analogous | Bursztyn et al., JPE 2019, doi:10.1086/701605; Roll et al., *J. Consumer Affairs* 2024, doi:10.1111/joca.12597 (abstracts) |
| An energy-specific effect of time-to-contact on cure | **NOT ESTABLISHED.** No GB or overseas energy trial found. | - |

### What this means for an automated early-warning and self-serve engine

- **Contact on day 1, and a person by day 5 for whoever has not engaged** (DERIVED from w33669). The
  measured loss from automation is about 12pp at day 5, but only about 1pp if a human takes over by
  day 6. So automation is supported as the FIRST touch with a fast human fallback. It is not
  supported as the only touch for anyone who has not engaged. The paper is about AI *calls*, not
  self-serve offers; whether a self-serve offer carries the same "promise" deficit is a GAP.
- **Expect most first misses to self-cure** (about 80% in 30 days, an industry claim). An early
  warning should therefore act on a forecast of a missed payment, not on a single miss. Otherwise
  the engine spends contacts on accounts that cure anyway.
- **Expected cure for an automated plan: no GB figure.** If the model needs a prior, the honest
  form is a range: **25-45% complete or cured, 45-65% broken**, from Victoria, IVAs and
  credit-counselling (DERIVED, analogous). Put most of the break hazard in the first 3-6 months.
  Report it as a range with this reason, never as a point. The GB slot stays `None`.
- **Lower payments: the evidence splits by size of cut.** A cut big enough to change monthly
  liquidity lowers default roughly one-for-one (HAMP, elasticity about 1). A token reduction did
  nothing (MMI: 0.14pp of the balance). Forgiveness tied to payment kept was the lever that raised
  completion (MMI, and the 2001 US arrearage-forgiveness programmes in
  `risk_based_payment_plans_outside_gb_energy.md`). This supports "a lower payment for a period"
  only where the reduction is material. "Some money steadily beats none" is supported for liquidity
  relief and forgiveness earned by paying.
- **GAPs:**
  - GB energy plan completion and break flows (Ofgem SOR Q3.6-3.27, collected and unpublished);
  - water-sector plan outcomes (Ofwat unreachable this pass);
  - Australian national (AER) hardship exit data (unreachable);
  - any energy trial of contact timing;
  - the cure rate of a SELF-SERVE plan versus an agent-set one (none found anywhere).

## The world's answer to an offer (2026-10-12)

**2026-10-12, the world lane, on the director's principles of 2026-10-11** ("the world creates
customer behaviour behind the curtain, from evidence ... where evidence is missing, carry a labelled
range, not a number ... the world answers every plan offer None; that's the first gap"). No new
source was read for this section. It turns the evidence above into a household that answers the
offer it is SENT, from its own money, with no reference to who sends it or why.

**The stimulus, defined before any rate.** A household in arrears is told one of three things:
(a) *a repayment plan*: pay the arrears at an instalment, which it names itself in the SLC 27.8
conversation or the supplier names; (b) *a lower monthly payment for a period*; (c) *a pause*
(breathing space) for a number of months. Its answer is agree or decline, and then, for a plan,
kept or broken.

| Choice the world makes | Range carried (toggle) | Evidence | Mark |
|---|---|---|---|
| Take-up, flat over means and offer shape | 0.32-0.53 (`plan_take_up_share`) | MMI control arm 31.85% started a programme; PFRC/StepChange 37% + 16% = 53% agreed a plan (selected population, so a ceiling). 16% agreed a plan they felt unaffordable, so an unaffordable offer is still agreed | analogues, DERIVED range |
| The household's own instalment | the arrears over 46-96 weeks (`plan_weeks_to_recover`) | Ofgem social-obligations data annexes, mean weeks to recover a credit-arrangement debt: 46, 58, 68 (2014) and 46, 77, 96 (2015) at the three largest suppliers | ESTABLISHED range, a decade old |
| A plan is kept or broken whole; break share | 0.45-0.65 (`plan_break_share`) | the derived prior above (s.A): Victoria 45-64% excluded, IVAs ~1 in 3, Ofgem 2015 ~40% with a miss in a year | DERIVED from analogues |
| Breaks fall in the first six instalments | (design choice, `BREAK_WINDOW_INSTALMENTS`) | "most of the hazard in the first 3-6 months" (s.A); the upper end of that reading | named simplification |
| An unaffordable instalment breaks more, in proportion | break share x (named / own instalment), capped at 1 | Ganong & Noel (HAMP): a 1% payment change moves default about 1%; Ofgem 2015 break shares rise with the weekly amount | analogue elasticity |
| An income shock breaks a plan | a household whose stress tier rises to HIGH after agreeing breaks at the next instalment | the mechanism every analogue names (liquidity); no rate is added | no new number |
| A lower payment: token cuts do nothing | cut under 5.9% of the payment: no effect (`TOKEN_CUT_SHARE`) | MMI: a 0.14pp-of-balance cut on a 2.38% payment had no detectable effect | ESTABLISHED (RCT), analogue |
| A lower payment: material cuts lower failed collections | failure x (1 - e x cut), e in 0.25-1.0 (`plan_lower_payment_failure_elasticity`) | HAMP elasticity about 1 as the ceiling; the floor is a choice | analogue ceiling |
| A pause: a household still in difficulty may not resume | 9-40% fail the first collection after (`plan_pause_resume_failure_share`); a LOW-stress household always resumes | FCA, Covid forbearance key findings, Fig. 1: 9% (smaller deposit-takers) to 40% (high-cost credit) of expired first deferrals needed further help | analogue range |

**Cure is an outcome, not an input.** A plan kept to its last instalment has cleared the debt. So
the world's cure share is what the break share, the plan length and the household's later money
leave; it is not set. At the derived prior's ends (break 0.45-0.65) the cure share before
income shocks and departures is 0.35-0.55, against the prior's 0.25-0.45 net of the 6-19% of analogue exits that
are switches. That agrees.

**Shipped off.** Every toggle defaults to 0 (or, for the weeks, to a midpoint read only when
take-up is on), so the shipped world answers every offer None with the reason named, exactly as
before. A harness switches it with `plan_offer_response.BASIS = basis_at("low"|"high")`.

**GAPs the world carries rather than fills:**
- take-up split by means, by offer shape, or by who makes it (none published; simplification 4);
- the effect of the household's pay-or-heat state on keeping (`self_rationing.py` is not wired
  into the run, so no household carries it);
- what a household does in the months of a pause (the supplier presents nothing: its act, not
  the household's) and how a broken plan's debt is later repaid (simplification 2);
- every GB energy flow above: SOR Q3.1 (entries), Q3.3 (weeks), Q3.6-3.27 (failed arrangements),
  collected by Ofgem and unpublished. The practitioner question stands.
