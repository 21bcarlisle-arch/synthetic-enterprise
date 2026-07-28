# [DIRECTOR-RULING + ADVISOR-STAGED] — K-PILOT amendments, then the pilot brief VERBATIM (2026-07-28)

The pilot brief below is director-decided and carried verbatim from the parallel advisor channel. **It stands as written.** Four amendments and one decision are added here by the director; where they conflict with the text below, **these govern.**

## A. THE CONTENT IS THE PRIMARY DELIVERABLE (director's addition)

Director's words: *"A key part of the pilot is to see the first bits of knowledge and explanation."*

The definition-of-done below has eight items, of which only #1 is "the page exists" — the rest are drills, mutation proofs and graph checks. Left as-is, this pilot could produce excellent machinery and one thin page. Therefore:

- **DoD 0 (ranked above all others): the page must genuinely explain.** An intelligent lay reader, with no energy background, should finish it understanding how GB wholesale electricity prices are formed, what characteristically happens, and where our model of it is weak. The Child's test from Board Spec 005 applies: understood unaided, sayable back in their own words.
- **If the mechanics threaten the content, the content wins.** Any drill, schema or graph check that cannot be completed without thinning the page is **deferred to the generalisation proposal**, and that deferral is a legitimate reported outcome — not a failure. Say which you deferred and why.
- The **~80%-derivation score stays** as an honest measurement, but it is a *finding*, not a target. A page that needed 60% fresh writing to actually explain is a better pilot result than a thin page that scored 90% derived. (R12.)

## B. MONTHLY RENDER CADENCE (director's decision)

*"I don't think we need daily updates of actual data. Monthly is fine for now."*

**Data re-render is monthly**, decoupled from the rate-of-change class:

- the **rate-of-change class** (settled / slow / fast / live) governs how often **claims** are reviewed — the knowledge dimension;
- **data refresh is monthly for the pilot**, whatever the class — the data dimension;
- "live" continues to mean *pipeline-rendered, never prose*; it does not mean continuously refreshed.

Both staleness dimensions still surface per page, so "data-fresh, knowledge-stale" remains legible — on a cadence that costs almost nothing. If you judge some specific block genuinely needs a faster cadence, propose it with the reason.

## C. Knowledge pages are the THIRD canon layer

Coherence with the derivation ruling:

- **Pitch v7** — canon for **purpose and argument**.
- **THE_MODEL_ON_A_PAGE** — canon for **state**: what exists, what is planned.
- **Knowledge pages** — canon for **the domain**: how the world works, independent of us.
- The site derives from all three. **Disagreement between layers is a finding for the director, never an edit by whoever touched a file last.**

This matters immediately: a knowledge page states how prices form *in the world*; the model-on-a-page states what our engine currently does. Where the page's expected-shape block and our engine disagree, that is the membrane firing (§1.8 below) — a fidelity finding, not a page correction.

## D. The external-register rule applies

This is a public explanatory surface, so `e56c145f6` governs: internal vocabulary — atoms, rungs, HARDEN, R-numbers, lane names, campaign labels — appears nowhere on it. Provenance links may point into `/proof`; the page itself reads as a company explaining the world, not a project talking about itself.

## E. Sequencing and the right to argue it down

- This is **one bounded artefact, not a front.** It must not preempt the blocked-mint batch (`a8c182642`) or other ruled product work. Sequencing is yours under the standing rules; parking it with a stated blocking condition is a legitimate outcome.
- **The page is product; the drills are machinery.** Machinery does not outrank ruled product work (PRODUCT-FIRST).
- **You may argue the pilot is too large.** If, on reading the material, you judge that the eight DoD items turn this into a schema-engineering exercise rather than a knowledge one, **say so and propose a smaller first cut that still proves the thesis.** That is a good outcome, not a refusal.

---
---

# K-PILOT — one knowledge page: wholesale price formation (2026-07-28)

**Type:** bounded pilot, director-decided in the advisor channel 2026-07-28.
**Proportionality:** reversible / narrow — proceed under standing rules. Generalisation beyond this pilot is RESERVED (§5).

## 0. Zero-context orientation

The director has decided the project needs a **topic-keyed knowledge layer**: wiki-style pages that capture, validate, cite, and explain the end-to-end industry knowledge behind the SIM — for him, for external audiences, and for the agents themselves. Rationale on record: *"knowledge is the key to any business these days when coding is cheaper"* — the knowledge base is the demonstrable form of the method IP, and the gold standard of observability + explanation + education.

This is NOT a new campaign. It is **one page**, built to a decided format, to prove the approach before anything generalises. It matures the parked `docs/staging/in_progress/DOMAIN_ARTEFACT_LIBRARY.md` backlog item into its real shape. Roughly 70% of the raw material already exists in the repo (§3) — the pilot's thesis is that a page can be ~80% *assembled and derived*, not written fresh.

**Pilot subject: wholesale price formation (GB electricity).** Chosen because every rung already has material: the merit-order DISCOVER (2026-07-25), the residual-demand price engine (W1_6), the fidelity ledger, the spike-tail gap as the honest weakness, and a documented retraction (calm-years naked-hedging) as a worked belief-revision example.

