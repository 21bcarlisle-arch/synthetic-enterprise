# WEATHER PHYSICS HIERARCHY — design (FRAME, doc-only)

**Status:** DISCOVER/FRAME design output for `docs/staging/WEATHER_PHYSICS_HIERARCHY.md`
(director P1, QUEUE). Registered atoms this designs the detail for:
`W1_3_national_weather_signal` (L1), `W1_4_regional_weather_field` (L2),
`W1_5_premise_demand_shape` (L3), `W1_6_physics_price_signal` (L4),
`C13_weather_normalisation` (the coupled company twin), and the explicitly-LATER
follow-ons `W1_7_renewable_capacity_trends`, `W1_8_zonal_locational_pricing`,
`W1_9_dsr_flex_markets`. It writes **no simulation code, adds no tests, edits
neither `maturity_map.yaml` nor any engine** — those are BUILD's landing acts,
gated to Epoch 3 alongside `W1_2_generate_futures`. Everything below is specified
to be implementable against the *existing* price/weather machinery
(`sim/price_engine.py`, `sim/weather_engine.py`, `sim/generation_demand_history.py`,
`sim/system_prices_history.py`, `simulation/demand_model.py`, `simulation/household.py`)
per the SIMPLICITY GUARD (add discipline and one mechanism, not architecture).

**The director's steer is SET (verbatim: "the mechanism is ours ... Let's start with
the physics!").** The architectural decisions below — a latent blocking-high regime,
projection-based aggregation consistency, a layered premise response, price as pure
output — are the fixed frame. This doc designs the *detail* under them.

**Author's confidence tagging:** the four-layer structure, the two invariants, the
regime mechanism, and the price chain are the settled design. Numeric constants
(regime counts, persistence half-lives, covariance decay lengths, tolerances) are
proposals to be calibrated against real data at BUILD time and are flagged as such
in §8, not asserted as final.

---

## 0. The idea in one paragraph (so this doc stands alone)

GB power is a **coherent physical cascade**, not a set of independent draws. One
latent atmospheric regime (a **blocking high** vs a **mobile westerly**) sets whether
the country is cold-and-still or mild-and-windy, and it **persists for days**. That
national regime forces a joint national temperature/wind/solar signal (**L1**).
Regions deviate from the national signal, but **feasibly** — neighbours covary, and
the demand-weighted regional aggregate is made to equal the national signal *by
construction* (**L2**). Each premise's half-hourly demand is a **layered** response
to its own local weather and its own thermal/occupancy characteristics, and the
premises **add up to the country** (**L3**). Finally, the *same* L1 weather drives
national demand *and* renewable output; their difference is residual demand; the
merit order turns residual demand into a wholesale price — so **price is an output of
the physics, never an independent draw** (**L4**). The single correlation that has to
survive this cascade is **cold-and-still**: the coldest GB days are blocking-high
days with low wind, high heating demand, a tight margin, and a price spike. Draw
temperature and wind independently and that supplier-killing winter tail vanishes and
every hedge looks fine — a lie. The regime mechanism exists precisely to make that
tail *mechanistic and guaranteed*, not a fitted correlation coefficient that a
Gaussian copula would thin out.

---

## 1. The four-layer hierarchy (L1 → L4)

Each layer is **conditional on the one above** and draws from its **own named RNG
substream** (C-S2 discipline, §7): `national_regime`, `regional_field`, `premise_noise`,
`price` — so adding a draw in one layer can never shift another's outputs (the exact
failure the 01:09Z shared-life-event-RNG incident named). All four layers are
expressed in **weather/settlement-period terms without a hardcoded clock granularity**
(portability C-S1/§7): the design is stated per settlement period but the period
length is a parameter, not the number 48.

### 1.1 L1 — national weather (`W1_3`): a latent-regime mechanism, not a fitted copula

**Why not the existing engine as-is.** `sim/weather_engine.py` (Phase 3c) already does
a two-pass national-AR1-plus-regional-Cholesky construction with a *regime-switching
innovation covariance* ("standard" vs "stressed", where stressed = large wind-residual
magnitude). That is a real precursor and its calibration harness is reusable — but its
regime is a **variance switch fitted to wind residuals**, not a mechanism that
*jointly forces cold ∧ low-wind ∧ high-pressure*. A variance switch widens the spread;
it does not guarantee that the widened draws land in the cold-and-still corner. The
blocking-high state below is the mechanistic upgrade the director asked for.

**The regime states.** A hidden-Markov latent state `R_t ∈ {WESTERLY, BLOCKING_HIGH,
CYCLONIC}` on a daily step (period-length-parametric):

