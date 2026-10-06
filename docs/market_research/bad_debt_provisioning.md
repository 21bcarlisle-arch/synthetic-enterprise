# Bad-debt provisioning: what a GB domestic supplier provides for, how, and what our code does

**Knowledge:** bad-debt-provisioning

**2026-10-06, knowledge pass (the director, 2026-10-06: bad-debt provisioning "deserve[s] proper
knowledge work, not a re-check of a toggle value").** This file sits beside
`debt_and_collections.md` (the debt itself: populations, stocks, rules, collections) and answers a
narrower question: **how a supplier turns that debt into a number in its accounts and its price.**
It builds on, and does not repeat:
- `dd_failure_basis_and_live_arrears_provision_rates.md`, which first read Centrica's 2024-25 table;
- `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`, provision versus write-off;
- `practitioner_questions_as_assumption_toggles.md` Q3, the toggles this pass revisits.

**New in this pass:**
1. Centrica's UK residential age x method x live/final provision table, **2019 to 2025, seven
   year-ends**, read from each year's Annual Report Note 17 at source. Earlier passes had two years.
2. Centrica's residential provision roll-forward (opening, charge, write-offs, closing),
   **2015 to 2025**, and its recoveries after write-off, 2017 to 2025.
3. Centrica's published default definitions, write-off trigger, macroeconomic overlay by year,
   and its prepayment-recovery balances and their provision (the "no published prepayment row"
   gap is partly closed).
4. IFRS 9 read at source (EUR-Lex text of the standard): the simplified approach, the provision
   matrix, forward-looking adjustment, the 90-day default presumption, the write-off rule.
5. Ofgem's May 2025 debt-cost decision on what the "bad debt charge" is and why it is noisy.
6. Other suppliers' disclosures (section 3.4).
7. A discovery pass over our code (section 5), which finds the published bad-debt figure is the
   company's own flat assumption, and the harness grades the company on a different quantity
   from the one the company believes.

Every figure carries its source. Anything derived is labelled derived. Anything not established
is marked **GAP**. Text extraction was done with `pdftotext` on the primary PDFs; no figure here
comes from a web summary.

---

## 1. Definitions: what a provision is, and what it is not

Say what each thing counts before splitting or dividing anything. Five quantities get called "bad
debt", and they are not interchangeable.

| Quantity | What it counts | Kind | Where it shows |
|---|---|---|---|
| **Gross receivable** | Money billed and not yet paid, at a date. Includes balances not yet due (a DD customer's in-course balance; a bill inside its 14-day terms) | Stock, GBP, at a date | Balance sheet |
| **Provision (loss allowance)** | The supplier's estimate, at a date, of how much of the gross receivable it will never collect. Under IFRS 9 for trade receivables, a **lifetime expected credit loss**, measured at every reporting date | Stock, GBP, at a date | Balance sheet, netted off receivables |
| **Coverage** | Provision / gross receivable, for a group or bucket | Ratio of two stocks at one date | Notes (Centrica Note 17 "percentage of credit risk") |
| **Bad-debt charge (impairment charge, credit loss)** | The P&L cost of the year: the **change in provision plus write-offs, less recoveries of amounts previously written off** | Flow, GBP, over a year | Income statement |
| **Write-off** | The accounting derecognition of a receivable when there is "no reasonable expectation of recovering" it (IFRS 9 5.4.4). It uses up provision already made; on its own it costs nothing in the year it happens if the provision was adequate | Event, GBP | Movement in the provision |
| **Cash loss** | Money billed and never received, net of anything later recovered. Known only in hindsight, for a closed cohort | Flow over a cohort's life | Nowhere directly; a cohort study |

Three consequences follow, and each is a mistake this repository has made at least once:

1. **The charge is not the write-off.** Ofgem defines the cap's bad-debt cost as *"costs of
   write-offs and provisions in suppliers' accounts"* and measures it as *"Profit and loss charge
   incurred. Costs include write-offs and recoveries, movements in provisions and credit balance
   recognition"* (Ofgem, *Decision, Appendix 2: Debt-related costs*, May 2025, §2.3 and §3.14,
   Option A.2). A model that books only write-offs measures a narrower and much later quantity.
   At Centrica the gap is large: in 2022-2025 the residential charge was GBP 1,160m and residential
   write-offs GBP 391m (section 3.1, derived by summing).
2. **A write-off is not forgiveness and not the end of collection.** *"Enforcement activity
   continues in respect of balances that have been written off unless there are specific known
   circumstances (such as bankruptcy) that render further action futile"* (Centrica ARA, Note 17,
   every year 2018-2025). IFRS 7 35F(e) requires a supplier to disclose *"information about the
   policy for financial assets that are written-off but are still subject to enforcement
   activity"*. At Centrica, GBP 105m of 2025's GBP 135m written off was still under enforcement
   (Note 17 (iv)).
3. **Coverage is a ratio of stocks; the charge rate is a ratio of flows.** "Bad debt is 2% of
   revenue" (a charge over revenue) and "the provision is 40% of receivables" (a coverage) are
   different numbers with different denominators. Neither can be substituted for the other, and
   neither is a probability that a household defaults.

**Provisioning by account type.** The populations of `debt_and_collections.md` §1 are provisioned
on different curves, and the evidence says so directly:
- **Live, direct debit.** Lowest coverage. Much of the balance is not overdue at all: *"Direct
  debit customers typically pay in equal instalments over a twelve-month period"* (Centrica Note 17
  (ii)), so a DD account carries a receivable in the course of normal payment.
- **Live, pay on receipt (standard credit).** Due *"typically within fourteen days of invoicing"*
  (same note). The bulk of the provision.
- **Final (closed) accounts.** *"Final bill customers are those who are no longer customers of the
  Group and have switched energy supplier. These balances are deemed to have the highest credit
  risk"* (Note 17 (iv)). No supply lever remains.
- **Prepayment.** Debt being recovered through a prepayment meter is excluded from Centrica's aged
  table as a *"low residual credit risk amount"*, but it is provisioned, and the provision is
  disclosed in the footnote (section 3.1). It is not aged.
- **Unbilled.** Energy supplied and not yet billed is an asset too, provisioned separately (Centrica
  2020: GBP 324m gross unbilled residential, GBP 17m provision; Note 17). This is where
  `unbilled_energy_and_revenue_assurance.md` meets provisioning.

---

## 2. Method: IFRS 9 as suppliers apply it

### 2.1 What the standard requires (read at source)

Source: IFRS 9 *Financial Instruments*, as adopted in Commission Regulation (EU) 2016/2067
(EUR-Lex CELEX 32016R2067), fetched 2026-10-06. UK-adopted IFRS carries the same text.

- **The simplified approach, 5.5.15.** *"Despite paragraphs 5.5.3 and 5.5.5, an entity shall always
  measure the loss allowance at an amount equal to lifetime expected credit losses for: (a) trade
  receivables or contract assets that result from transactions that are within the scope of IFRS
  15, and that: (i) do not contain a significant financing component ..."* Energy receivables are
  exactly this. So there is **no stage 1/stage 2 test** for a supplier's customer book: every
  receivable carries a lifetime loss allowance from the day it arises.
