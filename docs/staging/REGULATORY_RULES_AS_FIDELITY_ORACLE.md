# REGULATORY_RULES_AS_FIDELITY_ORACLE.md
*Advisor-staged research artefact. Director-decided 2026-07-12 (in-console instruction). Provenance and usage rules below.*

---

## 0. Place in the epoch arc, and how this document may be used

**The director's method insight, stated as a standing principle:** every line of retail-energy regulation exists because the failure it addresses actually occurs. Back-billing caps exist because estimation regimes produce maxi-bills. Theft obligations exist because meters get tampered with. Winter disconnection bans exist because suppliers disconnect in winter. **Therefore a market's rulebook is a checklist of unhappy paths.** If the SIM never produces the situation a rule polices, either the SIM is missing a mechanism, or the mechanism is legitimately out of scope — but the gap should be a *decision*, not an accident. This document reads four-plus markets' rulebooks as that oracle.

**Epoch placement:**
- The **UK rows** feed Epoch 1 core fidelity and the Epoch 2 Value Cycle directly (billing physics, meter→cash, catch-up/back-billing are already the D-lane's charter).
- The **cross-market comparison** is PORTABILITY_DESIGN_CONSTRAINTS material: **nothing multi-market is to be built or stubbed until post-Epoch-3.** The multi-market content here is (a) a portability *lens* to check today's UK-only designs against, and (b) a pre-assembled artefact library for the Epoch-3+ walled-interfaces / go-live analysis work. The "global billing top 10" is a design-constraints register, not a build instruction.
- Per DOMAIN_ARTEFACT_LIBRARY discipline, every external anchor below carries a provenance tag:
  - `[validator-anchor]` — usable by the harness-outside-the-wall to check SIM/company outputs; must NOT be fed to the same generator it validates.
  - `[company-knowable]` — a real supplier would know this (it's published law/licence); the company-inside-the-wall may encode it in compliance/billing logic.
  - Most regulatory rules are legitimately **both** company-knowable (the company must comply) and validator-anchors (the harness checks compliance) — that dual use is fine because the rule text is public; what stays mutually exclusive is *statistical calibration* sources.
- Confidence flags: `[H]` fetched directly this pass from primary/near-primary sources; `[M]` fetched from secondary sources or partially confirmed; `[L]` from general knowledge, not fetched this pass — verify before encoding as an invariant.

---

## 1. Market rule digests

### 1.1 United Kingdom (GB) — Ofgem licence regime `[H]` `[company-knowable]` `[validator-anchor]`

**Back-billing — SLC 21BA (domestic, from 1 May 2018) and SLC 7A analogue (microbusiness, from 1 Nov 2018):**
- A supplier taking "charge recovery action" cannot recover charges for energy consumed **more than 12 months** before an accurate bill was issued. The clock anchors on the **date of accurate billing**, not the date of the read. Covers unit charges, standing charges and VAT; covers DD adjustments and charges applied to prepayment meters.
- Exceptions: (a) recovery action already taken compliantly (chasing a previously issued accurate bill is not back-billing); (b) **obstructive or manifestly unreasonable customer behaviour** — blocking meter access, tampering, theft; (c) Ofgem-specified circumstances. Crucially, Ofgem is explicit that **failing to provide meter readings is NOT customer fault** — the estimation risk sits with the supplier.
- Larger (non-micro) business customers fall outside 21BA; ordinary Limitation Act 1980 six-year contractual limitation applies instead.
- Practical consequence: a supplier that issues estimate after estimate and then true-ups after 2 years **loses the >12-month tranche as a write-off**. Ombudsman complaint volumes on this remain in the thousands per year — this is a live, common failure, not a corner case.

**Theft/tampering — SLC 12A + REC arrangements:**
- Since 2014-16, suppliers hold licence obligations to **detect, investigate and prevent** energy theft (gas first, then electricity). Industry machinery: the **Theft Risk Assessment Service (TRAS)** (ElectraLink-administered, live April 2016) scores theft likelihood per site from cross-supplier data; the **Theft Detection Incentive Scheme (TDIS)** under REC Schedule 7 sets per-supplier detection targets by market share; **ETTOS** (Crimestoppers-fronted tip-off hotline) feeds leads. Theft was estimated at ~£500m/yr at TRAS launch. Suppliers must engage with TRAS but choose which leads to investigate.
- Theft/tampering is exactly the customer-fault condition that pierces the 12-month back-billing cap.

**Other UK unhappy-path organs relevant to the oracle:** `[M]` (mechanisms confirmed in prior project passes or general knowledge; precise current parameters should be re-verified before encoding)
- Guaranteed Standards of Performance (GSOP): automatic fixed compensation for defined service failures (missed appointments, delayed switches, late final bills/refunds).
- Final bill after switch/closure within six weeks, with auto-compensation on breach.
- Erroneous transfer procedures (wrong meter point switched) with prescribed unwind and customer-held-harmless treatment.
- Deemed contracts: an occupier consuming without a contract is on deemed terms — a legally required tariff state.
- Priority Services Register; winter disconnection protections for vulnerable households; severe restrictions on warrant-installed prepayment (post-2023 rules).
- Complaints: 8 weeks or deadlock → Energy Ombudsman, binding on the supplier, **per-case fee charged to the supplier** — service failure has a direct unit cost.
- SLC 14 DD surplus rules (already built), SLC 25C channel choice (already built), Consumer Duty-style fair treatment principles (SLC 0/0A).

### 1.2 Australia — NECF (NSW/QLD/SA/TAS/ACT) + Victoria `[H]` `[company-knowable]` `[validator-anchor]`

**Undercharging — NERR Rule 30:**
- Where the retailer undercharged a small customer, recovery is limited to the amount undercharged in the **9 months** before the date the customer is *notified* — **unless the undercharge resulted from the customer's fault or unlawful act/omission**.
- **No interest** may be charged on the recovered amount.
- The amount must be shown as a **separate line item** with an explanation.
- The retailer must offer instalments over a period **the customer nominates**, up to the length of the undercharge period (max 12 months) — i.e. a 6-month back-bill earns a 6-month payment plan by right.
- Overcharging (Rule 31) has a mirrored refund obligation.

**Estimation — NERR Rule 21:** bills must be based on metering data or a method the customer agreed to; estimation is permitted when actual data can't be obtained; customers can submit **self-reads** (photo of the meter) and rule-change history shows regulator pressure against "grossly inaccurate" estimates; a customer can demand a meter check on dispute (customer pays if the meter is fine). Bill-smoothing requires **explicit informed consent** with a 12-month true-up (Rule 23).

**Bill frequency:** at least **every 100 days** (i.e. ~quarterly billing is the national norm — structurally different from UK monthly-DD culture).

**Victoria (ESC Energy Retail Code of Practice):** back-billing limited to **4 months** where the customer is not at fault (tightened from 9 months, effective 1 Jan 2021) — the strictest limit found in this pass. Victoria also runs **wrongful disconnection payments** (per-day compensation) and a **best-offer obligation** (retailer must periodically tell the customer on the bill if a better plan of its own exists) `[M]`.

**Life support:** registered life-support premises get near-absolute disconnection protection with civil penalties — the strongest single consumer protection in the NECF; hardship programs are mandatory and audited; illegal energy use (Rule 32) lets the retailer estimate and bill stolen energy outside the 9-month cap `[M]`.

### 1.3 France `[H]` `[company-knowable]` `[validator-anchor]`

**The 14-month rule — Code de la consommation Art. L224-11 (in force 17 Aug 2016, from the 2015 energy-transition law):**
- The supplier must bill **at least once a year on actual consumption**, and **no consumption older than 14 months before the last actual or self-read may be billed** — the clock anchors on the read, not the bill.
- Exceptions: (a) meter access refused; (b) the customer failed to transmit a self-read **after the network operator (DSO) wrote by registered letter with acknowledgment (LRAR)** inviting one; (c) **fraud**. Médiateur case law is strict on the letter: a generic reminder doesn't count — it must **explicitly invite a self-read**, or the exception fails and the 14-month cap bites. The evidence trail is decisive.
- Breach is a 5th-class contravention: €1,500 fine (€3,000 repeat).
- Separately, a **2-year payment prescription** (L218-2) extinguishes the right to demand payment of any issued bill after 2 years without a valid interruption.
- Médiateur case law also requires catch-up consumption to be **allocated pro-rata across the price periods it spans** (lissage prorata temporis) — billing it all at the latest (highest) price is non-compliant. This is a pure billing-engine correctness rule.
- Credit regularisation in the customer's favour: overpayments **> €25 must be refunded within 15 days** `[M]`.
- **Trêve hivernale:** absolute ban on disconnecting household electricity/gas for non-payment **1 November – 31 March** (power reduction partially permitted for electricity) — a calendar-windowed compliance rule. Chèque énergie (means-tested energy voucher) and FSL (local solidarity fund) sit alongside `[M]`.
- Structural notes: TVA is split-rate **within one bill** (5.5% on the standing charge/abonnement, 20% on consumption) `[M]`; ~95% Linky smart-meter penetration has made monthly actual billing the norm and regularisation bills a shrinking class; regulated tariff (TRV) still exists for households; domestic contracts terminable any time without fees.

### 1.4 Belgium — federal accord + three regional regimes `[H]/[M]` `[company-knowable]` `[validator-anchor]`

Belgium is the miniature stress test for "geography as parameter": **one small market, three regulators (VREG/Flanders, CWaPE/Wallonia, Brugel/Brussels) plus a federal consumer accord**, and rules genuinely diverge by region.

- **Billing-error rectification — federal "Consumer Accord":** supplier terms may not allow more than **12 months** to rectify billing errors (voluntary accord — most but not all suppliers are signatories; Mega, Cociter, Energie2030 noted as non-signatories in Wallonia sources). The federal ombudsman enforces credit-back of late rectifications against signatories.
- **Brussels:** rectification window extends to **2 years where the rectification concerns meter indexes**, and **5 years where customer bad faith** is established — an explicit three-tier fault-graded window in one region. Disconnection for non-payment requires a **justice-of-the-peace order** plus winter protection — the judicial-gate model `[M]`.
- **Wallonia:** the annual settlement bill must be issued within **60 days** of the DSO transmitting the index; refunds due to the customer within **30 days** of the settlement bill. Dunning is prescribed: reminder giving ≥14 days, then formal notice (mise en demeure) only if debt ≥ €100 (€200 dual-fuel) giving 15 days; **recovery fees capped at €55 per energy per calendar year**. Non-payment path runs through budget meters / protected-customer status / CPAS social services rather than simple disconnection `[M]`.
- **Flanders:** final bill within **4 weeks** of switch/move; the DSO acts as social supplier of last resort with budget-meter/minimum-supply machinery; supplier "dropping" of bad payers pushes customers to the DSO rather than off supply `[M]`.
- **Common Belgian structure:** strictly **separate contracts per fuel** (no single dual-fuel contract), EAN-coded supply points, 1-month switching notice, no termination fees, federal social tariff (price set by CREG) for protected categories, 6% domestic VAT plus federal excise and regional levies `[M]`.

### 1.5 Italy — the 2-year prescription `[H]` `[validator-anchor]` `[company-knowable]`

- Budget Law 2018 (L.205/2017) + ARERA delibera 97/2018 cut the prescription on electricity/gas/water consumption from 5 to **2 years** (electricity from Mar 2018, gas from Jan 2019, water from Jan 2020). Budget Law 2020 made it invocable **"in ogni caso"** (from 1 Jan 2020) — for domestic customers and microenterprises the 2-year bar applies even where the delay wasn't the seller's fault (the earlier customer-fault carve-out was removed for these classes). It also applies **between sellers and distributors** — the wholesale true-up chain is time-boxed too.
- Unique operational burden: the seller must **separately and clearly identify prescribable amounts on the bill** (or issue a separate bill for them), must **inform the customer of the right to refuse** them, and must **provide the opt-out form** (on the bill, website, and counters). Silence or payment waives the right. Prescription is interrupted only by formal registered demand (raccomandata A/R or PEC) — call-centre chasers and ordinary letters don't count.
- The prescription clock can run from the **regulated deadline by which the bill should have been issued** (Testo Integrato Fatturazione), not the actual late issue date — a "billing block" doesn't stop the clock.

### 1.6 EU framework — the floor under all EU markets `[H]` `[company-knowable]`

Directive (EU) 2019/944 (electricity, as amended by 2024/1711) + Annex I set the billing floor every member state transposes:
- Bills accurate, clear, free of charge; e-billing option; **on request, a clear explanation of how the bill was derived, especially where not based on actual consumption**.
- **Frequency:** with remote-readable meters, accurate billing information based on actual consumption **at least monthly**; without, **at least every 6 months** (every 3 on request or with e-billing).
- **Price breakdown into three defined components** (energy+supply / network / taxes-levies-fees) using EU-common definitions (Reg 2016/1952); **fuel-mix disclosure per contract** (product-level); comparison-tool reference.
- **Historical consumption:** cumulative data for ≥3 years on request; time-of-use detail for ≥24 months via internet/meter interface without undue delay.
- Switching: technical switch target **24 hours by 2026**; termination fees only on fixed-term-fixed-price contracts and capped at direct economic loss.
- Vulnerability: right to information on alternatives (payment plans, moratoria) **before** disconnection; 2024/1711 strengthens protection of vulnerable customers from disconnection and adds supplier **hedging-strategy supervision** by regulators (a striking validation of this project's hedging-mandate lane: hedging discipline is becoming a *retail licence* matter in the EU).
- GDPR governs granular metering data (consent/purpose limitation) — the UK's settlement-consent debate has EU cousins everywhere.

### 1.7 Sighting notes on other markets `[L]` — registered, not researched this pass
- **Germany:** annual billing minimum (EnWG §40 family), correction/limitation via general 3-year civil prescription (§195 BGB), supplier-of-last-resort (Grundversorgung) as the deemed-contract analogue. Verify before use.
- **Netherlands:** ACM-supervised; ~2-year consumer billing correction practice; postcode-based capacity tariff structure. Verify before use.
- **Ireland:** CRU rules transposing 2019/944 (see §1.6); back-billing customer-protection code analogous to UK. Verify before use.

---

## 2. Commonality and difference — what one supplier engine must cope with

### 2.1 The universal pattern (build once)
Every market studied converges on the same **five-part unhappy-path grammar**:
1. **A time-boxed recoverability window** for supplier-caused under-billing (12m UK / 9m NECF / 4m VIC / 14m FR / 12m BE-accord / 2y IT), always with
2. **a customer-fault exception** (obstruction, tampering, fraud, refused access) that pierces or extends the window — meaning *fault attribution with an evidence trail* is what determines money, everywhere;
3. **transparency duties on the catch-up artefact itself** (separate line item + explanation AU/IT; prescribable-amount disclosure IT; pro-rata price allocation FR);
4. **a mandatory payment-plan offer** proportional to the failure (AU matched-period instalments; FR/BE échéanciers; UK ability-to-pay principles);
5. **an escalation/ADR backstop with teeth** (Ombudsman UK/BE/AU state schemes; médiateur FR; ARERA conciliation IT) whose case economics land on the supplier.

Likewise universal: estimation is everywhere legal but everywhere *disciplined* (self-read rights, accuracy duties, annual actual-read minimums); disconnection is everywhere a guarded state machine (calendar ban FR; court order BXL; life-support register AU; vulnerability register UK; DSO-as-social-supplier Flanders); and theft everywhere flips the customer from protected to liable.

**Strategic read:** the grammar is one engine; the numbers, clock anchors, and evidence requirements are parameters. This directly supports the pitch thesis that geography is a parameter — but only if the billing core is built around *events, fault attribution, and reconstructible time* from the start, which is precisely the Epoch-2 bitemporal/event-primitive architecture. The regulation is an independent argument for the architecture already chosen.

### 2.2 The genuine differences (parameterise, don't assume)
| Dimension | UK | AU (NECF) | VIC | FR | BE | IT |
|---|---|---|---|---|---|---|
| Under-billing recovery window | 12m | 9m | 4m | 14m | 12m accord; BXL 2y index / 5y bad faith | 2y |
| Clock anchors on | accurate bill date | customer notification date | notification | last actual/self read | error/rectification | regulated bill-issue deadline |
| Interest on back-bill | not prohibited by 21BA (practice: no) | **prohibited** | prohibited | n/a | n/a | n/a |
| Instalment right | ability-to-pay principle | **matched period, customer-nominated** | matched | échéancier on request | prescribed dunning ladder | on request |
| Fault exception evidence | "obstructive/manifestly unreasonable", case-by-case | "fault or unlawful act" | same | **LRAR letter explicitly inviting self-read** | bad-faith finding (BXL) | (removed for domestic/micro since 2020) |
| Min bill frequency | monthly info norm (smart) | **every 100 days** | ~quarterly | annual actual minimum; monthly info (Linky) | annual settlement + monthly acomptes | per Testo Integrato |
| Who owns reads | supplier-led (→MHHS) | metering coordinator/retailer | same | **DSO (Enedis/GRDF)** | **DSO** | **DSO** |
| Disconnection guard | vulnerability rules, PPM restrictions | last resort + life support | + wrongful-disc. payments | **calendar ban Nov–Mar** | court order (BXL) / budget meter (WAL/VL) | bonus sociale, ARERA procedure |
| Tax in bill | 5% dom / 20% biz + CCL | GST 10% flat | GST 10% | **5.5% + 20% split within one bill** + accise + CTA | 6% dom + excise + regional levies | 10%/22% + oneri |
| Fuel bundling | dual-fuel single account norm | separate but bundle-marketed | same | separate contracts common | **strictly separate contracts per fuel** | separate |
| Structure | one national regulator | national rules + state schemes | state regulator | national | **3 regional regulators + federal accord** | national |

Two structural differences matter more than any parameter: **(a) read ownership** — in FR/BE/IT the DSO is the metering data source of truth and the supplier *receives* indexes through market flows, so estimation failure is partly a third-party failure with its own liability seams (the FR LRAR duty sits on the DSO, and IT's prescription binds the distributor too); the walled-interface adapter for "meter reads" must therefore model *whose* failure a missing read is. **(b) Regional fragmentation inside one country** (Belgium, Australian states) — the rule-pack unit is not "country", it's "jurisdiction", and one customer book can span several.

---

## 3. Gap read against the current SIM

What already exists (verified against live ASSUMPTIONS.md / LATEST.md, 2026-07-12): 12-month forced catch-up read cap; A/E-marked reads on bills; estimated-vs-actual physics with per-meter-type cadence; SLC14 DD refund events; pre-bill validation gate + domain invariants + population sanity; obligations register incl. back-billing; complaints with 56-day Ombudsman window; PSR register (company-side only, no SIM feed); cooling-off; VAT by segment; price cap; GSOP registered as obligation.

What the rulebooks say happens in reality but never happens in the SIM (the long list, condensed): back-billing **write-offs** as a P&L event; customer-fault attribution and its evidence trail; theft/tampering and its detection economics; access-refusal loops; erroneous transfers; crossed meters; faulty-meter rebills; deemed contracts; change of tenancy/move-in-move-out; final-bill deadline breaches and GSOP auto-payments; ombudsman case fees; prepayment mode incl. self-disconnection; debt-blocking of switches; repayment plans and Fuel Direct; disconnection state machine with vulnerability/winter guards; SIM-side vulnerability self-declaration; estimated-bill disputes with self-read replacement bills; pro-rata rebilling across price changes; billing-block/maxi-bill defect class; calendar-windowed protections.

---

## 4. Top 20 most useful SIM additions (director's requested list, ranked)

Ranked by (fidelity value x how much existing regulation says the phenomenon is common) x (how much of the Epoch-2 Value Cycle it exercises). Items 1–8 are the core; each names the rule that proves the phenomenon is real.

1. **Back-billing write-off physics.** When a catch-up bill spans more than the recoverable window, the excess becomes a supplier **loss** (write-off ledger event), not revenue. Today the SIM caps consecutive estimates but never books the cost of failing. This makes estimation quality a P&L lever — the exact incentive 21BA was designed to create. *(SLC 21BA)*
2. **Customer-fault attribution on every under-billing event.** A hidden SIM-side flag (obstruction / tampering / access refusal / none) + a company-side *claimed* attribution that must be evidenced — because fault is what pierces the cap in every market. Mis-attribution should be punishable (ombudsman loss). *(21BA exceptions; NERR r30(2)(a); L224-11 exceptions)*
3. **Energy theft & meter tampering.** Hidden per-customer theft propensity (small, segment-skewed); understated consumption at the meter; a detection process with lead-scoring (TRAS-analogue), investigation cost per lead, hit-rate, recovered revenue, and an unrecovered-losses line socialised into costs. ~£500m/yr industry-wide says this is material. *(SLC 12A, TRAS/TDIS)*
4. **Meter-access refusal loop with an evidence trail.** Appointment → failed visit → letters → (registered-letter escalation) → warrant/forced-read tail. The *evidence artefacts* (dated letters, visit logs) are what later preserve recovery rights — the French LRAR case law shows a defective letter forfeits the money. This is unhappy-path physics AND a document-trail capability in one.
5. **Faulty/stopped/drifting meter class + dispute-triggered meter test.** Meter error is the third great source of wrong bills after estimation and tariff error. Customer-requested test, customer pays if meter is fine (NERR pattern), rebill on proven fault — with the rebill obeying rule 18 below.
6. **Change of tenancy / move-in-move-out + deemed contracts.** Occupier churn at a fixed meter point, opening/closing reads (often estimated → disputes), deemed-rate supply until contract signed. This is the single most common real-world account event the SIM lacks entirely, and it stresses meter→cash end to end. *(UK deemed contract regime; BE/FR move-out final-bill deadlines)*
7. **Final-bill discipline + GSOP-style auto-compensation ledger.** Statutory deadline (6 weeks UK / 4 weeks Flanders) on closure/switch final bills; breach fires an automatic compensation payment event. Generalises to missed appointments and delayed refunds. Compensation as *automatic physics*, not complaint outcome. *(GSOP; BE regional deadlines)*
8. **Ombudsman escalation economics.** Deadlock/8-week complaints escalate; each case carries a **per-case fee to the supplier** plus a probability of directed remedy + goodwill. Converts service failure into a concrete unit cost the company can manage against. *(Energy Ombudsman model; médiateur; EWON)*
9. **Prepayment meter mode.** PPM tariff class, top-up behaviour, **self-disconnection events** (the invisible disconnection regulators care about most), standing-charge debt accruing while off-supply, restrictions on involuntary PPM installs for vulnerable customers.
10. **Disconnection-for-debt state machine with guards.** The full ladder (reminder → notice → plan offer → disconnection as last resort) with **calendar guards** (winter bans), **register guards** (vulnerability/life-support), and a wrongful-disconnection compensation event when the machine is run wrong. *(trêve hivernale; NERR life support; VIC payments; BXL court gate)*
11. **SIM-side vulnerability self-declaration events** feeding the (currently orphaned) PSR/vulnerability register — with imperfect disclosure (many vulnerable customers never register: a measurement-gap twin of the satisfaction wall-chart).
12. **Debt-conditional switching (objection) rules.** Supplier may block a switch for debt in defined cases (UK PPM debt assignment) and must not otherwise — couples collections to churn physics.
13. **Repayment plans with ability-to-pay + Fuel Direct analogue.** Plan set-up, adherence/breakage distributions, re-plan cycles — the dominant real collections path (75% of UK arrears sit on *no* plan: that statistic is itself an anchor for plan-uptake physics).
14. **Estimated-bill dispute + self-read replacement bill.** Customer submits a (photo) read; the company must validate (register order, rollover, plausibility) and issue a corrected bill promptly. *(NERR r21 family; UK practice)*
15. **Erroneous transfers.** Wrong-MPAN switches with prescribed unwind, customer held harmless, inter-supplier reconciliation — a switching unhappy path with a real industry-process shape.
16. **Crossed meters.** Two premises billed on each other's meters for years, discovered late; rebill both sides under back-billing constraints. A classic ombudsman staple that exercises identity, metering and rebilling simultaneously.
17. **Billing-block defect class + maxi-bill events.** A systemic "bills stopped issuing for cohort X" defect (the Italian *blocco di fatturazione* is regulated by name) — with the prescription clock running from when bills *should* have issued. Tests the bill-ageing watchdog (supplier feature #1).
18. **Pro-rata rebilling across price periods.** Any catch-up consumption spanning tariff changes must be allocated across the price periods it spans, never billed wholly at the latest price. *(French médiateur lissage rule — encode as a domain invariant.)*
19. **Calendar-windowed compliance physics.** Rules that are only true between dates (winter disconnection bans, seasonal cap resets) — a small generic mechanism (date-windowed obligations in the register) with several consumers.
20. **Interest-and-fees rules on arrears/back-bills as jurisdiction parameters.** No interest on back-billed amounts (AU), capped recovery fees (Wallonia €55/energy/yr), prescribed dunning ladders — collections revenue/cost realism and a portability lens in one.

---

## 5. Top 10 supplier/software features — "excellent billing" (build for UK now; all generalise)

1. **Unbilled-energy watchdog ("bill ageing").** Every account carries *days-since-last-accurate-bill*; alerting thresholds well inside the recoverable window; an unbilled-revenue provision on the balance sheet that grows (and impairs) as accounts age. The single highest-value control: it converts every back-billing rule into a managed metric.
2. **Recoverability engine.** Any catch-up bill is auto-split into recoverable vs write-off tranches per the active rule-set + fault attribution, before issue — the write-off is booked, not discovered in dispute.
3. **Evidence ledger for fault attribution.** First-class, timestamped record of access attempts, letters (and their *content* sufficiency), read requests, customer responses — the artefact that wins or loses the ombudsman case and the 14-month exception.
4. **Catch-up bill UX to the NERR r30 standard:** separate line item, plain-language explanation of why, and an auto-generated matched-period instalment offer in the same artefact. Adopt the strictest market's transparency as the house norm.
5. **Bitemporal, proration-correct rebilling engine.** Rebill any historical window across tariff versions, VAT-rate boundaries and price changes, reconstructible "as known at" any date — the regulatory case for the Epoch-2 bitemporal architecture, stated as a product feature.
6. **Estimation quality control.** Every estimate confidence-scored against the account's own history + weather; a gross-inaccuracy gate before issue (extends the existing pre-bill validation gate); estimate-vs-actual error tracked as a published KPI.
7. **Self-read intake pipeline.** Validated customer reads (register order, rollover, plausibility, photo evidence) triggering prompt replacement bills — the cheapest estimation-failure recovery there is.
8. **Theft/anomaly analytics.** Consumption-vs-archetype divergence scoring with an investigation queue managed on expected-value (lead score x recoverable x cost) — the company-side twin of SIM addition #3.
9. **Auto-compensation engine.** GSOP-class payments fired automatically from the event stream (missed appointment event → payment event), never waiting for a complaint. Cheap, and a genuine differentiator vs incumbents who pay only when chased.
10. **Statutory-clock service.** Every account carries its live regulatory clocks (back-billing window remaining, final-bill deadline, refund deadline, complaint SLA, prescription dates) as first-class objects with breach *prediction* — the compliance function moves from sampling to foresight.

---

## 6. Top 10 billing features to operate globally (portability-lens register — **no multi-market build until post-Epoch-3**)

1. **Jurisdiction rule-packs as declarative config.** Recoverability window, clock anchor, fault exceptions, interest prohibition, instalment mandate, disclosure duties — one mechanism, per-jurisdiction parameters (12m/9m/4m/14m/2y are the proof it's one mechanism). The rule-pack unit is *jurisdiction*, not country (Belgian regions, Australian states).
2. **Multi-rate, line-level tax engine** with rate history: split VAT within one bill (FR 5.5/20), segment-based VAT (UK 5/20 + CCL), flat GST (AU), reduced-rate + excise + regional levies (BE), and rebilling through past rate changes.
3. **Bitemporal billing ledger** (as §5.5) — the only architecture that satisfies rectification, prescription and dispute rules in *every* market simultaneously; a one-market shortcut here is the single most expensive thing to retrofit.
4. **Meter-read provenance model:** actual/estimated/self/remote **plus whose read it is** (DSO vs supplier vs customer) and whose failure a missing read is — because read ownership is the deepest structural difference between UK-style and continental markets, and it determines liability under the fault exceptions.
5. **Market-message adapter layer:** billing consumes typed interface events (UK MHHS/DTC, AU B2B/MSATS, FR GRD flows, BE MIG) — the wall IS the go-live seam, and the billing engine must already read the world only through it (Law #2 restated as a billing requirement).
6. **Instalment/budget-billing framework as one primitive** with per-market governance: UK DD smoothing + SLC14 refunds, AU bill smoothing with explicit informed consent + 12-month true-up, FR/BE mensualisation + annual regularisation with refund deadlines (>€25/15 days; 30 days Wallonia).
7. **Statutory-clock engine as config** (§5.10 generalised), including clocks that start from *regulated* deadlines rather than actual events (Italy's prescription-from-when-the-bill-should-have-issued).
8. **Collections/disconnection state machine with pluggable guards:** calendar windows, court-order gates, register checks, budget-meter/social-supplier handoff, wrongful-action compensation — same machine, different guard set per jurisdiction.
9. **Prescribed-amount disclosure & waiver workflow.** Italy's separate-line + opt-out-form regime is the extreme case; generalise as "amounts the customer may lawfully refuse, disclosed as such" — a transparency capability that also satisfies the softer UK/AU explanation duties.
10. **Consumption schema that is register-plural, unit-plural and contract-plural:** ToU-ready registers (already Defect-3'd), per-market gas conversion conventions (m³→kWh coefficients differ), and dual-fuel-single-bill vs strictly-separate-contract-per-fuel (Belgium) as a configuration, not an assumption baked into account identity.

---

## 7. Method note and what this document is NOT

- This is a **research + prioritisation artefact**: it registers problems, phenomena and requirements. It deliberately prescribes no module names, schedules or mechanisms beyond naming the regulatory fact each item answers to. Sequencing is the director's next re-rank; the natural entry points are the Epoch-2 D-lane (items §4.1–8 are largely its charter stated with sharper anchors) and the obligations-register/invariants library (items 18–20 are directly encodable as invariants).
- Per the portability constraint: §6 is a **design-constraints register only**. The only actions it implies *now* are negative ones — don't bake single-market assumptions (single VAT rate per bill, supplier-owned reads, dual-fuel-single-account identity, country-level rule granularity) into Epoch-2 foundations.
- Anchors flagged `[M]`/`[L]` must be re-verified by a discovery pass before being encoded as invariants; `[H]` items were fetched from primary or near-primary sources on 2026-07-12.

## 8. Sources (fetched 2026-07-12 unless noted)
- Ofgem: SLC 21BA decision + press release (May 2018 in force); Ofgem open letter on charge recovery expectations (2020); Ombudsman back-billing stance; Ofgem electricity-theft decision (2014) + open letter on theft obligations (2023); TRAS/TDIS/ETTOS via REC Schedule 7 materials and ElectraLink descriptions.
- AEMC: NERR Rule 30 (undercharging), Rule 21 (estimation), Rule 24 (100-day frequency), Rule 23 (bill smoothing/EIC) — energy-rules.aemc.gov.au; EWON back-billing guidance; ESC Victoria 4-month limit (Energy Retail Code of Practice, from 1 Jan 2021, via secondary confirmation).
- France: Code de la consommation Art. L224-11 (Légifrance) + Assemblée nationale QE 25398 (penalty regime); médiateur national de l'énergie case notes (LRAR sufficiency; lissage prorata temporis); L218-2 two-year prescription; trêve hivernale (secondary).
- Belgium: CWaPE (60-day settlement, 30-day refund, dunning ladder, €55 fee cap); Belgian federal energy Ombudsman (12-month accord rectification, regional final-bill deadlines: Flanders 4 weeks, Brussels/Wallonia 6 weeks on switch); FdSS prescription note (Brussels 2y index / 5y bad faith); SPF Economie consumer-accord references.
- Italy: ARERA press releases + delibere 97/2018, 569/2018, 184/2020 (2-year prescription, "in ogni caso" from 1 Jan 2020, disclosure + opt-out form duties); Budget Laws 2018/2020.
- EU: Directive (EU) 2019/944 Annex I + Arts. 10/18 (consolidated, incl. 2024/1711 amendments): billing frequency, three-component price breakdown (Reg 2016/1952), fuel-mix disclosure, historical-consumption rights, 24-hour switching by 2026, pre-disconnection information duties, supplier hedging supervision.