| State | Physical meaning | Temp anomaly | Wind | Solar/cloud |
|---|---|---|---|---|
| `WESTERLY` (mobile) | Atlantic fronts crossing GB — the GB default | near-seasonal-normal | **high** | variable/cloudy |
| `BLOCKING_HIGH` | anticyclone parked over/near GB; winter = the killer | **cold** (winter) / hot (summer) | **low** | clear (winter: low sun angle; summer: high irradiance) |
| `CYCLONIC` | deep low, storms | mild | **very high → cut-out** | cloudy |

Three states, not two, because the winter tail (`BLOCKING_HIGH`) and the storm tail
(`CYCLONIC` wind cut-out, the *other* renewable-drought mode) are physically distinct
and both matter for price; a two-state cold/mild switch conflates them. Three is the
SIMPLICITY-GUARD floor that still carries both tails — more states are a calibration
question deferred to §8, not designed in now.

**Transition / persistence structure.** A 3×3 transition matrix `P[R_t | R_{t-1}]`
with **strongly diagonal-dominant rows** so regimes persist for days (a blocking high
that dissolves after one day is not a blocking high). Persistence is parameterised as a
per-regime **expected dwell length** `d_R` (days), which maps to the self-transition
probability `P[R→R] = 1 − 1/d_R` for a geometric dwell. This is *the* temporal
autocorrelation the DoD demands — it lives in the regime chain, so temperature and wind
persist *together* rather than each carrying its own independent AR1. **Seasonality
enters the transition matrix, not the conditionals alone:** `P` is
month-of-year-indexed (`P_m`), so `BLOCKING_HIGH` is reachable and persistent in
Dec–Feb (winter anticyclonic blocking is a real, frequent GB pattern) and rarer/shorter
in summer. This is how "cold spells last" and "wind droughts persist for days" both fall
out of one object.

**Conditional distributions per regime.** Given `R_t`, draw the day's national
`(T̄, W̄, C̄)` (mean temperature, mean wind speed, mean cloud) from a per-regime,
**per-month** conditional (a small multivariate normal on deseasonalised residuals is
adequate — the tail dependence is carried by the regime, so the within-regime
correlation can stay simple). Seasonality enters here as the per-month **mean vector**
(the harmonic/deseasonalisation already in `weather_engine.py` is reused): `T̄` = month
climatology + regime anomaly + within-regime residual. Half-hourly translation
(diurnal temperature cosine, astronomical clear-sky solar envelope attenuated by cloud,
Ornstein-Uhlenbeck intraday wind) is **kept from the existing `weather_engine.py`
unchanged** — that machinery is calibrated and fit for purpose; only the day-level
driver is being replaced by the regime chain.

**How the cold∧still tail is GUARANTEED (not hoped for).** Because a *single* latent
state forces cold, low-wind, and clear-sky *jointly and simultaneously*, the joint
lower-left tail of (temperature, wind) is populated by construction every time
`BLOCKING_HIGH` is sampled in winter — its mass is `Σ_m∈winter π_m(BLOCKING_HIGH)`,
a controllable, non-vanishing quantity, **not** the product of two marginal tail
probabilities (which is what an independent draw, or a Gaussian copula with a modest
fitted ρ, collapses it to). This is the whole reason for the mechanism: tail dependence
is structural, not parametric.

