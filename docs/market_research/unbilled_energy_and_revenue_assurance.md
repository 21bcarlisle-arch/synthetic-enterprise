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
- **Design choice, K2 is published split by meter (2026-10-21, K8 for D48).** The two sources above
  measure different things: BEIS's 6% is a rate among smart customers, DESNZ's 35.8% / 45.3% a share
  of meters. A supplier's blended estimated share is (its traditional share) × (how often those
  meters go unread), plus the smart remainder, so one blended figure cannot say which of the two moved.
  `billing_accuracy.estimated_share_by_year_and_meter` splits it per fuel and year by the meter type
  the supplier holds for the supply point (a national metering record fact, not use). Its share of
  ACCOUNTS on a traditional meter, counted at each account's last bill of the year, is set beside
  DESNZ's end-2024 share of METERS, which is a like count. A bill with no meter type on record is
  "unknown", never guessed. On the 8b6fea024 run: smart meters 7–16% of kWh on estimates, traditional
  75–82%, and 71% of the book's electricity accounts traditional in 2024 against 35.8% nationally
  (`WORKER_FINDING_D48_THE_ESTIMATED_SHARE_IS_FLAT_BECAUSE_NO_METER_IS_EVER_EXCHANGED_AFTER_ACQUISITION_2026-10-21.md`).
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
- ~~**GAP:** the size of the GSP group correction factor in our window, and the £ per domestic
  customer-year a supplier pays for UIG.~~ **Researched 2026-10-17; the answers are below.**

#### What settlement charges a supplier for energy nobody was billed for (2026-10-17)

The two fuels differ in kind. Gas UIG is a **volume** a domestic supplier pays for every year.
Electricity group correction is mostly a **shape** that nets to about zero over a year. Electricity
theft reaches the supplier through line loss factors instead.

**Gas: the domestic UIG share and its price.**
- The price cap carries a UIG allowance: an uplift on the wholesale allowance. It is set from "the
  AUGE forecast of UIG for the Gas Year and the forecast consumption … for End User Category (EUC)
  1ND and 1PD and Profile Classes 3 and 4 (which approximate domestic consumers)". It was **1.86%** for
  July to September 2025, and would have been 1.88% for October to December 2025. [H] Ofgem, *Price
  cap – consultation on the Unidentified Gas allowance in the default tariff cap*, 30 July 2025, ¶11–12.
- Ofgem found that this under-recovered. The AUGE's bottom-up forecast covers 11 of its 25 contributors
  and explained only **64.8%** of benchmark UIG in 2025-26, against 84.1% in 2022-23 (¶21). Ofgem
  proposed **2.90%**: the average *post-reconciliation* UIG as a share of total throughput over gas
  years 2022-23 and 2023-24 (**2.80%**), reallocated to domestic classes by the AUGE's weighting
  factors (¶13, ¶25). That "would add circa **£4.30 per year**" at a benchmark of 12,000 kWh, priced
  at the cap 14b wholesale index (¶14, fn 11–12). Suppliers' own alternative came to 2.91% (fn 19).
  [H] same letter. Post-reconciliation figures for those gas years were then still only "circa
  90-98%" reconciled (¶26).
- Ofgem adopted this as a **temporary method in August 2025**. It re-ran it for October to December
  2026 on gas years 2023-24 and 2024-25, and aims at a long-term allowance from April 2027, built on
  Xoserve's analysis of post-reconciliation domestic UIG. [H] Ofgem, *Energy price cap – Temporary
  Unidentified Gas allowance for cap period 17a*, 9 July 2026, ¶3–7.
