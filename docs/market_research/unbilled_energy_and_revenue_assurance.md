# Unbilled energy and revenue assurance in GB domestic supply

**Knowledge:** unbilled-energy-and-revenue-assurance

**Asked by** the director's canon of 2026-10-05 (`docs/staging/done/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`),
step 1 "knowledge, now and wide", to feed step 2 "unbilled energy and billing accuracy". Knowledge
only: no code changes follow from this document. Researched 2026-10-05.

**How figures are marked.** **[H]** = read directly in the primary document named, this session
or in an earlier repo document that read it. **[M]** = from a search summary or a secondary source,
not read in the primary. **GAP** = searched for and not found; no number is supplied. Every ratio
this document computes says what its numerator and denominator count.

**A warning about the instrument, recorded because it nearly put two false numbers in this file.**
The page-summariser used to read Ofgem's 2018 back-billing decision returned "around 1.9 million of
the 26 million domestic consumers had received a backbill" and "average backbill £300–£400". The
PDF was then read as text: **neither figure appears in it.** Only figures checked against the
primary text are marked [H] below.

---

## 1. What unbilled energy is, and its kinds

**Definition.** Unbilled energy is energy that a supplier's customers have consumed, and that the
supplier is (or will be) charged for in settlement, but that has not yet been turned into a correct
charge on a customer's account. It is the gap between three quantities that are each measured
by a different party:

- **consumed**: what actually flowed through the meter (or round it), known to nobody exactly;
- **settled**: what the industry allocates to the supplier and charges it for (Elexon for
  electricity, Xoserve for gas), revised over months to years;
- **billed**: what the supplier has charged its customers, on actual or estimated reads.

A gap between *consumed* and *billed* at one supplier's customer is a **retail** gap: it is the
supplier's to close, and the customer's protection is the back-billing limit. A gap between
*consumed* and *settled* across the market is a **settlement** gap: it is allocated between
suppliers by rule, and no single supplier can see whose consumption it was. These are different
mechanisms, and `settlement_rebilling_best_practice.md` already warns that conflating them is a
fidelity error.

The kinds below arise differently, are detected differently, and have different owners. The cause
split follows from this definition: each kind is a different way for *consumed*, *settled* and
*billed* to disagree.

| # | Kind | Which quantities disagree | How it arises | Who detects it, and how |
|---|---|---|---|---|
| K1 | **Period-end accrual** (unbilled/unread revenue) | billed < consumed, *temporarily, by timing* | Every account is between bills at any period end. Billing runs monthly or quarterly; the books close on a date | The supplier, from its own billing system: last read date × consumption profile × tariff. It is an accounting estimate, not an error |
| K2 | **Estimated bill and its true-up** | billed ≠ consumed, *until the next actual read* | No actual read this cycle (traditional meter not read, no customer read, smart meter in "traditional mode") so the bill uses an estimate | The supplier, when an actual read arrives; the difference is the catch-up (positive or negative) |
| K3 | **Back-bill** (catch-up for energy not previously billed) | billed < consumed *for a long time* | K2 left uncorrected for months, a billing failure (account not billed, wrong tariff, wrong meter), or a DD set too low | The supplier, on finding it; **legally capped at 12 months** (SLC 21BA), so beyond 12 months the gap is the supplier's loss, not the customer's debt |
| K4 | **Unknown or unregistered consumption** | consumed > settled-to-any-named-customer | Theft (meter bypass/tamper), unregistered meters, gas "shipperless" and "unregistered" sites, an occupier the supplier does not know (empty home re-occupied, new tenant) | Partly the supplier (theft investigations, TRAS risk flags, "the occupier" accounts); mostly unseen: it surfaces only as UIG (gas) or GSP-group error (electricity) |
| K5 | **Meter faults and crossed meters** | billed customer ≠ consuming customer, or measured ≠ consumed | A meter that under/over-records, a wrong multiplier or correction factor, or two premises' MPANs/MPRNs swapped ("crossed") | The supplier via disputes, read validation and meter inspection; the customer usually raises crossed meters |
| K6 | **Settlement–billing mismatch** | settled ≠ billed | Settlement uses profiles and EAC/AA (electricity) or AQ and NDM allocation plus a UIG share (gas); billing uses reads. They converge only as reconciliation runs complete | The supplier, by reconciling its settled volume against billed volume; the industry, through reconciliation runs (SF→RF, 14 months) and gas meter-point reconciliation |
| K7 | **Smart-meter read failure** | a smart meter that should give K1–K2 no room behaves like a traditional one | WAN/comms loss, meter not enrolled/adopted by the new supplier ("traditional mode") | The supplier, from its own read-receipt data; published nationally by DESNZ |

K7 is a *cause* of K2, not a separate gap in money; it is listed separately because it is measured
separately (DESNZ), it has a different remedy (fix the comms, not send a reader), and Ofgem and
Citizens Advice hold smart customers to a shorter standard (6 months, against 12 for traditional).

---

## 2. Scale, kind by kind

### K1 Period-end accrual

- **British Gas Energy (Centrica), 31 Dec 2024: gross unbilled downstream energy income £670m
  (2023: £693m), against which a provision of £56m (2023: £56m) is held.** [H] Centrica plc Annual
  Report and Accounts 2024, Financial Statements, note 17 (p.213 of the ARA).
- **Group gross unbilled receivables £968m (2023: £1,065m), provision £61m (£69m), coverage 6% (6%);
  a 1pp change in coverage moves operating profit by £10m.** [H] same note, "Unbilled downstream
  energy income" table.
- **"Unread revenue" — energy supplied between the last meter reading and the year end, comprising
  both billed and unbilled revenue — £2,732m at 31 Dec 2024 (2023: £2,992m) for British Gas Energy
  and Centrica Business Solutions; a 2% change in the assumptions moves revenue and profit by £55m.**
  [H] same ARA, note 3, "Revenue recognition – unread gas and electricity meters" (p.179). Centrica
  says it is "estimated through the billing systems, using historical consumption patterns, on a
  customer-by-customer basis, taking into account weather patterns, load forecasts and the
  differences between actual meter readings being returned and system estimates", and that actual
  reads keep being compared to system estimates between the balance-sheet date and finalising the
  accounts; it also adjusts for "bill cancellation and re-bill rates".
- British Gas Energy revenue 2024 £12.1bn (2023: £17.7bn). [H] same ARA, auditor's key audit matter
  5.2. The auditor names revenue recognition, including the methodology to generate unbilled
  revenue, as a key audit matter, and re-performed the unbilled calculation with data analytics
  because it did not rely on controls after the migration to the ENSEK billing platform.
- **Derived here (not published as such):** BGE's year-end gross unbilled balance over its annual
  revenue is 670 / 12,065 = **5.6%** (2023: 3.9%). Numerator is a stock at one date; denominator is a
  year's flow. So the honest reading is "about **20 days** of average-day revenue" (2023: about 14).
  Because the stock is taken on 31 December, a high-consumption day, it is *fewer* winter days than
  that. It covers residential and small-business customers together.
- **Unread revenue is a different quantity from unbilled.** Unread includes revenue already *billed*
  on an estimate. Centrica's £2.7bn (unread) and £0.97bn (unbilled) count different things and must
  not be compared as if one were a share of the other.
- **GAP:** no other GB supplier's unbilled balance was read in this pass. One supplier's accounts
  are one witness, and British Gas's book is older, more traditional-meter and more gas-heavy than a
  new entrant's.

### K2 Estimated bills and their true-up

- **Ofgem (2018), citing Citizens Advice data:** "the median percentage of consumers receiving a
  bill reflecting a meter reading in the past year was 94.80% (Q1) and 94.40% (Q2) [2017] for
  suppliers with over 5,000 customer accounts." So about **5% of customers at the median supplier
  went a year without a bill on a read.** [H] Ofgem, *Decision: Protecting consumers from backbills*,
  5 March 2018, p.10.
- Same document: BEIS data "shows that **6% of smart meter customers still receive estimated
  bills**." [H] p.9 (Ofgem quoting respondents quoting BEIS; the BEIS table itself was not read).
- **Citizens Advice star rating** measures billing accuracy as the share of customers who received
  a bill based on a meter reading in the last **6 months (smart)** or **12 months (traditional)**;
  5 stars needs more than 98%, 1 star is below 90%. [M] Citizens Advice, *How the scores are worked
  out* (search summary). Per-supplier percentages for 2016–2025 are published quarterly but were not
  extracted this pass: **GAP** (the obvious next read).
