# Site surface audit — every surface vs the brief (2026-07-19)

**Why:** director Expert-Hour verdict (console, 2026-07-19) — the site FAILS the bar: incoherent,
sprawling, ~20 surfaces where `POESYS_SITE_BRIEF.md` specifies a **small set of doors**. SITE1
demoted L3→L1 (target stays L3); site is now below-target + drawable. **This is the director's
FIRST TASK: audit → keep/merge/retire → propose the coherent door set BEFORE rebuilding. No new
pages.** This document is DISCOVER-only (doc-only); it executes nothing.

## The brief's canonical door set (the target IA)

`POESYS_SITE_BRIEF.md §4` specifies **six public doors + one private**, reached from **one front
door** — organised by *visitor question*, never by internal architecture:

| # | Door | Persona / job |
|---|------|---------------|
| ⌂ | **Front Door** (`site/`) | 60-second: what this is, that it's alive, where to go. Must carry **THE THESIS CHART** (§6c — the dual-ledger gap; the single most important missing pixel). |
| ① | **The Company** (`site/company/`) | CEO/COO board pack: trading & risk, finance on three clocks, customers & ops (incl. a named household drill-down), compliance & controls. |
| ② | **The World** (`site/world/`) | Domain-expert: the two-sided wall, sim depth, difficulty rack, anchors register. |
| ③ | **The Proof** (`site/proof/`) | Everyone: predictions ledger, verification stack, open defects/simplifications, incident→rule timeline. |
| ④ | **The Method** (`site/method/`) | CTO casebook: operating model, R-rules with their stories, harness architecture. |
| ⑤ | **The Journey** (`site/project/`) | VC + Rich's public view: the maturity map rendered, activity view, epoch arc, the destination/thesis narrative. |
| ⑥ | **Simplified** (`site/simplified/`) | The honesty door — small, permanent, linked everywhere. |
| ⑦ | **Director** (`site/director/`, private) | Rich's console: action queue, dials, comments, digest archive. Linked from nowhere. |

Plus two **cross-cutting FEATURES, not doors** (§5, §6c): the **Expert-Hour tour selector** (a floating
persona walk) and the **glossary layer** (site-wide hover/tap definitions).

**§6 "What dies":** the SIM/Supplier/Platform split as top-level navigation; module inventories;
duplicated epoch prose; any hand-written figure; screenshots of what the live site can show.

## The audit — all 23 live surfaces

| Surface | Verdict | Reason (vs brief) |
|---------|---------|-------------------|
| `site/` | **KEEP** (Front Door ⌂) | Correct door. GAP: THE THESIS CHART (§6c) still missing — the headline pixel. |
| `site/company/` | **KEEP** (① The Company) | Correct door. Absorb `customers/` as the household drill-down (§6b keep-list). |
| `site/world/` | **KEEP** (② The World) | Correct door. Absorb `sim/` depth (§6b: sim tab re-homed under The World unchanged). |
| `site/proof/` | **KEEP** (③ The Proof) | Correct door. Absorb `timeline/` (incident→rule timeline is a Proof section). |
| `site/method/` | **KEEP** (④ The Method) | Correct door — the ONE method door. Merge `method-casebook/` in (dedupe). |
| `site/project/` | **KEEP** (⑤ The Journey) | This IS the map/trajectory door. Absorb `wip-flow/` (the activity view §4⑤). Present it AS "The Journey". |
| `site/simplified/` | **KEEP** (⑥ Simplified) | Correct door — small, permanent, honesty. |
| `site/director/` | **KEEP** (⑦ Director, private) | Correct private door. Absorb `staging-status/` (internal ops → the console). |
| `site/customers/` | **MERGE → Company** | The C6 household drill-down; §6b says it becomes The Company's household view, not a standalone door. |
| `site/sim/` | **MERGE → World** (then retire) | §6b: sim depth re-homed under The World. As a *top-level* surface it is the SIM split §6 kills. |
| `site/timeline/` | **MERGE → Proof** | The incident→rule timeline is a named Proof section (③), not its own door. |
| `site/wip-flow/` | **MERGE → Journey** | The activity view belongs in The Journey (§4⑤ "activity view"). |
| `site/method-casebook/` | **MERGE → Method** | Duplicate method surface — the sprawl the director named. One Method door only. |
| `site/staging-status/` | **MERGE → Director** | Internal staging state → the private console, not a public surface. |
| `site/glossary/` | **DEMOTE to a LAYER** | §6c wants glossary as a site-wide hover/tap LAYER, not a top-level door. Keep the data; retire the standalone page. |
| `site/tours/` | **DEMOTE to a FEATURE** | §5 wants the Expert-Hour tour as a floating selector, not a door surface. Keep the mechanism; retire the standalone page. |
| `site/supplier/` | **RETIRE** | The old Supplier split — §6 explicitly kills SIM/Supplier/Platform as navigation. Content already re-homed in The Company. |
| `site/platform/` | **RETIRE** | The old Platform split — §6 kills it. Content belongs in The Method/Director. |
| `site/shadow/` | **RETIRE** | The pre-redesign shadow mirror — wholly superseded by the six doors. |
| `site/shadow/customers/` | **RETIRE** | Legacy shadow mirror. |
| `site/shadow/project/` | **RETIRE** | Legacy shadow mirror. |
| `site/shadow/sim/` | **RETIRE** | Legacy shadow mirror. |
| `site/shadow/supplier/` | **RETIRE** | Legacy shadow mirror. |

