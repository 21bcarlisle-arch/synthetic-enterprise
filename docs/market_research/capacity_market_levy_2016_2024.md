# UK Capacity Market (CM) Levy — £/MWh by Year (2016–2024)

For simulation calibration (Phase 30a). Source: Ofgem Annex 9 v1.8 (November 2025),
sheet "1b Historical level tables", CM row. Units: £/customer/year at benchmark
3.1 MWh consumption — converted to £/MWh by dividing by 3.1.

## CM Levy Rates (£/MWh)

| Year (Apr–Mar OY) | £/cust/yr (Annex 9) | £/MWh | Source quality | Notes |
|---|---|---|---|---|
| 2016/17 | ~£1.5 est. | **~£0.5** | Low — pre-Annex 9 | TA auctions only; T-4 delivery had not yet started; Annex 9 coverage begins Apr 2017 |
| 2017/18 | £3.41 | **£1.10** | High — Annex 9 direct | First year in Annex 9; TA (£27.50/kW) + Early Auction (£6.95/kW, ~1 GW) only |
| 2018/19 | £11.36 | **£3.67** | High — Annex 9 direct | First full T-4 delivery year; T-4 at £19.40/kW (~49 GW); T-1 at £6.00/kW |
| 2019/20 | £14.85 | **£4.79** | High — Annex 9 direct | T-4 at £18.00/kW; T-1 at £0.77/kW (very cheap) |
| 2020/21 | £18.18 | **£5.86** | High — Annex 9 direct | T-4 at £22.50/kW; T-1 at £1.00/kW |
| 2021/22 | £14.49 | **£4.67** | High — Annex 9 direct | Cheapest year (~£649m total); T-4 at £8.40/kW (2017 auction excess capacity) |
| 2022/23 | £10.44 | **£3.37** | High — Annex 9 direct | T-4 suspended; T-3 at £6.44/kW (~36 GW); T-1 cleared at £75/kW cap but small volume |
| 2023/24 | £17.61 | **£5.68** | High — Annex 9 direct | T-4 at £15.97/kW + T-1 at £60/kW; higher T-1 uplift drives cost |
| 2024/25 | £22.54 (H1 only) | **£7.27** | Medium — H1 only | T-4 at £18.00/kW + T-1 at £35.79/kW; Oct 2024+ not yet in Annex 9 H1 figures |

## Key Findings

**Applies to all demand segments:** The CM levy is recovered from all electricity demand 
customers — domestic (resi), SME, and I&C — proportional to consumption. No domestic 
exemption unlike CCL. I&C at average load factors pays effectively the same £/MWh as 
domestic (±10-15% variation for demand-flexibility-managed loads).

**Highly variable year-to-year:** Range £0.5–7.3/MWh over 2016–2024. Driven by:
- Which auction year's capacity delivers in the current year (T-4 = 4 years prior)
- T-1 auction clearing prices (1 year prior, higher price, smaller volume)
- Total GB demand (denominator for cost recovery)

**Year-lag effect:** The 2021/22 cheapness (£4.67/MWh) reflects the 2017 T-4 auction 
at only £8.40/kW — capacity was plentiful post-Paris Agreement buildout. The expensive 
2023/24 year (£5.68/MWh) reflects the 2020 T-4 at £15.97/kW and 2023 T-1 at £60/kW.

**2022/23 apparent dip despite T-1 £75/kW:** T-4 was suspended for 2022 delivery, 
replaced by a T-3 at £6.44/kW but for only ~36 GW (less than usual). The T-1 volume 
was small (~5.8 GW). Total CM cost ~£1.5–1.8bn was less than 2023/24.

**Previous simulation estimate:** `historical_policy_costs_2016_2024.md` used "~£2-6/MWh
(highly variable)". Annex 9 confirms range £1.1–5.9/MWh for 2017-2024, mode ~£3.5-5/MWh.
The early years (2016/17: £0.5, 2017/18: £1.10) are well below the old estimate range.

## Simulation Implementation (Phase 30a)

CM levy uses the same Apr-Mar obligation year convention as RO:
- `_CM_LEVY_BY_YEAR` keyed by obligation year start (Apr-Mar calendar year of April start)
- `get_cm_levy_per_mwh(date_str)` uses `_ro_oy_start_year()` for the correct year mapping
- Applied to all segments (resi, SME, I&C) — no domestic exemption
- Included in `policy_cost_gbp` in settlement records alongside RO, CfD, CCL
- Passed through in tariff unit rate at renewals (same as RO/CfD)
