# C4_adoption_physics — FRAME (canonical per-atom, doc-only)

**Atom:** `C4_adoption_physics` · lane `C_customer_ops` · epoch **4**
· `level_current: 0` → `level_target: 2` · `loop_stage: idle` · dial 1
· `depends_on: [C3_satisfaction_heterogeneity, W2_2_population_draw, W1_reveal_over_time]`.
**Epoch-4-gated:** registered "do not start" per `docs/staging/done/ADOPTION_JOURNEY_REGISTER.md`
— DISCOVER/FRAME thought is available now (EPOCH_GATING_AND_ATOM_AUTHORSHIP); BUILD is not.

**Turn:** H17 Lane-3 FRAME, doc-only / no BUILD code (EPOCH_GATING Rule 1) / no map edit
(F1, level reported via `docs/design/atom_status/C4_adoption_physics.yaml`).

---

## Why this doc exists (and why it is NOT churn)

C4 had only a **DISCOVER-stage** research doc, `docs/market_research/adoption_physics_c4.md`
(real anchors for the *incidence* and *shape* of ToU/DER adoption — low overall incidence,
2.8–9%; a decisively segment-varying shape, Nesta's tech-affluent cohort at 30–40%; real
friction sources), plus the register itself
(`docs/staging/done/ADOPTION_JOURNEY_REGISTER.md`), which fixes SCOPE and placement but is
explicitly "registration only... do not design." Neither is a canonical FRAME terminus with
a single stated BUILD-unblock gate — so the idle-FRAME draw correctly kept re-offering C4 as
genuinely un-FRAMEd. This doc is that missing terminus. It **consolidates** the DISCOVER
findings, the register's scope, and `docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md`'s
already-anchored behavioural-economics ranges into C4's own four-parameter design and one
gate; it does not re-derive or re-run either source's research.

**Honest finding worth stating plainly, not buried:** all three `depends_on` atoms are
*already* at or beyond the level this atom needs from them
(`C3_satisfaction_heterogeneity` 3/3, `W2_2_population_draw` 2/2 at its own target,
`W1_reveal_over_time` 3/3 — verified live against `docs/design/maturity_map.yaml`, not
assumed from the register's 2026-07-11 snapshot, which pre-dates `W2_2` and `W1_reveal`
reaching their current levels). The *only* remaining block on C4's BUILD is the **epoch
gate itself** — Epoch-4 is not yet open — not any unmet prerequisite. That is the honest
epoch-sequencing intelligence this FRAME exists to state once, per §7.

---

## 1. The four latent per-customer parameters

Each is a **hidden, per-customer, SIM-side trait** — never company-observable directly
(§2). Definitions below name what each modulates, its plausible anchor, and its distinct
role in the adoption decision (the register's own list, made precise; DISCOVER's honest
open item is that *no numeric parameter values* were found — these are shapes and anchors,
not settled numbers, per R10).

| Parameter | What it modulates | Anchor (cited, not re-derived) |
|---|---|---|
| **Bother-threshold** `τ_i` | The minimum *perceived* £ (or equivalent time/effort) benefit below which customer `i` will not act on an available ToU/DER offer, even when objectively positive-EV. Distribution is the load-bearing object — for most of the population the real £ at stake sits *below* it (register, verbatim: "must be honestly true... not tuned away"). | Overall UK ToU incidence 2.8–9% vs Nesta's tech-affluent cohort at 30–40% (`adoption_physics_c4.md`) is the DECISIVE shape anchor: a segment-varying threshold distribution, not a flat population rate. Loss-aversion/framing literature (10–35% acceptance uplift from framing, `NUDGE_PHYSICS_BENCHMARKS.md`) modulates *perceived* benefit crossing `τ_i`, not `τ_i` itself. |
| **Friction sensitivity** `φ_i` | Customer `i`'s cost-of-ACTING — cognitive/comparison effort (tariff-structure matching, not just headline-rate comparison) and onboarding lead time (smart-meter install, 4–8 weeks current). Distinct from `τ_i` (value-of-outcome) and from **structural eligibility** (see below, a precondition gate, not a trait). | `NUDGE_PHYSICS_BENCHMARKS.md`'s "friction costs / switching effort" row: 5–10%/step completion decay, a 0.3–0.4× crisis-year macro multiplier (2021–2023) — real, energy-market-adjacent, not a lab import. |
| **Trust/reassurance** `ρ_i` | Customer `i`'s requirement for reassurance signals (data-privacy comfort with smart-meter/DER telemetry, switching-safety confidence) before acting even when `τ_i` is cleared and `φ_i` is low. Partly explains defaults/status-quo inertia as trust-driven, not merely lazy. | Defaults/status-quo bias, 15–35% relative reduction in switch probability (Madrian & Shea 2001; CMA 2016) — `NUDGE_PHYSICS_BENCHMARKS.md`. |
| **Reward responsiveness** `ω_i` | Customer `i`'s sensitivity to the register's own "incentives and loyalty" mechanics (points, discounted-window structures, commitment devices) — this is what "carries the persuasion load" (register, verbatim) precisely where `τ_i` is uncleared by the objective £ alone. | Commitment-device literature, 20–40% relative reduction in missed-payment when opted in (Ashraf/Karlan/Yin 2006; Thaler/Benartzi 2004) — imported by analogy (payment-plan commitment → adoption commitment), flagged L (magnitude) per the benchmarks doc's own confidence tagging. |

