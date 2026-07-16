# C13_weather_normalisation — FRAME (canonical per-atom, doc-only)

**Atom:** `C13_weather_normalisation` · lane `C_customer_ops` · epoch 3 · `provenance: proposal`
· `level_current: 0` → `level_target: 3` · `loop_stage: idle` · dial 3
· `depends_on: [W1_5_premise_demand_shape, A6_coupled_triad_gap_metric]`
· COUPLED twin of `W1_5_premise_demand_shape` (world twin: `W1_5`; this is the **company** leg).

**Turn:** H17 Lane-3 DISCOVER/FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map
edit — F1, level reported via `docs/design/atom_status/C13_weather_normalisation.yaml`).

---

## Why this doc exists (and why it is NOT churn)

C13's FRAME-stage thinking already existed but was **scattered across two non-canonical
files**, neither of which the intrinsic frame-saturation guard
(`supervisor.py::_atom_has_frame_doc`) recognises as C13's own FRAME:

1. `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6 — authoritative for the **wall**,
   the **gap metric**, and the **national-vs-regional hedging frontier**, but embedded in a
   shared multi-atom physics-hierarchy design (filename has no `FRAME`, and it is W1_3/4/5/6's
   home, not C13's).
2. `docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md` — the repo overlap audit, the real
   UK weather-normalisation **method** (HDD/CDD, CWV, seasonal-normal, AQ correction), the
   concrete **seam gap**, and the open questions. Filename is `_DISCOVER`, not `_FRAME` — a
   DISCOVER-stage doc, correctly read as **un-saturated** by the guard (a genuinely-unframed
   atom must never be falsely marked saturated — proven by
   `tests/background/test_frame_saturation_draw_marker.py::test_discover_stage_doc_under_design_is_not_a_frame_doc`).

The consequence: C13 was **repeatedly (and correctly) re-offered** by the idle-DISCOVER/FRAME
draw as genuinely-un-FRAMEd, because it had **no canonical per-atom FRAME terminus** stating
its single BUILD-unblock gate the way the other five drawn atoms do. This doc is that missing
terminus — it **consolidates** (does not re-derive) the two sources into C13's own FRAME with
its gate stated once, and by doing so makes `_is_frame_saturated(C13)` return `True` on the
next cycle (computed from disk, MAKE_IT_STICK — no marker to remember). That is the honest end
state: C13's FRAME work IS complete once consolidated; the ONLY remaining path to `level_target`
is BUILT, green, coupled code the epoch gate defers. Re-emitting FRAME content beyond this point
would be the churn SELF_INTERRUPT_DISCIPLINE + R12 forbid.

The two source docs remain authoritative for their own depth (§6 for the gap derivation, the
DISCOVER doc for the method grounding); this FRAME cites, it does not duplicate.

---

## 1. The wall (company-knowable vs SIM-internal) — from §6.1, confirmed against seam code

| Company CAN observe (through the wall) | Company CANNOT observe (SIM-internal) |
|---|---|
| Published **national + regional** weather forecasts/outturns (L2 is public) | Each premise's true `thermal_i` / `heating_type_i` (L3 ground truth, `simulation/household.py`) |
| Its **own meter reads** — confounded aggregate consumption of *its* book, via `get_settlement_data` | The **latent regime label** (L1 internal to the weather engine) |
| Wholesale prices (L4 outturn), via `get_forward_price` | The **counterfactual** demand under a different weather, and its book's true weather-sensitivity |

**Therefore the gap:** the company must **infer its book's weather sensitivity —
weather-normalise — from confounded meter data**. Genuinely hard; genuinely done badly in the
industry (weather-correction is a known error-prone step in real supplier settlement/forecasting).

**Seam gap confirmed against real code (DISCOVER §1):** `company/interfaces/sim_interface.py`
has **no** weather/degree-day/forecast method today (`get_settlement_data`, `get_forward_price`,
`get_customer_status`, `notify_churn`, … only). `point_in_time_view.py`'s own docstring already
records weather crossing as "left for a later pass". C13's BUILD is that later pass: it must add a
new **typed** crossing (`get_regional_weather_outturn`/`get_regional_weather_forecast`-shaped),
exposing the outturn value only — never the latent regime label — per the typed-flow-seam
preference (BACKGROUND_LANE_AND_WALL.md) and C-S3 async wall contracts.

**Hard don't-reuse finding (DISCOVER §1, single most important):** `sim/weather_hdd.py` computes
the SIM's own ground-truth HDD adjustment by reading each customer's **real** per-property weather
CSV directly — exactly the read a real supplier cannot do. C13 must **reconstruct the HDD/CDD
method company-side from observables only**, NOT import that code path.

## 2. The gap metric (from §6.2, per COUPLED_TRIAD_DESIGN §1 — the fifth worked example in the family)

- **Belief `b`:** the company's fitted weather-normalisation model applied to a *given, observed
  weather outturn* → a **predicted book demand** `D̂_book(weather_t)`.
- **Hidden truth `θ`:** the **actual** book demand the SIM realised under that same outturn
  (harness-side, reading L3 ground truth).

```
raw_gap(W1_5, C13) = (1/|P|) Σ_periods | D̂_book(weather_t) − D_book_actual(t) |
g0                 = same error from a NO-SKILL baseline — flat national degree-day correction
                     applied to the whole book (no book-specific, no regional discrimination)
