# Weather simulation — purpose, variable-selection order, forecast layer (DISCOVER→FRAME)

**Source:** `docs/staging/done/DIRECTOR_STEER_WEATHER_SIM_PURPOSE_2026-07-23.md`
(director-decided in advisor conversation 2026-07-23, advisor-staged). **Type:** [STEER] — a
**PURPOSE** re-framing of the W1 weather lane: what the lane is *for*, and how its variable set is
*chosen*. Mechanism mine; the constructs in the steer are the **wall**.

**Status:** DISCOVER→FRAME, **doc-only**. Provenance: **proposal**. The steer self-declares it
"authorizes no BUILD, opens no gate, moves no level." This FRAME honours that exactly: it writes
**no** `sim/`/`company/`/`harness/` code, edits **neither** `maturity_map.yaml` **nor** any engine,
claims **no** level, does **not** edit `DIRECTOR_CANON.md` (director-reserved, Law B — the design
principle below is recorded **proposed-for-canon**, the director ratifies). Touches only
`docs/design/`. Candidate atoms are **named, not registered** (orchestrator is sole map writer per
THREE_LANES until `H9`). Existing ratified levels (**W1_3/W1_4/W1_5/W1_6/C13 at L3**, confirmed in
`BOARD_SPEC_002_RECONCILIATION.md` against `gate_authorizations.jsonl`) are **unaffected** — the
steer says so explicitly and this FRAME cites the live map for levels.

**No network this session** (autonomous run): the availability/shape of the real NESO/Elexon
forecast archive (§3) is flagged **`[recall — verify at BUILD]`**; no external figure is fabricated
(Historical Ground Truth). In-repo levels/files are quoted from the live `docs/design/maturity_map.yaml`.

---

## 1. The design the steer establishes — recorded, PROPOSED-FOR-CANON

> **PRINCIPLE (proposed canon, v1, 2026-07-23): The W1 lane is the weather simulation *itself* —
> nothing else. Prices, premise demand and gross margin are the *consumers* of the weather (they
> define what "great" means) but are not in scope. Variables are chosen by
> `gather → correlate → select → simulate`, never by intuition; the selection test is tail
> explanatory power (worst-cell), not average R²; the design test is parsimony (minimum variables
> for maximum efficacy *including real-world uncertainty and error*); and the forecast layer — the
> same variables as forecasts at multiple horizons with error that shrinks toward delivery — is
> first-class.**

Scope discipline (decided): when a piece of work in this lane starts modelling price formation or
demand response, **it has left the lane**. Context, not scope: renewables' share rises yearly, so
weather's grip on wholesale prices tightens yearly; premise demand is heavily weather-dependent; and
weather risk is a top consideration when a retailer sets fixed prices. A stationary, tame weather
world makes every downstream claim soft.

## 2. What the repo already embodies vs what is genuinely new

The steer's own §2.1 credits the existing outturn-side correlation evidence, and it is real:

| Steer clause | In-repo status | Evidence |
|---|---|---|
| temp/HDD ≈ 55% of daily demand variance | **Met** | `sim/weather_price_chain.py` degree-day OLS, R²=0.55 (W1_6 L3) |
| gas+temp+wind ≈ 93% of derived price | **Met** | `weather_price_chain.py` derived-price regression; `TRIANGULATION_…FRAME.md` L105 |
| still-and-cold compound (built, validated) | **Met, with caveat** | season-conditioned covariance (NOT the refuted regime trigger — see Finding F-ii); `frame/W1_3_gap1_regime_trigger_REFUTED_FRAME.md` |
| cloud cover half-hourly, keep it | **Met** | already in the engine |
| tail/worst-cell selection discipline | **Met** | worst-cell rule, `EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md` MEASURE 2 |
| wind INCLUDING 30-min ramps | **Gap** | wind is a single mean-matched scalar (R10 simplification, W1_6; F2 caveat) |
| national + local deviation, anywhere-in-GB | **Partial** | 4-location calibration set is the known limitation; national datasets + GSP/DNO-keyed partition is the portable frame |
| extremes at the right FREQUENCY | **Open gap** | `reach_fraction` 12–32% on W1_3, reported-not-gated diagnostic (see Finding F-iii) |
| interannual winter-to-winter variability | **Partial — verify at BUILD** | not separately measured against the real high-single-digit swing |
| warming trend WITHOUT thinning extremes | **Partial** | trend carried; tail-preservation-under-trend not separately asserted |
| **the forecast layer** | **Genuinely new** | no existing surface; see §3 |

The genuinely ungathered data the steer names is the **forecast archive** — NESO/Elexon publish
day-ahead (and other-horizon) wind and demand forecasts alongside outturns. **Forecast-vs-outturn
pairs are the ONLY way to measure error-by-horizon; outturn data alone cannot reveal it, however
long the record.** This is the correct, non-obvious point that reorders the lane's next work.

## 3. The forecast layer — candidate atoms (NAMED, NOT REGISTERED)

Proposed candidate atoms, for the director/orchestrator to register when the lane is BUILD-opened.
None is registered here; none claims a level.

- **`W1_forecast_archive` (gather)** — ingest the real NESO/Elexon multi-horizon wind + demand
  forecast archive alongside outturns; store forecast-vs-outturn pairs. `[recall — verify at BUILD:
  exact endpoints/horizons published]`. This is the §2-step-1 gather that unblocks everything else.