**Structural eligibility is a fifth, separate, non-psychological gate** (DISCOVER's own
"structural flexibility precondition"): a customer can be maximally willing (`τ_i` cleared,
`φ_i` low, `ρ_i` satisfied) and still gain nothing without genuine load-shifting ability
(appliance timing, EV charging, storage). This is a **premise/asset eligibility flag**
(shares its shape with `W1_10_ev_heatpump_geography`'s premise asset assignment, a
*different* atom — EV/HP ownership geography, not customer psychology), not a fifth
psychological trait; C4 consumes it as an input, does not own it.

**Composite decision (shape, not a settled formula — BUILD's job, named here so BUILD is a
translation exercise):** customer `i` adopts offer `k` at a moment `t` when eligible AND
`value_i(k, t) · [1 + uplift(ρ_i, ω_i)] > τ_i(t) · friction_penalty(φ_i)` — i.e. threshold
and friction are cost-side, trust and reward are perceived-value-side multipliers, matching
the register's own separation of "rational £-response" from "engagement/loyalty carries the
load."

---

## 2. The epistemic wall

| Company CAN observe (through the wall) | Company CANNOT observe (SIM-internal) |
|---|---|
| Which customers took which offer, and when (`saas`/observable offer-response events) | Any individual customer's `τ_i`, `φ_i`, `ρ_i`, `ω_i` (L3 ground truth, this atom) |
| Its own bill-visible incentive/loyalty artefacts and their uptake (register: "statement lines, reward balances... NOT marketing copy") | The counterfactual — whether a non-adopting customer was *close* to `τ_i` or nowhere near it |
| Aggregate/segment adoption RATES within its own book, over time | The true segment-varying shape (Nesta-style tech-affluent skew) as ground truth — only its own book's *realised* outcomes |