- **Measurement, 5.5.17.** The ECL must reflect *"(a) an unbiased and probability-weighted amount
  that is determined by evaluating a range of possible outcomes; (b) the time value of money; and
  (c) reasonable and supportable information that is available without undue cost or effort at the
  reporting date about past events, current conditions and forecasts of future economic
  conditions."*
- **The provision matrix, B5.5.35.** *"An example of a practical expedient is the calculation of
  the expected credit losses on trade receivables using a provision matrix. The entity would use
  its historical credit loss experience (adjusted as appropriate in accordance with paragraphs
  B5.5.51-B5.5.52) ... A provision matrix might, for example, specify fixed provision rates
  depending on the number of days that a trade receivable is past due (for example, 1 per cent if
  not past due, 2 per cent if less than 30 days past due, 3 per cent if more than 30 days but less
  than 90 days past due, 20 per cent if 90-180 days past due etc.). Depending on the diversity of
  its customer base, the entity would use appropriate groupings if its historical credit loss
  experience shows significantly different loss patterns for different customer segments."*
  **The percentages in that paragraph are the standard's illustration, not evidence about energy.**
  Two of our unwired tables look like copies of its shape (section 5.1).
- **Forward-looking adjustment, B5.5.52.** Historical loss experience is *"an important anchor"*,
  but must be adjusted *"to reflect the effects of the current conditions and its forecasts of
  future conditions that did not affect the period on which the historical data is based"*, and
  changes in ECL *"should reflect, and be directionally consistent with, changes in related
  observable data ... (such as changes in unemployment rates ... payment status ...)"*.
- **Default, B5.5.37.** Default is defined as for internal credit-risk management, with *"a
  rebuttable presumption that default does not occur later than when a financial asset is 90 days
  past due"*. This is a provisioning definition, not a write-off date (the confusion is recorded in
  `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md` (a)).
- **Write-off, 5.4.4.** *"An entity shall directly reduce the gross carrying amount of a financial
  asset when the entity has no reasonable expectations of recovering a financial asset in its
  entirety or a portion thereof. A write-off constitutes a derecognition event."*

### 2.2 How a supplier actually applies it (Centrica, the one supplier that publishes the detail)

Centrica's Note 17 text, unchanged in substance from 2018 (first IFRS 9 year) to 2025:

- **Matrix by group, then by age.** *"For residential and business customers default rates are
  calculated initially by considering historical loss experience and applied to trade receivables
  within a provision matrix. The matrix approach allows application of different default rates to
  different groups of customers with similar characteristics. These groups are determined by a
  number of factors including: the nature of the customer, the payment method selected and, where
  relevant, the sector in which they operate."* (2025.) 2018 adds: *"The rate of default increases
  once the balance is 30 days past due and subsequently in 30-day increments."*
- **Ageing is by the customer's OLDEST unpaid invoice.** *"This ageing analysis is presented
  relative to invoicing date and presents receivables according to the oldest invoice outstanding
  with the customer."* (Note 17 (ii), 2020-2025.) A customer's whole balance sits in the bucket of
  its oldest invoice. **This matters for our code (section 5.4).**
- **Inputs beyond age.** *"using a combination of the age of the receivable in question, internal
  ratings based on a customer's payment history, and external data from credit rating agencies and
  wider macroeconomic information"* (2025). And *"disposable income analysis from a credit rating
  agency"* (2025).
- **Default definitions.** *"The Group applies different definitions of default for different
  groups of customers, ranging from sixty days past the due date to six to twelve months from the
  issuance of a final bill."* (2018-2025.) Receivables are *"generally considered to be credit
  impaired when the payment is past the contractual due date"*.
- **Write-off trigger.** *"Receivables are generally written off only once a period of time has
  elapsed since the final bill."* (2018-2025.) The length of that period is **not disclosed (GAP)**,
  and Ofgem says suppliers differ on it (Appendix 2, May 2025, §2.19: *"how long they chase up bad
  debt before writing it off"*).
- **Releases flow through the charge.** *"Due to the large number of individual receivables and the
  matrix approach employed, any reduction in provision is reflected in a reduced charge for the
  relevant period, rather than in separately identifiable reversals of previous provisions."*
- **Forward-looking overlay.** A separate "macroeconomic provision" on top of the matrix, sized by
  judgement (section 3.2). In 2024: *"there is a delayed impact on customer payments, such as
  forward-looking macroeconomic challenges ... Accordingly, management includes a macroeconomic
  provision adjustment"*, reduced *"as a result of the initial matrix model starting to more
  accurately reflect some of these forward-looking challenges."*
- **The model itself changes.** 2025's auditor's key audit matter: the provision was produced by
  *"an Ensek model being applied for the first time rather than the previous, well established,
  SAP model"*, and the auditor *"assessed historical debt collection patterns over 2024 and 2025 in
  order to estimate an expected profile of the recovery"*. A supplier's provision is a model
  output, re-estimated from its own cash collections; it can move because the model moved.

### 2.3 What Ofgem says about using provisions as a cost (May 2025)

From *Decision, Appendix 2: Debt-related costs*, May 2025:
- §4.29: *"the bad debt charge includes both provisions in relation to current consumption and
  changes to provisions made in relation to previous consumption. As provisions are refined over
  time, the bad debt charge in any period does not necessarily reflect expected costs in relation
  to consumption in that period. For example, we note one supplier's comment that it made high
  provisions in 2023, leading to a subsequent downward correction in 2024. Second, suppliers'
  provisioning methodologies can change over time."*
- §4.7: 2023 showed record debt-related costs, *"likely leading to rapid changes in provisioning
  policies and large additions to the bad debt charge"*.
- §5.12: *"debt costs will reflect suppliers' own provisioning rates at the time of billing as
  opposed to at the point of consumption"*. The correlation between a supplier's standard-credit
  share and its bad debt plus admin cost is weak, and *"particularly weak when we control for
  suppliers' changes in provisioning methodologies"* (§5.13).
- §3.19: *"Over time provisions will likely converge as revisions to previous provisions are
  made."*

**What this establishes.** The charge in a single year is a noisy, model-dependent, partly
backward-looking number. Grading a world against one year's charge is weak; grading against a
multi-year sum, or against coverage by bucket, is stronger.

---

## 3. Scale and method by supplier and year

### 3.1 Centrica / British Gas, UK residential: provision by age, method and live/final, 2019-2025

Source: Centrica plc Annual Report and Accounts, Note 17, *"Trade receivables due from [British Gas]
residential energy customers as at 31 December"*, each year's report (2025 from centrica.com; 2020-2024
from the annualreports.com archive copies of the same reports), the 2019 column read from the 2020
report's comparative. Provision / gross receivable, %, by days beyond invoice date (oldest invoice).
Coverage is **derived** from the GBP m figures printed in the note; the totals are as printed.

