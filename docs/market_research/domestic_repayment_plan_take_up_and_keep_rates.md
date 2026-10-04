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
| Take-up of an offered plan | **NOT ESTABLISHED.** No published rate found. | none of the sources below reports offers made or accepted |
| Share of instalments / plans kept, or a breakage hazard | **NOT ESTABLISHED.** No published rate found. | Ofgem's indicators are end-of-quarter stocks with no flow of plans started, completed or broken |
| Stock share of >91-day debtors on an arrangement | ESTABLISHED (as a stock) | Q2 2026: 888,824 electricity accounts "repaying a debt" (2.9%) against 1,187,788 "in arrears" with no arrangement (4.0%) -- Ofgem, *Debt and arrears indicators*, https://www.ofgem.gov.uk/data/debt-and-arrears-indicators, read 2026-10-04 |
| Share of debt VALUE held with no plan | ESTABLISHED (as a stock of GBP) | "75% sits with customers who are not on repayment plans" -- Ofgem, *Debt strategy -- a 'reset' and 'reform' for customers in debt*, Dec 2024, https://www.ofgem.gov.uk/sites/default/files/2024-12/Debt_Strategy_(5).pdf (search-indexed text; the PDF did not yield extractable text to the fetch tool). The NAO's "only 25% of total customer debt ... is held by customers who have repayment plans in place" is the same quantity |
| Share of repaying customers using a PPM | ESTABLISHED (as a stock) | "typically ranged between around 30% and 40% over the last 15 years" -- Ofgem, *Debt and arrears indicators* |

**Why the stock shares are not a take-up rate.** 2.9 / (2.9 + 4.0) = 42% of >91-day debtors are on
an arrangement at a quarter end. That counts households whose plans have lasted years (Ofgem's Q4
2025 average plan duration is 365 weeks, electricity) against debtors who may never have been
offered one, and excludes everyone whose plan broke and who fell back into arrears, and everyone
who agreed and cleared inside 91 days. Using 42% as a take-up probability would be choosing a
number because a number was needed.

## What was searched and could not be fully read

Not a guaranteed full-text negative, so stated: Ofgem's *Affordability and debt* call for input
(March 2024) and the December 2024 *Debt strategy* PDF returned largely image-based pages to the
fetch tool; Citizens Advice's written evidence COE0077 returned HTTP 403; Ofgem's *Domestic
suppliers' social obligations* annual reports (2012-2016) report counts of customers repaying debt
and PPM installs, and whether they also counted arrangements broken was not established from the
pages retrieved. Ofgem's 2022 *Market compliance review: customers in payment difficulty* found
suppliers "potentially not taking account of all relevant factors when setting customer repayment
plans" -- evidence of unaffordable plans in kind, not in rate. A Citizens Advice figure of 7% (gas)
/ 8% (electricity) of clients on a plan set at an unaffordable level (2016-2018) was found only
through search-engine synthesis with no named report, and is NOT cited as a fact.

**The next place to look**, if anyone does: the social-obligations report data tables, and a
supplier's own published collections data (none known).

## What the world does with this

`simulation/plan_offer_response.py` answers every plan offer with `accepted: None` and the reason
named, because no published rate establishes take-up or keeping. The answer crosses
`company/interfaces/sim_interface.py` (`answer_plan_offer`, `get_plan_instalments`), so the
company records the WORLD's reason on each offer. The mechanism that turns a rate into an answer
-- acceptance drawn at the take-up rate, then each monthly instalment paid or missed at the keeping
rate -- is built and tested with an injected basis, so the day a rate is sourced it is one constant.
The average weekly repayment in `company_debt_management.md` s.2 (GBP 6.01 electricity, GBP 4.40
gas, Q4 2025) is a mean over plans in force, the nearest published basis for an instalment, and is
not wired while take-up is unknown.