## 1. Decisions already made — transmit as decisions, do not relitigate

1. **Topic-keyed, not work-keyed.** Knowledge pages are keyed to the domain (the world), never to lanes/atoms/phases. The domain outlives every structure we drape over it; ASSUMPTIONS.md rows survived every reorg while phase-lettered docs became archaeology. Same principle.
2. **Six-rung page anatomy** (the director's core ask — "what's more important is the wiki format"):
   1. **Headline** — the claim in one sentence.
   2. **Plain explanation** — GCSE/A-level rung, no jargon.
   3. **Theory + visuals** — mechanism diagrams, maths where it earns its place, every claim cited.
   4. **Expected shape** — what the real-world data characteristically looks like, stated falsifiably in words (e.g. "spike tails reach £4,000/MWh in crisis years; negative prices in ~2% of periods post-2020").
   5. **Live evidence** — the actual history and SIM charts, rendered from the pipeline. Never static images (site constitution).
   6. **Residuals** — simplifications, fidelity gaps, counter-arguments, what we'd add next — **derived** from the registers, not hand-written.
3. **Bidirectional chart-page links.** Charts on the page render from the same pipeline data as the site; at least one existing site chart gains a "how this works" affordance back to the page. So a viewer (human or agent) can go chart to explanation to expectation and back, and quickly check the SIM is doing what we expect.
4. **Two graphs, one derived join.** The topic graph (domain edges) is a separate object from the atom graph (build edges). Starter edge vocabulary, deliberately small: `part-of`, `mechanism-of`, `drives`, `governed-by`, `prerequisite-for` (the pedagogical one), plus two join types `modelled-by` (topic to module) and `touched-by` (topic to atom). **Join edges are generated from primary state (evidence links, declarations), never hand-authored.** Many-to-many is the normal case: one atom (e.g. W1_6) spans several topics; one topic is touched by many atoms. You may propose vocabulary amendments with reasons; additions are schema changes, not casual.
5. **Every claim carries a class:** **Fact** (domain truth, cited, permanent) / **Choice** (our modelling decision, versioned, supersedable with rationale — R13-shaped where applicable) / **Wiring** (how it is currently connected — pure projection, regenerated, never asserted as truth, no revision ceremony). This vocabulary is what stops the wiki ever conflating "inherent" with "currently wired this way".
6. **Every topic (page-level default, per-block override) carries a rate-of-change class:** **settled** / **slow** / **fast** / **live**. The class sets a *floor* review cadence; event triggers always outrank it (the zonal-pricing lesson). "Live" content is never prose at all — pipeline-rendered only.
7. **Knowledge updates are not data updates — a membrane, not a nuance.** Data updates flow through the pipeline: charts re-render, freshness stamps move, prose untouched (render-not-author). Knowledge updates are authored belief revisions with corrections-in-place provenance: old claim struck through, new claim beside it, reason + artefact linked, dated (the Proof-door pattern, applied per page). Two independent staleness dimensions surfaced per page: data freshness (from existing pipeline stamps) and claim `last_verified` (from review discipline). A page can be data-fresh and knowledge-stale, or the reverse — the reader sees which.
8. **The expected-shape block IS the membrane.** Conforming data flows through silently forever. Data that crosses the stated shape stops being a data update and becomes a knowledge event: R4 investigation, then either fidelity work (model wrong) or an authored revision (understanding wrong, struck through).
9. **Bitemporal claims.** Knowledge claims distinguish valid time (when the world changed) from transaction time (when we learned/recorded it) — the same primitive the codebase already owns. Worked example required on the pilot page: the retracted calm-years near-naked-hedging claim, shown as a real revision with both clocks.
10. **Visual-skill tie-in (K3 discipline unchanged):** charts diagnose and communicate, numbers prove. The visual/vision skill judges rendered charts against the page's expected-shape block; a visual anomaly opens an R4 diagnosis, it never passes anything on its own.
11. **Coherence is checkable, not aspirational:** exactly one canonical page per topic (no duplicates); every topic referenced by any edge exists at least as a **stub** (stubs are a legitimate state — identity and place, not depth); `prerequisite-for` edges form an acyclic, walkable chain (a curriculum is a topological sort). All three are cheap graph queries and must be R15-failable.
12. **Structure-independence is a tested property, not an assurance** — see the reorg drill in §6.

## 2. The deliverable (all of it, nothing more)

- **One full-depth page: wholesale price formation**, all six rungs, per §1.
- **Its immediate neighbourhood as stubs** — roughly six linked topics (candidates: the GB electricity market; merit order / residual demand; gas price; carbon price; imbalance/cash-out and settlement; hedging and the forward market; the price cap — final set is yours, from the domain). The "linked topics" sidebar is **generated from the typed edges**, not hand-written.
- **One existing site chart wired with the backlink**, both directions live.
- **A machine-readable per-page schema** carrying: claim classes per block, rate-of-change class (+ per-block override), both staleness dimensions, citations, the typed edges. Encoding is your design; the fields above are decided.
- **The visual skill run once** against the page's expected-shape block, verdict logged.
- **The drills in §6 executed and evidenced.**
- **A short findings report + generalisation proposal** (§8) — and stop.

Housing (where the page lives in the IA, file formats, generators) is your design within the site constitution and the five-surface IA. Sequencing relative to the PUBLISHED_GAPS mints is your call under the standing rules — this is one bounded artefact, not a front; it must not preempt ruled work.

## 3. What already exists — reuse, do not reinvent (grep first)

- **ASSUMPTIONS.md** — the proto-knowledge-base (claim / SIM value / benchmark / source / confidence / last-checked). Topic pages generalise its row into a full page.
- **`docs/market_research/`** — deep sourced findings incl. the merit-order/SRMC stack DISCOVER (2026-07-25), scarcity-constants benchmark, era boundaries.
- **The World door** — already the per-node prototype of this format (real figure + anchor + evidence link).
- **Claim-status vocabulary, freshness stamps, corrections-in-place feed, fidelity ledger, simplifications register** — rungs 5-6 and the revision mechanics are these, reused.
- **`company/compliance/domain_invariants.py`** — encoded knowledge with effective-dates; where a page's claim has an invariant, the page derives from it.
- **Regulation-commons doctrine** — public-reality topics are commons, readable by every lane.
- **The bitemporal event-log primitive** — for the two-clock claim history.
- If any part of the graph/schema mechanics already exists somewhere (it may), say so and reuse — a "this candidate dies, X already covers it" finding is a good outcome.

## 4. Boundaries / walls (unchanged, restated for this surface)

- **Epistemic wall:** page content is restricted to public-reality commons + already-published evidence surfaces. Pages describing generator internals sit OUTSIDE the company's readable set — the wiki must not become a leak vector. State the wall placement explicitly in the page schema.
- **Render-not-author:** no hand-written figure anywhere on the page. Prose is authored; numbers are queries.
- **R12:** page counts / rungs completed are never a score, target, or headline.
- **Fictional clarity** applies to every public page, per the site constitution.
- **No harness changes, no CLAUDE.md changes, no new front, no map restructure** from this pilot. Anything of that shape goes in the §8 proposal.

## 5. Reserved for the director (do not decide these)

- **Generalisation** beyond the one page + stubs — the K-lane framing, dial share, and any topic-tree buildout return as a proposal.
- **Visibility policy** beyond the pilot. Pilot default: the page ships on the existing public site (its subject is public-reality commons and its evidence is already published) — anything gated/tiered is a later, separate decision (REPO_PRIVATE stays parked).
- **The interview/extraction mechanic** for the director's head (grill-me-shaped) — explicitly OUT of pilot scope; note it in the proposal if the pilot suggests it is the right next tool.

## 6. Definition of done — every check failable (R15)

1. Page live, **render-verified (R11)** — cite what was checked on the live surface.
2. Every citation resolves via a **failable link check** (proven to red on an injected dead link).
3. Expected-shape block present, stated falsifiably, and the **visual skill run** against it with the verdict logged (pass or a minted R4 — either is a valid outcome).
4. Chart-page **backlink live both directions**.
5. **Coherence checks pass** for the stub neighbourhood (one-canonical-page, no orphans, acyclic prerequisites) — each mutation-proven to fire (e.g. inject a duplicate topic, check reds).
6. **Reorg drill passed:** simulate a structure change (rename the owning lane / split a linked atom in a scratch copy) — authored prose requires **zero edits**; only generated projections move. Mutation-proven both ways.
7. **Revision drill passed:** the calm-years hedging retraction rendered as a two-clock, struck-through revision on the page, derived from the existing corrections feed.
8. **~80%-derivation claim honestly scored:** state what fraction of the page was assembled/derived from existing material vs written fresh. If the thesis fails, that finding is the pilot's headline — report it, do not massage it.

## 7. Risk section

- **Touches:** `site/**` (one page + one chart affordance), `docs/**` (schema + stubs), possibly one small generator under `tools/`. Additive throughout.
- **Blast radius:** low — no existing surface changes behaviour except the one opted-in chart backlink; publish gate + site-lane gate cover regressions.
- **Probable failure modes + inline mitigation:**
  - *Scope creep into building the full knowledge system* -> hard pilot boundary (§2/§5); generalisation is a proposal, not a follow-on commit.
  - *Hand-authored numbers drifting* -> render-not-author enforced; DoD 2's failable link/figure checks.
  - *Wall leak via explanatory prose* -> §4 wall placement declared in-schema; content restricted to commons + published evidence.
  - *Join edges quietly hand-authored* -> derivation from primary state is a DoD property, mutation-tested (edit primary state, edge must move).
  - *Competing with the gaps-ruling mints* -> bounded single artefact; you sequence it; if it cannot be scheduled without displacing ruled work, park it in `in_progress/` with the blocking condition stated and NTFY — that is a legitimate outcome.

## 8. On completion

One transition NTFY (R5) with: DoD evidence links, the derivation score, the visual-skill verdict, and a **short generalisation proposal** (K-lane shape, next 3-5 candidate topics, any schema amendments) addressed to the director for decision. Then stop — nothing generalises without his call.
