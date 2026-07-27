<!-- STATUS 2026-07-27: Phases A+B+C LANDED. Phase A (node→atom mapping + bidirectional coherence check, site/moap_coherence.py) and Phase B (computed node stage from mapped atom levels, site/moap_stage.py — LIVE/BUILDING/PLANNED derived per the mapping's _derivation_rule; R15 both-ways in site/test_moap_stage.py, 11 tests; live report shows 0 declared-vs-computed disagreements) landed earlier. Phase C NOW LANDED (site/moap_render.py + site/test_moap_render.py, 8 tests): the stage word RENDERED in the front-door diagram (site/index.html .node-head) is mechanically asserted to EQUAL the computed stage — render_findings() surfaces any node whose rendered claim OUTRUNS (over-claims) or LAGS its atoms; the real front door is clean (render_findings()==[]); the Timeframe-2 present-tense reading rule is now a test that fails the site-lane suite (pytest site/, tools/site_lane_gate.py) at publish rather than an editorial chore. R15 both-ways incl. the tautology-killer (flip on atom level alone). Phase D NOW LANDED -- atom COMPLETE, moved to done/: the DEDICATED cross-surface publish gate (tools/moap_coherence_gate.py + tests/tools/test_moap_coherence_gate.py, 12 tests), wired into tools/git-hooks/pre-commit right after the site-lane gate. It unions the three ready-made queries (Phase A hard mapping findings + moap_stage.stage_disagreements() + moap_render.render_findings()) and REFUSES a commit when any node's Live/Building/Planned stage disagrees across model/diagram/site/map. Crucially it triggers on the MAP (docs/design/maturity_map.yaml) -- closing the gap the site-lane gate misses (that gate fires only on site/ edits, so a map-only level change could flip a computed stage and let the front door over-claim past publish). SHADOW RAIL (the ruling's risk clause): tools/moap_coherence_gate.mode de-fangs a scanner false-positive to report-only instantly (default ENFORCE; no .mode file ships). R15 both-ways: unit 12/12 (fires per surface, tautology-killer flips on atom level alone, SHADOW returns 0 on the SAME findings ENFORCE blocks on) + LIVE fire proof (staged a real A1 level->0 map mutation, no site file staged -> gate refused rc=1 catching STAGE_DISAGREEMENT and STAGE_RENDER_DRIFT -> restored clean). pytest site/ 339 passed / 7 node-harness skips. -->
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
