# Debt and collections — what a GB domestic energy debt is, how big it is, the rules, and what our code does

**Knowledge:** debt-and-collections

**2026-10-05, knowledge pass (director's canon of 2026-10-05, step 1).** This file CONSOLIDATES
five notes already on disk and fills their gaps. It does not repeat their working; it cites them.
- `company_debt_management.md`: the lifecycle and the PPM terms. §7 is marked UNSUPPORTED.
- `gb_domestic_bill_payment_failure_and_arrears_prevalence.md`: the six quantities, and the Ofgem
  dashboard read as text.
- `dd_failure_basis_and_live_arrears_provision_rates.md`: there is no DD failure rate; the Centrica
  provision table.
- `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`: provision versus write-off.
- `domestic_debt_objection_rates_gb.md`: the SLC 14 objection.
- `domestic_repayment_plan_take_up_and_keep_rates.md`: plan take-up and breakage.

**New in this pass:**
1. **The full Ofgem quarterly series, 2006–Q2 2026, reached as data.** Earlier notes said it was
   unreachable. The charts are Everviz embeds, and `https://app.everviz.com/inject/<chart-id>/`
   returns each chart's config with its CSV inline. Chart ids are in the page HTML as
   `highcharts-<id>`. The series are in §2.1.
2. The 2025 price-cap debt allowance decision, and the 2023–25 float and ASC adjustments.
3. The involuntary-PPM rules, with the debt-trigger amount from the guidance itself.
4. The Fuel Direct deduction rates (DWP guidance V19).
5. The DRS impact assessment's recovery-time and collection-cost figures.
6. Centrica's 2025 bad-debt charge, write-offs and recoveries.
7. Energy UK's payment-method split of the debt stock.
8. A survey of what the code does today (§7).

**2026-10-08 pass:** §10 adds vulnerability as a hidden household state. It covers PSR and
financial-vulnerability prevalence, onset, the arrears overlap measured on one Ofgem instrument,
and how much a supplier knows. It sets the `vuln_*` assumption toggles.

Every figure carries its source. Where nothing establishes a quantity, it is marked **GAP**.
Nothing here is estimated to fill a slot. Anything this file derives is labelled as derived.

---

## 1. What a domestic energy debt is, and its distinct populations

**Definition, before any split.** A domestic energy debt is a sum the supplier has billed (or
should have billed) for energy supplied, plus standing charges, that has not been paid by the
date it fell due. Three things are said about it that are NOT the same quantity:

- **A payment event.** A direct debit returns unpaid, or a pay-on-receipt bill passes its due date.
  It is a flow over presentations or bills.
- **A balance.** An amount owed on an account at a point in time.
- **A loss.** The P&L charge, made of provisions plus write-offs, net of recoveries.

Ofgem's own statistical definitions both use a **91-day** bar (Ofgem, *Debt and arrears
indicators*, methodology):
- **"In arrears"** is a bill unpaid for more than 91 days with no repayment arrangement.
- **"In debt"** is a formal repayment arrangement lasting more than 91 days. It includes every
  PPM customer repaying a debt.

The two are mutually exclusive, and both are end-of-quarter stocks.

**Definition does not end at the bill.** A customer who has not paid is not one population. The
populations below have different triggers, different remedies, different legal clocks, and
different recovery curves. They must be measured separately.