- **Estimation exposure by meter (end 2024):** dumb meters plus smart meters in traditional mode are
  **~35.8% of domestic electricity meters and ~45.3% of domestic gas meters**; of installed smart
  meters, about 10% were not in smart mode. [H] DESNZ, *Smart Meter Statistics in Great Britain:
  Q4 2024*, read in `meter_read_latency_estimation_2026.md` §1. This is exposure, not an estimate
  rate: a dumb meter with a customer read is not estimated.
- **Settlement read coverage:** in DESNZ's sub-national data about **80% of NHH MPANs carry an
  Annualised Advance (two actual reads at least six months apart) and 20% an EAC estimate.** [H]
  DESNZ *Subnational methodology and guidance booklet*, read in
  `how_far_a_settled_eac_sits_from_next_years_use.md` §1.
- **Electricity settlement on actual data rises 30% (R1) → 60% (R2) → 80% (R3) → 97% (RF, 14
  months) of NHH energy.** [H] Elexon, *Settlement Timetable*, 2014, slide 2, read in
  `elexon_settlement_run_timetable_verified.md`. This is the best published curve for how fast
  estimated consumption is replaced by actual consumption, market-wide.
- **GAP:** the size distribution of a true-up (£ or kWh per catch-up, share positive vs negative).
  Nothing published was found. The 2018 decision records that suppliers write off "parts of
  estimated bills" under the limit, but gives no amount.

### K3 Back-billing and the 12-month limit

- **The rule.** Standard Licence Condition 21BA (electricity and gas supply licences) prevents
  suppliers "from backbilling domestic and microbusiness consumers for energy consumed more than 12
  months prior to the date of the bill", applying to "all meter types and payment methods". A bill
  may recover older charges only if (a) the bill was sent before the condition came into effect,
  (b) the supplier previously issued a compliant bill and is chasing previously billed charges, or
  (c) the consumer behaved in an obstructive or manifestly unreasonable way. [H] Ofgem decision,
  5 March 2018, pp.2 and 7. Effect 56 days after the decision for domestic (i.e. **May 2018**) and
  later for microbusinesses [H for the 56 days, p.13]; secondary sources give **1 May 2018** domestic
  and **1 November 2018** microbusiness [M].
- **History.** A voluntary domestic principle existed since 2007, after Energywatch's 2005
  super-complaint; the six largest suppliers had signed up, but the voluntary standards "do not cover
  the whole market, nor are they always followed". [H] same decision, p.2.
- Energy UK lists further cases where back-billing beyond 12 months is barred: the customer asked
  for an accurate bill and did not get one; the customer was never told of the charges by a statement
  of account; **the customer's direct debit had been set too low to cover the charges.** [M] Energy
  UK, *Energy UK Explains: Back billing*. The DD case links K3 directly to the DD-setting duty
  (SLC 27.15) already in the knowledge map.
- **Complaint scale.** About **10% of Ombudsman and Citizens Advice cases** related to back-billing
  at the time of the statutory consultation (2017). [H] decision p.6. **Energy Ombudsman back-billing
  cases: 3,238 in 2024 and 3,216 in 2025, out of 92,938 and 80,256 cases accepted** (≈3.5% and ≈4.0%).
  [M] Energy Ombudsman, *Annual data 2025* (page summary; the PDF report was not read). Energy UK
  puts back-billing at "4–5% of total complaints to the Energy Ombudsman" [M].
- **Cost of the rule.** One supplier estimated additional sector costs of **around £60m**, "mainly due
  to the costs of employing additional meter readers and writing off parts of estimated bills". [H]
  decision p.12. A respondent's estimate, not Ofgem's.
- **GAP:** number of back-bills issued, their average size, and the £ suppliers write off under
  21BA. The decision cites case studies and complaint shares but no counts. *Not established.*

### K4 Unknown and unregistered consumption (theft, unregistered, shipperless, unknown occupier)

- **Total theft (RECCo/Capgemini, 2021 methodology, published Jan 2023): "up to 1,069 GWh gas and
  2,837 GWh electricity per year", "up to £1.4 billion per year" at cap prices, "up to £50" on every
  consumer's bill.** [H for the text on RECCo's page, read directly] Retail Energy Code Company,
  *Energy theft costs consumers up to £1.4bn yearly*. "Up to" is RECCo's own wording: it is an upper
  estimate. The split by domestic/non-domestic is **not** on that page: GAP.
- **Ofgem (2014), electricity only: about 275,000 domestic theft cases "occurring at any time"
  (≈1% of domestic MPANs), 5,000 commercial, 4,500 cannabis farms; supplier detections from Ofgem's
  2011 questionnaire: 15,956 domestic, 750 commercial, 1,683 cannabis a year; total energy stolen
  "approximately £500m a year", half of it electricity.** [H] Ofgem, *Tackling Electricity Theft — the
  way forward*, Impact Assessment, March 2014, §2 and Appendix tables. Its model assumed 24–48
  months of back-assessed consumption after detection and a **20–30% average recovery rate** for
  domestic cases, and that **50–100% of stolen units are assessed as stolen for settlement**. One
  large supplier found **40% of its domestic theft cases at properties with a customer flagged
  vulnerable**, another "a high proportion" of offenders on prepayment. [H] same IA, §2.22 and §3.
- **Derived (2026-10-16): the IA prices each domestic case at a whole average home's use.** Its
  Table 4 gives 275,000 domestic cases, 5,000 commercial and 4,500 cannabis farms at any time,
  average use of 333, 1,195 and 9,000 kWh a month, and a retail price of £0.15/kWh. It says the case
  counts are "consistent with" about £250m a year. Those inputs give 1,099 + 72 + 486 = 1,657 GWh,
  or **£248m, only if each domestic case takes all of an average home's use**. At half of it the
  total is £166m; at a quarter, £125m. [derived from IA Table 4 and §3.2, read directly 2026-10-16.]
  This is the IA's own modelling, not a measurement of what a bypassed meter registers. Domestic
  cases are 66% of its total. Register row `q6_theft_share_of_premise_use_unregistered`: default
  1.0, low a **GAP** (partial tampering exists; its share is not published).
- **Derived (count over count, both Ofgem 2014):** detections per year / cases at any time
  = 15,956 / 275,000 ≈ **5.8%**. A rough annual detection hazard on a stock, not a detection rate per
  case-lifetime.
- **Gas UIG (target gas year 2024-25): total 7,761 GWh, of which theft 6,362 GWh (82%), average
  temperature assumption 997, average pressure assumption 323, no read at line in the sand 55,
  unregistered sites 53, incorrect correction factors 40, dead sites 23, isolated sites 21, IGT
  shrinkage 21, shipperless sites 15, consumption meter error −149.** 2023-24: total 8,497 GWh, theft
  6,823. [H] AUGE, *Final Allocation of Unidentified Gas Statement for Gas Year 2024-2025*, v1.2,
  31 March 2024, §1 Results table.
- **Actual final UIG "has been running at around 2.5% of throughput since Nexus go-live"** (June
  2017). By gas year at time of investigation: 17/18 3.81%, 18/19 2.19%, 19/20 2.69%, 20/21 2.90%,
  21/22 2.50%. The AUGE's identified contributors explain only 73–88% of actual UIG ("unfound UIG").
  [H] same statement, p.27.
- **UIG can go negative.** Xoserve reports an "extended period of negative UIG" from March 2022 to
  summer 2023 because the NDM algorithm over-allocated when consumption fell sharply in the price
  crisis. [M] Xoserve, *Unidentified Gas (UIG)* help-centre page (summary). This matters for our
  window: in 2022 the allocation *over*-charged suppliers' NDM portfolios rather than under.
- **Unregistered and shipperless sites are small in gas energy (53 and 15 GWh)** against theft
  (6,362 GWh). [H] AUG table above. **Electricity equivalents: GAP.** In electricity, theft and
  unregistered consumption sit in DNO "non-technical losses" and the GSP-group correction factor; no
  GB-wide published GWh was found this pass.
- **Unknown occupier / change of tenancy:** **GAP.** No published count of "the occupier" accounts or
  of consumption between occupiers was found. The knowledge map already records that home moves are
  20–40% of debt (Ofgem DRS 2025); the unbilled side of a move is not published.

