# SITE V5 — Structure confirmation against canon (Sequence step 1)

**Provenance.** This is the artifact required by `DIRECTOR_RULING_SITE_REBUILD_V5_STRUCTURE_2026-07-23.md`
§4.1 ("Structure confirmation first ... confirm this IA against canon ... If a genuine conflict emerges
that this ruling has not already resolved, propose back — do not silently resolve"). It is doc-only
(FRAME/DISCOVER lane), no build, no level move. It gates the surface-by-surface MVP build (§4.2).

**Verdict: CONFIRMED. No genuine unresolved conflict — no propose-back.** The one IA conflict (six-door
→ five-surface) is one the ruling itself resolved explicitly ("this ruling wins"). All remaining canon is
either affirmed by the ruling or reconciles cleanly. Redirect/kill mechanics are implementation items the
ruling declared "yours (open)" — recorded below, not escalated.

---

## 1. Canon cross-check

| Canon | Binding? per ruling | Conflict with the five-surface IA? | Resolution |
|---|---|---|---|
| `BRAND_CONSTITUTION.md` (BRAG palette, colour-is-information, six-glyph grammar, type-only wordmark, light-default ground) | **Binding** (ruling §3) | None. Governs visual/verbal identity, not IA. Sits ABOVE SITE_CONSTITUTION on visual identity. | Affirmed. Every new surface born light, BRAG status semantics (blue=verified-done, green=on-track, amber=at-risk/provisional, red=blocked). |
| `SITE_CONSTITUTION.md` rules **1–7** | **Binding except where the ruling changes the IA** (ruling §3) | Rules 1–7 are claim/evidence/passport/honesty/progressive-disclosure/**claim-status**/time-sensitive-honesty. **No conflict** — the ruling's didactic-graph + claim-status requirements are these rules restated. | Affirmed. Rule 6 (claim-status vocabulary) == ruling §3 claim-status discipline. Rule 7 time-sensitive facts stay data-driven. |
| `SITE_CONSTITUTION.md` **migration order** (six doors: Front / Journey / Company / Proof / World / Method+Simplified / Director) | Superseded on IA | **YES — the six-door IA conflicts with the five-surface IA.** | **Resolved by the ruling itself** ("Where this ruling conflicts with POESYS_SITE_BRIEF's six-door IA or the 2026-07-19 site-reorient steer, this ruling wins"). Journey and Method killed as separate doors; Method folds into Proof; Simplified register folds into Proof/World. Not a propose-back. |
| `POESYS_SITE_BRIEF.md` six-door IA | Superseded on IA | Same as above | Same — ruling wins, explicit. |
| `_redirects` (current: `/supplier`→`/company/`, `/sim`→`/world/`, `/platform`→`/method/`, `/method-casebook`→`/method/`) | Open (ruling §5 "redirect scheme is yours") | `/method/` becomes a killed door → its redirect targets must change; `/now/`, `/tours/` (Journey), `/shadow/` also killed. | Implementation item §3 below. No conflict. |
| Site-lane test gate (`site/test_*.py`: `test_home_door`, `test_evidence_links_resolve`, `test_expert_doors_mobile`) + publish-gate site checks | Binding (must stay green every commit) | None. | Keep green at every commit (ruling §6 mitigation b). These tests reference door URLs — update them in lockstep as doors are killed/renamed, or they red the site gate. |
| `background/fronts.yaml` — SUPPLIER front, `state: open`, `include_paths: [site/]` | Governs BUILD authorization | None. | **Site build is authorized now** — `site/` is an open, ungated front member (L2 SITE lane, runs parallel, never gates an epoch). No new gate to clear for the rebuild. Data-layer generators in `tools/` are also in-repo, ungated. |
| `BOARD_SPEC_005_RECONCILIATION.md` rows F1–F5 | Subordinate to the three goals; per-surface acceptance rubric | None (ruling §2, §3 fold them in). | Use rows as the per-surface rubric where they don't conflict with the three goals. |

**Data-layer dependency check.** The didactic graphs (ruling §3) require real run data. `site/data/` exists and
is regenerated from run outputs by `tools/` generators; the rendering-not-authoring rule (SITE_CONSTITUTION §3)
holds. No new data plumbing is a precondition of structure confirmation — each surface's specific graph data is
scoped inside that surface's phase.

---

## 2. The five-surface IA and current→new mapping

| # | Surface | Single job | Current dir(s) → | Notes |
|---|---|---|---|---|
| 1 | **Front door — the pitch** | marketing (10-second test) | `site/index.html` (rebuild to v4 argument) | Honesty line above the fold; carbon thesis £/tCO₂e. `/now/` killed as default landing — **swap the landing LAST within surface 1** (ruling §6 mitigation d). |
| 2 | **The World** | SIM causal-relationship observability | `site/world/` (absorb `site/sim` content already redirected here) | Spine = weather→wholesale→demographics/segments→usage&behaviour→bills→carbon; each link opens onto live data + external anchor (Elexon/ONS/DESNZ/Ofgem). Didactic graphs are the centre of gravity. |
| 3 | **The Company** | e2e supplier-SaaS evidence | `site/company/` (already absorbs `/supplier`) | Pricing, hedging, billing, credit & collections, customer service, compliance, monthly accounts — real outputs from the latest run. Product capability, **never effort metrics**. |
| 4 | **Proof** | "corrects itself in public", made real | `site/proof/` + fold in `site/method/`, `site/simplified/` | Fidelity results incl. failures; claim-status on every figure; corrections/retractions rendered in place; challenge channel. Method content folds in here. |
| 5 | **Director window** | authenticated ops (MVP) | `site/director/` | Off-nav, auth-gated. MVP = reserved queue first, machine health second. Spec-005 §3 delta-view / DO battery / stop control **DEFERRED — do not build this pass.** Reuse the comments-box auth pattern. |

## 3. Kills + redirect plan (implementation, mine — open per ruling §5)

**Killed (decided by ruling §2):**
- `/now/` as the **default landing** (the dir may stay; it stops being the front door). Landing swap is the LAST step of surface 1.
- The shadow site `site/shadow/**` — supersession banner + `noindex` **at minimum**, removal preferred.
- **Method** and **Journey** (`site/tours/`) as separate doors — Method folds into Proof; Journey killed.
- The **test-count** and **commits/day** charts as public surfaces (the publish-gate build stamp stays internal + untouched — note: CLAUDE.md's "N tests collected" figure feeds that internal stamp; do not remove it from CLAUDE.md).

**Redirect scheme (proposed, to land with the surfaces that kill each door):**
- `/method` , `/method/*` → `/proof/` (currently `/method/`; retarget when Method folds in — surface 4).
- `/method-casebook`, `/platform` (currently → `/method/`) → `/proof/`.
- `/tours` , `/tours/*` (Journey) → `/` or `/world/` (decide at surface 2/4 close).
- `/now`, `/now/*` → `/` (after the new front door lands — surface 1 last step).
- `/shadow/*` → `/` (if removed) or serve with `noindex` banner (if kept).
- Existing `/supplier`→`/company/` and `/sim`→`/world/` **stay** (still correct under the five-surface IA).
- **Full-link walk before each landing** (ruling §6 mitigation a) — no broken internal links when a door is killed.

## 4. Sequence — the five build phases (ruling §4.2, one surface per phase)

Structure is now confirmed, so §4.2 is unblocked. Build order **1→5**, one surface per phase, each landed
**live** and **Expert-Hour-reviewed against its single job** before the next starts. MVP = the surface does its
one job with real data and didactic graphs; not feature-complete, never fabricated. Tracked as a ranked campaign
in `PRIORITIES.md` (§SITE_V5). **Next drawable phase: Surface 1 — Front door MVP.**

**Per-surface DoD** (from the ruling + SITE_CONSTITUTION, reconciled): deployed & **pixel-verified live** (R11);
every figure carries a claim-status + basis-clock passport (rule 6, R14); every major graph states its hypothesis
in the page copy so an Expert Hour can fail it (ruling §6 mitigation c); evidence links resolve; killed doors 301
with a full-link walk done; the site-lane gate green at the commit; Expert-Hour PASS against the surface's single
job; one line in the digest.

## 5. Decided vs open (restated for the build ticks)

**Decided (do not reopen):** five-surface IA; the three goals as the standard; the kills; didactic-graph
requirement; sequence 1→5; deferral of the director-window DO battery. **Open (design is yours):** page-level
design, graph selection within the didactic rule, data-layer refactoring, redirect scheme, how Method folds into
Proof.