**How we DEMONSTRATE it (the DoD's "show the tail").** A diagnostic
(`harness/**` / `tools/`, its own file scope) that:
1. Bins simulated winter days on the (temp-percentile, wind-percentile) plane and plots
   the joint density, highlighting the cold-and-still corner (bottom-decile temp ∧
   bottom-decile wind).
2. Overlays the **same plane from real GB history** (generator anchor: Elexon demand +
   wind/solar via `sim/generation_demand_history.py`, joined to real Open-Meteo/weather
   outturns) — the model's corner mass must be **≥** the real corner mass, per the DoD's
   explicit test: *if our worst week is milder than GB's real worst week, the physics is
   still wrong.*
3. Reproduces a **named real GB blocking-high week** (candidate anchors for BUILD to
   confirm against real data, not fabricated here: a cold-snap winter week such as the
   widely-documented cold-still spells GB suppliers hedge against) and asserts the model
   *can and does* produce weeks at least that severe on the joint (heating-demand ∧
   low-wind) axis. The specific week is chosen at BUILD from the real record; naming a
   date here without checking the data would violate Historical Ground Truth.

The diagnostic reports a single scalar — **joint-tail coverage ratio** = (model
cold-still corner mass) / (real cold-still corner mass) — that must be ≥ 1.0, and is
the L1 exit evidence.

### 1.2 L2 — regional weather (`W1_4`): feasible, spatially correlated, consistent by construction

**Construction.** For each region `r` in the region set `𝓡` (BUILD chooses the real GB
partition — GSP groups / DNO regions / the four existing `weather_engine.py` calibration
locations extended; a portability note, §7, keeps the count parametric), form:

```
X_r = X_national + Δ_r
```

where `X` is the weather vector (temp, wind, solar) and `Δ_r` is a **regional
deviation** drawn from a mean-zero spatial field with a **distance-keyed covariance**
`Cov(Δ_r, Δ_s) = σ² · k(dist(r,s))` — an exponential/Matérn kernel `k` whose
correlation length is calibrated so neighbours covary strongly and distant regions
weakly (Cornwall and Aberdeen are not independent draws; Cornwall and Devon nearly move
together). Cholesky-factor the regional covariance once (the existing `weather_engine.py`
Pass-2 Cholesky machinery is directly reusable) and draw `Δ = L·z`, `z ~ N(0, I)` from
the **`regional_field` substream**.

**The aggregation-consistency invariant, precisely (regional → national).** Let `wᵣ` be
region `r`'s **demand weight** (population/demand share, `Σ_r wᵣ = 1`). Define the
reconciliation residual for weather variable `v` at period `t`:

```
ρ_agg(t) = Σ_r wᵣ · X_{r,v}(t)  −  X_national,v(t)
INVARIANT (I1):  |ρ_agg(t)| ≤ tol_agg   for every variable v and every period t
```

A raw spatial draw does **not** satisfy I1 (the weighted deviations don't sum to zero).
So the design is **projection, not luck**: after drawing `Δ`, apply a **rescale/projection
step** that removes the demand-weighted mean deviation —

```
Δ'_r = Δ_r − Σ_s w_s · Δ_s          # subtract the demand-weighted mean deviation
```

— which makes `Σ_r wᵣ · Δ'_r = 0` **identically** (it is an algebraic projection onto the
zero-weighted-mean manifold), hence `Σ_r wᵣ · X_r = X_national` exactly, up to floating
point. I1's `tol_agg` is therefore a **numerical** tolerance (machine-epsilon scale),
not a modelling fudge: consistency is *structural*. "Every region freezing while national
is mild" is not merely unlikely — it is **off the manifold and cannot be constructed.**

**R15 mutation test for I1.** The invariant must be able to FAIL. Mutation:
after the projection, **perturb one region off-manifold** — add a fixed offset `ε ≫
tol_agg` to `X_{r*,temp}(t)` for a single region `r*` (e.g. drive one region 10 °C
colder while leaving the rest). Assert the reconciliation check **FIRES**:
`|ρ_agg(t)| > tol_agg`. A second mutation attacks the *weights* (swap to uniform weights
while the field was projected under demand weights) and asserts the residual reopens.
The control is non-tautological because the checker recomputes `Σ_r wᵣ X_r` from the
region series and compares to the **independently held** national series — it does not
re-derive national from the same projected deviations it is checking (independence, per
R15's TAUTOLOGY pattern). Fail-open guard: a missing region, an empty weight vector, or
a NaN deviation must make the check **fail loud**, not pass (R15 FAIL-OPEN pattern).

**Regional weather is COMPANY-KNOWABLE.** L2 outputs sit on the **public side of the
wall** — regional forecasts and outturns are genuinely published in reality. The company
twin (§6) is allowed to read them. What it may *not* read is the premise-level truth (L3)
or the regime label (L1 latent state) — those are SIM internals.

### 1.3 L3 — premise demand shape (`W1_5`): layered, not flat; binds to W2 archetypes

Each premise `i`'s half-hourly demand is a **layered** composition, not a single draw:

```
d_i(t) = baseload_i(t)
       + heating_i · g_heat( T_{r(i)}(t) , thermal_i , heating_type_i )    # temp-driven, regional
       + occupancy_i · s_occ(t, archetype_i)                              # diurnal/day-type shape
       + solar_offset_i · g_solar( I_{r(i)}(t) )                          # if the premise self-generates
       + η_i(t)                                                           # idiosyncratic noise
```

where `r(i)` is premise `i`'s region, so it responds to **its own local (L2) weather**,
`T` and `I` are that region's temperature and irradiance, and `g_heat` is a thermal
response (heating-degree-day-style, convex below the heating threshold) whose slope is
governed by the premise's **thermal performance and heating type**. The idiosyncratic
noise `η_i` draws from the **`premise_noise` substream** — independent across premises,
independent of the weather and price substreams.

**Binding to the W2 customer archetypes.** The premise's characteristics are **not new
state** — they are read from the existing archetype layer:
- `archetype_i`, `heating_type_i` (heating system), `thermal_i` (EPC/insulation), and
  `occupancy_i` come from `simulation/household.py`'s `Household` (already carries
  `property_type`, `epc_rating`, `heating_system`, `insulation`, solar/battery/EV) and
  the archetype distributions owned by `W2_1_archetype_layers`
  (`simulation/household_segments.py`, already L3).
- Which premises exist / their mix comes from `W2_2_population_draw`
  (`simulation/population_draw.py`) — so L3 rides the *same* population the affordability
  cluster varies over, and adding weather response draws must not disturb the population
  draw (substream isolation, proven by `test_substream_isolation_*`).
- The half-hourly *shape* templates (`s_occ`) reuse `simulation/demand_model.py`'s
  existing archetype demand curves; L3 **modulates** them by local weather rather than
  replacing them.

This keeps L3 a *response function* over existing archetype state, honouring the
"second product fits inside this brain" portability lens (the demand response is keyed
by premise characteristics, not by fuel-hardcoded assumptions).

**The second aggregation-consistency invariant (premise → national demand).** Let `nᵢ`
be the number of real premises each simulated premise `i` represents (a scaling weight;
at the current ~31-account cast this is a large scale-up factor, at full population it
is ~1). Define:

```
ρ_dem(t) = Σ_i nᵢ · d_i(t)  −  D_national(t)
INVARIANT (I2):  |ρ_dem(t)| ≤ tol_dem   for every period t
```

where `D_national(t)` is the L4 national demand implied by L1 national weather (§1.4).
As with I1, this is enforced by **construction, not luck**: after composing the premise
demands, apply a **single national rescale factor** `α(t) = D_national(t) / Σ_i nᵢ d_i(t)`
and set `d'_i(t) = α(t)·d_i(t)`. A multiplicative rescale preserves each premise's
*shape and relative weather response* while forcing the aggregate to reconcile — "if the
premises don't add up to the country, the physics is wrong" becomes impossible by
construction. `tol_dem` is numerical. (Design note: rescale is multiplicative here, not
additive-projection as in I1, because demand is a positive quantity and its cross-premise
*ratios* — who is weather-sensitive vs flat — are the load-bearing information the L3
layering exists to create; an additive projection would distort them.)

**R15 mutation test for I2.** Mutation: **perturb one premise's response off-manifold**
after the rescale — e.g. multiply one premise's heating coefficient by 5 (a
super-responder) without re-running the rescale, or drop a premise's `nᵢ` scaling.
Assert I2 **FIRES**: `|ρ_dem(t)| > tol_dem`. Independence: the checker holds
`D_national(t)` from the L4 weather→demand relationship (an **independent** source) and
compares the summed premises to it — it does not define national as the premise sum (that
would be the TAUTOLOGY R15 forbids; the national demand is anchored to the
weather→demand curve, §1.4, not to the premises). Fail-loud on a missing premise, a zero
`Σ nᵢ d_i` (division guard), or a NaN.

### 1.4 L4 — price as a derived output (`W1_6`): the one-coherent-draw chain

**Price is never drawn.** The chain, in order, all downstream of the *same* L1 national
weather:

```
(1) national weather  X_national(t)          [L1]
(2) national demand   D_national(t) = f_demand( T_national(t), day_type, season )
(3) wind output       G_wind(t)     = capacity_wind · power_curve( W_national(t) )
    solar output      G_solar(t)    = capacity_solar · clearsky( t ) · (1 − cloud(t))
(4) residual demand   RD(t) = D_national(t) − G_wind(t) − G_solar(t)
(5) wholesale price   P(t) = gas_floor(gas_price) · ( RD(t) / dispatchable_margin )^γ
```

- **(2)** the weather→demand relationship `f_demand` is fitted against **real** Elexon
  national demand vs weather (`sim/generation_demand_history.py`); `sim/weather_hdd.py` /
  `sim/weather_price_sensitivity.py` already carry the heating-degree-day sensitivity
  primitives this reuses.
- **(3)** wind and solar are **functions of the SAME L1 weather** — this is the crux.
  `G_wind` uses the **existing idealised turbine power curve already in
  `sim/price_engine.py`** (cut-in 3 m/s, cubic ramp to rated at 12 m/s, cut-out 25 m/s).
  Solar uses the clear-sky-minus-cloud envelope already in `weather_engine.py`. Because
  both read L1's `W_national` and `cloud`, a blocking-high day *automatically* produces
  low `G_wind`, and there is no way to draw "cold" without also getting "low wind output"
  — the coherence is structural.
- **(5)** the merit-order price is the **existing `sim/price_engine.py`** engine:
  `gas_floor_price()` gives the £/MWh(e) floor from gas price and thermal efficiency, and
  `system_margin_price()` applies the convex margin shape
  `P = P_gas_floor · (demand / renewable_generation)^γ` — L4 supplies it *residual
  demand over dispatchable margin* as the tightness ratio. **This is a wiring change, not
  a new engine:** L4's contribution is feeding the price engine inputs that are all
  descendants of one weather draw, replacing today's separately-sourced demand/renewable
  series.

**The one-coherent-draw chain, demonstrated (cold-still → spike).** A single
`BLOCKING_HIGH` winter day flows deterministically down the chain: high heating demand
`D↑` (step 2) **∧** low wind output `G_wind↓` (step 3, same low `W`) → residual demand
`RD↑↑` (step 4) → tight margin ratio → **price spike `P↑↑`** (step 5). The diagnostic
(§1.1) is extended to plot `P(t)` against the (temp, wind) plane and confirm the
price spike sits in the cold-and-still corner — a spike that appears there **without
being drawn** is the proof the physics closed. The **anti-pattern this forbids**: any
code path that samples price (or SSP) independently of this chain. L4's exit test
includes a **grep-plus-assertion** that price in the physics path is *only* ever the
return of the merit-order chain, never a separate random draw (an epistemic check
mirroring the wall greps elsewhere).

**Point-in-Time Blindfold (Law 2) note.** L4 price is knowable at the simulated "now"
— it is the outturn of that period's realised weather, not a hindsight read. The company
sees the *published* price after settlement, on the same clock as reality; nothing in the
chain leaks a future regime state to the business layer.

---

## 2. The two aggregation-consistency invariants (formal, with mutation tests)

Restated together for the phase-close and R15 record. Both are **structural (by
construction), numerically toleranced, and mutation-tested** — the pattern the director
required ("consistency BY CONSTRUCTION, not by luck").

| # | Invariant | Formal statement | Enforced by | R15 mutation (must FIRE) | Independence (anti-tautology) |
|---|---|---|---|---|---|
| **I1** | regional → national weather | `\|Σ_r wᵣ X_r(t) − X_nat(t)\| ≤ tol_agg` ∀ v,t | demand-weighted-mean projection `Δ'_r = Δ_r − Σ w_s Δ_s` | offset one region's temp by ε≫tol; swap weight vector | checker recomputes weighted sum vs **independently held** national series |
| **I2** | premise → national demand | `\|Σ_i nᵢ d_i(t) − D_nat(t)\| ≤ tol_dem` ∀ t | multiplicative national rescale `α(t)` | ×5 one premise's heating coeff post-rescale; drop an `nᵢ` | national demand held from **weather→demand curve**, not defined as the premise sum |

Both mutation tests must additionally assert **fail-loud** on missing/empty/NaN/zero
inputs (R15 FAIL-OPEN and FAIL-SILENT patterns): an invariant that silently passes when
a region is absent or the checker can't run is a FAILED check, not a pass. The mutation
tests are the atoms' L-promotion evidence — no L3 for `W1_4`/`W1_5` without them (per
R15: no control counts unless a mutation test proves it fires).