### K5 Meter faults and crossed meters

- **Definition (Ofgem, SPAA CP10/190):** a customer billed for a meter point (MPRN) that is not
  measuring consumption at their premises; commonest in adjacent properties and blocks of flats,
  arising at install or later work. [M] search summary of the Ofgem SPAA decision page.
- **Counts of crossed meters: GAP.** No published count or rate of crossed meters, and no rule on
  whether correcting a crossed meter is an ordinary back-bill (21BA's 12 months) or an exception.
  "Consumption meter error" in gas UIG is −15 to −149 GWh (net over-recording, i.e. it *reduces*
  UIG), [H] AUG table.
- **The legal limit (researched 2026-10-17).** An in-service meter is held to the limit it met when
  new; the regulator states there is "no additional tolerance" in service. Electricity meters on GB
  national approval: **+2.5% to −3.5%** across the load range [H] NMRO 2015 §3.1–3.2. MID meters
  (most new and smart installs) are tighter and load-point specific: Class A ±2.5% at minimum current
  and ±2.0% at 1/5 and full load; B and C tighter still [H] OPSS IST Handbook 3.7, Tables 3–5. Gas,
  SI 1983/684 domestic mechanical: **±2%** at maximum and at 20% of maximum flow; domestic electronic
  adds ±3% at minimum flow [H] NMO 2011 §3.2. MID gas Class 1.5: ±3.0% [H] IST Handbook.
- **Disputed meters, examined (researched 2026-10-17).** This is the only published count, and it is
  a count of meters **someone already suspected**. Every report says the sample "is not representative
  of the whole meter population", so it is not a fault rate.
  - Electricity, 2003–2014: 2,345 meters were referred for determination under Schedule 7. 2,188 (93%)
    registered correctly and were correctly installed. 21 (0.9%) were outside the limits by under 5%,
    and 55 (2.3%) by over 5%, fast or slow. 73 (3.1%) had other failures: multiple-register faults,
    tamper evidence, demagnetisation, and component failure [H] NMRO 2015 §4.1. The fast/slow split was
    not recovered from the chart: **GAP**. It decides the sign. A slow meter is unbilled energy; a fast
    meter overbills the customer.
  - Domestic gas: of 1,276 disputed meters in 2003/04, 64% were accurate [H] Ofgem 2004. Of 1,288 in
    2011, 76% were accurate [H] NMO 2011.
  - **For 2016–2025: GAP.** Each report promised an annual series, and no successor after the 2015
    report was found. OPSS's guidance says only that the "vast majority" tested in 2021 were accurate
    [M]. At about 100–300 electricity referrals a year against over 28 million meters, disputes are a
    rare door. **What share of faulty meters are never disputed is not published.**
- **Smart meters.** DESNZ publishes the operating mode (end-2025: 7.7% of smart meters in traditional
  mode) and never recording accuracy. A smart-meter metrology fault rate is a **GAP**. Keep it apart
  from the comms-failure figure (K7). They are two different things.
- **What this means for the world build (K8).** No published number gives the population share of
  meters recording outside the limit, or the direction of the error. A world K5 therefore carries its
  prevalence as a named `None` until it is sourced. The legal limit (±2–3.5%) is the band an *accurate*
  meter may sit in, and it is established. The disputed-meter shares bound only the referred
  population.

### K6 Settlement versus billing

- **Electricity:** settlement runs II (1 week), SF (1 month), R1 (2), R2 (4), R3 (7), **RF (14 months,
  last scheduled)**, DF (28 months, disputes only). NHH energy on actual data 30/60/80/97% at
  R1/R2/R3/RF. MHHS cuts this to 4 months; central systems live 24 Sept 2025, after our window. [H]
  `elexon_settlement_run_timetable_verified.md`.
- **Gas:** UIG allocated daily per LDZ by weighting factors set by the AUGE; individual meter reads
  trigger reconciliations that adjust positions monthly through amendment invoices, so a supplier's
  position "will keep changing and may switch between debit and credit over time". [M] Xoserve UIG
  page. The AUGE says actual UIG "continues to move for four years as per the industry
  reconciliation mechanism". [H] AUG statement p.27. (Xoserve's page summary said 24 months; the two
  are not reconciled here: GAP on the exact gas reconciliation window.)
- **What reaches the supplier from settlement:** for electricity, the supplier's settled volume
  includes its share of GSP-group correction, so other parties' unmetered and stolen energy lands
  on its settlement bill pro rata. Elexon: GSP Group Correction allocates the difference between
  deemed consumption and energy entering the GSP group; errors include Line Loss Factors that account
  for "technical and non-technical losses (e.g. theft, unregistered export)". [M] Elexon, *GSP Group
  Correction Factors* (summary). For gas, the supplier (via its shipper) is charged its UIG share.
  **In both fuels a supplier pays for unbilled energy it never supplied to any customer it knows.**
- **GAP:** the size of the GSP group correction factor in our window, and the £ per domestic
  customer-year a supplier pays for UIG. Both are in principle derivable from published Xoserve /
  Elexon data; neither was derived this pass.

### K7 Smart meter read failures

- See K2: ~10% of installed smart meters not in smart mode end-2024; domestic traditional-mode
  shares 4.7% electricity, 9.1% gas; small suppliers 86% smart-mode against 90% for large. [H] DESNZ
  Q4 2024, via `meter_read_latency_estimation_2026.md`.
- **GAP:** the time series 2016–2025 of traditional-mode share, and the rate at which a working
  smart meter drops out (the hazard, not the stock). DESNZ publishes the quarterly stock; the
  hazard is not published.

---

## 3. What a real supplier can see, and what it cannot

This is the epistemic wall, and it matters most for K4 and K6.

| A supplier SEES (its own systems) | A supplier SEES (from industry flows) | Only the industry, or nobody, sees |
|---|---|---|
| Its own bills, and whether each was on an actual, customer or estimated read | Its settled volumes per run (SF…RF) and the reconciliation charges | True consumption between reads, at every premise |
| Every read it receives, its date and source; smart read failures on its own meters | EAC/AA (electricity) and AQ (gas) for its meter points | Theft it has not detected |
| Its own unbilled accrual (from last read date, profile and tariff) | The GSP group correction factor and UIG charges applied to it | Unregistered and shipperless sites, by definition not its customers |
| Disputes, complaints and back-bills it has issued; amounts written off under 21BA | TRAS theft-risk referrals (since REC/TRAS) | Which supplier's customers caused UIG or GSP correction |
| Meter faults it has investigated; crossed-meter cases its customers raise | Change-of-supply reads agreed with the old supplier | The UIG and theft totals until the AUGE / RECCo publish estimates |

So a supplier can measure K1, K2, K3, K7 and the *detected* part of K4/K5 **exactly**, from its own
books. It can measure K6 as a **residual**: its settled volume minus its billed volume, once
reconciliation has run. It can never attribute that residual to a premise. The industry estimates
(AUGE, RECCo) are published and so cross the wall as *public* figures, not as ground truth about
this supplier's book.

---

## 4. Revenue assurance as a practice

What suppliers and their auditors do, from the evidence read:

1. **Estimate unbilled/unread revenue per customer**, from last read, historical consumption,
   weather and load forecasts, and keep comparing actual reads to the estimate after the period end
   (Centrica note 3, [H]). Constrain recognised revenue for expected **bill cancellations and
   re-bills** (same, [H]).
2. **Provide against unbilled income at a lower rate than billed debt**, because once billed most
   of it falls into short collection cycles (Centrica note 17: 6% group coverage, [H]).
3. **Test billing completeness and accuracy**: agree billed volume and price to tariffs and to
   actual or estimated reads; build an expectation of billed revenue and investigate differences
   beyond thresholds; re-perform the unbilled calculation from source data (Centrica auditor KAM
   5.2, [H]).
4. **Chase actual reads** to stay inside SLC 21BA and the Citizens Advice 6/12-month standard;
   Ofgem expected the limit to incentivise meter reading and smart roll-out ([H] 2018 decision p.10).
5. **Detect theft** through TRAS risk scoring and investigations, recover assessed consumption, and
   put detected theft into settlement (Ofgem 2014 IA, [H]; RECCo Energy Theft Reduction schedule, [M]).
6. **Reconcile settlement to billing**: settled volume (per run) against billed volume, by meter
   point and in aggregate; challenge UIG and GSP correction through the industry processes.