| 31 Dec | DD <30 / 30-90 / >90 | DD all | Pay on receipt <30 / 30-90 / >90 | PoR all | Final bill <30 / 30-90 / >90 | Final all | Gross GBP m (DD / PoR / final) | All three |
|---|---|---|---|---|---|---|---|---|
| 2019 | 0.0 / 0.0 / 2.6 | 1.1 | 3.2 / 15.8 / 38.0 | 24.9 | 22.2 / 50.0 / 75.5 | 70.9 | 94 / 285 / 158 | 34.3 |
| 2020 | 0.0 / 0.0 / 5.9 | 2.4 | 2.6 / 14.3 / 47.7 | 34.8 | 18.2 / 50.0 / 81.4 | 75.2 | 82 / 319 / 161 | 41.6 |
| 2021 | 0.0 / 0.0 / 3.8 | 1.5 | 3.4 / 18.2 / 52.6 | 36.0 | 28.6 / 50.0 / 83.0 | 79.0 | 136 / 303 / 162 | 39.8 |
| 2022 | 0.0 / 0.0 / 34.8 | 6.9 | 3.4 / 13.0 / 62.9 | 41.7 | 25.0 / 46.2 / 79.5 | 74.1 | 333 / 458 / 201 | 36.6 |
| 2023 | 0.0 / 0.0 / 4.1 | 1.3 | 3.5 / 12.7 / 63.4 | 50.9 | 19.0 / 44.4 / 85.8 | 76.8 | 536 / 835 / 280 | 39.2 |
| 2024 | 0.0 / 0.0 / 4.4 | 1.7 | 4.5 / 14.3 / 54.6 | 47.6 | 36.8 / 63.6 / 89.6 | 85.6 | 597 / 960 / 388 | 41.1 |
| 2025 | 0.0 / 1.4 / 7.4 | 2.8 | 4.5 / 15.1 / 50.3 | 44.7 | 31.6 / 57.6 / 87.8 | 84.0 | 674 / 1,270 / 537 | 41.8 |

Pages: 2020 ARA p.139; 2021 Note 17 (British Gas Energy credit risk); 2022 p.168-169; 2023 p.170;
2024 Note 17; 2025 p.175. Small figures are rounded to GBP 1m in the source, so a 0.0% bucket means
"under GBP 0.5m", not exactly zero.

**Prepayment-recovery balances** (Note 17 (i), excluded from the table above, not aged): gross /
provision, GBP m, and coverage (derived): 2019 195/139 (71%); 2020 168/126 (75%); 2021 201/136
(68%); 2022 203/138 (68%); 2023 154/117 (76%); 2024 114/92 (81%); 2025 103/65 (63%). Centrica calls
these *"low residual credit risk amounts"* while provisioning them at 63-81%; the wording is theirs.

**What the table establishes (derived from it):**
- **Method and live/final dominate age.** In every year a final-bill balance under 30 days old is
  provisioned at 18-37%, more than a pay-on-receipt balance 30-90 days old (13-18%). A DD balance
  more than 90 days old is provisioned at 2.6-7.4% (except 2022), and in 2019 and 2024 at less than a PoR
  balance under 30 days old.
- **The shape is stable; the level drifts.** PoR >90 days ran 38% -> 63% (2019 -> 2023) and fell
  back to 50% by 2025. Final >90 ran 75% -> 90% -> 88%. DD stayed in single digits throughout,
  except 2022.
- **2022's DD >90 coverage of 34.8% is an outlier** (GBP 23m on GBP 66m). The same year Centrica
  added GBP 95m of macroeconomic provision (section 3.2); whether the overlay was booked against DD
  balances is **not disclosed (GAP)**. Do not read 34.8% as a matrix rate.
- **The receivable grew 4.6x in six years** (GBP 537m -> GBP 2,481m gross), DD receivables 7x.
  Coverage of the whole book moved only from 34% to 42%. Most of the growth in GBP of provision is
  growth in the receivable, not in the rate.
- **Final bills are 17-29% of gross receivables** (derived: 29% in 2019, 17% in 2023, 22% in 2025),
  and they carry 33-61% of the provision (derived: 61% in 2019, 33% in 2023, 43% in 2025). As the
  live pay-on-receipt book swelled after 2021, the provision's centre of gravity moved from closed
  accounts to live ones.
- **The closed-account rate is 71-86% across the seven years** (84.0% in 2025, the figure the
  brief calls "about 84%"; 70.9% in 2019 is the low end).
- **Most of the provision sits on old debt.** 2025's auditor: of GBP 1,038m credit losses
  recognised on UK residential billed receivables, *"£812m (2024: £609m) relate to customer
  balances in excess of 360 days old"* (Independent auditor's report, key audit matter, ARA 2025).
  Centrica's buckets stop at ">90 days"; the 90-360 and 360+ split is published only in that line.

### 3.2 Centrica: charge, write-offs, recoveries, overlay, charge as % of revenue

