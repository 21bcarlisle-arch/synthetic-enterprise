# W1_5_premise_demand_shape — FRAME (canonical per-atom, doc-only)

**Atom:** `W1_5_premise_demand_shape` · lane `W1_market_weather` · dial 3 · `provenance: proposal`
· `level_current: 0` → `level_target: 3` · `loop_stage: idle`
· `depends_on: [W1_4_regional_weather_field]`
· COUPLED twin of `C13_weather_normalisation` (company leg: `C13`; this is the **world/SIM** leg).

**Turn:** H17 Lane-3 FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1,
level reported via `docs/design/atom_status/W1_5_premise_demand_shape.yaml`).

---

## Why this doc exists (and why it is NOT churn)

W1_5's FRAME-stage thinking already exists — it is **§1.3 and the I2 half of §2** of
`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md`, the shared multi-atom physics-hierarchy
design that registered `W1_3`/`W1_4`/`W1_5`/`W1_6` and `C13` together. But that filename
carries no `FRAME` (it is the *hierarchy's* home, not `W1_5`'s own), so the intrinsic
frame-saturation guard (`supervisor.py::_atom_has_frame_doc`, which requires an `evidence`
entry whose **filename** contains `FRAME`) correctly reads W1_5 as genuinely un-FRAMEd and
keeps re-offering it to the idle DISCOVER/FRAME draw — exactly the pattern already closed for
`C13_weather_normalisation` (`docs/design/frame/C13_weather_normalisation_FRAME.md`),
`W1_3_national_weather_signal`, `W1_4_regional_weather_field`, and `W1_7_renewable_capacity_
trends`, all of which needed the identical missing-terminus fix.

This doc is that missing terminus. It **consolidates, does not re-derive**,
`WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.3 (the premise-demand decomposition), the I2 half of
§2 (the premise→national reconciliation invariant + its mutation test), §6 (the wall + the
`C13` gap metric, W1_5's own coupled-triad half), and §7 (the C-S2 substream discipline). By
authoring it, `_is_frame_saturated(W1_5)` becomes `True` on the next cycle — computed from
disk, MAKE_IT_STICK, no marker to remember — so the next idle draw yields W1_5 to genuinely
un-FRAMEd work instead. That is the honest end state: FRAME work on W1_5 IS complete once
consolidated; the only remaining path to `level_target` is BUILT, gap-measured, coupled code
the epoch gate defers. Re-emitting FRAME content beyond this point is the churn
SELF_INTERRUPT_DISCIPLINE + R12 forbid.

`WEATHER_PHYSICS_HIERARCHY_DESIGN.md` remains authoritative for the full four-layer cascade
(L1–L4) and its cross-atom detail; this FRAME cites it, it does not duplicate it.

---

## (a) The demand decomposition — grounded in §1.3

Each premise `i`'s half-hourly demand is a **layered composition**, not a single draw, reading
its own **local (L2, `W1_4`) weather**, not the national signal:

```
d_i(t) = baseload_i(t)
       + heating_i · g_heat( T_r(i)(t), thermal_i, heating_type_i )   # temp-driven, regional
       + occupancy_i · s_occ(t, archetype_i)                          # diurnal/day-type shape
       + solar_offset_i · g_solar( I_r(i)(t) )                        # if premise self-generates
       + η_i(t)                                                       # idiosyncratic noise