| # | Population | What triggers it | What the supplier can do | Why it is a separate population |
|---|---|---|---|---|
| P1 | **Credit-meter arrears, live account, direct debit** | A DD returns, is re-presented up to twice within 30 days (Bacs rules via bureaux; British Gas: retry after 14 days, then DD cancelled), or the fixed DD is set below consumption so a balance builds up | Re-present the DD; review the DD amount; SLC 27 payment-difficulty steps; repayment plan; PPM (voluntary, or involuntary under SLC 28B) | Lowest loss. Centrica 2025: DD live receivables 2.8% provisioned overall, 7.4% past 90 days |
| P2 | **Credit-meter arrears, live account, standard credit (pay on receipt)** | The bill is not paid by its due date | As P1, without the DD mechanics | The core of the debt stock. Energy UK: SC is about 16% of households (DESNZ) but about **50% of accounts in debt or arrears and about 75% of the £ value**. Centrica 2025: 44.7% provisioned, 50.3% past 90 days |
| P3 | **Repayment plan (credit)** | Agreed under SLC 27.8 on ability to pay | Collect the instalments; re-plan when one breaks | Ofgem "in debt". A plan breaks often: about 40% of large-supplier credit plans had at least one miss in 2015 (Ofgem social obligations 2015, Fig. 13, read off the chart). Take-up of an offered plan: **GAP** |
| P4 | **Prepayment debt** | A PPM fitted for debt (voluntary, or involuntary under warrant or remote switch), or debt carried onto a PPM through DAP | Recover by a weekly deduction from top-ups. 2025 means for new PPM-for-debt installs: £6.01/wk electricity, £4.40/wk gas, agreed over 365 and 342 weeks | Recovery is automatic while the household tops up. The household's remedy is to self-disconnect, not to default. 30–40% of repaying customers use a PPM (58% at the peak, Q4 2023) |
| P5 | **Final-account (closed) debt** | The account closes by switch, home move or death with a balance unpaid | Final bill, then DCA, then sale or write-off. No supply lever remains | Centrica 2025: final bills **84% provisioned**, 87.8% past 90 days. Ofgem's DRS weights provisioning by Closed versus Live |
| P5a | **Change-of-tenancy / unnamed "occupier" accounts** | A new occupier uses supply on a deemed contract and never opens an account | Letters to "the occupier"; a PPM remote switch is proposed (Ofgem home-moves CFI, Dec 2025) | Ofgem (suppliers' evidence): **20–40% of all domestic debt**, stable since before the crisis. Energy UK: **10–15%**, with more than 1m households whose details the supplier does not hold. **The two published ranges do not overlap** (§2.4) |
| P6 | **Deceased customers' debt** | The account holder dies | A claim against the estate. Family members are not liable unless they held a joint account | **GAP on scale.** No published count or £. Practice is from supplier help pages and secondary guides only (bereavement hold, no late charges) |
| P7 | **Disputed bills** | The customer disputes the amount: an estimate, a back-bill, or a meter fault | Complaints process; Energy Ombudsman after 8 weeks or deadlock; the back-billing limit (12 months when the customer is not at fault) | A billing-accuracy failure that presents as debt. **GAP on scale.** No published share of the debt stock is in dispute. This is where canon step 2 meets debt: an unbilled or mis-billed balance is not the same as a refusal to pay |
| P8 | **Debt as a block on switching (SLC 14 objection) and DAP** | A credit customer with debt more than 28 days old (after written notice) tries to switch | The losing supplier may object. A PPM customer under the DAP threshold (£500 as of 2016) may take the debt with them | Not a population of debt. It is a mechanism that keeps population P1–P3 on the book. About 28–30% of indebted switch attempts were blocked in 2013–15. No post-2016 figure (`domestic_debt_objection_rates_gb.md`) |

**The single most important definitional point for this project.** "Write-off" is an ACCOUNTING
event, not forgiveness. Centrica 2025, Note 17 (iv): *"Materially all write-offs relate to trade
receivables where enforcement activity is ongoing"*, and *"Enforcement activity continues in
respect of balances that have been written off unless there are specific known circumstances (such
as bankruptcy)."* Ofgem's Debt Strategy (Dec 2024) says the same from the customer side:
*"While suppliers are 'writing off' a proportion of debt they do not expect to recover this does not
translate to reducing the burden of debt for individual customers."* A model that drops the
customer's balance at write-off gets both the cash and the customer's position wrong.

---

## 2. Scale and dynamics, per population

### 2.1 The Ofgem series, 2016–2025 (NEW: reached as data, not read off narrative text)

Source: Ofgem, *Debt and arrears indicators*. The data was fetched 2026-10-05 from each chart's
Everviz config:
- arrears accounts `gvS7WsWVw`;
- accounts repaying `QG6XVhNPt`;
- average arrears `oJdJwK0mD`;
- average debt on plan `qrr9QdzQD`;
- total £ `0IwJatYrR`;
- PPM share `8mVG4XDzJ`;
- disconnections `GZOZpyFkv`;
- smart-PPM self-disconnection `FIUVSADKN` and `ftCyZiKt2`;
- PPM plan length by supplier `C_44TBGG7` and `sMLuVas8y`;
- weekly rate by supplier `ioDAqyvJr` and `OWxkboWD5`.

Each is fetched with `curl https://app.everviz.com/inject/<id>/`. The counts are **accounts per
fuel**, not households. A dual-fuel household in arrears on both fuels counts twice across the two
columns.

Q4 of each year:

| Q4 of | Elec accounts in arrears (no plan) | Elec accounts repaying (plan) | Avg elec arrears £ | Avg elec debt on plan £ | Gas accounts in arrears | Gas accounts repaying | Total £bn: debt / arrears / combined | % of repaying elec customers using a PPM |
|---|---|---|---|---|---|---|---|---|
| 2016 | 508,349 | 681,195 | 570 | 427 | 388,287 | 577,375 | not in series (starts Q1 2018) | 40 |
| 2017 | 601,795 | 654,923 | 555 | 441 | 459,450 | 541,503 | — | 38 |
| 2018 | 648,429 | 661,339 | 589 | 456 | 505,500 | 543,540 | 0.52 / 0.62 / 1.14 | 36 |
| 2019 | 694,191 | 739,947 | 654 | 458 | 539,605 | 588,221 | 0.56 / 0.73 / 1.29 | 37 |
| 2020 | 701,517 | 725,814 | 774 | 490 | 554,698 | 568,371 | 0.58 / 0.87 / 1.45 | 34 |
| 2021 | 775,721 | 979,224 | 905 | 425 | 602,038 | 731,151 | 0.68 / 1.11 / 1.79 | 30 |
| 2022 | 778,598 | 877,337 | 1,028 | 529 | 686,605 | 698,745 | 0.73 / 1.31 / 2.04 | 44 |
| 2023 | 1,005,350 | 753,887 | 1,303 | 678 | 862,163 | 609,999 | 0.85 / 2.25 / 3.10 | 58 |
| 2024 | 1,045,302 | 810,544 | 1,617 | 715 | 866,843 | 669,167 | 0.97 / 2.88 / 3.85 | 52 |
| 2025 | 1,146,497 | 829,275 | 1,773 | 799 | 929,768 | 685,246 | 1.10 / 3.44 / 4.55 | 41 |
| *Q2 2026* | *1,187,788* | *888,824* | *1,872* | *842* | *954,966* | *726,838* | *1.26 / 3.76 / 5.02* | *40* |

**An internal check that passes (derived).** Count × average reproduces the £ series. For Q2 2026
arrears: 1,187,788 × £1,872 + 954,966 × £1,613 = £3.76bn, against the published £3.76bn. For debt:
888,824 × £842 + 726,838 × £697 = £1.26bn, against £1.26bn. The three series are one
consistent dataset.

**What the series says (derived from the table, not quoted).**
- **The 2022 crisis is mostly a 2023-onward surge in £, not in heads.**
  - Electricity accounts in arrears rose ×2.3 from 2016 to 2025.
  - Average arrears rose ×3.1.
  - Arrears £ rose ×5.5 from 2018 to 2025 (0.62 → 3.44).
  - Debt on plans rose only ×2.1 over the same years.
- Ofgem's State of the Market (Jan 2026) says the same: the customers in debt or arrears rose 5%
  (3.4m → 3.6m) while the average per customer rose 11%. *"Intensity, not incidence."*
- **The mix has flipped.** In Q1 2018 arrears with no plan were about equal in value to debt on a
  plan (0.56 against 0.53). By 2025 they were three times it. The narrative on the Ofgem page
  says so too. Ofgem's Debt Strategy and the NAO: **75% of debt value sits with customers who have
  no plan.**
- **The dip in Q4 2022 and Q1 2023 is policy, not cure.** The arrears count fell from 894,732
  (Q2 2022) to 663,189 (Q1 2023), then jumped to 1,019,640 (Q3 2023). Ofgem attributes the fall to
  the financial support then in force: the Energy Bills Support Scheme and the Energy Price
  Guarantee.
- **The PPM route was shut, then partly reopened, and the stock tells you.**
  - Disconnections for debt have been zero since Q1 2023, and in single digits since 2017.
  - Involuntary PPM installs paused in Feb 2023.
  - The share repaying through a PPM rose from 30% (Q4 2021) to 58% (Q4 2023), then fell to 40%.
  - At the same time, arrears with no plan grew fastest.
- **Self-disconnection is the PPM population's form of default.** Smart-PPM customers
  self-disconnecting at least once in a quarter, electricity: 667,960 (Q2 2022), a peak of 946,400
  (Q3 2023), then 564,191 (Q2 2026).

### 2.2 The broader stock (more than 30 days)

Energy UK puts debt and arrears more than **30 days** old at about **£5.5bn**, against about £4.5bn
at Ofgem's 91 days. The gap has been *"consistently around £1 billion"* (Energy UK, *Energy debt:
everyone pays*, Feb 2026, p. 4 and Fig. 1, from Energy UK's own supplier data collection). Baringa
forecasts +£1.6bn in 2026 without intervention (cited there). The 30–91-day tranche is where
self-curing lateness and future arrears are mixed together. **No published source splits it.**

### 2.3 Who holds it

- **By payment method (Energy UK, Feb 2026, p. 13, supplier data).** SC customers are about 50% of
  accounts in debt or arrears and about 75% of the £ value. The DESNZ household shares are DD 72%
  and SC 16%.
- **By income (Ofgem DRS impact assessment, Nov 2025, §1.3, §3.1).** About 60% of the eligible
  (2022–24) debt is held by households in the bottom three income deciles.
- **By vulnerability.**
  - Energy UK supplier data: about 10% of arrears £ comes from WHD recipients, and about 25% from
    customers with "do not install PPM" characteristics. About 70% of arrears comes from customers
    with no clear indicator of their circumstances (pp. 10–11).
  - Baringa (cited there): of households in debt, about ¼ are extremely financially vulnerable,
    about ½ are financially vulnerable, and about ¼ are at-risk or not vulnerable.
- **Payment method of debt objections, 2013–15.** Credit 46–48%, DD 11–12%, PPM 32–36% (Ofgem
  objections IA §1.27).

### 2.4 Final-account and change-of-tenancy debt

- Ofgem home-moves CFI (Dec 2025, §2.5; executive summary): unnamed accounts may be **20–40%** of
  all debt, "stable since before the energy crisis", which *"suggests that some at least of this
  portion of debt is driven by behavioural factors rather than affordability."*
- Energy UK (Feb 2026, p. 12): **10–15%**, with more than 1m households whose details the
  supplier does not hold.
- **The two ranges do not overlap.** Neither source gives its method. Treat the share as
  **unresolved between 10% and 40%**. It is a practitioner question.
- Centrica's closed-account provisioning (84–86%) is the best published recovery signal for P5.

### 2.5 Cures, roll rates, recovery

- **Roll rates from stage to stage (current → 30 → 60 → 90 → plan, write-off or cure): GAP.**
  Ofgem collects flows through the SOR template: entries to arrangements, failed arrangements, and
  mean weeks to recover (Q3.1–Q3.27). It publishes only stocks. No supplier publishes roll rates.
- **Cure rates.** The only published cohort cure figures are:
  - **"Just over half"** of customers blocked by a debt objection had repaid when reported, about
    70% of those within 3 months (Ofgem objections decision 2016, p. 3; IA §1.38–1.39). This is a
    selected population (indebted switchers), 2013–14.
  - **Recovery rate, Energy UK Fig. 5.** Debt less than 12 months old: 60%, 56%, 38%. Debt more
    than 12 months old: 31%, 15%, 9%. The three years are 2022-23, 2023-24 and 2024-25. The
    definition is not disclosed. Aged arrears rose from 52% to 65% of arrears between 2023 and
    2025.
- **Time to recover.** *"The estimated average time for recovering outstanding Eligible Debt is
  more than 22 months"* (DRS impact assessment, Nov 2025, §3.10, from SOR data). The 2015 mean
  weeks to recover a credit-arrangement debt were 46 (British Gas), 96 (E.ON) and 77 (EDF) (Ofgem
  2015 social obligations data annex).
- **Recovery after write-off.** Centrica Group, Note 17 (iii)/(iv): recoveries of previously
  written-off receivables were £3m (2025) and £10m (2024), against write-offs of £135m and £160m
  (residential plus business). That is about 2–6% of a year's write-offs (derived; years and
  cohorts differ, so this is indicative only). **Debt-sale prices to purchasers, in pence per £:
  GAP.** Nothing found for GB energy.
- **Collection cost.** *"The average cost for collecting debt is 3 pence per £1 of debt and
  arrears"*, from the 2024 average debt administration cost (DRS impact assessment, fn 6).

### 2.6 Loss: bad-debt charge and the price-cap allowance

**Supplier P&L (Centrica plc, ARA 2025).**
- Retail bad-debt charge: £418m (2024: £369m).
  - UK Home Energy Supply (domestic): **£277m** (£237m).
  - UK Business Energy Supply: £132m (£120m) (Strategic report).