---

## 3. The cold-and-still joint dependence (the correlation that matters most)

Consolidated because it is the single most important design property.

- **Mechanism (not a coefficient):** the latent `BLOCKING_HIGH` regime (§1.1) is a
  *common cause* that forces cold ∧ low-wind ∧ clear jointly and persistently. Tail
  dependence is carried by the shared latent state, so it does **not** thin out the way a
  Gaussian-copula tail does (a copula with a fitted ρ under-weights the corner — exactly
  the failure the directive names).
- **Guarantee:** corner mass = `Σ_m∈winter π_m(BLOCKING_HIGH)`, a controllable
  non-vanishing quantity set by the winter transition matrix, not the product of two
  marginal tail probabilities.
- **Demonstration (DoD "show the tail"):** the joint-density diagnostic (§1.1) with the
  **joint-tail coverage ratio ≥ 1.0** against real GB history, plus reproduction of a
  real GB blocking-high winter week (date chosen from the real record at BUILD). Extended
  at L4 to show the **price spike** lands in the same corner.
- **Same family, also carried:** solar anti-correlated with heating demand
  (seasonal: winter = high heat ∧ low sun angle; diurnal: evening peak ∧ no sun) falls
  out of the per-month regime conditionals and the astronomical solar envelope; **wind
  droughts persist for days** falls out of `BLOCKING_HIGH`'s dwell length `d_R`.