**Provision roll-forward, residential customers, GBP m** (Note 17, "Movements in the provision for
credit losses by class", residential column, as published in each year's report).

| Year | Opening | Charge (increase in impairment) | Written off | Closing |
|---|---|---|---|---|
| 2015 | 388 | 109 | 138 | 359 |
| 2016 | 359 | 117 | 81 | 395 |
| 2017 | 395 | 102 | 150 | 347 |
| 2018 | 347 | 85 | 89 | 343 |
| 2019 | 343 | 145 | 101 | 387 |
| 2020 | 387 | 174 | 129 | 432 |
| 2020 restated | 346 | 132 | 78 | 400 |
| 2021 | 400 | 84 | 58 | 426 |
| 2022 | 426 | 234 | 93 | 567 |
| 2023 | 567 | 396 | 113 | 850 |
| 2024 | 850 | 245 | 111 | 984 |
| 2025 | 984 | 285 | 74 | 1,195 |

**Scope caution.** Until 2020 the "residential customers" column is Group-wide and includes North
America (Direct Energy, sold 2021) and Ireland; the 2021 report restated 2020 for continuing
operations (the "2020 restated" row). From 2021 it is UK and Ireland residential. 2016 and 2017 are
IAS 39 incurred-loss years (*"The provision for credit losses is based on an incurred loss model"*,
2016 and 2017 Note 17); IFRS 9 applies from 2018. So the decade is not one consistent series, and
these rows are not a UK-only charge before 2021.

**Recoveries of amounts previously written off, Group, GBP m** (Note 17 footnote, excluded from the
charge): 2017 5 (*"in respect of the sale of debt that had been written off in prior years"*); 2018
7; 2019 6; 2020 15; 2021 7; 2022 7; 2023 8; 2024 10; 2025 3. Against Group write-offs (all classes)
published in the same report: 235, 180, 183, 216, 81, 119, 173, 160, 135. Same-year ratio
(derived; the recovered amounts come from earlier cohorts): 2.1%, 3.9%, 3.3%, 6.9%, 8.6%, 5.9%,
4.6%, 6.3%, 2.2%. **Pooled 2017-2025: GBP 68m / GBP 1,482m = 4.6%** (derived). 2017's line is the
only direct evidence found that Centrica sells written-off energy debt; the price is not given.

**The charge as a share of revenue, and coverage of UK gross receivables** (Audit and Risk Committee
report, "Credit provisions", each year; Note 17 sensitivity paragraph):

| Year | Bad-debt charge / UK energy supply revenue (UK Downstream) | Closing provision / UK energy supply gross receivables | Macroeconomic overlay, GBP m |
|---|---|---|---|
| 2019 | 1.2% | 28% | not disclosed |
| 2020 | 2.2% | 34% | 30 (booked for COVID-19) |
| 2021 | 1.1% | 29% | 30 (maintained) |
| 2022 | 2.1% | 26% | 125 (+95) |
| 2023 | 2.7% as published; 2.9% as restated in the 2024 report | 34% | 175 (+50) |
| 2024 | 2.6% | 38% | 49 |
| 2025 | 2.6% for Retail (Note 17: 2.7% of Retail IFRS 15 revenue) | 38% of Retail gross receivables | 11 |

Residential alone (2024 Strategic Report, British Gas Energy): *"bad debt as a percentage of customer
revenue falling to 2.3% (2023: 3.1%) and 6.1% (2023: 8.0%) for residential and small business
respectively"*. UK Home Energy Supply bad debt: GBP 277m in 2025 (2024: GBP 237m); residential plus
small business GBP 541m in 2023 and GBP 352m in 2024.

**What the series establishes (derived):**
- **The residential charge rate ran 1.1% to 3.1% of revenue over 2019-2025**, at a supplier with a
  standard-credit-heavy legacy book. 2021 is the low (COVID overlay released, support schemes);
  2023 the high.
- **From 2022 the provision stopped being consumed by write-offs.** Charge 2022-2025: 234 + 396 +
  245 + 285 = GBP 1,160m. Written off: 93 + 113 + 111 + 74 = GBP 391m. The stock rose GBP 426m ->
  GBP 1,195m. Before the crisis the two were close (2016-2021: charge GBP 707m, written off GBP
  608m; GBP 665m and GBP 557m with 2020 restated; pre-2021 rows include North America). This is the accounting face of what Ofgem's series shows as arrears: old debt not
  collected and not yet written off.
- **The overlay is the forward-looking leg of IFRS 9, made visible.** It rose with the crisis
  (GBP 30m -> 175m) and was run down as the matrix itself caught up. At its 2023 peak it was 13% of
  Centrica's total credit-loss provision (175 / 1,309, derived; the overlay covers billed and
  unbilled debt across the Group, so the ratio is indicative).

### 3.3 The price cap's allowance against reality

Detail in `debt_and_collections.md` §2.6; the comparison only is drawn here.
- **What the cap allowed.** Cap 13a (Oct-Dec 2024), excluding additional adjustments: DD GBP 25
  (1.4% of the DD cap), standard credit GBP 121 (6.5%), prepayment GBP 10 (0.6%) (Ofgem App. 2
  consultation Dec 2024, Table 2.1). From 1 July 2025 a distinct allowance of **GBP 71 per dual-fuel
  customer, about 3.6% of bills**, covering bad debt, debt administration and debt-related working
  capital together (Ofgem decision overview May 2025, §2.9; App. 2 decision §4.32). The working-
  capital part is benchmarked at about GBP 22 per customer (App. 2 decision §7.13). **The split of
  the remaining GBP 49 between bad debt and administration was not found in the decision text
  (GAP).**
- **What happened.** Centrica's UK residential bad-debt charge alone: 2.3% (2024) and 3.1% (2023) of
  customer revenue. Ofgem's own industry series peaked in summer 2023 *"at well over twice the level
  seen in the previous year"* (App. 2 decision §2.20).
- **The gap that funded the float.** Ofgem found under-recovery for April 2022 to March 2024, set a
  GBP 31 "float" allowance from April 2024, and found the first float over-recovered by about GBP
  2.50 per customer per year (`debt_and_collections.md` §2.6).
- **Like for like.** The allowance is bad debt plus admin plus working capital, per customer, set
  on an industry weighted average of a 2023-24 baseline. Centrica's ratio is bad debt only, one
  supplier, per GBP of revenue. They can be compared in direction and rough size, not equated.

### 3.4 Other suppliers

Read from Companies House statutory accounts, 2026-10-06. **Every filing reached was a scanned
image with no text layer** (`pdfinfo` Creator `go-tiff2pdf`), so these figures were transcribed
from the rendered page images, not extracted by `pdftotext`. Octopus FY2024 Note 14, Octopus FY2023 Note 13 (ageing), OVO FY2024 Note 3 and E.ON Next FY2024
Note 18 were re-read by eye against the page images for this file; the rest are as
transcribed by a delegated read and are marked **[transcribed, single read]**. All figures are
**whole-book** (domestic and business together) unless stated; none of these suppliers publishes a
method x live/final x age table like Centrica's.

| Supplier, entity, year | Gross trade receivables | Provision | Coverage (derived) | Charge in year | Charge / revenue (as stated) | Method text |
|---|---|---|---|---|---|---|
| **Octopus Energy Ltd**, FY to 30 Apr 2024 (Note 14, pp. 38-39) | GBP 1,596.9m | GBP 696.6m | 44% | GBP 211.2m charged to admin expenses; written off GBP 20.3m; GBP 236.3m provision acquired with Shell Energy Retail | 2.9% (FY2023: 1.6%), Strategic Report [transcribed] | *"Provision rates are calculated based on historic non-payment trends ... applied to the different ages, payment methods and supply status of customers"*; ageing by *"payment obligation"* shortfall, not by bill |
| Octopus Energy Ltd, FY to 30 Apr 2023 (Note 13, p. 45; ageing verified) | GBP 825.8m | GBP 270.8m | 33% | GBP 159.6m; written off GBP 35.8m | 1.6% | Ageing table of OVERDUE debtors only (GBP 350.3m gross): 0-3 months 35% covered (37.1/105.1), 3-6 months 56%, 6-12 months 77%, >12 months 92% (127.4/138.2); *"The ageing is based on historic payment behaviour of accounts rather than the age of the specific debt"* |
| **OVO Energy Ltd**, FY2024 (Notes 3, 4, 5, 22; Note 3 verified, figures transcribed) | GBP 1,168m (trade debtors and accrued income) | GBP 651m (2023: 510m; 1 Jan 2023: 252m) | 56% (2023: 47%) | Net impairment GBP 212m (2023: 214m) | 3.9% of revenue excluding EPG income, *"consistent"* with 2023 | IFRS 9 simplified approach; portfolio *"split into segments"* on *"collection rates experienced within each segment"*; 10% worse rates = +GBP 60m. Rise attributed to *"continued suspension of warrant activity increasing the impairment risk on aged debts"* |
| **E.ON Next Energy Ltd**, FY2024 (Notes 2, 5, 18, pp. 30, 41, 50) | GBP 1,787m (2023: 2,001m), of which GBP 1,023m unbilled and accrued (2023: 1,358m) | GBP 1,073m (2023: 1,061m) | 60% (2023: 53%) of gross including unbilled | GBP 284m (2023: 604m) [transcribed] | Not stated; turnover GBP 7,941m (2023: 12,325m) gives 3.6% (2023: 4.9%), derived | *"expected loss rates are based on available external and internal information as well as historical default ratios"*; takes the FRS 101 exemption from IFRS 7, so no ageing table. Its auditor named *"a fraud risk related to inappropriate calculation of the expected credit loss for trade receivables in response to possible pressures to meet profit targets"* [transcribed] |

