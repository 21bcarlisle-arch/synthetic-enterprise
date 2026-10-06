# How a supplier shapes an estimate for an unread month — method and the published monthly shape

**Knowledge:** metering-and-reads

*Discovery pass, 2026-10-06. How a GB supplier turns an annual estimate (EAC/AQ) into an amount
for one unread month, and the published monthly shape each fuel uses. Builds on
`what_a_supplier_holds_to_size_a_direct_debit.md` (annual-figure precedence, TDCV) and
`how_far_a_settled_eac_sits_from_next_years_use.md` (how far that annual figure drifts). This page
is the within-year shape; those two are the annual level and its error.*

---

## 1. Electricity NHH: EAC from a meter advance, by profile class

An EAC/AA converts a meter advance into an annual figure by dividing by the **sum of the Profile
Class 1 (domestic unrestricted) coefficients over the read period**, then re-weights it across the
year by the same coefficients — the Elexon/BSC method (BSCP504, "EAC/AA calculation"). **BSCP504
was not read in this session**; named, not cited. The mechanism is confirmed instead by DESNZ:

> "The AA is an estimate of annualised consumption based on consumption recorded between two meter
> readings at least 6 months apart … an EAC is used where two such meter readings are not available
> … using historical information and the profile information relating to the meter."
> — DESNZ, *Subnational methodology and guidance booklet* (2026), §3.1.3

**Exact Elexon PC1 monthly/HH coefficients were not obtainable here.** Elexon's site search and
document portal returned no usable public numeric table within this session's reach; the live
figures sit in Elexon's BMRS/SVAA systems. **Named gap**, not a number guessed to fill it.

## 2. Best published GB domestic electricity monthly shape (not PC1-exact)

**DESNZ Energy Trends Table 5.5**, "Domestic sales" column — actual metered GB domestic
electricity sold monthly. Computed from the published spreadsheet (retrieved 2026-10-06,
`gov.uk/government/statistics/electricity-section-5-energy-trends`), 3-year average 2023–2025:

| month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| share | 10.81% | 8.87% | 9.12% | 8.14% | 7.25% | 6.73% | 6.78% | 6.96% | 7.30% | 8.18% | 9.65% | 10.22% |

**Confidence: H for the figures** (primary spreadsheet, three independent years, sums to 100%) —
**M as a PC1 proxy**. It blends Profile Class 1 and Class 2 (Economy 7) households and is actual
2023–2025 weather, not a seasonal-normal construction. PC1-only would likely peak sharper in
winter and sit flatter in summer than this blend, because PC2 households shift load to off-peak
hours rather than concentrating it seasonally the same way — expectation only, not a sourced
number.

## 3. Gas NDM: AQ, EUC, ALP/DAF, "seasonal normal" — confirmed by Xoserve directly

> "Annual Quantity (AQ) — An estimate of the amount of gas (in kWh) that a supply meter point will
> use in the coming year **under 'seasonal normal' weather conditions**."
> — Xoserve, *An Introduction to Demand Estimation and DESC* (updated Oct 2023)

> "Non-daily metered sites (Classes 3 and 4): AQ is based on the consumption between two meter
> readings [9–36 months apart]. **The calculation is adjusted for the impact of the actual weather
> experienced in that period.** It's then converted to a 12-month estimate."
> — Xoserve, *Annual Quantity (AQ)* help page, retrieved 2026-10-06

So the AQ is weather-corrected **at calculation time** (actual weather in the read window stripped
out) and then expressed on a **seasonal-normal basis** going forward — not re-based to the actual
weather of the billing year until the next AQ recalculation.

The monthly shape spreading that AQ across a year is the **Annual Load Profile (ALP)**, governed by
DESC and keyed to **End User Category (EUC)**: domestic NDM sites sit in the 0–293 MWh/yr band,
which splits by domestic/non-domestic and prepayment/non-prepayment (EUC01B = domestic
non-prepayment). The **Daily Adjustment Factor (DAF)** reacts to actual day-to-day weather for
system balancing/allocation, not for re-stating a bill estimate. Source: Xoserve *Demand
Estimation* help page and the DESC introduction slides (both retrieved 2026-10-06).

**The exact EUC01B ALP table was not obtainable here.** Xoserve states the "Derived Factors (EUCs,
ALPs, DAFs and PLFs) for the current gas year" live in **"the UK Link secure area," UNC-party
access only** — a structural gap stated by the source itself, not a search failure.

## 4. Best published GB domestic gas monthly shape (not EUC01B-exact)

