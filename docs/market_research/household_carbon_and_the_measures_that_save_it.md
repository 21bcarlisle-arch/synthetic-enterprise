# Household carbon, and the measures that save it

**Knowledge:** household-carbon-and-the-measures-that-save-it

*2026-10-05. Step 1 of `docs/staging/done/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`, answering the
director's investigation of the same day: whether a gas-heated home's heating is about five times the
carbon of all its electricity, whether our knowledge has the balance right, three claims to test, and
a map of measures by cash and carbon as the basis for next best action. Every derived figure below was
printed at its real inputs before it was written here. The grid figures are annual and seasonal
means of the built series `sim/cache/grid_carbon_history.json` (read through `sim/grid_carbon_history.py`),
weighted as each table says; the scratch scripts that printed them were not committed, so each table
states its method in enough detail to recompute it.*

Each figure is marked **[sourced]** (read from a cited publication), **[measured]** (computed here from
a cited series in the repo), **[derived]** (arithmetic on sourced and measured figures, with the
arithmetic shown) or **[gap]** (not established — no number is offered).

---

## 1. What household carbon is

Before any number, the thing being counted. "A household's carbon" splits into parts that behave
differently, are measured differently, and are visible to a supplier differently:

| Part | What it is | Factor basis | Can a supplier see the kWh? |
|---|---|---|---|
| **Gas burnt at home** | Combustion of natural gas for space heating, hot water and (a small, unmeasured share) cooking | DESNZ *Scope 1* natural-gas factor, per kWh **gross CV**. Almost exactly constant over 2016–2025 (§2) because the chemistry does not change | Yes — its own gas meter |
| **Upstream of the gas** | Extraction, processing, transport of that gas ("well-to-tank", WTT) | DESNZ *WTT – fuels*, natural gas, 0.03021 kgCO2e/kWh gross CV in the 2023–2025 sets [sourced] | Derivable from the same meter |
| **Electricity used at home** | Generation emissions of the kWh imported | Either NESO's half-hourly national series (generation basis, T&D losses NOT included -- see §2), or DESNZ *Scope 2* "electricity generated" (+ separate *T&D* and *WTT* factors) | Yes — its own electricity meter, half-hourly if smart and settled half-hourly |
| **The car** | Petrol/diesel burnt, or electricity charged | DESNZ *Passenger vehicles* per km | Only the electricity, and only as unlabelled load |
| **Embodied carbon of kit** | Manufacturing a battery, panels, a heat pump, insulation | Lifecycle studies (ICCT, IPCC AR5, UNECE) | No |

Two consequences carry through the rest of this page:

1. **"Electricity carbon" is two different numbers depending on the basis**, and they differ by 30–45%
   in the latest years. NESO's series is the grid's *own year*, generation only. DESNZ's "UK electricity"
   factor in reporting year *Y* is a **two-year-lagged** annual figure (the 2025 set's 0.177 reflects
   the 2023 grid) and DESNZ advises adding **T&D losses** (0.01853 in 2025) [sourced: DESNZ 2025 flat
   file]. This page uses NESO for the grid as it was, and shows DESNZ beside it. A customer-facing
   statement must pick one and say which.
2. **A supplier sees fuels, not end uses.** It sees gas kWh, not "heating"; electricity kWh, not "EV".
   Everything a supplier says about a *measure* is an inference from a change in a meter.

### 1a. The electricity figure customers see: its definitions, stated (2026-11-11)

*On the director's 11 Nov steer (`docs/staging/advisor/DIRECTOR_STEER_STATE_OUR_CARBON_DEFINITIONS_AND_ADD_A_SECOND_INDEPENDENT_CHECK_2026-11-11.md`, item 1).*
The household's electricity carbon (`company/billing/carbon_footprint.py`,
`company/carbon/half_hourly_footprint.py`) multiplies its kWh by NESO's published national intensity
(`sim/grid_carbon_history.py` in the world, `docs/market_data/grid_intensity_feed.json` at the seam). That figure is:

| Choice | Ours | Why, and what it leaves out |
|---|---|---|
| **Average or marginal** | **Average**: the emissions of the generation NESO's national mix counts, over that generation, per half hour. *Corrected beside the claim (11 Nov, item 2):* this row first said "every GB generator". NESO's mix counts transmission-metered plant plus its estimate of embedded wind and solar. Embedded and captive thermal (gas CHP, waste, landfill gas, oil) is not in it. On Ember's UK figures that is about 43 TWh a year, §1b | GHG Protocol *Scope 2 Guidance* (2015) §6.10: location-based scope 2 is "based on average energy generation emission factors", and "Companies shall not use marginal emission factors … for a location-based scope 2 calculation" [sourced, PDF read 11 Nov]. The same paragraph says marginal factors "can be more useful for avoided emissions analyses". That is the open side, below |
| **Direct or lifecycle** | **Operational, at the generator**, on NESO's Table 1 factors: gas CCGT 394, coal 937 g/kWh; nuclear, wind, solar and hydro **zero**, so no lifecycle for them | Biomass sits at 120 g/kWh. That is neither its stack CO2 nor zero, so it carries some convention. **GAP:** what NESO's 120 counts is not established here. Electricity Maps defaults to the IPCC AR5 factors and offers both a lifecycle and a direct set [sourced, electricitymaps.com/methodology, 11 Nov]. Their figures are not ours to compare until the basis is matched |
| **Losses** | **Generation basis, losses NOT included** (measured 2026-10-05, §2) | DESNZ advises adding T&D (0.01853 kg/kWh in 2025). A figure that adds them says so |
| **Imports** | Inside NESO's historic mix, as NESO counts them. In our fill for the half hours NESO left blank: **one fixed factor per market**, NESO Table 1 (France 53, Netherlands 474, Belgium 179, Ireland 458 g/kWh), Norway from its annual SSB mix with thermal at 394. None of them varies by hour, and none is flow-traced. **ElecLink and Viking are left out** because NESO's mix leaves them out (`OUTSIDE_NESO_MIX`, `sim/elexon_fuel_outturn.py`) | *Corrected beside the claim:* the steer's "imports are counted at `import_factor` (one factor …)" is one factor **per market**, not one in total. Whether hourly or flow-traced import factors move GB's average materially (item 3): **small**. In Tranberg et al. (2019, *ESR*, doi:10.1016/j.esr.2019.100367, supplementary Table 4), hourly flow tracing over 2017 took GB from 346 kgCO2eq/MWh produced to 349 consumed, **+0.9%**. Their basis is ecoinvent fuel-chain factors, not ours. The import factors it implies differ from each exporter's own average by -9% (France to GB, 69 against 76) to +19% (Netherlands to GB, 871 against 734), Table 5. GB's import share was about 7% in 2017 and 15% in 2024-25. Even at twice the 2017 effect, flow tracing stays near ±2%, an order below the scope gap in §1b. So we stop there, as the steer asks. Scarlat et al. (2021, *Applied Energy*) was not read: the publisher returned 403 |
| **Consumption-based** | **No.** Generation in GB, imports added at their factor. No flow tracing of what GB re-exports | Electricity Maps is "attributional, location-based, and consumption-based", with flow tracing [sourced, their methodology page]. That difference has to be named before any figure of theirs is set beside ours |

**"Carbon saved by shifting" on average intensity is a stated choice, not a fact.** Moving a kWh
from 18:00 to 03:00 changes which plant runs at the margin, not the average. Our timing figures (§5)
are average-basis, and §4(b)'s caveat gives the marginal bound (up to 3.7× for solar, *if* the margin
were always CCGT, which is not established). The published GB side of that debate has been listed and
not yet read. These candidates are at **abstract level**, and none sets anything:
Thomson, Harrison & Chick (2016), "Marginal greenhouse gas emissions displacement of wind power in Great
Britain", *Energy Policy* (doi:10.1016/j.enpol.2016.11.012); Hawkes (2014), "Long-run marginal CO2
emissions factors in national electricity systems", *Applied Energy* (doi:10.1016/j.apenergy.2014.03.060);
Beltrami et al. (2020), "Where did the time (series) go? Estimation of marginal emission factors with
autoregressive components", *Energy Economics* (doi:10.1016/j.eneco.2020.104905).

