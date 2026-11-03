# Domain invariants at git=0a6391d186

**0 unexcepted breach(es) across 0 invariant(s); 6 excepted. ENFORCED: nothing unexcepted, so the publish stands.**
- INV_UNIT_RATE_EPG_HOUSEHOLD 350: excepted until the printed energy line priced on the printed kWh (the same volume the Treasury's share is computed on), graded 0 on a fresh run
- INV_PPM_NOT_CREDIT_BILLED 12: excepted until a statement document type for the SME prepayment leg, or the invariant scoped to domestic accounts
- INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 6: excepted until the raw export carrying each account's void and occupier window, and the row exempting a month the payer did not hold on its 1st
- INV_EBSS_CREDIT_ON_THE_BILL 6: excepted until the raw export carrying each account's void and occupier window, as for INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23
- INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL 6: excepted until the carbon panel counting energy used as the row says (true-up kWh in the months they reconcile; knowledge page first)
- INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER 3: excepted until the three storage homes' bills printing the two-rate settlement they hold, under ruling step 3 (a; their heating type was read 2026-10-30). (b) and (c) are the row's lawful tail and stay excepted

Domain invariants over 1293 accounts

| invariant | status | breached | flagged | checked | unit |
|---|---|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | CLEAN | 0 (0.0%) | 0 (0.0%) | 5522 | SVT term x cap window it overlaps (single-register electricity) |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 2348 | SVT term x pre-cap half-year it overlaps (single-register electricity) |
| INV_UNIT_RATE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 4740 | SVT term x cap window it overlaps (gas) |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 1785 | SVT term x pre-cap half-year it overlaps (gas) |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 387 | SVT term x cap window it overlaps (multi-register electricity) |
| INV_UNIT_RATE_FIXED | FLAGGED | 0 (0.0%) | 8 (0.6%) | 1337 | fixed term, graded once at the window it was struck in |
| INV_UNIT_RATE_EPG_HOUSEHOLD | BREACHED | 350 (11.1%) | 0 (0.0%) | 3163 | domestic SVT bill period inside an EPG window (household all-in rate, ex-VAT) |
| INV_STANDING_CHARGE_SVT_ELEC | CLEAN | 0 (0.0%) | 0 (0.0%) | 21263 | SVT bill period (electricity) |
| INV_STANDING_CHARGE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 16577 | SVT bill period (gas; ceiling in DD-only windows) |
| INV_STANDING_CHARGE_FIXED | CLEAN | 0 (0.0%) | 0 (0.0%) | 16085 | fixed bill period |
| INV_ANNUAL_USE_ELEC_ACCOUNT | FLAGGED | 0 (0.0%) | 8 (0.5%) | 1752 | complete calendar account-year (electricity) |
| INV_ANNUAL_USE_GAS_ACCOUNT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1423 | complete calendar account-year (gas) |
| INV_ANNUAL_USE_BOOK_MEDIAN | CLEAN | 0 (0.0%) | 0 (0.0%) | 12 | TDCV row x fuel class (book median) |
| INV_READ_DUTY_ANNUAL | FLAGGED | 0 (0.0%) | 311 (27.5%) | 1130 | credit account (prepayment excluded): longest run without an actual read |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | FLAGGED | 0 (0.0%) | 1 (100.0%) | 1 | book (electricity kWh) |
| INV_BILL_AT_LEAST_TWICE_YEARLY | CLEAN | 0 (0.0%) | 0 (0.0%) | 46456 | bill period of a domestic credit account |
| INV_OPENING_READ | FLAGGED | 0 (0.0%) | 1293 (100.0%) | 1293 | account: days from first period_start to its typed opening read |
| INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1293 | account |
| INV_PAYMENT_AMOUNT_SIGN | CLEAN | 0 (0.0%) | 0 (0.0%) | 41768 | DD or prepayment payment |
| INV_DD_CADENCE | FLAGGED | 0 (0.0%) | 1 (0.0%) | 35081 | account-month with a DD payment |
| INV_DD_STEP_CHANGE | FLAGGED | 0 (0.0%) | 1400 (4.0%) | 34615 | successive pair of positive DD collections |
| INV_PPM_NOT_CREDIT_BILLED | BREACHED | 12 (0.2%) | 0 (0.0%) | 6263 | period on a prepayment account |
| INV_FUEL_IDENTIFIER | CLEAN | 0 (0.0%) | 0 (0.0%) | 52828 | bill period |
| INV_GAS_SINGLE_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 586 | gas meter (account x meter_serial) |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | CLEAN | 0 (0.0%) | 0 (0.0%) | 27558 | electricity period on profile class 1 or 2 |
| INV_CROSS_FUEL_PRICE_SCALE | CLEAN | 0 (0.0%) | 0 (0.0%) | 9870 | SVT term x cap window it overlaps (both fuels) |
| INV_EV_ADOPTION_ELECTRICITY_ONLY | UNCHECKABLE | | | | UNCHECKABLE ON THE RAW EXPORT, and it must stay so (2026-10-30): the company holds no asset-change record. An EV, heat pump or PV install is |
| INV_PERIODS_CONTIGUOUS | CLEAN | 0 (0.0%) | 0 (0.0%) | 104372 | bill period (day count) and successive pair (contiguity) |
| INV_BACK_BILLING_12M | FLAGGED | 0 (0.0%) | 144 (0.4%) | 37579 | bill period of a domestic account from 2018-05-01 |
| INV_PERIOD_CONSUMPTION_NON_NEGATIVE | CLEAN | 0 (0.0%) | 0 (0.0%) | 55998 | register-period |
| INV_READ_MONOTONIC | CLEAN | 0 (0.0%) | 0 (0.0%) | 15168 | successive pair of actual reads on one register |
| INV_PERIOD_MATCHES_READS | CLEAN | 0 (0.0%) | 0 (0.0%) | 52828 | period billed on reads |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | CLEAN | 0 (0.0%) | 0 (0.0%) | 54459 | successive pair of periods on one meter register |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | CLEAN | 0 (0.0%) | 0 (0.0%) | 94 | change of printed register set between contiguous periods on one serial |
| INV_VAT_RATE | CLEAN | 0 (0.0%) | 0 (0.0%) | 52828 | period |
| INV_NON_COMMODITY_WITHIN_ALL_IN | CLEAN | 0 (0.0%) | 0 (0.0%) | 52828 | period |
| INV_REGISTER_ID_ONE_LABEL | CLEAN | 0 (0.0%) | 0 (0.0%) | 55998 | register id on one period, and each relabel between periods on one serial |
| INV_SERIAL_REGISTER_COUNT_STABLE | FLAGGED | 0 (0.0%) | 2 (0.0%) | 104363 | period, and each successive pair of periods on one serial |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | CLEAN | 0 (0.0%) | 0 (0.0%) | 33495 | domestic account on an SVT term on the 1st of a month (unit rate; standing charge) |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | BREACHED | 6 (0.3%) | 0 (0.0%) | 2273 | account-month on supply, Oct 2022 to Mar 2023 |
| INV_RENEWAL_NOTICE_42_TO_49_DAYS | CLEAN | 0 (0.0%) | 0 (0.0%) | 1171 | domestic fixed term owed a statement |
| INV_OVERDUE_WITHIN_BALANCE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1076 | collections journey opening |
| INV_ESTIMATE_RUN_WITHIN_TENURE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1 | estimate run printed on the page, against its leg's bills by the moment's date |
| INV_COLLECTIONS_EVENTS_ORDERED | CLEAN | 0 (0.0%) | 0 (0.0%) | 1076 | collections journey |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | UNREACHED | 0 | 0 | 0 | statute-barred write-off |
| INV_MPAN_CORE_FORMAT | CLEAN | 0 (0.0%) | 0 (0.0%) | 707 | electricity supply point (account, MPAN core) |
| INV_EBSS_CREDIT_ON_THE_BILL | BREACHED | 6 (0.3%) | 0 (0.0%) | 2273 | bill covering a qualifying 1st, Oct 2022 to Mar 2023 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | CLEAN | 0 (0.0%) | 0 (0.0%) | 17149 | household collections step printing an overdue figure |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | CLEAN | 0 (0.0%) | 0 (0.0%) | 1293 | account (page revenue against page bills before VAT) |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | NOT_IN_EXPORT | | | | needs `payment_record`, which no period of this export carries |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | BREACHED | 6 (0.1%) | 0 (0.0%) | 8657 | account-year on both panels |
| INV_SMART_METER_BILLED_ON_ITS_OWN_READS | FLAGGED | 0 (0.0%) | 21 (105.0%) | 20 | fuel-year of Smart bills |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | FLAGGED | 0 (0.0%) | 136 (0.4%) | 30708 | estimated bill on a rung its declared policy grades |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | BREACHED | 3 (0.1%) | 14 (0.3%) | 4309 | run of estimated bills bounded by actual reads |
| INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1293 | supply points printing a meter type |
| INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE | UNCHECKABLE | | | | UNCHECKABLE BY THE RUNNER, by design rather than for want of a field: the committed panel is computed in the page's own JavaScript (stagePri |
| INV_METER_SERIAL_ONE_SUPPLY_POINT | CLEAN | 0 (0.0%) | 0 (0.0%) | 52828 | bill period (commodity, meter_serial, supply point) |
| INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF | CLEAN | 0 (0.0%) | 0 (0.0%) | 23745 | gas read/bill record (one period's register advance) |
| INV_TWO_RATE_BILL_PRINTS_ONE_READ_PAIR_PER_REGISTER | UNCHECKABLE | | | | NOT YET GRADED (2026-11-03): no evaluator in tools/domain_invariant_runner. Written blind, from docs/market_research and site/data/knowledge |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | UNCHECKABLE | | | | NOT YET GRADED (2026-11-03): no evaluator in tools/domain_invariant_runner. Written blind, from docs/market_research and site/data/knowledge |