- *"The bad debt charge as a percentage of revenue increased to 2.6% (2024: 2.2%)"* for Retail.
  The closing provision was 38% (36%) of Retail gross receivables (Audit and Risk Committee
  report).
- Residential credit-loss provision: £984m → £1,195m in 2025. The charge was £285m against only
  £74m written off (Note 17). **The provision is growing about four times faster than write-offs
  crystallise.** That is the stock-of-old-arrears problem Energy UK describes.

**The price-cap allowance (what the regulated price assumes debt costs).** Sources: Ofgem,
*Appendix 2: Debt-related costs*, consultation Dec 2024 and **decision May 2025**; the extension
decision of Feb 2025.

| Period | Allowance | Source |
|---|---|---|
| 2019 – Mar 2025 (base) | Debt costs inside opex (DD baseline) plus the payment-method uplift (SC extra) plus EBIT working capital. Built from a **2017** baseline-year RFI, scaled with the cap level. Cap 13a (Oct–Dec 2024), excluding AA: **DD £25 (1.4%), SC £121 (6.5%), PPM £10 (0.6%)** of the cap | App. 2 consultation, Table 2.1, §2.11–2.14 |
| COVID-19 | A temporary debt allowance with float and true-up | App. 2 decision §2.21, §5.69–5.70 (amount not extracted this pass) |
| **Oct 2023 →** | **Additional Support Credit allowance, £9** per customer per year | App. 2 decision §2.14; ASC decision 2023 |
| **Apr 2024 →** | **Debt "float" adjustment allowance, £31** per customer per year (benchmark consumption; **£28 at TDCV**). Covers under-recovery for Apr 2022 – Mar 2024 (cap periods 8–11b) | App. 2 consultation fn 7, §2.15, §2.18 |
| Apr–Sep 2025 | Float extended at £31. Under-recovery about £195m (Apr–Sep 2024). The first float **over-recovered by about £2.50 per customer per year**, about £55m | Extension decision, Feb 2025 |
| Cap 14a (Apr–Jun 2025), including AA | DD £57 (3.3%), SC £161 (8.6%), PPM £19 (1.1%) | App. 2 decision, Table 1.1 |
| **From 1 Jul 2025** | A distinct debt-related cost allowance: **£71 per dual-fuel customer per year on average = 3.6% of bills**. The weighted average uses 2023 and 2024 data. Bad debt and working capital scale with the cap; admin scales with CPIH. Allocation: **DD £57, SC £160, PPM £19**. The float and ASC roll off | Decision overview, May 2025, §2.9, §2.55; App. 2 decision Table 5.1 |

- The *"typical consumer pays around £52 per year"* towards debt costs: this is DD on the SVT,
  from the home-moves CFI, Dec 2025, §2.2.
- Energy UK: about £50 DD and about £140 SC, under the April 2026 cap.

**Do not mix these figures with the "1% DD / 6% SC of bills in bad debt" in
`company_debt_management.md` §5.** Those are cost-recovery ratios in the price, not loss rates on a
book. The ratio was 1.4/6.5 (2024), not 1/6.

### 2.7 What is NOT established (consolidated)

- A DD return rate (first attempt, or net of re-presentation), for energy or economy-wide.
- Bills unpaid at their due date, or at 28 days, by payment method.
- An income-stress segmentation of payment failure. The category does not exist publicly.
- Take-up of an offered plan; a per-instalment keep rate (only a 2012–15 annual "at least one
  miss" share exists).
- Roll rates; any annual entry flow into arrears; decade-cumulative incidence.
- The close-to-write-off clock (supplier policy, said by Ofgem to differ).
- The DCA-versus-write-off order.
- Debt-sale prices.
- The scale of deceased-customer debt; the scale of disputed debt.
- The 10–40% change-of-tenancy share (unresolved).
- An industry age × method × live/final provision table. Ofgem considered one and rejected it. One
  supplier's (Centrica's) table exists.
- Debt-objection rates after 2016.

---

## 3. Rules

| Rule | What it requires | Source |
|---|---|---|
| **SLC 27 (payment difficulty, Ability to Pay)** | Identify payment difficulty. Offer arrangements that take account of ability to pay (27.8). Offer a PPM where safe and reasonably practicable. Give information on support. Do not take disproportionate action. Suppliers must monitor *"credit customers' broken arrangements"* (British Gas SLC 27.8 decision, Apr 2017) | SLC 27; `company_debt_management.md` §6 |
| **Debt standards (proposed, not yet decided)** | Standardise ability-to-pay assessments, using an objective tool such as the Standard Financial Statement. Accept credible third-party repayment offers. A "Debt Guarantee" | Ofgem, *Improving debt standards* consultation, Dec 2024. **No final decision was found this pass** |
| **SLC 28B, involuntary PPM (Code of Practice 18 Apr 2023 → licence from 8 Nov 2023)** | No involuntary PPM unless all of these hold: <br>• the **Debt Trigger** is met — charges outstanding **3 months or more** after the bill, **£200 or more per fuel**, and not on (or moving to) a plan; <br>• **at least 10 attempts** to contact, through several channels; <br>• SLC 27 duties met; <br>• a **Site Welfare Visit**, with body-cam or audio; <br>• safe and practicable under the Precautionary Principle. <br>Banned for 75+ with no support in the house, and for children under 2. No staff incentives tied to installs. Warrant costs capped at £150 per 12 months. Extended to 2027 | Ofgem PPM licence decision Sep 2023 (SLC 28.7–28.9, definitions); PPM guidance (Safe and Reasonably Practicable) §5.2, §5.6 |
| Restart of involuntary installs | Supplier by supplier, from Jan 2024: EDF, Octopus, ScottishPower, then E.ON, Tru, UW. **Number of involuntary installs since: GAP** (not found) | Ofgem press releases, 2024 |
| **Disconnection** | Legally possible after the demand and a 7-day notice. Winter moratorium. Protected groups. In practice **zero since Q1 2023** | Ofgem indicators, `GZOZpyFkv` |
| **SLC 14 debt objection; DAP** | The losing supplier may object to the switch of a customer with debt more than 28 days old (after written notice). PPM customers under the DAP threshold may assign the debt | `domestic_debt_objection_rates_gb.md` |
| **Back-billing limit** | No billing for consumption more than 12 months back where the customer is not at fault | `company_debt_management.md` §1 (SLC 21BA). Text not re-read this pass |
| **Limitation** | 6 years, restarted by a part-payment or an acknowledgement | Limitation Act 1980 ss. 5, 29(5) |
| **Fuel Direct (third-party deductions, UC)** | Arrears deduction = a **flat 5% of the UC standard allowance**. It is not taken at all if the full 5% cannot be. Utilities usage plus arrears is capped at 25%. Overall deductions cap is **15%** (Fair Repayment Rate). Usage deductions do not count toward the 15%. Rates from April 2026 (Energy Action Scotland, *Advisors Toolkit* fact sheet 2f, 2026, secondary): about £17–£33 a month by household type | DWP *Deductions guidance* V19 (deposited paper DEP2025-0769), pp. 2–4 |
| **Debt Relief Scheme, phase 1** | Write off debt accrued **1 Apr 2022 – 31 Mar 2024** for customers on means-tested benefits owing **£100 or more** who are engaged: on a plan, paying toward usage, or re-engaging through a plan, a smart meter, Fuel Direct or advice. Closed accounts are included only if engaging. About £0.5bn, with a further about £0.5bn planned for 2026. Energy UK expects £312–473m. Funded through network charges, Pay When Paid. Suppliers are reimbursed for the **un-provisioned** part only. Bill impact £3.23–£5.13 per household, one year | Ofgem DRS working paper Aug 2025; statutory consultation Nov 2025; impact assessment Nov 2025; home-moves CFI p. 3 |
| **Home moves (proposed)** | A remote switch to PPM mode on move-out, so the new occupier must open an account. Possibly pre-loaded credit and a zero standing charge | Ofgem home-moves CFI, Dec 2025, §2.6, §3.1 |

---

## 4. Collections practice

**The dunning sequence.** `company_debt_management.md` §1 holds the sequence: reminder at
T+7–14 days, demand, 28 days, a 7-day notice. It is a legal minimum, not a practice distribution.
**What actually happens in what order and at what intervals is supplier policy and is not
published.**

The fixed points are:
1. A DD is retried, then cancelled and the customer moved off DD (British Gas).
2. SLC 27 contact and a plan offer come before escalation.
3. 10 contact attempts and a welfare visit come before any involuntary PPM.
4. DCA placement, write-off and sale happen in an order that is supplier-specific (§2.7).
5. Enforcement continues after the accounting write-off (Centrica).

