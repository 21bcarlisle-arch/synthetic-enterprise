<!-- SUPERVISOR_DRAW: closed -->
<!-- draw-visibility marker (2026-07-24): CLOSED — R11 live-pixel verify CONFIRMED, archiving to done/. -->

# [PLANNER-MINTED] Walk each front-door MODEL-ON-A-PAGE node to ITS evidence (per-node deep anchors) (2026-07-24)

> **CLOSED (2026-07-24, worker tick): DONE — R11 live-pixel verify CONFIRMED on poesys.net.**
> The CDN has propagated `136573668`. Live fetch of https://poesys.net/ serves all 6 `node-look` hrefs with
> their #fragments (`./proof/#method-anchor`, `./world/#causal-chain`, `./customers/#cust-who`,
> `./world/#crossings`, `./company/#state-decisions`, `./proof/#not-proven`), and each fragment `id` was
> confirmed present on its deployed target page (curl over the 6 target pages: every `id="…"` found, none
> MISSING). The claim "walk any front-door diagram node to its evidence anchor" now holds on the rendered
> site, not just the file. The MOAP live gate (`site/link_walk.py::moap_node_findings`) prevents regression
> to page-tops. Mint discharged — archived to `docs/staging/done/`.
>
> **STATUS (2026-07-24, worker tick): BUILT + GATED + PUSHED — live-pixel verify now CONFIRMED (above).**
> Audit confirmed the gap was real (all 6 diagram nodes linked to bare page-tops). Wired every node to its
> verified deep anchor (method→/proof/#method-anchor, world→/world/#causal-chain, households→/customers/#cust-who,
> wall→/world/#crossings, company→/company/#state-decisions, score→/proof/#not-proven). New MOAP gate in
> `site/link_walk.py` (`moap_node_findings`) fails closed on a bare page-top / missing #id, R15-proven both ways
> + live-gate green (`test_link_walk.py`, 8 passed; site suite 306 passed/7 skipped). Committed+pushed `136573668`.
> **BLOCKING SUB-ITEM (the only open thing):** R11 live-pixel verify — at 20:xxZ poesys.net still served the old
> page-top hrefs (deploy of 136573668 not yet propagated). UNBLOCKS: once the CDN serves 136573668, one fetch of
> https://poesys.net/ confirms the 6 `node-look` hrefs render with their #fragments; then archive to done/. The
> live gate now PREVENTS any regression to page-tops, so this is a confirmation fetch, not further build.

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7 — rungs 1–6 empty this tick). **Propose-then-proceed.** Ruling-checked before minting: this is the explicitly-named "next" item and is distinct from the already-closed `world_spine_inline_graphs` (see "Distinctness" below) — not a re-draw.

## Ratified goal / campaign follow-on served
- **`DIRECTOR_RULING_CANONICAL_DOOR_A_COMMIT_THE_FOLD_2026-07-24.md`, "After the fold" — verbatim:** *"The SITE_MODEL_SPINE campaign is unblocked — proceed per its open items (**evidence pages behind the diagram nodes next**)."* §A (the canonical-door decision that blocked this) is now RESOLVED by that ruling, so the evidence-behind-the-nodes work is unblocked for the first time.
- **DIRECTOR_AXES §1 (Website):** *"Usefulness to him as an operational window — can he open the site and understand the state of the company without asking"* + *"Simplicity/clarity as a marketing tool — legible to someone who is not the builder."* The model-on-a-page diagram is the front-door's legibility spine; a node that walks to its own evidence is the difference between "asserted" and "verifiable at a click."

## The concrete gap (verified 2026-07-24)
The front-door model-on-a-page has a node-by-node stage view ("Live / Building / Planned, one click to a look-at-this view"), but the node links resolve only to **page-tops** — `./proof/`, `./world/`, `./customers/` — not to the specific evidence for that node. A reader clicking the "weather → wholesale" node lands at the top of a page and must hunt for the figure. The claim "walk any node to its numbers" is therefore only coarsely true from the front door.

## Real-world fidelity / value gained
Each diagram node deep-links to ITS evidence anchor (the specific real figure + external anchor + repo artefact for that node — e.g. the weather node → the live 240 HDD figure and its Open-Meteo anchor on /world; the wholesale node → SSP £85.92/MWh and its Elexon anchor; the score node → the honest "NOT YET MEASURED" carbon state). The front-door diagram becomes a genuine index into the evidence archive, not a picture over a page-top link — directly serving the "legible to a non-builder / understand without asking" bar.

## Scope (propose-then-proceed, fully reversible)
1. **FRAME (draw now):** enumerate the diagram's nodes and, for each, the single canonical evidence anchor that already renders its real figure (most already exist as landed anchors on /world and /proof — this is anchor-wiring, not new evidence pages, keeping the build honest and small).
2. **BUILD (reversible):** replace each node's page-top href with its per-node deep anchor; where a target page lacks a stable `id` anchor for that figure, add the `id` (no new content — anchor precision only).
3. **R15 + R11:** extend `site/link_walk.py` / `test_link_walk.py` (the LIVE publish gate) so each MOAP node href must resolve to a *fragment anchor that exists on the target page* (fail-closed if a node points at a bare page-top or a missing `id`); verify on the DEPLOYED site after the next publish that each node click lands on its rendered figure (R11 — rendered value, not the file alone).

## Distinctness (why this is NOT a re-draw of a closed mint)
- `PLANNER_MINTED_world_spine_inline_graphs_2026-07-24.md` was closed NO-BUILD because inline graphs *on surface_2 /world* were already satisfied. **This mint is different:** it is the FRONT-DOOR diagram's node→evidence *walk* (deep-anchor precision), not graphs on /world. It explicitly REUSES /world's already-landed per-node evidence as anchor targets rather than rebuilding them — so it cannot collide with what closed that sibling.
- Honest scope caveat carried for the builder: the coarse page-level links already exist; the delta is per-node anchor precision + a gate that enforces it. If a fresh audit finds every node already resolves to a live fragment that renders its figure, close NO-BUILD and say so (do not manufacture anchors for their own sake).

## Walls named (untouched)
- No epistemic/curriculum/ground-truth surface touched — this is site-lane anchor wiring (`site/**`, L2, disjoint from any build).
- Axis-1 verdict remains the director's by right; this produces a more-walkable surface, never a self-awarded verdict.

## Propose-then-proceed window
Standard: RUNG-1 next tick. Fully reversible (href edits + a gate extension; git reverts). Proceed under standing site-lane authority (L2 parallel-permanent); no wall requires a director act. Director may waive the wait per the 2026-07-24 waiver precedent.

— RUNG-7 planner, 2026-07-24 worker tick.
