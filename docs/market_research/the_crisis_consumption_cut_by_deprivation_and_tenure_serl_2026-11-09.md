**Knowledge:** the-customer-needs-framework

# The crisis consumption cut by deprivation and tenure: SERL smart-meter statistics 2020-2023 (2026-11-09)

The fourth step of the registration pack's order (`docs/director/UKDS_REGISTRATION_PACK.md`). The price-sensitivity
evidence could state how much households cut their use in the crisis only from survey answers. SERL's statistical
release measures it from smart meters, by group. The question is: **how much did gas-heated homes cut their gas, weather
adjusted, in the winter of the Energy Price Guarantee, and did the deprived and the renters cut more or less than the
rest?** The precarity factor (sister pages) is what the world would scale such a response by; SERL holds no payment
method or income, so its two precarity-adjacent groupings are **area deprivation (IMD quintile)**, which a supplier
can observe from the postcode, and **tenure**.

**Data.** Smart Energy Research Lab: Statistical Data, 2020-2023, Safeguarded Access (SN 8963, 2nd edition), file
`serl_daily_energy_use_in_gb_domestic_buildings_2020_to_2023_aggregated_statistics.csv`. It is already aggregated by
SERL: each row is a group's mean daily use in a month, with the group's mean heating degree days (`mean_hdd`). Counts
are rounded to the nearest 10, and groups under 10 are suppressed by the depositor. Read in `~/ukds/` only. **Disclosure
here:** I publish only group means and contrasts of groups of at least 100 homes. Citation: Elam, S., Few, J., McKenna,
E., Hanmer, C., Pullinger, M., Zapata-Webborn, E., Oreszczyn, T., Anderson, B., DLUHC, ECMWF, Royal Mail Group (2024).
*Smart Energy Research Lab: Statistical Data, 2020-2023: Safeguarded Access.* 2nd Edition. UK Data Service. SN: 8963,
DOI: 10.5255/UKDA-SN-8963-2.

## 1. Definitions, fixed before any value was read

Only the documentation, the column names and the list of groups and months had been read.

- **Homes:** primary space heating = gas, PV = all, weekday and weekend together, unit kWh/day.
- **Weather model, per group:** the group's monthly mean daily gas use = a + b × the group's monthly mean HDD, fitted by
  ordinary least squares on the twelve months of **2021** (the baseline year: the price cap stood at £1,138-1,277).
- **The crisis winter:** October 2022 to March 2023 (the Energy Price Guarantee's first winter).
- **The cut** = 1 − (sum of actual monthly means over the crisis winter) / (sum of the baseline model's predictions at
  those months' HDD). Absolute cut in kWh/day is the same difference averaged over the six months.
- **Sensitivity, fixed now:** refit the baseline on April-December 2021 only, which leaves out the January-March 2021
  lockdown, when people were at home more. If the two baselines give cuts more than 3 points apart, the page says the
  lockdown months move the answer.
- **Groups:** IMD quintile (1 = most deprived) and tenure (owner outright or mortgaged, private rent, social rent).
- **Electricity:** the same model for electricity imports in the same gas-heated homes.
- **Persistence:** the same cut computed for October-December 2023 against the same 2021 baseline.
- **The panel changes.** SERL grew from about 2,700 gas-heated homes in 2020 to about 8,100 later. Each month's mean is
  over whichever homes reported that month, so a cut mixes behaviour with the changing make-up of the panel. A
  comparison within a group (the same IMD quintile, the same tenure) controls only part of that.

## 2. Predictions, filed before any value was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| C1 | All gas-heated homes cut weather-adjusted gas by 10-20% in the crisis winter | outside 10-20% |
| C2 | **The most deprived cut less, in percent**: IMD quintile 1's cut is at least 2 points smaller than quintile 5's | gap under 2 points, or reversed |
| C3 | **Social renters cut less, in percent**, than owner-occupiers, by at least 2 points | gap under 2 points, or reversed |
| C4 | Electricity imports fall by a smaller percentage than gas | electricity's cut ≥ gas's |
| C5 | The cut persists: October-December 2023's cut is at least half the crisis winter's | under half |
| C6 | In kWh/day, the least deprived quintile's absolute gas cut is larger than the most deprived's | not larger |

Each verdict will sit beside its prediction. A refuted prediction stays as written.