**The levers that are actually live today (2023–26)** are:
- contact and engagement;
- the plan (with its affordability assessment);
- a PPM, voluntary or restricted-involuntary;
- Fuel Direct;
- referral to debt advice;
- hardship funds and discretionary write-off;
- DCA and sale on closed accounts.

Disconnection is not a lever. The **objection** is a passive lever: it keeps a debtor on the book.

**What the regulator says works, and what is evidenced.** This is thin.
- **Lower and affordable instalments break less.** Ofgem 2015: the share of credit plans with at
  least one failed payment rises with the weekly amount, from 23% at under £3/wk to about 41% at
  over £9/wk (large suppliers, read off the chart). It differed about ×2 between supplier tiers.
  This is the best energy-specific evidence that the terms change the outcome.
  - PFRC/StepChange 2025: of 256 debt-advice clients, 16% had agreed a plan they felt was
    unaffordable.
  - StepChange 2016/18: 7–8% "set a repayment rate I couldn't afford".
- **Engagement is the binding constraint, not only affordability.** About 70% of arrears £ has no
  circumstance flag (Energy UK). About 75% of £ is not on a plan. The DRS is built around
  re-engagement, and its cost-neutral scenario assumes **32% engagement and 20% changed payment
  behaviour**. Those figures are taken from **E.ON Next's Winter Support Scheme** and WHD
  experience (DRS impact assessment fn 11). They are a supplier's own scheme, not a trial.
- **Contact-strategy trials: no energy-specific RCT was found.** The closest published RCTs are in
  other sectors:
  - Behavioural Insights Team for DfC Northern Ireland, 2018, **mortgage** early arrears: making
    contact rose from 45.9% to 62.2% with redesigned letters plus SMS.
  - BIT 2012 *Fraud, error and debt*: personalised SMS raised payment of **court fines** by about
    10pp.

  Transferring either to energy is an assumption. **GAP**: an energy-specific contact or terms
  trial. The third side (a practitioner) is the right next step.

---

## 5. What a real supplier SEES (the epistemic wall)

**Sees:**
- its own bills, amounts and dates;
- each DD presentation and its ARUDD return code;
- each payment, its amount and channel;
- PPM top-ups and the debt recovered through them;
- smart-PPM self-disconnection events and durations (it reports them to Ofgem);
- meter reads and estimates;
- each plan agreed, its instalments, and each miss;
- contact attempts and responses;
- PSR and vulnerability flags the customer has disclosed;
- WHD and DWP data-matching results (benefit eligibility, as a flag);
- Fuel Direct enrolment;
- the outcome of its debt objections;
- change-of-tenancy notifications;
- a death notification;
- complaints and disputes;
- credit-reference data at sign-up and in collections (bureau scores, not finances);
- and, where the customer consents, an income-and-expenditure statement (SFS) at the
  ability-to-pay assessment.

**Does not see:**
- the household's true income, savings and other debts, beyond what a bureau score or a
  self-declared I&E reveals;
- whether non-payment is *can't* or *won't*;
- who actually lives at an unnamed-account premises;
- whether a PPM household is rationing or self-disconnecting short of a reportable event (older
  meters);
- whether a leaver will pay a final bill;
- the true consumption behind an estimated bill.

**Consequence for modelling.** The world may draw a household's ability to pay. The company must
only see its consequences: payments, returns, plan behaviour, contact, flags. Any company-side
"income-stress tier" is a wall breach unless it is the output of the company's own scoring on
observables.

---

## 6. Negotiation: what the evidence supports

1. **Set the instalment from an affordability assessment, not from the balance.** This is the law
   (SLC 27.8). The 2015 breakage gradient by weekly amount supports it.
2. **Long horizons are normal.** Agreed PPM-for-debt plans averaged 342–365 weeks in 2025, with a
   range of 137–737 weeks by supplier. Credit-arrangement mean recovery was 46–96 weeks (2015). A
   debt cashflow forecast is therefore a multi-year annuity with a breakage hazard, not a lump sum.
3. **Engagement first.** The value is concentrated in unengaged, un-planned arrears. A contact
   strategy that converts arrears into a plan moves more £ than one that tunes plan terms. The
   evidence for any specific contact design is from other sectors (§4).
4. **Partial forgiveness can pay.** The DRS's premise is that writing off the un-provisioned part
   of old debt plus re-engagement costs about the same or less than continued collection. The
   recovery time is more than 22 months, the collection cost is 3p per £, and working capital
   costs 12.2% a year (DRS impact assessment §3.10). It is a modelled claim, not an observed one.
   The cost-neutral case rests on one supplier's scheme figures.

---

## 7. What our code does

This is a survey of the tree at `a52651e29` (worktree), made 2026-10-05. Line numbers are as found.
**The short version:** the world side is far richer than the knowledge behind it. The company sees
its own ledger and little else. Nothing forecasts a customer's debt cashflow.

**The world (`simulation/`):**

- **`simulation/arrears_engine.py`**: payment outcome, the write-off rule, and DCA/sale.
  - `payment_outcome()` (l. 412) draws each residential bill's fate from
    `_DD_FAILURE_PROB = {"LOW": 0.03, "MODERATE": 0.12, "HIGH": 0.35}` (l. 156) and `_ON_TIME_PROB`
    (l. 157), keyed on an income-stress tier.
  - **Both are unsourced.** The tier is a category no published source uses (§2.7;
    `knowledge_map.md` row 97).
  - A fuel-poverty multiplier of ×1.3 / ×0.9 (ll. 408–409) is a declared choice.
  - **PPM never fails** (ll. 396–405 say so and name what is missing). Self-disconnection,
    standing charge accrued while off supply, emergency-credit debt and debt recovered on the
    meter are all absent. The world therefore produces **no P4 population**, while the published
    stock has 30–58% of repayers on a PPM.
- **Bad debt** is `balance_settlement_from_outcomes` (l. 784).
  - The write-off is the balance at close, or at the 6-year statute bar (sourced). That matches
    §1 on the AMOUNT.
  - The close→write-off date is a declared convention (`WRITE_OFF_DATE_CONVENTION`, l. 643).
  - Live-arrears provisioning (`LIVE_ARREARS_PROVISION_RATES`, l. 654, Centrica 2025) is
    **sourced but OFF by default**. Which row a failed DD falls into depends on the C1 gap
    (first presentation or net of re-presentation; l. 665). So a stayer's arrears cost £0 in
    `bad_debt_gbp` by default. That is a declared gap, not a zero.
  - After write-off the stages run DCA +30d → RECOVERED +180d or SOLD +90d. These carry:
    - `DCA_RECOVERY_RATE` 30/20/20%;
    - `DCA_COMMISSION_RATE` 0.15;
    - `DEBT_SALE_HAIRCUT_PCT` 0.12 (ll. 184–191).

    All are labelled "illustrative, unbenchmarked", and **§2.5 finds no published debt-sale
    price**. The direction is unsupported by the one public signal: Centrica's recoveries after
    write-off are about 2–6% of a year's write-offs.
  - Write-off is modelled as the end of the customer's liability. Centrica says enforcement
    continues after write-off (§1).
- **`simulation/payment_behaviour_source.py:466` `later_settlement_date`**: a failed bill is repaid
  later in 50% of cases, 70% of those within 3 months. These are Ofgem's 2016 figures for
  **debt-blocked switchers**, applied to every failed bill. That is a selected population used as
  the general one. The module names seven gaps (ll. 420–432) that lean toward overstating time in
  debt. `REPRESENTATION_SUCCESS_SHARE = None` (l. 450) is honest.
- **`simulation/plan_offer_response.py`**: take-up, keep rate and instalment are all `None`, with
  reasons (ll. 71–88). It is correct and honest. Every plan offer answers `accepted=None`.
- **`simulation/debt_objection.py`**: an SLC 14 block on churn.
  - `DEBT_OBJECTION_BLOCKED_SHARE` is 0.2833, from 2013–15 data.
  - It is wired into `customer_events.py:991–1018` through `WorldDebtBook`.
  - It is world-only. The company neither decides nor sees the objection (named gap 2).
  - DAP is prose only.
- **`simulation/final_bill_outcome.py`**: P5a gone-away debt.
  - It is anchored to an Ofgem figure of "25–39%" (press release, 30 Oct 2025).
  - The per-move rate is drawn from a Beta distribution with mean 0.12, a declared calibration
    choice.
  - **This file finds two published ranges, 20–40% (Ofgem CFI) and 10–15% (Energy UK), that do not
    overlap.** The anchor needs revisiting.
- Not modelled anywhere:
  - deceased customers' debt (an enum, `account_closure.py:36`, and nothing more);
  - Fuel Direct (zero hits);
  - the DRS;
  - involuntary PPM conversion as a collections route;
  - the price-cap debt allowance as a comparison figure.

