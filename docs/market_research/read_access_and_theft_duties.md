# Read access and theft duties in GB domestic supply

**Knowledge:** read-access-and-theft-duties

**Asked by** the director, 2026-10-06: read access and theft duties "deserve proper knowledge work,
not a re-check of a toggle value. Treat them like the step-1 areas: sources, what's established,
what isn't, written up as knowledge. Then set the toggles from what you find." The work builds on
`unbilled_energy_and_revenue_assurance.md` (kinds K2, K3, K4) and the Q2 section of
`practitioner_questions_as_assumption_toggles.md`. It does not repeat them. Researched 2026-10-06.
This is knowledge work only. The register `assumption_toggles.yaml` is the one file it edits.

**How figures are marked.** **[H]** means read this session in the primary text named: the statute
on legislation.gov.uk, the licence PDF, or the Ofgem, RECCo or AUGE document, downloaded and
read as text. **[M]** means from a search snippet or a secondary source, not read in the primary.
**[derived]** means arithmetic shown here, with what each number counts. **GAP** means searched
for and not found, so no number is given. No web summariser was used for any figure. Every
document was fetched and grepped as text, because a summariser invented figures the day before.

**Two premises in the brief turned out to be wrong, and both change the frame:**
1. "The licence requires an inspection, or a read, every two years": **the two-yearly inspection
   duty was repealed on 1 April 2016**, in both fuels (Ofgem decision, 4 February 2016) [H]. For
   the whole of our window the read duty is SLC 21B.4: take all reasonable steps to get a read
   **once a year**.
2. "`MAX_CONSECUTIVE_ESTIMATED_PERIODS`, the 1-in-6 monthly read rate": **both were gone from
   `simulation/meter_reads.py` before this pass.** W2_36 slice 2 (`977e17453`) replaced them with
   the two-class process calibrated to the register's Q2 rows (§5).

---

## 1. Definitions

Each of these is a different thing, measured and acted on differently.

- **Read duty.** The supplier's licence duty of *effort* to get a meter reading: SLC 21B.4 in
  both fuels. It is not a guarantee of a read, and it is not a duty to visit.
- **Inspection duty.** A licence duty to physically inspect a meter at a fixed interval (safety,
  tamper, register). Repealed in 2016 (§2.1). What remains is health-and-safety law and
  risk-based practice.
- **Right of entry.** The supplier's statutory *power* to enter premises at reasonable times to
  read, inspect or change a meter. Its counterpart is not a positive duty on the customer. The
  power cannot be exercised against the occupier's will without a magistrate's warrant (§2.2).
- **Access failure.** A visit that does not produce a read. The causes are different events:
  - nobody home;
  - the occupier refuses;
  - the meter is inaccessible (a locked cupboard, the landlord holds the key);
  - the meter is unreadable or faulty.

  Only a **refusal after reasonable requests** is "obstructive" in the 21BA sense (§2.4). A
  failed visit is not.
- **Persistent non-read.** A meter that stays unread across many cycles. This is a state of a
  household or premises, not one failed visit. It is what makes back-bills long (Q2).
- **Theft of electricity or gas.** The licence definitions (SLC 12A.16 electricity, 12A.17 gas)
  borrow the statutory offences:
  - restoring a supply without consent;
  - damaging plant;
  - altering a meter's register, or preventing it from registering.

  The criminal offence of *abstracting* electricity is Theft Act 1968 s.13 (up to five years) [H].
- **Detected, confirmed, assessed.**
  - A *lead* (TRAS score, tip-off, supplier analytics, field agent) becomes an *investigation*.
  - An investigation ends confirmed, unproven, no theft, or no longer supplied.
  - A confirmed case has an *assessed* volume (REC Theft Calculator).
  - The assessed volume may be entered into settlement and billed to the customer.

  Each stage is counted separately in the published data. Do not divide one stage by another
  without saying which.
- **Who pays.** Two different routes, and they must not be merged:
  - **Undetected theft** is never metered. So it never lands on the thief's supplier's settled
    volume. It is **smeared across all suppliers by market share**: GSP Group Correction in
    electricity, Unidentified Gas (UIG) in gas.
  - **Detected theft**, once assessed, can be entered into settlement against the thief's
    supplier, which then tries to recover it from the thief.

## 2. Read access

### 2.1 The supplier's duties to read and to inspect

- **SLC 21B.4 (both fuels):** "take all reasonable steps to obtain a meter reading (including any
  meter reading transmitted electronically from a meter to the licensee or provided by the
  Customer and accepted by the licensee) for each of its Customers at least once every year". It
  does not apply to prepayment meters. It took effect on 31 December 2014 (21B.3). [H] Electricity
  supply SLCs, consolidated to 1 August 2025, p.167. Gas supply SLCs, consolidated to 1 April 2024,
  21B.4(a).
  - **The duty counts a customer's own read and a smart meter's transmitted read.** It is a duty
    to *obtain* a read, not to *visit*.
- **SLC 21B.5:** make a bill or statement available at least twice a year. This does not apply
  to prepayment, smart, or unmetered supply. **21B.5A:** a customer whose meter can be read
  remotely may ask for monthly billing information. [H] same.
- **The two-yearly inspection duty was repealed from 1 April 2016.** Ofgem decided on 4 February
  2016 to modify:
  - electricity SLC 12 (it repealed 12.14 to 12.16);
  - gas SLC 12 (it repealed 12.8 to 12.16) and gas SLC 17;
  - the gas transporter conditions.

  Ofgem's stated reason: "licence conditions 21B.4 and 21B.5 meet the objectives of billing
  accuracy in a more effective and efficient way than a static meter inspection interval".
  Suppliers "should be able to satisfy themselves of their existing obligations under health and
  safety legislation, which could include a risk-based approach". [H] Ofgem, *Decision on reforming
  suppliers' meter inspection obligations*, letter of 4 Feb 2016, pp.1–4. The consolidated SLCs
  read this pass show 12.14–12.16 (electricity) and 12.8–12.16 (gas) as "Not Used" [H].
  - Before the repeal, British Gas ran under a consent: risk-based inspection with a five-year
    backstop, plus minimum theft-detection obligations [H] (Ofgem July 2015 consultation §1.86–1.87,
    1.119).
