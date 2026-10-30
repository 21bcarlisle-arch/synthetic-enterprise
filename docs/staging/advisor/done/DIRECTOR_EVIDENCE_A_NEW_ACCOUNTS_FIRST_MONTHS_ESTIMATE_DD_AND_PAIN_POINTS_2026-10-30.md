**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] A new account's first months: opening estimate, first DD, opening read, and the pain points customers meet (2026-10-30)

**Type:** EVIDENCE, through the advisor channel, for `DIRECTOR_STEER_PAIN_POINTS_DRIVE_THE_LOOP_KNOWLEDGE_THEN_SIM_REACTION_THEN_SUPPLIER_TESTS_2026-10-30.md`. The director's words, from chat on Fri 30 Oct, 07:30 GMT: "Create knowledge in this area and in unbilled. What do different people do. What are the pros and cons. What do customers experience. What pain points should we measure. Is the SIM making customers react and behave to pain points?"

Written by an advisor research pass (web-sourced). Items tagged [unverified] are calibration assumptions, not evidence. Verify them with your own network access as you draft the Knowledge pages, as the 25 Oct verification steer asks.

**Correction to note:** the unbilled pack finds that SLC 21B is an *annual* reasonable-steps read duty. The two-yearly duty was a meter *inspection* duty (SLC 12.14–12.16), repealed in 2016. Check this against what the invariant library holds as "the read duty".

---

# Evidence Pack: A New GB Domestic Energy Account's First Months

**Scope:** how a GB domestic supplier sets the opening consumption estimate and the first direct debit (DD), and what the customer goes through in months 0–12. It is written as input to a simulated supplier whose simulated households react to real pain points.

**Research date:** 30 October 2026. The search budget was limited, so the pack leans on fetched primary pages from Ofgem, Elexon, the Energy Ombudsman, Citizens Advice, Which?, MSE, supplier help pages and the Centrica accounts.

**Conventions:**
- A URL sits beside every factual claim.
- **[unverified]** means I could not confirm the claim from a primary or reputable source within budget. It may be true, but the simulation should treat it as an assumption and not as evidence.
- Text marked *Analysis* is my reasoning, not sourced fact.

---

## Part (a): Standard practice and how suppliers differ

### a.1 Where the opening consumption figure comes from

On a new account the supplier has to forecast twelve months of consumption before it holds any meter data of its own. Five main inputs exist, roughly in order of quality.

**1. The previous supplier's or the industry's history, once the switch has completed.**
- Octopus's help pages say it first estimates the next 12 months, divides the cost by 12, and then refines that once the switch completes: "your previous supplier's historical usage data gives a more accurate estimate" (https://octopus.energy/help-and-faqs/articles/monthly-payments/).
- So the *first* DD is usually set before the best data arrives, and it is corrected later. That is the root of most first-year pain.