**What this adds (derived):**
- **The method is the same everywhere it is described:** a matrix by age, payment method and supply
  status (live or closed), rates from the supplier's own collection history. Octopus states the
  three axes in almost Centrica's words.
- **Ageing conventions differ between suppliers.** Centrica ages by oldest invoice; Octopus by the
  shortfall against a payment obligation, explicitly *"rather than the age of the specific debt"*.
  Neither ages bill by bill. That supports section 5.4's finding about our per-bill ageing.
- **Charge rates of 1.6-3.9% of revenue across four suppliers in 2023-2024** (Centrica UK 2.6-2.9%,
  Octopus 1.6-2.9%, OVO 3.9%, E.ON Next 3.6-4.9% derived). The `prov_charge_share_of_revenue_resi`
  band (1.1-3.1%) is Centrica's and sits at the lower half of this; OVO and E.ON Next are higher, on
  whole books and with EPG-distorted denominators. The band's high end is kept at Centrica's 3.1%
  because it is the only residential-only figure; OVO's 3.9% is recorded as the higher witness.
- **Coverage of whole-book receivables of 33-60%** at 2023-24 year-ends, consistent in size with
  Centrica's 41-42% residential. Not comparable bucket by bucket.
- **The pattern of 2022-25 holds across suppliers:** provisions grew much faster than write-offs
  (Octopus wrote off GBP 20.3m against a GBP 211.2m charge in FY2024; OVO's provision went 252 ->
  651 in two years). Everyone named the paused warrant / PPM route as a cause.

**SSE plc (GB household supply until the sale to OVO, January 2020)**, Annual Reports FY2017,
FY2019 and FY2020 (annualreports.com archive copies, text layer, `pdftotext`; key lines re-grepped
for this file):
- FY2019 KPI table, SSE Energy Services (held for disposal), GB domestic: *"Aged debt (GB domestic)
  82.8 76.9"* and *"Bad debt expense (GB domestic) 40.5 42.5"* (GBP m, March 2019 and March 2018).
  FY2017 KPI, GB and Ireland household and small business: bad debt expense GBP 47.9m (2016: 44.0m),
  aged debt GBP 80.2m (2016: 103.2m).
- FY2019 Note A6.2: the discontinued (GB domestic) book's trade receivables GBP 379.2m gross, of
  which GBP 128.4m more than 90 days past due, against an allowance of GBP 79.1m: **21% coverage**
  (derived) of a book whose "not past due" part is GBP 125.9m.
- Method, FY2019 onwards: *"A provision matrix is utilised to estimate the lifetime expected credit
  losses - based on the age, status and risk of each class of receivable - which is periodically
  updated to include changes to both forward-looking and historical inputs."* IFRS 9 adoption
  *"has not resulted in any movement on the calculated impairment provisions"*.
- Not disclosed: a default definition, write-offs separately from the allowance movement, a charge
  as % of revenue, recoveries.

**Not reached (GAP):** ScottishPower Energy Retail Ltd (SC190287) and EDF Energy Customers Ltd /
EDF Energy Holdings Ltd statutory accounts, 2016-2025: every filing sampled is a scanned image and
was not transcribed this pass; years before FY2022 for OVO, Octopus and E.ON Next; OVO Group and Octopus Energy
Group consolidated accounts (downloaded, not read). No supplier other than Centrica publishes a
domestic-only provision.

---

## 4. What a supplier sees and decides

### 4.1 Setting the provision from its own book

Everything a supplier provisions on is its own observation, which is why this is a lever the
company can legitimately hold under the epistemic wall:
- **Grouping:** payment method, live or final, customer type (residential, small business, I&C),
  and, at Centrica, an internal rating from payment history plus bureau data (section 2.2).
- **Age:** days beyond invoice date of the oldest unpaid invoice, in 30-day steps (Centrica 2018).
- **Rates from its own history:** *"recalculation of management's provision rates based on
  historical cash collection ... validation of key metrics such as debt ageing and historical
  recovery rates by customer class"* (Centrica 2025, auditor's response to the key audit matter).
  In credit-risk practice this is a roll-rate or cohort-recovery calculation. **Published roll
  rates and cure rates for GB energy: none (GAP, unchanged from `debt_and_collections.md` §2.5).**
  What is published is the output of that calculation (the coverage table), not its inputs.
- **Forward-looking overlay:** a judgement on top, informed by macroeconomic forecasts and
  affordability data (section 3.2).
- **Default and write-off clocks:** 60 days past due at the earliest; final bills six to twelve
  months after issue; write-off "a period of time" after the final bill (Centrica).

**A practitioner frame we have not checked (third side).** It is ordinary credit-risk practice to
derive bucket rates as the product of roll rates (current -> 30 -> 60 -> 90 -> charged off) from a
supplier's own monthly ageing reports, and to treat a balance whose customer has entered a payment
arrangement as a separate group. Nothing published confirms either for a GB energy supplier. The
director is the source for whether an arrangement re-ages a balance, and whether an account on a
plan sits in its age bucket or its own group. **Asked, not assumed.**

### 4.2 How the provision feeds pricing and forward CLV

- **Pricing.** Ofgem prices bad debt into the cap per customer, by payment method (section 3.3).
  A supplier's own tariff must cover the same cost. The expected loss on a customer's NEXT year of
  billing is a charge rate (flow) from the matrix applied to what that customer is expected to owe,
  not the coverage of today's balance.
- **The leaving premium.** A balance moving from live to final is re-provisioned from the live row
  to the final-bill row. At Centrica 2025: a PoR balance aged 30-90 days goes from 15.1% to 57.6%.
  This is the mechanism `company/pricing/value_based_renewal.py` already prices (section 5.5).
- **Forward CLV (canon step 3).** A customer's forward value is margin less cost to serve less the
  expected credit loss on future billing, with a discount. Three provisioning facts constrain it:
  1. the loss rate depends on payment method and on whether the customer leaves;
  2. the time to recover is long (more than 22 months on average for eligible debt, Ofgem DRS
     impact assessment Nov 2025 §3.10), so time value matters (IFRS 9 5.5.17(b));
  3. Ofgem uses 12.2% a year for the cost of carrying debt (same source).