**Tally:** 23 surfaces → **8 kept** (Front + 6 doors + Director) · **6 merged** into a door · **2
demoted** to a cross-cutting feature/layer · **7 retired** (2 legacy splits + the 5-surface shadow
mirror). Result matches the brief's "small set of doors" exactly.

## Proposed coherent door set (the rebuild target — NOT executed here)

```
site/                 Front Door        ⌂   (+ THE THESIS CHART — the one missing headline pixel)
├── company/          The Company       ①   (⊇ customers household drill-down)
├── world/            The World         ②   (⊇ sim depth)
├── proof/            The Proof         ③   (⊇ incident→rule timeline)
├── method/           The Method        ④   (⊇ method-casebook)
├── project/          The Journey       ⑤   (⊇ wip-flow activity view)
├── simplified/       Simplified        ⑥
└── director/         Director (private)⑦   (⊇ staging-status)

cross-cutting features (not doors): glossary LAYER · Expert-Hour tour selector
retired: supplier/ · platform/ · shadow/{,customers,project,sim,supplier}
```

## Sequencing for the rebuild (after director review of THIS audit)

Per brief §7 (presentation-layer restructure over the same generated data, door by door):
1. **Retire the dead** first (shadow mirror, supplier/, platform/) — pure deletion + old-URL
   redirects; lowest risk, biggest coherence win, removes the surfaces that drag the average down.
2. **Merge the fragments** into their owning door (customers→Company, sim→World, timeline→Proof,
   wip-flow→Journey, method-casebook→Method, staging-status→Director) — content re-home, not rebuild.
3. **Demote glossary/tours** to a layer/feature.
4. **Front Door: add THE THESIS CHART** (§6c) — the highest gap-to-value single artefact.
5. Re-run the door-render-harness + mobile pass per door; each door graded vs the brief's success
   criteria (§8) before it counts.

**Nothing above is executed in this pass** — the director asked for the audit + the proposed door
set *before* rebuilding, and for no new pages. The retire/merge/demote work is the drawable SITE-lane
build that this audit unblocks, to be done against this map after the director's read.

## Note on BRAND1

BRAND1 (`BRAND_CONSTITUTION`) is a *different* case from SITE1 — it shipped real, tested deliverables
(design-tokens JSON, brand-rules file, preserved exemplar, `brand_compliance.py` + 9 passing tests),
so it is **not** "equally unrealised". But its map level was L3 while its own honest note reads L2
(its L3 DoD — the LIVE site consuming the tokens end-to-end + a live-pixel pass — is unmet, and is
entangled with exactly the sprawl being retired here). Corrected L3→L2 to match its own documented
honest status; the end-to-end token adoption rides on the coherent door set being rebuilt.