- **`W1_forecast_error_model` (simulate)** — emit the same weather variables as *forecasts* at
  multiple horizons (seasonal normals months out → day-ahead → within-day) with realistic error that
  shrinks toward delivery; anchor `σ(horizon)` on the real pairs above. **Epistemic note (decided):**
  forecast error is the *natural* epistemic wall on the future — forecasts are genuinely public
  (company-knowable), outturn arrives only at delivery, so **no artificial blinding is needed**.
  Generator and validator anchors must remain independent sources (standing anti-marking-own-homework
  rule, R15/R13-adjacent).
- **`W1_wind_ramps` (refine)** — represent 30-minute wind ramp structure, replacing/decomposing the
  single mean-matched scalar. Directly addresses Finding F-ii's F2 caveat. `file_scope` overlaps
  `weather_price_chain.py` / W1_4 / W1_7 — sequencing note, not a registration.
- **`W1_gb_partition` (refine)** — national signal + local deviation resolvable *anywhere in GB* via
  a GSP/DNO-style keyed partition; current 4 segments become the first sample points, not the frame.
  "New segment, new place — no rebuild" is the acceptance test.

## 4. Re-rank input for the next W1 draw sequencing (this is what §6 of the steer asks for)

Recorded here (PRIORITIES.md untouched — this is re-rank *input*, the ranked queue stays the sole
authority; surfaced for the next sequencing decision, not silently applied):

1. **Forecast-archive gather rises to the front of *new* W1 work.** It is the one genuinely
   ungathered dataset, it unblocks the entire forecast layer, and it is doc/data work (no BUILD gate
   to open for the gather itself). Everything else in the lane is refinement of already-L3 physics.
2. **Premise-fidelity refinements drop** under this lens — the steer names them "supporting cast to
   the national drivers." (Blast-radius note from the steer §6.)
3. **The still-and-cold / reach_fraction / interannual items are refinements to already-L3 atoms**
   (new BUILD work, not level regressions) — sequence them *after* the forecast-layer gather unless
   the director elevates a specific tail gap.
4. **Wind-ramp + GB-partition** are the two structural refinements that most change downstream tail
   fidelity; rank above cosmetic premise tuning.

## 5. Director findings — surfaced, NOT silently resolved (steer §6 mitigation)

- **F-i (scope ownership of the spike-tail defect).** The steer's §1 scope line puts price formation
  *outside* this lane (price is a consumer), yet §5 lists "the spike-tail defect" among W1 open
  sequencing items. The spike-tail (recalibrated max £574 vs real £4,038; neg-price share 0.013% vs
  2.241% — `EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md`) lives on the **price/residual (consumer)**
  side, not the weather-only lane. Reading it as in-lane would breach the steer's own scope
  discipline. **Surfaced for the director:** confirm the spike-tail is owned by the price/consumer
  lane and merely *sequenced against* (not *inside*) W1 — that is this FRAME's reading, not resolved.
- **F-ii (which construct "preserve the still-and-cold compound" preserves).** Two live facts sit
  under this clause: (a) the earlier joint cold-still *regime trigger* was built, measured, and
  **REFUTED** (it made fidelity worse) — the fix that produced the validated tail was a
  **season-conditioned covariance** (`frame/W1_3_gap1_regime_trigger_REFUTED_FRAME.md`); and (b)
  Finding **F2** (`BOARD_SPEC_002_RECONCILIATION.md`) flags that home-weather and
  wind-*generation*-weather are collapsed to **one national wind series**, so the joint tail "may be
  partly an artefact of the collapse rather than real physics." **Surfaced:** "preserve it" is read
  as *preserve the season-conditioned-covariance tail, not revive the refuted regime trigger*, and
  the F2 single-wind-series caveat means the wind-ramp/two-series refinement (§3 `W1_wind_ramps`) is
  the honest way to keep the compound while removing the artefact risk. Not resolved here.
- **F-iii (an L3-ratified atom carrying a re-elevated open gap).** The steer names
  `reach_fraction` 12–32% (extreme *frequency*, not depth) as "the gap" on **W1_3, which is ratified
  L3** with reach_fraction as a declared reported-not-gated simplification. No contradiction (levels
  are untouched; the steer says so), but **surfaced** so it is understood that closing this is new
  fidelity BUILD on an already-L3 atom, never a level regression, and does not reopen ratification.

## 6. Decided vs Open (mirrors steer §5)

**Decided (the wall):** lane scope = weather only; the `gather→correlate→select→simulate` order;
tail-weighted (worst-cell) variable selection; parsimony as the design test; the forecast layer as
first-class; anywhere-in-GB portability as a design constraint; trends carried without thinning
extremes.

**Open (mine / the orchestrator's):** mechanisms throughout; which forecast horizons to model; the
region partition; how ramps are represented; sequencing against the existing W1 backlog and the
spike-tail defect (per F-i, the latter is a consumer-side item); whether existing atoms absorb this
or the §3 candidates are registered — **that registration is a BUILD-open decision, director/twin's,
not taken here.**

---
*Absorption record: doc-only PURPOSE steer → this FRAME. No map edit, no level move, no gate opened.
Candidate atoms named-not-registered. Three tensions surfaced as director findings (F-i/F-ii/F-iii),
none silently resolved. Steer archived to `docs/staging/done/`.*
