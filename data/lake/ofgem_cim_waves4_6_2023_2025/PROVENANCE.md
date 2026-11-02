# Ofgem, Consumer Impacts of Market Conditions survey, Waves 4-6: A15 and switching-intent extract

**The raw workbooks are NOT stored here.** They are 25-28 MB each; the extract below is what any page reads. Re-fetch
to check: the URLs and SHA-256 of the files as retrieved on 2026-11-02 by the delivery seat.

| Wave | Fieldwork | Source | SHA-256 |
|---|---|---|---|
| 4 | July 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-11/CIM_Wave_4_FINAL_Data_Tables_Accessible_v2_0.xlsx | `08a24d8fa20bc88577446069c75bd2308050a718ec27fe41801d1752ab05944a` |
| 5 | Jan-Feb 2024 | https://www.ofgem.gov.uk/sites/default/files/2024-09/CIM_Wave_5_Data_Tables.xlsx | `c78b36d07923082970a52ef0a775f06bc82a69d960a5eaa98f2768287bbd3645` |
| 6 | Jan-Feb 2025 | https://www.ofgem.gov.uk/sites/default/files/2025-07/Consumer%20impacts%20of%20market%20conditions%20survey%20wave%206%20data%20tables.xlsx | `26112f87b048471b18f5434bb8b2e874ab10a0154cec5151d555a611cda01b3e` |

Wave 3 is in `../ofgem_cim_wave3_2022/`. No Wave 7 had been published on Ofgem's research pages when searched (2 Nov 2026).
Licence: Ofgem publications, Open Government Licence v3.0.

- `a15_and_switching_intent_across_waves_3_to_6.csv`: for question A15 (all DD, standard-credit and prepayment payers;
  Tables 13, 19, 16 and 17 in Waves 3-6) nine reason rows, and for D3_3 ("will switch to a new supplier in the next three
  months", Tables 110, 102, 82, 78) the "Summary: Will" row, each at the Total and at eight crossbreak columns: age 16-24
  and 65-74; income under £16k and £80k+; bill difficulty none and behind; trust to treat fairly, trust and not.
  Weighted column %, unweighted and effective base as printed.
- **The crossbreaks are not the same question across waves.** Wave 3's "Keeping up with bills" has three classes
  (no difficulties, struggling, behind). Waves 4-6 split "struggling" in two. Wave 5 labels the column "household
  bills"; Wave 6 labels it "other household bills (not energy)" and adds a separate energy-bills column that is not
  used here. Only "no difficulties" and "behind on bills" are read, and they are the same words in all four waves.
- **A15's answer list changed.** Wave 4 added six answer options (including "I actively chose to pay this way" and
  "because I've always paid this way") and a neutral net; Wave 6 added one more. Levels do not compare across Waves 3-4;
  contrasts within a wave do. The page says so.
- Read by: `docs/market_research/the_customer_needs_framework_cost_worry_switching_cim_waves_3_6_2026-11-02.md`.

- `cost_worry_wtp_and_revealed_switching_by_column.csv` (added 2026-11-02): weighted column % with unweighted and
  effective base, long format (wave, table, row, crossbreak group, column). Wave 3 C4 (Table 87, from the stored
  Wave 3 workbook); Wave 4 Tables 94 (C4), 155-156 (D8_5/6), 164 (E3, direct debit), 175-177 (E4_3/4/6); Wave 5
  Tables 70 (C4), 139-140 (D8_5/6), 148 (E3, direct debit); Wave 6 Tables 56 (C4), 102 (E3, direct debit). Columns
  kept: total, age bands, income <16k and 80k+, bill difficulty (every "keeping up with" group), trust to treat fairly,
  payment method, affordability experience. The three raw workbooks were re-fetched on 2026-11-02 and their SHA-256
  matched the table above. Wave 5 has two bill-difficulty groups (household and energy bills), Wave 6 two (other
  household bills, not energy; and energy bills). Read by:
  `docs/market_research/revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md`.

- `e20a_actions_to_reduce_cost_waves_3_to_6.csv` (added 2026-11-02): question E20a, "Which of the following actions, if
  any, have you taken in order to reduce the costs of your energy bills" (Wave 3 Table 163, from the stored Wave 3
  workbook; Wave 4 Table 178; Wave 5 Table 156; Wave 6 Table 108). Waves 4-6 add "in the past 3 months". Every answer
  row and Ofgem's "Net: Taken any action", at the Total and every column of the crossbreak groups Age_2, Income v2,
  Keeping up with (every variant), Home ownership, Individual Payment Method and Trust to treat fairly. Long format:
  weighted column % (proportion x 100), unweighted base and effective base, as printed. Nothing is reweighted. The Wave
  4-6 workbooks were re-fetched on 2026-11-02 and their SHA-256 matched the table above. Read with openpyxl: each
  answer row's weighted count is followed by its column-proportion row. Read by:
  `docs/market_research/price_sensitivity_is_two_traits_cutting_use_and_shopping_cim_waves_3_6_2026-11-02.md`.
