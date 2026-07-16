# FRAME — W1_6_physics_price_signal: concrete price-as-derived-output recommendation

**Atom:** `W1_6_physics_price_signal` — "L4 price as a DERIVED output: national
weather → national demand + renewable output → residual demand → merit order →
wholesale price (price is NEVER an independent draw)." `level_current: 0`,
`level_target: 3`, epoch 3 (**BUILD-gated** per EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1). `depends_on: [W1_3_national_weather_signal, W1_5_premise_demand_shape]`.

**This FRAME is doc-only.** It writes no `sim/`/`company/` code, changes no
`level_current`, and edits no `maturity_map.yaml` line (the level is recorded
via an `atom_status/` inbox, held at 0 — a FRAME cannot earn L1, which the map
rubric reserves for "been BUILT in any form"). Scope is `docs/design/` only.

Its job is the one thing the DISCOVER pass
(`docs/design/W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md`) explicitly deferred: it
names its §3 open questions "honest, not decided here." A FRAME **decides**
them, with rationale, so BUILD inherits a spec rather than a question list.
Every decision below cites the DISCOVER or the code it rests on; nothing here is
new empirical claim (no network this session — figures the DISCOVER flagged
`[UNVERIFIED]` stay flagged).

---

## 1. The problem, restated in one paragraph

