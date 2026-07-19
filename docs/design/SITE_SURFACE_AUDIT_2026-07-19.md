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

## v4 ADDENDUM (2026-07-19, evening) — reorient to the ratified purpose

`DIRECTOR_STEER_SITE_REORIENT_TO_PURPOSE` + `PURPOSE_PITCH_V4.md` landed after the audit above. The
audit's **structural verdict is unchanged** — the sprawl still dies (shadow/*, supplier/, platform/
retired; the six-door consolidation stands; v4 resurrects nothing). What changes is the **job each
kept door does**, because the thesis is no longer "autonomous supplier → go-live" but **carbon
abatement through personalisation, £/tCO₂e, autonomy as the *how***.

**Per-door reorientation (content, not structure):**
- **Front Door ⌂** — THE THESIS CHART becomes the **£/tCO₂e carbon story** (the AI-native
  cost-to-serve gap is the *numerator mechanism*, not the headline). The claim strip states the
  regulatory reality up front (a fully autonomous licensed supplier will not be permitted) and that
  the mission is *chosen, not derived*.
- **The Journey ⑤** — carries the "three possible outcomes (software method · commercial products
  incl. bill-validation · an operating supply business — furthest & least certain), chosen
  direction, capped-human as a research condition" framing. NOT a go-live march.
- **The Company ①** — gains the **carbon three-ledger** view (saved / spent-serving / net) once the
  instrumentation exists; personalisation (per-household cost-and-carbon trajectory) as the product.
- **The World ②** — gains **reluctant homes** (real building stock / half-working kit — the
  remaining carbon is in the *other* homes) and, when built, the business-customer population.
- **The Proof ③** — features **what is not proven** (§13: personalisation-keeps-paying,
  timing-beats-messaging, any real tonne abated) as a first-class surface; the self-caught errors
  (§12) are the credibility spine.
- **Simplified ⑥ / all doors** — claim-status on every figure (constitution rule 6) and the three
  time-sensitive honesty facts (rule 7).

