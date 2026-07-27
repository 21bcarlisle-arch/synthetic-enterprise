<!-- STATUS 2026-07-27: Phase A (node→atom mapping + bidirectional coherence check) LANDED, R15 both ways, live gate green. OPEN: Phase B (computed stage from mapped atom levels), Phase C (site renders from the derivation), Phase D (publish-gate disagreement check). B unblocks NOW — the mapping shape has landed; twin §3a can BUILD-open within the SUPPLIER front (site/). Parked in in_progress/ so it stays drawable without re-granting empty supervisor turns. -->
<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — Coherence by derivation: model → diagram → site → map derive from one truth (§6) (2026-07-27)

**Provenance:** RUNG-7 mint from a ratified ruling's WORK THIS CREATES block (§2+§4, landed 6f2be1d41).
Source: `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27.md`, deliverable **6** ("Coherence
derivation per §6: node→atom mapping, computed stages, site rendering from the derivation, and the
publish-gate disagreement check"). **The ruling explicitly authorizes PHASING and requires a phase plan
proposed before building** ("§6 is the largest and may be proposed in stages; propose before building").

**The requirement (§6 verbatim intent):** the model, the diagram, the site and the map "must not be
kept in sync by hand; three of them must be derived from one."
- `THE_MODEL_ON_A_PAGE.md` (`docs/design/`) is the single source of truth for what exists.
- Every diagram node maps to named atoms; a node's stage (**Live / Building / Planned**) is **computed
  from those atoms' levels**, never hand-set.
- The site renders from the same derivation — a node cannot read "Live" while its atoms sit below target.
  The existing editorial reading rule (Timeframe-2 present-tense = claim-status defect) becomes
  **mechanical**.
- **Bidirectional:** a node with no atoms is a gap (→ §5 backlog); an atom with no node serves no part
  of the model and must be questioned.
- **Gate:** publish FAILS when model, diagram, site and map disagree.

**Serves:** §6 (the director's coherence requirement); the front-door legibility bar (DIRECTOR_AXES §1
"understand the state of the company without asking"); builds directly on the LANDED
`moap_node_evidence_anchors` work ([[project_site_model_spine_campaign]]) which already wired each of the
6 front-door diagram nodes to its evidence anchor and added the `site/link_walk.py::moap_node_findings`
live gate — this mint makes the node STAGE (not just its evidence href) derived+gated.

**Robustness gained (one sentence):** a diagram node's Live/Building/Planned stage is computed from its
mapped atoms' actual levels and rendered identically on the site, with publish failing on any
disagreement between model, diagram, site and map — so the front door can never claim "Live" for a node
whose atoms are below target, and drift becomes a gate failure rather than an editorial chore.

---

## Scope — PROPOSE PHASE PLAN FIRST, then BUILD per phase (site + harness lanes)
- **Lane:** site (`site/**`) + harness (derivation + publish gate). **Target level:** L2 per phase.
- **PROPOSED PHASING (the "propose before building" deliverable — for director/twin nod on the shape;
  each phase is its own atom + own commit + failing test first):**
  - **Phase A — node→atom mapping (data):** author the canonical map from each MODEL-ON-A-PAGE / front-
    door diagram node to its named atom id(s) in `maturity_map.yaml`. This is the keystone; everything
    else derives from it. R15: a node with no mapped atom is flagged (bidirectional gap → §5 backlog);
    an atom mapped to no node is flagged for questioning. LOW risk, unblocks B–D.
  - **Phase B — computed stage:** a derivation that reads the mapped atoms' levels and computes each
    node's stage (Live = all atoms at target; Building = some below; Planned = none started), replacing
    any hand-set stage. R15: raise/lower an atom's level → the node's computed stage changes.
  - **Phase C — site renders from the derivation:** the front-door node stage view reads the computed
    stage (not hand-authored text); the Timeframe-2-present-tense reading rule becomes a mechanical
    check on the derived stage. R11 live-pixel verify on poesys.net after publish.
  - **Phase D — publish-gate disagreement check:** extend the publish gate (alongside
    `site/link_walk.py`) to FAIL when model, diagram, site and map disagree on any node's stage. R15
    both ways: introduce a deliberate disagreement (site says Live, atom below target) → gate RED;
    aligned → green. Shadow rail on the scanner change (the ruling's risk clause).
- **Exit criteria (whole atom):** all four phases landed, each R15/R11-proven, publish gate green, live
  site verified. Until then, each phase closes independently.
- **Deps:** builds on landed `moap_node_evidence_anchors` + the SITE-model-spine campaign. Complements
  #5 (a node-with-no-atoms gap feeds the §5 backlog). LARGEST scope — expect multiple worker ticks; do
  NOT attempt in one tired mega-turn ([[feedback_operational_rebuild_standard]]).

## Walls untouched (director-reserved)
- One-way doors: none — git-reversible; no real market/money/secrets.
- L3 level moves stay `blocked_on: director_level_up` ([[feedback_levels_are_proposals]]); the node→atom
  MAPPING and the stage DERIVATION are harness/site work, but any atom LEVEL change remains a proposal
  the commit gate reverts.
- Curriculum values / model canon (`THE_MODEL_ON_A_PAGE.md` is Tier-2 canon) — the derivation READS it
  as truth; it does not rewrite the canon.

## Window
§6 is PROPOSE-THEN-PROCEED by the ruling's own words. Phase A (node→atom mapping) is the proposal's
concrete first artifact and is drawable now; B–D proceed once the mapping shape is nodded (twin §3a can
BUILD-open within the fronts, per [[feedback_check_fronts_before_twin_open]]).

— Planner mint, RUNG-7 refill from ruling WORK THIS CREATES §4, 2026-07-27.
