# EU-ETS / UK-ETS market carbon price — closing the W1_6b NAMED GAP (2026-08-03)

**Serves**: `sim/merit_order_reconstruction.py`'s `ets_price_gbp_per_tonne` parameter, previously
DEFAULTING TO 0.0 because "no citable published series was found"
(`docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md` §4b, Assumption 3).
This document sources a real, citable, primary-published series and closes that gap for the
2016-2020 calm window (with 2021-2025 also sourced as a bonus, not required by this atom).

**Epistemic scope**: discovery-only, external published `gov.uk`/`assets.publishing.service.gov.uk`
sources. No `sim/`, `company/`, or simulation output read or used to shape any figure below (R13).
No fabricated constants — every numeric claim below is directly quoted from a fetched primary
document, cross-checked against independent general knowledge of EUA spot-price history where
possible (noted per row), not inferred or interpolated from nothing.

**Retrieved**: 2026-08-03. Network available this session (`gov.uk`, `assets.publishing.service.gov.uk`
both HTTP 200, confirmed at task start).

---

## 0. Why the 2026-07-25 pass missed this source

The prior DISCOVER pass (§4b of the 2026-07-25 doc) checked HMRC's "Determinations of the EU ETS
carbon price" / "Determinations of the UK ETS carbon price" pages and dismissed them as
"civil-penalty default-price determinations, not a published historical average-price series."
**That characterisation is only half right.** The determinations ARE legally used to set civil
penalties (for installations that fail to surrender enough allowances) — but the VALUE itself is
not an arbitrary default: it is computed by a stated, auditable formula directly from real traded
EUA/UKA futures (or, for the first UK ETS year, real auction clearing prices), over a stated
historical reference window, converted at the real Bank-of-England average FX rate for that window.
Reading the actual PDF text (not just the page summary) shows the methodology and the two raw
inputs (€ futures price, £/€ FX rate) for every year — this is a genuine, resolvable, primary
market-price series, just published under a "civil penalty" heading rather than a "market data"
heading. Re-reading the primary document, not just its title, closed this gap.

---

## 1. The regulatory mechanism (why this is a real market price, not a default)

**Regulation 49 of the Greenhouse Gas Emissions Trading Scheme Regulations 2012** (2016-2020
scheme years, EU ETS era) requires the Secretary of State to publish, one month before each scheme
year begins, a "carbon price" computed as:

- **Futures Price**: the average end-of-day December-[scheme-year] EU Allowance (EUA) futures
  price, traded over the ~12-month window from **12 November of (scheme-year − 2)** to
  **11 November of (scheme-year − 1)**.
- **Exchange Rate**: the average Bank-of-England Euro-Sterling exchange rate over the same window.
- **Carbon price (£) = Futures Price (€) × Exchange Rate (£/€)**.

From 2021 (post-Brexit, UK ETS launch), **Article 46 of the Greenhouse Gas Emission Trading
Scheme Order 2020** takes over with an analogous mechanism: the 2021 scheme year uses the
**actual UK ETS auction-clearing-price-weighted average** (the scheme had just launched, so no
prior futures history existed); 2022 onward reverts to the same December-futures-average
methodology, now on UKA (UK Allowance) futures rather than EUA.

**Key caveat, stated explicitly (not smoothed over)**: because the reference window ends
~13-14 months before the scheme year it is nominally "for," each figure is best read as a
**lagged proxy for market conditions roughly one calendar year before its label**, not a same-year
realised spot average. E.g. the "2020 carbon price" (£21.93) reflects EUA futures trading between
Nov 2018 and Nov 2019 — i.e. it is closer to a measure of real 2019 market conditions than 2020's.
**This document does NOT re-label the years** — it uses the government's own "scheme year X"
label as the calendar-year key (matching what the SRMC engine needs: `ets_price_gbp_per_tonne`
indexed by the same `year` the reconstruction is already keyed on), and flags the lag as a stated
simplification. A cross-check below shows this labelling is directionally sound anyway (§4).

---

## 2. The sourced series (H confidence — every figure quoted verbatim from the primary PDF)

| Scheme year | Futures price | FX rate (£/€) | **ETS carbon price (£/tCO2)** | Reference window | Methodology |
|---|---|---|---|---|---|
| 2016 | €7.63 | 1.36 | **£5.61** | 12 Nov 2014 – 11 Nov 2015 | Dec-2016 EUA futures average |
| 2017 | €5.85 | 1.25 | **£4.67** | 12 Nov 2015 – 11 Nov 2016 | Dec-2017 EUA futures average |
| 2018 | €5.57 | 1.15 | **£4.86** | 12 Nov 2016 – 11 Nov 2017 | Dec-2018 EUA futures average |
| 2019 | €14.27 | 1.13 | **£12.61** | 12 Nov 2017 – 11 Nov 2018 | Dec-2019 EUA futures average |
| 2020 | €24.85 | 1.13 | **£21.93** | 12 Nov 2018 – 11 Nov 2019 | Dec-2020 EUA futures average |
| 2021 | — | — | **£47.96** | 1 Jan 2021 – 11 Nov 2021 | actual UK ETS auction-clearing-price-weighted average (scheme launch year, no prior futures history) |
| 2022 | — | — | **£52.56** | 1 Jan 2021 – 11 Nov 2021 | Dec-2022 UKA futures average (same window as 2021 — first full futures cycle) |
| 2023 | — | — | **£83.03** | 12-month period ending 11 Nov 2022 | Dec-2023 UKA futures average |
| 2024 | — | — | **£64.90** | 12-month period ending 11 Nov 2023 | Dec-2024 UKA futures average |
| 2025 | — | — | **£41.84** | 12-month period ending 11 Nov 2024 | Dec-2025 UKA futures average |

