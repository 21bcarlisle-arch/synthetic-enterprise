# Fidelity Evidence — Price Engine Recalibration (Epoch-2, 2026-07-19)

**Atom:** `sim/price_engine.py` wholesale price physics engine (Regime-3 generative path).
**Status this pass:** structural + calibration fix landed; engine remains gated OFF in every
production phase (real historical SSP is still what every phase reads). Emitted in atom-G
emit-DoD shape per director instruction (atom G's own gate is not built yet).

This is a **baseline fidelity fix, decided blind to company P&L** (R12/R13) — the price engine
has no live consumer in the company layer today, so this recalibration changes only a generative
code path nothing currently reads. Nothing in company P&L can move as a result of this commit.

---

## 1. The fitted relationship

### 1.1 Gas floor (marginal cost of gas-fired generation, now with carbon)

```
P_gas_floor = (gas_price_gbp_per_mwh + carbon_price_gbp_per_tonne * EF_GAS_TCO2_PER_MWH_TH)
              / thermal_efficiency
```

- `thermal_efficiency = 0.50` (unchanged from Phase 3b original)
- `EF_GAS_TCO2_PER_MWH_TH = 0.184` tCO2/MWh(th) — **R10 simplification**, see §3.
- `carbon_price_gbp_per_tonne` defaults to `0.0` — **not fit in this pass** (no real historical
  UK-ETS/EU-ETS series wired in yet; see §3). With the default, this formula reduces exactly to
  the pre-recalibration `gas_price / thermal_efficiency`, so the existing `gas_floor_price` default
  tests remain valid unchanged.

### 1.2 System margin — residual-demand scarcity form (replaces the raw-ratio form)

```
RD = demand_mw - renewable_generation_mw                    (residual/thermal demand)
x  = RD / DISPATCHABLE_CAPACITY_MW                           (normalized scarcity)
multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
P_HH = P_gas_floor * multiplier
```

**Calibrated constants** (fit against real Elexon SSP, full window 2016-03-01..2025-06-07,
n=157,106 settlement periods, via `simulation/run_phase3b_recalibration.py`):

| Constant | Value | Fit method |
|---|---|---|
| `DISPATCHABLE_CAPACITY_MW` | 35,000 | **asserted** (R10, not fit — see §3) |
| `X_TIGHT` | 0.70 | selected from grid search (see §2.2 for why not the pure argmin) |
| `SCARCITY_EXPONENT` (p) | 2.0 | selected from grid search |
| `A0` | 0.326998 | closed-form OLS (`numpy.linalg.lstsq`) at the selected grid point |
| `A1` | 1.334629 | closed-form OLS at the selected grid point |
| `A2` | 3.828327 | closed-form OLS at the selected grid point |

This replaces the original spec'd form `P_HH = P_gas_floor * (demand_mw/renewable_mw)^gamma`
(`gamma` in [1.5, 2.5]), which overestimated real SSP by roughly 10x even at gamma=1.5 (raw
demand/renewable ratio has median ~3.46; `3.46^1.5 ≈ 6.4x` the gas floor — see
`docs/calibration/price-engine.md` for the original diagnosis).

---

## 2. Strength — MAE, R², distribution match, lift over naive baseline

### 2.1 Full-window fit quality (n=157,106, 2016-03-01..2025-06-07)

| Metric | Naive (gas floor alone) | 3-feature OLS regression* | **Recalibrated engine (this pass)** |
|---|---|---|---|
| MAE | £35.775/MWh | £33.96/MWh | **£32.790/MWh** |
| RMSE | £76.263/MWh | £72.13/MWh | **£70.159/MWh** |
| R² | 0.3135 | 0.3858 | **0.4190** |

\* `simulation/run_phase3b_regression.py`, `SSP ~ gas_price + demand_mw + wind_mw`, documented in
`docs/calibration/price-engine.md`'s 2026-06-11 addendum. The recalibrated physics form **beats**
both the naive gas-floor baseline and the existing 3-feature OLS regression on every metric, using
only structurally-motivated features (gas+carbon floor, residual-demand scarcity) rather than a
black-box linear fit.

**Hard bar set by the recalibration brief:** MAE ≤ £34/MWh — **cleared** (£32.79, a further
£1.17/MWh below the OLS baseline that set the bar).

### 2.2 Lift over the naive gas-floor-alone baseline

```
naive (gas floor only): MAE=£35.775  RMSE=£76.263  R2=0.3135
model (recalibrated):   MAE=£32.790  RMSE=£70.159  R2=0.4190
MAE reduction: £2.985 (8.3% better)
```

The residual-demand scarcity term earns its place: it improves on the gas floor alone by 8.3% MAE
and materially improves R² (0.314 → 0.419), confirming demand/renewable tightness carries real
explanatory power beyond gas price alone — as merit-order theory predicts.

**Grid-search note on the selected constants:** the pure MAE-argmin grid point is `X_TIGHT=1.38,
p=1.5` (MAE=£32.498) — but this sits right at the edge of the observed `x` range (max observed
x ≈ 1.64), so the convex kicker fires on well under 0.1% of periods: a fit that is, in practice,
indistinguishable from a plain linear-in-x model. `X_TIGHT=0.70, p=2.0` was selected instead — it
costs only £0.29/MWh of MAE (32.79 vs 32.50) relative to the argmin, but keeps the scarcity term
genuinely load-bearing across roughly the tighter 30-40% of periods (x=0.70 sits close to the
60-70th percentile of the observed x distribution), matching the physical intent stated in the
brief ("blows up convexly only when RD is unusually tight") rather than only the top ~1% of
samples. This is a documented judgement call, not a P&L-driven tune (R12) — it trades a negligible
amount of MAE for a materially more meaningful/less degenerate structural fit; both configurations
clear the £34 bar by a wide margin.

### 2.3 Distribution match (full window)

| | mean | median | p95 | min | max |
|---|---|---|---|---|---|
| **Real SSP (actual)** | £77.19 | £55.04 | £220.00 | -£185.33 | £4,037.80 |
| **Recalibrated model** | £69.24 | £48.75 | £217.15 | -£10.47 | £574.22 |

Against the brief's bands:
- Median £48.75 — within the £40-70 target band. ✓
- Mean £69.24 — within the £65-90 target band. ✓
- P95 £217.15 — within the £180-270 target band. ✓
- Min -£10.47 — **negative**, confirming the form is structurally capable of sub-zero output
  (real min is -£185.33; the model reaches only -£10.47 and only 0.013% of periods go negative
  vs 2.241% in reality — see honesty note below). ✓ (capability), gap noted (magnitude/frequency).
- Max £574.22 vs real £4,037.80 — the model does not reproduce the most extreme spike tail (a
  3-feature/5-constant structural model cannot capture rare BM-driven multi-thousand-pound spikes
  that depend on plant outages, interconnector trips, and reserve-scarcity pricing not present in
  these inputs at all). This is an honest known gap, not concealed by the MAE/median/p95 pass.

**Honesty note (negative-price frequency/magnitude gap):** the model is structurally capable of
negative prices and does produce them, clearing the brief's literal bar ("must be capable of
producing negative prices"), but underproduces both their frequency (0.013% vs 2.241% real) and
depth (-£10 vs -£185 real) — an OLS fit minimizing squared error naturally smooths tail behaviour
toward the bulk of the distribution. If a future pass needs negative-price *frequency* fidelity
(e.g. for a curtailment/negative-pricing company capability), this is the gap to close next —
likely via a wider/steeper "abundance" kicker mirroring the tight-margin kicker on the low side of
`x`, which was not requested by this recalibration's bar and was not added to avoid over-fitting
past what a 5-constant structural form can honestly support.

### 2.4 Per-year table (globally-fit constants applied within each year)

| Year | n | SSP mean £ | Model mean £ | MAE £ | R² |
|---|---|---|---|---|---|
| 2016 | 14,484 | 39.32 | 32.63 | 17.18 | 0.0663 |
| 2017 | 17,169 | 44.40 | 42.89 | 17.16 | 0.0388 |
| 2018 | 17,305 | 57.27 | 55.83 | 19.43 | -0.0065 |
| 2019 | 17,226 | 41.75 | 30.54 | 18.82 | -0.1819 |
| 2020 | 16,576 | 34.79 | 19.29 | 22.19 | -0.0321 |
| 2021 | 16,833 | 115.06 | 103.37 | 50.22 | 0.1566 |
| 2022 | 14,963 | 200.07 | 213.57 | 79.16 | 0.3474 |
| 2023 | 17,457 | 94.56 | 74.72 | 44.12 | 0.1660 |
| 2024 | 17,523 | 71.14 | 62.17 | 29.35 | 0.2095 |
| 2025 | 7,570 | 89.85 | 69.59 | 35.09 | 0.1148 |

**Reading this honestly:** as with the OLS regression before it, per-year R² is weak-to-negative
in calm, low-variance years (2018-2020 — a globally-fit set of constants applied to a low-variance
year can do worse than that year's own mean, hence R²<0), and strongest in the 2022 gas-crisis
year (R²=0.347, the highest of any year, both here and in the OLS regression's own per-year table).
This is expected: gas price genuinely dominates the signal when it's moving by 5-10x, and dominates
less when it's flat. The 2019/2020 mean underestimate (model ~£20-30 below actual) reflects the
model structurally pricing toward the gas floor when residual demand is unremarkable — a genuine
limitation of a 5-constant global fit across a 9-year window spanning very different regimes
(pre-crisis calm vs 2021-22 crisis vs 2023-25 partial normalization), named here rather than
tuned away.

---

## 3. R10 simplifications — hand-set constants, what would ground them

Per R10 (absurdity-class defects require registering the invariant/simplification, not an instance
patch), every hand-set (not-fit-to-data) constant introduced or retained in this recalibration:

1. **`EF_GAS_TCO2_PER_MWH_TH = 0.184`** (tCO2 per MWh thermal, natural gas combustion). Standard
   DESNZ/DEFRA greenhouse-gas conversion-factor convention for natural gas. **Would be grounded
   by:** pulling the specific year's published DESNZ/DEFRA GHG conversion factor table (the figure
   drifts slightly year to year, e.g. 2016 vs 2025 factors differ in the third decimal place) and
   time-indexing it, rather than using one fixed value across the whole 2016-2025 window.

2. **`DISPATCHABLE_CAPACITY_MW = 35,000`** (approximate GB dispatchable generation fleet capacity:
   CCGT + OCGT + coal + nuclear + net interconnector import capacity). Asserted as a round-number
   physical scale for normalizing residual demand, not fit to SSP data (per the recalibration
   brief's instruction to register it as an R10 simplification). **Would be grounded by:** a
   National Grid ESO capacity-register figure for the specific settlement date — this fleet has
   shrunk materially over 2016-2025 as coal capacity exited (the last GB coal plant closed
   2024-09-30), so a single fixed figure across the whole window is a real simplification, not
   just a rounding choice.

3. **`carbon_price_gbp_per_tonne` defaulting to `0.0`** throughout `simulation/run_phase3b_recalibration.py`
   — no real historical UK-ETS/EU-ETS carbon price series is wired into this recalibration pass.
   The carbon term in `gas_floor_price` is structurally present and unit-tested (see
   `tests/sim/test_price_engine.py`'s carbon tests) but does not participate in the calibrated fit
   above — A0/A1/A2 above are fit entirely against the no-carbon floor. **Would be grounded by:**
   sourcing a real UK ETS (effective Jan 2021 onward) / EU ETS (pre-2021, GB was under the EU
   scheme) carbon price series, time-indexed at `effective_from`/`effective_to` boundaries per the
   regulation-commons doctrine, and re-running this calibration with the carbon term active to
   check whether it improves the fit (the theoretical case is strong — the 2021-2022 SSP spike
   coincided with an EU/UK carbon price spike as well as the gas spike — but this was not tested in
   this pass).

4. **`X_TIGHT = 0.70` and `SCARCITY_EXPONENT (p) = 2.0`** — selected from a grid search (not the
   pure MAE-argmin; see §2.2 for the documented judgement call) rather than derived from first
   physical principles. These are genuinely fit-to-data choices (unlike 1-3 above, which are
   asserted physical constants), but the SELECTION among near-equal-MAE grid points is a modelling
   judgement, logged here for transparency.

5. **No third-party published benchmark cross-checks the fitted `A0/A1/A2` magnitudes as literal
   numbers** (the gap named in the fidelity-ledger row's `independent_anchor` field). A DISCOVER
   pass on 2026-07-24 (full findings + citations: `docs/market_research/ssp_scarcity_constants_external_benchmark_2026-07-24.md`)
   sought a published UK benchmark and found two genuine ANCHORS that bound and contextualise the
   scarcity term without benchmarking its functional form (both `observed-with-evidence`):
   - **DECC Capacity Market (2015)** — the Dynamic Dispatch Model "allows market prices to spike up
     to £6,000/MWh" (regulatory price ceiling). The fitted multiplier's own max output (~£574/MWh)
     sits ~1 order of magnitude below both this ceiling and the real observed SSP max (£4,038/MWh) —
     externally grounding, not newly discovering, the already-honest **tail-underproduction** gap
     (§ elsewhere in this doc). This is a bound, not a licence to raise the tail: R12 forbids tuning
     toward it; the tail gap remains a diagnosed mechanism issue, unchanged this pass.
   - **Statutory Security of Supply Report (2025)** — the GB Reliability Standard is LOLE ≤ 3 hrs/yr
     (~0.034 % of periods). The code's scarcity kicker firing on ~30–40 % of periods is therefore
     better read as a general **tight-margin markup** than a literal loss-of-load mechanism — a
     naming/interpretation note (`inferred`), not a defect and not a recalibration cue.

   **No source using the identical `A0 + A1·x + A2·max(0, x−X_TIGHT)^p` functional form was found**, so
   `A0/A1/A2` as literal magnitudes **remain unbenchmarked — the gap STANDS, now bounded** by the
   two anchors above. Honoured throughout (R12/R13): this pass GATHERED and RECORDED external context
   only; **no constant was changed, no recalibration performed or recommended**, decided blind to
   company P&L.

---

## 4. Provenance

- **Calibrated against:** `sim/cache/elexon_ssp_full.json` (real Elexon System Sell Price,
  half-hourly settlement periods), joined against `sim/cache/elexon_demand_full.json` (Elexon
  `/demand/outturn`), `sim/cache/elexon_agws_full.json` (Elexon AGWS wind+solar generation,
  **deduplicated to latest publishTime per key** — see the data-quality finding in
  `simulation/run_phase3b_recalibration.py`'s module docstring), and `sim/gas_data/nbp_sap.csv`
  (FRED PNGASEUUSDM TTF-proxy gas price, `sim/gas_prices_history.py`).
- **Window:** 2016-03-01 to 2025-06-07 (the AGWS/demand data-availability window — both endpoints
  return no data before ~2016-03-01, a real boundary, not a bug).
- **n = 157,106** settlement periods with all four inputs present (matches the n reported by the
  pre-existing OLS regression on the same join, confirming the join logic itself is unchanged —
  only the renewable-generation deduplication differs).
- **Blind to company P&L:** this recalibration run touches no company-layer code, reads no
  company state, and is not gated by or tuned against any P&L outcome (R12/R13). The price engine
  remains gated OFF in every production simulation phase — nothing currently reads
  `sim/price_engine.py`'s output, so this commit cannot perturb current results.
- **Reproducible:** `python3 -m simulation.run_phase3b_recalibration` regenerates every number in
  this document from the cached real data.

---

## 5. Proposed level

**Proposed: L1 (structural fix + calibration evidence landed; NOT proposing L2/L3).**

Rationale: the ~10x overestimate defect is fixed and the hard MAE/distribution bar is cleared with
real-data evidence (this document + the recalibration script), and the fix is R15-mutation-tested
(a reversion to the old raw-ratio form fails `test_price_engine_realistic_distribution_over_sample_periods`
hard — every sample period would price in the thousands of £/MWh). However: (a) the engine has
**no live consumer** — it is gated off in every production phase, so there is no coupled-triad
company-side test of it yet (per COUPLED TRIAD doctrine, "no world/SIM atom reaches L3 until the
company has been tested against it and the gap measured" — that has not happened here and can't,
while the engine is unwired); (b) the negative-price frequency/magnitude gap (§2.3) and the
uncalibrated carbon term (§3.3) are named, real limitations, not fully closed. Wiring this engine
into any live phase (replacing or supplementing the OLS regression for Regime-3 projection) would
be a separate, larger decision requiring its own gate — not proposed here.

## DIRECTOR FIDELITY STEER (console 2026-07-19) — the top gap is the spike tail, not calm-year MAE
The emitter's first result ("structural model worse than OLS in 6/10 years") is the **average trap**. Scored
**worst-cell** (atom A / G1 CVaR), the model is **strongest in 2022** (R²=0.347, its best year, beating OLS's
own 2022) and weakest in **calm 2018–2020** — years where nothing commercial is at stake. Ranked by
**exposure / value-at-risk** (atom F), the top fidelity gap is the **extreme spike tail the engine
under-represents**:

| metric | model | real | under-representation |
|---|---|---|---|
| max SSP | £574/MWh | £4,038/MWh | ~7× |
| negative-price frequency | 0.013% | 2.241% | ~170× |

The spike tail is what triggers **collateral calls and kills suppliers** — so under VaR ranking this is the
**TOP price-engine fidelity priority**, far above reducing calm-year MAE. **W1_6's real L2→L3 fidelity target
is reproducing the extreme tail** (spike magnitude + negative-price frequency), NOT the mean. Registered as
director direction; the emitter/G1 scoring already computes worst-cell CVaR — the emphasis is now exposure-tail,
not average.

## Named simplification — calm-year negative-lift bound (registered 2026-07-24, scope-2b)
**`simplification_id: ssp_scarcity_form_calm_low_x_underfit_bounded_2026_07_24`** (on the W1_6
fidelity-ledger row; mechanised by `background/fidelity_evidence_ledger.py::fidelity_evidence_gate`
reason (d) — a positive aggregate lift that hides negative per-cell lifts reds the DoD gate until an
honest bound is registered; R15 both-ways proven in `tests/test_fidelity_evidence_ledger.py`).

**The bound.** The single-global residual-demand scarcity form (`sim/price_engine.py`, one A0/A1/A2
across 2016-03..2025-06) EARNS its structure in scarcity/high-x and crisis regimes but UNDER-FITS the
renewables-heavy low-x calm years, LOSING to a per-cell OLS in 6 of 10 year-cells (y2019 −0.79,
y2020 −3.22, y2021 −2.21, y2023 −0.27, y2024 −1.18, y2025 −2.28 £/MWh MAE lift). The headline
+1.17 £/MWh aggregate lift is therefore CONCENTRATED (2022 crisis peak +5.55, plus 2016–18 wins
against the weak gas-floor baseline), NOT a uniform edge.

**Decomposition (evidence, not assertion).** `tools/ssp_scarcity_dwell_fraction.py` (Test A) refuted
the "scarcity term dormant in calm years" hypothesis — the convex kicker is live 17.5–55% of every
year — and redirected the mechanism to **secular x-distribution drift** (median x 0.73→0.46 over the
decade as renewables grow). `tools/ssp_refit_local_vs_global.py` (Test B) then decomposed the loss by
refitting the SAME form locally per cell (X_TIGHT/exponent/A2 held fixed):
- **~half is calibration-recoverable** — a same-form local A0/A1 refit FLIPS y2019/y2023/y2024
  non-negative (per-year A0 drifts 0.11→1.11, A1 0.9→2.0 with the x-distribution).
- **~3 cells are form-irreducible** — y2020 (−0.41), y2021-crisis (−1.20), y2025 (−2.73) stay
  negative even after a local refit: a residual the residual-demand form cannot represent at up to
  ~£2.7/MWh MAE regardless of calibration freshness.

**Why accepted (not tuned) — R13/R12.** (1) The form must be ONE physics across the window (a
baseline/fidelity property, decided blind to company P&L). (2) The director's **2026-07-19 console
steer** (recorded above) ranks calm-year MAE as *"the average trap … years where nothing commercial
is at stake"* below the spike-tail priority — so honestly bounding-and-registering the calm-year loss
is the director-aligned close, and recalibrating it is explicitly NOT the top price-engine fidelity
work.

**The recoverable half is a DELIBERATE follow-on, not closed here (part-2a).** An era-aware A0/A1
recalibration tracking the observed x-drift would recover y2019/y2023/y2024, but the era partition is
an R13-sensitive baseline choice that must be externally grounded (renewables-penetration / dispatchable-
capacity boundaries — the module already flags `DISPATCHABLE_CAPACITY_MW=35000` as held-constant while
the real fleet shrank with coal exit), NOT autonomously curve-fit to flip the sign of a lift cell. It is
tracked as the part-2a follow-on on `PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md`.
