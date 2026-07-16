# FRAME — W1_4_regional_weather_field — Regional (GSP/DNO) weather field over the national signal

- **atom**: `W1_4_regional_weather_field` | lane `W1_market_weather` | epoch/dial 3
- **level_current**: 0 → **level_target**: 3 | **depends_on**: `W1_3_national_weather_signal`
- **stage**: BUILD-gated (`loop_stage: idle`). This is DISCOVER/FRAME work only — no BUILD code.

## 1. What this atom is & real-world grounding

W1_3 produces a **national** weather signal (a GB-aggregate temperature/wind/irradiance path that drives
national demand and non-dispatchable generation). Real GB weather is not uniform: at any instant the
system experiences a **spatially-varying field**. Scotland runs colder and windier; the South East is
milder and lower-wind; the South West and coasts get more Atlantic frontal weather; wind resource is
concentrated in the north and offshore. These differences are **material to a supplier and to the
system**: heating demand, embedded (distribution-connected) PV and wind output, network constraints, and
loss-of-load risk all vary by locality, not just nationally.

This atom adds the **L2 regional layer**: spatially-correlated regional **deviations** laid *on top of*
the W1_3 national signal, keyed by a GB region set. The natural keys are the real market geographies:

- **GSP Groups** — the 14 Grid Supply Point Groups (the `_A`…`_P` distribution regions used in Elexon
  settlement / profiling and in the DUoS/loss framework). This is the settlement-native regionalisation
  and the strongest candidate key.
- **DNO licence areas** — the 14 distribution network operator areas (aligned 1:1 with GSP Groups in
  practice), the physical-network view.
- **NESO/ESO zones** — coarser transmission/constraint zones (e.g. the B6 Scotland–England boundary),
  relevant to network constraint and embedded-generation curtailment.

The field is a set of per-region deviations `Δ_r(t)` (e.g. regional temperature = national + Δ_temp_r,
regional wind = national scaled/offset by Δ_wind_r) that are **spatially coherent** and, critically,
**aggregation-consistent** with W1_3. *No specific regional temperature/wind climatology numbers are
fabricated here: any regional mean, offset, or covariance value is a **benchmark required (source:
Met Office / Open-Meteo reanalysis / NESO regional demand)**.*

## 2. The central INVARIANT — demand-weighted regional aggregate reconciles to the national signal

The atom's **defining invariant**: the regional field is not free — it must **reconcile** to the national
signal that W1_3 already published. If you re-aggregate the regional values back up using the correct
weights, you must recover the national signal within tolerance. This is what makes the regional layer a
*decomposition* of the national truth rather than an independent, contradictory second story.

Conceptually, for a weather variable `x` at time `t`:

```
  x_national(t)  ==  Σ_r  w_r(t) · x_region_r(t)      within tolerance ε
```

where `w_r(t)` are the **reconciliation weights**. The weight choice is variable-specific and must match
how the national signal is physically constructed:

- **Demand-relevant variables (temperature):** `w_r` = **regional demand share** (demand-weighted mean),
  because national demand responds to a demand-weighted temperature, not a land-area-weighted one. A cold
  snap over the densely-populated South East moves national demand more than the same snap over the
  sparsely-populated Highlands.
- **Generation-relevant variables (wind, irradiance):** `w_r` = **regional installed-capacity share** for
  that technology (a wind-capacity-weighted regional wind reconciles to national wind generation drive).

Equivalently in deviation form, the invariant is that the **weighted regional deviations sum to zero**:
`Σ_r w_r(t) · Δ_r(t) == 0`, so adding the regional field neither adds nor removes national-level energy —
it only *redistributes* it spatially.

**Acceptance condition (R15 — controls must be able to FAIL):** the reconciliation invariant MUST be
**mutation-tested**. The killer test plants a region whose deviation is corrupted (e.g. one GSP Group's
temperature deviation multiplied, or the reconciliation weights swapped for area weights) such that the
demand-weighted regional aggregate **no longer equals** the national signal — and the check MUST FAIL on
it. Three failure surfaces to close explicitly, matching the R15 doctrine:
- **TAUTOLOGY:** the checker must recompute the aggregate **independently** from the regional field, not
  read back a stored "national" value that was itself derived from the same sum — otherwise it always
  passes. The national signal it reconciles against is W1_3's, produced upstream and independently.
