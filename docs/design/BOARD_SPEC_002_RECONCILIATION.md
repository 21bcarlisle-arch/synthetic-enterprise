# BOARD SPEC 002 — WEATHER — line-by-line reconciliation (practitioner fidelity oracle, weather axis)

**What this is.** A line-by-line reconciliation of every scoreable expectation in *BOARD SPECIFICATION 002 — Weather*
(`docs/staging/BOARD_SPEC_002_WEATHER_2026-07-22.md`, verbatim blind practitioner spec) against **(a)** the weather
cascade as actually built in this repo (`sim/weather_engine.py`, `sim/weather_price_chain.py`, `sim/weather_demand_chain.py`,
`sim/weather_tail_demonstration.py`, `sim/weather_hdd.py`, `company/pricing/weather_normalisation_belief.py`, read this
session) and **(b)** the ratified levels in `docs/design/maturity_map.yaml` + `docs/observability/gate_authorizations.jsonl`.
Per the board's instruction and the standing triangulation steer, each of §1–§4's requirements and all 10 battery items (§5)
is an individually scoreable row that joins the practitioner fidelity oracle. It follows the reconciliation STRUCTURE fixed
by `docs/design/BOARD_SPEC_005_RECONCILIATION.md` (not re-invented) and reuses the weather findings already established in
`docs/design/TRIANGULATION_WEATHER_DEMAND_PRICE_FRAME.md` §2.

**Provenance.** proposal · DISCOVER→FRAME · **doc-only** · **no level claimed**. Writes no `sim/`/`company/`/`harness/`
code, edits no `maturity_map.yaml`, no engine, no `DIRECTOR_CANON.md`. Touches only `docs/design/`. Per the steer, conflicts
between board expectation and ratified canon/build are surfaced as **director findings, not silently resolved**.

**Evidence discipline (R9, R11, no fabrication).** Every row cites a specific file path + what was found there, read this
session (2026-07-22, autonomous run, no network). Where a thing was searched for and not found, the row says "not found
after checking X". **ABSENT is a first-class, expected verdict — nothing is inflated.** No figure, test name, or code anchor
is fabricated; numbers are quoted from the source files or the map/ledger. Where I am unsure a requirement is met I say
PARTIALLY MET and state precisely what is missing.

