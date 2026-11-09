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

## 3. Results (D)

Gas-heated homes, 7,140 or more reporting in each crisis-winter month. The smallest published group is social renters
(620 homes). Groups under 100 homes (part-own, rent free, no answer) are not shown. **Intervals** are 95% from 2,000
draws that perturb each monthly mean by SERL's own standard error. They treat months as independent, which is rough,
and they do not cover the panel's changing make-up (§1).

**The lockdown months move the answer.** On the registered 2021 baseline, the cut is 12.7%. Leaving out January-March
2021 gives 6.9%. That is 5.8 points apart, over the 3-point bound set in §1, so both are shown. The lockdown inflated
2021's winter use, which flatters the cut; the April-December baseline has only three heating months to fit the slope.
**The honest statement is a cut of 7-13%.** The SERL panel holders' own estimate, on per-home data, is a median of
10.8% (on file as P, `heating_behaviour_comfort_and_health_floors_2026-10-25.md` §5), which sits inside it.

| # | Result (registered baseline; April-December 2021 in brackets) | Verdict |
|---|---|---|
| C1 | All gas-heated homes: **12.7% [12.0, 13.3]** (6.9% [6.1, 7.8]) | **Held on the registered baseline**, which the sensitivity shows is lockdown-inflated |
| C2 | IMD 1 minus IMD 5: **+1.6 points [-0.4, +3.6]** (-0.1 [-2.6, +2.6]). The most deprived cut **at least as much** | **Refuted**: no deprivation gradient in the percentage cut |
| C3 | Social renters minus owner-occupiers: **+0.5 [-1.8, +2.8]** (+0.5 [-2.5, +3.5]) | **Refuted**: social renters cut the same |
| C4 | Electricity imports minus gas: **+0.9 [-0.2, +1.9]** (+2.6 [+1.1, +4.0]) | **Refuted**: electricity fell by at least as much as gas |
| C5 | October-December 2023: **5.7%**, 0.45 of the crisis winter's 12.7% | **Refuted**, narrowly: just over half the cut had gone by late 2023. The two windows cover different months |
| C6 | Absolute gas cut: IMD 5 **8.2 kWh/day**, IMD 1 **6.1** | **Held** |

**By group, gas, crisis winter (cut %, registered baseline; April-December baseline in brackets).**

| IMD quintile (1 = most deprived) | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Gas cut | 14.4 (7.6) | 12.9 (6.7) | 13.9 (8.0) | 11.1 (5.5) | 12.8 (7.8) |
| kWh/day | 6.1 | 6.0 | 7.2 | 6.2 | 8.2 |
| Homes (fewest in a month) | 1,420 | 1,580 | 1,330 | 1,310 | 1,500 |

| Tenure | Own outright or mortgage | Private rent | Social rent |
|---|---|---|---|
| Gas cut | 13.1 (7.2) | **17.0 (11.2)** | 13.5 (7.7) |
| Electricity cut | 14.6 (10.5) | 9.4 (5.5) | 10.2 (5.6) |
| Homes (fewest in a month) | 5,920 | 420 | 620 |

Private renters cut gas **3.9 points more** than owner-occupiers [+1.2, +6.6] (+4.0 [+0.5, +7.4] on the other
baseline): the one group contrast that clears zero on both.

## 4. What this means

1. **The crisis cut was general, not concentrated in the comfortable.** In percent, the most deprived areas cut gas as
   much as the least deprived, and social renters as much as owners. I predicted the reverse (C2, C3), on the
   reasoning that the deprived had less headroom. That reasoning is not supported at area level. The absolute cut is
   larger where use is larger (C6), so the kWh and the pounds saved still lean to the better-off.
2. **Private renters cut gas the most**, against the CIM survey finding that renters lower the thermostat less often
   (sister page §2). One reading consistent with both: renters who cannot change the boiler heat fewer hours or rooms.
   This page cannot tell which. It is a lead for the comfort-floor page, not a finding about the floor.
3. **For the world's model of crisis demand:** a weather-adjusted fall of 7-13% in gas and a similar fall in
   electricity in the EPG winter, with no deprivation gradient in percent, partly persisting into late 2023. Area
   deprivation is not a lever on the size of the cut. This bears on the open GAP on the price-sensitivity page (an
   elasticity of consumption by income band): at area level the gradient is flat. **It is not an income-band answer**:
   SERL's statistical release has no household income, and IMD is a property of the area, not the household.
4. **For the precarity proxy (sister page):** IMD is the one precarity-adjacent grouping a supplier holds for every
   customer, from the postcode. On consumption response it separates nothing. Whether it separates precarity itself is
   not testable on the end-user Understanding Society file, which carries no IMD.

**Not established here.** Per-home distributions (SERL's per-home Observatory needs a university partnership). How much
of the cut is the panel's changing make-up. The cut by income or payment method. No world or supplier value changes on
this page.