**What good looks like:** **GAP** for any published benchmark of "billed volume / settled volume"
for a well-run domestic supplier. The closest published standards are the Citizens Advice >98%
five-star billing-accuracy threshold [M], and Elexon's 97% NHH-on-actuals at RF [H].

### 4a. Screening low and zero consumption for theft: the window, and what "occupied" means

Added 2026-10-17, before the company's two structural flags were built (K8). The duties are in
`read_access_and_theft_duties.md` §3.1 and are only summarised here: SLC 12.1 (electricity) asks
"all reasonable steps to detect and prevent" theft, interference and damage; SLC 12A.5–12A.6 ask the
same and an investigation where there are "reasonable grounds to suspect"; 12A.7 puts the supplier
in REC Schedule 7 (TRAS, ETTOS, TDIS) [H, via that page]. **No licence condition or code read
prescribes how a supplier screens its own consumption data, over what window, or at what cut.**

**What is published about the screen.**
- **Supplier analytics is one lead source among several, and a small one.** Ofgem's 2010
  questionnaire (published 26 March 2012), electricity, weighted by theft cases found: data
  collector 26%, meter operator 21%, the DNO's Revenue Protection Service (RPS) 14%, supplier
  "analysis" **8%**, other (revenue protection officers, tip-offs, housing associations, police, new
  tenants) 24%. Gas: "analysis" 9%. Ofgem added that the RPO-generated share "will, to some extent,
  be data driven" [H]. The 85% gas figure in §3.2 of the duties page pools tip-offs with analysis.
- **TRAS takes a monthly extract of the whole portfolio** (address, account, last billed amount,
  arrears) and returns risk scores [M, ENGIE's TRAS notice; SPAA CP13/239]. Its "Relevant
  Information" list was explicitly provisional in the 2013 decision, and the scoring model is the
  provider's (Experian's). **GAP:** which consumption features TRAS scores, and over what window.
- **How long a theft runs before detection:** domestic gas "approximately 2 years and 4 months"
  (2010 questionnaire, Table 6) [H]; electricity "just under 2 years", with spikes at 365 and 730
  days where suppliers cut off their recording (TEM 2023 §3.1) [H, via the duties page]. A window
  of a year or more therefore sees most thefts whole; a month sees about one twenty-fourth of one.
- **What a void looks like in published practice.** The BSC's Long Term Vacant process (P196, 2007;
  window amended by P245, 2009) lets a supplier settle a non-half-hourly site at zero only after its
  data collector has twice reported a failed read coded **02 "Site Not Occupied"** (D0004, J0024),
  the visits **75 to 215 calendar days apart**; any other code resets the clock. The window was
  chosen to fit quarterly and six-monthly read cycles [H, P245 proposal form]. Gas has the same
  shape: two visits 75–215 days apart, then zero commodity charges with the AQ kept for capacity
  [M, UNC 0282 decision summary].
- **Zero gas use in an occupied home is ordinary.** Ofgem's open letter of 20 June 2014: "a maximum
  of 323,000 zero gas consuming domestic meters", 2% of domestic gas meters, including homes that
  have a meter and do not use it, and periodic zero-users such as seasonal homeowners [H].

**What "occupied account" means.** Published practice defines the negative only: a site is *not
occupied* when the industry's evidence says so (two "Site Not Occupied" visits, or a notified
change of tenancy). **GAP:** no published positive definition of an occupied account for theft
screening. What a real supplier holds is whether the account has a **named** liable occupier, or is
billed to "the occupier" or charged to the owner for a void (B7, §5 K4). That is the design's
definition below, and it is a design choice, not a published one.

**What this design takes from it, and why** (`company/billing/theft_indicator.py`):
1. **An empty period on a named occupier's electricity account is a lead without a cut.** Zero
   advance between two actual reads needs no threshold: it is zero. A named occupier rules out the
   void that would otherwise explain it, because published practice treats a void as an *absence*
   of an occupier. Electricity only: an occupied home's fridge and standby keep an electricity
   meter turning, but a gas meter in an occupied home is idle in up to 2% of homes (Ofgem 2014), so
   a gas empty period is not evidence of anything and the flag reports gas as not screened.
2. **The annual window is at least 360 days of the company's own expectation.** That window is a
   design choice, not a published one (**GAP**: the screening window). It is chosen because
   published thefts run about two years, voids run about a month, and a year removes the seasonal
   shape error the W2_36 probe found in a monthly expectation.
3. **The annual window's cut stays `None`.** No published actual/expected cut was found here or in
   the duties page (§5). Without a caller's cut the window is reported `unscreened`, as the ratio
   screen already is.

**GAPs carried:** TRAS's consumption features and window; any published actual/expected screening
cut; a positive definition of "occupied"; the rate at which empty periods on named electricity
accounts are confirmed theft (TRAS publishes outcomes by payment method only).

**The opening read at a change of tenancy** (added 2026-10-17, before the flag was given one; K8).
The empty-period flag needs an actual read at each end of a span, so the question is whether a
supplier holds an actual read on the day an incoming occupier's account opens.
- **With the same supplier, no industry process sets the read.** BSCP504 v53.0 (Oct 2024) names a
  change of tenancy only to end a Long Term Vacant period: "the date of the change of tenancy should
  be used as the end date" (§4.15.5), and a CoT is a reason the site stops qualifying (§4.15.4) [H].
  Its read-taking rules are for a change of **supplier**. A CoT with the incumbent sends no
  registration flow (`home_moves.md` §3). The read is the supplier's own.
- **The change-of-supplier rule is the published precedent for an opening read.** The read is taken
  "within the SSD ±5 days" from actual reads in precedence remote, meter operator final, data
  collector, then customer own. If none is valid by SSD+5, "a valid Old Supplier Estimated reading
  … must be used", and the new data collector deems one by SSD+8 (BSCP504 §4.4.1, step 3.2.6.11)
  [H]. Gas has the same shape: the incoming shipper submits the opening read, or an estimated
  opening read within 10 days (UNC 0427S, 7 days before it) [M]. **So an opening read always
  exists, and it is either actual or deemed.**
- **At a CoT the opening read is the outgoing account's closing read.** The meter does not change,
  so one read closes one account and opens the next (`home_moves.md` §3). It is actual if the
  customer gave one, or if a smart meter was read remotely on the day. Otherwise it is estimated
  (§8.2 there: a final read is actual "sometimes") [M, Citizens Advice and supplier guidance].
  **GAP:** the share of change-of-tenancy boundary reads that are actual. None found.

**What the design takes from it** (`company/billing/theft_indicator.py`):
4. **An incoming account opens on the outgoing account's closing read.** `boundary_read_status`
   reads that read off the outgoing account at the same meter point, if its period ends the day
   before the account opens. `empty_period_flags(periods, opening_read_status)` judges the first
   span only when that read is **actual**. A deemed opening read is the supplier's own guess, so a
   zero advance from it is not measured. Without a closing read on the boundary, nothing is judged.
   Graded on the run book in
   `docs/staging/records/WORKER_PREREG_W2_36_THE_OPENING_READ_AT_A_CHANGE_OF_TENANCY_2026-10-17.md`.


**What trues up a closing read after supply ends** (added 2026-10-17, before the dispute seed was
given any realisation route; K8). A closing estimate becomes the deemed read: "a valid Old Supplier
Estimated reading … must be used" (§4.4.1, above). The question is what can replace it later.
- **Electricity: the disputed change-of-supplier read.** "The new Supplier can dispute the change
  of Supplier reading at any point up to twelve months after the change of Supplier, where in the
  Supplier's view there is difference of more than 250kWh" (BSCP504 v53.0 §4.4.1(b)) [H]. The old
  supplier may also dispute within 12 months of SSD (steps 3.2.6.36 new supplier, 3.2.6.37 old
  supplier, both on the D0300 flow). The old supplier has no read of its own after the loss, so its
  first option is to "send a request to the new Supplier to provide an actual Meter register
  reading" [H]. If the suppliers cannot agree, the new data collector takes a current read and
  deems the switch-date read backwards from it. A revision under 250 kWh is not entered into
  settlement [H]. "The CoS reading is assumed to be correct by the Old Supplier, until the Old
  Supplier disputes" it (footnote 22) [H]. After the 12 months, the read can be replaced only by
  mutual agreement between the two suppliers or by an authorised BSC Trading Dispute (§4.14.5) [H].
