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

**Typical terms (Ofgem debt and arrears indicators, calendar 2025):** *corrected 2026-10-04 -- the
duration and weekly rows are for PREPAYMENT METERS INSTALLED FOR DEBT in the year (length agreed,
weighted by new installs), not for all plans and not realised durations; no credit-account figure is
published. See `domestic_repayment_plan_take_up_and_keep_rates.md`.*

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

> **UNSUPPORTED (2026-09-27).** No source was ever given for this matrix, and the one published age × method table found contradicts its DD front end: Centrica ARA 2025 Note 17 provisions ALL live DD debt past 90 days at 4.4–7.4%, against 15–25% here at 91–180 days. Do not wire it. Use `dd_failure_basis_and_live_arrears_provision_rates.md`.

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

---

## 8. 2026-10-11 pass — what is lawful per customer, for a risk-based personal payment plan

*Knowledge pass for the director's design: a personal payment plan merged with debt management,
where credit risk sets DRIFT TOLERANCE (how far a balance may wander from zero) rather than the
annual amount paid. Filed HERE rather than `debt_and_collections.md` because that file already
carries the detailed, heavily-cited treatment of SLC 27.8 (ability-to-pay), SLC 28B (involuntary
PPM) and vulnerability (its §10, V1/V2 split) — this section cites that work rather than duplicating
it, and adds the three things neither that file nor this one yet covers: security deposits,
risk-based DD lawfulness, and payment-method cost-reflective pricing. Where this section leans on
`debt_and_collections.md`, it says so and does not re-derive the figures.*

### Rules (ESTABLISHED, cited — new this pass)

1. **Ofgem's own evidence that risk-based segmentation of customers is normal, published practice.**
   *"Most suppliers conduct credit checks of new customers to assess their risk, or if existing
   customers are looking to move from prepayment to direct debit."* — Ofgem, *Affordability and debt
   in the domestic retail market: call for input*, March 2024, §3.8. [H] This is direct evidence that
   a supplier segmenting customers by credit risk, before any payment-method decision, is itself
   unremarkable and not something the regulator treats as suspect.
2. **The ability-to-pay duty's own description, restated in the same 2024 document** (§1.20): *"Our
   rules include offering an affordable repayment plan at the earliest opportunity, requiring
   additional support credit and emergency credit for PPM customers, strong rules around supplier
   conduct for customers struggling to pay, and customer service."* This restates SLC 27.8 (already
   the primary citation in `debt_and_collections.md` §3) rather than adding a new numeric rule — no
   affordability formula is given here either.
3. **A named, separate instrument exists: Ofgem's "Consumer standards decision".** The March 2024
   call for input cites it (footnote 23, §3.6): *"In our recent consumer standards decision we
   emphasised the need for suppliers to proactively engage with consumers at the earliest opportunity
   if there are signs they are in payment difficulty."* [M — the citing document is primary, but this
   pass did not reach the Consumer Standards decision itself, so its exact date, SLC reference and
   full scope are not independently confirmed; see GAP 3.] This is the probable home of any 2023-24
   "ability-to-pay" strengthening beyond SLC 27.8 itself, and is worth a dedicated follow-up pass.
4. **Vulnerability and risk are already distinguished in this repo's knowledge, and that distinction
   binds the PPP design.** `debt_and_collections.md` §10.1 establishes two non-identical
   vulnerabilities: V1 (PSR needs-code, SLC 0/26, a weak arrears predictor, RR~1.2-1.5) and V2
   (financial vulnerability, which no register records, a strong predictor, RR~3.6-4.6). A
   credit-risk score is closer to a V2 proxy than a V1 one, but is not the same thing as either —
   nothing read this pass or previously establishes that a credit bureau score and Ofgem's
   financial-vulnerability segmentation are the same measurement.