**2. The industry EAC for electricity, sent on the D0019 flow.**
- Non-half-hourly (NHH) Data Collectors work out an Estimate of Annual Consumption (EAC) and an Annualised Advance (AA) for each meter register from successive readings and profile data. They send these to the supplier on the D0019 flow, and suppliers are encouraged to link D0019s to their billing systems as an independent check (https://www.elexon.co.uk/guidance-note/erroneous-large-eacaas-management-resolution/).
- EACs and AAs drive Supplier Volume Allocation in settlement, so a wrong value shifts energy, and therefore cost, between suppliers (same URL).
- Elexon names "incorrect Change of Supplier readings", switched multi-register reads, meter exchange timing and rollover errors as common root causes of bad EACs (same URL). The opening EAC that a gaining supplier inherits can therefore already be corrupted at the switch.

**3. The gas AQ from Xoserve.**
- Xoserve's Annual Quantity (AQ) is the gas equivalent of the EAC. Ofgem treats Xoserve AQ data as a complementary source for corroborating consumption trends, and uses weather correction through the Seasonal Normal Composite Weather Variable set by Xoserve's Demand Estimation Sub-committee (https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf).
- Rolling monthly AQ recalculation from meter reads (UNC Project Nexus) and the gaining supplier's or shipper's access to AQ at switch: **[unverified]**. I did not fetch a Xoserve primary page.

**4. The customer's declared use at quote.**
- Customers usually give one of three things at quote: annual kWh from an old bill, an annual £ spend, or nothing, in which case they pick low, medium or high or give property size.
- Loop's guidance says "your future usage will be estimated by the information you gave when switching", levelled across the year for seasonality (https://kb.loop.homes/knowledge/how-will-my-new-supplier-calculate-my-direct-debit).

**5. Defaults from comparison sites and Ofgem's Typical Domestic Consumption Values (TDCVs).**
- Ofgem revised the TDCVs with effect from **1 July 2026** (decision of 27 May 2026) (https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf). The new values are lower than the 2023 values across the board:

| Category | Low | Medium | High | Previous (2023) L / M / H |
|---|---|---|---|---|
| Electricity Profile Class 1 (single rate) | 1,600 | 2,500 | 3,800 kWh | 1,800 / 2,700 / 4,100 |
| Electricity Profile Class 2 (multi-rate) | 1,900 | 3,400 | 6,100 kWh | 2,200 / 3,900 / 6,700 |
| Gas | 6,000 | 9,500 | 14,000 kWh | 7,500 / 11,500 / 17,000 |

- The Economy 7 split stays at 58% day and 42% night (same URL).
- TDCVs are built from the DESNZ sub-national consumption dataset (medians, with an adjustment for very low and nil meter points). They are "a common reference point for communicating prices and bills where actual consumption is unknown", and they feed the price cap's illustrative typical bill and benchmark consumption (same URL).
- Comparison sites' exact defaults (property-size or occupancy-based estimators that map to TDCVs) are **[unverified]**. I did not fetch Uswitch's or MSE's estimator methodology.

**6. The previous occupier's history, for people moving home.**
- On a move-in the EAC or AQ belongs to the meter point, not the person, so a new tenant inherits the previous household's consumption profile. Citizens Advice tells movers to read the meters on the day they arrive "so they can produce an accurate first bill" (https://www.citizensadvice.org.uk/consumer/energy/energy-supply/moving-home-your-energy-supply/moving-home-dealing-with-your-energy-supply/).
- *Analysis:* a household of one moving into a home last occupied by a family of five, or the reverse, starts with a systematically biased forecast. The simulation should model this explicitly.

*Simulation implication (analysis):* model the opening forecast error as a mixture.
- A small error where a smart meter, or a valid EAC or AQ, is available.
- A medium error where the customer declared their own figure.
- A large, structurally biased error where a TDCV default or the previous occupier's history was used.

The forecast should then converge as the switch completes and actual reads arrive.

### a.2 The opening read at change of supplier

**Purpose.** A Switch Meter Reading (SMR) is used for both the losing supplier's closing bill and the gaining supplier's opening bill. It marks the point where responsibility for consumption moves between them. The standard gas process sits in the UNC and the electricity process in the BSC (https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/rec_v2.0_-_switch_meter_reading_exceptions.pdf). That document is the 2018 REC v2.0 consultation draft; the live REC schedule may differ **[unverified]**.

**Smart meters (DCC-enrolled).** The gaining supplier reads the meter remotely. In the draft REC procedure, the exception process starts if the losing supplier has a reading but has not received a proposed SMR from the gaining supplier within 10 Working Days. A single-element smart meter may need 48 time-of-use registers plus the cumulative register transferred (same URL).

**Customer-provided reads.** If no read is available, the gaining supplier can ask for a Customer Own Read or send a meter reading agent within 10 Working Days (same URL). Citizens Advice also advises customers to read meters on move-in and move-out days (URL above).

**The deemed read (electricity, D0086).**
- If no valid actual reading arrives, the NHH Data Collector creates a *deemed* change-of-supplier reading and sends it on the D0086 flow.
- Elexon's CP0768 records that many NHH Data Collectors that have not received a D0086 by SSD+8 (eight days after the Supply Start Date) fall back on their own historical data from when they last held the supply. It warns of "a significant risk that poor data will be used resulting in disputed reads", because several months may have passed between transfers (https://www.elexon.co.uk/change-proposal/cp0768/).
- The deemed value is generally computed by rolling forward from the last valid read using the EAC and the profile **[unverified]**. Neither fetched source states the formula.
- For gas, the procedure starts if no actual or estimated read comes from the Gas Retail Data Agent within 15 Working Days (losing supplier) or 17 Working Days (gaining supplier). For electricity on non-DCC meters the limits are 30 and 32 Working Days (https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/rec_v2.0_-_switch_meter_reading_exceptions.pdf).

**Read disputes.**
- Who and when: the consumer, losing supplier or gaining supplier can raise a dispute within **12 months** of the Supplier Effective From Date. The consumer can contact either supplier and does not need to name the other (same URL).
- Materiality thresholds: **250 kWh** for electricity and **1,200 kWh** for gas. Below them, the supplier should normally offer an accommodation, such as a cash allowance, and keep the original SMR. Above them, or if the consumer rejects the accommodation, a dispute is raised (same URL).
- Data flows: D0300 for electricity and SAR flows for gas, with a 5 Working Day response target and escalation at days 5, 10 and 15 (same URL).
- *Simulation implication:* a deemed opening read is a latent error. It surfaces only when the first actual read arrives, often months later, as a "catch-up" either up or down.

### a.3 How suppliers set and review the first direct debit

**The licence rule (SLC 27.15).**
- Ofgem's decision of 26 August 2022 amended SLC 27.15 by removing two qualifiers: the "all reasonable steps" qualifier and the exemption where a Principal Term of the contract says otherwise. Suppliers must now set fixed DDs on the "best and most current information available" in every case. That includes meter readings and information from consumers and third parties about their circumstances and preferences (https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20letter%20DD%20rules.pdf). The change took effect 56 days after publication, around 21 October 2022 (same URL).
- Ofgem said suppliers need not reset a DD every time new information arrives. They should reassess when information is likely to have a *material* impact (same URL).
- Ofgem *rejected* fixed review intervals, quarterly reviews, on-demand reviews and a 12-month balance limit (same URL). There is no mandated "3-month" or "6-month" first review for new customers. Those intervals are supplier choices.

**The Ofgem Direct Debit Market Compliance Review (2022–23).**
- July 2022: Ofgem reviewed DD setting at the large suppliers after the April 2022 cap rise (https://www.ofgem.gov.uk/press-release/ofgem-requires-improvements-energy-suppliers-customer-direct-debits).
  - Over 7 million standard variable tariff customers saw DD increases between February and April 2022, averaging **62%**, and about 8% (around 500,000 households) saw rises above 100%.
  - The cap itself rose 54% for a medium user (same URL).
  - Ratings: no significant issues for British Gas, EDF, ScottishPower and SO Energy. Minor weaknesses for Bulb, E.ON, Octopus, Outfox the Market, OVO, Shell and Utility Warehouse. Moderate or severe weaknesses for Ecotricity, Good Energy, Green Energy UK, Utilita, TruEnergy and UKEIH (https://www.ofgem.gov.uk/decision/ofgem-seeks-improvements-12-suppliers-relation-customer-direct-debit-setting).
- February 2023 progress update (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update):
  - 56 concerns were raised, and 53 (95%) had been resolved.
  - Almost 1 million DDs were in scope for the "100%+ increase" review. Issues were confirmed on about 4,000, and £117,580 of compensation was paid.
  - The improvements secured work as de facto supplier commitments:
    - More frequent adequacy assessments.
    - Tolerance-triggered extra reviews when a DD rises beyond a set threshold.
    - Surplus credit refunded or used to lower the DD.
    - Faster refunds on request.
    - Formal DD and refund policies.
    - Clearer communications and self-serve portals.
  - Best-practice expectations: review DDs in line with quarterly cap changes, reduce DDs for customers in credit so the account heads towards **near zero over 12 months**, and return credit promptly on request.
  - Drivers of DD increases that Ofgem named: leaving cheap fixes for SVTs, credit or debit balances being factored in, **"estimated billing that differs from later meter readings, often leaving a debit balance"**, and quarterly cap changes against 12-month DD forecasts.
- Related credit-balance policy: in March 2021 Ofgem consulted on automatic annual refunds of credit above £0 for fixed-DD customers and protection of credit above a threshold, covering up to £1.4bn of surplus credit, about £65 per household (https://ofgem.gov.uk/publications/ofgem-reforms-could-see-credit-balances-around-ps14-bn-automatically-returned). I could not confirm that the auto-refund was adopted as drafted **[unverified]**. The August 2022 SLC 27.15 tightening came out of that same credit-balance workstream (https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20letter%20DD%20rules.pdf).
- "2023–24 DD rules": beyond the February 2023 update I found no new DD-specific licence change in 2023–24. Ofgem wrote to the ESNZ Committee on credit balances in December 2023 (https://www.ofgem.gov.uk/sites/default/files/2023-12/ESNZ%20Committee%20letter%20on%20CCBs.pdf), but I did not read its content **[unverified]**.
- Switching speed: since 1 April 2024 a switch that takes more than 5 working days earns the customer £30 automatically (https://uk.news.yahoo.com/british-gas-ovo-edf-eon-061513470.html; secondary source).

### a.4 Named supplier practice

MSE's supplier-by-supplier DD guide (https://blog.moneysavingexpert.com/utilities/energy-direct-debits) is the main comparative source, together with supplier help pages:

| Supplier | Review cadence | Customer control | Credit and refund stance |
|---|---|---|---|
| **Octopus** | Constant background review. Help page: after "a few months" an "account health check" may suggest a change, with an email beforehand (https://octopus.energy/help-and-faqs/articles/monthly-payments/) | Change anytime online; must speak to Octopus to reduce while in debt; Balance Forecast tool shows the 12-month projected balance (same URL) | Aims for about a month's credit by end of April; refund anytime with a read or a working smart meter (MSE URL) |
| **Octopus variable DD** | Each bill is collected in full 10 working days after it is emailed (https://octopus.energy/help-and-faqs/articles/variable-direct-debit/) | Some customers can switch in the dashboard; most need an agent (same URL) | No credit build-up; much higher winter payments; a smart meter is recommended; unusually large bills are held for review (https://octopus.energy/blog/variable-direct-debit-guide/) |
| **OVO** | Checked daily, but updated only every three months if needed, plus after SVT price announcements (MSE URL) | Reduce up to 10% below recommended (MSE URL) | Aims for 1 month's payment in credit by end of March. New joiners aim for no balance owed after one year. Refund needs 90+ days open, 2+ DD payments, reads within 28 days unless smart, and at least £5 (https://ovoenergy.com/help/direct-debit-review) |
| **OVO "smart payments"** | **[unverified]**: the OVO help page does not mention a product by this name (same URL) | — | — |
| **British Gas** | One or two formal reviews a year, with background monitoring (MSE URL) | Increase anytime; decrease only to the recommended amount (MSE URL) | Refund on request, no minimum (MSE URL) |
| **EDF** | Every three months; new rates feed into the next review (MSE URL) | Reduce up to 10% below recommended (MSE URL) | Refund on request, which may raise ongoing payments (MSE URL) |
| **E.ON Next** | Every three months, plus after confirmed price changes (MSE URL) | Reduce up to 10% below recommended online (MSE URL) | Refund on request; may need a read (MSE URL) |
| **Scottish Power** | Constant background review, but updated only every three months (MSE URL) | Online DD manager; decreases stop at a threshold (MSE URL) | Refund anytime, or choose refunds at each review, otherwise credit is spread over 12 months (MSE URL) |
| **So Energy** | At least twice a year, plus after price changes and when usage moves outside tolerance (MSE URL) | Limits vary (MSE URL) | Refund, or lower the DD (MSE URL) |
| **Fuse** | No periodic review; variable DD only (MSE URL) | Wallet top-ups (MSE URL) | Refund with a read within 14 days (MSE URL) |
| **Outfox** | Every three to six months; payments split evenly or weighted to winter (MSE URL) | Contact to review (MSE URL) | Refund if credit exceeds one month's DD (MSE URL) |

Further general points from the MSE guide (MSE URL):
- Standard DDs are the estimated annual cost divided by 12.
- Debt or credit is spread over the next 12 months.
- Notice of a DD change ranges from 5 working days to one month, with 14 days common.

None of the sources named a specific *first* review point for new customers, such as "3 months after joining" (MSE URL, "not stated" for every supplier). Octopus's "after a few months" is the closest (https://octopus.energy/help-and-faqs/articles/monthly-payments/). A blanket "most suppliers review about twice a year" comes from Loop (https://kb.loop.homes/knowledge/how-will-my-new-supplier-calculate-my-direct-debit). A specific 3-month or 6-month first review for any named supplier is **[unverified]**.

**Pros and cons of each approach (analysis, grounded in the sources above):**

- **Fixed or level DD with periodic review** (British Gas, EDF, E.ON Next, Scottish Power).
  - Pros: payments are predictable, and summer credit funds winter (https://octopus.energy/blog/variable-direct-debit-guide/).
  - Cons: credit is held, and the lag between reviews lets errors compound. Infrequent reviews (British Gas: 1–2 a year) mean larger step changes when they happen.
- **Fixed DD with continuous monitoring and a credit target** (Octopus about one month by April, OVO one month by March).
  - Pros: smaller, earlier corrections.
  - Cons: a deliberate credit buffer holds customer cash, and it reads as "overcharging" to people who don't know the target exists. OVO's refund conditions add friction (https://ovoenergy.com/help/direct-debit-review).
- **Variable or pay-what-you-use DD** (Octopus variable DD, Fuse).
  - Pros: no credit is held, and there is no forecast error to correct later.
  - Cons: winter payments are much higher, so affordability shocks are seasonal. Several payments in one month are possible. It depends on smart reads, with estimated bills otherwise (https://octopus.energy/blog/variable-direct-debit-guide/).
- **Customer-adjustable bounds** (EDF, E.ON Next and OVO allow −10%).
  - Pros: give customers some agency.
  - Cons: let customers under-pay and build arrears (MSE URL).

---

## Part (b): What goes wrong for customers

### b.1 DD too low leading to arrears and a big step-up

- Ofgem names "estimated billing that differs from later meter readings, often leaving a debit balance" as a driver of DD increases (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update).
- When a debit balance is spread over 12 months *on top of* a re-forecast run-rate, the step-up is roughly additive. *Analysis:* a customer whose opening estimate was 30% low, discovered at month 6, faces both a 30% run-rate increase and recovery of six months of under-payment, so the DD rises well over 30%.
- Arrears at system level, Ofgem Q2 2026 (https://www.ofgem.gov.uk/data/debt-and-arrears-indicators):
  - Total debt and arrears reached **£5.02bn**.
  - 1,187,788 electricity accounts (4.0%) and 954,966 gas accounts (3.9%) were in arrears with no repayment arrangement.
  - Average un-arranged arrears were £1,872 for electricity and £1,613 for gas.
  - Ofgem notes that arrears include "direct debit customers who defaulted on payments" but publishes no split by payment method.
- A Citizens Advice debt expert reports that when a supplier refuses to lower an unaffordable DD, a prepayment meter may be presented as the only option, which the author argues is wrong under SLC 27.5 (https://medium.com/adviser/utility-debt-and-unaffordable-direct-debits-944d10e7dd2a).

### b.2 DD too high leading to credit build-up and refund requests

- The MSE survey of April–May 2022 drew 41,000+ self-selected responses; the analysed sample was 4,177 (https://blog.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey).
  - Among in-credit customers on the price cap, **25%** had their DD at least doubled against a 54% cap rise. Doubling rates by supplier: British Gas 33%, Octopus 32%, Shell 30%, E.ON 27%, EDF 25%, Bulb 21%, OVO 15%, SSE 15%.
  - 46% of those whose DD doubled had **not challenged** it, mainly because they didn't know they could.
- MSE also reported that a quarter of in-credit price-cap customers said their DD had doubled (https://blog.moneysavingexpert.com/news/2022/07/ofgem-review-energy-supplier-s-direct-debits).
- Refund friction: OVO's conditions are 90 days open, 2 DD payments, reads within 28 days and at least £5, and refunds may push the DD up later (https://ovoenergy.com/help/direct-debit-review).
- On a home move the losing supplier should send the final bill within 6 weeks and refund credit within 10 working days of it, with compensation due if either deadline is missed (https://www.citizensadvice.org.uk/consumer/energy/energy-supply/moving-home-your-energy-supply/moving-home-dealing-with-your-energy-supply/).

### b.3 Estimated bills, catch-up bills and bill shock in year one

- **Back-billing (SLC 21BA):** suppliers may not bill domestic or microbusiness consumers for energy used more than 12 months before the bill. The exception is obstructive or "manifestly unreasonable" consumer behaviour; simply not providing a meter reading does *not* qualify (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf).
- Back-billing made up about 10% of Ombudsman and Citizens Advice cases at the time (same URL).
- The Energy Ombudsman accepted 3,216 back-billing cases in 2025, against 3,238 in 2024 (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025).
- Read-based billing: the median share of consumers receiving a read-based bill in the past year was about 94.4–94.8% in 2017, and about 6% of smart meter customers were still getting estimated bills (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf).
- Citizens Advice now scores "billing accuracy" as the share of bills based on a meter reading. Smart customers are measured over the last 6 months and traditional-meter customers over 12 months. Five stars needs more than 98% (https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/).
- *Analysis:* for a new account, the first actual read after a deemed opening read, or after a TDCV-based estimate, is the moment of bill shock. Year one is therefore peak-risk, and the 12-month back-billing cap limits the supplier's recovery only if the error goes unnoticed for more than a year.

### b.4 New tenants on deemed contracts

- A person moving into a property is automatically placed on a "deemed contract" at the supplier's default or standard variable tariff once they tell the supplier they have moved in. They can switch tariff or supplier once responsible for the property; a new supplier should complete the switch within 5 working days; and they must still pay at least one bill to the incumbent (https://www.citizensadvice.org.uk/consumer/energy/energy-supply/moving-home-your-energy-supply/moving-home-dealing-with-your-energy-supply/).
- Detail on deemed contracts (SLC 7) and on whether exit fees can apply to them is **[unverified]**; the Citizens Advice page does not cover it (same URL).
- Pain mechanics (analysis): the tenant often does not know who the supplier is, inherits the previous occupier's EAC or AQ, may not give a move-in read, and receives a first bill that mixes estimated consumption with an unknown opening read. Moving-in reads are the main protection (same URL).

### b.5 Comparison-site quotes built on default usage

- TDCVs are the reference consumption "where actual consumption is unknown" (https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf).
- The 2026 cut (medium electricity 2,700 to 2,500 kWh, gas 11,500 to 9,500 kWh, same URL) lowers illustrative quotes. *Analysis:* a household whose real use sits at the old medium will see a quote, and possibly a first DD, about 7% low on electricity and about 17% low on gas.
- How each comparison site defaults usage, and how much that quote is passed through to the supplier's first DD, is **[unverified]**.

### b.6 Complaint statistics

**Energy Ombudsman.**
- 2025: 80,256 cases accepted, down 14% from 92,938 in 2024. Billing disputes were **56%** of disputes reviewed. Back-billing cases numbered 3,216. Supplier signposting averaged 48%, with a range of 25–68% (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025).
- H1 2026: 46,532 cases accepted, **up 16%** year on year and the third consecutive quarterly rise. Billing was **58%** of the total (https://www.energyombudsman.org/news/energy-ombudsman-h1-data-2026):

| Category | H1 2025 | H1 2026 | Change |
|---|---|---|---|
| Billing | 23,441 | 27,006 | +15% |
| Smart meters | 4,555 | 4,817 | +6% |
| Customer service | 3,666 | 3,500 | −5% |
| Standard meters | 1,097 | 1,095 | −0.2% |

  These four categories do not sum to the total.

**Citizens Advice star rating** (https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/):
- Category weights: Ease of Contact 30% (call wait 18%, email 6%, other channels 6%); **Billing and Metering 25%** (billing accuracy 15%, smart meter operation 10%); Complaints to third parties 35%, scored per 10,000 customers (5 stars at 5 or fewer, 0.5 stars above 80); Customer Commitments 10%.
- Billing accuracy bands run from more than 98% for 5 stars down to below 90% for 1 star.
- A revised methodology applies from the March 2026 release (decision 28 August 2025) (https://www.citizensadvice.org.uk/policy/publications/decision-document-on-revised-methodology-for-the-citizens-advice-star-rating-aug-25/). I could not confirm whether the page I fetched shows the old or the revised weights **[unverified]**.

**Ofgem customer service data** (https://www.ofgem.gov.uk/customer-service-data):
- Q2 2026 complaints per 100,000 accounts: **936** across all suppliers (−11% year on year), 919 for large, 1,529 for medium (+10% year on year) and 161 for small.
- January 2026 satisfaction among credit-meter customers: billing accuracy **80%** (down from 82%), ease of understanding bills 82% (down from 85%), overall service 77% (an all-time high), switching process 87%.
- Ofgem does not publish a complaints-by-category split; suppliers publish their own top 5 complaint reasons (same URL).

**Which?**
- January 2026 survey: 11,945 customers, fieldwork September–October 2025, 17 suppliers (https://www.which.co.uk/reviews/energy-companies/article/best-and-worst-energy-companies).
- Total scores: E 79%, Octopus 74%, E.ON Next 66%, OVO 61%, British Gas 59%, EDF 58%, Scottish Power 56%.
- Bill accuracy stars: Octopus 3, E.ON Next 3, British Gas, OVO, EDF and Scottish Power 2 each.
- Which? weights its own assessment as complaints 30%, contact 25%, support 25%, smart meters 10%, switching 10% (same URL).
- Older Which? complaint data (October 2021, n = 8,803) (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T):
  - 14% had an issue; 89% of those complained; 47% of complainants were dissatisfied with handling.
  - Bills or statements made up **44%** of complaints and payments 24%.
  - Among payment, bill or price complainants: 32% had a one-off payment taken without warning, 21% received an inaccurate bill, **13% saw their DD increase without warning**, and 9% struggled to get a credit refund.

---

## Part (c): Pain points and GB evidence on how customers react

The evidence on *quantified behavioural reaction*, such as churn elasticity to a DD increase, is thin in public GB sources. What exists is listed below, with gaps flagged.

**P1. Opening estimate wrong (default-based or inherited).**
- Link to complaints: billing is 56–58% of Ombudsman cases (https://www.energyombudsman.org/news/energy-ombudsman-h1-data-2026).
- Ofgem names estimate-versus-read divergence as a cause of debit balances and DD rises (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update).
- No GB figure was found for how opening-estimate error translates into churn **[unverified]**.

**P2. DD step-up after the first review.**
- Complaints: 13% of payment, bill or price complainants cited a DD increase without warning (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T).
- Contacts: billing was the second most common reason to contact a supplier, at 21% (Q1 2022). One respondent quoted: "The direct debit went from £80 per month to £140" (https://www.ofgem.gov.uk/sites/default/files/2022-07/Consumer%20Perceptions%20of%20energy%20markets%20%20Q1%202022.pdf).
- Passivity: 46% of customers whose DD doubled did not challenge it (https://blog.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey). That is a useful *inertia* parameter: about half of customers absorb a large increase without contact.
- Payment default: 13% of credit-meter consumers had fallen behind on a bill in Q1 2022, up from 9% in Q4 2021. Of those who fell behind, 43% contacted their supplier, and among credit-meter customers who fell behind only 31% reached out first (same Ofgem Q1 2022 URL).
- DD cancellation rates after an increase: no public figure found **[unverified]**.

**P3. Excess credit or refund friction.**
- Complaints: 9% of payment complainants had difficulty getting a refund (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T).
- Regulatory salience: suppliers committed to proactive refunds and lower DDs for customers in credit (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update).
- Trust: the 2022 episode drew public accusations from consumer champions; MSE coverage reported that energy rises "smell wrong" (https://www.inkl.com/news/martin-lewis-says-energy-bill-rises-smell-wrong-as-direct-debits-double-for-1-in-4; secondary source).

**P4. Catch-up or back-bill (bill shock).**
- Complaints: about 10% of Ombudsman and Citizens Advice cases in 2017–18 (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf); 3,216 Ombudsman back-billing cases in 2025 (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025).
- Churn intent: an Opower survey of 1,000 British customers found almost 61% said they *would* switch after an unexpectedly high bill (https://www.heatingsave.co.uk/blog/news/over-61-percent-of-customers-to-switch-suppliers-after-getting-a-high-bill-survey-says). That is stated intent, the date is unknown and the source is secondary, so treat it as **[unverified]** as a behavioural rate. Actual switching after bill shock will be far lower because of inertia.

**P5. Estimated bills (no reads).**
- Measured directly by Citizens Advice "billing accuracy" (15% of the star rating) (https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/).
- Satisfaction with billing accuracy is falling: 80% in January 2026 against 82% previously (https://www.ofgem.gov.uk/customer-service-data).

**P6. Opening-read dispute (deemed D0086).**
- Disputes are allowed for 12 months, with thresholds of 250 kWh (electricity) and 1,200 kWh (gas) (https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/rec_v2.0_-_switch_meter_reading_exceptions.pdf).
- Elexon flags poor fallback data as a dispute driver (https://www.elexon.co.uk/change-proposal/cp0768/).
- Frequency of CoS read disputes: **[unverified]**.

**P7. Deemed-contract new tenant.**
- Placed on SVT or default rates automatically (https://www.citizensadvice.org.uk/consumer/energy/energy-supply/moving-home-your-energy-supply/moving-home-dealing-with-your-energy-supply/).
- No GB data found on deemed-customer complaint or churn rates **[unverified]**. *Analysis:* deemed customers are among the most likely to switch away early because they never actively chose the supplier.

**P8. Slow or failed switch.**
- £30 automatic compensation after 5 working days since April 2024 (https://uk.news.yahoo.com/british-gas-ovo-edf-eon-061513470.html).
- Switching satisfaction: 87% (https://www.ofgem.gov.uk/customer-service-data).

**P9. Poor complaint handling compounds the original pain.**
- 47% of complainants were dissatisfied with handling and 14% unresolved (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T).
- Supplier signposting to the Ombudsman averaged only 48% in 2025 (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025).

**Gaps worth stating plainly.** No public GB source quantified:
1. The churn elasticity to a DD increase of x%.
2. The DD cancellation rate after an increase.
3. The share of customers who actually switch after bill shock.

The simulation should treat these as calibrated assumptions with sensitivity ranges. Suppliers hold this data internally, and Ofgem's RFIs collected DD distributions (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update), but none of it is published per customer.

---

## Part (d): The gap between billing and settlement in the first months

**The two clocks.**
- **Settlement clock.** Electricity is settled through Elexon's runs. The current timetable runs from the Initial Settlement run through to Final Reconciliation (RF) at **14 months**. Under Market-wide Half-Hourly Settlement (MHHS), RF falls to 7 months from 1 April 2027 and to 4 months from 2 July 2027, and the first financial run (SF) moves from 15 to 7 Working Days, subject to an April 2027 decision (https://www.elexon.co.uk/bsc/article/new-settlement-timetable-reducing-from-14-months-to-seven-months-from-april-2027/).
- Meter migration to half-hourly began on 22 October 2025, with all meters due by 7 May 2027 and the old and new regimes running together until July 2027 (https://www.elexon.co.uk/2025/10/22/suppliers-start-moving-meters-to-half-hourly-settlement-hitting-a-major-milestone-for-clean-power-2030/).
- **Billing clock.** The customer is billed on the supplier's own reads and estimates, and the DD collects a level forecast.

**Why the gap is widest in a new account's first months (analysis, supported where cited):**

1. **Volume allocation.** For NHH meters, settlement allocates volume from EAC and AA values, so a wrong EAC "shifts energy between Suppliers". It also raises DUoS and TNUoS charges and has to be fixed before the last reconciliation run, or through a Trading Dispute afterwards (https://www.elexon.co.uk/guidance-note/erroneous-large-eacaas-management-resolution/).
   - Incorrect CoS readings are a listed root cause (same URL). A new customer with a deemed opening read and an inherited EAC can therefore be mis-settled *and* mis-billed, in different directions, until actual reads flow.
   - The supplier pays settlement on the EAC view while it bills on its own estimate, and each is corrected on a different timetable.
2. **Imbalance exposure.** The supplier hedges and buys wholesale energy against its forecast of portfolio demand. If new customers' true consumption differs from the opening forecast (TDCV defaults, inherited EAC), the difference is cashed out at imbalance prices in settlement **[unverified]**. Elexon's imbalance pricing mechanics were not fetched. Under MHHS, actual half-hourly data from smart meters will shorten the period over which this mis-estimate persists (https://www.elexon.co.uk/2025/10/22/suppliers-start-moving-meters-to-half-hourly-settlement-hitting-a-major-milestone-for-clean-power-2030/).
3. **Revenue recognition and unbilled revenue.** Suppliers recognise revenue for energy supplied, including an **unbilled revenue** estimate for consumption not yet read or billed.
   - Centrica's auditor treats "unread revenue", meaning billed and unbilled, as a Key Audit Matter because of "the consumption estimations required to be made in respect of unread meters".
   - The auditor recalculates British Gas Energy's unbilled estimate and compares prior-period estimates with later billed activity (https://www.centrica.com/media/3srnxu5f/centrica-ara25-financial-statements.pdf).
   - For a growing book of new accounts, unbilled revenue rests on the least reliable consumption data the supplier holds, so the estimation risk sits mostly on recent joiners.
4. **Cash versus revenue.** A level DD collects cash ahead of winter use. Credit balances are a liability (customer cash held), and Ofgem's 2021 consultation tied the size of credit balances to supplier failure and mutualisation risk (https://ofgem.gov.uk/publications/ofgem-reforms-could-see-credit-balances-around-ps14-bn-automatically-returned).
   - Under-set DDs create receivables that may become bad debt: system-wide arrears stand at £5.02bn (https://www.ofgem.gov.uk/data/debt-and-arrears-indicators).
   - A first DD set too low therefore turns a forecast error into working-capital *and* credit risk. One set too high creates regulatory and complaint risk (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update).
5. **The back-billing cap ties the clocks together.** If a new account's under-billing goes unnoticed for more than 12 months, SLC 21BA stops recovery of the older consumption (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf). Settlement may still have charged the supplier for it, so the supplier carries the loss.

**Simulation implication (analysis):** model at least three ledgers per new account, each corrected on its own timetable:
- Settled volume (EAC-based now, HH actuals after MHHS).
- Billed volume.
- Cash collected.

The supplier's P&L should feel the *difference* through imbalance cost, unbilled revenue true-ups, bad debt and back-billing write-offs.

---

## Summary table: pain points

| # | Pain point | How the customer meets it | Measurable signal | Evidence of customer reaction (URL) | Suggested simulation behaviour |
|---|---|---|---|---|---|
| 1 | Opening estimate wrong (TDCV default, declared figure, inherited EAC or AQ) | First DD feels too low or too high; first real bill diverges | Forecast error % at month 3 and 6 (estimated against read-based annualised use) | Ofgem names estimate-versus-read divergence as a cause of debit balances (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update) | Draw opening error by data source (smart < EAC/AQ < declared < TDCV < previous occupier); error decays as reads arrive |
| 2 | DD step-up at first review | Notice of a large increase, often after a few months | DD change %; contact within 14 days; DD cancellations; arrears onset | 13% of payment complainants saw a DD rise without warning (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T); 46% of those doubled did not challenge (https://blog.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey) | Probability of contact and complaint rises with step size; about 50% inert even at +100%; affordability-constrained households default or cancel the DD |
| 3 | Debit balance or arrears from a DD set too low | Balance grows; then recovery is added to the DD | Debit balance £; days past due; repayment plans | 13% of credit-meter consumers fell behind (Q1 2022); 43% of those contacted the supplier (https://www.ofgem.gov.uk/sites/default/files/2022-07/Consumer%20Perceptions%20of%20energy%20markets%20%20Q1%202022.pdf); £5.02bn system arrears (https://www.ofgem.gov.uk/data/debt-and-arrears-indicators) | Payment default hazard depends on DD/income ratio; a minority seek help proactively |
| 4 | Excess credit and refund friction | Credit visible in the app; refund refused or conditional | Credit balance per account; refund requests; refund cycle time | 9% of payment complainants struggled to get a refund (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T); OVO's refund conditions (https://ovoenergy.com/help/direct-debit-review) | Refund request probability rises with credit / monthly DD; a refusal lowers trust and raises complaint probability |
| 5 | Estimated bills | No read; bill marked "estimated" | % of bills read-based (6 or 12 months) | Citizens Advice billing accuracy metric (https://www.citizensadvice.org.uk/about-us/how-citizens-advice-works/citizens-advice-consumer-work/supplier-performance/energy-supplier-performance1/how-the-scores-are-worked-out/); billing-accuracy satisfaction down to 80% (https://www.ofgem.gov.uk/customer-service-data) | Each consecutive estimate slightly lowers trust; latent error accumulates for P6 |
| 6 | Catch-up or back-bill shock | First actual read reveals under-billing | Catch-up £ against monthly DD; back-bills over 12 months | About 10% of cases were back-billing (https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf); 3,216 Ombudsman back-billing cases in 2025 (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025); 61% state they'd switch after a high bill [unverified] (https://www.heatingsave.co.uk/blog/news/over-61-percent-of-customers-to-switch-suppliers-after-getting-a-high-bill-survey-says) | Large spike in contact and complaint probability; churn intent high but realised churn damped by inertia; supplier write-off of over-12-month portion |
| 7 | Opening-read dispute | Closing and opening bills don't match the customer's read | Disputes raised; accommodations paid; resolution days | 12-month window, 250 / 1,200 kWh thresholds (https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/rec_v2.0_-_switch_meter_reading_exceptions.pdf); poor fallback data (https://www.elexon.co.uk/change-proposal/cp0768/) | Customers with a photo read dispute; below threshold, accept an accommodation; above, a dispute workflow costs time |
| 8 | Deemed-contract new tenant | Auto-placed on SVT; previous occupier's profile; unknown supplier | Time to first contact; time on deemed terms; early loss rate | Deemed-contract mechanics (https://www.citizensadvice.org.uk/consumer/energy/energy-supply/moving-home-your-energy-supply/moving-home-dealing-with-your-energy-supply/); churn rates [unverified] | High early switch-away probability; inherited EAC bias in the opening forecast |
| 9 | Default-based comparison quote | Quote and DD built on low/medium/high | Quote-to-actual gap; complaints citing "quote" | TDCV medium cut to 2,500 / 9,500 kWh (https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf) | Households above the TDCV medium start under-paying; perceived broken promise at the step-up |
| 10 | Poor complaint handling | Complaint unresolved; not told about the Ombudsman | Complaints per 100k; 8-week deadlock rate; signposting % | 47% dissatisfied with handling (https://www.which.co.uk/news/article/common-energy-company-complaints-a1fN84z7760T); 936 complaints per 100k (https://www.ofgem.gov.uk/customer-service-data); 48% signposting (https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025) | Escalation to the Ombudsman after 8 weeks; feeds the star-rating complaints score; trust shock |

## Supplier levers to experiment with

1. **Opening-estimate source hierarchy**: wait for the EAC or AQ before the first DD, or apply TDCV defaults with a margin.
   - Metrics: forecast error at months 3 and 6; first-review step size; debit balances; imbalance cost on new joiners; unbilled-revenue true-up.
2. **Timing of the first DD review**: 1, 3 or 6 months after the switch, or triggered by the first actual read.
   - Metrics: DD step size; contacts; complaints per 100k; arrears onset; churn at 12 months.
3. **Review cadence and tolerance trigger**: continuous, quarterly or twice yearly; a ±x% band that triggers a reassessment (https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update).
   - Metrics: frequency and size of DD changes; complaints; credit and debit balance distributions; regulatory compliance risk.
4. **Credit target**: zero by month 12, or one month by the end of winter (Octopus and OVO style).
   - Metrics: credit held (£ liability); refund requests; arrears in winter; trust; working capital.
5. **Spreading period for debit recovery**: 12 months as standard, or longer for affordability-flagged customers.
   - Metrics: DD step size; default rate; bad debt; repayment-plan uptake.
6. **Step-change cap and phasing**: cap any single rise, for example at +30%, and phase the rest.
   - Metrics: complaint probability; DD cancellations; arrears; time to balance neutrality.
7. **Variable or pay-what-you-use DD for smart customers** (Octopus variable DD style).
   - Metrics: credit held; winter affordability defaults; payment failures; estimated-bill exposure.
8. **Proactive refunds**: automatic refunds above a threshold, against refunds on request with conditions.
   - Metrics: credit liability; refund-related complaints; trust; DD increases after refunds.
9. **Read capture at switch and move-in**: app photo read prompts, smart-read retrieval SLAs, and an early meter-reader visit for non-smart homes.
   - Metrics: share of deemed D0086 or estimated SMRs; CoS disputes; billing-accuracy score; catch-up bills.
10. **Smart meter installation and commissioning prioritised for new joiners.**
    - Metrics: read-based bill %; smart operation %; catch-up incidence; settlement accuracy.
11. **Communications on DD changes**: notice length (5 days to 1 month), explanation quality and a forecast tool (Octopus Balance Forecast).
    - Metrics: contacts per DD change; challenge rate; complaints; trust.
12. **Back-billing guard**: alert on accounts approaching 12 months without a read.
    - Metrics: write-offs under SLC 21BA; back-billing complaints; Ombudsman cases.
13. **Deemed-customer onboarding**: rapid contact, a move-in read, and an offer to move onto a chosen tariff.
    - Metrics: early churn of deemed customers; opening-forecast error; first-bill complaints.
14. **Complaint handling and Ombudsman signposting.**
    - Metrics: complaints per 100k; 8-week deadlock rate; signposting %; star rating (35% weight on complaints).
15. **Allowed customer DD adjustment band**, for example −10% below recommended.
    - Metrics: customer agency and satisfaction against arrears build-up.

---

**What I could not confirm, in one place:**
- OVO's "smart payments" product.
- Any supplier's specific first review at 3 or 6 months for new customers.
- New 2023–24 DD licence rules beyond the 2022 SLC 27.15 change and the February 2023 compliance update.
- Whether Ofgem's 2021 auto-refund proposal was adopted.
- How comparison sites set default usage.
- The D0086 deeming formula.
- Xoserve rolling AQ mechanics.
- Imbalance price mechanics.
- Deemed-contract (SLC 7) detail.
- Any published GB churn elasticity for a DD increase or for bill shock. The Opower figure of about 61% is stated intent from a secondary source.

These should be calibration parameters in the simulation, not evidence.
## Done

2026-10-30, the worker. The knowledge this pack was for is written and published:
`docs/market_research/a_new_accounts_first_months_2026-10-30.md` (topic `payments-and-direct-debit`,
whose site entry now points at it). It covers the opening-estimate rungs, the opening read, what named
suppliers do about the first DD with pros and cons, ten pain points each defined before it is measured,
and the levers set against what the world does today (the 30 Oct pain-point audit).

- **Verified first-hand:** Ofgem's 27 May 2026 TDCV decision, Table 1, text extracted from the PDF. Its
  PC2 row (1,900 / 3,400 / 6,100 kWh) closes a GAP that `what_a_supplier_holds_to_size_a_direct_debit.md`
  §3 and `company/billing/annual_consumption_estimate.TDCV_BY_DATE` both carried as "not established".
  Both now hold it. No 2016-2025 book reads that row.
- **Everything else** is graded [P] (the pack's URL, not re-read) and its [unverified] items stay GAPs.
- **The read-duty correction** was checked: the invariant library already holds an annual duty
  (`INV_READ_DUTY_ANNUAL`, with the repealed inspection duty named). Nothing to correct.
- **SIM reaction and the experiment** are not built here. They are `new-account-first-months-experiment`
  in `docs/direction/priority_order.yaml`, drawn after the correctness exit test.
