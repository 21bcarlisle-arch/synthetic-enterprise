# UK Electricity Price Distribution at High Renewables Penetration: 2027+ Scenarios

**Research date:** June 2026  
**Scope:** Quantitative parameters for simulation of UK energy market dynamics under 50–70%+ renewable penetration  
**Status:** Research complete; confidence ratings are H (high), M (medium), L (low)

---

## 1. Price Distribution Shape at 40–70% Renewable Penetration

### Observed Bimodal Signature (2025 data)

The clearest empirical evidence for a bimodal price distribution comes from Ember Energy's 2025 analysis of Great Britain's wholesale market. In 2025, the market exhibited a pronounced two-population structure:

- **Low-gas-fraction hours** (gas < 20% of generation mix): mean price ~**£60/MWh** [confidence: H, source: Ember Energy 2026]
- **High-gas-fraction hours** (gas > 50% of mix): mean price ~**£130/MWh** [H, Ember 2026]

This ~£70/MWh gap between the two modal regions is the empirical signature of an emergent bimodal distribution. By 2025, gas was generating either >50% or <20% of the grid approximately **50% of the time**, with a 30–50% "middle band" occurring only 30% of the time — a striking compression of the previously dominant centre of the distribution.

### Mode Locations and Split Estimates

Based on synthesising the Ember data with academic analysis (arXiv 2501.10423, Cambridge EPRG WP2503):

| Renewable Penetration | Approx. Lower Mode | Approx. Upper Mode | Estimated Hour Split (low:high) | Confidence |
|---|---|---|---|---|
| ~40% (2023 baseline) | £70–90/MWh | £120–150/MWh | 35:65 | M |
| ~44% (2024) | £60–80/MWh | £110–140/MWh | 40:60 | M |
| ~47% (2025) | £55–70/MWh | £120–135/MWh | 45:55 | M |
| ~60% (projected 2027–28) | £20–50/MWh (with deepening negative tail) | £100–130/MWh | 55:45 | L |
| ~70%+ (projected 2029–30) | £0–40/MWh (large negative tail) | £90–130/MWh | 60:40 | L |

**Caveats on distribution shape:** The lower mode is not stable — it has a growing left tail of deeply negative prices (see Section 2). A proper simulation should model the lower population as a truncated Gaussian centred around £30–50/MWh in 2027, with a left tail extending to -£50 to -£100/MWh, rather than a clean two-point bimodal. The upper mode is anchored to gas marginal cost and remains relatively stable in £/MWh terms but accounts for a shrinking fraction of hours.

### Merit-Order Effect Magnitude

From arXiv 2501.10423 (causal inference on UK APX data 2018–2024):

- **Wind:** Each additional 1 GWh of wind reduces the price by **up to £7/MWh** at low penetration; effect diminishes non-linearly at mid-penetration then re-intensifies. Quantile regression shows the 10th–90th percentile range **narrows** as wind increases — lower peak prices, but also fewer high-price spikes.
- **Solar:** Up to **£9/MWh per 1 GWh** at very low penetration; diminishes rapidly. An unexpected "bump" in observational data at 4–7% solar penetration is an artefact corrected away in causal analysis.
- Wind's price-suppression effect has become **significantly more pronounced** over 2021–2024 as its market share grew. [H]

---

## 2. Negative Price Frequency: Historical and Projected

### Historical Annual Negative Hours (N2EX Day-Ahead)

| Year | Negative-Price Hours | Notes |
|---|---|---|
| 2021 | ~7 | Pre-solar surge baseline |
| 2022 | 19–29 | Sources vary; Aurora/Modo figures differ |
| 2023 | 107–176 | Wide range across sources; Modo: 107h, ESS-News/Squeaky: 176h |
| 2024 | 139–179 | Drax: 155h; Modo: 149h; ScienceDirect review: 179h |
| 2025 | Record expected | Analysts forecast 2025 to exceed 2024; 17 consecutive hours on 25 May 2025 |