5. **Involuntary PPM and remote-switch rules are a hard gate, already fully cited.**
   `debt_and_collections.md` §2.1's table (row P4) and its SLC 28B citation set out the Debt Trigger
   (3 months, £200/fuel, not on a plan), 10 contact attempts, SLC 27 duties met, a Site Welfare
   Visit, and the age/vulnerability bans (75+ alone, under-2s in the house). A PPP that routes a
   high-risk customer toward prepayment cannot do so as an internal risk decision alone; it must
   clear this statutory gate regardless of what the risk model says.

### GAPs (new this pass)

1. **Security deposits for domestic customers (SLC 27.2-27.3, by the task's own numbering) were not
   reached.** The consolidated licence conditions PDF previously cited in `what_a_supplier_holds...`
   has moved (404) and a working replacement URL was not found within this pass's search budget.
   Nothing in this file or elsewhere in the knowledge base states when a domestic security deposit
   may lawfully be required, what "reasonable" means, or the refund rule. **Do not build a deposit
   feature on an assumption; this is an open clause reference, not a confirmed absence of one.**
2. **Payment-method cost-reflective pricing (SLC 27.2A, by the task's numbering) was not reached**
   at the clause-text level. What IS established, in `debt_and_collections.md` §2.2 (cited there,
   not re-derived here): the price cap's debt-related cost ALLOWANCE is split by payment method —
   from 1 July 2025, **DD £57, SC £160, PPM £19** per dual-fuel customer per year (Decision overview,
   May 2025, §2.9/§2.55). That is the cap's own allowance for the cost DIFFERENCE between methods,
   which is evidence the regulator treats payment-method pricing as cost-based, but it is not the
   same thing as confirming a specific licence clause mandates cost-reflectiveness at the
   individual-supplier level. Flagged as a gap between adjacent evidence, not resolved.
3. **The Consumer Standards decision itself (see Rule 3 above) was not retrieved.** Its date, SLC
   numbering, and whether it created any NEW numeric or procedural ability-to-pay obligation beyond
   SLC 27.8's existing wording are all open.
4. **No published rule on whether a risk-based personal payment plan, as a named product, is
   itself something Ofgem has considered.** Everything here is assembled from adjacent, separately
   published rules (DD reassessment, ability-to-pay, vulnerability, PPM gates, capital/ringfencing);
   no source read across any pass addresses a "personalised plan merged with debt management" as a
   single regulatory object. That composite is this project's own design, not a published category.

### What this means for a risk-based personal payment plan

- **ALLOWED, on stronger evidence than before this pass:** segmenting customers by credit risk at
  onboarding or at a payment-method change is explicitly normal, Ofgem-acknowledged practice — the
  PPP's basic premise (tier customers by risk, manage drift tolerance per tier) is not itself in
  tension with anything read.
- **ALLOWED, already established in this file's companion:** offering a repayment plan "at the
  earliest opportunity" and tailoring it to ability to pay (SLC 27.8) — a PPP that front-loads a
  conversation about affordability for a drifting high-risk account is doing what the rule already
  asks for, not something novel.
- **FORBIDDEN or gated, already established in this file's companion:** moving a high-risk customer
  to prepayment as a unilateral consequence of a risk score, without clearing the SLC 28B Debt
  Trigger, contact-attempt and welfare-visit gates. "Kept near zero without winter bill shock" must
  not, by itself, become a route to an involuntary PPM switch that skips those steps.
- **UNCLEAR, and now the two biggest open clauses for this design specifically:** (a) whether a
  deposit-like mechanism — asking a higher-risk customer to hold a larger pre-funded balance rather
  than running near zero — would be read as a security deposit (SLC 27.2-27.3, unretrieved) with its
  own separate "reasonable" test, rather than as a direct-debit sizing choice under SLC 27.15; and
  (b) whether the payment-method cost differential rule (SLC 27.2A, unretrieved) constrains how far
  a *risk-tier* differential (as opposed to a *payment-method* differential) may go. Both should be
  closed before a feature that visibly varies what a customer is asked to hold by risk tier is built,
  not after.
- **Vulnerability is an override, not a tier.** Per `debt_and_collections.md` §10, a PSR-registered
  (V1) or financially vulnerable (V2) customer's protections apply regardless of their credit-risk
  tier. A high-risk, financially vulnerable customer must get the SLC 27.8/0/26 protections in full;
  "kept near zero" cannot become a substitute for the ability-to-pay and vulnerability duties that
  already bind that customer independent of any risk score.

## Licence text follow-up (2026-10-11)

*Source: Electricity Supply Standard Licence Conditions, "Consolidated to 1 August 2025", 611 pp.,
read in full text. The Ofgem URL
`https://www.ofgem.gov.uk/sites/default/files/2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf`
now 301-redirects to `/energy-regulation/how-we-regulate/energy-licences-and-guidance`. The copy read
is the Wayback capture of 30 Jul 2026 of that same URL:
http://web.archive.org/web/20260730084410/https://www.ofgem.gov.uk/sites/default/files/2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf .
The consolidation carries Ofgem's own caveat: "Consolidated conditions are not formal Public Register
documents and should not be relied on". The formal text is on the EPR (epr.ofgem.gov.uk), which was
bot-blocked this pass. Gas SLC 27 mirrors it; the gas text was not read this pass.*

### Payment-method cost differences — SLC 27.2A / 27.2B (ESTABLISHED, verbatim)
- **27.2A**: *"Any difference in terms and conditions as between payment methods for paying Charges
  for the Supply of Electricity shall reflect the costs to the supplier of the different payment
  methods."*
- **27.2B**: *"In this condition, 'terms' means all terms on which a supply of electricity is offered
  or provided, including terms as to price, which significantly affect the evaluation of that
  supply."*
- Context, 27.1-27.2: the licensee must offer "a wide choice of payment methods", including cash at
  least fortnightly and prepayment. That duty does not apply (27.2(b)) to a supplier with fewer than
  50,000 Domestic Customers. **27.2A has no such size exemption.**
- **Reading:** this is a cost-reflectivity rule over payment METHODS. It covers price and any other
  term that significantly affects the offer. A risk-tiered plan that varies terms by method needs each
  difference to trace to a method cost. The text says nothing about differences WITHIN one method by
  customer risk. Whether 27.2A reaches those is NOT ESTABLISHED and needs SLC 0 (fair treatment)
  read alongside. [DERIVED]

### Security deposits — SLC 27.3 / 27.4 (ESTABLISHED, verbatim)
- **27.3**: *"A licensee must not require a Domestic Customer to pay a Security Deposit in relation to
  the supply of electricity to his premises ...: (a) if that customer agrees that the premises may be
  supplied through a Prepayment Meter and it is safe and reasonably practicable in all the
  circumstances of the case for the premises to be so supplied; or (b) if it is unreasonable in all
  the circumstances of the case to require that customer to pay a Security Deposit."*
- **27.4**: *"A Security Deposit must not exceed a reasonable amount."*
- Definition (SLC 1): "Security Deposit means a deposit of money as security for the payment of
  Charges".
- SLC 22.7(c): the duty to supply (22.2/22.3) does not apply where "the licensee requires the
  Domestic Customer to pay a Security Deposit and he does not do so", unless the deposit breaches
  27.3 or 27.4.
- **So the licence states WHEN a deposit is barred (prepayment accepted and safe, or unreasonable in
  all the circumstances) and caps its SIZE ("reasonable amount"). It sets no number and no test of
  reasonableness beyond those words.**
- **Refund: the current consolidated SLC 27 has NO deposit-refund clause.** "Security Deposit" appears
  only at SLC 1, 22.7(c), 27.3, 27.4 and the 27 heading. A refund rule, if one exists, sits elsewhere
  (contract terms, guidance, or a deleted older paragraph). NOT ESTABLISHED; a candidate for a gas-SLC
  and Ofgem-guidance check.

### Payment difficulty after the Consumer Standards decision (ESTABLISHED)
- **The decision.** Ofgem, *Modification of the standard conditions of all electricity supply
  licences* (s.11A notice), dated **18 October 2023**, **effective 14 December 2023**:
  https://www.ofgem.gov.uk/sites/default/files/2023-10/Decision%20Notice%20-%20Electricity%20Supply%20Licence%20modification_0.pdf
  - Statutory consultation notice: 26 Jul 2023. 53 responses.
  - It added **27.5B**, modified **27.8A**, and added **31G.3A-3E** (enquiry service / debt advice).
  - Stated purpose: "to introduce additional requirements for suppliers to assist customers
    struggling with their bills". This is the Consumer Standards package.
- **27.5B (new, Dec 2023) — the first-contact trigger.** The licensee must make proactive contact "at
  the earliest opportunity to identify whether a customer is in payment difficulty, by contacting the
  Domestic Customer no later than after: (a) two consecutively missed monthly scheduled payments; or
  (b) one missed quarterly scheduled payment; or (c) a customer has informed the licensee that they
  are unable to make the next scheduled payment."
- **27.8**: take "all reasonable steps to ascertain the Domestic Customer's ability to pay and must
  take this into account when calculating instalments".
- **27.8A** lists what "due consideration" means for repayment plans (current text):
  - (a) credit management policies that allow case-by-case handling and link staff incentives to
    "successful customer outcomes not the value of repayment rates";
  - (b) proactive contact, including the 27.5B trigger and signposting debt advice under 31G;
  - (c) understanding ability to pay, including "proactively exploring payment amounts and payment
    methods which are appropriate to the individual circumstances of each customer";
  - (d) setting repayment rates on ability to pay:
    - (i) use all available information, including warrant and site-visit findings;
    - (ii) "Only setting default amounts when there is insufficient information ... the levels of
      any default repayment rate should be reasonable";
    - (iii) "Not insisting on substantial upfront payments before reconnection";
    - (iv) "Pausing scheduled repayments for an appropriate period of time as part of the customer's
      repayment plan and reviewing the customer's repayment plan in accordance with their ability to
      pay at regular intervals before re-instating scheduled repayments";
  - (e) making sure the customer understands the arrangement: how much, how deducted, when the debt
    will be repaid, what to do if difficulties arise; for prepayment, that weekly debt recovery runs
    regardless of usage;
  - (f) monitoring arrangements: failed arrangements for credit customers, meter use for prepayment,
    staff approach (call listening), failed arrangements "to understand whether inappropriate rates
    are being set", and overall repayment rates and recovery periods;
  - (g) re-engaging "after an initial occurrence of a failed repayment arrangement", including
    whether a different plan or method "would be more suitable".
- **27.5A**: no charge for the 27.6 services (benefit deduction, instalments, prepayment, efficiency
  advice). **27.8C**: contract terms must reflect 27.5-27.8.
- **Which 27.8A limbs were new in Dec 2023 is NOT ESTABLISHED.** The notice marks its changes in
  yellow highlight and double underline, which text extraction loses. 27.8A existed before 2023 (the
  notice "modifies" it). The pre-2023 decision that introduced it was not located this pass.

### What this means for a risk-based personal payment plan
- A risk-tiered pre-funded buffer for high-risk customers looks like a **Security Deposit** in
  substance: money held "as security for the payment of Charges". If so, 27.3(a) bars it outright for
  a customer who accepts a safe prepayment meter, and 27.3(b)/27.4 make it subject to a
  reasonableness test. [DERIVED; the line between a DD sized above expected consumption and a deposit
  is not drawn in the licence text]
- 27.8A(f)(iii) already obliges the company to monitor failed arrangements "to understand whether
  inappropriate rates are being set". A plan-failure metric is a licence duty, not an optional KPI.