- **Gas: the Shipper/Supplier Agreed Read.** The incoming shipper provides the opening read. A
  replacement "must be Agreed between the Incoming and Outgoing Shipper" (UNC TPD Section M, as
  summarised to the DWG). Under SPAA Schedule 11, "disputes need to be initiated within 12 months
  of the CoS" and resolved within 70 business days. Where the volume is 1,200 kWh or less, the
  outgoing supplier is encouraged to accept [M, Joint Office DWG paper, Jan 2020].
- **Who may raise it, and the customer's part.** The REC switch-read exceptions schedule (Ofgem
  consultation draft, Oct 2018) lets "the Consumer, Losing Supplier or Gaining Supplier" raise a
  dispute within 12 months. A consumer may contact either supplier. Under 1,200 kWh (gas) or 250 kWh
  (electricity), the supplier "shall not dispute … unless the Consumer specifically requests a new
  Switch Meter Reading, but should instead attempt to resolve the dispute with an accommodation
  e.g. cash allowance". Both suppliers then bill on the agreed read. "Where the Losing Supplier
  presents the Consumer with an amended final account as a result of a dispute", it explains how
  the read was set (§§3.5–3.6, 4.1, 4.3) [M: a draft; the in-force REC text was not read].
- **A home mover has no such route.** A change of tenancy with the same supplier has no second
  supplier and no D0300. The closing read is the supplier's own (above), so nothing in industry
  process sets a window or a threshold for correcting it. The SLC 21BA 12-month bar still applies to
  any demand (§K3) [reasoning from the sources above].
- **Which side has the reason to dispute** [reasoning]. An undercharging closing estimate puts the
  register at the switch below the true one. The gaining supplier's first actual read then carries
  the missed kWh onto its own customer's bill, so the gaining supplier, or the customer, has a
  reason to dispute it. An overcharging closing estimate is the reverse. The gaining supplier gains,
  and only the losing supplier has a reason to dispute, but it holds no read. **For a switcher, the
  household pays for the same kWh either way.** A dispute moves them between the two suppliers'
  bills. The household's own position changes only by the difference in rates and by any 21BA bar.
  That makes most of a corrected switch read a transfer between suppliers, not value created (M2).

**GAPs:** the in-force REC wording (after 2021) and the in-force UNC Section M text, which were not
read directly; how many disputed switch reads are raised a year, and what share are upheld (no
published count found); how soon a gaining supplier gets its first actual read after the switch
(this sets when, inside the 12 months, a dispute could arrive); whether an amended final account
after a dispute is treated as a back-bill under 21BA when it reaches beyond 12 months.

**Measured on the graded run output** (`/var/tmp/closing-money-run-20261017.json`, cc23de757;
`docs/staging/records/SEAT_PREREG_WHICH_OPEN_CLOSING_RUNS_A_DISPUTED_SWITCH_READ_COULD_EVER_REACH_2026-10-17.md`).
Of the 403 open closing runs, 265 are switchers, 132 home movers and 6 on both lists. The £3,471
dispute seed (`8cd8e9954`) is new demand summed over the undercharge runs. Of it, **£2,222 across 17
switcher runs passes the dispute threshold**, so a dispute from the gaining supplier could ever
reach it. C7 alone is £1,431. None of those 17 runs closed within 12 months of the run's end. **The
other £1,248, across 193 runs, has no industry route:** £833 sits on switchers under the threshold,
where the REC says offer an accommodation, and £415 sits on movers, which only the supplier's own
correction could reach. The world draws no gaining supplier, so it raises no D0300 and no dispute
ever arrives. The seed stays a ceiling until the world models the gaining supplier's first read.

### 4b. What a supplier must do with an account its screen flags

Added 2026-10-17, before the billing run was given the screen (K8). The duties are sourced in
`read_access_and_theft_duties.md` §2.4 and §3.1–3.3 and are quoted from there; the visit and the
assessment are read here from the electricity Revenue Protection Code of Practice (RPCoP), DCUSA
Schedule 23, Version 5.11 [H, read as text, 71 pp.].

**1. A flag is a lead, and the duty it engages is an investigation.**
- SLC 12A.5 asks "all reasonable steps to detect and prevent" theft, and **12A.6 asks for an
  investigation where there are "reasonable grounds to suspect"** [H, via the duties page §3.1].
  SLC 12.1 asks the same of electricity metering [H, same]. No condition says that a supplier's own
  screen *is* reasonable grounds, so whether one empty period meets 12A.6 is the supplier's
  judgement: **GAP**, unpublished.
- The RPCoP puts the work on the supplier: "The Supplier shall investigate and resolve all cases of
  Theft of Electricity other than Theft in Conveyance. Where theft is identified, the Supplier shall
  seek to recover the Relevant Costs from the Perpetrator, and shall (to the extent possible under
  the BSC) arrange for the stolen electricity to be entered into Settlement" (§4, OBLIGATION) [H].

**2. The TRAS referral.** The supplier is party to REC Schedule 7 (SLC 12A.7). TRAS takes a monthly
extract of the whole book and returns risk scores (§4a above) [M]. A screen's flag therefore sits
*alongside* the TRAS score: the supplier reads both before it spends a visit. **GAP:** whether a
supplier may or must feed its own flag into TRAS, and how TRAS weighs it. Not published. Since
R0173 (approved 22 May 2025), TDIS pays for desktop investigations and site visits whatever their
outcome [H, via the duties page]. So in 2025 a visit to a flagged account earns something even when
no theft is found. Before that, it earned nothing.

**3. The site visit.** All [H], RPCoP:
- **Unannounced.** The revenue protection agent "visits the Premises without prior notification,
  provides appropriate identification … and requests entry to inspect" (§9). Police may be asked
  to attend if a breach of the peace is likely.
- **Care with vulnerable people.** People with a disability, a mental health condition, or under 18
  "should not be interviewed alone" (§9). §13 asks reasonable steps to identify a Vulnerable
  Customer, and SLC 12A.11(a)–(d) set the safeguards [H, via the duties page].
- **A warrant only after refusal.** "Where access to the Premises has not been gained after
  reasonable attempts have been made, the Party should seek to obtain a warrant" (§9). It is
  granted under the Rights of Entry (Gas and Electricity Boards) Act 1954 and Schedule 6 of the
  Electricity Act. Refusing a reader is lawful; obstructing a warranted entry is the offence
  (duties page §2.2).
- **Make safe first.** "safety is paramount" (§3.3(a)). Tampered equipment is rectified "as soon as
  reasonable practicable", and supply may be de-energised meanwhile (§15.2). The supplier should
  "consider all available options for the maintenance of supply, including fitting a prepayment
  meter and payment by instalments" (§15.4).

**4. How the unbilled energy is assessed.** The assessment "is carried out in a systematic,
reasonable, consistent and transparent way" (§15.3, OBLIGATION) [H]. Appendix 7 lists five
methods, "in no particular order", saying "No one single method is necessarily appropriate in all
cases" [H]. §15.3's best practice nonetheless recommends following "the order as set out in
Appendix 7":
1. past consumption history, where there is "an obvious step change following an earlier
   established level or pattern";
2. an audit of appliances, with the customer's permission, on standard consumption figures;
3. "typical consumption levels for the type of property", by premises type, tariff, occupants,
   other fuels and location;
4. monitoring ongoing consumption;
5. a load test.

How long the theft ran is to be agreed with the customer where possible. It is bounded by "when the
meter was last inspected", and "Length of occupancy should be confirmed and validated" (App. 7
§2.4). The supplier sets the final assessment and tells the distributor (§2.2). It should be
completed on site where possible, or issued as an interim and then a final assessment (§15.2).

**5. How it is billed, and whether the back-billing limit applies.**
- **What is charged.** The "Relevant Costs" are the value of the energy taken, the cost of
  repairing or replacing equipment, and the investigation (§3.3(b), §15.5) [H]. Only "direct and
  reasonably foreseeable costs … Such costs should not be a penalty" (§15.4) [H]. Invoices carry
  VAT and Climate Change Levy as statute requires (§15.5) [H]. The supplier enters the assessed
  units into settlement and pays for them (§4) [H].
