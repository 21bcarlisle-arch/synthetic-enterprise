**Knowledge:** the-customer-needs-framework

# Precarity, affluence and life stage on one record: Understanding Society wave 14 (2026-11-09)

The 30 Oct parsimony ruling asks for a few latent household factors (precarity, affluence and life stage), drawn from
the attributes that predict the rest, with the remainder left independent. Until now each candidate was graded one
attribute at a time from Ofgem's published one-way tables (CIM waves 3-6; framework page §7, page 4). Those pages left
two questions that only a joint record can answer:

1. Does **"life stage outweighs income"** hold once both are measured on the same households, or is it age standing
   in for income (or the reverse)?
2. Is **precarity one factor**, and is income one of its indicators or a separate axis? The framework page found that
   bill difficulty separates the needs and income band does not, but it could not hold the two together.

**Data.** Understanding Society, UKDS SN 6614, wave 14 (`n_`, fieldwork 2022-2024: the crisis wave), household
response file joined to the household reference person's age. The analysis unit is the household, and it is weighted
by the household cross-sectional weight. The licensed files are read in `~/ukds/` only (W11 as amended 3 Nov). This
page holds only aggregate outputs: weighted percentages, contrasts and loadings.

**Disclosure rule used here.** No cell is published on fewer than 30 unweighted households. Percentages are given to
one decimal place and loadings to two. No record, identifier or row leaves `~/ukds/`. Citation:
University of Essex, Institute for Social and Economic Research (2025). *Understanding Society: Waves 1-15, 2009-2024
and Harmonised BHPS: Waves 1-18, 1991-2009.* UK Data Service. SN: 6614.

**Grades.** D = derived here from the record. This page changes no world or supplier value.

## 1. Definitions, fixed before any outcome was read

Only the data dictionary (variable names, labels and codes) had been read when this section was written.

- **Behind on bills**: `xphsdba` = "behind with some bills" or "behind with all bills". This covers all household
  bills, not energy alone. Wave 14 has no energy-specific arrears question.
- **Precarity indicators** (household): behind on bills; problems paying for housing (`xphsdb`); cannot keep the home
  adequately warm (`hheat` = No); would like savings of £x a month but cannot afford them (`matdepf` = 2); cannot afford
  contents insurance (`matdepe` = 2); cannot afford a holiday (`matdepa` = 2); the reference person finds it quite or
  very difficult to manage financially (`finnow` 4-5).
- **Affluence indicators**: log equivalised net household income (`fihhmnnet1_dv` / `ieqmoecd_dv`); owner occupier
  (`tenure_dv` 1-2); number of cars.
- **Life stage**: the reference person's age (`hrpid` joined to `indall.age_dv`); children present (`nkids_dv` > 0);
  pensioner present (`npensioner` > 0).
- **Income quintile**: weighted quintiles of equivalised net income across all households.
- **Payment method**: the electricity (or dual-fuel) payment code for prepayment, as labelled in the dictionary.

## 2. Predictions, filed before any outcome was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| U1 | 4-10% of households are behind with some or all bills | outside 4-10% |
| U2 | **Life stage outweighs income** on arrears, on the record: in a weighted logistic model of behind on bills on reference-person age band (6 bands) and income quintile together, the age range (highest minus lowest band's average predicted share) exceeds the income-quintile range | income range ≥ age range |
| U3 | Reference persons aged 65+ are behind on bills in under 2% of households | 2% or more |
| U4 | **Precarity is one factor and income is not its indicator.** A one-factor model on the seven precarity indicators gives every indicator a loading ≥ 0.40; added to that model, log equivalised income loads with an absolute value under 0.50 | any indicator under 0.40, or income ≥ 0.50 |
| U5 | **Affluence is separate from precarity**: in a three-factor model on all indicators, income, owner occupation and cars load mainly (largest absolute loading) on a factor other than the one the arrears indicator loads on | income's largest loading is on the arrears factor |
| U6 | Prepayment for electricity is at least three times as common among households behind on bills as among those up to date | ratio under 3 |

Each verdict will sit beside its prediction. A refuted prediction stays as written.

## 3. Results

*To be filled from the fit. Nothing below this line was known when sections 1 and 2 were written.*