- **Derived (our arithmetic on Ofgem's figures):** a 1.04-point uplift worth £4.30 at 12,000 kWh
  implies a wholesale index of about 3.4p/kWh in July to September 2025. At that price the whole
  2.90% is about **£12 per domestic customer-year**. It scales with the wholesale price, so 2022's
  price multiplies it several-fold. The sign of the price risk did not hold through the crisis,
  though: UIG ran **negative** from March 2022 to summer 2023 (K4 above), so NDM portfolios were then
  over-charged. Neither a per-year £ series for 2016–2025 nor the cap's own 2019–2025 percentages were
  extracted here. The cap's Annex 2 model holds the percentages (row 31 and 38, tab '3a Allowances').
- **Two quantities, not one.** `q6_uig_share_of_ldz_throughput` (0.025, range 0.0219–0.0381) is UIG
  over *all* LDZ throughput. What a domestic supplier pays is the domestic-reallocated share: 2.90%
  on the 2022-24 average. Ofgem's reallocation by the AUGE's weights took 2.80% overall to 2.90%
  domestic, so in that period the domestic share sat slightly above the all-throughput share. A build that charges a domestic book the
  LDZ figure undercharges it.

**Electricity: the group correction is a shape, and theft sits in the loss factors.**
- "To a first order of approximation, the volumes of energy allocated by GSPGCF sum to zero over
  the course of a whole year, i.e. the errors in settlement are primarily shape errors rather than
  volume errors." The annualised demand ratios across GSP groups are "centred around a value of 1.0".
  The stated reason: "LDSOs are required to include 'non-technical losses' in their generic Line Loss
  Factors". So the gap between units entering a network and units billed to suppliers is largely
  "accounted for through Line Loss Factors (LLFs), not GSPGCF". [H] Elexon, *Strawman Scaling Factors
  for GSP Group Correction*, PSRG paper, DCP0047 Attachment B, 1 October 2010, §2.1–2.3.
- **The size of the shape:** the mean absolute deviation of GSPGCF from 1.0 across settlement periods
  is "roughly 0.07". That is about 3.5% of NHH energy settled in the wrong half-hour, about 6 TWh a year
  on about 180 TWh of NHH (§2.5, §3.1–3.3). Distribution losses were about 5% of units distributed,
  with theft quoted as an "'anecdotal' figure of 1%" (Sohn Associates for Ofgem, 2009, via §6.1–6.2).
  [H] same paper. **Era:** these are 2010 figures. Correction was extended to HH losses from April
  2013 and to HH import from 2014 (BSC Issue 55 form, Elexon 2014 [H]). Since then, NHH no longer
  carries the whole shape alone. No figure for our window was found.
- **So in electricity, a supplier pays for stolen units as an uplift on its loss-adjusted settled
  volume, pro rata to its share of the group.** It does not pay through a net annual GSPGCF charge.
  An undetected theft on the supplier's own book costs it the unbilled units **plus** a small share
  of everyone's theft through the LLF. A thief on a rival's book costs it only the share.

**What this means for the W2_36 build (step 3 of §7):**
1. **Gas:** charge the supplier its domestic UIG share on settled volume: 2.90% on 2022–24 data,
   and a different figure per gas year. The negative 2022–23 period is part of the record. A flat
   constant over the decade would erase it, so the build reads a series or carries the gap as `None`
   by year. Whether the company may *see* its UIG charge is not in doubt: shippers get it on
   Xoserve's invoices, and it is in the cap.
2. **Electricity:** **no** net annual GSP correction charge on volume. Only a shape term exists, and
   the world's settlement does not model it. The theft cost is a loss-factor uplift, and our world
   has no line loss factors at all (no `simulation/` or `sim/` code names one). That gap is on the
   cost side, outside unbilled energy, and is noted here only so the build does not invent a GSPGCF
   charge to stand in for it.
3. The price cap allowance and the world's charge must be **one number** in a run year. Otherwise
   the company's margin carries a UIG gain or loss that real suppliers did not have on average.

#### What a losing supplier is settled on for its last span (2026-10-19, K8 for leg (b) of the leaver finding)

Asked by `SEAT_FINDING_A_LEAVER_NEVER_READ_BILLS_A_QUARTER_OF_ITS_TRUE_USE_AND_REFUSED_THE_PUBLISH_2026-10-19.md`,
leg (b). This section is written before any build. The rules are already quoted in §4a ("What
trues up a closing read after supply ends" and "The opening read at a change of tenancy"); here
they are set against our code, and the design choices are stated.

**What the rules require** (§4a, BSCP504 v53.0 §4.4.1, UNC TPD M5.13, REC Schedule 30).
- The change-of-supplier read closes the losing supplier and opens the gaining one. It is actual
  if one is valid within SSD ±5 days, otherwise "a valid Old Supplier Estimated reading … must be
  used" and is deemed. Gas works the same way through the opening read the CDSP estimates.
- The losing supplier's NHH settled volume for its last span is the advance from its last
  settled read to that CoS read. Energy recorded after the CoS read is the gaining supplier's: once
  the gaining supplier takes its first actual read, the residual lands on its customer's bill and in
  its settlement. "The CoS reading is assumed to be correct by the Old Supplier, until the Old
  Supplier disputes" it.
- The read changes only through a dispute inside 12 months. Electricity needs a difference over
  250 kWh, gas over 1,200 kWh. The only "shall initiate" falls on the supplier the consumer
  contacted (REC Sch 30 9.4); a supplier's own dispute is a "may". An agreed replacement read
  amends the closing bill too (8.1(b)).

**So, for the losing supplier: consumed = settled = billed, all at the CoS read.** An estimated
CoS read that is too low is not a loss to the losing supplier. It bills less and is charged less,
and the difference moves to the gaining supplier's book at its first actual read. That is a
transfer between suppliers, priced by the dispute rule. The losing supplier creates no value and
loses none.

**What our code does instead.** `simulation/hedged_settlement.run_hedged_term` forms
`revenue_gbp` and `wholesale_cost_gbp` on `consumption_mwh`, the world's true demand, for every
half-hour of the term, including a churned leg's last span. The company's ledger bills the
leaver to the CoS read, which since 2026-10-17 can be an estimate
(`simulation.meter_reads.simulate_final_read`). So on a churned leg that closes on an estimate,
`margin_gbp` counts revenue on energy the company never billed and wholesale on energy it would not
have been charged for. Measured on the 19 Oct book (finding, "Measured"): all 275 estimate-closed
legs carry it, netting about £4,605, of which C7 is about £5,000 on the undercharge side.

**Choices for the build, and why.**
1. **The world settles a churned leg's last span on the CoS-read advance, not on true demand.**
   The span is from the leg's last actual (or last settled) read to its exit. Within it, scale every
   volume field of each settled row by (CoS read − opening read of the span) / (true kWh over the
   span). The profile stays the true one; only the level moves to the read. This keeps the shape
   and makes the span's total equal the billed total. It is a **world** change (W7: the world
   settles as GB settlement does), so it is decided blind to the P&L, and its sign is not looked at
   first.
2. **Scaling hits revenue and wholesale together**, and the levies with them, because every
   per-MWh charge on a supplier's NHH volume is on its settled volume. The standing charge does not
   scale: it is per day, and the leaver is billed for its days.
3. **No dispute is modelled in the first build.** It is a named simplification. A dispute needs a
   consumer who notices, or a supplier that chooses to act, so no rule makes it certain. **GAP:**
   the share of CoS reads disputed, by size of error. Because a dispute moves value between two
   suppliers and creates none, leaving it out moves little in expectation. It does drop the
   variance on legs like C7, which F11 says to name and not to hide.
4. **A half-hourly-settled meter is different, and is out of scope here.** Its settlement is its
   own interval data, not a read advance, so the losing supplier is settled on exactly what it
   supplied, and that same data is a read it can bill. C7 is drawn with a smart meter and HH demand,
   yet returned 42 estimates out of 42. A meter that settles on its data but never yields a billing
   read cannot be both. Which side is wrong (the read stream or the settlement class) is a question
   for the meter-read model. It is recorded in the leaver finding and is not folded in here.
5. **The gaining supplier's side is outside the book** and is not modelled. The residual leaves
   with the customer.

**Prediction for that build, filed now.** On the 19 Oct book, the 275 estimate-closed churned legs'
settled margin moves by about −£4,600 in total (the measured net), and C7 2016–2019 billed/gross
moves above 1 without any read being forced. The 130 legs that closed on an actual read move by
less than £1 each: their CoS read is the true advance, up to the read's own rounding. If any of
those 130 moves by more, the span's opening read is mis-located.

**Re-read before building (worker, 20 Oct): choice 1 cannot be built as written, and the stake has
shrunk.**

*Choice 1 collides with the bill.* The bill is built from the same settlement rows that the margin
sums. `saas/bill_generator.generate_bill` takes the commodity amount as `sum(revenue_gbp) −
sum(standing_charge_gbp)` and the use as `sum(consumption_kwh)`. An estimated bill reuses that
true bill's unit rate (`company/billing/monthly_bill_assembly.py`, `true_bill`). Bills are
assembled only after the run: in phase 4c (`simulation/run_phase4c_on_phase2b.build_monthly_bills`),
and again by `tools/generate_billing_ledger` from the run output. Neither can see a scaled row as
anything but the household's use. So the two ways of scaling a row both fail:

- **Scale `consumption_kwh` and the money together.** The bill's "true" side then becomes the CoS
  read, and the true-versus-billed gap a revenue-assurance screen measures (D48) goes to zero
  by construction. `simulate_read` is also handed the scaled kWh.
- **Scale the money and keep `consumption_kwh`.** The bill's unit rate falls by the scale, and an
  estimated final bill is billed at the wrong rate.

A third problem: the CoS read is only known once the bill run has decided that the last read is
estimated. That run is the company's `final_read_for` call, made after the run, so the world cannot
scale anything while it settles.

*The build shape this implies.* The rows stay true; that is the household's use, and the bill
reads it. The world adds the settlement view **beside** the rows: a per-leg
`cos_read_settlement` entry written in phase 4c once the bills exist. It holds the span (the
trailing estimated run), the billed kWh, the true kWh, the scale, and the change in settled margin.
The settled change is the scale minus 1, times the span's volume-proportional margin: revenue less
the standing charge, less wholesale, policy and network costs. The capital cost and the hedge P&L
are left out, because a forward's P&L is on its own notional, not on the customer's settled
volume. Margin readers (`saas/reporting/annual_report.py`, and the defect-4 sweep's gross) then
add the entry. This choice is new here and replaces choice 1's "scale every volume field of each
settled row".

*The stake, measured on the current base.* By `tools.closing_estimate_run_money.summarise` on
`run_output_59e1658d6_20261019T200818Z.json`, the unpublished book carrying 6208ea6dd (C7's own
registry EAC, leg (d)), the open estimate-closed runs over all 574 closing supply points are:

| | undercharge | overcharge | net (true − billed) |
|---|---|---|---|
| electricity | £2,022 / 10,431 kWh (118) | −£1,698 / −9,664 kWh (101) | £324 / 767 kWh |
| gas | £1,612 / 43,016 kWh (99) | −£2,131 / −36,946 kWh (68) | −£519 / 6,070 kWh |

On 8b6fea024, the electricity undercharge was £6,957 and 45,998 kWh. C7 accounted for about
£4,900 of that, and leg (d) has removed it. **The revised prediction replaces the −£4,600 above:**
on a book carrying 6208ea6dd, the settlement view moves the whole book's settled margin by under
£1,000 in absolute value over the decade. That is under 0.2% of its £555,900 net, and no account
year changes sign against the defect-4 gate. So leg (b) is now a fix to what the margin means, worth
little money. It no longer blocks the publish or lane D. It waits behind leg (c) and is not built in
this turn.

#### A held bill on an account that closes (2026-10-21, K8 for D48)

Asked by `SEAT_FINDING_D48_THE_UNBILLED_ACCRUAL_IS_THE_ENERGY_THE_PRE_BILL_GATE_HELD_2026-10-20.md`.
On the 44a21e3e8 run, from 2021-12 to the run end, the whole of K1's accrual is one leaver's
held estimates: PROS-2017-0117, 2017-12 to its exit on 2018-04-11, 12,825 kWh and £1,635 net. The
domestic-ceiling hold waits for an actual read. On a closed account none comes. Written before any
build.

**What the rules require.**
- SLC 27.17: "all reasonable steps to send a final Bill … within 6 weeks" of the transfer or
  termination (read in `home_moves.md`, electricity SLC p.246). The final bill is the closing
  statement. It runs from the last billed read to the closing read.
- The closing read for a losing supplier is the change-of-supplier read. It is actual if one is
  valid within SSD ±5 days. Otherwise it is the Old Supplier Estimated read, which is deemed. The
  losing supplier is settled on the advance to it. It changes only through a dispute within 12
  months, over 250 kWh for electricity or 1,200 kWh for gas (the section above, and §4a).
- SLC 21BA.1: the final bill may recover only units "consumed within the 12 months preceding" it.
  A supplier failing to work its own hold is not a 21BA.2 exception. Ofgem says not giving a read
  is not obstruction either (`slc_21b_21ba_reads_and_back_billing.md`, S4 p.10).

**What follows for a held estimate once the account closes.**
1. The read the hold waits for will never reach this supplier. After the exit, the meter's next
   read belongs to the gaining supplier. "Held until an actual read replaces it" becomes a hold
   nothing can end.
2. For the losing supplier, the closing read settles the volume question that the ceiling raised.
   Even an estimated closing read is the one it is settled on, so billing it matches what the
   supplier pays for. Withholding the bill does not protect the customer from a wrong volume. The
   published remedy for a wrong closing read is the dispute, which the customer or either supplier
   may raise.
3. The closing read does not settle the other defect the ceiling catches, a business premise
   labelled domestic. That still needs the council tax listing (`release_confirmed_domestic`).
4. An interim estimate the gate held between the last read and the closing read goes out on the
   final bill. That makes the final bill's date the date the energy was billed.
5. An interim older than 12 months at the final bill is barred. It is never billed, so it is a
   write-off, not unbilled energy waiting to be billed.

No published source describes how a supplier's exception queue handles a final bill, or how long
it takes. **GAP.**

**Choices for the build, and why.**
- `build_monthly_bills` stamps `final_bill: True` on a churned account's last bill. Closure is a
  fact the company already acts on when it asks for the closing read.
- `pre_bill_validation.validate_bills` releases a held bill when every reason is consumption
  scale, the account is resi, the address is listed, and the bill is in the account's closing run:
  the estimated bills after its last actual read, through a final bill that is itself on an
  estimate. If the final read is actual, its catch-up already carries the held energy, as before.
  The released copy carries `pre_bill_release` with `issued_with_final_bill`.
- The accrual counts a bill released this way as unbilled at any month end before the final
  bill's month.
- **21BA:** an interim any part of which is outside the 12 months before the final bill
  (`BackBillingAssessment.cap_applies`) stays held. This is conservative: the part a pro-rated copy
  could still recover is not billed. Its energy stays in the accrual's over-12-months column.
  **GAP:** that barred energy is not yet booked to the write-off register.
- **Not built:** a dispute of the closing read. As in the section above, a dispute moves value
  between suppliers and creates none.

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
- **Gas: the Agreed Opening Meter Reading, and since 0811S a corrective one** (UNC TPD Section M
  v6.01, 8 March 2024, read as text 2026-10-17) [H]. The incoming shipper must submit a valid
  opening read by "the 10th Business Day after the Supply Point Registration Date" for a Class 3
  or 4 meter (M5.13.3(b)). Otherwise the CDSP estimates one "for a Read Date which is the Supply
  Point Registration Date" (M5.13.7(c)). The withdrawing shipper "may (if it has bona fide and
  material grounds for doing so)" object (M5.13.10). A replacement is an "Agreed Opening Meter
  Reading … agreed between the Proposing User and the Withdrawing User" (M5.13.11). It cannot
  replace an opening read the registered user itself submitted for the registration date
  (M5.13.11). Section M sets no 12-month window of its own. Modification 0811S added a one-sided
  route "at any time more than two months after the date of the Opening Meter Reading" where no
  agreed read exists. The withdrawing shipper, or the proposing shipper outside the wider tolerance
  band, notifies a Corrective Opening Meter Reading. It stands unless the other side rejects it
  within 20 Supply Point Systems Business Days (M5.13.17–5.13.21). The 12-month window and the
  1,200 kWh threshold come from the supply side: SPAA Schedule 11 then (Joint Office DWG paper,
  Jan 2020) [M], and REC Schedule 30 now (next bullet) [H].
- **Who may raise it, and the customer's part** (REC Schedule 30, *Resolution of Consumer-Facing
  Switching and Billing Problems*, v1.1, effective 4 November 2022, Section C; read as text
  2026-10-17 through the MHHS programme's redline of it, quoting only the base wording) [H].
  Section C covers a read "disputed by the Consumer, Losing Supplier or Gaining Supplier … and
  12 months have not passed since the Supply Effective From Date (or later, where the Energy
  Suppliers have bilaterally agreed to follow this process)" (7.3(a)). It is mandatory for domestic
  suppliers, for NHH electricity and for gas. A supplier "may initiate" the procedure (9.2). Where
  the consumer disputes, the supplier "shall endeavour to reach an agreement with the Consumer
  without invoking this disputes process" (9.3). The supplier the consumer contacted applies the
  threshold (9.4). At 1,200 kWh or less for gas, or 250 kWh or less for electricity, it "shall not
  dispute … unless the Consumer specifically requests a new Switch Meter Reading, but shall instead
  attempt to resolve the dispute with an accommodation (e.g. cash allowance to the Consumer)". Above
  the threshold, or if the consumer refuses the accommodation, it "shall initiate a dispute". If
  both suppliers raise it, the gaining supplier's request takes precedence (9.7). Once a read is
  agreed, the consumer is "sent amended opening and / or closing bills covering the full disputed
  period … corrected for the full period of erroneous data, regardless of whether an equivalent
  correction is applied within settlements" (8.1(b)). The 2018 draft said "should" where the
  in-force text says "shall" on the accommodation. Otherwise it matches.
- **What this means for who starts a dispute** [reasoning from the REC text above]. The only
  "shall initiate" in Section C hangs on the supplier "contacted by the Consumer" (9.4). A
  supplier's own dispute, with no consumer contact, is a "may" (9.2). So nothing in the code makes a
  dispute certain when a switch read is wrong by more than the threshold. A dispute needs a consumer
  who notices, or a supplier that chooses to act, inside 12 months.
- **When the gaining supplier first reads a non-smart meter.** No published distribution was found;
  the rules set the bounds. **Gas** [H, Section M v6.01]: "the User shall use its reasonable
  endeavours to secure that a Valid Meter Reading is obtained and provided to the CDSP at least once
  in the first 12 month period of ownership" (M5.9.10). Failing that, "at least once in the first
  24 months of ownership" (M5.9.11). **Electricity** [H, BSCP504 v53.0]: "Suppliers aren't required
  to read Metering Systems Profile Class 1 to 4 every three months … Suppliers may determine reading
  frequency to meet billing requirements and performance standards" (§4.20, which covers remotely
  read meters; for a meter read by hand, the binding rule is SLC 21B.4 below). Where the switch read fails or
  is missing, the new data collector deems it from "one or two new actual Meter register readings …
  obtained either in line with the reading cycle for that Metering System or obtained as special
  readings". Both reads must fall "within 12 months of the change of Supplier" (§4.5.2). **Both
  fuels** [H, commons `slc_21b_21ba_reads_and_back_billing.md`]: SLC 21B.4 says "take all
  reasonable steps to obtain a meter reading … at least once every year". Before the switch date a
  customer read is accepted from five days before to five days after (supplier guidance) [M]. So
  the first actual read after a switch comes from the gaining supplier's ordinary read process,
  with no switch-specific read obligation. The rules aim it at 12 months at most.
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

**GAPs** (narrowed 2026-10-17; the in-force REC and UNC wording is now read, above):
- **How many disputed switch reads are raised a year, and what share are upheld.** Searched: Elexon
  PAB headline reports, RECCo performance-assurance pages, the Xoserve PARR schedules and the
  ombudsman's annual data. No count found. In December 2022 the gas CDSP itself said "the possible
  volumes for this process are currently unknown" (UNC 0811S Workgroup Report, ROM assessment) [H].
  0811S created a monthly PARR report counting Corrective Opening Meter Readings, with rejection
  shares, by peer and in industry total (PARR Schedule 2A/2B draft, 2023) [H]. If its industry
  totals are ever published, that is the first gas count. It counts only the exceptions route,
  not every agreed read.
- **The distribution of the gaining supplier's first actual read** inside the 12-month bound above.
  It is the same quantity as the ordinary read cadence of a traditional meter (§K2's read classes),
  started at the switch date. Practitioner.
- **Whether an amended final account after a dispute counts as a back-bill under 21BA.** REC 8.1(b)
  asks for correction "for the full period of erroneous data", and the dispute window runs 12 months
  from the switch, so an amended final bill can reach energy more than 12 months old. Neither text
  read says how the two meet.

**What a world build can take from this, and what it must not invent** [reasoning]. The first-read
leg needs no new number: draw the gaining supplier's first actual read from the read process the
world already runs for a traditional meter, starting at the switch date. Mark the 12-month bound
as the rule, not the cadence. A dispute rate has no published anchor. The REC text makes a
dispute conditional on a consumer noticing or a supplier choosing, not automatic above the
threshold. So "every over-threshold undercharge found by a first read inside 12 months is disputed"
is an upper bound, and it is the only honest one. Any result built on it for the £2,222 seed is a
ceiling and must be published as one. The rate stays a GAP row that draws nothing until it is
sourced.

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

**The world leg, and what it reaches** (added 2026-10-17;
`docs/staging/records/SEAT_PREREG_HOW_MUCH_OF_THE_DISPUTE_SEED_A_GAINING_SUPPLIERS_FIRST_READ_REACHES_2026-10-17.md`).
`simulation/meter_reads.gaining_supplier_first_read` draws the first actual read from the meter's
ordinary read process. It uses the same household, read class and smart-mode state, month by month
from the switch date, with no new cadence. `switch_read_dispute` makes a dispute possible only for
an undercharge over the threshold whose first read falls inside 12 months. The default reads the
GAP row `q6_switch_read_dispute_share` and raises none. The `ceiling` arm raises every possible one.
On the graded run, the ceiling reaches **£701 of the £2,222, across 12 of the 17 runs**. The other
£1,522 sits on 5 households whose next supplier also gets no read within the 12 months. C7 (£1,431)
is one of them, in the hard-to-read class. So the read process limits the seed more than the
dispute rate does. The ceiling assumes the agreed read is the true register and keeps the 21BA bar.
Nothing in a run raises the dispute yet: the company has no amended-final-bill path (REC 8.1(b)).

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

### 4c. A domestic-ceiling hold the council tax list cannot answer (2026-10-21, K8 for D48)

**What the rules require.** The VAT reduced rate on fuel and power applies to a "qualifying use":
supply to a dwelling, or supply under the de minimis. The de minimis is 33 kWh a day or 1,000 kWh a
month of electricity, and 145 kWh a day or 4,397 kWh a month of gas [H] HMRC, *VAT Notice 701/19*,
s.3.2.1, 4.2, 5.2. "The provider must be certain that the supply is to a dwelling" (s.3.2.1). A
supplier that applies the reduced rate wrongly "and cannot satisfy us that you have taken reasonable
steps" pays the VAT it undercharged (s.3.1). Where a premises is in mixed use, the supplier "should
obtain a certificate from your customer" declaring the qualifying percentage (s.3.5). In England and
Wales the council tax list is public. In Scotland the list is kept by the Scottish Assessors, also
public, and searchable by address [H] gov.scot, *Council tax*. So a dwelling anywhere in GB is
somewhere a supplier can look up.

**What follows for a hold the list cannot answer.** No published source describes a supplier's
exception queue for this. Two steps follow from the rules above. (1) An address absent from the list
is a reason to ask the customer, not to bill at 20%: the guidance puts the burden on reasonable
steps, and its own instrument for an uncertain premises is the customer's declaration. (2) An answer
of "not a dwelling" is a business supply. The account is re-segmented, and the bill issues at the
standard rate. No published source gives the time a supplier takes over either step.

**What the model does, and why.** In this world every domestic supply point is at a dwelling the
world either drew (`live_premises`) or authored (the hand-authored founders' `home_type`), and a run
refuses a resi electricity account with neither (`dwelling_records.build_properties` raises
`DwellingNotDrawn`). So the world's listing answers for every domestic address it supplies.
Until 2026-10-21 it did not answer for the authored ones. The four held actual-read bills on
OCC-d8e674fa38de, at founder C8's semi, were held for that reason and no other.
`simulation/run_phase4c_on_phase2b._authored_dwellings` is the fix. **Design choice:** the
contact/certificate route and the re-segmentation route are not built. In this world no domestic
hold reaches the queue without a listing answer, so either route would be a mechanism nothing
reaches. **GAP:** an address genuinely missing from the list (a new build before banding, a
conversion) is not modelled. That is the population the two steps above would serve.

### 4d. A domestic-ceiling hold on an estimate at a rate the account's own meter has measured (2026-10-21, K8 for D48)

Asked by the grade of the first run carrying the held-bill releases
(`docs/staging/records/WORKER_PREREG_D48_THE_FIRST_RUN_CARRYING_THE_HELD_BILL_RELEASES_2026-10-21.md`).
On the 9ca972774 run, 40 bills are held, all estimates and all on listed dwellings. 32 of them are
one account, PROS-2017-0336, a listed dwelling whose meter reads 2,500-5,000 kWh a month. Each of its
estimates is over the ceiling, so each waits for an actual read. From 2019-04 to 2020-05 it was sent
no bill at all, then one catch-up of £5,067 for 14 periods at 2020-06-30.

**What the rules require.**
- "At least twice yearly" a bill or statement [H] SLC 21B.5 (`back_billing_and_liability.md` §12).
  A hold that waits for a read the meter does not give for 14 months breaches it.
- A dwelling takes the reduced VAT rate at any volume [H] HMRC VAT Notice 701/19 s.3.2.1 (§4c). So
  once the listing answers, the only question the ceiling still asks of an estimate is whether its
  VOLUME is wrong.
- 21BA limits what the late catch-up can recover (§12, point 3), so a long hold also puts the
  supplier's own revenue at risk.

**What follows.** The ceiling's volume half exists to catch an estimate that is wrong in scale, such
as a month's energy put on a seven-day stub (§4c, `release_confirmed_domestic`). It is a population
screen with no source (`need_domestic_electricity_high_tail.md`: "observed sim population plus
headroom"). For one account, the better evidence is that account's own meter. If an earlier actual
read on this supply point already measured a daily rate at least as high as the estimate's, the
estimate is not wrong in scale. Holding it protects nobody: the energy is billed anyway, later and
all at once. An estimate above anything the meter has measured, or on an account with no actual read
yet, is the case the screen exists for, and it stays held.

**No published source** describes how a supplier's exception queue treats a high-volume estimate on
a confirmed dwelling. **GAP.** The rule above uses no threshold. It compares the estimate with a rate
the supplier has already measured at the same meter.

**Choices for the build, and why.**
- The measured rate is the read-to-read rate: an actual-read bill's own kWh, plus the kWh its
  catch-up reconciled (billed and true-up), over the days from the end of the previous actual-read
  bill to its own period end. It uses only the company's own bills from before this one, so the
  company knew it when it billed.
- The release is decided in one function, `pre_bill_validation.release_on_measured_rate`. Both the
  issuance door (`validate_bills`) and the assembly's catch-up (`monthly_bill_assembly`) ask it. If
  they disagreed, a released estimate would be counted as billed nothing, and billed a second time by
  the next read's catch-up.
- The released bill is a marked copy carrying `pre_bill_release`, as the other two releases are.

### 4e. A meter already on supply is exchanged for a smart one (2026-10-21, K8 for W2 / D48)

Asked by the measure of the 8b6fea024 run: 0 of 945 accounts changed meter type in their life, so
the book was 29% smart in 2024 against 68.9% nationally, and K2's blended estimated share stayed flat
(`WORKER_FINDING_D48_THE_ESTIMATED_SHARE_IS_FLAT_BECAUSE_NO_METER_IS_EVER_EXCHANGED_AFTER_ACQUISITION_2026-10-21.md`).
The meter was drawn once, at acquisition, and nothing changed it afterwards.

**What the published record says.**
- The national installed stock of domestic smart meters: 10.6% (2016) to 68.9% (2024). [H] DESNZ,
  *Smart Meter Statistics in Great Britain: Q4 2024*, Table 5a. This is already the series behind
  `premise_population.smart_meter_penetration`, interpolated linearly between the two ends and held
  flat outside them.
- Nearly all of that stock was fitted to premises that were already on supply. The roll-out was an
  exchange programme: suppliers fitted smart meters at their own customers' existing supply points,
  under the roll-out duty in their licences (an "all reasonable steps" duty to 2020, then annual
  install targets from 2022). [M] The licence condition numbers and target levels were not read this
  pass: **GAP**, the next read is the commons. A meter fitted when a supply point is first connected
  is a small share of the flow.
- A meter exchange is a fact the supplier holds about its own supply point. The meter's details
  are on the national metering record and arrive in the industry flows, and the supplier, or its
  installer, fitted it.

**The conditional hazard.** If the stock reads p(y) at the end of year y, and only meters still
traditional can be exchanged, then the chance that a traditional meter is exchanged during year y
is h(y) = (p(y) − p(y−1)) / (1 − p(y−1)). For a household drawn smart at acquisition with
probability p(A) and exchanged at h(y) in each later year, the chance of being smart at the end of
year Y is 1 − (1 − p(A)) · Π(1 − h(y)) = p(Y), because the product telescopes. So every cohort, of
any acquisition year, carries the national stock. On the linear series h runs from 8.2% (2017) to
19.0% (2024) and is 0 in 2025, where the series is held flat.

**GAP: in-book versus national.** No published series separates a supplier's installs at its own
supply points from the national stock. For example, there is no evidence on whether switchers are
fitted faster or slower, whether a small supplier's install rate differs from a large one's (DESNZ
does publish the smart-mode share by supplier size, §K7, but not the install hazard), or whether
prepayment or vulnerable households are fitted at a different rate. The national hazard is the
stated belief. It is a belief about an average, not a measured supplier rate.

**Choices for the build, and why.**
- **Where it is drawn.** `life_events.smart_meter_installed_event` emits the `smart_meter_installed`
  event that already existed and that `apply_events` already handled. It draws from its own
  per-premise substream, so no other draw moves. The draw is keyed on the premise, not the account,
  so a dual-fuel home's two legs are exchanged in the same visit, which is how a dual install is
  done.
- **Where it acts.** The world's read feed (`meter_reads.SimulatedReadFeed`) reads every period
  against the meter in force at that period's end, not the acquisition stamp. The meter on the wall
  decides how the read arrives. The company is not asked what it thinks the meter is.
- **What the company sees.** Each read event already carries the meter that took it, and the
  published meter-read log is projected from those events. After an exchange, the supply point's
  reads arrive from a smart meter. That is the observable, the same fact the acquisition stamp
  already rendered, and no future date crosses the wall: the company learns of an exchange only from
  a read taken after it.
- **Behind a switch, default off.** Turning it on moves every traditional account's reads after its
  exchange date, which moves the world digest. The per-customer, opex-credit, bad-debt and
  retention-netting arms are being graded on the current world. So the switch lands off, and turning
  it on waits for those grades and the value-arms re-take that follows.
- **Not built:** a smart meter that drops back into traditional mode (§K7, hazard unpublished), and
  a different hazard for gas, which follows the same series because the repository holds one.

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
| K1 accrual | `saas/ledger.py:unbilled_revenue_accrual` (L309) → `saas/reporting/annual_report.py:_section_unbilled_revenue_accrual`. A second implementation, `company/finance/revenue_accruals.py` (`RevenueAccrualsLedger`) with `company/finance/period_reconciliation.py`, has **no non-test caller**. `E3_accrual_restatement` is closed at 2/2 with its Expert Hour `not_attempted` | Yes (report only) | **Mis-defined.** It adds up the *whole amount* of every estimated bill that no catch-up covers yet. That is the *billed-on-estimate* part of Centrica's "unread revenue", not "unbilled revenue" (consumed and not yet billed). It does not measure the estimate's error, and it does not measure consumption since the last bill. Bills are calendar-month (`monthly_bill_assembly._billing_month`) with a 5-day read cutoff, so true period-end unbilled consumption is close to zero by construction. **Update 2026-10-05 (D48 slice 2):** renamed `estimated_billing_outstanding` by another lane the same day. It also kept, for ever, every estimate a read had closed with a correction under the £5 materiality threshold: 83% of the decade run's £93,059. Corrected: a read now ends the run. `company/billing/billing_accuracy.estimated_billing_outstanding_grade` grades each run open at a month end against its later read. Decade run, runs open at a year end: net +10% (electricity), +24% (gas) of the run's billed kWh under-billed. At a June month end: −2% and −26%. The trailing-mean estimate carries the season into every period-end position. **Update 2026-10-06 (D48 slice 3):** the company now shapes its own estimate by a published monthly profile (`company/billing/unread_month_estimate.py`, sources in `how_a_supplier_shapes_an_estimate_for_an_unread_month.md`). Same world, one variable: December net +3.2% (electricity) and −6.5% (gas); June +1.6% and −3.8%. Gas gross fell from 53% to 16%; electricity gross did not fall **Update 2026-10-20 (D48, the accrual itself):** unbilled energy is now computed, beside the billed-on-estimate figure and never added to it: `company/billing/billing_accuracy.unbilled_accrual`. Per account at a month end, the company's own figure for each period (the actual read, or the estimate it made from its last reads, the registry EAC/AQ or TDCV, already on the bill) less what it ISSUED. Every account is billed every calendar month to the month end, so the only used-and-not-charged energy is a bill the pre-bill gate HELD: a held estimate stays unbilled until an actual read ends its run (E3's rule, `saas.ledger.open_estimated_bills`, reused); a held actual-read bill, and any catch-up it carried, is never billed. Valued at the held bill's own price, net of VAT. **Design choice:** the accrual does not re-estimate a period with a second estimator (an annualised-advance EAC), because the difference between two of the company's estimators is not energy used and not billed. **GAP:** a real supplier closing on a date between bill runs carries part of a month unbilled on every account; calendar billing to the month end makes that zero here by construction, so this figure is the billing-failure part of K1 only. SEAT_FINDING_D48_THE_UNBILLED_ACCRUAL_IS_THE_ENERGY_THE_PRE_BILL_GATE_HELD_2026-10-20.md |
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
5. ~~The electricity GSP-group correction in our window; £ of UIG per domestic gas customer-year.~~
   **Answered 2026-10-17 (K6):** domestic UIG is 2.90% on 2022–24 data, about £12 per year at 2025
   prices. GSPGCF nets to about zero over a year, and electricity theft sits in loss factors. **Still
   open:** the cap's UIG percentage by year for 2019–2025, and a GSPGCF figure from inside our window.
6. How often crossed meters and meter faults happen across the population, and the fast/slow split.
   Researched 2026-10-17: the legal limits and the disputed-meter shares (2003–2014, 2011) are now
   in K5. They bound the referred population only. No 2016–2025 series was found.
7. A second supplier's unbilled balance (only Centrica was read).
8. Per-supplier Citizens Advice billing-accuracy percentages 2016–2025 (published, not extracted).
9. The exact gas reconciliation window (the AUGE says four years; the Xoserve summary said 24
   months).
10. Disputed switch reads: a yearly count and the share upheld (none published; the gas CDSP called
    volumes "unknown" in 2022); the distribution of the gaining supplier's first actual read
    inside the 12-month rule bound. The in-force REC Schedule 30 and UNC Section M wording was read
    on 2026-10-17 and is no longer a gap (§4a). The world now draws the first read from §K2's read
    process and runs the dispute only as a ceiling arm; the share raised is register row
    `q6_switch_read_dispute_share`, null.

**Commons gap:** `docs/domain_artefact_library/regulatory/` has no artefact for SLC 21BA. The primary
text is the Ofgem decision of 5 March 2018, read here.

**Code gaps, in the order other work rests on them:**
1. The world has no separation between consumed, settled and billed energy (§5 headline).
2. `unbilled_revenue_accrual` measures the wrong quantity, and a second, dead accrual
   implementation duplicates it.
   **Update 2026-10-20:** renamed `estimated_billing_outstanding` (2026-10-05); unbilled energy proper is
   `billing_accuracy.unbilled_accrual` (K1 row above).
3. The forced read at 12 months makes the back-billing cap unreachable.
4. `EP5_settlement_true_ups` (settlement corrections landing in the books) is unbuilt.
5. The UIG and theft registers are built and never reached, and nothing world-side feeds them.
   **Update 2026-10-17:** `theft_indicator`'s empty-period screen is now called by the billing
   run, behind a switch that defaults off (§4b). On the published run book, switched on, it flags
   16 electricity spans. All 16 are voids and none is a lead, so it raises no charge. The run draws
   no theft (the world's theft is a study), so the switch-on arm cannot yet find one. The other
   registers are still unreached.
6. ~~The back-billing module cites the wrong licence condition and leaves out microbusinesses.~~
   **Corrected 2026-10-17:** it was fixed on 2026-10-05 (`65329aa39`), and this entry was never
   updated. `company/billing/back_billing.py` now cites SLC 21BA and covers microbusinesses from
   1 November 2018. Whether a customer is a microbusiness is the caller's fact, and no production
   caller supplies it yet (the registered gap `microbusiness_back_billing_cap`).
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
  v53.0, 1 October 2024, §4.4.1, §4.5.2, §4.15.4–4.15.5 and §4.20:
  <https://www.mhhsprogramme.co.uk/api/documentlibrary/Background%20Programme%20Context/P478_BSCP504_v53.1.pdf>. Read as text [H].
- Ofgem, *REC v2.0 – Switch Meter Reading Exceptions* (consultation draft schedule, 15 Oct 2018):
  <https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/rec_v2.0_-_switch_meter_reading_exceptions.pdf>. Read as text [M: draft].
- Joint Office, DWG, *Issue: Shipper / Supplier Agreed Readings* (Jan 2020; UNC Section M, SPAA Schedule 11, ICoSS rules):
  <https://gasgovernance.co.uk/sites/default/files/related-files/2023-08/AOB%206.1%20SAR%20Discussion%20V2.0.pdf>.
  Read as text 2026-10-17 [H for what it says; [M] for the SPAA rules it summarises].
- RECCo, *REC Schedule 30 – Resolution of Consumer-Facing Switching and Billing Problems*, v1.1,
  effective 4 November 2022, Section C. Read as text 2026-10-17 in the MHHS programme's redline
  (MHHS-DEL1516 v0.3), base wording only:
  <https://www.mhhsprogramme.co.uk/uploads/eed6956a-6182-4795-9a38-799fad2361c2/MHHS-DEL1516-REC_Schedule_30_-_Resolution_of_Consumer_Facing_Switching_and_Billing_Issues_v0.3.pdf> [H].
- Joint Office, *UNC TPD Section M – Supply Point Metering*, v6.01, 8 March 2024, M5.9.9–5.9.12 and
  M5.13: <https://gasgovernance.co.uk/sites/default/files/related-files/2024-03/15_tpd_section_m_-_supply_point_metering.pdf>. Read as text [H].
- Joint Office, *UNC 0811S Workgroup Report* (Shipper Agreed Read exceptions), 12 December 2022:
  <https://gasgovernance.co.uk/sites/default/files/2023-05/302.12%20a%29%20Workgroup%20Report%200811.pdf>;
  and *Draft PARR Reports – Modification 0811S* (2023):
  <https://gasgovernance.co.uk/sites/default/files/2023-07/5.2%20b%2529%20DRAFT%20PARR%20Reports%20-%20Modification%200811S%20-%20For%20Review.pdf>. Both read as text [H].
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
- Elexon, *Strawman Scaling Factors for GSP Group Correction*, PSRG, DCP0047 Attachment B, v0.1,
  1 October 2010: <https://assets.elexon.co.uk/wp-content/uploads/sites/11/2012/02/28172513/dcp0047_attachment_b.pdf>. Read as text [H].
- Elexon, BSC Issue 55 form, *Review of the approach to the calculation and application of GSP Group
  Correction Scaling Weights*, 2014: <https://assets.elexon.co.uk/wp-content/uploads/sites/11/2014/02/28164701/Issue_55_Form_v1.0.pdf>. Read as text [H].
- Ofgem, *Price cap – consultation on the Unidentified Gas allowance in the default tariff cap*,
  30 July 2025: <https://www.ofgem.gov.uk/sites/default/files/2025-07/Energy-price-cap-additional-wholesale-allowance-unidentified-gas.pdf>. Read as text [H].
- Ofgem, *Energy price cap – Temporary Unidentified Gas allowance for cap period 17a*, 9 July 2026:
  <https://www.ofgem.gov.uk/sites/default/files/2026-07/Energy-price-cap-update-for-the-unidentified-gas-allowance-October-to-December-2026.pdf>. Read as text [H].
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
