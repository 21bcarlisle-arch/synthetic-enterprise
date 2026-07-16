# FRAME — W1_3_national_weather_signal

**Atom:** `W1_3_national_weather_signal`
**Lane:** `W1_market_weather` · **Dial:** 3 · **level_current:** 0 · **level_target:** 3
**depends_on:** `W1_2_generate_futures`
**Stage:** FRAME/DISCOVER (Lane-3, doc-only). BUILD-gated (`loop_stage: idle`). No build code proposed here.

---

## 1. What this atom is & real-world grounding

A **coherent, joint, national weather signal** for Great Britain: a time series of three
correlated variables — **temperature**, **wind** (capacity-factor-relevant wind speed), and
**solar** (irradiance / PV capacity factor) — emitted at the sim's settlement cadence (nominally
half-hourly, aggregatable to daily) with **realistic temporal autocorrelation**.

Weather is the single largest exogenous driver of a UK energy supplier's fortunes. It moves
**both sides of the book simultaneously**:

- **Demand** — heating load tracks temperature via heating-degree-days. A cold spell raises
  gas/electric heating demand across the whole book at once; there is no diversification against
  national temperature because every customer feels the same weather.
- **Renewable supply / wholesale price** — wind and solar generation set the residual demand the
  conventional fleet (and the wholesale market) must cover. Low wind + low solar means high
  residual demand, high System Buy Price, and expensive imbalance for anyone short.

The atom produces the **L1 NATIONAL** signal — one number per variable per timestep for GB as a
whole. It is the aggregate that the later **W1_4 regional field** (L2 spatial layer) must
reconcile to (see §5). This atom is not a regional/grid-square model; it is the national envelope.

---

## 2. The physics to capture

The central, non-negotiable physics is **temporal persistence**. Real weather is driven by
synoptic systems (anticyclones, Atlantic depressions) that sit over or track across the country on
**multi-day to multi-week** timescales. Consequences:

- **Temporal autocorrelation (persistence).** Temperature, wind and solar each have a
  characteristic autocorrelation length. Cold *spells* last; wind *droughts* last. A blocking
  high in winter can park still, cold, clear-then-foggy conditions over GB for a week or more.
  *Benchmark required (source: Open-Meteo / ERA5 reanalysis)* for the daily-lag autocorrelation
  function of each variable and the empirical distribution of spell durations — do not fabricate
  the numbers; calibrate them.

- **Cross-correlation / joint structure.** The variables are not independent. The supplier's
  nightmare is the **co-occurrence** of cold + still + dark: a winter anticyclone gives
  simultaneously **high heating demand, low wind, and low solar** — the classic
  **Dunkelflaute** ("dark doldrums"). This is a property of the *joint* distribution: the tail of
  the joint (cold ∧ still ∧ dark) is far fatter than the product of the marginal tails. Capturing
  the marginals correctly but sampling them independently **destroys exactly the event that breaks
  a supplier**.

- **Seasonality.** Marginals and correlations are season-dependent: solar has a strong annual
  cycle (near-zero contribution mid-winter), Dunkelflaute risk concentrates in
  Nov–Feb, summer demand is weather-light. Persistence structure itself shifts by season.

**Why IID noise is wrong.** Independent, identically-distributed sampling reproduces the mean and
variance of each variable but **systematically under-samples the tail events that matter**. Under
IID, a 5-day cold-and-still spell has probability (p_cold · p_still)^5 — vanishingly rare — so the
company would (correctly, given that world) learn to hold almost no hedge and carry thin capital.
A supplier's ruin is driven by the *persistence and joint occurrence* of adverse weather (sustained
peak demand met at sustained peak imbalance prices), not by any single half-hour. A world without
autocorrelation is a world with no Dunkelflaute, and a company optimised against it is dangerously
mis-calibrated. **The autocorrelation IS the physics; it is not noise to be smoothed away.**

---

## 3. Method options

All options must be **calibrated to real UK statistics** from reanalysis, and must reproduce (as
acceptance targets) the empirical marginals, the per-variable autocorrelation functions, the
spell-duration distributions, and the joint tail (Dunkelflaute frequency/duration). Numbers to be
sourced, not invented — *benchmark required (source: Open-Meteo / ERA5 reanalysis)*.

