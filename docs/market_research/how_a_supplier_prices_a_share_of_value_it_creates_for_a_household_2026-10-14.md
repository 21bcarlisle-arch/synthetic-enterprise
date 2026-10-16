# How a GB supplier prices a share of value it creates for a household: the rules, the published splits, and the analogues

**Knowledge:** next-best-action-and-cross-sell

**Read 2026-10-14**, opened by C34's own finding that next-best-action's joint-value rule is
positive-sum in all 18 test cells (+£13 to +£107 over 48 months) but negative on the supplier's own
side in all 18 (it gives up £2-3/month of margin when advice cuts consumption), so the rule as built
chooses nothing (`next_best_action_and_cross_sell.md` §6.1). The question this file answers: when
real GB suppliers, or close analogues, create value for a household and want to keep some of it,
what mechanism and what split does the published record actually show? All figures below were
fetched and read this pass; none is from training-data recall. Sources are quoted verbatim where the
quote carries the figure.

---

## 1. The rules: what a GB domestic supplier may charge for, or share, when it helps a household

**Read from Ofgem, *Electricity Supply Standard Licence Conditions, consolidated to 1 August 2025*
(ofgem.gov.uk, fetched 2026-10-14; Ofgem's own caveat: "Consolidated conditions are not formal Public
Register documents and should not be relied on").**

- **SLC 22B.1, the Ban on Acquisition-only Tariffs.** "The licensee must ensure that all its Tariffs
  are available to, and are capable of being entered into by, both new and existing Domestic
  Customers." The carve-outs at 22B.2 are a Closed Fixed Term Tariff, a Collective Switching Tariff, a
  Dead Tariff, and (22B.2(d)) a tariff "offered to a particular group of Domestic Customers defined on
  the basis of criteria specified by the licensee, provided that the criteria do not in any way relate
  to whether or not the Domestic Customer is a new or existing Domestic Customer." **ESTABLISHED:** a
  priced tariff open only to households who accept an advice-linked fee, and not one of the named
  exceptions, would need to be offered to new customers too, or it is barred. This reaches a
  *tariff*. Whether a standalone advice fee charged alongside the existing tariff (not itself a new
  tariff) is caught by 22B at all is **NOT ESTABLISHED** — nothing in the condition's text or Ofgem's
  commentary (`a_save_offer_against_the_switching_rules_and_the_seam.md` §1d, §6) addresses it.
- **SLC 0.6-0.7, Standards of Conduct.** "Apart from any matters relating to Deemed Contracts,
  standard condition 0 does not apply in respect of the amount or amounts of any Charges for the
  Supply of Electricity or any other type of charge or fee, applied or waived." Condition 0 does apply
  "to the exercise of a licensee's discretion to apply or waive any fee or charge" (0.7). **ESTABLISHED:**
  Ofgem's fairness rule does not bound a fee's *size*; it bounds the *behaviour* around deciding to
  apply or waive one, and the *information* given about it (SLC 0.3(b): must be complete, accurate,
  "relates to products or services which are appropriate to the Domestic Customer", and must not
  "create a material imbalance ... in favour of the licensee"). A shared-savings fee is therefore
  unconstrained in *depth* by SLC 0, but constrained in *how it is sold and to whom*.
- **No licence condition found that names a savings-share, commission or success fee as a
  permitted or forbidden charge type.** The 611-page consolidated text was searched for "energy
  saving", "energy efficiency advice", "commission" and "shared savings"; the only hit is SLC 43,
  which is about the Secretary of State's information-gathering power over smart-metering savings,
  not pricing. **GAP, confirmed by absence, not by a ruling:** Ofgem's licence is silent on
  shared-savings fee structures for domestic retail advice. Silence is not permission; it means the
  general law (below) is what actually governs the design.
- **Consumer credit law reaches a shared-savings fee the moment it is recovered over time rather
  than deducted once.** The precedent is domestic, GB, and energy-specific: the Green Deal's "Golden
  Rule" financing mechanism was a regulated consumer credit agreement under the Consumer Credit Act
  1974. The Consumer Credit (Green Deal) Regulations 2012 (SI 2012/2798, legislation.gov.uk, fetched
  2026-10-14), Explanatory Note: "Section 95B, which was inserted by section 29 of the [Energy Act]
  2011 Act, enables a creditor to claim compensation from a debtor where all or part of the credit
  outstanding under a green deal plan is repaid early. **Section 95B only applies to green deal plans
  that are regulated consumer credit agreements under the 1974 Act.**" **ESTABLISHED:** a mechanism
  that funds an action now and recovers a share of the future saving through instalments on the energy
  bill is consumer credit, and brings FCA authorisation, affordability assessment and early-repayment
  rules with it. A fee taken as a one-off deduction from a one-off, already-realised saving (for
  example, a single cashback payment) is a different legal shape and was not found to trigger the same
  regime — but no source confirming that boundary for a *savings-share* fee specifically (as opposed to
  a financed measure) was found. **GAP.**
- **Consumer Rights Act 2015, Part 2 (unfair terms).** Not specifically tested in this pass against a
  shared-savings fee. The test turns on "significant imbalance" and transparency; a fee keyed to a
  counterfactual the household cannot itself verify (what it would have spent without the advice) is
  the kind of term the imbalance test was written for. **GAP: no case law or guidance found that
  applies this to an energy savings-share fee.**
- **FCA regulation of the fee itself (rather than any financing wrapped around it) was not
  established either way.** A pure advice fee, paid once, outside a credit agreement, was not found to
  require FCA authorisation. This is reasoned from absence, not from a positive finding, and should be
  read as a GAP alongside the others above.

---

## 2. Published GB energy practice where created value is split between provider and household

### 2.1 NESO's Demand Flexibility Service (DFS): the only GB mechanism with a full, published chain

**Source for 2022/23: Octopus Energy Group, *Consumer flexibility: ready to replace coal*, Simona
Burchill & Kieron Stopforth, 8 June 2023 (fetched from octoenergy-production-media.s3.amazonaws.com,
2026-10-14) — Octopus's own account of its own scheme, not an independent audit.**

- **What NESO paid the provider.** "Test events were dispatched at a Guaranteed Acceptance Price (GAP)
  of £3,000/MWh" — £3.00/kWh. "Live events were dispatched in response to system stress conditions and
  were cleared through an auction" at an unpublished, presumably higher, price.
- **What Octopus paid households.** "The average incentive levels were £2.25/kWh for Test and
  £3.69/kWh for Live events."
- **The computable split, Test events only (the one side with both prices published):** of the £3.00/kWh
  NESO paid, Octopus passed through £2.25/kWh (**75%**) and retained £0.75/kWh (**25%**) before its own
  costs (engagement, measurement, the Kraken platform). For Live events the household rate (£3.69/kWh)
  exceeds the Test GAP, which only shows that Live auction-clearing prices ran above £3,000/MWh; NESO's
  actual Live clearing price was not found in what could be fetched, so Octopus's margin on Live events
  **cannot be computed** from this source. **GAP.**
- **Aggregate, both event types blended:** "paid out over £5.4 million to customers" against "1.86GWh of
  demand" shifted ≈ **£2.90/kWh** blended average — consistent with the two published rates once
  weighted by event mix.
- **Scale and persistence.** 700,000 customers signed up of 1.4 million invited; "the average opt-in
  earned £8 over the course of the Service and the top 5% earned over £40." Octopus's own second-year
  press release (*Price cap protect: Octopus' customers beating the price cap by reducing energy
  usage*, 22 January 2024, octopus.energy/press, fetched 2026-10-14) gives winter 23/24: "1,200,000"
  signed up, "£4m" paid in 10 hours of events that winter, "Accumulative average earning of top 5%: >£60."
- **The price has since fallen sharply at the NESO end.** NESO, *Demand Flexibility Service Market
  Information Report*, published 11 August 2026 (neso.energy/document/385526/download, fetched
  2026-10-14): the GAP for the August-September 2026 test events is **£500/MWh (£0.50/kWh) for demand
  turn-down and £180/MWh (£0.18/kWh) for demand turn-up** — a fall of roughly 83% on the turn-down side
  since winter 2022/23's £3,000/MWh. The report states these levels were "set to be in line with the
  high end of attainable revenue, informed by actual scenarios observed this year", i.e. the ceiling
  itself has compressed, not just what any one provider chose to pass on.
- **Reading this against the next-best-action question.** DFS shows a documented, published,
  three-quarter pass-through of a wholesale-side value stream to the household, with the supplier
  (Octopus, acting as the provider/aggregator) keeping the remaining quarter. It is the closest GB
  energy precedent to "a household benefit, funded by value the supplier itself monetises elsewhere,
  split by a fixed ratio." It is **not** a precedent for sharing a saving that has no separate
  wholesale-side monetisation — DFS payments are funded by NESO's balancing spend, not by the
  household's own avoided consumption value to the supplier.

### 2.2 Smart Export Guarantee (SEG): no mandated split, and a published spread between import and export prices

**Source: Ofgem, SEG webpage (ofgem.gov.uk/environmental-and-social-schemes/smart-export-guarantee-seg,
fetched 2026-10-14).** "SEG Licensees determine the rate, contract length and other terms which SEG
Generators will receive. **SEG tariff rates must always be above zero.**" No minimum, no benchmark to
wholesale, no formula: Ofgem sets only a floor of "not zero".

**Source: Which?, *The best Smart Export Guarantee rates*, rates "correct in April 2026" (which.co.uk,
fetched 2026-10-14).**

| tariff (who may take it) | rate, p/kWh |
|---|---|
| Octopus Intelligent Octopus Flux (solar + battery, Octopus import customers) | 23p |
| EDF Export Exclusive 12m V3 (solar/battery installed through EDF) | 18p |
| British Gas Export and Earn Plus | 15.1p |
| Octopus Outgoing Octopus (solar only, Octopus customers) | 12p |
| EDF SEG Export Variable (anyone) | 5.6p |
| Octopus SEG (anyone) | 4.1p |
| British Gas SEG (anyone) | 3.02p |
| EDF SEG Export Variable (anyone) | 3p |

The same article: "British Gas, EDF Energy, Good Energy and Scottish Power pay 15p/kWh for their
import energy customers (or those who are willing to switch to them)" — read against the open
(anyone-eligible) SEG rates of 3-5.6p/kWh from the same four suppliers, the same household's imported
and exported kWh are priced roughly **3 to 5 times apart** depending on whether it also holds the
supplier's import tariff. Octopus, quoted in the same article: **"We don't make a huge amount of
money by offering these cut-price export products, but they benefit a greener grid and world. Because
of this, we're happy to do the work to provide these tariffs for our customers."** That is a supplier's
own account of its margin on the open SEG rate, not an audited figure, and it is self-serving (it is
a press quote), so it is graded **L**.

### 2.3 Energy Company Obligation (ECO): full-cost funding, not a savings share

**Source: Ofgem, ECO webpage (ofgem.gov.uk/environmental-and-social-schemes/energy-company-obligation-eco,
fetched 2026-10-14).** "The ECO scheme works by placing a Home Heating Cost Reduction Obligation
(HHCRO) on medium and large energy suppliers... The overall target for these measures is divided
between suppliers based on their relative share of the domestic gas and electricity market." The
supplier funds the measure (insulation, a heating upgrade) **in full**, as a licence obligation sized
by market share, not by a formula linked to the household's own savings. **ESTABLISHED: this is the
opposite polarity to a shared-savings fee** — the household keeps 100% of the bill saving, and the
supplier's "return" is regulatory compliance, not a cash share, with the obligation's cost ultimately
recovered across the supplier's whole customer base (a transfer across the book, not a value share
with the recipient household).

