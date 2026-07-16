# FRAME — B5_regional_basis_risk — the company carries regional basis it cannot hedge (COUPLED company twin of W1_8)

- **atom (PROPOSED)**: `B5_regional_basis_risk` | lane `B_commercial` | value_stream `wholesale_to_price` | epoch/dial 3
- **provenance**: `proposal` (agent-authored CANDIDATE atom — DISCOVER/FRAME-workable now, **never BUILD until the director/twin opens it**; EPOCH_GATING)
- **level_current**: 0 → **level_target**: 3 | **depends_on**: `W1_8_zonal_locational_pricing`
- **stage**: DISCOVER/FRAME only (BUILD-gated, `loop_stage: idle`) — doc, no code, level unchanged.

This FRAME is doc-only. It writes no `sim/`/`company/` code, changes no `level_current`, and edits no
`maturity_map.yaml` line (F1 — a fork records output via an `atom_status/` inbox and proposes a stanza;
adding the atom to the map is the orchestrator's single-writer edit). Scope is `docs/design/` only.

> **PROPOSED MAP STANZA (for the orchestrator to insert — not written by this fork):** the exact YAML
> is at the foot of this doc (§8) and in the fork's final report. It registers a company-side coupled
> twin at `provenance: proposal`, `level_current: 0`, `level_target: 3`, `loop_stage: idle`, depending
> on `W1_8_zonal_locational_pricing`.

---

## 0. Why this atom exists — the gap the W1_8 FRAME itself names

`docs/design/frame/W1_8_zonal_locational_pricing_FRAME.md` §2 states plainly that W1_8 (the SIM-side
zonal price generator) **cannot reach L3 alone**: per COUPLED_TRIAD's binding rule, *no world/SIM atom
reaches L3 until a company has been tested against it and the gap measured*. The W1_8 FRAME identifies
`B3_hedge_tariff_alignment` as the nearest existing coping posture but records that there is **no
dedicated company-side "regional-basis-risk" atom yet**, so the coupling is "largely UNBUILT" and
"authoring or opening that company atom is a separate, coupled piece of work."

This FRAME **is that separate work**: it authors the coupled company twin as a candidate atom so the
W1_8↔company pair exists on the map and the belief-vs-truth basis gap has a home to be reported against.
It re-derives none of the W1_8 SIM-side mechanics (which are saturated in that 222-line FRAME); it
frames only the **company side** and the **harness gap**.

**Overlap check (why this is a distinct atom, not a duplicate):**
- `B3_hedge_tariff_alignment` (L2, B_commercial) hedges cost to a **single national forward curve** and
  has **no notion of regional basis** — it is the posture this basis risk *attacks*, not a capability
  that carries or measures it. B5 is the missing regional dimension B3 structurally cannot represent.
- `C13_weather_normalisation` (proposal, C_customer_ops, twin of W1_5) **mentions** regional basis in
  passing ("GB has NO regional forward market, so hedge-to-national leaves a regionally-skewed book
  exposed") but its capability is **weather-normalisation of book demand** from confounded meter data —
  a *demand-inference* twin, not a *price-basis / hedge-exposure* capability, and coupled to W1_5 not
  W1_8. B5 is the price-side twin; the two are complementary, not overlapping.
- No `B_commercial` hedging atom covers **regional/zonal basis** specifically (B1 margin bridge, B2 opex
  cost-to-serve, B4 competitor field are unrelated; B3 is national-only). Confirmed by reading the
  stanzas, not assumed.

---

## 1. What this atom is & real-world grounding

A real GB supplier today hedges wholesale cost against a **single national** forward curve — because
that is the only forward market that exists. **There is no regional forward market**: you cannot buy an
instrument that pays out on a Scottish (or any sub-national) energy price specifically. If GB were to
move to **zonal / locational** settlement under REMA (the counterfactual W1_8 generates), a supplier
would then **settle** its regional volumes at **published zonal prices** while its hedge still pays at
the **national** price. A book that is **regionally skewed** — concentrated in a zone whose price
diverges from the national reference — therefore carries **basis risk that is unhedgeable by
construction**: no instrument exists to lay it off.

This is a genuine, real-world coping failure, not a contrived one. The company:
- **can observe** (through the wall) the settled/published zonal prices, its own metered volumes by
  region, and the national forward curve it hedged against;
- **cannot observe** the SIM's true regional basis field, congestion model, or reconciliation weights
  (epistemic wall — those are W1_8 internals);
- **cannot buy** a regional-basis hedge (the real-world structural fact, preserved through the wall).

So the company must form an **approximate, possibly stale or biased belief** about its own regional
basis exposure from observed settled prices, and it is **allowed to be wrong** — mis-estimating its
zonal concentration or the basis distribution, or (worse, and realistically) **assuming its national
hedge protects it when it does not**. That belief-vs-truth divergence is the whole point.

**R13 (baseline/curriculum split) — pinned hard.** Because a zonal regime is a **counterfactual absent
from real GB 2016–2025 history**, the *existence and severity* of the zonal regime this atom is exposed
to is a **director-authored, named, versioned CURRICULUM scenario** (inherited directly from W1_8 §6:
"Scenario: REMA zonal, moderate congestion" vs "severe split"), **never agent-tuned** in response to
the company's realised basis loss. This atom builds the company's *capability to carry and (mis)believe
basis exposure*; it must **never** be used to argue the curriculum should be softened because the
company loses money under it. The baseline world stays national-single-price; under the baseline this
atom's basis is identically zero and the capability sits dormant — correctly.

---

## 2. COUPLED TRIAD — the gap is the score

Per COUPLED_TRIAD every capability is a 3-loop: SIM adds depth → COMPANY discovers & copes through the
wall (allowed to be wrong) → HARNESS measures the belief-vs-truth GAP. **This atom is the COMPANY leg of
the `W1_8_zonal_locational_pricing` triad.**

- **The pairing (name it explicitly):** `W1_8_zonal_locational_pricing` (SIM: generates the true zonal
  price field + true regional basis, aggregation-consistent with the national reference) **↔**
  `B5_regional_basis_risk` (COMPANY: settles regional volumes at published zonal prices, hedged only
  nationally, forms an approximate basis belief, carries the unhedgeable residual) **↔** HARNESS: the
  regional-basis belief-vs-truth gap.
- **SIM adds (W1_8, already framed):** the true zonal marginal price per zone per timestep and the true
  regional basis `basis_z(t) = price_z(t) − price_national(t)` — the thing the company cannot hedge.
- **COMPANY discovers / copes (B5, this atom — allowed to be wrong):**
  1. reads settled/published **zonal** prices for the zones it serves (observable only, via the typed
     wall) and its own **regional volume mix** (its book weight per zone);
  2. holds a hedge struck against the **national** forward curve (from B3) — with **no** regional-basis
     instrument available to buy;
  3. forms a **belief** about its regional-basis exposure (e.g. "my northern concentration + expected
     northern basis ⇒ £X of unhedged cost-at-risk") from observed settled prices — a belief that can be
     **stale, biased, or wrongly assume the national hedge covers it**;
  4. realises a **basis P&L**: cost lands at the zonal price, hedge pays at the national price, residual
     = `Σ_z volume_z · basis_z` — the unhedged regional cost.
  The permitted failure modes: under-estimating zonal concentration, mis-shaping the basis distribution,
  or the headline error — **believing a national hedge is regional protection when it is not**.
- **HARNESS measures (the GAP):** `company's assumed-national-hedge protection / believed basis
  exposure` **vs** `SIM ground-truth realised zonal basis cost`. Two facets, both reported:
  - **belief gap** — distance between the company's inferred/assumed regional basis and W1_8's
    ground-truth basis for the company's own zones;
  - **exposure gap** — the realised unhedged basis P&L the company did **not** believe it was carrying
    (the money the "national hedge protects me" assumption silently left on the table).
  Reported **per coupled pair** each digest and at the **Proof door**, per COUPLED_TRIAD. The harness
  anchors the truth side on W1_8 ground truth and the belief side on the company's own observable-only
  inputs — the two sides must be **independent** (R15: no tautology; the company never reads SIM
  internals to score itself). Normalised to a no-skill baseline per `A6_coupled_triad_gap_metric`
  (natural no-skill baseline: "assume zero basis / national hedge fully protects" — the naive posture
  the capability must beat to earn any level above the baseline).

---

## 3. Level decomposition (target L3) — modest and honest

- **L0 (current):** DISCOVER + this FRAME. No code, no company basis belief. ✅ (this doc)
- **L1 — the company observes settled zonal prices + its regional book weight, and computes a realised
  basis P&L with NO regional hedge available.** The company reads published zonal prices through the
  wall, knows its own volume-per-zone, and reconciles that it is hedged only nationally; it computes the
  realised regional basis residual `Σ_z volume_z · basis_z(t)`. No belief/forecast sophistication yet —
  L1 is just *carrying the exposure honestly and surfacing it as a number*. Under the national-baseline
  curriculum this residual is identically zero (no basis exists), which is the correct dormant behaviour.
- **L2 — the company forms a forward BELIEF about its basis exposure and a (necessarily national-only)
  hedge decision under it.** The company infers an expected regional basis from observed settled zonal
  prices (stale/biased permitted), sizes its cost-at-risk from regional concentration, and makes its
  hedge decision knowing it **cannot** lay the basis off — it can only reshape the *book* (accept, or
  concentrate/diversify regionally) not buy protection. The belief is explicitly separable from truth so
  the gap is measurable.
- **L3 — coupled-triad gap measured (COUPLED_TRIAD).** The belief-vs-truth basis gap (both facets, §2)
  is measured against W1_8's ground-truth zonal field under a **director-authored zonal-severity
  scenario**, with a regionally-skewed book that is hedged only nationally, and reported per zone per
  digest + Proof door. Time-scale invariance of the basis-P&L accumulation stated explicitly (C-S5).
  Per COUPLED_TRIAD, **neither W1_8 nor B5 reaches L3 until this pair has been run and the gap
  measured** — the two atoms release the L3 gate together.

---

## 4. The epistemic wall — load-bearing here

The wall is what makes this atom *hard* and *honest*, so it is stated concretely:

- The company reads **only** the settled/published zonal prices (and its own book), through the typed,
  versioned SIM/company adapter (`company/interfaces/sim_interface.py` style) — exactly as a real
  supplier reads a published locational price.
- The company **never** reads W1_8's zonal-generation internals: the true `basis_z`, the congestion
  model, the reconciliation weights, or the RNG substream state. A BUILD that let any `company/`/`saas/`
  module import the zonal generator or its intermediates would be an **epistemic violation** and fail
  the verifier — it would let the company "hedge" a basis it is physically supposed to be unable to
  hedge, and would let it score its own belief against ground truth (destroying both the atom's point
  *and* the harness's independence, R15 tautology).
- The harness sits **outside** the wall: it may read W1_8 ground truth **and** the company's observable
  belief and compute the gap — the company may not.

---

## 5. Aggregation-consistency link (to W1_8 §4)

W1_8's defining invariant is that the demand-weighted zonal aggregate reconciles to the national
reference (`Σ_z w_z·price_z == price_national`), equivalently the **weighted basis sums to zero** — the
basis only *redistributes* national cost across zones. B5 inherits the consequence directly and it is
the crux of the coping failure: **at the national/portfolio level a fully-diversified book carries no
basis** (the weighted basis nets to zero), but a **regionally-skewed** book (over-weight in a
high-basis zone) carries the residual. So the company's exposure is a **function of its own book
geometry vs the reconciliation weights** — a book weighted like the national demand shares is basis-neutral;
any deviation from those weights is exactly the unhedgeable exposure. The harness can therefore sanity-check
that a book matched to the national weights shows ~zero realised basis (a useful non-tautological control
edge, R15 FAIL-OPEN guard: a "zero basis on a matched book" result must be *derived*, not asserted).

---

## 6. Portability & scale-readiness

- **Portability:** the basis-exposure logic is **keyed by zone/regime, not hardcoded to GB zones** — it
  consumes a typed zonal-price observation over a configurable zone key set (the same seam W1_8 exposes)
  plus the company's own book weights, so a second market (its own zones, or nodal granularity) fits
  behind the unchanged interface. The rule "residual = Σ book_weight · observed_basis" is
  geography-independent. Hardcoded zone names/count in shipped company code = portability debt,
  remediated on next touch. Product-as-first-class: basis is per (zone × product) wherever a second
  product would settle regionally.
- **Scale-readiness (C-S1..C-S5):** zonal price observations are **events arriving over time** — the
  company must cope with zonal prints arriving one at a time, late, or out of order (C-S1); processing
  the same zonal print twice must not double-count the basis residual (C-S2 idempotency; the belief
  update reads from its own state, does not perturb other subsystems); request/response for a zonal
  snapshot are separate events in time, not same-step resolution (C-S3); the running basis-P&L
  accumulation persists behind the append-only event-log abstraction (C-S4); and any L3 claim states
  whether the basis-accumulation logic is time-scale invariant (C-S5). **SIMPLICITY GUARD:** a book
  weight vector + observed zonal basis + a dot-product residual + a belief field is the whole mechanism
  — no regional-hedge-market cathedral (there is, by construction, no market to model).

---

## 7. Open questions (NOT decided here)

- **Belief construction (L2):** how the company infers expected regional basis from observed settled
  zonal prices — a naive last-value carry, a seasonal-normal, or a short lookback — is a BUILD-time
  design question; whichever is chosen must be **observable-only** and is *allowed to be wrong*.
- **No-skill baseline (A6):** confirm the "assume-zero-basis / national-hedge-fully-protects" naive
  posture is the right no-skill baseline to normalise the gap against, or whether a "match-book-to-
  national-weights" baseline is the fairer floor. Deferred to the A6 gap-metric owner.
- **Coupling registration:** at BUILD, `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` must gain
  `W1_8 ↔ B5` (mirroring the pending `W1_5 ↔ C13` note) so the pair's gap is reported — flagged for
  BUILD, not done here (map/code edit).
- **Book-reshape vs accept (L2 strategy):** since the basis cannot be hedged, the only levers are
  book geometry (regional concentration) and price — where the company sits on that frontier is
  strategy and must be *visible*, not optimised silently. Ties to `B3_hedge_tariff_alignment` and the
  C13 note about the same frontier.

---

## 8. Proposed map stanza (for the orchestrator; F1 — this fork does not edit the map)

```yaml
- id: B5_regional_basis_risk
  name: "Regional basis risk (COUPLED): the company settles regional volumes at published zonal prices but can only hedge nationally -- no regional forward market exists -- so a regionally-skewed book carries unhedgeable basis; gap = assumed-national-hedge protection vs realised zonal basis cost (company twin of W1_8)"
  lane: B_commercial
  value_stream: wholesale_to_price
  epoch: 3
  level_current: 0
  level_target: 3
  loop_stage: idle
  dial_inherited: 3
  provenance: proposal
  evidence: [docs/design/frame/B5_regional_basis_risk_FRAME.md, docs/design/frame/W1_8_zonal_locational_pricing_FRAME.md]
  file_scope: [docs/design]
  simplifications: ['2026-07-16 H17 Lane-3 DISCOVER (fork, doc-only): AUTHORED as the coupled company-side twin of W1_8_zonal_locational_pricing (provenance: proposal, EPOCH_GATING -- the agent may AUTHOR candidate atoms, never BUILD until opened). The company observes settled/published zonal prices through the wall, holds a national-only hedge (B3), and CANNOT buy a regional-basis hedge because no regional forward market exists (the real-world structural fact) -- so a regionally-skewed book carries unhedgeable basis and may wrongly assume its national hedge protects it. GAP = assumed-national-hedge protection / believed basis exposure vs SIM ground-truth realised zonal basis cost (Sigma_z volume_z * basis_z); reported per coupled pair each digest + Proof door. Pinned to R13: the zonal regime existence/severity is director-authored CURRICULUM (inherited from W1_8 sec6), never agent-tuned to company basis loss; under the national baseline this atom is dormant/zero. Distinct from B3 (national-only, no regional notion) and C13 (weather-normalisation demand twin of W1_5, mentions basis only in passing). Aggregation-consistency (W1_8 sec4): a book matched to national demand weights is basis-neutral; the skew is the exposure. COUPLED_TRIAD binding rule: W1_8 and B5 release L3 TOGETHER -- neither alone. BUILD opens with W1_8 (gated on W1_6_physics_price_signal + a director-opened zonal curriculum scenario); at BUILD, register W1_8<->B5 in background/coupled_triad.py::_AUTHORITATIVE_COUPLING. Level HELD at 0 (BUILD-gated). See docs/design/frame/B5_regional_basis_risk_FRAME.md.']
  expert_hour: {status: not_attempted, last: null, findings: []}
  real_world_twin: "a real GB supplier with a regionally-skewed book hedged only to the single national forward curve, carrying regional basis it has no instrument to lay off"
  depends_on: [W1_8_zonal_locational_pricing]
```

---

## 9. What this FRAME is NOT claiming

- NOT a level move — held at **L0** (a proposal atom's FRAME ≠ built; EPOCH_GATING Rule 1, BUILD-gated).
- NOT a map edit — the stanza in §8 is a **proposal** for the orchestrator's single-writer fold (F1).
- NOT a claim the coupling is built — W1_8 and B5 both stay L0/gated until the pair is run and the gap
  measured (COUPLED_TRIAD).
- NOT any new numeric claim — no basis figures, no zonal prices, no P&L numbers are fabricated; a
  regional forward market does not exist in real GB, and whether a zonal regime runs at all is director
  curriculum (R13).