- **FAIL-OPEN:** an empty/missing region set, all-zero deviations, or a NaN weight must **fail**, not pass
  trivially (a degenerate field is not a reconciled field).
- **FAIL-SILENT:** if the national signal or the weight table is unavailable, the check is a **FAILED**
  check, never a skipped-and-green one.
The tolerance `ε` is a stated, justified number (float round-off + any declared, named simplification),
never a slack big enough to hide a real reconciliation break.

## 3. Spatial coherence & feasibility

Regional deviations must be **spatially coherent**: a cold spell or a wind lull is a synoptic-scale event
spanning neighbouring regions, not an artefact confined to one GSP Group. Neighbouring regions are
**positively correlated**; correlation decays with distance. Independent per-region noise is *wrong* — it
would let Scotland freeze while the adjacent Borders stay mild, which is unphysical and would also make the
national aggregate implausibly smooth.

Method options (to settle at BUILD, not decided here):
- **Spatial covariance / Gaussian field:** draw regional deviations from a multivariate normal with a
  covariance matrix whose off-diagonals encode an inter-region **adjacency/distance** structure (e.g.
  exponential decay in centroid distance). Then **project** the draw onto the constraint surface so the
  weighted deviations sum to zero (a linear reconciliation step), preserving coherence while enforcing the
  invariant.
- **Conditional sampling given the national signal:** sample the regional field *conditioned* on the
  already-fixed national value — the national signal is a hard constraint, regional structure fills the
  remaining degrees of freedom. This makes the reconciliation invariant hold **by construction** (still
  mutation-tested to prove the construction is honest, per §2).

**Feasibility:** regional values must be physically possible — temperatures within realistic bounds, wind
speeds non-negative and within regional climatological ceilings, irradiance non-negative and diurnally
consistent. A named feasibility check rejects impossible regional values; a planted out-of-range region is
a second mutation test.

## 4. COUPLED TRIAD (mandatory — the gap is the score)

- **SIM adds (world depth):** generates the regional weather **ground-truth field** — spatially-coherent,
  feasible, reconciling to W1_3's national signal. The SIM knows the true per-region temperature/wind/
  irradiance and therefore the true regional demand and true embedded-generation output.