*Corrected beside the claim, twice.* On 11 Nov morning this page said the steer's Electricity Maps
"withdrawal" was not on their pages. **That was wrong, and the steer was right.** Their publication
"Our latest research on Marginal emission factors" (published 13 May 2024, updated 14 Jan 2025,
electricitymaps.com/resources/publications/our-latest-research-on-marginal-emission-factors) concludes:
"marginal signals come with major limitations, such as the incompatibility with regulation, which is
why we no longer offer marginal signals". Their 2018 machine-learning article, updated the same day,
carries the same note. The miss was searching the explainer and methodology pages and not the
publications list. Two reasons now stand together for not using marginal for this figure: the GHG Protocol's
"shall not", and the practitioner who built a marginal signal and then withdrew it. Neither of them settles
"saved by shifting", which stays a stated choice.

### 1b. Ember as a second check on 2016–2025 (2026-11-11, steer item 2)

*Pre-registered before the data was read:
`docs/staging/records/SEAT_PREREG_WHAT_EMBER_SAYS_ABOUT_OUR_GB_CARBON_HISTORY_2026-11-11.md`.*
**Knowledge only (W6).** The file was fetched once by the harness. Nothing in `sim/`, `company/` or `saas/` reads it.

**What each one counts, before any differencing.** The basis is read from *Ember Methodology v1.6*
(files.ember-energy.org/public-downloads/ember_electricity_data_methodology.pdf) and checked against the
factors its own CSV implies. Ember is CC-BY-4.0 (ember-energy.org/creative-commons). Source: Ember, yearly
electricity data, release of 3 Nov 2026.

| | Ours (`sim/grid_carbon_history.py`, NESO historic mix) | Ember, United Kingdom |
|---|---|---|
| Area | GB | **UK**, Northern Ireland included (from Green Collective) |
| Generation counted | Transmission-metered, plus NESO's embedded wind and solar | All. GB from ESO, "upscaled for bio, gas and hydro based on the quarterly total generation reported by DESNZ" to capture "captive and small thermal". Annual from the Energy Institute, **gross** |
| Factors | Operational at the stack: gas 394, coal 937, biomass 120, zero-carbon 0 | **Lifecycle CO2e**, upstream methane included. Gas per Jordaan et al. 2022, CHP-adjusted. Bio 230, solar 48, hydro 24, other fossil 700 (IPCC AR5 midpoints), cut 6% for thermal on gross generation. The CSV implies gas 480, coal 962, bio 216, nuclear 4.8, wind 12.7, other fossil 658 |
| Imports | In the denominator, at a factor | **Out.** Intensity is over generation only ("Total generation" row) |
| Clock | Half-hourly, averaged here by energy over each calendar year | Annual |

**By year.** "Ours" is NESO's intensity weighted by its GENERATION column, which is the figure
a customer's annual kWh actually meets. "Ember rebased" is Ember's TWh by fuel, converted to net
(÷1.06 thermal, ÷1.01 other), priced at NESO's operational factors, with Ember's net imports added at the
import factor NESO's own mix implies that year (below). It is shown as a range because NESO has no factor for Ember's "other fossil" (300, NESO's OTHER, to 700).

| Year | Ember as published (lifecycle, UK, no imports) | Ours | Published ÷ ours | Ember rebased to our basis | Rebased ÷ ours |
|---|---|---|---|---|---|
| 2016 | 333 | 282 | +18% | 265–277 | −6% to −2% |
| 2017 | 302 | 249 | +21% | 237–248 | −5% to −1% |
| 2018 | 286 | 222 | +29% | 218–230 | −2% to +3% |
| 2019 | 268 | 195 | +37% | 197–210 | +1% to +8% |
| 2020 | 243 | 173 | +40% | 177–188 | +3% to +9% |
| 2021 | 267 | 187 | +43% | 194–206 | +4% to +10% |
| 2022 | 255 | 183 | +40% | 188–201 | +3% to +10% |
| 2023 | 235 | 151 | +56% | 164–178 | +9% to +18% |
| 2024 | 216 | 128 | +69% | 144–158 | +13% to +24% |
| 2025 | 218 | 130 | +68% | 146–162 | +13% to +25% |

**Where they agree.** The shape agrees: the two move the same way in all 9 steps, falling in 7 and rising in 2021 and 2025. On a matched basis the two agree within a few percent in 2016–2018.

**Where they part, and the leading explanation.** The rebased gap grows from about −4% to about +19% because
Ember counts generation NESO's mix does not. Against NESO's GB columns, Ember's UK figures carry 14–19 TWh more gas,
16–19 TWh more bioenergy and waste, and 10–13 TWh of "other fossil" in every year, about 43 TWh or 13% of
generation. That is steady, while NESO's transmission gas halved. So the share of the carbon that
the national figure does not see grows as the transmission system decarbonises. Adding only that
excess thermal to ours, at operational factors, lifts 2024 from 128 to 145–167. **I cannot yet say** how much
of it is Northern Ireland, which is a different system, and how much is GB embedded and captive thermal,
which a GB household's kWh does meet. DESNZ *Energy Trends* 5.1 and *DUKES* 5.6, by region and producer type, would split it.
**GAP.**

**What it means for the customer figure (F11, erring against our thesis).** If most of the excess is GB embedded
thermal, our customer figure **understates** GB average intensity by roughly 10–25% in 2023–2025, and by less
earlier. A low grid figure flatters every electrification measure in §4 and §5. The series is NOT changed: the
steer asks for what and why first, and the GB/NI split is not established. Finding:
`docs/staging/SEAT_FINDING_THE_NATIONAL_CARBON_FIGURE_DOES_NOT_COUNT_EMBEDDED_THERMAL_2026-11-11.md`.

**The "few percent ABOVE" fill bias.** Ember cannot apportion it, because Ember has no half-hours. But the
check led to the term. On the half hours where both exist:

| Year | Fill − historic mix | Fill import share | Historic-mix import share | Fill import factor | Historic mix's implied import factor | ElecLink + Viking share of import MW |
|---|---|---|---|---|---|---|
| 2016 | −3.5% | 6.7% | 6.7% | 240 | 241 | 0 |
| 2018 | +0.1% | 7.3% | 7.4% | 218 | 192 | 0 |
| 2021 | +2.4% | 10.2% | 10.3% | 161 | 117 | 0 |
| 2023 | +5.0% | 10.7% | 12.2% | 128 | 72 | 14% |
| 2024 | +7.1% | 12.4% | 15.7% | 103 | 57 | 24% |
| 2025 | +3.9% | 11.8% | 15.2% | 93 | 74 | 25% |

The bias is the **import term**. (1) The fill's per-market factors price imports at 20–55 g above (2018–2025) the factor
NESO's own mix implies. That factor is the residual after GAS, COAL, BIOMASS and OTHER at NESO's table, so it
also absorbs any domestic difference, and it is an attribution, not a measurement. (2) The fill's import share
falls short of the historic mix's by about the ElecLink and Viking flows it leaves out, which suggests
**NESO's historic mix does count those two cables**, contrary to `OUTSIDE_NESO_MIX`'s premise for this file. At
2024 shares, (1) is about 5–6 g and (2) about 1–3 g, against an 8.8 g bias. Before 2018 the sign flips,
which is consistent with the pre-split OTHER pricing. **Effect today: none.** `coverage_by_year` shows 0 filled
half hours in every year, so the fill reaches no published value.

---

## 2. The ratio: gas against all electricity, 2016–2025

**The household.** Ofgem's Typical Domestic Consumption Value (TDCV), *medium*, Profile Class 1 (single
rate), gas and electricity, kWh/yr [sourced]:

- 2023 review (in force from October 2023): **gas 11,500, electricity 2,700** — Ofgem, *Decision for
  Typical Domestic Consumption Values 2023*, https://www.ofgem.gov.uk/decision/decision-typical-domestic-consumption-values-2023 .
- 2026 review (in force from 1 July 2026, outside our record): **gas 9,500, electricity 2,500** —
  Ofgem, *Review of typical domestic consumption values: decision* (May 2026), Table 1,
  https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf .
- Earlier revisions [sourced, Ofgem TDCV decision letters]: **12,500 / 3,100** from 1 Sept 2015
  (`tdcvs_2015_decision_1.pdf`); **12,000 / 3,100** from 1 Oct 2017 (`tdcvs_2017_decision.pdf`);
  **12,000 / 2,900** from 1 Apr 2020 (`tdcvs_2020_decision_letter_0.pdf`), carried through the postponed
  2021 review ("Medium TDCVs are currently 12000 kWh for gas, 2900 kWh for electricity profile class 1",
  `tdcv_decision_letter_2021_0.pdf`, footnote 5). Each year below uses the value in force for most of it.
  *Aside: `company/regulatory/price_cap.py`'s header says "3100kWh elec, 12000kWh gas" for every period
  through 2025, which is the 2017–2020 value only.*

**Gas factor** [sourced, DESNZ *Greenhouse gas reporting: conversion factors*, flat file for each year,
Scope 1, Fuels › Gaseous fuels › Natural gas, kWh (**Gross CV**), kgCO2e]:
2016 0.18400 · 2017 0.18416 · 2018 0.18396 · 2019 0.18385 · 2020 0.18387 · 2021 0.18316 · 2022 [not parsed] ·
2023 0.18293 · 2024 0.18290 · 2025 0.18296. *(2021 read from the full set `.xlsm`, Fuels sheet; the 2022 files could not be parsed — the 2021 and 2023 values bracket it and are both shown.)* Gross CV is the right basis because GB gas meters are
billed in kWh converted at the gross calorific value. WTT (0.03021) is **excluded** from the table below
so that both fuels are counted at the point of use; adding it raises the gas column by 16.5%.