Today wholesale price enters the sim as an *input* the company can effectively
treat as exogenous-and-given. W1_6's target state (L4) is that price is a
**derived output** of the weather→demand→residual-demand→merit-order chain, so a
cold-and-still spell *mechanistically* produces a price spike rather than one
being drawn independently. The chain's physics engine already exists
(`sim/price_engine.py`, Phase 3b, 15 tests) — but the DISCOVER's load-bearing
finding is that it **already failed its own calibration gate** (~10× SSP
overestimate at every gamma in the spec'd `[1.5, 2.5]` range) and was formally
superseded on 2026-06-11. So W1_6 is **not** a green-field build and **not** a
re-wire of a working engine; it is a *recalibration-and-recompose* atom on top of
a known-broken proxy, and the first honest BUILD step is a calibration run, not
code.

## 2. What already exists — audit inherited from the DISCOVER (no re-derivation)

| Component | File | Status the FRAME builds on |
|---|---|---|
| Merit-order physics (gas floor, margin term, wind power curve, chain) | `sim/price_engine.py` | Real code, 15 tests; **superseded** — raw-ratio margin term fails calibration ~10× |
| Fitted-distribution price generator | `sim/bimodal_generator.py` | Calibration-fitted (incl. negative-price days); currently the live price mechanism |
| Lookback price-sensitivity heuristic | `saas/.../weather_price_sensitivity.py` | Separate mechanism; exact thresholds not re-quoted by DISCOVER |
| National weather signal | W1_3 (`sim/weather_engine.py`) | `depends_on` — must be jointly cold∧still, not wind-residual-only, before W1_6 can show the spike |

The three coexisting price mechanisms (physics / fitted / heuristic) are the
DISCOVER's open question 3, decided in §3.4 below.

## 3. The six deferred decisions — resolved

### 3.1 Ratio form (DISCOVER Q1) — DECIDED: residual-demand / dispatchable-margin, calibration-gated, not gamma-retuned

The Phase-3b failure traces to the margin term being `(demand / renewable)^gamma`
on **raw** national MW — a ratio of 3–5 raised to gamma≥1.5 multiplies the gas
floor ~6×, overshooting real SSP by ~10×. The corrected structure is the one the
chain already specifies but never calibrated: residual demand
`RD = D − G_wind − G_solar` over the **dispatchable headroom**, not over raw
renewables. Concretely the margin term becomes a function of stack tightness
`RD / dispatchable_capacity ∈ [0, 1]`, so it approaches the gas floor when the
thermal fleet is lightly loaded and rises steeply only near full dispatch —
matching real merit-order convexity.

**Binding constraint (R12, anti-goal-seek):** BUILD re-runs
`simulation/run_phase3b_calibration.py` (or a successor) against real SSP with
the *new* ratio form **before** the chain is trusted. If it still fails, **that
is the finding** — gamma is NOT retuned toward the benchmark, and negative
calibration is reported, not hidden. Price is a diagnostic; calibration MAE is a
sanity flag, never a target (R12, R13-baseline half).

### 3.2 Carbon-cost term (DISCOVER Q2) — DECIDED: add at BUILD, calibration-checked, real source or named simplification

Real CCGT SRMC is `gas/η + carbon_price × emissions_factor / η`; the engine
models only the first term. The omission is real and *undetected* (unlike the
deliberately-scoped-out interconnector/CM/CfD items). **Decision:** add the
carbon term at BUILD because it is structurally simple and structurally correct —
BUT its numeric inputs (UK ETS allowance price, emissions factor) must come from a
**real published source** (ICE/UK-ETS auction results or DESNZ carbon-price
statistics), never fabricated. If BUILD cannot obtain a real time series, the
carbon term is registered as a **named C-S5/R10 simplification** ("carbon cost
omitted, no calibrated source") rather than filled with an invented number.

Note (from DISCOVER §2): carbon pushes the floor *up*, and the calibration error
is *over*estimate — so carbon is not the fix for §3.1; the ratio term is. Adding
carbon and fixing the ratio are independent changes and must be calibrated as
such (add carbon *after* the ratio fix passes, so its marginal effect is
measurable, not confounded).

### 3.3 Negative pricing & discrete steps (DISCOVER Q4) — DECIDED: out of scope for L3, named simplification, not faked

The ratio form is strictly positive and smooth; real SSP has negative periods
(must-run low-carbon > demand) and discrete plant-level jumps. **Decision:** W1_6
at L3 does **not** grow a negative-price branch or a discrete stack — that would
be re-implementing `bimodal_generator.py`'s fitted negative-price component *by
mechanism*, a much larger atom. Instead: register "no negative price, smooth not
stepped" as an explicit named simplification (C-S5 time/structure declaration),
and let the calibration bar (§3.1) report the MAE cost of that simplification
against real SSP (which does include negative/spiky periods) rather than
suppressing those periods from the comparison. Honest gap, measured, not hidden.

### 3.4 Three-mechanism reconciliation (DISCOVER Q3) — DECIDED: baseline/curriculum split (R13), not redundancy to delete

`price_engine.py` (physics), `bimodal_generator.py` (fitted), and
`weather_price_sensitivity.py` (heuristic) coexisting is not obviously coherent —
but it is **not** three-way redundancy to collapse. **Decision (R13 wall):**
- `price_engine.py` (recalibrated per §3.1) is the **BASELINE** derived-price
  mechanism — the physics chain W1_6 owns, changed only for fidelity reasons,
  blind to company P&L.
- `bimodal_generator.py` stays a **CURRICULUM** generator — a director-authored,
  named, versioned way to inject stress regimes (negative-price days, crisis
  bimodality) that the physics baseline deliberately does not model. It is NOT
  retired by W1_6; retiring/merging it is a **director curriculum decision**
  (one-way-door cat. 6), not the agent's.
- `weather_price_sensitivity.py` is a company-side/heuristic layer and is on the
  far side of the wall from the SIM price physics — BUILD reads it in full
  (DISCOVER Q6) to confirm it consumes published price rather than duplicating
  the SIM's price formation; if it duplicates, that is a separate finding.

This split is itself the R13 artefact: baseline changes for fidelity, curriculum
changes by director fiat, and W1_6 only ever touches the baseline.

### 3.5 W1_3 joint-regime dependency (DISCOVER Q5) — DECIDED: hard blocker, already in `depends_on`, not re-litigated

W1_6 cannot *mechanistically* demonstrate the cold-and-still spike until W1_3's
regime trigger is jointly cold∧wind, not wind-residual-only. This is correctly
captured in `depends_on: [W1_3_national_weather_signal]`. **Decision:** W1_6's L3
DoD (§5) is written so its spike-demonstration test *consumes* W1_3's joint
regime — W1_6 does not build a private weather shortcut to fake the spell. If
W1_3 is not yet joint at BUILD time, W1_6's spike test is `xfail(strict)` against
that named dependency, not silently skipped.

### 3.6 `weather_price_sensitivity.py` exact values (DISCOVER Q6) — DECIDED: BUILD reads in full first

Deferred purely because the DISCOVER read the file only in part. **Decision:**
BUILD's first read-only step (before any edit) is a full read of that file to
decide absorb-vs-leave-separate per §3.4; no design choice is pre-committed here
beyond "it is company/heuristic-side, presumed a consumer of price, not a second
price former."

## 4. The SIM/company wall (load-bearing, not optional)

Price formation is **SIM-side physics**. The company layer must NOT read the
merit-order stack, the residual-demand calc, gamma, gas floor, or any internal —
it observes only the **published SSP** (a market-data observable) exactly as a
real supplier reads Elexon SSP. W1_6's chain lives entirely behind
`company/interfaces/sim_interface.py`; its outputs cross the wall only as the
already-published price series. A BUILD that lets any company/saas module import
the price engine or its intermediates is an epistemic violation and fails the
verifier. This preserves the point of the atom: the company copes with observed
price, it does not see how the world made it.

## 5. Level decomposition (L0 → L3) and file_scope

- **L0 (now):** DISCOVER + this FRAME. No code. ✅ (this doc)
- **L1 (skeletal):** recalibration harness — the §3.1 residual-demand /
  dispatchable-margin form wired into `simulation/run_phase3b_calibration.py`
  (or successor), run against real 2019 (calm) + 2022 (crisis) SSP, MAE reported.
  No claim the chain "works" — L1 is "built in some form + calibration number
  exists," pass or fail.
- **L2 (working):** the recalibrated engine is the derived-price path for a real
  sim run (behind the wall), carbon term added-or-named-simplified (§3.2),
  negative-price gap named (§3.3), R13 split documented (§3.4).
- **L3 (demonstrated + gap-measured, COUPLED_TRIAD):** the cold∧still spell (via
  W1_3's joint regime, §3.5) mechanistically produces a price spike; and the
  **belief-vs-truth gap** is measured — the company's price expectation vs the
  SIM's derived price under that regime, reported per the coupled-triad rule. No
  world atom reaches L3 until the company has been tested against it.

**file_scope for BUILD (proposed, disjoint):** `sim/price_engine.py`,
`simulation/run_phase3b_calibration.py`, `docs/calibration/price-engine.md`,
`tests/sim/test_price_engine.py`. Explicitly NOT `sim/bimodal_generator.py`
(curriculum, director-owned) and NOT any `company/`/`saas/` file (wall).

## 6. Invariants to make mutation-tested at BUILD (R15)

Each must be shown to FAIL on its own named defect, not just pass:
1. **Price is derived, never drawn** — a test that mutates the weather input and
   asserts the price *moves as a consequence*; if price is independent of weather,
   the test fails. (Kills a regression to independent-draw price.)
2. **Residual-demand identity** — `RD == D − G_wind − G_solar` exactly; mutate a
   sign and it fails. (Kills the raw-ratio regression that caused the ~10× miss.)
3. **Merit-order monotonicity** — price non-decreasing in residual demand at fixed
   gas floor; mutate to non-monotone and it fails.
4. **Wall invariant** — no `company/`/`saas/` import of the price engine or its
   intermediates (epistemic verifier; already enforced repo-wide).
5. **Calibration gate is a diagnostic, not a target** — the calibration test
   asserts the MAE is *reported*, never asserts MAE < a tuned threshold that would
   invite gamma-fitting (R12). A test that passed by narrowing the comparison
   window is itself the defect.

## 7. Coupled-triad gap metric (the score is the gap)

Per COUPLED_TRIAD_DESIGN: W1_6 (WORLD/SIM depth) is complete only once the
COMPANY has faced it and the HARNESS has measured the belief-vs-truth gap. The
concrete metric: under the cold∧still regime, `gap = company_expected_price −
sim_derived_price` (signed, £/MWh), reported per digest and on the Proof door.
A large gap is not a bug to tune away — it is the finding (the company is *allowed*
to misread the world through the wall); it becomes the score the company's own
forecasting atoms are then measured against.

## 8. What this FRAME is NOT claiming

- NOT that the chain works — it does not; the inherited calibration failure is
  unresolved and BUILD's first step is a calibration run that may fail again.
- NOT a level move — held at L0 (FRAME ≠ built).
- NOT a decision to retire `bimodal_generator.py` — that is a director curriculum
  call (§3.4), one-way door.
- NOT any new numeric claim — every figure the DISCOVER flagged `[UNVERIFIED]`
  (UK ETS price, emissions factor, real SSP means) stays flagged; BUILD sources
  them from real published data or registers a named simplification.
- NOT in scope: interconnectors, Balancing Mechanism, CfD, Capacity Market —
  deliberate simplifications, named per DISCOVER §2.
