# UK Energy Supplier Debt Management — Research Findings

Sources: Ofgem debt/arrears indicators, Citizens Advice, Watt-Logic, Ofgem PPM review, Ofgem debt strategy

## 1. Debt Lifecycle and Timeframes

| Stage | Timeframe | Notes |
|-------|-----------|-------|
| Bill issued | T+0 | Payment due 14–28 days |
| Overdue / first reminder | T+7–14d post-due | SLC 27: must identify financial difficulty, not just chase |
| Formal written demand | ~ T+3–4 weeks | Mandatory 28-day wait before disconnection notice can be sent |
| Repayment plan offer | Before further action | SLC 27.8: must be based on ability to pay; must be offered before escalating |
| Disconnection notice (7 days) | 28 days after written demand | Earliest possible: demand + 28d + notice + 7d = ~5 weeks minimum |
| PPM warrant / disconnection | After 7-day notice | PPM now requires court warrant + vulnerability check; disconnection extremely rare |
| External DCA referral | ~60–90 days internal fail | If internal collections exhausted |
| County Court Judgement | 3–6 months+ | CCJs rising: 179 (2022) → 349 (2023) |
| Statute of limitations | 6 years from last payment | After 6 years, debt cannot be pursued through courts |

**Minimum timeline from first miss to legal disconnection: ~5 weeks** (unresponsive, non-vulnerable, non-winter customer).

**Backbilling limit:** 12 months — supplier cannot bill for consumption more than 12 months before bill date if customer not at fault.

**Home-move debt:** ~20–40% of total energy debt stock arises from customers moving without settling. Significantly harder to recover.

## 2. Payment Plans

**Mechanism:** SLC 27.8 requires affordable repayment arrangements. Fuel Direct (benefits deduction) floor: £3.70/week for arrears + current usage.

**Typical terms (Q4 2025 Ofgem data):**

| Metric | Electricity | Gas |
|--------|------------|-----|
| Average repayment duration | **365 weeks (7 years)** | **342 weeks (6.6 years)** |
| Average weekly repayment | £6.01/week | £4.40/week |
| Average debt under plan | £799 | £651 |

**Key observation:** Nearly three-quarters of total energy debt (by value) sits with customers who have no repayment plan — majority of debtors haven't engaged at all.

**Write-off estimate:** £1.1–1.7bn (~1/3 of total debt stock) ultimately written off. Blended portfolio ultimate loss rate ~30-35% of all aged receivables in current elevated environment (historic normal: 5–10%).

## 3. Prepayment Meters (PPM) and the 2023 Scandal

**PPM prevalence:** ~4.3 million UK households on PPM. 41% of electricity repayment plan customers and 38% of gas plan customers use PPM as the repayment mechanism.

**Demographics:** 47% of PPM customers are in the lowest income quintile; 23% have a disability or long-term health condition.

**The 2023 PPM warrant scandal:**
- British Gas contractors force-fitting PPMs in vulnerable homes without adequate checks
- 94,000 PPMs installed under warrant across industry 2018-2023 (British Gas, Scottish Power, OVO = 70%)
- All major suppliers paused warrant-based PPM installations in February 2023
- British Gas settlement: **£20m to Ofgem redress fund + £70m debt written off** for vulnerable customers
- From November 2023: vulnerable households exempt from forced switching; strict protocol required
- PPM moratorium cost suppliers ~£25m/month additional bad debt (Feb–Sep 2023)

**Self-disconnection (PPMs running out of credit):**
- ~3.2 million PPM customers self-disconnected at least once in 2024
- 63% of PPM customers self-disconnect at least once per year
- Q4 2025: 564,588 electricity + 412,268 gas customers self-disconnected
- ~800,000 people went more than 24 hours without supply because they couldn't afford to top up

## 4. Disconnection