### 2.4 "Heat as a Service" (HaaS): a flat subscription, not a savings share

**Source: EIBI, *Heat as a service trials undertaken* (eibi.co.uk, fetched 2026-10-14); corroborated
by edie.net, 26 February 2020 (paywalled beyond the intro, read to the extent available).** Bristol
Energy and Baxi Heating ran a year-long, BEIS-funded trial via Energy Systems Catapult's Living Labs
(100 homes across Newcastle, Manchester, the West Midlands, Gloucestershire and Bridgend). The
quoted mechanism: a **"Heat Plan" where consumers purchased 'hours of warmth' rather than units of
energy (kWh)"**, at **"a fixed price based on data about the thermal efficiency of their home and the
number of hours of warmth needed by the customer each week."** **ESTABLISHED: this is a flat
subscription fee, decoupled from metered kWh, not a percentage of any measured saving.** It is the one
published GB "comfort/outcome-priced" trial found, and it does not use the shared-savings shape at
all; it substitutes a different unit of sale (hours of warmth) for the usual one (kWh).

---

## 3. Analogues outside domestic energy retail, with published splits

### 3.1 Energy Performance Contracting / ESCO shared-savings contracts

**Source: Hawaii State Energy Office, *Pros & Cons of Guaranteed Energy Savings vs. Shared Savings
Performance Contracts* (as of February 2013), energy.hawaii.gov, fetched 2026-10-14.** Describing the
"Traditional model": "The ESCO provides financing as well as project development and implementation
costs... The dollar value of measured consumption savings times actual utility rates using utility
bill reconstruction may be divided between the Owner and the ESCO. **A typical division of the value
of future savings would be 85% for the ESCO and 15% for the Owner.** The ESCO would receive the
largest share in the beginning due to its up-front investment; but, the ESCO share may decrease over
time depending upon the term of the agreement." The IEA's own ESCO contracts page (iea.org, read via
search snippet, fetched 2026-10-14, not quoted verbatim this pass) corroborates the shape — the ESCO
"assumes both the technical and the credit risk... with the energy savings shared between the ESCO and
the client over the contract period" — without giving its own numeric split, so it is treated as
corroboration of the mechanism, not a second number.