**New surfaces the purpose implies — PROPOSED, NOT built (no new pages until the director's eye):**
these are *content within existing doors*, not new door directories, except where a genuinely new
organ is required. They also imply **new map atoms** (author-then-propose, not build):
1. **Carbon three-ledger instrumentation** — the largest new build the purpose implies (no carbon
   ledger / per-household cost-and-carbon trajectory / £/tCO₂e computation exists today, per the
   Note on Claims). Its DoD must cite `CARBON_NOT_A_TARGET_CONSTRAINT.md` (diagnostic, never a
   maximand). *Company + World surfaces render it once built.*
2. **Volunteer programme gate** — "will not open until a security posture review has completed" is a
   *public commitment*; register it as a real gate atom, not an aspiration. Blocks the validation
   track. (Security-posture = safety/platform — director-reserved.)
3. **Business-customer population** (§10) — I&C above the procurement line, micro/SME below; the
   current world is domestic-only. New SIM scope.
4. **State-layer discovery anchors** (§13 "timing beats messaging" — the least-anchored, most-
   likely-wrong claim): needs discovery anchors before code.
5. **Prior-art discovery pass** (Power TAC, agent-based electricity-market modelling, US rate-design)
   — the differentiation table (§3) is a public claim and must be evidenced like any other.

**Sequence (unchanged principle — propose first):** reconcile the canon (this pass) → director
reviews the reorientation shape → THEN the retire/merge/rebuild runs. Nothing above is executed.

## CORRECTION (2026-07-20) — shadow/* is the advisor deployment mirror, NOT dead sprawl

The original audit listed `site/shadow/` + its 4 sub-surfaces as **RETIRE** ("the pre-redesign shadow
mirror, wholly superseded"). **On closer inspection that is WRONG and I'm reversing it.**
`tools/mirror_github_pages.py` (per the staged `ADVISOR_GITHUBIO_MIRROR.md` instruction) copies
`site/shadow/` → `docs/shadow/` and named state JSONs → `docs/state/` so **GitHub Pages serves them** —
it is the **advisor's github.io visibility mirror**, a deliberately-requested surface + part of the
deployment mechanism, not a superseded public door. `process_run_complete` regenerates and commits it
every run.

**Reclassified: KEEP (or retire only with director/advisor sign-off).** Deleting it would (a) remove
the advisor's visibility surface and (b) touch the GitHub Pages deployment — platform-administration
adjacent (one-way-door category 8), outside the "proceed on the door set" authorization (which covers
the public doors, not the advisor's deployment mirror). The retirement of the genuinely-dead surfaces
(platform/, supplier/ page — both done) does NOT extend to this. Flagged for the director: is the
advisor github.io shadow mirror still wanted, or has the new door set superseded it? Until answered,
it stays.

**Retire-the-dead phase status:** `platform/` retired (20cf4e51b), `supplier/` page retired
(f8021aa87). `shadow/*` reclassified KEEP (above). `sim/` retirement needs the same deployment check
before action. The remaining site work is the content MERGES (customers→Company, timeline→Proof,
wip-flow→Journey, method-casebook→Method) + the v4 narrative reorientation of the kept doors — larger
content passes, not deletions.

## MERGE-PASS SCOPING (2026-07-20) — the remaining site work is entangled, not isolated deletes

The clean isolated orphan-retirements are **done**: `platform/` (20cf4e51b), `supplier/` page
(f8021aa87), `method-casebook/` (75de25db8), `staging-status/` (a011fff8a). What remains is a
**coherent content-merge pass**, not more piecemeal deletes — each remaining surface is entangled:

- **`timeline/` + `sim/`** — both carry the "~30 UK suppliers failed (2021-22)" fact, and a
  cross-surface consistency control (`test_generate_shadow_html.py::test_2021_22_crisis_supplier_
  failure_count_is_single_sourced`) checks that fact across `{index, sim, project, timeline}` with a
  `mentions_fact >= 3` sanity floor. The fact currently lives on **only 2 kept doors** (`world`,
  `project`) — `index` no longer mentions it post-v4-reorientation. So retiring `sim`+`timeline`
  requires FIRST re-homing the crisis-survival evidence onto a 3rd kept door (**The Proof §12 "why
  believe it"** is the v4-correct home — it's data-driven via `proof.json`, so a generator change),
  THEN reworking the control to reference kept doors only. Order matters: content first, delete second.
- **`customers/`** — load-bearing (the Front Door pulse links to it for the last-bill drill-down);
  becomes The Company's household view (§6b keep-list). Re-home as a Company sub-view, don't delete.
- **`wip-flow/`** — the activity view; has its own generator (`generate_wip_flow_data`); re-homes
  into The Journey (§4⑤). Generator + data preserved, surface re-homed.
- **`glossary/` → a site-wide layer**, **`tours/` → the floating Expert-Hour selector** (§5/§6c) —
  feature-demotions (integrate across doors), not deletes.

**Doing these as rushed single-doorbell chunks risks content loss + breaking the cross-surface
controls.** They should be one careful merge pass (re-home content → rework the control → retire the
now-empty surface), ideally with fresh context. Sequenced, low-risk, but not isolated.

### PROGRESS + refined findings (2026-07-20)
- **`timeline/` — RETIRED** (5f8f81efd re-homed the crisis-survival fact to Proof §12; 0262fec7b
  repointed the cross-surface control to `world/` + strengthened it to the consistent "around 30 …
  suppliers" phrasing, then deleted the surface). Proved the content-first order is clean and safe.
- **`sim/` — the HARD one, needs content-migration first (do NOT rush-delete).** Confirmed by
  inspection: its "Customers" stress-KPI content (High/Moderate/Low-Stress bands) and the multi-tab
  SIM Explorer are **UNIQUE to sim/ — present on NO kept door** (company/world/customers checked).
  AND `site/data/sim_data.json` is **load-bearing** — consumed by `generate_world_data`,
  `generate_project_state`, `generate_shadow_html`, `acquisition_funnel_port`, `mirror_github_pages`
  — so the data + `generate_sim_data` **stay**; only the page can go. Plus a dedicated coupled test
  (`test_sim_tab_consistency.py`, a Node render harness over the Customers sub-tab) and the
  cross-surface control still list it. **Plan:** (1) migrate the stress-KPI explorer content into The
  World's `renderSimDepth` (generator + render change, content-loss-sensitive — verify each KPI
  lands); (2) rework/retire `test_sim_tab_consistency` onto the World surface; (3) drop `sim` from the
  cross-surface control (`mentions_fact` then needs a 3rd static kept mention or a proof.json check —
  the crisis fact is already on Proof data-side for this); (4) retire the page, keep the data. This is
  a genuine content-migration, best done as a focused pass, not a marathon-tail chunk.
- **`customers/`, `wip-flow/`** — same class (load-bearing/content re-home), unstarted.

## Note on BRAND1

BRAND1 (`BRAND_CONSTITUTION`) is a *different* case from SITE1 — it shipped real, tested deliverables
(design-tokens JSON, brand-rules file, preserved exemplar, `brand_compliance.py` + 9 passing tests),
so it is **not** "equally unrealised". But its map level was L3 while its own honest note reads L2
(its L3 DoD — the LIVE site consuming the tokens end-to-end + a live-pixel pass — is unmet, and is
entangled with exactly the sprawl being retired here). Corrected L3→L2 to match its own documented
honest status; the end-to-end token adoption rides on the coherent door set being rebuilt.
