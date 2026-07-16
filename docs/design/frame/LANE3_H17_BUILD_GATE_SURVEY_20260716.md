# Lane-3 BUILD-gate survey — H17 re-draw of 6 idle atoms (2026-07-16)

**Turn:** H17 Lane-3 DISCOVER/FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1).
**Scope drawn:** `H18_harness_self_mutation_audit`, `W1_2_generate_futures`,
`B4_competitor_field`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`,
`W1_4_regional_weather_field`.

## Why this doc exists (and why it is NOT six new FRAME docs)

All six drawn atoms **already carry a complete, substantive FRAME doc** under
`docs/design/frame/` (five authored in the 2026-07-16 08:23 batch, H18 at 16:37). Each
existing FRAME already reaches its own honest terminus and records **level HELD** with a
named BUILD-gate. Re-emitting a near-identical FRAME for a FRAME-saturated atom would be
churn — precisely the make-work that SELF_INTERRUPT_DISCIPLINE and R12 (anti-goal-seek)
forbid. The draw text is a doorbell (R7): verified against real disk state, the premise
"these atoms need a fresh FRAME" is stale.

So the genuine, bankable Lane-3 increment this re-draw produces is **epoch-sequencing
intelligence**: for each atom, the single precise gate that unblocks BUILD, in one place,
so the next epoch-open / BUILD-open decision (DIRECTOR_TWIN or director) can act from a map
rather than re-reading six docs. Every level is **HELD** — no FRAME turn can honestly move
these, because their targets (→L1/L2/L3) all require BUILT, green code that is BUILD-gated.

## The gate table

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `W4_2_verifier_timing_extension` | 1 | 1 (→3) | Director re-opens `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` (closed B/C) — a **Tier-1 safety-control** decision to build real data-flow/timing detection into a named wall control | **WALL** (director-reserved, safety control) |
| `H18_harness_self_mutation_audit` | 2 | 0 (→2) | Epoch-2 BUILD-open (TWIN, within open epoch) + actually build green meta-control mutation tests for M1–M5 | DIAL (epoch sequencing) |
| `W1_2_generate_futures` | 3 | 1 (→2) | (a) `W1_reveal_over_time` resolved (blindfold enforcer for a pre-generated path); (b) a **director-authored** named baseline-continuation scenario (curriculum, R13, category-6-adjacent); (c) Epoch-3 BUILD-open | DIAL + **curriculum WALL** (scenario authorship) |
| `W1_3_national_weather_signal` | 3 | 1 (→3) | Epoch-3 BUILD-open; build the latent blocking-high persistence regime + gap-measured vs company; declare C-S5 timescale | DIAL (epoch sequencing) |
| `W1_4_regional_weather_field` | 3 | 1 (→3) | `W1_3` at L-usable first (depends on national L1); then build the aggregation-consistency invariant (mutation-tested) + gap | DIAL (depends_on + epoch) |
| `B4_competitor_field` | 4 | 0 (→1) | `W2_3_competitor_field` (WORLD) must emit an observable competitor field first; then wire belief + one live coupling across the typed wall | DIAL (COUPLED_TRIAD depends_on) |

## Per-atom notes (the non-obvious bits worth carrying forward)

- **W4_2 — the only WALL in this set.** Its L3 target is *not* an authorization: the timing-
  detection build was closed B/C as a Tier-1 safety-control gate. The honest disposition
  (per its FRAME §6) is HOLD at L1 — the wall-timing burden stays on the PreToolUse hook +
  as-of snapshot + human review. Re-opening is director-console-only; nothing in this re-draw
  is new information that would prompt an escalation, so none is raised. Approach C (as-of
  snapshot structural fix) may retire the "extend the verifier" framing entirely if ever opened.

- **W1_2 / W1_3 / W1_4 — built code exists but level is correctly low.** `sim/scenario/bimodal_generator.py`
  (W1_2) and `sim/weather_engine.py` Pass 1/Pass 2 (W1_3/W1_4) are real, tested mechanism code.
  The low levels are NOT mis-registration: the atoms' levels track the *coupled-triad* state
  (company faced the world + gap measured + curriculum-authored scenario), not raw mechanism
  existence. W1_2 in particular is curriculum-gated — the engine exists; *which* futures the
  company lives through is the director's, never agent-chosen (R13).

- **B4 — two orphaned pre-built modules.** `company/market/tariff_benchmarking.py` and
  `company/pricing/renewal_pricing_engine.py` are real and Ofgem/CMA-anchored but have **zero
  non-test callers**. L1 is "belief + one live coupling" — wiring one of these across the typed
  wall once `W2_3` emits an observable field. The wiring, not the modules, is the missing L1 work.

- **H18 — self-referential doctrine.** When built it must satisfy its own R15 doctrine: each
  meta-control organ (M1 deadman, M2 naive/LLM-judge outcome-miss, M3 claim hook, M4/M5) gets a
  *both-directions* (fire AND quiet) mutation assertion, and the class fails automatically if a
  future meta-control ships without one (R10 closure, not instance closure).

## Meta-finding (QUEUE, not fix-on-sight — SELF_INTERRUPT_DISCIPLINE)

The idle-DISCOVER/FRAME self-refill (`supervisor.py::_idle_discover_frame_draw`) re-drew six
atoms whose FRAME stage is **saturated**, with no remaining FRAME-stage work — a **DIAL defect**
(Rule 0: empty feasible work within a stage), not a WALL. Candidate remedy to register as a
harness atom (do not build here): track a per-atom `frame_saturated` / last-stage-output marker
so a saturated atom is not re-drawn for the *same* stage until its BUILD-gate opens, and instead
the draw yields to genuinely un-FRAMEd idle atoms. This keeps the treadmill honest rather than
generating duplicate-FRAME churn. Filed as intelligence for the next harness pass.

---

## Addendum — H17 re-draw (2026-07-16, later) — B5 folded into the gate table

The idle-DISCOVER/FRAME self-refill re-drew a **near-identical** set: `W1_2_generate_futures`,
`B4_competitor_field`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`,
`W1_4_regional_weather_field` — **plus `B5_regional_basis_risk`** (which this survey's original
table did not carry) and **minus `H18_harness_self_mutation_audit`**. Verified against real disk
state: the five shared atoms are unchanged since the survey above (same commit-day, nothing built,
gates identical) — re-emitting their FRAMEs would be the exact duplicate-FRAME churn the meta-finding
warns against, so no new per-atom FRAME is written. `B5` already carries a complete 19KB FRAME
(`docs/design/frame/B5_regional_basis_risk_FRAME.md`, committed `5de4b2a91`); the only genuine,
non-churn Lane-3 increment this re-draw yields is folding B5's single BUILD-unblock gate into the
consolidated table so the epoch-sequencing intelligence covers every currently-drawn atom.

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `B5_regional_basis_risk` | 3 | 0 (→3) | `W1_8_zonal_locational_pricing` opens BUILD first (itself gated on `W1_6_physics_price_signal` **and** a **director-authored named zonal curriculum scenario**, R13); B5 releases **coupled with W1_8** (COUPLED_TRIAD: neither reaches L3 alone); at BUILD, register `W1_8↔B5` in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` | DIAL (depends_on) + **curriculum WALL** (zonal-regime scenario authorship, director-reserved) |

- **B5 — the company leg of the W1_8 coupled pair.** It authors the company-side twin (provenance
  `proposal`, L0→L3) that gives the W1_8 belief-vs-truth *regional-basis* gap a home: the company
  observes settled/published zonal prices through the wall, holds only a **national** hedge (from B3),
  and **cannot buy** a regional-basis hedge (no regional forward market — the real structural fact),
  so a regionally-skewed book carries unhedgeable basis it may wrongly assume its national hedge covers.
  Gap = believed (national-hedge) protection vs SIM-truth realised zonal basis cost `Σ_z vol_z·basis_z`.
  **Dormant/zero under the national baseline** — the exposure only exists inside a director-authored
  zonal-curriculum scenario, and per R13 that scenario's severity is **never** tuned to company basis
  loss. Held at **L0** (proposal-atom FRAME ≠ built; BUILD-gated, EPOCH_GATING Rule 1).

*This addendum is the only change: five shared atoms re-confirmed HELD with no new FRAME (anti-churn),
B5 added to the gate table. No BUILD code, no map edit (F1). Meta-finding above now has a second data
point — a saturated-atom re-draw recurred within the same day, reinforcing the `frame_saturated`-marker
remedy as worth registering as a harness atom.*

---
*No BUILD code, no map edit (F1 — levels reported via `docs/design/atom_status/*.yaml` inbox).
Every level HELD; see the gate table for what each atom's real progress depends on.*
