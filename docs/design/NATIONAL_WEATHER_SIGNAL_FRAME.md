# FRAME — W1_3_national_weather_signal: concrete generative-model recommendation

**Atom:** `W1_3_national_weather_signal` · **Lane:** `W1_market_weather` · **Dial:** 3
**level_current → level_target:** 0 → 3 (this doc lands L1) · **depends_on:** `W1_2_generate_futures`
**Stage:** FRAME/DISCOVER, Lane-3, doc-only. No product code, no map edit, no git action taken here.

This doc does not re-derive the case for the atom — `docs/design/frame/W1_3_national_weather_signal_FRAME.md`
(2026-07-16) and `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` (2026-07-13, director-steered) already
cover the real-world grounding, the COUPLED_TRIAD framing, and C-S2/C-S5 scale-readiness in full — cited
here, not repeated. This doc's job is the thing the prior FRAME explicitly deferred: **pick one concrete
generative model, justify it against the named alternatives, and specify calibration + validation +
substream design in enough detail that BUILD is a translation exercise, not a design exercise.**

It also folds in the map's own 2026-07-15 DISCOVER finding (`maturity_map.yaml`, this atom's
`simplifications`): the core mechanism is **already built, uncredited**, in `sim/weather_engine.py`. This
FRAME therefore recommends *extending* that engine to close three named gaps, not building a new one.

---

## 1. The problem, restated in one paragraph

Weather is the one exogenous input that moves both sides of a UK supplier's book at once: temperature
drives heating demand, wind/solar drive residual generation the wholesale market must cover. If temperature,
wind and solar are drawn independently and without persistence, three things that are true in reality become
false in the simulation: (a) cold spells and wind lulls do not persist for days, so the demand and price
shocks a real supplier prices insurance against never appear; (b) cold, still, dark conditions do not
co-occur above the rate implied by drawing marginals independently, so the GB "Dunkelflaute" tail — the
event that actually threatens a supplier's capital — is structurally absent; (c) a company whose hedge and
capital models are trained against this world will look safe and will not be. Getting persistence and joint
structure right is therefore not a nicety, it is what makes the coupled company-side test (§6, §9) mean
anything.

---

## 2. What already exists — audit of `sim/weather_engine.py`

Confirmed by direct read (this session) and consistent with the map's 2026-07-15 DISCOVER finding and
`docs/calibration/weather-engine.md`'s own published numbers:

- **Pass 1 — national macro** (`fit_national_macro_model` / `simulate_national_macro`): a 3-variable
  (`temperature_mean_c`, `wind_speed_mean_ms`, `cloud_cover_pct`) daily national series. Each variable is
  deseasonalised by harmonic regression (annual + semi-annual cycle), then modelled as an **AR1
  mean-reverting process on the residuals** (`phi` per variable, fitted from real autocorrelation — e.g.
  temperature 0.779, wind 0.575, cloud 0.437 on the real 2016-2025 series). **This is the temporal
  persistence half of the requirement, already present.**
- **Joint structure**: the AR1 innovations for the three variables are drawn jointly from a **fitted
  covariance matrix** (Cholesky-factorised), so contemporaneous cross-correlation between temperature, wind
  and cloud cover is preserved by construction, not sampled independently. **This is the joint-structure
  half of the requirement, already present in a first form.**
- **Regime-switching**: a 2-state Markov chain ("standard"/"stressed") with its own transition matrix and
  its own innovation covariance per state — days classified stressed are the top 10% by `|wind residual|`.
  This is exactly the "hybrid regime-switching" shape the prior FRAME (§3, "(likely)") recommends, already
  built, calibrated on 3,446 real days.
- **Half-hourly translation** already exists and is documented as in-sample-only validated: diurnal
  temperature shape, an astronomical clear-sky solar envelope attenuated by cloud cover, and an
  AR1/Ornstein-Uhlenbeck half-hourly wind process around the day's mean.
- **Regional layer** (Pass 2, Cholesky cross-location deviations) is the mechanism `W1_4_regional_weather_field`
  will need, not this atom's L1 scope — noted for continuity, not claimed here.