**The seam (`company/interfaces/sim_interface.py`).** Only three methods carry payment or plan
information:
- `get_payment_method` (l. 175);
- `answer_plan_offer` (l. 304);
- `get_plan_instalments` (l. 315).

The company's arrears state is derived from its own ledger (`payment_observation_consumer`), which
is right under the wall in §5. No PPM, self-disconnection, Fuel Direct or bureau-score observable
crosses.

**The company (`company/`, `saas/`). Live:**
- **`company/billing/arrears_engine.py`**:
  - ageing into 30/60/90+;
  - dunning ladders by segment;
  - B2B statutory interest;
  - a write-off event;
  - the Debt Respite hold.
- **`company/billing/collections_journey.py`**: dated per-account stages and plan offers.
  `UNREACHED_EXITS` (ll. 96–102) honestly names three exits it cannot reach: arrangement,
  disconnection-equivalent and write-off.
- **`company/billing/payment_plan.py`**: a plan defaults after 2 misses (`_DEFAULT_THRESHOLD = 2`,
  l. 21). **Uncited.** The SOR definition of a failed instalment (10 working days) is published; a
  default threshold is not.
- **`company/billing/dd_collections_desk.py`**: stops a DD after 2 returns (l. 127, British Gas,
  single-source).
- **`company/pricing/default_belief.py`**: the own-book expected loss by arrears state, shrunk
  toward `PRIOR_LOSS_RATE = 0.020` (l. 74). It feeds the **renewal price**, not the P&L or a
  forecast. It treats "unbilled for 62 days" as closed (l. 83).

**The company. Built but wired to nothing (only tests and `internal_seams.py` reach them):**
- `company/finance/bad_debt_provision.py`: 0.5/5/20/50/90%.
- `company/finance/debt_age_analysis.py`: 2/5/15/40/80%.
- `company/finance/debt_collection.py`: recovery by stage, 0.95→0.

These are three mutually inconsistent and uncited tables. `bad_debt_reconciliation.py` reports
them as `unwired`.

Further unwired modules:
- `company/finance/cash_flow_forecast.py`: portfolio-level and weekly, with no debt dimension and
  no caller.
- The PPM registers `ppm_debt_loading.py`, `prepayment.py` and `ppm_emergency_credit_register.py`.
  Their constants are uncited: a £250 load cap, 5% or 50p/25p recovery per top-up, £5/£10
  emergency credit.
- `ppm_warrant_register.py`, `debt_referral.py` (£200 referral threshold), `winter_moratorium.py`,
  `payment_plan_adequacy.py`.

**One of these contradicts the published rules, and one is uncited where a figure now exists.**
- `ppm_warrant_register.py` says involuntary installs were "banned"/"suspended" after April 2023,
  and that suppliers "may only install voluntarily". **That is wrong.** Installs resumed under
  SLC 28B from 8 Nov 2023, and suppliers were re-permitted one by one from Jan 2024. The register
  also misses the rule's own terms: 3 months outstanding, 10 attempts, a welfare visit with
  recording, and bans by household type. Its £200 minimum matches the guidance's £200, but per
  fuel.
- The PPM recovery per top-up is uncited, while the agreed weekly rates for new installs are now
  published by supplier (£2.57–£17.17/wk, §2.1).

Neither is live. Each should be checked against §3 before it is wired.

**Still live, partly superseded.**
- `saas/payment_behaviour.py`: a 4-segment provision table, 0.5–8% (l. 35), used on bill-level
  annotation.
- `saas/cost_to_serve.py`: `BAD_DEBT_RATE` 2% residential (l. 69). Its own docstring says it
  overstated bad debt about 30×. It is still read by `simulation/bad_debt_incidence.py` and
  `settlement_clocks.py`.

**Billing against debt (canon step 2).**
- `saas/ledger.py:309` `unbilled_revenue_accrual` and `company/finance/revenue_accruals.py`
  account for unbilled revenue only. They do not reach arrears or bad debt.
- `company/billing/back_billing.py` enforces the 12-month cap with no link to debt.
- Billing does not distinguish an unpaid balance from a disputed or mis-billed one (P7) or an
  unnamed-occupier one (P5a). In the published world those are 10–40% of the stock.

**What a per-customer debt cashflow forecast would need, and what is missing:**
1. **A per-account debt state the company observes**: age, method, live or final, plan or no plan,
   PPM. *Exists* in `collections_journey` and the arrears engine, apart from PPM.
2. **Transition hazards from that state**: cure, roll to the next age band, plan take-up, plan
   break, move to PPM, close, write-off. *Missing.* Not published (§2.5). The company must learn
   them from its own book, as `default_belief` does for loss. That requires the world to generate
   a credible variety of trajectories.
3. **An amount and timing model per state**: instalment size, PPM recovery per week, final-bill
   recovery curve. *Partly published*: PPM £/wk and length by supplier; Centrica's
   live/final provision; the 22-month mean recovery; 3p per £ collection cost. None is wired.
4. **Discounting and working capital**: Ofgem uses 12.2% a year (DRS impact assessment). *Not in
   code.*
5. **A held-back test**: forecast in year t, compare with t+1..n. The Ofgem quarterly series (§2.1)
   gives an aggregate target the world's own book can be checked against. *Not used.*
6. **The world must generate the populations**:
   - PPM debt (P4) is absent;
   - plan take-up is `None`;
   - failure incidence is invented;
   - "intensity not incidence" is untested;
   - unnamed-occupier and disputed debt are not distinguished from refusal to pay.

**A forecast built on today's world would forecast the invented 3/12/35% tiers back to us.**

---

## 8. Gaps

**Knowledge gaps**, each filed as a gap and not estimated:

| Gap | Where the answer probably is | Route |
|---|---|---|
| Roll rates and cure rates, by stage | Ofgem SOR flows (collected, unpublished); supplier MI | Practitioner (the director); or an Ofgem data request, which is a real-world contact and reserved |
| Plan take-up and keep rate | As above, plus the 2012–14 and 2016 social-obligations reports (not yet read) | Read those reports; ask the practitioner |
| DD return rate (first attempt or net) | Bacs member data; supplier MI | Practitioner |
| Share of the stock that is change-of-tenancy (10–15% or 20–40%) | The two sources disagree and neither gives its method | Practitioner; the responses to Ofgem's CFI when published |
| Debt-sale price and DCA recovery for energy | Debt-purchaser trade press; supplier ARAs (OVO, E.ON UK, Octopus; Octopus's filing is a scan with no OCR here) | A further published-source pass |
| Deceased-customer debt and disputed-debt scale | Not found | Practitioner |
| Bad-debt charge as % of revenue, 2016–2025, by year | Centrica ARAs 2016–2025 (only 2024–25 read here); Ofgem consolidated segmental statements | A further pass. A compilation is feasible |
| Involuntary PPM installs since 2024 | Ofgem PPM monitoring | A further pass |
| Effect of contact strategy and terms in **energy** | No RCT found | Practitioner; the director rules whether the cross-sector evidence transfers |
| The improving-debt-standards decision | Not located | Watch Ofgem |

**Code gaps**, in order of what they block:

1. **Failure incidence is invented.** `_DD_FAILURE_PROB` 3/12/35% on an income-stress tier.
   - It is now checkable against a target: the Ofgem quarterly stock and average-balance series,
     2012–2026, by fuel (§2.1).
   - The world's book should reproduce the shape: arrears share about 2–4% of accounts per fuel,
     the average arrears path, and the post-2023 intensity rise.
   - It should be **graded, not fitted** (baseline/curriculum split: a fidelity reason, blind to
     company results).
2. **No PPM debt** (P4). It is 30–58% of repayers in the published stock. Self-disconnection is
   the observable that stands in for default.
3. **The world's cure draw** (`later_settlement_date`) uses a debt-blocked-switcher cohort as if it
   were every failed bill.
4. **The gone-away anchor** (`final_bill_outcome.py` "25–39%") disagrees with Energy UK's 10–15%.
5. **Post-write-off recovery and sale** constants are illustrative. Write-off ends the customer's
   liability in the world, but not in practice.
6. **Unwired, uncited tables.**
   - Three mutually inconsistent provision and recovery tables in `company/finance/`.
   - `saas/cost_to_serve.BAD_DEBT_RATE` is still read.
   - A PPM warrant register that misstates the post-2023 rules.

   Either delete these, or re-source them before anything wires them. They are the shape
   CLAUDE.md warns about: a plausible number that becomes load-bearing.
7. **The company cannot see or decide** the objection, a PPM conversion, Fuel Direct, or a bureau
   score. A debt *negotiating* tool has almost no levers yet.
8. **No per-customer debt cashflow forecast** exists (§7, items 1–6).

---

## 9. What this says about the order of work

The canon (2026-10-05) puts "debt cashflow forecasting and negotiating tools" first among the
step-5 levers. Its stated reason is that step 2 (billing accuracy) comes first because "debt and
cashflow work rests on knowing what was actually billed". The evidence supports that reason, and
makes it stronger. **Three proposals follow, each with its evidence. Per the canon: raised,
carried on, the director rules.**

**1. Move change-of-tenancy (unnamed "occupier") accounts INTO step 2, not step 5's home-moves
lever.**
- Evidence: a deemed-contract occupier who never opens an account is at once:
  - unbilled or mis-addressed energy (step 2's subject);
  - a single debt population of **10–40% of the whole stock** (Energy UK; Ofgem CFI);
  - the lowest-recovery population (closed and final accounts are 84–88% provisioned at
    Centrica).
- Ofgem says it is *"driven by behavioural factors rather than affordability"* and is fixing it
  in the registration process, not in collections.
- Building "what was actually billed" without the occupier account leaves out the biggest
  billing-shaped share of debt. Building the debt forecast without it forecasts the wrong
  population.
- This is cheaper than it looks: `final_bill_outcome.py` and `company/crm/change_of_tenancy_register.py`
  already exist.

**2. Insert a world-fidelity item before the debt lever: grade the world's debt against the Ofgem
series.**
- The canon's own third test is "whether the world contains what it needs yet". For debt it does
  not:
  - payment-failure incidence is invented (3/12/35%);
  - there is no PPM debt;
  - plan take-up is honestly `None`;
  - the cure draw is borrowed from a selected cohort.
- A forecast built on that world learns the invented tiers back.
- The new evidence makes a check possible that was not possible last week. Ofgem's full quarterly
  series is now reachable as data, 2012–2026:
  - counts, average balances and £ by plan and no plan;
  - PPM share;
  - self-disconnection.
- That is exactly a held-back target in the canon's step-3 sense: forecast from earlier years,
  check against later.
- Proposal: a **debt-world grading** atom sits with step 3. It checks the world's own book
  against the series' shape (incidence against intensity, the 2023 surge, the arrears/debt mix)
  before step 5's debt lever is drawn. This is graded for fidelity, not fitted to company results.

**3. Split the step-5 debt lever: forecasting first; negotiating tools after the knowledge
exists.**
- What drives the outcome is thinly evidenced in energy:
  - plan terms: one 2015 chart;
  - contact strategy: only mortgage and court-fine RCTs;
  - take-up and keep rates: an established absence.
- The company also has almost no levers across the seam today: no objection decision, no PPM
  conversion, no Fuel Direct, no bureau view.
- Forecasting is buildable now:
  - the company's own-ledger state (`collections_journey`, the arrears engine);
  - the hazards learned from its own book, as `default_belief` already does for loss;
  - the published amounts and timings (§2.5, §2.6);
  - the 12.2% working-capital rate.
- Negotiation needs, first:
  - the third side (practitioner answers on take-up, keep, roll and cure);
  - seam work, so the company can actually choose a term, a PPM or a referral.
- Recommend asking the director the practitioner questions in §8 now, in parallel. They are
  cheap and unblock the second half.

**Nuance within step 1:** debt overlaps three other knowledge areas, and should be read with them:
- **home moves**: the occupier account;
- **unbilled energy**: estimates and disputes, P7;
- **communications**: engagement is the binding constraint, and about 70% of arrears £ has no
  circumstance flag.

The highest-value single piece of knowledge still missing across all of them is a
**practitioner's roll-and-cure table** for a standard-credit book.

---

## 10. Vulnerability as a hidden household state (2026-10-08 pass)

**Why this section exists.** The director's order of 2026-10-08 says the world should draw
vulnerability as a hidden household state, not assign it by rule. Today
`company/regulatory/priority_services_register.py` assigns PSR status by rule, so the company knows
exactly who is vulnerable. The company must infer it instead, from payments, contact, declared
needs and PSR registration. It must also treat a vulnerable customer at least as well as anyone in
the same position (fairness ruling, 2026-10-08). The regulatory text (needs codes, SLC 26/27) is in
the commons: `docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md`.
This section holds the quantities. The toggles are in `assumption_toggles.yaml` under the question
"Vulnerability as a hidden state".

All sources were fetched 2026-10-08 unless stated. The web-search budget was exhausted for this
pass, so every source here was reached by fetching a known publication URL and following its links.
Nothing was recalled. Page numbers are PDF page numbers.

### 10.1 Say what it is first: there are at least two vulnerabilities, not one

The published record measures two different things under the one word:

- **(V1) Needs-code vulnerability.** This is what the PSR registers: age, disability, illness,
  medical equipment, young children, communication needs, or a temporary need. It decides
  **services and protections**: the winter ban, the involuntary-PPM bans, and priority
  reconnection.
- **(V2) Financial vulnerability.** This means low resilience, no savings buffer, or a recent
  income shock. It drives **arrears**.

The two overlap, but in Ofgem's own survey they predict arrears very differently (§10.4).
Ofgem says plainly that the PSR captures V1 only: *"with limited/specific needs codes, relevant to
safety and off supply situations, many circumstances or characteristics are not captured by the
PSR"* (CVS 2025, p. 47). A single latent "vulnerable" flag would rebuild the bill-shock failure,
where one percentage was measured across two populations with different triggers. **The world
should draw V1 and V2 as separate states, correlated, not as one.**

### 10.2 Prevalence

| Measure | Value | Year | Source |
|---|---|---|---|
| Customers on a supplier PSR | 3.6m electricity, 3.0m gas (**13%** of customers, both fuels) | 2016 | Ofgem press release, 25 Oct 2016 |
| Customers on a supplier PSR | 6,703,753 electricity (**24%**), 5,646,740 gas (**24%**); +12% elec, +19% gas on 2017 | 2018 | Ofgem, *Vulnerable consumers in the energy market: 2019*, p. 16 |
| PSR by nation, 2018 | England 24% / 24%; Wales 26% elec, 28% gas; Scotland 21% elec, 22% gas | 2018 | same |
| PSR from supplier returns (GB) | 6,650,733 electricity, 5,598,632 gas | 2018 | Ofgem, *Monitoring social obligations: 2018 annual data report*, p. 28 |
| PSR 2017 (**derived**) | about 5.99m electricity, about 4.75m gas (2018 count ÷ 1.12 / 1.19) | 2017 | derived from the 2019 report |
| Respondents who say they or their household are on the PSR | **16%** | Jan–Feb 2024 | Ofgem, *Consumer Impacts of Market Conditions survey*, Wave 5 (CIM W5), p. 31; n = 3,439 |
| Likely eligible but not on the PSR | **39%**, of whom 28% are not aware of the PSR at all | Jan–Feb 2024 | CIM W5, p. 31. *"consistent with December 2022 and July 2023"* |
| Likely PSR-eligible, registered or not (**derived**) | **55%** (16% + 39%) | 2024 | CIM W5 data tables, table 159 bases |
| On the PSR, by group | aged 65+: 29%; disability in household: 36%; expecting or child under 5: 17% | 2024 | CIM W5, p. 31 |
| UK adults with ≥1 FCA characteristic of vulnerability | **52%** (27.3m) in 2022; **49%** (26.4m) in 2024 | May 2022, May 2024 | FCA *Financial Lives 2024*, key findings p. 10 |
| …by driver, 2022 → 2024 | poor health 9% → 9%; negative life event 22% → 20%; low resilience 27% → 26%; low capability 22% → 17% | 2022, 2024 | FCA FLS 2024 key findings p. 10 |
| Adults with drivers in 2 or more of the 4 categories | 37% of the vulnerable (9.8m) | 2024 | FCA FLS 2024 *Vulnerability & financial resilience*, p. 24 |
| Financially vulnerable or highly vulnerable (Ofgem segmentation) | **30%** of consumers. "Highly vulnerable" means not able to save and cannot afford unexpected expenses | 2024 | CIM W5, p. 11 |
| UK adults behind on at least one household bill | about 7m; about 1.4m behind on energy, council tax **and** water | Mar 2025 | Ofgem CVS 2025, p. 40 (citing others) |
| Fuel poverty (LILEE), England | **13.0%** (3.17m) in 2023; 13.1% in 2022 | 2023 | DESNZ annual fuel poverty statistics, as cited in Ofgem CVS refresh consultation, Sep 2024, p. 30 |
| Fuel poverty, England (older definition) | 11.1% | 2016 | Ofgem CVS 2025 (2019), §4.7 |

Notes on the table:

- **The 2016 → 2018 jump** from 13% to 24% coincides with the January 2017 widening of eligibility
  to "any energy customers in vulnerable situations ... including those whose situation is
  temporary" (2016 press release), and with needs-code alignment (electricity Jun 2017, gas
  Jan 2018). Part of the rise is definitional. How much is a **GAP**.
- **The admin figure is 24% (2018); the survey figure is 16% (2024).** These are two instruments,
  not a fall. Admin counts accounts on a register. The survey asks the respondent whether anyone
  in the household is registered, and a household can be registered without knowing it.
- **The 2016 13% still appears in the staging proposal for this work** (`SEAT_PROPOSAL_THE_ORDER_FOR_VOIDS_VULNERABILITY_AND_THEFT_2026-10-08.md`).
  It is nine years stale for the sim's later years.
- **FLS is person-level, cross-sector and UK.** It is not a household energy measure. The FLS
  original-algorithm series (2017/2020) did not extract unambiguously from the chart text, so only
  the 2022/2024 updated-algorithm headline is quoted.
- **GAP: the PSR count for any year after 2018.** Ofgem's annual *Vulnerable consumers* report and
  social-obligations data reports were not found after the 2019 edition (2018 data). The
  `/publications/vulnerable-consumers-energy-market-2020` URL returns 404.
- **GAP: the needs-code mix** (share of registrations by code). The code list is published
  (commons §1a) but no distribution by code was found.

### 10.3 Dynamics: onset, recovery, season

| Quantity | What is published | Source |
|---|---|---|
| Adults with a negative life event in the last 12 months (job loss, unwanted cut in hours, bankruptcy, separation, serious illness of self or close family, bereavement, becoming main carer) | **20%** in 2024 (10.9m); 22% in 2022. Original algorithm: 19% 2017, 21% 2020, 20% 2022, 18% 2024 | FCA FLS 2024 vulnerability report, p. 36 |
| Adults whose ONLY driver is a recent life event | **10.1%** of all UK adults | same, p. 24 |
| Types of event | Each type is individually small. The chart's labels run from 0.1% to 5.2% of adults a year per event type across 2017–2024 (job loss, cut hours, bankruptcy, separation, divorce, serious illness of self or family, deaths, becoming a carer). The per-type mapping did not extract reliably from the chart text, so no per-type figure is quoted | same, p. 38 |
| Temporary PSR need codes | 32 *Temporary – Life changes*, 33 *Temporary – Post hospital recovery*, 34 *Temporary – Young adult householder (<18)* | Ofgem CVS 2025, Appendix 6 |
| The regulator expects the register to move | *"we expect to see the number of customers on each supplier's PSR fluctuate in recognition of the fact that consumer vulnerability is complex and can be transient"* | Ofgem *Vulnerable consumers 2019*, p. 17 |
| Winter months | October–March | commons artefact §2 |
| Debt stock seasonality | see the quarterly Ofgem series in §2.1 | §2.1 |

**What this does and does not establish.**

- The life-event rate is a **12-month incidence among adults**. The 10.1% "life event only" stock
  is the nearest thing to an annual inflow into vulnerability for people who had no other driver.
  Each person can only be counted inside its 12-month window, so the stock approximates the annual
  flow.
- That is the basis for `vuln_annual_onset_rate`. It is an ESTIMATE for **temporary, event-driven
  V2/V1 onset only**. It does not cover the deterministic onsets: reaching pensionable age, which
  the world already knows from age, and a child being born.
- **GAP: recovery/exit rates.** No published GB source found gives how long a vulnerability lasts,
  or the annual share leaving the PSR for a reason other than death or a move. FLS's 12-month
  window is a property of the **instrument**, not a measured duration, so `vuln_annual_recovery_rate`
  is null.
- **GAP: seasonality of vulnerability onset.** Nothing found shows that onset concentrates in
  winter. What concentrates in winter is the **protection** (SLC 27 winter months) and the
  consumption, and so the bill.

### 10.4 Vulnerability and arrears: the overlap, measured on one instrument

The Ofgem CIM Wave 5 data tables (Jan–Feb 2024, n = 3,439, table 159, question F5A) cross the
answer *"falling behind with some energy bills"* or *"have fallen behind with energy bills"* by
PSR status and by Ofgem's financial-vulnerability segment. The outcome is **self-reported behind
on energy bills at the time of the survey**, which is not the Ofgem 91-day arrears indicator.

| Group (share of respondents) | Behind on energy bills | Relative risk vs the rest (**derived**) |
|---|---|---|
| All respondents | 7.6% | — |
| On PSR (16%) | 10.3% | **1.45** vs not on PSR (7.1%); 95% CI about 1.1–1.9 |
| Likely eligible, registered or not (56%) | 8.1% | 1.16 vs not eligible (7.0%) |
| Likely eligible and NOT registered (39%) | 7.2% | — |
| Financially "highly vulnerable" (16%) | 21.9% | **4.6** vs everyone else (4.8%); CI about 3.6–5.8 |
| Financially "vulnerable" or "highly vulnerable" (30%) | 15.2% | **3.6** vs everyone else (4.2%); CI about 2.8–4.6 |
| Financially "doing well" (29%) | 0.9% | — |

- The CIs are derived from the tables' effective sample sizes with a log-RR normal approximation.
- About 950 respondents carry no financial segment. They sit in "everyone else".

**Read together, this is the most decision-relevant finding of the pass.** Needs-code
vulnerability (V1, what the PSR knows) is a **weak** predictor of energy arrears, at RR about 1.2–1.5.
Financial vulnerability (V2, which no register records) is a **strong** one, at RR about 3.6–4.6.
This agrees with Energy UK's supplier data (§2.3): about 70% of arrears £ comes from customers with
**no** clear circumstance indicator. A world that drives arrears off the PSR flag would put the
risk in the wrong households.

### 10.5 What a supplier observes: how much is known to it

| Measure | Value | Source |
|---|---|---|
| Registered share of likely-PSR-eligible households (**derived**, same instrument) | **29%** (16 ÷ 55) | CIM W5 |
| …the same with the 2018 admin numerator (**derived**, mixed instruments) | about 44% (24 ÷ 55) | 2019 report and CIM W5 |
| Why the eligible-aware are not registered | 62% think they are ineligible; 13% see no benefit; 9% need more information; 9% have not got round to it; 8% do not know how | CIM W5, p. 32 |
| Of those with an energy affordability issue in the last 3 months: does the supplier know? | **41%** yes in total: 17.6% told the supplier, 11.7% the supplier contacted them, 11.7% "aware but no contact". 51% no; 8% don't know | CIM W5 data tables, table 150 (E26) |
| …among those with *repeat or recent* affordability issues | **61%** yes (29.0% told, 18.5% supplier contacted, 13.7% aware but no contact) | CIM W5 data tables, table 151 |
| How suppliers learn of circumstances | *"energy companies rely almost exclusively on customer disclosure"* | Ofgem CVS refresh consultation, Sep 2024, p. 38 |
| Data sharing | PSR shared supplier ↔ DNO (needs codes aligned 2017/18). All DNOs had water data-sharing agreements by 2023; *"fully functional ... during 2025"* expected | *Vulnerable consumers 2019* p. 12; CVS refresh consultation p. 24 |
| Self-disconnecting PPM households who tell their supplier | 9% (22% told anyone in authority) | Citizens Advice 2018, as cited in Ofgem CVS 2025 (2019), p. 36, fn 81 |

**The epistemic wall, restated for this state.** The world draws V1 and V2. The company sees:

- a PSR registration, only when the household discloses it or data-sharing brings it;
- declared needs, through contact;
- affordability, only through its consequences: missed and returned payments, plan breaks, PPM
  self-disconnection events (smart), and contact.

Registration is itself a **world draw**: the household chooses to disclose. It is not a company
decision. Once a household has disclosed, the company may hold the needs code. It may not hold the
latent state.

### 10.6 Protections that change outcomes (pointers, not restated)

| Protection | Effect | Where |
|---|---|---|
| Winter disconnection ban (SLC 27, Oct–Mar) | No disconnection of a pensionable-age household living alone or only with other pensioners or under-18s. "All reasonable steps" for disabled or chronically sick. In practice zero debt disconnections since Q1 2023 | commons §2; §3 above |
| Energy UK Vulnerability Commitment ("Safety Net") | Voluntary, all year: never knowingly disconnect a customer who cannot safeguard their welfare. **13 suppliers, about 90% of UK households** | commons §2; CVS refresh consultation p. 24 |
| Involuntary PPM (SLC 28B, Code of Practice 2023) | Banned for 75+ with no support in the house, and for children under 2. Site Welfare Visit and 10 contact attempts | §3 above |
| Ability to pay (SLC 27.8) | Arrangements must take account of ability to pay | §3 above |

**Every one of these protections keys on V1 (age, health, children). None keys on V2.** That
matters for the fairness ruling. A household that is financially vulnerable but not V1 has no
categorical protection, only SLC 27's ability-to-pay duty. To treat it "at least as well as anyone
in the same position", the company must infer V2 from behaviour, and the evidence above says that
is where the arrears are.

### 10.7 GAPs opened or confirmed by this pass

- PSR registered count after 2018 (§10.2).
- The needs-code mix (§10.2).
- How much of the 2016 → 2018 rise is definitional (§10.2).
- How long a vulnerability lasts, and the PSR exit rate (§10.3).
- Seasonal onset (§10.3).
- The correlation between V1 and V2 at household level. CIM gives the marginal overlap only
  through the arrears crosstab. The joint distribution needs the microdata, which was not fetched.
- The share of PSR registrations that come by data-sharing rather than customer disclosure.
- **Practitioner question (the third side):** how often does a supplier's vulnerability team
  learn of a circumstance at the first missed payment, at collections contact, or never?

---

## Sources

All fetched 2026-10-05 unless stated otherwise.

**§10 sources, fetched 2026-10-08 (PDF page numbers):**

- **Ofgem press release, 25 Oct 2016**, *More customers in vulnerable situations to receive help
  under the Priority Services Register*.
  <https://www.ofgem.gov.uk/press-release/more-customers-vulnerable-situations-receive-help-under-priority-services-register>
- **Ofgem, *Vulnerable consumers in the energy market: 2019*** (2018 data).
  <https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/vulnerable_consumers_in_the_energy_market_2019_final.pdf>
  - pp. 8, 12, 16–17.
- **Ofgem, *Monitoring social obligations: 2018 annual data report*.**
  <https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/monitoring_social_obligations_-_2018_annual_data_report.pdf>
  - p. 28.
- **Ofgem, *Consumer Vulnerability Strategy 2025*** (published 2019).
  <https://www.ofgem.gov.uk/sites/default/files/docs/2020/01/consumer_vulnerability_strategy_2025.pdf>
  - §4.7, §5.6, §5.16, fn 81.
- **Ofgem, *Consumer Vulnerability Strategy: Refresh* consultation, Sep 2024.**
  <https://www.ofgem.gov.uk/sites/default/files/2024-09/Consumer_Vulnerability_Strategy_Refresh_Consultation_paper_September_2024.pdf>
  - pp. 24, 30, 38.
- **Ofgem, *Consumer Vulnerability Strategy* (refreshed), Apr 2025.** Linked from
  <https://www.ofgem.gov.uk/policy/consumer-vulnerability-strategy>.
  <https://www.ofgem.gov.uk/sites/default/files/2025-04/Final%20CVS%2015042025-20250414111309.pdf>
  - pp. 40, 47; Appendix 6 (PSR needs codes).
- **Ofgem, *Consumer Impacts of Market Conditions survey*, Wave 5 (Jan–Feb 2024): final report and
  data tables.**
  <https://www.ofgem.gov.uk/sites/default/files/2024-09/CIM_Wave_5_Final_Report.pdf>
  <https://www.ofgem.gov.uk/sites/default/files/2024-09/CIM_Wave_5_Data_Tables.xlsx>
  - Report pp. 11, 30–32.
  - Data tables 150, 151, 159. The relative risks in §10.4 are computed from the weighted counts.
- **FCA, *Financial Lives 2024*: key findings, and *Vulnerability & financial resilience*.**
  <https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf>
  <https://www.fca.org.uk/publication/financial-lives/fls-2024-vulnerability-financial-resilience.pdf>
  - Key findings p. 10.
  - Vulnerability report pp. 21, 24, 36, 38.

- **Ofgem, *Debt and arrears indicators*.** <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators>
  - The page text gives the definitions and methodology.
  - The data series come from `https://app.everviz.com/inject/<id>/` for the chart ids in §2.1.
- **Ofgem, *Consultation – Appendix 2: Debt-related costs*, Dec 2024.**
  <https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf>
  - §2.1–2.23, Table 2.1, fn 7.
- **Ofgem, *Decision – Appendix 2: Debt-related costs*, May 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-05/Appendix-2-Decision-Debt-related-costs.pdf>
  - Table 1.1, §2.14, Table 4.1, §4.32, Table 5.1, §7.23.
- **Ofgem, *Energy price cap operating cost and debt allowances decision: overview*, May 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-05/Energy-price-cap-operating-cost-and-debt-allowances-decision-overview_0.pdf>
  - §2.9, §2.52–2.55.
- **Ofgem, *Additional debt related costs adjustment allowance extension decision*, Feb 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-02/Energy-price-cap-additional-debt-related-costs-extension-decision.pdf>
- **Ofgem, *Debt strategy: a 'reset' and 'reform'*, Dec 2024.**
  <https://www.ofgem.gov.uk/sites/default/files/2024-12/Debt_Strategy_(5).pdf>
- **Ofgem, *Improving debt standards in the domestic retail market*, consultation, Dec 2024.**
  <https://www.ofgem.gov.uk/consultation/improving-debt-standards-domestic-retail-market>
  - Not read in full this pass.
- **Ofgem, *DRS policy update working paper*, Aug 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf>
  - Summary table, §3.16–3.21, §4.1–4.4.
- **Ofgem, *Debt Relief Scheme impact assessment*, Nov 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-11/Debt_Relief_Scheme_Impact_Assessment.pdf>
  - §1.2–1.3, §3.1, §3.7–3.17, fn 6, fn 7, fn 11, Table 2, §5.7.
- **Ofgem, *Call for input: Tackling energy debt in the supplier home-moves process*, Dec 2025.**
  <https://www.ofgem.gov.uk/sites/default/files/2025-12/Tackling-energy-debt-in-home-moves-process-call-for-input.pdf>
  - Executive summary, §2.1–2.7, §3.1.
- **Ofgem, *State of the Market: Energy Retail Highlights*, Jan 2026.**
  <https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf>
  - "Debt and arrears".
- **Ofgem, *PPM decision — standard licence conditions (electricity)*, Sep 2023.**
  <https://www.ofgem.gov.uk/sites/default/files/2023-09/PPM%20decision%20standard%20licence%20ELEC_1.pdf>
  - SLC 28.7–28.9, definitions.
- **Ofgem, *PPM Guidance (Safe and Reasonably Practicable)*, Sep 2023.**
  <https://www.ofgem.gov.uk/sites/default/files/2023-09/PPM%20Guidance_Safe%20and%20Reasonably%20Practicable.pdf>
  - Lines on "75+", "under 2"; §5.2 (£200 per fuel); §5.6 ("at least 10 attempts").
- **Ofgem, involuntary-PPM press releases and pages.** The Code of Practice of 18 Apr 2023;
  restart permissions in 2024; *Extending protections on prepayment meters installed under warrant
  to 2027*.
  <https://www.ofgem.gov.uk/guidance/involuntary-prepayment-meter-energy-supplier-code-practice>
- **Energy UK, *Energy debt: everyone pays*, Feb 2026.**
  <https://www.energy-uk.org.uk/wp-content/uploads/2026/02/Energy-UK_Energy-Debt-Everyone-Pays_February-2026.pdf>
  - pp. 4–6, Fig. 5, pp. 10–13, p. 19.
- **Centrica plc, *Annual Report and Accounts 2025*.**
  <https://www.centrica.com/media/ckfb0qxj/annual-report-and-accounts-2025-untagged.pdf>
  - Retail bad debt in the Strategic report; Audit and Risk Committee; Note 17.
- **DWP, *Deductions guidance* V19 (House of Commons deposited paper DEP2025-0769).**
  <https://data.parliament.uk/DepositedPapers/Files/DEP2025-0769/057_DeductionsGuidance_V19.pdf>
- **Behavioural Insights Team, *Testing behaviourally-informed messaging to increase rates of
  contact between mortgage lenders and customers facing arrears*, Jun 2018.**
  <https://www.bi.team/wp-content/uploads/2019/02/20180704-BIT-Final-Report-R1.pdf>
  - This is a mortgage study, not energy.
- **BIT, *Applying behavioural insights to reduce fraud, error and debt*, 2012.**
  <https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/60539/BIT_FraudErrorDebt_accessible.pdf>
  - Not re-read this pass. The SMS result is as summarised in search.
- **Re-cited from the consolidated notes, not re-fetched:**
  - Ofgem objections decision and IA 2016;
  - Ofgem social obligations 2015 report and annex;
  - StepChange 2019;
  - PFRC/StepChange 2025;
  - British Gas DD help page;
  - Pay.UK Bacs statistics;
  - NAO's 25%-on-plans restatement.
- **Deceased customers: secondary guides only** (afterlossguide.co.uk, withfarra.co.uk). Treated as
  practice description, not evidence of scale.