gap                = raw_gap / g0        # dimensionless, per COUPLED_TRIAD reading convention
```

Reading convention (identical to every coupled pair): `gap→0` = perfect recovery
(**structurally unreachable** — reaching it means the observables leaked L3 thermal truth, an
epistemic-wall DEFECT, not a triumph); `gap→1` = no better than the blind national correction;
`0<gap<1` = learned some book-specific/regional structure, not all (the honest steady state);
`gap>1` = worse than blind (a harmful model — red). **Trend is the story:** `Δgap` falling = the
company is learning its book's weather shape; static = not adapting (a finding); rising =
regressing. Basis note (R14): a gap is a ratio with no settled/billed/banked clock, but the pair
must state its measurement basis (which book, which weather window, as-of date) so a falling trend
can't be an artefact of a changed population/weather window (anti-R12: the gap is a DIAGNOSTIC,
never a target — never tune the model toward a lower gap by leaking truth).

## 3. What C13 fits, concretely (from DISCOVER §2–§3 — a named regression, not a black box)

A per-segment (book-wide until segmentation exists) **regression of observed consumption against a
regional degree-day series built from the observable regional weather feed** — the real
"regression-based normalisation" method: fit consumption-per-unit-HDD/CDD on the company's own
`get_settlement_data` history, then feed a given weather outturn back through the fitted coefficient
to produce the predicted demand `D̂_book` of §2. Grounded in the four real UK methods (DISCOVER §2):
HDD/CDD (gas base 15.5°C), NESO seasonal-normal comparison, the gas-industry **Composite Weather
Variable** (effective temperature + wind chill — temperature-only will systematically under-explain
demand vs the SIM's wind-coupled L3 physics, a candidate **named simplification** per R10, not a
defect to hide), and AQ weather correction. The model is **genuinely re-fittable and genuinely
capable of being wrong** when the book's composition shifts faster than the regression window
adapts — which is *why* real suppliers get this wrong, and the point of the atom.

## 4. The strategy surface this creates (from §6.3 — the hedging frontier, make BOTH extremes bite)

GB has **no regional forward market**, so regional basis cannot be hedged today (the zonal-pricing
debate — see LATER atom `W1_8`, and its own company twin `B5_regional_basis_risk`). The SIM must
make both ends of the frontier cost real money:
- **Hedge to the NATIONAL forecast** (liquid, cheap) with a **regionally-skewed book** → left
  exposed when its region deviates cold-and-still harder than the national mean (the L2 regional
  field guarantees such deviations exist; the aggregation invariant guarantees they don't wash out).
  Residual regional basis shows up as a P&L miss the national hedge didn't cover.
- **Protect regionally** (proxy-hedge, over-hedge, bespoke shaped cover) → eat basis risk (the proxy
  isn't your region), illiquidity, and premium cost.

Where the company sits on that frontier is **visible strategy**, surfaced through the coupled-gap
reporting (COUPLED_TRIAD §5, digest + Proof door). Naive-national → widening C13 gap + P&L basis
leak in cold-still weeks; over-protection → cost drag. Neither extreme is free.

## 5. Honest limits carried forward (from DISCOVER §4 — not asserted as designed)

- **Statistical power:** real weather CSVs exist for only **4** locations (C1–C4) across the current
  ~31-account cast — a company-side regression on this cast is thin (reconfirmed, not approximated).
- **No region partition yet:** the regional degree-day input depends on `W1_4_regional_weather_field`
  landing (the region set — GSP groups vs DNO regions vs the 4 locations — is a BUILD decision).
- **CWV/seasonal-normal exact parameters** are named real methods, NOT sourced numbers — BUILD must
  confirm current published figures against Historical Ground Truth, never invent them.

## 6. Open questions for BUILD (from DISCOVER §5 — genuine judgement calls, not answered here)

1. No-skill baseline `g0`: flat national degree-day factor **or** Ofgem TDCV bands
   (`domain_invariants.py`)? They fail differently — name the choice explicitly at BUILD.
2. Electric-heating base temperature: no settled UK constant (gas fixes 15.5°C); fit from real
   Elexon electricity-demand-vs-temperature data rather than reuse the gas figure by default.
3. CWV wind-chill term in the first cut, or deferred as a named simplification (temperature-only
   HDD first)? Decide explicitly — temperature-only will under-explain vs the wind-coupled L3 physics.
4. Refit cadence/window given book-composition drift — the exact real-world failure mode; a genuine
   BUILD-time judgement call, not designed here.

---

## 7. The single BUILD-unblock gate (the epoch-sequencing intelligence — HELD at L0)

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `C13_weather_normalisation` | 3 | **0 (→3)** | (1) `W1_5_premise_demand_shape` reaches an L-usable premise-demand truth to measure against (itself gated on `W1_4` regional field, `W1_3` national signal); (2) `A6_coupled_triad_gap_metric` available (the gap machinery); (3) **Epoch-3 BUILD-open** (TWIN, within the open epoch); then BUILD adds the typed weather-observable seam method, fits the company regression, and registers `W1_5↔C13` in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING`. **COUPLED:** neither `W1_5` nor `C13` reaches L3 alone — `W1_5` cannot reach L3 until C13 has run against it and the gap is measured (symmetric, COUPLED_TRIAD binding rule). | DIAL (depends_on + epoch sequencing) |

**Pre-BUILD action items (named, not done here — out of this Lane-3 doc-only scope):**
- Add the typed weather-observable crossing to `company/interfaces/sim_interface.py` (the seam gap
  above) — a BUILD-time addition, correctly not built now.
- Extend `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` with `W1_5→C13` (currently absent —
  the map's own note flags this; editing that file is BUILD, out of scope for this fork).

**Disposition:** level **HELD at 0** (proposal atom; FRAME complete ≠ built; BUILD-gated,
EPOCH_GATING Rule 1). This FRAME is C13's canonical terminus; the next idle draw reads C13 as
frame-saturated and yields to genuinely-un-FRAMEd work instead. No BUILD code, no map edit (F1).

---

*Sources consolidated (not re-derived): `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6
(wall, gap, hedging frontier), `docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md` (repo audit,
method grounding, seam gap, open questions), `docs/design/COUPLED_TRIAD_DESIGN.md` §1 (gap-formula
family). Domain methods named as real, checkable UK-energy practice; exact current-edition
figures/coefficients flagged uncertain and left for BUILD to confirm against a real published source
(Historical Ground Truth).*