- **A second read incentive sits in settlement, not the licence.** The BSC (Section S Annex S-1)
  "requires that at least 97% of non-half hourly electricity is settled on the basis of actual
  metered data by the time of Elexon's final volume allocation run (i.e. within 14 months)". A
  supplier that misses it pays performance charges. [H for Ofgem's statement] Ofgem, *Reforming
  suppliers' meter inspection obligations*, consultation, 23 July 2015, §1.116. The BSC annex
  itself was not read [M].
  - This is the same 97%-at-RF figure the Q2 calibration already uses (Elexon timetable). It is
    an *obligation level*, not only an observed rate.
- **Gas settlement before and after Nexus.** Before June 2017, a small site's AQ could change only
  once a year and small sites were not individually reconciled. UNC432 (Project Nexus) brought
  rolling AQ and individual reconciliation. [H] same consultation, §1.117–1.118. Since Nexus a gas
  read feeds settlement directly, which strengthens the read incentive in gas from mid-2017.
- **What site reads cost.** Meter operators told DECC that:
  - a routine inspection costs **£3 per meter** on an area-based round;
  - a scheduled-appointment visit to a high-risk meter costs **£17.50 per site**;
  - suppliers then "read traditional meters through a successful site visit every 6 months".

  [H] the 2015 consultation §1.152, 1.170–1.172, citing DECC's smart metering impact assessment
  (not read). These are pre-2015 figures. The "every 6 months" is the suppliers' own description of
  practice, not a measured rate.

### 2.2 The customer's side: a power of entry, not a duty to give access

- **Electricity.** "Any officer or other person authorised by an electricity supplier may at all
  reasonable times enter any premises to which electricity is being supplied by him for the
  purpose of (a) ascertaining the register of any electricity meter … (b) removing, inspecting or
  re-installing any electricity meter". Removing or installing a meter needs **two working days'
  notice**. [H] Electricity Act 1989 Sch 6 para 7(2) and 7(5).
- **Gas.** An officer authorised by a gas supplier or shipper "may at all reasonable times … enter
  a consumer's premises for the purpose of (a) inspecting gas fittings; (b) ascertaining the
  quantity of gas" [H]. Gas Act 1986 Sch 2B para 23(2).
- **Obstruction offences.** "A person who intentionally obstructs a person exercising powers of
  entry conferred by this Schedule shall be liable … to a fine not exceeding level 3" [H].
  Electricity Act Sch 6 para 10(6); Gas Act Sch 2B para 28(4).
- **But no entry without consent or a warrant.** "No right of entry to which this Act applies
  shall be exercisable … except (a) with consent given by or on behalf of the occupier … or (b)
  under the authority of a warrant", except in an emergency. "No person shall be liable to a
  penalty … by reason only of his refusing admission to a person who seeks to exercise the right
  of entry without a warrant." [H] Rights of Entry (Gas and Electricity Boards) Act 1954 s.1(1)
  and 1(3), applied by Electricity Act Sch 6 para 10(1).
  - **So refusing a meter reader is lawful. Only obstructing a warranted entry is an offence.**
- **The warrant.** A justice may grant one on sworn information that:
  - admission is "reasonably required";
  - the operator would otherwise be entitled to enter;
  - the relevant enactment's requirements are met.

  Where the enactment sets no notice of its own, the warrant needs admission sought after at least
  **24 hours' notice**, or an emergency refusal, or unoccupied premises, or a case where asking
  would defeat the purpose. [H] 1954 Act s.2(1)–(2).
- **Warrant practice, current directions.** Applications are listed by purpose, as separate CSV
  files:
  - installation of prepayment meters;
  - commercial disconnection;
  - safety, theft and tamper;
  - any other purpose.

  Notice to the occupier is **15 business days** before the hearing for debt cases and **10** for
  safety, theft or tamper. "For theft, safety and tamper, there may properly have been none"
  contact attempts. [H] Senior Presiding Judge and Chief Magistrate, *Directions: warrants for
  pre-payment meters*, revised September 2024 / 2025.
- **Contract terms.** Suppliers' terms conventionally require the customer to allow access and to
  give reads. [M, no supplier's terms read this pass.] Ofgem is explicit that **not providing a
  read is not obstruction** (§2.4).

### 2.3 Smart meters and remote reads

- A transmitted read satisfies 21B.4 (§2.1). By the end of 2024:
  - about **10% of installed smart meters were not in smart mode**;
  - in traditional mode were **4.7% of all domestic electricity meters and 9.1% of gas**;
  - small suppliers ran 86% smart mode, large suppliers 90%.

  [H] DESNZ Q4 2024, read in `meter_read_latency_estimation_2026.md`.
- **Smart-mode performance is partly a supplier trait.** Ofgem publishes smart mode by supplier.
  At 31 Dec 2024: E 98.0%, E.ON 93.3%, OVO 94.1%, EDF 89.2%, ScottishPower 86.3%, British Gas
  85.1%. By 30 June 2026, British Gas had reached 91.7%. [H] Ofgem, *Smart meter performance*
  page. **So the read-exposed share of a smart book ranges about 2% to 15% by supplier** [derived,
  1 − smart-mode share].
- **From 2026** (after our window), suppliers must fix a faulty smart meter within **90 days** of
  being told. DESNZ says "92% of smart meters work as they should". [H] DESNZ press release, 10
  March 2026. Within our window the duty was "all reasonable steps" with no time limit.
- **GAP:** the hazard of a working smart meter dropping out of smart mode, and how long it stays
  out. DESNZ and Ofgem publish stocks, not transitions.

### 2.4 When access is refused or fails, and how that meets back-billing

- **The 12-month limit and its exception.** SLC 21BA.1 limits any "charge recovery action" to
  units "consumed within the 12 months preceding" it. Under 21BA.2(c) it does not apply where "the
  licensee has been unable to take a charge recovery action for the correct amount … due to
  obstructive or manifestly unreasonable behaviour of the Domestic Customer". [H] Electricity SLCs
  p.169. The gas text is the same.
- **What Ofgem said counts as obstruction.** [H] Ofgem decision, 5 March 2018, pp.9–10:
  - "consumers are likely to fall within this exception if the supplier identifies a problem,
    makes reasonable requests to physically access the meter, and consumers ignore or refuse
    them";
  - its examples are "stealing electricity or gas" and "prevents physical access to the meter
    (for example by not allowing a meter reader into the home without good reason)";
  - "We do not consider a consumer to be obstructive or manifestly unreasonable when he or she
    does not supply a meter reading";
  - "If consumers do not respond to requests for meter readings, the backstop measure should be
    that suppliers take a meter reading themselves";
  - suppliers must "keep evidence of the consumer's behaviour".
- **So the exception is earned by the supplier's own documented access attempts.** A supplier
  that never asked for access cannot use it, whatever the household did.
- **Cases suppliers raised that Ofgem did not resolve one by one:**
  - a meter behind a locked cupboard, with the landlord holding the key;
  - a fault lying with a third party;
  - a genuine misread in a bank of meters.

  [H] p.8. Ofgem's answer was the general principle of "case-by-case" assessment.
- **Theft is obstruction for 21BA.** Theft charges are not capped at 12 months. No licence cap
  replaces the 12-month one; the theft rules require evidence instead (SLC 12A.11(g), §3.1). The
  modules that type a "3-year theft back-bill" (§5) have **no source**. A general limitation
  period applies [M, Limitation Act not read].

### 2.5 Published rates

| Quantity | Value | Grade |
|---|---|---|
| Domestic consumers with no bill on a read in 12 months (H1 2017) | "just over 7%" | [H] Ofgem 16 Nov 2017 ¶1.1 (in Q2) |
| Median supplier with a read-based bill in the year (Q1/Q2 2017) | 94.8% / 94.4% | [H] Ofgem 5 Mar 2018 p.10 |
| NHH energy settled on actuals at R1/R2/R3/RF | 30/60/80/97% | [H] Elexon (in Q2) |
| BSC performance standard at RF | ≥97% | [H via Ofgem 2015 §1.116] |
| Complaint back-bills: median length | 24 months (n = 203) | [H] Ofgem 2017 (in Q2) |
| Share of suspected **gas** theft found by meter inspections | <4%; 85% from tip-offs and suppliers' own analysis | [H] Ofgem 2015 §1.93, from SPAA theft reporting |
| British Gas: share of theft leads from inspection visits | ~5% | [H] Ofgem 2015 §1.86 |
| Smart meters not in smart mode, by large supplier, Dec 2024 | 2.0%–14.9% | [H] Ofgem smart meter performance |
| **Access failure per read visit** | **GAP** | No source found |
| **Share of 12-month non-reads caused by refusal, against no-one-home, against an inaccessible meter** | **GAP** | Practitioner |
| **Warrants sought for meter reading or inspection** (not PPM) | **GAP** | The court directions list the category; no counts are published |
| Prepayment meters fitted under warrant, 2022 | 94,201 | [H] gov.uk, DESNZ data, Feb 2023. A debt measure, not a read-access one |

**Where warrants actually concentrate.** Published warrant counts are for **prepayment
installation on debt**: 94,201 in 2022, 70% of them by three suppliers [H].
- Magistrates' listing of PPM warrants was suspended on **6 February 2023** [H].
- Ofgem's strengthened rules took effect in **November 2023**. The first suppliers restarted
  involuntary PPM in **January 2024** [H] (Ofgem, *Market compliance review: prepayment meter
  installations*, 3 June 2026).
- The review found "no widespread instances of inappropriate PPM installations". Suppliers paid
  £7m in compensation, wrote off £13m and gave £55m in support [H] same.
- **Read access is not, in practice, a warrant activity.** Neither the 2018 decision nor the
  court directions treat a warrant as the normal remedy for an unread meter [H, by absence in both
  texts]. The remedy Ofgem names is the supplier's own read attempt (§2.4).

## 3. Theft

### 3.1 The duties

- **SLC 12.1 (electricity):** take all reasonable steps "to detect and prevent (a) the theft or
  abstraction of electricity … (b) damage to … Metering Equipment … (c) interference with any
  Metering Equipment" [H].
- **SLC 12A (electricity and gas), the theft condition.** In force since **January 2013 for gas
  and July 2014 for electricity** [H] (Ofgem 2015 §1.79). [H] electricity SLC 12A.1–12A.16; gas
  12A.1–12A.17.
  - The objective covers detecting, investigating and preventing theft, including by "deterrence
    and the security of the supply" (12A.1(a)).
  - It requires conduct that is "fair, transparent, not misleading, appropriate and
    professional" (12A.1(b)).
  - 12A.5: "all reasonable steps to detect and prevent". 12A.6: investigate where there are
    "reasonable grounds to suspect".
  - 12A.7: be party to the Authority-directed **Theft Arrangement**, which is now **REC
    Schedule 7, Energy Theft Reduction**.
  - 12A.3 also brings in DCUSA Clause 30.9 (Damage or Interference), a notification duty. **GAP:**
    its deadline was not read.
- **Investigation standards, SLC 12A.11.** All of these are [H]:
  - (a) identify whether the occupants are of pensionable age, disabled or chronically sick, or
    will have difficulty paying the theft charges;
  - (b) take ability to pay into account when setting instalments, including all the charges
    collected through a prepayment meter;
  - (c) offer a prepayment meter before disconnecting such a household, where safe and
    practicable;
  - (d) take all reasonable steps not to disconnect pensionable, disabled or chronically sick
    occupants **in winter**;
  - (e) evidence the statutory disconnection power **on the balance of probabilities**;
  - (f) comply with DCUSA and the BSC for the theft;
  - (g) evidence, on the balance of probabilities, that the theft was this customer's
    "intentional act or … culpable negligence" **before requiring payment**;
  - (h) explain in plain language the basis of the assessment, the charge, how to dispute it and
    how to restore supply.
- **REC Schedule 7.** All of these are [H] REC v1.1 Energy Theft Reduction Schedule, effective 15
  January 2021:
  - the **TRAS** (a cross-industry risk-scoring service);
  - the **Energy Theft Tip-Off Service (ETTOS)**: the registered supplier must read a tip-off
    within **10 working days** and investigate it under the Revenue Protection Code of Practice
    (8.4);
  - a **Theft Target Methodology** whose targets must "result in a net benefit to Consumers as
    compared to taking no action" (7.6);
  - a **Theft Detection Incentive Scheme (TDIS)**: per-supplier targets by market share, and a
    "Theft Detection Value" for each detection, "based on the likely net cost to an Energy
    Supplier of having undertaken activity to detect the theft" (Annex 3 §4.1).

  TDIS replaced the electricity scheme under DCUSA and the gas scheme under SPAA, from April 2022.
  The TRAS contract was first awarded to Experian, and suppliers were directed to set it up by
  February 2016 [H] (Ofgem 2015 §1.82).
- **Why the incentive exists: detection costs a supplier money.** Ofgem's 2014 package targeted
  "the financial disincentive that suppliers face to expend resources consistently to detect and
  investigate" [H] (Ofgem 2015 §1.81). The mechanism, from the 2014 IA [H]:
  - a supplier that detects theft must enter the stolen units into settlement and pay for them;
  - it recovers only part from the thief;
  - an undetected theft costs it only its market-share slice of the smear: "group correction
    smearing in settlement is distributed according to market share" (§2.19).
- **R0173 (approved 22 May 2025)** adds TDIS payments for desktop investigations and site visits,
  whatever their outcome. It also requires the outcome of every ETTOS lead to be fed back. [H]
  Ofgem decision on R0173.

### 3.2 How theft is detected

- **Lead sources.** [H] Ofgem 2015 §1.93 (SPAA theft reporting):
  - tip-offs and suppliers' own analysis gave **85%** of suspected gas theft incidents;
  - meter inspections gave **under 4%**.

  British Gas's inspection visits gave ~5% of its theft leads [H] §1.86.
- **Hit rate per investigation.**
  - **TRAS, 2014 to March 2021, ~300,000 investigations:** 23% confirmed, 50% no theft, 10%
    unproven, 16% still under investigation. [H] RECCo/Capgemini *Theft Estimation Methodology*
    (TEM), 2023, §3.1.
  - **Reliable-supplier subset:** 24% confirmed. Proactive investigations convert at **15%** and
    reactive ones at **42%**. Residential converts at 25%, commercial at 12%. [H] TEM, H5
    findings.
  - **ETTOS leads (2024):** "only 37% of ETTOs leads were investigated, with a conversion rate of
    22% to confirmed thefts". [H] Ofgem R0173 decision.
  - **2011 (Ofgem questionnaire), electricity domestic:** 41,670 investigations and 15,956
    detections, so **38%** [derived, detections over investigations, both counts of domestic
    electricity cases a year]. [H] Ofgem 2014 IA Table 4.
- **Bias towards prepayment.** Of TRAS investigations with a recorded payment method, **66% were
  prepayment**. Confirmed rates by method: prepayment device 18%, PAYG 34%, standing order 20%,
  cash or card 22%, fixed DD 12%, variable DD 6%. Key meters with no recorded method: 40% confirmed
  (~18k cases). [H] TEM Table 6.
  - The company should read these as rates **among investigated** households. They are not theft
    rates by payment method.
- **Duration.** Detected thefts last on average "just under 2 years". Spikes at 90/180 days
  (cannabis cycles), at quarterly reads, and at 365/730 days (suppliers' 1- or 2-year cut-offs in
  recording) [H] TEM §3.1. Ofgem's 2014 model used 12/24/36 months before detection
  (low/medium/high) [H] IA Table 5.
- **Smart meters.** Smart tamper alerts and granular data were expected to make detection easier
  [H] Ofgem 2015 §2.4, 4.13. The TEM listed "theft can occur equally in properties with or without
  smart meters" as a hypothesis and did not test it [H]. **GAP:** no published detection rate by
  meter type.

### 3.3 Who pays for stolen energy

- **Undetected electricity theft** is in no supplier's metered volume. It surfaces in the GSP
  group's difference between energy entering the group and deemed consumption, and is **smeared
  by GSP Group Correction across suppliers** in proportion to market share [H, Ofgem 2014 IA
  §2.19]. Elexon describes line losses as including "non-technical losses (e.g. theft)" [M, in the
  unbilled doc]. **GAP:** the size of the GSP correction factor in our window.
- **Undetected gas theft** is a component of **UIG**. UIG is allocated daily to shippers by
  AUGE weighting factors.
  - For gas year 2024-25 the AUGE put theft at **6,362 GWh of 7,761 GWh** of identified UIG [H].
  - **That theft figure is an assumption, not a measurement.** "Several assumptions feed the
    current total gas theft estimate of 1.48% of total consumption … driven largely by the views
    of electricity theft" studies at 1–2.5% of throughput [H] AUG Statement 2024-25 pp.29–30.
  - **Actual final UIG** was 3.81% (GY17/18), 2.19%, 2.69%, 2.90% and 2.50% (GY21/22) of
    throughput, "around 2.5% … since Nexus go-live". It "continues to move for four years" [H]
    p.27.
  - Throughput implied: 12.5 TWh is 2.50%, so about **500 TWh** a year [derived from the AUG
    table's own pair].
- **Detected theft** is entered into settlement by the supplier and billed to the thief, with 12A
  safeguards. Ofgem's 2014 model assumed:
  - **50–100%** of stolen units are assessed for settlement;
  - **24–48 months** of legal consumption follow detection;
  - an average **recovery rate of 20–30%** for domestic cases.

  [H] IA Table 5. A detecting supplier's net cost per domestic case is £100–300 of its own costs
  plus £200–400 for the investigation, before settlement charges [H] same table.
- **So for a supplier's prices, theft arrives through the smear.** The smear is a market-wide
  rate × the supplier's share, and it does not depend on how much theft is in its own book. Its
  **own** book's theft matters only to the **detection decision**:
  - what detection gains: recovery, future billed consumption, and TDIS payments;
  - what detection costs: investigation costs and the settlement charge for the entered units.

  [derived from the two routes above]

### 3.4 Scale

| Quantity | Value | Source |
|---|---|---|
| Electricity theft, GB, a year | 1,703–2,837 GWh; "0.5–0.9%" of 2019 UK generation | [H] TEM (2023) |
| Gas theft, GB, a year | 636–1,059 GWh; "0.1%" of 859.8 TWh 2019 demand | [H] TEM |
| Gas theft, AUGE assumption | 6,362 GWh (GY24-25); 1.48% of consumption | [H] AUG Statement |
| £ a year (Dec 2022 cap prices) | £737m–£1,233m electricity, £93m–£155m gas; "£29 to £48" a household | [H] TEM |
| £ a year (Ofgem 2025) | "£830 million to £1.388 billion" | [H] Ofgem R0173 |
| £ a year (RECCo 2026) | "£0.9–£1.4 billion" | [H] RECCo Energy Theft Business Case 2026-27 |
| Domestic electricity theft cases at any time (2014) | 275,000, "approximately 1 per cent of domestic MPANs"; 5,000 commercial; 4,500 cannabis | [H] Ofgem 2014 IA Table 4 |
| Domestic electricity detections a year (2011) | 15,956 (and 41,670 investigations) | [H] same |
| TRAS investigations, 2014–Mar 2021 | ~300,000, peak 2018/19; post-TRAS (RPA) ~54k by 2022 | [H] TEM §3.1 |
| Tip-off reports (Stay Energy Safe) | 2,613 (2017-18) → 13,415 (2024-25) | [H] RECCo business case |
| Metering interference incidents | +370% 2017→2021 | [H] Ofgem R0173, citing TEM |
| TDIS target attainment | "Suppliers currently meet 40% of their TDIS targets overall" | [H] Ofgem R0173 |
| Domestic recovery rate on detected theft | 20–30% (model assumption, 2014) | [H] Ofgem 2014 IA |
| Value per confirmed case | £2,000 "conservatively", in recovered or prevented loss | [H] RECCo business case. A ROI assumption, not a measurement |

**Readings, with what each ratio counts:**
- **Annual detection hazard, domestic electricity:** 15,956 detections a year ÷ 275,000 thefts
  in progress ≈ **5.8%** [derived]. The two figures are from different years (2011 and 2014),
  and the stock was itself calibrated to a £250m value. So this is a stock-and-flow ratio of two
  modelled figures, not an observed per-case probability.
- **TRAS-era confirmed cases a year:** ~300,000 ÷ ~7 years × 23% ≈ **10,000 a year**, all fuels
  and sectors [derived]. That is below 2011's 15,956 domestic electricity detections alone.
  Together with the 40% TDIS attainment, published detection **fell** after 2014.
- **One respondent to R0173** said TDIS targets reflect "a fundamental overestimation of the level
  of Energy Theft" [H]. Ofgem did not adjudicate.
- **RECCo's own documents disagree on conversion:** 50% ("industry benchmark") in the ROI model;
  76% "conversion" for Stay Energy Safe reports (probably contacts to usable reports, undefined)
  [H]. Neither matches TRAS's measured 23%. Use the TRAS figure.
- **Vulnerability.** One large supplier (2014) found **40%** of its domestic theft cases at
  properties with a vulnerable flag; another found "a high proportion" of offenders on
  prepayment [H] (2014 IA, in the unbilled doc). Confirmed theft rates are higher in fuel-poor and
  deprived areas, and investigations are skewed towards them even more [H] TEM figures 15–19.

### 3.5 What is not established

- The domestic share of the TEM totals. The TEM covers all sectors and includes cannabis farms
  and crypto-mining [H, its own outliers].
- The size of electricity GSP Group Correction in 2016–2025, and £ per domestic customer-year of
  UIG.
- Detection and theft rates by meter type, smart against traditional.
- The real recovery rate on domestic theft after 2014. The 20–30% is a 2014 model input.
- Counts of theft, safety and tamper warrants.
- Whether the price cap's wholesale or other allowances already carry UIG and GSP-correction
  costs. **Not read this pass, and it matters before any smear is charged** (§7).

## 4. What a supplier sees and decides

| It SEES (own systems) | It SEES (industry) | It never sees |
|---|---|---|
| Every read it receives, its source (customer, reader, smart) and date; each visit outcome (read, no-one home, refused, no access to the meter) | TRAS risk scores and outcomes; ETTOS tip-offs on its sites | Theft it has not detected; the market-wide theft stock |
| Consumption against EAC/AQ; sudden falls; zero-consumption occupied sites; smart tamper alerts | Its settled volume per run, its UIG and GSP-correction charges | Which supplier's customers caused the smear |
| Its letters and access requests, and the replies (the 21BA.2(c) evidence) | Change-of-supply reads; the old supplier's reading history (ElectraLink-style read history, [M]) | Why a household is unread, unless a visit records why |
| PSR and vulnerability flags; payment method; debt | REC Theft Calculator assessments | True consumption between reads |

**Its decisions, in the order a real one makes them:**
1. **Whom to chase for a read, and how:** a letter, a text, a self-read prompt, an area round
   (£3) or an appointment (£17.50) [H, 2015 costs]. The trigger is its own read history and the
   21B.4 and 21BA clocks. A targeted rule pays only if non-reading persists, and the supplier can
   see persistence in its own history (Q2).
2. **When to treat refusal as obstruction.** Only after documented, reasonable access requests,
   with evidence kept (2018 decision). This decision sets whether a long catch-up is barred.
3. **Whom to investigate for theft.** It weighs lead quality against cost:
   - the TRAS score, a tip-off, or its own analytics;
   - an investigation costs £200–400 (2014);
   - proactive leads convert at 15%, reactive at 42%;
   - TDIS pays for detections, and since R0173 for investigations too.
4. **Whether to seek a warrant.** For theft, safety or tamper: 10 business days' notice, and
   contact attempts may properly be none. For a read: in practice no.
5. **How to bill a confirmed theft.** It must:
   - assess the volume with the Theft Calculator and enter it into settlement;
   - evidence intent or culpable negligence before asking for payment;
   - set ability-to-pay instalments;
   - offer prepayment before disconnecting;
   - take all reasonable steps not to disconnect vulnerable occupants in winter.

The supplier decides all of these from observables. None of them needs the world's true theft
stock. The world must generate the theft and the access behaviour. The company must only see their
traces.

## 5. What our code does

Census of this worktree (base `d45a141f2`), 2026-10-06. Callers were found by grepping for each
module name outside `tests/`.

**World (`sim/`, `simulation/`).**

| Path | What it does | Verdict |
|---|---|---|
| `simulation/meter_reads.py` | Two read classes (W2_36 slice 2). The hard-to-read share comes from `q2_persistent_unread_share`; the easy rate is solved to `q2_no_read_12m_share`. Hard class reads at 0.02 a month. Smart not-communicating is 0.10, drawn independently each month. | **Right:** the forced read and 1-in-6 are gone, and the calibration is to published moments. **Wrong:** a read *arrives* by probability. There is no visit, no self-read, no access refusal, and **no supplier lever**. Ofgem's own remedy (the supplier takes the read itself) cannot be modelled, and the 21BA.2(c) exception can never be evidenced. **Wrong:** smart not-in-smart-mode is a *state* that persists, with a 2–15% spread by supplier (§2.3). The code draws it afresh each month and types its own 0.10, which is not in the register. **Open:** the hard-to-read class is keyed to `customer_id`. Locked cupboards and landlord keys are *premises* traits that outlive a tenant (Ofgem 2018 p.8). |
| (none) | Theft, tamper, unregistered use, UIG, GSP-correction smear | **Missing.** `grep -i theft\|tamper\|obstruct` over `sim/` and `simulation/` returns nothing relevant. Settlement equals true consumption (unbilled doc §5), so neither the smear nor detected theft can exist. |

**Company (`company/`).**

| Path | Production caller? | Verdict |
|---|---|---|
| `company/billing/theft_indicator.py` | **None** (test only) | Flags actual < 40% / 65% of EAC as "investigate" / "watch". The thresholds are unsourced. "Report to Ofgem if unresolved" is **wrong**: no source read requires reporting theft to Ofgem. The duties are to investigate, enter into settlement, and feed TRAS and TDIS. Low use against EAC equally flags vacancy and faulty meters (TEM H4). The idea is a legitimate lead source (suppliers' own analytics, §3.2). |
| `company/billing/energy_theft_book.py` | Only `obligations_register` and `revenue_protection_visit_register` (themselves unreached) | Cites "GS(SS)5 / TP(SS)3: notify the DNO within 2 working days". **No such instrument was found in any source read**; the real hook is DCUSA Clause 30.9 (deadline a GAP). "3-year theft back-bill" is **unsourced**: 21BA.2(c) removes the 12-month limit and sets no 3-year one. Also cites the wrong condition ("SLC 31A"). "~2.6 TWh stolen; residential ~60%" is unsourced; the TEM gives 1.7–2.8 TWh electricity, with no domestic split. |
| `company/billing/revenue_protection_register.py` | Only `obligations_register` | The same unsourced 3-year cap and "GS(SS)5". Cites "Electricity Act 1989 Section 10": the theft and meter provisions are **Schedules 6 and 7**. |
| `company/billing/theft_risk_scoring_register.py` | Only `revenue_protection_visit_register` | Score bands 30/60/80 and "£400M+ (UK Energy)" are unsourced. It duplicates what TRAS provides industry-wide. The indicator list (tamper alerts, night load, empty-home use) is reasonable practice [M]. |
| `company/billing/revenue_protection_visit_register.py` | **None** | Has an `ACCESS_DENIED` outcome, which is the right concept. No warrant path and no evidence trail for 21BA.2(c). |
| `company/market/uig_allocation_register.py` | **None** | "UIG adds ~0.5–2%" is **wrong**: actual final UIG is 2.19–3.81% (§3.3). "High UIG ≥2% triggers Xoserve investigation" is unsourced. "Proportional to throughput share" is wrong: UIG is allocated by AUGE weighting factors by matrix position. |
| `company/billing/ppm_warrant_register.py` | **None** | "Ofgem banned force-fitting from April 2023" is **wrong**. Listing was suspended on 6 Feb 2023, rules were strengthened in Nov 2023, and involuntary PPM restarted in Jan 2024 (§2.5). The £200 minimum debt is unsourced. |
| `company/billing/back_billing.py` | Yes, via `_resolve_catchup` | The cap is right (21BA, 365 days, microbusiness corrected). **Missing:** no 21BA.2(c) path. `BackBillingReason` has no obstruction or theft reason, so every long catch-up is capped. That is correct for today's world, which has no obstruction. It becomes wrong the day theft or refusal is generated. |
| `company/billing/meter_assets.py` | `company/carbon/half_hourly_footprint.py` | Certification periods (TRAD 10, SMETS 15, AMR 7 years) are unsourced. `days_until_cert` reads **`date.today()`**, the wall clock, inside company code. It has no last-read or last-visit date, so it cannot carry the read history Ofgem relies on. |
| `company/compliance/obligations_register.py` (`theft_revenue_protection_conduct`) | Register | Names SLC 12A only as "Ofgem SLC (theft)". Its trackers are the two unreached modules above. |

**Atoms.**
- **W2_36** (level 0, target 3) has "theft and unregistered consumption" in its title, and its
  `file_scope` covers only the read process. The theft half has no file in scope.
- **D48** (level 1) measures billing accuracy company-side, correctly blind to the world's use.
  It inherits the missing 21BA.2(c) path.
- `uig_allocation_register` is on no map row (unbilled doc §5).

**What is right.** The world keeps the read process a world fact and the estimate the company's
work (D48 slice 4). The read calibration follows published moments. The company's back-billing
cap reads the licence condition correctly for every case that does not involve obstruction.

## 6. Gaps

**Knowledge not established (searched, not found):**
1. **Access failure per read visit**, and its split into no-one home, refusal and inaccessible
   meter. A practitioner question: the third side.
2. The share of long-unread households a supplier could evidence as obstructive under 21BA.2(c).
3. Counts of warrants for theft, safety, tamper or reading. The courts list them by purpose but
   publish no counts.
4. The domestic split of TEM theft. The theft rate by meter type. The recovery rate after 2014.
5. The size of the electricity GSP Group Correction in 2016–2025.
6. Whether the price cap allowances already carry UIG and GSP-correction costs.
7. Per-supplier Citizens Advice billing-accuracy series, 2016–2025. Only the current quarter's
   scores were reached this pass.
8. The deadline in DCUSA Clause 30.9. The BSC Annex S-1 text (read only through Ofgem).
9. The hazard of a smart meter leaving smart mode, and how long it stays out.

**Commons gap.** `docs/domain_artefact_library/regulatory/` holds none of the texts read here:
SLC 12, 12A, 21B or 21BA, the 1954 Act s.1–2, Sch 6 para 7 and 10, Sch 2B para 23 and 28, or REC
Schedule 7. The quotations above are the candidates for it.

**Code gaps, in the order other work rests on them:**
1. **No supplier read lever in the world.** A read arrives by probability. There is no visit or
   access event the company can cause or observe.
2. **No theft and no smear.** The world generates no theft, and settlement equals truth.
3. **No 21BA.2(c) path** in `back_billing.py`, and no evidence trail of access requests to
   support one.
4. **Five theft and warrant modules carry unsourced or wrong regulatory claims** (GS(SS)5, a
   3-year cap, "report to Ofgem", the April 2023 "ban", UIG 0.5–2%). Four have no production
   caller.
5. **The smart not-in-smart-mode rate** is a constant typed in code, drawn independently each
   month. It is not in the register, and it is a state in reality.
6. `meter_assets.py` reads the wall clock.

## 7. Toggles set

Changes to `docs/market_research/assumption_toggles.yaml`. A new question, **Q6 read access and
theft**, is added. No value the world currently reads was changed.

**Revisited:**
- `q2_no_read_12m_share`: the default stays **0.07** and the low stays **0.054**. The high is
  raised from 0.07 to **0.085**, and the meaning now names the denominator mismatch.
  - Ofgem's 7% counts all domestic consumers.
  - `simulation/meter_reads.py` calibrates the same 7% among *read-exposed* meters only.
  - Smart meters were a minority in H1 2017 (10–22% by segment in the repo's own rollout curve,
    `saas/smart_meter_rollout.py`). So the share among read-exposed homes was about 0.07 ÷ (1 −
    smart share) ≈ 0.078–0.09 [derived].
  - The default is unchanged because the smart share in H1 2017 is itself uncertain and the
    world reads the default. The high end now covers the corrected figure.
  - It is also a **pre-21BA (2017) figure**. 21BA (May 2018) raised the incentive to read. No
    post-2018 series was reached (gap 7).
- `q2_persistent_unread_share`: values unchanged. The basis now notes:
  - read-access evidence supports a persistent class as a *premises* trait (locked cupboard,
    landlord key; Ofgem 2018 p.8);
  - the invariance proof (21BA-barred revenue invariant in π) **assumes no obstruction
    exception**. That holds only while `q6_obstructive_share_of_long_unread` is 0.

**Added (Q6):** all values and bases are in §2–§3.

| id | default | low | high | verdict |
|---|---|---|---|---|
| `q6_theft_share_of_electricity_consumption` | 0.009 | 0.005 | 0.025 | DOESNT_MATTER for pricing (argued); MATTERS_AND_RESOLVABLE for revenue-protection shape |
| `q6_theft_share_of_ldz_gas_throughput` | 0.0021 | 0.0013 | 0.0148 | as above |
| `q6_theft_prevalence_domestic_electricity` | 0.01 | 0.0012 | 0.016 | as above |
| `q6_theft_annual_detection_hazard` | 0.058 | 0.035 | 0.10 | MATTERS_AND_RESOLVABLE |
| `q6_theft_confirmed_per_investigation` | 0.23 | 0.15 | 0.42 | RESOLVED |
| `q6_theft_recovery_share` | 0.25 | 0.20 | 0.30 | MATTERS_AND_RESOLVABLE |
| `q6_theft_months_before_detection` | 24 | 12 | 36 | RESOLVED |
| `q6_uig_share_of_ldz_throughput` | 0.025 | 0.0219 | 0.0381 | RESOLVED |
| `q6_smart_not_in_smart_mode_share` | 0.10 | 0.02 | 0.149 | RESOLVED for level; persistence is a code finding |
| `q6_read_visit_access_failure_rate` | null | null | null | DOESNT_MATTER until a read-visit lever exists; then a practitioner question |
| `q6_obstructive_share_of_long_unread` | 0.0 | 0.0 | null | DOESNT_MATTER while the world has no access request |

Nothing goes to the director's escalation list. No toggle above is both decision-changing today
and unresolvable:
- the theft volumes do not reach pricing except through the smear, which is a published rate;
- the access-failure rate has no deciding code yet.

The one practitioner question to hold for when W2_37's read-chasing lever is built: **"Of read
visits to traditional credit meters, what share fail, and of those, how many are no-one home,
refused, or a meter you cannot get to?"**

## What this says about the order of work

1. **The cheapest true thing first: fix the five modules' regulatory claims.** This touches
   `energy_theft_book`, `revenue_protection_register`, `theft_risk_scoring_register`,
   `uig_allocation_register` and `ppm_warrant_register`.
   - No world change.
   - Each wrong claim (a 3-year cap, GS(SS)5, the April 2023 "ban", UIG 0.5–2%) would be read as
     established the day a lane wires the module.
   - It also prevents the most likely wrong next step: wiring `theft_indicator`'s unsourced
     thresholds as the detection model.
2. **Then the smear, before own-book theft, because only the smear reaches prices.**
   - What a supplier pays for theft is UIG (2.2–3.8% of gas throughput, published) and GSP
     correction (size a GAP), both by market share.
   - First check whether the cap allowances already carry them (gap 6). If they do, charging the
     smear only matters for margin against the cap, and the work is a cost line, not a world
     change.
   - The order inside: gap 6, then the GSP-correction size (gap 5), then a settlement charge.
3. **Then a read-access mechanism in the world.** This replaces "a read arrives with probability
   p" with "the supplier asks or visits; the household answers, refuses, or is not there".
   - It is what makes SLC 21B.4 effort, the 21BA.2(c) exception and W2_37's read-chasing value
     modellable at all.
   - It needs the practitioner answer above before a number is chosen. Until then the two-class
     process stays, calibrated to the same published moments.
   - Key the hard-to-read class to the premises, not the customer.
   - Make smart not-in-smart-mode a persisting state, read from the register.
4. **Own-book theft last.** It decides only the revenue-protection decision:
   - whom to investigate;
   - whether to enter units into settlement and bill them;
   - the 12A.11 safeguards.

   That decision has no company code today. When it is built, the world draws theft at
   `q6_theft_prevalence_domestic_electricity`, so detection is graded on the company's own lead
   data. Gas waits on the 10× gap between the TEM and the AUGE.

**A coupling to keep visible:** the Q2 invariance result (barred revenue does not depend on
persistence) holds only while no obstruction exception exists. Steps 3 and 4 both create one. So
the Q2 verdict must be re-run when either lands.

---

## Sources

All read as text this session [H] unless marked.
- Electricity Act 1989, Sch 6 para 7, 10; Sch 7 para 11. Gas Act 1986, Sch 2B para 10, 11, 23,
  28. Rights of Entry (Gas and Electricity Boards) Act 1954, s.1–2. Theft Act 1968, s.13. All
  from legislation.gov.uk, current revised text.
- Ofgem, *Electricity Supply Standard Licence Conditions*, consolidated to 1 August 2025: SLC 12,
  12A, 21B, 21BA.
  <https://www.ofgem.gov.uk/sites/default/files/2023-03/Electricity%20Supply%20Standard%20Consolidated%20Licence%20Conditions%20-%20Current.pdf>.
- Ofgem, *Gas Supply Standard Licence Conditions*, consolidated to 1 April 2024: SLC 12, 12A,
  21B.
  <https://www.ofgem.gov.uk/sites/default/files/2024-07/Gas_Supply_Standard_Consolidated_Licence_Conditions.pdf>.
- Ofgem, *Decision on reforming suppliers' meter inspection obligations*, 4 Feb 2016:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2016/02/decision_on_reforming_suppliers_meter_inspection_obligations.pdf>.
- Ofgem, *Reforming suppliers' meter inspection obligations*, consultation, 23 July 2015:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2015/07/reforming_suppliers_meter_inspection_obligations_final.pdf>.
- Ofgem, *Decision: Protecting consumers from backbills*, 5 March 2018:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf>.
- Ofgem, *Tackling Electricity Theft – the way forward*, Impact Assessment, March 2014:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2014/03/electricitytheft-iafinal_0.pdf>.
- Ofgem, *Decision to approve R0173: Improvements to the TDIS*, 22 May 2025:
  <https://www.ofgem.gov.uk/sites/default/files/2025-05/Authority%20decision%20to%20approve%20R0173%20Improvements%20to%20the%20Theft%20Detection%20Incentive%20Scheme%20%28TDIS%29.pdf>.
- REC v1.1, *Energy Theft Reduction Schedule*, effective 15 January 2021:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2021/02/rec_v1.1_-_theft_schedule_0.pdf>.
- RECCo / Capgemini Invent, *Theft Estimation Methodology* (2023):
  <https://retailenergycode.co.uk/alt/wp-content/uploads/2026/02/TEM-report.pdf>.
- RECCo, *Business Case: Energy Theft Programme 2026-27*:
  <https://retailenergycode.co.uk/alt/wp-content/uploads/2026/02/RECCo-Energy-Theft-Business-Case-2026-27.pdf>.
- AUGE, *Final Allocation of Unidentified Gas Statement for Gas Year 2024-2025*, v1.2, pp.27–30:
  <https://www.gasgovernance.co.uk/sites/default/files/related-files/2024-03/final_aug_statement_2024-2025.pdf>.
- Ofgem, *Smart meter performance* (smart mode by supplier, 2024–2026):
  <https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/metering/smart-meters/smart-meter-performance>.
- Ofgem, *Market compliance review: prepayment meter installations*, 3 June 2026:
  <https://www.ofgem.gov.uk/sites/default/files/2026-06/Market-Compliance-Review-prepayment-meter-installations.pdf>.
- DESNZ / gov.uk, *Just 3 energy suppliers making up over 70% of all forced installation of
  prepayment meters* (2022 warrant data).
- Courts and Tribunals Judiciary, *Directions … warrants for pre-payment meters* (revised
  2024/2025).
- DESNZ, *Tough new rules force suppliers to fix faulty smart meters*, 10 March 2026.
- Repo documents relied on: `unbilled_energy_and_revenue_assurance.md`,
  `practitioner_questions_as_assumption_toggles.md` (Q2), `meter_read_latency_estimation_2026.md`.