**Conclusion: this is not a greenfield build.** The honest remaining gap, per the 2026-07-15 finding and
confirmed by this read, is three specific, named items — not "build a weather generator."

---

## 3. Three named gaps vs. this atom's own DoD (this is the BUILD scope)

### Gap 1 — the stressed regime is wind-only, not jointly cold+still

`fit_national_macro_model` classifies "stressed" purely on `|wind_speed residual| > 90th percentile`.
Cold-and-still (Dunkelflaute) therefore only emerges as a *side-effect* of the innovation covariance's
temp/wind correlation term, not as an explicit mechanistic state. The director's own steer
(`WEATHER_PHYSICS_HIERARCHY_DESIGN.md`, quoted in the map) is precise on this: *"model a latent
BLOCKING-HIGH weather regime... so COLD-AND-STILL arises MECHANISTICALLY, not from a fitted Gaussian
correlation that under-weights tail dependence."* A Gaussian covariance systematically under-weights tail
co-occurrence relative to a real blocking anticyclone's near-deterministic joint signature (cold + calm +
clear-then-foggy + high pressure). **Recommended fix**: reclassify the regime trigger jointly — a day is
"stressed" if it sits in the joint tail of (low wind residual **and** low temperature residual, i.e. an
anticyclonic blocking signature), not wind alone. This is a small, precise change to
`fit_national_macro_model`'s regime-classification line, not a redesign — the AR1/Cholesky/Markov
scaffolding underneath is unchanged.

### Gap 2 — no "show the tail" artefact, no winter-tail-vs-real-worst-week comparison

The engine's own calibration report (`docs/calibration/weather-engine.md`) validates **distributional**
fit (means, std devs, cross-location correlation) but never checks the **joint tail** — the frequency and
duration of simulated cold+still spells against a real GB benchmark. This atom's own DoD (map
simplification, 2026-07-13) requires exactly this: *"the joint cold-still tail demonstrated (SHOW the
tail); winter-tail report compared to a real GB worst week."* Not built anywhere yet. Dunkelflaute logic
does exist, but on the **price** side (`sim/scenario/bimodal_generator.py`), disconnected from this weather
regime — a coupling gap, not a duplicate.

### Gap 3 — anchoring rule at risk (marking own homework)

The engine calibrates on the same 4-customer-location real series it would also be checked against. The
atom's registered anchoring rule requires the GENERATOR anchor (real historical weather, e.g. Open-Meteo
per-location) and the VALIDATOR anchor (an independent published source — NESO system demand, Met Office
seasonal/extreme-event bulletins, published UK degree-day series) to be **different sources**. No
independent validator is wired in yet.

None of these three gaps is greenfield; all three are precisely scoped extensions to an already-built,
already-calibrated engine.

---

## 4. Method recommendation (against the prior FRAME's three options)

The prior FRAME (§3) listed VAR/VARMA, copula-based joint sampling, and block-bootstrap as the candidate
families, converging on "hybrid regime-switching" as the likely L3 answer without committing. This doc
commits, using the audit in §2-3 as the deciding evidence:

**Recommended: keep the built regime-switching AR1 + Cholesky-covariance engine as the core mechanism,
extended with a jointly-classified regime trigger (Gap 1).** This is a hybrid of option (a) VAR — the
within-regime dynamics are exactly a seasonally-deseasonalised VAR(1) on (temp, wind, cloud) — and the
"(likely)" hybrid/regime-switching recommendation, which the codebase already instantiates.

Justification against the alternatives, now that a real implementation exists to compare against:

- **vs. pure VAR/VARMA (option a) with no regime layer**: a single-regime Gaussian VAR under-weights the
  joint tail exactly as the director's steer warns — this is *why* Gap 1 matters, not a reason to discard
  the VAR core. The regime layer is the cheap, already-built fix for VAR's known tail-dependence weakness;
  discarding the VAR core and starting over with a copula would throw away 3,446-day calibrated, tested
  machinery to fix one classification line.
