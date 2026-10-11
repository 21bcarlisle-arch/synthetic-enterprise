**Knowledge:** debt-and-collections

# Risk-based payment-plan design outside GB energy: limits, timing and plan shape

**2026-10-11, discovery agent.** Asked by the director (2026-10-11), designing a personal payment
plan per customer where credit risk sets how far a balance may drift from zero (not how much is
paid over the year): how banks/lenders/insurers/telecoms/utilities elsewhere set risk-based limits,
payment timing and plan shape, plus evidence on payday-aligned collection dates. **Every finding
below is from OUTSIDE GB energy and is marked analogous, never as GB energy evidence** -- none of
it is what a GB supplier does or sees.

**Method note.** Live web search was unavailable this pass (DuckDuckGo returned a bot challenge;
most direct URL guesses at specific utility/consumer-body sub-pages 404'd). Two primary-source PDFs
were fetched and read in full; the rest below is general industry/regulatory knowledge, marked `M`
and flagged with a GAP for live re-verification rather than invented as `H`.

## 1. Risk-based limits (credit, overdrafts, BNPL)

| Finding | Mark | Source |
|---|---|---|
| Credit card "persistent debt": defined as a customer paying MORE in interest/fees/charges than principal over a rolling 18 months. At 18 months the firm must prompt the customer to change repayment behaviour; if still persistent at 36 months, the firm must proactively offer a repayment plan, which can include waiving/reducing/cancelling further interest and charges. | ESTABLISHED, analogous | FCA, *PS18/04 -- Credit card market study: persistent debt and earlier intervention remedies*, Feb 2018, https://www.fca.org.uk/publication/policy/ps18-04.pdf (fetched 2026-10-11, read in full) |
| Lenders must assess affordability (CONC 5.2A) before EVERY credit-limit increase, proportionate to the amount and the customer's apparent risk; customers can opt out of automatic limit increases altogether. | ESTABLISHED (rule exists), M -- handbook page itself returned a 500/Cloudflare block this pass, GAP for a direct handbook cite | General FCA consumer-credit knowledge; CONC 6.3/5.2A |
| BNPL ("deferred payment credit") was brought into FCA regulation, extending affordability checks and persistent-debt-style protections to BNPL limits. | DERIVED / NOT independently verified live this pass | training knowledge only -- GAP: no FCA page fetched successfully (404 on the obvious URL) |
| Retail credit-limit SETTING itself (how a score converts to a £ limit) is bank-proprietary behavioural scoring (bureau data + income/expenditure + repayment history), reviewed periodically; no published formula. | NOT ESTABLISHED as a public rule, ESTABLISHED as a practice | general trade knowledge; GAP: the score-to-limit mapping is commercially confidential everywhere we looked |

**GAP:** no regime anywhere publishes a formula converting a risk score directly into a numeric
"permitted balance drift" -- every regime found sets a LIMIT (a ceiling) and a TIME horizon (how
long persistent drift is tolerated before forced correction), not a drift band either side of zero.

**What this suggests for a GB energy payment plan.** The FCA's shape -- low risk is given a wide
limit and a long horizon (18-36 months) before anything is forced; high risk gets review sooner and
a smaller limit -- maps cleanly onto "risk sets the envelope width and the correction clock, not the
annual total." It does NOT transfer the specific numbers (18/36 months is sized to credit-card
revolving debt, not a seasonal heating bill), and it is a REMEDIAL trigger (something has already
gone wrong) rather than the director's design, which is preventative (the envelope is set before
drift happens). Doesn't transfer: credit-limit regimes have no equivalent of "prompt refund of
surplus credit" -- credit is one-directional (a limit on owing, not a limit on being owed).

## 2. Utility bill smoothing elsewhere

