# GB Dispatchable Fleet & Renewables Penetration — Era Boundaries 2016-2025

**Task**: ground the *era boundaries* of the GB power system's dispatchable-fleet capacity and
renewables penetration across 2016-2025 from published sources only, to inform a future
recalibration of `DISPATCHABLE_CAPACITY_MW` in the SSP scarcity model
(`x = (demand_MW - renewables_MW) / DISPATCHABLE_CAPACITY_MW`), currently held constant at
35,000 MW across the whole window. **This document does NOT compute or look at the model's `x`
series or any simulation output** — boundaries below are drawn purely from real-world capacity
and generation-share turning points, per the task's explicit instruction not to reverse-engineer
from model residuals.

Retrieved 2026-07-24. All quantitative tables below are **observed-with-evidence**, pulled live
this session from DESNZ's DUKES (Digest of UK Energy Statistics) Chapter 5 spreadsheets. Narrative
policy/history claims not independently re-fetched this session are marked **inferred** (general
public record, not primary-sourced today) and confidence-tagged accordingly.

---

## Executive summary

1. **Coal generation share collapsed almost entirely in a single year (2015→2016: 22.4%→9.0%)**,
   driven by the April 2015 carbon price floor increase — well *before* the 2016-2025 window
   starts. Within the window itself coal share declined more gradually: 9.0% (2016) → 2.1% (2019)
   → 0.7% (2024) → 0% from 1 October 2024 (Ratcliffe-on-Soar, the UK's last coal power station,
   closed that date — observed-with-evidence, Wikipedia, cross-checked against DUKES capacity
   data showing coal capacity falling to ~18 MW residual by end-2024).
2. **"Total fossil fuels capacity" (DUKES definition: coal+oil+gas+mixed-fuel+other fossil,
   EXCLUDING nuclear and bioenergy) fell from 49,835 MW (2016) to 36,250 MW (2024)** — a 27%
   decline — in three visible steps, not a smooth line: ~50 GW plateau (2016-18) → sharp drop to
   ~42-44 GW plateau (2019-22) → renewed sharp drop to ~36-40 GW (2023-24).
3. **This fossil-only trajectory is a striking match for a constant-35,000-MW "dispatchable
   capacity" assumption at the END of the window (2024: 36,250 MW, only ~3.6% above 35,000) but
   NOT at the start (2016: 49,835 MW, ~42% above 35,000).** A constant calibrated near the
   late-window value would under-state the true denominator by roughly 40% in 2016-18 — which,
   holding demand and renewables fixed, mechanically inflates a residual-demand scarcity ratio in
   early years relative to late years. This is presented as a real-world MATCH pattern, not a
   model-fit exercise — see Confidence/Caveats for the boundary between grounding and inference.
4. **Renewables generation share rose from 24.5% (2016) to 50.4% (2024)**, crossing 40% in 2020
   (helped by the COVID demand contraction) and 50% for the first time in 2024, with the main
   step-changes tracking offshore wind commissioning waves.
5. **Candidate 3-era partition, grounded in the fossil-capacity plateaus above**: **Era A
   2016-2018** (coal-material, fossil ~50 GW), **Era B 2019-2022** (post-major-closure plateau,
   fossil ~42-44 GW), **Era C 2023-2025** (final coal exit, fossil ~36 GW and falling). A coarser
   2-era split at the 2018/2019 boundary is also defensible if only one break is wanted.

---

## 1. Coal capacity, generation share, and phase-out timeline

### 1a. Coal generation share of total GB generation, 2015-2024 (observed-with-evidence)

| Year | Coal generation (GWh) | Total generation (GWh) | Coal % of generation |
|---|---|---|---|
| 2015 | 75,878 | 338,875 | 22.4% |
| 2016 | 30,669 | 339,164 | 9.0% |
| 2017 | 22,530 | 338,198 | 6.7% |
| 2018 | 16,831 | 333,752 | 5.0% |
| 2019 | 6,917 | 327,175 | 2.1% |
| 2020 | 5,700 | 310,296 | 1.8% |
| 2021 | 6,785 | 307,881 | 2.2% |
| 2022 | 5,943 | 324,821 | 1.8% |
| 2023 | 3,775 | 294,079 | 1.3% |
| 2024 | 2,040 | 284,956 | 0.7% |

