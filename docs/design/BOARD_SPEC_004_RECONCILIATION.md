# BOARD SPEC 004 — WHOLESALE PRICE FORMATION — line-by-line reconciliation

**What this is.** A line-by-line reconciliation of every scoreable expectation in *BOARD SPECIFICATION 004 — Wholesale
price formation* (`docs/staging/BOARD_SPEC_004_PRICE_FORMATION_2026-07-22.md`, verbatim blind practitioner spec) against
**the price-formation machinery as actually built** — the merit-order engine, the weather→price chain, the forward pricer,
and the scenario/curriculum generators — read this session. Distinct from `WHOLESALE_TRADING_BOARD_RECONCILIATION_2026-07-22.md`
(Spec 001, the *desk that trades* these prices); Spec 004 is the *machinery that makes* them. Where the two converge —
above all gas-first (Spec 001 F1) — the row cites it. Each of §1–§4's requirements and all 12 battery items (§5) is an
individually scoreable, re-scoreable row; the 12-item battery joins the standing practitioner fidelity oracle alongside
Spec 001's.

**Provenance.** proposal · DISCOVER→FRAME · **doc-only** · **no level claimed**. Writes no `sim/`/`company/`/`saas/` code,
edits no `maturity_map.yaml`, no engine. It reuses (does not re-invent) the price section of
`docs/design/TRIANGULATION_WEATHER_DEMAND_PRICE_FRAME.md` §1/§4. Per the steer, conflicts between board expectation and
ratified design are surfaced as director findings, not silently resolved.

**Evidence discipline (R9 / R11, no fabrication).** Every row cites a specific file read this session (2026-07-22,
autonomous run, no network). Where a mechanism was searched and not found, the row says "not found after checking X".
ABSENT is a first-class, expected verdict — nothing is inflated. Figures quoted (MAE £32.79, R²=0.419, real-SSP tail
stats, gap-ledger numbers) are read from the named artefacts, not invented.

---

## The framing that governs every row: TWO price paths

The engine cannot be scored without this distinction, and it changes the verdict on most tail items:

1. **The HISTORICAL window (2016-03 → 2025-06), used by every production simulation phase.** The company observes the
   **real Elexon System Sell Price** through `sim/system_prices_history.py` / `company/interfaces/sim_interface.py`
   (`get_system_prices_range("2015-11-07","2025-06-07")`, read line 308-311). This is the *actual settlement record*:
   `sim/cache/elexon_ssp_full.json` carries n=168,026 periods, **2.17% negative** (min **−£185.3/MWh**), **max £4,037.8/MWh**.
   So negative prices, the scarcity hockey stick, the 2021–22 regime, fat tails, gas–power correlation, and even the
   French-nuclear-crisis GB price event are all **present by ground truth** in this window — they are the real record, not
   something the generator formed. The board's own test ("formed, not merely generated") cannot be failed here because
   nothing is generated.