| Finding | Mark | Source |
|---|---|---|
| Victoria (Australia) regulates energy retailers under its OWN "Payment Difficulty Framework" (not the national AER rules): retailers must offer tailored, flexible payment assistance and disconnect only as a last resort; current guideline effective from 1 Oct 2026, replacing an earlier 2019 framework. | ESTABLISHED, analogous | Essential Services Commission (Vic), *Guideline: Payment difficulty framework*, https://www.esc.vic.gov.au/electricity-and-gas/codes-guidelines-and-policies/payment-difficulty-framework (fetched 2026-10-11) |
| The rest of Australia operates bill smoothing / flexible payment options and AER-approved per-retailer Hardship Policies under the National Energy Customer Framework. | ESTABLISHED (framework exists), M | general regulatory knowledge; GAP -- aer.gov.au did not respond this pass (connection failed), so the numeric content of a Hardship Policy was not re-checked live |
| US utilities widely offer "budget billing" / "equal payment plan" / "levelized billing": the monthly amount is set from a rolling ~12-month average of usage/cost, with an annual "true-up" month that reconciles actual vs billed (credit refunded, or a shortfall spread forward); enrolment typically requires the account not already be significantly in arrears, and a plan can be cancelled back to actual billing if the shortfall grows too large. | ESTABLISHED as a widespread PRACTICE, M, analogous | general utility-industry/PUC-tariff knowledge; GAP -- direct fetches of named utilities' own budget-billing pages (Georgia Power, Con Edison, PG&E, Dominion, Duke, Xcel) all 404'd this pass, and the EIA RECS billing-assistance table was not located under a guessed URL; NOT independently re-verified live |
| Separately, some US states run ability-to-pay utility plans (e.g. Ohio's Percentage of Income Payment Plan, PIPP) that cap the bill at a fixed share of household income regardless of usage -- a different anchor (affordability) from budget billing's anchor (smoothed actual cost). | ESTABLISHED (exists), M, analogous | general knowledge; GAP -- not re-fetched live this pass |
| New Zealand (Electricity Authority / Commerce Commission) and Ireland (CRU) both publish consumer-protection/hardship codes requiring suppliers to offer payment plans before disconnection. | NOT ESTABLISHED in this pass beyond the regulator existing | comcom.govt.nz and cru.ie both loaded (200) but the specific guideline text was not located within budget; GAP, flagged for a follow-up pass rather than guessed |
| Take-up and arrears/breakage rates under ANY of the above (US budget billing, Australian smoothing) | NOT ESTABLISHED | no live figure found this pass -- same shape of gap as `domestic_repayment_plan_take_up_and_keep_rates.md` finds for GB: regulators publish the existence of the mechanism, rarely its flow-level success rate |

**What this suggests for a GB energy payment plan.** US budget billing's shape -- a smoothed amount
set from a trailing average with a scheduled true-up, and an eligibility gate that excludes accounts
already deep in arrears -- is the closest working analogue anywhere to "low risk gets smoothing."
Victoria's framework is the closest analogue to "higher risk is kept near zero without winter
shock": it is built explicitly around TAILORED assistance scaled to the individual's
capacity, not a uniform percentage. Doesn't transfer: none of these regimes claims the
portfolio-level property the director states ("credits and debits net out across the book") --
that is a supplier-side balancing claim, not a customer-facing rule, and nothing published audits
it from outside.

## 3. Insurers and telecoms

| Finding | Mark | Source |
|---|---|---|
| UK mobile/telecom credit checks: a failed or thin-file credit check typically results in a SIM-only, pre-pay, or deposit-required offer rather than a worse PRICE -- risk changes the product/limit, not the unit rate. | ESTABLISHED as a widespread practice, M, analogous | general telecoms-industry knowledge; GAP -- no specific operator deposit figure independently fetched this pass (404s on guessed deposit-policy pages) |
| Device/handset credit on a contract is underwritten separately from the airtime plan via a bureau-based affordability check; the CREDIT LIMIT (device price band) varies by score while the INSTALMENT SHAPE (fixed equal monthly payments over 24-36 months) is the same for every customer who qualifies. | ESTABLISHED as a practice, M, analogous | general telecoms-industry knowledge; GAP, not freshly cited |
| US utility security deposits: many investor-owned utilities require a deposit from new customers who fail a credit screen, commonly sized near one to two months' estimated bill, refunded (often with interest) after ~12 months of on-time payment, under state PUC-filed tariffs. | ESTABLISHED as a practice, M, analogous | general utility-tariff knowledge; GAP -- not freshly cited, same utility-site 404s as section 2 |
| Insurance monthly instalments are a separate regulated credit agreement (interest/APR-bearing); non-payment typically leads to a short grace period then CANCELLATION of cover, not a managed balance. | ESTABLISHED, analogous (as a CONTRAST) | general insurance-market knowledge |

**What this suggests for a GB energy payment plan.** Telecoms' split of "risk sets the limit/product,
a fixed instalment shape serves everyone inside it" is the cleanest real-world precedent for the
director's "risk sets the envelope, not the annual total." Doesn't transfer: insurance's
pay-or-lose-cover response to missed payment is the opposite of a tolerated drift band, and is a
useful negative example -- energy supply (with SLC 27/28 and PPM-as-last-resort) is already
structurally closer to the utility-deposit model than the insurance model, which argues against
importing instalment-insurance-style cancellation logic.

## 4. Payday-aligned collection dates

| Finding | Mark | Source |
|---|---|---|
| Offering customers a choice of Direct Debit collection date (so it can be set after salary/benefit payday) is a widely used UK utility/water-company affordability and vulnerability tool. | ESTABLISHED as a practice, M | general knowledge of GB utility/water vulnerability strategies (e.g. referenced in CCW and Ofwat affordability work); GAP -- the specific water-company pages guessed this pass (Anglian, South West Water) 404'd, and Ofwat's own affordability page returned 403, so no live page confirms the current wording |
| A quantified causal effect of payday-aligned collection on Direct Debit failure rates, arrears, or missed-payment rates | **NOT ESTABLISHED this pass** | DuckDuckGo search was blocked (bot challenge); Pay.UK's own DD-specific page returned 403; Bacs document library loaded but was not searched to a specific report within budget; Money and Mental Health Policy Institute's site loaded and its search function surfaced no DD-dated hit for "payday"; StepChange main page loaded but was not searched further. **This is the single weakest-evidenced part of the director's question and the one most worth a dedicated follow-up pass with working search.** |

**What this suggests for a GB energy payment plan.** The PRACTICE of offering a choice of collection
date is well established as existing; the EVIDENCE that it reduces failed payments is, as of this
pass, a gap rather than a finding -- treat "align collection with payday reduces failures" as a
plausible, industry-practised hypothesis, not yet a sourced number, until a follow-up pass with
working web search confirms or refutes it.

## Summary of GAPs (for a follow-up pass)

1. No live citation for FCA credit-limit-increase affordability rule text (CONC handbook page
   blocked) or for FCA BNPL regulation (404 on guessed URL).
2. No live citation for US budget-billing mechanics at a named utility, or for EIA RECS enrolment
   figures (guessed table numbers were wrong tables).
3. No live citation for AER (national Australia), New Zealand or Ireland hardship-code mechanics
   beyond the regulator existing.
4. No live citation for telecom/US-utility deposit sizing.
5. **No quantified evidence, found this pass, that payday-aligned Direct Debit dates reduce failed
   payments** -- the director's most specific evidence request is the one this pass answers
   weakest; search tooling (not the literature) was the binding constraint.

## Payday-aligned collection: follow-up with web search (2026-10-11)

*Tooling note: the WebSearch budget was spent before this pass began. Bing and DuckDuckGo returned
nothing or captchas, and Brave answered a few queries before rate-limiting. The evidence below came
through the OpenAlex and NBER APIs and from direct fetches. All primary documents were downloaded
and read as text. No UK DD-specific quantitative study was found. That is a search-coverage limit,
not proof that none exists.*

**Bottom line: QUANTIFIED evidence exists that bill timing against income timing moves late payment
and disconnection at electricity utilities. It comes from two studies, US and Argentina. Both are
about BILL/DUE-DATE timing for pay-on-receipt customers, not Direct Debit collection-date choice.
Neither randomises the remedy. No quantified UK evidence on choosing a DD date was found. Mark:
DERIVED for GB DD (an analogous mechanism with a measured effect), NOT ESTABLISHED as a GB DD effect
size.**

| Finding | Mark | Source |
|---|---|---|
| US electricity utility, 2015-18 administrative data. In below-median-income block groups, accounts whose bill arrives within 1 day of the 1st of the month (when most US benefits land) show **-36% probability a bill is not paid on time (base 55.9%)**, **-67% outstanding unpaid balance (base $206.90)**, **-43% probability of being eligible for disconnection (base 33.8%)** and **-64% probability of disconnection (base 10.9%)**. In older, below-median-income areas (Social Security paid on other days): -31% unpaid (base 45.5%), -50% overdue amount, -45% disconnection (base 7.68%). In high-income areas the effect "nearly vanishes". | ESTABLISHED as a published estimate, M (labelled "PRELIMINARY DRAFT"; observational, cross-sectional variation in bill-cycle timing; the authors themselves call for an RCT) | Barrage, Chin, Chyn & Hastings, *The Impact of Bill Receipt Timing among Low-Income and Aged Households: New Evidence from Administrative Electricity Bill Data*, NBER Retirement & Disability Research Center paper NB19-09, Aug/Sep 2019. Paper: https://www.nber.org/sites/default/files/2023-06/NB19-09%20Barrage%20Chin%20Chyn%20Hastings%20REVISED-VD.pdf ; summary: https://www.nber.org/sites/default/files/2023-05/NB19-09%20Barrage%20Chin%20Chyn%20Hastings%20Summary.pdf |
| Tucumán, Argentina, 2019-22: more than 20,000 electricity customers on the AUH social-security benefit. The benefit payday is set by the last digit of the beneficiary ID and the bill due date varies with billing logistics, so the same household experiences both orderings (within-household identification). **When payday falls just after the due date, on-time payment drops ~4-4.5 pp, "nearly 30%".** When payday falls after the suspension date, paying before suspension drops ~3 pp (~7%). There is **no effect for customers paying by credit card**, which the authors read as a liquidity channel. Mismatch occurs in 53% of low-income cases. | ESTABLISHED as a published estimate, M-H on design (natural experiment, household fixed effects); working paper, not peer-reviewed | Diaz-Campo, Gars, Danon, Kestelman Borges & Marquez Ragonesi, *Timing matters: exploring the causal effect and potential mechanisms of a liquidity shock on delayed payments*, AAEP 2024 conference paper, version 31 Aug 2024, https://aaep.org.ar/works/works2024/4743.pdf (abstract; §5 p.15-18; conclusion) |
| US regulators codify payday alignment as a RIGHT for benefit-income customers. Illinois **83 Ill. Adm. Code 280.70 "Preferred Payment Date"**: a monthly-billed residential customer whose primary income is a benefit received within 10 days after the regular due date "shall be entitled to a preferred payment date". Eligible: TANF/AABD, GA/SSI, Social Security or Veterans, unemployment compensation. **The utility must notify the customer of the option after 2 late payments in 12 months.** The date may be up to 10 days after the billing date, optionally combined with a budget plan. The utility may remove the customer after more than 4 late payments in 12 months, with a 12-month bar on re-offer. Amended eff. 1 Nov 2014. | ESTABLISHED (rule text) | https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-83-SS-280.70 |
| CFPB *Consumer Insights on Paying Bills*, 28 Nov 2018: respondents cite income/bill timing misalignment as a cause of falling behind. It recommends asking billers to move due dates to match income and gives a "Request a change in your bill due date" worksheet. No effect size. | ESTABLISHED (qualitative) | https://www.consumerfinance.gov/data-research/research-reports/consumer-insights-paying-bills/ |
| UK qualitative evidence: low-income households want to choose the DD day "to fit in with the timing of salary or other income payments"; inflexible dates (council tax cited repeatedly) cause distress and missed-payment charges. A cited Moneyline trial of **Variable Recurring Payments** (flexible pull timing/amount) for affordable-credit repayments found **"a 10% drop in arrears compared to those using standard Direct Debits"**. That is a VRP effect, not date choice alone. It is reported second-hand (Moneyline 2024, *Financial inclusion through innovation*), and the report notes energy is "very different" from debt repayments. | ESTABLISHED as qualitative + one second-hand trial figure, L-M for the 10% | Davies & Collard (University of Bristol PFRC), *Flexible payments: understanding payment needs in low-income households*, Fair By Design / Barrow Cadbury Trust, 31 Oct 2024, https://www.bristol.ac.uk/media-library/sites/geography/pfrc/documents/Flexible-payments-for-low-income-consumers.pdf (pp. on DD date flexibility; conclusion, fn 51) |
| Pay.UK/Bacs DD failure rates by collection-date alignment; MMHPI, StepChange, FCA, Ofwat or BIT trials with a measured DD date-choice effect | **NOT ESTABLISHED** (not reached: search engines blocked) | - |

**How to carry this into GB DD design:**
- The mechanism (liquidity at the moment of the pull) is consistent across two settings with very
  different institutions. The effect is concentrated in low-income, benefit-dependent households.
- The Argentine credit-card null is the cleanest evidence that it is liquidity and not inattention.
- An effect size for "let the customer pick their DD date" in GB is still owed. The US figures are
  bill-receipt timing for pay-on-receipt accounts, so they would overstate the effect for customers
  who already chose their DD date.
- If the model needs a number, the honest form is a range from these two studies, applied to the
  share of customers whose collection date currently precedes their income date, plus a `None` for GB
  DD with this reason. [DERIVED]

## US budget billing: follow-up (2026-10-11)

**Mechanics: ESTABLISHED from rule and tariff text at two states and one named utility. Outcomes
(arrears, disconnections, enrolment shares): NOT ESTABLISHED. No published figure was found this
pass.**

| Finding | Mark | Source |
|---|---|---|
| **Pennsylvania, 52 Pa. Code §56.12(8) "Budget billing"**. Gas, electric and steam utilities must offer residential customers, "on a year-round rolling enrollment basis", a billing procedure "which averages estimated public utility service costs over a 10-month, 11-month or 12-month period". The utility "shall review accounts at least three times during the optional billing period". At the end of the budget year, a reconciliation of $100-$300 is amortised over 6 months on request, and one above $300 over at least 12 months on request. (Last amended eff. 1 Jun 2019, 49 Pa.B. 2815.) | ESTABLISHED (rule text) | https://www.law.cornell.edu/regulations/pennsylvania/52-Pa-Code-SS-56-12 |
| **Illinois, 83 Ill. Adm. Code 280.80 "Budget Payment Plan"** (eff. 1 Nov 2014). The intent is to equalise payments "based upon the customer's average bill". **Eligibility is tied to arrears:** a current account may enrol any time; an account with a past-due amount must pay it in full or enter a Deferred Payment Agreement first. Adjustment: whenever the plan "will not be successful if left at its current level", with written notice. **Mandatory review at least once between the 4th and 7th month.** A large shortfall offers pay-off or re-levelling; a large credit offers refund or re-levelling. No late charge unless the account is in overall budget deficit, and then only on the late instalment. The utility may cancel if a payment is short or 21 days in arrears, and the shortfall becomes due on the next bill. The customer may cancel any time. | ESTABLISHED (rule text) | https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-83-SS-280.80 |
| **PG&E (California), Electric Rule 9 §H "Budget Billing"** (Advice 7747-E, eff. 31 Oct 2025). Enrol in any month, subject to PG&E approval. The amount is **"one-twelfth of the annual bill as estimated by PG&E, based on the customer's historical billings for the most recent year"**, or comparable customers if there is no history. **"Reviewed and adjusted each billing cycle to reduce the likelihood of a large imbalance"**, with notice on the bill. A participant is removable, and service terminable, if a bill containing a prior unpaid budget amount becomes delinquent under Rule 11. | ESTABLISHED (tariff text) | https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_RULES_9.pdf |
| So "rolling 12-month average + annual true-up month" is ONE design, not THE design. The three texts show: (a) a fixed annual estimate with an end-of-year reconciliation amortised forward (PA, with ≥3 interim reviews); (b) a mandatory mid-term review plus ad hoc re-levelling (IL); (c) continuous per-cycle re-levelling with no distinct true-up month (PG&E). | DERIVED (comparison of A-grade texts) | above |
| Budget-billing outcomes: enrolment share, arrears or disconnection of enrolees vs non-enrolees, at any named utility or PUC | **NOT ESTABLISHED** | none found. OpenAlex returned no such study. Utility budget-billing web pages (PG&E, Georgia Power, Con Edison) 404'd at guessed URLs. |

**For GB design:**
- The US rules treat arrears as an ENTRY gate (IL: clear it or enter a DPA first) and a large drift
  as a re-levelling trigger, not as a reason to price differently.
- Re-levelling cadence is a regulated choice spanning per-cycle (PG&E) to ≥3 per year (PA). The GB
  analogue is SLC 27.15's DD-review duty.
- Amortising a year-end shortfall over 6-12 months by regulation (PA) is a codified answer to the
  "catch-up shock" problem. [DERIVED]