**DESNZ Energy Trends Table 4.2**, "Domestic" demand column — published monthly only from **2023
onward** (earlier years marked `[x]`, not available at this granularity). Computed from the
spreadsheet (retrieved 2026-10-06, `gov.uk/government/statistics/gas-section-4-energy-trends`),
3-year average, the only three complete years available:

| month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| share | 17.05% | 13.42% | 12.30% | 7.87% | 4.10% | 2.61% | 2.33% | 2.29% | 3.43% | 7.13% | 12.24% | 15.22% |

**Confidence: H for the figures** (primary source, direct computation, three years) — **M as an
EUC01B proxy**. DESNZ's "Domestic" sector is broader than one EUC band (not filtered to
non-prepayment; DESNZ's sectoral split need not match Xoserve's EUC boundaries exactly), and —
unlike the ALP — this is **actual realised weather for 2023–2025**, not seasonal-normal. A true
seasonal-normal ALP would be smoother year-on-year than this average already shows (e.g. January
2025 ran markedly colder than January 2023–2024, visible in the per-year shares behind this table).

## 5. Do bill estimates use these industry profiles, and against what weather basis

**Established:**
- Gas AQ is explicitly built and expressed **on a seasonal-normal weather basis** (§3) — not actual
  weather for the billing year in progress.
- The registry annual figure (EAC electricity, AQ gas) ranks second, behind the supplier's own
  metered history, under SLC 27.15 — per `what_a_supplier_holds_to_size_a_direct_debit.md` §2,
  reused here, unchanged.
- Ofgem's TDCV is the explicit published fallback "in the absence of individual consumers' data"
  (Ofgem, 2023 TDCV decision §1.1, already cited in the companion document) — an annual figure, no
  published monthly breakdown found in either pass.

**Not established, named as a gap rather than assumed:**
- No supplier or Ofgem statement was retrieved confirming whether an individual domestic bill
  *estimate* is weather-corrected at issue, or is a flat annual-figure/12 split. Supplier sites
  (Centrica/British Gas and others) were not reachable through this session's JS-free fetch
  tooling; no quote is repeated here without being re-verified.
- Whether a supplier's billing engine re-derives a monthly split from the ALP/PC1 shape, or simply
  divides EAC/AQ by 12 (the director's practitioner statement already on record for the DD path),
  is **not established for the bill path** — only for direct-debit sizing.

## 6. What a supplier can and cannot know

**Can know:** the registry EAC/AQ and its vintage; its own prior meter-read history for the
account; the published *industry-average* monthly shape for the meter class (PC1/PC2 electricity,
EUC gas); the Ofgem TDCV fallback; whether the AQ in force was struck on a seasonal-normal or
actual-weather basis (§3).

**Cannot know, from the published record:** the household's own weather response, as distinct from
the EUC-average DAF; the exact Elexon PC1 or Xoserve EUC01B ALP tables (gated to settlement-system
participants); and, per §5, whether a given supplier's bill-estimate arithmetic applies any
seasonal shape at all, as opposed to a flat /12.

## Sources

- DESNZ, *Energy Trends Table 4.2*: https://www.gov.uk/government/statistics/gas-section-4-energy-trends (retrieved 2026-10-06, "Domestic" column, 2023–2025)
- DESNZ, *Energy Trends Table 5.5*: https://www.gov.uk/government/statistics/electricity-section-5-energy-trends (retrieved 2026-10-06, "Domestic sales" column, 2023–2025)
- Xoserve, *Annual Quantity (AQ)*: https://www.xoserve.com/help-centre/supply-points-metering/annual-quantity-aq/, retrieved 2026-10-06
- Xoserve, *Demand Estimation*: https://www.xoserve.com/help-centre/demand-attribution/demand-estimation/, retrieved 2026-10-06
- Xoserve/Joint Office of Gas Transporters, *An Introduction to Demand Estimation and DESC* (Oct 2023): https://www.gasgovernance.co.uk/sites/default/files/related-files/2025-07/DESC%20An%20Introduction.pdf
- DESNZ, *Subnational methodology and guidance booklet* (2026), §3.1.3 — already cited in `how_far_a_settled_eac_sits_from_next_years_use.md`
- Ofgem, *Decision on revised Typical Domestic Consumption Values*, 25 May 2023, §1.1 — already cited in `what_a_supplier_holds_to_size_a_direct_debit.md`
- Not read, named for the next reader: BSCP504 (EAC/AA calculation); Elexon's live BMRS/SVAA profile coefficient data; the EUC01B Annual Load Profile table (UK Link secure area, UNC-party access only).
