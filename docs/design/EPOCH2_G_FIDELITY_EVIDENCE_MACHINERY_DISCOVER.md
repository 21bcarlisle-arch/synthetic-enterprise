# EPOCH-2 ATOM G — the FIDELITY-EVIDENCE MEASUREMENT MACHINERY + the EMIT-as-you-build discipline (DISCOVER/FRAME, doc-only)

**Status:** DISCOVER/FRAME, doc-only. `provenance: proposal`; **no level claimed.** Writes only
under `docs/design/`; edits neither `maturity_map.yaml`, `supervisor.py`, `coupled_triad.py`,
`coupled_gap_ledger.json`, `CLAUDE.md` nor any engine — those are the orchestrator's / BUILD's
landing acts. **W1 BUILD stays CLOSED** (Epoch-3 BUILD-gated per `EPOCH_GATING_AND_ATOM_AUTHORSHIP`
Rule 1; this campaign proceeds through DISCOVER/FRAME until the director opens it). Isolated
worktree; no push; one commit. **No network this pass** — no market figure fabricated (Historical
Ground Truth); the only empirical numbers quoted are already-committed repo records, cited as such.

**Source of task:** `docs/staging/DIRECTOR_ADDENDUM_FIDELITY_EVIDENCE_2026-07-19.md` — the four
requirements: (1) the four-layer inspection chain navigable both directions; (2) fidelity scored as
a GRID with three measures, none population averages; (3) EMIT as you build; (4) the site renders it
(the SITE rendering is a *separate* SITE-lane atom — this doc designs the DATA/record model it will
render, not the HTML). Extends the campaign scoring frame (`EPOCH2_A_…`) and the cascade-correlation
method (`EPOCH2_D_…`); homed as atom **G** in `EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md`.

**What this atom OWNS that no other campaign atom owns.** Atom A defines *the objective* (the
worst-cell grid, the MAX rule). Atom D defines *the correlation estimator* (the joint-tail lift `L`).
The physics atoms (B/C, E, W1) *produce* the relationships. **G owns the machinery that makes all of
it INSPECTABLE and SCORED rather than asserted — the three fidelity measures, the evidence-record
shape every atom must emit, the four-layer navigable data model, and the R15 mechanism that makes the
measures themselves falsifiable.** In one line: *A says what "good" means, D says how to estimate a
coupling, G says how you PROVE — to a skeptical veteran's eye — that the SIM is faithful and not
inadvertently naive, overly simplistic, or pointlessly complicated.*

**Adopt / adapt / reject of the filed toolkits (`ADVISOR_IDEAS_CROSS_DISCIPLINE_2026-07-18.md`,
the addendum names A5 + D1–D6 as live here).** Explicit dispositions, threaded through the sections
that use them:

| Idea | Disposition | Where |
|---|---|---|
| **A5** Goodhart test at every metric's birth | **ADOPT — it is the load-bearing spine of measure 1.** The frozen-baseline rule IS A5 applied to "lift": lift is a metric that becomes a target, so the thing it is measured against (the baseline) must be un-gameable. | §1.1, §5 |
| **B5** naive-baseline ensembles / "a sophisticated organ that can't beat a naive baseline is the fastest signal it's gone wrong" | **ADOPT as the definition of the naive baseline** — the naive baseline IS the "deliberately crude actuarial baseline" of B5, frozen and scored against the sophisticated organ. | §1.1 |
| **C4** demote-with-tripwire, never delete (dormant ≠ dead) | **ADOPT — it is the honest disposition of a low-lift / low-ablation-Δ driver.** A driver that beats naive nowhere today is a *pruning candidate flagged with its reactivation tripwire*, never deleted; the map-of-ignorance view surfaces it. | §1.2, §1.3, §5 |
| **C5** worst-cell coverage, not average fit | **ADOPT — this is measure 2, inherited wholesale from atom A** (C5 is the idea, atom A is its instantiation; G renders A's per-cell surface as evidence). | §1.2 |
| **C7** adaptive fidelity — compute follows consequence | **ADAPT — governs WHERE the expensive evidence (ablation, per-cell) is emitted densely vs cheaply**, not a new mechanism; the emit-DoD (§3) spends recording effort where consequence lives (crisis regime, worst cell). | §3.4 |
| **D1** common random numbers (CRN) | **ADOPT — it is the mandatory discipline under measure 3 (ablation).** Without CRN the ablation Δ drowns in Monte-Carlo noise; C-S2 substream determinism is what makes CRN cheap here. | §1.3 |
| **D2** orthogonal-array designs | **ADAPT — the affordable way to ablate MANY couplings** without enumerating the 2^k on/off grid; declared as a BUILD efficiency option, not required for the first cut. | §1.3, §7 |
| **D3** Bayesian-optimal run choice | **ADAPT (weak) — "which ablation run most reduces our uncertainty about what matters?"** as a standing question for the ablation batch, not machinery now. | §7 |
| **D5** importance sampling for rare events | **ADAPT — the honest way to get enough crisis-regime (G2/G3) mass to measure a worst cell / ablation Δ at current small cast**; flagged as the BUILD answer to the small-sample limiter, weights corrected so estimates stay unbiased. | §1.2, §7 |
| **D6** EVT for tails | **REFERENCE — already owned by atom D** (POT/GPD marginal tails under the joint-tail estimator); G consumes D's `L`, does not re-derive EVT. | §1.3 |
| **A6** present tradeoff frontiers, not blended recommendations | **NOTE — relevant to the SITE atom, not G's data model**; the inspection chain's CONSTRAINT layer (§4) records the binding constraint + trade-off so the site *can* show the frontier, but G does not build the frontier renderer. | §4 |

---

## 0. The one-paragraph idea

The director wants to *eyeball the evidence of fidelity — the proof this is a great SIM and not
inadvertently misguided, overly simplistic, or pointlessly complicated.* "Great" is not "high average
fit" and it is not "many modules"; it is **beating what any basic outfit models, exactly where it
commercially matters, and proving the integration is real by showing what breaks when you cut it.**
So fidelity is scored on a **grid of three measures, none of them population averages: (1) LIFT over
a frozen, independent naive baseline** — table stakes is matching naive, value is beating it where it
bites; **(2) WORST-CELL COVERAGE** on atom A's driver × (archetype × regime) grid, with the *map of
ignorance* (cells no driver explains) shown as a first-class honest view, not hidden; **(3) ABLATION
VALUE of couplings** — sever a coupling under common random numbers and measure what disappears, so
*"integration that changes nothing anywhere is decorative; integration that erases the crisis when
cut IS the value."* Each measure is built to be able to **fail**: the baseline is hash-pinned so lift
can't be gamed by moving it (A5); an unmeasured cell scores top-severity so blindness can't hide
(atom A's FAIL-OPEN rule); a coupling whose ablation Δ≈0 is honestly flagged decorative, not quietly
dropped. And because *"a viewer over data nobody recorded is worthless,"* the recording of this
evidence — fitted relationship, strength, provenance, per-cell contribution, binding constraint,
ablation Δ — is a **definition-of-done requirement that travels with every campaign physics atom**,
emitted as it builds into an evidence ledger sibling to `coupled_gap_ledger.json`. The site is the
instrument that renders it; this atom is the machinery and the record model behind it.

---

## 1. THE THREE-MEASURE GRID (none are population averages)

The three measures answer the veteran's three questions the addendum names (req 4): **"yes, that's
what drives it"** (measure 1 — the ranked lift shows what beats naive), **"you're missing X"**
(measure 2 — the map of ignorance shows the unexplained cell), **"why is Y in there"** (measure 3 —
the ablation Δ shows whether Y's coupling actually does anything). All three are computed **per
driver × cell**, never as a population scalar, and all three feed the same per-cell surface the atom-A
worst-cell rule already governs.

### 1.1 MEASURE 1 — LIFT over a FROZEN, INDEPENDENT naive baseline

**The object.** For each driver `m` and each cell `(archetype, regime)`, lift is *how much the model's
explanation of that cell beats the explanation a basic outfit would get with the crude baseline* —
weighted by commercial impact, not raw explanatory power:

```
lift(m, cell) = [ err_naive(cell) − err_model(m, cell) ] × commercial_weight(cell)
```

where `err_·` is the cell's belief-vs-truth error in the metric its physics dictates (the atom-A
`gap(cell)` family: classification / detection / attribution / belief-TV / VaR-ratio / the atom-D
joint-tail lift error). **Table stakes = `lift ≈ 0` (you match naive — "anyone can do that").
Value = `lift > 0` where `commercial_weight` is large.** A driver with high raw explanatory power but
`lift ≈ 0` is modelling the obvious (the primary/most-obvious relationship the director calls low
value); a driver with modest raw power but large lift in a crisis cell is *exactly the "lower-
occurrence, high-commercial-impact effect where the value lies."*

**The naive baseline — what it IS (B5 adopted).** Per driver, the "any basic outfit" model — the
deliberately crude actuarial default a competitor would ship without this project's physics:

| Driver family | The naive baseline it is scored against |
|---|---|
| Weather / cascade correlation (D1–D8) | **independence** — draw each variable from its own marginal, couplings off (`L = 1`); the "average correlation" model D's §2 names as the killer erasure. |
| Affordability / collections (A1 cluster) | **flat population prior** — predict the book-average affordability band for every customer (the `tv_prior` already in the W2_4 ledger row, `≈0.491`). |
| Demand shape / cost-to-serve (A2) | **single average PC-profile EAC** — one smooth load shape, no per-customer convexity. |
| Price incidence / who-eats-the-spike (A4, req 3) | **uniform exposure** — assume every customer carries identical price risk (the "a spike hurts us everywhere" naive model B/C §req-3 falsifies). |
| Export / self-gen (A3) | **monotone importer** — assume volume ≥ 0, supplier always the seller. |

Each is the *simplest defensible* competitor model — never a strawman tuned to lose (a strawman
inflates lift; see §5). The naive baseline is itself run through the **same** wall (observable-only)
and the **same** cell grid, so lift is a like-for-like model-minus-naive on identical inputs.

**Un-gameable: FROZEN + INDEPENDENT (A5 / Goodhart — the one trap this measure has).** The moment
lift becomes a target, the cheapest way to raise it is to *weaken the baseline*. That is forbidden by
mechanism, not by exhortation:

1. **Hash-pinned, versioned baseline.** Each naive baseline is a named artefact with a content hash
   (`baseline_id`, `baseline_hash`, `baseline_version`) committed to the repo. A lift figure is
   invalid unless it cites the `baseline_hash` it was computed against. Changing a baseline **bumps
   its version and invalidates every prior lift computed against the old hash** — a baseline change is
   a visible, reviewable event, never a silent drift. (Directly the A5 discipline: the baseline is a
   metric-defining artefact, fenced from the optimisation.)
2. **Computed INDEPENDENTLY of the model under test.** The baseline's error is produced by a separate
   code path that never reads the model's internals, its parameters, or its outputs (mirrors atom D's
   anti-marking-own-homework wall and the R15 TAUTOLOGY guard). A baseline that shares state with the
   model could be silently co-moved to flatter the lift; independence blocks it.
3. **Baseline lives on the BASELINE side of R13.** It changes only for *fidelity-to-reality* reasons,
   decided blind to the model's lift — never because lift "looks low." A crude baseline that a
   sophisticated organ *cannot* beat is a **finding about the organ** (B5), never a cue to nerf the
   baseline. This is the R13 wall applied to the measurement layer.

**`commercial_weight(cell)` — flagged as a VALUES call, not invented here.** Weighting lift by
"where it commercially matters" requires a harm/impact weight per cell. That is a **director values
decision** (R13 curriculum — the same call atom A §6 Q4 and COUPLED_TRIAD flag). This atom does **not**
invent the weight: it ships **`commercial_weight = 1` (equal)** as the null and **surfaces the
unweighted lift surface** so the director can author the weight against a real exposure surface
(`π × harm-per-unit`, atom A §1.4 / atom F). A model must never be tuned toward a chosen weight (R12).
See §6 + §7.

### 1.2 MEASURE 2 — WORST-CELL COVERAGE + the MAP OF IGNORANCE

**Inherited from atom A (C5 adopted, not re-derived).** The per-cell `gap(cell)` surface and the
`FIDELITY_SCORE = MAX over cells gap(cell)` rule are atom A's. G's contribution is the **coverage
overlay**: *which drivers explain which cells*, and the **honest surfacing of cells no driver
explains.**

**The coverage record — driver→cell attribution.** For every cell, G records the ranked list of
drivers that reduce that cell's gap (their per-cell lift, §1.1), so the cell carries an *explanation
provenance*: "A2@G3 is explained by {demand-shape D4 (lift 0.4), joint-tail D1 (lift 0.3)}; residual
unexplained gap 0.25." This is the "ranked drivers per cell" the director wants to eyeball (req 4).

**The MAP OF IGNORANCE is a FIRST-CLASS view (the honest part).** A cell for which **no driver posts
positive lift** — the model explains it no better than naive — is one of two things, and the record
says which:

- **MISSING PHYSICS** — a real supplier-relevant effect the SIM does not yet contain (e.g. A3 export
  cells today: no export coupling registered, atom A §5.3 S4). Flagged **`ignorance: missing_physics`**
  with the named absent mechanism → a candidate BUILD atom.
- **UNTESTED EDGE** — the physics may exist but the cell has no measurement (no population in that
  archetype, no run in that regime; atom A §3.4 FAIL-OPEN). Flagged **`ignorance: untested`** and,
  per atom A's rule, **scored ≥ the worst measured cell for the headline** — never silently dropped.

Rendering the map of ignorance honestly IS the "you're missing X" answer the veteran needs, and it is
the anti-Goodhart guard for measure 2 (§5): a frame that could hide its blind cells could pass while
blind. **Tie to atom A's worst-cell MAX rule:** the map of ignorance and the worst-cell argmax are two
views of the same surface — the worst cell is either a measured-but-poorly-explained cell (fix the
physics) or an ignorance cell (build the physics / draw the population). A low-lift-everywhere driver
is a **C4 demote-with-tripwire candidate** (dormant, not dead — surfaced with its reactivation
condition, never deleted).

### 1.3 MEASURE 3 — ABLATION VALUE of the couplings

**The object.** *"Integration is much of our value" (director). Prove it: sever a coupling and show
what disappears.* For each registered coupling `k` (an atom-D dependence link, a macro↔micro seam, a
world↔supplier seam):

```
ablation_Δ(k, cell) = outcome(cell | k LIVE) − outcome(cell | k CUT)
```

where **CUT** means the coupling's joint dependence is set to the independence null — concretely,
**`L(k) := 1.0`** in atom-D terms (replace the joint draw with two independent marginal draws), or the
seam's message replaced by its marginal/naive default. `outcome(cell)` is the cell's headline: its
**gap** (does explanation collapse without the coupling?) and, where the cell has a £ consequence, its
**crisis-regime financial outcome** (does the loss/VaR the coupling was supposed to create vanish?).
The two headline ablation metrics:

```
Δ worst-cell        = MAX-gap(frame | k LIVE) − MAX-gap(frame | k CUT)
Δ crisis-outcome    = outcome(G2/G3 cell | k LIVE) − outcome(G2/G3 cell | k CUT)
```

**The verdict rule (the director's sentence, made numeric):**
- `|Δ| ≈ 0` **everywhere** ⇒ the coupling is **DECORATIVE** — cutting it changes nothing; it is
  diagrammatic integration, not real. **Flagged honestly `ablation_verdict: decorative`**, a
  **C4 demote-with-tripwire** candidate (armed with the regime condition under which it *might*
  matter), **never hidden and never silently kept.**
- `Δ` large **in a crisis cell** ⇒ the coupling **ERASES THE CRISIS WHEN CUT** — this IS the value;
  `ablation_verdict: load_bearing`, ranked by `|Δ|` in the crisis regime.
- `Δ ≈ 0` on average **but large in one worst cell** ⇒ load-bearing *exactly where atom A scores* —
  the ablation surface is per-cell for this reason (a coupling dormant on the population mean can be
  the whole story in G3, mirroring C4's regime-dependence).

**Un-gameable / not-noise: COMMON RANDOM NUMBERS is MANDATORY (D1 adopted — the discipline that makes
the measure real).** The LIVE and CUT runs must use **identical seed, identical population draw,
identical weather path** — only coupling `k` toggled. **Why mandatory, not optional:** the ablation Δ
is a *difference of two noisy simulation outputs*; run-to-run Monte-Carlo variance on an ~8-minute
run with a small cast is comparable to, or larger than, the effect being measured. Without CRN the
Δ **drowns in noise** — a load-bearing coupling reads Δ≈0 (false-decorative) and a decorative one
reads Δ≠0 (false-load-bearing) purely from seed noise. **C-S2 makes CRN cheap and exact here:** the
substream determinism discipline (each stochastic subsystem draws from its own named, seeded
substream) means toggling coupling `k` perturbs **only** `k`'s draws — every other subsystem's stream
is byte-identical across LIVE and CUT, so the Δ is *causally* attributable to `k` and nothing else.
CRN without substream isolation would still leak (cutting `k` shifts the shared RNG cursor and moves
every downstream draw — the exact 01:09Z incident C-S2 was written for). So the ablation measure
**depends on** and **exercises** C-S2; an atom claiming a clean ablation Δ without substream isolation
is reporting noise (§5, §7).

**Affordability at small cast (D5 adapted).** A crisis-regime ablation needs enough mass in the
crisis corner to resolve Δ; at ~31 accounts, G2/G3 cells are thin. **Importance sampling** (D5) —
oversample the crisis regime, correct the weights so the outcome estimate stays unbiased — is the
honest BUILD answer to get a measurable Δ without waiting for the population-draw atom, and
**orthogonal-array ablation designs** (D2) recover many couplings' main-effect Δ's without
enumerating the 2^k on/off grid. Both flagged for BUILD (§7); ship the single-coupling CUT-one-link
ablation (atom D §4's mutation) first. EVT tails (D6) are atom D's; G consumes the resulting `L`.

---

## 2. PROVENANCE TAGGING — every relationship carries its epistemic status

Every relationship in the evidence ledger (a fitted correlation, a threshold, a cost coefficient, a
band boundary) carries a **`provenance`** enum, honestly declared:

| `provenance` | Meaning | Consequence |
|---|---|---|
| `estimated_from_data` | fitted from a real series with a stated statistic + CI + independent-anchor check (atom D §3 protocol) | the gold standard; records the series, statistic, `u`, CI, anchor |
| `assumed` | a structural modelling assumption not fitted (e.g. a functional form, a default `u`) | recorded with the assumption + what would ground it |
| `asserted` | a specific value/sign set by hand, not derived (a hand-set constant) | **MUST be registered as a simplification (R10)** — `simplification_id` linking to the invariant/simplification library; an `asserted` relationship with no `simplification_id` is a **DoD failure** (§3) |

**How it is recorded + surfaced.** `provenance` is a required field on every evidence-ledger record
(§3); the SITE atom renders it as a per-relationship badge (green estimated / amber assumed / red
asserted-with-simplification-link). **The surfacing is the control:** the director can scan a
relationship and immediately see whether it is *earned from data* or *asserted* — the "misguided or
overly simplistic" sniff test made visible. An `asserted` relationship not registered as a
simplification is caught by the DoD gate (§3.3), not left to discipline (MAKE_IT_STICK: mechanism,
not exhortation). This extends the R10 honesty rule (asserted ≠ estimated) that atom D §3 step 6 and
atom A §5 already apply — G makes it a *field on every record*, not a per-doc footnote.

---

## 3. EMIT-AS-YOU-BUILD (req 3) — the DoD extension every physics atom carries

*"A viewer over data nobody recorded is worthless; the recording requirement travels with every
campaign atom's definition-of-done."* This section makes emit a **definition-of-done gate**, not a
retrofit and not a convention.

### 3.1 What EVERY campaign physics atom must RECORD as it builds

A physics atom (B/C price/cost, D correlations, E billing, W1 cascade, any Epoch-2+ physics) is **not
DONE** until, for each material relationship and decision it introduces, it has emitted:

1. **The fitted relationship + its strength + provenance** — the estimated object (a correlation /
   coefficient / threshold / band), its strength (atom-D `L(u)` with its `u`, or `λ`, or a coefficient
   with a CI), and its `provenance` (§2). For `estimated_from_data`: the series, statistic, CI, and
   independent-anchor check (atom D §3). For `asserted`: the `simplification_id` (§2).
2. **The per-cell explanatory contribution** — for each cell the relationship touches, its **lift**
   (§1.1) against the frozen naive baseline: how much this driver improves *this* cell over naive.
   This is what populates measure 2's driver→cell coverage map.
3. **The binding constraint per material decision** — for each material company decision the physics
   drives, **which constraint bound** and **what trade-off was made** (the CONSTRAINT layer, §4):
   e.g. "hedged to 0.87 not the naive VaR-min 0.92 because collateral capacity bound; shadow price of
   collateral = £X/MWh" (B4 shadow-price framing). A decision recorded without its binding constraint
   is a decision whose *why* is lost — the exact thing req 1's CONSTRAINT layer exists to prevent.
4. **The coupling ablation Δ where cheaply obtainable** — if the atom introduces or crosses a
   coupling, the CRN ablation Δ (§1.3) for that coupling on the cells it touches. "Where cheaply
   obtainable" (C7 adaptive — spend the ablation compute where consequence lives): mandatory for a
   coupling that touches a crisis cell; deferrable-with-a-registered-gap for a coupling far from any
   scored cell (recorded as `ablation: deferred`, reason stated — a deferred ablation is a known debt,
   not a silent omission).

### 3.2 The record shape — a sibling EVIDENCE LEDGER

Extend the existing evidence plumbing rather than invent new machinery. `coupled_gap_ledger.json`
already records, per coupling: `baseline`, `components`, `g0`, `gap`, `metric`, `note`, `raw_gap`,
`measured_at`, `run_git_commit`, `twin_atom_id` — the belief-vs-truth **gap**. G adds a **sibling
ledger, `fidelity_evidence_ledger.json`**, keyed by relationship (not by coupling), that records the
*evidence behind* the gap. Kept a sibling (not crammed into the gap ledger) so the gap ledger's
existing consumers (Proof door, digest) are untouched — the shared-surface lesson (write an un-wired
entry to a consumed surface → red its consumer's tests) is respected: the new ledger gets its own
consumer wired at BUILD, the gap ledger is not disturbed.

Proposed record (one per material relationship; illustrative shape, BUILD fixes exact keys):

```jsonc
{
  "rel_id": "D1_temp_wind_winter_lowtail",          // stable relationship id
  "atom_id": "D_cascade_correlation",               // emitting atom (DoD owner)
  "layer": "EVIDENCE",                               // which inspection-chain layer (§4)
  "relationship": {
    "kind": "joint_tail_lift",                       // correlation / coefficient / threshold / band
    "observables": ["temperature_mean", "wind_speed_mean"],
    "conditioning": "winter_DJF",                    // the regime it lives in (anti-pooling, D §3)
    "strength": { "stat": "L", "value": 2.34, "u": 0.10, "ci": [1.7, 3.1],
                  "ci_method": "block_bootstrap" },  // strength WITH its u and CI
    "provenance": "estimated_from_data",             // §2 enum
    "series_ref": "W1_3 4pt proxy [recall — verify capacity-weighted at BUILD]",
    "independent_anchor": "NESO low-wind-cold stress [recall]",
    "simplification_id": null                         // required non-null iff provenance=="asserted"
  },
  "per_cell_lift": [                                   // measure 1 → measure 2 coverage
    { "cell": "A2_G3", "err_naive": 0.62, "err_model": 0.28,
      "lift": 0.34, "commercial_weight": 1.0 },
    { "cell": "A1_G3", "err_naive": 0.40, "err_model": 0.33, "lift": 0.07, "commercial_weight": 1.0 }
  ],
  "ablation": {                                       // measure 3
    "coupling_id": "D1_temp_wind",
    "crn": { "seed": 4711, "population_hash": "…", "weather_path_hash": "…",
             "substream_isolated": true },            // C-S2 proof — required true for a valid Δ
    "delta_worst_cell": 0.21,                          // MAX-gap LIVE − CUT
    "delta_crisis_outcome": { "cell": "A2_G3", "metric": "VaR_ratio", "value": 0.44 },
    "verdict": "load_bearing"                          // load_bearing / decorative / deferred
  },
  "baseline_ref": { "baseline_id": "weather_independence_v1",
                    "baseline_hash": "…", "baseline_version": 1 },  // §1.1 frozen-baseline pin
  "measured_at": "…", "run_git_commit": "…",
  "basis": { "sub_population": "A2 winter DJF", "as_of_run": "…", "regime_injection": "G3" } // R14
}
```

Notes: `baseline_hash` present ⇒ lift is auditable and can't be gamed by moving the baseline (§1.1).
`crn.substream_isolated` present-and-true is a **required precondition for a valid ablation Δ** (§1.3
/ §5). `basis` carries the atom-A §3.5 / R14 clock so a falling worst-cell / rising lift trend can't
be an apples-to-oranges artefact of a changed population or re-drawn regime.

### 3.3 The DoD GATE — mechanised, so it can't decay (MAKE_IT_STICK)

Emit is a **gate**, not a hope. Proposed mechanism (BUILD): a phase-close check
(`fidelity_evidence_gate`) that, for the atom being closed, asserts every material relationship it
introduced has a `fidelity_evidence_ledger.json` record with (a) non-null `strength` + `provenance`;
(b) `provenance=="asserted" ⇒ simplification_id != null` (R10 mechanised); (c) at least one
`per_cell_lift` entry citing a valid `baseline_hash`; (d) for a coupling touching a crisis cell, a
non-deferred `ablation` block with `crn.substream_isolated == true`. **Missing evidence = the atom is
not done** — the same shape as the existing `basis-labels-present` gate (R14) and the epistemic
verifier. This is the "recording requirement travels with every atom's DoD" made into code, per the
MAKE_IT_STICK diagnosis (a rule lives as enforced code or it evaporates). It must itself be
R15-failable (§5): mutation = strip a relationship's evidence record → the gate MUST red.

### 3.4 Adaptive emit density (C7 adapted)

Emit effort follows consequence: **dense** recording (per-cell lift on every cell, mandatory ablation)
for relationships touching a **crisis regime or a worst cell**; **coarse** recording (strength +
provenance, ablation deferred-with-reason) for relationships far from any scored cell. This is C7's
"compute follows consequence" applied to the *recording* budget, not the simulation — it keeps the
emit-DoD from taxing every trivial relationship equally while guaranteeing the cells that decide the
score are densely evidenced. The deferral is always *recorded* (`ablation: deferred`, reason), never
silent.

---

## 4. THE FOUR-LAYER INSPECTION CHAIN (req 1) — the DATA/record model, navigable both directions

The addendum's req 1: for any relationship or behaviour, four layers navigable **both** directions —
from an odd output *back* to its cause, and from a relationship *forward* to its consequences. This
section designs the **data model** (the SITE rendering is the separate SITE-lane atom §6). Each layer
is a record type; the layers link by stable ids so navigation is a graph traversal.

| Layer | What it records | Key fields | Links |
|---|---|---|---|
| **(a) EVIDENCE** | the underlying data + fit behind a relationship — the wind-vs-price scatter, the fitted `L`, its strength + provenance | `rel_id`, `relationship{strength, u, ci, provenance, series_ref, independent_anchor}` (§3.2) | → produces WORLD outputs (fwd); ← cited by a BELIEF gap (back) |
| **(b) WORLD** | the simulated output as an **explorable multi-variable time series** for the sniff test — what the relationship actually generated | `world_series_ref`, variables, regime label (hidden from company), `driven_by: [rel_id…]` | ← EVIDENCE that drove it; → observed-by BELIEF |
| **(c) BELIEF / ACTION** | what the **company observed, believed at the time (point-in-time, NEVER hindsight), did**, and the measured **belief-vs-truth gap** | `cell`, `belief` (observable-only), `action`, `gap` (the `coupled_gap_ledger.json` row), `as_of` (PIT stamp), `truth_ref` (harness-only) | ← WORLD it observed; ← EVIDENCE it mis/estimated; → CONSTRAINT that bent the action |
| **(d) CONSTRAINT** | **why the action was not the naive optimum** — which constraint bound, the trade-off, the transversal pressure (collateral / cash / obligations) that bent the decision | `binding_constraint`, `shadow_price` (B4), `naive_optimum`, `trade_off`, `transversal_pressure` | ← the ACTION it bent; → the EVIDENCE/relationship whose exploitation it prevented |

**Both-directions navigation (the load-bearing property).** The links are bidirectional edges in a
graph keyed by `rel_id` / `cell` / `world_series_ref`:

- **Odd output → cause** (the director sees a weird number and drills down): a suspicious WORLD series
  or a large BELIEF gap → follow `driven_by` / `truth_ref` back to the **EVIDENCE** relationships that
  produced it and the **CONSTRAINT** that bent the response → *"this odd result comes from D1's
  joint-tail lift meeting A2's shape, and the hedge under-covered because collateral bound."*
- **Relationship → consequences** (the director picks a relationship and asks "so what?"): an EVIDENCE
  `rel_id` → forward through the WORLD series it drives → the BELIEF/ACTION cells it moves (via
  `per_cell_lift`) → the CONSTRAINT decisions it participates in → *"if I distrust this correlation,
  here is every cell and decision that rests on it"* (which is also the C4 pruning view — cut this
  relationship, what loses fidelity?).

**Wall discipline in the model (req 5).** Layer (c) records the company's **observable-only** belief
with its point-in-time `as_of` — never hindsight; `truth_ref` (the SIM answer key) is a **harness-only**
field the company never reads (the gap is truth − belief, held only by the harness). Layer (b)'s
`regime label` is hidden from the company (a real supplier gets no labelled regime). The inspection
chain is a *harness/director* instrument that spans both sides of the wall; the company sees only its
own layer-(c) observables. **A layer-(c) belief that could see `truth_ref` is a wall leak** (gap→0),
caught red — the same TAUTOLOGY guard as atom A §3.4.

**The CONSTRAINT layer is where req-1's "why not naive" and A6/B4 meet.** Recording `naive_optimum`,
`binding_constraint`, `shadow_price`, and `trade_off` is exactly the data the SITE atom needs to show
a **tradeoff frontier** (A6 — the scalarisation visible at the approver's seat) rather than a blended
recommendation. G records the data; the SITE atom renders the frontier.

---

## 5. R15 / ANTI-GOODHART — making the MEASURES themselves able to FAIL

Per R15, no measure counts as evidence unless a **mutation test** proves it fires on its own named
defect. Each of the three measures + the emit gate has a killer mutation and the three-guard check
(TAUTOLOGY / FAIL-OPEN / FAIL-SILENT):

**Measure 1 (LIFT) — the one Goodhart trap is the frozen baseline.**
- **Killer mutation (baseline-gaming):** construct a "model" that games lift by *weakening the
  baseline* — swap the crude naive baseline for a strawman that fails everywhere, so lift inflates
  though the model is unchanged. The control MUST catch it: because every lift cites a `baseline_hash`
  and a baseline change **bumps the version and invalidates prior lifts**, a lift computed against a
  new (weaker) baseline is flagged as *baseline-changed*, not silently accepted; the reviewer sees the
  baseline moved. **A lift that rose only because the baseline fell is catchable** — the measure fails
  the gamer. (This is A5 mechanised.)
- **TAUTOLOGY:** the baseline error is computed by an independent code path that never reads the
  model (§1.1) — a baseline sharing state with the model would let both co-move; independence blocks
  it. **FAIL-OPEN:** a missing/empty baseline error ⇒ lift is **undefined and top-severity**, never
  `lift = err_model` (which a zero-baseline would silently produce). **FAIL-SILENT:** baseline
  artefact unavailable ⇒ the lift check is a FAILED check, never skipped-green.

**Measure 2 (WORST-CELL / MAP OF IGNORANCE) — inherits atom A §3.4's mutations.**
- **Killer mutation:** a model near-perfect on 14 cells, blind (gap≈0.95) on 1 → a MEAN reads ≈0.16
  (looks great, the bug), the **worst-cell MAX reads ≈0.95 → FAIL.** Symmetric mutation: mark one cell
  `untested` → the headline MUST refuse a clean score (FAIL-OPEN). G's addition: mutate the
  driver→cell coverage so an unexplained cell is **omitted** from the map → the map-of-ignorance
  completeness check MUST red (a blind cell that isn't shown is the measure-2 defect).
- **FAIL-OPEN** is the whole point (unmeasured cell counts top-severity); **FAIL-SILENT:** truth or
  belief unavailable for a cell ⇒ that cell FAILS, never green.

**Measure 3 (ABLATION) — must be able to show "decorative", and must not report noise as signal.**
- **Killer mutation A (decorative must surface):** register a coupling that is **wired but inert**
  (the seam exists in the diagram but the CUT run produces an identical outcome). The ablation MUST
  report `Δ≈0 → verdict: decorative` **honestly and visibly** (a C4 demote-with-tripwire flag), never
  hide it or quietly keep the coupling as if load-bearing. A machinery that can't say "this
  integration is decorative" fails req-3's own test.
- **Killer mutation B (noise ≠ signal — the CRN guard):** run the same coupling's ablation **without**
  CRN / substream isolation (`crn.substream_isolated == false`) → the Δ becomes seed-noise-dominated
  and unstable across seeds. The control MUST reject a Δ whose `crn.substream_isolated != true` as
  **not a valid ablation** (top-severity, not a reported number). This is what stops a false
  "load-bearing" (or false "decorative") reading from noise — the ablation is only evidence under CRN.
- **TAUTOLOGY:** the CUT run recomputes the outcome from the generated series, never reads a stored
  "designed Δ". **FAIL-OPEN:** empty crisis-cell sample / NaN Δ ⇒ FAIL loud. **FAIL-SILENT:** LIVE or
  CUT run unavailable ⇒ the ablation is a FAILED check.

**The emit-DoD gate (§3.3) — R15-failable itself.** Mutation: strip a closed atom's evidence record →
the `fidelity_evidence_gate` MUST red. A gate that passes when the evidence is missing is the
FAIL-OPEN pattern the whole emit requirement exists to prevent (a viewer over data nobody recorded).

**The provenance surfacing (§2) — failable.** Mutation: mark an `asserted` relationship with no
`simplification_id` → the DoD gate MUST red (an asserted relationship dressed as estimated is the R10
defect). This makes "honesty about provenance" a control, not a promise.

---

## 6. WALL / CURRICULUM + DECOMPOSITION (the homed atom split)

### 6.1 Baseline vs director curriculum — the values calls flagged, not invented

Per R13, the agent controls both sides of the wall, so anything that is a *values* choice must face
the director:

- **`commercial_weight(cell)` (measure 1) is a VALUES call.** Weighting lift by "where it commercially
  matters" is a harm/impact weighting — the same call atom A §6 Q4 and COUPLED_TRIAD flag. **Ship
  equal weight (`=1`) as the null; surface the unweighted lift surface; do NOT invent a weight.** The
  director authors it against a real exposure surface (`π × harm-per-unit`, atom F). A model must never
  be tuned toward the chosen weight (R12). **Flag for director sign-off.**
- **The naive baselines are BASELINE (R13).** They change only for fidelity-to-reality reasons, blind
  to the model's lift (§1.1). Their *definition* (what "a basic outfit" models per driver) is a
  fidelity judgement, not a difficulty dial — versioned, hash-pinned, reviewable. A director may
  *review* a baseline's realism; it is never softened to raise lift.
- **The measures are DIAGNOSTICS, never targets (R12).** Lift, worst-cell coverage, and ablation Δ are
  reported; none may feed a reward, selection, or promotion signal (A5 fence). A rising lift / falling
  worst-cell is a *finding to interpret*, never an objective to optimise toward — the same anti-goal-
  seek wall atom A §0 and D §6 hold.
- **The wall (req 5).** The randomness and generating structure live in the SIM; the company infers
  from observables; the inspection chain's layer (c) is observable-only with a PIT `as_of`; `truth_ref`
  is harness-only. The evidence machinery is a *harness/director* instrument spanning both sides — the
  company never reads it, never sees its own lift/gap/ablation (a real supplier gets no scored answer
  key). A cell whose gap reaches 0 is a **leak**, not a triumph.

### 6.2 The proposed ATOM SPLIT (the addendum asks the measurement machinery be decomposed into homed atoms)

The machinery is **not** one mega-atom. Proposed decomposition (candidates, `provenance: proposal`;
homing + lane + stage; BUILD stays director-gated):

| Atom | Scope | Lane / home | Stage | Depends on |
|---|---|---|---|---|
| **G1 — grid-scorer** | the three-measure computation: lift-vs-frozen-baseline, worst-cell coverage overlay + map of ignorance, CRN ablation Δ; the frozen-baseline artefacts (hash-pinned, versioned) + their R15 mutation tests | G_data_learning (harness) | FRAME→BUILD (gated) | atom A (grid + worst-cell rule), atom D (`L` estimator), C-S2 (substream isolation for CRN) |
| **G2 — emit-ledger + DoD gate** | `fidelity_evidence_ledger.json` schema (sibling to the gap ledger) + the `fidelity_evidence_gate` phase-close check + its R15 mutation; wiring its own consumer (not disturbing the gap ledger's) | G_data_learning (harness) | FRAME→BUILD (gated) | G1 (record shape), the phase-close skill |
| **G3 — inspection-chain data model** | the four-layer record types (EVIDENCE / WORLD / BELIEF-ACTION / CONSTRAINT) + the bidirectional link graph + the PIT/wall discipline in the schema | G_data_learning (harness) | FRAME→BUILD (gated) | G1, G2, the gap ledger, the bitemporal spine (B2 PIT belief store) |
| **G4 — site fidelity instrument** *(SITE lane)* | renders the ranked drivers per cell, drill-to-evidence, world sniff-test, belief/action/gap follow-through, why-not-naive frontier (A6), map-of-ignorance, provenance badges | **site/** (L2 SITE, parallel) | continuous (renders each Gx output) | G1–G3 data model (renders, does not compute) |

**Sequencing note (LAW A — diagnostic, not target).** G1 (the measures) and G2 (the emit ledger) are
the load-bearing pair — until they exist, the physics atoms have nowhere to emit and the DoD gate
can't gate. G3 (inspection chain) composes their records into the navigable graph. G4 (SITE) renders
and runs in parallel from the first Gx output (L2 SITE is never idle waiting on L1). The emit-DoD
(§3) is a **cross-cutting requirement** that lands with G2 and then travels with *every* campaign
physics atom's close — it is the one piece that is not self-contained to lane G. **W1 BUILD stays
CLOSED**; all of G is DISCOVER/FRAME until the director opens it.

### 6.3 Portability / scale (honoured by constraint, not retrofitted)

- **Function-keyed, not GB-keyed.** The three measures are keyed by *driver / cell / coupling*, never
  by a GB tariff, fuel, or absolute unit; a second market multiplies cells and couplings, never
  changes a measure. The naive baselines are per-*driver-family* (§1.1), so a second geography ships
  its own crude baseline behind the same slot.
- **C-S2 is load-bearing for measure 3** (§1.3) — the ablation *depends on* substream determinism;
  this is a case where a C-S constraint is not optional discipline but the thing that makes the
  measurement valid. **C-S4:** the evidence ledger is durable state behind the append-only event-log
  abstraction (storage form swappable). **C-S5:** the correlation strengths are daily (atom D); any G
  atom claiming L3+ declares the daily-vs-half-hourly basis as a named simplification (R10).
- **Emit is additive (the addendum's own risk note):** the emit-DoD is *recording*, not behaviour
  change — blast radius is campaign-wide but purely additive; it changes no simulation output, only
  what is recorded alongside it.

---

## 7. OPEN QUESTIONS / what BUILD needs (unresolvable here — network / data / director)

1. **`commercial_weight(cell)` — the values call (measure 1).** Equal-weight is shipped as the null;
   the harm/impact weight that makes lift "where it commercially matters" is **director-authored**
   (R13), ranked on a real exposure surface (`π × harm-per-unit`, atom F). **Flag for director
   sign-off; do not invent.** (Mirrors atom A §6 Q4, COUPLED_TRIAD harm-matrix.)
2. **The frozen naive baselines' exact definitions.** What precisely "a basic outfit" models per
   driver (§1.1) is a fidelity judgement needing a real competitor/actuarial reference — verify at
   BUILD against published UK supplier practice / actuarial defaults (no network here). Each ships
   hash-pinned + versioned; a baseline's realism is director-reviewable, never softened to raise lift.
3. **Small-cast statistical power for ablation Δ + worst-cell (D5/D2 adapted).** At ~31 accounts the
   crisis cells are thin; a stable ablation Δ or per-cell lift may need **importance sampling** (D5,
   oversample crisis, correct weights) and/or **orthogonal-array ablation designs** (D2, many couplings
   in few runs). BUILD calls: which; block/CI method; the real fix is population volume (W2_2 draw),
   not a measurement tweak (R12). Ship single-coupling CRN ablation (atom D §4 mutation) first.
4. **Which ablation runs to spend (D3 adapted).** With expensive ~8-min runs, "which single ablation
   most reduces our uncertainty about what matters?" is the standing Bayesian-optimal question for the
   ablation batch — a BUILD prioritisation heuristic, not machinery now.
5. **CRN / substream-isolation coverage (C-S2 dependency).** Measure 3 is only valid where every
   stochastic subsystem draws from a named, isolated substream (§1.3). BUILD must confirm the current
   engine's RNG is substream-isolated for the couplings being ablated; any shared-stream subsystem is a
   **blocker** for a valid ablation there (recorded as a gap, not worked around — a Δ without isolation
   is noise, §5).
6. **The inspection chain's WORLD-series + BELIEF store (G3 dependency).** Layer (b) needs an explorable
   multi-variable time-series store; layer (c) needs the point-in-time belief record (the bitemporal
   spine, B2). BUILD confirms both exist / are wired before G3 can compose the navigable graph; a
   layer-(c) belief that isn't PIT-stamped is a wall-discipline blocker.
7. **Grid/coupling completeness for coverage (measure 2).** The map of ignorance is only honest if the
   grid and coupling registry span the real physics; atom A §6 Q6's data-driven needs-clustering and
   atom D's dependence inventory must be run at BUILD so an unexplained cell is genuinely "missing
   physics / untested edge", not "un-registered coupling". A3 export coverage waits on the S4 export
   coupling registration (atom A §5.3).
8. **BUILD-open + level.** All of G is DISCOVER/FRAME; BUILD-open within the open epoch is the
   director/twin's call (EPOCH_GATING); one-way doors + the values call (item 1) stay director-reserved.
   No level claimed here (`provenance: proposal`).

---

*Sources read/reasoned this pass (no network): `docs/staging/DIRECTOR_ADDENDUM_FIDELITY_EVIDENCE_2026-07-19.md`
(the four requirements — read directly); `docs/design/EPOCH2_A_SCOPE_OF_NEED_SCORING_FRAME_DISCOVER.md`
(the driver × archetype × regime grid, worst-cell MAX rule, `gap=raw_gap/g0` metric family, R15
FAIL-OPEN/TAUTOLOGY/FAIL-SILENT guards, the scoring-vs-value-weight split, the values-call flags);
`docs/design/EPOCH2_D_CASCADE_CORRELATION_ESTIMATION_DISCOVER.md` (the joint-tail lift `L`, its null
of 1.0, the CUT-one-link R15 mutation, the both-sides-of-the-wall estimation framing, CRN/C-S2
dependence); `docs/design/ADVISOR_IDEAS_CROSS_DISCIPLINE_2026-07-18.md` (A5 Goodhart-at-metric-birth,
B5 naive-baseline ensembles, C4 demote-with-tripwire, C5 worst-cell, C7 adaptive fidelity, D1 CRN,
D2 orthogonal arrays, D3 Bayesian-opt runs, D5 importance sampling, D6 EVT, A6 tradeoff frontiers,
B4 shadow prices — each adopted/adapted/rejected explicitly in the header table);
`docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md` (atom homing, the 5-requirement→atom map,
G's home); `docs/observability/coupled_gap_ledger.json` (the existing gap-record shape G's evidence
ledger is a sibling to — W2_10/C12 attribution 0.516, W2_11/D5 detection, W2_4/C6 belief with
`tv_prior≈0.491` the affordability naive baseline); `background/coupled_triad.py::_AUTHORITATIVE_COUPLING`
(the coupling registry the ablation iterates — confirmed no export/self-gen pair yet). The only
empirical numbers cited (W1_3 decile lift 2.34×, winter corr +0.507, `tv_prior≈0.491`) are
already-committed repo records, quoted as directional anchors. R10/R12/R13/R14/R15, COUPLED_TRIAD,
C-S2/C-S4/C-S5, EPOCH_GATING, MAKE_IT_STICK, portability + scale constraints, and the epistemic wall
referenced inline. Provenance: proposal; no level claimed; no market figure fabricated (Historical
Ground Truth).*
