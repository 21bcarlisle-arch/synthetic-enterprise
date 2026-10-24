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

## Ability to pay and repayment plans: the full rule set, its history, and what Ofgem has said since (2026-10-11)

*Goes deeper than the "Licence text follow-up" section above, which already quotes 27.5B, 27.8 and
27.8A(a)-(g). Not repeated here. Licence text: the same consolidation (Electricity SLCs, consolidated
to 1 Aug 2025, Wayback 30 Jul 2026 capture of
`ofgem.gov.uk/sites/default/files/2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf`),
pp. 239-246. Gas text not read.*

### The parts of SLC 27 the earlier passes did not quote (ESTABLISHED, verbatim or close paraphrase)
- **27.5**: the duty is triggered when the supplier "becomes aware or has reason to believe" the customer
  "is having or will have difficulty paying". So it is a forecast trigger ("will have"), not only an
  arrears trigger. 27.5B (two missed monthly payments) is the latest point for contact, not the first.
- **27.6, the menu that must be offered**: (a)(i) payment deducted at source from a social security
  benefit "where available" (Fuel Direct / Third Party Deductions); (a)(ii) regular instalments
  "calculated in accordance with 27.8" paid other than by PPM; (a)(iii) a PPM where safe and reasonably
  practicable, instalments again per 27.8; (b) energy-efficiency information. **27.5A**: none of it may
  be charged for.
- **27.8** has two limbs the earlier pass left out. The supplier must give due consideration to (a)
  "relevant information provided by third parties, where it is available", and (b) for PPM recovery,
  "the value of all of the charges that are to be recovered through that meter". That means debt plus
  ongoing use plus standing charge: affordability is judged on the total weekly outgoing, not the debt
  rate alone.
- **27.8C**: contract terms must say that charges "may not be demanded or recovered unless and until"
  27.5-27.8 (and 28.15-28.16) have been complied with. **A plan set in breach of 27.8 makes the debt
  contractually unrecoverable until it is cured.**
- **27.9**: no disconnection for unpaid charges unless "all reasonable steps" to recover through a PPM
  were taken first. **27.9A**: disconnection *includes* credit-limiting that stops supply and
  load-limiting that "significantly" constrains it (non-PPM). So a smart-meter throttle is a
  disconnection in law.
- **27.10-27.11A**: the Winter bar (pensioners alone or only with pensioners or under-18s); "all
  reasonable steps to avoid" Winter disconnection where there is a pensioner, a disabled or a chronically
  sick person; a duty to check which applies first. **27.11C**: none of 27.5-27.11B applies to the
  statutory (safety/theft) disconnection power.
- **28.15**: any recovery action, and the costs sought, must be "proportionate in the context of the
  amount of the charges". This is not limited to warrants.

### History: when 27.8A came in (closes GAP 3 of the "2026-10-11 pass" section and the "which limbs were new" gap)
- **27.8A was introduced by Ofgem's *Self-disconnection and self-rationing: decision*, Oct 2020, in force
  15 Dec 2020** (decision PDF §1.5, ch. 4,
  https://www.ofgem.gov.uk/sites/default/files/docs/2020/10/self-disconnection_and_self-rationing_decision.pdf).
  Ofgem called these the "updated Ability to Pay principles", moved from guidance into the licence. The
  2020 text of (d) ends at (iii) "not insisting on substantial upfront payments before reconnection".
  **ESTABLISHED.**
- **(d)(iv), "pausing scheduled repayments for an appropriate period ... reviewing ... at regular
  intervals before re-instating", is NOT in the 2020 text but IS in the Aug 2025 consolidation.** The
  only modification between the two found in any pass is the 18 Oct 2023 Consumer Standards notice.
  **DERIVED: the pause limb is a Consumer Standards (Dec 2023) addition.** (b)(i) (27.5B contact) and
  (b)(iv) (31G debt advice) are the same: they cite provisions created by that notice.
- **"Failed repayment arrangement" has a published definition:** "full payment has not been received by
  the supplier within 10 working days after the agreed payment date" (Social Obligations Reporting, cited
  at decision §4.25). Re-engagement under (g) is expected "as soon as" a failure on that definition is
  identified, and on every failure, not only the first (§4.26). **ESTABLISHED.**
- **Default rates** (§4.22): only where the customer has not engaged; "guidelines only"; must change
  when information arrives; "should be reasonable". **ESTABLISHED.**

### Minimum and maximum repayment rates: there are none (ESTABLISHED as an absence)
- No SLC, guidance or decision read sets a floor, a ceiling, a maximum term or a percentage-of-income
  cap for supplier repayment plans. The only numeric repayment rates in the system are the **DWP Fuel
  Direct / Third Party Deduction** rates (UC: a flat 5% of the standard allowance; see
  `debt_and_collections.md` §3). Those are DWP's, not Ofgem's.