---

## 4. Price as derived output — what existing code it plugs into

| Chain step | Existing module reused | What L4 changes |
|---|---|---|
| national demand from weather | `sim/generation_demand_history.py` (real Elexon demand, generator anchor), `sim/weather_hdd.py`, `sim/weather_price_sensitivity.py` | feeds L1-derived national temperature into the fitted `f_demand`, replacing separately-sourced demand |
| wind output from wind speed | `sim/price_engine.py` turbine power curve (cut-in/cubic/rated/cut-out) | feeds L1's `W_national`, so wind output is a function of the same weather |
| solar output | `sim/weather_engine.py` clear-sky-minus-cloud envelope | feeds L1's cloud/irradiance |
| residual demand → price | `sim/price_engine.py` `gas_floor_price()` + `system_margin_price()` (`P = P_gas_floor·(D/G)^γ`) | supplies residual-demand/margin as the tightness ratio |
| calibration/validation target | `sim/system_prices_history.py` (real historical SSP) | the price chain is validated against real SSP before it is trusted for forward projection — the calibration gate `price_engine.py` already documents |

**No new price engine is built.** L4 is a wiring layer that guarantees the price
engine's *inputs* are all descendants of one coherent weather draw. This is the "single
most important correlation" made to hold end-to-end without touching the merit-order
maths.

