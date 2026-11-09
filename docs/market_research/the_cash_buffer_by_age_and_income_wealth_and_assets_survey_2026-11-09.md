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

## 3. Results (D)

Round 8: 15,128 households with a positive weight; round 7: 17,534. The smallest published cell has 198 households.
**The intervals are a simple bootstrap (200 replicates).** The end-user file carries no PSU or strata, so they
understate the true variance. Treat them as a lower bound on the uncertainty.

| # | Result | Verdict |
|---|---|---|
| S1 | **19.5%** of households have under £1,000 liquid (round 8) | **Refuted**, narrowly: just under 20% |
| S2 | Median buffer: under 35 **£4,000**, 75+ **£16,000**, ratio **4.0**. It peaks at 65-74 (£18,000) | **Refuted**: under 5, and not monotone at the top |
| S3 | Adjusted thin-buffer range: age **22.7 pp [19.0, 27.4]**, income quintile **34.3 pp [31.5, 37.1]**; difference -11.6 [-16.2, -6.3] | **Refuted. On the buffer, income outweighs life stage** |
| S4 | **68.7%** of households in non-mortgage arrears have a thin buffer (n = 313), against 17.1% of the rest | **Held** |
| S5 | Lowest income quintile, aged 65+: median buffer **£9,600** (n = 1,546), 16.3% thin | **Held** |
| S6 | Round 7 (2018-20): **23.6%** thin, against 19.5% in round 8: 4.1 points | **Held** |

**Buffer by age band and by income quintile, round 8 (weighted).**

| Reference person's age | <35 | 35-44 | 45-54 | 55-64 | 65-74 | 75+ |
|---|---|---|---|---|---|---|
| Median liquid, £ | 4,000 | 5,200 | 6,900 | 12,000 | 18,000 | 16,000 |
| Under £1,000, % | 28.0 | 22.4 | 23.3 | 19.1 | 13.1 | 9.8 |
| Households | 914 | 1,593 | 2,378 | 3,186 | 3,845 | 3,212 |

| Equivalised income quintile | 1 (lowest) | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Median liquid, £ | 3,000 | 4,000 | 7,300 | 13,600 | 27,200 |
| Under £1,000, % | 35.5 | 28.4 | 18.1 | 11.6 | 4.3 |
| Households | 2,810 | 2,746 | 2,740 | 3,041 | 3,664 |

The two ends of the joint: households in the lowest quintile whose reference person is under 45 have a median
buffer of **£700**, and 54.2% are thin (n = 351). Those in the top quintile and under 35 have **£15,000**, and 7.1% are
thin (n = 198).

## 4. What this means for the parsimony ruling, read with the sister page

1. **Income enters through the buffer, not through arrears.** On the Understanding Society record, age and income tie
   on arrears (16.0 against 16.6 pp), and income is only a moderate indicator of the precarity factor. On the buffer,
   income leads by 11.6 points. The affluence axis that 6614 could not separate from tenure shows up here, as the
   cash a household can draw on. Together, the two records support **two latent axes plus an observed age**:
   precarity (bill difficulty, a cold home, prepayment and renting, moderately related to income) and the cash buffer
   (led by income, rising with age). Age bears on both, and on neither alone.
2. **The cash-flow need (M3) has a measured size.** One household in five held under £1,000 in cash going into the crisis,
   and more than two in three households in arrears were thin. That is the population for which a catch-up bill or a
   direct-debit step-up arrives as a cash-flow event and not only as a cost.
3. **The age claim was too strong.** "Cash buffers rise steeply with age" (the 30 Oct synthesis) holds to 65-74 and
   then dips. Pensioners on low incomes still hold a median £9,600. So an income-poor pensioner is often cash-held,
   and income alone would misread them.
4. **Not established here.** The crisis itself: round 8 ends in March 2022, and round 9 is not held. The buffer was
   measured at a pandemic high (S6), so the crisis buffer was very likely lower than shown. The joint of the buffer
   with arrears is on one record here (S4) but rests on 313 households. Nothing on this page changes a world or
   supplier value.