- **vs. copula-based joint sampling (option b)**: copulas give more direct control of joint-tail
  dependence in principle, but "more moving parts... fiddly to fit and validate" (prior FRAME's own
  assessment) is a real cost, and the regime-switching approach achieves the same practical effect (large,
  clustered, correlated excursions in the tail state) with parameters that map directly to physical
  concepts (a persistent blocking-high dwell time, a transition matrix) rather than a copula family
  parameter that has to be reverse-justified against reanalysis. Not recommended as a replacement; could be
  revisited at L3+ if the jointly-classified regime (Gap 1 fix) still under-fits the measured tail (§6).
- **vs. block bootstrap of reanalysis (option c)**: physically faithful "for free" and worth keeping in
  mind as the **validation** anchor (§6) — a good check is "does a block-bootstrap of real windows produce
  a similar Dunkelflaute frequency/duration to the parametric engine's output" — but as the *generator* it
  is limited to the variety of severity actually observed in 2016-2025 and cannot be extended smoothly for
  a director-authored curriculum scenario (R13) that asks for a colder-than-observed winter. The parametric
  engine can be re-parameterised for curriculum severity without needing more historical years; a bootstrap
  cannot. Recommended role: independent **validation check**, not the generator.

**Solar treatment — explicit design choice, not a fourth variable.** The engine does not model solar as an
independently-drawn correlated variable; it derives half-hourly solar irradiance deterministically from
(astronomical clear-sky envelope) × (1 − k·cloud_fraction), where cloud_cover_pct is the third jointly-
modelled macro variable. This is physically defensible — at daily/half-hourly resolution, solar irradiance
variability over a fixed location is overwhelmingly cloud-driven, and cloud cover is already inside the
joint AR1/Cholesky system, so solar inherits the correct persistence and cross-correlation with
temperature/wind *through* cloud cover, without needing its own stochastic draw. **Registered
simplification (R10-visible, not silent)**: this means "solar" is not a fourth jointly-fitted stochastic
variable but a deterministic function of an already-joint variable (cloud cover) plus a deterministic
astronomical function of (day-of-year, time-of-day, latitude). If a future validation pass finds solar
capacity-factor persistence deviates materially from cloud-cover-implied persistence (e.g. haze/aerosol
effects cloud_cover_pct doesn't capture), that would be the trigger to promote solar to its own jointly-
modelled variable — not assumed necessary today.

---

## 5. Calibration to real Open-Meteo statistics

Already done, per `docs/calibration/weather-engine.md`, and re-usable without re-fitting for this atom's
extension:

- Seasonal harmonics, AR1 `phi` per variable, regime transition matrix, and standard/stressed innovation
  covariances are fitted on the real 2016-01-01..2025-06-07 daily national series (3,446 days, 4 locations
  averaged) — Historical Ground Truth law honoured (Open-Meteo Historical Weather Archive, via
  `sim/weather_ingestor.py`, no invented values).
- Distributional fit is close: national means/std devs match real data to ~0.1-0.3 units across all three
  macro variables; cross-location temperature correlation reproduces 0.952 (real) vs 0.952 (synthetic).

**What calibration does NOT yet cover, and must before L2/L3 (this is §3's Gap 2/3, restated as
calibration targets rather than code gaps):**
- The **per-variable autocorrelation function beyond lag-1** — `phi` is a single AR1 coefficient fitted
  from lag-1 correlation; the *spell-duration distribution* (how many consecutive days a cold/still episode
  actually lasts in reality) is a derived property of an AR1 process and has not been checked against the
  real empirical spell-duration distribution. An AR1 process has a specific (geometric-ish) spell-duration
  shape; real blocking highs may have fatter-tailed dwell times. This is exactly what the regime-switching
  Markov chain is *for* (its own transition matrix has its own dwell-time distribution, separately fittable
  and checkable), but no one has yet compared the *stressed*-regime dwell-time distribution against real
  multi-day cold-spell/wind-drought duration records.
- The **joint tail rate**: how often, in the real 2016-2025 window (or a longer/independent reanalysis
  window), do cold ∧ still ∧ overcast conditions co-occur for 3+/5+/7+ consecutive days — versus how often
  the synthetic engine's jointly-reclassified stressed regime produces the same. Not measured anywhere yet.

---

## 6. Point-in-Time reveal and the SIM/company wall

This atom sits on the W1 "reveal-over-time" spine (per `docs/design/charters/W1_market_weather.md`) — the
generated national weather path is SIM ground truth, generated once per run (deterministically, given a
seed), but the company must only ever observe it **as a real trading desk would**: realised weather for
days that have passed, and — if a forward weather signal is modelled at all — a probabilistic/degraded
forecast for near-term days, never the exact future path. Concretely:
- The company's demand-forecast and hedge-decision code (`company/`, `saas/`) reads **realised** national
  weather (and, downstream, its own meter reads) via the SIM/company interface
  (`company/interfaces/sim_interface.py`) — never `weather_engine.py`'s regime state, AR1 residuals, or
  transition matrix directly. Per `.claude/rules/epistemic-wall-sim.md`, any new observable this atom
  exposes must cross only at that seam.
- No forward-weather-forecast observable is introduced by this atom — that is a separate, not-yet-scoped
  capability (a synthetic "Met Office forecast" with realistic skill decay by lead time). Absent that, the
  company's only legitimate source of weather-linked information about the future is exactly what a real
  supplier has: historical seasonal-normal expectations (already `sim/weather_hdd.py`'s
  `REFERENCE_MONTHLY_HDD` table) and its own priced-in weather-sensitivity assumption
  (`sim/weather_price_sensitivity.py`), not the true forward path.
- **depends_on `W1_2_generate_futures`**: the weather signal is one exogenous driver feeding the same
  synthetic-future scaffold that futures/forward-curve generation establishes — sequencing this after W1_2
  means the market-data seam (how a generated future is revealed and consumed) already exists for weather to
  plug into, rather than this atom inventing its own reveal mechanism in parallel.

---

## 7. RNG substream design (C-S2 — load-bearing, not optional)

Per the prior FRAME §7 and the project's own 01:09Z incident precedent (adding draws to a *shared* RNG
silently shifted every other subsystem's output): the weather generator's national macro simulation
(`simulate_national_macro`) and any Gap-1 regime-reclassification logic must draw exclusively from a single
named substream, e.g. `rng.substream("weather_national")`, obtained once per run from the run's seeded RNG
factory and never from a shared/global `np.random` call. Concretely for this engine:
- `simulate_national_macro(params, day_of_year, rng)` already takes an explicit `rng: np.random.Generator`
  parameter (confirmed by read, §2) — the substream discipline is a *wiring* requirement (the caller must
  pass the named substream, not `np.random.default_rng()` or a shared instance), not a code change to the
  function signature.
- Determinism check: same seed ⇒ identical national weather path, byte-for-byte, across repeated runs —
  this is what makes a harness-injected Dunkelflaute scenario (§9) reproducible, and what lets a re-run
  after a code change be diffed against a prior run's weather path to confirm the change didn't silently
  perturb weather (or vice versa).
- **C-S5 declaration**: the persistence structure (AR1 `phi`, regime dwell times) is fitted at **daily**
  resolution and translated to half-hourly via a separate, deterministic (non-autocorrelated-draw)
  translation layer (diurnal shape, clear-sky envelope, wind AR1 *within* a day). The autocorrelation length
  is therefore NOT time-scale invariant by construction — it is explicitly a daily-cadence model with a
  deterministic sub-daily shape layered on top. This is the registered simplification C-S5 asks for: stated
  here, not silently assumed.

---

## 8. Validation plan — what becomes a mutation-tested invariant

Three checks, each with a real external benchmark (never the company's own P&L, per R12/R13):

1. **Autocorrelation-length check.** Compute the empirical lag-N autocorrelation of the synthetic national
   series for each variable (already partially done via the fitted `phi`, but not checked as an *output*
   property of full simulated paths) and compare against the real Open-Meteo daily series' own empirical
   ACF out to ~14-21 days. Tolerance: synthetic ACF within a stated band of real ACF at each lag up to the
   point both decay to near-zero. **Mutation test**: inject a broken generator that draws each day
   independently (phi forced to 0) and confirm the check FAILS loudly — proves the check isn't a tautology
   that would pass on IID noise.
2. **Spell-duration distribution check.** Define a "cold spell" / "wind lull" as N+ consecutive days with
   residual below a fixed real-data-calibrated threshold; compare the empirical duration distribution
   (median, 90th percentile, max) of synthetic spells against real spells over the same historical window.
   **Mutation test**: force regime transition probabilities to make regimes 1-day-only (no persistence) and
   confirm the check fails.
3. **Joint-tail (Dunkelflaute) rate check — the anchoring-rule-critical one.** Count synthetic occurrences
   of the jointly-reclassified stressed regime (Gap 1 fix) lasting 3+/5+ days per synthetic decade, and
   compare against an **independently-sourced** real-world benchmark distinct from the Open-Meteo series
   used to fit the generator — candidates: NESO's own published system-stress/Dunkelflaute commentary,
   Met Office seasonal bulletins citing named blocking-high events (e.g. the well-documented Nov 2021 GB
   wind-drought episode), or a published UK degree-day extreme-event record. **Mutation test**: replace the
   joint regime trigger with the current wind-only trigger (Gap 1's "before" state) and confirm the
   joint-tail rate measurably under-counts relative to the independent benchmark — this is the concrete,
   falsifiable version of the director's "a fitted Gaussian correlation... under-weights tail dependence"
   claim, and is what closes Gap 3 (anchoring rule) at the same time.

These three become the atom's invariant library entries at BUILD time (L2/L3 acceptance targets, §9);
per R15 each ships with its own mutation test, per the doctrine that a control which cannot fail is worse
than none.

---

## 9. Level decomposition (L0 → L3) and file_scope

- **L0 (prior state, before this doc and the 2026-07-15 DISCOVER finding):** registered as greenfield, dial
  3, `loop_stage: idle`. Understated — the underlying engine already existed uncredited.
- **L1 (this doc lands it):** the concrete method is chosen and justified (§4), the three real remaining
  gaps are named precisely against the already-built engine (§3), calibration status is inventoried
  against what's covered vs. missing (§5), the RNG substream and C-S5 requirements are pinned down for the
  existing function signature (§7), and the validation plan with mutation-test shape is specified (§8).
  `file_scope: [docs/design]` — no code, no map edit, this fork's own scope.
- **L2 (BUILD target, next real phase):** Gap 1 shipped — regime classification reclassified to a joint
  cold+low-wind condition (small, targeted change to `fit_national_macro_model`); Gap 2 shipped — a "show
  the tail" artefact exists (a calibration-report-style doc/script reporting synthetic Dunkelflaute
  frequency/duration per decade); checks #1 and #2 from §8 pass with their mutation tests proven to fail on
  the broken variant. `file_scope` at L2: `sim/weather_engine.py`, `docs/calibration/weather-engine.md`
  (updated), a new test module (e.g. `tests/sim/test_weather_regime_joint_tail.py`).
- **L3 (this atom's full target):** Gap 3 closed — an independent (non-Open-Meteo) validator anchor
  sourced and check #3 (§8) run and passing within a stated tolerance against it; the W1_4 aggregation-
  consistency invariant (regional field reconciling to this national signal) wired as a hard, mutation-
  tested check per the prior FRAME §5; C-S2/C-S5 statements verified true in the shipped code (substream
  actually wired at the real call site, not just declared possible). `file_scope` at L3 additionally
  touches `company/interfaces/sim_interface.py` only if/when a weather observable is exposed to the company
  (confirmed absent today, per the C13 DISCOVER finding cited in the map) — out of this atom's L3 scope
  unless a consuming atom (demand model, C13) requires it first.

---

## 10. What this doc is NOT claiming

No BUILD code was written or run. No calibration numbers in §5 were re-derived — they are quoted from the
existing `docs/calibration/weather-engine.md`. No map edit was made directly; the only mechanism used is the
atom_status inbox (`docs/design/atom_status/W1_3_national_weather_signal.yaml`) per H9's contended-write
fix, folded by the integrator, not by this fork. Level claimed is 1 (framed with a committed method
recommendation), never 2 or 3 — those require the Gap-1/2/3 code, tests, and independent-anchor validation
above to actually exist and pass.