- **COMPANY discovers/copes (through the wall — may be wrong):** the company never reads the SIM's regional
  field. It observes **regional consequences** through the wall — regional metered demand (via its own
  customers' locations / GSP Group), regional embedded generation as seen in settlement, published regional
  weather/temperature series a real supplier could buy (Met Office / third-party). It must *build its own
  belief* about regional structure to forecast regional demand, site-mix exposure, and shaping cost. A
  supplier that treats the country as spatially uniform, or mis-estimates its regional concentration, is a
  *permitted* failure mode.
- **HARNESS measures (belief-vs-truth GAP):** company's regional demand/embedded-generation **estimate vs
  SIM truth** per region; and it **enforces the aggregation invariant** as a structural gate on the SIM
  field. The gap is reported per coupled pair (W1_4 SIM ↔ company regional forecasting ↔ this harness) each
  digest and at the Proof door. Per COUPLED_TRIAD: this atom may not reach L3 until the company has been
  tested against the regional field and the gap measured.

## 5. Level decomposition (target L3)

- **L1** — A small fixed region set (e.g. Scotland / North / Midlands / South) with **static** demand-share
  weights. Deviations are simple, spatially-coherent offsets on temperature only, reconciled to the W1_3
  national signal. The reconciliation invariant exists and is mutation-tested from day one. No embedded-gen
  consequence yet.
- **L2** — Full **14 GSP-Group** region set; wind and irradiance regionalised (with capacity-share weights
  for the generation variables); a proper spatial covariance / conditional-sampling method giving realistic
  inter-region correlation; feasibility checks. Regional embedded-generation output exposed as a company
  observable. Reconciliation invariant holds across all variables, weighted correctly per variable.
- **L3** — **Time-varying weights** (demand and capacity shares evolve — e.g. growing northern wind, load
  growth by region); regional network-constraint / curtailment consequences (embedded-gen spill when a
  boundary binds); curriculum-controlled regional severity events (director-authored). Full triad gap
  reported per region. Time-scale-invariant reconciliation (C-S5) stated explicitly.

## 6. Dependencies & sequencing

- `depends_on: W1_3_national_weather_signal` — this is a **layer on top of** the national signal: the
  regional field is defined *as deviations from* the national value, and its defining invariant reconciles
  *to* that value. It **cannot exist before W1_3** — without a stable national signal there is nothing to
  decompose and nothing to reconcile against. Building regional structure on a placeholder national signal
  would bake a fake decomposition.
- **BUILD-gated now** because W1_3 is upstream and not yet settled. **Unblocks BUILD when** W1_3 exposes a
  stable national weather signal at the SIM seam AND the reconciliation weights (regional demand shares,
  regional generation-capacity shares) have a benchmark source.
- DISCOVER/FRAME (this artifact), the reconciliation-method choice (§3), region-key research (GSP vs DNO vs
  NESO zone), and benchmark-sourcing of regional climatology + weights are all available **now** and do not
  move BUILD level.

## 7. Scale-readiness lenses

- **C-S2 — RNG substream discipline + deterministic replay:** the regional deviation draws MUST come from
  their **own named, seeded RNG substream** (`weather.regional`), distinct from the national-signal
  substream and from every other subsystem — so adding/altering regional draws can never shift another
  subsystem's outputs (the exact class of bug the 01:09Z life-event incident proved). Replaying a weather
  history reproduces an identical regional field and therefore identical reconciliation.
- **C-S5 — time-scale invariance:** the **reconciliation invariant is time-scale invariant** — the
  weighted-sum-equals-national identity holds at any settlement granularity (HH, hourly, daily), since it is
  an algebraic identity over whatever time index the national signal uses. This holds as long as the weights
  and the national signal share the same time index; any per-period-weight assumption that breaks under a
  different granularity is registered as a named simplification (R10). The *sampling* method (covariance /
  conditional) is likewise granularity-agnostic. State this explicitly at L3.
- **C-S1 / C-S4:** regional field values arrive/persist through the same append-only event-log / typed-seam
  discipline as the national signal; no batch-completeness assumption in any company-side consumer.
- **SIMPLICITY GUARD:** satisfy with the simplest construct — a region set + a weight table + a covariance
  structure + a linear reconciliation projection. No region-adapter cathedral, no GIS engine.

## 8. Portability lens

- The **region set is keyed by market geography, not hardcoded to GB.** Model it as a typed
  `RegionField` over a configurable region key set with an associated weight table — a second geography
  (different settlement regions, different DNO-equivalents, different climatology) must fit **behind the
  same seam** by supplying its own region set + weights + covariance, without touching the reconciliation
  logic. The reconciliation invariant (weighted regional == national) is geography-independent by design.
- Avoid embedding "14 GSP Groups" as a constant in logic; it is *this geography's* configuration. Hardcoded
  region names/count in already-shipped code = portability debt, remediated on next touch, not speculatively.

## 9. Curriculum note (R13 — the baseline/curriculum split)

- **Baseline (fidelity-only):** the *realistic* regional climatology — inter-region correlation structure,
  typical regional offsets, the demand-share and capacity-share weights — is calibrated **to reality, blind
  to company P&L**. It changes only for fidelity-to-reality reasons (better reanalysis data, corrected
  weights), never because company results look wrong.
- **Curriculum (director-owned):** *regional severity* — how extreme a regional cold snap / wind lull /
  regional constraint event a given world throws at the company — is a **named, versioned, director-authored
  scenario** ("Scenario: 2010 Scotland deep freeze"), never silent parameter drift and never tuned by the
  agent in response to company outcomes. The agent controls both sides of the wall, so regional difficulty
  must face the director.