- **Payment must be evidenced first.** SLC 12A.11(g): evidence, on the balance of probabilities,
  that the theft was this customer's "intentional act or … culpable negligence" **before requiring
  payment**. 12A.11(h) asks a plain-language explanation of the assessment, the charge, and how to
  dispute it [H, via the duties page]. The customer is told of their right to go to the Energy
  Ombudsman (RPCoP App. 7 §2.5) [H].
- **Ability to pay.** Instalments take ability to pay into account (SLC 12A.11(b)). The RPCoP adds
  case-by-case handling and monitoring of broken arrangements (§15.7) [H].
- **The 12-month limit does not apply where the customer is at fault.** SLC 21BA.2(c) lifts it
  where recovery was prevented by "obstructive or manifestly unreasonable behaviour of the Domestic
  Customer". Ofgem's 2018 decision names "stealing electricity or gas" as its example [H, via the
  duties page §2.4]. **No licence cap replaces it.** The evidence test of 12A.11(g) does that work.
  A general limitation period applies [M, Limitation Act not read]. The "3-year theft back-bill"
  some modules typed has no source (duties page §2.4).
- **What is recovered in practice.** Ofgem's 2014 model assumed **20–30%** recovered on domestic
  cases [H, IA Table 5], and a proactive investigation is confirmed **15%** of the time [H, TEM].
  Both are an era's averages, not this book's.

**6. What a void, and a zero gas period, call for.** No theft act. A void is billed as it is
already billed: the owner's deemed charge, or "the occupier" (B7). And nothing was consumed
unbilled, because the meter did not advance and the premise was empty. A zero gas period is
ordinary in up to 2% of occupied homes (§4a), so no duty is engaged.

**What the design takes from it** (`company/billing/theft_indicator.screen_billing_run`, called from
`company/billing/monthly_bill_assembly.build_monthly_bills` behind
`DecisionPolicy.theft_screen_in_billing_run`, default off):
5. Each flag is recorded with its act: `investigate` → `refer_for_investigation`, `void` →
   `bill_the_void`, gas `not_screened` → `none`. The billing run raises no charge from a flag.
   Under 12A.11(g) nothing may be charged before an investigation confirms the theft, and the
   company has no investigation yet.
6. For a lead, the record carries **what the act would charge if confirmed**. The unrecorded kWh is
   assessed by Appendix 7 method 1 (the account's own daily level over its earlier read-to-read
   spans) or, failing that, method 3 (the registry EAC/AQ, the company's only typical figure for the
   property). It is valued at the account's own billed commodity rate, with no 21BA cap. Neither
   the 15% nor the 20–30% is applied: they are an era's averages, and the gross charge is the
   quantity a supplier's investigation decides on.

**GAPs carried:** whether a supplier's own flag meets 12A.6's "reasonable grounds"; how TRAS uses a
supplier's flag; the cost of a desktop investigation and a site visit to a supplier in 2016–2025
(Ofgem 2014 gives £200–400 an investigation, a model input); the current REC Schedule 8 (Unbilled
Energy Code of Practice) text, which succeeded DCUSA Schedule 23 at REC v2.0 [M, the supplier
copy fetched returned a web page, not the document]; the gas code's assessment methods (not read).

---

## 5. What our code does

From a census of this worktree on 2026-10-05 (base `a52651e29`). The load-bearing claims were
re-read directly: the settlement docstring, the ledger function, the meter-read constants, and the
no-caller greps for `theft_indicator`, `uig_allocation_register` and `revenue_accruals`.

**The headline: three quantities collapse into one.** The world settles the supplier on each
customer's TRUE consumption. The docstring of `simulation/settlement_run_series.py` says so: "the
TRUE final settled figure … settle from the customer's TRUE consumption shape; this is the RF /
true-final value, UNCHANGED", and the RF value is "by construction, the untouched true settled
figure". D3's catch-up then trues every bill up to the same true consumption. So in our world
**consumed = settled (at RF) = billed (after catch-up)**, at every premise, by construction. In GB,
gas UIG alone is about 2.5% of throughput, settled to suppliers and billed to nobody (§2 K4). So
revenue assurance has nothing to find here, and kinds K4, K5 and most of K6 cannot arise.

| Kind | What exists | Reached in a run? | Verdict |
|---|---|---|---|
| K1 accrual | `saas/ledger.py:unbilled_revenue_accrual` (L309) → `saas/reporting/annual_report.py:_section_unbilled_revenue_accrual`. A second implementation, `company/finance/revenue_accruals.py` (`RevenueAccrualsLedger`) with `company/finance/period_reconciliation.py`, has **no non-test caller**. `E3_accrual_restatement` is closed at 2/2 with its Expert Hour `not_attempted` | Yes (report only) | **Mis-defined.** It adds up the *whole amount* of every estimated bill that no catch-up covers yet. That is the *billed-on-estimate* part of Centrica's "unread revenue", not "unbilled revenue" (consumed and not yet billed). It does not measure the estimate's error, and it does not measure consumption since the last bill. Bills are calendar-month (`monthly_bill_assembly._billing_month`) with a 5-day read cutoff, so true period-end unbilled consumption is close to zero by construction. **Update 2026-10-05 (D48 slice 2):** renamed `estimated_billing_outstanding` by another lane the same day. It also kept, for ever, every estimate a read had closed with a correction under the £5 materiality threshold: 83% of the decade run's £93,059. Corrected: a read now ends the run. `company/billing/billing_accuracy.estimated_billing_outstanding_grade` grades each run open at a month end against its later read. Decade run, runs open at a year end: net +10% (electricity), +24% (gas) of the run's billed kWh under-billed. At a June month end: −2% and −26%. The trailing-mean estimate carries the season into every period-end position. **Update 2026-10-06 (D48 slice 3):** the company now shapes its own estimate by a published monthly profile (`company/billing/unread_month_estimate.py`, sources in `how_a_supplier_shapes_an_estimate_for_an_unread_month.md`). Same world, one variable: December net +3.2% (electricity) and −6.5% (gas); June +1.6% and −3.8%. Gas gross fell from 53% to 16%; electricity gross did not fall |
| K2 estimate and true-up | `simulation/meter_reads.py::simulate_read` (world) → `company/billing/monthly_bill_assembly.build_monthly_bills` (`_annotate_billing_basis` L183, `_resolve_catchup` L211), called from `simulation/run_phase4c_on_phase2b.py:337`. `D3_catchup_rebilling` closed 3/3, Expert Hour passed | Yes | **Built, and the shape is sound.** The estimate is the mean of the customer's last 3 actual periods (`ESTIMATE_TRAILING_WINDOW = 3`), so a winter estimate made from autumn actuals undershoots and the seasons produce real catch-ups. Smart not-communicating is 10%, blended across fuels where DESNZ gives 4.7% electricity and 9.1% gas in traditional mode. A traditional meter gets an actual read with probability **1/6 per month, independently each month** (the code flags this as unverified). **Update 2026-10-05:** superseded by W2_36 slice 2 (`977e17453`): two read classes from the assumption register's Q2 rows. D48 slice 1 now measures K2 company-side (`company/billing/billing_accuracy.py`). It reads each bill's basis and a read-time true-up stamped by `_resolve_catchup`, never the world's use. First real run, 2016–2020: 61% of electricity kWh and 59% of gas kWh billed on estimates. **Update 2026-10-06 (D48 slices 3–4):** the world no longer estimates. `simulate_read` reports status only. The company estimates every unread period itself in `company/billing/unread_month_estimate.py`: from its own last three reads shaped by the published profile, or before its first read from the registry EAC/AQ spread by that profile |
| K3 back-bill | `company/billing/back_billing.py` (365-day cap, pro-rata write-off), invoked by `_resolve_catchup` | Yes | **Can bind only at the margin.** `meter_reads.MAX_CONSECUTIVE_ESTIMATED_PERIODS = 12` forces an actual read after 12 estimated months, so no unread run goes much past the cap (whether a 12-month run plus the read lag ever crosses 365 days was not measured). The world enforces the regulation as if it were physics. In reality a meter can go unread for years (no access, a crossed meter, an account never billed), and that is exactly when 21BA costs the supplier money. Two more problems: the module calls the rule "SLC 31A" and treats it as domestic-only, but Ofgem's decision inserts **SLC 21BA** and extends it to microbusinesses from late 2018 (§2 K3). **Correction 2026-10-05:** the forced read at 12 is gone (W2_36 slice 2, `977e17453`), so the cap now binds from the run. D48 slice 1 measures the barred energy by days, as the money cap is. First real run, 2016–2020: 0.36% of electricity and 0.05% of gas undercharge kWh barred. Full decade (D48 slice 2, 2016 to mid-2025, 175 accounts): **1.05% and 1.25%** (17 and 6 barred true-ups). This is not the W2_36 sweep's 5.5%, which is a different quantity |
| K4 theft, unregistered, unknown occupier, UIG | Company-side registers: `company/billing/theft_risk_scoring_register.py`, `revenue_protection_register.py` (3-year theft back-bill), `revenue_protection_visit_register.py`, `energy_theft_book.py`, `theft_indicator.py` (called by the billing run since 2026-10-17, behind a switch that defaults off: §4b), `company/market/uig_allocation_register.py` (**no caller**, and not on the maturity map), `company/crm/change_of_tenancy_register.py`. **World side: nothing for theft, UIG, unregistered, shipperless or crossed meters anywhere in `sim/` or `simulation/`** (grep) | No | **Absent from the world.** The company has scaffolding to detect things the world never generates, so every register here can only ever read empty. **Update 2026-10-05 (W2_36 slice 3):** the unknown-occupier part now arises in the world when home moves are on. Each move-out carries `unnamed_kwh_expected`: the meter point's annual quantity × `q1_unnamed_months_per_cot` / 12 (`sim/customer_state_layer.py`). Since B7 slice 3 the incoming deemed leg is settled and billed from the move date, and since B7 slice 4 the part inside the window (`unnamed_until`) is booked as occupier debt (`occupier_debt_gbp`), not as paid. Recovery of that debt: GAP. Theft, unregistered and UIG are still absent. **Update 2026-10-16 (W2_36 theft study):** theft now arises at a premise in `simulation/meter_reads.py` (`premise_theft_months`, `premise_theft_study`), as the director ruled on 2026-10-08: a minutes-tier study, not a settled book. Each premise holds a theft state as a stationary two-state chain. The stock is `q6_theft_prevalence_domestic_electricity`, and its turnover is `q6_theft_months_before_detection`, read as the 2011–14 world's mean duration with that era's detection already in it. While a theft runs, the meter registers `1 − q6_theft_share_of_premise_use_unregistered` of true use. No run reads it. **Update 2026-10-16 (screen graded, `tools/theft_void_screen_probe.py`):** an actual/expected ratio screen cannot tell a theft from a void by the ratio, only by the window. An empty calendar month is a theft about nine times in ten; a month under 0.65 flags more private voids than thefts. The third source, occupied homes, is priced on the published run's own book against the company's own expectation (its last three actual reads shaped by the published profile). No occupied home empties a month or a year. But under 0.65 a month flags about 1,800 times per 10,000 premise-years, mostly April to September, and mostly in weather-driven (`fabric_physics`) homes whose seasonal swing is steeper than the profile. That is the expectation's shape error, not low use, and it is more flags than private voids (1,740) or thefts (about 1,100) produce at that cut. In the run a void sits on the incoming account's first stub, so a billing-period screen sees it as an empty period. Whether the world's summer-to-winter swing in those homes matches published heating-season shapes: GAP. Unregistered and UIG are still absent |
| K5 meter faults, crossed meters | `company/billing/meter_dispute.py` (`METER_FAULT`); nothing for crossed meters | Not established | Absent from the world |
| K6 settlement vs billing | `company/regulatory/settlement_reconciliation.py` (Elexon run months, now correct at RF 14), `simulation/settlement_timetable.py`, `simulation/settlement_run_series.py`; `tools/generate_margin_bridge.py` (a money bridge between settlement margin and ledger margin). `EP5_settlement_true_ups` is **0/3, idle** | Reporting only | The revision series is derived from the *billing* estimate and resolves to truth at RF, so by design it does not change the final value. Nothing compares billed kWh to settled kWh (no such module, per grep). No GSP correction and no UIG charge reach cost. The variance bands (±0.5% HH, ±4% NHH) are still uncited (knowledge map) |
| K7 smart read failure | `SMART_METER_NOT_COMMUNICATING_RATE = 0.10`, drawn independently for each customer-period | Yes | It takes a stock (DESNZ, end-2024) and uses it as an independent monthly probability. In reality traditional mode is a *state* a meter stays in (lost WAN, or not adopted after a switch). Neither the hazard nor the persistence is published (§2 K7) |