**Therefore the gap:** the company can only ever fit an **aggregate or segment-level belief**
about adoption propensity from realised offer-response outcomes — never read the four
per-customer parameters. Per `COUPLED_TRIAD_DESIGN.md` §1, the coupled pair is C4 (hidden
truth `θ`, the four latent traits + eligibility) against its company-response leg,
`C5_key_moment_conversion` (belief `b`, the company's detected-moment + fitted-propensity
model) — both carry the `C` lane prefix here (customer psychology and the company's
response to it sit in the same lane, unlike the `W2_x`↔`C_x` pairs in
`background/coupled_triad.py::_AUTHORITATIVE_COUPLING`, which cross lanes; that table has
no C4→C5 entry today — a genuine BUILD-time registration gap, named not fixed here, same
class as C13's `W1_5→C13` gap). `gap→0` (perfect recovery) would mean the company inferred
individual latent traits from aggregate behaviour — structurally unreachable and a wall
DEFECT if seen, not a triumph, identical reading convention to every other coupled pair.

---

## 3. RNG substream discipline (C-S2)

Each of the four latent parameters is drawn from its **own named, seeded substream** —
never a shared "adoption" RNG — so that adding, re-anchoring, or re-shaping any *one*
parameter's distribution can never shift another's draws or any unrelated subsystem's
draws. This is the direct precedent of the real **01:09Z incident** (CLAUDE.md, "Key
learnings"; `docs/design/W1_10_FRAME.md` §7, `docs/design/NATIONAL_WEATHER_SIGNAL_FRAME.md`
§7, `background/gap_metric.py::_substream_seed`): adding illness/divorce draws to a
*shared* life-event RNG silently shifted every downstream draw population-wide — a class
bug, not an instance, per R10.

Proposed substream names (BUILD's to confirm, not to invent differently without reason):
`adoption_bother_threshold`, `adoption_friction_sensitivity`, `adoption_trust_reassurance`,
`adoption_reward_responsiveness` — deliberately namespaced away from `W1_10`'s existing
`adoption_field` substream (EV/heat-pump ownership *geography*, a different atom and a
different kind of "adoption" — structural asset uptake, not psychological offer-response —
collision avoided by naming, not by coincidence).

---

## 4. Composition with C5_key_moment_conversion

The register's own framing: "adoption is state- and event-dependent" (EV purchase, house
move, boiler failure, smart-meter install, bill shock, renewal). C5 owns DETECTING these
moments through the wall (an inference problem in its own right — a real supplier does not
see "customer just had a boiler failure" as a labelled fact, only downstream signals). C4
owns what happens **once a moment is detected and a window opens**: a key moment does not
change `τ_i`, `φ_i`, `ρ_i`, `ω_i` themselves (they are stable per-customer traits) — it
**transiently modulates the composite decision**, most naturally as a temporary reduction
applied to the effective threshold comparison (`τ_i(t)` in §1's composite is time-indexed
for exactly this reason: a bill-shock week or a smart-meter-install week is a real, bounded
window where the same objective £ value is more likely to clear the same stable `τ_i`).
BUILD decides the exact functional form (multiplicative window discount vs. an additive
temporary threshold reduction) — named as an open BUILD judgement call, not designed here.

---

## 5. What L1/L2 mean for C4 in `C_customer_ops` terms

- **L0 (current, confirmed 0):** none of the four latent parameters exist; no per-customer
  adoption trait distributions are drawn; any adoption-adjacent behaviour in the SIM today
  (if present at all) is not physically grounded in this atom's traits.
- **L1:** the four latent parameters exist as real per-customer SIM ground truth, each from
  its own named RNG substream (§3), anchored to the real shapes in §1 (segment-varying, not
  flat) — but not yet wired into a live adoption-decision function or exposed to any
  observable offer-response event.
- **L2 (target):** the composite decision (§1) is live and produces real observable
  offer-response outcomes crossing the wall through existing interfaces (which offer, which
  customer, when); composes with C5's key-moment windows (§4); the coupled-gap machinery
  (§2) can measure company belief against hidden truth once C5 itself is also built (C5
  remains its own, separately epoch-gated, atom — C4 reaching L2 does not require C5 to be
  built, only compatible with it per §4's interface).
- **L3+ (not this atom's target):** not specified — `level_target: 2` is the map's own
  ceiling for C4; a company-side fitted-propensity model closing the gap belongs to C5's
  own level definitions, not re-specified here.

---

## 6. Known simplifications (R10)

- **No numeric parameter values, only shapes/anchors** (DISCOVER's own honest open item,
  carried forward unresolved): converting the segment-varying shape into concrete
  per-segment `τ_i`/`φ_i`/`ρ_i`/`ω_i` distributions is real, unstarted BUILD-time work.
- **Cross-domain import risk:** three of four anchors (`NUDGE_PHYSICS_BENCHMARKS.md`'s own
  cross-cutting note) are imported from non-energy domains (retirement savings, tax debt,
  retail pricing) — directionally credible, magnitude not UK-energy-verified. Only the
  overall-incidence/Nesta-segment anchor is energy-sector-specific.
- **Composite decision formula (§1) is a shape, not a settled equation** — BUILD must
  decide the exact functional form and confirm it degrades sensibly at the boundaries
  (`τ_i→0`, `φ_i→0`) rather than producing an unrealistic always-adopt/never-adopt edge.
- **Consumer Duty two-sidedness** (register, verbatim): gamified incentives and key-moment
  pressure have real mis-selling/vulnerability edges — `ω_i` and C5's window-detection must
  both be visible to the compliance organs at BUILD time, not modelled as pure upside.

---

## 7. The single BUILD-unblock gate

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `C4_adoption_physics` | 4 | **0 (→2)** | **Epoch-4 BUILD-open** (TWIN, standing approver for BUILD-within-the-open-epoch per EPOCH_GATING_AND_ATOM_AUTHORSHIP §3a) — the sole remaining condition. All three `depends_on` atoms are already at/beyond their own required levels (§ "Why this doc exists," verified live): `C3_satisfaction_heterogeneity` 3/3, `W2_2_population_draw` 2/2, `W1_reveal_over_time` 3/3. Once Epoch-4 opens, BUILD (a) wires the four named RNG substreams (§3), (b) implements the composite decision (§1) with structural-eligibility as an input gate, (c) exposes offer-response outcomes through the existing observable-interface pattern, (d) registers the `C4→C5` coupling in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (§2's named gap). | DIAL (epoch sequencing only — no unmet dependency) |

**Disposition:** level **HELD at 0** (idle atom; FRAME complete ≠ built; epoch-gated per
`ADOPTION_JOURNEY_REGISTER.md`, EPOCH_GATING Rule 1). This FRAME is C4's canonical
terminus; the next idle draw reads C4 as frame-saturated and yields to genuinely-un-FRAMEd
work instead. No BUILD code, no map edit (F1).

---

*Sources consolidated (not re-derived): `docs/market_research/adoption_physics_c4.md`
(incidence/shape anchors, friction sources, honest open items),
`docs/staging/done/ADOPTION_JOURNEY_REGISTER.md` (scope, non-negotiables, epoch
placement), `docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md` (behavioural-economics
magnitude anchors for friction/trust/reward), `docs/design/COUPLED_TRIAD_DESIGN.md` §1
(gap-formula family), `docs/design/W1_10_FRAME.md` §7 / `docs/design/
NATIONAL_WEATHER_SIGNAL_FRAME.md` §7 (RNG substream discipline precedent, 01:09Z). Domain
behavioural-economics figures are real, checkable published studies (per the benchmarks
doc's own confidence tagging); exact per-parameter numeric values remain uncited and are
flagged for BUILD to confirm, never invented (R10).*
