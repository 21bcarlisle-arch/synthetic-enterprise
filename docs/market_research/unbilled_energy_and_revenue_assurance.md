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
- **Counts: GAP.** No published annual number of crossed meters or faulty-meter disputes found.
  "Consumption meter error" in gas UIG is −15 to −149 GWh (net over-recording, i.e. it *reduces*
  UIG), [H] AUG table. Electricity meter-accuracy statistics: GAP.

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
| K4 theft, unregistered, unknown occupier, UIG | Company-side registers: `company/billing/theft_risk_scoring_register.py`, `revenue_protection_register.py` (3-year theft back-bill), `revenue_protection_visit_register.py`, `energy_theft_book.py`, `theft_indicator.py` (**no caller**), `company/market/uig_allocation_register.py` (**no caller**, and not on the maturity map), `company/crm/change_of_tenancy_register.py`. **World side: nothing for theft, UIG, unregistered, shipperless or crossed meters anywhere in `sim/` or `simulation/`** (grep) | No | **Absent from the world.** The company has scaffolding to detect things the world never generates, so every register here can only ever read empty. **Update 2026-10-05 (W2_36 slice 3):** the unknown-occupier part now arises in the world when home moves are on. Each move-out carries `unnamed_kwh_expected`: the meter point's annual quantity × `q1_unnamed_months_per_cot` / 12 (`sim/customer_state_layer.py`). It is not yet settled to or billed by the company, because the incoming deemed leg (B7 slice 3) is not supplied. Theft, unregistered and UIG are still absent |
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
6. How often crossed meters and meter faults happen.
7. A second supplier's unbilled balance (only Centrica was read).
8. Per-supplier Citizens Advice billing-accuracy percentages 2016–2025 (published, not extracted).
9. The exact gas reconciliation window (the AUGE says four years; the Xoserve summary said 24
   months).

**Commons gap:** `docs/domain_artefact_library/regulatory/` has no artefact for SLC 21BA. The primary
text is the Ofgem decision of 5 March 2018, read here.

**Code gaps, in the order other work rests on them:**
1. The world has no separation between consumed, settled and billed energy (§5 headline).
2. `unbilled_revenue_accrual` measures the wrong quantity, and a second, dead accrual
   implementation duplicates it.
3. The forced read at 12 months makes the back-billing cap unreachable.
4. `EP5_settlement_true_ups` (settlement corrections landing in the books) is unbuilt.
5. The UIG and theft registers are built and never reached, and nothing world-side feeds them.
6. The back-billing module cites the wrong licence condition and leaves out microbusinesses.

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
- RECCo, *New report estimates energy theft costs consumers up to £1.4bn yearly*:
  <https://retailenergycode.co.uk/energy-theft-costs-consumers-up-to-1-4-billion-yearly/> [H, page text].
- Xoserve, *Unidentified Gas (UIG)*: <https://www.xoserve.com/help-centre/demand-attribution/unidentified-gas-uig/> [M].
- Energy Ombudsman, *Annual data 2025*: <https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025> [M].
- Energy UK, *Energy UK Explains: Back billing*: <https://www.energy-uk.org.uk/publications/energy-uk-explains-back-billing/> [M].
- Citizens Advice, *How the scores are worked out* (star rating) [M].
- Elexon, *GSP Group Correction Factors* (BSC settlement page) [M].
- Ofgem, SPAA CP10/190, *Process for the resolution of crossed meters* [M].
- Repo documents read and relied on: `elexon_settlement_run_timetable_verified.md`,
  `meter_read_latency_estimation_2026.md`, `how_far_a_settled_eac_sits_from_next_years_use.md`,
  `settlement_rebilling_best_practice.md`, `unbilled_revenue_accrual_e3.md`.