---

## 5. Independence anchoring (anti-marking-own-homework)

The generator and validator anchors are **different sources**, named explicitly (R:
anti-marking-own-homework; the company never validates against SIM ground truth):

| Role | Anchor | Used for |
|---|---|---|
| **GENERATOR** | real historical **weather↔demand↔wind/solar** relationships — Elexon demand + wind/solar (`sim/generation_demand_history.py`), real weather outturns (Open-Meteo, the `weather_engine.py` calibration set), real SSP (`sim/system_prices_history.py`) for the price calibration gate | fitting `f_demand`, the power curve, the regime conditionals, γ |
| **VALIDATOR** (must be a DIFFERENT source than the fitted series) | independent **published sub-national statistics** — DESNZ/BEIS *sub-national energy consumption statistics* (regional gas+electricity consumption), regional **degree-day** publications, and published **system demand** series **not** used in the generator fit | checking the L2 regional field's demand-weighted aggregate and the L3 premise aggregate reproduce real regional consumption *shares* and real degree-day gradients |

Concretely: the L1/L4 physics is *fit* on the weather↔demand↔price record; it is
*validated* on regional consumption/degree-day statistics it never saw during fitting. If
the two disagree, the physics is wrong — that is the point of keeping them separate. The
specific published datasets are named as classes here (DESNZ sub-national consumption,
Met Office/BEIS degree days); BUILD confirms the exact current dataset editions against
the real sources rather than fabricating a citation (Historical Ground Truth).

**Wall corollary:** the company-side twin (§6) validates against **public** regional
forecasts/outturns and its **own** meter reads — *never* against L1's latent regime label
or L3's true premise thermal parameters. The harness (which sees both sides) is the only
layer that scores the gap.

---

## 6. The coupled twin `C13_weather_normalisation` + its gap + the hedging frontier

Per COUPLED_TRIAD_DESIGN: this is the company-response half of `W1_5`/`W1_6`. Under the
binding rule, **`W1_5` cannot reach L3 until `C13` has been run against it and the gap
measured** (`couples_with: [W1_5_premise_demand_shape]`, symmetric).

### 6.1 What the company can and cannot see (the wall)

- **CAN see (company-knowable):** published national **and regional** forecasts and
  outturns (L2 is public); wholesale prices (L4 outturn); its **own meter reads**
  (confounded aggregate consumption of *its* book, via
  `company/interfaces/sim_interface.py`).
- **CANNOT see:** each premise's **true thermal characteristics** (L3 `thermal_i`,
  `heating_type_i` ground truth), the **counterfactual** demand under a different weather,
  the **latent regime label**, or the true weather-sensitivity of its book.

**Therefore the gap:** the company must **infer its book's weather sensitivity —
weather-normalisation — from confounded meter data.** This is genuinely hard and, per the
directive, genuinely done badly in the industry (weather-correction is a known
error-prone step in real supplier settlement/forecasting).

### 6.2 The gap metric (per COUPLED_TRIAD_DESIGN §1)

`C13`'s belief `b`: a **predicted demand** for its book under a *given, observed weather
outturn* — i.e. the company's fitted weather-normalisation model applied to the realised
weather. The hidden truth `θ`: the **actual** book demand the SIM realised under that same
weather outturn (harness-side, reading L3 ground truth).

```
raw_gap(W1_5, C13) = (1/|P|) Σ_periods | D̂_book(weather_t) − D_book_actual(t) |
g0                 = the same error from a NO-SKILL baseline — flat degree-day
                     correction using the NATIONAL sensitivity applied to the whole book
                     (no book-specific, no regional discrimination)
gap                = raw_gap / g0        # dimensionless, per COUPLED_TRIAD reading convention
```

