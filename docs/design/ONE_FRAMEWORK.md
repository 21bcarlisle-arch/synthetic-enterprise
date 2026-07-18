# ONE FRAMEWORK — the single structure that subsumes horizons, epochs, the value cycle, the maturity map, the Hardening Loop, the coupled triad, and the dials

**Status:** DISCOVER/FRAME **PROPOSAL**, doc-only, director-facing. No code, no `maturity_map.yaml`, no `supervisor.py` edits. Written in an isolated worktree, 2026-07-18. The director ratifies; the build plan (§7) is built one gated sub-step at a time.

**The problem (director, verbatim intent):** *"Multiple versions of the truth. Horizons, epochs, the maturity map, THE_VALUE_CYCLE_FRAMING, the charters each describe the vision's structure and drift against each other, so 'what to build, in what order, at what level' has no coherent answer."*

**The claim of this document, in one line:** these are **not competing maps** — they are the **columns of one table, the stages of one loop, and the terms of one draw**. There is already a single structure (`docs/design/maturity_map.yaml` + `background/supervisor.py`'s draw). What is missing is the recognition that everything else is a *projection of it*, plus the binding of three drifted dimensions (epoch, value-stream, compounding-order) back to the mechanism so the framework is **enforced, not just written**.

---

## 1. The single structure

### 1.1 The one thing: the ATOM is the quantum; every map is a projection; the DRAW is the arbiter

There is exactly one canonical object — the **atom** (`maturity_map.yaml`, 113 today). Every "dimension" the director named is either a **field of the atom** (a coordinate), a **stage the atom passes through** (the loop), or a **term in the function that picks the next atom** (the draw). Nothing floats free of the atom.

The dimensions sort into **three families**, and this is the whole framework:

```
                         ┌─────────────────────────────────────────────────────┐
   ①  COORDINATES        │  WHERE an atom sits — static facets of ONE table.    │
   (facets = GROUP-BYs)  │  Different "maps" = different GROUP-BY of one atom set│
                         │    lane          → Function-matrix view              │
                         │    value_stream  → Value-cycle-flow view             │
                         │    epoch         → Campaign view                     │
                         │    level_current → maturity (how real it is)         │
                         │    couples_with  → coupled-triad partner             │
                         │    depends_on    → dependency graph                  │
                         │    file_scope    → concurrency (disjointness)        │
                         │    front         → authorization region              │
                         └─────────────────────────────────────────────────────┘
                                              │ an atom rises through…
                         ┌─────────────────────────────────────────────────────┐
   ②  THE LOOP           │  HOW an atom earns a level — vertical motion.        │
   (the Hardening Loop)  │    loop_stage: DISCOVER→FRAME→BUILD→VERIFY→HARDEN     │
                         │    L0→L1→L2→L3→L4→L5, gated by the loop + Expert Hour │
                         │    coupled-triad: no world atom →L3 until its company │
                         │    twin's belief-vs-truth GAP is measured            │
                         └─────────────────────────────────────────────────────┘
                                              │ which one moves next is decided by…
                         ┌─────────────────────────────────────────────────────┐
   ③  THE DRAW           │  WHICH atom is picked, in what order — the arbiter.  │
   (supervisor pipeline) │    FILTER  authorized? (front ∩ ¬gate)               │
                         │    FILTER  loop-stage eligible? (BUILD / idle / site)│
                         │    FILTER  coupled-L3 gate, deps met, file-disjoint  │
                         │    WEIGHT  by dial   (the equaliser = velocity)      │
                         │    TIE-BREAK  compounding-return, then critical-path │
                         │             (LAW A: a diagnostic, never a target)    │
                         └─────────────────────────────────────────────────────┘
```

- **Horizons, epochs, value-cycle stages, the function matrix** are all **family ①** — they are *the same atom set grouped by a different column*. They cannot "drift against each other" any more than a spreadsheet's rows drift when you sort by a different column. Where they *appear* to drift, it is because a column has decayed (value_stream, §2) or is unenforced (epoch, §2) — a data-hygiene defect, not a rival map.
- **The maturity levels + the Hardening Loop + the coupled triad** are **family ②** — the *process* every atom runs to move up. One loop, not several.
- **The dials, the compounding-return order, the critical path, the fronts/gates** are **family ③** — they are not maps at all; they are *knobs and precedence rules on the one draw*.

### 1.2 The test: one answer to "what / in what order / at what level"

Given the framework, the three questions collapse to **one function evaluated over one table**:

- **What to build?** = the **output of the draw** (`_maturity_map_draw_concurrent`) — the atom(s) that survive the filters, weighted by dial.
- **In what order?** = the draw's **precedence**: authorization (front/gate) → eligibility (loop-stage) → dial weight → tie-break (compounding-return, then critical path). Deterministic given the atom fields + the director's dials/fronts.
- **At what level?** = the atom's **loop_stage** advancing `level_current → level_target`, each step earned by passing the loop and (for L3) the coupled gap.

There is no second answer because there is no second object. The epoch arc doesn't answer "what next" — it *describes* the campaign; the draw answers it. The value cycle doesn't answer "at what level" — it *groups* for the veteran's eye; the loop answers it. **Every framing is a lens on the atom; the draw is the only decider.**

### 1.3 Worked example — one atom seen through every dimension at once

`W1_5_premise_demand_shape` (the per-premise half-hourly demand layer of the weather cascade, §3):

| Dimension (family) | This atom's value | What it means here |
|---|---|---|
| lane (①) | `W1_market_weather` | Function view: it's a World/Weather capability |
| value_stream (①) | `wholesale_to_price` | Cycle view: it feeds price formation |
| epoch (①) | 3 | Campaign view: filed under the walls/physics epoch |
| level_current→target (①/②) | L0 → L3 | It doesn't exist yet; target is "faithful" |
| couples_with (①) | `C13_weather_normalisation` | Coupled twin: the company must discover its book's weather sensitivity through the wall |
| depends_on (①) | `W1_4_regional_weather_field` | Cascade layer above it (regional weather) must exist first |
| file_scope (①) | `simulation/**` | Concurrency: disjoint from company/harness work, co-drawable |
| front (①) | `SIM_ACTORS` | Authorization: inside the director-opened SIM-actors region |
| loop_stage (②) | `discover` | Hardening-Loop position: research-only right now |
| coupled-L3 gate (②) | blocked until C13's gap measured | Cannot reach L3 until the company has been tested against it |
| dial (③) | 4 (hot) | Velocity: W1 is a hot lane |
| gate check (③) | epoch 3 ≤ SIM_ACTORS ceiling 3 → OK; DISCOVER→BUILD is a reserved gate | Thinking is free now; BUILD-open needs a director console act |

Reading this row **is** the answer for this atom: *right now it is DISCOVER-only (loop_stage), authorized to think (front), gated from BUILD (stage gate), and it cannot reach its L3 target until C13's gap is measured (coupled loop).* One row, one answer, every dimension consistent — because they are one object.

---

## 2. Conflict ledger — where two sources drifted, and the resolution

Each is named, resolved, and (where reversible) given a default + log so the director reverses at a boundary, not before.

| # | The drift (source A vs source B) | Resolution | Rationale (one line) |
|---|---|---|---|
| **C1** | **Epoch arc (narrative order)** vs **compounding-return (build order)** — COMPOUNDING_WORK_FIRST.md states them as explicitly disagreeing. | **Narrative DESCRIBES, the draw DECIDES.** Epoch stays the atom's *campaign coordinate* (family ①, a view). Build order is a **draw tie-break** (family ③). Add a `compounding: true` atom flag the draw prefers in tie-breaks — because today "compounding goes first" is **prose-only, unenforced** (grep confirms no code reads it), i.e. a decayed rule (MAKE_IT_STICK). | Where narrative and build order disagree, build order wins — but only as a *tie-break under LAW A*, never a target. |
| **C2** | **Horizons (S1–S5: proof→depth→scale→products→go-live)** vs **Epochs (1–5: fidelity→value-cycle→walls→evolution→go-live)** — two 5-step time axes that are near-parallel but not identical. | **One spine, two owners.** Epoch is the **build campaign** coordinate (on the atom). Horizon is the **director's strategic overlay**, expressed *through the mechanism he already controls* — which **fronts** are open and how the **dials** are set — NOT as a second axis on the atom. S1 "proof-first / start the clock early" = a standing dial on the shadow-live atoms; S2 "depth-before-scale" = dials up on customer-physics, down on population-scale; S5 go-live = an epoch-5 front the director hasn't opened. | Two parallel axes is the drift; collapsing the strategic one onto fronts+dials removes it without losing the director's steering. |
| **C3** | **Value-stream view** vs **function-matrix view** — MATURITY_MAP.md §6 already says these "dissolve into view toggles." But the data has **decayed**: 77 of 113 atoms carry `value_stream: close_to_learn` (a default dumping-ground), only 36 are genuinely classified. | **value_stream is a CURATED FACET, not a free-typed field.** It is a **view only — the draw must never read it** (and today correctly doesn't). Re-derive/curate it (a one-pass classification, ideally computed from lane+capability, checked at phase-close) so the Value-Cycle view is honest. **Default + log:** treat the 77 `close_to_learn` as *unclassified*, not as a claim, until re-curated. | A view is only as good as its column; a decayed column looks like a rival map. Fix the data, not the model. |
| **C4** | **MATURITY_MAP.md: "epoch gating gates BUILD"** vs **the draw never reads `epoch`** — enforcement is only indirect (via `loop_stage: idle`), so the epoch *ceiling* is honour-system until fronts land. | **Adopt SELF_GOVERNANCE fronts as the mechanism that finally BINDS epoch to the draw.** A front's `epoch_ceiling` gate makes "advance into epoch > ceiling" a HOLD the draw enforces. Until fronts land, epoch is documented-but-unenforced and must be *labelled as such* — not asserted as a live gate. | A rule the mechanism doesn't read is a rule that has already decayed; name it honestly and mechanise it. |
| **C5** | **COUPLED_TRIAD_DESIGN.md schema (`couples_with`, `gap` on the atom)** vs **the yaml has 0 `couples_with` fields** — yet the draw's coupled-L3 gate is *already wired*, reading a **separate** `coupled_gap_ledger.json`. Split brain: the gate reads a side-file the schema and site can't see. | **Land `couples_with` in the yaml as the single source of the coupling topology;** keep the ledger for *measured gap values only* (the volatile part). The draw reads `couples_with` for topology + ledger for the number; the site renders the coupling from the same field. | One source for structure, one for measurement — no facet the mechanism uses should live only in a side-file. |
| **C6** | **"The agent proposes level-ups; it never moves a cell"** (MATURITY_MAP §0) vs a **real 2026-07-18 incident** where the orchestrator self-levelled W1_4/D5/E4, and MAP_TRUTH_RECONCILIATION's finding that the map had **no external-truth reconciliation**. | **LEVEL is a GATE (family ②/③ boundary), not a self-serve field.** Keep the built F1 (atomic in-commit inbox) + F2 (fail-closed reconciliation stop), and add SELF_GOVERNANCE §10.1's `LEVEL_SELF_PROMOTION` alarm. The agent's path is build→verify→**propose**→director+advisor move the cell. | The map drives the draw; a wrong level makes the loop re-draw finished or skip earned work — level integrity is load-bearing, so it is a wall. |
| **C7** | **Three ordering signals** — dial weight (MATURITY_MAP §8), compounding-return (COMPOUNDING_WORK_FIRST), critical-path tie-break (PROVISIONAL_PLAN §Use) — with no stated precedence, so "in what order" is genuinely ambiguous. | **Fix the precedence in the draw, in this order:** ① authorization filter (front/gate) → ② eligibility filter (loop-stage, deps, coupled-L3, disjoint) → ③ dial-weighted random pick → ④ tie-break: compounding-first, then critical-path. All of ③–④ are **LAW A diagnostics/tie-breaks, never targets or gates.** | Three signals with no precedence is three answers; a fixed precedence makes it one. |
| **C8** | **Canonical prose (MATURITY_MAP.md v1.1, SELF_GOVERNANCE §10.2 "run the canonical map")** vs **the yaml being the machine store** — risk the human spec and the machine store silently diverge (the very class MAP_TRUTH_RECONCILIATION gated on). | **The yaml is the single source of truth for the draw; MATURITY_MAP.md is its human-readable spec and MUST be kept a projection of it** (levels/dials/lanes generated or checked, not hand-maintained in parallel). This framework doc is the *reconciliation layer* naming that rule. | Two authorities for one fact is the self-report-vs-external-truth class; declare one authority. |

**Reversibility note (PROCEED_BY_DEFAULT):** C1, C2, C3, C7 resolutions are reversible dials — change a flag, a curation pass, or the tie-break precedence and re-draw. C4, C5, C6, C8 touch the *schema/mechanism* and so are gated (SELF_GOVERNANCE's schema/sim-structure gate); they are **proposed here, ratified by the director, built in §7**.

---

## 3. The coupled physical system — weather → house → usage → wholesale price as ONE cascade

The director's steer: treat weather → house/premise physics → usage → wholesale price as **one coupled physical system, not scattered atoms**. The framework re-expresses the scattered `W1_3/W1_4/W1_5/W1_6 + C13` atoms as a **single ordered cascade** whose atoms are its **layers**, each coupled to a company twin, each gap-measured — the coupled triad applied down a physical chain.

### 3.1 The cascade as one object (family ① dependency chain + family ② coupled loop)

```
   LATENT REGIME (blocking-high vs westerly)  ── the common cause, persists for days
            │  drives, jointly
            ▼
   W1_3 national weather  (L1 layer) ─────────────┐
            │ conditional-on, projected-consistent │ SAME weather drives BOTH
            ▼                                       ▼
   W1_4 regional weather field (L2 layer)     wind/solar output
            │ premise responds to its region       │
            ▼                                       │
   W1_5 premise demand shape (L3 layer)            │
            │ premises sum to the country          ▼
            ▼                              residual demand = demand − renewables
   national demand ────────────────────────────────┘
            │                                        │
            └──────────────► W1_6 physics price signal (L4 layer) ── merit order
                             PRICE IS AN OUTPUT, NEVER A DRAW
                                        │
                        ┌───────────────┴────────────────┐
                        │  THE WALL (company sees outturns │
                        │  + regional forecasts + its own  │
                        │  meter reads — NOT L1 regime,    │
                        │  NOT L3 true thermal params)     │
                        ▼                                  │
             C13 weather_normalisation  (company twin)     │
             infers its book's weather sensitivity from    │
             confounded meter data — allowed to be wrong   │
                        │                                  │
                        ▼                                  │
             HARNESS: gap = |belief − truth| / no-skill    │  ← the score
             (structurally unreachable 0 = wall leak)      │
```

**The single correlation the whole cascade exists to keep alive:** *cold-and-still* — the coldest GB days are blocking-high days with low wind, high heating demand, tight margin, and a price spike. Drawn independently, that supplier-killing winter tail vanishes and every hedge looks fine — a lie. The latent regime makes the tail **mechanistic and guaranteed**, and price falls out of it as an *output*.

### 3.2 How the framework re-expresses the scattered atoms (this is framing, NOT a build)

W1 stays **DISCOVER** — nothing here proposes building it. The re-expression, in framework terms:

- **The five atoms are one cascade, not five features.** In family ① they are a **`depends_on` chain** (`W1_3 → W1_4 → W1_5 → W1_6`, with `W1_7/8/9 → W1_6` already wired). Propose grouping them under a `chain: weather_cascade` tag (a *view* facet, like value_stream) so the site can render the cascade as one flow, and so the draw's dependency walk treats them as the ordered chain they physically are.
- **Each layer is coupled** (family ②). Add `couples_with` so `W1_5 ⇄ C13` (and, as they mature, `W1_6 ⇄` the company's price/hedge read). The coupled-L3 gate then *automatically* enforces "no cascade layer reaches L3 until the company has been defeated by it" — the physics can't claim faithfulness until the company has had to cope with it through the wall.
- **The gap is the strategy surface.** C13's belief-vs-truth gap over the national-vs-regional hedging frontier *is* where the company's hedging skill becomes visible and cat-and-mouse becomes real (WEATHER_PHYSICS_HIERARCHY §6.3). GB has no regional forward market, so both frontier extremes must cost money — the gap reporting (COUPLED_TRIAD §5) surfaces where the company sits.

So `W1_3/4/5/6 + C13` are not five items on a to-do list — they are **one coupled physical system**: a cascade (family ①), rising through the loop as coupled pairs (family ②), drawn as a disjoint triad (family ③, `simulation/**` + `company/**` + `harness/**` co-draw). The framework's contribution is to *name the cascade as a first-class object* so the mechanism treats it as one.

---

## 4. VISIBLE — canon + site

**Canon:** this document is the canonical framework, versioned (see §5). It sits beside `MATURITY_MAP.md` (which it reconciles) and is linked from `docs/PROJECT_OVERVIEW.md`.

**Site — reuse the existing render, don't build a new one.** The Project door (`site/project/index.html`, fed by `tools/generate_maturity_map_data.py`) **already renders four toggles of the one atom set**: Function Matrix, Value-Stream flow, Campaign (epoch), Activity view. That render *is* the framework made visible — it is already "many maps, one data." The framework adds, on the *same* data:

1. **A "Framework" explainer panel** — the §1.1 three-family diagram, so a viewer sees *why* the toggles are one thing (the current site shows the toggles but not the unifying idea).
2. **A "Coupled" view toggle** — render `couples_with` pairs and their gaps (the Proof door's `coupled_gaps` block already exists — reuse it as a Project-tab view too).
3. **A "Cascade" strip** for the weather chain (§3) — one row rendering `W1_3→…→W1_6→C13` as a flow, each layer's level + its gap chip.
4. **A "Fronts/Gates" overlay** — shade each atom by authorization (in an open front / gated / off-front), so "what is the loop allowed to build right now" is answerable from the page (SELF_GOVERNANCE's IaC test, rendered).

Every one of these is a projection of the **same** `maturity_map.yaml` + the gap ledger + `fronts.yaml` — no new source of truth, per the map's own "data, not prose; views are toggles" doctrine.

---

## 5. LIVING — the amendment mechanism

The framework must **evolve under the director's amendment and everything re-derive** — like the map's own versioning.

**Single source, everything downstream re-derives.** The atom table (`maturity_map.yaml`) + the console-act ledger (`gate_authorizations.jsonl`) + `fronts.yaml` are the three authoritative inputs. The site, the supervisor's draw, the digest, and the Proof/Project doors all *read* them. Change an input → every reader re-derives on next run. No behaviour-determining state lives outside these readable, committed files (OPS1 IaC).

**How the director amends — five reversible knobs and two gated ones:**

| Amendment | Mechanism | Reversible? |
|---|---|---|
| Turn a lane's velocity | edit `dial_inherited` | yes (dial) |
| Re-classify an atom's view facet (value_stream, chain) | edit the facet field | yes (view only, draw ignores) |
| Open / close a front | director **console act** → `FRONT_OPEN`/`FRONT_CLOSE` in the ledger | one-way-ish (gated) |
| Clear a specific gate for one atom | console act → `GATE_CLEAR` | gated |
| Ratify a level-up | director+advisor level-authorization record | gate (never self-serve) |
| Re-rank / add an atom | edit the atom (agent may author `provenance: proposal`) | yes; BUILD-gated until ranked |
| Change the STRUCTURE (lanes, levels, the loop, this framework's schema) | **epoch-boundary or explicit versioned overturn only** | structural gate |

**Versioning.** This doc carries a version (`ONE_FRAMEWORK v1`) and an amendment log at its foot. Structural changes bump the version *and* MATURITY_MAP.md's (proposal: bank this framework as the trigger to cut **MATURITY_MAP.md v1.2**, per SELF_GOVERNANCE §10.5). The **DIRECTOR_TWIN canon rule** applies: the framework's *structure* changes only by the director's explicit versioned overturn, never by the agent learning from outcomes.

---

## 6. MECHANISM — how the framework becomes THE SPINE THE SUPERVISOR DRAWS FROM (the crux)

This is what separates the framework from "a document nobody enforces." The rule is absolute: **every dimension the framework names must be either (a) a field the draw reads, or (b) a facet the site renders — nothing floats free.** Today the draw reads: `level_current/target`, `dial_inherited`, `loop_stage`, `depends_on`, `file_scope`, the coupled gap ledger, stall state, external-block state. It does **not** read `epoch`, `value_stream`, `couples_with` (the field), `compounding`, or any front/gate. That gap *is* the "document nobody enforces" risk, made concrete.

### 6.1 The draw is already the arbiter — the framework makes it read the whole schema

The proposal is **one draw pipeline reading one schema**, with each family-③ dimension a named, ordered stage. Recast `_maturity_map_draw_concurrent` as an explicit pipeline (it is nearly this already):

```
draw(atoms, dials, fronts, ledger) =
  ① AUTHORIZE   keep a iff authorized_build(a) = in_open_front(a) AND NOT crosses_gate(a)
                                                                       (SELF_GOVERNANCE — NEW)
                 → this is where `epoch` (ceiling), schema/values/one-way-door gates finally bite
  ② ELIGIBLE    keep a iff loop_stage matches the lane being drawn (build|idle|site),
                 level_current < effective_target, deps met, coupled-L3 gate open,
                 file_scope disjoint from picks so far                (EXISTS today)
  ③ WEIGHT      pick primary ∝ dial_inherited; greedily add disjoint others   (EXISTS today)
  ④ TIE-BREAK   among equal-dial candidates prefer compounding:true,
                 then on-critical-path                                (compounding = NEW field)
```

### 6.2 Proposed schema + draw changes (propose only — do NOT implement here)

1. **Land `couples_with` in the yaml** (C5). Draw reads it for coupling topology; the gap *value* stays in the ledger. Fixes the split brain where the L3 gate reads a side-file the schema can't see.
2. **Add a `compounding: true` flag** (C1, C7) as a family-③ tie-break the draw prefers — mechanising COMPOUNDING_WORK_FIRST, which is otherwise **prose-only and already at decay risk**. Strictly a tie-break under LAW A (a diagnostic, never a target or a gate).
3. **Wire fronts/gates into `authorize` (stage ①)** (C4) — adopt SELF_GOVERNANCE_SCOPE_MODEL wholesale; this is the mechanism that finally makes `epoch` (via `epoch_ceiling`), the loop_stage BUILD-open gate, the schema gate, the values gate, and the level gate **enforced by the draw**, not honour-system. Its own §8 build plan is the sub-plan.
4. **Add `chain: weather_cascade` view facet** (§3) — draw ignores it (view only), site renders the cascade strip; the physical coupling is enforced by `depends_on` + `couples_with` which the draw already/will read.
5. **Curate `value_stream`** (C3) — a one-pass re-classification + a phase-close check that a new atom names a real stream (not the `close_to_learn` default). View-only; draw never reads it.
6. **Keep `epoch` a facet the *gate* reads, never the draw directly** — the draw stays lane/level/dial/loop-driven; `epoch` enters only through the front's `epoch_ceiling`. This preserves "epoch gates BUILD, never thought" cleanly: DISCOVER/FRAME on any epoch is always drawable; only BUILD-into-a-higher-epoch is gated.

### 6.3 The enforcement guarantee (R15 — the framework's own controls must be able to fail)

The framework is only real if its bindings can **fail loud**:
- **value_stream / couples_with hygiene** → a phase-close check fails on an atom with `value_stream: close_to_learn` used as an unclassified default, or a `level_target ≥ 3` atom with no `couples_with` (a registration defect COUPLED_TRIAD §4 already names).
- **epoch/front enforcement** → SELF_GOVERNANCE's `DRAW_OFF_FRONT` / `GATE_CROSSED` reconciler alarms, mutation-tested (its M1–M7).
- **level integrity** → the built F1/F2 reconciliation stop + the `LEVEL_SELF_PROMOTION` alarm (C6).
- **compounding tie-break** → a unit test that, given two equal-dial candidates one flagged `compounding`, the draw prefers it — and does NOT treat it as a gate (the non-compounding one still draws when it's the only candidate).

A binding that cannot fail is worse than none. Each proposed field ships **with the control that proves the draw honours it.**

---

## 7. Build plan — gated sub-steps (propose; the director builds one at a time)

Ordered by compounding return (the framework's own §1 medicine, taken first). Each is doc-or-narrow-code, each gated, none opens a front or moves a level.

| # | Sub-step | What lands | Gate / exit test |
|---|---|---|---|
| **0** | **Ratify this framework** as canon; link from PROJECT_OVERVIEW. | `ONE_FRAMEWORK.md` v1 accepted; the three-family model is the standing vocabulary. | Director says "this is the spine." No code. |
| **1** | **Data-hygiene pass (view facets)** — curate `value_stream` (C3), add `couples_with` topology to the yaml (C5, land COUPLED_TRIAD's schema), add `chain: weather_cascade` (§3). **Data only, draw unchanged.** | Yaml carries honest facets; site Value-Stream + a new Coupled/Cascade view render truthfully. | Phase-close check fails on a `close_to_learn` default or a target-≥3 atom with no twin. R11: verify the rendered site view. |
| **2** | **Mechanise the compounding tie-break** (C1/C7) — add the `compounding` flag + draw tie-break + its R15 test. | COMPOUNDING_WORK_FIRST stops being prose-only. | Test: equal-dial pair → compounding preferred; sole non-compounding candidate → still drawn (not a gate). |
| **3** | **Fronts/gates — SELF_GOVERNANCE sub-steps 1–5** (C4, and it carries C6's level gate at its §10.1). Build with both fronts **HELD** — the mechanism proves itself while authorizing nothing. | `fronts.yaml` + reconciler + ledger record types + the draw's `authorize` stage; epoch/schema/values/level gates finally *enforced*. | Its own M1–M7 mutation tests green; reconciler CLEAN on the live map; draw with fronts HELD still draws DISCOVER/FRAME (no idle stall). |
| **4** | **Reconcile the human spec to the machine store** (C8) — make MATURITY_MAP.md's levels/dials/lanes a generated/checked projection of the yaml; bank the evolution as **MATURITY_MAP.md v1.2**. | The prose canon can no longer silently diverge from the yaml. | A drift between the doc's stated level and the yaml fails a check. |
| **5** | **Site — the framework views** (§4): Framework explainer panel, Coupled view, Cascade strip, Fronts/Gates overlay — all on the existing Project-door render. | The single structure is *visible*; "what is the loop allowed to build now" is answerable from the page. | R11: fetch the live door, confirm each view renders from the one data source. |
| **6** | **(Director act) Open the two fronts** — SELF_GOVERNANCE sub-step 6, the console act that turns self-governance on, now expressed in the framework's vocabulary. | The loop self-governs within SIM_ACTORS + SUPPLIER, holding at gates. | Reconciler shows both fronts ON_FRONT, CLEAN; off-front/gated promotions still alarm. |

Sub-steps 1–2 are reversible dials (proceed by default). 3–4 touch schema/governance (director-gated). 6 is the director's own console act. **No sub-step leaves a parallel old path running** (OPS1 discipline).

---

## Amendment log

- **v1 (2026-07-18)** — initial proposal. Single structure = atom (coordinates) → Hardening Loop (levels) → draw (arbiter); three families; 8-row conflict ledger; weather cascade re-expressed as one coupled physical system; mechanism = bind epoch/value_stream/couples_with/compounding/fronts to the draw or render them, nothing free-floating.

---

*Sources read: `docs/design/MATURITY_MAP.md` (v1.1) + `docs/design/maturity_map.yaml` (113 atoms; epoch 17/67/19/7/4; value_stream skew 77 close_to_learn/21 meter_to_cash/9 wholesale_to_price/6 price_to_bill; 0 `couples_with` fields); `background/supervisor.py::_maturity_map_draw_concurrent`/`_is_valid_candidate`/`_idle_discover_frame_draw`/`_site_lane_draw_concurrent` + the coupled-L3 gate (reads `coupled_gap_ledger.json`, not the yaml); `docs/design/THE_VALUE_CYCLE_FRAMING.md` (Epoch-2 spine, four movements); `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` (the L1–L4 cascade, cold-and-still, C13 twin); `docs/design/COUPLED_TRIAD_DESIGN.md` (gap metric, level-def amendment, draw-coupling, `couples_with`/`gap` schema); `docs/design/SELF_GOVERNANCE_SCOPE_MODEL.md` (fronts/gates, epoch/schema/values/level gates, §10 addendum); `docs/design/OPERATIONAL_LAYER_DESIGN.md` (design-the-whole/IaC spine); `docs/design/MAP_TRUTH_RECONCILIATION.md` (F1/F2 level reconciliation); `docs/design/PROVISIONAL_PLAN.md` (critical-path tie-break, director-hours bottleneck, LAW A); `docs/staging/in_progress/COMPOUNDING_WORK_FIRST.md` (build-order-beats-narrative, prose-only today); `docs/staging/done/STRATEGIC_HORIZON_DECISIONS.md` (S1–S5 horizons); `docs/staging/done/Destinationvision.md` (the destination / SIM-interface swap); `tools/generate_maturity_map_data.py` + `site/project/index.html` (existing four-toggle render). Standing laws: RULE 0, PROCEED_BY_DEFAULT, MAKE_IT_STICK, LAW A, R10–R15, EPOCH_GATING, DIRECTOR_TWIN canon.*