```

`r(i)` is premise `i`'s region (its `W1_4` local weather, not the national `W1_3` mean);
`g_heat` is a convex-below-threshold thermal response whose slope is set by the premise's
`thermal_i` (EPC/insulation) and `heating_type_i`. **Nothing here is new state**: `archetype_i`,
`heating_type_i`, `thermal_i`, `occupancy_i` are read from `simulation/household.py`'s
`Household` (already carries `PropertyType`, EPC rating/`InsulationLevel`, `HeatingSystem`,
solar/EV — confirmed present in the live module), the archetype mix from
`W2_1_archetype_layers` (`simulation/household_segments.py`), and which premises exist from
`W2_2_population_draw` (`simulation/population_draw.py`). The half-hourly *shape* templates
(`s_occ`) reuse `simulation/demand_model.py`'s existing archetype curves — L3 **modulates** an
already-existing shape by local weather rather than replacing it (SIMPLICITY GUARD: add
discipline, not a new demand engine). `simulation/household_demand.py`'s existing
`epc_multiplier * (1 + ev_fraction) * max(0, 1 - solar_fraction)` composite is the closest
existing precursor for the non-weather layers and should be extended, not duplicated.

## (b) THE RECONCILIATION INVARIANT (I2) — mutation-tested, per R15

Let `nᵢ` be the number of real premises simulated premise `i` represents (a scale-up factor at
the current ~31-account cast; ≈1 at full population). Define the residual:

```
ρ_dem(t) = Σ_i nᵢ · d_i(t)  −  D_national(t)
INVARIANT (I2):  |ρ_dem(t)| ≤ tol_dem   for every period t
```

`D_national(t)` is held from the **L4 weather→demand curve** (`WEATHER_PHYSICS_HIERARCHY_
DESIGN.md` §1.4's `f_demand`), an **independent** source — the checker must never define
national demand as the premise sum it is checking (the TAUTOLOGY pattern R15 forbids). This is
enforced **by construction, not luck**: after composing premise demands, a single national
**multiplicative** rescale `α(t) = D_national(t) / Σ_i nᵢ d_i(t)` is applied,
`d'_i(t) = α(t)·d_i(t)`, preserving each premise's *shape and relative weather response* (the
ratios are the load-bearing information L3 layering exists to create) while forcing exact
reconciliation. `tol_dem` is numerical (machine-epsilon scale), not a modelling fudge.

**The named defect the mutation test must inject and detect (R15 — a control that cannot fail
is worthless):** perturb one premise's response **off-manifold after the rescale** — e.g.
multiply one premise's heating coefficient by 5 (a fabricated super-responder) without
re-running `α(t)`, or drop one premise's `nᵢ` scaling entirely. The check MUST FIRE:
`|ρ_dem(t)| > tol_dem`. A second mutation attacks the denominator directly (zero out
`Σ_i nᵢ d_i(t)` — a division-guard case) and must fail loud, not divide-by-zero silently
(FAIL-OPEN pattern). A third — an empty premise set or a NaN `d_i` — must likewise fail loud,
never pass trivially (FAIL-OPEN) or pass because the checker itself errored out unnoticed
(FAIL-SILENT). No L3 for `W1_5` without these three mutation tests actually demonstrated
green-then-red (R15: no control counts as evidence for a promotion unless mutation-tested).

## (c) RNG substream discipline (C-S2)