- **(a) Multivariate autoregressive (VAR / VARMA).** A vector-autoregressive model on the
  (temp, wind, solar) vector, with seasonally-varying coefficients, captures both persistence
  (AR lags) and contemporaneous cross-correlation (residual covariance). Pros: transparent,
  cheap, replayable, parameters map to physics. Cons: Gaussian-ish innovations may under-fit the
  joint *tail* (the very thing that matters) unless residuals are heavy-tailed / regime-switched.

- **(b) Copula-based joint sampling.** Fit realistic marginals per variable (e.g. skew for
  temperature, bounded/heavy for wind and solar), then couple them with a copula chosen for
  **tail dependence** (e.g. a t- or Gumbel-family copula) so cold∧still∧dark co-occur at the
  observed rate. Persistence added via a copula on lagged states or a hidden regime. Pros: direct
  control of the joint tail. Cons: more moving parts; persistence + joint-tail together is
  fiddly to fit and validate.

- **(c) Block bootstrap of reanalysis.** Resample *contiguous multi-day blocks* of real historical
  (temp, wind, solar) jointly. By construction this preserves persistence, cross-correlation, and
  the real joint tail — you are replaying real weather blocks. Pros: physically faithful "for
  free", no distributional assumptions. Cons: limited to observed history's variety (won't
  synthesise unseen severities), block-boundary discontinuities, finite sample of extreme spells.

- **(likely) Hybrid / regime-switching.** A hidden weather-regime layer (e.g.
  cyclonic / anticyclonic-blocking / mixed) with persistent regime dwell times, and a within-regime
  generator (VAR or block-bootstrap) per regime. This most directly encodes the physics: regimes
  *are* the synoptic systems, dwell-time persistence *is* the spell length, and the anticyclonic
  regime *is* Dunkelflaute. Recommended for L3; simpler forms suffice for L1/L2.

Method choice is a BUILD-time decision; this FRAME fixes the **acceptance targets** the chosen
method must hit, not the method.

---

## 4. COUPLED TRIAD framing (the gap is the score)

- **SIM** generates the national weather **ground truth** — the true (temp, wind, solar) path,
  including its persistence and joint tail. This is a WORLD/SIM capability.
- **COMPANY** observes **only realised weather and its consequences** — the demand it actually
  meters, the generation/prices it actually sees, degree-days it can compute from public
  observations. It **never** reads the SIM's weather-model internals (regime states, AR
  coefficients, copula parameters, the forward realisation). Per the epistemic wall, the company's
  demand-forecast and hedge models are approximations built from *observed outcomes* — a real
  supplier calibrates load models on historical weather + published forecasts, and is allowed to
  be wrong about persistence and tail co-occurrence.
- **HARNESS** measures the **belief-vs-truth gap**: does the company's demand/hedge/capital posture
  **survive persistent adverse spells** it did not fully anticipate? Concretely — inject a
  calibrated Dunkelflaute / cold-spell and measure imbalance cost, hedge shortfall, capital
  drawdown vs. the company's own pre-spell expectation. A company that hedges as if weather were
  IID will show a large, quantified gap under a persistent tail spell; that gap **is the score**
  for this coupled pair.

Per COUPLED_TRIAD: this WORLD atom may not reach L3 until the company has been tested against it
and the gap measured; correspondingly no demand/hedge company capability is "complete" until it has
faced a weather world that can defeat it (a real Dunkelflaute).

---

## 5. Level decomposition (target L3)

- **L1 — national signal, persistence present.** Single GB series for (temp, wind, solar) with
  correct **marginals** and **per-variable temporal autocorrelation** (spells persist), plus basic
  **seasonality**. Contemporaneous cross-correlation present but joint-tail fidelity not yet
  validated. Deterministic + replayable (§7). Consumable by demand + generation layers.

- **L2 — joint tail validated.** The **joint distribution** is calibrated so cold∧still∧dark
  co-occurrence (Dunkelflaute frequency and duration) matches the reanalysis benchmark within a
  stated tolerance. Seasonally-varying correlation. Harness has a Dunkelflaute injection scenario
  and measures the company gap on it.

