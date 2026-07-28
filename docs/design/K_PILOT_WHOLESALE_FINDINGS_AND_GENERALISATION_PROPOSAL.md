# K-PILOT findings + generalisation proposal — wholesale price formation

**For the director. 2026-07-28. In response to `ADVISOR_PILOT_KNOWLEDGE_PAGE_WHOLESALE_2026-07-28.md`.**

The pilot was built **content-first**, per amendment §A ("the content is the primary deliverable;
if the mechanics threaten the content, the content wins"). One full-depth explanatory page shipped;
the heavier graph/schema machinery was deliberately deferred into this proposal, which §A names a
legitimate outcome. Below: what shipped, the honest scores, what was deferred and why, and the
generalisation proposal.

## 1. What shipped (this tick)

- **The page** — `site/knowledge/wholesale-price-formation/index.html`, reached from the World door
  (nav link + a "how the wholesale price forms →" affordance on the causal chain, so the backlink is
  live **both directions**, DoD 4).
- **Six explanatory sections** (the anatomy, in reader language, no internal vocabulary): the claim
  in one sentence → in plain terms → how it works (SRMC + cited figures) → what the data should look
  like (falsifiable expected-shape) → live evidence (links to the pipeline-rendered price history,
  never a static image) → where our picture is still weak.
- **A machine-readable page schema** — `site/data/knowledge_wholesale.json`: claim class per block
  (**Fact / Choice / Wiring**), rate-of-change class (+ per-block capability), **both staleness
  dimensions** (data freshness + claim `last_verified`), citations, typed edges, wall placement.
- **The stub neighbourhood** (7 topics) and the **"related topics" sidebar generated from the typed
  edges**, not hand-authored (mutation-proven: remove an edge → the neighbour disappears).
- **The belief-revision worked example** rendered as a struck-through, two-clock revision (the
  calm-years near-naked-hedging retraction), DoD 7.
- **Coherence checks, each failable** (DoD 5): exactly-one-canonical-page, no-orphan-edge-targets,
  acyclic prerequisites — each with an injected-defect mutation that reds it.

**Evidence:** `site/knowledge/wholesale-price-formation/test_knowledge_wholesale.py` — 13 tests
green (R11 render via the page's own JS against the real data file; R15 mutations; the three
coherence checks). Full site suite: **370 passed, 7 skipped**. `link_walk`: 0 dead links.
Render-verified **locally** against the real published JSON; **live-surface (R11) publish is pending
the next publish cycle** — not yet claimed as verified on poesys.net.

## 2. Honest scores (findings, not targets — R12)

- **Derivation: ~82% assembled/derived** from existing material (the SRMC/merit-order DISCOVER of
  2026-07-25, the published fidelity gaps, the recorded hedging retraction, the scarcity-constants
  benchmark) vs ~18% written fresh (the plain-language explanation and the connective prose). The
  thesis — "a page can be mostly assembled, not written fresh" — **held** for a topic this
  well-sourced. It will not hold as strongly for a thinly-sourced topic; that is the expected finding.
- **The content is not thin.** An intelligent lay reader finishes the page understanding: price is
  marginal not average; gas is usually the marginal plant; therefore bills track gas + carbon; and
  the specific honest gaps in our model of that.

## 3. Deferred to this proposal (per §A — legitimate, named)

- **Visual-skill automated run (DoD 3, second half).** The expected-shape block is present and
  falsifiable, but the live-evidence block **links to** the World-door price chart rather than
  embedding one, so there is no on-page chart for the visual skill to judge yet. Verdict: **deferred
  with the embedded-chart work.** Proposed: embed one pipeline-rendered price sparkline on the page,
  then run the visual skill against the expected-shape bands.
- **Per-citation failable link check (DoD 2).** Citations render as **named sources** (e.g. "DUKES
  Table 5.10.C (DESNZ)"), with the resolvable URLs living in the DISCOVER doc behind `/proof`. The
  internal evidence links (`/world`, `/proof`) ARE link-walk-checked and fail on a dead target. A
  per-citation **URL** register with its own dead-link mutation test is the clean next step.
- **Reorg drill (DoD 6).** Not run. Structure-independence is *designed in* (the sidebar and all
  joins derive from the typed edges / primary state; authored prose references no lane/atom), but the
  scratch-copy rename-and-prove drill was not executed this tick.
- **The two typed graphs as a general object.** The pilot ships edges as page-local data with the
  starter vocabulary. Separating the **topic graph** from the **atom graph** and generating the
  **join edges** (`modelled-by`, `touched-by`) from primary state across the whole repo is the
  generalisation, not a one-page concern.

## 4. Generalisation proposal (RESERVED — your call, §5)

- **K-lane shape.** A thin **Knowledge lane**: topic-keyed pages under `site/knowledge/`, each with
  the schema above; a top-level "Knowledge" entry in the site nav (deliberately NOT added this tick —
  IA placement is your decision). Dial share: small — this is a slow-cadence surface (monthly data
  render, claim review on rate-of-change class), so it should not out-draw product work.
- **Next 3-5 candidate topics** (each already has repo material, so each should assemble well):
  1. **Imbalance & cash-out / settlement** — the £6,000/MWh ceiling, the settlement timetable work.
  2. **Hedging & the forward market** — the forward-curve basis wall, the hedging-ratio series.
  3. **The retail price cap** — how wholesale reaches the household; the cap mechanics.
  4. **The merit order & residual demand** — promote the current stub to full depth off the SRMC work.
  5. **Carbon pricing (CPS + ETS)** — the one clean constant vs the still-open ETS series.
- **Schema amendments to consider:** (a) a per-citation URL field with a link-check; (b) an embedded
  pipeline-chart slot so the visual skill has something to judge on every page; (c) a repo-wide
  join-edge generator so `touched-by` / `modelled-by` derive from declarations, never hand-authored.
- **Out of pilot scope, noted:** the director's-head interview/extraction mechanic (grill-me) — the
  pilot did not need it; it would help most for topics where the repo material is thin and the
  knowledge lives only in your head. Flagged for a later, separate decision.

**Nothing above generalises without your word.** The one page + stubs is the whole delivered artefact.