**Sources (each a distinct fetched primary PDF, DESNZ/BEIS/DECC, `gov.uk`-hosted)**:
- 2016: "Determination by the Secretary of State for Energy and Climate Change of the 2016 carbon
  price," `https://assets.publishing.service.gov.uk/media/5a816e0be5274a2e87dbd95d/Determination_by_the_Secretary_of_State_for_Energy_and_Climate_Change_of_the_2016_carbon_price.pdf`,
  signed 30 Nov 2015.
- 2017: "Carbon Penalty Price Determination for 2017,"
  `https://assets.publishing.service.gov.uk/media/5a82b8c2ed915d74e62374c6/Carbon_Penalty_Price_Determination_for_2017.pdf`,
  signed 28 Nov 2016.
- 2018: "Carbon Penalty Price Determination 2018,"
  `https://assets.publishing.service.gov.uk/media/65ae50fc0ff90c000d955f3d/carbon-penalty-price-determination-2018.pdf`,
  signed 30 Nov 2017.
- 2019: "Carbon Penalty Price Determination for 2019,"
  `https://assets.publishing.service.gov.uk/media/5c010891e5274a0fd8ee89bb/Carbon_Penalty_Price_Determination_for_2019.pdf`
  (also mirrored at `.../attachment_data/file/760600/...`), signed 30 Nov 2018.
- 2020: "EU ETS carbon penalty price determination 2020,"
  `https://assets.publishing.service.gov.uk/media/6479e55fb32b9e000ca960cc/eu-ets-carbon-penalty-price-determination-2020.pdf`,
  signed 29 Nov 2019.
- 2021/2022: "UK ETS: Carbon prices for use in civil penalties, 2021 and 2022," collection page
  `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2021-and-2022`.
- 2023: `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2023`.
- 2024: "UK ETS: Carbon prices for use in civil penalties, 2024" (via
  `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price`).
- 2025: `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2025`.
- Collection pages: `https://www.gov.uk/government/publications/determinations-of-the-eu-ets-carbon-price`
  (2014-2020) and `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price`
  (2021-2026).

**Confidence: H for 2016-2020** — each figure independently read from the raw PDF text (not a
web-search summary; two of the six PDF fetches were re-verified by reading the raw document a
second way after the summarising tool initially returned a plausible-looking but WRONG figure for
the 2020 document — see §3 methodology note). **Confidence: M for 2021-2025** — sourced from a
rendered HTML gov.uk page (methodology text quoted directly) rather than the underlying PDF; not
independently re-verified against the raw PDF this session, and not required for this atom's
2016-2020 calm-cell scope (carried as a bonus / next-pass item).

---

## 3. Methodology note — a caught tool error, corrected before use

**This matters for R9 (evidence before narrative) and general data-integrity discipline.** The
first WebFetch of the 2020 determination PDF returned a summarised answer claiming "£16.30,
€20.87, October 2018" — internally inconsistent (that "2019"-labelled content contradicted the
already-fetched, independently-sourced 2019 determination of £12.61/€14.27, and the URL was
explicitly the 2020 document). This was caught by cross-checking the summary against the
already-fetched adjacent-year data, not trusted at face value. The PDF was then read directly
(bypassing the summarising step) and the correct primary content extracted: **£21.93, €24.85, FX
1.13, window 12 Nov 2018 – 11 Nov 2019, signed 29 Nov 2019** — this is the figure used in §2.
**No other figure in this document was accepted from a single-pass web-summary tool without this
kind of cross-check**; the 2016-2020 figures were all read from the primary PDF text directly.

---

## 4. Cross-check against known EUA spot-price history (sanity check, not a separate source)

The lagged-window methodology (§1) means each "scheme year X" figure is closer to a measure of
real EUA market conditions in calendar year (X−1). Checking against well-known EUA spot-price
history (EUA traded roughly flat ~€5-8/tonne 2013-2017, then rose through 2018 to a ~€20-25 range
by 2019-2020) — the sourced figures track this shape almost exactly one year "early" relative to
their label: the 2017 determination (€5.85, window mostly-2016) and 2018 determination (€5.57,
window mostly-2017) sit right in the well-known 2016-2017 EUA trough; the 2019 determination
(€14.27, window mostly-2018) sits below the commonly-cited full-2018 average (~€15-16) because the
window includes the still-low Nov-Dec 2017 prices, exactly as expected from a straddling window;
the 2020 determination (€24.85, window mostly-2019) matches the commonly-cited 2019 EUA average
almost exactly. **This is offered as a plausibility cross-check on the sourced figures, not as an
independent data source** — no separate EUA time series was fetched to perform this check; it
draws on general knowledge of the well-documented 2016-2020 EUA price trajectory. It supports
confidence that the six primary-document reads above were transcribed correctly, and that using
the government's own year-label (rather than re-assigning to a shifted calendar year) is a
defensible, if approximate, choice for this atom's purposes.

---

## What this unblocks

`sim/merit_order_reconstruction.py`'s `ets_price_gbp_per_tonne` NAMED GAP (previously hard-defaulted
to 0.0 for every year, meaning the reconstruction's only live carbon term was the flat £18/tCO2
Carbon Price Support) can now default to this real, year-varying, primary-sourced series for
2016-2024 (2025 not needed — the calm-window measurement only reaches 2020), while still accepting
an explicit override for testing. **What this document does NOT do**: it does not re-run or tune
the reconstruction (that is BUILD's job, done in `sim/merit_order_reconstruction.py` and measured
in `simulation/run_merit_order_reconstructibility.py`, per R12 — the measurement is a diagnostic,
reported honestly whatever it shows, never tuned toward a target). Coal variable O&M and the
%-of-hours-gas-is-marginal NAMED GAPS from the 2026-07-25 pass remain open; not addressed here.
