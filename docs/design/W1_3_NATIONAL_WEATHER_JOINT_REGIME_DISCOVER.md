# W1_3_national_weather_signal — DISCOVER pass: the joint COLD-AND-STILL regime

**Status:** DISCOVER, doc-only. `W1_3_national_weather_signal` is `level_current: 1`,
`level_target: 3`, `loop_stage: idle`, epoch 3, BUILD-gated behind `W1_2_generate_futures`.
This pass writes **no** sim/company code, edits neither `maturity_map.yaml` nor any engine, and
touches only `docs/design/`. It deepens the joint **cold-and-still** ("dunkelflaute meets cold
snap") half of this atom empirically, toward a **buildable L1/L2 invariant**, mirroring the
DISCOVER depth + invariant style of the sibling `W1_4_regional_weather_field` pass
(`docs/design/W1_4_REGIONAL_WEATHER_FIELD_DISCOVER.md`, landed L2 this session). It is world/SIM-side
framing only — the epistemic wall is kept intact (§2 states what the company observes, never SIM
internals).

**Relationship to the authoritative design.** `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.1/§3
is authoritative for the L1 *mechanism* — the latent 3-state `{WESTERLY, BLOCKING_HIGH, CYCLONIC}`
regime chain, why a common-cause latent state carries tail dependence where a fitted Gaussian copula
thins it, and the joint-tail-coverage-ratio ≥ 1.0 exit test. This doc does **not** re-derive that
mechanism. It supplies the thing that design left to "calibration at BUILD" and the map's own
2026-07-15/07-16 findings left open: a **concrete, repo-measured joint-tail characterisation** — real
numeric thresholds and lift factors from the committed weather record — plus the single **candidate
invariant** a future L1/L2 build must satisfy, stated in the R10 invariant-library style without code.
It also sharpens the map's standing gap (1) on this atom: *the existing regime trigger keys on wind
residual alone, not the joint cold-and-still condition* — §1.3 gives the empirical reason that gap
matters.

---

## 0. Repo grounding — what the national series already is (honest audit)

- `sim/weather_engine.py` **Pass 1** (`fit_national_macro_model` / `simulate_national_macro`) already
  builds a **national daily** joint series for `(temperature_mean_c, wind_speed_mean_ms, cloud_cover_pct)`
  by averaging the four calibration locations, fits seasonal harmonics, and drives a **regime-switching
  mean-reverting AR1** with a 2×2 transition matrix and regime-specific innovation covariance
  (`cov_standard` vs `cov_stressed`). This is the built precursor; it is why the atom sits at L1, not 0.
- **The national series backing all of this is 4 point locations** (`sim/weather_data/{C1..C4}.csv`,
  named London/Manchester/Glasgow/Cotswolds in the engine docstring), averaged — **not** a
  capacity-weighted GB wind-output series. The wind variable is 10 m wind *speed* at 4 points, a proxy
  for renewable-output "stillness", not GB wind *generation*. Every number in §1 below is therefore a
  **directional anchor from this 4-point proxy**, explicitly not a final calibration target — a real
  capacity-weighted GB wind-output series (NESO/Elexon `sim/generation_demand_history.py`) is the BUILD
  anchor (§5). This caveat is load-bearing and repeated at each figure.
- **The stressed-regime trigger keys on `abs(wind_resid) > 90th percentile` — wind alone** (engine
  lines ~114-118). Cold-and-still therefore arises today only *implicitly*, through the temp/wind
  correlation inside `cov_stressed`, never as an explicit jointly-classified state. §1.3 is the
  empirical case that this is insufficient.

---

## 1. The regime, precisely defined (empirically, from the committed record)

I computed the joint statistics directly from the 4-location national daily series (3,446 real days,
2016-01-01 → 2025-06-07; **winter = Dec/Jan/Feb, n = 872 days**). Method: national daily mean over
C1-C4; winter subset; empirical percentiles; joint-tail count vs the independence product. Reproducible
from `sim/weather_data/*.csv` with no network. **All figures are 4-point-proxy directional anchors,
verify against capacity-weighted GB series at BUILD.**

### 1.1 Candidate jointly-observable thresholds (winter-conditioned)

"Cold-and-still" is a **joint winter-tail** event — it is only meaningful conditioned on winter, because
the marginals are seasonal (a "still" summer day is not a supplier problem). Two candidate threshold sets:

| Definition | Temp threshold (winter) | Wind threshold (winter) | Basis |
|---|---|---|---|
| **Decile (severe)** | mean temp ≤ **~0.9 °C** (winter p10) | mean wind ≤ **~2.3 m/s** (winter p10) | joint bottom-decile corner; the "killer" tail |
| **Quintile (stress)** | mean temp ≤ **~2.4 °C** (winter p20) | mean wind ≤ **~2.8 m/s** (winter p20) | broader stress band; more days, more statistical power |

The **joint regime** = both conditions true simultaneously (bottom-left corner of the
(temp-percentile, wind-percentile) plane), winter-conditioned. The percentile keying (not absolute
°C / m/s) is deliberate and portable: thresholds are defined as *tail quantiles of the realised winter
distribution*, so a second geography (or a shifted-climatology future world) re-derives its own corner
without hardcoded GB constants (portability, §4).

### 1.2 The joint tail is FATTER than independent — measured lift

| Corner | P(cold) | P(still) | P(cold ∧ still) observed | Independent product | **Lift (obs / indep)** | Days |
|---|---|---|---|---|---|---|
| Decile | 0.102 | 0.101 | **0.024** | 0.0103 | **2.34×** | 21 |
| Quintile | 0.201 | 0.201 | **0.075** | 0.0403 | **1.85×** | 65 |

**The joint cold-and-still corner carries ~1.9–2.3× the mass an independent draw would give it.** This
is the empirical face of the FRAME's core thesis: sample temperature and wind independently (or with a
mis-fit correlation) and you under-populate the supplier-killing corner by roughly half to two-thirds.
The lift **grows deeper into the tail** (1.85× at quintile → 2.34× at decile), i.e. the dependence is a
*tail* dependence, not a uniform correlation — exactly what a Gaussian copula with a single fitted ρ
thins out and what the latent-regime mechanism exists to carry structurally.

### 1.3 Why the wind-only trigger is insufficient — the seasonal-aggregation trap (decisive finding)

Pearson correlation of national daily (temp, wind):

- **All-year: −0.06** (≈ zero — statistically no relationship)
- **Winter (DJF): +0.507** (strong: cold days *are* still days in winter)

**A model fit to the all-year correlation sees essentially no temp/wind dependence and would generate a
near-independent joint tail — annihilating cold-and-still.** The dependence is real but *seasonally
localised*; it is invisible in the pooled statistic. This is the concrete, repo-measured reason the
atom's standing gap (1) matters: a wind-residual-only regime trigger, and any single all-year fitted
correlation, both miss that the cold∧still coupling **switches on in winter**. The invariant (§3) must
therefore be a **winter-conditioned joint** property, not an all-year one — and the mechanism must make
the coupling *seasonal*, which the design's month-indexed transition matrix `P_m` (blocking-high
reachable/persistent Dec-Feb) already does. This finding independently validates that design choice.

### 1.4 Persistence — the regime lasts days, not a half-hour

The event that breaks a supplier is a *sustained* spell, not a single cold half-hour. From the record,
consecutive-day quintile cold-and-still spells:

- **32 spells; mean 2.0 days; max 7 days; 15 spells ≥ 2 days; 4 spells ≥ 4 days.**
- Deseasonalised lag-1 autocorrelation: **temperature 0.78, wind 0.57** — both strongly persistent.

Multi-day cold-and-still spells are common (roughly half of all cold-still spells run ≥ 2 days) and the
tail reaches a full week. **Persistence is not noise to smooth away — it is the physics** (FRAME §2): a
world without it prices a 5-day spell as `p^5` (vanishing) and teaches the company to carry no hedge.
The design carries this in the regime **dwell length** `d_R`; the measured 2–7 day spell range and
0.57–0.78 autocorrelations are the directional calibration targets that dwell must reproduce (BUILD
anchor: capacity-weighted series, §5).

---

## 2. Why it matters to the company (the coupled-triad GAP)

The company **never reads the SIM weather engine** — not the regime label, not the AR1 coefficients,
not the innovation covariance, not the forward realisation. Per the epistemic wall it observes only
**consequences**: the demand it meters, the wholesale/imbalance prices it is charged, published weather
outturns/forecasts a real supplier could buy, its own bills and payments.

**The capability that must cope:** the company's **demand forecast + hedge/capital posture**. During a
joint cold-and-still regime, national heating demand rises *while* renewable output collapses *at the
same time and for several days* — residual demand and imbalance prices spike jointly and persistently.

**What the company would MISbelieve (the gap the harness measures):** if the company (allowed to be
wrong, like a real supplier) has calibrated its demand-and-price model on data pooled across seasons —
or on any model that treats temperature and wind risk as roughly independent — it will **underestimate
the joint-tail probability by the ~1.9–2.3× lift of §1.2** and the *persistence* of §1.4. Concretely it
will hold too little hedge and too thin a capital buffer going into winter, because in its belief a
5-day cold-and-still spell is `(p_cold·p_still)^5` rather than the far larger regime-driven mass. The
belief-vs-truth GAP is measured as: **realised imbalance cost / hedge shortfall / capital drawdown
during an injected cold-and-still spell, versus the company's own pre-spell expectation of those
quantities.** A company that hedged as if weather were independent-and-memoryless shows a large,
quantified gap; that gap **is the score** for this coupled pair. Per COUPLED_TRIAD this WORLD atom may
not reach L3 until that company gap has been measured against an injected spell.

*(The company-side normalisation twin is `C13_weather_normalisation`; its gap metric is designed in
WEATHER_PHYSICS_HIERARCHY_DESIGN.md §6 and is not re-specified here.)*

---

## 3. The candidate INVARIANT (R10 style, for a future L1/L2 build — no code)

The world-generator must satisfy a **joint-tail-dependence** property. Stated as a testable invariant:

> **INVARIANT W1_3-JT1 (winter joint-tail dependence is non-vanishing and exceeds independence).**
> Over a generated multi-year run, restricted to winter (DJF) national days, let `p_cold` = P(temp ≤
> winter-p10), `p_still` = P(wind ≤ winter-p10), and `p_joint` = P(temp ≤ winter-p10 ∧ wind ≤
> winter-p10). Then the **joint-tail lift** `L = p_joint / (p_cold · p_still)` must satisfy `L ≥ L_min`,
> with `L_min` a stated, real-data-anchored floor (directional anchor from the 4-point record: decile
> **2.34×**; a conservative floor such as `L_min = 1.5` is defensible pending the capacity-weighted
> recalibration). Equivalently, the generated joint-tail-coverage ratio against the real winter record
> (design §1.1) must be **≥ 1.0** — the model's cold-still corner mass is at least the real corner mass.

Companion properties the same build must hold (each an R10-class invariant, class-failing not
instance-failing):

- **W1_3-JT2 (persistence, not just marginal tail):** the generated distribution of *consecutive-day*
  cold-and-still spell lengths must have a mean and a max in the real range (directional: mean ≈ 2 d,
  max ≥ ~5 d), and per-variable deseasonalised lag-1 autocorrelation ≥ a stated floor (directional:
  temp ~0.78, wind ~0.57). A generator that reproduces the joint *marginal* tail but not its
  *persistence* fails this — the two are separately load-bearing.
- **W1_3-JT3 (seasonal localisation — the anti-pooling guard):** the temp/wind joint dependence must be
  **winter-conditioned**, matching the record's split (all-year corr ≈ 0, winter corr ≈ +0.5). A build
  whose dependence is uniform across the year, or fitted to a pooled all-year statistic, fails: it would
  either fabricate summer cold-still coupling or (the real risk, §1.3) wash the winter coupling out.

**R15 — the invariant must be able to FAIL (mutation tests, designed not coded here):**
- **TAUTOLOGY guard:** the checker must recompute `p_joint`, `p_cold`, `p_still` **independently** from
  the generated series, never read back a stored "designed lift" parameter — otherwise it always passes.
  The real-record corner mass it compares against is an **independent** anchor (the historical series,
  or the BUILD capacity-weighted series), not re-derived from the generator.
- **FAIL-OPEN guard:** a killer mutation = **replace the joint draw with two independent marginal draws**
  (or swap the winter-conditioned regime for an all-year fitted correlation). The invariant MUST fire:
  `L` collapses toward 1.0 and the coverage ratio drops below 1.0. An empty winter subset, all-equal
  temps, or a NaN must **fail loud**, not pass on a degenerate series.
- **FAIL-SILENT guard:** if the real-record anchor or the generated series is unavailable, the check is
  a **FAILED** check, never skipped-and-green.

This is the single most important buildable control for the atom: it is the mechanised form of the
FRAME's "SHOW the tail" DoD, and it directly catches a regression to the wind-only / independent-draw
failure mode the record proves would be wrong.

---

## 4. Portability / scale flags (C-S constraints; R13 curriculum-vs-baseline split)

- **R13 — PHYSICS is baseline, SEVERITY is director curriculum.** The *existence, sign and shape* of the
  cold-and-still joint dependence — the ~1.9–2.3× tail lift, the winter localisation, the multi-day
  persistence — is **baseline**: calibrated to reality (reanalysis / real GB series), decided **blind to
  company P&L**, changed only for fidelity-to-reality reasons (R13, R12). If the company loses money in a
  faithfully-severe cold-still winter, that is a *finding*, never a licence to soften the tail. **Which**
  cold-and-still worlds the company lives through — "a 2010-style two-week February blocking high", a
  stress ensemble — is **director-authored, versioned curriculum**, never silent parameter drift and
  never agent-tuned toward an outcome. The generator provides the *capability* to produce severe
  cold-still faithfully; the director chooses the *diet*. `L_min` and the spell-length floors are
  baseline-fidelity constants, **not** difficulty dials.
- **Portability — no hardcoded GB constants.** Thresholds are **percentile/quantile-keyed** (winter p10/
  p20), not absolute °C / m/s, so a second geography or a shifted-climate future world re-derives its own
  corner. "Winter = DJF" is a Northern-Hemisphere convention → register the cold-season months as a
  configurable parameter (portability debt if hardcoded), not the literal `{12,1,2}`.
- **C-S2 — RNG substream + deterministic replay.** The joint regime draws MUST come from the design's
  own named `national_regime` substream (per WEATHER_PHYSICS_HIERARCHY_DESIGN.md §7), isolated from every
  other subsystem — the 01:09Z shared-RNG lesson. Deterministic replay is what makes the injected
  cold-still spell (§2) and the joint-tail measurement (§3) reproducible.
- **C-S5 — time-scale invariance declaration.** The joint-tail statistics here are **daily**;
  autocorrelation length and spell duration are inherently timescale-tied. Any L3 claim must state the
  daily-regime / half-hourly-diurnal coupling as a named simplification (R10) — the joint-tail invariant
  itself is stated on the daily series and must declare that basis.

---

## 5. Open questions / what BUILD needs (could not resolve without network or a director call)

1. **Capacity-weighted GB wind-output series (the biggest one).** Every §1 figure is a **4-point wind-
   *speed* proxy**, not GB wind *generation*. The real joint-tail lift, spell distribution and thresholds
   must be recomputed against a capacity-weighted GB renewable-output series (NESO/Elexon via
   `sim/generation_demand_history.py`) before `L_min` and the spell floors are fixed. Requires a real data
   pull — no network in this fork. The 4-point lift (2.34× decile) is a **plausible lower bound** (point
   wind speed is smoother and less concentrated than capacity-weighted output, which clusters wind in
   Scotland/North Sea — a blocking high hits the fleet harder than it hits a 4-point average), so the true
   lift is likely **≥** what I measured, but this must be verified, not assumed.
2. **External anchor for the joint tail (recall, verify at BUILD).** NESO's capacity-market /
   loss-of-load-expectation work and its published characterisations of "low wind + cold" stress periods,
   and the widely-documented GB winter blocking-high events (e.g. cold-still spells suppliers hedge
   against), are the natural independent validator anchors. I cite these from **recall only — flag:
   verify against the primary source at BUILD** (no network here; Historical Ground Truth forbids
   fabricating a specific date/figure in a DISCOVER doc). The design's anti-marking-own-homework rule
   (generator anchor ≠ validator anchor) applies: fit on the weather record, validate on independent
   published stress-period statistics.
3. **`L_min` floor + spell-length tolerances — a values/calibration call.** The exact promotion floor
   (`L_min = 1.5`? the measured 2.34×? a real-record coverage ratio ≥ 1.0 with a stated tolerance) is a
   calibration decision to settle at BUILD against the capacity-weighted series; whether it is an exit
   gate is the director/twin's BUILD-open call (Epoch 3).
4. **Winter definition and threshold quantile.** DJF vs a heating-season definition (Nov-Mar), and
   decile vs quintile as the *primary* invariant corner — a modelling choice affecting statistical power
   (21 vs 65 tail days on the current record) that BUILD settles against the fuller series.
5. **Coupling to `W1_6` price + `W1_4` regional.** The cold-still tail's *price* consequence lives in the
   L4 chain (`W1_6`), and a regionally-skewed book's exposure lives in the `W1_4` regional field; whether
   the joint-tail invariant is asserted at the national level only, or also propagated as a regional-basis
   stress, is a cross-atom sequencing question for the orchestrator (design §6.3), not resolved here.

---

*Sources (all read/computed this pass, no network): `sim/weather_engine.py` (Pass 1 regime-switching AR1,
wind-only trigger, 4-location national average — read directly); `sim/weather_data/{C1,C2,C3,C4}.csv`
(the real Open-Meteo record; joint-tail lift, correlations, spell durations and autocorrelations in §1
computed directly from these 3,446 days / 872 winter days); `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md`
§1.1/§3/§6/§7 (authoritative L1 mechanism, joint-tail-coverage exit test, coupled twin — not re-derived
here); `docs/design/frame/W1_3_national_weather_signal_FRAME.md` (the frame deepened); `docs/design/W1_4_REGIONAL_WEATHER_FIELD_DISCOVER.md`
(sibling DISCOVER depth + invariant style mirrored); `docs/design/maturity_map.yaml` (`W1_3` entry:
level_current=1, three standing open gaps). External NESO/blocking-high characterisations in §5.2 are
**recall only, flagged for BUILD-time verification** against primary sources; capacity-weighted GB
wind-output recalibration (§5.1) is the named first BUILD data task. R10/R12/R13/R15, COUPLED_TRIAD,
C-S2/C-S5, Historical Ground Truth, and the epistemic wall referenced inline.*