**A cheap check of K2 against the published record.** If an actual read arrives independently with
probability 1/6 a month, the chance a traditional meter gets no actual read in 12 months is
(5/6)^12 = **11.2%** (the forced read at month 12 then cuts it off). Ofgem's 2017 median supplier
had **5.2–5.6%** of *all* customers without a read-based bill in a year (§2 K2). These are not the
same population: ours is traditional meters only, and theirs includes the then-small smart base and
customer reads. So this is not a refutation. It does say that the read process is the first thing
to calibrate, and that the missing ingredient is **persistence**. In reality, a minority of
households are almost never read and the rest are read regularly. That is what makes back-bills
large and rare rather than small and common. Persistence is not published: **a practitioner
question.**

---

## 6. Gaps

**Knowledge not established (searched, not found):**
1. Per-household persistence of read absence: who goes unread, and for how long. Practitioner.
2. The size distribution of catch-up bills; the number and £ of back-bills; the £ written off under
   21BA.
3. Billing-cycle norms 2016–2025: monthly or quarterly, calendar or anniversary, by payment method.
   This sets how big K1 is. Practitioner (too obvious to anyone in the trade to be written down).
4. The domestic/non-domestic split of the RECCo theft estimate; a detection count after 2014.
5. The electricity GSP-group correction in our window; £ of UIG per domestic gas customer-year.
   Both can be derived from published Xoserve/Elexon data; neither was derived in this pass.
6. How often crossed meters and meter faults happen across the population, and the fast/slow split.
   Researched 2026-10-17: the legal limits and the disputed-meter shares (2003–2014, 2011) are now
   in K5. They bound the referred population only. No 2016–2025 series was found.
7. A second supplier's unbilled balance (only Centrica was read).
8. Per-supplier Citizens Advice billing-accuracy percentages 2016–2025 (published, not extracted).
9. The exact gas reconciliation window (the AUGE says four years; the Xoserve summary said 24
   months).
10. Disputed switch reads: a yearly count and the share upheld; how soon a gaining supplier first
    reads the meter; the in-force REC and UNC Section M wording (§4a, 2026-10-17).

**Commons gap:** `docs/domain_artefact_library/regulatory/` has no artefact for SLC 21BA. The primary
text is the Ofgem decision of 5 March 2018, read here.

**Code gaps, in the order other work rests on them:**
1. The world has no separation between consumed, settled and billed energy (§5 headline).
2. `unbilled_revenue_accrual` measures the wrong quantity, and a second, dead accrual
   implementation duplicates it.
3. The forced read at 12 months makes the back-billing cap unreachable.
4. `EP5_settlement_true_ups` (settlement corrections landing in the books) is unbuilt.
5. The UIG and theft registers are built and never reached, and nothing world-side feeds them.
   **Update 2026-10-17:** `theft_indicator`'s empty-period screen is now called by the billing
   run, behind a switch that defaults off (§4b). On the published run book, switched on, it flags
   16 electricity spans. All 16 are voids and none is a lead, so it raises no charge. The run draws
   no theft (the world's theft is a study), so the switch-on arm cannot yet find one. The other
   registers are still unreached.
6. The back-billing module cites the wrong licence condition and leaves out microbusinesses.
7. The world's closing read is always actual (`simulation/meter_reads.final_read_for`, added
   2026-10-17). Published practice makes it actual only "sometimes" (§4a). So every incoming
   account's opening read is actual whenever a closing read exists, and the empty-period flag
   judges more first periods on the run book than a real book would allow. Filed as
   `SEAT_FINDING_THE_WORLDS_CLOSING_READ_IS_ALWAYS_ACTUAL_2026-10-17.md`.
   **Corrected 2026-10-17:** fixed in code by `600be30bc`, the same morning, and this entry was not
   updated by the two later commits to this page. `simulate_final_read` now makes the closing read
   actual only for a smart meter in smart mode. Any other meter takes the period's ordinary read. The
   customer-given share is the register's GAP row `q6_closing_read_customer_given_share`, which draws
   nothing until sourced. On a replay over the run book, 45 of 137 electricity move-out boundary reads
   stay actual and judged void stubs fall from 17 to 11. The published run book (78f77c34e) predates
   the fix, so the switch-on table in §4b and the 16 void spans were read on always-actual closing
   reads. The 19 Oct publish is the first book on the corrected rule.

