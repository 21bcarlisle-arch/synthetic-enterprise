# Historical UK Electricity Policy and Network Costs 2016–2024

For simulation calibration (Phase 21a). Sources: REF.org.uk, Ofgem RO Guidance, EMR Settlement,
LCCC Data Portal, Ofgem Price Cap Annex 3.

## 1. Renewables Obligation — By Obligation Year (Apr–Mar)

| OY | Obligation (ROCs/MWh) | Buy-out price (£/ROC) | Effective cost floor (£/MWh) |
|----|----------------------|----------------------|------------------------------|
| 2016–17 | 0.348 | £44.77 | ~£15.6 |
| 2017–18 | 0.409 | £45.58 | ~£18.6 |
| 2018–19 | 0.468 | £47.22 | ~£22.1 |
| 2019–20 | 0.484 | £48.78 | ~£23.6 |
| 2020–21 | 0.471 | £50.05 | ~£23.6 |
| 2021–22 | 0.492 | £50.80 | ~£25.0 |
| 2022–23 | 0.491 | £52.88 | ~£26.0 |
| 2023–24 | 0.469 | £59.01 | ~£27.7 |
| 2024–25 | 0.491 | £64.73 | ~£31.8 |

**Note:** Suppliers sourcing ROCs from market pay 5–15% above buy-out (ROC market premium). Buy-out fund proceeds are redistributed to compliant suppliers, broadly offsetting the premium. For simulation: use effective cost floor column. Formula: obligation × buy-out = £/MWh.

**Data sources:** REF.org.uk obligation levels; Ofgem RO buy-out prices (annual publication).

## 2. CfD Supplier Obligation — Approximate Annual Average ILR (£/MWh)

| Calendar year | Avg. ILR (£/MWh) | Notes |
|---------------|-----------------|-------|
| 2016 | ~£0.0–0.3 | CfD fleet tiny; levy near zero |
| 2017 | ~£1.3 | Rose through year (~£1.0 Q1, ~£1.5 Q3–Q4) |
| 2018 | ~£3.2 | Q1 £2.86, Q2 £3.82, Q3–Q4 ~£2.5–3.5 |
| 2019 | ~£3.5–4.5 | Fleet growing; consistent positive levy |
| 2020 | ~£3.0–4.5 | COVID: BEIS froze adjustment Apr 2020; ~£4/MWh stable |
| 2021 | ~£1.5 | Q1–Q2 positive; ILR cut to £0/MWh from Oct 2021 |
| **2022** | **~−£3 to −£8** | **NEGATIVE — wholesale > all CfD strike prices; LCCC paid back to suppliers** |
| 2023 | ~£5–8 | £0 at start, rose to £8.12 from March 2023; Q2 £3.82 |
| 2024 | ~£10–12 | Feb 2024 in-period adj to £10.748/MWh; further rises through year |

**Critical note:** The 2022 negative CfD levy is economically significant — during the energy crisis, wholesale prices exceeded CfD strike prices, so low-carbon generators paid into the scheme and those receipts were redistributed to suppliers. This slightly offset the massive commodity cost increase in 2021-22.

**Data sources:** EMR Settlement Ltd quarterly ILR announcements; LCCC Data Portal; Solar Power Portal coverage of 2022 negative levy.

## 3. Network Charges — Indicative Domestic-Equivalent (£/MWh, electricity)

TNUoS set in £/kW demand (converted at 45% load factor ≈ 3,942 h/yr). DUoS varies by DNO and voltage. Post-TCR (April 2023) TNUoS residual → fixed £/MPAN standing charge for domestic (breaks direct £/MWh comparison).

| Year (Apr–Mar) | TNUoS est. (£/MWh) | DUoS est. (£/MWh) | Combined (£/MWh) |
|----------------|--------------------|--------------------|------------------|
| 2016–17 | ~£12–14 | ~£20–25 | ~£32–39 |
| 2017–18 | ~£12–14 | ~£20–25 | ~£32–39 |
| 2018–19 | ~£13–15 | ~£21–26 | ~£34–41 |
| 2019–20 | ~£13–15 | ~£22–27 | ~£35–42 |
| 2020–21 | ~£12–14 | ~£22–27 | ~£34–41 |
| 2021–22 | ~£12–14 | ~£23–28 | ~£35–42 |
| 2022–23 | ~£14–16 | ~£25–30 | ~£39–46 |
| 2023–24 | ~£14–16* | ~£26–31 | ~£40–47 |
| 2024–25 | ~£15–17* | ~£27–33 | ~£42–50 |