**Caveat, stated plainly.** This is a US public-sector commercial/institutional building retrofit
contract, financed capital-equipment shape. It is **not** domestic, **not** GB, and **not** an energy
*supply* relationship — the ESCO is a contractor to a building owner, not that owner's electricity
retailer. The 85/15 split is also levered by the ESCO's own capital outlay, which a supplier's
advice-driven next-best-action (no capex, just advice and a tariff nudge) does not carry. It is useful
only as evidence that a "majority share to the value-creating party while it is still owed for its
up-front cost, tapering as the debt clears" shape is an established contracting norm somewhere in
energy, not as a number to import.

### 3.2 GB Green Deal "Golden Rule": a financed cap, not a revenue share

**Source: gov.uk, *How savings figures are calculated under the Green Deal's Golden Rule* (archived
DECC-era guidance, fetched 2026-10-14).** Worked example in the source: "the customer would be told
that the expected savings from a typical household in that property are £103, and that **the maximum
first year repayment under the Green Deal would be £103.**" The mechanism (cross-checked against four
further summaries, including Wikipedia's *The Green Deal* and englishlawguide.co.uk, both read for
corroboration only) caps what the finance provider may recover through the bill at the estimated
first-year saving — so in year one the household's *net* cash position is unchanged (100% of the
estimated saving is recovered as repayment), and once the balance is repaid the household keeps 100%
of any further saving. This is **a financing cap, not a permanent percentage split** — the opposite
shape to the ESCO's ongoing 85/15. As §1 establishes, it is also regulated consumer credit (SI
2012/2798), which is the reason its shape had to be a capped, time-limited repayment rather than an
open-ended share.