**Electricity** [measured]: the annual mean of `sim/grid_carbon_history.py` (NESO's Historic GB
Generation Mix `CARBON_INTENSITY`, one basis 2016-2025), **weighted by the Elexon Profile Class 1
domestic load shape** (`sim/profile_class_1.py`), because a household does not consume evenly across
the day. NESO's series is generation intensity and **excludes T&D losses**. The DESNZ column uses
that reporting year's "electricity generated" + "T&D" factors.
*Corrected 2026-10-05, and the earlier same-day correction withdrawn.* The earlier note said NESO's
national series does NOT exclude losses, on the strength of NESO's methodology text ("corrected to
account for transmission losses to give the intensity of consumption"; NESO FOI/25/152, 24 Nov
2025). **The data has not matched that text since 2020-04-27 period 34** [measured, G14]: the
Carbon Intensity API's `actual` reads about 1.14x NESO's Historic Generation Mix before that half
hour and about 1.02x after, and its implied fuel factors after it are NESO's table with no loss
multiplier. So the API carried a loss uplift until 2020-04 and is generation basis since. The
series used here is now the Historic Generation Mix, which is generation basis throughout. **So
"DESNZ generated + T&D" is per kWh consumed and NESO is per kWh generated**; part of the gap
between the columns IS losses (DESNZ's T&D factor, 0.01853 in 2025), the rest is DESNZ's two-year
lag and factor basis. Whether a household figure adds losses is a definition decision; if it does,
they are a separate named line, never folded into the NESO value. The company's annual level
(`docs/market_data/grid_intensity_feed.json`, `annual_level`) is NESO demand-weighted (Elexon INDO),
which reads within 2.5 g of the PC1-weighted figures below in every whole year 2017-2024. The NESO
columns below were recomputed on the historic mix the same day; on the API they read 8-14% higher
for 2016-2019.

| Year | TDCV gas / elec kWh | Gas kgCO2e | Elec kgCO2e (NESO, PC1-weighted) | **Ratio (NESO)** | Elec kgCO2e (DESNZ gen+T&D) | Ratio (DESNZ) |
|---|---|---|---|---|---|---|
| 2016 | 12,500 / 3,100 | 2,300 | 886 | **2.6×** | 1,393 | 1.7× |
| 2017 | 12,500 / 3,100 | 2,302 | 783 | **2.9×** | 1,192 | 1.9× |
| 2018 | 12,000 / 3,100 | 2,208 | 700 | **3.2×** | 952 | 2.3× |
| 2019 | 12,000 / 3,100 | 2,206 | 614 | **3.6×** | 860 | 2.6× |
| 2020 | 12,000 / 2,900 | 2,206 | 506 | **4.4×** | 734 | 3.0× |
| 2021 | 12,000 / 2,900 | 2,198 | 552 | **4.0×** | 670 | 3.3× |
| 2022 | 12,000 / 2,900 | 2,195–2,198 (bracket) | 531 | **4.1×** | 612 | 3.6× |
| 2023 | 12,000 / 2,900 | 2,195 | 445 | **4.9×** | 652 | 3.4× |
| 2024 | 11,500 / 2,700 | 2,103 | 356 | **5.9×** | 608 | 3.5× |
| 2025 | 11,500 / 2,700 | 2,104 | 362 | **5.8×** | 528 | 4.0× |

Grid intensity used (g/kWh, PC1-weighted / time-mean) [measured, historic mix]: 2016 286/274 ·
2017 252/240 · 2018 226/214 · 2019 198/189 · 2020 175/168 · 2021 190/183 · 2022 183/181 · 2023 153/149 ·
2024 132/124 · 2025 134/127. Clock-change days are left out of the PC1 weighting (the profile has 48
periods) and kept in the time mean. DESNZ electricity factors by reporting year (generation / T&D) [sourced, flat files and the
2025 methodology paper Table 9]: 2016 0.41205/0.03727 · 2017 0.35156/0.03287 · 2018 0.28307/0.02413 ·
2019 0.25560/0.02170 · 2020 0.23314/0.02005 · 2021 0.21233/0.01879 · 2022 0.19338/0.01769 ·
2023 0.20707/0.01792 · 2024 0.20705/0.01830 · 2025 0.17700/0.01853.

And **the same household every year** (11,500 / 2,700 throughout), so the only thing moving is the
grid:

| Year | Gas kg | Elec kg (NESO, PC1) | Ratio |
|---|---|---|---|
| 2016 | 2,116 | 772 | 2.7× |
| 2017 | 2,118 | 682 | 3.1× |
| 2018 | 2,116 | 610 | 3.5× |
| 2019 | 2,114 | 535 | 4.0× |
| 2020 | 2,115 | 471 | 4.5× |
| 2021 | 2,106 | 514 | 4.1× |
| 2022 | 2,104–2,106 | 494 | 4.3× |
| 2023 | 2,104 | 414 | 5.1× |
| 2024 | 2,103 | 356 | 5.9× |
| 2025 | 2,104 | 362 | 5.8× |

**Verdict: "about five times" is right for 2023–2025 and was not right before.** On the grid's own
annual intensity, the gas of a TDCV-medium home is **5.1× its electricity in 2023 and 5.8–5.9× in
2024–2025**. In 2016 it was **2.7×** (same household) or **2.6×** (that year's TDCV). The ratio more than
doubled over the decade, and **all of the movement is the grid**: the gas factor moved by 0.6% while
the household's electricity intensity fell by 53% (286 → 134 g/kWh PC1-weighted). On DESNZ's lagged
factors with T&D the 2025 ratio is **4.0×**, because DESNZ's 2025 factor still carries the 2023 grid.
At the 2026 TDCV (9,500 / 2,500) and the 2025 grid the ratio is **5.2×** [derived: 9,500 × 0.18296 =
1,738 kg; 2,500 × 0.134 = 335 kg].

So the director's figure holds **now** and should be quoted with its year: "five to six times, on
2024–25's grid". It will keep rising while the grid decarbonises and gas does not.

---

## 3. The balance of our knowledge

A census of the knowledge layer and the code, run 2026-10-05 over this worktree (file counts by grep;
classification by reading).

**Research docs (`docs/market_research/`, 142 files):** 51 mention time-of-use, load shifting or flex;
23 mention insulation, loft or cavity; 13 mention heat pumps. Of those, **21 timing docs discuss carbon,
against 4 insulation docs and 8 heat-pump docs**. The dedicated carbon research is all electricity-grid:
`what_ep13_established_about_gb_grid_carbon.md` (43 steps of half-hourly reconstruction), the NESO
interconnector and biomass notes. **No research doc held a household gas carbon figure or a
measure-by-measure carbon saving until this one.** Gas appears as a *demand* subject
(`gas_demand_what_drives_it…`, `gas_demand_cumulative_hdd_cwv.md`, `mains_gas_is_a_meter_fact…`,
`need_domestic_gas_high_tail.md`) and never as a carbon subject.

**Knowledge pages (`site/knowledge/`, 22 pages):** **none** is about household carbon. `carbon-price` is the
allowance price (a wholesale cost). `what-a-house-does-to-its-energy` (fabric physics) mentions tonnes once,
as an aspiration. The knowledge map (`docs/institutional/knowledge_map.md`) has 3 carbon rows: operational
carbon (the company's own compute), grid intensity, and a ToU response row; **no row covers gas carbon,
heating carbon, or the carbon of a measure.**

**Code.**
- `company/carbon/half_hourly_footprint.py` — the only *live* household carbon instrument — is
  **"Electricity emissions only"** by design (`FOOTPRINT_BASIS`, line 92) and lists gas first under
  `NOT_INCLUDED` ("a near-constant factor per kWh burned, and the only lever on it is using less").
- It is **published**: `site/data/explore_carbon.json` (generated 2026-10-04 by
  `tools/generate_explore_carbon.py`, shown at `site/explore/`) gives per-account footprints for 244
  accounts on that electricity-only basis.
- `company/carbon/carbon_ledger.py` (E5 SAVED/SPENT) is fuel-agnostic and its SPENT side is the company's
  own compute; E5 is parked at level 1 of 3.
- A dual-fuel household class exists — `company/regulatory/carbon_emissions.CustomerCarbonFootprint`,
  gas at 183 g/kWh — but `build_customer_footprint` has **no production caller** (tests only).
  `company/portal/app.py:35` imports `estimate_carbon` and never calls it.
- The gas and heating *advice* modules carry **money only**: `company/pricing/fabric_intervention.py`
  (insulate / heat_pump / solar_pv / time_shift / turn_down, ranked by lifetime £; no carbon field),
  `company/crm/decarb_recommender.py`, `company/billing/efficiency_advice.py`.
- Electricity timing code: `sim/grid_carbon_{history,intensity,future}.py`, `sim/neso_carbon_intensity.py`,
  `sim/elexon_fuel_outturn.py`, `sim/neso_embedded_generation.py`, `tools/tou_*` (3),
  `tools/r3_carbon_score_ceiling.py`, `company/sustainability/carbon_intensity_register.py`.
- Gas factors in code: **two unreconciled values** — 183.0 g in `company/regulatory/carbon_emissions.py:126`
  and **0.18253** in `company/sustainability/environmental_impact.py:32`. The second is DESNZ's
  **CO2-only** column (row `…_6_2`), not the CO2e column (0.1829 in 2023/2024) its comment claims, and
  its "combustion-only 0.2037" is the net-CV figure, a different basis.

**Verdict.** The balance is wrong in the direction the director suspected, and more sharply. The carbon
knowledge and code are **electricity-timing-centric**: 21 timing documents discuss carbon against 12
heating documents (4 insulation, 8 heat pump), none of which holds a gas carbon figure; a 43-step grid
reconstruction; and no household gas-carbon knowledge at all. On the 2025 grid the customer-facing footprint the company publishes covers **365 kg of a
TDCV-medium home's ~2,470 kg (15%)** and omits the **2,104 kg (85%)** that is gas [derived, §2]. And the
timing lever that the code is built around is worth **~36 g per kWh shifted** in 2025 (§5), against
**183 g per kWh of gas not burnt** — five times as much per kWh, on four times as many kWh.

---

## 4. The director's three claims, tested

### (a) "An EV is a large total saving, but it raises the household's electricity carbon, and the supplier cannot net it off because it cannot see the petrol."

**Inputs.**
- Mileage: **7,100 miles/yr per car** (England, 2024; 6,200 for petrol cars, 8,900 for BEVs) — DfT,
  *National Travel Survey 2024*, https://www.gov.uk/government/statistics/national-travel-survey-2024/nts-2024-introduction-and-main-findings [sourced]. = 11,426 km.
- Petrol, average car, per km: **0.16272 kgCO2e tailpipe + 0.04599 WTT = 0.2087** (DESNZ 2025;
  2017: 0.18568 + 0.05051) [sourced, DESNZ flat files, Passenger vehicles › Cars (by size) › Average car › Petrol, and WTT – cars].
- BEV, average car, per km: **0.03663 Scope 2 + 0.00384 T&D + 0.01049 WTT = 0.0510** (DESNZ 2025)
  [sourced]. DESNZ's implied consumption is 0.03663 / 0.177 = **0.207 kWh/km** [derived].
- Battery debt: ICCT (July 2025) — a BEV's production emissions are **about 40% higher** than a petrol
  car's, "more than offset after about 17,000 km of use in the first one or two years"; lifecycle
  **63 gCO2e/km BEV vs 235 gCO2e/km petrol (−73%)** on the projected 2025–2044 EU mix — ICCT, *Life-cycle
  greenhouse gas emissions from passenger cars in the European Union: a 2025 update*,
  https://theicct.org/publication/electric-cars-life-cycle-analysis-emissions-europe-jul25/ [sourced]. The
  ICCT 2021 study puts the EU battery mix at **60 kgCO2e per kWh of battery** [sourced, ICCT July 2021,
  *A global comparison of the life-cycle GHG emissions of combustion engine and electric passenger cars*].

| DESNZ set | Petrol car kgCO2e/yr (tailpipe + WTT) | BEV kgCO2e/yr (DESNZ: gen + T&D + WTT) | Saving | BEV kWh/yr | BEV kg at NESO overnight / time-mean |
|---|---|---|---|---|---|
| 2017 | 2,699 | 1,063 | 1,635 | 2,386 | 552 / 624 |
| 2019 | 2,627 | 784 | 1,844 | 2,481 | 459 / 528 |
| 2023 | 2,393 | 765 | 1,628 | 2,783 | 384 / 423 |
| 2025 | 2,385 | 582 | **1,803** | 2,365 | **269 / 306** |

[derived: km × DESNZ per-km factors; kWh = km × (DESNZ Scope 2 per km ÷ DESNZ generation factor); NESO
columns = kWh × that calendar year's overnight (settlement periods 2–9) or time-mean intensity.] The petrol
side improved by 12% over the decade (new cars more efficient); the BEV side by 45% (the grid).

**Verdict: true on all three counts, and the second is larger than it sounds.**
- *Large total saving:* **≈1.8 t CO2e/yr** on DESNZ 2025 factors (2,385 kg petrol → 582 kg BEV, well-to-wheel)
  [derived] — the same order as the entire gas footprint of the home (2,104 kg). The battery debt is
  repaid in ~17,000 km, about **1.5 years** at 11,426 km/yr [derived from ICCT].
- *Raises household electricity carbon:* the EV adds **≈2,365 kWh/yr** — **0.88× the TDCV home's whole
  electricity use** [derived]. At the 2025 grid that is **+269 kg** if charged overnight (00:30–04:30
  mean 113.9 g/kWh) or **+306 kg** at the annual time-mean [measured × derived]. The household's
  *electricity* carbon roughly **doubles** (365 → ~640–670 kg).
- *Cannot net it off:* correct. The supplier sees the added kWh (and, half-hourly, a charging-shaped
  load) but never the petrol not bought. It can **estimate** the avoided petrol only by assuming a
  mileage and a counterfactual car. A "you saved" statement about an EV is therefore always an
  estimate with two assumptions, never a meter fact.

Where the claim is incomplete: **smart charging is a second, separate, small, evidenced saving**. Moving
the EV's 2,365 kWh from the 16:00–19:00 window to 00:30–04:30 saves 36.0 g/kWh in 2025 = **85 kg/yr**
[measured × derived] — under 5% of the EV's own total saving, but it is the one EV carbon claim a
supplier can **evidence from its own half-hourly data**.

### (b) "Solar is now mostly a money decision."

**Inputs.**
- Yield: NESO's embedded-solar estimate, annual generation over capacity, **0.089–0.105 capacity factor**
  = **782–915 kWh per kWp per year** across 2016–2025 (`sim/cache/neso_embedded_generation.json`)
  [measured]. This is a fleet figure, not a rooftop one; MCS/EST rooftop yields are the better
  household anchor where cited below.
- Displaced intensity: the grid intensity **in the hours solar generates**, i.e. the half-hourly series
  weighted by NESO's own embedded-solar output [measured]. This is an **average**, not a marginal,
  displacement factor — see the caveat below.
- Panel lifecycle: **41 gCO2e/kWh**, median for rooftop PV (range 26–60), IPCC AR5 WGIII Annex III,
  Table A.III.2, https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf [sourced].

| Year | kWh/kWp | Solar-weighted g/kWh | Gross kgCO2e displaced per kWp | Net of panel lifecycle |
|---|---|---|---|---|
| 2016 | 915 | 276 | 253 | 215 |
| 2017 | 859 | 232 | 200 | 164 |
| 2018 | 887 | 243 | 216 | 179 |
| 2019 | 894 | 203 | 181 | 145 |
| 2020 | 913 | 169 | 154 | 116 |
| 2021 | 855 | 182 | 156 | 121 |
| 2022 | 913 | 177 | 161 | 124 |
| 2023 | 846 | 142 | 120 | 85 |
| 2024 | 782 | 105 | 82 | 50 |
| 2025 | 896 | 105 | 94 | 58 |

The solar-weighted intensity is **lower than the annual mean** in every year (2025: 105 vs 129 g/kWh)
because solar runs when the grid is already cleanest, and the gap widened as solar's own share grew.

**Money, per kWp per year** [derived]: a self-consumed kWh is worth the import unit rate it avoids
(Oct 2025 cap 26.35p, `docs/market_research/svt_rates_active_passive_2016_2025.md`, H); an exported kWh
earns a Smart Export Guarantee rate (Ofgem SEG Year 5, 2024-25: average **untied 4.47p**, **tied 15.39p**,
as reported from Ofgem's SEG annual report [sourced, secondary]). The self-consumption share is a [gap] for a typical home: it depends on occupancy and is not published as a single figure by any source read.
So the money is bounded rather than pinned [derived, 2025]: per kWp, 896 kWh × 26.35p = **£236** if
all self-used, 896 × 4.47p = **£40** if all exported untied (£138 tied). A typical **4.5 kWp** system
(EST's current typical size, cost ~£7,600, EST *Solar panels* page, figures "based on fuel prices as of
July 2026") therefore earns between ~£180 and ~£1,060/yr; EST's static July 2023 *Solar guide* puts a
3.5 kWp system at **£530–£565/yr** with SEG (import 30.0p, SEG 5.45–5.5p) and **~800 kg CO2/yr** [sourced].
In **2016** EST's archived page (web.archive.org/web/20160614221819) gave a 4 kWp system ~3,800 kWh/yr
in southern England, FIT generation + export payments of ~£215 each, bill savings ~£195–210 and
**1,560–1,650 kg CO2/yr**, "nearly two tonnes" [sourced]. EST's own carbon figure fell from ~1.6–2.0 t
(2016, 4 kWp) to ~0.8 t (2023, 3.5 kWp) — the same direction as the measured series above, and
EST's figures are higher than ours because DESNZ's factor lags and includes losses.

**Verdict: true, and it flipped during the record.** Per kWp, the carbon displaced fell from
**253 kg (2016) to 82–94 kg (2024–25)** gross, **215 → 50–58 kg** net of the panels' own lifecycle — a
**63–68% fall gross, 73–77% net**. Over the same decade the money per self-consumed kWh roughly **doubled** (≈14p → 26p).
In 2016 the panel's carbon was a substantial share of its case; by 2025 a 4.5 kWp system displaces
~0.42 t/yr gross (4.5 × 94 kg) — about **one fifth of the home's gas carbon** — while saving several hundred pounds.
Solar is now **money-led**, with a real but modest carbon co-benefit.

*Caveat that could reverse the carbon size, not the verdict:* displacing the **margin** (usually gas
CCGT, which NESO's own methodology prices at 394 g/kWh — `sim/elexon_fuel_outturn.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH`) rather than the average would
roughly multiply the 2025 figure by 3.7 (394 / 105), if the margin were always CCGT — which is itself not established. Which is right
for a household claim is a method choice the industry does not settle; the GHG Protocol location-based
basis is the average, and this page uses it. [gap: a published GB marginal emission factor series
by half hour is not held in the repo.]

### (c) "A heat pump is often carbon-led."

**Inputs.**
- Heat demand: the TDCV home's 11,500 kWh of gas at an **in-situ boiler efficiency of 82.5%** (mean of the
  combination boilers in the Energy Saving Trust's 2009 field trial of 60 condensing boilers, "In-situ
  monitoring of efficiencies of condensing boilers", final report,
  https://assets.publishing.service.gov.uk/media/5a75149be5274a3cb28697f7/In-situ_monitoring_of_condensing_boilers_final_report.pdf
  [sourced]) = **9,488 kWh of heat** [derived]. This treats all the gas as heat and hot water; the cooking
  share is a [gap].
- Heat pump efficiency, **measured, not catalogue**: **median SPFH4 2.80** for ASHPs in the Electrification
  of Heat demonstration (Energy Systems Catapult, *Interim Heat Pump Performance Data Analysis Report*,
  March 2023, https://es.catapult.org.uk/wp-content/uploads/2023/03/EoH-Interim-Heat-Pump-Performance-Data-Analysis-Report-1.pdf);
  **median SPFH2 2.65** for ASHPs in the RHPP field data (DECC, *Final report on analysis of heat pump data
  from the RHPP scheme*, March 2017, https://assets.publishing.service.gov.uk/media/5a82b8faed915d74e62374d8/DECC_RHPP_161214_Final_Report_v1-13.pdf)
  [sourced]. EoH also records a median of **2.44 on cold days** [sourced, secondary report of the same study].
- Grid: the **October–March** mean of `sim/grid_carbon_history.py` [measured], because a heat pump draws
  most of its electricity in winter (2025: 141 g/kWh vs 129 annual).

| Year | Gas kgCO2e (11,500 kWh) | HP kgCO2e at SPF 2.80 (3,388 kWh × Oct–Mar grid) | Saved | % | Saved at SPF 2.65 |
|---|---|---|---|---|---|
| 2016 | 2,116 | 1,136 | 980 | 46% | 916 (43%) |
| 2018 | 2,116 | 904 | 1,211 | 57% | 1,160 |
| 2020 | 2,115 | 620 | 1,494 | 71% | 1,459 |
| 2022 | 2,104 | 568 | 1,537 | 73% | 1,505 |
| 2023 | 2,104 | 501 | 1,602 | 76% | 1,574 |
| 2025 | 2,104 | 478 | **1,626** | **77%** | 1,599 (76%) |

October–March grid intensity (g/kWh) [measured]: 2016 335 · 2018 267 · 2020 183 · 2022 168 · 2023 148 · 2025 141.

**Running cost on flat cap rates** [derived from the Ofgem cap unit rates in
`docs/market_research/svt_rates_active_passive_2016_2025.md`, H-confidence periods]: the heat pump is cheaper
than the boiler only when the electricity/gas unit-rate ratio is below **SPF ÷ boiler efficiency = 3.39**
(2.80/0.825). The cap ratio was:

| Cap period | p_e / p_g | Gas £/yr | HP £/yr (SPF 2.80) | HP minus gas |
|---|---|---|---|---|
| Jan 2019 | 4.43 | 429 | 560 | +£131 |
| Oct 2020 | 5.73 | 345 | 582 | +£237 |
| Apr 2021 | 5.67 | 384 | 642 | +£258 |
| Apr 2022 | 3.85 | 848 | 960 | +£113 |
| Oct 2022 (cap; EPG paid 3.30) | 3.52 | 1,697 | 1,758 | +£61 |
| Oct 2023 | 3.97 | 794 | 928 | +£135 |
| Apr 2025 | 3.87 | 804 | 916 | +£112 |
| Oct 2025 | 4.19 | 723 | 893 | **+£169** |

2016 (the source's ~13.5–14.5p / ~3.8–4.2p ranges, M confidence) gives a ratio of about 3.5: near
break-even. EST's current page [sourced, *Air source heat pumps*, July 2026 prices, 3-bed semi]: **£260/yr
saving against an old G-rated gas boiler**, a further **£330/yr on a heat-pump electricity tariff**, a
further **£105/yr if the gas supply is disconnected**, and "little or no saving" against a modern A-rated
boiler without a tariff switch; installed cost **~£12,000**; Boiler Upgrade Scheme grant **£7,500** from
23 October 2023 (£5,000 before) [sourced]. EST's 2016 page (March 2016 prices, 4-bed detached) gave
£415–£635/yr against an *older non-condensing* gas boiler, 2,100–3,300 kg CO2/yr, plus RHI payments of
~£1,000–1,500/yr — a different counterfactual and a subsidy, so not comparable with ours.

**Verdict: true for a flat-tariff household in every cap period on the record.** The heat pump
saves **≈1.0 t (2016) rising to ≈1.6 t CO2e/yr (2023–25), 46% → 77%** of the heating carbon, while costing
**£60–£260/yr more** to run on flat cap unit rates, before the gas standing charge (which disappears only
if the gas supply is capped) and before any heat-pump time-of-use tariff. Only in **Oct 2022's cap** (ratio
3.52, and 3.30 at the EPG rates households actually paid) did it come near break-even. The 2019–2021 ratios
(4.4–5.7) made it clearly carbon-led; 2023–2025 (3.9–4.2) still carbon-led, by ~£110–170/yr. **It becomes
win-win only through a tariff or a price ratio below ~3.4**, which is exactly the lever a supplier holds.
Installed cost and the Boiler Upgrade Scheme grant are in §5.

*Where it is partly wrong:* the carbon saving rose by 66% over the record purely because the grid
decarbonised. In 2016 a heat pump at SPF 2.65 saved only **43%** of the heating carbon. The claim is
"carbon-led" now; in 2016 it was "weakly carbon-led".

---

## 5. The measures, mapped by cash and carbon

**Basis.** A gas-heated home on the 2025 record. Gas saved is valued at the Oct 2025 cap gas unit rate
(6.29p/kWh) and carbon at 0.183 kgCO2e/kWh; electricity at 26.35p and the measured grid (time-mean
129 g/kWh, or the half-hourly spread for timing measures). **Where EST gives a £ figure without carbon,
the carbon is derived** by converting £ to kWh at the stated rate — marked [derived], and only as good as
the assumption that EST's price basis is close to 6.29p (EST says it averages recent and projected cap
periods). The fabric measures use EST's **2016** archived figures for a **semi-detached** house *lacking*
the measure, because those are the last EST tables giving kWh-equivalent carbon by house type: the
physical gas saving is converted to kWh at the 2016 DESNZ gas factor (0.184 — an assumption about EST's own factor, which it does not state; the implied 2016 price, 4.4–4.5p/kWh, is consistent with that year's gas rates) and then re-priced at 2025 rates. These are for a house **lacking** the measure. EST's 2016 tables give gas CO2 for GB and oil CO2 for Northern Ireland (loft, semi: 580 kg gas, 710 kg oil); only the GB gas figures are used.

| Measure | £/yr (2025) | kgCO2e/yr | Upfront | Verdict | Sources | Over 2016–2025 |
|---|---|---|---|---|---|---|
| **Loft insulation 0→270 mm** (semi) | ~£198 | 580 | £750 | **Win-win** | EST 2016 archive, gas-heated GB semi (580 kg, £140, £300; web.archive.org/web/20160614221814); EST current cost | Carbon flat (gas factor fixed); £ ×1.4 with gas price; cost ×2.5 |
| Loft top-up 120→270 mm | £17 (EST current) | 55 (EST 2016, semi) | £600 | Win-win, small | EST current; EST 2016 | as above |
| **Cavity wall** (semi) | ~£222 | 650 | £2,200 (current; £475 in 2016) | **Win-win** | EST 2016 archive (650 kg, £160; web.archive.org/web/20160615002522); EST current cost | Carbon flat; payback lengthened as cost rose faster than price |
| **Solid wall** (semi) | ~£376 | 1,100 | £12,000 internal / £15,000 external (EST current, 3-bed semi) | **Carbon-led** (payback ~30–40 yrs) | EST 2016 archive (1,100 kg, £260; web.archive.org/web/20160610164719); EST current cost | Carbon flat; cost-heavy throughout |
| **Draught-proofing** | £55 (EST current) | ~160 [derived] | ~£250 | **Win-win** | EST current | — |
| **Heating controls** (programmer, thermostat, TRVs) | £100 (EST current) | ~290 [derived] | £600 (none) / £370 (TRVs) | **Win-win** | EST *Heating controls* (updated 28 Sept 2026) | — |
| Smart thermostat | ~£33–£36 (4.5–5% of 11,500 kWh) | ~95–105 | [gap] | Win-win, small, **trial-measured** | Behavioural Insights Team, *Evaluating the Nest Learning Thermostat*, 31 Oct 2017: basic functionality ~4.5–5% of total household gas (£25–27/yr medium homes at 2017 prices); its Seasonal Savings feature a further 3.8% ±1.0% | — |
| **Thermostat down 1°C** | £120 (EST current) | ~350 [derived] | £0 | **Win-win, zero-capital** | EST current (22→21°C) | Implied kWh is 17% of TDCV gas: EST's archetype is larger than TDCV-medium |
| **Boiler flow temperature** 80→60°C | £65 at 9% … £26 at 3.6% | 190 … 76 | £0 | **Win-win if done; small as an advice campaign** | Nesta 13 Oct 2022 (modelled 9%, £112 at then prices); Salford lab 12%; Nesta's own note: compensation cuts 8%→3.6%; Nesta RCT (12 Oct 2023, ~61,000 homes): **~0.4%** per household *advised* | The field effect of advice is a tenth of the modelled effect of adoption |
| Hot-water cylinder jacket | £45 (EST, Jan 2024 prices) | ~110–135 [derived, 6–7.4p] | ~£30 | Win-win | EST *Insulating tanks, pipes and radiators* | — |
| Efficient shower head / 4-min showers | £25 / £45 (EST, includes water bills) | [gap] (energy share not separated) | low | Win-win | EST bathroom tips | — |
| **Heat pump** (ASHP, vs working gas boiler) | **−£112 to −£169** on flat cap rates (this page); EST: +£260 vs old G-rated boiler, +£330 more on HP tariff, +£105 if gas disconnected | **~1,600** (SPF 2.80); EST secondary: 1,900 vs new boiler | ~£12,000 − £7,500 BUS | **Carbon-led on flat tariffs; win-win on a HP tariff or vs an old boiler** | §4(c) | Carbon saving 46%→77%; money was worst in 2020–21 (ratio 5.7) |
| **Solar PV** (4.5 kWp) | ~£180–£1,060 (self-use share is the gap); EST 2023: £530–565 (3.5 kWp) | **~420 gross / ~260 net** (2025, average displacement); EST 2023: ~800 | ~£7,600 | **Money-led** (was much closer to carbon-led in 2016) | §4(b) | Carbon per kWp −63%; £ per self-used kWh ~×1.9 |
| **Home battery** | [gap] for battery alone; MCS Foundation (Sept 2024): ~£300/yr added to solar + heat pump | **−15 to +31 g per kWh cycled**; 2025: +7.5 (RTE 80%) to +19 (RTE 87%) g/kWh | £1,500–£10,000 (5 kWh ≈ £4,600, EST) | **Money-led; carbon ≈ neutral, negative in 2016 and 2022–23 at RTE 80%** | RTE: IEA 4E *Advancing the energy efficiency of home energy storage systems*, Feb 2025 (AC-coupled 80–95%; 87% under independent test) | Carbon value per kWh fell to ~0 in 2022 when the evening–night spread narrowed to 28 g |
| **EV** (replacing a petrol car) | electricity 2,365 kWh × 26.35p = £623 flat; petrol cost [gap] | **~1,800** saved (DESNZ well-to-wheel); battery debt repaid in ~1.5 yrs | [gap] (vehicle price is not an energy measure) | **Carbon-led for the household's energy account; large total win** | §4(a) | Saving roughly flat 1,600–1,850: cleaner grid offset by cleaner petrol cars |
| **EV smart charging** (16–19h → 00:30–04:30) | [gap]: tariff-dependent | **~85** (2,365 kWh × 36 g) | £0 with a smart charger | Win-win, small; **the one EV carbon a supplier can evidence** | §4(a), measured spread | Per-kWh value 59 g (2016) → 28 g (2022) → 36 g (2025) |
| **ToU load shifting / flex** (non-EV) | £0.01–£0.88/household-yr at measured pass-through (ceiling £51.36) | **3.6 kg per 100 kWh shifted** (2025); the shiftable kWh is R3's open question | £0 | **Neither**: small on both axes for a household without an EV or heat pump | `domestic_shift_response_as_a_function_of_pass_through.md`; measured spread | Peak-to-trough per kWh: 59 → 36 g |
| **LED** (halogen spots → LED) | £45 (EST) | **35** (EST) | low | Win-win, small carbon | EST *Lighting* | Carbon per £ falls with the grid |
| Efficient appliances | [gap]: EST gives running costs (F-rated 424 L fridge-freezer £80/yr), not a replacement saving | [gap] | — | Money-led, small carbon (electricity) | EST *Top five energy consuming appliances* | Carbon per kWh saved fell 57% |

**The timing measures at the real half-hourly spread** [measured, `sim/grid_carbon_history.py`], g/kWh
saved by moving one kWh:

| Year | Evening 16–19h → night 00:30–04:30 | Day average → day's cleanest 4 h | Day's dirtiest 4 h → cleanest 4 h | Battery, RTE 87% |
|---|---|---|---|---|
| 2016 | 58.9 | 44.7 | 87.7 | 19.0 |
| 2019 | 51.3 | 47.5 | 87.6 | 23.7 |
| 2022 | 27.6 | 40.8 | 78.3 | 2.3 |
| 2024 | 41.7 | 39.9 | 78.9 | 26.1 |
| 2025 | 36.0 | 41.3 | 81.6 | 19.0 |

Even the perfect daily timing — every flexible kWh moved from the day's dirtiest four hours to its
cleanest, every day — is worth ~80 g/kWh, **less than half of what not burning a kWh of gas is worth
(183 g)**, and the realistic shift is ~36–41 g. **Per kWh, insulation beats timing four- to five-fold, and
a household has ~4× more gas kWh than electricity kWh to work on.**

**The map, in brief.**
- **Win-win (saves both):** loft and cavity insulation, draught-proofing, heating controls, thermostat −1°C,
  flow temperature, cylinder jacket, LED, smart charging. All but LED and smart charging are **gas** measures.
- **Carbon-led:** heat pump (on flat tariffs), solid-wall insulation, EV (on the household's energy account).
- **Money-led:** solar PV (now), home battery, efficient appliances; ToU shifting is small on both.

---

## 6. What a supplier can see, and so show

The director's direction is that carbon's main job is to **show customers what they have saved and could
save**. The epistemic wall decides which "you saved X kg" statements are honest. Three classes:

| Class | Measures | What the supplier holds | What it may say |
|---|---|---|---|
| **Evidenced from its own meters** | Thermostat down, flow temperature, controls, insulation, draught-proofing, hot-water measures (as a **fall in gas kWh**); LED, appliances, solar self-consumption (as a fall in electricity import); timing measures (as a **shift in half-hourly kWh**) | Before/after meter reads; half-hourly data where smart and settled | "Your gas use fell by N kWh, weather-corrected, = N × 0.183 kg". **Attribution to a specific measure is an inference**: the meter sees the fall, not its cause. Weather correction is required, and the company has degree-day machinery in the world but must hold its own observable weather |
| **Estimable, not evidenced** | Solar export (export meter is visible under SEG, generation is not unless metered); EV avoided petrol; battery's net effect; the counterfactual for any measure | A meter that shows one side; an assumed counterfactual | "We estimate…", with the assumptions named (mileage, counterfactual car, displacement basis) |
| **Invisible** | A heat pump replacing a boiler **where the gas account closes or moves to another supplier**; a car the household no longer drives; anything in a home that has left the book | The electricity rise, if the electricity stays; **nothing on the gas side** once it closes | Only what the customer tells it. Without the gas history the supplier would book the heat pump as a **carbon increase** (more electricity) — the exact wrong sign |

Two hazards follow, both worth a control when this is built:

1. **The sign error.** A dual-fuel customer who installs a heat pump and drops gas looks, on the electricity
   side alone, like +3,400 kWh ≈ +480 kg. The true change is ≈ −1,600 kg. Any "your carbon this year"
   surface that reads electricity only will report the household's best decision as its worst.
2. **The basis error.** NESO-own-year and DESNZ-lagged-with-T&D differ by ~45% for electricity in 2025
   (135 vs 196 g/kWh). A statement must name its basis. Gas has no such ambiguity (the factor moved 0.6% in
   ten years), which makes **gas savings the most defensible carbon statement a supplier can make.**

### 6a. A part year prints no annual figure (2026-10-30)

*K8 page for the household carbon panel's leg 3 (`INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL`).*

- **What the evidence says.** A saving is shown against a whole-year baseline. CalTRACK's billing and
  daily methods take "a 365-day baseline … with no more than 37 missing days (10%)"
  (`proving_and_showing_household_savings_2026-10-25.md`, CalTRACK section) **[sourced]**. A year
  that is short by more than that is not comparable with another year, because the missing months
  are a season: a household that joined in October has a winter-only gas year.
- **What we found.** On the 209c3350ab book, 1,621 of 5,564 billed fuel-legs printed a `co2e_kg` in a
  part year (fewer than 11 months billed), and the year's total was printed on part years too (C2
  2018: 1,681.97 kg beside `full_year` false) **[measured]**. The panel's heading says "(part year)",
  but the figure in the table reads as the household's carbon for the year.
- **The design choice.** A fuel leg billed for fewer than 12 months in a calendar year prints
  `co2e_kg` null, with the reason naming the months billed. Its grid-loss line is null for the same
  reason. A year with any part-year leg prints no total. Each leg carries its own `full_year`, so a
  reader (and the row) can tell which leg made the year partial. The kWh and the months billed are
  still printed, because they are what the supplier billed and they are true for the span. The
  change between two years already refuses a part year (`household_change`).
- **Why 12 months and not 11.** The panel's existing cut (`FULL_YEAR_MONTHS`) is stricter than
  CalTRACK's 10%. A stricter cut prints fewer figures, which errs against our own thesis (F11).
- **What is not established [gap].** A whole-year figure for a household that joined or left during
  the year could be estimated by weather-normalising the months held. That needs the company's own
  degree-day observable (§7), so it is not built.

---

## 7. Gaps

- **DESNZ 2022 natural-gas factor** — both 2022 spreadsheets failed to parse (xlrd assertion). Bracketed by
  2021 (0.18316) and 2023 (0.18293); re-read from the gov.uk condensed set with another reader.
- **Gas split by end use** (space heat / hot water / cooking) for a TDCV home. The heat-pump and
  boiler-efficiency arithmetic treats all gas as heat.
- **In-situ boiler efficiency after 2009.** The EST field trial (82.5% combis) is the only measured figure
  read; the stock has changed since.
- **EST's current fabric savings by house type.** The live EST pages render savings in a calculator and
  have dropped carbon figures; cavity and solid-wall savings are no longer stated as text. This page uses
  the 2016 archive for carbon. A current kWh figure per measure and archetype is not established.
- **The archetype mismatch.** EST's measures are priced for a house *lacking* the measure (often a 3-bed
  semi). How many TDCV-medium homes lack each measure is not established here (the EPC open data in
  `docs/market_research/epc_open_data.md` is the route).
- **Solar self-consumption share** for a typical home; **EV petrol cost**; **battery-only £ saving**;
  **appliance replacement saving**; **shower measures' energy share**.
- **A GB half-hourly marginal emission factor series.** Every displacement figure here is average-basis;
  marginal would raise solar, battery and timing values — by up to 3.7× for solar if the margin were always CCGT (§4b), which is itself not established.
- **Heat-pump tariff prices** across 2016–2025, needed to say when a heat pump became win-win.
- **Persistence** of behavioural measures (thermostat, flow temperature) beyond the trial windows.
- **Weather correction** for evidencing a gas saving from meter reads: the company would need its own
  degree-day observable.

---

## 8. What this says about the order of work

The director's order is unchanged at the step level by anything here: knowledge (1), unbilled (2),
forward CLV (3), per-customer decisions (4), levers (5), forward simulation (6), comms (7). What the
evidence changes is **what is inside step 5's value-add lever, and the order of the knowledge work within
step 1**. Three proposals, each with its evidence.

**Proposal 1 — within step 5, heating measures go above flex and timing.** Evidence: on the 2025 grid a
TDCV-medium home's gas is 5.8× its electricity (§2); a kWh of gas not burnt saves 183 g against 36–41 g for
a realistically shifted kWh and ~80 g for a perfectly shifted one (§5); the win-win measures are almost all
gas measures, several are zero-capital (thermostat, flow temperature, controls), and their carbon is
**constant across the record** because the gas factor is (§5). Timing measures for a household without an
EV or heat pump are small on both axes (£0.01–£0.88/yr at measured pass-through; ~3.6 kg per 100 kWh).
The proposed merit order for next-best-action on carbon is: (1) zero-capital gas behaviour (thermostat,
flow temperature, controls); (2) cheap fabric (loft, cavity, draught-proofing); (3) heat pump, with the
supplier's own heat-pump tariff as the lever that turns it from carbon-led to win-win; (4) EV with smart
charging; (5) solar and battery, sold as money products; (6) ToU shifting.

**Proposal 2 — the carbon a customer is shown must include gas before it is shown to anyone.** Evidence:
the only live household footprint (`half_hourly_footprint.py`, published at `site/data/explore_carbon.json`)
counts ~15% of the home's carbon and would report a heat-pump installation as a carbon *increase* (§6).
This is a defect of the "absurdity fixed as a class" kind and belongs ahead of any further carbon-timing
work. The fix is small: the gas factor is already in code (`carbon_emissions.py`, once the two values are
reconciled) and gas meter reads already cross the seam.

**Proposal 3 — within step 1, add "home heating as a product" to the knowledge areas**, alongside EV, solar
and batteries. The canon names "EV, solar and batteries as products"; the evidence here says the heat pump
(+ its tariff) and fabric advice carry more carbon and as much money per customer, and they are where a
supplier's own data (its gas meter) can evidence the saving. Without this, step 5's value-add lever would
be built around the money-led products and miss the win-win ones.

Not proposed: moving heating above steps 2–4. Unbilled energy, forward CLV and per-customer decisions are
the spine the lever is judged against, and nothing here argues they stop being foundational. EP13 stays
parked; G14 (NESO's series) is sufficient for every timing figure on this page.

---

## T&D losses by reporting year, 2016-2025 (DESNZ/BEIS conversion factors)

Read directly from the official "Greenhouse gas reporting: conversion factors `<year>`" publications on
gov.uk (BEIS for 2016–2022, DESNZ from 2023), "Transmission and distribution" sheet / "Factors by
Category" sheet, row "T&D- UK electricity" / "Electricity: UK", total **kg CO2e** column (not the CO2,
CH4 or N2O sub-components). The 2021 and 2022 official `.xls` releases (flat, condensed and full sets
alike) raise a shared-string-table assertion error in standard xlrd/pandas parsers; the figures below for
those two years were recovered by patching that one tolerance check in a scratch copy of xlrd (never
touching the installed package) and cross-checked against two to three independent official files each,
which agreed exactly.

| Reporting year | kgCO2e/kWh | Source title | URL | Read from |
|---|---|---|---|---|
| 2016 | 0.03727 | Greenhouse gas reporting: conversion factors 2016 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2016 | file (flat file, "Factors by Category") |
| 2017 | 0.03287 | Greenhouse gas reporting: conversion factors 2017 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2017 | file (flat file, "Factors by Category") |
| 2018 | 0.02413 | Greenhouse gas reporting: conversion factors 2018 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2018 | file (flat file, "Factors by Category") |
| 2019 | 0.02170 | Greenhouse gas reporting: conversion factors 2019 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2019 | file (flat file, "Factors by Category") |
| 2020 | 0.02005 | Greenhouse gas reporting: conversion factors 2020 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2020 | file (flat file, "Factors by Category") |
| 2021 | 0.01879 | Greenhouse gas reporting: conversion factors 2021 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2021 | file (condensed set, "Transmission and distribution" sheet; confirmed identical in the flat file, "Factors by Category") |
| 2022 | 0.01769 | Greenhouse gas reporting: conversion factors 2022 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2022 | file (condensed set AND full set AND flat file, "Transmission and distribution"/"Factors by Category" — all three agree exactly) |
| 2023 | 0.017915 | Greenhouse gas reporting: conversion factors 2023 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2023 | file (flat file, "Factors by Category") |
| 2024 | 0.01830 | Greenhouse gas reporting: conversion factors 2024 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024 | file (flat file, "Factors by Category") |
| 2025 | 0.01853 | Greenhouse gas reporting: conversion factors 2025 | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025 | file (flat file, "Factors by Category") — matches the value already recorded on this page |

No GAPs: all ten reporting years were read directly from an official DESNZ/BEIS workbook, not from a
secondary source or an estimate.

**Caveat (from the publications' own guidance).** T&D factors are reported **separately** from the
generation factor and are additive: a consumer's full Scope-2+3 electricity footprint is "electricity
generation" (Scope 2) plus "T&D" (Scope 3, grid losses getting the power from plant to the purchaser), and
the two must not be confused with the pre-2013 combined "electricity consumption" figure. The published
factors for calendar/reporting year Y are built from UK grid data that lags by roughly **two years** (e.g.
the 2022 publication's T&D figure is described as reflecting generation-mix and loss data from around
2020), so a reporting-year label does not mean same-year grid conditions. The 2022 BEIS "major changes"
document records the T&D factor as having moved **-6% versus 2021** (consistent with the 0.01879 →
0.01769 figures read here), attributing it to a falling generation factor partially offset by increased
losses — cited here only as corroboration of the two read values, not as the source of either.