- **L3 — full physical fidelity + reconciliation.** Regime structure (or equivalent) reproducing
  spell-duration distributions and severe multi-week blocking; validated against reanalysis
  acceptance targets for marginals, ACFs, spell durations, and joint tail. **Reconciliation
  invariant with W1_4:** when the L2 spatial/regional field (`W1_4`) exists, its regional series
  **must aggregate (population-/capacity-weighted) back to this national L1 signal** within
  tolerance — a hard invariant, not a soft check. The national signal is the anchor; the regional
  field is a disaggregation of it.

*(This atom owns the NATIONAL L1 signal. The spatial field is W1_4's L2 layer; the two are coupled
by the aggregation-consistency invariant above.)*

---

## 6. Dependencies & sequencing

- **depends_on: `W1_2_generate_futures`.** Futures/forward-curve generation is upstream; the
  weather signal feeds demand and renewable-generation realisations that price against those
  curves, so the futures scaffold and the market-data seam it establishes come first.
- **Downstream consumers:** national demand model (degree-day heating load), renewable generation
  model (wind/solar capacity factors → residual demand), and thereby wholesale/imbalance pricing
  and the company's hedge/capital decisions. Also the anchor for `W1_4` (regional field).
- **What unblocks BUILD:** (i) `W1_2` at its required level; (ii) reanalysis benchmark statistics
  actually pulled (Open-Meteo / ERA5) — marginals, ACFs, spell-duration and joint-tail targets —
  since these are the acceptance criteria and must exist before a generator can be validated;
  (iii) a chosen method (§3) and the SIM/company observable seam confirmed (company sees realised
  weather only). Director opens the atom for BUILD-within-epoch per epoch-gating.

---

## 7. Scale-readiness (C-S2 is critical here)

**RNG substream discipline (C-S2) is the load-bearing constraint for this atom.** The weather
generator is a new stochastic subsystem drawing many random numbers per timestep. It **MUST draw
from its own named, seeded substream** (e.g. `rng.substream("weather_national")`), never the shared
global RNG. Precedent: the real **01:09Z life-event incident**, where adding illness/divorce draws
to the *shared* life-event RNG shifted **every downstream draw** and silently changed unrelated
subsystem outputs. Weather draws are high-volume and would be a far worse offender — a single added
weather variable on a shared stream would perturb churn, pricing, every other stochastic system.
Isolation makes weather's draws inert to the rest of the world and vice versa.

- **Deterministic replay (C-S2):** same seed ⇒ identical national weather path; replaying a history
  reproduces identical state. This is what makes the harness's Dunkelflaute injections reproducible
  and the belief-vs-truth gap a stable measurement.
- **C-S5 (time-scale invariance):** at L3 the atom must declare whether its persistence structure is
  time-scale invariant (half-hourly vs daily generation) or register the assumed cadence as a named
  simplification per R10 — autocorrelation length is inherently timescale-tied, so this needs an
  explicit statement.
- **SIMPLICITY GUARD:** a named substream + a seed is the whole mechanism; no RNG framework
  cathedral. Persistence behind the existing sim interface (C-S4) — no new storage architecture.

---

## 8. Curriculum note (R13 — the baseline/curriculum split)

- **Baseline is calibrated to reality, blind to company P&L (R13, R12).** The generator's
  parameters (marginals, autocorrelation, joint tail) are fixed by fidelity to reanalysis **only**,
  decided without reference to how the company's margin looks. If the company loses money in a
  faithfully-severe winter, that is a finding — **never** a reason to soften the weather. Margin is
  a diagnostic, not a target (R12); weather severity is not tuned toward any outcome.
- **Severity/scenario selection is director-authored curriculum.** *Which* worlds the company lives
  through — "a 2010-style cold December", "a two-week February Dunkelflaute", a stress ensemble —
  are named, versioned, director-authored curriculum artefacts, not silent parameter drift and not
  agent-chosen in response to company results. The agent controls both sides of the wall, so the
  curriculum must face the director. The generator provides the *capability* to produce severe
  weather faithfully; the director chooses the *diet*.