---

## 7. What this says about the order of work

**Step 2 has a prerequisite the order does not name: a world in which consumed, settled and billed
are three different numbers.** Today they converge by construction, so the company cannot measure
unbilled energy. Whatever it measures is a timing artefact that always nets to zero. Without that
separation, step 2's "the world must generate unbilled energy the way it arises in reality" has
nothing to stand on, and step 3's forward CLV would be fitted to a book that never leaks revenue.
Evidence: the §5 headline and the `settlement_run_series` docstring; GB UIG is about 2.5% of gas
throughput, and theft is up to 2.8 TWh of electricity and 1.1 TWh of gas a year [H].

**Proposed order inside step 2, by the canon's four tests:**

1. **The definition first, and it is cheap.** Redefine the ledger's "unbilled" as consumption not
   yet billed, and report "billed on estimate" separately, as Centrica does. No world change. It
   makes the existing measurement honest before anything is built on it, and other work rests on it
   (debt work reads "what was billed").
2. **Remove the world's forced read, and replace independent monthly reads with a read state that
   persists** per household and per smart meter. This is the one change that lets K2 and K3 arise
   with a realistic shape. It needs a practitioner answer (gap 1) before any number is chosen, so
   it goes to the director as a question with a recommendation.
3. **Add unknown consumption on the world side (theft, unregistered) and charge its settlement share
   to the supplier**: UIG for gas, GSP correction for electricity. Sourced magnitudes exist for gas
   (the AUG table) and for total theft. The electricity GSP correction needs deriving first (gap 5).
4. **Then EP5**: settlement corrections landing in the books, and a billed-kWh against settled-kWh
   reconciliation in the company. That is revenue assurance proper.

**Something that may be cheaper than it looks: step 2 and the debt lever share one rule.** Under
21BA's "DD set too low" exception (Energy UK, [M]), a DD set too low becomes an unrecoverable
back-bill after 12 months. So the DD-setting work already in flight (SLC 27.15) and back-billing
should be built on one definition of "the charges due", not two.

**Nothing found argues for moving step 2 later.** It points the other way. Until code gap 1 is
closed, every £ of bad debt and CLV is computed on a book that can lose revenue only through
non-payment.

---

## Sources

- Ofgem, *Decision: Protecting consumers who receive backbills* (SLC 21BA), 5 March 2018:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf>. Read as text [H].
- Centrica plc, *Annual Report and Accounts 2024, Financial Statements*: auditor's KAM 5.2; note 3,
  "Revenue recognition – unread gas and electricity meters", p.179; note 17, credit risk and
  "Unbilled downstream energy income", p.213.
  <https://www.centrica.com/media/vakdtnhh/annual-report-24_financial-statements.pdf>. Read as text [H].
- AUGE, *Final Allocation of Unidentified Gas Statement for Gas Year 2024-2025*, v1.2, 31 March 2024:
  <https://www.gasgovernance.co.uk/sites/default/files/related-files/2024-03/final_aug_statement_2024-2025.pdf>. Read as text [H].
- Ofgem, *Tackling Electricity Theft: the way forward*, Impact Assessment, March 2014:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2014/03/electricitytheft-iafinal_0.pdf>. Read as text [H].
- DCUSA, *Schedule 23 – Revenue Protection Code of Practice*, Version 5.11:
  <https://dcusa-cdn-1.s3.eu-west-2.amazonaws.com/wp-content/uploads/2019/08/20104215/Schedule-23-Revenue-Protection-Code-Of-Practice-v1-0.pdf>.
  Read as text 2026-10-17 [H]: §3.3, §4, §9, §13, §15.2–15.7, Appendix 7.
- RECCo, *New report estimates energy theft costs consumers up to £1.4bn yearly*:
  <https://retailenergycode.co.uk/energy-theft-costs-consumers-up-to-1-4-billion-yearly/> [H, page text].
- Ofgem, *Overview of questionnaire responses on theft of energy*, 26 March 2012:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2012/03/overview-of-questionnaire-responses-on-theft-of-energy_0.pdf>. Read as text [H].
- Ofgem, *Open letter: Treatment of low and zero consumers of gas*, 20 June 2014:
  <https://www.ofgem.gov.uk/ofgem-publications/88276/openletter-treatmentoflowandzeroconsumersofgas.pdf>. Read as text [H].
- Elexon, *P245 Modification Proposal: Changes to Long Term Vacant Site Timescales*, 23 October 2009:
  <https://assets.elexon.co.uk/wp-content/uploads/2012/02/28171042/p245_long_term_vacant_site_timescales.pdf>. Read as text [H].
- Elexon, *BSCP504 Non-Half Hourly Data Collection for SVA Metering Systems Registered in SMRS*,
  v53.0, 1 October 2024, §4.4.1 and §4.15.4–4.15.5:
  <https://www.mhhsprogramme.co.uk/api/documentlibrary/Background%20Programme%20Context/P478_BSCP504_v53.1.pdf>. Read as text [H].
- Ofgem, *REC v2.0 – Switch Meter Reading Exceptions* (consultation draft schedule, 15 Oct 2018):
  <https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/rec_v2.0_-_switch_meter_reading_exceptions.pdf>. Read as text [M: draft].
- Joint Office, DWG, *Issue: Shipper / Supplier Agreed Readings* (Jan 2020; UNC Section M, SPAA Schedule 11, ICoSS rules):
  <https://gasgovernance.co.uk/sites/default/files/related-files/2023-08/AOB%206.1%20SAR%20Discussion%20V2.0.pdf> [M].
- Joint Office, *Final Modification Report 0427S* (estimated opening reads, 7 to 10 days):
  <https://www.gasgovernance.co.uk/sites/default/files/ggf/Final%20Modification%20Report%200427S%20v2.0.pdf> [M, search summary].
- Joint Office, UNC 0282 decision (gas vacant sites): <https://www.gasgovernance.co.uk/sites/default/files/ggf/UNC282D.pdf> [M].
- Ofgem, SPAA CP13/239 *TRAS Arrangements: TRAS Product* decision, 2013 [H, letter text]; ENGIE,
  *Energy Theft Risk Assessment Service* customer notice [M].
- Xoserve, *Unidentified Gas (UIG)*: <https://www.xoserve.com/help-centre/demand-attribution/unidentified-gas-uig/> [M].
- Energy Ombudsman, *Annual data 2025*: <https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025> [M].
- Energy UK, *Energy UK Explains: Back billing*: <https://www.energy-uk.org.uk/publications/energy-uk-explains-back-billing/> [M].
- Citizens Advice, *How the scores are worked out* (star rating) [M].
- Elexon, *GSP Group Correction Factors* (BSC settlement page) [M].
- Ofgem, SPAA CP10/190, *Process for the resolution of crossed meters* [M].
- NMRO, *Electricity Meters – Disputed Meter Accuracy Report, determinations 2003–2014*, June 2015:
  <https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/454144/Electricity_Determination_Report_2003-2014.pdf>. Read as text [H].
- NMO, *Gas Meters – Disputed Meter Accuracy, 1 January–31 December 2011*:
  <https://assets.publishing.service.gov.uk/media/5a7c4fa8e5274a2041cf3261/gas-meter-dispute-report-2011v1.pdf>. Read as text [H].
- Ofgem, *Gas Meters – Disputed Meter Accuracy, 1 February 2003–1 January 2004*, May 2004:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2004/06/12304_0.pdf> [H].
- OPSS, *In-Service Testing Handbook* 3.7: <https://assets.publishing.service.gov.uk/media/66bb4394a3c2a28abb50e0d4/In-service-testing-handbook-3.7.pdf> [H];
  OPSS guidance, *Electricity meter accuracy disputes* and *Gas meter accuracy and disputes* (gov.uk) [M].
- DESNZ, *Smart Meters in Great Britain, Quarterly Update December 2025* [H].
- Repo documents read and relied on: `elexon_settlement_run_timetable_verified.md`,
  `meter_read_latency_estimation_2026.md`, `how_far_a_settled_eac_sits_from_next_years_use.md`,
  `settlement_rebilling_best_practice.md`, `unbilled_revenue_accrual_e3.md`.
