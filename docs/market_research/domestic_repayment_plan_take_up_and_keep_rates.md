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