**Process and protections:**
- **Winter moratorium (Oct–Mar):** Cannot disconnect if all residents are pensionable age or all are under 18
- **Year-round protection (large suppliers):** Disability, severe financial hardship, children under 6 — cannot disconnect
- **Priority Services Register (PSR) customers:** Extra steps required; cannot disconnect without exceptional circumstances
- **Reconnection:** Must occur within 24 hours of debt clearance + reconnection fee

**In practice:** Residential disconnection is now extremely rare. Suppliers use PPM, DCA, and CCJ instead. Reputational risk of disconnection is too high.

## 5. Bad Debt Rates and Write-Off

**By payment method:**
- **Direct debit customers:** ~1% of bills in bad debt (Ofgem allowance basis)
- **Standard credit customers:** ~6% of bills in bad debt

**Price cap bad debt allowances:**
- Baseline: ~£52/year per household (debt + collection costs embedded in cap)
- Temporary additional (from April 2024): +£28/year per DD or SC customer (for above-normal post-crisis debt)

**Total debt stock:** £4.43bn (June 2025) — up 71% since 2023, 20% year-on-year.

## 6. Vulnerable Customer Obligations (SLC 27)

**Priority Services Register (PSR):** Suppliers must offer and maintain. Eligibility: pensionable age, chronic illness, disability, children under 5, mental health conditions. Services: priority emergency support, advance outage notice, accessible billing, free meter readings, password scheme.

**Payment difficulty obligations (SLC 27.8):**
- Proactively contact customers showing payment difficulty signs
- Set repayment based on ability to pay
- No interest or penalty fees on domestic arrears
- Pause arrears collection if customer cannot cover current consumption
- Provide information on grants and hardship funds

## 7. IFRS 9 Debt Provisioning Matrix (Indicative)

| Debt age | Standard Credit customer | Direct Debit customer |
|----------|-------------------------|----------------------|
| 0–30 days | 1–2% | 0.3–0.5% |
| 31–60 days | 5–8% | 1–2% |
| 61–90 days | 15–20% | 5–8% |
| 91–180 days | 35–50% | 15–25% |
| 181–365 days | 60–75% | 40–60% |
| >365 days | 85–95% | 70–85% |

Calibration anchor: Ofgem shows SC customers generate ~6× the bad debt rate of DD customers.

**Vacancy/home-move debt:** 60–80% provision from point of identification (customer moved without forwarding address).

## Implications for Simulation

| Gap | Priority | Fix |
|-----|----------|-----|
| Bad debt by payment method | High | Model 1% (DD) vs 6% (SC) loss rate per year on revenue |
| Debt lifecycle stages | Medium | Add staged debt state to customer records (current → overdue → plan → write-off) |
| PPM self-disconnection | Low | Model as probabilistic consumption shortfall for lowest-income customers |
| IFRS 9 provision matrix | Medium | Apply aging buckets to receivables for realistic bad debt provision line in P&L |
| 12-month backbilling cap | Low | Already not in scope (billing cycles are within 12 months) |

**Quick win:** The single biggest simulation improvement is segmenting bad debt by payment method (1% vs 6%). If any of our customers are on standard credit rather than direct debit, bad debt expectation should be materially higher.

## Key Numbers

| Metric | Value |
|--------|-------|
| Customers in electricity arrears (Q4 2025) | 1.15m (3.9% of all customers) |
| Average electricity arrears (no plan) | £1,773 |
| Average electricity debt (on plan) | £799 |
| PPM households | 4.3 million |
| Annual write-off estimate | £1.1–1.7bn (~1/3 of debt stock) |
| Bad debt as % DD bills | ~1% |
| Bad debt as % SC bills | ~6% |
| Bad debt cap allowance | ~£52/year + £28 temporary |
| PPM plan average duration (electricity) | 365 weeks (7 years) |
| PPM weekly repayment (electricity) | £6.01/week avg |
| Minimum disconnection timeline | ~5 weeks from formal demand |
| Statute of limitations | 6 years |
| CCJs issued (2023) | 349 (up from 179 in 2022) |