- **What the supplier cannot see.** The household's true ability to pay. A provision built from the
  company's own ledger is legitimate; one keyed on the world's income-stress draw would cross the
  wall.

---

## 5. What our code does (discovery, the third side)

Read at worktree HEAD `bfa6715d1`, 2026-10-06. Line numbers as found.

### 5.1 The three provision and recovery tables in `company/finance/`

| Module | What it holds | Right | Wrong or missing |
|---|---|---|---|
| `company/finance/bad_debt_provision.py` | `_PROVISION_RATES` by age only: <=30d 0.5%, 31-60 5%, 61-90 20%, 91-180 50%, 180+ 90% (l. 18-24) | Ages a receivable and reports coverage | **No method and no live/final axis**, the two factors Centrica and Ofgem treat as primary. Uncited. Its 31-90-day rates (5-20%) are 3-20x Centrica's DD rows and its 91-180 rate (50%) is 7x Centrica's DD >90 (7.4%). Closest to a PoR-only book |
| `company/finance/debt_age_analysis.py` | `_PROVISION_RATE` by age: 2/5/15/40/80% (l. 44-50). Docstring: "based on UK energy debt recovery experience" | Same shape as IFRS 9 B5.5.35's illustration | Uncited despite the docstring. No method, no live/final. `age_bucket()` measures days since **invoice date** but labels the buckets "days overdue", so a 14-day-terms bill is "31-60 days overdue" at 31 days old |
| `company/finance/debt_collection.py` | `_RECOVERY_PROBABILITY` by collection stage: 0.95 reminder -> 0.65 DCA -> 0.40 legal -> 0 write-off (l. 19-26); docstring cites "Agency recovery rate 60-75p/GBP for energy debts" | Stage-based expected recovery is a legitimate frame | **Uncited and contradicted**: no published source found for 60-75p per GBP on energy debt; the nearest published signals are the final-bill >90-day complement (10-25p, section 3.1) and Lowell's 5.4p all-sector purchase price (`practitioner_questions_as_assumption_toggles.md` Q3) |

All three are **wired to nothing**: no production import outside tests
(`company/finance/bad_debt_reconciliation.py` reports two of them as `unwired`). They disagree with
each other (0.5% vs 2% current; 50% vs 40% at 91-180 days) and with the published table.
**Recommendation: retire them, do not re-source them.** The sourced matrix already lives in
`company/pricing/value_based_renewal.py` (l. 444-460) and is used by
`company/pricing/default_belief.py`. A second sourced copy would be the VAT shape (one rule, several
implementations, one fixed). If a finance-side provision report is wanted, it should import those
rows.

### 5.2 `saas/cost_to_serve.BAD_DEBT_RATE` and `saas/payment_behaviour.py`

- `saas/cost_to_serve.py` l. 69: `BAD_DEBT_RATE = {"resi": 0.02, "SME": 0.01, "I&C": 0.005}`,
  commented *"Bad debt provision as a fraction of revenue"*. **It is a charge rate, not a
  provision**: provision is a stock against receivables. Against published charge rates the resi 2%
  is inside Centrica's 1.1-3.1% (section 3.2), so the LEVEL is defensible as a whole-book charge
  rate. The module docstring (l. 25) says Phase QD *"found the flat BAD_DEBT_RATE formula below
  overstated true bad debt ~30x"*. **That finding compared 2% against the world's write-off-only
  emergent figure, not against any published charge.** On the published record the world's figure
  was the outlier, not the 2% (section 5.3). The docstring should not be read as evidence that 2% is
  too high.
- `saas/payment_behaviour.py` l. 37-42: `DEFAULT_PROBABILITY_BY_CREDIT_RISK` 0.5/2/5/8% of revenue,
  called "default probability" and "provision rate" in one breath. It is applied per bill as a
  haircut (`bad_debt_provision_gbp`). Uncited; four hand-typed customers carry segments, everyone else
  is "medium" 2% (`company/pricing/default_belief.py` docstring says the same).

### 5.3 `saas/ledger.py`: provision, write-off and cash loss in one event

- l. 118-128: `make_payment_received_event` books cash collected = billed minus the provision.
- l. 132-145: `make_bad_debt_event` posts the same provision as a **write-off**, 30 days after the
  expected payment date.
- l. 460-471: every bill gets both events whenever a credit-risk segment is supplied.

So one number is at once the provision, the write-off and the cash shortfall, on every bill,
immediately. That is three of section 1's quantities collapsed into one, and it **cannot be wrong**,
because nothing that happens later feeds back into it (`bad_debt_reconciliation.py`'s own docstring
says so: *"Structurally incapable of ever being wrong"*).

**What the site publishes.** `site/data/dashboard.json` (generated 2026-10-05) carries two
bad-debt series and declares the ledger one authoritative:
- the ledger (management accounts) reads 1.6-3.1% of revenue in every year 2016-2025, 2.0-2.3% in
  most (derived from `management_accounts.annual`);
- the world's realised series (`financial.annual`, arrears-engine write-offs) reads 0.2% to 14%,
  lumpy: 2021 14.0%, 2022 0.0%, 2024 5.3% of revenue (derived).

The "authoritative" figure is the company's own flat assumption. It sits in the published band
because it was set there, not because the world produced it. The world's figure is write-off-timed
on a small book, so a few leavers move it by whole percentage points, and a year with no leaver
reads zero (2022, the crisis year). **Neither series is a provision-based charge.**

### 5.4 The own-book default belief, and what the harness grades it against

- **`company/pricing/default_belief.py`: right in kind.** It computes, per account-year, the
  bad-debt CHARGE (change in provision plus write-offs) the company books off its own ledger, using
  Centrica's 2025 rows for live accounts and the final-bill row once the account reads as closed,
  then shrinks the money-weighted charge share by arrears state towards a 2.0% prior. That is the
  IFRS 9 / Ofgem Option A.2 quantity, built only from company observables. The knowledge map
  (row "The company's own default belief", 2026-10-03) measured it at 2.05% book-wide, monotone in
  arrears state (0.42% clean to 5.55% worsening).
- **Three method gaps against the published practice:**
  1. **Ageing per bill, not per customer.** It ages each unpaid bill FIFO
     (`fifo_unpaid_bills`) and provisions each at its own age. Centrica ages the **whole balance by
     the oldest invoice**. Per-bill ageing provisions the recent bills of a long-standing debtor at
     the <30-day rate (4.5% PoR) where Centrica's convention would put them at the >90-day rate
     (50.3%). It therefore under-provisions persistent debtors relative to the source it cites.
  2. **DD past 30 days is re-rated onto the PoR row** (`value_based_renewal._live_rate`, l. 508-514,
     `DIRECT_DEBIT_REPRESENTATION_WINDOW_DAYS = 30`). Centrica's own table holds GBP 243m of DD
     receivables more than 90 days old at 7.4%, so DD accounts DO carry old balances on a DD footing
     in the source. The re-rating is a modelling choice about what a returned DD becomes, not
     something the table says, and it raises a DD stayer's >90-day rate from 7.4% to 50.3%. **This
     is a practitioner question** (what is a DD balance over 90 days: a live DD customer whose
     instalments run behind consumption, or a returned DD?), not a defect to fix blind.
  3. **One year (2025) held for every year.** Section 3.1 now gives seven year-ends. PoR >90 days
     ran 38-63%, final >90 days 75-90%. A world graded in 2019 against 2025's coverage is graded
     against a post-crisis book.