### 3.3 Telecoms and financial-services analogues

**Not found, this pass, beyond what the existing next-best-action and save-offer documents already
carry (which do not address value-sharing pricing directly).** The brief for this file named
"telecoms or financial analogues already noted in the context docs" as a candidate; neither
`next_best_action_and_cross_sell.md` nor `a_save_offer_against_the_switching_rules_and_the_seam.md`
in fact prices a shared-savings mechanism — their analogues (Ofcom's prospective "best tariff" rule,
Which?/Citizens Advice haggling guidance) were themselves recorded as **GAP, not retrieved**, in
§7c of the save-offer document. This pass did not re-attempt those two specific URLs; the gap stands
as previously filed, and is not duplicated with new wording here.

---

## 4. GAPs, labelled

1. Whether a standalone advice fee (not itself a new "Tariff") is reached by SLC 22B at all. **GAP.**
2. Whether the Consumer Rights Act 2015 unfair-terms test has ever been applied, by the courts, the
   CMA or Ofgem, to a savings-share fee in energy. **GAP — not found in what could be read.**
3. Whether a one-off, immediately-deducted shared-savings fee (no instalment, no financing) falls
   outside consumer credit regulation the way a financed one (Green Deal) does not. **GAP.**
4. NESO's actual Live-event clearing price for DFS winter 2022/23, which would let Octopus's margin
   on Live events be computed the way its Test-event margin can be. **GAP.**
5. Any GB supplier's own published shared-savings or advice-fee structure for *energy efficiency
   advice specifically* (as opposed to DFS flexibility or SEG export). **Not found** across three
   search strategies (licence text, Ofgem schemes, consumer press); reads as "not published", not
   "not found in what could be read".