**Level authority resolved up front (R16 — the ledger is authority, not the map field).** The FRAME
(`TRIANGULATION_…FRAME.md` §2) flagged a C13 "L2-vs-L3" tension. Checked against `gate_authorizations.jsonl` this session:
each weather atom carries a director-console ratification entry — `W1_3 → L3` (ts 1784541430, console 2026-07-20 "RATIFIED:
W1_3 → L3"), `W1_4 → L3` (ts 1784633789, console 2026-07-21 "W1_4 → L3 RATIFIED"), `W1_5 → L3` (ts 1784641860,
"W1_5 → L3 RATIFIED"), `W1_6 → L3` (ts 1784554889, console 2026-07-20 "RATIFIED … the weather-driven price engine is
bank[ed]"), `C13 → L3` (ts 1784647184, console 2026-07-21 "C13 → L3 RATIFIED"). The map's `level_current: 3` on
W1_3/W1_5/W1_6/C13 and `3` on W1_4 are therefore **ledger-backed director ratifications, not agent self-promotions** —
the FRAME tension is resolved. (Nuance recorded honestly: those ledger rows carry `action: "LEVEL_UP_PROPOSED"`, but their
`provenance` is the director's verbatim console ratification — the console act, per R16, is the authority, not the action
label.)

---

## Reconciliation table

Verdict legend: **MET** (a built artefact proves the requirement / avoids the failure) · **PARTIALLY MET** (present but
incomplete, or the credibility-guard exists but a named piece is missing) · **ABSENT** (searched, not found; for a §5
battery item, ABSENT means the *credibility guard* is absent so the named failure is present) · **N/A**.

### §1 — The variables that matter, and why

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 1.TEMP.sovereign | temperature is the sovereign variable (space-heating driven by inside–outside gap) | W1_5/W1_6 degree-day demand | **MET** | `weather_price_chain.py` L172-177 `_hdd`/`_cdd` (base 15.5/18.0°C) + `demand_from_weather` L240-244: demand = base + b_hdd·HDD + b_cdd·CDD, OLS on real INDO/Open-Meteo, R²≈0.55 (docstring L36). Heating dominates the fitted demand response | Temperature is the primary demand driver by construction |
| 1.THERMAL.lag | thermal lag — an *effective temperature* blending today with preceding days, wind-adjusted | C13 CWV (advisor flag a) | **PARTIALLY MET** | Wind-adjustment present: `weather_normalisation_belief.py` L149-156 `_windchill_dd` = HDD·excess-wind-above-4 m/s (the CWV term), optional 4th OLS regressor L262-264. **No temporal lag / preceding-day blend**: `demand_from_weather` and `predict()` are keyed to same-day temperature only; grep of the demand/normalisation files finds no lagged or multi-day effective-temperature construction | The wind-composite half exists; "yesterday's cold in today's walls" (multi-day effective temperature) is absent — advance = a lagged/EMA effective-temperature input (see Director Findings F1, battery item 3) |
| 1.NONLIN.hockey | non-linear hockey stick — flat above ~14–16°C, steep below, steeper in deep cold | degree-day HDD/CDD kink | **PARTIALLY MET** | Piecewise-linear kink present: `_hdd` floors below 15.5°C, `_cdd` above 18°C (`weather_price_chain.py` L172-177) → flat summer, linear-steep winter. **No deep-cold steepening**: the relationship is a single linear slope below the base; no second kink / convex cold-tail / secondary-heating term found | Basic hockey stick met; the "steeper still in deep cold" tail is a single-slope approximation — advance = a convex or multi-segment cold-tail term |
| 1.WIND.demand | wind chill raises heating demand at any given temperature | C13 CWV term | **PARTIALLY MET** | `_windchill_dd` term exists and is fitted, not fabricated. But on the real record the coefficient fitted **NEGATIVE** (b_windchill ≈ −23.1, C13 map simplification 2026-07-21) — GB cold spells are anticyclonic/still, so real cold-and-windy days are a milder regime | The demand-side wind term is real but weak/negative in GB — this is correct physics, not a defect (Director Findings F6); advance = keep the term, register the sign as the honest finding |
| 1.WIND.price | wind *generation* displaces gas and moves price the other way; both doors from the same draw | W1_6 price chain | **MET** | `weather_price_chain.py` L266-278 `wind_output_from_speed` = fleet · turbine power curve → L313-324 `residual_demand` = demand − wind − solar → `synthetic_price` (merit order). One `(temp, wind, cloud)` draw drives both demand and generation (L291-310 `derive_price`) | Both doors swing from one draw — strongest §1 row; ties to battery item 8 |
| 1.SOLAR | solar irradiance & daylight shape the electricity profile; solar gains offset heating | engine half-hourly + W1_6 solar | **PARTIALLY MET** | Solar modelled: `weather_engine.py` L281-296 astronomical clear-sky irradiance × cloud attenuation (half-hourly); `weather_price_chain.py` L281-288 solar generation. `simulation/demand_model.py` subtracts `solar_generation` (per FRAME §3). **But no daylight/lighting load term**: demand is temperature-only, "no explicit daylight/working-day term" is a registered R10 simplification (`weather_price_chain.py` L52-54) — the winter-evening-peak-as-daylight phenomenon is absent | Irradiance/generation modelled; the demand-profile daylight/lighting shape is a registered gap — advance = a daylight/lighting load term |
| 1.PRECIP | precipitation & humidity minor — may be honestly omitted *provided the omission is registered* | engine MACRO_VARS | **PARTIALLY MET** | `weather_engine.py` L59 `MACRO_VARS = [temperature, wind, cloud]` — precipitation/humidity not modelled. Precipitation *is* ingested (`weather_ingestor.py` maps `precipitation_sum → precipitation_mm`) but dropped by the engine; humidity not ingested. **The omission is not registered as an explicit simplification** in the engine's R10 notes | Omission is honest but implicit — advance = a one-line registered R10 simplification naming precip/humidity as deliberately omitted |

### §2 — Spatial structure

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 2.REGIONAL.zones | regional distribution zones, each with its own composite from designated stations | W1_4 regional field | **PARTIALLY MET** | `weather_engine.py` L200-238 Pass 2 fits a Cholesky cross-location covariance over per-location deviations, physically bound to the national front. **But keyed to only 4 hand-picked calibration points** (C1-C4 = London/Manchester/Glasgow/Cotswolds, `weather_tail_demonstration.py` L84), *not* GB's 14 DNO licence areas or GSP groups; W1_4 map note (2026-07-16) confirms "zero of the real-UK-region grounding (partition, weights) exists" | A spatial-deviation field exists but not real regional distribution zones — advance = map to DNO/GSP partition with demand weights (W1_4 L2→L3 named remainder) |
| 2.NATIONAL.composite | population-weighted national composite (adequate for a nationally-spread book) | engine Pass 1 national signal | **PARTIALLY MET** | `weather_tail_demonstration.py` L143-146 `load_national_daily`: national = **unweighted mean** of the 4 locations (`np.mean([...], axis=0)`), not population-weighted | A national composite exists but is a simple 4-station mean, not population-weighted — advance = population/demand weights on the composite |
| 2.SPATIAL.corr | spatial correlation high but not perfect; a single-station model gets aggregate variance wrong | W1_4 aggregation-consistency | **MET** | `weather_engine.py` Pass 2 preserves the real cross-location correlation (W1_4 map note: reproduced "to max abs error 0.026") rather than collapsing to one station; aggregation-consistency holds to ~1e-4 (`tests/sim/test_weather_regional_field.py`, R15 mutation-proven). The regional field is *not* a single-station collapse | The variance-diversification mechanism exists (though on 4 points); the requirement to not be single-station is met |
| 2.WIND-vs-homes | the weather driving wind *generation* is not the weather at the *homes* — collapsing both manufactures correlation | W1_6 wind link | **ABSENT** | `weather_price_chain.py` L303-304, L322: wind generation uses the **same national `wind_speed_ms` series** that drives household demand — there is no separate northern/offshore wind-site weather. Wind-fleet output and demand are driven by one national wind draw | The exact §2/battery-6 failure: home-weather and wind-site-weather collapsed to one series; the diversification the real system lacks is instead manufactured *present*. Advance = a distinct wind-site weather series (Director Findings F2) |
| 2.KNOW-simplification | a national simplification is legitimate only if the model *knows* it and registers what it suppresses | R10 simplification register | **PARTIALLY MET** | Some simplifications registered: `weather_price_chain.py` L49-58 R10 block (solar proxy, temperature-only demand, single wind-fleet scalar). **But the wind-site≠home collapse (2.WIND-vs-homes) and the suppressed aggregate-variance diversification are not registered** | Registration is partial — advance = register the wind-location collapse and the variance it suppresses |

### §3 — Persistence, seasonality, extremes, trend

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 3.PERSISTENCE | synoptic systems lasting days, blocking patterns lasting weeks; duration, not depth, drains storage | future generator (advisor flag c) | **PARTIALLY MET** | Generator has day-to-day persistence: `weather_engine.py` L179-183 AR1 (`resid[t] = phi·resid[t-1] + innovation`), phi fitted per variable; half-hourly wind is a discretised OU process (L299-308). Multi-day spells producible: `weather_tail_demonstration.py` envelope reaches the real Dec-2022 7-day worst week (map: envelope max 1.75 ≥ real 1.45). **But no explicit multi-week blocking-high regime**: W1_3's DoD "latent BLOCKING-HIGH weather regime (hidden-Markov/persistence state)" was *not* built — the map records the fix as a *season-conditioned covariance*, calendar-determined, not a persistence regime; `reach_fraction` only 12–32% (a gap-1 signal the engine under-produces tail *frequency*) | AR1 persistence + envelope-reaches-real avoid the "independent daily draws" disqualifier, but week-scale blocking and tail frequency are the honest gaps — this is battery item 1 |
| 3.COMPOUND | still-and-cold — winter temp & wind correlated in the dangerous direction; "the most important number" | W1_3 season-conditioned covariance | **MET** | `weather_engine.py` L133-163: innovation covariance fitted **conditionally on season** — cold-season (Dec-Feb) cov carries the measured +0.53 winter temp/wind coupling vs +0.18 outside (L94-105, L133-147); `simulate_national_macro` L176-181 selects it by actual calendar season. Validated: simulated winter D1 decile lift **2.875, within the real block-bootstrap CI [1.54, 3.38]** (map, was ~1.77 with a single all-year cov); marginals preserved | The single most important correlation is built and mutation-validated — strongest §3 row (battery item 2). Advisor flag (a) agreement recorded in F6 |
| 3.INTERANNUAL | interannual variability large — winter-to-winter swings move annual heating demand high single digits | future generator | **PARTIALLY MET** | The AR1 process produces some year-to-year variation via accumulated residual draws, but it **mean-reverts to the same fitted seasonal climatology each year** (`weather_engine.py` L187 seasonal + resid); no large-scale-pattern (NAO-class) interannual driver found, and the interannual variance magnitude is **not measured/verified** against the observed high-single-digit swing | Some interannual variance exists but is not calibrated/verified to the observed magnitude — battery item 10; advance = measure simulated winter-to-winter demand swing vs real |
| 3.TREND | the warming trend is real and must be carried, but must not delete the extremes | seasonal model / normals | **ABSENT** | `weather_engine.py` L68-91 fits seasonal harmonics on `day_of_year` only — **no year/trend term**; the 2016-2025 climatology is stationary. Normalisation reference is fixed & untrended: `weather_hdd.py` L17-30 `REFERENCE_MONTHLY_HDD` = Met Office **1991-2020** normals, no re-base schedule | No warming trend anywhere in generator or normalisation — the "trend that thins extremes" opposite failure is N/A because there is no trend at all. Material (Director Findings F3, battery item 7) |

### §4 — What "weather-normalised" must mean (three questions + same basis for three masters)

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 4.Q1 | normal relative to what? — a stated reference climatology, trend-adjusted, re-based on a schedule | C13 baseline + weather_hdd normals | **PARTIALLY MET** | A reference is stated: `weather_hdd.py` L15-30 1991-2020 Met Office HDD normals; C13 g0 baseline = climatological-mean no-skill (map, 2026-07-21). **But untrended and no re-base schedule** — exactly the "untrended 30-year average is systematically cold" bias §4.Q1 warns of | Reference exists and is stated but untrended/un-rebased — advance = trend-adjust the normal + a stated re-base schedule (couples to 3.TREND) |
| 4.Q2 | adjusted through what sensitivity? — a fitted demand–weather curve, per fuel/segment, non-linearity respected, not a flat scalar | C13 fit + weather_hdd factor | **PARTIALLY MET** | Fitted-curve path meets it: `weather_normalisation_belief.py` `fit_weather_normalisation_belief` is closed-form OLS on HDD/CDD[/CWV], respecting the kink (not a flat scalar). **But two problems**: (i) `weather_hdd.py` L78-88 `get_weather_factor` is a **flat actual/reference HDD ratio clipped [0.3, 2.0]** — the flat scalar §4.Q2 rejects, still live; (ii) not per-fuel/segment — `book_weighted_temperature` (regional) is built but unwired to the real-record triad (C13 map note) | Fitted curve good; flat-ratio path and per-segment absent — advance = retire/reconcile the flat scalar (F5), wire per-book sensitivity |
| 4.Q3 | carrying what error? — the residual error propagates into hedge volumes; not treated as exact | C13 + coupled triad gap | **PARTIALLY MET** | The belief carries `r2`/`n_train` (dataclass L159-178) and the coupled triad **measures** the belief-vs-truth gap (`coupled_gap_ledger.json#W1_5_premise_demand_shape` present; population gap ~0.66, cold_windy_tail worst cell). **But no propagation of that residual error into hedge volumes / performance measurement** as an explicit error band found | Error is measured as the gap but not propagated into hedge volumes — advance = carry the normalisation residual as a volume error band |
| 4.SAME-BASIS | the *same* basis must serve hedge-volume-setting, forecast-evaluation, and management reporting | NEW (advisor flag d) | **ABSENT** | No single normalisation basis demonstrably serving all three masters found. C13 is the demand belief; a shared basis feeding hedge volume + forecast eval + management reporting is not wired (grep of company pricing/reporting for a shared normalisation basis = none) | First-class new requirement (advisor flag d) — advance = one canonical normalised-demand basis consumed by all three (Director Findings F4) |

### §5 — The battery (a weather system is NOT credible if…) — verdict = does the build AVOID the failure

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 7.1 | independent daily draws — no persistence, no synoptic structure, no multi-day spells | 3.PERSISTENCE (flag c) | **PARTIALLY MET** | AVOIDS the disqualifier: AR1 persistence (`weather_engine.py` L179-183) + the show-the-tail envelope reaches the real 7-day worst week. But no multi-week blocking regime; `reach_fraction` 12–32% under-produces tail frequency | Not disqualified, but week-scale blocking + frequency are gaps — see 3.PERSISTENCE |
| 7.2 | temperature & wind independent in winter — the still-and-cold compound tail missing/thin | 3.COMPOUND (flag a) | **MET** | Season-conditioned covariance carries the +0.53 winter temp/wind coupling; sim winter D1 lift 2.875 in real CI [1.54, 3.38] (`weather_engine.py` L133-163). Mutation to a single all-year cov drops it to ~1.77 and fails | The joint tail is built and mutation-validated |
| 7.3 | instantaneous response only — no thermal lag, no effective-temperature construction | 1.THERMAL.lag | **ABSENT** | Demand is keyed to same-day temperature; grep of demand/normalisation files finds no thermal-lag or multi-day effective-temperature construction (the CWV wind term exists but is not a temporal lag) | The failure is present — the industry's effective-temperature blend is not built (Director Findings F1) |
| 7.4 | a linear demand–temperature relationship — no hockey stick | 1.NONLIN.hockey | **PARTIALLY MET** | AVOIDS pure linearity: HDD/CDD kink gives flat summer / steep winter (`weather_price_chain.py` L172-177). But a single slope below the base — no deep-cold steepening | Hockey-stick kink present; cold-tail convexity absent |
| 7.5 | tame extremes — worst fortnight milder than history; no Dec-2010/2018-class event producible | W1_3 show-the-tail | **MET** | `weather_tail_demonstration.py`: over 25 seeded sims the engine's worst winter week envelope reaches the real worst (Dec-2022, severity 1.45; envelope max 1.75); `assert_tail_not_smoothed` (L289-303) FIRES on a smoothed engine (R15 both directions) | Extremes are not tamed; caveat = reach_fraction 12–32% (frequency, reported not gated) |
| 7.6 | one point for everything — a single series driving demand AND generation, simplification unregistered | 2.WIND-vs-homes | **PARTIALLY MET** | The national-composite simplification is board-permitted *if registered*; some R10 registration exists (`weather_price_chain.py` L49-58). But wind-generation and demand run off **one national wind series** (L303-304) and that specific collapse + its suppressed variance are **not registered** | The collapse is present and only partly registered — the sharpest half of this is 2.WIND-vs-homes ABSENT (F2) |
| 7.7 | no trend, or normals fixed forever — or the opposite (a trend that thins extremes) | 3.TREND | **ABSENT** | No warming trend in the generator (`weather_engine.py` harmonics on day-of-year only) and fixed untrended 1991-2020 normals (`weather_hdd.py` L15-30). The "normals fixed forever" failure is present; the opposite (trend-thins-extremes) is N/A (no trend) | Trend absent (F3) — note this is the *first* failure of item 7, not the second |
| 7.8 | weather moves demand but not price (or price but not demand) — one draw must drive both | W1_6 + coupled triad (flag b) | **MET** | One coherent weather draw drives both: `weather_price_chain.py derive_price` (demand + wind/solar → residual → merit-order price). **R15/shared-draw proof**: `tests/sim/test_weather_price_chain.py` L118-137 — cutting the demand-temp link AND wind collapses the cold-still spike ratio (map: 2.18→1.23; test asserts `spike_ratio < 1.35` and a ≥0.7 drop). Coupled triad wired `W1_6 → C13` (`background/coupled_triad.py` L91), gap in `coupled_gap_ledger.json#W1_6_physics_price_signal` | Claim MET with the R15 shared-draw proof cited (advisor flag b satisfied) — one draw drives both doors |
| 7.9 | "weather-normalised" without a stated basis — no reference climatology, no fitted sensitivity, no error carried | §4 Q1–Q3 | **PARTIALLY MET** | AVOIDS the bare failure: C13 has a fitted sensitivity (OLS degree-day), a stated 1991-2020 reference, and a measured gap (error). But the basis is untrended (4.Q1), the flat-scalar path co-exists (4.Q2), and the error is not propagated to hedge volumes (4.Q3) | Not a bare failure but incomplete across all three questions |
| 7.10 | every winter average — interannual variance absent; annual demand swings suspiciously small | 3.INTERANNUAL | **PARTIALLY MET** | AR1 residual draws give some winter-to-winter variation, but mean-revert to one fixed climatology and the magnitude is unmeasured/unverified against the observed swing | Some variance present, magnitude unverified — see 3.INTERANNUAL |

---

## Director findings — where the board's expectation conflicts with the build or reveals an honest gap (flag, do not resolve)

**F1 — Thermal lag / effective-temperature composite is absent (§1 THERMAL.lag, §5 item 3).** The board's veteran "demands
immediately" an effective temperature blending today with preceding days ("yesterday's cold is still in today's walls").
The build keys demand to **same-day** temperature (`weather_price_chain.demand_from_weather`,
`weather_normalisation_belief.predict`). C13 added the *wind-adjustment* half of the industry composite (the CWV
`_windchill_dd` term) but **not the temporal-lag half**. This is the industry mechanism the board says "was corrected for
decades ago." Advisor flag (a) verified: the composite is indeed C13's territory, and C13 has built the wind term but not
the lag. **For the director:** is a lagged/EMA effective-temperature input an L3→L4 refinement on W1_5/C13?

**F2 — Home-weather and wind-generation-weather are collapsed to one national series (§2 WIND-vs-homes, §5 item 6).** The
board is explicit: "the weather that drives wind generation is not the weather at the homes… collapsing both to one series
manufactures a correlation the real system does not have." `weather_price_chain.py` drives both national demand and wind-fleet
output from the **same** `wind_speed_ms` national series. This is a genuine structural gap AND it is not registered as a
simplification. It is the sharpest spatial finding — and it interacts with 3.COMPOUND: the built cold-and-still coupling is
partly *because* one wind series serves both roles, so the joint tail may be partly an artefact of the collapse rather than
independently earned. **For the director:** does a distinct wind-site (northern/offshore) weather series enter W1_6, and how
does that reconcile with the validated cold-still price spike?

**F3 — No warming trend anywhere; normals are fixed and untrended (§3 TREND, §4 Q1, §5 item 7).** The generator's climatology
is stationary over 2016-2025 (`weather_engine` harmonics carry no year term) and the normalisation reference is the fixed
1991-2020 Met Office HDD normals (`weather_hdd.py`) with no re-base schedule. The board calls carrying the trend a
requirement ("seasonal normals drift warmer… the industry periodically re-bases"), and §4.Q1 warns an untrended normal
"is systematically cold against the current climate and will bias every volume forecast high." This is a **direct volume-bias
risk** into hedge sizing. **For the director:** is a warming-trend term (generator) + a trend-adjusted re-based normal
(normalisation) an R13 baseline-fidelity change?

**F4 — Same-basis-for-three-masters is absent (§4 SAME-BASIS, advisor flag d).** No single normalisation basis is
demonstrably shared across hedge-volume-setting, forecast-evaluation, and management reporting. The board's Doer warns
that otherwise "the company will hedge one number, measure itself against a second, and report a third." This is a new
requirement on C13's remit — currently C13 is the demand belief but its output is not wired as the *one* basis three
consumers read. **For the director:** does one canonical normalised-demand basis become the single source for hedge/forecast/
reporting?

**F5 — Two co-existing normalisation methods, one of which is the flat scalar the board rejects (§4 Q2).** C13's
`fit_weather_normalisation_belief` is a fitted degree-day curve (good), but `sim/weather_hdd.py::get_weather_factor` is still
a **flat actual/reference HDD ratio clipped [0.3, 2.0]** — precisely the "restated by a flat scalar" the board says §4.Q2
must not be. These two normalisation paths co-exist unreconciled (echoing the W1_6 DISCOVER finding of three uncoordinated
price mechanisms). Not a canon conflict — a straightforward reconcile-or-register. **Advance:** retire the flat scalar into
the fitted-curve path, or register `weather_hdd.get_weather_factor` as a legacy gas-billing scalar distinct from the C13
normalisation basis.

**F6 — Recorded agreement (NOT a conflict): the board's still-and-cold and C13's negative-fitted wind-chill are the SAME
phenomenon (advisor flag a).** The board's §1 asks for a wind-chill demand uplift AND (battery 2) a still-and-cold compound
tail. On the real GB record C13's wind-chill coefficient fitted **negative** (b_windchill ≈ −23.1) because — as
`weather_demand_chain.py` L73-90's own docstring states — GB cold spells are anticyclonic and **still**, so cold-and-windy
days are a milder, rarer regime (only ~3 deep-corner days). The board and the data **agree**: cold arrives with stillness.
The consequence worth recording: the *demand-side* wind-chill uplift the board's §1 names is real but WEAK in GB precisely
because cold days are calm, while the *price-side* cold-and-still spike (7.2/7.8) is STRONG. The negative-fitted CWV term is
therefore correct physics reported honestly (R12, not tuned), not a defect — the two board asks pull in the same direction,
they do not conflict.

**F7 — Level authority confirms, does not conflict.** Recorded for completeness: the FRAME's C13 "L2-vs-L3" tension is
resolved by the ledger (all five atoms director-console ratified to their map levels — see header). No conflict; the map is
ledger-backed. Flagged only because the FRAME left it open.

---

## Summary scoreline

**30 scoreable expectations · 7 MET · 18 PARTIALLY MET · 5 ABSENT · 0 N/A.**

By section (MET / PARTIAL / ABSENT): §1 variables 2/5/0 · §2 spatial 1/3/1 · §3 persistence/seasonality/extremes/trend
1/2/1 · §4 normalisation 0/3/1 · §5 battery 3/5/2.

**The strongest area is the coupled cold-and-still physics** — the season-conditioned temp/wind covariance (3.COMPOUND /
7.2, sim D1 lift 2.875 in the real CI), the show-the-tail envelope reaching the real Dec-2022 worst week (7.5), and the
one-draw-drives-both-demand-and-price chain with its R15 shared-draw proof (1.WIND.price / 7.8). These are built,
mutation-validated, and ledger-ratified to L3. **The weakest areas are the temporal and normalisation-discipline dimensions**
the board weights heavily.

**The 3 most material gaps:**
1. **No thermal lag / effective-temperature composite (F1, §1 THERMAL.lag, 7.3 ABSENT)** — demand is keyed to same-day
   temperature; the industry's preceding-days blend is absent. C13 built the wind half of the composite but not the lag half.
2. **No warming trend anywhere and fixed untrended normals (F3, §3 TREND + §4 Q1, 7.7 ABSENT)** — a direct, systematic
   volume-forecast-high bias into hedge sizing; the board makes carrying the trend (without thinning the extremes) a
   requirement.
3. **Home-weather and wind-generation-weather collapsed to one national series (F2, §2 WIND-vs-homes, 7.6)** — the build
   manufactures a correlation the real system lacks and does not register the collapse; and **same-basis-for-three-masters
   is absent (F4, §4)** — no single normalisation basis serves hedge/forecast/reporting.