**Source divergence note:** The 2023 discrepancy (107h vs 176h) likely reflects different market instruments — Modo tracks the N2EX day-ahead half-hourly data, while some sources use the system sell price (SSP). For simulation, use ~150h for 2023 and ~165h for 2024 as central estimates. [M]

**Key 2026 data point:** In April 2026, **16.9% of midday half-hours** cleared at negative day-ahead prices, up from 11.3% in summer 2025 and 7.7% in summer 2024 — confirming accelerating trend. [H, source: El-Balad/market analysis, 2026]

### Projected Negative Hours 2027–2030

- **Modo Energy projection (Sep 2024):** ~**1,000 hours of negative pricing by 2027**, based on extrapolating solar/wind buildout trajectory. [M — directionally credible but the magnitude is sensitive to battery storage deployment rate]
- **NESO FES 2025 clean power 2030 scenario:** Offshore wind grows from ~15 GW to 43–50 GW by 2030; onshore wind doubles to 27 GW; solar triples to ~47 GW. This capacity expansion, absent grid investment, directly drives curtailment and negative prices.
- **Negative frequency will likely peak and then decline** post-~2027 as: (a) unsubsidised CfDs reduce must-run incentives, (b) large-scale battery storage absorbs surplus. Modo's analysis explicitly notes a probable decline after 2027.

**Simulation parameter (2027 central case):** 600–1,000 negative-price hours per year. Use a log-normal distribution for depth, anchored to observed range below.

### Price Depth During Negative Events

- Deepest observed N2EX hourly price: **-£54.17/MWh on 16 July 2023** [H]
- Second deepest observed: **-£35.18/MWh on 25 May 2025** [H]
- Typical negative event: -£5 to -£25/MWh range
- The Balancing Mechanism (BM) can in theory produce deeper negative prices; no formal floor is published by NESO. Observed BM clearing prices below -£100/MWh exist in ancillary data but are rare and transient.

---

## 3. Dunkelflaute: Frequency, Duration, and Gas Price Correlation

### Definition Used

Dunkelflaute = period when combined wind + solar output falls below approximately 5–10% of installed capacity, typically identified by a 48-hour running mean capacity factor below 0.06 (Kittel & Schill, arXiv 2410.00244).

### Frequency and Duration

| Metric | Value | Confidence | Source |
|---|---|---|---|
| Events per year (UK, >1 day) | 2–10 | M | Sunsave/SferribyUK; arXiv 2410.00244 |
| Typical duration per event | 12–72 hours; occasionally multi-day | M | Multiple sources |
| Monthly hours of reduced output in peak winter months | 50–150 hours/month | L | Sunsave 2025 analysis |
| Seasonal concentration | Oct–Feb (41% of events last >3 days) | M | Wood Mackenzie 2024; arXiv 2410.00244 |
| Summer vulnerability for UK | Exists; UK uniquely exposed due to wind reliance | M | arXiv 2410.00244v3 |

**Key UK-specific finding (arXiv 2410.00244v3):** Unlike most European nations where dunkelflaute is a winter-only phenomenon, the UK's heavy reliance on wind means significant summer dunkelflaute risk exists. Wind droughts in summer can be "very severe events" for UK-type portfolios.

**Most extreme documented event:** The winter 1996/97 pan-European drought lasted 55 days under idealised interconnection assumptions. Individual severe events in recent historical data last up to 2–3 weeks.

**January 2025 UK event (IEA Electricity 2025 reference):** On 8 January 2025, a localised UK dunkelflaute lasting approximately 1 day — low wind at night combined with interconnector unavailability, plant outages, and high demand — triggered a NESO Electricity Margin Notice. Prices spiked sharply during this event.

### Gas Price Correlation

No published paper directly quantifies the dunkelflaute–gas price correlation coefficient for the UK in this research sweep. However, the mechanism is well-established:

- Gas sets the marginal price ~85% of hours in 2024 even at 44% renewable penetration [H, Ember 2025]
- During dunkelflaute, renewable penetration collapses to <10% of installed capacity; gas fill-rate rises to 60–80%+ of the mix
- Price data confirms: hours with gas > 50% of mix averaged £130/MWh in 2025, vs £60/MWh when gas < 20% [H, Ember 2026]
- **Implied correlation:** Dunkelflaute → gas fraction exceeds 50% → prices jump from ~£60 to ~£130/MWh range, i.e., a ~2× price multiple [M]
- Gas commodity price (NBP) provides a second-order amplification during dunkelflaute if cold snaps coincide with Europe-wide demand surges (cf. January 2026 UK cold snap, already documented)

**For simulation:** Model dunkelflaute hours as a price distribution draw from the upper mode (~£100–180/MWh), correlated with gas day-ahead price. A reasonable correlation structure is: P(electricity | dunkelflaute) = f(gas_price × 1.4) with ±30% noise. [L — parametric guidance only]

---

## 4. Curtailment Costs as Fraction of Wholesale Price

### UK Constraint Payments

| Year | Total Constraint/Balancing Cost | Wind Curtailment Fraction | Notes |
|---|---|---|---|
| 2020–21 | ~£600M (estimated) | — | Pre-surge baseline |
| 2024 (April 2024–Jan 2025) | £1.9 billion | ~24% to wind farms | NESO data; transmission constraints 71% of total |
| 2024/25 full year | ~£1.7 billion total | £380–395M wind switch-off | Redispatch + wind curtailment |
| 2025 calendar year | ~£1.46 billion wind-related | ~£380M wind off, ~£1.08B gas replacement | Wind switch-off fell but replacement gas cost rose |

**Curtailment as fraction of wholesale revenue:** 
- UK wholesale electricity turnover ~£15–25 billion/year (at ~£80–100/MWh average × 300 TWh demand)
- Constraint payments of £1.7–1.9 billion represent roughly **7–12% of total wholesale turnover** [M]
- NESO projects constraint costs could reach **£4–8 billion/year by 2030** depending on grid investment pace, which would represent 15–30% of wholesale turnover at current price levels [M, NESO Clean Power 2030 analysis]

### Germany Analogue

Germany at ~55–60% renewable penetration (2023–2024) provides the closest operational analogue:

- 2023: **€3.13 billion** total redispatch costs; **19 TWh curtailed** (~3.5% of annual generation); cost per MWh curtailed ≈ €165/MWh [H, Clean Energy Wire]
- 2024: **€2.776 billion** total; **€554M renewable curtailment compensation**; 3.5% of renewable generation curtailed [H]
- 2025 (first 3 quarters): **€2.2 billion** total grid management costs; curtailment compensation fell 22% to ~**€435M**

**Key ratio:** German curtailment compensation is running at ~15–20% of the total grid congestion management cost, with the remainder being redispatch of gas plants. The 3.5% curtailment fraction of total renewable generation is a useful benchmark — at equivalent UK renewable penetration, expect 3–5% of wind/solar generation to be curtailed. [M]

---

## 5. Key Academic and Regulatory Papers

| Reference | Key Quantitative Contribution | Access |
|---|---|---|
| Kittel & Schill (2024), arXiv 2410.00244 "Quantifying the Dunkelflaute" | European VRE drought characterisation; duration distributions; 35 weather years | Open access arXiv |
| arXiv 2501.10423, "Do we actually understand the impact of renewables on electricity prices?" (2025) | Causal merit-order effect for UK: £7/MWh per GWh wind, £9/MWh solar; quantile regression showing narrowing of price distribution with higher wind | Open access arXiv |
| arXiv 2411.17683, "Coping with the Dunkelflaute: Power system implications of VRE droughts in Europe" (2024) | Storage requirements during droughts; 351 TWh needed at European scale; event durations of multiple weeks possible | Open access arXiv |
| Cambridge EPRG WP2503 (March 2025) | UK 2030 VRE scenario implications; price formation at high penetration | Cambridge JBS (PDF) |
| MDPI Energies 14(20) 6508 (2021), "Brief Climatology of Dunkelflaute Events over North and Baltic Sea" | Seasonal and geographic dunkelflaute statistics using 72 years ERA5 data | MDPI open access |
| NESO Annual Balancing Costs Report June 2025 (document 362561) | UK constraint payments £1.7–1.9B/year; breakdown by mechanism | NESO portal PDF |
| NESO FES 2025 / Clean Power 2030 Annex 1 (document 346791) | Capacity buildout: offshore wind 43–50 GW, solar 47 GW by 2030; constraint cost range £1–8B | NESO portal |
| Ember Energy, "British power prices increasingly independent from gas" (2026) | £60 vs £130/MWh bimodal price gap; gas price-setting 85% of hours in 2024 | Ember website (open) |
| IEA Electricity 2025 report, Supply chapter | Jan 2025 UK dunkelflaute event; European dunkelflaute Nov–Dec 2024 context | IEA website |
| Baringa/DECC CfD Negative Pricing Report (2015) | CfD 6-hour rule genesis; early negative price projections | Gov.uk (PDF) |