Source: DUKES Table 5.6.J "Annual summaries of electricity fuel use, generation and supply",
"All generating companies / Generation" rows, `DUKES_5.6.xlsx`, downloaded from
https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes
(file: https://assets.publishing.service.gov.uk/media/688a31dda11f859994409290/DUKES_5.6.xlsx),
retrieved 2026-07-24. **Confidence: H** (primary published statistical series, self-summed from
raw GWh figures in the fetched workbook).

### 1b. Coal capacity, 2016-2024 (observed-with-evidence)

| Year | Coal-fired capacity, all generating companies (MW) |
|---|---|
| 2016 | 13,699 |
| 2017 | 13,363 |
| 2018 | 12,337 |
| 2019 | 6,817 |
| 2020 | 5,361 |
| 2021 | 5,360 |
| 2022 | 5,340 |
| 2023 | 2,046 |
| 2024 | 18 |

Source: DUKES Table 5.7.A "Capacity by fuel", `DUKES_5.7.xlsx`, same publication, retrieved
2026-07-24. **Confidence: H.** The 2019 cliff (12,337→6,817 MW) and the 2023 cliff (5,340→2,046
MW) and the 2024 near-zero (18 MW, a residual/rounding artefact — the last unit closed
30 September 2024, so DUKES' annual snapshot captures ~9 months of a fully-closed fleet) are the
three biggest single-year moves in the whole 2016-2024 capacity series for any fuel.

### 1c. Phase-out policy and plant-closure anchors

- **30 September 2024 — Ratcliffe-on-Soar power station (Nottinghamshire, 2,116 MW, Uniper)
  closed, marking the end of coal-fired electricity generation in Great Britain** after 142 years
  of coal power (since Holborn Viaduct, 1882). Observed-with-evidence: Wikipedia
  (https://en.wikipedia.org/wiki/Ratcliffe-on-Soar_Power_Station, fetched 2026-07-24), directly
  corroborated by the DUKES 5.7 coal-capacity series collapsing to ~18 MW for calendar-year 2024
  (§1b). **Confidence: H** (specific date independently fetched this session and cross-checked
  against an independent, directly-fetched government statistical series).
- **April 2015 — UK carbon price floor increase** (part of a mechanism introduced 2013, raised
  to a binding top-up level in April 2015) is widely credited as the single largest driver of the
  one-year 22.4%→9.0% coal-generation-share collapse visible in the data (§1a) — this move
  predates the 2016-2025 window but explains why 2016 already opens with coal at a much-reduced
  9.0% share rather than a smoothly-declining series from a much higher 2016 starting point.
  **Confidence: M — inferred**, well-established public-policy record, not independently
  re-fetched from a primary DECC/HMT source this session.
- **November 2015 — then-Energy Secretary Amber Rudd announced government intent to close all
  unabated coal power stations by 2025**, subject to security-of-supply conditions being met by
  new gas/other capacity. **Confidence: M — inferred**, well-established, not re-fetched this
  session (a targeted search for the primary DECC/BEIS announcement and the subsequent 2021
  legislation bringing the date forward to 1 October 2024 did not surface a working link via
  gov.uk's current search index this session — treat the *date itself* (well-corroborated by the
  independently-fetched Wikipedia/DUKES cross-check in the point above) as solid, but the
  *policy-announcement provenance* as background context only).
- Individual mid-decade coal-station closures (e.g. Longannet, Scotland's last coal station,
  closed March 2016; Aberthaw B and Fiddler's Ferry, closed March 2020) are **not independently
  verified this session** and are omitted from the grounded evidence above — the aggregate DUKES
  capacity series (§1b) is the load-bearing evidence for the shape of the retirement curve, not
  any specific station-level date beyond Ratcliffe-on-Soar.

---

## 2. Dispatchable / firm capacity trajectory, 2016-2024

DUKES Table 5.7.A gives capacity by fuel per year. Two candidate "dispatchable capacity"
aggregates are constructed here, both **observed-with-evidence** (direct DUKES figures or simple
sums of DUKES rows, no external modelling):

- **(A) "Total fossil fuels capacity"** — DUKES' own published aggregate (note 11: coal + oil +
  gas + mixed/dual-fired + other fossil fuels). Excludes nuclear and bioenergy.
- **(B) "Thermal + nuclear"** — a broader sum built here from individual DUKES rows: coal + oil +
  gas + mixed + nuclear + bioenergy + other fossil. Includes baseload nuclear and biomass, which
  a scarcity/merit-order model may or may not want to treat as "dispatchable" (nuclear in
  particular runs largely price-inelastic baseload, not a flexible margin-setting resource).

| Year | (A) Total fossil fuels capacity (MW) | Nuclear capacity (MW) | Bioenergy capacity (MW) | (B) Thermal+nuclear sum (MW) |
|---|---|---|---|---|
| 2016 | 49,835 | 9,261 | 5,701 | 64,698 |
| 2017 | 51,021 | 9,261 | 6,058 | 66,340 |
| 2018 | 50,274 | 9,261 | 7,511 | 67,046 |
| 2019 | 43,938 | 9,261 | 7,851 | 61,051 |
| 2020 | 42,638 | 7,833 | 7,960 | 58,431 |
| 2021 | 42,650 | 7,833 | 8,149 | 58,632 |
| 2022 | 42,536 | 5,883 | 8,126 | 56,545 |
| 2023 | 39,814 | 5,883 | 8,184 | 53,882 |
| 2024 | 36,250 | 5,883 | 8,265 | 50,398 |

Source: DUKES Table 5.7.A, "All generating companies" rows for Coal fired / Oil fired / Gas
fired / Mixed or dual fuelled / Nuclear stations / Bioenergy and waste / Other fossil fuels /
"Total fossil fuels capacity [note 11]", `DUKES_5.7.xlsx`, retrieved 2026-07-24. **Confidence:
H** for column (A) (direct published aggregate) and the individual fuel columns; **H** for column
(B) as an arithmetic sum of the same directly-fetched rows (not itself a DUKES-published
aggregate, so labelled here as a derived/summed figure rather than a quoted one).

**2025 data**: DUKES' annual Chapter 5 release (accessed 2026-07-24) covers complete calendar
years only through 2024 — no full-year 2025 capacity figures exist in this publication yet.
Trend continuation into 2025 (fossil capacity likely continuing to fall modestly, absent any new
large CCGT commissioning) is **inferred only, not observed** — flagged, not stated as fact,
per the task's era-boundary grounding requirement.

### Is a constant 35,000 MW a defensible mid-window average?

- Against definition (A) ("Total fossil fuels capacity", the closest DUKES aggregate to a
  classic "dispatchable thermal fleet" concept excluding baseload nuclear): 35,000 MW is **~30%
  below** the 2016 figure (49,835 MW) and **~3.6% above** the 2024 figure (36,250 MW). It is a
  reasonable proxy for the LATEST year in the window, and a poor one for the earliest years — not
  merely "miscentred", materially wrong for roughly the first half of the decade.
- Against the broader definition (B) (thermal+nuclear): 35,000 MW is **~46% below** the 2016
  figure (64,698 MW) and **~30% below** even the 2024 figure (50,398 MW) — i.e. under this wider
  definition a constant 35,000 MW would be too low across the ENTIRE window, not just miscentred
  by era. Which of (A) or (B) is the closer real-world analogue to the model's intended
  `DISPATCHABLE_CAPACITY_MW` concept is a modelling judgement outside this document's scope (this
  agent does not read the simulation code) — both are reported so that judgement can be made with
  the real numbers in hand.
- **Observed-with-evidence, not inferred**: whichever definition is closer, the real-world
  dispatchable fleet was NOT flat across 2016-2025 — it moved in visible, dated steps (§4), and
  any single constant necessarily privileges one part of the decade over the rest.

---

## 3. Renewables capacity and generation-share trajectory, 2015-2024

### 3a. Generation share by source, all-generating-companies, 2015-2024 (observed-with-evidence)

| Year | Coal % | Gas % | Nuclear % | Renewables % (wind+solar+hydro-natural-flow+bioenergy) | Wind % | Solar % |
|---|---|---|---|---|---|---|
| 2015 | 22.4 | 29.5 | 20.8 | 24.6 | 11.9 | 2.2 |
| 2016 | 9.0 | 42.3 | 21.1 | 24.5 | 11.0 | 3.1 |
| 2017 | 6.7 | 40.4 | 20.8 | 29.2 | 14.7 | 3.4 |
| 2018 | 5.0 | 39.4 | 19.5 | 33.0 | 17.1 | 3.8 |
| 2019 | 2.1 | 40.7 | 17.2 | 36.6 | 19.5 | 3.8 |
| 2020 | 1.8 | 36.1 | 16.2 | 43.1 | 24.4 | 4.0 |
| 2021 | 2.2 | 39.9 | 15.0 | 39.8 | 21.1 | 3.9 |
| 2022 | 1.8 | 38.5 | 14.6 | 41.6 | 24.7 | 4.3 |
| 2023 | 1.3 | 34.6 | 13.8 | 46.5 | 27.9 | 5.0 |
| 2024 | 0.7 | 30.4 | 14.2 | 50.4 | 29.2 | 5.0 |

Source: computed directly from DUKES Table 5.6.J GWh figures (§1a source), retrieved 2026-07-24.
Renewables % follows DUKES' own definitional note (5.7 note 9): wind (onshore+offshore) + solar +
bioenergy (thermal renewable) + hydro (natural flow) — **excludes pumped hydro**, which DUKES
explicitly does not count as renewable since the pumping electricity can come from any source.
**Confidence: H.**

Notable step-changes: 2017→2018 (+3.8pp renewables share, offshore wind ramp + solar additions);
2019→2020 (+6.5pp, boosted partly by the COVID-19 demand contraction shrinking the denominator,
not solely by new build — total generation fell from 327.2 TWh to 310.3 TWh that year, a
mechanical share-inflation effect worth flagging as a confound, see Caveats); 2024 crossing the
50% threshold for the first time in the published series.

### 3b. Renewables installed capacity (de-rated per DUKES methodology), 2016-2024

| Year | Onshore wind (MW, de-rated 0.43) | Offshore wind (MW, de-rated 0.43) | Solar (MW, de-rated 0.17) | Total renewables capacity, DUKES-published (MW) |
|---|---|---|---|---|
| 2016 | 4,658 | 2,276 | 2,025 | 16,270 |
| 2017 | 5,417 | 3,005 | 2,169 | 18,274 |
| 2018 | 5,773 | 3,518 | 2,220 | 20,650 |
| 2019 | 6,019 | 4,252 | 2,269 | 22,022 |
| 2020 | 6,052 | 4,465 | 2,304 | 22,412 |
| 2021 | 6,232 | 4,840 | 2,365 | 23,219 |
| 2022 | 6,350 | 5,939 | 2,499 | 24,533 |
| 2023 | 6,603 | 6,285 | 2,754 | 25,446 |
| 2024 | 6,919 | 6,888 | 3,108 | 26,800 |

Source: DUKES Table 5.7.A, "All generating companies" rows, `DUKES_5.7.xlsx`, retrieved
2026-07-24. **Confidence: H** for the de-rated figures as published.

**Important methodological note**: per DUKES note 4, wind and solar capacity in this table are
**de-rated for intermittency** (factors of 0.43 for wind, 0.17 for solar, per the Electricity Act
1989 convention) — these are NOT nameplate/installed MW. Back-calculating approximate nameplate
capacity by dividing by the de-rating factor gives, e.g., offshore wind nameplate ≈2,276/0.43 =
~5,293 MW (2016) rising to ≈6,888/0.43 = ~16,019 MW (2024) — this back-calculation is **inferred**
(a derived approximation using the published factor, not itself a DUKES-quoted nameplate figure)
and is directionally consistent with widely-reported UK offshore wind buildout (Hornsea One
commissioned 2019-20, Hornsea Two 2022, Seagreen 2023, Dogger Bank phases 2023-25 — these
individual project dates are **not independently re-verified this session**, background context
only).

---

## 4. Candidate era boundaries

Grounded in the fossil-fuel-capacity plateau structure of §2 Table (A) and the coal
generation-share cliffs of §1a — **not** in any model output:

| Candidate era | Years | Real-world grounding | Fossil capacity (A) range |
|---|---|---|---|
| **Era A — "Coal still material"** | 2016-2018 | Coal generation share 9.0%→5.0%, still a visible part of the merit order; fossil capacity roughly flat 49.8-51.0 GW (small net additions offsetting early coal closures); nuclear fleet at its decade-high 9,261 MW throughout | ~50-51 GW |
| **Era B — "Post-major-coal-closure plateau"** | 2019-2022 | Coal share falls below 3% and stays there (2.1%→1.8%); fossil capacity drops sharply from Era A (49.8/50.3 GW in 2018 to 43.9 GW in 2019, then plateaus 42.5-43.9 GW for four years); first nuclear capacity step-down (9,261→7,833 MW in 2020); renewables share crosses 40% (2020, partly COVID-demand-inflated) | ~42-44 GW |
| **Era C — "Coal exit completed"** | 2023-2025 | Coal capacity collapses from 5,340 MW (2022) to 2,046 MW (2023) to 18 MW / zero from 1 Oct 2024; fossil capacity falls again to 39.8 GW (2023) and 36.3 GW (2024); second nuclear step-down (7,833→5,883 MW in 2022, carried through); renewables share crosses 50% (2024) | ~36-40 GW (falling) |

**Coarser 2-era alternative**, if only a single breakpoint is wanted: split at the **2018/2019
boundary** — this is where both the coal-share cliff (5.0%→2.1%) and the fossil-capacity cliff
(50.3→43.9 GW, a 12.5% one-year drop, the single largest year-on-year move in the whole
2016-2024 fossil-capacity series) coincide. Pre-2019: coal materially present, fossil capacity
~50 GW. Post-2019: coal residual/near-zero, fossil capacity 36-44 GW and trending down.

**A finer 4th-era candidate for 2025 onward** cannot yet be grounded — no full-year 2025 DUKES
data exists as of this session (§2). Flagged for a follow-up DISCOVER pass once DUKES 2026
(covering 2025) or NESO/Elexon settlement-derived capacity proxies become available.

---

## 5. Confidence / caveats

- **Primary quantitative evidence (§1a, §1b, §2, §3a, §3b) is H-confidence**: all pulled live
  this session directly from DESNZ's published DUKES Chapter 5 workbooks
  (`DUKES_5.6.xlsx`, `DUKES_5.7.xlsx`), themselves the standard official UK electricity-statistics
  series (successor to historical DTI/DECC/BEIS series, now published by DESNZ). No intermediate
  aggregation website or secondary source was used for the numeric tables.
- **The Ratcliffe-on-Soar closure date (30 September 2024) is H-confidence**: independently
  fetched from Wikipedia this session AND cross-checked against the independently-fetched DUKES
  coal-capacity collapse to ~18 MW for calendar-year 2024 — two independent sources agreeing.
- **Individual coal-station-level closure dates other than Ratcliffe-on-Soar, and the specific
  2015/2021 policy-announcement provenance, are M-confidence / inferred**: well-established
  public record but not independently re-fetched from a primary government source this session
  (gov.uk's current search index did not surface a working link to the original announcements
  within this session's search budget). These do not affect the load-bearing capacity/generation
  numbers, which stand on their own regardless of the exact policy-announcement citation.
- **2020 renewables-share spike is a confound, not a pure capacity signal**: the +6.5pp jump in
  renewables generation share 2019→2020 is partly a demand-denominator effect (COVID-19 lockdown
  reduced total GB generation from 327.2 TWh to 310.3 TWh that year) rather than solely new
  renewable capacity coming online. Any era boundary drawn near 2020 should account for this
  confound rather than treating the share jump as a pure structural break.
- **De-rated vs nameplate renewables capacity (§3b)**: DUKES Table 5.7 wind/solar capacity
  figures are de-rated for intermittency by fixed statutory factors (0.43 wind, 0.17 solar), NOT
  raw installed nameplate MW. Any comparison to a model's raw installed-capacity assumption must
  account for this, or use the back-calculated (inferred) nameplate approximation given in §3b.
- **Pumped hydro (2,744 MW, roughly constant across 2016-2024) is excluded from both
  "dispatchable" candidate definitions (A) and (B)** in §2 — it is dispatchable storage, not a
  net energy source, and DUKES itself excludes it from "renewables". Whether a scarcity-pricing
  model's residual-demand denominator should include it is a modelling judgement outside this
  document's scope; flagged so it isn't silently dropped or silently double-counted downstream.
- **No 2025 full-year capacity or generation-mix data exists yet** in the DUKES annual series as
  published (accessed 2026-07-24). The Era C boundary's "2025" label is a forward projection of
  the observed 2022-2024 trend, not itself observed. A future DISCOVER pass should re-check DUKES'
  next annual release (expected to cover 2025) or pull partial-year 2025 figures from Energy
  Trends' quarterly ET 5.1-5.6 series (also available at
  https://www.gov.uk/government/statistics/electricity-section-5-energy-trends, sampled this
  session but not analysed for this task) before treating any 2025 figure as grounded.
- **This document deliberately does not look at, compute, or reference the simulation's `x`
  scarcity-ratio series or SSP output**, per the task's explicit instruction that era boundaries
  must be established blind to any model residual (R12/R13 discipline). The §2 "Is 35,000 MW
  defensible" discussion compares the constant only against independently-sourced real-world MW
  figures, never against a fitted or observed model output.

## Sources (full list)

- DUKES Table 5.6 "Fuel input, and by-products of, electricity generators", `DUKES_5.6.xlsx`
  — https://assets.publishing.service.gov.uk/media/688a31dda11f859994409290/DUKES_5.6.xlsx
  (via https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes),
  retrieved 2026-07-24.
- DUKES Table 5.7 "Plant capacity", `DUKES_5.7.xlsx`
  — https://assets.publishing.service.gov.uk/media/688a28b38b3a37b63e739064/DUKES_5.7.xlsx
  (same publication page), retrieved 2026-07-24.
- DUKES 2025 Chapter 5 (Electricity) narrative PDF
  — https://assets.publishing.service.gov.uk/media/688a28656478525675739051/DUKES_2025_Chapter_5.pdf,
  retrieved 2026-07-24 (referenced for publication context, not separately quoted numerically
  in this document).
- Wikipedia, "Ratcliffe-on-Soar Power Station" — https://en.wikipedia.org/wiki/Ratcliffe-on-Soar_Power_Station,
  retrieved 2026-07-24 (closure date and capacity cross-check only).
- gov.uk "Electricity Section 5: Energy Trends" (ET 5.1-5.6, quarterly-updated series) —
  https://www.gov.uk/government/statistics/electricity-section-5-energy-trends, browsed
  2026-07-24 for publication landscape only; not used for the numeric tables in this document
  (DUKES annual tables 5.6/5.7 were the more directly relevant capacity+generation series found).