Reading convention (identical to every coupled pair): `gap→0` = perfect recovery
(**structurally unreachable** — reaching it means the observables leaked L3 thermal truth,
an epistemic-wall defect, not a triumph); `gap→1` = no better than the blind national
degree-day correction; `0<gap<1` = learned some book-specific/regional structure but not
all (the honest steady state); `gap>1` = worse than blind (a harmful normalisation model
— red). **Trend is the story:** `Δgap` falling = the company is learning its book's
weather shape; static = not adapting (a finding); rising = regressing. Basis note (R14):
a gap is a ratio, no settled/billed/banked clock, but the pair states its measurement
basis (which book, which weather window, as-of date) so a falling trend can't be an
artefact of a changed population/weather window.

### 6.3 The national-vs-regional hedging frontier (make BOTH extremes bite)

This is the *strategy surface* the physics exists to create. GB has **no regional
forward market** (the zonal-pricing debate is precisely about this — see the LATER atom
`W1_8`), so regional basis cannot be hedged today. The SIM must make both ends of the
frontier cost real money:

- **Hedge to the NATIONAL forecast** (the liquid, cheap instrument) and a
  **regionally-skewed book** (e.g. concentrated in a region that deviates cold-and-still
  harder than the national average) is left **exposed** when its region deviates — the
  L2 regional field *guarantees* such deviations exist and the aggregation invariant
  *guarantees* they don't wash out into an implausibly mild national mean. The residual
  regional basis shows up as a P&L miss the national hedge didn't cover.
- **Protect regionally** (proxy-hedge, over-hedge, buy shaped/bespoke cover) and you
  eat **basis risk** (the proxy isn't your region), **illiquidity** (thin/absent regional
  instruments), and **cost** (the premium for bespoke shape).

Where the company sits on that frontier is **visible strategy** — surfaced through the
coupled-gap reporting (COUPLED_TRIAD §5, digest + Proof door). A company that hedges
naively to national will show a *widening* `C13` gap and a P&L basis leak in cold-still
weeks; a company that over-protects will show cost drag. Neither extreme is free — that
is the cat-and-mouse the directive demands, and it is only *possible* because L2 makes
regional deviation real and L4 makes cold-still tighten price.

---

## 7. Portability + scale constraints honoured (cited)

- **No hardcoded clock speed / settlement granularity (portability).** All four layers
  are specified per *settlement period* with the period length a **parameter**, not the
  literal 48; the regime chain steps on a *day* defined as `N` periods, `N` configurable.
  Monetary treatment (price) stays in `sim/price_engine.py`'s existing units, not
  re-hardcoded.
- **C-S1 event-arrival tolerance.** The company twin `C13` consumes weather
  forecasts/outturns, prices, and meter reads as they arrive — it must weather-normalise
  correctly if reads arrive **one at a time, late, or out of order** (no assumption of a
  complete batch). The gap computation is defined over whatever periods have arrived,
  labelled with its coverage basis (§6.2).
- **C-S2 deterministic replay + named RNG substreams.** Four **named, seeded substreams**
  — `national_regime`, `regional_field`, `premise_noise`, `price` — each derived in
  isolation exactly as `simulation/population_draw.py::_substream()` already does
  (SHA-256 of base seed + salt → an independent `random.Random`), so **adding a draw in
  one layer can never shift another's outputs** (the 01:09Z shared-RNG incident's lesson;
  proven-testable by the existing `test_substream_isolation_*` pattern). Replaying a
  history reproduces identical weather, demand, and price.
- **C-S3 asynchronous wall contracts.** `C13`'s forecast-request and outturn-response are
  **separate events in time**, never same-period resolution — the company forecasts,
  *then later* sees the outturn; the gap is computed on the realised outturn. This is the
  same law as the approval-interface latency finding — one mechanism.
- **C-S4 persistence behind an interface.** Weather/demand/price series persist only via
  the existing append-only event-log abstraction; the storage form stays swappable.
- **C-S5 time-scale invariance declaration.** The regime chain and the diurnal/intraday
  shapes are **not** fully time-scale invariant (a daily regime step and a half-hourly
  diurnal cosine assume a specific coupling of day↔period). This is **registered as a
  named simplification** (per R10/C-S5): at L3+, each layer states its time-scale
  assumption; the period-count `N` is the single knob, and any sub-daily regime dynamics
  are an explicit LATER extension, not claimed now.
- **SIMPLICITY GUARD.** No new stores, brokers, or adapter cathedrals: L1 upgrades the
  *day-driver* of the existing `weather_engine.py`; L2 reuses its Cholesky; L4 wires the
  existing `price_engine.py`. The design *adds discipline* (a latent regime, two
  projections, four substreams, two invariants) — **not architecture**.

---

## 8. Explicitly LATER (registered follow-ons, not designed here)