2. **The GENERATIVE machinery, for BEYOND-history / Regime-3 futures.** This is where "was it FORMED?" actually bites:
   `sim/price_engine.py` (merit-order spark-spread engine), `sim/weather_price_chain.py` (W1_6, weather→price chain,
   **L3**, `level_current: 3`), `sim/forward_curve.py` (the company's forward belief), and the curriculum scenario
   generators `sim/scenario/bimodal_generator.py` + `sim/scenario/gas_scenario_generator.py`.

**Verdicts below score the machinery (path 2)** — the thing the board specifies — and flag where a MET rests on real data
(path 1) rather than on formation. Verdict legend: **MET** (a built mechanism forms it) · **PARTIALLY MET** (present but
incomplete / rests on real data not formation / wrong axis) · **ABSENT** (searched, not found) · **N/A**.

---

## §1 — The fundamental machinery

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 1.MERIT | price set by short-run cost of the most expensive unit; zero-SRMC fills first | `sim/price_engine.py::system_margin_price` | **MET** | `system_margin_price` (L131-166): residual demand `RD=demand−renewable`, `x=RD/DISPATCHABLE_CAPACITY_MW`, multiplier `A0+A1x+A2·max(0,x−X_TIGHT)^2` — a merit-order form where renewables displace down the stack and thermal sets the margin | Renewables fill first BY CONSTRUCTION (they subtract from residual); gas plant sets the margin in the middle |
| 1.SPARK | GB power ≈ gas × heat rate + carbon + margin (spark-spread arithmetic) | `price_engine.py::gas_floor_price` | **MET** | `gas_floor_price` (L110-128): `(gas + carbon·EF_GAS_TCO2_PER_MWH_TH)/thermal_efficiency` — exactly gas×(1/η heat rate) + carbon, scaled by the merit multiplier. The floor **is** spark-spread arithmetic, not a weather regression | Carbon term inactive by default (see 1.CARBON); THERMAL_EFFICIENCY=0.50 (heat rate ≈2.0), R10 |
| 1.RECON | **RECONSTRUCTIBILITY TEST (advisor flag a)** — power substantially reconstructible from gas, carbon, demand, wind on ordinary days, or it was only generated | `price_engine.py` + `weather_price_chain.py::derive_price` | **MET** | The engine literally computes `synthetic_price(gas, demand, renewable)` = `gas_floor(gas,carbon) × merit_multiplier(demand−wind−solar)` (L189-200) — reconstructible from exactly {gas, carbon, demand, wind, solar}. Fit to real SSP: **MAE £32.79/MWh, R²=0.419** (price_engine docstring L59-61) beating OLS baseline. It is FORMED, not generated | **Answers advisor flag (a): the SIM engine is gas-ARITHMETIC-led (spark spread × scarcity multiplier), NOT a weather regression.** The "weather-led" label is the front chain (weather is the exogenous driver); price is formed by spark arithmetic. Converges with Spec 001 F1 gas-first from the second direction. The COMPANY BELIEF (`weather_price_belief.py`) IS a linear regression `price~gas+temp+wind` (r²=0.926, gap ledger) — correct as a *belief*, not the generator |
| 1.NEG | high wind/mild/low-demand → prices to zero or negative; low-single-digit % of periods | `price_engine.py` (multiplier < 0) + `bimodal_generator.py` | **MET** | `system_margin_price` can fall below zero when renewables flood (x very negative), docstring L152-155 cites real SSP to −£185. `bimodal_generator.py` schedules `negative_days_per_year` 5–28 (L49, presets L74-124) calibrated to "165–1000 negative hours/year". Real record: 2.17% negative | Formed in the engine AND scheduled in the curriculum AND real in-window; frequency band credible |
| 1.SCARCITY | low wind + high demand → convex hockey stick into thousands £/MWh | `price_engine.py` convex tail; real record | **MET** | Convex tail `A2·max(0,x−X_TIGHT)^SCARCITY_EXPONENT`, A2=3.83, exponent=2.0 (L99-103); real max £4,037.8; `bimodal_generator.py` crisis-spike overlay (docstring L14) | Convexity is structural, not linear; magnitude anchored to the real tail |
| 1.NONLIN | price–load–wind surface violently non-linear: flat/negative one end, near-vertical the other | `price_engine.py::system_margin_price` | **MET** | Single multiplier is linear-below-X_TIGHT with a squared kicker above it and can pass through zero — flat/negative at high renewables, near-vertical at tight margin | The whole point of the residual-demand-scarcity form (docstring L145-160) |
| 1.CARBON | carbon price a genuine input to marginal cost (moves spreads and stack order) | `price_engine.py::gas_floor_price` carbon term | **PARTIALLY MET** | Carbon term is structurally present and unit-tested (`EF_GAS_TCO2_PER_MWH_TH=0.184`, L91) but **`carbon_price_gbp_per_tonne` defaults to 0.0 in every live call** (L77-83, L113); no real UK-ETS/EU-ETS series is wired; `weather_price_chain` leaves it at default (its R10 note L55-56) | Structure without an active input. Would advance = a time-indexed UK-ETS series (post-Jan-2021) into the chain — the module's own named R10 future work |
| 1.INTERCONNECT | interconnectors couple GB to continental prices when uncongested (the 2022 French-nuclear channel) | none | **ABSENT** | No interconnector / continental-coupling / cross-border price mechanism anywhere (`grep -riE "interconnect"` sim/ = only a docstring word in `price_engine.py:73` "interconnector import capacity" inside the fleet number, and a comment in `gas_scenario_generator.py`). The French-nuclear channel is inexpressible | First-class gap; also battery 11. In-window French events are embedded in real SSP but no mechanism forms them |
| 1.GAS.STOCKFLOW | NBP forms from pipeline + LNG + interconnector + storage + demand, priced at the margin of a global market | `sim/gas_prices_history.py` | **PARTIALLY MET** | Gas is a **real** monthly TTF-proxy series (FRED PNGASEUUSDM, `gas_prices_history.py` docstring L1-26) — a genuine priced-at-the-margin outturn, not a random draw. But it is an *ingested series*, not a *formed stock-and-flow balance*: no pipeline/LNG/interconnector/storage/demand decomposition | The gas price is real and correct in-window; formation of it from stocks and flows is absent (see 1.GAS.LNG, 1.GAS.STORAGE) |
| 1.GAS.LNG | LNG the marginal source since 2021–22, pricing GB against Asian netbacks | none | **ABSENT** | No LNG cargo / Asian-netback / global-marginal-cargo mechanism (`grep -riE "lng"` sim/ = docstring/comment words only in `gas_scenario_generator.py`). The global channel is not modelled | Matches FRAME §4 "LNG arbitrage ABSENT — the largest gap." Proposed `SPEC004_storage_flows` atom (FRAME §5) |
| 1.GAS.STORAGE | storage stocks the anxiety gauge; winter–summer spread; injection/withdrawal intertemporal curve logic | `forward_curve.py` seasonal table (belief only) | **ABSENT** | No storage stock-level state variable, no injection/withdrawal economics, no inter-temporal coupling in FORMATION. `forward_curve.py::GAS_MONTH_SEASONAL_MULTIPLIER` (L82-88) encodes a winter/summer *shape* but it is a static calibrated table in the company's forward *belief pricer*, not storage physics | FRAME §4: "point-in-time merit order with no inter-temporal storage state — the largest gap." Battery 6 |
| 1.JOINT | the same weather draw moves demand up, wind down, power gas-burn up, both prices up, *together* | `weather_price_chain.py::derive_price`; `background/coupled_triad.py` | **MET** | `derive_price` (L291-310) composes ONE (temp, wind, cloud) draw → demand (degree-day OLS) + renewable (power curve + solar) → residual → price. `cold_still_spike` (L377-395): tail 157 vs rest 72 £/MWh (**2.2×**) from ONE draw; R15-proven the coupling is causal. Coupled-triad wall enforced | The spec's central demand ("sever it anywhere and every downstream result is decorative"). Converges with Spec 001 battery item 5 (PASS). Power-sector gas-burn feedback (demand → gas price up) is *implicit* (real gas series), not a formed loop |

**§1 scoreline: 7 MET · 2 PARTIALLY MET · 3 ABSENT.**

---

## §2 — Modellable versus random, by horizon

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 2.DAYAHEAD | within-day/day-ahead substantially deterministic given weather forecast + availability | `weather_price_chain.py` (C-S2 deterministic replay) | **MET** | The chain is closed-form and deterministic (docstring L24 "all closed-form, deterministic — C-S2 replay"): given weather + gas, price is fixed. Fundamentals dominate | The deterministic-given-weather half is exactly the chain's design |
| 2.OUTAGE.SPIKE | residual randomness is forecast error + **stochastic outages**; no unplanned-outage process = a real spike driver removed | none | **ABSENT** | No stochastic unplanned-outage process anywhere; `flex_dispatch.py:46` explicitly "No availability/utilisation split." Plant availability is deterministic | Duplicate of battery 11; the board calls this "a real driver of spikes… removed" |
| 2.WEEKS | weeks–months: weather IS the randomness; price = expectation over weather + a risk premium | `weather_price_chain.py` + `forward_curve.py` | **PARTIALLY MET** | Weather-as-randomness MET (the chain's driver). But "expectation over the weather distribution **plus a risk premium**" is not formed as such — `forward_curve.py` has a term_premium (see 4.FWD.BELIEF) but it is not an integral over a weather distribution | Advance = a forward = E[spot | weather dist] + premium construction |
| 2.SEASONS | seasons–years modellable only in scenario terms, dominated by shocks no fundamental model contains (geopolitics/fleet crises/intervention) | `bimodal_generator.py` / `gas_scenario_generator.py` named presets | **PARTIALLY MET** | Scenario framing MET: named presets `baseline_2025 / central_2027 / stress_dunkelflaute_2027 / low_renewables_2027 / battery_saturation_2029` (L72-124). But the *shocks* it names — geopolitics, fleet crises, **intervention** — are absent (crisis spike is a rare tail draw, not a modelled geopolitical/intervention state) | The scenario axis is renewable-penetration, not geopolitical shock (see §3 finding) |
| 2.FWD.NOTFORECAST | **"a forward price is not a forecast"** — realised spot lands far from it; a sim where forwards predict spot has confused market with oracle | `forward_curve.py` (premium) + LAW A doctrine + real record divergence | **MET** | `forward_curve.py` = `spot_ewma × seasonal × (1+term_premium)` (L203) — a risk-adjusted expectation, forward ≠ spot. Project doctrine LAW A ("the plan/forward is not a target") and BC-1/BC-2 (FRAME §1 clause 3, §4). A pre-2021 forward vs realised 2021–22 real SSP diverges by 5–10× by construction | Structure and doctrine both present. Battery 9 partner; the *dynamics* of the premium are the gap (4.PREMIUM.DYN) |
| 2.STRUCTURAL | transition rewriting the machinery: distribution becoming bimodal, both tails growing, middle shrinking; a static model ages | `bimodal_generator.py` + `sim/renewable_capacity_trend.py` (W1_7) | **PARTIALLY MET** | Bimodal IS modelled (`bimodal_generator.py` two-regime + rising `lower_mode_fraction` 0.45→0.60 across the 2025→2029 presets, growing negatives + dunkelflaute). W1_7 adds a per-year renewable-capacity trend (`_wind_fleet_mw(p, year)`, chain L247-255). But it is **discrete presets**, not a continuously-aging distribution, and the merit-order engine's own constants (`DISPATCHABLE_CAPACITY_MW=35000`, A0–A2) are static | Battery 12 partner; the transition is represented across curriculum eras but the baseline engine is calibrated to one window |

**§2 scoreline: 2 MET · 3 PARTIALLY MET · 1 ABSENT.**

---

## §3 — Mean reversion, and when it breaks

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 3.REVERT | spot mean-reverts to marginal-fuel cost with fast half-lives; spikes collapse in days | `forward_curve.py::_ewma` (belief) + `bimodal_generator.py` overlays | **MET** | Fast local reversion is present: `forward_curve.py` EWMA half-life 30d (L106) tracks recent spot; `bimodal_generator.py` spike overlays (dunkelflaute 1–5 days, negative days single-day) revert to the regime draw. Real SSP spikes collapse in days | Fast reversion — the textbook half — is there |
| 3.JUMPMEAN | reversion is to a level that can itself JUMP — the long-run mean is a regime variable | `bimodal_generator.py` regime chain | **PARTIALLY MET** | `bimodal_generator.py` has a first-order Markov regime chain (upper gas-marginal mode vs lower renewable-depressed mode, L127-146, persistence 0.85) — the mean is not a single constant. BUT the regimes are **renewable-penetration** modes, fast-switching (~6-7 day dwell), NOT the gas-balance crisis regime that steps the level up and holds it for a year | The mean can jump *within* the renewable axis; the crisis-level jump is a rare spike overlay, not a persistent regime (the §3 finding) |
| 3.CONTAIN | **2021–22 containable-AFTER-onset, not perpetually many-sigma (advisor flag b)** — the disqualifying signature is an architecture that cannot contain the crisis once begun | real record (path 1) + `forward_curve.py` EWMA adaptivity | **PARTIALLY MET** | In-window 2021–22 is *contained by being the real record* (path 1). The forward EWMA (30d) would follow a level shift up rather than declaring it impossible → not a stationary fixed-mean architecture. BUT the *generative* machinery for beyond-history has no persistent crisis regime that holds a 5–10× level for a year — so a synthesised 2021–22 would not be first-class | Advisor flag (b): the disqualifier (crisis architecturally impossible) is AVOIDED, but the crisis is not first-class in the generator. Battery 5 partner |
| 3.STEPUP | what changed structurally: global marginal cargo; resting level AND vol stepped up; gas–power corr → unity; collateral a factor; intervention in the mechanism | `bimodal_generator.py` gas-regime conditioning | **PARTIALLY MET** | Gas is regime-conditioned to the electricity regime (`gas_scenario_generator.py` upper/lower regime means, L28-35) → a gas–power correlation channel. But "resting level and vol both stepped up" as a crisis-regime, the global-cargo step, collateral, and intervention are not modelled here (collateral → 3.COLLATERAL; intervention → 3.INTERVENTION) | Correlation channel present; the joint level+vol step-up is not |
| 3.COLLATERAL | collateral and credit became price-formation factors (distressed hedging, forced unwinds moved prices) | none (SIM-side) | **ABSENT** | No collateral/credit feedback into price FORMATION on the SIM side. (Spec 001 F2 found the company-side price-move→margin-call loop is *unwired*; there is no SIM-side distressed-hedging-moves-price channel either) | Converges with Spec 001 F2 "collateral is a cause of death." Distressed-hedging-as-price-formation is a genuine absence |
| 3.INTERVENTION | government intervention (caps, subsidies, market interventions) now part of the price state space | `company/pricing/ofgem_price_cap.py` (retail cap only) | **ABSENT** | No wholesale-market intervention (emergency caps, subsidies, interventions) in the price state space. The Ofgem cap that exists (`ofgem_price_cap.py`, Spec 001 battery 8 = FAIL, static dict) is a *retail* cap, not a wholesale-price-formation intervention | The board explicitly makes intervention "part of the state space, not outside it" — absent |
| 3.REGIMELAYER | **required architecture (advisor flag b): fast reversion + jumps with realistic decay + a regime layer where level, vol, correlations move JOINTLY** | `bimodal_generator.py` (partial regime layer) | **PARTIALLY MET** | Two of three limbs present: fast reversion (3.REVERT) + jumps (bimodal overlays). A regime layer EXISTS (Markov chain) and gas is regime-conditioned (a correlation limb). BUT level/vol/correlation do **not** move *jointly as a crisis regime* — the axis is renewable penetration (fast, cyclical), not the gas-balance crisis (slow, persistent, everything-correlates-at-once) | **Records the convergence (advisor flag b) with the director's mean-reversion-within-regime steer AND FRAME §5's proposed `SPEC004_residual_regime_process`** (Lucia–Schwartz jump-diffusion + Markov regime-switching layered on the fundamental stack). The gap: right structure, wrong regime axis |

**§3 scoreline: 1 MET · 4 PARTIALLY MET · 2 ABSENT.**

---

## §4 — Sentiment and recency: do they move prices, or only beliefs?

*The board's answer is a genuine REFINEMENT of the earlier wall-split (advisor flag c): sentiment moves REAL prices through
premium dynamics and flow-mediated channels, so premium dynamics belong SIM-side, not only company-side recency.*

| id | board_text (short) | reconciles_to | verdict | evidence | notes |
|---|---|---|---|---|---|
| 4.FWD.BELIEF | forwards ARE traded beliefs = aggregated expectation + a risk premium | `forward_curve.py::generate_forward_price` | **MET** | `forward = spot_ewma × seasonal_shape × (1 + term_premium)`, `term_premium = BASE_TERM_PREMIUM·√tenor·(risk_factor/1.2)` (L197-203); BASE=6% elec / 5% gas (L101-102). A term-structured risk premium exists | Structure present; the question is whether the premium *moves* (next row) |
| 4.PREMIUM.DYN | risk premia widen after crises, compress after calm; a constant premium through a crisis "leaves the humans out" | `forward_curve.py` term_premium (static) | **ABSENT** | `term_premium` scales only with tenor and a fixed `risk_factor` (default 1.2); it is **static** — no widen-after-crisis / compress-after-calm dynamic. The one recency input is `weather_sensitivity_multiplier` (cold-spell ×1.10, `weather_price_sensitivity.py`), a weather premium, not a fear/recency risk-premium dynamic | The board calls a constant-premium-through-a-crisis a failure. Advance = a state-dependent premium |
| 4.FLOW | the channel amateurs miss — **sentiment moves physical decisions → moves fundamentals** (fear-as-injection-demand, precautionary hedging, cargo diversion, self-scheduling) | none | **ABSENT** | No sentiment→flow→fundamental channel: no injection-demand-from-fear, no precautionary-hedging-moves-spot, no self-scheduling-against-feared-scarcity. (Requires a gas storage state to even express — see 1.GAS.STORAGE) | The board's sharpest §4 point; depends on the absent storage/flow layer |
| 4.CONVERGE | credible structure = **sentiment-inflected forwards converging onto fundamentals-dominated spot at delivery** | `forward_curve.py` (lookback) + `weather_price_chain.py` (spot) | **PARTIALLY MET** | The *convergence-onto-fundamentals* limb is structurally present: the forward EWMA lookback shrinks toward delivery and spot settles on the fundamentals chain / real SSP. But the *sentiment-inflection* limb is absent (4.PREMIUM.DYN, 4.FLOW), so it is convergence without the belief term to resolve | Half the structure ("term of belief resolving into fact") has the "fact" end but not the "belief" end |
| 4.SIMSIDE | **advisor flag c (finding): premium dynamics belong SIM-side, not only company-side recency** | FRAME §1 clause 4 wall-split | **ABSENT (recorded as Director Finding F3)** | Today ALL premium/recency lives company-side (the 120-day trailing estimator + `forward_curve.py` EWMA, FRAME §1 clause 4 "correct AS a belief"). The SIM generator has NO risk-premium/sentiment channel — it is fundamentals + regime overlays. The board argues this is a *correction*: premium dynamics move real prices and should sit SIM-side | Genuine framing correction to the triangulation steer; see Director Findings |

**§4 scoreline: 1 MET · 1 PARTIALLY MET · 3 ABSENT.**

---

## §5 — The battery (12 disqualifiers) — verdict = does the machinery AVOID the failure?

Verdict convention (matching the board): **MET** = disqualifier avoided (credible) · **PARTIALLY MET** = partly avoided ·
**ABSENT** = disqualifier present (the failure the item names is real in the build).

| # | Disqualifier (board §5) | verdict | evidence / anchor |
|---|---|---|---|
| 1 | Power unanchored from gas and carbon; not reconstructible on ordinary days | **MET** | Avoided: `price_engine.py` IS spark-spread arithmetic `(gas + carbon·EF)/η × merit_multiplier`, reconstructible from {gas, carbon, demand, wind}; MAE £32.79/R²=0.419 vs real SSP (1.SPARK, 1.RECON). *Caveat:* carbon inactive (item folds 1.CARBON PARTIAL) |
| 2 | No hockey stick; scarcity convexity/spike magnitude inside the record | **MET** | Avoided: convex tail `A2·max(0,x−X_TIGHT)^2` (1.SCARCITY); real max £4,037.8; bimodal crisis overlay |
| 3 | No negative prices, or token frequency vs low-single-digit reality **(advisor flag d)** | **MET** | Avoided: engine multiplier goes negative in oversupply; `bimodal_generator.py` schedules 5–28 neg-days/yr (calibrated 165–1000 neg-hours); real record 2.17% negative (min −£185.3). Frequency band credible |
| 4 | Wind uncorrelated with price at delivery; displacement mechanism absent | **MET** | Avoided: residual-demand displacement is the engine's core; joint tail proven from one weather draw (`cold_still_spike` 2.2×, gap ledger wind_corr 0.61); Spec 001 battery 5 PASS partner |
| 5 | Reversion to a fixed mean; 2021–22-class level shift architecturally impossible | **PARTIALLY MET** | Partly avoided: EWMA belief adapts to a level shift, bimodal has a regime Markov chain, real record contains 2021–22 → not a stationary fixed-mean architecture. BUT the persistent crisis regime is not first-class in the generator (3.JUMPMEAN, 3.CONTAIN) |
| 6 | Storage absent from gas formation; no winter–summer/injection–withdrawal logic | **ABSENT** | Disqualifier present: no storage stock state, no LNG, no inter-temporal formation (1.GAS.STORAGE, 1.GAS.LNG). The forward seasonal table is a belief shape, not storage physics. FRAME §4 "the largest gap" |
| 7 | Gaussian returns; no jumps, fat tails, vol clustering; spike decays like noise | **PARTIALLY MET** | Partly avoided: jumps + fat tails via bimodal overlays (dunkelflaute, crisis spikes, negatives) + real fat-tailed record; regime persistence gives some clustering. BUT jumps are discrete overlays without explicit realistic *decay dynamics*; no explicit vol-clustering/GARCH process (FRAME §5 proposes Lucia–Schwartz jump-diffusion for exactly this) |
| 8 | The severed joint driver — weather moves demand but not price, or prices independent of demand | **MET** | Avoided — the strongest area: one weather draw → demand + wind + residual + price, coupled-triad wall enforced (`coupled_triad.py`), R15-proven causal (1.JOINT). The shared disqualifier of Specs 001/002/004 |
| 9 | Forwards that forecast; forward=expected spot, no premium/term structure/premium dynamics; or a desk profiting reliably **(xref Spec 001 item 10)** | **PARTIALLY MET** | Partly avoided: risk premium + √tenor term structure present (`forward_curve.py`, 4.FWD.BELIEF); forward ≠ spot. BUT premium is static (no stress dynamics, 4.PREMIUM.DYN). **Cross-ref by design: Spec 001 item 10 (desk-profit alarm) = FAIL (spec-only, no code)** — the "or a desk profiting reliably" clause is not guarded |
| 10 | Flat volatility; no winter/summer vol, no rise toward delivery; far curve as noisy as prompt | **PARTIALLY MET** | Partly avoided: seasonal price *shape* present (`MONTH_SEASONAL_MULTIPLIER`, `GAS_MONTH_SEASONAL_MULTIPLIER`, winter/summer). BUT no explicit *volatility* term structure — no modelled rise in vol as delivery approaches (the term_premium grows with tenor, but that is premium not vol). Real record embeds vol clustering |
| 11 | No outage process; plant availability deterministic; French/foreign-fleet shocks inexpressible **(advisor flag d)** | **ABSENT** | Disqualifier present: no stochastic unplanned-outage process (`flex_dispatch.py:46` "No availability/utilisation split"); no interconnector/foreign-fleet channel (1.INTERCONNECT ABSENT). The French channel is inexpressible |
| 12 | Static regime; correlations/vol/level frozen at one era; the transition invisible **(advisor flag d)** | **PARTIALLY MET** | Partly avoided: the curriculum spans eras (2025→2029 presets with rising renewable fraction + growing negatives/spikes) and W1_7 adds a per-year capacity trend, so the transition is *not invisible*. BUT the merit-order engine's own correlations/vol/level constants are a single-window calibration; the joint level+vol+corr crisis regime is not modelled (§3) |

**Battery scoreline: 5 MET (1,2,3,4,8) · 5 PARTIALLY MET (5,7,9,10,12) · 2 ABSENT (6,11).**

**Recommendation (endorsing Spec 001's):** register these 12 as a **standing R15-failable practitioner fidelity oracle**,
peer to Spec 001's battery and the regulatory oracle — each verdict re-measured per run, not asserted once. Items 3, 6, 11,
12 have concrete generator audits (negative-price frequency; storage state; outage process; regime staticity) that a control
can check directly.

---

## Director findings — where the board's expectation refines or conflicts with the built design

**F1 — The reconstructibility test is PASSED, and it corrects the "weather-led" framing (advisor flag a).** The engine is
*not* a weather regression; it is **spark-spread arithmetic** (`(gas + carbon·EF)/η`) scaled by a residual-demand scarcity
multiplier — power is reconstructible from {gas, carbon, demand, wind} by construction, MAE £32.79/R²=0.419 vs real SSP.
"Weather-led" describes the exogenous *driver* of the front chain, not the price *formation*, which is gas-arithmetic. This
**converges with Spec 001 F1 (gas-first) from a second, independent direction** — the machinery reconciliation and the desk
reconciliation agree the anchor is gas. The one qualifier: the carbon limb of the spark spread is inactive (defaults 0.0),
so today it is a gas-only spark spread. **For the director:** wire a time-indexed UK-ETS series (the engine's own named R10)
so the spread is gas+carbon, as §1 requires.

**F2 — The regime layer exists but on the WRONG AXIS (advisor flag b).** §3 requires a regime layer where level, volatility
and correlations move *jointly* — the gas-balance crisis regime (slow, persistent, everything-correlates-at-once), such that
2021–22 is *containable after onset*. The build HAS a regime layer (`bimodal_generator.py` Markov chain) but its axis is
**renewable penetration** (fast-switching, ~6–7 day dwell, cyclical) with the crisis as a rare *spike overlay*, not a
persistent level+vol+corr regime. In-window 2021–22 is only "contained" because it is the real record (path 1); a
*synthesised* 2021–22 would not be first-class. This **converges with the director's mean-reversion-within-regime steer and
FRAME §5's proposed `SPEC004_residual_regime_process`** (Lucia–Schwartz jump-diffusion + Markov regime-switching on the
fundamental stack). **For the director:** does the generative price path get a gas-balance crisis regime (level+vol+corr
jointly), distinct from the renewable-penetration bimodality it already has?

**F3 — §4 is a genuine correction to the wall-split: premium dynamics belong SIM-side (advisor flag c).** The earlier
triangulation framing (FRAME §1 clause 4) placed recency/sentiment/premium wholly *company-side* as belief, and called
`forward_curve.py`'s single-regime EWMA "correct AS a belief." The board §4 argues sentiment moves **real** prices through
two channels — premium dynamics (risk premia widen after crises / compress after calm) and **flow-mediated fundamentals**
(fear-as-injection-demand). Both are absent SIM-side today: the premium is static, and no sentiment→flow→fundamental channel
exists (it would need the absent gas-storage state to express). This is not merely a company-belief gap — the board says the
SIM generator itself should carry premium dynamics and belief-becomes-flow. **For the director:** does a risk-premium /
sentiment-flow channel move onto the SIM side of the wall, converging onto fundamentals-dominated spot at delivery?

**F4 — Gas is a real INGESTED series, not a FORMED stock-and-flow balance — the largest single machinery gap.** `gas_prices_history.py`
provides a real monthly TTF-proxy (correct and priced-at-the-margin in-window), but there is no formation from pipeline /
LNG / interconnector / storage / demand, and no inter-temporal storage logic. Since the power spark spread is anchored to
gas, everything downstream inherits gas's un-formed character beyond history. Battery items 6 (storage), 1.GAS.LNG, 1.GAS.STORAGE
all trace here, as does §4.FLOW (which needs a storage state to express fear-as-injection-demand). **For the director:** the
proposed `SPEC004_storage_flows` atom (FRAME §5) — inter-temporal gas storage / LNG / interconnector state on the price path.

**F5 — Most §1 tail phenomena are MET by REAL DATA, not by FORMATION — an honest scope note, not a defect.** Negative prices,
the hockey stick, 2021–22, fat tails, gas–power correlation, even the French-nuclear GB event are all present in the
production (historical-window) path because it observes the *actual Elexon SSP record* (2.17% negative, max £4,038). The
generative machinery (path 2) is what the board's "formed, not generated" test actually scores, and it is where the gaps
above (F1 carbon, F2 regime axis, F3 sentiment, F4 gas formation, outage, interconnector) live. **Not a conflict** — but the
board should know that the battery's tail items pass *in-window by ground truth* and are only partially formed for futures.

---

## Summary scoreline

**42 scoreable expectations · 16 MET · 15 PARTIALLY MET · 11 ABSENT · 0 N/A.**

By section (MET / PARTIAL / ABSENT): §1 machinery 7/2/3 · §2 horizons 2/3/1 · §3 reversion&regime 1/4/2 ·
§4 sentiment 1/1/3 · §5 battery 5/5/2.

**The strongest area is the fundamental core** — the spark-spread arithmetic passes the reconstructibility test (F1,
converging with Spec 001 gas-first), the merit-order convexity gives the hockey stick and negatives, and the joint weather
driver (the shared disqualifier of Specs 001/002/004) is rigorously formed and R15-proven. **The weakest areas are exactly
the ends the board says a price engine is judged at:** the gas *formation* (storage/LNG/interconnector absent, F4), the
*crisis regime* (a regime layer exists but on the renewable-penetration axis, not the gas-balance crisis axis, F2), and
*sentiment/premium dynamics* (static premium, no fear-as-flow, and the board argues these belong SIM-side, F3). No stochastic
outage process and no interconnector/French channel round out the ABSENT list.

**The 3 most material gaps:**
1. **Gas is ingested, not formed (F4)** — no storage stock-and-flow / LNG / interconnector state, so the winter–summer
   spread and intertemporal curve logic (§1) and the fear-as-injection-demand channel (§4.FLOW) cannot be expressed. Because
   the power spark spread is anchored to gas, this is the load-bearing gap. Battery 6 + 1.GAS.LNG/STORAGE.
2. **The regime layer is on the wrong axis + sentiment/premium dynamics are absent SIM-side (F2 + F3)** — a bimodal
   renewable-penetration Markov chain exists, but not the gas-balance crisis regime where level, vol and correlation step up
   *jointly* and hold (§3); and the risk premium is static with no widen-after-crisis dynamic and no belief→flow channel
   (§4). Advisor flags (b) and (c) converge here.
3. **No stochastic outage process and no interconnector/French channel (battery 11 + §1.INTERCONNECT), and the carbon limb of
   the spark spread is inactive (1.CARBON)** — real spike drivers and a genuine marginal-cost input removed/omitted from
   formation; MET in-window only by the real settlement record (F5).

*All scope changes route through the WHOLESALE_VALUE_CHAIN / triangulation propose-then-proceed gate; this reconciliation is
analysis and authorises nothing to build. The 12-item battery is recommended as a standing R15-failable fidelity oracle.*