Premise idiosyncratic noise `η_i(t)` draws from its **own named, seeded substream**
(`premise_noise`, per `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §7), derived exactly as
`simulation/population_draw.py::_substream()` already does (SHA-256 of base seed + salt → an
independent `random.Random`) — distinct from `national_regime`, `regional_field`, and `price`.
This is not a stylistic preference: it is the direct fix for the class of bug the real 01:09Z
shared-life-event-RNG incident proved (adding a new draw to a shared stream shifted every
downstream draw). Consequence for W1_5 specifically: adding, removing, or re-parameterising a
premise's noise draw must never shift the national weather path, the regional field, or the
price chain's output — testable via the existing `test_substream_isolation_*` pattern, not
merely asserted. Replaying a history with the same seed must reproduce identical premise
demands (C-S2 deterministic replay).

## (d) The wall — company-knowable vs SIM-internal

| Company CAN observe (through the wall) | Company CANNOT observe (SIM-internal, this atom) |
|---|---|
| Published **national + regional** (`W1_4`) weather forecasts/outturns | Each premise's true `thermal_i` / `heating_type_i` / `archetype_i` (this atom's L3 ground truth) |
| Its **own meter reads** — confounded aggregate consumption of *its* book | The idiosyncratic noise draw `η_i(t)` and the true per-premise weather-sensitivity slope |
| Wholesale prices (L4 outturn) | The counterfactual demand a premise would show under different weather |

The company can never read `d_i(t)` or its decomposition directly — only the settled meter
total of its own book, already confounded by tariff, billing cycle, and its own customer mix.
This is precisely why `C13_weather_normalisation` must **infer** book-level weather
sensitivity from confounded reads rather than read it off — the wall is what makes that
company-side problem genuinely hard, matching real supplier weather-correction practice.

## (e) The coupled-triad gap — how C13 measures against this world leg

Per `COUPLED_TRIAD_DESIGN` and `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6.2 (full formula
owned by `C13`'s own FRAME, cited not repeated here): `C13`'s belief `b` is its fitted
weather-normalisation model's **predicted** book demand `D̂_book(weather_t)` under a given,
observed weather outturn; the hidden truth `θ` this atom supplies is the **actual** book
demand `Σ_{i∈book} nᵢ d_i(t)` the SIM realised under that same outturn (harness-side read of
this atom's own L3 ground truth, never exposed to `C13` directly). `gap = raw_gap / g0` reads
0→perfect-recovery (structurally unreachable — reaching it means an observable leaked L3
truth, a wall defect not a triumph), 1→no-better-than-blind-national-correction,
0<gap<1→genuine partial learning (the honest steady state). **Binding COUPLED_TRIAD rule:**
`W1_5` may not reach `level_target` (L3) until `C13` has actually been run against it and the
gap measured — symmetric, neither atom completes alone.

## (f) L1/L2/L3 for W1_5, in W1 terms

- **L1** — flat per-archetype demand with a single national temperature sensitivity (no
  regional or per-premise variation); the reconciliation invariant exists and is
  mutation-tested from day one (per R15, an invariant is never deferred to "later").
- **L2** — full layered decomposition (a)-(c) above wired to real `W1_4` regional weather and
  real `household.py`/`household_segments.py` archetype state; I2 holds across the whole
  population; premise-level noise substream isolated and proven.
- **L3** — time-varying archetype mix and thermal-performance drift (retrofit/heat-pump
  adoption reshaping `g_heat` over the run), curriculum-controlled regional severity events
  feeding through `T_r(i)(t)`, and the `C13` gap actually measured and reported per digest
  (the coupled-triad binding condition for L3, not optional polish).

## (g) Known simplifications (R10)

- **Temperature-only `g_heat` in the first cut** — a Composite-Weather-Variable (wind-chill)
  term is named in §1.3/§6.3's hedging-frontier discussion as a real refinement; deferring it
  is a named simplification, not a hidden gap, and will under-explain demand versus the
  wind-coupled L1/L4 physics until added.
- **Small-cast statistical power** — at the current ~31-account cast, the I2 aggregate and the
  `C13` gap are directionally noisy (per §9 of the hierarchy design); `W2_2_population_draw`
  reaching full population is the real fix, not a W1_5-side patch.
- **C-S5 time-scale invariance** — `g_heat`/`s_occ` couple a daily regime step (L1) to a
  half-hourly diurnal shape; this coupling is **not** fully time-scale invariant and must be
  registered explicitly as a named exception if W1_5 ever claims a settlement-granularity
  change (per the hierarchy design's own §7 admission for the wider cascade).

---

## The single BUILD-unblock gate

| Atom | Level (held) | Single BUILD-unblock gate | Gate class |
|------|--------------|---------------------------|------------|
| `W1_5_premise_demand_shape` | **0 (→3)** | `W1_4_regional_weather_field` reaches an L-usable regional weather field to drive `T_r(i)(t)`/`I_r(i)(t)` — **current map state: `W1_4` at `level_current: 1`, still `loop_stage: idle`, its own BUILD-unblock gate (per `docs/design/frame/W1_4_regional_weather_field_FRAME.md`) unmet** — plus **Epoch-3 BUILD-open** (TWIN, within the open epoch, per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md). Then BUILD adds the layered premise-demand composition over the existing `household.py`/`household_segments.py`/`demand_model.py` state, wires the I2 rescale + its three mutation tests, isolates the `premise_noise` substream, and registers `W1_5↔C13` in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (currently absent, same gap `C13`'s own FRAME already flags). | DIAL (depends_on + epoch sequencing) |

**Disposition:** level **HELD at 0** (proposal atom; FRAME complete ≠ built; BUILD-gated,
EPOCH_GATING Rule 1). This FRAME is W1_5's canonical terminus; the next idle draw reads W1_5
as frame-saturated and yields to genuinely-un-FRAMEd work instead. No BUILD code, no map edit
(F1).

---

*Sources consolidated (not re-derived): `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.3
(premise-demand decomposition), §2 (I2 invariant + mutation test), §6 (wall + gap metric,
hedging frontier), §7 (C-S2 substream discipline), §9 (open simplifications);
`docs/design/frame/C13_weather_normalisation_FRAME.md` (the coupled company leg, gap-formula
detail owned there); `docs/design/frame/W1_4_regional_weather_field_FRAME.md` (the dependency's
own gate state); `docs/design/COUPLED_TRIAD_DESIGN.md` (gap-formula family); live
`simulation/household.py`, `simulation/household_demand.py`, `simulation/household_segments.py`,
`simulation/population_draw.py::_substream()` (real precursor code confirmed present).*
