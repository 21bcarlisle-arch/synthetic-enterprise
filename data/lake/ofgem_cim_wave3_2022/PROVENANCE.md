# Ofgem, Consumer Impacts of Market Conditions survey, Wave 3 (fieldwork 21 Nov - 11 Dec 2022): data tables

- **Source:** https://www.ofgem.gov.uk/sites/default/files/2023-05/CIM%20Wave%203%20Data%20Tables.xlsx, linked from
  https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-3-novdec-2022
- **Retrieved:** 2026-11-02, by the delivery seat. SHA-256 of the raw file:
  `7e97f463d23388c1f79e958051fa267be511b8f032074860e567bd398804c8f4`
- **Publisher, vintage:** Ofgem; survey run by BMG; tables published May 2023. GB adults responsible for energy bills.
- **Licence:** Ofgem publications are under the Open Government Licence v3.0 unless stated otherwise.
- **What is here:** `CIM_Wave_3_Data_Tables.xlsx`, raw and unmodified; and
  `a15_why_this_payment_method_by_column.csv`, Table 13 (question A15, "Why do you use the payment method you use?",
  base: all who pay by direct debit, prepayment or standard credit) in tidy form. That is one row per reason per
  crossbreak column, holding the weighted column %, the column's unweighted base and its effective sample size, all
  as the workbook prints them. "Positive reasons" and "Negative reasons" are Ofgem's own nets.
- **How the CSV was made:** the workbook was read with the Python standard library (zipfile + XML; no third-party
  reader is installed here). For Table 13, each reason row's weighted count is followed by a row of column
  proportions. The CSV takes those proportions x 100, with the "Unweighted Total" and "Effective Sample Size for
  Statistic Base" rows of the same table. Cells printed `-` (an empty column) are omitted. Nothing is reweighted
  or recomputed.
- **Read by:** `docs/market_research/why_households_pay_the_way_they_do_cim_wave3_2026-11-02.md`.
