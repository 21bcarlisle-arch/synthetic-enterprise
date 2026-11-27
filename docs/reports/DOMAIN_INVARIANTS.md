# Domain invariants at git=601887d76a

**0 unexcepted breach(es) across 0 invariant(s); 6 excepted. ENFORCED: nothing unexcepted, so the publish stands.**
- INV_UNIT_RATE_EPG_HOUSEHOLD 381: excepted until the printed energy line priced on the printed kWh (the same volume the Treasury's share is computed on), graded 0 on a fresh run
- INV_PPM_NOT_CREDIT_BILLED 12: excepted until a statement document type for the SME prepayment leg, or the invariant scoped to domestic accounts
- INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER 3: excepted until none. All six on the 001e4f680a book are (a), the row's lawful tail under a published practice (section 11). A gas run like (b) would leave under British Gas's same-period-last-year rule, which is not built (section 11)
- INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 4: excepted until the gas half of W2_30 (a fitted seasonal split for the premises now refused it, or a hot-water term that moves year to year), and a post-heat-pump gas residual that carries cooking's season (the finding above), graded on a fresh run. If neither has landed by recheck_by, re-grade the newest book and re-file.
- INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD 1: excepted until the W2_30 slice n17_year_on_year_slice_note (docs/design/simplifications/W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape.yaml), with the premises' weather cells from the ERA5 pull (W1_14_weather_cells_for_household_heat_load), graded on a fresh run. If neither has landed by recheck_by, re-grade the newest book and re-file this with the newest counts.
- INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT 7: excepted until n29-close-set-off-nets-issued-debt: the set-off nets the other leg's issued, not-yet-collected final bill on the refund day (home_moves.md s.8.8e, next free choice), graded 0 on a fresh run.

Domain invariants over 1382 accounts

| invariant | status | breached | flagged | checked | unit |
|---|---|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | CLEAN | 0 (0.0%) | 0 (0.0%) | 5667 | SVT term x cap window it overlaps (single-register electricity) |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 2191 | SVT term x pre-cap half-year it overlaps (single-register electricity) |
| INV_UNIT_RATE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 4762 | SVT term x cap window it overlaps (gas) |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 1385 | SVT term x pre-cap half-year it overlaps (gas) |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 376 | SVT term x cap window it overlaps (multi-register electricity) |
| INV_UNIT_RATE_FIXED | FLAGGED | 0 (0.0%) | 55 (3.6%) | 1539 | fixed term, graded once at the window it was struck in |
| INV_UNIT_RATE_EPG_HOUSEHOLD | BREACHED | 381 (11.4%) | 0 (0.0%) | 3339 | domestic SVT bill period inside an EPG window (household all-in rate, ex-VAT) |
| INV_STANDING_CHARGE_SVT_ELEC | CLEAN | 0 (0.0%) | 0 (0.0%) | 21291 | SVT bill period (electricity) |
| INV_STANDING_CHARGE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 15703 | SVT bill period (gas; ceiling in DD-only windows) |
| INV_STANDING_CHARGE_FIXED | CLEAN | 0 (0.0%) | 0 (0.0%) | 18269 | fixed bill period |
| INV_ANNUAL_USE_ELEC_ACCOUNT | FLAGGED | 0 (0.0%) | 33 (1.9%) | 1781 | complete calendar account-year (electricity) |
| INV_ANNUAL_USE_GAS_ACCOUNT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1438 | complete calendar account-year (gas) |
| INV_ANNUAL_USE_BOOK_MEDIAN | CLEAN | 0 (0.0%) | 0 (0.0%) | 12 | TDCV row x fuel class (book median) |
| INV_READ_DUTY_ANNUAL | FLAGGED | 0 (0.0%) | 323 (27.0%) | 1196 | credit account (prepayment excluded): longest run without an actual read |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | FLAGGED | 0 (0.0%) | 1 (100.0%) | 1 | book (electricity kWh) |
| INV_BILL_AT_LEAST_TWICE_YEARLY | CLEAN | 0 (0.0%) | 0 (0.0%) | 47317 | bill period of a domestic credit account |
| INV_OPENING_READ | FLAGGED | 0 (0.0%) | 1382 (100.0%) | 1382 | account: days from first period_start to its typed opening read |
| INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1382 | account |
| INV_PAYMENT_AMOUNT_SIGN | CLEAN | 0 (0.0%) | 0 (0.0%) | 42561 | DD or prepayment payment |
| INV_DD_CADENCE | FLAGGED | 0 (0.0%) | 1 (0.0%) | 35805 | account-month with a DD payment |
| INV_DD_STEP_CHANGE | FLAGGED | 0 (0.0%) | 575 (1.6%) | 34970 | successive pair of positive DD collections |
| INV_PPM_NOT_CREDIT_BILLED | BREACHED | 12 (0.2%) | 0 (0.0%) | 6670 | period on a prepayment account |
| INV_FUEL_IDENTIFIER | CLEAN | 0 (0.0%) | 0 (0.0%) | 54111 | bill period |
| INV_GAS_SINGLE_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 619 | gas meter (account x meter_serial) |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | CLEAN | 0 (0.0%) | 0 (0.0%) | 27997 | electricity period on profile class 1 or 2 |
| INV_CROSS_FUEL_PRICE_SCALE | CLEAN | 0 (0.0%) | 0 (0.0%) | 9994 | SVT term x cap window it overlaps (both fuels) |
| INV_EV_ADOPTION_ELECTRICITY_ONLY | UNCHECKABLE | | | | UNCHECKABLE ON THE RAW EXPORT, and it must stay so (2026-10-30): the company holds no asset-change record. An EV, heat pump or PV install is |
| INV_PERIODS_CONTIGUOUS | CLEAN | 0 (0.0%) | 0 (0.0%) | 106840 | bill period (day count) and successive pair (contiguity) |
| INV_BACK_BILLING_12M | FLAGGED | 0 (0.0%) | 146 (0.4%) | 39159 | bill period of a domestic account from 2018-05-01 |
| INV_PERIOD_CONSUMPTION_NON_NEGATIVE | CLEAN | 0 (0.0%) | 0 (0.0%) | 57586 | register-period |
| INV_READ_MONOTONIC | CLEAN | 0 (0.0%) | 0 (0.0%) | 15986 | successive pair of actual reads on one register |
| INV_PERIOD_MATCHES_READS | CLEAN | 0 (0.0%) | 0 (0.0%) | 54111 | period billed on reads |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | CLEAN | 0 (0.0%) | 0 (0.0%) | 55906 | successive pair of periods on one meter register |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | CLEAN | 0 (0.0%) | 0 (0.0%) | 113 | change of printed register set between contiguous periods on one serial |
| INV_VAT_RATE | CLEAN | 0 (0.0%) | 0 (0.0%) | 54111 | period |
| INV_NON_COMMODITY_WITHIN_ALL_IN | CLEAN | 0 (0.0%) | 0 (0.0%) | 54111 | period |
| INV_REGISTER_ID_ONE_LABEL | CLEAN | 0 (0.0%) | 0 (0.0%) | 57586 | register id on one period, and each relabel between periods on one serial |
| INV_SERIAL_REGISTER_COUNT_STABLE | FLAGGED | 0 (0.0%) | 1 (0.0%) | 106840 | period, and each successive pair of periods on one serial |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | CLEAN | 0 (0.0%) | 0 (0.0%) | 32683 | domestic account on an SVT term on the 1st of a month (unit rate; standing charge) |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | CLEAN | 0 (0.0%) | 0 (0.0%) | 2343 | account-month on supply, Oct 2022 to Mar 2023 |
| INV_RENEWAL_NOTICE_42_TO_49_DAYS | CLEAN | 0 (0.0%) | 0 (0.0%) | 1320 | domestic fixed term owed a statement |
| INV_OVERDUE_WITHIN_BALANCE | CLEAN | 0 (0.0%) | 0 (0.0%) | 931 | collections journey opening |
| INV_ESTIMATE_RUN_WITHIN_TENURE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1 | estimate run printed on the page, against its leg's bills by the moment's date |
| INV_COLLECTIONS_EVENTS_ORDERED | CLEAN | 0 (0.0%) | 0 (0.0%) | 931 | collections journey |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | UNREACHED | 0 | 0 | 0 | statute-barred write-off |
| INV_MPAN_CORE_FORMAT | CLEAN | 0 (0.0%) | 0 (0.0%) | 763 | electricity supply point (account, MPAN core) |
| INV_EBSS_CREDIT_ON_THE_BILL | CLEAN | 0 (0.0%) | 0 (0.0%) | 2343 | bill covering a qualifying 1st, Oct 2022 to Mar 2023 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | CLEAN | 0 (0.0%) | 0 (0.0%) | 5517 | household collections step printing an overdue figure |
| INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT | UNREACHED | 0 | 0 | 0 | arrears notice line a fuel page prints |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1382 | account (page revenue against page bills before VAT) |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1198 | account (printed payment counter against collections due) |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | CLEAN | 0 (0.0%) | 0 (0.0%) | 8878 | account-year on both panels |
| INV_SMART_METER_BILLED_ON_ITS_OWN_READS | FLAGGED | 0 (0.0%) | 27 (135.0%) | 20 | fuel-year of Smart bills |
| INV_DUAL_FUEL_TRADITIONAL_READS_TAKEN_TOGETHER | CLEAN | 0 (0.0%) | 0 (0.0%) | 1 | book of traditional dual-fuel bill periods |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | FLAGGED | 0 (0.0%) | 249 (0.8%) | 30637 | estimated bill on a rung its declared policy grades |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | BREACHED | 3 (0.1%) | 28 (0.7%) | 4245 | run of estimated bills bounded by actual reads |
| INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1382 | supply points printing a meter type |
| INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE | UNCHECKABLE | | | | UNCHECKABLE BY THE RUNNER, by design rather than for want of a field: the committed panel is computed in the page's own JavaScript (stagePri |
| INV_METER_SERIAL_ONE_SUPPLY_POINT | CLEAN | 0 (0.0%) | 0 (0.0%) | 54111 | bill period (commodity, meter_serial, supply point) |
| INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF | CLEAN | 0 (0.0%) | 0 (0.0%) | 24175 | gas read/bill record (one period's register advance) |
| INV_TWO_RATE_BILL_PRINTS_ONE_READ_PAIR_PER_REGISTER | UNCHECKABLE | | | | NOT YET GRADED (2026-11-03): no evaluator in tools/domain_invariant_runner. Written blind, from docs/market_research and site/data/knowledge |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | BREACHED | 4 (3.0%) | 3 (2.2%) | 135 | gas leg with a measured month a year after another |
| INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD | BREACHED | 1 (100.0%) | 11 (1100.0%) | 1 | electricity book (measured month-pairs) |
| INV_BACK_BILLING_ON_RECEIPT_FROM_ISSUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 527 | undercharge catch-up on a credit bill paid on receipt, issued with 21BA in force |
| INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL | CLEAN | 0 (0.0%) | 0 (0.0%) | 1133 | re-offer of the repayment plan (a further bill missed) |
| INV_CAST_TARIFF_LABEL_IS_THE_BILLED_TERM | FLAGGED | 0 (0.0%) | 20 (52.6%) | 38 | Explore cast moment x fuel leg it prints a tariff for |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP_ALL_IN_FLOOR | CLEAN | 0 (0.0%) | 0 (0.0%) | 1385 | SVT term x pre-cap half-year it overlaps (gas) |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP_ALL_IN_FLOOR | CLEAN | 0 (0.0%) | 0 (0.0%) | 2191 | SVT term x pre-cap half-year it overlaps (single-register electricity) |
| INV_DEFAULT_DUAL_FUEL_COST_FOLLOWS_THE_PUBLISHED_DEFAULT_BILL | CLEAN | 0 (0.0%) | 0 (0.0%) | 3 | year on year, DD default dual fuel at 3100/12000 kWh (months priced: 2016 9, 2017 12, 2018 12, 2019 12, 2020 12, 2021 12, 2022 12, 2023 12, 2024 12, 2025 6) |
| INV_DEFAULT_TARIFF_TWO_REGISTER_INVOICE_WITHIN_MULTI_REGISTER_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 850 | printed Day/Night bill on a default term (not graded: 476 not a default term, 283 pre-cap, 84 spans a term change) |
| INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE | CLEAN | 0 (0.0%) | 0 (0.0%) | 850 | printed Day/Night bill (g 843, no note, within 850) |
| INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE | FLAGGED | 0 (0.0%) | 1 (100.0%) | 1 | book: its successful DD collections, graded on Leg A |
| INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM | FLAGGED | 0 (0.0%) | 1040 (2.2%) | 47341 | printed bill with a tariff label |
| INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED | FLAGGED | 0 (0.0%) | 13 (59.1%) | 22 | Explore cast moment printing a household payment tally |
| INV_DD_COLLECTION_IS_DATED_ON_A_BACS_PROCESSING_DAY | CLEAN | 0 (0.0%) | 0 (0.0%) | 35950 | direct debit collection |
| INV_DD_DUE_ON_A_NON_PROCESSING_DAY_IS_COLLECTED_ON_THE_NEXT_PROCESSING_DAY | UNCHECKABLE | | | | GAP (1): the "next working day" rule is quoted from Bacs bank-holiday guidance (via CIPP) and Pay.UK for bank holidays, and from a vendor (G |
| INV_DD_COLLECTIONS_PILE_ONTO_MONDAYS_AS_THE_WEEKEND_ROLL_PREDICTS | UNCHECKABLE | | | | GAP: no source publishes the distribution of GB energy customers' chosen collection days, or the weekday distribution of energy DD collectio |
| INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START | FLAGGED | 0 (0.0%) | 188 (19.2%) | 980 | account paying by direct debit from its first payment |
| INV_OPENING_DAY_CREDIT_IS_ONLY_WHAT_WAS_COLLECTED_ON_OR_AFTER_SUPPLY_START | UNCHECKABLE | | | | GAP (1): only Octopus was found publishing a collection ON the supply start date. Suppliers that collect after it would show £0 on the welco |
| INV_GAS_AGAINST_WEATHER_IS_COMPUTED_OVER_FULL_SUPPLIED_YEARS_ONLY | UNCHECKABLE | | | | GAP (1): CalTRACK's 365-day/37-missing-day rule is for a savings baseline, not a year-on-year weather correlation. It is borrowed as the nea |
| INV_GAS_WEATHER_R_IS_PRINTED_ONLY_WITH_THE_BOUND_ITS_YEARS_EARN | UNCHECKABLE | | | | GAP (1): no knowledge page read here gives the published year-to-year spread of GB annual HDD 2016-2025, or the published distribution of a  |
| INV_WINTER_SUMMER_RATIO_NEEDS_A_FULL_WINTER_AND_A_FULL_SUMMER | UNCHECKABLE | | | | GAP: CalTRACK's 90% is a savings-baseline coverage rule, borrowed as the nearest published sufficiency rule. No source sets one for a househ |
| INV_ELECTRIC_HEATING_VERDICT_AGREES_WITH_THE_HOMES_GAS_SUPPLY | UNCHECKABLE | | | | GAP (1): SERL's 1.36-1.47 is the MEDIAN gas-heated home's monthly max/min, not a per-household band, and not the Dec-Feb/Jun-Aug ratio the p |
| INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO | FLAGGED | 0 (0.0%) | 26 (1.7%) | 1575 | closed account (one fuel leg) and each write-off on one |
| INV_REFUND_WITHIN_THE_PAGE_CREDIT | CLEAN | 0 (0.0%) | 0 (0.0%) | 188 | refund line on one fuel leg's page ledger |
| INV_FIXED_TERM_RATES_HOLD_FOR_THE_TERM | UNCHECKABLE | | | | GAP (1): the knowledge layer holds no licence text that forbids a supplier varying the price of a domestic Fixed Term Supply Contract during |
| INV_HOUSEHOLD_PAGE_LEDGER_SUMMARY_RECONCILES_TO_ITS_BALANCE | UNCHECKABLE | | | | GAP (1): the knowledge layer does not hold the SLC 31A / 31H text on what a statement of account must itemise (31A is read only through Ofge |
| INV_HOUSEHOLD_PAGE_PAID_STAGE_COVERS_EVERY_FUEL_ACCOUNT | UNCHECKABLE | | | | GAP (1): no licence text read requires a combined two-fuel balance on a household statement. The knowledge page marks the one-statement prac |
| INV_HOUSEHOLD_PAGE_NARRATED_FACT_IS_TRUE_OF_THE_ACCOUNT | UNCHECKABLE | | | | GAP (1): the 0.25 share (and the 0.5 breach line) is a stated belief chosen by the row, not a published threshold. No source in the knowledg |
| INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT | BREACHED | 7 (4.5%) | 0 (0.0%) | 156 | refund line on a fuel leg whose household prints another fuel leg |
