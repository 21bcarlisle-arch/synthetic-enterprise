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