- The 2020 decision says Ofgem is "engaging with DWP" on misalignment between the licence and DWP's rules
  on when Third Party Deductions can be used (§1.26). **Note: §2 of this file gives "£3.70/week" as a
  Fuel Direct floor with no date or source. It predates the UC 5% rule and should be read as stale.**
  [DERIVED; legacy-benefit rate not re-read this pass]
- **Observed, not regulated**: 2025 electricity PPM-for-debt rates ran £2.69-£17.17/wk and 137-737
  weeks by supplier (https://www.ofgem.gov.uk/data/debt-and-arrears-indicators, 24 Sep 2026). That spread
  is consistent with there being no rate rule.

### What Ofgem has said about ability to pay since (ESTABLISHED unless marked)
- **PPM guidance §6 (13 Sep 2023)**, binding before any involuntary PPM. 6.1: offer "the cheapest
  payment option" and "an affordable, sustainable repayment plan". 6.2: a customer who "agrees, and
  adheres to" a plan must be accepted, and the supplier "should not threaten Involuntary PPM to try and
  secure higher payment than is affordable". 6.3: if the customer can afford ongoing use but not the
  debt, consider "delaying repayment start (seasonality or change in financial circumstances)".
- **Ofgem, *Guide for energy suppliers and debt advice providers*** (PDF dated "28 January 2025", in the
  2026-01 folder,
  https://www.ofgem.gov.uk/sites/default/files/2026-01/Guide_for_energy_suppliers_and_debt_advice_providers.pdf,
  pp. 9-11). It is good-practice guidance, not a rule.
  - A Standard Financial Statement (SFS; CFS in Scotland) from an FCA-authorised or local-authority debt
    adviser "should be duly considered and, in many cases, removes the need to ask for further financial
    information". It "may form the foundation" of the instalment.
  - Poor practice: rejecting an offer without saying why; asking for a second income-and-expenditure
    check; "expect[ing] that a large debt can be repaid over a short (three to six month) period" from a
    low-income or deficit-budget household.
- **Compliance findings.** The autumn-2022 payment-difficulty review found "severe weaknesses" at Tru,
  Utilita and ScottishPower and issued provisional orders
  (https://www.ofgem.gov.uk/decision/ofgem-completes-review-how-suppliers-support-customers-payment-difficulty,
  page re-stamped Aug 2025). The Jun 2026 PPM review found "unaffordable default debt repayment rates
  when customers were not present", and refusals of part-payment or a DD plan on the day of a warrant.
- **Debt strategy update, 6 Nov 2025**
  (https://www.ofgem.gov.uk/policy/debt-strategy-update-supporting-reduction-energy-debt):
  - Standardised ability-to-pay assessment is a priority, to come "through phase 2 of the DRS". The Dec
    2024 *Improving debt standards* proposals have **no decision** (none in Ofgem's sitemap, 10 Oct 2026).
  - The "Debt Guarantee" became a consumer "Know your rights" guide ("the right to an affordable
    repayment plan").
  - The 2023 involuntary-PPM rules are under evaluation, "to conclude ... in the first half of 2026".
    **No outcome found.**
- **Write-off.** No licence condition obliges domestic write-off. The only proposed obligation is DRS
  phase 1 (statutory consultation 6 Nov 2025, decision "expected ... January 2026"; **none found**).
  Its terms are in `debt_and_collections.md` §3. Otherwise write-off is supplier discretion.

### GAPs
- E1: gas SLC 27 text (assumed to mirror electricity; not read). E2: DRS phase 1 decision (expected Jan
  2026; not found). E3: involuntary-PPM evaluation outcome (due H1 2026; not found). E4: the Aug 2025 ASC
  letter (not reached). E5: no standard ability-to-pay method yet; SFS acceptance is good practice only.

### What this means for an automated self-serve response
- **May be automated (the rules allow and partly require it):** contact at the 27.5B trigger or on a
  *forecast* of difficulty (27.5 "will have"); the full 27.6 menu (plan, PPM, Fuel Direct signposting);
  a provisional, "reasonable" default plan for a non-engaging customer; a pause, review and re-instate
  cycle (27.8A(d)(iv)); a delayed start for seasonality (PPM guidance 6.3); re-engagement on every
  failure (10-working-day definition); accepting an SFS-based adviser offer; monitoring whether failing
  plans mean rates are set too high (27.8A(f)(iii)).
- **"Some money steadily beats none" fits the rules.** 27.8 makes affordability binding with no floor,
  so a low rate that holds is lawful, and a high rate that fails is what 27.8A(f)(iii) asks the
  supplier to detect. [DERIVED]
- **Must stay human, or at least human-reviewable:** "case-by-case" handling (27.8A(a)(i)) means the
  engine cannot be the only route, so a person must be reachable (31G.3A, with 31G.3B priority for
  vulnerable situations). Also anything resting on third-party information (27.8(a)), and any rejection
  of a debt adviser's offer, which must give its reason.
- **Forbidden:** charging for any 27.6 service; insisting on substantial upfront payment before
  reconnection; incentives linked to repayment value (27.8A(a)(ii)), which applies equally to an
  optimiser's objective [DERIVED]; recovering while 27.5-27.8 is unmet (27.8C); treating a smart
  load-limit as anything but a disconnection (27.9A).

## Self-disconnection and self-rationing: the duties, and what a supplier must do on detection (2026-10-11)

*Correction to the brief that started this pass: the self-disconnection duties are **SLC 27A**, not
"SLC 28.1A". 27A was created by the Oct 2020 decision cited in the section above, in force 15 Dec 2020.
Text: the same Aug 2025 electricity consolidation, pp. 247-249.*

### The rules (ESTABLISHED, verbatim or close paraphrase)
- **27A.1 Identify.** For every PPM customer, "take all reasonable steps to identify on an ongoing and
  continuous basis, whether that Domestic Customer is Self-Disconnecting". If they are, offer
  "appropriate support" under 27A, 27.8 and the other PPM duties, taking vulnerability into account.
- **Definitions (27A.9).**
  - *Self-disconnection*: a PPM customer "experiences an interruption to their electricity supply because
    the credit on the meter has been exhausted".
  - *Self-rationing*: a customer "deliberately limits its electricity use to save money for other goods or
    services". This is defined without reference to a PPM.
- **27A.2 Emergency and friendly-hours credit must be offered to every PPM customer**, unless technically
  unfeasible or outside the supplier's control. In that case there must be "alternative short-term
  support in a timely manner" (27A.3).
  - Friendly-hours credit is credit "overnight, at weekends and public holidays".
  - **Ofgem refused to set amounts or hours** (decision §3.11): it did not want "a potential race to the
    bottom".
- **27A.4**: if the customer is or will be in difficulty, repayment of emergency or friendly credit must
  be calculated under 27.8 (ability to pay).
- **27A.5 Additional Support Credit (ASC).** "On each and every occasion" the supplier identifies that a
  PPM customer **in a Vulnerable Situation** has self-disconnected or is self-disconnecting, or has
  reason to believe they are self-rationing, it must offer ASC "in a timely manner". This is on top of
  emergency credit.
  - 27A.6: the amount and the repayment instalments must be assessed under SLC 27.
  - 27A.7: the supplier may decline ASC only if, "acting reasonably", it is not in the customer's best
    interest. It must then give "alternative appropriate support" under SLC 0 and 31G.2. The decision
    (§3.31) names non-repayable financial support and debt-advice signposting.
  - ASC is a "fixed amount of credit". **No amount is prescribed.**
- **27A.7A-C Involuntary PPM credit.** It is automatic on every involuntary installation and repaid under
  27.8. PPM guidance §10.1 sets it at **£30 per meter** (or an equivalent non-disconnection period that
  must not leave a negative balance).
- **27A.8**: every PPM customer must be told, in a usable form and frequency, what each credit facility is,
  when it can be used and how it is repaid. 28.1(bb) repeats this at installation.
- **There is NO licence duty to identify self-rationing.** Ofgem decided against one (decision §2.28) and
  chose to monitor instead. The ASC duty bites only when the supplier "becomes aware or has reason to
  believe" it is happening.
- **What on detection.** PPM guidance §9.1 (applies to all PPMs, 13 Sep 2023):
  - monitor top-up and disconnection patterns;
  - on self-disconnection, "make multiple attempts to contact the customer using various contact
    channels" to understand why;
  - offer "sufficient" ASC "amounts and frequencies".
  - §9.1(b): if self-disconnection is "frequent or prolonged" and the customer relies on ASC beyond the
    supplier's own ASC policy, the supplier **must re-assess whether a PPM is still safe and reasonably
    practicable**. That can end in moving the customer off PPM (28.2(c)).
- **Annual re-check (28.3)**: contact every PPM customer at least yearly to assess whether a PPM remains
  safe and reasonably practicable.
- **Meter-fault interruptions (31G.3A(c))**: a 24-hour enquiry service for customers off supply because of
  a meter fault.

### Reporting and scale (ESTABLISHED)
- **Reporting.** The 2020 decision imposed no new reporting condition. Ofgem monitors self-disconnection
  through its RFIs (§2.22). It now publishes smart-PPM counts in the debt and arrears indicators, from
  all suppliers since Q3 2023 (before that, the largest 8, about 98% of the market).
- **Latest (Q2 2026, indicators page dated 24 Sep 2026).**
  - Electricity: 564,191 smart-PPM customers self-disconnected at least once; 368,659 for over 3 hours;
    2,038,289 events.
  - Gas: 304,428 customers; 245,056 for over 3 hours; 958,551 events.
  - Ofgem warns the counts rise as more meters gain the connectivity to report.
- **So the same identification duty observes different things by meter type.** A smart PPM reports
  each event. For a traditional PPM the supplier can see only top-up gaps. [DERIVED]

### GAPs
- E6: ASC amounts and frequencies actually offered (supplier policy; not published), and the Aug 2025
  letter that "clarif[ied] expectations" on ASC targeting (not reached).
- E7: the self-rationing proxy a supplier uses. No rule, and no published method.
- E8: the share of self-disconnections ended by emergency or friendly credit versus top-up. Not
  published.

### What this means for an automated self-serve response
- **May be automated, and largely must be:**
  - continuous identification of self-disconnection from smart data (27A.1 says "ongoing and
    continuous");
  - automatic emergency and friendly-hours credit;
  - the £30 involuntary-PPM credit;
  - a first offer of ASC with 27.8-sized repayment;
  - multi-channel contact after an event;
  - a trigger that escalates "frequent or prolonged" self-disconnection to a suitability review.
- **Must stay human:**
  - the 27A.7 judgement that ASC is *not* in a vulnerable customer's best interest, and the alternative
    support offered instead;
  - the safe-and-reasonably-practicable re-assessment after repeated self-disconnection;
  - anything that rests on suspected self-rationing, which is a judgement about intent the data cannot
    settle.
- **Forbidden:**
  - an ASC policy that caps support below need for a vulnerable customer and leaves no alternative
    (27A.7);
  - repaying emergency credit or ASC at a rate not set under 27.8;
  - leaving a PPM customer without the information in 27A.8.
- **Modelling note.** Self-disconnection is the PPM population's form of default
  (`debt_and_collections.md` §2.1). An engine that sizes a PPM debt rate must count the
  self-disconnection it causes as a cost, not a saving. [DERIVED]

## Involuntary prepayment since 2023: the complete gate, the do-not-install list, and what happened to installations (2026-10-11)

*`debt_and_collections.md` §3 already gives the headline gate (Debt Trigger £200 per fuel and 3 months,
10 attempts, a Site Welfare Visit, the 75+/under-2 bans, the £150 warrant cap). This section adds the
rest of SLC 28.7-28.22 and the guidance. Sources:
- the same Aug 2025 electricity consolidation, pp. 250-257;
- Ofgem, *PPM Guidance (Safe and Reasonably Practicable)*, 13 Sep 2023, OFG1163,
  https://www.ofgem.gov.uk/sites/default/files/2023-09/PPM%20Guidance_Safe%20and%20Reasonably%20Practicable.pdf
  (binding through 28.4).*

### Timeline (ESTABLISHED)
- Late 2022: media allegations. Jan 2023: market compliance review (MCR) opened. All suppliers stopped
  involuntary installs and remote switches.
- 18 Apr 2023: voluntary Code of Practice.
- Licence and guidance decision Sep 2023, in force **8 Nov 2023**.
- Restart required a second independent audit. EDF, Octopus and ScottishPower restarted first, in
  **Jan 2024**.
- MCR final report, **3 Jun 2026**
  (https://www.ofgem.gov.uk/sites/default/files/2026-06/Market-Compliance-Review-prepayment-meter-installations.pdf):
  - "All [suppliers] can now carry out involuntary PPM activity, although not all have chosen to do so";
  - British Gas "does not currently carry out involuntary PPM activity";
  - Utilita and OVO were moved to enforcement.
- The warrant-trauma, warrant-charge and £150-cap limbs (28.10-28.13) had a 30 Jun 2025 sunset in the
  licence text (28.19). They were extended to 2027 (Ofgem decision, May 2025; see
  `gb_payment_method_migration_rates.md`).

### The licence gate beyond the headline (ESTABLISHED)
- **28.21: "involuntary" covers two routes.** One is a warrant install. The other is a remote smart
  switch to prepay mode when there are outstanding charges, alternatives have been offered under
  SLC 27, SLC 23 notice has been given, and there is no explicit Consent.
  - **Consent (28.22)** must be "unmistakably given ... rather than implied or retained in terms and
    conditions", recorded, and "not given under pressure". A consent clause in T&Cs is not consent.
- **28.7 order of conditions:** Debt Trigger; multiple engagement attempts; SLC 27/27A/28 compliance;
  Site Welfare Visit(s); a positive safe-and-reasonably-practicable finding, including the Precautionary
  Principle and a PSR check. 28.8: 28.7 prevails over any other SLC.
  - **Precautionary Principle**: assume anyone facing involuntary PPM "is likely to be in financial
    difficulty and therefore more likely to self-disconnect".
- **28.9:** accept any relevant financial information and authorised representatives; **no staff
  incentives tied to the number of installations**; body-cam or audio on welfare visits; aftercare; keep
  the records (guidance 11.1: **at least five years**).
- **28.10**: no warrant where it "would be severely traumatic" because of an existing mental-capacity or
  psychological vulnerability.
- **28.11**: no warrant costs charged to a customer whose vulnerability impaired engagement, or whose
  severe financial vulnerability would be worsened.
- **28.14/28.15**: warrant use and recovery costs must be proportionate to the debt.
- **28.17/28.18 Debt completion.** Once an involuntary-PPM customer has repaid all debt, the supplier
  must offer a suitability re-assessment, information on other methods and tariffs, and the option to
  move. It must implement a move "as soon as reasonably practicable" (credit checks allowed, any deposit
  "reasonable").

### Do not install (guidance 3.7) and further assessment needed (3.8) (ESTABLISHED, verbatim list)
- **Do not install.** Applies where no one in the household can access, operate or top up the meter
  (physical or mental incapacity, or technical reasons), or the household has any of:
  - **a continuous-supply health need**: powered medical equipment ("heart/lung ventilators, dialysis
    equipment, stair lift, hoist or refrigerated medication"), carelines or health alarms, or "a medical
    dependency on a warm home" (for example circulatory disease or sickle cell);
  - **an occupant aged 75+ "without support in the house"**;
  - **children under 2**;
  - **"chronic/severe or terminal health conditions"** (cancer, cardiovascular or respiratory disease
    including COPD, organ failure).
- **Further assessment needed**, assessed with the Precautionary Principle:
  - children 5 and under;
  - other serious medical conditions (neurological, respiratory, nutritional, mobility-limiting);
  - serious mental or developmental conditions (depression, dementia, learning disabilities,
    schizophrenia);
  - **temporary situations (pregnancy, bereavement)**.
  - 3.9: suppliers are "encouraged" to check suitability for any household with an adult over 65 or a
    child under 16.
  - 3.12: if a further-assessment household's ability-to-pay check shows it "will, frequently or for
    prolonged periods self-disconnect", the PPM **must** be treated as not safe and reasonably
    practicable.
- **Discrepancy, flagged:** Ofgem's consumer page "Installing a prepayment meter without your
  permission" (updated 16 Sep 2026) says a supplier "must not" install where "anyone's temporary
  circumstances make a prepayment meter unsafe or unsuitable, for example pregnancy or bereavement".
  The guidance puts those in further-assessment-needed, not do-not-install. **The binding text is the
  guidance. The consumer page is the public promise.** A company that treats them as do-not-install
  satisfies both. [DERIVED]

### Required steps (guidance §§4-6, 10-11) (ESTABLISHED)
- In the 3 months before execution: **at least 10 engagement attempts**, multi-channel and at various
  times. Translation and accessible formats. **At least one Site Welfare Visit in every case** (5.3).
  - Postal-only accounts may do fewer than 10, but must evidence their attempts to find other contact
    details (5.10).
  - If there is no contact at the visit, the supplier may proceed (warrant or remote switch), but must
    try to assess vulnerability without the customer, with a Welfare Officer in Edge Cases, and write to
    say what happens next (5.7-5.8).
- **An assessment team independent of debt-recovery and installation** must review every case (5.13).
  A **Welfare Officer** or senior decision-maker must be present or contactable at visits (5.14). Senior
  authorisation is needed before the move (§4 table).
- Smart by default under warrant, and the reason for any non-smart install recorded (7.1-7.3).
- **Aftercare** (10.1-10.4): £30 credit per meter; at least 3 contact attempts in the first fortnight,
  the first within 3 days; checks that the customer can top up; a fix for a faulty in-home display.
  Non-compliant installs must be offered reversal and compensation.
- Monthly QA of a sample of cases (11.4).

### Effect (ESTABLISHED / NOT ESTABLISHED)
- **Pre-rules window, from the MCR.** Over 150,000 involuntary installs or switches were reviewed (Jan
  2022 to Jan 2023, excluding British Gas). **1,925 (under 2%) should not have happened**, mostly "poor
  quality assurance or human error". Remediation: £7m compensation, £13m written off, £55m hardship and
  relief. Tiers: £40-60 for process issues; £250 for insufficient support or unfair treatment; £500 for
  vulnerability not considered; **£1,000 for an inappropriate install, switch or use**.
- **Post-restart volumes (2024-2026): NOT ESTABLISHED.** Ofgem collects weekly reports from each
  restarted supplier (MCR §1) but publishes no count, and the debt and arrears indicators have no
  involuntary-install series. Also flagged in `gb_payment_method_migration_rates.md`.

### What this means for an automated self-serve response
- **May be automated:** the Debt Trigger test; scheduling the 10 multi-channel attempts; PSR and
  do-not-install screening as a hard exclusion; flagging further-assessment households for review; the
  £30 credit and aftercare schedule; the 28.17 debt-completion offer and the move back on request;
  record retention.
- **Must stay human:** the Site Welfare Visit; the independent case assessment; Welfare Officer Edge
  Case decisions; the safe-and-reasonably-practicable judgement for further-assessment households; any
  decision to proceed without contact.
- **Forbidden:** an engine that *decides* an involuntary PPM (warrant or remote switch) on a score; any
  install for a do-not-install household; a T&Cs clause treated as Consent; incentives or an optimiser
  objective on install counts; threatening involuntary PPM to win a higher-than-affordable rate from a
  customer keeping to a plan (guidance 6.2).
- **Involuntary PPM is the end of a human-gated process, never a self-serve response.** [DERIVED from
  the above]

## The world's side of the route from debt to prepayment (2026-10-16, atom W2_42)

*K8 page for `simulation/payment_method_dynamics.py::move_to_prepayment_for_debt`. The rules are the
section above and `debt_and_collections.md` §3. This section says what the world does with them.*

### What the world does (DESIGN CHOICES, each named)
- **The world executes a meter change for debt only by a lawful route, and refuses any other with a
  named reason.** Two routes: by the household's recorded explicit Consent (28.22), when the household
  answers yes (`answer_prepayment_offer`); or involuntarily (warrant or remote switch, 28.21) when the
  28.7 gate holds. The refusal reason is the first unmet condition, in 28.7's order.
- **The involuntary gate the world checks, from 8 Nov 2023:** the Debt Trigger (£200 or more per fuel,
  3 months or more outstanding, not on or moving to a plan); at least 10 engagement attempts; at least
  one Site Welfare Visit; and that no one in the household is on the do-not-install list.
- **Feb 2023 to the end of Dec 2023 is refused as paused.** Every supplier stopped in Feb 2023, the
  rules came into force 8 Nov 2023, and the first restarts (after a second independent audit) were in
  Jan 2024. The world does not model the audit, so it treats 1 Jan 2024 as the restart for any supplier.
- **Do-not-install is drawn from the hidden PSR-type state (V1).** `vulnerability_state` draws V1 but no
  needs code (no distribution of registrations by code is published). The world cannot say which V1
  households are on the do-not-install list, so it treats every V1 household as do-not-install. That
  is the Precautionary Principle, and it errs against the thesis (F11): it can only shrink the route.
  A V1 household that never disclosed is still protected: the protection is the household's fact, not
  the supplier's record of it.
- **The Consent route is not barred by V1.** The do-not-install list is guidance for involuntary moves
  (3.7). A household that asks for a prepayment meter may have one.

### GAPs
- **The gate before Feb 2023 is NOT ESTABLISHED.** 28.7 dates from Nov 2023. What a warrant needed
  before then (the 1954 Rights of Entry Act route, SLC 28's older "safe and reasonably practicable"
  text) was not located. The world refuses an involuntary move dated before Feb 2023 with that reason,
  rather than invent a gate. The real record has about 150,000 such moves in Jan 2022 to Jan 2023
  alone, so this understates the route for 2016-2022. A refusal that names the gap is how it gets
  found.
- **Do-not-install prevalence.** Energy UK (Feb 2026, pp. 10-11) puts about 25% of arrears £ with
  customers who have do-not-install characteristics. That is a £ share of arrears, not a share of
  households, so it does not set a prevalence. It is the check to run when the route is wired.
- **Unlawful installs.** Under 2% of the reviewed pre-rules moves should not have happened (MCR, Jun
  2026). The world refuses them instead, so a company defect shows as a refusal and not as a harmed
  household. That is a simplification of the world, not a fact about it.
- **Debt recovery on the new meter** (£6.01 electricity, £4.40 gas a week, Ofgem 2025, §2) is not built.
  It is built where the run first changes a meter, together with the household's life on it.

### What reaches it (2026-10-16, the Consent door)
Every run, through one seam door: `SimInterface.request_prepayment_move`. The company's residential
ladder already selects `prepayment_or_debt_agency` at 90 days overdue
(`company/billing/arrears_engine.py`). From this slice the collections desk
(`company/billing/collections_journey.py`) makes that step a real ask, by the Consent route only, and
records `prepayment_offered` straight after it with the world's answer.

DESIGN CHOICES, each named:
- **Consent only.** The company asks by explicit Consent (28.22). The door refuses an involuntary
  route with its reason: that decision is the director's reserved shape and is never automated.
- **The ask is one per journey, at the 90-day step.** The ladder puts the agency hand-over and the
  prepayment offer on one rung. The desk records the prepayment offer; the agency referral is not
  built, so it is not claimed.
- **What crosses back is what the conversation tells a supplier:** whether the meter is changed, and
  a reason. Never the household's V1 state.
- **Shipped, the household cannot answer.** The take-up share (`method_prepayment_offer_take_up_share`)
  ships at 0, as no published rate of take-up exists, so every offer is recorded unanswered with the
  world's reason. An agreed move is reachable through an injected world only.
- **A moved meter ends the journey on the `prepayment` exit.** GAP: life on the meter (debt recovered
  from top-ups at £6.01 / £4.40 a week, §2) is still not built, so the debt stays on the ledger and a
  later overdue read can open a new journey. This can only happen in an injected world today.

## After the last rung: what a supplier must and may do once the notices have gone, and when it stops (2026-10-24)

*K8 page for `the-collections-ladder-has-a-step-after-the-second-notice`. Raised by the 19 Oct run: a
£93.68 bill of April 2019 drew two notices, then nothing for five years, until it was written off 13 days
after the household left (`docs/staging/SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_AND_NO_MOVER_OR_TWO_RATE_HOME_2026-10-23.md`
§3). The rules are cited in the sections above and in `debt_and_collections.md` §3–4; this section only
puts them in order from the point where our ladder ran out.*

### What the rules require after the plan offer and the final notice (ESTABLISHED unless marked)
- **The SLC 27 duty does not end with the plan offer.** 27.5 is triggered whenever the supplier "has
  reason to believe" the customer "is having or will have difficulty paying". 27.5B (two missed monthly
  payments) is the *latest* point for contact. 27.6 is the menu that must then be offered (Fuel Direct
  where available, instalments under 27.8, a PPM where safe and practicable). **DERIVED:** each further
  missed bill on an account already in arrears is a fresh reason to believe, so the 27.6 offer is owed
  again. It is not owed once per debt.
- **Re-engagement after a failure is explicit for a broken plan.** 27.8A(g) asks for re-engagement "after
  an initial occurrence of a failed repayment arrangement", and §4.26 of the 2020 decision says on every
  failure, "as soon as" it is identified. A failure is defined as full payment not received within 10
  working days of the agreed date. **GAP A1:** no published text gives a re-contact cadence for a
  household that declined or never answered an offer. The duty is plain; the clock is not.
- **Prepayment.** By Consent: SLC 28.22, at any time. Involuntary: SLC 28B's Debt Trigger (3 months or
  more past the bill, £200 or more per fuel, not on a plan), at least 10 contact attempts, a Site Welfare
  Visit, and the do-not-install list (`debt_and_collections.md` §3; involuntary PPM section above). The
  involuntary route is the director's reserved shape here and is never automated.
- **Referral.** 31G.3A–3E: an enquiry service and signposting to free debt advice. Breathing Space
  holds all action (`debt_and_collections.md`, Breathing Space). Placement with a debt agency is
  supplier practice, and its order against write-off and sale is supplier-specific (§2.7 there). **GAP
  A2:** no published age or amount at which a *live* account is placed.
- **Proportionality.** 28.15: any recovery action, and its costs, must be proportionate to the amount.
  27.8C: nothing may be demanded while 27.5–27.8 are unmet.
- **Disconnection** is lawful only after all reasonable steps to recover through a PPM (27.9), and
  there have been none in GB since Q1 2023. It is not a lever.

### When it stops: the write-off
- **No licence condition obliges or dates a domestic write-off** (above, "What Ofgem has said about
  ability to pay since"). A live account's arrears cost money through provision while they stay
  (`how_a_gb_supplier_decides_to_write_off_a_failed_payment.md` (c)).
- **A live account is written off by an event, never on a clock.** The three published events are:
  - a scheme: the Debt Relief Scheme, phase 1;
  - redress;
  - **the statute bar.** Limitation Act 1980 s.5 bars an action on a simple contract debt six years
    after the cause of action, and s.29(5) restarts the clock on any payment or written acknowledgement
    by the debtor.
- **DERIVED:** on a balance-based running account, every payment on the account counts towards the
  oldest debt (Clayton's Case, `account_hierarchy_payment_allocation.md` s.1). So a debt becomes
  statute-barred only when the household has paid nothing for six years *and* the bill is six years
  past due. A supplier can read both off its own ledger.
- **GAP A3:** whether a supplier writes off at the bar or keeps a barred debt on the account
  (non-court collection of a barred debt is not unlawful in itself). **GAP A4:** DRS eligibility needs
  benefit status, which a supplier holds only when the household has told it. Not built.

### Design choices (the company desk, `company/billing/collections_journey.py`)
- **The further step is a re-offer of the 27.6 menu, through the plan door, on each bill that falls
  overdue after the ladder's top rung.** It is keyed to an observable event (a missed bill), not to an
  invented interval (GAP A1). Shipped, the world answers every offer None
  (`domestic_repayment_plan_take_up_and_keep_rates.md`), so the step is a recorded act. The world does
  not yet price it.
- **The write-off is the statute bar and nothing else:** `WriteOffReason.STATUTE_BARRED`, posted to the
  company ledger on the day both six-year conditions hold, for the debt they cover. No live-account
  write-off on any other clock (GAP A3 is erred on the side of chasing).
- **Not built:** live agency placement (GAP A2), DRS (GAP A4), Fuel Direct, and involuntary PPM (reserved).

## One ladder for one act: the ledger's per-bill notices take their days from the desk (2026-10-24)

*K8 page for `the-published-household-record-shows-the-desks-collections-journey`. There are two
ladders for the same act. The billing ledger's per-bill notices (`arrears_engine.LEDGER_NOTICES`) are
the published per-bill record, and they offered a payment plan at day 21 past due. The company
desk's rungs (`_DUNNING_PATHS`, run by `collections_journey`) offer it at day 28. The comment on
`LEDGER_NOTICES` recorded the disagreement when the notices moved out of the world (2026-10-12) and
left it unresolved. This is the VAT rule's shape: one requirement, two implementations.*

### What the rules and published practice say (ESTABLISHED unless marked)
- **No rule names a day for the plan offer.** SLC 27.8 says an affordable arrangement must be offered
  *before* any further action, and 27.5B makes two missed monthly payments the *latest* point for
  contact (section 1 table; "After the last rung" above). Neither 21 nor 28 is published. Both are
  inside the table's "Formal written demand ~T+3–4 weeks".
- **The first reminder is the same on both ladders.** Day 7 is the lower bound of "T+7–14d post-due"
  (`RESIDENTIAL_FIRST_REMINDER_THRESHOLD_DAYS`).

### Design choice
- **One source of days.** The ledger's FIRST_NOTICE is dated at the residential ladder's `reminder`
  rung and its SECOND_NOTICE at the `repayment_plan_offer` rung, both read off `_DUNNING_PATHS`. They
  are not restated. The desk's 28 is kept rather than the ledger's 21, for three reasons. It is the
  one that was reasoned against the table (the comment above `_DUNNING_PATHS`, 2026-10-04). It is the
  one the live desk acts on. And both domestic ladders, residential and micro-SME, already offer at 28.
- **The names stay.** FIRST_NOTICE and SECOND_NOTICE are the ledger's stage names, and several readers
  key on them. Only their dates come from the desk.
- **Commercial is not touched.** The I&C ledger's single DISPUTE_NOTICE (day 14) is a different act
  from the I&C desk's rungs (reminder 0, interest notice 7, final demand 21). It is not reconciled
  here, because there is no shared step to align. **GAP B1:** whether a disputed I&C invoice should
  run the desk's ladder at all is unexamined.
- **Both views are published, side by side.** The per-household record (`reaction_chain`) now carries
  the desk's journey (`collections_*` events), including the rungs past the plan offer, the re-offer
  past the top rung and the statute-bar write-off. The ledger's per-bill notices stay beside it. The
  explore cast's debt journey reads the desk's events when a record has them.

### Prediction, written before the change is run on a book
Moving SECOND_NOTICE from day 21 to day 28 moves no money. The notices are dated statements, and no
money figure reads their dates. Some notices disappear: a bill whose write-off date falls on days
21–27 loses its SECOND_NOTICE, because a notice dated after the write-off is not sent. Every other
SECOND_NOTICE is dated 7 days later. FIRST_NOTICE does not move. The count of SECOND_NOTICE stages on
any book can only fall.

**Measured against the published book (`docs/state/billing_ledger.json`, 19 Oct), after the prediction
above was written:** 342 cases carry a SECOND_NOTICE. None is written off on days 21–27. **Correction:
the prediction named only one way a notice is lost, and there is a second.** A case that credits or
repayments settle in full on days 21–27 loses its notice too, because `with_credits_applied` keeps
only the notices dated on or before the last credit. One case does this. So on that book 341 notices
remain, each dated 7 days later, and no money figure moves.
