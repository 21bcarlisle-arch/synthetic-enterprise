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

## 3. Results (D)

Weighted by `hhdeng2_xw`. 21,385 households carry a positive weight. Intervals are 95% from 200 bootstrap replicates
that resample PSUs within strata. The smallest published cell has 1,286 households.

| # | Result | Verdict |
|---|---|---|
| U1 | **10.2%** of households are behind with some or all bills (n = 21,270) | **Refuted**, narrowly: just over the 10% bound |
| U2 | Age range **16.0 pp [14.6, 17.6]**; income-quintile range **16.6 pp [14.8, 18.6]**; difference -0.6 [-2.6, 1.2]. With tenure and children added, 11.0 against 10.3 | **Refuted as worded.** On arrears the two are a tie, not an ordering |
| U3 | **2.5%** of households whose reference person is 65+ (n = 7,258): 3.7% at 65-74, 1.3% at 75+ | **Refuted**: the 65-74 band carries it over |
| U4 | One factor, seven indicators (n = 8,385; see the caution below): loadings 0.72-0.85. Income added: **-0.39** | **Held** on measured income. Not robust: see §4 |
| U5 | Three factors (n = 8,335): arrears loads on factor 3 (0.75); income's largest loading is -0.27 on factor 2 (owner -0.86, cars -0.57), against -0.25 and -0.19 on the others | **Held as worded, and it does not support an affluence factor.** Income splits almost evenly across all three, and the eigenvalues (5.53, 1.05, 0.80) support one strong factor and a weak second, not three |
| U6 | Prepayment for electricity: **36.0%** of households behind on bills (n = 1,573) against **10.4%** up to date (n = 18,492), ratio **3.45** | **Held** |

**Caution on U4 and U5. The sample I specified was selected, which I did not know when I wrote the definitions.** Wave
14 asks the material-deprivation items of non-pensioner households only (2.3% coverage where a pensioner is present),
because pensioners get a separate module. It asks the housing-payment item only of households with housing costs (none
of the outright owners). So U4 and U5 ran on non-pensioner households with rent or a mortgage. The verdicts stand as
graded, but they describe that population. §4 re-runs the test on the indicators asked of every household.

**Behind on bills by age band and income quintile, one-way (weighted %).**

| Reference person's age | <30 | 30-39 | 40-49 | 50-64 | 65-74 | 75+ |
|---|---|---|---|---|---|---|
| Behind on bills | 15.8 | 17.6 | 14.9 | 10.1 | 3.7 | 1.3 |
| Households | 1,294 | 2,744 | 3,496 | 6,470 | 3,859 | 3,399 |

| Equivalised income quintile | 1 (lowest) | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Behind on bills | 20.2 | 12.2 | 9.8 | 5.7 | 3.3 |
| Households | 3,824 | 4,160 | 4,183 | 4,443 | 4,613 |

## 4. On every household: four indicators asked of all (D)

These indicators are asked of every household: behind on bills, cannot keep warm, finding it difficult (reference
person), prepayment, log equivalised income, owner occupation and cars. On them, n = 17,473.

- **One precarity factor:** eigenvalues 3.50, 1.04, 0.85. One-factor loadings: arrears +0.83, finding it difficult
  +0.69, cannot keep warm +0.67, prepayment +0.63, **owner occupation -0.81**, cars -0.45, **income -0.37**.
- **Two factors (varimax):** one is difficulty (finding it difficult -0.82, arrears -0.71, cold -0.69), the other tenure
  and assets (owner +0.90, prepayment -0.66, cars +0.49). **Income loads +0.27 and +0.24: weakly, and equally, on
  both.**
- **Age and income are nearly independent of each other** (r = +0.03) and both relate to arrears: age -0.34 and
  income -0.29 (biserial). That is why U2's adjusted ranges equal its one-way ranges: in this record age does not stand
  in for income, nor income for age.
- **Is income weak only because one month's income is noisy?** This is the threat that flatters our thesis, so it was
  tested (F11). For the 13,699 households whose reference person also headed a household in wave 13, the two waves'
  log equivalised incomes correlate at only **0.51**. Averaging them strengthens every income relation: arrears -0.30
  to -0.34, and the factor loading -0.37 to **-0.43** (n = 11,787). A reliability correction for the remaining noise
  would put it at about -0.5. **So U4's income bound holds on measured income, but not once noise is allowed for.**
  The robust statement is narrower: income is a weaker indicator of precarity than bill difficulty, a cold home,
  prepayment or tenure, and it is not negligible.

## 5. What this means for the parsimony ruling

1. **Precarity is one factor, and its indicators are difficulty and tenure, not income.** Arrears, a cold home,
   finding it difficult and prepayment load 0.63-0.85. Renting loads as strongly (0.81). Income is a moderate
   correlate (-0.37 to about -0.5 after noise). This confirms, on one record, the framework page's split ("precarity
   read as bill difficulty works, read as income does not") and sizes it. The world already draws a financial-stress
   state that drives nothing yet (`vuln.ability_to_pay`). This page is evidence for wiring that state as the precarity
   factor, correlated with tenure and only moderately with income, rather than deriving it from income.
2. **Life stage is a separate axis, and on arrears it ties with income rather than outweighing it.** The CIM finding
   (age range 33 pp against income 12 pp on switching intent) was about stated intent. On revealed arrears the two
   ranges are 16.0 and 16.6 pp, independent and additive. Tenure absorbs about a third of each.
3. **Affluence is not a third factor in this record.** What separates from difficulty is tenure and assets (owner
   occupation, cars, not prepaying), with income attached weakly to both. The remaining wealth question, liquid savings
   by age and income, is SN 7215's to answer. It is the next increment of this work, not done here.
4. **What a supplier could observe:** prepayment, arrears and contact are a supplier's own records. Tenure and age are
   held only if the customer gives them. Income is not held. Factors 1 and 2 are therefore largely visible through the
   supplier's own observables (W1).

**Not established here.** Energy-specific arrears: wave 14 asks about bills in general. Cause: these are
cross-sectional associations. Effects within a household over time: this page fits nothing longitudinal beyond the
two-wave income average. No world or supplier value changes on this page.