Per the director's sequencing ("Physics first ... renewable trends etc afterwards"),
these are sequenced follow-on atoms — **noted, not designed**:

- **`W1_7_renewable_capacity_trends`** — growing wind/solar capacity and generation-mix
  evolution over the 2016→2025→forward window (today L4 treats capacity as a
  calibrated constant; the *trend* is a later layer on top).
- **`W1_8_zonal_locational_pricing`** — the regional-basis market that does **not** exist
  today; this is exactly the missing market that makes §6.3's frontier bite. Building it
  later *creates* the hedge the company currently cannot buy — a natural next turn of the
  cat-and-mouse.
- **`W1_9_dsr_flex_markets`** — demand-side response / flexibility, which would let
  premises (L3) respond to price, closing a feedback loop deliberately left open now.
- **EV / heat-pump adoption geography** — a structural shift in the premise (L3) thermal
  and load response, regionally uneven; a later reshaping of `g_heat`/`baseload`, not a
  physics change now.

Each depends on the L1–L4 physics landing first (`depends_on` already wires
`W1_7/8/9 → W1_6` in the map). Registering them keeps the sequence visible without
starting them.

---

## 9. Open questions / honest simplifications

- **Regime count (3) and dwell lengths** — three states carry both tails (blocking-high
  cold-still and cyclonic storm-drought); whether a fourth (e.g. a distinct summer
  anticyclone) earns its keep is a **calibration question** answered against real
  regime-frequency data at BUILD, not asserted now.
- **Region partition and demand weights `wᵣ`** — GSP groups vs DNO regions vs an extended
  version of the four existing `weather_engine.py` locations; the demand weights must come
  from a **real** source (DESNZ sub-national consumption) and are validator-anchored, not
  fitted. Named as the first BUILD decision.
- **Covariance kernel and correlation length** (`k`, `σ²`) — exponential vs Matérn and the
  length scale are fitted to real inter-region weather correlations; proposed, not fixed.
- **γ and the dispatchable-margin denominator in L4** — inherited from the existing
  `price_engine.py` calibration gate against real SSP; L4 does not re-open the merit-order
  calibration, it feeds it coherent inputs. If the coherent-input price fails the SSP
  calibration gate, that is a finding about the *inputs*, surfaced not silently retuned
  (R12 anti-goal-seek: price is a diagnostic, never a target).
- **Multiplicative I2 rescale vs additive** — the multiplicative national rescale
  preserves premise *ratios* (the load-bearing weather-sensitivity information) but
  assumes the national/premise-sum ratio is roughly uniform across the book within a
  period; if a period's rescale factor is far from 1, that is itself a signal the
  weather→demand curve and the premise layering disagree — worth logging, not hiding.
- **Small-cast statistical power** — at the current ~31-account cast the L3 aggregate and
  the `C13` gap are noisy; `W2_2_population_draw` is the real fix. Until then the gap and
  the joint-tail diagnostic are **directional, labelled provisional**, not precise scores
  — consistent with COUPLED_TRIAD's "small scale now" and LAW A (the plan is a
  diagnostic).
- **Named real-week anchor** — the specific GB blocking-high winter week for the
  demonstration is chosen from the **real record at BUILD** (Historical Ground Truth
  forbids fabricating a date here); the design fixes the *test* (joint-tail coverage ratio
  ≥ 1.0 against real history), not the calendar date.

---

*Sources: `docs/staging/WEATHER_PHYSICS_HIERARCHY.md` (director P1 spec);
`docs/design/COUPLED_TRIAD_DESIGN.md` (gap metric + coupling rules);
`sim/price_engine.py` (merit-order: `gas_floor_price`/`system_margin_price`, turbine
power curve), `sim/weather_engine.py` (Phase-3c two-pass national-AR1 + regional-Cholesky
precursor + regime-switching covariance), `sim/generation_demand_history.py` (real Elexon
demand + wind/solar generator anchor), `sim/system_prices_history.py` (real SSP validation
target), `sim/weather_hdd.py` / `sim/weather_price_sensitivity.py` (HDD/sensitivity
primitives), `simulation/demand_model.py` + `simulation/household.py` +
`simulation/household_segments.py` (premise/archetype state), `simulation/population_draw.py::_substream()`
(RNG substream discipline); maturity_map atoms W1_3/W1_4/W1_5/W1_6/C13/W1_7/W1_8/W1_9.
Rules referenced inline: R10, R12, R13, R14, R15, MAKE_IT_STICK, EPOCH_GATING,
PORTABILITY + SCALE (C-S1..C-S5), SIMPLICITY GUARD, COUPLED_TRIAD, LAW A, Historical
Ground Truth + Point-in-Time Blindfold.*