---

## 6. UK Negative Price Floor

### Market Rules

There is **no published statutory negative price floor** for the UK N2EX day-ahead market equivalent to, say, Australia's -$1,000/MWh floor [H]. The N2EX is a bilateral exchange auction with no explicit minimum.

**Observed minimum:** -£54.17/MWh (July 2023 N2EX day-ahead) [H]

**CfD mechanism (price floor for subsidy purposes):**
- Under AR1–AR3 CfDs: payments suspended when day-ahead price is negative for **6 or more consecutive hours**; during <6-hour negative spells, CfD payment is capped at the strike price (i.e., effectively a zero floor for the top-up payment)
- Under AR4+ CfDs (from ~2022): the threshold reduces — **any single hour** with a negative reference price triggers payment suspension
- This creates a strong incentive for CfD-supported generators to curtail or store during negative price events [H]

**Can prices go below -£100/MWh?**
- Formally: yes, there is no market floor preventing it
- Practically: at approximately -£50 to -£100/MWh, most dispatchable generators and batteries find it economic to absorb the surplus, putting a soft floor on sustained negative depth
- BM (Balancing Mechanism) actions can temporarily clear more deeply negative than the day-ahead market, but are typically short-duration
- **For simulation:** Use -£75/MWh as a practical 5th-percentile floor for extreme negative events in 2027; events below -£50/MWh should have probability <0.5% of negative-price hours [L — parametric estimate based on observed range and market structure]

---

## Summary Parameter Table for Simulation

| Parameter | 2025 Observed | 2027 Central | 2027 Range | Confidence |
|---|---|---|---|---|
| Annual renewable penetration | ~47% | ~58–62% | 52–68% | M |
| Negative-price hours/year | ~165–200 | 500–1,000 | 300–1,200 | L |
| Deepest negative price (floor) | -£54/MWh | -£75/MWh | -£50 to -£120 | L |
| Lower mode centre (£/MWh) | ~£60 | ~£30–45 | £0–60 | M |
| Upper mode centre (£/MWh) | ~£130 | ~£110–130 | £90–160 | M |
| Hour split lower:upper mode | ~45:55 | ~55:45 | 50:60 low | L |
| Dunkelflaute events/year | 2–10 | 2–10 | unchanged | M |
| Dunkelflaute price premium | ~2× lower mode | ~2–3× lower mode | — | L |
| UK constraint costs (£B/year) | £1.7 | £2.5–4.0 | £1.5–8.0 | L |
| Curtailment as % of renewable gen | ~2–3% | ~4–6% | 3–8% | M |

---

## Research Gaps

1. **No UK-specific dunkelflaute frequency table** by year with duration histogram exists in open data — the arXiv 2410.00244 paper has this for Europe but behind a pay-per-read ERA5 analysis wall. A targeted run using Elexon half-hourly data could fill this.
2. **Bimodal distribution mode locations** are inferred from Ember's binned gas-fraction analysis, not a direct price histogram fit. A Gaussian mixture model on BMRS settlement period data would sharpen these parameters.
3. **Dunkelflaute–gas price correlation coefficient** is not directly published; existing papers focus on storage needs rather than real-time price dynamics.
4. **Post-2027 negative price decline** (from Modo's projection) is mentioned but not quantified; depends heavily on battery storage deployment timeline.
