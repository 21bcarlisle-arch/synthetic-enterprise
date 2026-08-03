# PREMISE FABRIC PHYSICS — DISCOVER + FRAME (doc-only)

**Status:** DISCOVER/FRAME output for `docs/staging/ADVISOR_DISCOVERY_PREMISE_FABRIC_PHYSICS_2026-08-03.md`
(director-approved in live conversation, advisor-drafted). **No code, no engine change, no level move.**
Companion: `docs/design/PREMISE_TWO_LEVEL_TEST_HARNESS_SPEC.md` (deliverable 3).
Framed atoms minted into `docs/design/maturity_map.yaml` (deliverable 2): `W1_11_fabric_physics_core`,
`W1_12_premise_trace_generator`, `C14_thermal_parameter_inference`, `H_GAP_fabric_belief_truth_gap`.

**Evidence discipline (R9):** every claim below is tagged `observed-in-code`, `observed-in-report`
(the director's 2026-08-03 house-usage review, quoted in the staged doc), `domain-knowledge`
(my own knowledge of UK building physics / published statistics, **not** fetched this pass — no
network in autonomous runs), or `inferred`. Numeric anchors tagged `domain-knowledge` are
**candidates to verify at BUILD against the named source**, never settled constants.

---

## 0. The finding in one sentence

`observed-in-code` — **The premise generator uses a crowd mean as an individual trace**: every
home's texture is `sim/profile_class_1.py::load_pc1_shape()`, the Elexon Profile Class 1 GAD
*average* profile keyed only by (season, day-type), and every downstream term either rescales it
by a scalar or adds a fixed block-shaped heating vector. A population mean is smooth *by
construction* — so the model is simultaneously **too smooth at Level 1** (an individual home
cannot be recovered by rescaling the average of millions) and **un-smoothable at Level 2** (if
every home is the same shape, aggregating N of them returns that same shape, so aggregation
smooths nothing). One defect, both failures. This is not a tuning problem; it is a
wrong-object problem, and no amount of noise sprinkled on the current path fixes it.

---

## 1. Mechanism-level diagnosis — what actually produces each failed statistic

The director's review reported five failed statistics. Each traces to a specific line of shipped
code. This section is the R4 diagnosis (name the mechanism before designing the fix).

| Reported statistic (`observed-in-report`) | Producing mechanism (`observed-in-code`) |
|---|---|
| Median period-to-period change 0.008–0.012 kWh vs ~0.7 kWh mean (~1.5%) | `build_demand_shape` (`simulation/demand_model.py:609`) starts from `base_shape` = the PC1 **GAD ensemble average**, which is a smooth curve because it is the mean of millions of homes. There is **no per-period stochastic term anywhere** in the call chain. |
| Day-vs-next-day shape correlation 0.97 | The only thing that changes between consecutive days is the scalar `hdd = max(0, 15.5 − mean_temp_c)` (`demand_model.py:62`) and the (season, day-type) column selection. Same column + similar HDD ⇒ near-identical shape by construction. |
| No half-hour below 0.05 kWh in ten years | The PC1 average has a strictly positive floor at every period; every subsequent operation is a multiplication by a **positive** scalar or an addition of a non-negative heating term. Nothing in the chain can drive a period toward zero. There is no absence/away state and no appliance on/off state — **an empty house is not representable**. |
| Repeating rescaled-fraction values | Every per-home differentiator is a **scalar** on the whole 48-vector: `Household.epc_consumption_multiplier()` (`simulation/household.py:161`), `occupancy_volume_factor(...)`, and `premise_demand.idiosyncratic_factor` (explicitly documented there as mean-1 and shape-preserving). A scalar changes the **level** and can never change the **texture**. |
| Identical block timing across homes; C8–C9 correlation 0.95; 3-home aggregate peak/mean 5.9 vs 5.7 for one home | Heating load is added as `hdd × k × HEATING_PERIOD_WEIGHTS`, and `HEATING_PERIOD_WEIGHTS` (`demand_model.py:93`) is a **single module-level constant**: uniform weight over periods 13–20 and 34–44, identical for every premise in the country. Every home therefore heats at exactly the same minutes with exactly the same rectangular shape. The only per-period variation is `occupancy_multiplier(pattern, period, ...)`, keyed to a small enum of occupancy patterns, so homes cluster into a handful of near-identical shapes. **Diversity is the thing that makes crowds smooth; there is essentially none, so aggregation cannot smooth.** |
| Gas has no premise-level trace | `GAS_HEATING_KWH_PER_DEGREE_DAY = 8.0` (`demand_model.py:74`) is one flat national constant applied to every gas-heated home, over the same national block weights. Gas has no fabric term, no thermal dynamics, and no per-premise timing at all. |

Two further mechanism facts that constrain the design:

- `observed-in-code` — **The weather input is a DAILY MEAN.** `build_demand_shape` takes
  `mean_temp_c` and derives a daily HDD scalar. Intraday temperature, solar gain timing and
  overnight cooling are invisible to the heating term (solar irradiance enters only as a *PV
  generation* subtraction, never as a *thermal gain*). No thermal-dynamics model can be fitted on
  top of the current input contract — **the fabric layer needs half-hourly weather in, not a daily
  mean.** This is the single biggest interface change the design implies.
- `observed-in-code` — `simulation/household.py` **already holds the right structural variables**
  (`PropertyType`, `BuildEra`, `HeatingSystem`, `BoilerAge`, `InsulationLevel`, EPC rating), but
  collapses them into two scalars: `epc_consumption_multiplier()` (a level multiplier) and
  `seasonal_flatness_factor()` (a seasonality multiplier). The fabric information **is already
  carried**; it is thrown away at the point of use. Layer 1 below is largely a matter of routing
  those existing fields into a physics function instead of a lookup table.

### 1a. What this means for W1_5's L3 status (coupled-triad consequence)

`observed-in-code` + `inferred` — `W1_5_premise_demand_shape` sits at **level 3 / harden** in the
maturity map. Its L3 evidence is the **aggregation-consistency** invariant in
`simulation/premise_demand.py` (`reconciliation_residual`, `aggregate_reconciles`,
`noise_is_unbiased`). Those controls are real, independent and R15-failable — and they are all
**level-and-sum controls**. Not one of them looks at texture, timing, trough behaviour or
between-home diversity. W1_5 therefore passes every control it has while failing both levels of
the test a director applied by eye in an afternoon.

That is the coupled triad's own definition of the gap, and it is worth recording plainly rather
than softening: **a level was earned against the controls that existed, and the world could still
be defeated.** The remedy is not to demote W1_5 retroactively — the aggregation work is correct
and stays — but to (a) land the two-level test as a standing, failable control
(`docs/design/PREMISE_TWO_LEVEL_TEST_HARNESS_SPEC.md`), (b) let it fail against today's generator,
and (c) make it the exit test for the new atoms. A control that is introduced already-passing has
proved nothing (R15); this one is introduced **already-failing**, against a named defect, which is
the strongest possible birth condition for it.

---

## 2. The design — two layers, cleanly separable

```
  weather (half-hourly, local)  ─┐
  fabric parameters (per premise)─┼─► LAYER 1: fabric physics ──► "standard-occupancy" demand
                                 │       2R2C thermal model            (gas + electricity)
  LCT assets (HP/EV/PV/battery) ─┘       + heating-system controller           │
                                                                               ▼
  occupancy / setpoints / heating hours ──► LAYER 2: behaviour ──► ACTUAL metered demand
  tariff scheduling / income constraint          (modifies WHEN and HOW MUCH)
```

The separability requirement (hard requirement 1 in the staged doc) is met by a **strict
contract**: Layer 1 is a pure function of `(fabric, weather, assets, setpoint schedule)` and knows
nothing about segments, engagement, psychology or tariffs. Layer 2 supplies **only** the setpoint
schedule, the occupancy/gain profile and an appliance event stream; it may not reach inside the
thermal model. Concretely — Layer 2's entire influence on Layer 1 is three arguments. That is the
seam, and it is testable: *hold Layer 2 fixed and vary fabric, and only level+character move; hold
fabric fixed and vary Layer 2, and only timing+volume move.*

### 2.1 Layer 1 — fabric physics

**Verdict on appendix item A (2R2C): ADOPT as the core.** See §4A for reasoning.

State: indoor-air temperature `T_i` (fast node) and building-mass temperature `T_m` (slow node).

```
C_i dT_i/dt = (T_a − T_i)/R_ia + (T_m − T_i)/R_im + Φ_h + Φ_p + f_i·Φ_s
C_m dT_m/dt = (T_i − T_m)/R_im                          + (1−f_i)·Φ_s
```

- `R_ia` — air-node-to-ambient resistance (ventilation + fast fabric losses)
- `R_im` — air-to-mass coupling
- `C_i` — air + furnishings heat capacity (small ⇒ minutes-to-an-hour response ⇒ **this is what
  produces boiler cycling and therefore half-hourly spikiness**)
- `C_m` — structural thermal mass (large ⇒ days ⇒ **this is what produces fabric character**:
  a solid-wall Victorian terrace with high `C_m` runs long and smooth; a modern timber-frame house
  with low `C_m` cycles hard and spikes)
- `Φ_h` heating power, `Φ_p` occupant+appliance gains, `Φ_s` solar gain, `f_i` solar split to air

`domain-knowledge` — the mechanism that turns this into **spiky half-hourly demand** is not the RC
model itself but the **controller on top of it**: a thermostat with a deadband (typ. ±0.5 °C)
plus a boiler with a finite modulation range. The air node crosses the deadband, the boiler fires
at its rated output, the air node overshoots, the boiler stops. In a half-hourly aggregation this
appears as a partial duty cycle that varies period to period — the missing texture. **A 2R2C
model with a continuous, perfectly-modulating heat source would reproduce today's smoothness.**
This is the single most important implementation note in the document: *the deadband is not a
detail, it is the mechanism.*

**Fabric character emerges rather than being asserted:** the time constant `τ_m = R_im · C_m`
determines how long the heating must run per cycle and how deep the overnight setback drift is.
High-`τ_m` homes have few long cycles (smooth, high day-to-day correlation *within* winter, slow
response to a cold snap); low-`τ_m` homes have many short cycles (spiky, fast response). The
between-home *timing* diversity that Level 2 demands therefore falls out of fabric variation plus
setpoint-schedule variation — it does not have to be injected as noise. That matters: injected
noise would fail hard requirement 2's spirit even if it passed its letter.

**The parameter set — "a simple number of available variables" (director's words).**
The company-visible parameter vector, all EPC-class:

| Variable | EPC field (`observed-in-report`, `docs/market_research/epc_open_data.md`) | Drives |
|---|---|---|
| Floor area (m²) | `TOTAL_FLOOR_AREA` | scale of `C_m`, `C_i`, envelope area |
| Property type | `PROPERTY_TYPE` | storey/exposure geometry |
| Built form | `BUILT_FORM` | **exposed-envelope fraction** (detached ≫ mid-terrace) ⇒ `R_ia` |
| Construction age band | `CONSTRUCTION_AGE_BAND` | fabric U-values and airtightness priors |
| Walls description | `WALLS_DESCRIPTION` | solid vs cavity, insulated or not ⇒ `R_ia` **and** `C_m` |
| Habitable rooms | `NUMBER_HABITABLE_ROOMS` | heated-volume proxy, occupancy prior |
| Main fuel / mains gas flag | `MAIN_FUEL`, `MAINS_GAS_FLAG` | which commodity carries heat |
| Main heating description | `MAINHEAT_DESCRIPTION` | emitter type + system efficiency ⇒ controller |
| SAP points / rating | `CURRENT_ENERGY_EFFICIENCY`, `CURRENT_ENERGY_RATING` | **calibration cross-check only** — see §3 |
| Modelled kWh/m²/yr | `ENERGY_CONSUMPTION_CURRENT` | **calibration cross-check only** |

`inferred` — that is **nine structural fields**, all present in the bulk EPC download and all
already represented (in enum form) on `simulation/household.py::Household`. The mapping
`(built form, age band, walls, floor area) → (R_ia, R_im, C_i, C_m)` is the RdSAP-parameterised
step, and it is a small deterministic function, not a machine-learning problem. This satisfies the
director's "simple number of available variables" constraint without approximation.

**LCT rewiring of the electricity side** (`domain-knowledge`, all candidates to verify at BUILD):

- **Heat pump** — `Φ_h` divided by a **temperature-dependent COP**, so electricity demand rises
  super-linearly as ambient falls (roughly: COP falls from ~3.5 at 7 °C ambient to ~2.2 at −2 °C
  for a typical ASHP at 45 °C flow). This is the mechanism behind heat-pump winter peaks and it
  is *invisible* in today's flat `ELEC_HEATING_KWH_PER_DEGREE_DAY["heat_pump"] = 1.2`. Heat pumps
  also typically run **weather-compensated and near-continuously**, i.e. *smoother* than a boiler —
  so the design must produce different texture by heating system, not one texture for all.
- **EV** — event-driven: arrival time, state-of-charge deficit, charger power. Today it is a flat
  spread over a fixed period set (`EV_CHARGING_PERIODS`), which is a timing-diversity killer.
- **PV** — by orientation and pitch, against the same irradiance field; already partly present.
- **Battery** — deferred with item G (§4G).

### 2.2 Layer 2 — behaviour

Layer 2 supplies exactly three things to Layer 1 and nothing else:

1. **Setpoint schedule** — target temperature by half-hour, per day-type. Heating hours,
   setback depth, weekend/weekday difference, holiday/away days.
2. **Gain profile `Φ_p`** — metabolic + appliance heat, which is also the hook for the
   **appliance event stream** (kettle, oven, shower) that supplies non-heating electricity texture.
3. **Income/comfort constraint** — the **prebound effect**: fuel-poor households under-heat, so
   actual consumption falls materially below the physics prediction at standard occupancy. This is
   the honest home for a correction that today is buried inside `epc_consumption_multiplier()`'s
   docstring ("adjusted 50% toward 1.0 for prebound effect, Firth et al. 2013" —
   `observed-in-code`). Moving it from a hard-coded multiplier into a **behavioural response to
   income stress and price** makes it a live mechanism instead of a constant, and it plugs
   straight into the existing `IncomeStress` enum and the self-rationing detector.

`inferred` — the existing segment/engagement/psychology work attaches to Layer 2 **unchanged**:
`occupancy_pattern`, `people_count`, `children_count`, `pensioner_present`, `someone_employed` are
already the arguments to `occupancy_multiplier`, and they become the arguments to the setpoint
schedule and gain profile instead. No segmentation rework is implied by this design. That is a
deliberate design goal — the fabric layer must not fork the segmentation programme.

### 2.3 Where fabric archetypes sit relative to existing archetype dimensions

`inferred` — the existing household archetype dimensions are **behavioural and commercial**
(occupancy pattern, people count, income stress, engagement, tariff). Fabric is a **new,
orthogonal dimension**, not a re-cut of the existing ones: a low-income household can live in a
well-insulated flat and a high-income household in a leaky Victorian detached. The design
therefore adds fabric as a **cross-product dimension** rather than extending the archetype enum —
and the cross-product is exactly where the interesting business cases live (the fuel-poor
solid-wall home is the ECO/insulation target; the affluent leaky detached is the heat-pump target).
Collapsing fabric into the existing archetypes would destroy the mission-relevant cases. **Frame
verdict: separate dimension, joined at the premise, never merged into the archetype enum.**

---

## 3. Anchors and the independence rule

Hard requirement 4: validation must use anchors the generator did not.

| Anchor | Role | Used to **parameterise** | Used to **validate** |
|---|---|---|---|
| **RdSAP / SAP methodology** | fabric physics parameterisation from EPC fields | ✅ U-values, airtightness, thermal mass by age band and wall construction | ❌ **never** — it is the generator's own input |
| **NEED** (National Energy Efficiency Data framework: EPC-linked *actual metered* annual consumption) | annual **level** | ❌ | ✅ mean and **spread** of annual gas/electricity by property type × age band × floor-area band |
| **SERL** (Smart Energy Research Lab: half-hourly smart-meter data linked to EPC/survey) | **timing and texture** | ❌ | ✅ half-hourly load shapes, diversity/coincidence factors, texture statistics |
| Existing weather engine (W1_3/W1_4) | local weather input | ✅ | — |
| Elexon PC1 GAD (`sim/data/profile_class_1_gad.csv`) | — | ❌ **removed as an individual-home input** | ✅ the *aggregate* of many generated homes should approach the PC1 average shape |

The independence rule reduces to one crisp statement: **SAP parameterises, NEED and SERL judge.**
If a future build calibrates against NEED and then validates against NEED, the check is theatre
and must be rejected at Expert Hour.

The PC1 row deserves emphasis because it inverts the current architecture. Today PC1 is the
**input** to every individual home. In the new design PC1 becomes an **output test**: generate a
few thousand diverse homes, aggregate them, and the result should converge on the PC1 average
profile. That is a genuine, independent, R15-failable check — and it is the same statistic the
current generator passes *trivially and meaninglessly* (it passes because PC1 was the input;
it would pass even if every home were physically absurd).

**`domain-knowledge` — practicality of SERL access (an explicitly open question in the staged
doc).** SERL is a UKRI-funded observatory whose *record-level* half-hourly data is available to
accredited researchers under a data-access agreement, with an application process and an
institutional requirement. `inferred` — that is very likely impractical for this project and
should not be assumed. However, SERL publishes **statistical reports and summary tables** (load
shapes by dwelling and household characteristic, and diversity statistics), and those published
statistics are sufficient for every validation target in the harness spec, because every target
is a *distributional* statistic, not a record-level one. **Frame verdict: design against published
SERL statistics; treat record-level access as a bonus, never a dependency.** If the published
tables turn out to be insufficient for a specific target, the fallback is the LCL (Low Carbon
London) half-hourly household dataset, which is openly published — record that as the named
fallback rather than leaving the dependency open. **All of this is `domain-knowledge` and must be
re-verified by a DISCOVER agent with network access before any BUILD relies on it.**

### 3.1 The gas resolution question (open question, answered with a recommendation)

Hard requirement 3 asks for premise-level gas treatment and asks the design to justify the
resolution.

`domain-knowledge` — the physical facts that decide this: domestic gas is metered in the UK by a
**daily-read (or less frequent) meter for the vast majority of premises**; smart gas meters do
record half-hourly, but gas settlement operates on daily quantities, and gas demand is dominated
by space and water heating, which the thermal model resolves naturally at sub-hourly steps anyway.

**Recommendation: model gas at the SAME half-hourly step as electricity, but hold it to
DAILY-resolution validation targets.** Reasoning:

- The 2R2C model produces `Φ_h` at the simulation time step regardless; **producing a half-hourly
  gas trace is free** once the thermal model exists, and truncating it to daily would throw away
  information the model already has.
- What is *not* free is **evidence**: there is far weaker public anchor data for half-hourly
  domestic gas texture than for electricity. So the harness spec holds gas to daily-level
  validation (annual level, seasonal ratio, HDD-response gradient, day-to-day variability) and
  explicitly **registers half-hourly gas texture as an unvalidated simplification** in the atom's
  `simplifications` list rather than claiming fidelity it cannot evidence.
- This is the honest split: **half-hourly by construction, daily by evidence.** Claiming
  half-hourly gas *fidelity* without an anchor would be exactly the kind of unfalsifiable claim
  R15 exists to prevent.

---

## 4. Appendix items A–G — adopt / adapt / reject, with reasons

**A. 2R2C grey-box thermal model — ADOPT as Layer 1's core.**
It is the standard building-physics lumped-parameter form, its four parameters map cleanly onto
EPC-derivable quantities, and — decisively — the two-node structure is what separates *fast*
(cycling, spikes, Level 1 texture) from *slow* (fabric character, thermal mass, Level 2 diversity)
behaviour. A 1R1C model would give level and lag but not the character split; a full multi-zone
model would be unjustifiable complexity against the SIMPLICITY GUARD and unparameterisable from
EPC data. **Adoption carries one mandatory rider (§2.1): a deadband thermostat + finite-modulation
boiler on top. 2R2C without the controller reproduces today's smoothness and would fail Level 1
again** — this is the most likely way a future build gets this wrong.

**B. UKF parameter inference behind the wall — ADOPT, sequence second.**
This is the strategically important item and the reason this work is more than a fidelity fix.
It creates a genuine belief-vs-truth mechanism of the same class as the payment triad: SIM knows
actual `(R, C)`; the company observes EPC-class data (itself an imperfect estimate of real fabric —
`observed-in-report`, EPC coverage is ~60% of stock and biased toward transacting properties) plus
meter reads plus weather, and must *infer* thermal parameters. The gap is measurable, real
suppliers genuinely do this, and it is exactly the coupled-triad shape.

Two `inferred` design cautions to carry into the atom: (i) the company must **never** be handed
the SIM's `(R, C)` — the inference runs strictly on observables through
`company/interfaces/sim_interface.py`, and an epistemic-verifier pass is a gate on this atom, not
a nicety; (ii) UKF vs a simpler estimator is an implementation choice to settle at BUILD — the UKF
is justified by the non-linearity (temperature-dependent COP, deadband switching), but if the
first cut can be done with regularised least squares on the heating-response gradient, do that
first and escalate only if the gap metric demands it (SIMPLICITY GUARD). **Adopt the mechanism;
leave the estimator open.**

**C. GARCH(1,1) on price forecast errors — ADAPT, and register against the named spike-tail
defect, not here.**
Volatility clustering is real and the named defect is real (`observed-in-report`: max £574 vs real
£4,038; negatives 0.013% vs 2.241%). But GARCH is a **statistical** description of variance, and
this project's settled direction is **mechanism-first** physics (`WEATHER_PHYSICS_HIERARCHY_DESIGN`:
"price as pure output"). Bolting a statistical variance process onto a mechanism-generated price
would make the price partly unfalsifiable and would sit uneasily with R12 (a fitted variance
process is very close to a tuned output). **Adapt: use GARCH as a DIAGNOSTIC — fit it to real SSP
history and to generated history, and compare the persistence parameters as a falsifiable gap
statistic.** If the generated series has materially lower volatility persistence, that is evidence
about the *mechanism* (item D's non-linearity is the likely culprit) rather than a licence to
inject variance. This item belongs to the spike-tail atom, not to fabric physics; noted here for
the record and left there.

**D. Non-linear price S-curve on net load AND ramp rate — ADAPT, and note the coupling.**
The *ramp-rate* half is the genuinely new idea and is mechanistically sound: real scarcity pricing
responds to how fast the residual load is tightening, not only to its level, because flexibility
is rate-limited. This is a refinement candidate for the price engine and belongs to the
merit-order/price atoms (`W1_6b_merit_order_reconstruction` is at L1/build). **The coupling worth
recording: fabric physics changes the demand series' own ramp characteristics** — real homes
have sharper aggregate morning ramps than a smoothed average profile implies — so item D should
be evaluated *after* the fabric work lands, or its calibration will be against a demand series
known to be too smooth. Sequencing note, not a blocker.

**E. Aggregation weightings (population-weighted temperature, capacity-weighted wind, cumulative
HDD windows) — PARTLY CONVERGED, adopt the remainder.**
`observed-in-code` — the weather hierarchy **already** does demand-weighted regional aggregation
reconciling to national (`sim/weather_engine.py::simulate_regional_deviations`, and
`simulation/premise_demand.py`'s demand-weighted aggregate), so population-weighted temperature is
substantially built; record as **convergence evidence, not new input**, per the staged doc's
instruction. The genuinely new item is **cumulative HDD windows for gas** — gas demand depends on
the *recent history* of temperature, not just today's, because of building thermal mass and
(at system level) storage/linepack drawdown. That is the same `C_m` insight one level up, and it
is a real gap: today's `heating_degree_days()` is memoryless. **Adopt: the 2R2C model gives
premise-level thermal memory for free, and the system-level cumulative-HDD window should be
registered against the gas-demand chain.** Capacity-weighted wind: check against W1_4 at BUILD.

**F. Premise-level cost stack (DUoS bands, TNUoS, line-loss factors per half-hour) — REGISTER for
the value-cycle epoch, do not build here.**
Correct and genuinely needed for true per-home margin, and it is *enabled* by this work (a
per-home half-hourly trace is precisely what makes a per-home cost stack meaningful — today it
would be meaningless because every home has the same shape). But it is a **cost/settlement** item,
not a demand-physics item, and it belongs with the activity-based-pricing / cost-to-serve thread
(CLAUDE.md's standing "activity-based pricing" principle). Noted as a downstream beneficiary;
registered, not minted here.

**G. MILP flexibility optimisation — REGISTER, sequence later, per the director's own instruction.**
Explicitly deferred in the staged doc, and correctly: it requires Layer 1 to exist (there is
nothing to pre-heat without thermal mass) and it *is* the personalisation/carbon engine rather
than a component of the demand model. `inferred` design note for whenever it is drawn: a rolling
48-period MILP per premise across a large book is computationally serious, so the likely shape is
MILP for a representative archetype set plus a cheap policy fitted from it — record that as a
known constraint now so the atom is not framed as naively per-premise.

**Explicitly excluded and staying excluded** (director: "it has branded a little... don't go off
track"): real-DCC data acquisition, beta trials, VLP/SaaS commercialisation, cost-arbitrage-first
framing. The mission framing stands: **savings count only from reduced or time-shifted usage,
never from discounting.**

---

## 5. The wall — what the company sees, and the gap that becomes the score

| | SIM ground truth | Company observable |
|---|---|---|
| Fabric | actual `R_ia, R_im, C_i, C_m`, actual airtightness | **EPC-class fields only** — and only where a certificate exists (~60% of stock, transaction-biased), possibly up to 10 years stale, and itself a *modelled estimate* of the real fabric |
| Behaviour | actual setpoints, actual occupancy, actual away-days | inferred from meter reads + contact history only |
| Weather | the true local field | published/observed weather (genuinely public — stays public side) |
| Demand | the generated trace | metered reads at the customer's actual read frequency |

`inferred` — the EPC-vs-actual gap is the mechanism, and it is real-world faithful in a way that
is worth stating precisely: **a real supplier's fabric knowledge is an estimate of an estimate.**
EPC is a modelled assessment (often a reduced-data assessment with assumed values for anything not
visible on a walk-round), and the supplier then reads the EPC. Three distinct error sources —
EPC modelling error, EPC staleness, and EPC absence — each of which a real supplier genuinely
faces. Modelling all three is cheap here and gives the company something honest to be wrong about.

The measured gap (the harness's third loop) is defined in the harness spec: per-premise
`|inferred HLC − actual HLC| / actual HLC`, its distribution across the book, and — the one that
actually matters commercially — **the £ consequence**: how much worse is a fabric-targeted
intervention decision (insulate / heat-pump / PV / time-shift) made on EPC beliefs than the same
decision made on ground truth? That is the number that turns an epistemics exercise into a
business result, and it is the mission link (hard requirement 7): which homes gain from which
measure is HLC × weather × occupant arithmetic, and £/tCO₂e falls out of it.

**Coupled-triad binding (CLAUDE.md):** no world atom reaches L3 until the company has been tested
against it and the gap measured. `W1_11` and `W1_12` are therefore capped below L3 until `C14`
and `H_GAP` exist. That is recorded in the minted atoms' `depends_on`/`couples_with`, not merely
asserted here.

---

## 6. Coherence with existing work (hard requirement 6)

- **Weather hierarchy (`WEATHER_PHYSICS_HIERARCHY_DESIGN.md`)** — this design **is** L3 of that
  hierarchy done properly, not a fork. It keeps L1/L2 untouched and keeps the aggregation-
  consistency invariant. **One interface change is unavoidable and must be flagged loudly: L3
  currently consumes a DAILY MEAN temperature; the fabric model needs a HALF-HOURLY local weather
  series** (temperature, irradiance, wind). Whether W1_3/W1_4 already expose sub-daily local
  weather, or need extending, is the **first question any BUILD on `W1_11` must answer** — it is
  recorded as an open dependency on the minted atom rather than assumed either way.
- **Population coverage design** (`DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN`,
  `docs/market_research/POPULATION_COVERAGE_*.md`) — **reconcile with, do not layer over** (the
  staged doc is explicit). Fabric is a new marginal dimension in the joint population structure;
  it must enter the existing fusion/joint-structure machinery as a dimension with its own marginal
  and its own joint constraints (fabric correlates with tenure, income and region — a fuel-poverty
  joint that the coverage design already has machinery for), **not** as a bolt-on attribute
  sampled independently. Independent sampling would break the fuel-poverty joint and produce a
  population where nobody is both poor and in a leaky home, which is the single most important
  cell for the mission.
- **Segmentation / engagement / psychology** — untouched; attaches to Layer 2 via the existing
  occupancy fields (§2.2). One taxonomy, per the standing segmentation constraint.
- **Model-on-a-page (ratified)** — fabric physics is a refinement *inside* the existing
  premise-demand box; it adds no new box to the page. `inferred`, to confirm at FRAME close.
- **R12/R13** — calibration is blind to P&L. This is a **baseline** fidelity change (real-world
  fidelity), decided on fidelity grounds only, never because company results look wrong. Note the
  live risk and pre-empt it: **more realistic peaks will very likely worsen imbalance costs and
  margin.** That is a *correct* consequence of removing a smoothing artefact and must not be
  treated as a regression or tuned back. Recording it here, before the numbers move, so that the
  reaction is pre-committed rather than negotiated after the fact.
- **C-S2 (RNG substream discipline)** — the trace generator is a large new source of draws
  (appliance events, away days, setpoint jitter). Each **must** take its own named seeded
  substream, following the existing pattern in `premise_demand.py::_substream`. Without this, the
  new draws shift every downstream subsystem's sequence and replay determinism breaks.
- **C-S1 / C-S4** — unchanged; this is generation-side work behind existing interfaces.

---

## 7. Framed atoms (deliverable 2 — minted into `maturity_map.yaml` as proposals)

| Atom | What it is | Level | Stage | Key dependency |
|---|---|---|---|---|
| `W1_11_fabric_physics_core` | 2R2C thermal model + deadband controller + EPC→parameter mapping. The physics only; no population wiring. | 0→3 | frame | half-hourly local weather from W1_3/W1_4 (**open**) |
| `W1_12_premise_trace_generator` | Per-premise half-hourly gas+elec traces for the whole book: Layer 2 behaviour, appliance events, away days, LCT rewiring, fabric-dimension entry into the population joint. Must pass the two-level test. | 0→3 | frame | `W1_11`, population coverage design |
| `C14_thermal_parameter_inference` | Company-side inference of per-premise thermal parameters from meter reads + weather + EPC-class data, strictly through the wall. | 0→3 | frame | `W1_12`, `sim_interface` |
| `H_GAP_fabric_belief_truth_gap` | The harness loop: the two-level test as a standing failable control, plus the EPC-vs-actual and inferred-vs-actual gap metrics and their £ consequence. | 0→3 | frame | `W1_12`, `C14` |

All four are minted `provenance: proposal`, `loop_stage: frame`, level 0 — **DISCOVER/FRAME-workable
now, no BUILD authorised by this pass**, exactly as the staged doc requires. Each carries the
open questions above in its `simplifications` list so they cannot be lost.

---

## 8. Open questions carried forward (honest list)

1. **Does W1_3/W1_4 already produce sub-daily local weather?** Not established this pass. First
   question for `W1_11`. If not, extending it is a prerequisite and changes that atom's size.
2. **UKF vs a simpler estimator for `C14`** — deliberately left open (SIMPLICITY GUARD; start
   simple, escalate on evidence).
3. **SERL published statistics sufficiency** — `domain-knowledge` says probably yes for
   distributional targets; LCL named as fallback. **Requires a network-enabled DISCOVER pass to
   confirm; nothing here may be built on it until then.**
4. **Every numeric constant in §2.1** (COP-vs-temperature, deadband width, U-values by age band)
   is `domain-knowledge` and a **candidate to verify**, not a settled value.
5. **Computational cost** of a per-premise 2R2C simulation across the full book at half-hourly
   resolution over ten years is not estimated here. It is plausibly the binding constraint on
   `W1_12`'s design (and may force an archetype-and-perturb approach rather than true per-premise
   simulation). Flagged as a sizing question for that atom's FRAME.

---

*Doc-only. No code changed, no engine touched, no map level moved. Blast radius zero.*
