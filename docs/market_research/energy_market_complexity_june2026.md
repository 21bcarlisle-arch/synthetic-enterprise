# Energy Market Complexity — Research Findings for Scenario Generation

**Date:** 2026-06-21  
**Sources:** Wikipedia 2021 UK gas crisis; NESO FES 2025; SQ Energy; Future Change; NextEnergy Capital; Modo Energy; Oxford Review of Economic Policy; House of Commons PAC; Ofgem FRC transparency report 2025; RAP gas network analysis; The Conversation heat pumps; ScienceDirect electrification; UK Gov EV Smart Charging Action Plan; Storelectric dunkelflaute; Wood Mackenzie; arXiv renewable stress; OIES LNG; Bloomfield/CCC stress scenarios 2025.

---

## 1. The 2021-22 Non-Linear Crisis: Anatomy of a Cascade

The crisis was non-linear because five distinct feedback loops amplified an initial commodity shock into systemic market failure.

**The storage-hedging failure loop.** Rough storage (70% of UK capacity) closed by Centrica in 2017. UK entered 2021 with weeks not months of gas buffer. NBP rose 400% between early 2021 and September 2021; gas spiked 70% in September alone to 180p/therm. Suppliers with <6 months forward hedging faced instantaneous cost exposure with no price cap relief (cap was set quarterly, lagging market by months — this "cap-to-cost gap" was the direct cash destruction mechanism).

**The hedging-asset contamination loop.** Failed supplier's positive-value hedges went into the insolvent estate — unavailable to the SOLR. SOLR acquired customer books without the hedges, had to buy at spot. 29 suppliers failed, affecting ~4 million households. SOLR recovery mechanism: 15-month minimum lag before levy payments arrived — acquiring suppliers fronted wholesale costs with no income recovery.

**The SOLR mutualization-tariff loop.** SOLR costs recovered via levies hit all consumers through standing charges: ~£2.7bn total, ~£94/household. This increased the energy cost burden, adding to demand destruction on top of commodity prices.

**The regulatory capital void.** Ofgem had no meaningful capital adequacy requirements pre-crisis. Most failed suppliers had insufficient capital to absorb even minor losses. Post-crisis: minimum £115 adjusted net assets per dual-fuel-equivalent customer (confirmed vs our £130 figure — possible different measurement conventions); ringfencing of RO balances mandated.

**Simulation implication:** A realistic stress scenario must model:
1. The cap-lag mechanism (suppliers carrying MTM losses on unhedged positions while capped tariffs prevent revenue recovery)
2. The SOLR cascade (each failure increases acquiring-supplier capital strain)
3. The delayed levy recovery (15-27 months to cash settlement)
This is a state-dependent contagion model, not a simple price-up scenario.

---

## 2. "As Yet Unseen" Scenarios in NESO FES 2025