- **`tools/decision_probe.py`: the harness grades on a different quantity.** Its truth term
  (l. 241-275) charges each renewal decision with the world's **write-offs** on that term's bills
  (`term_bad_debt_shares`, from `simulation.arrears_engine.balance_write_offs`). The world's
  stayer provision (leg 4b, `LIVE_ARREARS_PROVISION_RATES`, `arrears_engine.py` l. 654) is **off by
  default** (`SIM_STAYER_FAILED_DD_BUCKET` unset). So the company believes a provision-based charge,
  and is scored against write-offs, which for a stayer are zero. Before dividing or differencing
  the two, say what each counts: they are not the same quantity, so their gap is not an estimation
  error. Its module docstring (l. 31) still says bad debt is not counted, which is stale.
- **The 2.0% prior** (`PRIOR_LOSS_RATE`, l. 74) cites ASSUMPTIONS.md's 1-3% range, which matches
  Centrica's published 1.1-3.1% charge rate (section 3.2). Keep it, and re-cite it to the series.

### 5.5 `company/billing/dd_collections_desk.py`

- l. 115-127: `DD_STOP_THRESHOLD_CONSECUTIVE_RETURNS = 2`, single-source (British Gas help page),
  the reading caveated. Correct to carry as a named, single-source rule.
- Its provisioning consequence is the point: the stop moves the account from the DD row to the PoR
  row, and in `value_based_renewal` that multiplies by about seven to eleven the provision on the same
  money (DD >90: 7.4%; PoR >90: 50.3%). So this threshold is a provisioning input, and its
  sensitivity should be printed on the charge, not only on collections.

### 5.6 The atoms

- **W2_38 (world debt graded against Ofgem's series):** grades stocks and balances (accounts in
  arrears, average arrears, PPM share). **Add the provisioning shape to its acceptance criteria:**
  the world's own book, provisioned with the company's matrix, should land coverage by method and
  live/final inside the 2019-2025 ranges of section 3.1, and the world's bad-debt CHARGE (not its
  write-offs) inside the published charge band (`prov_charge_share_of_revenue_resi`). Graded, never
  fitted.
- **EP4 (collections journey):** `collections_journey.UNREACHED_EXITS` names write-off as
  unreachable. A provision needs the write-off trigger as a dated event; the published one is "a
  period of time after the final bill" with default at six to twelve months after the final bill
  (`prov_final_bill_default_months`).
- **B11 (forward CLV):** `company/analytics/forward_clv.py` l. 9 and l. 483 state its margin is
  *"before cost-to-serve and bad debt"*. The expected credit loss on future billing is absent from
  the spine every lever is judged against. A forward CLV that omits it values a standard-credit
  household like a DD one, and a likely leaver's final balance at face value.

---

## 6. Gaps

**Knowledge gaps (not estimated):**

| Gap | Where the answer probably is | Route |
|---|---|---|
| Roll rates and cure rates behind any supplier's matrix | Supplier MI; Ofgem SOR flows (unpublished) | Practitioner (the director) |
| How a balance on a repayment arrangement is grouped and aged (re-aged on agreement, or own group) | Supplier policy | Practitioner |
| What a DD balance aged over 90 days is (live DD behind consumption, or a returned DD) | Supplier MI; Centrica's own table implies the former exists at scale | Practitioner |
| The close-to-write-off period | Supplier policy; Centrica says only "a period of time" | Practitioner |
| Bucket coverage beyond 90 days (90-360, 360+) | Centrica publishes only the GBP 812m >360-day line (2025) | Further reads of auditors' reports; practitioner |
| A second supplier's age x method x live/final table | Octopus FY2023 publishes overdue debt by age only (35% at 0-3 months to 92% past 12 months), aged by payment behaviour; no one else splits method or live/final | ScottishPower and EDF filings are scanned images, not transcribed; SSE publishes only a blended allowance |
| The split of the GBP 71 cap allowance into bad debt and administration | Ofgem cap model workbook | A further pass on the model file |
| Debt-sale prices for GB energy | Debt-purchaser disclosures; Centrica 2017 confirms sales happen | A further published-source pass |
| Whether the 2022 DD >90 coverage (34.8%) carries the overlay | Centrica 2022 report does not say | Leave as an outlier |
| NAO material on supplier debt provisioning | Not re-fetched this pass (search budget exhausted); NAO's 25%-on-plans restatement is re-cited in `debt_and_collections.md` | A further pass |

**Code gaps**, in the order they block:
1. **No provision-based bad-debt charge exists on the world side by default**, so the world cannot
   be graded on the quantity Ofgem and every supplier report. (Leg 4b exists, sourced, off.)
2. **The harness grades the company's provision-based belief against write-offs** (section 5.4).
3. **The published bad-debt figure is the company's flat assumption**, which cannot be wrong
   (section 5.3).
4. **Ageing convention differs from the cited source** (per bill vs oldest invoice).
5. **Forward CLV omits expected credit loss** (B11).
6. **Three unwired, uncited, mutually inconsistent tables** in `company/finance/`.
7. **Prepayment debt has a published (unaged) coverage** (63-81%) and the code treats it as having
   none.

---

## 7. Toggles set

All in `docs/market_research/assumption_toggles.yaml`, file schema unchanged (scalar `default`,
`low`, `high`, each with a basis). Coverage toggles are provision / gross receivable at a year-end,
by days beyond invoice date of the oldest unpaid invoice, from Centrica Note 17 2019-2025 (section
3.1). Default = 2025 (the latest year-end); low and high = the extremes of the seven year-ends, each
named.

**Revisited (Q3):**
- `q3_post_write_off_recovery_share`: default 0.05 kept, now on a nine-year pooled basis (Centrica
  2017-2025, 4.6%). Low 0.02 kept (2017 2.1%, 2025 2.2%). **High lowered 0.10 -> 0.086** (2021,
  the highest same-year ratio): the old high rested on "fresher debt fetches more", which has no
  source. **Meaning tightened**: this is recovery after a Centrica-style LATE write-off (after the
  final bill has aged). The world writes off at the final bill's due date
  (`WRITE_OFF_DATE_CONVENTION`), much earlier, so its post-write-off recovery is properly compared
  with the final-bill >90-day complement (1 - coverage: 10-25%, section 3.1), not with this toggle.
  **This corrects Q3's code finding** that the world's DCA 20-30% "sits above every published
  signal": net of 15% commission it is 17-26%, which overlaps that 10-25% band. The constants
  remain unsourced; they are not shown to be wrong.
