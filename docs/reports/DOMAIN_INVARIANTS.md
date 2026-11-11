# Domain invariants at git=6fe7827ab2

**0 unexcepted breach(es) across 0 invariant(s); 7 excepted. ENFORCED: nothing unexcepted, so the publish stands.**
- INV_UNIT_RATE_EPG_HOUSEHOLD 337: excepted until the printed energy line priced on the printed kWh (the same volume the Treasury's share is computed on), graded 0 on a fresh run
- INV_PPM_NOT_CREDIT_BILLED 12: excepted until a statement document type for the SME prepayment leg, or the invariant scoped to domestic accounts
- INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 7: excepted until the raw export carrying each account's void and occupier window, and the row exempting a month the payer did not hold on its 1st
- INV_EBSS_CREDIT_ON_THE_BILL 7: excepted until the raw export carrying each account's void and occupier window, as for INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23
- INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER 7: excepted until (a) an electrically heated home's estimate following its own seasonal shape from its reads, not the class average (whether a GB supplier does so is a GAP; knowledge page first). (b) and (c) are the row's lawful tail and stay excepted
- INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 1: excepted until the gas half of W2_30 (a fitted seasonal split for the premises now refused it, or a hot-water term that moves year to year), graded on a fresh run. If neither has landed by recheck_by, re-grade the newest book and re-file.
- INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD 2: excepted until the W2_30 slice n17_year_on_year_slice_note (docs/design/simplifications/W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape.yaml), with the premises' weather cells from the ERA5 pull (W1_14_weather_cells_for_household_heat_load), graded on a fresh run. If neither has landed by recheck_by, re-grade the newest book and re-file this with the newest counts.

Domain invariants over 1302 accounts

| invariant | status | breached | flagged | checked | unit |
|---|---|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | CLEAN | 0 (0.0%) | 0 (0.0%) | 5699 | SVT term x cap window it overlaps (single-register electricity) |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 2208 | SVT term x pre-cap half-year it overlaps (single-register electricity) |
| INV_UNIT_RATE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 4832 | SVT term x cap window it overlaps (gas) |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 1438 | SVT term x pre-cap half-year it overlaps (gas) |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 373 | SVT term x cap window it overlaps (multi-register electricity) |
| INV_UNIT_RATE_FIXED | FLAGGED | 0 (0.0%) | 8 (0.5%) | 1477 | fixed term, graded once at the window it was struck in |
| INV_UNIT_RATE_EPG_HOUSEHOLD | BREACHED | 337 (10.3%) | 0 (0.0%) | 3261 | domestic SVT bill period inside an EPG window (household all-in rate, ex-VAT) |
| INV_STANDING_CHARGE_SVT_ELEC | CLEAN | 0 (0.0%) | 0 (0.0%) | 21327 | SVT bill period (electricity) |
| INV_STANDING_CHARGE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 15980 | SVT bill period (gas; ceiling in DD-only windows) |
| INV_STANDING_CHARGE_FIXED | CLEAN | 0 (0.0%) | 0 (0.0%) | 17767 | fixed bill period |
| INV_ANNUAL_USE_ELEC_ACCOUNT | FLAGGED | 0 (0.0%) | 15 (0.8%) | 1794 | complete calendar account-year (electricity) |
| INV_ANNUAL_USE_GAS_ACCOUNT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1464 | complete calendar account-year (gas) |
| INV_ANNUAL_USE_BOOK_MEDIAN | CLEAN | 0 (0.0%) | 0 (0.0%) | 12 | TDCV row x fuel class (book median) |
| INV_READ_DUTY_ANNUAL | FLAGGED | 0 (0.0%) | 320 (28.1%) | 1139 | credit account (prepayment excluded): longest run without an actual read |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | FLAGGED | 0 (0.0%) | 1 (100.0%) | 1 | book (electricity kWh) |
| INV_BILL_AT_LEAST_TWICE_YEARLY | CLEAN | 0 (0.0%) | 0 (0.0%) | 47535 | bill period of a domestic credit account |
| INV_OPENING_READ | FLAGGED | 0 (0.0%) | 1302 (100.0%) | 1302 | account: days from first period_start to its typed opening read |
| INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1302 | account |
| INV_PAYMENT_AMOUNT_SIGN | CLEAN | 0 (0.0%) | 0 (0.0%) | 42543 | DD or prepayment payment |
| INV_DD_CADENCE | FLAGGED | 0 (0.0%) | 1 (0.0%) | 36167 | account-month with a DD payment |
| INV_DD_STEP_CHANGE | FLAGGED | 0 (0.0%) | 496 (1.4%) | 35355 | successive pair of positive DD collections |
| INV_PPM_NOT_CREDIT_BILLED | BREACHED | 12 (0.2%) | 0 (0.0%) | 6291 | period on a prepayment account |
| INV_FUEL_IDENTIFIER | CLEAN | 0 (0.0%) | 0 (0.0%) | 53921 | bill period |
| INV_GAS_SINGLE_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 590 | gas meter (account x meter_serial) |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | CLEAN | 0 (0.0%) | 0 (0.0%) | 28051 | electricity period on profile class 1 or 2 |
| INV_CROSS_FUEL_PRICE_SCALE | CLEAN | 0 (0.0%) | 0 (0.0%) | 10107 | SVT term x cap window it overlaps (both fuels) |
| INV_EV_ADOPTION_ELECTRICITY_ONLY | UNCHECKABLE | | | | UNCHECKABLE ON THE RAW EXPORT, and it must stay so (2026-10-30): the company holds no asset-change record. An EV, heat pump or PV install is |
| INV_PERIODS_CONTIGUOUS | CLEAN | 0 (0.0%) | 0 (0.0%) | 106540 | bill period (day count) and successive pair (contiguity) |
| INV_BACK_BILLING_12M | FLAGGED | 0 (0.0%) | 148 (0.4%) | 38580 | bill period of a domestic account from 2018-05-01 |
| INV_PERIOD_CONSUMPTION_NON_NEGATIVE | CLEAN | 0 (0.0%) | 0 (0.0%) | 57117 | register-period |
| INV_READ_MONOTONIC | CLEAN | 0 (0.0%) | 0 (0.0%) | 15605 | successive pair of actual reads on one register |
| INV_PERIOD_MATCHES_READS | CLEAN | 0 (0.0%) | 0 (0.0%) | 53921 | period billed on reads |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | CLEAN | 0 (0.0%) | 0 (0.0%) | 55563 | successive pair of periods on one meter register |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | CLEAN | 0 (0.0%) | 0 (0.0%) | 99 | change of printed register set between contiguous periods on one serial |
| INV_VAT_RATE | CLEAN | 0 (0.0%) | 0 (0.0%) | 53921 | period |
| INV_NON_COMMODITY_WITHIN_ALL_IN | CLEAN | 0 (0.0%) | 0 (0.0%) | 53921 | period |
| INV_REGISTER_ID_ONE_LABEL | CLEAN | 0 (0.0%) | 0 (0.0%) | 57117 | register id on one period, and each relabel between periods on one serial |
| INV_SERIAL_REGISTER_COUNT_STABLE | FLAGGED | 0 (0.0%) | 2 (0.0%) | 106540 | period, and each successive pair of periods on one serial |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | CLEAN | 0 (0.0%) | 0 (0.0%) | 32959 | domestic account on an SVT term on the 1st of a month (unit rate; standing charge) |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | BREACHED | 7 (0.3%) | 0 (0.0%) | 2321 | account-month on supply, Oct 2022 to Mar 2023 |
| INV_RENEWAL_NOTICE_42_TO_49_DAYS | CLEAN | 0 (0.0%) | 0 (0.0%) | 1304 | domestic fixed term owed a statement |
| INV_OVERDUE_WITHIN_BALANCE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1013 | collections journey opening |
| INV_ESTIMATE_RUN_WITHIN_TENURE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1 | estimate run printed on the page, against its leg's bills by the moment's date |
| INV_COLLECTIONS_EVENTS_ORDERED | CLEAN | 0 (0.0%) | 0 (0.0%) | 1013 | collections journey |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | UNREACHED | 0 | 0 | 0 | statute-barred write-off |
| INV_MPAN_CORE_FORMAT | CLEAN | 0 (0.0%) | 0 (0.0%) | 712 | electricity supply point (account, MPAN core) |
| INV_EBSS_CREDIT_ON_THE_BILL | BREACHED | 7 (0.3%) | 0 (0.0%) | 2321 | bill covering a qualifying 1st, Oct 2022 to Mar 2023 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | CLEAN | 0 (0.0%) | 0 (0.0%) | 6385 | household collections step printing an overdue figure |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1302 | account (page revenue against page bills before VAT) |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1139 | account (printed payment counter against collections due) |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | CLEAN | 0 (0.0%) | 0 (0.0%) | 8836 | account-year on both panels |
| INV_SMART_METER_BILLED_ON_ITS_OWN_READS | FLAGGED | 0 (0.0%) | 21 (105.0%) | 20 | fuel-year of Smart bills |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | FLAGGED | 0 (0.0%) | 232 (0.7%) | 31375 | estimated bill on a rung its declared policy grades |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | BREACHED | 7 (0.2%) | 25 (0.6%) | 4425 | run of estimated bills bounded by actual reads |
| INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1302 | supply points printing a meter type |
| INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE | UNCHECKABLE | | | | UNCHECKABLE BY THE RUNNER, by design rather than for want of a field: the committed panel is computed in the page's own JavaScript (stagePri |
| INV_METER_SERIAL_ONE_SUPPLY_POINT | CLEAN | 0 (0.0%) | 0 (0.0%) | 53921 | bill period (commodity, meter_serial, supply point) |
| INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF | CLEAN | 0 (0.0%) | 0 (0.0%) | 24274 | gas read/bill record (one period's register advance) |
| INV_TWO_RATE_BILL_PRINTS_ONE_READ_PAIR_PER_REGISTER | UNCHECKABLE | | | | NOT YET GRADED (2026-11-03): no evaluator in tools/domain_invariant_runner. Written blind, from docs/market_research and site/data/knowledge |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | BREACHED | 1 (0.7%) | 2 (1.4%) | 140 | gas leg with a measured month a year after another |
| INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD | BREACHED | 2 (200.0%) | 58 (5800.0%) | 1 | electricity book (measured month-pairs) |
| INV_BACK_BILLING_ON_RECEIPT_FROM_ISSUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 560 | undercharge catch-up on a credit bill paid on receipt, issued with 21BA in force |
| INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL | CLEAN | 0 (0.0%) | 0 (0.0%) | 1248 | re-offer of the repayment plan (a further bill missed) |
| INV_CAST_TARIFF_LABEL_IS_THE_BILLED_TERM | FLAGGED | 0 (0.0%) | 21 (50.0%) | 42 | Explore cast moment x fuel leg it prints a tariff for |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP_ALL_IN_FLOOR | CLEAN | 0 (0.0%) | 0 (0.0%) | 1438 | SVT term x pre-cap half-year it overlaps (gas) |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP_ALL_IN_FLOOR | CLEAN | 0 (0.0%) | 0 (0.0%) | 2208 | SVT term x pre-cap half-year it overlaps (single-register electricity) |
| INV_DEFAULT_DUAL_FUEL_COST_FOLLOWS_THE_PUBLISHED_DEFAULT_BILL | CLEAN | 0 (0.0%) | 0 (0.0%) | 3 | year on year, DD default dual fuel at 3100/12000 kWh (months priced: 2016 9, 2017 12, 2018 12, 2019 12, 2020 12, 2021 12, 2022 12, 2023 12, 2024 12, 2025 6) |
| INV_DEFAULT_TARIFF_TWO_REGISTER_INVOICE_WITHIN_MULTI_REGISTER_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 842 | printed Day/Night bill on a default term (not graded: 592 not a default term, 246 pre-cap, 78 spans a term change) |
| INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE | CLEAN | 0 (0.0%) | 0 (0.0%) | 842 | printed Day/Night bill (g 916, no note, within 842) |
| INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE | FLAGGED | 0 (0.0%) | 1 (100.0%) | 1 | book: its successful DD collections, graded on Leg A |
| INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM | FLAGGED | 0 (0.0%) | 1051 (2.2%) | 47552 | printed bill with a tariff label |
| INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED | FLAGGED | 0 (0.0%) | 19 (67.9%) | 28 | Explore cast moment printing a household payment tally |
| INV_DD_COLLECTION_IS_DATED_ON_A_BACS_PROCESSING_DAY | CLEAN | 0 (0.0%) | 0 (0.0%) | 36305 | direct debit collection |
| INV_DD_DUE_ON_A_NON_PROCESSING_DAY_IS_COLLECTED_ON_THE_NEXT_PROCESSING_DAY | UNCHECKABLE | | | | GAP (1): the "next working day" rule is quoted from Bacs bank-holiday guidance (via CIPP) and Pay.UK for bank holidays, and from a vendor (G |
| INV_DD_COLLECTIONS_PILE_ONTO_MONDAYS_AS_THE_WEEKEND_ROLL_PREDICTS | UNCHECKABLE | | | | GAP: no source publishes the distribution of GB energy customers' chosen collection days, or the weekday distribution of energy DD collectio |
| INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START | FLAGGED | 0 (0.0%) | 192 (20.2%) | 950 | account paying by direct debit from its first payment |
| INV_OPENING_DAY_CREDIT_IS_ONLY_WHAT_WAS_COLLECTED_ON_OR_AFTER_SUPPLY_START | UNCHECKABLE | | | | GAP (1): only Octopus was found publishing a collection ON the supply start date. Suppliers that collect after it would show £0 on the welco |
| INV_GAS_AGAINST_WEATHER_IS_COMPUTED_OVER_FULL_SUPPLIED_YEARS_ONLY | UNCHECKABLE | | | | GAP (1): CalTRACK's 365-day/37-missing-day rule is for a savings baseline, not a year-on-year weather correlation. It is borrowed as the nea |
| INV_GAS_WEATHER_R_IS_PRINTED_ONLY_WITH_THE_BOUND_ITS_YEARS_EARN | UNCHECKABLE | | | | GAP (1): no knowledge page read here gives the published year-to-year spread of GB annual HDD 2016-2025, or the published distribution of a  |
| INV_WINTER_SUMMER_RATIO_NEEDS_A_FULL_WINTER_AND_A_FULL_SUMMER | UNCHECKABLE | | | | GAP: CalTRACK's 90% is a savings-baseline coverage rule, borrowed as the nearest published sufficiency rule. No source sets one for a househ |
| INV_ELECTRIC_HEATING_VERDICT_AGREES_WITH_THE_HOMES_GAS_SUPPLY | UNCHECKABLE | | | | GAP (1): SERL's 1.36-1.47 is the MEDIAN gas-heated home's monthly max/min, not a per-household band, and not the Dec-Feb/Jun-Aug ratio the p |
| INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO | FLAGGED | 0 (0.0%) | 87 (5.2%) | 1687 | closed account (one fuel leg) and each write-off on one |
| INV_REFUND_WITHIN_THE_PAGE_CREDIT | CLEAN | 0 (0.0%) | 0 (0.0%) | 176 | refund line on one fuel leg's page ledger |
| INV_FIXED_TERM_RATES_HOLD_FOR_THE_TERM | UNCHECKABLE | | | | GAP (1): the knowledge layer holds no licence text that forbids a supplier varying the price of a domestic Fixed Term Supply Contract during |
| INV_HOUSEHOLD_PAGE_LEDGER_SUMMARY_RECONCILES_TO_ITS_BALANCE | UNCHECKABLE | | | | GAP (1): the knowledge layer does not hold the SLC 31A / 31H text on what a statement of account must itemise (31A is read only through Ofge |
| INV_HOUSEHOLD_PAGE_PAID_STAGE_COVERS_EVERY_FUEL_ACCOUNT | UNCHECKABLE | | | | GAP (1): no licence text read requires a combined two-fuel balance on a household statement. The knowledge page marks the one-statement prac |
| INV_HOUSEHOLD_PAGE_NARRATED_FACT_IS_TRUE_OF_THE_ACCOUNT | UNCHECKABLE | | | | GAP (1): the 0.25 share (and the 0.5 breach line) is a stated belief chosen by the row, not a published threshold. No source in the knowledg |
