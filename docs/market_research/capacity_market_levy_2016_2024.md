# UK Capacity Market (CM) Levy — £/MWh by Year (2016–2025)

For simulation calibration (Phase 30a). Source: Ofgem Annex 9 **v1.11**, sheet
"1b Historical level tables", CM row of the Typical-consumption table (Electricity,
Single-Rate Metering Arrangement). Fetched 2026-09-07 from
<https://www.ofgem.gov.uk/sites/default/files/2026-08/Annex-9-Levelisation-allowance-methodology-and-levelised-cap-levels-v1.11.xlsx>.

**THE LAW NOW LIVES IN THE COMMONS, NOT HERE.**
`docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json` is the single
home both lanes read, and it carries Annex 9's cap-period rows verbatim.
`tests/architecture/test_cm_levy_commons.py` re-derives every figure below from them. This
note is the write-up; it is no longer the source of record, and it must not be edited to
disagree with the artefact.

## HOW THE CONVERSION ACTUALLY WORKS — corrected 2026-09-07

This note previously said Annex 9 publishes "£/customer/year ... divided by 3.1". **Annex 9
does not publish a per-year figure at all.** It publishes an *annualised* level in force
during each **cap period** — six-month periods to Sep 2022, quarterly after. An obligation
year is the **duration-weighted mean** of the cap periods overlapping Apr–Mar, and the
£/MWh is that *unrounded* mean ÷ 3.1.

Two things follow, and both were live defects:

* **The weighting is not a plain average.** 2022/23 spans one six-month period (£9.217) and
  two quarterly ones (£11.671 each). Weighted 6/3/3 → £10.444 → **£3.37**. A plain mean of
  the three → £10.853 → £3.50. The published figure is £3.37.
* **The division is on the unrounded mean.** 2018/19's mean is £11.364754, and
  11.364754/3.1 = 3.6661 → **£3.67**. Running it against the *rounded* £11.36 in the table
  below gives 3.66, which is how a BLOCKING finding came to be filed on 2026-09-07 against a
  row that was correct all along. The £/cust/yr column here is a **rounded display**; the
  6dp values are in the artefact.

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
| 2024/25 | £21.67 | **£6.99** | High — Annex 9 direct, full year | **CORRECTED 2026-09-07 from £22.54 / £7.27**, which was Apr–Sep 2024 only. v1.11 publishes all four quarters and H2 (£20.798) is well below H1 (£23.470, £21.614), so the half-year reading **overstated the year by 4.0%** |
| 2025/26 | £26.80 | **£8.64** | High — Annex 9 direct, full year | **NEW 2026-09-07.** v1.8 did not carry this year and the artefact recorded it as not established; v1.11 publishes Apr 2025 – Mar 2026 in full |

## Key Findings

**Applies to all demand segments:** The CM levy is recovered from all electricity demand 
customers — domestic (resi), SME, and I&C — proportional to consumption. No domestic 
exemption unlike CCL. I&C at average load factors pays effectively the same £/MWh as 
domestic (±10-15% variation for demand-flexibility-managed loads).

**Highly variable year-to-year:** Range £0.5–8.6/MWh over 2016–2025. Driven by:
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
(highly variable)". Annex 9 confirms range £1.1–8.6/MWh for 2017-2025, mode ~£3.5-5/MWh.
The early years (2016/17: £0.5, 2017/18: £1.10) are well below the old estimate range, and
the last two (2024/25: £6.99, 2025/26: £8.64) are above it — the series is still climbing,
so an upper bound taken from this note will date.

**2026/27 is NOT established.** v1.11 publishes Apr–Jun, Jul–Sep and Oct–Dec 2026 (9 of 12
months); Jan–Mar 2027 is not yet set, so the year cannot be duration-weighted. Those three
cap periods are carried in the artefact and deliberately produce no levy row — a 9-month
mean would be a real-looking number for a year nobody has published, which is precisely the
shape of the 2024/25 defect above.

## Simulation Implementation (Phase 30a)

CM levy uses the same Apr-Mar obligation year convention as RO:
- `_CM_LEVY_BY_YEAR` keyed by obligation year start (Apr-Mar calendar year of April start)
- `get_cm_levy_per_mwh(date_str)` uses `_ro_oy_start_year()` for the correct year mapping
- Applied to all segments (resi, SME, I&C) — no domestic exemption
- Included in `policy_cost_gbp` in settlement records alongside RO, CfD, CCL
- Passed through in tariff unit rate at renewals (same as RO/CfD)
