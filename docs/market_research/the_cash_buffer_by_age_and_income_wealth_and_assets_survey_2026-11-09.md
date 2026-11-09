**Knowledge:** the-customer-needs-framework

# The cash buffer by age and income: Wealth and Assets Survey rounds 7 and 8 (2026-11-09)

The second half of the parsimony fit. The Understanding Society page
(`precarity_affluence_and_life_stage_on_one_record_understanding_society_2026-11-09.md`) found one precarity factor,
indicated by bill difficulty and tenure, and no separate affluence factor beyond tenure and assets. It left one wealth
question open: **how big a household's cash buffer is, by age and income.** That buffer is the size of the cash-flow
need (M3: cash flow, "when, and how much at once") and the headroom against a winter bill or a direct-debit step-up.
Today the world carries it as an assumption with a range (registration pack, row 7215).

**Data.** Wealth and Assets Survey, UKDS SN 7215. Round 8 household file (fieldwork April 2020 to March 2022, which
covers the pandemic, when savings rose) and round 7 (April 2018 to March 2020) as the pre-pandemic check. The
analysis unit is the household, weighted by the round's cross-sectional household weight. The licensed files are read
in `~/ukds/` only (W11 as amended 3 Nov). This page holds only aggregates.

**Disclosure rule used here.** No cell is published on fewer than 30 unweighted households. Medians are rounded to the
nearest £100 and shares to one decimal place. Citation: Office for National Statistics (2025). *Wealth and Assets
Survey, Waves 1-5 and Rounds 5-8, 2006-2022.* UK Data Service. SN: 7215.

## 1. Definitions, fixed before any value was read

Only the data dictionary had been read when this section was written.

- **Liquid savings** = current accounts in credit (`DVCaCrValR8_aggr`) + savings accounts (`DVSaValR8_aggr`) + cash
  ISAs (`DVCISAVR8_aggr`). Investment ISAs, bonds, shares and pensions are excluded: they cannot pay a bill this month
  without cost or delay.
- **Thin buffer** = liquid savings under £1,000.
- **Age** = reference person's grouped age (`HRPDVAge8R8`): 16-24 and 25-34 are merged as under 35, then 35-44,
  45-54, 55-64, 65-74, 75+.
- **Income quintile** = weighted quintiles of net equivalised income before housing costs (`NetEquIncAnn_BHCR8`).
- **In arrears** = household arrears excluding mortgage arrears above zero (`TotArr_excMortR8_aggr`).
- Round 7 uses the same variables with its own suffix.

## 2. Predictions, filed before any value was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| S1 | 20-35% of households have a thin buffer (round 8) | outside 20-35% |
| S2 | The median liquid buffer of households aged 75+ is at least 5 times that of households under 35 | ratio under 5 |
| S3 | **On the buffer, life stage outweighs income**: in a weighted logistic model of a thin buffer on age band and income quintile together, the age range exceeds the income range (the reverse of the arrears tie on the sister page would be a finding) | income range ≥ age range |
| S4 | At least 60% of households in arrears have a thin buffer | under 60% |
| S5 | In the lowest income quintile, households aged 65+ have a median buffer of at least £5,000 (income-poor, cash-held) | under £5,000 |
| S6 | Round 7's thin-buffer share is at least 3 points above round 8's (pandemic saving) | gap under 3 points |

## 3. Results

*To be filled from the fit. Nothing below this line was known when sections 1 and 2 were written.*