- `q3_plan_take_up_share`, `q3_instalment_miss_probability_monthly`: **unchanged.** Nothing in the
  provisioning record bears on them. Centrica's shrinking prepayment-recovery balance (GBP 203m ->
  103m, 2022-2025) reflects the paused PPM route, not plan take-up.

**Added (provisioning):**

| Toggle | Default | Low | High | Basis (each end) |
|---|---|---|---|---|
| `prov_coverage_live_dd_30_90d` | 0.014 | 0.0 | 0.014 | 2025; 2019-2024 all under GBP 0.5m |
| `prov_coverage_live_dd_over_90d` | 0.074 | 0.026 | 0.348 | 2025; 2019; 2022 (outlier, overlay year) |
| `prov_coverage_live_por_under_30d` | 0.045 | 0.026 | 0.045 | 2025; 2020; 2024-25 |
| `prov_coverage_live_por_30_90d` | 0.151 | 0.127 | 0.182 | 2025; 2023; 2021 |
| `prov_coverage_live_por_over_90d` | 0.503 | 0.380 | 0.634 | 2025; 2019; 2023 |
| `prov_coverage_final_bill_under_30d` | 0.316 | 0.182 | 0.368 | 2025; 2020; 2024 |
| `prov_coverage_final_bill_30_90d` | 0.576 | 0.444 | 0.636 | 2025; 2023; 2024 |
| `prov_coverage_final_bill_over_90d` | 0.878 | 0.755 | 0.896 | 2025; 2019; 2024 |
| `prov_coverage_prepayment_recovery` | 0.63 | 0.63 | 0.81 | 2025; 2025; 2024 (unaged) |
| `prov_forward_looking_overlay_share` | 0.006 | 0.0 | 0.134 | 2025 (11/1,818); pre-2020 none disclosed; 2023 (175/1,309) |
| `prov_charge_share_of_revenue_resi` | 0.022 | 0.011 | 0.031 | median UK Downstream 2019-2025; 2021; 2023 residential |
| `prov_final_bill_default_months` | 9 | 6 | 12 | midpoint (not a measurement); Centrica's stated range |

DD under 30 days is 0.0 in all seven years and is not a toggle (RESOLVED). Every coverage toggle is
one supplier; the verdicts say so.

**What changed, in one line:** Q3's recovery high came down and its meaning was pinned to write-off
timing; twelve provisioning toggles were added, the first ones in the register that describe how a
supplier accounts for debt rather than how a household behaves.

---

## 8. What this says about the order of work

The canon's step 3 is the forward CLV every lever is judged against; step 5 puts debt forecasting
and negotiating first among levers; W2_38 grades the world's debt before any debt lever is drawn.
The provisioning evidence changes the order inside that, in four ways. Raised, carried on; the
director rules.

1. **Fix the definition before the grading.** W2_38 should grade the world's bad debt as the
   quantity Ofgem and every supplier report (charge = change in provision + write-offs -
   recoveries), not write-offs alone. Concretely: turn the world's stayer provision on (its rates
   are sourced) and settle which row a failed-DD stayer sits in by asking the practitioner question
   in section 5.4 item 2, then grade. Grading write-offs against Ofgem's arrears stocks compares a
   late flow with a stock.
2. **Make the harness and the company measure the same thing before any A/B on default belief.**
   `tools/decision_probe.py` should score the company's belief against the world's charge, not its
   write-offs. Until then a "better" belief can read as worse.
3. **Put expected credit loss into B11 now, from the company's own ledger.** The machinery exists
   (`default_belief.py`). The forward CLV is the spine; a spine without bad debt mis-ranks exactly
   the households a debt lever would target. This is cheaper than EP4 and unblocks it.
4. **Retire before building.** Delete the three unwired `company/finance/` tables and point any
   finance report at the one sourced matrix. Re-key the published board figure from the flat 2%
   haircut to the provision-based charge the company already computes, with the bound its sample
   earns. Both are reversible and small.

Negotiating tools (plan terms, DCA versus sale) stay after the knowledge exists, as
`debt_and_collections.md` §9 already argues; provisioning adds no evidence on take-up or keep.

---

## Sources

All fetched 2026-10-06 and read from the text layer with `pdftotext`, unless stated.

- **Centrica plc, *Annual Report and Accounts 2025*.**
  <https://www.centrica.com/media/ckfb0qxj/annual-report-and-accounts-2025-untagged.pdf>
  Note 17 (pp. 171-176); Audit and Risk Committee report ("Credit provisions"); Independent
  auditor's report (key audit matter on billed debt provision); Strategic report (Retail).
- **Centrica plc, *Annual Report and Accounts* 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
  2024**, archive copies at `https://www.annualreports.com/HostedData/AnnualReportArchive/c/LSE_CNA_<year>.pdf`
  (the published reports as filed). Note 17 in each; Audit and Risk Committee reports 2020-2024;
  2024 Strategic Report (British Gas Energy).
- **IFRS 9 *Financial Instruments*** as in Commission Regulation (EU) 2016/2067,
  <https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R2067>: 5.4.4, 5.5.15,
  5.5.17, B5.5.35, B5.5.37, B5.5.52; IFRS 7 35F(e) (same regulation).
- **Ofgem, *Decision - Appendix 2: Debt-related costs*, May 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-05/Appendix-2-Decision-Debt-related-costs.pdf>
  §2.2-2.6, §2.19-2.22, §3.14, §3.18-3.19, §4.7, §4.18, §4.29-4.33, §5.12-5.13, §7.13.
- **Companies House statutory accounts (scanned images, read from page images):** Octopus Energy
  Limited (09263424), Annual Report and Financial Statements FY2023 (Note 13) and FY2024 (Note 3.1,
  Note 14); OVO Energy Ltd (06890795), year ended 31 December 2024 (Notes 3, 4, 5, 22, Strategic
  Report); E.ON Next Energy Limited (03782443), year ended 31 December 2024 (Notes 2, 5, 18,
  auditor's report). <https://find-and-update.company-information.service.gov.uk/>
- **SSE plc, *Annual Report* 2017, 2019, 2020**, archive copies at
  `https://www.annualreports.com/HostedData/AnnualReportArchive/S/LSE_SSE_<year>.pdf` (2020 file
  name carries a suffix): KPI tables (Retail / SSE Energy Services), Note A6.2.
- **Re-cited, not re-fetched this pass:** Ofgem App. 2 consultation Dec 2024 (Table 2.1); Ofgem
  decision overview May 2025 (§2.9); Ofgem DRS working paper Aug 2025 (§5.20, the 75% blended
  provisioning rate) and impact assessment Nov 2025 (§3.10); Lowell Group year-end report 2013;
  all via `debt_and_collections.md`, `dd_failure_basis_and_live_arrears_provision_rates.md` and
  `practitioner_questions_as_assumption_toggles.md`.