NESO FES 2025 (published October 2024, first as independent public corporation) defines "Electric Engagement" vs. "Holistic Transition" scenarios. Key numbers:
- Electricity demand range: 540–646 TWh by 2050 (up from FES 2024's 458–550 TWh)
- 2030 demand ramp faster than 2024 projections
- Solar: 56–62 GW by 2035 (range narrowed from 42–69 GW in FES 2024 — much higher certainty)
- EVs: potentially 51 GW of grid flexibility by 2050 (exceeds current gas generation capacity)
- At 70%+ renewables: bimodal/fat-tailed price distribution replaces Gaussian (very low/negative during surplus; very high during wind droughts)

**Dunkelflaute + interconnector loss scenario.** January 2025 event: localized dunkelflaute, wind fell to 2 GW by Jan 8, NESO bought back exports from Nemo/BritNed/Viking simultaneously, wholesale prices hit £1,040/MWh around 13:00 on Jan 5. Wood Mackenzie analysis: correlated dunkelflaute risk (UK/France/Belgium/Netherlands share similar weather patterns and have correlated renewable generation profiles). If all experience simultaneous renewable drought, interconnectors provide no rescue.

---

## 3. Renewable Intermittency and Negative Price Dynamics

**Current trajectory (GB negative pricing):**
- Negative price hours: 29 (2022) → 107 (2023) → 149 (2024, "historic high") → 17 consecutive hours May 2025
- 2025 projected to set another record; 2027 is the projected peak (~1,000 hours/year)
- Curtailment costs: >£1.5bn/year; ~25% to wind farms paid to switch off; GB curtailment +22% YoY to 10 TWh
- REGOs provide a rough floor around −£5/MWh

**The 2027 inflection point (Modo Energy):** CfD-backed generators are price-insensitive (receive strike price regardless), causing negative-price amplification. Post-2027, as more unsubsidized merchant capacity is built, those generators respond to price signals and self-curtail — negative-price frequency projected to decline. Regime change: two distinct market phases.

**At 70%+ renewables (academic research):** Temporal price volatility decreases up to ~40% penetration (averaging out fossil fuel spikes), then sharply increases above 40–50% (oversupply creates extreme lows; wind/solar droughts create extreme highs). Mean price compressed, variance exploding. "Price cannibalization": wind capture price diverges increasingly from baseload, undermining merchant project economics.

**Geographic bottleneck:** Wind in Scotland/North Sea; demand in southern England. North-south transmission constraints force negative pricing in north even when southern prices are positive — locational basis risk not captured in a single-price simulation.

---

## 4. The Electrification of Heat

Current: ~25M gas boilers; heat pump penetration 1–2%. Government target: 600,000 installations/year by 2028; net-zero trajectory requires 1.6M/year by 2035.

**Gas demand impacts:** Full heat pump penetration eliminates ~80–90% of residential gas demand (heat pumps +61% electricity demand, nearly eliminating gas for heating, operating at 3–4× boiler efficiency).

**Electricity peak load reshaping:** Full heat pump adoption can increase winter evening peak demand by >100% above current levels. At 50% penetration in terraced homes (poor insulation, high heat demand), evening peak demand could exceed 100 kWh from ~68 kWh baseline.

**Network reinforcement cost:** 5.7M heat pumps by 2035 → reinforcement of 42% of distribution network → £40.7bn cost.

**Gas network death spiral (RAP analysis):** Gas transmission/distribution network has ~£8bn decommissioning costs and assets depreciated over 45-year timelines to 2077. As customers disconnect, fixed costs shared across shrinking base → transportation charges per remaining customer rise → additional incentive to disconnect. Estimated stranded assets: £3–4bn by 2050. Remaining gas users (disproportionately lower-income) face escalating bills. Government expected to decide on gas grid future by 2026.

**Simulation implication:** Gas/electricity interaction is bi-directional. A simulation treating them as independent misses the cross-commodity feedback.

---

## 5. EV Smart Charging and the Overnight Load Profile

Government: ~10M EVs with zero tailpipe emissions by 2030.

**Without smart charging:** 1M EVs charging 6–10pm → +7 GW to peak demand.
**With smart charging:** Same 1M EVs → <1 GW additional overnight. The difference is 7×.

**V2G (Vehicle-to-Grid):** NESO projects EVs providing 51 GW of flexibility by 2050 — largest flexibility asset in the system. V2G transforms the overnight trough into an asset: EVs absorb surplus renewable generation, then discharge into evening peaks.

**The behavioral bifurcation:** Two scenarios with the same EV count produce radically different load profiles. UK gov's 2021 EV Smart Charging Action Plan mandates smart-charging capability but cannot mandate participation. If EV owners prefer convenience charging (plug in when home, ignore price signals), the flexibility benefit evaporates.

---

## Key Numbers for Simulation Parameterization

| Parameter | Current | 2030 | 2035/2050 |
|---|---|---|---|
| Negative price hours/year | ~149 (2024) | ~1,000 (projected peak ~2027) | Declining as merchant capacity grows |
| UK renewable capacity (GW) | ~56 GW | 161 GW (FES target) | 309 GW (FES 2050 high) |
| EVs on UK roads | ~1–2M | ~10M | — |
| EV flexibility potential | — | — | 51 GW (2050) |
| Heat pump penetration | ~1–2% | 600K/yr target | 1.6M/yr for net zero |
| Gas network stranded assets | — | — | £3–4bn by 2050 |
| Curtailment cost | >£1.5bn/year | Increasing | — |
| Winter peak increase (full HP) | Baseline | +100%+ possible | — |
| SOLR cost (2021-22 crisis) | £2.7bn (~£94/household) | — | — |
| Supplier failures (2021-22) | 29 suppliers, 4M customers | — | — |
| Negative price regime change | 2027 projected peak | Decline post-2027 | — |