*Post-TCR TNUoS residual is a fixed standing charge; £/MWh equivalents are estimated at typical domestic consumption (~2,500 kWh/year).

**For precise post-Q1 2019 values:** Ofgem Price Cap Annex 3 (downloadable XLSX from ofgem.gov.uk/energy-price-cap) publishes actual p/kWh network allowances by quarter. Use that as the authoritative source for post-2019 calibration.

## 4. Combined Non-Wholesale Cost to Supplier (£/MWh, electricity)

| Year | RO cost | CfD levy | Network (mid) | **Subtotal** | + FiT (~£7) + CM (~£4) + BSUoS (~£10) | **All-in non-wholesale** |
|------|---------|----------|---------------|------------|--------------------------------------|------------------------|
| 2016 | ~£16 | ~£0 | ~£35 | **~£51** | +~£21 | **~£72** |
| 2017 | ~£19 | ~£1 | ~£36 | **~£56** | +~£21 | **~£77** |
| 2018 | ~£22 | ~£3 | ~£37 | **~£62** | +~£22 | **~£84** |
| 2019 | ~£24 | ~£4 | ~£38 | **~£66** | +~£22 | **~£88** |
| 2020 | ~£24 | ~£4 | ~£38 | **~£66** | +~£22 | **~£88** |
| 2021 | ~£25 | ~£1 | ~£38 | **~£64** | +~£22 | **~£86** |
| 2022 | ~£26 | −£5 | ~£43 | **~£64** | +~£25 | **~£89** |
| 2023 | ~£28 | ~£5 | ~£44 | **~£77** | +~£25 | **~£102** |
| 2024 | ~£32 | ~£11 | ~£46 | **~£89** | +~£26 | **~£115** |

**Additional charges excluded from subtotal:**
- **Feed-in Tariff (FiT):** ~£5–9/MWh (steadily declining as FiT fleet matures)
- **Capacity Market (CM):** ~£2–6/MWh (highly variable by auction year)
- **BSUoS (Balancing Services Use of System):** ~£5–15/MWh (very volatile; peaked in 2021-22)
- **Warm Home Discount pass-through:** ~£0.5–1/MWh
- **Energy Company Obligation (ECO):** embedded in opex allowance

**Elexon SSP is commodity-only.** Adding the "All-in non-wholesale" column to SSP gives the approximate full cost stack a real supplier faces on each MWh supplied.

## 5. Implication for Simulation (Phase 21a Design)

Our sim uses Elexon SSP as the cost signal. Real UK electricity supply cost = SSP + ~£72–115/MWh non-wholesale (varies by year, with the biggest driver being the RO growing from £16 to £32/MWh and CfD levy from £0 to £11/MWh over 2016–2024).

**Minimum Phase 21a scope (highest-value, clean to implement):**
- Add `ro_levy_gbp = consumption_kwh / 1000 × ro_cost_per_mwh(year)` to each electricity settlement record
- Add `cfd_levy_gbp = consumption_kwh / 1000 × cfd_rate_per_mwh(year)` (note: negative in 2022 → rebate)
- Use the year-indexed tables above as lookup

**Network charges (deferred to Phase 23a):** Adding network charges requires also adding them to the tariff (otherwise margin collapses). This is a larger refactor — both the cost and revenue sides need updating simultaneously. The Ofgem price cap Annex 3 is the authoritative source for post-2019 values.

**2022 CfD rebate note:** In 2022 our sim will show suppliers receiving a small CfD rebate (negative levy) — this is accurate and partially offsets the 2021-22 commodity crisis. It should reduce the simulated loss slightly.

## 6. Data Sources

| Source | What it covers | URL |
|--------|---------------|-----|
| REF.org.uk | RO obligation levels by year | ref.org.uk/energy-data/notes-on-the-renewable-obligation |
| Ofgem RO Guidance | Buy-out prices by obligation year | ofgem.gov.uk → RO Guidance for Suppliers PDF |
| EMR Settlement | Quarterly CfD ILR history | emrsettlement.co.uk/updates-lccc-interim-levy-rate |
| LCCC Data Portal | CfD levy datasets | lowcarboncontracts.uk/data-portal |
| Ofgem Price Cap Annex 3 | Network cost allowances by quarter (post-Q1 2019) | ofgem.gov.uk/energy-price-cap (download XLSX) |
