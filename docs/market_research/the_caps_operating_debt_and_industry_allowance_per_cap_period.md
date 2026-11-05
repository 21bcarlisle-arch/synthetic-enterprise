**Knowledge:** price-cap

# What the cap allows a supplier to serve a domestic account, per cap period, and what the book charges (2026-11-04)

Written before changing `saas/cost_to_serve.py` (K8). It answers gap 2 of N21
(`docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_THE_PAGES_PUBLISH_A_FOURTEEN_PERCENT_MARGIN_AFTER_COST_TO_SERVE_AGAINST_THE_LIBRARYS_TWO_TO_FIVE_2026-11-04.md`).
That gap is that the book charged a flat, unanchored £55 per fuel account per year.

## 1. What is published

**Source.** Ofgem, *Default tariff cap level* model v1.28
(https://www.ofgem.gov.uk/sites/default/files/2025-11/Default-tariff-cap-level-v1.28.xlsx).
- **Sheets:** `ElecSingle_Other_Benchmark` and `Gas_Other_Benchmark`.
- **Basis:** direct debit (the "Other" payment method), nominal, ex VAT.
- **Benchmark consumption:** 3,100 kWh electricity and 12,000 gas to December 2025.
- Read cell by cell on 2026-11-04. Every component used here is **identical in all 15 regions**, checked
  programmatically.
- Columns before January 2019 are Ofgem's own back-casts of the 2017 benchmark ("for illustration only"). The cap
  was not in force then.

**The 2017 base.** Ofgem's operating cost benchmark is **£78.26 electricity and £89.20 gas per direct-debit customer
per year**, base period April–September 2017.
- Source: *Default Tariff Cap: Decision*, Appendix 6, Table A6.2
  (https://www.ofgem.gov.uk/system/files/docs/2018/09/appendix_6_-_operating_costs.pdf).
- The model's v1.28 April 2017 column reads 78.264 and 89.2021.
- The benchmark is set at the lower-quartile supplier less £5 per dual-fuel customer, about 15% above the frontier
  (§2.30–2.31).

**What OC contains** (Table A6.1):
- customer contact;
- billing, payment collections and **bad debt**;
- **metering**: rental, installation, maintenance and reading, including smart;
- **sales and marketing**, including third-party commissions;
- central overhead: IT, property, HR, regulation;
- **depreciation and amortisation**;
- industry charges: Elexon, Xoserve and the smart-metering bodies.

ECO and FiT administration are removed (they sit in the policy allowance). WHD administration is added (Table A6.3).

**The components, by cap period from 2019 (£ per account per year at benchmark consumption, DD).**
- **OC:** operating costs, CPIH-indexed from the 2017 base.
- **PAAC:** the fixed payment-method additional cost.
- **SMNCC:** the smart-metering net cost change.
- **CO and IC:** from July 2025, Ofgem's operating-cost review replaced OC and PAAC with core operating costs (CO)
  and industry charges (IC). Debt moved to DRC.

| Cap period from | Elec OC | Elec PAAC | Elec SMNCC | Gas OC | Gas PAAC | Gas SMNCC |
|---|---:|---:|---:|---:|---:|---:|
| Apr 2015 * | 76.50 | 3.35 | – | 87.19 | 3.11 | – |
| Oct 2015 * | 76.66 | 3.35 | – | 87.37 | 3.12 | – |
| Apr 2016 * | 76.89 | 3.36 | – | 87.63 | 3.13 | – |
| Oct 2016 * | 77.35 | 3.38 | – | 88.15 | 3.15 | – |
| Apr 2017 * | 78.26 | 3.42 | 0.00 | 89.20 | 3.19 | 0.00 |
| Oct 2017 * | 79.26 | 3.47 | −0.19 | 90.34 | 3.23 | −0.15 |
| Apr 2018 * | 80.41 | 3.52 | 2.39 | 91.65 | 3.27 | 1.90 |
| Oct 2018 * | 81.10 | 3.55 | 11.49 | 92.43 | 3.30 | 12.67 |
| Jan 2019 | 81.10 | 3.55 | 11.49 | 92.43 | 3.30 | 12.67 |
| Apr 2019 | 82.02 | 3.59 | 13.91 | 93.48 | 3.34 | 14.64 |
| Oct 2019 | 82.63 | 3.61 | 14.01 | 94.18 | 3.36 | 14.93 |
| Apr 2020 | 83.09 | 3.63 | 16.59 | 94.70 | 3.38 | 17.17 |
| Oct 2020 | 83.32 | 3.64 | 16.86 | 94.96 | 3.39 | 11.17 |
| Apr 2021 | 83.78 | 3.66 | 16.49 | 95.49 | 3.41 | 10.90 |
| Oct 2021 | 85.31 | 3.73 | 16.53 | 97.23 | 3.47 | 7.98 |
| Apr 2022 | 87.84 | 3.84 | 15.15 | 100.11 | 3.58 | 3.38 |
| Oct 2022 | 92.28 | 4.04 | 16.07 | 105.17 | 3.76 | 3.46 |
| Apr 2023 | 95.95 | 4.20 | 17.32 | 109.36 | 3.91 | 4.02 |
| Oct 2023 | 99.09 | 4.33 | 15.51 | 112.94 | 4.03 | 1.66 |
| Apr 2024 | 99.94 | 4.37 | 16.06 | 113.90 | 4.07 | 1.02 |
| Oct 2024 | 101.85 | 4.45 | 19.20 | 116.08 | 4.15 | 3.16 |
| Apr 2025 | 103.46 | 4.53 | 19.82 | 117.92 | 4.21 | 2.89 |
| Jul 2025 | CO 93.41 | IC 18.08 | 1.67 | CO 100.22 | IC 14.58 | −5.44 |
| Oct 2025 | CO 95.69 | IC 19.20 | −2.07 | CO 102.67 | IC 15.34 | −3.66 |

\* Ofgem back-cast. Quarterly periods from October 2022 repeat the half-year values shown, and are omitted here.

**Debt, published separately, and not used here:**
- **PAP** is the percentage payment-method uplift: bad debt plus working capital, DD 0.49% electricity and 0.41%
  gas of the core benchmark (Appendix 8, Table A8.1).
- **DRC** is the debt-related costs allowance from July 2025.
- The **adjustment allowance (AA)** carried two debt floats:
  - COVID-19 bad debt: April 2021, £9.98 electricity + £13.71 gas; October 2021, £4.43 each.
  - Additional debt-related costs: April 2024 to June 2025, £15.90 + £14.67.

  Its October 2022 to March 2024 values are wholesale-related (Ofgem's 24 August 2023 letter), and Ofgem publishes
  no split of them.

## 2. What the book already charges, and what is netted out

The book bears several of OC's categories on lines of its own:

| OC category | Book line | Netted from the charge? |
|---|---|---|
| DD bad debt inside OC: £0.84 electricity, £0.46 gas, 2017 (Appendix 6 §2.6) | emergent bad debt, ledger 6001 (`simulation/arrears_engine.py`) | **Yes.** Netted at the published figure, indexed with OC. |
| Bad debt and working capital beyond DD (PAP, DRC, AA floats) | bad debt 6001; capital cost 5200 | **Not charged.** None of them is in the sum. |
| Sales and marketing | acquisition spend, ledger 6300 (£74,230 on a6b7a0fd47) | **No: GAP.** Ofgem publishes no split of OC by category. It is charged whole, so the book double-counts some acquisition. On a6b7a0fd47 the bound is the book's own acquisition line, about £17 per leg-year. This errs *against* our thesis (F11). |
| Meter reading | read visits, ledger 6100 (£1,509) | **No.** Too small to net, and its share of OC is unpublished. |
| Central overhead | fixed cost, ledger 6200 (£5,700) | **No.** Same reason. |
| Depreciation | nothing (N21 gap 3) | It is inside OC, so charging OC closes gap 3 for the domestic book. |
| Smart metering (DCC, SEGB, SMICoP) | nothing on the P&L. `saas/opex_ledger.py` charges DCC only on its benchmark ledger. | SMNCC is charged. |

## 3. The charge, and the choices it makes

`saas/cost_to_serve.py` charges each **resi** fuel account, for each day it is served, 1/365 of:
- **OC + PAAC + SMNCC − DD bad debt in OC** for the cap period in force on that day, to June 2025;
- **CO + IC + SMNCC** from July 2025. CO excludes debt, so nothing is netted.

The choices:
- **Benchmark consumption, not nil.** The nil column (about £39–52 electricity) is the share Ofgem *recovers*
  through the standing charge. That is a tariff design choice, not the cost. `company/crm/renewal_advice_desk.py`
  credits the nil column as recovery, and that stays right. The cost per account is the benchmark figure.
  - **GAP:** Ofgem's benchmark scales a little with consumption. Charging it per account ignores that.
- **Direct debit.** SC's PAAC is about £10 more per fuel. The book has SC and PPM accounts, so this errs low, *for*
  our thesis, by up to about £10 per SC fuel-account-year. It is stated rather than modelled, because the charge
  would then depend on the payment channel the account is on each day.
- **Before April 2015:** the April 2015 figure. **After the last published period:** the last figure. Neither is
  reached by a 2016–2025 book.
- **SME and I&C:** unchanged at £120 and £500. The domestic cap does not cover them, and no published source
  decomposes their cost to serve: **GAP**.

**The band a dual-fuel DD account must sit in (the control).**
- Lower edge: the published OC + PAAC + SMNCC (or CO + IC + SMNCC) for both fuels, less DD bad debt.
- Upper edge: the same plus PAP and the debt floats at their published values. That is the whole
  "operating, debt and industry" allowance, about £15–40 more per dual-fuel account (PAP £4–15; the 2024–25
  debt float £30.57).
- The flat £110 per dual-fuel account sits **below the lower edge in every period**. That is what the test is red
  on.

**Reconciling the £297.92** that `ASSUMPTIONS.md` cites for July–September 2026.
- It is 16% of the £1,862 GB-average DD cap at 2,700 / 11,500 kWh, and it includes VAT and DRC.
- v1.30, Eastern, ex VAT, for the same period: CO + DRC + IC + SMNCC = £274.55.
- **GAP:** the remaining ~£9 after VAT is not reconciled here. The candidates are region and rounding.

## 4. Effect on the a6b7a0fd47 book (offline repricing, not a run)

Pre-registered in `docs/staging/records/SEAT_PREREGISTRATION_N21_MARGIN_UNDER_THE_CAPS_SOURCED_COST_TO_SERVE_2026-11-04.md`.
- Every leg-month in the run was repriced at the period's charge. The run carries no settlement records, so the
  module itself cannot be rerun over the book.
- **Cost to serve:** £240,607 → about **£447k**. By year it is 1.5× (2016) rising to 2.2× (2024–25).
- **N21's margin:** 15.50% → about **9.7%**. The next fresh book grades it.

**Downstream: the renewal desk now charges the same cost.**
- `company/crm/renewal_advice_desk.term_contribution_per_year` and `company/pricing/value_based_renewal` read the
  dated charge, so the one cost has one home.
- A 2019 electricity leg is now charged £98.63 against the £41.57 nil-column opex the desk credits as recovery.
  Under £55 it was £41.57 against £55.
- The rest of the cost is recovered through the unit rate's spread over its pre-margin floor. That spread is
  already inside the contribution. So more legs read negative, and the desk advises fewer households.
- That is the cost being real, not a defect. `next_best_action_and_cross_sell.md` §6.1 was written against the
  £55 and is noted there.
