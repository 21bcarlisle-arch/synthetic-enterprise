# BOARD SPEC 003 — HOUSEHOLD DEMAND — line-by-line reconciliation

**What this is.** A line-by-line reconciliation of every scoreable expectation in *BOARD SPECIFICATION 003 —
Household demand* (`docs/staging/BOARD_SPEC_003_HOUSEHOLD_DEMAND_2026-07-22.md`, verbatim blind practitioner
spec) against the demand model **as actually built** — the `W1_5_premise_demand_shape` premise-demand
machinery, the meter unhappy-path physics, the population/segmentation draw, and the life-events engine, all
read this session. Each of §1–§4's requirements and all 11 battery items (§5) is an individually scoreable,
re-scoreable row; the domain "NOT credible" battery joins the standing practitioner fidelity oracle established
by Spec 001. Companion to `BOARD_SPEC_005_RECONCILIATION.md` (same structure) and the prior
`TRIANGULATION_WEATHER_DEMAND_PRICE_FRAME.md` §3 (reused, not re-invented).

**Provenance.** proposal · DISCOVER→FRAME · **doc-only** · **no level claimed**. Writes no `sim/`/`simulation/`/
`company/`/`saas/` code, edits no `maturity_map.yaml`, no engine, no `DIRECTOR_CANON.md`. Touches only
`docs/design/`. Per the steer, **conflicts between board expectation and ratified state, and honest gaps, are
surfaced as director findings, not silently resolved.**

**Evidence discipline (R9/R11, no fabrication).** Every row cites a specific file path + what was found this
session (2026-07-22, autonomous run, no network). Files read directly: `simulation/premise_demand.py`,
`simulation/demand_model.py`, `simulation/household_demand.py`, `simulation/household.py`,
`simulation/population_draw.py`, `simulation/household_segments.py`, `simulation/meter_reads.py`,
`simulation/life_events.py` (event-type grep), `company/market/seasonal_demand.py`,
`company/market/hh_data_quality.py`, `sim/profile_class_1.py`, `docs/observability/gate_authorizations.jsonl`.
**No figure fabricated**; where a surface was searched and not found, the row says "not found after checking X".
ABSENT is a first-class, expected verdict — nothing is inflated.

**Level fact (R16, verified this session).** `W1_5_premise_demand_shape` is `level_current: 3`, and the L3 is
**genuinely ledger-backed**: `gate_authorizations.jsonl` line 74, `LEVEL_UP_PROPOSED level 3`, ts 1784641860,
director verbatim "W1_5->L3 RATIFIED". So the map's `3` is authority-backed, not a self-promotion. The L3 was
certified on the aggregation-consistency invariant + the mean-1 idiosyncratic-noise DoD term — a *narrower* bar
than this board's two-level test (see Director Findings F1).

---

## Reconciliation tables

Verdict legend: **MET** (a code surface proves the model satisfies the expectation / avoids the named failure) ·
**PARTIALLY MET** (present but incomplete, mis-calibrated, or at the wrong granularity) · **ABSENT** (searched,
not found — or the model commits the named failure) · **N/A**.