6. The Ofcom "best tariff" and Which?/Citizens Advice haggling-guidance analogues named in the
   existing save-offer document remain unretrieved (its own §7c, carried forward, not re-attempted
   here).
7. Whether FCA Consumer Duty (PS22/9) or GIPP-style pricing-practice rules reach a savings-share fee
   specifically, as opposed to insurance products generally (already an open question in the
   next-best-action document, §4.5, not resolved here).

---

## 5. What this means for the supplier's design, stated as evidence and not a decision

Ranked by how directly the evidence supports each shape; no number is recommended, per the
director's own question.

1. **A fixed, flat per-action or subscription-style fee** is the most directly evidenced GB domestic
   energy shape (HaaS's "Heat Plan", §2.4) — but it was tested as a substitute for metered billing
   generally, not a price on one piece of advice, and no take-up or margin figures were found. Support:
   **GB, domestic, energy — but the wrong unit of comparison.**
2. **A margin/revenue share has two published precedents** (ESCO 85/15 tapering, §3.1; DFS's 75/25
   Test-event pass-through, §2.1) — one keeps a minority share of value the supplier did not capitalise
   (DFS), the other a majority share while still owed for capital spent (ESCO). Neither is domestic
   retail energy advice. Support: **indirect analogy, two different ratios, neither GB domestic.**
3. **Financing the action and recovering a capped share of the future saving via bill instalments has
   a GB, domestic, energy-specific precedent (Green Deal's Golden Rule, §3.2) — but it is regulated
   consumer credit**, which brings a different build cost (FCA authorisation, affordability
   assessment, early-repayment formula) than a same-session fee or a tariff-margin adjustment would.
   Support: **the most directly evidenced of the three mechanisms for GB domestic energy, but its
   evidence also establishes a structural precondition (credit regulation) rather than a clean number.**
4. **A flat per-kWh reward funded by a wholesale-side value stream** (DFS, SEG) is strongly evidenced
   in GB domestic energy — but it rewards shifted/exported kWh that NESO or the wholesale market pays
   for, not a household's avoided spend from advice, which has no separate wholesale-side buyer.
   Support: **strong evidence the mechanism exists, weak relevance here, because the funding source
   does not carry across.**
5. **No standing fee at all (`cut_share`/equivalent left `None`) is the position the save-offer
   document already reached for its own, different pricing question (§7d), for the same underlying
   reason: nothing in the published record prices *this* mechanism directly.** Nothing found this pass
   changes that position for an advice-sharing fee either. It remains the one choice the evidence does
   not contradict, because it is not a choice about a size at all.

---

## 6. The choices C35 makes, and why (2026-10-16, K8 for `company/crm/next_best_action.py`)

The director, 2026-10-15: the share is "not a ruling from me" but the supplier's own commercial
optimisation, judged on joint value under both no-loss floors (C34), against the household's
response to the price.

1. **What is optimised is EXPECTED joint value: take-up × (our change + the household's benefit).**
   The fee is a transfer. It leaves the joint value of a taken action unchanged, so the share moves
   joint value only through whether households take the action. Under take-up that falls with the
   share, the best share is the LOWEST that clears our floor. Anything above it moves value from the
   household to us and costs households who would have said yes. This is M2 in mechanism form.
2. **The fee is one-off.** Recovering it by instalments is regulated consumer credit (§1, the Green
   Deal precedent), and the company holds no credit permission. Whether a one-off fee is clear of
   credit regulation is §4 GAP 3. It is carried, not resolved.
3. **The supplier searches only the shares it has tried and observed.** It has no grid of its own and
   no elasticity number. No published source prices take-up of a savings-share fee for advice (§4
   GAP 5). The price comes from the supplier's own tests, which is the real twin: testing what share
   households will pay.
4. **With no tried share, the action is priced as C34 prices it.** That is a named reason on the
   decision, never an invented response.
5. **GAP, world side:** the world's household (W2_39, `simulation/contact_response.py`) answers a
   contact, but it has no response to a PRICED share of advice. So in a run the supplier can never
   observe a take-up point, and C35 stays dormant. The design question belongs to the world: does a
   household weigh a one-off fee against its own expected saving, and with what discounting? Until
   it is answered from evidence, C35 is at L1.