### §1 — The drivers, decomposed honestly

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 1.gas.physics | Gas = building physics (floor area, age, insulation, glazing, heating system efficiency) setting the loss *envelope*, filtered through behaviour (setpoint ≈10%/°C, hours, rooms, setback) | `demand_model.build_demand_shape` gas branch; `household.epc_consumption_multiplier` | PARTIALLY MET | `demand_model.py:56,162-165` gas load = `HDD × GAS_HEATING_KWH_PER_DEGREE_DAY(8.0)`, gated on `heating_system=="gas_boiler"`; `household.py:176-184` EPC multiplier A..G = 0.75..2.20 scales the envelope. But the envelope is a **single scalar** (EPC band + one deg-day coefficient), not floor-area/glazing/construction physics; **no thermostat setpoint, heating-hours, per-room, or setback behaviour** exists (grep: none). No BREDEM/SAP/RC thermal network (FRAME §3 finding, still true) | Advance = the `SPEC003_housing_physics_gap` candidate atom (BREDEM/RC lumped-parameter thermal + behavioural setpoint/hours knobs), closing the EPC→SAP provenance loop |
| 1.gas.occupancy | Occupancy scales hot water and cooking | `demand_model.occupancy_multiplier` | PARTIALLY MET | `demand_model.py:93-119` occupancy_multiplier(single/family/elderly, period) shifts *when* load lands (evening 1.25–1.4) | Occupancy shifts the shape's timing but there is no explicit hot-water/cooking demand component keyed to occupant count; it is a timing multiplier, not a volume driver |
| 1.gas.veteran | Physics explains most variance *across* stock; behaviour most *between similar homes*; weather most *within one home over time* | whole premise chain | PARTIALLY MET | Across-stock physics (EPC 0.75–2.20) ✓; within-home-over-time weather (HDD, `premise_demand.py:99-105`) ✓; **between-similar-homes behaviour is only the CV=0.15 idiosyncratic factor** (`premise_demand.py:246`) — see 2.twins | The middle term (the board's whole thesis "knowing the household beats knowing the house") is present in mechanism but ~4× too tight in magnitude |
| 1.elec.inverts | Non-heating electricity inverts the ranking: occupancy + appliance stock dominate (people, hours, tumble dryer, shower, freezer, EV), building minor; exceptions = electric-heated (behaves like gas) + LCT (EV/HP double the home) | `demand_model` elec branch; `household.ev_annual_kwh`/`ashp_annual_kwh` | PARTIALLY MET | Occupancy multiplier ✓; **appliance-stock heterogeneity ABSENT** (no per-home tumble-dryer/shower/freezer draw — grep: none); electric-heating present (`ELEC_HEATING_KWH_PER_DEGREE_DAY` storage 3.0 / heat_pump 1.2, `demand_model.py:57-60`); EV +2,143 kWh (`household.py:223`), ASHP +5,500 kWh (`household.py:234`) | Advance = an appliance-ownership vector per home so non-heating elec variance comes from stock, not a scalar |
| 1.residual.random | A residual that must stay genuinely random (guests, illness, whim); a model that explains everything has overfitted | `premise_demand.idiosyncratic_factor` | MET | `premise_demand.py:273-291` mean-1 strictly-positive lognormal per premise from a named C-S2 substream, deterministic on replay, R15 `noise_is_unbiased` control mutation-proven | Mechanism is clean and aggregation-preserving; the open question is its *magnitude* (2.twins), not its existence |

### §2 — Variation: between similar homes, and within one home over time

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 2.twins | Between physical twins the famous **factor of two to three** in heating consumption; a population clustering tightly around physics-predicted demand has deleted the field's best-documented fact | `premise_demand.idiosyncratic_factor` (CV) | PARTIALLY MET | The only within-physics-cell spread is the idiosyncratic lognormal at **`_DEFAULT_CV = 0.15`** (`premise_demand.py:246`), i.e. ~±15% (≈1.4× P90/P10), **far below the 2–3× the board names**. The CV is self-flagged R10 "conventional diagnostic band, NOT a fitted truth" (`premise_demand.py:239-245`) | **Headline §2 gap.** Mechanism exists and is correctly mean-preserving, but the calibration deletes exactly the fact the board says is decisive. Advance = calibrate CV (and make it heating-specific/behavioural) to a SERL-class 2–3× twin spread |
| 2.righttail | Across the book a **heavy right tail**: long tail of large hard-to-heat homes at several × median, fat mass of small flats below; mean > median | `population_draw` EAC draw; `household` EPC | PARTIALLY MET | `population_draw.py:98-119,247-248` EAC = `uniform(low,high)` within one of three **bounded TDCV bands** (weights LOW/MED/HIGH 0.30/0.45/0.25 — near-symmetric, `DEFAULT_BAND_WEIGHTS`); HIGH gas caps at 15,000 kWh (~1.6× the 9,500 median), so **no long tail beyond the band cap**. EPC multiplier (up to 2.20) adds a mild right-tilt. No lognormal/heavy-tail book, no enforced mean>median | Distribution is bounded-uniform-in-bands + a mild EPC tilt, not the right-skewed heavy tail; the commercial edge the Worrier flags (margin/debt/abatement concentrate in the tail) is not reproducible. Advance = a right-skewed (e.g. lognormal) consumption book |
| 2.withinhome | Within one home: weather-corrected annual moves 10–20% YoY (occupancy/habit/kit drift), *discontinuously* at life events (baby, retirement, home-working, EV, boiler, lodger — **steps not trends**); plus scheduled absences (holidays, void weeks → gas to pilot/zero) | `life_events.py`; `household_demand.HouseholdDemandRegister` | PARTIALLY MET | **Steps: strong.** `life_events.py` emits solar_install, battery, ev_acquired, heat_pump, boiler_replaced, insulation_upgraded, job_loss, income_recovery, new_baby, retirement_starts, illness, divorce; `household_demand.py:98-141` applies them as **date-aware** EPC/EV/ASHP/solar/gas step changes. **Gaps:** no "home-working" or "lodger" event; **no continuous 10–20% YoY drift** (only discrete events + weather); **no holidays / void weeks / tenancy-absence / summer-gas-zero** (grep for void/holiday/pilot in `simulation/` = only `sme_distress.py`, a non-domestic path) | Advance = a within-home slow-drift term + domestic void/holiday/tenancy-absence events (the zeros the board demands) |

### §3 — The half-hourly truth: spiky homes, smooth crowds

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 3.individual | An individual home's HH electricity trace is **jagged, spiky, frequently near zero** — base 50–150 W punctured by short violent spikes (3 kW kettle 2 min, 9 kW shower 8 min, oven cycling); gas near-binary (boiler firing in bursts then off) | `demand_model.build_demand_shape` × `premise_demand.idiosyncratic_factor` | **ABSENT** | The per-premise HH trace is `build_demand_shape` = a **smooth** 48-period profile-class base × occupancy multiplier + degree-day load spread across period *weights* (`demand_model.py:157-187`), then multiplied by **one mean-1 scalar** (`premise_demand.py:103-105` — `[v * idiosyncratic_factor for v in shape]`). It is a **scaled copy of a smooth average curve**: no base-load floor, no appliance spikes, no zero-visiting, no binary gas firing. **Advisor flag (a) confirmed at code level, without flattery** | The exact failure §3 names. Advance = a bottom-up appliance/occupancy event simulator (kettle/shower/oven cycling, boiler on/off) producing genuine HH spikiness per home |
| 3.smoothcrowd | Smoothness is a property of **aggregation, not homes**: sum a few thousand diverse homes → morning ramp, daytime trough, 17:00–20:00 evening peak, overnight floor | `premise_demand` aggregation invariant; `sim/profile_class_1.py` | MET (aggregate only) | The **aggregate** is right and anchored: `profile_class_1.py:1-25` uses **real published Elexon/UKERC GAD** PC1 shapes (5-season × 3-day-type); `premise_demand.aggregate_reconciles` (`:189-202`) is an R15-failable summed-to-national invariant. But note the aggregate is correct *because* each home is a smooth scaled average (3.individual) — the crowd's smoothness is inherited from smooth individuals, not earned by averaging spiky ones | Aggregate profile is genuinely met; the *mechanism* that produces it is the disqualified one (see 3.twolevel) |
| 3.twolevel | The Doer's **two-level test**: a credible model is right at both levels *simultaneously*; a model giving every home a scaled copy of the average curve "has faked the crowd by falsifying every individual in it" | whole premise chain | **ABSENT** | This is **precisely** what the code does: individual = smooth base curve × mean-1 scalar (3.individual); aggregate = reconciled national (3.smoothcrowd). The model is right at the aggregate level and **faked at the individual level** — the failure mode the board names verbatim | The board's most-failed section, and the model fails it. Advance = spiky-individual generator that still sums (LLN) to the anchored aggregate — the two-level test as an explicit dual invariant |
| 3.perfectvsreal | Realistic = spiky HH, skewed book, stepped years, zero-visiting, **seasonally switched** (heating season a *decision* with **distributed start dates**), observed through an **imperfect meter estate** (missing intervals, failed comms, estimated legacy reads) — "Spec 006's information wall begins here" | `meter_reads.py`; `hh_data_quality.py`; degree-day model | PARTIALLY MET | Meter estate: **built** (`meter_reads.py` — smart not-communicating 10%, estimated-from-trailing reads, delay, back-billing cap; advisor flag (b) — the unhappy-path physics, cite it) but at **monthly-billing** granularity, not HH missing-interval injection; `hh_data_quality.py` is a company-side *checker* (flags gaps/estimates/zeros) not a generator. **Heating-season switch + distributed start dates: ABSENT** — heating is a *continuous* HDD response (`demand_model.heating_degree_days`, fires whenever temp<15.5), no seasonal on/off decision, no start-date distribution (grep: none). Spiky/zeros: absent (3.individual, 2.withinhome) | Advance = (1) heating-season switch with a per-home start-date distribution; (2) HH-level gap/estimate injection into the generated stream, not just billing-level |

### §4 — Gas versus electricity shape, side by side

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 4.scale | A dual-fuel home burns roughly **3–4× more gas than electricity** annually | `population_draw.TDCV_BANDS_KWH` | MET | `population_draw.py:98-109` gas MEDIUM 9,000–10,000 vs elec MEDIUM 2,300–2,700 kWh/yr → **~3.6–4.0×**; LOW 6,000/1,600 ≈ 3.75×; HIGH 14,000/3,800 ≈ 3.7× — squarely in the band | Anchored to Ofgem TDCV 2026; clean pass |
| 4.seasonality | Gas seasonality **extreme** (winter several-fold summer, summer = hot water + cooking only); electricity **mild** (winter ~1.5× summer, driven by lighting/darkness not heating) | `demand_model` HDD gas; `company/market/seasonal_demand.py` | PARTIALLY MET | Premise physics: gas = base + 8×HDD, so summer (HDD=0) collapses to the cooking/HW base → premise-level gas seasonality *is* several-fold ✓. Non-heating elec has **no HDD term** → weakly seasonal ✓. **BUT** the company-side `seasonal_demand.py:22-27` `_SEASONAL_INDEX` (0.80–1.35, ≈1.7× winter/summer) is applied **fuel-flat** — the same index for gas and electricity, understating gas and overstating elec seasonality at the portfolio layer (see Director Findings F3) | Two demand representations disagree on gas seasonality; the portfolio model needs a fuel-differentiated (steep-gas) index |
| 4.intraday | Gas peaks hardest **winter morning** (recovery burn after overnight setback) + broad evening plateau; electricity peaks **early evening year-round** | `demand_model.HEATING_PERIOD_WEIGHTS`; `occupancy_multiplier` | PARTIALLY MET | Elec evening peak ✓ (`occupancy_multiplier` evening 1.25–1.4, `demand_model.py:105-119`). **Gas intraday wrong:** `HEATING_PERIOD_WEIGHTS` (`:77-80`) spreads heating **equally** across morning (13–20) *and* evening (34–44) — no winter-morning recovery-burn dominance, no overnight-setback model | Advance = an overnight-setback + morning-recovery gas profile (asymmetric morning-heavy weights in winter) |
| 4.tempsens | Gas **steeply** weather-driven (Spec 002's hockey stick); non-heating electricity only **weakly** | `demand_model` HDD coefficients | MET | Gas 8.0 kWh/HDD (steep, `:56`); non-heating elec has no HDD term (only electric-heating homes get 1.2–3.0 kWh/HDD, `:57-60`) — the asymmetry the board describes | Slope calibration is a seed estimate (`:55` "seed estimates pending enrichment"), not fitted — a calibration note, not a structural gap |
| 4.crossover | Electrically heated homes (storage heaters on off-peak, resistive, heat pumps) make elec behave like gas (**night-charging shapes**, deep winter sensitivity); EV homes add an **overnight mountain** | `demand_model` elec-heating; EV block; `household` | PARTIALLY MET | Electric-heating homes present with HDD sensitivity (storage 3.0, heat_pump 1.2 kWh/HDD); EV overnight block present (`EV_CHARGING_PERIODS = range(1,9)`, 00:00–04:00, `:124`) ✓. **BUT storage-heater night-charging (Economy-7 overnight *charge* shape) is ABSENT** — electric heating uses the same morning+evening `HEATING_PERIOD_WEIGHTS`, not an overnight charge block; the "small but financially stressed" legacy off-peak population's distinctive shape is not modelled | Advance = an Economy-7/storage-heater overnight-charge profile distinct from the heat-load timing |

### §5 — The battery: what makes a simulated demand model NOT credible (11 items)

Semantics: **MET** = the model *avoids* the named failure (meets the credibility bar); **ABSENT** = the model
*commits* the failure; **PARTIALLY MET** = partly avoids it.

| id | board_text (short) | reconciles_to | verdict | evidence | notes / what would advance it |
|---|---|---|---|---|---|
| 5.1 | Physical twins that consume alike; physics predicting demand too well | 2.twins | PARTIALLY MET | Idiosyncratic noise exists but CV=0.15 (~±15%) vs the board's 2–3× — the model **partly commits** this failure (`premise_demand.py:246`) | = 2.twins; calibrate the behavioural spread |
| 5.2 | Smooth per-home curves resembling scaled average profiles | 3.individual | **ABSENT** | The model **commits** this failure exactly: per-home trace = smooth base × single scalar (`premise_demand.py:103-105`) | The headline defect |
| 5.3 | No zeros, voids, or absences; no summer gas floor; every home always on | 2.withinhome, 3.perfectvsreal | **ABSENT** | No domestic void/holiday/tenancy-absence/zero events (grep: only `sme_distress.py`, non-domestic). Summer gas *floor* exists (HDD=0 → base) but never *zero* | Add domestic voids/holidays/tenancy zeros |
| 5.4 | Continuous temperature response per home; no heating-season switch, no setback, no distribution of season start dates | 3.perfectvsreal, 4.intraday | **ABSENT** | Heating is continuous HDD, always-on below 15.5°C; no season switch, no setback, no start-date distribution (grep: none) | Add the heating-season decision + start-date distribution |
| 5.5 | Seasonality ratios wrong (gas winter/summer below several-fold, or elec seasonality gas-like without electric heating) | 4.seasonality | PARTIALLY MET | Premise-physics gas seasonality is several-fold ✓ and elec is mild ✓; but the portfolio `seasonal_demand.py` index is fuel-flat ~1.7× (understates gas) — a partial commit at the portfolio layer | Fuel-differentiate the seasonal index (F3) |
| 5.6 | A symmetric book; no heavy right tail; mean and median coincident | 2.righttail | PARTIALLY MET | Bounded-uniform TDCV bands (near-symmetric weights) + a mild EPC right-tilt — no heavy tail, mean≈median-ish (`population_draw.py:119,247`) | Right-skew the consumption book |
| 5.7 | Frozen households; static annual consumption; no life-event steps; no kit replacement | 2.withinhome | MET | **Avoided well:** `life_events.py` + `household_demand.py` give date-aware steps (baby, retirement, EV, HP, boiler, insulation, job-loss, divorce, illness) and kit replacement (boiler_replaced, heat_pump) | Strongest area; only the slow-drift term is missing (2.withinhome) |
| 5.8 | Mistimed or missing peaks; no 17:00–20:00 elec peak, no winter-morning gas spike, no weekend distinction, no seasonal migration | 3.smoothcrowd, 4.intraday | PARTIALLY MET | Elec 17–20 evening peak ✓ (occupancy); weekend distinction ✓ (`profile_class_1.py:37` Wd/Sat/Sun day-types); seasonal migration ✓ (real 5-season GAD structure). **BUT no distinct winter-morning gas spike** (4.intraday — gas morning=evening) | Fix the gas morning-recovery peak |
| 5.9 | Perfect observation; every home HH-metered, no estimated reads, no gaps — the legacy meter estate absent (seam into Spec 006 item 6) | 3.perfectvsreal; `meter_reads.py` | PARTIALLY MET | **Avoided at billing level:** `meter_reads.py` models smart not-communicating (10%), estimated-from-trailing reads, delay, back-billing cap; `hh_data_quality.py` checks gaps/estimates. **But not injected as HH missing intervals in the generated demand stream** — the imperfection lives in the billing path, not "demand as the supplier experiences it" at the half-hour | Advance = HH-level gap/estimate injection; this is the explicit Spec-006 information-wall seam |
| 5.10 | One level right, the other faked; the two-level test failed either direction | 3.twolevel | **ABSENT** | The model is right at the aggregate and **faked at the individual** — the two-level test fails in exactly the direction §3 describes | = 3.twolevel |
| 5.11 | Clean elasticity; textbook price/message responsiveness, no inattention, no non-response mass, no decline-and-never-act (Spec 006's disengaged majority) | `household_segments.py`; `company/pricing/price_elasticity.py`; `company/crm/churn_model.py` | PARTIALLY MET | **Non-response mass exists:** `household_segments.py:51-73` persistent per-customer engagement archetypes ACTIVE/PASSIVE/**DISENGAGED** (0.48/0.23/0.29 share; per-renewal active prob 0.65/0.15/**0.02**), anchored to Ofgem 2018; segment-level `price_elasticity.py` + `churn_model.py` disengaged-persistence. **But** this is **churn/switching-side** response, not **demand-side** response to price signals or DSR *messages*; and "disengaged" is 29%, not the *majority* Spec 006 posits. **Reconcile jointly with Spec 006** (advisor flag d) | Advance = a demand-side (consumption/DSR) response model with a genuine non-response mass, reconciled to Spec 006's disengaged-majority segmentation |

---

## Director findings — board-vs-built tensions and honest gaps (flag, do not resolve)

**F1 — The two-level test is the headline honest gap, and W1_5's ledger-backed L3 rests on a narrower bar than
the board's.** W1_5 is legitimately ratified to L3 (`gate_authorizations.jsonl:74`, director "W1_5->L3
RATIFIED", ts 1784641860) — the L3 certified the *aggregation-consistency invariant* + a *mean-1 idiosyncratic-
noise* DoD term. Both are real and R15-proven. But the board's §3/§5.2/§5.10 two-level test is a **harder bar
that the L3 does not clear**: the individual HH trace is a smooth average curve × one scalar
(`premise_demand.py:103-105`), i.e. "every home a scaled copy of the average" — the failure the board names
verbatim. This is not an R16 defect (the L3 is authority-backed) and not a canon conflict; it is an honest gap
between what L3 certified and what a blind practitioner demands. **For the director:** does the individual-trace
spikiness gap warrant a new atom (bottom-up appliance/occupancy HH generator) sequenced against the L3 cell, or
is smooth-individual an accepted simplification given the aggregate is anchored?

**F2 — The behavioural factor-of-2-3 (the field's best-documented fact) is deleted by calibration, not by
design.** The mechanism (mean-1 idiosyncratic lognormal) is correct and aggregation-preserving, but
`_DEFAULT_CV = 0.15` (`premise_demand.py:246`, self-flagged R10 "conventional band, NOT a fitted truth") gives
~±15% between physical twins vs the board's 2–3×. The board calls a tight-clustering population "deleting the
single best-documented fact in the field". This is a **calibration** gap (couples to the segmentation work's
SERL/EPC priors), reversible via CV, not a structural rebuild.

**F3 — Two demand representations disagree on gas seasonality.** Premise-level physics
(`demand_model.build_demand_shape`, HDD × 8.0) produces several-fold gas winter/summer seasonality — board-
consistent. But the portfolio-level `company/market/seasonal_demand.py:22-27` applies a **fuel-flat** ~1.7×
seasonal index to *both* gas and electricity, understating gas and making elec look gas-like — the board's
§5.5 failure at the portfolio layer. Not a wall/canon conflict; an internal inconsistency between the SIM
generator and the company forecast surface.

**F4 — No BREDEM/SAP/RC thermal physics (carried forward from `TRIANGULATION_WEATHER_DEMAND_PRICE_FRAME.md`
§3, still true).** The building envelope is a scalar EPC multiplier (`household.py:176-184`) + one degree-day
coefficient, not a physics network; the board's §1 physics decomposition (floor area, glazing, construction,
system efficiency as *separable* drivers) is collapsed to one number. Closes directly onto the EPC→SAP
provenance loop and the segmentation EPC/census priors. The named candidate atom `SPEC003_housing_physics_gap`
already captures this.

**F5 — Battery item 11 must reconcile jointly with Spec 006 (advisor flag d).** The built non-response mass is
**churn/switching-side** (`household_segments.py` persistent DISENGAGED 29% + `price_elasticity.py`), not
**demand-side** price/message responsiveness; and "disengaged" here is a 29% minority, whereas Spec 006 posits a
disengaged *majority*. Whether the two are the same population under one taxonomy is a Spec-006 reconciliation
item, not resolvable inside Spec 003 alone.

---

## Summary scoreline

**28 scoreable expectations · 5 MET · 17 PARTIALLY MET · 6 ABSENT · 0 N/A.**

By section (MET / PARTIAL / ABSENT): §1 drivers **1 / 4 / 0** · §2 variation **0 / 3 / 0** · §3 half-hourly
truth **1 / 1 / 2** · §4 gas-vs-elec **2 / 3 / 0** · §5 battery **1 / 6 / 4**.

**The strongest half is the aggregate and the timeline:** the national aggregate is anchored to real Elexon/UKERC
profile-class GAD and R15-reconciled (3.smoothcrowd, 4.scale, 4.tempsens MET), and the within-home life-event
step machinery is genuinely good (5.7 MET). **The weakest half is precisely the section the board says most
simulations fail — the individual half-hourly home:** it is a smooth average curve × one scalar, failing the
two-level test (3.individual / 3.twolevel / 5.2 / 5.10 all ABSENT). Advisor flag (a) is confirmed at the code
level, without flattery.

**The 3 most material gaps:**
1. **Individual HH traces are smooth scaled averages, not spiky/zero-visiting homes — the two-level test fails**
   (3.individual, 3.twolevel, 5.2, 5.10; F1). `premise_demand.py:103-105` multiplies a smooth base curve by one
   mean-1 scalar; there are no appliance spikes, no base-load floor, no binary gas firing.
2. **The factor-of-2-3 behavioural spread between physical twins is deleted by CV=0.15** (2.twins, 5.1; F2) — the
   mechanism is right, the magnitude is ~4× too tight and self-flagged uncalibrated.
3. **No heating-season switch / distributed start dates, and no domestic zeros/voids/holidays** (5.3, 5.4,
   2.withinhome, 3.perfectvsreal) — heating is a continuous always-on HDD response and every home is always on.

*Reconciliation authored per the standing steer: the four §2/§3/§4 "NOT credible" battery seeds plus these 11
items join the practitioner fidelity oracle; findings → proposals via propose-then-proceed (generator/engine
changes return as named proposals — `SPEC003_housing_physics_gap` and a new bottom-up-HH-trace candidate).*
